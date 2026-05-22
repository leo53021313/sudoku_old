import { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { GirlVeteran } from '../../motifs/GirlVeteran.jsx';
import { MilkTea } from '../../motifs/MilkTea.jsx';

const QUESTIONS = [
  { text: '前女友跟我比 · 誰比較好？', bg: '#FFD93D', color: '#000', rotate: -2 },
  { text: '你心中的女神是誰？', bg: '#C4B5FD', color: '#000', rotate: 3 },
  { text: '你喜歡我哪裡？', bg: '#FF6B6B', color: '#FFFDF5', rotate: -3 },
  { text: '猜猜看 · 今天我哪裡不一樣？', bg: '#FFFDF5', color: '#000', rotate: 2 },
];

const OVERSHOOT = [0.34, 1.56, 0.64, 1];

export default function Ch9Step6() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['B']);
  const firedRef = useRef(false);

  const [hearts, setHearts] = useState([]);

  useEffect(() => {
    if (beatIndex === 0) {
      setHearts([]);
      let id = 0;
      const t = setInterval(() => {
        setHearts(h => [...h, { id: id++, x: Math.random() * 80 - 40 }].slice(-3));
      }, 350);
      return () => clearInterval(t);
    }
  }, [beatIndex]);

  useEffect(() => {
    if (beatIndex === 2 && !firedRef.current) {
      firedRef.current = true;
      climax.play();
      triggerShake();
    }
  }, [beatIndex, climax, triggerShake]);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
    }}>
      {/* 中央 hero 奶茶 — beat 0/1 中下方主角、beat>=2 fade-out 讓位給角落 reaction-shot */}
      {/* Wrapper handles absolute centering — motion's transform animation would clobber translateX(-50%) */}
      <div style={{ position: 'absolute', left: '50%', bottom: 60, transform: 'translateX(-50%)', zIndex: 15 }}>
        <motion.div
          initial={false}
          animate={beatIndex < 2 ? { scale: 1, opacity: 1 } : { scale: 0, opacity: 0 }}
          transition={{ duration: 0.3, ease: OVERSHOOT }}
          style={{ position: 'relative' }}
        >
          <MilkTea width={200} rotation={-3} shadow={10} variant={beatIndex >= 1 ? 'normal' : 'happy'} />
        </motion.div>
      </div>

      {/* 左下 reaction-shot 奶茶 — beat>=2 fade-in、縮小到 width 130、question variant + 浮動 ❓ */}
      {/* delay 0.2s 讓中央奶茶先淡出再進場、crossfade 不重疊太久 */}
      <motion.div
        initial={false}
        animate={beatIndex >= 2 ? { scale: 1, opacity: 1 } : { scale: 0.5, opacity: 0 }}
        transition={{ duration: 0.5, delay: 0.2, ease: OVERSHOOT }}
        style={{ position: 'absolute', left: 40, bottom: 40, zIndex: 15 }}
      >
        <div style={{ position: 'relative' }}>
          <MilkTea width={130} rotation={-3} shadow={8} variant="question" />

          {/* 浮動 ❓ — beat>=2 才 render；父層 div 是 position:relative，這裡 absolute anchor 到奶茶 */}
          {beatIndex >= 2 && [0, 1].map(i => (
            <motion.div
              key={i}
              initial={false}
              animate={{ y: [0, -50], opacity: [0, 1, 1, 0], scale: [0.5, 1, 1, 1] }}
              transition={{ duration: 1.6, repeat: Infinity, repeatType: 'loop', delay: i * 0.3, ease: 'easeOut' }}
              style={{
                position: 'absolute', top: -15, left: 40 + i * 35,
                fontSize: 28, fontWeight: 900, color: '#FF3B30',
                WebkitTextStroke: '2px #000', pointerEvents: 'none', zIndex: 16,
              }}
            >
              ?
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* 告白成功 ✓ sticker — 只在 beat 0 出現，beat>=1 scale+opacity 退場 */}
      <div style={{ position: 'absolute', left: '50%', bottom: 280, transform: 'translateX(-50%)', zIndex: 14 }}>
        <motion.div
          initial={false}
          animate={beatIndex < 1
            ? { scale: 1, opacity: 1, rotate: -8 }
            : { scale: 0, opacity: 0, rotate: 0 }}
          transition={{ duration: 0.4, ease: OVERSHOOT }}
          style={{
            background: '#FFD93D', color: '#000',
            padding: '12px 28px', border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
            fontWeight: 900, fontSize: 28,
            whiteSpace: 'nowrap',
          }}
        >
          告白成功 ✓
        </motion.div>
      </div>

      {/* 💗 粒子 — beat 0 啟動，beat>=1 停止生成（舊粒子讓動畫自然淡出） */}
      {hearts.map(h => (
        <div
          key={h.id}
          style={{
            position: 'absolute',
            left: `calc(50% + ${h.x}px)`, bottom: 240,
            transform: 'translateX(-50%)',
            pointerEvents: 'none', zIndex: 13,
          }}
        >
          <motion.div
            initial={{ y: 0, opacity: 1 }}
            animate={{ y: -180, opacity: 0 }}
            transition={{ duration: 2.0, ease: 'easeOut' }}
            style={{ fontSize: 36 }}
          >
            💗
          </motion.div>
        </div>
      ))}

      {/* 標題 — beat>=1 clip-path 從左刷出 */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1
          ? { clipPath: 'inset(-24px)', opacity: 1 }
          : { clipPath: 'inset(0px 100% 0px 0px)', opacity: 0 }}
        transition={{ duration: 0.8 }}
        style={{ fontWeight: 900, fontSize: '2.5rem' }}
      >
        以為穩了 · <span style={{ background: '#FF6B6B', color: '#FFF', padding: '4px 16px' }}>結果更多關卡等著奶茶</span>
      </motion.div>

      {/* 老油條 — beat>=1 從右上 spring-in */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1
          ? { scale: 1, opacity: 1, rotate: 4 }
          : { scale: 0, opacity: 0, rotate: 0 }}
        transition={{ duration: 0.5, delay: 0.2, ease: OVERSHOOT }}
        style={{ position: 'absolute', top: 48, right: 48, zIndex: 15 }}
      >
        <GirlVeteran width={200} rotation={0} shadow={10} />
      </motion.div>

      {/* 4 張陷阱題卡 — beat>=2 cascade */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 32 }}>
        {QUESTIONS.map((q, i) => (
          <motion.div
            key={i}
            initial={false}
            animate={beatIndex >= 2
              ? { scale: 1, opacity: 1, rotate: q.rotate, transition: { duration: 0.4, delay: 0.05 + i * 0.15, ease: OVERSHOOT } }
              : { scale: 0, opacity: 0, rotate: q.rotate }}
            whileHover={{
              scale: 1.1,
              rotate: q.rotate,
              boxShadow: '16px 16px 0 0 #000',
              transition: { duration: 0.2, ease: 'easeOut' },
            }}
            style={{
              background: q.bg, color: q.color,
              padding: '28px 36px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
              fontWeight: 900, fontSize: 24, textAlign: 'center', maxWidth: 360,
              cursor: 'pointer',
            }}
          >
            {q.text}
          </motion.div>
        ))}
      </div>
    </main>
  );
}
