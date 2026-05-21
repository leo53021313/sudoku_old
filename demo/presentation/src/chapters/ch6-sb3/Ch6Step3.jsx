import { motion } from 'motion/react';
import { useState, useEffect } from 'react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { GirlNew } from '../../motifs/GirlNew.jsx';
import { MilkTea } from '../../motifs/MilkTea.jsx';

// 沿用全片 sticker overshoot ease
const OVERSHOOT = [0.34, 1.56, 0.64, 1];

// 並肩 stage 尺寸（絕對定位，避免女生佔位導致奶茶 beat0 偏離置中）
const STAGE_W = 820;
const STAGE_H = 460;
const MILKTEA_W = 300;
const GIRL_W = 300;

export default function Ch6Step3() {
  const { beatIndex } = usePresentationContext();
  const [plusses, setPlusses] = useState([]);

  // + 浮動只在 beat 3 啟動
  useEffect(() => {
    if (beatIndex < 3) {
      // 用 setTimeout 避免在 effect 同步呼叫 setState（lint: react-hooks/set-state-in-effect）
      const t = setTimeout(() => setPlusses([]), 0);
      return () => clearTimeout(t);
    }
    let id = 0;
    const t = setInterval(() => {
      setPlusses(prev => [
        ...prev,
        { id: id++, x: Math.random() * 80 + 10 },
      ].slice(-15));
    }, 400);
    return () => clearInterval(t);
  }, [beatIndex]);

  // 奶茶 beat0-1 置中、beat>=2 左移讓位給女生
  const milkTeaX = beatIndex >= 2 ? -200 : 0;

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* 並肩 stage */}
      <div style={{ position: 'relative', width: STAGE_W, height: STAGE_H }}>
        {/* 奶茶 + 名牌（置中基準 left，beat>=2 動畫左移） */}
        <motion.div
          initial={false}
          animate={{ x: milkTeaX }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          style={{
            position: 'absolute', top: 0,
            left: (STAGE_W - MILKTEA_W) / 2,
            width: MILKTEA_W,
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16,
          }}
        >
          {/* 奶茶登場 beat0 */}
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, ease: OVERSHOOT }}
          >
            <MilkTea width={MILKTEA_W} rotation={-3} shadow={12} />
          </motion.div>

          {/* 名牌「奶茶」 beat>=1 */}
          <motion.div
            initial={false}
            animate={beatIndex >= 1
              ? { scale: 1, opacity: 1 }
              : { scale: 0, opacity: 0 }}
            transition={{ duration: 0.4, ease: OVERSHOOT }}
            style={{
              background: '#FFD93D', color: '#000',
              padding: '8px 24px', border: '4px solid #000',
              boxShadow: '5px 5px 0 0 #000',
              fontWeight: 900, fontSize: 28, whiteSpace: 'nowrap',
            }}
          >
            奶茶
          </motion.div>
        </motion.div>

        {/* 女生 beat>=2 從右側滑入 */}
        <motion.div
          initial={false}
          animate={beatIndex >= 2
            ? { x: 0, opacity: 1 }
            : { x: 80, opacity: 0 }}
          transition={{ duration: 0.5, ease: OVERSHOOT }}
          style={{
            position: 'absolute', top: 20,
            left: STAGE_W - GIRL_W - 30,
            width: GIRL_W,
            pointerEvents: 'none',
          }}
        >
          <GirlNew width={GIRL_W} rotation={4} shadow={12} />
        </motion.div>
      </div>

      {/* + 浮動 beat3 */}
      {plusses.map(p => (
        <motion.div
          key={p.id}
          initial={{ y: 0, opacity: 1 }}
          animate={{ y: -300, opacity: 0 }}
          transition={{ duration: 2, ease: 'easeOut' }}
          style={{
            position: 'absolute', left: `${p.x}%`, bottom: '20%',
            fontSize: 48, fontWeight: 900, color: '#10B981',
            WebkitTextStroke: '2px black', pointerEvents: 'none',
          }}
        >
          +
        </motion.div>
      ))}

      {/* beat3 字幕 */}
      <motion.div
        initial={false}
        animate={beatIndex >= 3 ? { y: 0, opacity: 1 } : { y: 20, opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          marginTop: 48, fontWeight: 700, fontSize: '1.5rem', color: '#000',
          textAlign: 'center', maxWidth: 900,
        }}
      >
        奶茶只要看到對方持續回覆訊息，就會覺得對方也喜歡他。
      </motion.div>
    </main>
  );
}
