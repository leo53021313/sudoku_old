import { motion } from 'motion/react';

export default function Ch9Step4() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        style={{ fontWeight: 900, fontSize: '3rem', textAlign: 'center' }}
      >
        AI 在<span style={{ background: '#FFD93D', padding: '0 16px', border: '4px solid #000' }}>模仿</span>人類
      </motion.div>

      {/* Plane left + arrow ← + bird right */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 48, marginTop: 32 }}>
        <motion.div
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          style={{ fontSize: 200 }}
        >
          ✈️
        </motion.div>

        <motion.svg
          width="120" height="40" viewBox="0 0 120 40"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.6, delay: 0.7 }}
          style={{ overflow: 'visible' }}
        >
          <motion.path
            d="M 10 20 L 20 10 L 10 20 L 110 20 L 100 30 L 110 20 L 100 10"
            fill="none" stroke="#000" strokeWidth="6" strokeLinecap="square"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.6, delay: 0.7 }}
          />
        </motion.svg>

        <motion.div
          initial={{ x: 100, opacity: 0 }}
          animate={{ x: 0, opacity: 1, y: [0, -6, 0] }}
          transition={{
            x: { duration: 0.5, delay: 0.4 },
            opacity: { duration: 0.5, delay: 0.4 },
            y: { duration: 1.2, repeat: Infinity, ease: 'easeInOut', delay: 1 },
          }}
          style={{ fontSize: 200 }}
        >
          🐦
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.2 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', color: '#666', textAlign: 'center' }}
      >
        就像飛機 · 是人類模仿鳥類才造出來
      </motion.div>
    </main>
  );
}
