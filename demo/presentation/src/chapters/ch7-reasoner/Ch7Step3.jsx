import { useState } from 'react';
import { motion } from 'motion/react';

// 難度進程靠「顏色三階（黃→紫→紅）」+「左低右高攀升」表達，所有 sticker 高度一致、寬度隨字數變。
const TECHS = [
  { name: 'Naked Single', color: '#FFD93D', tip: '一格只能填一個數' },
  { name: 'Hidden Single', color: '#FFD93D', tip: '一個數字在一行/列/區只有一處能填' },
  { name: 'Box-Line', color: '#FFD93D', tip: '區內某數限制於某行/列' },
  { name: 'Pointing Pair', color: '#FFD93D', tip: '兩格限定一行/列' },
  { name: 'Naked Pair', color: '#C4B5FD', tip: '兩格共用兩個候選數' },
  { name: 'Naked Triple', color: '#C4B5FD', tip: '三格共用三個候選數' },
  { name: 'Hidden Pair', color: '#C4B5FD', tip: '兩個數只能在兩格中之一' },
  { name: 'Hidden Triple', color: '#C4B5FD', tip: '三個數只能在三格中' },
  { name: 'XY-Wing', color: '#FF6B6B', tip: 'Y-shaped 三格鏈消除' },
  { name: 'XYZ-Wing', color: '#FF6B6B', tip: 'XYZ 變體三格鏈' },
  { name: 'Swordfish', color: '#FF6B6B', tip: '三行三列交叉消除' },
  { name: 'X-Wing', color: '#FF6B6B', tip: '兩行兩列交叉、最強招之一' },
  { name: 'T&E (試錯)', color: '#FF6B6B', tip: 'Trial and Error 暴力試' },
];

// 統一尺寸（高度固定，寬度由內容決定）；shadow 一致
const STICKER = { padding: '11px 18px', fontSize: 16, shadow: '5px 5px 0 0 #000' };

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
          // 從左到右逐步攀升：x 往右、y 往上（bottom% 遞增），代表一招比一招難。
          // 均勻間距 + 統一高度：垂直步距 ≥ 一張的高度，每張都完全在前一張上方，文字不會被覆蓋。
          const p = i / (TECHS.length - 1);
          const x = p * 72;
          const y = 3 + p * 87;
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
                ...STICKER,
                border: '4px solid #000', boxShadow: STICKER.shadow, fontWeight: 900,
                transform: `rotate(${(i % 2 === 0 ? -1 : 1) * (3 + i % 4)}deg)`,
                opacity: hoverIdx === -1 ? 1 : isHovered ? 1 : 0.4,
                cursor: 'pointer', whiteSpace: 'nowrap',
                transition: 'opacity 0.2s',
                // 較早（左下、簡單）的 sticker 疊在上層，後面 sticker 的外框就不會蓋到前一個的文字
                zIndex: isHovered ? 50 : TECHS.length - i,
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
