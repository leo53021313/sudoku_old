import { motion } from 'motion/react';

export default function Ch8Step5() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
    }}>
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.8 }}
        style={{ fontWeight: 900, fontSize: '5rem' }}
      >
        光講不夠看
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        style={{ fontWeight: 700, fontSize: '2rem', color: '#000' }}
      >
        給大家看一下 AI 即時解數獨的題目
      </motion.div>

      <motion.svg
        width="80" height="120" viewBox="0 0 80 120"
        animate={{ y: [0, 16, 0] }}
        transition={{ duration: 1.2, ease: 'easeInOut', repeat: Infinity }}
      >
        <motion.path
          d="M 40 10 L 40 90 M 10 70 L 40 100 L 70 70"
          fill="none" stroke="#000" strokeWidth="8" strokeLinecap="square" strokeLinejoin="miter"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.6, delay: 1.0 }}
        />
      </motion.svg>
    </main>
  );
}
