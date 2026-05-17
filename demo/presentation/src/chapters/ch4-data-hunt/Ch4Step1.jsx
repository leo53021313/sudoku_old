import { motion } from 'motion/react';

export default function Ch4Step1() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <motion.div
        initial={{ scale: 0, opacity: 0, rotate: 0 }}
        animate={{ scale: 1, opacity: 1, rotate: 2 }}
        transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FFD93D', color: '#000',
          padding: '24px 56px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          fontWeight: 900, fontSize: '4rem',
        }}
      >
        Kaggle
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        style={{
          marginTop: 32, fontWeight: 700, fontSize: '1.75rem',
          textAlign: 'center', maxWidth: 800,
        }}
      >
        題目+完整答案 整理好的資料集
      </motion.div>

      {/* 3 data cards stagger */}
      <div style={{ marginTop: 48, display: 'flex', gap: 16 }}>
        {[0, 1, 2].map(i => (
          <motion.div
            key={i}
            initial={{ y: 30, scale: 0.8, opacity: 0 }}
            animate={{ y: 0, scale: 1, opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.9 + i * 0.1, ease: [0.34, 1.56, 0.64, 1] }}
            style={{
              width: 140, height: 100, background: '#FFFFFF',
              border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
              padding: 16, fontWeight: 700, fontSize: 14,
              transform: `rotate(${[-3, 1, 4][i]}deg)`,
            }}
          >
            dataset #{i + 1}
            <div style={{ marginTop: 12, color: '#999' }}>n=10k</div>
          </motion.div>
        ))}
      </div>

      {/* 但問題來了 — 紅叉叉 burst climax */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: [0, 1.2, 1], opacity: 1 }}
        transition={{ duration: 0.6, delay: 1.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', inset: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          pointerEvents: 'none',
        }}
      >
        <div style={{
          fontWeight: 900, fontSize: '8rem', color: '#FF6B6B',
          WebkitTextStroke: '4px black', textShadow: '12px 12px 0 #000',
          rotate: -5,
        }}>
          ✗ 但問題來了
        </div>
      </motion.div>
    </main>
  );
}
