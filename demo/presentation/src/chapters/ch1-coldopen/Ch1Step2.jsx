import { motion } from 'motion/react';

export default function Ch1Step2() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      gap: 32, fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Psychology degree card — slide in from bottom-right with overshoot */}
      <motion.div
        initial={{ x: 200, y: 80, scale: 0.8, opacity: 0 }}
        animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FFFFFF', color: '#000',
          border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          padding: '48px 64px', rotate: -2,
          fontWeight: 900, fontSize: '3.75rem', lineHeight: 1.1,
          textAlign: 'center',
        }}
      >
        心 理 學 系
        <div style={{ fontSize: '1.875rem', marginTop: 12, color: '#000' }}>· 畢業</div>
      </motion.div>

      {/* Red arrow drawn by stroke-dasharray animation */}
      <motion.svg
        width="120" height="40" viewBox="0 0 120 40"
        style={{ overflow: 'visible' }}
      >
        <motion.path
          d="M 10 20 L 100 20 M 90 10 L 100 20 L 90 30"
          fill="none" stroke="#FF6B6B" strokeWidth="6" strokeLinecap="square" strokeLinejoin="miter"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.6, delay: 0.6, ease: 'easeOut' }}
        />
      </motion.svg>

      {/* 敬請期待 yellow stamp — scales in from 0 */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4, delay: 1.1, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FFD93D', color: '#000',
          border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          padding: '32px 48px', rotate: 3,
          fontWeight: 900, fontSize: '2.25rem',
        }}
      >
        敬請期待
      </motion.div>
    </main>
  );
}
