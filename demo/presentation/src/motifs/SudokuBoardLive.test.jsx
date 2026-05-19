import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { SudokuBoardLive } from './SudokuBoardLive.jsx';

const SOLVED = [
  [5,3,4, 6,7,8, 9,1,2],
  [6,7,2, 1,9,5, 3,4,8],
  [1,9,8, 3,4,2, 5,6,7],
  [8,5,9, 7,6,1, 4,2,3],
  [4,2,6, 8,5,3, 7,9,1],
  [7,1,3, 9,2,4, 8,5,6],
  [9,6,1, 5,3,7, 2,8,4],
  [2,8,7, 4,1,9, 6,3,5],
  [3,4,5, 2,8,6, 1,7,9],
];

describe('SudokuBoardLive', () => {
  it('renders 81 cells', () => {
    const { container } = render(<SudokuBoardLive cells={SOLVED} active={false} />);
    const cells = container.querySelectorAll('[data-role="cell"]');
    expect(cells.length).toBe(81);
  });

  it('renders 20 grid lines (10 vertical + 10 horizontal)', () => {
    const { container } = render(<SudokuBoardLive cells={SOLVED} active={false} />);
    const lines = container.querySelectorAll('[data-role="grid-line"]');
    expect(lines.length).toBe(20);
  });

  it('cells with value 0 render empty', () => {
    const empty = Array.from({ length: 9 }, () => Array(9).fill(0));
    const { container } = render(<SudokuBoardLive cells={empty} active={false} />);
    const cells = container.querySelectorAll('[data-role="cell"]');
    cells.forEach(c => expect(c.textContent).toBe(''));
  });

  it('marks highlighted cells with data-highlight="true"', () => {
    const { container } = render(
      <SudokuBoardLive cells={SOLVED} highlights={[[0,0],[4,4]]} active={false} />
    );
    const highlighted = container.querySelectorAll('[data-role="cell"][data-highlight="true"]');
    expect(highlighted.length).toBe(2);
  });
});
