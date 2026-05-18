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

        {/* Center bidirectional arrow overlay (preserved) */}
        <motion.svg
          width="120" height="40" viewBox="0 0 120 40"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.9 }}
          style={{
            position: 'absolute', left: '50%', top: '50%',
            transform: 'translate(-50%, -50%)',
            overflow: 'visible', zIndex: 5,
          }}
        >
          <motion.path
            d="M 10 20 L 20 10 L 10 20 L 110 20 L 100 30 L 110 20 L 100 10"
            fill="none" stroke="#000" strokeWidth="6" strokeLinecap="square"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.6, delay: 0.9 }}
          />
        </motion.svg>
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
