import { motion } from 'motion/react';

export default function Ch2Step2() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{
          background: '#000', color: '#FFFDF5',
          padding: '12px 28px',
          fontWeight: 900, fontSize: 18, letterSpacing: '0.1em',
          marginBottom: 48,
        }}
      >
        機器學習 · ②/3
      </motion.div>

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.5, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '7rem', lineHeight: 1.05,
          letterSpacing: '-0.04em',
        }}
      >
        unsupervised
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0 }}
        style={{
          marginTop: 24,
          fontWeight: 700, fontSize: '2rem', color: '#000',
        }}
      >
        白話：<span style={{
          background: '#C4B5FD', padding: '4px 16px',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          marginLeft: 8,
        }}>自己分類整理</span>
      </motion.div>

      {/* Clothes piles: one messy → 3 sorted */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.4 }}
        style={{
          position: 'absolute', right: 64, top: '50%', transform: 'translateY(-50%)',
          display: 'flex', alignItems: 'center', gap: 24,
        }}
      >
        <div style={{ fontWeight: 900, fontSize: 18, textAlign: 'center' }}>
          <div style={{
            width: 80, height: 80, background: '#999',
            border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: '#FFF', marginBottom: 8,
          }}>👕👖👔</div>
          一堆
        </div>
        <div style={{ fontWeight: 900, fontSize: 24 }}>→</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ background: '#FF6B6B', border: '3px solid #000', padding: 4, fontWeight: 900, fontSize: 12, textAlign: 'center' }}>紅</div>
          <div style={{ background: '#FFD93D', border: '3px solid #000', padding: 4, fontWeight: 900, fontSize: 12, textAlign: 'center' }}>黃</div>
          <div style={{ background: '#C4B5FD', border: '3px solid #000', padding: 4, fontWeight: 900, fontSize: 12, textAlign: 'center' }}>紫</div>
        </div>
      </motion.div>
    </main>
  );
}
