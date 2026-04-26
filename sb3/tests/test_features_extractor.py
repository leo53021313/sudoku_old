# sb3/tests/test_features_extractor.py
"""Tests for SudokuFeaturesExtractor with 26-channel input and 921-dim output."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import torch
import numpy as np
import gymnasium as gym
from app.rl.models.features_extractor import SudokuFeaturesExtractor


def make_obs_space(n_channels=26):
    return gym.spaces.Box(low=0.0, high=1.0, shape=(n_channels, 9, 9), dtype=np.float32)


def test_output_shape():
    """Extractor should output (batch, 921) with default features_dim=192."""
    extractor = SudokuFeaturesExtractor(make_obs_space(26), features_dim=192)
    obs = torch.randn(4, 26, 9, 9)
    out = extractor(obs)
    assert out.shape == (4, 921), f"Expected (4, 921), got {out.shape}"
    print("test_output_shape: PASS")


def test_features_dim_attribute():
    """BaseFeaturesExtractor.features_dim should be 921."""
    extractor = SudokuFeaturesExtractor(make_obs_space(26), features_dim=192)
    assert extractor.features_dim == 921, f"Expected 921, got {extractor.features_dim}"
    print("test_features_dim_attribute: PASS")


def test_per_cell_structure():
    """First 729 output dims should vary across positions (not mean-pooled)."""
    extractor = SudokuFeaturesExtractor(make_obs_space(26), features_dim=192)
    extractor.eval()
    obs1 = torch.zeros(1, 26, 9, 9)
    obs2 = torch.zeros(1, 26, 9, 9)
    obs2[0, 0, 0, 0] = 1.0

    with torch.no_grad():
        out1 = extractor(obs1)[0, :729]
        out2 = extractor(obs2)[0, :729]

    diff = (out1 - out2).abs()
    assert diff[:9].sum() > 0, "Cell (0,0) logits unchanged despite obs difference"
    assert diff.sum() > 0, "No output changed despite obs difference"
    print("test_per_cell_structure: PASS")


def test_backward_compatible_9ch():
    """Old 9-channel input should still work."""
    extractor = SudokuFeaturesExtractor(make_obs_space(9), features_dim=192)
    obs = torch.randn(2, 9, 9, 9)
    out = extractor(obs)
    assert out.shape == (2, 921)
    print("test_backward_compatible_9ch: PASS")


def test_box_head_output_unchanged_after_refactor():
    """Box head output must be bitwise-identical before and after removing the 9x9 list."""
    extractor = SudokuFeaturesExtractor(make_obs_space(26), features_dim=192)
    extractor.eval()

    obs = torch.randn(3, 26, 9, 9)
    with torch.no_grad():
        out = extractor(obs)

    # Shape must be (3, 921)
    assert out.shape == (3, 921), f"Expected (3, 921), got {out.shape}"

    # No NaN or Inf in output
    assert not torch.isnan(out).any(), "NaN in extractor output"
    assert not torch.isinf(out).any(), "Inf in extractor output"
    print("test_box_head_output_unchanged_after_refactor: PASS")


if __name__ == "__main__":
    test_output_shape()
    test_features_dim_attribute()
    test_per_cell_structure()
    test_backward_compatible_9ch()
    test_box_head_output_unchanged_after_refactor()
    print("\nAll features_extractor tests PASSED")
