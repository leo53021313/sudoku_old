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

      {/* 漫畫思考泡泡點鏈：由小到大，沿兩張貼紙的中線水平直連——從正妹（左下）的
          右邊一路連到當兵解數獨（右下）的左邊。bottom = 貼紙垂直中心（14% + 半高 144px），
          y:'-50%' 把圓心對齊中線。青綠 #2EC4B6 實心泡泡（冷色）在捷運背景圖上對比最強、最跳。 */}
      {[
        { left: '26%', size: 16 },
        { left: '42%', size: 26 },
        { left: '58%', size: 38 },
        { left: '74%', size: 54 },
      ].map((b, i) => (
        <motion.div
          key={i}
          initial={{ scale: 0, opacity: 0, x: '-50%', y: '-50%' }}
          animate={{ scale: 1, opacity: 1, x: '-50%', y: '-50%' }}
          transition={{
            delay: 0.6 + i * 0.13,
            duration: 0.4,
            ease: [0.34, 1.56, 0.64, 1],
          }}
          style={{
            position: 'absolute', left: b.left, bottom: 'calc(14% + 144px)',
            width: b.size, height: b.size, borderRadius: '50%',
            border: '3px solid #000', background: '#2EC4B6',
            boxShadow: `${Math.max(2, Math.round(b.size * 0.1))}px ${Math.max(2, Math.round(b.size * 0.1))}px 0 0 #000`,
            pointerEvents: 'none', zIndex: 25,
          }}
        />
      ))}
    </main>
  );
}
