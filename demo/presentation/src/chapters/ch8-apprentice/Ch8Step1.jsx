import { useEffect, useState } from 'react';
import { motion } from 'motion/react';

// 擦入動畫的結束狀態用四邊各擴 24px 的負值 inset：否則 inset(0 0 0 0) 會貼著 border-box，
// 把溢出的 box-shadow（右下）與 inline span 溢出 line box 的上下邊框一起裁掉。
const REVEAL_END = 'inset(-24px)';

// 反向思考 highlight reveal 在 delay 0.6 + duration 0.9 後完成 ≈ 1.5s。
// Anticipation window: 0 → 1.5s（reveal in flight），Aftermath: reveal 落定後 +500ms 起延後 settle。
const REVEAL_SETTLED_AT_MS = 1500;
const AFTERMATH_DELAY_MS = 500;

export default function Ch8Step1() {
  const [revealSettled, setRevealSettled] = useState(false);
  const [aftermath, setAftermath] = useState(false);

  useEffect(() => {
    const t1 = setTimeout(() => setRevealSettled(true), REVEAL_SETTLED_AT_MS);
    const t2 = setTimeout(() => setAftermath(true), REVEAL_SETTLED_AT_MS + AFTERMATH_DELAY_MS);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, []);

  const anticipationActive = !revealSettled;

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 24,
    }}>
      <motion.div
        initial={{ opacity: 1 }}
        animate={{ opacity: 0 }}
        transition={{ duration: 1.2, ease: [0.4, 0.0, 0.2, 1] }}
        style={{
          position: 'fixed', inset: 0, zIndex: 60, background: '#000', pointerEvents: 'none',
        }}
      />

      <motion.div
        initial={{ clipPath: 'inset(0px 100% 0px 0px)', opacity: 0 }}
        animate={anticipationActive
          ? { clipPath: REVEAL_END, opacity: 1, scale: [1, 1.015, 0.99, 1], rotate: [0, 0.6, -0.4, 0] }
          : { clipPath: REVEAL_END, opacity: 1, scale: 1, rotate: 0 }}
        transition={anticipationActive
          ? { clipPath: { duration: 0.9, delay: 0.6, ease: 'easeOut' },
              opacity: { duration: 0.9, delay: 0.6, ease: 'easeOut' },
              scale: { duration: 1.4, repeat: Infinity, ease: 'linear' },
              rotate: { duration: 1.4, repeat: Infinity, ease: 'linear' } }
          : { duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
        style={{
          fontWeight: 900, fontSize: '4rem', textAlign: 'center', lineHeight: 1.4,
        }}
      >
        <motion.span
          animate={aftermath ? { rotate: 1 } : { rotate: 0 }}
          transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
          style={{
            background: '#FF6B6B', color: '#FFF', padding: '4px 24px',
            border: '6px solid #000',
            boxShadow: aftermath ? '4px 4px 0 0 #000' : '8px 8px 0 0 #000',
            display: 'inline-block',
            transition: 'box-shadow 0.35s cubic-bezier(0.22, 1, 0.36, 1)',
          }}
        >反向思考</motion.span>
        <br/>
        先解簡單的陷阱題答案
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.4 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', color: '#666' }}
      >
        之後從容面對各式各樣的老油條陷阱題
      </motion.div>

      <motion.div
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.8 }}
        style={{
          position: 'absolute', bottom: 80,
          fontWeight: 700, fontSize: 18, color: '#666',
        }}
      >
        AI 也是、我把題目反過來給他 →
      </motion.div>
    </main>
  );
}
