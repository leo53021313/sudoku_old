import { motion } from 'motion/react';

// Impact speed-lines that burst outward from behind the decision stamp.
// Clean radiating black bars (alternating long/short) — neo-brutalist punch,
// no halftone texture. Each bar grows from its inner end then fades.
function SpeedLines({ count = 16, delay = 1.15 }) {
  return (
    <div
      aria-hidden="true"
      style={{ position: 'absolute', left: '50%', top: '50%', width: 0, height: 0, zIndex: -1, pointerEvents: 'none' }}
    >
      {Array.from({ length: count }).map((_, i) => {
        const angle = (360 / count) * i;
        const long = i % 2 === 0;
        return (
          <div key={i} style={{ position: 'absolute', left: 0, top: 0, transform: `rotate(${angle}deg)` }}>
            <motion.div
              initial={{ scaleX: 0, opacity: 0 }}
              animate={{ scaleX: [0, 1, 1], opacity: [0, 1, 0] }}
              transition={{ duration: 0.55, delay, ease: 'easeOut', times: [0, 0.4, 1] }}
              style={{
                position: 'absolute',
                left: long ? 95 : 80, top: -3,
                width: long ? 140 : 80, height: 6,
                background: '#000', borderRadius: 3,
                transformOrigin: '0% 50%',
              }}
            />
          </div>
        );
      })}
    </div>
  );
}

export default function Ch3Step3() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
      fontWeight: 900, fontSize: '5rem', lineHeight: 1.2, gap: 16,
    }}>
      {/* "OK" wipes in first — the beat opens with the verdict */}
      <motion.div
        initial={{ clipPath: 'inset(0px 100% 0px 0px)', opacity: 0 }}
        animate={{ clipPath: 'inset(-24px)', opacity: 1 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        <span style={{
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '0 32px', border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
          rotate: -2, display: 'inline-block',
        }}>OK</span>
      </motion.div>

      {/* "所以我要走 純 RL" — the decision lands like a stamp slamming down,
          speed-lines bursting out from behind it on impact */}
      <motion.div
        style={{ display: 'flex', alignItems: 'center', gap: 24, justifyContent: 'center' }}
      >
        <motion.span
          initial={{ opacity: 0, x: -24 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.6 }}
        >
          所以我要走
        </motion.span>
        <span style={{ position: 'relative', display: 'inline-block' }}>
          <SpeedLines delay={1.15} />
          <motion.span
            initial={{ scale: 2.4, opacity: 0, rotate: 2 }}
            animate={{ scale: 1, opacity: 1, rotate: 2 }}
            transition={{ duration: 0.45, delay: 0.95, ease: [0.34, 1.56, 0.64, 1] }}
            style={{
              background: '#FFD93D', color: '#000',
              padding: '0 24px', border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
              display: 'inline-block', position: 'relative', zIndex: 1,
            }}
          >
            純 RL
          </motion.span>
        </span>
      </motion.div>

      {/* Forward beat — the pivot to "find data" rises in last */}
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 1.7 }}
        style={{ fontSize: '3rem', marginTop: 32 }}
      >
        下一步是找資料
      </motion.div>
    </main>
  );
}
