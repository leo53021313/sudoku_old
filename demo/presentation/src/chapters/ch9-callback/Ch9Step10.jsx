import { motion } from 'motion/react';
import { useEffect, useState } from 'react';

export default function Ch9Step10() {
  const [phase, setPhase] = useState(1);

  useEffect(() => {
    const t = setTimeout(() => setPhase(2), 9000);
    return () => clearTimeout(t);
  }, []);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 24,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        style={{ fontWeight: 900, fontSize: '2rem' }}
      >
        我真的是一個 <span style={{ background: '#C4B5FD', padding: '0 16px', border: '4px solid #000' }}>極度的 I 人</span>
      </motion.div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 48, marginTop: 24 }}>
        {/* MBTI Pie chart — phase 1 full 100% I, phase 2 shrinks to side */}
        <motion.svg
          animate={{ width: phase === 1 ? 240 : 120, height: phase === 1 ? 240 : 120 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          viewBox="0 0 100 100"
          style={{ flex: '0 0 auto' }}
        >
          <circle cx="50" cy="50" r="45" fill="#FFFDF5" stroke="#000" strokeWidth="6" />
          {phase === 1 ? (
            <motion.circle
              cx="50" cy="50" r="45" fill="#C4B5FD" stroke="#000" strokeWidth="6"
              initial={{ strokeDasharray: '0 283', strokeDashoffset: 0 }}
              animate={{ strokeDasharray: '283 0', strokeDashoffset: 0 }}
              transition={{ duration: 1.5 }}
              style={{ transformOrigin: 'center', transform: 'rotate(-90deg)' }}
            />
          ) : (
            // Phase 2: 30% I (purple), 70% E? — represent as partial pie
            <path d="M 50 5 A 45 45 0 0 1 90 65 L 50 50 Z" fill="#C4B5FD" stroke="#000" strokeWidth="6" />
          )}
          <text x="50" y="55" textAnchor="middle" fontWeight="900" fontSize="24" fontFamily="Space Grotesk">
            I {phase === 1 ? '100%' : '30%'}
          </text>
        </motion.svg>

        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 1.6, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            background: '#C4B5FD', color: '#000',
            padding: '24px 40px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            fontWeight: 900, fontSize: 28, rotate: -3,
          }}
        >
          極度 I 人
        </motion.div>

        {/* Phase 2 only: 業務工作 sticker + I→E bar */}
        {phase === 2 && (
          <>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
              style={{
                background: '#FFD93D', color: '#000',
                padding: '20px 36px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
                fontWeight: 900, fontSize: 28, rotate: 2,
              }}
            >
              業務工作
            </motion.div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <div style={{ position: 'relative', width: 280, height: 40, background: '#FFFDF5', border: '4px solid #000' }}>
                <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: '30%', background: '#C4B5FD' }} />
                <div style={{ position: 'absolute', right: 0, top: 0, bottom: 0, width: '40%', background: '#FF6B6B' }} />
                <motion.div
                  initial={{ left: '0%' }}
                  animate={{ left: '60%' }}
                  transition={{ duration: 4, ease: 'easeInOut' }}
                  style={{
                    position: 'absolute', top: -4, width: 12, height: 48,
                    background: '#000', border: '2px solid #FFFDF5',
                  }}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700, fontSize: 14 }}>
                <span>I 0%</span><span>E 100%</span>
              </div>
            </div>
          </>
        )}
      </div>

      {phase === 1 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 2.0 }}
          style={{ fontWeight: 700, fontSize: '1.5rem' }}
        >
          <span style={{ background: '#FFD93D', padding: '2px 12px', border: '4px solid #000' }}>明明我很 E</span>
        </motion.div>
      )}

      {phase === 2 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          style={{ fontWeight: 700, fontSize: '1.25rem', color: '#666', textAlign: 'center', marginTop: 16 }}
        >
          天天逼自己跟陌生人講話 · 才慢慢變得比較 E
        </motion.div>
      )}
    </main>
  );
}
