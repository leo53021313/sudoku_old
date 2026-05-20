import { motion } from 'motion/react';
import { useState, useEffect } from 'react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';

// 三個 beat（左鍵點擊推進，取代原本的 9s setTimeout）：
//   beat 0 → 極度的 I 人（100% I 圓餅）
//   beat 1 → 明明我很 E（黃色貼紙吐槽）
//   beat 2 → 業務工作（I→E 進度條跑完 4s 後，右邊才浮出 30% I 圓餅）
export default function Ch9Step10() {
  const { beatIndex } = usePresentationContext();
  const isPhase2 = beatIndex >= 2;
  // 進度條 4s 動畫跑完才顯示右邊的 30% 圓餅；退回 beat 時重置
  const [barDone, setBarDone] = useState(false);
  useEffect(() => {
    if (!isPhase2) setBarDone(false);
  }, [isPhase2]);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 24,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        style={{ fontWeight: 900, fontSize: '2rem' }}
      >
        我真的是一個 <span style={{ background: '#C4B5FD', padding: '0 16px', border: '4px solid #000' }}>極度的 I 人</span>
      </motion.div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 48, marginTop: 24 }}>
        {/* beat 0/1：100% I 圓餅 + 極度 I 人貼紙（beat 2 整組收起） */}
        {!isPhase2 && (
          <>
            <svg width={240} height={240} viewBox="0 0 100 100" style={{ flex: '0 0 auto' }}>
              <circle cx="50" cy="50" r="45" fill="#FFFDF5" stroke="#000" strokeWidth="6" />
              <motion.circle
                cx="50" cy="50" r="45" fill="#C4B5FD" stroke="#000" strokeWidth="6"
                initial={{ strokeDasharray: '0 283', strokeDashoffset: 0 }}
                animate={{ strokeDasharray: '283 0', strokeDashoffset: 0 }}
                transition={{ duration: 1.5 }}
                style={{ transformOrigin: 'center', transform: 'rotate(-90deg)' }}
              />
              {/* donut hole：白底蓋掉切片黑線，細內框；加大半徑讓數字不被遮 */}
              <circle cx="50" cy="50" r="32" fill="#FFFDF5" stroke="#000" strokeWidth="2" />
              <text x="50" y="50" textAnchor="middle" dominantBaseline="central"
                fontWeight="900" fontSize="16" fontFamily="Space Grotesk" fill="#000">
                I 100%
              </text>
            </svg>

            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5, delay: 1.6, ease: [0.34, 1.56, 0.64, 1] }}
              style={{
                background: '#C4B5FD', color: '#000',
                padding: '24px 40px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
                fontWeight: 900, fontSize: 28, rotate: -3,
              }}
            >
              極度 I 人
            </motion.div>
          </>
        )}

        {/* beat 2：業務工作貼紙 + I→E 進度條 +（4s 後）右邊 30% 圓餅 */}
        {isPhase2 && (
          <>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
              style={{
                background: '#FFD93D', color: '#000',
                padding: '20px 36px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
                fontWeight: 900, fontSize: 28, rotate: 2,
              }}
            >
              業務工作
            </motion.div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <div style={{ position: 'relative', width: 280, height: 40, background: '#FFFDF5', border: '4px solid #000' }}>
                <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: '30%', background: '#C4B5FD' }} />
                <div style={{ position: 'absolute', right: 0, top: 0, bottom: 0, width: '40%', background: '#FF6B6B' }} />
                <motion.div
                  initial={{ left: '0%' }}
                  animate={{ left: '60%' }}
                  transition={{ duration: 4, ease: 'easeInOut' }}
                  onAnimationComplete={() => setBarDone(true)}
                  style={{
                    position: 'absolute', top: -4, width: 12, height: 48,
                    background: '#000', border: '2px solid #FFFDF5',
                  }}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700, fontSize: 14 }}>
                <span>I 0%</span><span>E 100%</span>
              </div>
            </div>

            {/* 進度條跑完才浮出的 30% I 圓餅 */}
            {barDone && (
              <motion.svg
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
                width={150} height={150} viewBox="0 0 100 100" style={{ flex: '0 0 auto' }}
              >
                <circle cx="50" cy="50" r="45" fill="#FFFDF5" stroke="#000" strokeWidth="6" />
                <path d="M 50 5 A 45 45 0 0 1 90 65 L 50 50 Z" fill="#C4B5FD" stroke="#000" strokeWidth="6" />
                {/* donut hole：白底蓋掉切片黑線，細內框；加大半徑讓數字不被遮 */}
                <circle cx="50" cy="50" r="32" fill="#FFFDF5" stroke="#000" strokeWidth="2" />
                <text x="50" y="50" textAnchor="middle" dominantBaseline="central"
                  fontWeight="900" fontSize="16" fontFamily="Space Grotesk" fill="#000">
                  I 30%
                </text>
              </motion.svg>
            )}
          </>
        )}
      </div>

      {/* beat 1：明明我很 E（beat 2 換成解釋字幕） */}
      {beatIndex === 1 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
          style={{ fontWeight: 700, fontSize: '1.5rem' }}
        >
          <span style={{ background: '#FFD93D', padding: '2px 12px', border: '4px solid #000' }}>明明我很 E</span>
        </motion.div>
      )}

      {/* beat 2：解釋字幕 */}
      {isPhase2 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          style={{ fontWeight: 700, fontSize: '1.25rem', color: '#666', textAlign: 'center', marginTop: 16 }}
        >
          天天逼自己跟陌生人講話 · 才慢慢變得比較 E
        </motion.div>
      )}
    </main>
  );
}
