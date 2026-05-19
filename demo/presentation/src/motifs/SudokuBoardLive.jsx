import { motion } from 'motion/react';

const SIZE = 540;
const STROKE_OUTER = 6;
const STROKE_BOX = 4;
const STROKE_THIN = 1;

export function SudokuBoardLive({ cells, highlights = [], active = true }) {
  const cellSize = (SIZE - STROKE_OUTER * 2) / 9;
  const highlightSet = new Set(highlights.map(([r, c]) => `${r}-${c}`));

  const lines = [];
  for (let i = 0; i <= 9; i++) {
    const x = STROKE_OUTER + i * cellSize;
    const isEdge = i === 0 || i === 9;
    const sw = isEdge ? STROKE_OUTER : (i % 3 === 0) ? STROKE_BOX : STROKE_THIN;
    lines.push({ key: `v${i}`, x1: x, y1: 0, x2: x, y2: SIZE, sw });
    lines.push({ key: `h${i}`, x1: 0, y1: STROKE_OUTER + i * cellSize, x2: SIZE, y2: STROKE_OUTER + i * cellSize, sw });
  }

  return (
    <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`}
         style={{ background: '#FFFDF5', boxShadow: '12px 12px 0 0 #000' }}>
      {lines.map((ln, i) => (
        <motion.line
          key={ln.key}
          data-role="grid-line"
          x1={ln.x1} y1={ln.y1} x2={ln.x2} y2={ln.y2}
          stroke="#000" strokeWidth={ln.sw}
          initial={active ? { pathLength: 0 } : { pathLength: 1 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.3, delay: active ? i * 0.08 : 0 }}
        />
      ))}
      {cells.flatMap((row, r) => row.map((val, c) => {
        const isHl = highlightSet.has(`${r}-${c}`);
        const cx = STROKE_OUTER + c * cellSize + cellSize / 2;
        const cy = STROKE_OUTER + r * cellSize + cellSize / 2;
        return (
          <g key={`${r}-${c}`} data-role="cell" data-highlight={isHl ? 'true' : 'false'}>
            {isHl && (
              <motion.rect
                x={STROKE_OUTER + c * cellSize + 2}
                y={STROKE_OUTER + r * cellSize + 2}
                width={cellSize - 4} height={cellSize - 4}
                fill="none" stroke="#FF6B6B" strokeWidth={4}
                animate={{ opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
              />
            )}
            {val !== 0 && (
              <motion.text
                x={cx} y={cy}
                textAnchor="middle" dominantBaseline="central"
                fontFamily="Space Grotesk" fontWeight={900} fontSize={28} fill="#000"
                initial={active ? { scale: 0, opacity: 0 } : { scale: 1, opacity: 1 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{
                  duration: 0.4,
                  delay: active ? 1.8 + (r * 9 + c) * 0.015 : 0,
                  ease: [0.34, 1.56, 0.64, 1],
                }}
              >{val}</motion.text>
            )}
          </g>
        );
      }))}
    </svg>
  );
}
