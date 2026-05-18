import { motion } from 'motion/react';

export default function Ch7Step2() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 1.2, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '3.5rem', textAlign: 'center', lineHeight: 1.4,
          maxWidth: 1300,
        }}
      >
        用人類玩數獨的解題技巧
        <br/>
        <motion.span
          initial={{ clipPath: 'inset(0 100% 0 0)' }}
          animate={{ clipPath: 'inset(0 0 0 0)' }}
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
          initial={{ clipPath: 'inset(0 100% 0 0)' }}
          animate={{ clipPath: 'inset(0 0 0 0)' }}
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
