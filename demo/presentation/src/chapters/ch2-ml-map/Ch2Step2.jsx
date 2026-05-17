import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch2Step2() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
    }}>
      {/* Kicker top */}
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{ marginBottom: 48 }}
      >
        <Sticker variant="kicker" bg="ink" textColor="cream">機器學習 · ①/3</Sticker>
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
        白話：<Sticker variant="sat-md" bg="secondary" style={{ marginLeft: 8 }}>看著答案抄筆記</Sticker>
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
        <Sticker variant="sat-md" bg="cream">老師</Sticker>
        <div style={{ fontWeight: 900, fontSize: 20 }}>↓</div>
        <Sticker variant="sat-md" bg="secondary">題目 + 答案</Sticker>
        <div style={{ fontWeight: 900, fontSize: 20 }}>↓</div>
        <Sticker variant="sat-md" bg="muted">學生硬背</Sticker>
      </motion.div>
    </div>
  );
}
