import { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { AiSticker } from '../../components/AiSticker.jsx';
import { GirlNew } from '../../motifs/GirlNew.jsx';

export default function Ch9Step5() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'C']);
  const firedRef = useRef(false);
  const [pluses, setPluses] = useState([]);
  const [minuses, setMinuses] = useState([]);

  useEffect(() => {
    if (beatIndex >= 1) {
      let id = 0;
      const t = setInterval(() => {
        setPluses(p => [...p, { id: id++, x: Math.random() * 40 + 10 }].slice(-10));
      }, 350);
      return () => clearInterval(t);
    }
  }, [beatIndex]);

  useEffect(() => {
    if (beatIndex >= 2) {
      let id = 0;
      const t = setInterval(() => {
        setMinuses(m => [...m, { id: id++, x: Math.random() * 40 + 50 }].slice(-10));
      }, 350);
      return () => clearInterval(t);
    }
  }, [beatIndex]);

  useEffect(() => {
    if (beatIndex === 3 && !firedRef.current) {
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
      {/* Beat 0+ background girl-new callback (grayscale ghost) */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { opacity: 0.3 } : { opacity: 0 }}
        transition={{ duration: 0.6 }}
        style={{
          position: 'absolute', inset: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          filter: 'grayscale(1)',
          pointerEvents: 'none',
        }}
      >
        <GirlNew width={340} rotation={-4} shadow={14} />
      </motion.div>

      {/* Beat 0+ brain center — AI brain-reward sticker */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { scale: 1, opacity: 1 } : { scale: 0, opacity: 0 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ zIndex: 10 }}
      >
        <AiSticker
          src="/images/ai/ch9/brain-reward.png"
          alt="大腦與獎懲 token"
          width={320}
          rotation={0}
          shadow={12}
        />
      </motion.div>

      {/* Beat 1+ left positives */}
      {beatIndex >= 1 && (
        <div style={{ position: 'absolute', top: 0, bottom: 0, left: '5%', width: '40%' }}>
          <div style={{
            position: 'absolute', top: 80,
            fontWeight: 900, fontSize: 20, background: '#10B981', color: '#FFF',
            padding: '8px 20px', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          }}>回訊息</div>
          {pluses.map(p => (
            <motion.div
              key={p.id}
              initial={{ y: 0, opacity: 1 }}
              animate={{ y: -400, opacity: 0 }}
              transition={{ duration: 2.5, ease: 'easeOut' }}
              style={{
                position: 'absolute', bottom: 0, left: `${p.x}%`,
                fontSize: 40, fontWeight: 900, color: '#10B981',
                WebkitTextStroke: '2px black',
              }}
            >+</motion.div>
          ))}
        </div>
      )}

      {/* Beat 2+ right negatives */}
      {beatIndex >= 2 && (
        <div style={{ position: 'absolute', top: 0, bottom: 0, right: '5%', width: '40%' }}>
          <div style={{
            position: 'absolute', top: 80, right: 0,
            fontWeight: 900, fontSize: 20, background: '#FF6B6B', color: '#FFF',
            padding: '8px 20px', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          }}>已讀不回</div>
          {minuses.map(m => (
            <motion.div
              key={m.id}
              initial={{ y: -300, opacity: 1 }}
              animate={{ y: 400, opacity: 0 }}
              transition={{ duration: 2.5, ease: 'easeIn' }}
              style={{
                position: 'absolute', top: 0, right: `${m.x}%`,
                fontSize: 40, fontWeight: 900, color: '#FF6B6B',
                WebkitTextStroke: '2px black',
              }}
            >–</motion.div>
          ))}
        </div>
      )}

      {/* Beat 3 punchline */}
      <motion.div
        initial={false}
        animate={beatIndex >= 3
          ? { scale: 1, opacity: 1, y: 0 }
          : { scale: 0.85, opacity: 0, y: 100 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: 64, left: 0, right: 0, textAlign: 'center',
          zIndex: 20,
        }}
      >
        <span style={{
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '24px 48px', border: '8px solid #000', boxShadow: '16px 16px 0 0 #000',
          fontWeight: 900, fontSize: '3.5rem', display: 'inline-block', rotate: -2,
        }}>
          跟 AI 訓練一模一樣
        </span>
      </motion.div>
    </main>
  );
}
