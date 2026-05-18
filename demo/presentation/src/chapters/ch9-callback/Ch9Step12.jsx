import { motion } from 'motion/react';

export default function Ch9Step12() {
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
        style={{ fontWeight: 700, fontSize: '1.5rem', color: '#666' }}
      >
        繼續嘗試跟其他女生聊天
      </motion.div>

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 1.0, delay: 0.4, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '3rem', textAlign: 'center', lineHeight: 1.4,
        }}
      >
        祝大家未來在職場上
        <br/>
        <span style={{
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '8px 32px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          display: 'inline-block', marginTop: 16, rotate: -2,
        }}>
          不被挫敗給擊敗
        </span>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.6 }}
        style={{ fontWeight: 700, fontSize: '1.25rem', color: '#666', marginTop: 16 }}
      >
        不是每個女生都那麼老油條
      </motion.div>
    </main>
  );
}
