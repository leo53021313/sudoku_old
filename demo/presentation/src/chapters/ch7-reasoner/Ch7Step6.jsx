import { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';

export default function Ch7Step6() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'B', 'C']);
  const firedRef = useRef(false);
  const [count, setCount] = useState(0);

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
            animate={{ opacity: [1, 0] }}
            transition={{ duration: 0.6, repeat: Infinity, ease: 'steps(2)' }}
            style={{ marginLeft: 16, color: '#FF6B6B' }}
          >_</motion.span>
        )}
      </motion.div>

      {/* Beat 2 punchline: "0" drop-in */}
      <motion.div
        animate={beatIndex === 2
          ? { scale: [0, 1.4, 1.0, 0.95, 1.0], y: [0, 0, 0, 0, 0], opacity: 1 }
          : { scale: 0, opacity: 0 }}
        transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FFD93D', color: '#000',
          padding: '32px 96px', border: '8px solid #000', boxShadow: '20px 20px 0 0 #000',
          fontWeight: 900, fontSize: '12rem', lineHeight: 1, rotate: -3,
          position: 'relative', zIndex: 50,
        }}
      >
        0
      </motion.div>
    </main>
  );
}
