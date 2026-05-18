import { motion } from 'motion/react';
import { AiSticker } from '../../components/AiSticker.jsx';

export default function Ch1Step7() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* girl + flappy stickers persisted */}
      <div style={{ position: 'absolute', bottom: '14%', left: '8%' }}>
        <AiSticker
          src="/images/ai/ch1/girl-daydream.png"
          alt="正妹發呆中"
          width={280}
          rotation={-4}
          shadow={8}
        />
      </div>
      <div style={{ position: 'absolute', top: '14%', right: '8%' }}>
        <AiSticker
          src="/images/ai/ch1/codebullet-flappy.png"
          alt="Code Bullet flappy bird"
          width={280}
          rotation={3}
          shadow={8}
        />
      </div>

      {/* NEW: 沒手機·解數獨 AI sticker bottom-right, scales in */}
      <motion.div
        initial={{ x: 200, y: 100, scale: 0.7, opacity: 0 }}
        animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: '14%', right: '8%',
        }}
      >
        <AiSticker
          src="/images/ai/ch1/soldier-sudoku.png"
          alt="軍人解數獨"
          width={280}
          rotation={2}
          shadow={8}
        />
      </motion.div>
    </main>
  );
}
