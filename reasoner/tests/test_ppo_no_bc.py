from reasoner.train.ppo import SudokuMaskablePPO


def test_ppo_class_has_no_bc_pass_method():
    """Sanity: confirm we did not accidentally bring _bc_pass over from sb3."""
    assert not hasattr(SudokuMaskablePPO, "_bc_pass")


def test_ppo_class_inherits_from_maskable_ppo():
    from sb3_contrib import MaskablePPO
    assert issubclass(SudokuMaskablePPO, MaskablePPO)
