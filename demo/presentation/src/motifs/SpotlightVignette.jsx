// Radial gradient overlay with multiply blend — per outline-visual.md §7 / §8 climax G
import { motion } from 'motion/react';

export function SpotlightVignette({ active = false, centerX = '50%', centerY = '50%' }) {
  return (
    <motion.div
      aria-hidden="true"
      initial={false}
      animate={{ opacity: active ? 1 : 0 }}
      transition={{ duration: 0.5 }}
      style={{
        position: 'fixed', inset: 0, zIndex: 50, pointerEvents: 'none',
        background: `radial-gradient(circle at ${centerX} ${centerY}, transparent 25%, rgba(0,0,0,0.6) 100%)`,
        mixBlendMode: 'multiply',
      }}
    />
  );
}
