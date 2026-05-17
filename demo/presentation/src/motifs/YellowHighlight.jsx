// Yellow highlight box for keyword emphasis — supports mask-reveal animation
import { motion } from 'motion/react';

export function YellowHighlight({ active = false, children, padding = '4px 12px', className = '', style = {} }) {
  return (
    <motion.span
      initial={false}
      animate={active ? { clipPath: 'inset(0 0 0 0)' } : { clipPath: 'inset(0 100% 0 0)' }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className={className}
      style={{
        display: 'inline-block',
        background: '#FFD93D',
        border: '3px solid #000',
        boxShadow: '4px 4px 0 0 #000',
        padding,
        fontFamily: 'Space Grotesk', fontWeight: 900,
        ...style,
      }}
    >
      {children}
    </motion.span>
  );
}
