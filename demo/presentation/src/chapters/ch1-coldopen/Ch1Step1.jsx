import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch1Step1() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
    }}>
      {/* Black → cream fade overlay (one-shot when this step mounts) */}
      <motion.div
        aria-hidden="true"
        initial={{ opacity: 1 }}
        animate={{ opacity: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{
          position: 'fixed', inset: 0, zIndex: 70,
          background: '#000', pointerEvents: 'none',
        }}
      />

      {/* 資展會 badge top-left (absolute inside SafeArea is allowed for fixed-corner chrome) */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ position: 'absolute', top: 0, left: 0 }}
      >
        <Sticker variant="kicker" bg="secondary" rotation={-3}>資展會 2026</Sticker>
      </motion.div>

      {/* 期中報告 hero */}
      <motion.div
        initial={{ scale: 0.7, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ display: 'inline-block', transform: 'rotate(-2deg)' }}
      >
        <Sticker variant="hub-mega" bg="accent" textColor="cream" style={{ fontSize: '7rem', padding: '56px 96px', letterSpacing: '0.08em', lineHeight: 1 }}>
          期中報告
        </Sticker>
      </motion.div>

      {/* presented by [presenter name] — mask-reveal */}
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.8, delay: 1.2, ease: 'easeOut' }}
        style={{
          marginTop: 48,
          fontSize: 28, fontWeight: 700, color: '#000',
          textAlign: 'center', letterSpacing: '0.05em',
        }}
      >
        presented by{' '}
        <span style={{
          background: '#000', color: '#FFFDF5',
          padding: '4px 20px', marginLeft: 8,
          fontWeight: 900,
        }}>
          王文杰
        </span>
      </motion.div>
    </div>
  );
}
