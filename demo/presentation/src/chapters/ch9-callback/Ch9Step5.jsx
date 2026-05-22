import { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { MilkTea } from '../../motifs/MilkTea.jsx';

const OVERSHOOT = [0.34, 1.56, 0.64, 1];

// 粒子發射位置（label 中心點下方）
const PLUS_SPAWN = { left: '15%', top: 70 };
const MINUS_SPAWN = { left: '85%', top: 70 };
// 大腦泡泡中心（粒子飛行目的地）
const BUBBLE_CENTER_X = '50%';
const BUBBLE_CENTER_Y = '35%';

export default function Ch9Step5() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'C']);
  const firedRef = useRef(false);
  const brainFlashTimerRef = useRef(null);
  const [pluses, setPluses] = useState([]);
  const [minuses, setMinuses] = useState([]);
  const [aftermath, setAftermath] = useState(false);
  const [brainFlash, setBrainFlash] = useState(null); // 'plus' | 'minus' | null

  // + 粒子在 beat 1~2 期間連發；beat 3 起停止 spawn（殘留在飛的粒子會自然飛完）
  useEffect(() => {
    if (beatIndex < 1 || beatIndex >= 3) return;
    let id = 0;
    const t = setInterval(() => {
      setPluses(p => [...p, { id: id++ }].slice(-10));
    }, 300);
    return () => clearInterval(t);
  }, [beatIndex]);

  // beat 3：− 粒子從紅 label 連發飛向大腦泡泡
  useEffect(() => {
    if (beatIndex < 3) return;
    let id = 0;
    const t = setInterval(() => {
      setMinuses(m => [...m, { id: id++ }].slice(-10));
    }, 300);
    return () => clearInterval(t);
  }, [beatIndex]);

  // beat 4：climax + shake + aftermath（沿用既有結構）
  useEffect(() => {
    if (beatIndex === 4 && !firedRef.current) {
      firedRef.current = true;
      climax.play();
      triggerShake();
      const t = setTimeout(() => setAftermath(true), 700);
      return () => clearTimeout(t);
    }
  }, [beatIndex, climax, triggerShake]);

  // 奶茶 variant：beat 0-1 normal / beat 2-3 happy / beat 4 crashed
  const milkTeaVariant =
    beatIndex >= 4 ? 'crashed'
    : beatIndex >= 2 ? 'happy'
    : 'normal';

  // 奶茶 motion：beat 2 前傾 / beat 4 下沉
  const milkTeaAnimate =
    beatIndex >= 4 ? { y: 16, rotate: -5, scale: 0.95, filter: 'grayscale(0.7)' }
    : beatIndex >= 2 ? { y: -8, rotate: 2, scale: 1.05, filter: 'grayscale(0)' }
    : { y: 0, rotate: -3, scale: 1, filter: 'grayscale(0)' };

  // 大腦在 climax 時褪色
  const bubbleFilter = beatIndex >= 4 ? 'grayscale(1)' : 'none';

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* 「回訊息」綠 label（beat 1+） */}
      {beatIndex >= 1 && (
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.4, ease: OVERSHOOT }}
          style={{
            position: 'absolute', top: 40, left: '8%',
            fontWeight: 900, fontSize: 32, background: '#10B981', color: '#FFF',
            padding: '14px 32px', border: '6px solid #000', boxShadow: '9px 9px 0 0 #000',
            zIndex: 12,
          }}
        >回訊息</motion.div>
      )}

      {/* 「已讀不回」紅 label（beat 3+） */}
      {beatIndex >= 3 && (
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.4, ease: OVERSHOOT }}
          style={{
            position: 'absolute', top: 40, right: '8%',
            fontWeight: 900, fontSize: 32, background: '#FF6B6B', color: '#FFF',
            padding: '14px 32px', border: '6px solid #000', boxShadow: '9px 9px 0 0 #000',
            zIndex: 12,
          }}
        >已讀不回</motion.div>
      )}

      {/* 思考泡泡 + 大腦（beat 0+） */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0
          ? { scale: 1, opacity: 1, x: '-50%' }
          : { scale: 0, opacity: 0, x: '-50%' }}
        transition={{ duration: 0.5, ease: OVERSHOOT }}
        style={{
          position: 'absolute', top: '15%', left: '50%',
          filter: bubbleFilter,
          transition: 'filter 0.6s ease',
          zIndex: 10,
        }}
      >
        {/* 思考泡泡 — 圓邊框（整個泡泡 + brain 同步閃爍） */}
        <motion.div
          animate={brainFlash === 'plus'
            ? { scale: [1, 1.04, 1], boxShadow: '0 0 0 10px rgba(16,185,129,0.55), 8px 8px 0 0 #000' }
            : brainFlash === 'minus'
              ? { scale: 1, x: [-3, 3, -2, 0], boxShadow: '0 0 0 10px rgba(255,107,107,0.55), 8px 8px 0 0 #000' }
              : { scale: 1, x: 0, boxShadow: '0 0 0 0 transparent, 8px 8px 0 0 #000' }}
          transition={{ duration: 0.25 }}
          style={{
            width: 240, height: 240,
            background: '#FFFDF5',
            border: '6px solid #000',
            borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* 大腦 sticker（內嵌、縮小避免溢出圓邊；自身也輕微脈衝呼應外圈 flash） */}
          <motion.img
            src="/images/ai/ch9/brain-reward.png"
            alt="大腦"
            animate={brainFlash === 'plus'
              ? { scale: [1, 1.08, 1] }
              : brainFlash === 'minus'
                ? { scale: [1, 0.96, 1] }
                : { scale: 1 }}
            transition={{ duration: 0.25 }}
            style={{ width: 150, height: 'auto' }}
          />
        </motion.div>

        {/* 思考泡泡尾巴 — 兩個小圓朝奶茶頭頂方向 */}
        <div style={{
          position: 'absolute', bottom: -20, left: '30%',
          width: 18, height: 18, borderRadius: '50%',
          background: '#FFFDF5', border: '4px solid #000',
        }} />
        <div style={{
          position: 'absolute', bottom: -42, left: '24%',
          width: 10, height: 10, borderRadius: '50%',
          background: '#FFFDF5', border: '3px solid #000',
        }} />
      </motion.div>

      {/* 奶茶（中央偏下、隨 beat 變 variant + 動作） */}
      <motion.div
        initial={false}
        animate={{ ...milkTeaAnimate, opacity: beatIndex >= 0 ? 1 : 0, x: '-50%' }}
        transition={{ duration: 0.5, ease: OVERSHOOT }}
        style={{
          position: 'absolute', bottom: '28%', left: '50%',
          zIndex: 11,
        }}
      >
        <MilkTea width={200} rotation={0} shadow={10} variant={milkTeaVariant} />

        {/* beat 2 / 3 happy 時頭旁飄 ✨ */}
        {(beatIndex === 2 || beatIndex === 3) && (
          <>
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1, y: [0, -8, 0] }}
              transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
              style={{
                position: 'absolute', top: 10, left: -28,
                fontSize: 28, color: '#FFD93D',
                WebkitTextStroke: '2px #000', fontWeight: 900,
              }}
            >✦</motion.div>
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1, y: [0, -10, 0] }}
              transition={{ duration: 1.4, repeat: Infinity, ease: 'easeInOut', delay: 0.3 }}
              style={{
                position: 'absolute', top: 20, right: -28,
                fontSize: 24, color: '#FFD93D',
                WebkitTextStroke: '2px #000', fontWeight: 900,
              }}
            >✦</motion.div>
          </>
        )}
      </motion.div>

      {/* + 粒子（綠 label → 大腦泡泡） */}
      {pluses.map(p => (
        <motion.div
          key={`plus-${p.id}`}
          initial={{ left: PLUS_SPAWN.left, top: PLUS_SPAWN.top, opacity: 1, scale: 1 }}
          animate={{ left: BUBBLE_CENTER_X, top: BUBBLE_CENTER_Y, opacity: [1, 1, 0], scale: [1, 1, 0.5] }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
          onAnimationComplete={() => {
            clearTimeout(brainFlashTimerRef.current);
            setBrainFlash('plus');
            brainFlashTimerRef.current = setTimeout(() => setBrainFlash(null), 250);
          }}
          style={{
            position: 'absolute',
            fontSize: 42, fontWeight: 900, color: '#10B981',
            WebkitTextStroke: '3px black',
            zIndex: 9, pointerEvents: 'none',
          }}
        >+</motion.div>
      ))}

      {/* − 粒子（紅 label → 大腦泡泡） */}
      {minuses.map(m => (
        <motion.div
          key={`minus-${m.id}`}
          initial={{ left: MINUS_SPAWN.left, top: MINUS_SPAWN.top, opacity: 1, scale: 1 }}
          animate={{ left: BUBBLE_CENTER_X, top: BUBBLE_CENTER_Y, opacity: [1, 1, 0], scale: [1, 1, 0.5] }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
          onAnimationComplete={() => {
            clearTimeout(brainFlashTimerRef.current);
            setBrainFlash('minus');
            brainFlashTimerRef.current = setTimeout(() => setBrainFlash(null), 250);
          }}
          style={{
            position: 'absolute',
            fontSize: 42, fontWeight: 900, color: '#FF6B6B',
            WebkitTextStroke: '3px black',
            zIndex: 9, pointerEvents: 'none',
          }}
        >−</motion.div>
      ))}

      {/* Beat 4 punchline */}
      <motion.div
        initial={false}
        animate={
          beatIndex >= 4
            ? aftermath
              ? { scale: 1, opacity: 1, y: 0, rotate: 1 }
              : { scale: 1, opacity: 1, y: 0, rotate: 0 }
            : { scale: 0.85, opacity: 0, y: 100, rotate: 0 }
        }
        transition={beatIndex >= 4 && aftermath
          ? { duration: 0.35, ease: [0.22, 1, 0.36, 1] }
          : { duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: 64, left: 0, right: 0, textAlign: 'center',
          zIndex: 20,
        }}
      >
        <span style={{
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '24px 48px', border: '8px solid #000',
          boxShadow: aftermath ? '12px 12px 0 0 #000' : '16px 16px 0 0 #000',
          fontWeight: 900, fontSize: '3.5rem', display: 'inline-block', rotate: '-2deg',
          transition: 'box-shadow 0.35s cubic-bezier(0.22, 1, 0.36, 1)',
        }}>
          跟 AI 訓練一模一樣
        </span>
      </motion.div>
    </main>
  );
}
