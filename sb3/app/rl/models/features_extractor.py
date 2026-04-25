# app/rl/models/features_extractor.py
# -*- coding: utf-8 -*-
"""
SudokuFeaturesExtractor — ports the constraint-head architecture from
SudokuPPONet (app/sudoku/torch_agent.py) to SB3's BaseFeaturesExtractor.

Input:  (batch, 9, 9, 9)  — 9-channel channels-first Sudoku observation
Output: (batch, features_dim)  — mean-pooled cell features

Architecture:
  Cell embedding: Linear(9→128) → LayerNorm → ReLU → Linear(128→128) → LayerNorm → ReLU
  27 ConstraintHeads (9 row + 9 col + 9 box): gated local+context attention
  Fused: (batch, 81, 192)
  Mean pool over 81 cells → (batch, 192)
  Final linear → (batch, features_dim)
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
        B    = cells.size(0)
        local = F.relu(self.fc(cells))                          # (B, 9, head_dim)
        ctx   = self.gate(cells.reshape(B, -1)).unsqueeze(1)    # (B, 1, head_dim)
        return local + torch.sigmoid(ctx) * local               # gated residual


class SudokuFeaturesExtractor(BaseFeaturesExtractor):
    """
    Constraint-head feature extractor for Sudoku observations.

    Parameters
    ----------
    observation_space : gymnasium.spaces.Box
        Shape (9, 9, 9) — 9 channels × 9 × 9 board.
    features_dim : int
        Output feature dimension (default 192).
    cell_dim : int
        Cell embedding dimension (default 128).
    head_dim : int
        Constraint head output dimension (default 64).
        fused_dim = head_dim × 3 = 192 (must equal features_dim default).
    """

    def __init__(
        self,
        observation_space,
        features_dim: int = 192,
        cell_dim: int = 128,
        head_dim: int = 64,
    ) -> None:
        super().__init__(observation_space, features_dim)

        in_channels = observation_space.shape[0]  # 9
        self.cell_dim = cell_dim
        self.head_dim = head_dim

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

        fused_dim = head_dim * 3  # 192
        self.proj = nn.Linear(fused_dim, features_dim)

    def forward(self, observations: torch.Tensor) -> torch.Tensor:
        # observations: (batch, 9, 9, 9)  — channels-first
        B = observations.size(0)

        # Reshape: (B, 9, 9, 9) → (B, 81, 9) for per-cell embedding
        x = observations.permute(0, 2, 3, 1).reshape(B, 81, -1)  # (B, 81, in_ch)
        emb = self.cell_embed(x)                                   # (B, 81, cell_dim)
        emb_ = emb.reshape(B, 9, 9, self.cell_dim)

        # Row heads: each head processes one row of 9 cells
        row_out = torch.stack(
            [self.row_heads[r](emb_[:, r]) for r in range(9)], dim=1
        )  # (B, 9, 9, head_dim)

        # Column heads: each head processes one column of 9 cells
        col_out = torch.zeros(B, 9, 9, self.head_dim, device=observations.device)
        for c in range(9):
            col_out[:, :, c, :] = self.col_heads[c](emb_[:, :, c, :])

        # Box heads: each head processes one 3×3 box (9 cells)
        box_out = torch.zeros(B, 9, 9, self.head_dim, device=observations.device)
        for b in range(9):
            br, bc = (b // 3) * 3, (b % 3) * 3
            box_cells = emb_[:, br:br+3, bc:bc+3, :].reshape(B, 9, self.cell_dim)
            result = self.box_heads[b](box_cells)                  # (B, 9, head_dim)
            box_out[:, br:br+3, bc:bc+3, :] = result.reshape(B, 3, 3, self.head_dim)

        # Fuse per-cell outputs from all three constraint types
        fused = torch.cat([
            row_out.reshape(B, 81, self.head_dim),
            col_out.reshape(B, 81, self.head_dim),
            box_out.reshape(B, 81, self.head_dim),
        ], dim=-1)  # (B, 81, head_dim * 3)

        # Mean pool over 81 cells → global board representation
        pooled = fused.mean(dim=1)  # (B, head_dim * 3)
        return self.proj(pooled)    # (B, features_dim)
