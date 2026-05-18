import { motion } from 'motion/react';
import { AiSticker } from '../../components/AiSticker.jsx';

export default function Ch1Step4() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Caption from top */}
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3, ease: 'easeOut' }}
        style={{
          position: 'absolute', top: 64, left: 0, right: 0,
          textAlign: 'center',
          fontWeight: 900, fontSize: '2rem', color: '#000',
        }}
      >
        靈感哪來呢？某天捷運上⋯
      </motion.div>

      {/* 正妹 AI sticker bottom-left, overshoot in */}
      <motion.div
        initial={{ x: -200, y: 100, scale: 0.7, opacity: 0 }}
        animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: '14%', left: '8%',
        }}
      >
        <AiSticker
          src="/images/ai/ch1/girl-daydream.png"
          alt="正妹發呆中"
          width={280}
          rotation={-4}
          shadow={8}
        />
      </motion.div>
    </main>
  );
}
