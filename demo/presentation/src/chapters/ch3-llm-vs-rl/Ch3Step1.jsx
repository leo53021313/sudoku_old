import { motion } from 'motion/react';

export default function Ch3Step1() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      fontFamily: 'Space Grotesk', overflow: 'hidden',
    }}>
      {/* Left column wipe-in from left, 60% width */}
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)' }}
        animate={{ clipPath: 'inset(0 0 0 0)' }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        style={{
          position: 'absolute', top: 0, bottom: 0, left: 0, width: '60%',
          background: 'transparent', padding: 64,
          display: 'flex', flexDirection: 'column',
          justifyContent: 'center', alignItems: 'center', textAlign: 'center',
        }}
      >
        {/* Background scrolling text grid (subtle low-density) */}
        <div
          aria-hidden="true"
          style={{
            position: 'absolute', inset: 0, overflow: 'hidden',
            opacity: 0.08, fontSize: 14, fontFamily: 'monospace',
            lineHeight: 1.6, padding: 12, color: '#000',
          }}
        >
          {Array.from({ length: 50 }).map((_, i) => (
            <div key={i}>The quick brown fox jumps over the lazy dog 一二三四 ABC </div>
          ))}
        </div>

        {/* "LLM" hero with overshoot stamp */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            fontWeight: 900, fontSize: '10rem', lineHeight: 1, color: '#000',
            position: 'relative', zIndex: 1,
          }}
        >
          LLM
        </motion.div>

        {/* Purple sub-label */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 1.0 }}
          style={{
            background: '#C4B5FD', color: '#000',
            padding: '8px 20px', alignSelf: 'center',
            border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
            fontWeight: 900, fontSize: 22, marginTop: 16, rotate: -2,
            position: 'relative', zIndex: 1,
          }}
        >
          supervised + RLHF
        </motion.div>

        {/* Tagline */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 1.4 }}
          style={{
            marginTop: 32, fontWeight: 700, fontSize: '1.5rem', maxWidth: 600,
            position: 'relative', zIndex: 1,
          }}
        >
          把整個人類網路寫過的東西全部讀一遍
        </motion.div>
      </motion.div>
    </main>
  );
}
