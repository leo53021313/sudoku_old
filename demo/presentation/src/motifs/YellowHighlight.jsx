// Yellow highlight box for keyword emphasis — supports mask-reveal animation
import { motion } from 'motion/react';

export function YellowHighlight({ active = false, children, padding = '4px 12px', className = '', style = {} }) {
  return (
    <motion.span
      initial={false}
      // 展開後用四邊各擴 12px 的負值 inset：否則 inset(0 0 0 0) 貼著 border-box，
      // 會把溢出框外的 box-shadow（右下 4px）裁掉。
      animate={active ? { clipPath: 'inset(-12px)' } : { clipPath: 'inset(0px 100% 0px 0px)' }}
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
