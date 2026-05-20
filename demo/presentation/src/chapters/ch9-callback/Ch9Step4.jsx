import { motion } from 'motion/react';
import { AiSticker } from '../../components/AiSticker.jsx';

export default function Ch9Step4() {
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
        transition={{ duration: 0.5 }}
        style={{ fontWeight: 900, fontSize: '3rem', textAlign: 'center' }}
      >
        AI 在<span style={{ background: '#FFD93D', padding: '0 16px', border: '4px solid #000' }}>模仿</span>人類
      </motion.div>

      {/* Airplane + bird AI sticker (single 16:9 illustration) + center SVG arrow overlay */}
      <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: 32 }}>
        <motion.div
          initial={{ scale: 0.85, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        >
          <AiSticker
            src="/images/ai/ch9/airplane-bird.png"
            alt="飛機與鳥並置"
            width={900}
            rotation={0}
            shadow={12}
          />
        </motion.div>

        {/* Center "≈" analogy badge — sits in the empty gap between bird and airplane (鳥 ≈ 飛機) */}
        <motion.div
          initial={{ opacity: 0, scale: 0.6 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, delay: 0.9, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            position: 'absolute', left: '42%', top: '10%',
            transform: 'translate(-50%, -50%) rotate(-3deg)',
            minWidth: 92, height: 56,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            padding: '0 22px',
            background: '#FFFDF5',
            border: '4px solid #000',
            borderRadius: 999,
            boxShadow: '4px 4px 0 0 #000',
            zIndex: 5,
            fontWeight: 900,
            fontSize: '2.4rem',
            lineHeight: 1,
            color: '#000',
          }}
        >
          ↔
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.4 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', color: '#666', textAlign: 'center' }}
      >
        就像飛機 · 是人類模仿鳥類才造出來
      </motion.div>
    </main>
  );
}
