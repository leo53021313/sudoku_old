import { useEffect } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';

// 擦入動畫的結束狀態用負值 inset：裁切框往右/下各擴 24px（> box-shadow 的 12px），
// 否則 inset(0 0 0 0) 會貼著 border-box 把硬陰影一起裁掉（clip-path 在 rotate 前的
// 本地座標套用，所以陰影固定落在右下，只要往右下擴展即可）。
const REVEAL_END = 'inset(0px -24px -24px 0px)';

export default function Ch7Step1() {
  const { triggerShake } = usePresentationContext();

  // Trigger light shake when 重寫 highlight slides in (~700ms after mount)
  useEffect(() => {
    const t = setTimeout(() => triggerShake(), 700);
    return () => clearTimeout(t);
  }, [triggerShake]);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', color: '#666', marginBottom: 24 }}
      >
        核心想法只有一個
      </motion.div>

      <motion.div
        initial={{ clipPath: 'inset(0px 100% 0px 0px)', opacity: 0 }}
        animate={{ clipPath: REVEAL_END, opacity: 1 }}
        transition={{ duration: 1.0, delay: 0.3, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '4rem', textAlign: 'center', lineHeight: 1.3,
        }}
      >
        我只好整個計分獎勵系統
        <br/>
        <motion.span
          initial={{ clipPath: 'inset(0px 100% 0px 0px)' }}
          animate={{ clipPath: REVEAL_END }}
          transition={{ duration: 0.4, delay: 0.7, ease: 'easeOut' }}
          style={{
            background: '#FFD93D', color: '#000',
            padding: '4px 32px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            display: 'inline-block',
            fontSize: '5rem', rotate: -2, marginTop: 16,
          }}
        >
          重寫
        </motion.span>
      </motion.div>
    </main>
  );
}
