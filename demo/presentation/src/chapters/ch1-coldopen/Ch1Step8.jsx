import { useEffect, useRef } from 'react';
import { motion, useAnimate } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { BoomDoubleRing } from '../../motifs/BoomDoubleRing.jsx';
import { YellowHighlight } from '../../motifs/YellowHighlight.jsx';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch1Step8() {
  const { beatIndex, advance, triggerShake } = usePresentationContext();
  const [stickersScope, animateStickers] = useAnimate();
  const firedClimaxRef = useRef(false);

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
      triggerShake();
    }
  }, [beatIndex, triggerShake]);

  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
    }}>
      {/* 3 background stickers + MRT — wrapped in stickersScope for shake animation */}
      <div ref={stickersScope} style={{
        position: 'absolute', inset: 0, opacity: 0.35,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <AssetPlaceholder type="[E]" width={720} height={400} todo="ch1 s8 捷運背景" />
        <div style={{ position: 'absolute', bottom: '14%', left: '8%' }}>
          <Sticker variant="sat-md" bg="secondary" rotation={-4} style={{ borderRadius: 24 }}>
            正妹發呆中
          </Sticker>
        </div>
        <div style={{ position: 'absolute', top: '14%', right: '8%' }}>
          <Sticker variant="sat-md" bg="muted" rotation={3}>
            Code Bullet
            <div style={{ fontSize: 16, marginTop: 4 }}>· flappy bird</div>
          </Sticker>
        </div>
        <div style={{ position: 'absolute', bottom: '14%', right: '8%' }}>
          <Sticker variant="sat-md" bg="accent" textColor="cream" rotation={2}>
            沒手機·解數獨
          </Sticker>
        </div>
      </div>

      {/* Beat 0+ : BoomDoubleRing covers center */}
      <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}>
        <BoomDoubleRing active={beatIndex >= 0} size={320} />
      </div>

      {/* Beat 1+ : Cream BOOM card with "訓 練 AI 解 數 獨" */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1
          ? { scale: 1, opacity: 1 }
          : { scale: 0.8, opacity: 0 }}
        transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ position: 'relative', zIndex: 30, rotate: -2 }}
      >
        <Sticker
          variant="hub-md"
          bg="cream"
          padding="40px 64px"
          style={{ lineHeight: 1.1, display: 'flex', alignItems: 'center', gap: 12 }}
        >
          訓 練
          <span style={{
            background: '#FF6B6B', color: '#FFFDF5',
            padding: '0 20px', border: '4px solid #000',
          }}>AI</span>
          解 數 獨
        </Sticker>
      </motion.div>

      {/* Beat 2 : Punchline yellow highlight box (placeholder before; mask-reveal text on beat 2)
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
          靈感就是這麼 <em style={{ fontStyle: 'normal', color: '#FF6B6B' }}>莫名其妙</em> 地蹦出來
        </YellowHighlight>

        {/* Placeholder underlying frame visible before beat 2 — shows users where the text will land. */}
        {beatIndex < 2 && (
          <div style={{
            position: 'absolute', inset: 0,
            border: '4px dashed #FFD93D',
            pointerEvents: 'none',
          }} />
        )}
      </motion.div>
    </div>
  );
}
