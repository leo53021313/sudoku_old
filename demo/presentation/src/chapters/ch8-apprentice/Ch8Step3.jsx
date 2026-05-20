import { motion } from 'motion/react';
import { useEffect, useState } from 'react';

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
const REMOVAL_SEQ = [
  [1,3],[4,7],[7,2],[0,4],[3,1],[6,7],[2,2],[5,5],[8,1],[4,4],
];

export default function Ch8Step3() {
  const [count, setCount] = useState(3);

  useEffect(() => {
    let cur = 3;
    const id = setInterval(() => {
      cur = cur + 1;
      if (cur > 10) {
        clearInterval(id);
        return;
      }
      setCount(cur);
    }, 500);
    return () => clearInterval(id);
  }, []);

  const blanks = new Set(REMOVAL_SEQ.slice(0, count).map(([r, c]) => `${r}-${c}`));
  // 最新一次被挖空的格子（count 從 3 起跳，初始 3 格不閃，之後每 +1 高亮新格）
  const newestKey = count > 3 ? `${REMOVAL_SEQ[count - 1][0]}-${REMOVAL_SEQ[count - 1][1]}` : null;

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
        style={{ fontWeight: 900, fontSize: '1.5rem' }}
      >
        讓難度跟著他的能力走
      </motion.div>

      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(9, 1fr)',
        width: 540, height: 540,
        border: '6px solid #000', background: '#000',
        boxShadow: '12px 12px 0 0 #000',
      }}>
        {BOARD.flatMap((row, r) =>
          row.map((val, c) => {
            const isEmpty = blanks.has(`${r}-${c}`);
            const isNew = `${r}-${c}` === newestKey;
            const borderRight = (c + 1) % 3 === 0 && c < 8 ? '4px solid #000' : '1px solid #000';
            const borderBottom = (r + 1) % 3 === 0 && r < 8 ? '4px solid #000' : '1px solid #000';
            return (
              <motion.div
                key={`${r}-${c}`}
                animate={
                  isNew
                    // 最新挖空的格子：先塌縮、再過衝放大歸位，伴隨黃色閃光 + 紅色內框環，視覺上明確「又多一格」
                    ? {
                        scale: [0.35, 1.28, 1],
                        backgroundColor: ['#FFD93D', '#FFD93D', '#FFFDF5'],
                        boxShadow: [
                          'inset 0 0 0 5px #FF5252',
                          'inset 0 0 0 5px #FF5252',
                          'inset 0 0 0 0px #FF5252',
                        ],
                      }
                    : { scale: 1, backgroundColor: '#FFFDF5', boxShadow: 'inset 0 0 0 0px #FF5252' }
                }
                transition={isNew
                  ? { duration: 0.45, times: [0, 0.4, 1], ease: 'easeOut' }
                  : { duration: 0.2 }}
                style={{
                  background: '#FFFDF5', color: '#000',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontWeight: 700, fontSize: 24,
                  borderRight, borderBottom,
                }}
              >
                {isEmpty ? '' : val}
              </motion.div>
            );
          })
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontWeight: 900, fontSize: 24 }}>
        空格:
        <motion.span
          key={count}
          initial={{ scale: 1.5 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 500, damping: 18 }}
          style={{
            display: 'inline-block',
            background: '#FFD93D', color: '#000',
            padding: '4px 16px', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
            fontFamily: 'monospace', fontSize: 32, rotate: -2,
          }}
        >
          {count}
        </motion.span>
        / 10
      </div>
    </main>
  );
}
