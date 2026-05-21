import { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { SpotlightVignette } from '../../motifs/SpotlightVignette.jsx';

// === APPROACH A · ANTICIPATION + AFTERMATH DEMO ===
// beat 0: black flash (existing)
// beat 1: red placeholder up + ANTICIPATION (slow red-tint breath + box micro-wobble)
// beat 2: climax (existing A+B+C+G) → +700ms → AFTERMATH (box tilt-decay -3°→-1°, shadow 20→16)

export default function Ch6Step6() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'B', 'C', 'G']);
  const firedRef = useRef(false);
  const [blackFlash, setBlackFlash] = useState(false);
  const [aftermath, setAftermath] = useState(false);

  // Beat 0: black flash 100ms
  useEffect(() => {
    if (beatIndex === 0) {
      setBlackFlash(true);
      const t = setTimeout(() => setBlackFlash(false), 100);
      return () => clearTimeout(t);
    }
  }, [beatIndex]);

  // Beat 2 climax — full A+B+C+G, then aftermath at +700ms
  useEffect(() => {
    if (beatIndex === 2 && !firedRef.current) {
      firedRef.current = true;
      climax.play();
      triggerShake();
      const t = setTimeout(() => setAftermath(true), 700);
      return () => clearTimeout(t);
    }
  }, [beatIndex, climax, triggerShake]);

  const anticipationActive = beatIndex === 1;

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Black flash overlay */}
      {blackFlash && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 60, background: '#000', pointerEvents: 'none',
        }} />
      )}

      {/* Climax overlays — only render when beatIndex 2 + climax fires */}
      <SpotlightVignette active={climax.activeFX.G} />

      {/* Red placeholder + climax + aftermath all on this motion node */}
      <motion.div
        animate={
          beatIndex === 2
            ? aftermath
              ? { scale: 1, rotate: 2 }                                                    // aftermath: -3+2 = -1
              : { scale: [0.85, 1.4, 1.0, 0.95, 1.0], rotate: 0 }                          // climax overshoot
            : anticipationActive
              ? { scale: [1.0, 1.015, 0.99, 1.0], rotate: [0, 0.6, -0.4, 0] }              // anticipation wobble
              : { scale: beatIndex >= 1 ? 1 : 0, rotate: 0 }
        }
        transition={
          beatIndex === 2
            ? aftermath
              ? { duration: 0.35, ease: [0.22, 1, 0.36, 1] }
              : { duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }
            : anticipationActive
              ? { duration: 1.4, repeat: Infinity, ease: 'linear' }
              : { duration: 0.3 }
        }
        style={{ position: 'relative', zIndex: 50 }}
      >
        <div style={{
          background: '#FF6B6B',
          color: beatIndex >= 2 ? '#FFFDF5' : 'transparent',
          padding: '64px 128px',
          border: '6px solid #FFFDF5',
          boxShadow: aftermath ? '16px 16px 0 0 #000' : '20px 20px 0 0 #000',
          fontWeight: 900, fontSize: '8rem', lineHeight: 1,
          letterSpacing: '0.2em', rotate: -3,
          minWidth: 600, minHeight: 200, textAlign: 'center',
          transition: 'box-shadow 0.35s cubic-bezier(0.22, 1, 0.36, 1)',
        }}>
          {beatIndex >= 2 ? '備胎' : '  '}
        </div>
      </motion.div>

      {/* Beat 1+ subtitle below */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1 ? { y: 0, opacity: 1 } : { y: 20, opacity: 0 }}
        transition={{ duration: 0.5, delay: beatIndex === 1 ? 0.2 : 0 }}
        style={{
          marginTop: 48, fontWeight: 700, fontSize: '1.5rem', color: '#000', zIndex: 50, position: 'relative',
        }}
      >
        看似有進展 · 結果什麼都沒發生
      </motion.div>
    </main>
  );
}
