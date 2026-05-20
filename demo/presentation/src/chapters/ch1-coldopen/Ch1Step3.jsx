import { motion } from 'motion/react';

export default function Ch1Step3() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Kicker: 期中主題 */}
      <motion.div
        initial={{ x: -200, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{
          background: '#000', color: '#FFFDF5',
          padding: '12px 28px',
          fontWeight: 900, fontSize: 20, letterSpacing: '0.1em',
          marginBottom: 48,
        }}
      >
        期中主題
      </motion.div>

      {/* Hero: 訓 練 [AI] 解 數 獨, with red & yellow emphasis boxes */}
      <motion.div
        initial={{ scale: 0.85, letterSpacing: '0.1em', opacity: 0 }}
        animate={{ scale: 1, letterSpacing: '-0.04em', opacity: 1 }}
        transition={{ duration: 0.72, delay: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          fontWeight: 900, fontSize: '6rem', lineHeight: 1.05,
          display: 'flex', alignItems: 'center', gap: 16,
          textAlign: 'center',
        }}
      >
        <span style={{ color: '#000' }}>訓 練</span>
        <span style={{
          background: '#FF6B6B', color: '#FFFDF5',
          border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
          padding: '0 24px', rotate: -2,
        }}>AI</span>
        <span style={{
          background: '#FFD93D', color: '#000',
          border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
          padding: '0 24px', rotate: 2,
        }}>解 數 獨</span>
      </motion.div>

      {/* 4 floating decoratives — 角落動 */}
      <motion.div
        initial={{ x: -120, y: -120, opacity: 0, scale: 0 }}
        animate={{ x: 0, y: 0, opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 1.0, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', top: '12%', left: '8%',
          width: 64, height: 64, background: '#C4B5FD',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          rotate: 8,
        }}
      />
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 12, ease: 'linear', repeat: Infinity }}
        style={{
          position: 'absolute', top: '14%', right: '10%',
          width: 64, height: 64,
        }}
      >
        <motion.svg
          width="64" height="64" viewBox="0 0 64 64"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 1.1, ease: [0.34, 1.56, 0.64, 1] }}
        >
          <polygon points="32,4 38,24 60,24 42,36 50,58 32,46 14,58 22,36 4,24 26,24"
            fill="#FFD93D" stroke="#000" strokeWidth="3" strokeLinejoin="miter" />
        </motion.svg>
      </motion.div>
      <motion.div
        initial={{ scale: 0, opacity: 0, x: -120, y: 120 }}
        animate={{ scale: 1, opacity: 1, x: 0, y: 0 }}
        transition={{ duration: 0.5, delay: 1.2, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: '14%', left: '10%',
          width: 64, height: 64, borderRadius: '50%', background: '#FF6B6B',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
        }}
      />
      <motion.div
        initial={{ scale: 0, opacity: 0, x: 120, y: 120 }}
        animate={{ scale: 1, opacity: 1, x: 0, y: 0 }}
        transition={{ duration: 0.5, delay: 1.3, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: '12%', right: '8%',
          width: 64, height: 64,
          border: '4px solid #000',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontWeight: 900, fontSize: 36, rotate: -8,
          background: 'transparent', color: '#000',
        }}
      >
        ?
      </motion.div>
    </main>
  );
}
