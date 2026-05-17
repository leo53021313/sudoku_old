// 4 or 8 inkblot paths radiating with stagger — per outline-visual.md §7 / §8 climax E
import { motion } from 'motion/react';

const BLOBS = [
  'M0,0 C8,-12 22,-8 28,4 C32,12 18,24 6,18 Z',
  'M0,0 C-10,-6 -4,-22 8,-16 C18,-10 14,8 4,12 Z',
  'M0,0 C12,-4 24,12 14,18 C2,22 -8,8 -2,-2 Z',
  'M0,0 C-14,-8 -4,18 6,14 C18,8 8,-12 0,-6 Z',
  'M0,0 C10,8 0,22 -10,16 C-18,12 -10,-4 0,-4 Z',
  'M0,0 C-8,6 -22,-2 -16,-14 C-8,-22 6,-12 4,-2 Z',
  'M0,0 C8,12 -10,20 -16,10 C-22,0 -8,-12 0,-6 Z',
  'M0,0 C16,4 18,-12 6,-18 C-4,-22 -10,-8 -2,-2 Z',
];

export function InkSplatter({ active = false, count = 8, radius = 140, centerX = '50%', centerY = '50%' }) {
  const blobs = BLOBS.slice(0, count);
  return (
    <div aria-hidden="true" style={{
      position: 'absolute', left: centerX, top: centerY,
      width: 0, height: 0, zIndex: 40, pointerEvents: 'none',
    }}>
      {blobs.map((path, i) => {
        const angle = (i / count) * Math.PI * 2;
        const r = radius * (0.6 + 0.4 * ((i * 7) % 5) / 5);
        const x = Math.cos(angle) * r;
        const y = Math.sin(angle) * r;
        return (
          <motion.svg
            key={i}
            initial={false}
            animate={{ scale: active ? 1 : 0, opacity: active ? 1 : 0 }}
            transition={{ duration: 0.3, delay: active ? 0.08 * i : 0, ease: [0.34, 1.56, 0.64, 1] }}
            width="40" height="40" viewBox="-20 -20 40 40"
            // Motion v12 can't merge CSS transform string with `animate.scale` — use separate
            // rotate property and pre-offset left/top by -half-width (40px svg → -20px).
            style={{ position: 'absolute', left: x - 20, top: y - 20, rotate: i * 47 }}
          >
            <path d={path} fill="#000" />
          </motion.svg>
        );
      })}
    </div>
  );
}
