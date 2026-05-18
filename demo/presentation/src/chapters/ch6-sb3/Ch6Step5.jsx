import { motion } from 'motion/react';

export default function Ch6Step5() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      gap: 64, fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* 新女生 sticker grayscale fade */}
      <motion.div
        initial={{ filter: 'grayscale(0)' }}
        animate={{ filter: 'grayscale(1)', opacity: 0.5 }}
        transition={{ duration: 1.0 }}
        style={{
          background: '#FFB6C1', color: '#000',
          padding: '24px 40px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          fontWeight: 900, fontSize: '1.5rem', transform: 'rotate(-4deg)', lineHeight: 1.3,
          textAlign: 'center',
        }}
      >
        剛認識的<br/>新女生 ✨
      </motion.div>

      {/* Curve with red flat-section highlight band */}
      <div style={{ position: 'relative' }}>
        <svg viewBox="0 0 400 240" width="500" height="300" style={{ overflow: 'visible' }}>
          <line x1="20" y1="220" x2="380" y2="220" stroke="#000" strokeWidth="3" />
          <line x1="20" y1="220" x2="20" y2="20" stroke="#000" strokeWidth="3" />

          {/* flat-section red band */}
          <motion.rect
            x="240" y="45" width="140" height="50" fill="#FF6B6B"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.4 }}
            transition={{ duration: 0.5 }}
          />

          <path
            d="M 20 200 L 80 180 L 140 140 L 200 90 L 260 50 L 380 50"
            fill="none" stroke="#000" strokeWidth="4" strokeLinecap="square"
          />
        </svg>

        <motion.div
          initial={{ x: 40, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          style={{
            position: 'absolute', top: '20%', right: -180,
            fontWeight: 900, fontSize: '1.5rem', maxWidth: 200, lineHeight: 1.3,
          }}
        >
          拿固定分數 ·<br/>
          <span style={{ background: '#FF6B6B', color: '#FFF', padding: '2px 12px', border: '3px solid #000' }}>
            不思進取
          </span>
        </motion.div>
      </div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.8 }}
        style={{
          position: 'absolute', bottom: 80,
          fontWeight: 700, fontSize: '1.25rem', color: '#666',
        }}
      >
        一直沒辦法完整解出一道題
      </motion.div>
    </main>
  );
}
