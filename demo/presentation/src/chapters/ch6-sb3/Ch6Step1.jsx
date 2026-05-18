import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { CrashLine } from '../../motifs/CrashLine.jsx';

export default function Ch6Step1() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'C']);
  const firedRef = useRef(false);

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

      <CrashLine
        active={beatIndex >= 1}
        filled={beatIndex >= 2}
        text="⋯⋯我又錯了"
        width={720}
      />
    </main>
  );
}
