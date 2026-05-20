import { motion } from 'motion/react';

// 擦入動畫的結束狀態用負值 inset：裁切框往右/下各擴 24px（> box-shadow 的 8px），
// 否則 inset(0 0 0 0) 會貼著 border-box 把硬陰影一起裁掉（clip-path 在 rotate 前的
// 本地座標套用，陰影固定落在右下，只要往右下擴展即可）。
const REVEAL_END = 'inset(0px -24px -24px 0px)';

export default function Ch7Step2() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <motion.div
        initial={{ clipPath: 'inset(0px 100% 0px 0px)', opacity: 0 }}
        animate={{ clipPath: REVEAL_END, opacity: 1 }}
        transition={{ duration: 1.2, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '3.5rem', textAlign: 'center', lineHeight: 1.4,
          maxWidth: 1300,
        }}
      >
        用人類玩數獨的解題技巧
        <br/>
        <motion.span
          initial={{ clipPath: 'inset(0px 100% 0px 0px)' }}
          animate={{ clipPath: REVEAL_END }}
          transition={{ duration: 0.4, delay: 1.3 }}
          style={{
            background: '#FF6B6B', color: '#FFF',
            padding: '2px 24px', border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
            display: 'inline-block', rotate: -2,
          }}
        >
          反過來
        </motion.span>
        {' '}
        <motion.span
          initial={{ clipPath: 'inset(0px 100% 0px 0px)' }}
          animate={{ clipPath: REVEAL_END }}
          transition={{ duration: 0.4, delay: 1.6 }}
          style={{
            background: '#FFD93D', color: '#000',
            padding: '2px 24px', border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
            display: 'inline-block', rotate: 2,
          }}
        >
          驗證
        </motion.span>
        {' '}
        AI 的每一步
      </motion.div>
    </main>
  );
}
