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

      {/* Title hero — outer wrapper handles entrance scale/opacity,
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
            padding: '48px 80px', textAlign: 'center',
            fontWeight: 900, fontSize: '5.5rem', letterSpacing: '0.05em', lineHeight: 1.1,
          }}
        >
          2026 資展會<br />期中報告
        </motion.div>
      </motion.div>

      {/* Presenter line — mask-reveal from left */}
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.8, delay: 1.2, ease: 'easeOut' }}
        style={{
          marginTop: 48,
          fontSize: 28, fontWeight: 700, color: '#000',
          maxWidth: 720, textAlign: 'center', lineHeight: 1.4,
        }}
      >
        Presented by 王文杰
      </motion.div>
    </main>
  );
}
