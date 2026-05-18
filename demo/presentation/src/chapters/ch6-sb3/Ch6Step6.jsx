import { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { SpotlightVignette } from '../../motifs/SpotlightVignette.jsx';
import { HalftoneBurst } from '../../motifs/HalftoneBurst.jsx';
import { InkSplatter } from '../../motifs/InkSplatter.jsx';

export default function Ch6Step6() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'B', 'C', 'E', 'G']);
  const firedRef = useRef(false);
  const [blackFlash, setBlackFlash] = useState(false);

  // Beat 0: black flash 100ms
  useEffect(() => {
    if (beatIndex === 0) {
      setBlackFlash(true);
      const t = setTimeout(() => setBlackFlash(false), 100);
      return () => clearTimeout(t);
    }
  }, [beatIndex]);

  // Beat 2 climax — full A+B+C+E+G
  useEffect(() => {
    if (beatIndex === 2 && !firedRef.current) {
      firedRef.current = true;
      climax.play();
      triggerShake();
    }
  }, [beatIndex, climax, triggerShake]);

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
      <HalftoneBurst active={climax.activeFX.B} centerX="50%" centerY="50%" />
      <InkSplatter active={climax.activeFX.E} count={8} radius={160} centerX="50%" centerY="50%" />

      {/* Beat 1+ red placeholder + fill on beat 2 */}
      <motion.div
        animate={beatIndex === 2
          ? { scale: [0.85, 1.4, 1.0, 0.95, 1.0] }
          : { scale: beatIndex >= 1 ? 1 : 0 }}
        transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ position: 'relative', zIndex: 50 }}
      >
        <div style={{
          background: '#FF6B6B',
          color: beatIndex >= 2 ? '#FFFDF5' : 'transparent',
          padding: '64px 128px',
          border: '6px solid #FFFDF5',
          boxShadow: '20px 20px 0 0 #000',
          fontWeight: 900, fontSize: '8rem', lineHeight: 1,
          letterSpacing: '0.2em', rotate: -3,
          minWidth: 600, minHeight: 200, textAlign: 'center',
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
