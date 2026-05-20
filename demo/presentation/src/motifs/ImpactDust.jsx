// 衝擊塵爆：印章從天砸下落地瞬間，底部四散黑色碎塊。
// 搭配印章 y 軸墜落 overshoot 使用，營造物理打擊感。
import { motion } from 'motion/react';

// 從落點向外飛散的碎塊（x/y = 終點位移，s = 邊長，d = 額外延遲）
const CHUNKS = [
  { x: -260, y: 30, s: 22, d: 0 },
  { x: -150, y: 70, s: 14, d: 0.04 },
  { x: -80, y: 96, s: 10, d: 0.02 },
  { x: 90, y: 92, s: 12, d: 0.03 },
  { x: 170, y: 64, s: 16, d: 0.05 },
  { x: 268, y: 24, s: 20, d: 0.01 },
  { x: -210, y: -34, s: 12, d: 0.06 },
  { x: 220, y: -40, s: 14, d: 0.05 },
];

export function ImpactDust({ active = false }) {
  return (
    <div style={{ position: 'absolute', left: '50%', top: '78%', width: 0, height: 0, zIndex: -1 }}>
      {CHUNKS.map((c, i) => (
        <motion.div
          key={i}
          initial={false}
          animate={active
            ? { x: c.x, y: c.y, opacity: [1, 1, 0], scale: 1, rotate: c.x }
            : { x: 0, y: 0, opacity: 0, scale: 0, rotate: 0 }}
          transition={{ duration: 0.5, ease: 'easeOut', delay: active ? 0.2 + c.d : 0 }}
          style={{
            position: 'absolute',
            width: c.s, height: c.s,
            background: '#000',
            boxShadow: '3px 3px 0 0 rgba(0,0,0,0.4)',
          }}
        />
      ))}
    </div>
  );
}
