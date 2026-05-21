import { motion } from 'motion/react';

export default function Ch3Step2() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      fontFamily: 'Space Grotesk', overflow: 'hidden', display: 'flex',
    }}>
      {/* Left 50% — LLM */}
      <div style={{
        flex: '0 0 50%', padding: 64, position: 'relative',
        display: 'flex', flexDirection: 'column',
        justifyContent: 'center', alignItems: 'center', textAlign: 'center',
      }}>
        {/* LLM slides from Ch3Step1's center position (viewport center, ~10rem)
            to this left-half center at 6rem. Left-half center is at 25vw of the
            viewport; an initial x of +25vw px places the word on viewport center
            so it visually continues from Step 1. Scale 10/6 matches Step 1's
            font-size during the entrance. motion's x/y treat unit strings
            inconsistently across versions, so compute the px value at render. */}
        <motion.div
          initial={{ x: window.innerWidth * 0.25, scale: 10 / 6 }}
          animate={{ x: 0, scale: 1 }}
          transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
          style={{ fontWeight: 900, fontSize: '6rem', color: '#000' }}
        >
          LLM
        </motion.div>
        <motion.div
          initial={{ y: -200, scale: 0, opacity: 0 }}
          animate={{ y: 0, scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.85, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            marginTop: 24, background: '#FF6B6B', color: '#FFFDF5',
            padding: '20px 36px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            fontWeight: 900, fontSize: 32, rotate: -3, alignSelf: 'center',
          }}
        >
          LLM = 模仿
        </motion.div>
      </div>

      {/* Center 6px divider — sits BELOW the VS sticker (lower z-index) */}
      <div style={{
        position: 'absolute', left: '50%', top: 0, bottom: 0, width: 6,
        background: '#000', transform: 'translateX(-50%)', zIndex: 1,
      }} />
      {/* VS sticker — centered on the divider. Use motion x/y (not a raw
          transform string) so the -50% centering composes with scale/rotate
          instead of being clobbered by motion's transform handling. */}
      <motion.div
        initial={{ scale: 0, rotate: 0 }}
        animate={{ scale: 1, rotate: -10 }}
        transition={{ duration: 0.5, delay: 0.55, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', left: '50%', top: '50%',
          x: '-50%', y: '-50%',
          background: '#FFD93D', color: '#000',
          border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          width: 120, height: 120, borderRadius: '50%',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontWeight: 900, fontSize: 36, zIndex: 5,
        }}
      >
        VS
      </motion.div>

      {/* Right 50% — 我的 AI */}
      <motion.div
        initial={{ clipPath: 'inset(0 0 0 100%)' }}
        animate={{ clipPath: 'inset(0 0 0 0)' }}
        transition={{ duration: 0.6, delay: 0.55, ease: 'easeOut' }}
        style={{
          flex: '0 0 50%', padding: 64, position: 'relative',
          display: 'flex', flexDirection: 'column',
          justifyContent: 'center', alignItems: 'center', textAlign: 'center',
        }}
      >
        <div style={{ fontWeight: 900, fontSize: '4rem', color: '#000' }}>我的 AI</div>

        {/* Door icon (drawn as black-bordered rect for now) */}
        <div style={{
          marginTop: 24, alignSelf: 'center',
          width: 100, height: 140, background: '#FFFFFF',
          border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
          position: 'relative',
        }}>
          <div style={{
            position: 'absolute', right: 12, top: '50%',
            width: 8, height: 8, background: '#000', borderRadius: '50%',
          }} />
        </div>

        <motion.div
          initial={{ y: -200, scale: 0, opacity: 0 }}
          animate={{ y: 0, scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 1.25, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            marginTop: 24, background: '#FFD93D', color: '#000',
            padding: '20px 36px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            fontWeight: 900, fontSize: 24, rotate: 3, alignSelf: 'center',
          }}
        >
          自己摸出規則
        </motion.div>
      </motion.div>
    </main>
  );
}
