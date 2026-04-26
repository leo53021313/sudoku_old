import pytest
from app.web.reader import _PuzzleHTMLParser, get_level_url, BlockedError, SUDOKU_LEVELS


def _make_html(values: dict) -> str:
    """Build minimal websudoku-style HTML. values: {(col, row): digit_str}"""
    parts = []
    for row in range(9):
        for col in range(9):
            val = values.get((col, row), "")
            readonly = " readonly" if val else ""
            parts.append(f'<input id="f{col}{row}" value="{val}"{readonly}>')
    return "".join(parts)


def test_parser_reads_81_cells():
    html = _make_html({(0, 0): "5", (8, 8): "9"})
    p = _PuzzleHTMLParser()
    p.feed(html)
    assert p.cell_count == 81
    assert p.board[0][0] == 5
    assert p.board[8][8] == 9


def test_parser_fixed_flags():
    html = _make_html({(1, 2): "7"})  # col=1, row=2 → board[row][col] = board[2][1]
    p = _PuzzleHTMLParser()
    p.feed(html)
    assert p.fixed[2][1] is True
    assert p.fixed[0][0] is False


def test_get_level_url_all_levels():
    for lvl in [1, 2, 3, 4]:
        url = get_level_url(lvl)
        assert f"level={lvl}" in url
        assert "east.websudoku.com" in url


def test_get_level_url_invalid_raises():
    with pytest.raises(ValueError):
        get_level_url(5)


def test_blocked_error_is_runtime_error():
    assert issubclass(BlockedError, RuntimeError)
