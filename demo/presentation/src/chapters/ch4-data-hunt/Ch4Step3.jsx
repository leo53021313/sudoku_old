import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { RedStamp } from '../../motifs/RedStamp.jsx';

export default function Ch4Step3() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'C']);
  const firedRef = useRef(false);

  // beat 2 觸發 climax（A 震動 + C overshoot），只觸發一次。
  // 延遲到 stamp 落定時才震 —— 讓觀眾先看清網站截圖，再被「這個受害者」蓋章砸下。
  useEffect(() => {
    if (beatIndex === 2 && !firedRef.current) {
      firedRef.current = true;
      const t = setTimeout(() => { climax.play(); triggerShake(); }, 650);
      return () => clearTimeout(t);
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

      {/* Beat 1+ : URL websudoku.com sticker 從下方滑入並往上移定位。
          beat 2 之後再往上挪一截，讓出下方空間給受害者截圖。 */}
      <motion.div
        initial={false}
        animate={
          beatIndex >= 2 ? { y: -32, opacity: 1 }
          : beatIndex >= 1 ? { y: 0, opacity: 1 }
          : { y: 60, opacity: 0 }
        }
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

      {/* 受害者舞台 —— beat 2「網站真實截圖 + 受害者紅 stamp」合在一起；
          beat 3 截圖 fade away，由副標「簡簡單單被我攻破」取代。 */}
      <div style={{
        position: 'relative', marginTop: 16,
        width: 1080, height: 600,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        {/* Beat 2 : 截圖 + stamp 合體；beat 3 整塊 fade away */}
        <motion.div
          initial={false}
          animate={beatIndex === 2 ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.92 }}
          transition={{ duration: 0.45, ease: 'easeOut' }}
          style={{
            position: 'absolute', inset: 0,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            pointerEvents: 'none',
          }}
        >
          <div style={{ position: 'relative', transform: 'rotate(-2deg)' }}>
            <img
              src="/images/ch4/websudoku.png"
              alt="websudoku.com 網站截圖"
              style={{
                display: 'block', width: 1000,
                border: '6px solid #000', boxShadow: '16px 16px 0 0 #000',
              }}
            />
            {/* 受害者紅 stamp —— 蓋在右下角邊緣（不擋截圖主體），delay 後才砸下，讓觀眾先看截圖。
                climax C overshoot 在 stamp 落定時彈跳（同 ch1 s8 pattern）。 */}
            <motion.div
              animate={beatIndex === 2
                ? { scale: [0.85, 1.4, 1.0, 0.95, 1.0] }
                : { scale: 1 }}
              transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1], delay: beatIndex === 2 ? 0.65 : 0 }}
              style={{ position: 'absolute', bottom: -44, right: -36, zIndex: 30 }}
            >
              <RedStamp active={beatIndex >= 2} rotation={-8} size="medium" delay={0.65} nowrap>這個受害者</RedStamp>
            </motion.div>
          </div>
        </motion.div>

        {/* Beat 3 : 截圖 fade away 後，由副標「簡簡單單被我攻破」取代（稍延遲淡入做交接） */}
        <motion.div
          initial={false}
          animate={beatIndex >= 3 ? { y: 0, opacity: 1 } : { y: 24, opacity: 0 }}
          transition={{ duration: 0.45, delay: beatIndex >= 3 ? 0.2 : 0 }}
          style={{
            position: 'absolute', inset: 0,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            textAlign: 'center', fontWeight: 900, fontSize: '3rem', lineHeight: 1.2,
          }}
        >
          簡簡單單被我攻破
        </motion.div>
      </div>
    </main>
  );
}
