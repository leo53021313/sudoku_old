import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { AiSticker } from '../../components/AiSticker.jsx';

export default function Ch2Step4() {
  // Stamp lands at delay 1.8s. Aftermath = slow ±1° hover starts 500ms after stamp settles.
  const [aftermath, setAftermath] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setAftermath(true), 1800 + 500 + 500);
    return () => clearTimeout(t);
  }, []);

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
        機器學習 · ③/3
      </motion.div>

      <motion.div
        initial={{ clipPath: 'inset(0px 100% 0px 0px)', opacity: 0 }}
        animate={{ clipPath: 'inset(-24px)', opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.5, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '5rem', lineHeight: 1.05,
          letterSpacing: '-0.04em', display: 'flex', alignItems: 'baseline', gap: 16,
        }}
      >
        <span style={{
          background: '#FF6B6B', color: '#FFFDF5', padding: '0 20px',
          border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
        }}>RL</span>
        <span style={{ fontSize: '3rem', color: '#666' }}>· reinforcement learning</span>
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
          background: '#FFD93D', padding: '4px 16px',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          marginLeft: 8,
        }}>試錯加獎懲</span>
      </motion.div>

      {/* AlphaGo red stamp drops in last (climax, preserved)
          AFTERMATH: 500ms after stamp settles, slow ±1° infinite hover. */}
      <motion.div
        initial={{ y: -200, scale: 0, opacity: 0, rotate: -8 }}
        animate={
          aftermath
            ? { y: 0, scale: 1, opacity: 1, rotate: [-3, -1, -3] }
            : { y: 0, scale: 1, opacity: 1, rotate: -2 }
        }
        transition={
          aftermath
            ? { duration: 4, repeat: Infinity, ease: 'linear' }
            : { duration: 0.5, delay: 1.8, ease: [0.34, 1.56, 0.64, 1] }
        }
        style={{
          position: 'absolute', bottom: '20%', right: 96,
          background: '#FF6B6B', color: '#FFFDF5',
          border: '6px solid #000',
          boxShadow: aftermath ? '8px 8px 0 0 #000' : '12px 12px 0 0 #000',
          padding: '20px 36px',
          fontWeight: 900, fontSize: 32,
          transition: 'box-shadow 0.35s cubic-bezier(0.22, 1, 0.36, 1)',
        }}
      >
        AlphaGo · 打敗世界圍棋王
      </motion.div>

      {/* Dog handshake AI illustration (replaces 🐕 ↔ 🤝 emoji) */}
      <motion.div
        initial={{ opacity: 0, x: 60 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 1.4 }}
        style={{
          position: 'absolute', left: 64, top: '60%',
        }}
      >
        <AiSticker
          src="/images/ai/ch2/dog-handshake.png"
          alt="訓練狗握手"
          width={420}
          rotation={-3}
          shadow={8}
        />
      </motion.div>
    </main>
  );
}
