// Yellow outer ring + red inner ring stamp — per outline-visual.md §7
import { motion } from 'motion/react';

export function BoomDoubleRing({ active = false, size = 320, style = {} }) {
  const animate = active ? { scale: 1, opacity: 1 } : { scale: 0, opacity: 0 };
  return (
    <div style={{ position: 'relative', width: size, height: size, ...style }}>
      <motion.div
        initial={false}
        animate={animate}
        transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1], delay: 0.08 }}
        style={{
          position: 'absolute', inset: 0,
          border: '8px solid #FFD93D',
          borderRadius: '50%',
          boxShadow: '8px 8px 0 0 #000',
        }}
      />
      <motion.div
        initial={false}
        animate={animate}
        transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1], delay: 0.12 }}
        style={{
          position: 'absolute', inset: '20%',
          border: '8px solid #FF6B6B',
          borderRadius: '50%',
          boxShadow: '6px 6px 0 0 #000',
        }}
      />
    </div>
  );
}
