class WebSudokuReader:
    def __init__(self, page):
        self.page = page

    def find_puzzle_context(self):
        # 先找 iframe 裡的 puzzle
        for frame in self.page.frames:
            try:
                if frame.locator("#puzzle_grid").count() > 0:
                    return frame
            except:
                pass

        # 如果主頁就有，也支援
        if self.page.locator("#puzzle_grid").count() > 0:
            return self.page

        raise RuntimeError("Could not find puzzle grid in page or iframe.")

    def cell_selector(self, row, col):
        # websudoku 的 id 是 f{col}{row}
        return f"#f{col}{row}"

    def read_board(self):
        target = self.find_puzzle_context()
        target.wait_for_selector("#puzzle_grid input")

        board = []
        fixed = []
        raw_cells = []

        for row in range(9):
            board_row = []
            fixed_row = []
            raw_row = []

            for col in range(9):
                selector = self.cell_selector(row, col)
                el = target.locator(selector)

                if el.count() == 0:
                    raise ValueError(f"Cell not found: row={row}, col={col}, selector={selector}")

                # 這裡要用 input_value，不要用 get_attribute("value")
                value = el.input_value().strip()

                if value.isdigit():
                    num = int(value)
                else:
                    num = 0

                readonly = el.get_attribute("readonly") is not None

                board_row.append(num)
                fixed_row.append(readonly)
                raw_row.append(value)

            board.append(board_row)
            fixed.append(fixed_row)
            raw_cells.append(raw_row)

        return board, fixed, raw_cells