import { motion } from 'motion/react';

export default function Ch2Step4() {
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
        transition={{ duration: 0.8, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '5rem', lineHeight: 1.1,
          textAlign: 'center', maxWidth: 1200,
        }}
      >
        那 ChatGPT 跟 Claude · 又是哪一招？
      </motion.div>

      {/* Yellow ? sticker — drops in from top with 720° spin */}
      <motion.div
        initial={{ y: -300, rotate: 0, scale: 0, opacity: 0 }}
        animate={{ y: 0, rotate: 720, scale: 1.1, opacity: 1 }}
        transition={{ duration: 0.9, delay: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          marginTop: 48,
          background: '#FFD93D', color: '#000',
          border: '6px solid #000', boxShadow: '16px 16px 0 0 #000',
          width: 200, height: 200, borderRadius: '50%',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontWeight: 900, fontSize: 120,
        }}
      >
        ?
      </motion.div>
    </main>
  );
}
