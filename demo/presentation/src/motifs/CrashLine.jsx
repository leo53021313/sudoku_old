// Cream big-text box + 6px red border + flash + blinking caret placeholder
import { useState, useEffect } from 'react';
import { motion } from 'motion/react';

export function CrashLine({ active = false, filled = false, text = '⋯⋯結果我錯了', width = 720 }) {
  const [flashCount, setFlashCount] = useState(0);

  useEffect(() => {
    if (filled) {
      setFlashCount(2);
      const t1 = setTimeout(() => setFlashCount(1), 200);
      const t2 = setTimeout(() => setFlashCount(0), 400);
      return () => { clearTimeout(t1); clearTimeout(t2); };
    }
  }, [filled]);

  return (
    <motion.div
      initial={false}
      animate={active ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.3 }}
      style={{
        width,
        background: '#FFFDF5',
        border: `6px solid #FF6B6B`,
        boxShadow: filled ? '16px 16px 0 0 #000' : '8px 8px 0 0 #000',
        padding: '32px 48px',
        fontFamily: 'Space Grotesk', fontWeight: 900, fontSize: '3rem',
        textAlign: 'center',
        transform: 'rotate(1deg)',
        transition: 'box-shadow 200ms',
        outline: flashCount === 2 ? '4px solid #FF6B6B' : 'none',
        outlineOffset: 4,
      }}
    >
      {filled ? text : <BlinkingCaret />}
    </motion.div>
  );
}

function BlinkingCaret() {
  return <span style={{ animation: 'caret-blink 1s steps(2) infinite', color: '#FF6B6B' }}>_</span>;
}
