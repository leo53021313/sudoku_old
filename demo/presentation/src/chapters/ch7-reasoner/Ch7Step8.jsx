import { motion } from 'motion/react';

export default function Ch7Step8() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
    }}>
      <motion.div
        initial={{ background: '#FFFDF5' }}
        animate={{ background: '#000' }}
        transition={{ duration: 0.8 }}
        style={{
          position: 'fixed', inset: 0, zIndex: 9, pointerEvents: 'none',
        }}
      />

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 1.5, delay: 0.6, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '3.5rem', color: '#FFFDF5', textAlign: 'center', lineHeight: 1.4,
          maxWidth: 1200, zIndex: 10, position: 'relative',
        }}
      >
        AI 永遠拿不到
        <br/>
        <span style={{ background: '#FF6B6B', padding: '4px 24px', border: '6px solid #FFF', display: 'inline-block', marginTop: 16 }}>
          「整題解完」那個大獎
        </span>
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 2.0 }}
        style={{
          fontWeight: 700, fontSize: '1.5rem', color: '#FFFDF5', zIndex: 10, position: 'relative',
        }}
      >
        就跟奶茶不知道陷阱題的正確解答一樣
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 3.0 }}
        style={{
          position: 'absolute', bottom: 64,
          fontWeight: 700, fontSize: 18, color: '#999', zIndex: 10,
        }}
      >
        反向思考⋯
      </motion.div>
    </main>
  );
}
