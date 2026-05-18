import { useEffect } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';

export default function Ch7Step1() {
  const { triggerShake } = usePresentationContext();

  // Trigger light shake when 重寫 highlight slides in (~700ms after mount)
  useEffect(() => {
    const t = setTimeout(() => triggerShake(), 700);
    return () => clearTimeout(t);
  }, [triggerShake]);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', color: '#666', marginBottom: 24 }}
      >
        核心想法只有一個
      </motion.div>

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 1.0, delay: 0.3, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '4rem', textAlign: 'center', lineHeight: 1.3,
        }}
      >
        我只好整個計分獎勵系統
        <br/>
        <motion.span
          initial={{ clipPath: 'inset(0 100% 0 0)' }}
          animate={{ clipPath: 'inset(0 0 0 0)' }}
          transition={{ duration: 0.4, delay: 0.7, ease: 'easeOut' }}
          style={{
            background: '#FFD93D', color: '#000',
            padding: '4px 32px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            display: 'inline-block',
            fontSize: '5rem', rotate: -2, marginTop: 16,
          }}
        >
          重寫
        </motion.span>
      </motion.div>
    </main>
  );
}
