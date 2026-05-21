import { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { SpotlightVignette } from '../../motifs/SpotlightVignette.jsx';

export default function Ch9Step11() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'C', 'G']);
  const firedRef = useRef(false);
  const [aftermath, setAftermath] = useState(false);

  useEffect(() => {
    if (beatIndex === 3 && !firedRef.current) {
      firedRef.current = true;
      climax.play();
      triggerShake();
      const t = setTimeout(() => setAftermath(true), 700);
      return () => clearTimeout(t);
    }
  }, [beatIndex, climax, triggerShake]);

  const anticipationActive = beatIndex === 2;

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 24,
    }}>
      <SpotlightVignette active={climax.activeFX.G} />

      {/* Beat 0+ kicker + halftone densify */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { y: 0, opacity: 1 } : { y: -20, opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          position: 'absolute', top: 80,
          fontWeight: 900, fontSize: '1.75rem', color: '#000',
        }}
      >
        從挫敗中學習就行了
      </motion.div>
      {beatIndex >= 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.3 }}
          transition={{ duration: 0.4 }}
          style={{
            position: 'fixed', inset: 0, zIndex: 6, pointerEvents: 'none',
            backgroundImage: 'radial-gradient(#000 1.5px, transparent 1.5px)',
            backgroundSize: '12px 12px',
          }}
        />
      )}

      {/* Beat 0+ crash-line frame (bigger version: 6px red border + scale 1.3 on beat 3) */}
      <motion.div
        initial={false}
        animate={
          beatIndex === 3
            ? aftermath
              ? { scale: 1, opacity: 1, rotate: 1, filter: 'drop-shadow(0 0 0px rgba(255,107,107,0))' }
              : { scale: [1, 1.3, 1], opacity: 1, rotate: 0, filter: 'drop-shadow(0 0 0px rgba(255,107,107,0))' }
            : anticipationActive
              ? { scale: [1, 1.012, 0.992, 1], opacity: 1, rotate: [0, 0.4, -0.3, 0],
                  filter: ['drop-shadow(0 0 0px rgba(255,107,107,0))', 'drop-shadow(0 0 18px rgba(255,107,107,0.55))', 'drop-shadow(0 0 0px rgba(255,107,107,0))'] }
              : beatIndex >= 0
                ? { scale: 1, opacity: 1, rotate: 0, filter: 'drop-shadow(0 0 0px rgba(255,107,107,0))' }
                : { scale: 0.9, opacity: 0, rotate: 0, filter: 'drop-shadow(0 0 0px rgba(255,107,107,0))' }
        }
        transition={
          beatIndex === 3
            ? aftermath
              ? { duration: 0.4, ease: [0.22, 1, 0.36, 1] }
              : { duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }
            : anticipationActive
              ? { duration: 1.6, repeat: Infinity, ease: 'linear' }
              : { duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }
        }
        style={{
          background: '#FFFDF5', color: '#FF6B6B',
          border: '6px solid #FF6B6B',
          boxShadow: beatIndex === 3
            ? (aftermath ? '14px 14px 0 0 #000' : '20px 20px 0 0 #000')
            : '12px 12px 0 0 #000',
          padding: '48px 80px', minWidth: 800, minHeight: 240,
          textAlign: 'center', rotate: -2,
          position: 'relative', zIndex: 30,
          transition: 'box-shadow 0.35s cubic-bezier(0.22, 1, 0.36, 1)',
        }}
      >
        <div style={{ fontWeight: 900, fontSize: '3.5rem', lineHeight: 1.3 }}>
          {/* Beat 2+ first line.
              Both branches are <motion.span> at the same JSX position. Without distinct
              keys React reuses the DOM node across the swap, and Motion ignores `initial`
              on updates — the cursor branch's `opacity: [1, 0]` infinite oscillation can
              then bleed into the text branch, making "人生第一次的外向" flicker/fade. */}
          {beatIndex >= 2 ? (
            <motion.span
              key="text"
              initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 1 }}
              animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
            >
              人生第一次的外向
            </motion.span>
          ) : (
            <motion.span
              key="cursor"
              animate={{ opacity: [1, 0] }}
              transition={{ duration: 0.6, repeat: Infinity, ease: 'steps(2)' }}
            >_</motion.span>
          )}
          <br/>
          {/* Beat 3+ second line */}
          {beatIndex >= 3 && (
            <motion.span
              initial={{ clipPath: 'inset(0 100% 0 0)' }}
              animate={{ clipPath: 'inset(0 0 0 0)' }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
            >
              · 換來一輩子的內向
            </motion.span>
          )}
        </div>
      </motion.div>

      {/* Beat 1+ subtitle */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1 ? { y: 0, opacity: 1 } : { y: 20, opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          position: 'absolute', bottom: 80,
          fontWeight: 900, fontSize: '1.5rem',
        }}
      >
        但是<span style={{ background: '#FF6B6B', color: '#FFF', padding: '2px 12px', border: '4px solid #000' }}>不要停滯不前</span>
      </motion.div>
    </main>
  );
}
