import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { SpotlightVignette } from '../../motifs/SpotlightVignette.jsx';
import { GirlVeteran } from '../../motifs/GirlVeteran.jsx';

export default function Ch7Step7() {
  const { beatIndex, advance, triggerShake } = usePresentationContext();
  const climaxA = useClimax(['A', 'G']);  // beat 3
  const climaxB = useClimax(['A', 'G']);  // beat 4
  const climaxBoth = useClimax(['B']);         // beat 5 (double burst)
  const firedA = useRef(false);
  const firedB = useRef(false);
  const firedBoth = useRef(false);

  // Auto-advance from beat 4 → beat 5 after 400ms
  useEffect(() => {
    if (beatIndex === 4) {
      const t = setTimeout(() => advance(), 400);
      return () => clearTimeout(t);
    }
  }, [beatIndex, advance]);

  useEffect(() => {
    if (beatIndex === 3 && !firedA.current) {
      firedA.current = true;
      climaxA.play();
      triggerShake();
    }
    if (beatIndex === 4 && !firedB.current) {
      firedB.current = true;
      climaxB.play();
      triggerShake();
    }
    if (beatIndex === 5 && !firedBoth.current) {
      firedBoth.current = true;
      climaxBoth.play();
    }
  }, [beatIndex, climaxA, climaxB, climaxBoth, triggerShake]);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 24,
    }}>
      <SpotlightVignette active={climaxA.activeFX.G || climaxB.activeFX.G} />

      {/* The 'asker' character — appears on beat 0 alongside hero */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0
          ? { scale: 1, opacity: 1, rotate: 4 }
          : { scale: 0, opacity: 0, rotate: 0 }}
        transition={{ duration: 0.5, delay: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', top: 48, right: 48, zIndex: 15,
        }}
      >
        <GirlVeteran width={200} rotation={0} shadow={10} />
      </motion.div>

      {/* Beat 0: hero */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { clipPath: 'inset(-24px)', opacity: 1 } : { clipPath: 'inset(0px 100% 0px 0px)', opacity: 0 }}
        transition={{ duration: 0.8 }}
        style={{
          fontWeight: 900, fontSize: '3rem',
        }}
      >
        <span style={{ background: '#FFD93D', padding: '4px 24px', border: '6px solid #000', boxShadow: '8px 8px 0 0 #000' }}>
          女生陷阱題
        </span>
      </motion.div>

      <div style={{ display: 'flex', gap: 48, marginTop: 32 }}>
        {/* Beat 1: trap 1 left */}
        <motion.div
          initial={false}
          animate={beatIndex >= 1 ? { rotate: -3, x: 0, opacity: 1 } : { rotate: -30, x: -200, opacity: 0 }}
          transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            background: '#FF6B6B', color: '#FFF',
            padding: '24px 32px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            fontWeight: 900, fontSize: '1.5rem', maxWidth: 320, lineHeight: 1.3, textAlign: 'center',
          }}
        >
          和你媽一起<br/>掉進水裡<br/>你會先救誰？
        </motion.div>

        {/* Beat 2: trap 2 right */}
        <motion.div
          initial={false}
          animate={beatIndex >= 2 ? { rotate: 4, x: 0, opacity: 1 } : { rotate: 30, x: 200, opacity: 0 }}
          transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            background: '#C4B5FD', color: '#000',
            padding: '24px 32px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            fontWeight: 900, fontSize: '1.5rem', maxWidth: 320, lineHeight: 1.3, textAlign: 'center',
          }}
        >
          你覺得我<br/>該不該去<br/>運動？
        </motion.div>
      </div>

      {/* Answer arrows + placeholders — 整列等到 beat 2「你覺得我該不該去運動」出現後才顯示 */}
      <div style={{ display: 'flex', gap: 48, marginTop: 32 }}>
        <motion.div
          initial={false}
          animate={{ opacity: beatIndex >= 2 ? 1 : 0 }}
          transition={{ duration: 0.4 }}
          style={{ minWidth: 340, textAlign: 'center', fontWeight: 700, fontSize: 18 }}
        >
          說要 →
          <motion.span
            initial={false}
            animate={beatIndex >= 3
              ? { scale: [0.9, 1.2, 1], opacity: 1 }
              : { scale: 0.9, opacity: beatIndex >= 2 ? 0.4 : 0 }}
            transition={{ duration: 0.4 }}
            style={{
              marginLeft: 8,
              background: '#FF6B6B', color: '#FFF',
              padding: '4px 12px', border: '4px solid #000',
              display: 'inline-block',
            }}
          >
            {beatIndex >= 3 ? '❌ 嫌那個女生胖' : '❌ ???'}
          </motion.span>
        </motion.div>
        <motion.div
          initial={false}
          animate={{ opacity: beatIndex >= 2 ? 1 : 0 }}
          transition={{ duration: 0.4 }}
          style={{ minWidth: 340, textAlign: 'center', fontWeight: 700, fontSize: 18 }}
        >
          說不用 →
          <motion.span
            initial={false}
            animate={beatIndex >= 4
              ? { scale: [0.9, 1.2, 1], opacity: 1 }
              : { scale: 0.9, opacity: beatIndex >= 2 ? 0.4 : 0 }}
            transition={{ duration: 0.4 }}
            style={{
              marginLeft: 8,
              background: '#FF6B6B', color: '#FFF',
              padding: '4px 12px', border: '4px solid #000',
              display: 'inline-block',
            }}
          >
            {beatIndex >= 4 ? '❌ 你不關心健康' : '❌ ???'}
          </motion.span>
        </motion.div>
      </div>

      {beatIndex >= 5 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4 }}
          style={{
            marginTop: 32, fontWeight: 900, fontSize: 24,
            background: '#FFD93D', color: '#000',
            padding: '12px 28px', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          }}
        >
          兩面不討好
        </motion.div>
      )}
    </main>
  );
}
