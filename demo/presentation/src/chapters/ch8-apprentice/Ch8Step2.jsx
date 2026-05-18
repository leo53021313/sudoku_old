import { motion } from 'motion/react';

const BOARD = [
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
const EMPTY_CELLS = [[1,3],[4,7],[7,2]];

export default function Ch8Step2() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 16,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        style={{ fontWeight: 900, fontSize: '1.5rem', color: '#666' }}
      >
        他一定解得出來
      </motion.div>

      <motion.div
        initial={{ scale: 0.85, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          display: 'grid', gridTemplateColumns: 'repeat(9, 1fr)',
          gap: 0, width: 540, height: 540,
          border: '6px solid #000', background: '#000',
          boxShadow: '12px 12px 0 0 #000',
        }}
      >
        {BOARD.flatMap((row, r) =>
          row.map((val, c) => {
            const isEmpty = EMPTY_CELLS.some(([er, ec]) => er === r && ec === c);
            const borderRight = (c + 1) % 3 === 0 && c < 8 ? '4px solid #000' : '1px solid #000';
            const borderBottom = (r + 1) % 3 === 0 && r < 8 ? '4px solid #000' : '1px solid #000';
            return (
              <motion.div
                key={`${r}-${c}`}
                animate={isEmpty ? { boxShadow: ['inset 0 0 0 0 #FF6B6B', 'inset 0 0 0 4px #FF6B6B', 'inset 0 0 0 0 #FF6B6B'] } : {}}
                transition={isEmpty ? { duration: 1.2, repeat: Infinity, ease: 'easeInOut' } : {}}
                style={{
                  background: '#FFFDF5', color: '#000',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontWeight: 700, fontSize: 24, fontFamily: 'Space Grotesk',
                  borderRight, borderBottom,
                }}
              >
                {isEmpty ? '' : val}
              </motion.div>
            );
          })
        )}
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.9 }}
        style={{ fontWeight: 900, fontSize: '2rem' }}
      >
        只有 <span style={{ background: '#FF6B6B', color: '#FFF', padding: '0 16px', border: '4px solid #000' }}>3 格空</span>
      </motion.div>
    </main>
  );
}
