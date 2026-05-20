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

  it('frame is flush with the SVG edge; internal lines stay inside the frame', () => {
    // Two bugs guarded here:
    //  - internal lines spanning the full 0→SIZE extent → ends poked past the
    //    frame as stubs ("每條線都會跑出邊框");
    //  - frame inset from the SVG edge → a gap between the frame and the offset
    //    box-shadow ("陰影對齊").
    const SIZE = 540;
    const STROKE_OUTER = 6;
    const half = STROKE_OUTER / 2;
    const { container } = render(<SudokuBoardLive cells={SOLVED} active={false} />);
    const lines = Array.from(container.querySelectorAll('[data-role="grid-line"]'));

    let frameCount = 0;
    lines.forEach((ln) => {
      const x1 = Number(ln.getAttribute('x1'));
      const y1 = Number(ln.getAttribute('y1'));
      const x2 = Number(ln.getAttribute('x2'));
      const y2 = Number(ln.getAttribute('y2'));
      const isVertical = x1 === x2;
      const pos = isVertical ? x1 : y1;
      const spanLo = isVertical ? Math.min(y1, y2) : Math.min(x1, x2);
      const spanHi = isVertical ? Math.max(y1, y2) : Math.max(x1, x2);
      const isFrame = pos === half || pos === SIZE - half;
      if (isFrame) {
        frameCount++;
        // outer edge flush with SVG (shadow aligns) + full span for square corners
        expect(spanLo).toBe(0);
        expect(spanHi).toBe(SIZE);
      } else {
        // internal lines stop at the frame inner edge — no protruding stubs
        expect(spanLo).toBeGreaterThanOrEqual(STROKE_OUTER);
        expect(spanHi).toBeLessThanOrEqual(SIZE - STROKE_OUTER);
      }
    });
    expect(frameCount).toBe(4);
  });

  it('marks highlighted cells with data-highlight="true"', () => {
    const { container } = render(
      <SudokuBoardLive cells={SOLVED} highlights={[[0,0],[4,4]]} active={false} />
    );
    const highlighted = container.querySelectorAll('[data-role="cell"][data-highlight="true"]');
    expect(highlighted.length).toBe(2);
  });
});
