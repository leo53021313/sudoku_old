import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { ComicSpeedLines } from '../../motifs/ComicSpeedLines.jsx';
import { ImpactDust } from '../../motifs/ImpactDust.jsx';
import { StarburstShards } from '../../motifs/StarburstShards.jsx';
import { SpotlightVignette } from '../../motifs/SpotlightVignette.jsx';

const FOOTER_TEXT = '我這兩個月一直用班上的電腦 · 瘋狂訓練我的 AI';

// beat 2 爆點視覺切換：1 = 漫畫集中線、2 = 印章從天砸下+塵爆、3 = 星爆 POW 碎片。
// 改這個數字後重整頁面即可比較三種效果。
const CLIMAX_VARIANT = 1;

export default function Ch9Step13() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'B', 'C', 'G']);
  const firedRef = useRef(false);

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
      <SpotlightVignette active={climax.activeFX.G} />

      {/* Beat 0+ kicker */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { y: 0, opacity: 1 } : { y: -20, opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          position: 'absolute', top: 64,
          fontWeight: 700, fontSize: '1.5rem', color: '#666',
        }}
      >
        最後再補個笑話 ⋯
      </motion.div>

      {/* Beat 1+ salary-thief sticker — beat 2 起被「踢飛」出畫面，讓位給集中線爆點 */}
      <motion.div
        initial={false}
        animate={
          beatIndex >= 2
            ? { x: 1500, y: -560, rotate: 520, scale: 0.8, opacity: 0 }
            : beatIndex >= 1
              ? { x: 0, y: 0, rotate: 2, scale: 1, opacity: 1 }
              : { x: 0, y: 0, rotate: 2, scale: 0.85, opacity: 0 }
        }
        transition={beatIndex >= 2
          ? { duration: 0.45, ease: [0.5, 0, 0.85, 0.3] }
          : { duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '20px 36px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          fontWeight: 900, fontSize: '1.75rem',
        }}
      >
        想必大家未來出職場後都是 · 薪水小偷
      </motion.div>

      {/* Beat 2+: morph from placeholder "我不一樣 → ?" → FINAL "電費小偷" stamp */}
      <div style={{ position: 'relative', zIndex: 30 }}>
        {/* 爆點背景視覺（依 CLIMAX_VARIANT 切換），墊在印章後方 */}
        {beatIndex >= 2 && (
          <div style={{
            position: 'absolute', left: '50%', top: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: -1,
          }}>
            {CLIMAX_VARIANT === 1 && <ComicSpeedLines active size={1100} delay={0.28} receded={beatIndex >= 3} />}
            {CLIMAX_VARIANT === 3 && <StarburstShards active />}
          </div>
        )}
        {beatIndex >= 2 && CLIMAX_VARIANT === 2 && <ImpactDust active />}

        <motion.div
          animate={beatIndex === 2
            ? (CLIMAX_VARIANT === 2
                ? { y: [-460, 0, -26, 0], scale: 1 }
                : { scale: [0.85, 1.5, 1.0, 0.95, 1.0] })
            : { scale: beatIndex >= 1 ? 1 : 0, y: 0 }}
          transition={{ duration: CLIMAX_VARIANT === 2 ? 0.55 : 0.6, ease: [0.34, 1.56, 0.64, 1] }}
        >
          <div style={{
            background: beatIndex >= 2 ? '#FF6B6B' : '#FFFDF5',
            color: beatIndex >= 2 ? '#FFFDF5' : '#000',
            padding: '40px 72px', border: '8px solid #000', boxShadow: '20px 20px 0 0 #000',
            fontWeight: 900, fontSize: beatIndex >= 2 ? '5rem' : '2.25rem', rotate: -3, lineHeight: 1.2,
            textAlign: 'center', minWidth: 480,
            transition: 'background 0.3s, color 0.3s, font-size 0.3s',
          }}>
            {beatIndex >= 2 ? (
              <>
                但我不一樣 · 我是
                <br/>
                電費小偷
              </>
            ) : (
              <>我不一樣 → <span style={{ color: '#FF6B6B' }}>?</span></>
            )}
          </div>
        </motion.div>
      </div>

      {/* Beat 3+ footer type-in + END */}
      {beatIndex >= 3 && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            style={{
              position: 'absolute', bottom: 96,
              fontWeight: 700, fontSize: '1.25rem', color: '#000',
              textAlign: 'center', maxWidth: 800,
            }}
          >
            <TypeIn text={FOOTER_TEXT} duration={1.5} />
          </motion.div>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 2.0 }}
            style={{
              position: 'absolute', bottom: 32, right: 32,
              fontWeight: 900, fontSize: 20, color: '#000', letterSpacing: '0.2em',
            }}
          >
            — END —
          </motion.div>
        </>
      )}
    </main>
  );
}

function TypeIn({ text, duration = 1.5 }) {
  // Render characters with stagger via clipPath
  return (
    <motion.span
      initial={{ clipPath: 'inset(0 100% 0 0)' }}
      animate={{ clipPath: 'inset(0 0 0 0)' }}
      transition={{ duration, ease: 'linear' }}
      style={{ display: 'inline-block' }}
    >
      {text}
    </motion.span>
  );
}
