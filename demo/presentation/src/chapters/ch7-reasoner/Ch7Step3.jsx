import { useState } from 'react';
import { motion } from 'motion/react';

const TECHS = [
  { name: 'Naked Single', size: 'sm', color: '#FFD93D', tip: '一格只能填一個數' },
  { name: 'Hidden Single', size: 'sm', color: '#FFD93D', tip: '一個數字在一行/列/區只有一處能填' },
  { name: 'Box-Line', size: 'sm', color: '#FFD93D', tip: '區內某數限制於某行/列' },
  { name: 'Pointing Pair', size: 'sm', color: '#FFD93D', tip: '兩格限定一行/列' },
  { name: 'Naked Pair', size: 'md', color: '#C4B5FD', tip: '兩格共用兩個候選數' },
  { name: 'Naked Triple', size: 'md', color: '#C4B5FD', tip: '三格共用三個候選數' },
  { name: 'Hidden Pair', size: 'md', color: '#C4B5FD', tip: '兩個數只能在兩格中之一' },
  { name: 'Hidden Triple', size: 'md', color: '#C4B5FD', tip: '三個數只能在三格中' },
  { name: 'XY-Wing', size: 'lg', color: '#FF6B6B', tip: 'Y-shaped 三格鏈消除' },
  { name: 'XYZ-Wing', size: 'lg', color: '#FF6B6B', tip: 'XYZ 變體三格鏈' },
  { name: 'Swordfish', size: 'lg', color: '#FF6B6B', tip: '三行三列交叉消除' },
  { name: 'X-Wing', size: 'xl', color: '#FF6B6B', tip: '兩行兩列交叉、最強招之一' },
  { name: 'T&E (試錯)', size: 'xl', color: '#FF6B6B', tip: 'Trial and Error 暴力試' },
];

const SIZE_MAP = {
  sm: { padding: '8px 16px', fontSize: 14, shadow: '4px 4px 0 0 #000' },
  md: { padding: '12px 20px', fontSize: 16, shadow: '6px 6px 0 0 #000' },
  lg: { padding: '16px 28px', fontSize: 20, shadow: '8px 8px 0 0 #000' },
  xl: { padding: '20px 36px', fontSize: 26, shadow: '12px 12px 0 0 #000' },
};

export default function Ch7Step3() {
  const [hoverIdx, setHoverIdx] = useState(-1);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        style={{
          background: '#000', color: '#FFFDF5',
          padding: '12px 28px', fontWeight: 900, fontSize: 18,
          marginBottom: 16,
        }}
      >
        13 招 · 真實技巧名
      </motion.div>

      {/* Stairs: each tech is a step, ascending diagonal */}
      <div style={{
        position: 'relative', width: 1000, height: 540,
      }}>
        {TECHS.map((t, i) => {
          const sz = SIZE_MAP[t.size];
          const x = (i / TECHS.length) * 90;
          const y = 95 - (i / TECHS.length) * 85;
          const isHovered = i === hoverIdx;
          return (
            <motion.div
              key={i}
              initial={{ y: 30, scale: 0.8, opacity: 0 }}
              animate={{ y: 0, scale: isHovered ? 1.15 : 1, opacity: 1 }}
              transition={{
                opacity: { duration: 0.3, delay: 0.4 + i * 0.08 },
                y: { duration: 0.3, delay: 0.4 + i * 0.08 },
                scale: { duration: 0.2 },
              }}
              onMouseEnter={() => setHoverIdx(i)}
              onMouseLeave={() => setHoverIdx(-1)}
              style={{
                position: 'absolute', left: `${x}%`, bottom: `${y}%`,
                background: t.color, color: '#000',
                ...sz,
                border: '4px solid #000', boxShadow: sz.shadow, fontWeight: 900,
                transform: `rotate(${(i % 2 === 0 ? -1 : 1) * (3 + i % 4)}deg)`,
                opacity: hoverIdx === -1 ? 1 : isHovered ? 1 : 0.4,
                cursor: 'pointer', whiteSpace: 'nowrap',
                transition: 'opacity 0.2s',
                zIndex: isHovered ? 20 : 1,
              }}
            >
              {t.name}
              {isHovered && (
                <div style={{
                  position: 'absolute', top: '110%', left: 0,
                  background: '#000', color: '#FFFDF5',
                  padding: '8px 12px', fontSize: 12,
                  whiteSpace: 'nowrap', fontWeight: 700,
                }}>
                  {t.tip}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      <div style={{ marginTop: 16, fontWeight: 700, color: '#666', fontSize: 16 }}>
        低階 → → → 高階
      </div>
    </main>
  );
}
