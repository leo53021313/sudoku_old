import { useState } from 'react';
import { motion } from 'motion/react';
import { useClimax } from '../../climax/useClimax.js';
import { HalftoneBurst } from '../../motifs/HalftoneBurst.jsx';
import { CounterUp } from '../../motifs/CounterUp.jsx';

export default function Ch8Step4() {
  const climax = useClimax(['B']);
  const [showFinal, setShowFinal] = useState(false);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
    }}>
      <HalftoneBurst active={climax.activeFX.B} centerX="50%" centerY="50%" />

      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        style={{ fontWeight: 900, fontSize: '2.5rem' }}
      >
        破關獎勵調更大
      </motion.div>

      <CounterUp
        from={20}
        to={50}
        prefix="+"
        duration={1200}
        onComplete={() => { climax.play(); setShowFinal(true); }}
      />

      <motion.div
        animate={showFinal ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
        transition={{ duration: 0.5 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', textAlign: 'center', color: '#666' }}
      >
        誘惑超過刷部分分數的賤招
      </motion.div>
    </main>
  );
}
