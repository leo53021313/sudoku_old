import { motion } from 'motion/react';

export default function Ch6Step2() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      gap: 64, fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Left: Python toolbox sticker */}
      <motion.div
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        style={{
          background: '#C4B5FD', color: '#000',
          padding: '20px 36px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          fontWeight: 900, fontSize: 24, rotate: -3, maxWidth: 360, lineHeight: 1.3,
        }}
      >
        社群現成<br/>Python 工具箱
      </motion.div>

      {/* Right: scoring rule card */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FFFFFF', color: '#000',
          padding: '32px 48px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          fontWeight: 900, fontSize: '2rem', textAlign: 'center', lineHeight: 1.3,
        }}
      >
        只要他<br/>
        <span style={{ display: 'inline-block', margin: '12px 0', background: '#FFD93D', padding: '4px 16px', border: '4px solid #000', boxShadow: '4px 4px 0 0 #000' }}>填對一格</span>
        <br/>就給分數
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, delay: 1.0 }}
          style={{ marginTop: 16, fontSize: '3rem', color: '#FF6B6B' }}
        >+1</motion.div>
      </motion.div>
    </main>
  );
}
