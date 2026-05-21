import { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { CrashLine } from '../../motifs/CrashLine.jsx';

export default function Ch6Step1() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'C']);
  const firedRef = useRef(false);
  const [aftermath, setAftermath] = useState(false);

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
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { y: 0, opacity: 1 } : { y: -30, opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          position: 'absolute', top: 80,
          fontWeight: 900, fontSize: '2rem',
        }}
      >
        正當我以為成了套皮仔⋯⋯
      </motion.div>

      {/* CrashLine wrapped for anticipation wobble + aftermath settle */}
      <motion.div
        animate={
          beatIndex >= 2
            ? aftermath
              ? { scale: 1, rotate: 1 }                                          // aftermath settle delta +1°
              : { scale: 1, rotate: 0 }                                          // climax holds
            : anticipationActive
              ? { scale: [1.0, 1.012, 0.992, 1.0], rotate: [0, 0.5, -0.4, 0] }   // anticipation wobble
              : { scale: 1, rotate: 0 }
        }
        transition={
          beatIndex >= 2
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
          active={beatIndex >= 1}
          filled={beatIndex >= 2}
          text="⋯⋯我又錯了"
          width={720}
        />
      </motion.div>
    </main>
  );
}
