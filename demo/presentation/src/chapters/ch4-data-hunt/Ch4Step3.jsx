import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { RedStamp } from '../../motifs/RedStamp.jsx';
import { InkSplatter } from '../../motifs/InkSplatter.jsx';

export default function Ch4Step3() {
  const { beatIndex, advance, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'C', 'E']);
  const firedRef = useRef(false);

  // 在 beat 2 點擊後 200ms 自動推進到 beat 3（顯示副標）
  useEffect(() => {
    if (beatIndex === 2) {
      const t = setTimeout(() => advance(), 200);
      return () => clearTimeout(t);
    }
  }, [beatIndex, advance]);

  // beat 2 觸發 climax（A 震動 + C overshoot + E ink-splatter），只觸發一次
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
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Beat 0+ : kicker hero「終極目標：去每個數獨網站霸榜」 */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { y: 0, opacity: 1 } : { y: -40, opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          position: 'absolute', top: 80, left: 0, right: 0, textAlign: 'center',
          fontWeight: 900, fontSize: '2.5rem',
        }}
      >
        終極目標：去每個數獨網站霸榜
      </motion.div>

      {/* Beat 1+ : URL websudoku.com sticker 從左側 slide-in */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1 ? { x: 0, opacity: 1 } : { x: -200, opacity: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        style={{
          background: '#000', color: '#FFFDF5',
          padding: '16px 32px', border: '4px solid #000',
          fontFamily: 'monospace', fontWeight: 700, fontSize: 28,
          display: 'flex', alignItems: 'center', gap: 8,
        }}
      >
        websudoku.com
        <motion.span
          animate={{ opacity: [1, 0] }}
          transition={{ duration: 0.6, repeat: Infinity, ease: 'steps(2)' }}
          style={{ color: '#FF6B6B' }}
        >_</motion.span>
      </motion.div>

      {/* Beat 2+ : 受害者紅 stamp 填入 + ink-splatter (A+C+E climax) */}
      <div style={{ marginTop: 48, position: 'relative' }}>
        {beatIndex >= 2 && (
          <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
            <InkSplatter active count={8} radius={100} centerX="50%" centerY="50%" />
          </div>
        )}
        <RedStamp active={beatIndex >= 2} rotation={4} size="medium">這個受害者</RedStamp>
      </div>

      {/* Beat 3+ : 副標「簡簡單單被我攻破」fade-up */}
      <motion.div
        initial={false}
        animate={beatIndex >= 3 ? { y: 0, opacity: 1 } : { y: 20, opacity: 0 }}
        transition={{ duration: 0.4 }}
        style={{
          marginTop: 32, fontWeight: 700, fontSize: '1.5rem', color: '#666',
        }}
      >
        簡簡單單被我攻破
      </motion.div>
    </main>
  );
}
