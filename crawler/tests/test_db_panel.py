# crawler/tests/test_db_panel.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import MagicMock


def test_refresh_shows_error_label_on_db_failure(qapp, tmp_path):
    """When get_pool_stats raises, _total_lbl must show an error message."""
    from app.gui.db_panel import DbPanel
    from app.db.pool_db import PuzzlePoolDB

    db = PuzzlePoolDB(str(tmp_path / "test.db"))
    panel = DbPanel(db, max_pool_size=50_000)

    # Make get_pool_stats raise
    db.get_pool_stats = MagicMock(side_effect=Exception("DB locked"))

    panel.refresh()

    label_text = panel._total_lbl.text()
    assert "DB" in label_text or "錯誤" in label_text or "Error" in label_text, \
        f"Expected error label, got: {label_text!r}"


def test_refresh_resets_error_flag_on_success(qapp, tmp_path):
    """After a failed refresh, a successful refresh must clear the error label."""
    from app.gui.db_panel import DbPanel
    from app.db.pool_db import PuzzlePoolDB

    db = PuzzlePoolDB(str(tmp_path / "test.db"))
    panel = DbPanel(db, max_pool_size=50_000)

    # Fail first
    db.get_pool_stats = MagicMock(side_effect=Exception("DB locked"))
    panel.refresh()
    assert panel._refresh_error_shown is True

    # Succeed next — create a new DB that works
    real_db = PuzzlePoolDB(str(tmp_path / "test.db"))
    panel.db = real_db

    panel.refresh()
    assert panel._refresh_error_shown is False
    assert "總計" in panel._total_lbl.text(), \
        f"Expected success label, got: {panel._total_lbl.text()!r}"
