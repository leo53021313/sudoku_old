import { motion } from 'motion/react';

export default function Ch1Step2() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      gap: 32, fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Background card — slide in from bottom-right with overshoot */}
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
        <div style={{
          fontSize: '1.5rem', letterSpacing: '0.3em', marginBottom: 20,
          color: '#FF6B6B',
        }}>背 景</div>
        心 理 學 系
        <div style={{ fontSize: '1.875rem', marginTop: 12, color: '#000' }}>· 畢業</div>
      </motion.div>
    </main>
  );
}
