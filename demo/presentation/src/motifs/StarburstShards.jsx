// 星爆 POW 碎片：印章周圍鋸齒星形錯峰彈出再定格。
// 四角閃星 + 三角碎片交錯，漫畫爆點感，黃/紅/黑配色呼應全片。
import { motion } from 'motion/react';

// 四角閃星路徑（凹邊菱形，100×100 viewBox）
const STAR = 'M50 0 L61 39 L100 50 L61 61 L50 100 L39 61 L0 50 L39 39 Z';

// a = 環繞角度(度)，dist = 離中心距離，size = 像素，d = 延遲
const SHARDS = [
  { a: -90, dist: 250, size: 76, color: '#FFD93D', d: 0 },
  { a: -30, dist: 300, size: 56, color: '#000', d: 0.06 },
  { a: 30, dist: 280, size: 64, color: '#FF6B6B', d: 0.04 },
  { a: 90, dist: 230, size: 50, color: '#FFD93D', d: 0.08 },
  { a: 150, dist: 290, size: 60, color: '#000', d: 0.05 },
  { a: 210, dist: 270, size: 70, color: '#FF6B6B', d: 0.02 },
  { a: -150, dist: 240, size: 52, color: '#FFD93D', d: 0.07 },
  { a: -60, dist: 200, size: 40, color: '#000', d: 0.1 },
];

// fade=true：碎片在 burst 後繼續可見 ~0.6s、最後 ~0.8s 自身 opacity 飛散到 0（呼應 ImpactDust 風格）。
export function StarburstShards({ active = false, fade = false }) {
  return (
    <div style={{ position: 'absolute', left: '50%', top: '50%', width: 0, height: 0 }}>
      {SHARDS.map((s, i) => {
        const rad = (s.a * Math.PI) / 180;
        const dx = Math.cos(rad) * s.dist;
        const dy = Math.sin(rad) * s.dist;
        const delay = active ? 0.08 + s.d : 0;
        return (
          <motion.svg
            key={i}
            width={s.size}
            height={s.size}
            viewBox="0 0 100 100"
            initial={false}
            animate={active
              ? {
                  x: dx - s.size / 2,
                  y: dy - s.size / 2,
                  scale: [0, 1.3, 1],
                  opacity: fade ? [1, 1, 0] : 1,
                  rotate: s.a,
                }
              : { x: -s.size / 2, y: -s.size / 2, scale: 0, opacity: 0, rotate: 0 }}
            transition={fade
              ? {
                  default: { duration: 0.45, ease: [0.34, 1.56, 0.64, 1], delay },
                  opacity: { duration: 1.4, times: [0, 0.45, 1], ease: 'easeOut', delay },
                }
              : { duration: 0.45, ease: [0.34, 1.56, 0.64, 1], delay }}
            style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible' }}
          >
            <path d={STAR} fill={s.color} stroke="#000" strokeWidth={6} strokeLinejoin="round" />
          </motion.svg>
        );
      })}
    </div>
  );
}
