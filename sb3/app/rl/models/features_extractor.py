# app/rl/models/features_extractor.py
# -*- coding: utf-8 -*-
"""
SudokuFeaturesExtractor — constraint-head architecture with per-cell action head.

Input:  (batch, C, 9, 9)  — C channels, channels-first (C=26 for new obs, C=9 legacy)
Output: (batch, 729 + features_dim)  — per-cell action logits + global context

Architecture:
  Cell embedding:   Linear(C→128) → LayerNorm → ReLU → Linear(128→128) → LayerNorm → ReLU
  27 ConstraintHeads (9 row + 9 col + 9 box): gated local+context attention
  Fused:            (batch, 81, 192)
  Per-cell logits:  cell_proj(fused) → (batch, 81, 9) → (batch, 729)
  Global context:   global_proj(fused.mean(dim=1)) → (batch, features_dim)
  Output:           cat([per_cell_logits, global_ctx], dim=-1) → (batch, 729 + features_dim)
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
        Shape (C, 9, 9) — C channels (26 for new obs, 9 for legacy).
    features_dim : int
        Global context dimension (default 192).
        Actual extractor output = 729 + features_dim (= 921 at default).
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
        fused_dim   = head_dim * 3            # 192
        actual_dim  = 9 * 81 + features_dim   # 729 + 192 = 921
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

        # Per-cell projection: fused (B, 81, 192) → action logits (B, 81, 9) → (B, 729)
        self.cell_proj   = nn.Linear(fused_dim, 9)
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
        col_out = torch.zeros(B, 9, 9, self.head_dim, device=observations.device)
        for c in range(9):
            col_out[:, :, c, :] = self.col_heads[c](emb_[:, :, c, :])

        # Box heads
        box_out = torch.zeros(B, 9, 9, self.head_dim, device=observations.device)
        for b in range(9):
            br, bc    = (b // 3) * 3, (b % 3) * 3
            box_cells = emb_[:, br:br+3, bc:bc+3, :].reshape(B, 9, self.cell_dim)
            result    = self.box_heads[b](box_cells)                 # (B, 9, head_dim)
            box_out[:, br:br+3, bc:bc+3, :] = result.reshape(B, 3, 3, self.head_dim)

        # Fuse per-cell outputs: (B, 81, head_dim * 3)
        fused = torch.cat([
            row_out.reshape(B, 81, self.head_dim),
            col_out.reshape(B, 81, self.head_dim),
            box_out.reshape(B, 81, self.head_dim),
        ], dim=-1)

        # Per-cell action logits: (B, 81, 9) → (B, 729)
        cell_logits = self.cell_proj(fused).reshape(B, 729)

        # Global context for value head: mean-pool → (B, global_dim)
        global_ctx = self.global_proj(fused.mean(dim=1))

        # Concatenate: (B, 921)
        return torch.cat([cell_logits, global_ctx], dim=-1)
