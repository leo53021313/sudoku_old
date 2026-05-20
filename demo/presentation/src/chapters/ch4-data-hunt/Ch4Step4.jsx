import { motion } from 'motion/react';
import { useState, useEffect } from 'react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';

export default function Ch4Step4() {
  const { beatIndex } = usePresentationContext();

  // proxy 池的高亮在 IP 之間輪替 —— 視覺化「一次好幾萬個 IP 不斷換著爬」。
  // 只在 beat 1（proxy 出場）時推進，beat 0 不需要。
  const [highlightIdx, setHighlightIdx] = useState(0);
  useEffect(() => {
    if (beatIndex < 1) return;
    const id = setInterval(() => setHighlightIdx(i => (i + 1) % 30), 200);
    return () => clearInterval(id);
  }, [beatIndex]);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* 紅警示 hero —— beat 0 置中放大砸下；beat 1 縮小上移成上下文（讓位給 proxy 池） */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={
          beatIndex >= 1
            ? { scale: 0.62, opacity: 0.85, y: -300, rotate: -3 }
            : { scale: 1, opacity: 1, y: 0, rotate: -3 }
        }
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute',
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '24px 48px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          fontWeight: 900, fontSize: '3rem', whiteSpace: 'nowrap',
        }}
      >
        才爬 20 題就被封 IP
      </motion.div>

      {/* Beat 0 only : 網站封鎖回饋 —— 模擬瀏覽器擋頁，呼應原文「網站顯示我的 IP 被封鎖」 */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1 ? { opacity: 0, y: 20, scale: 0.92 } : { opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.4, delay: beatIndex >= 1 ? 0 : 0.7 }}
        style={{
          position: 'absolute', top: 'calc(50% + 96px)',
          background: '#FFFDF5', color: '#000',
          border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
          fontFamily: 'monospace', fontSize: 24, fontWeight: 700,
          display: 'flex', alignItems: 'center', gap: 16, padding: '14px 28px',
          pointerEvents: 'none',
        }}
      >
        <span style={{ color: '#FF6B6B' }}>403</span>
        <span>你的 IP 已被封鎖</span>
      </motion.div>

      {/* Beat 1 : proxy 出場 —— 標語 + 好幾萬個 IP 池輪替 */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1 ? { y: -64, opacity: 1 } : { y: -40, opacity: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        style={{
          position: 'absolute',
          fontWeight: 900, fontSize: '1.6rem', textAlign: 'center', pointerEvents: 'none',
        }}
      >
        proxy · 類似 VPN · 一次好幾萬個 IP
      </motion.div>

      {/* IP 池 —— beat 1 才 stagger 浮現；高亮持續輪替代表 IP 不斷切換 */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1 ? 'visible' : 'hidden'}
        variants={{
          hidden: { opacity: 0 },
          visible: { opacity: 1, transition: { staggerChildren: 0.03 } },
        }}
        style={{
          position: 'absolute', top: 'calc(50% + 24px)',
          display: 'grid', gridTemplateColumns: 'repeat(10, 1fr)', gap: 8,
          maxWidth: 800,
        }}
      >
        {Array.from({ length: 30 }).map((_, i) => (
          <motion.div
            key={i}
            variants={{
              hidden: { scale: 0, opacity: 0 },
              visible: { scale: 1, opacity: beatIndex >= 1 && i === highlightIdx ? 1 : 0.4 },
            }}
            transition={{ duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
            style={{
              background: i === highlightIdx ? '#FFD93D' : '#FFFDF5',
              border: '3px solid #000',
              boxShadow: i === highlightIdx ? '4px 4px 0 0 #000' : '2px 2px 0 0 #000',
              padding: '8px 4px',
              fontFamily: 'monospace', fontWeight: 700, fontSize: 12,
              textAlign: 'center', transform: `rotate(${(i * 7) % 5 - 2}deg)`,
              transition: 'background 0.15s, opacity 0.15s',
            }}
          >
            {`${(i * 17 + 23) % 256}.${(i * 31) % 256}`}
          </motion.div>
        ))}
      </motion.div>

      {/* Beat 1 : 池子底下補一句「+ 數萬個」—— 30 格只是示意，真實規模更大 */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1 ? { opacity: 1 } : { opacity: 0 }}
        transition={{ duration: 0.4, delay: beatIndex >= 1 ? 0.9 : 0 }}
        style={{
          position: 'absolute', top: 'calc(50% + 220px)',
          fontFamily: 'monospace', fontWeight: 700, fontSize: 20,
          pointerEvents: 'none',
        }}
      >
        + 數萬個 IP 不斷輪替 ↻
      </motion.div>
    </main>
  );
}
