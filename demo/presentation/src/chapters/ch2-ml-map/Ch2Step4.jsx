import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch2Step4() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{ marginBottom: 48 }}
      >
        <Sticker variant="kicker" bg="ink" textColor="cream">機器學習 · ③/3</Sticker>
      </motion.div>

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.5, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '7rem', lineHeight: 1.05,
          letterSpacing: '-0.04em', display: 'flex', alignItems: 'baseline', gap: 16,
        }}
      >
        <Sticker variant="hub-lg" bg="accent" textColor="cream">RL</Sticker>
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
        白話：<Sticker variant="sat-lg" bg="secondary" style={{ marginLeft: 8 }}>試錯加獎懲</Sticker>
      </motion.div>

      {/* AlphaGo red stamp drops in last (climax) — outer choreography untouched */}
      <motion.div
        initial={{ y: -200, scale: 0, opacity: 0, rotate: -8 }}
        animate={{ y: 0, scale: 1, opacity: 1, rotate: -2 }}
        transition={{ duration: 0.5, delay: 1.8, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ position: 'absolute', bottom: '20%', right: 96 }}
      >
        <Sticker variant="sat-lg" bg="accent" textColor="cream">
          AlphaGo · 打敗世界圍棋王
        </Sticker>
      </motion.div>

      {/* Dog handshake placeholder text */}
      <motion.div
        initial={{ opacity: 0, x: 60 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 1.4 }}
        style={{
          position: 'absolute', left: 64, top: '60%',
          fontSize: 64, fontWeight: 900,
        }}
      >
        🐕 ↔ 🤝
      </motion.div>
    </div>
  );
}
