import { useEffect, useRef, useState } from 'react';
import { motion, useAnimate } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { SpotlightVignette } from '../../motifs/SpotlightVignette.jsx';
import { YellowHighlight } from '../../motifs/YellowHighlight.jsx';
import { AiSticker } from '../../components/AiSticker.jsx';

export default function Ch1Step8() {
  const { beatIndex, advance, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'C']);
  const [stickersScope, animateStickers] = useAnimate();
  const firedClimaxRef = useRef(false);
  const [aftermath, setAftermath] = useState(false);

  // Auto-advance from beat 0 → beat 1 after 400ms.
  useEffect(() => {
    if (beatIndex === 0) {
      const t = setTimeout(() => advance(), 400);
      return () => clearTimeout(t);
    }
  }, [beatIndex, advance]);

  // Beat 0 entry: shake the 3 background stickers (150ms).
  useEffect(() => {
    if (beatIndex === 0) {
      animateStickers(stickersScope.current,
        { x: [0, 4, -4, 2, -2, 0], y: [0, 2, -2, 1, -1, 0] },
        { duration: 0.15 }
      );
    }
  }, [beatIndex, animateStickers, stickersScope]);

  // Beat 2 (punchline reveal): trigger A (screen shake) + C (overshoot on punchline box).
  // C is implemented as scale keyframes on the punchline wrapper below.
  useEffect(() => {
    if (beatIndex === 2 && !firedClimaxRef.current) {
      firedClimaxRef.current = true;
      climax.play();
      triggerShake();
      const t = setTimeout(() => setAftermath(true), 700);
      return () => clearTimeout(t);
    }
  }, [beatIndex, climax, triggerShake]);

  const anticipationActive = beatIndex === 1;

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* 3 background stickers + MRT — wrapped in stickersScope for shake animation */}
      <div ref={stickersScope} style={{
        position: 'absolute', inset: 0, opacity: 0.35,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <img
          src="/images/ai/ch1/mrt-window.png"
          alt="台北捷運車廂內視"
          style={{
            position: 'absolute', inset: 0,
            width: '100%', height: '100%',
            objectFit: 'cover', objectPosition: 'center',
          }}
        />
        <motion.div
          animate={anticipationActive ? { rotate: [0, 0.5, -0.5, 0] } : { rotate: 0 }}
          transition={anticipationActive
            ? { duration: 1.6, repeat: Infinity, ease: 'linear', delay: 0 }
            : { duration: 0.2 }}
          style={{ position: 'absolute', bottom: '14%', left: '8%' }}
        >
          <AiSticker
            src="/images/ai/ch1/girl-daydream.png"
            alt="正妹發呆中"
            width={280}
            rotation={-4}
            shadow={8}
          />
        </motion.div>
        <motion.div
          animate={anticipationActive ? { rotate: [0, -0.5, 0.5, 0] } : { rotate: 0 }}
          transition={anticipationActive
            ? { duration: 1.6, repeat: Infinity, ease: 'linear', delay: 0.4 }
            : { duration: 0.2 }}
          style={{ position: 'absolute', top: '14%', right: '8%' }}
        >
          <AiSticker
            src="/images/ai/ch1/codebullet-flappy.png"
            alt="Code Bullet flappy bird"
            width={280}
            rotation={3}
            shadow={8}
          />
        </motion.div>
        <motion.div
          animate={anticipationActive ? { rotate: [0, 0.5, -0.5, 0] } : { rotate: 0 }}
          transition={anticipationActive
            ? { duration: 1.6, repeat: Infinity, ease: 'linear', delay: 0.8 }
            : { duration: 0.2 }}
          style={{ position: 'absolute', bottom: '14%', right: '8%' }}
        >
          <AiSticker
            src="/images/ai/ch1/soldier-sudoku.png"
            alt="軍人解數獨"
            width={280}
            rotation={2}
            shadow={8}
          />
        </motion.div>
      </div>

      {/* Beat 0+ : 聚光暈影 —— 壓暗四周忙碌的照片/貼紙，中央留亮，把焦點打在 punchline 卡片上 */}
      <SpotlightVignette active={beatIndex >= 0} />

      {/* Beat 1+ : Cream BOOM card with "訓 練 AI 解 數 獨" */}
      <motion.div
        initial={false}
        animate={
          beatIndex === 2 && aftermath
            ? { scale: 1, opacity: 1, rotate: 2 }
            : beatIndex >= 1
              ? { scale: 1, opacity: 1, rotate: 0 }
              : { scale: 0.8, opacity: 0, rotate: 0 }
        }
        transition={
          beatIndex === 2 && aftermath
            ? { duration: 0.35, ease: [0.22, 1, 0.36, 1] }
            : { duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }
        }
        style={{
          position: 'relative', zIndex: 30,
          background: '#FFFDF5', color: '#000',
          border: '6px solid #000',
          boxShadow: aftermath ? '12px 12px 0 0 #000' : '16px 16px 0 0 #000',
          padding: '40px 64px', rotate: -2,
          fontWeight: 900, fontSize: '4rem', lineHeight: 1.1,
          display: 'flex', alignItems: 'center', gap: 12,
          transition: 'box-shadow 0.35s cubic-bezier(0.22, 1, 0.36, 1)',
        }}
      >
        訓 練
        <span style={{
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '0 20px', border: '4px solid #000',
        }}>AI</span>
        解 數 獨
      </motion.div>

      {/* Beat 2 : Punchline yellow highlight box (mask-reveal text on beat 2)
          Wrapper also performs C overshoot (scale keyframes) when beatIndex hits 2. */}
      <motion.div
        animate={beatIndex === 2
          ? { scale: [0.85, 1.4, 1.0, 0.95, 1.0] }
          : { scale: 1 }}
        transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ marginTop: 56, position: 'relative', zIndex: 30 }}
      >
        <YellowHighlight
          active={beatIndex >= 2}
          padding="16px 32px"
          style={{ fontSize: '2.5rem' }}
        >
          靈感就這麼 <em style={{ fontStyle: 'normal', color: '#FF6B6B' }}>莫名其妙</em> 地蹦出來
        </YellowHighlight>
      </motion.div>
    </main>
  );
}
