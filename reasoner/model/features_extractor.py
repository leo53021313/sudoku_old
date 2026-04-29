# reasoner/model/features_extractor.py
# -*- coding: utf-8 -*-
"""
SudokuFeaturesExtractor — fill + eliminate per-cell action heads.

Input:  (batch, C, 9, 9)  — C channels, channels-first (C=24 in reasoner)
Output: (batch, 1458 + features_dim)
  - dims 0..728     : per-cell FILL logits (action 0..728  in env)
  - dims 729..1457  : per-cell ELIMINATE logits (action 729..1457 in env)
  - dims 1458..end  : global context (for value head, len = features_dim)

Architecture:
  Cell embedding:   Linear(C→128) → LayerNorm → ReLU → Linear(128→128) → LayerNorm → ReLU
  27 ConstraintHeads (9 row + 9 col + 9 box): gated local+context attention
  Fused:            (batch, 81, 192)
  Per-cell FILL logits:      cell_proj_fill(fused) → (batch, 81, 9) → (batch, 729)
  Per-cell ELIMINATE logits: cell_proj_elim(fused) → (batch, 81, 9) → (batch, 729)
  Global context:            global_proj(fused.mean(dim=1)) → (batch, features_dim)
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor


class ConstraintHead(nn.Module):
    """Gated constraint attention over 9 related cells."""

    def __init__(self, cell_dim: int = 128, head_dim: int = 64) -> None:
        super().__init__()
        self.fc   = nn.Linear(cell_dim, head_dim)
        self.gate = nn.Linear(cell_dim * 9, head_dim)

    def forward(self, cells: torch.Tensor) -> torch.Tensor:
        # cells: (batch, 9, cell_dim)
        B     = cells.size(0)
        local = F.relu(self.fc(cells))                       # (B, 9, head_dim)
        ctx   = self.gate(cells.reshape(B, -1)).unsqueeze(1) # (B, 1, head_dim)
        return local + torch.sigmoid(ctx) * local            # gated residual


class SudokuFeaturesExtractor(BaseFeaturesExtractor):
    """
    Constraint-head feature extractor with per-cell action head.

    Parameters
    ----------
    observation_space : gymnasium.spaces.Box
        Shape (C, 9, 9) — C channels.
    features_dim : int
        Global context dimension (default 192).
        Actual extractor output = 1458 + features_dim (= 1650 at default).
    cell_dim : int
        Cell embedding dimension (default 128).
    head_dim : int
        Constraint head output dimension (default 64).
        fused_dim = head_dim * 3 = 192.
    """

    def __init__(
        self,
        observation_space,
        features_dim: int = 192,
        cell_dim: int = 128,
        head_dim: int = 64,
    ) -> None:
        fused_dim   = head_dim * 3                   # 192
        actual_dim  = 2 * 9 * 81 + features_dim      # 1458 + 192 = 1650
        super().__init__(observation_space, actual_dim)

        in_channels      = observation_space.shape[0]
        self.cell_dim    = cell_dim
        self.head_dim    = head_dim
        self._global_dim = features_dim

        self.cell_embed = nn.Sequential(
            nn.Linear(in_channels, cell_dim),
            nn.LayerNorm(cell_dim),
            nn.ReLU(),
            nn.Linear(cell_dim, cell_dim),
            nn.LayerNorm(cell_dim),
            nn.ReLU(),
        )

        self.row_heads = nn.ModuleList([ConstraintHead(cell_dim, head_dim) for _ in range(9)])
        self.col_heads = nn.ModuleList([ConstraintHead(cell_dim, head_dim) for _ in range(9)])
        self.box_heads = nn.ModuleList([ConstraintHead(cell_dim, head_dim) for _ in range(9)])

        # Two per-cell projections — one for fill, one for eliminate.
        # Each maps fused (B, 81, 192) → (B, 81, 9) → flatten to (B, 729).
        self.cell_proj_fill = nn.Linear(fused_dim, 9)
        self.cell_proj_elim = nn.Linear(fused_dim, 9)
        # Global context for value estimation: mean-pool → (B, features_dim)
        self.global_proj = nn.Linear(fused_dim, features_dim)

    def forward(self, observations: torch.Tensor) -> torch.Tensor:
        # observations: (batch, C, 9, 9) — channels-first
        B = observations.size(0)

        # Per-cell embedding: (B, C, 9, 9) → (B, 81, C) → (B, 81, cell_dim)
        x   = observations.permute(0, 2, 3, 1).reshape(B, 81, -1)
        emb = self.cell_embed(x)                                    # (B, 81, cell_dim)
        emb_ = emb.reshape(B, 9, 9, self.cell_dim)

        # Row heads: each head processes one row of 9 cells
        row_out = torch.stack(
            [self.row_heads[r](emb_[:, r]) for r in range(9)], dim=1
        )  # (B, 9, 9, head_dim)

        # Column heads
        # emb_[:, :, c, :] is (B, 9, cell_dim) — 9 rows for column c
        # col_heads[c] output: (B, 9, head_dim)
        # stack along new dim=2 → (B, 9, 9, head_dim) where dim2 = col index
        col_out = torch.stack(
            [self.col_heads[c](emb_[:, :, c, :]) for c in range(9)], dim=2
        )

        # Box heads — scatter-free: collect 9 outputs, then reshape+permute into board layout
        box_results = []
        for b in range(9):
            br, bc = (b // 3) * 3, (b % 3) * 3
            box_cells = emb_[:, br:br+3, bc:bc+3, :].reshape(B, 9, self.cell_dim)
            box_results.append(self.box_heads[b](box_cells).reshape(B, 3, 3, self.head_dim))

        # stack: (B, 9, 3, 3, head_dim); box index b = box_row*3+box_col, so reshape splits it:
        # reshape → (B, box_row, box_col, local_row, local_col, head_dim)
        # permute(0,1,3,2,4,5) → (B, box_row, local_row, box_col, local_col, head_dim)
        # reshape → (B, 9, 9, head_dim): row = box_row*3+local_row, col = box_col*3+local_col
        box_out = (
            torch.stack(box_results, dim=1)
            .reshape(B, 3, 3, 3, 3, self.head_dim)
            .permute(0, 1, 3, 2, 4, 5)
            .reshape(B, 9, 9, self.head_dim)
        )

        # Fuse per-cell outputs: (B, 81, head_dim * 3)
        fused = torch.cat([
            row_out.reshape(B, 81, self.head_dim),
            col_out.reshape(B, 81, self.head_dim),
            box_out.reshape(B, 81, self.head_dim),
        ], dim=-1)

        # Per-cell FILL logits: (B, 81, 9) → (B, 729) — actions 0..728
        fill_logits = self.cell_proj_fill(fused).reshape(B, 729)
        # Per-cell ELIMINATE logits: (B, 81, 9) → (B, 729) — actions 729..1457
        elim_logits = self.cell_proj_elim(fused).reshape(B, 729)

        # Global context for value head: mean-pool → (B, global_dim)
        global_ctx = self.global_proj(fused.mean(dim=1))

        # Concatenate: (B, 1458 + features_dim) = (B, 1650) at defaults
        return torch.cat([fill_logits, elim_logits, global_ctx], dim=-1)
