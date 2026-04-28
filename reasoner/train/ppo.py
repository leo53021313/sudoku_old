"""SudokuMaskablePPO — thin subclass of MaskablePPO with NO BC.

Exists only to provide a stable extension point for future logging hooks
without modifying train.py. All training behavior is inherited unchanged
from sb3-contrib's MaskablePPO.
"""

from __future__ import annotations
from sb3_contrib import MaskablePPO


class SudokuMaskablePPO(MaskablePPO):
    """Pure MaskablePPO with no BC, no teacher capture, no monkey-patching."""
    pass
