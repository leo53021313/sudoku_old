import { motion } from 'motion/react';
import { AiSticker } from '../../components/AiSticker.jsx';

export default function Ch1Step6() {
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

      {/* ⋯⋯ ellipsis bubble above girl — stamp-in + pulse (preserved).
          水平：錨在女生示意圖中心（left 8% + 半寬 144px），用 motion x:'-50%' 置中。
          垂直：bottom = 女生 bottom 14% + 約 307px 高（含 -4° 旋轉外擴）+ 13px 間隙，
          讓泡泡底緣超過女生最上方框限、完全不覆蓋到圖。 */}
      <motion.div
        initial={{ scale: 0, opacity: 0, x: '-50%' }}
        animate={{ scale: [0, 1, 1], opacity: 1, x: '-50%' }}
        transition={{
          scale: { duration: 0.3, ease: [0.34, 1.56, 0.64, 1] },
          opacity: { duration: 0.3 },
        }}
        style={{
          position: 'absolute', bottom: 'calc(14% + 320px)', left: 'calc(8% + 144px)',
        }}
      >
        <motion.div
          animate={{ scale: [1, 1.08, 1] }}
          transition={{ duration: 1, ease: 'easeInOut', repeat: Infinity }}
          style={{
            background: '#FFFDF5', color: '#000',
            border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
            padding: '12px 24px', borderRadius: 32,
            fontWeight: 900, fontSize: 32, letterSpacing: '0.2em',
          }}
        >
          ⋯⋯
        </motion.div>
      </motion.div>

      {/* Bottom-right small caption (preserved) */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        style={{
          position: 'absolute', bottom: 32, right: 32,
          fontSize: 18, fontWeight: 700, color: '#666',
        }}
      >
        然後我繼續發呆⋯
      </motion.div>
    </main>
  );
}
