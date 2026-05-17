import { motion } from 'motion/react';

export default function Ch1Step1() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
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

      {/* 期中報告 badge top-left */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', top: 48, left: 48,
          background: '#FFD93D', color: '#000',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          padding: '12px 24px', rotate: -3,
          fontWeight: 900, fontSize: 18,
        }}
      >
        期中報告
      </motion.div>

      {/* 心虛 hero sticker — outer wrapper handles entrance scale/opacity,
          inner does infinite float micro-motion. Nested so the two compose. */}
      <motion.div
        initial={{ scale: 0.7, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ display: 'inline-block', rotate: -3 }}
      >
        <motion.div
          animate={{ y: [0, -4, 0, 4, 0] }}
          transition={{ duration: 4, ease: 'easeInOut', repeat: Infinity, delay: 1 }}
          style={{
            background: '#FF6B6B', color: '#FFFDF5',
            border: '6px solid #000', boxShadow: '16px 16px 0 0 #000',
            padding: '64px 96px',
            fontWeight: 900, fontSize: '8rem', letterSpacing: '0.1em',
          }}
        >
          心 虛
        </motion.div>
      </motion.div>

      {/* Caption — mask-reveal from left */}
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.8, delay: 1.2, ease: 'easeOut' }}
        style={{
          marginTop: 48,
          fontSize: 24, fontWeight: 700, color: '#000',
          maxWidth: 720, textAlign: 'center', lineHeight: 1.4,
        }}
      >
        報告太不正經、請各位同學和老師多包涵
      </motion.div>
    </main>
  );
}
