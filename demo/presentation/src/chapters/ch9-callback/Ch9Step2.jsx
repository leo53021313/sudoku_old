import { motion } from 'motion/react';

export default function Ch9Step2() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 16,
    }}>
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0, letterSpacing: '0.05em' }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1, letterSpacing: '0em' }}
        transition={{ duration: 1.2, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '5rem', textAlign: 'center', lineHeight: 1.3,
          color: '#FF6B6B',
        }}
      >
        這兩個月
        <br/>
        我不只在訓練 AI
      </motion.div>

      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '32px 64px', border: '8px solid #000', boxShadow: '20px 20px 0 0 #000',
          fontWeight: 900, fontSize: '6rem', rotate: -2, lineHeight: 1,
        }}
      >
        AI · 也在訓練我
      </motion.div>
    </main>
  );
}
