// Red stamp drops from above with overshoot bounce + shadow burst
import { motion } from 'motion/react';

export function RedStamp({ active = false, children, rotation = -3, size = 'large', shadow = '16px 16px 0 0 #000' }) {
  const fontSize = size === 'large' ? '5rem' : size === 'medium' ? '3rem' : '2rem';
  return (
    <motion.div
      initial={false}
      animate={active ? { y: 0, scale: 1, opacity: 1 } : { y: -200, scale: 0, opacity: 0 }}
      transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
      style={{
        display: 'inline-block',
        background: '#FF6B6B',
        color: '#FFFDF5',
        border: '6px solid #000',
        boxShadow: shadow,
        padding: '24px 48px',
        // Motion v12 can't merge CSS transform string with animated y/scale/opacity — use separate rotate prop.
        rotate: rotation,
        fontFamily: 'Space Grotesk', fontWeight: 900, fontSize,
      }}
    >
      {children}
    </motion.div>
  );
}
