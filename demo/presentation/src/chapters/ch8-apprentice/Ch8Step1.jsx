import { motion } from 'motion/react';

// 擦入動畫的結束狀態用四邊各擴 24px 的負值 inset：否則 inset(0 0 0 0) 會貼著 border-box，
// 把溢出的 box-shadow（右下）與 inline span 溢出 line box 的上下邊框一起裁掉。
const REVEAL_END = 'inset(-24px)';

export default function Ch8Step1() {
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
        animate={{ clipPath: REVEAL_END, opacity: 1 }}
        transition={{ duration: 0.9, delay: 0.6, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '4rem', textAlign: 'center', lineHeight: 1.4,
        }}
      >
        <span style={{
          background: '#FF6B6B', color: '#FFF', padding: '4px 24px',
          border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
        }}>反向思考</span>
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
