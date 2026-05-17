// Halftone dots burst from center — per outline-visual.md §7 / §8 climax B
import { motion } from 'motion/react';

export function HalftoneBurst({ active = false, size = 600, centerX = '50%', centerY = '50%' }) {
  return (
    <motion.div
      aria-hidden="true"
      initial={false}
      animate={{
        scale: active ? 3 : 0,
        opacity: active ? [1, 1, 0] : 0,
      }}
      transition={{ duration: 0.5, ease: 'easeOut', times: active ? [0, 0.2, 1] : [0, 1] }}
      style={{
        position: 'absolute', left: centerX, top: centerY,
        width: size, height: size, marginLeft: -size / 2, marginTop: -size / 2,
        zIndex: 40, pointerEvents: 'none',
        backgroundImage: 'radial-gradient(#000 2px, transparent 2.5px)',
        backgroundSize: '30px 30px',
        mask: 'radial-gradient(circle, #000 0%, #000 70%, transparent 100%)',
        WebkitMask: 'radial-gradient(circle, #000 0%, #000 70%, transparent 100%)',
      }}
    />
  );
}
