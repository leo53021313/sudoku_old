import { motion } from 'motion/react';
import { useEffect, useState } from 'react';

export default function Ch8Step4() {
  const [flipped, setFlipped] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setFlipped(true), 800);
    return () => clearTimeout(t);
  }, []);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        style={{ fontWeight: 900, fontSize: '2.5rem' }}
      >
        破關獎勵調更大
      </motion.div>

      <div style={{ perspective: 1000, width: 400, height: 240 }}>
        <motion.div
          initial={{ rotateY: 0 }}
          animate={{ rotateY: flipped ? 180 : 0 }}
          transition={{ duration: 0.6, ease: 'easeInOut' }}
          style={{
            position: 'relative', width: '100%', height: '100%',
            transformStyle: 'preserve-3d',
          }}
        >
          <div style={{
            position: 'absolute', inset: 0,
            backfaceVisibility: 'hidden',
            background: '#FF6B6B', color: '#FFF',
            border: '8px solid #000', boxShadow: '12px 12px 0 0 #000',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontWeight: 900, fontSize: '8rem',
          }}>
            +20
          </div>
          <div style={{
            position: 'absolute', inset: 0,
            backfaceVisibility: 'hidden',
            transform: 'rotateY(180deg)',
            background: '#FFD93D', color: '#000',
            border: '8px solid #000', boxShadow: '16px 16px 0 0 #000',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontWeight: 900, fontSize: '8rem',
          }}>
            +50
          </div>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.6 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', textAlign: 'center', color: '#666' }}
      >
        誘惑超過刷部分分數的賤招
      </motion.div>
    </main>
  );
}
