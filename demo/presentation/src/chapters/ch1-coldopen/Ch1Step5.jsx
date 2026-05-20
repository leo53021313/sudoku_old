import { motion } from 'motion/react';
import { AiSticker } from '../../components/AiSticker.jsx';

export default function Ch1Step5() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* 正妹 sticker persisted (no entrance animation) */}
      <div style={{
        position: 'absolute', bottom: '14%', left: '8%',
      }}>
        <AiSticker
          src="/images/ai/ch1/girl-daydream.png"
          alt="正妹發呆中"
          width={280}
          rotation={-4}
          shadow={8}
        />
      </div>

      {/* NEW: Code Bullet flappy bird AI sticker top-right, scales in */}
      <motion.div
        initial={{ x: 200, y: -100, scale: 0.7, opacity: 0 }}
        animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', top: '14%', right: '8%',
        }}
      >
        <AiSticker
          src="/images/ai/ch1/codebullet-flappy.png"
          alt="Code Bullet flappy bird"
          width={280}
          rotation={3}
          shadow={8}
        />
      </motion.div>

      {/* 漫畫思考泡泡點鏈：由小到大，從正妹腦中浮現往 flappy bird 方向冒出。
          全部落在兩張貼紙邊框外的對角空隙，不覆蓋任何圖。圓形泡泡用絕對定位
          的 div（非 SVG）以避免 preserveAspectRatio 拉伸成橢圓。
          青綠 #2EC4B6 實心填色（冷色），在偏暖的捷運背景圖上對比最強、最跳。 */}
      {[
        { left: '27%', top: '61%', size: 16 },
        { left: '39%', top: '55%', size: 26 },
        { left: '52%', top: '49%', size: 38 },
        { left: '65%', top: '43%', size: 54 },
      ].map((b, i) => (
        <motion.div
          key={i}
          // x/y 用 motion 自己的 transform（非 style.transform），才能與 scale 正確
          // 合成；用 -50% 把圓心錨在定位點上，scale 由圓心 pop。
          initial={{ scale: 0, opacity: 0, x: '-50%', y: '-50%' }}
          animate={{ scale: 1, opacity: 1, x: '-50%', y: '-50%' }}
          transition={{
            delay: 0.5 + i * 0.13,
            duration: 0.4,
            ease: [0.34, 1.56, 0.64, 1],
          }}
          style={{
            position: 'absolute', left: b.left, top: b.top,
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
