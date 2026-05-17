import { motion } from 'motion/react';

export default function Ch2Step1() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Kicker top */}
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
        機器學習 · ①/3
      </motion.div>

      {/* Big "supervised" mask-reveal */}
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.5, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '7rem', lineHeight: 1.05,
          letterSpacing: '-0.04em',
        }}
      >
        supervised
      </motion.div>

      {/* Subtitle: 白話 */}
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
          background: '#FFD93D', padding: '4px 16px',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          marginLeft: 8,
        }}>看著答案抄筆記</span>
      </motion.div>

      {/* Right-side text illustration */}
      <motion.div
        initial={{ opacity: 0, x: 60 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 1.4, ease: 'easeOut' }}
        style={{
          position: 'absolute', right: 64, top: '50%', transform: 'translateY(-50%)',
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12,
        }}
      >
        <div style={{
          background: '#FFFFFF', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          padding: '12px 20px', fontWeight: 900, fontSize: 16,
        }}>老師</div>
        <div style={{ fontWeight: 900, fontSize: 20 }}>↓</div>
        <div style={{
          background: '#FFD93D', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          padding: '12px 20px', fontWeight: 900, fontSize: 16,
        }}>題目 + 答案</div>
        <div style={{ fontWeight: 900, fontSize: 20 }}>↓</div>
        <div style={{
          background: '#C4B5FD', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          padding: '12px 20px', fontWeight: 900, fontSize: 16,
        }}>學生硬背</div>
      </motion.div>
    </main>
  );
}
