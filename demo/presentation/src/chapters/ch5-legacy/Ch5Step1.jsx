import { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { CrashLine } from '../../motifs/CrashLine.jsx';

export default function Ch5Step1() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'C']);
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
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Beat 0+ kicker top + halftone densify */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { y: 0, opacity: 1 } : { y: 30, opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          position: 'absolute', top: 80,
          fontWeight: 900, fontSize: '2rem', color: '#000',
        }}
      >
        我那時候很天真
      </motion.div>

      {/* Halftone dots overlay density 1.5x when beat >= 0 */}
      {beatIndex >= 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.25 }}
          transition={{ duration: 0.4 }}
          style={{
            position: 'fixed', inset: 0, zIndex: 6, pointerEvents: 'none',
            backgroundImage: 'radial-gradient(#000 1.5px, transparent 1.5px)',
            backgroundSize: '14px 14px',
          }}
        />
      )}

      {/* Beat 1+ prompt chat box */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1 ? { scale: 1, opacity: 1 } : { scale: 0, opacity: 0 }}
        transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FFFDF5', color: '#000',
          border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          padding: '24px 36px', maxWidth: 700,
          fontWeight: 700, fontSize: '1.5rem', lineHeight: 1.4,
          fontFamily: 'monospace',
          marginBottom: 56,
        }}
      >
        &gt; 幫我寫一個訓練 AI 解數獨的程式
      </motion.div>

      {/* Beat 2+ crash-line placeholder/fill — wrapped for anticipation wobble + aftermath settle */}
      <motion.div
        animate={
          beatIndex >= 3
            ? aftermath
              ? { scale: 1, rotate: 1 }                                          // aftermath: settle delta +1° on outer
              : { scale: 1, rotate: 0 }                                          // climax holds
            : anticipationActive
              ? { scale: [1.0, 1.012, 0.992, 1.0], rotate: [0, 0.5, -0.4, 0] }   // anticipation micro-wobble
              : { scale: 1, rotate: 0 }
        }
        transition={
          beatIndex >= 3
            ? { duration: 0.35, ease: [0.22, 1, 0.36, 1] }
            : anticipationActive
              ? { duration: 1.4, repeat: Infinity, ease: 'linear' }
              : { duration: 0.3 }
        }
        style={{
          position: 'relative',
          filter: aftermath
            ? 'drop-shadow(0 0 0 #FF6B6B)'
            : anticipationActive
              ? 'drop-shadow(0 0 6px rgba(255,107,107,0.35))'
              : 'none',
          transition: 'filter 0.35s cubic-bezier(0.22, 1, 0.36, 1)',
        }}
      >
        <CrashLine
          active={beatIndex >= 2}
          filled={beatIndex >= 3}
          text="⋯⋯結果我錯了"
          width={720}
        />
      </motion.div>
    </main>
  );
}
