import { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';

export default function Ch7Step6() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'B', 'C']);
  const firedRef = useRef(false);
  const [count, setCount] = useState(0);
  const [aftermath, setAftermath] = useState(false);

  // Beat 0: count-up across 2s
  useEffect(() => {
    if (beatIndex === 0) {
      let raf, start;
      const animate = (t) => {
        if (!start) start = t;
        const elapsed = t - start;
        const pct = Math.min(elapsed / 2000, 1);
        setCount(Math.floor(pct * 23456789));
        if (pct < 1) raf = requestAnimationFrame(animate);
      };
      raf = requestAnimationFrame(animate);
      return () => cancelAnimationFrame(raf);
    }
  }, [beatIndex]);

  // Beat 2 climax — fire + aftermath at +700ms
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
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
      background: beatIndex >= 0 ? 'rgba(255,107,107,0.15)' : 'transparent',
      transition: 'background 0.3s',
    }}>
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { opacity: 1 } : { opacity: 0 }}
        style={{
          fontWeight: 900, fontSize: '2rem', color: '#000',
        }}
      >
        練了
        <span style={{
          background: '#FF6B6B', color: '#FFF', padding: '4px 24px', margin: '0 12px',
          border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
          fontSize: '3rem', fontFamily: 'monospace',
        }}>
          {count.toLocaleString()}
        </span>
        次
      </motion.div>

      {/* Beat 1+ subtitle with caret placeholder */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1 ? { opacity: 1 } : { opacity: 0 }}
        style={{
          fontWeight: 700, fontSize: '2rem', textAlign: 'center',
        }}
      >
        完整解出一道題的機率是
        {beatIndex < 2 && (
          <motion.span
            animate={anticipationActive
              ? { opacity: [1, 0, 1, 0, 1], y: [-1, 1, -1, 1, 0] }
              : { opacity: [1, 0] }}
            transition={anticipationActive
              ? { duration: 0.4, repeat: Infinity, ease: 'linear' }
              : { duration: 0.6, repeat: Infinity, ease: 'steps(2)' }}
            style={{ marginLeft: 16, color: '#FF6B6B', display: 'inline-block' }}
          >_</motion.span>
        )}
      </motion.div>

      {/* Beat 2 punchline: "0" drop-in + aftermath settle */}
      <motion.div
        animate={
          beatIndex === 2
            ? aftermath
              ? { scale: 1, rotate: 1, opacity: 1 }                                            // aftermath delta +1°
              : { scale: [0, 1.4, 1.0, 0.95, 1.0], y: [0, 0, 0, 0, 0], rotate: 0, opacity: 1 } // climax overshoot
            : { scale: 0, rotate: 0, opacity: 0 }
        }
        transition={
          beatIndex === 2
            ? aftermath
              ? { duration: 0.35, ease: [0.22, 1, 0.36, 1] }
              : { duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }
            : { duration: 0.3 }
        }
        style={{
          background: '#FFD93D', color: '#000',
          padding: '32px 96px', border: '8px solid #000',
          boxShadow: aftermath ? '16px 16px 0 0 #000' : '20px 20px 0 0 #000',
          fontWeight: 900, fontSize: '12rem', lineHeight: 1, rotate: -3,
          position: 'relative', zIndex: 50,
          transition: 'box-shadow 0.35s cubic-bezier(0.22, 1, 0.36, 1)',
        }}
      >
        0
      </motion.div>
    </main>
  );
}
