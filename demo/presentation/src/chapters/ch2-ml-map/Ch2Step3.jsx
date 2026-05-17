import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch2Step3() {
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
        <Sticker variant="kicker" bg="ink" textColor="cream">機器學習 · ②/3</Sticker>
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
        白話：<Sticker variant="sat-md" bg="muted" style={{ marginLeft: 8 }}>自己分類整理</Sticker>
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
          <Sticker variant="sat-md" bg="muted" style={{ marginBottom: 8 }}>👕👖👔</Sticker>
          <div>一堆</div>
        </div>
        <div style={{ fontWeight: 900, fontSize: 24 }}>→</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <Sticker variant="sat-sm" bg="accent">紅</Sticker>
          <Sticker variant="sat-sm" bg="secondary">黃</Sticker>
          <Sticker variant="sat-sm" bg="muted">紫</Sticker>
        </div>
      </motion.div>
    </div>
  );
}
