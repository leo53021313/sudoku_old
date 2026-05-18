import { motion } from 'motion/react';

export default function Ch9Step7() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 16,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', color: '#666' }}
      >
        最後再跟大家分享
      </motion.div>

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 1.0, delay: 0.4, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '5rem', textAlign: 'center', lineHeight: 1.3,
        }}
      >
        大腦可塑性
        <br/>
        <motion.span
          initial={{ letterSpacing: '0.3em', opacity: 0 }}
          animate={{ letterSpacing: '0.05em', opacity: 1 }}
          transition={{ duration: 1, delay: 1.2 }}
          style={{
            background: '#C4B5FD', color: '#000',
            padding: '8px 32px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            display: 'inline-block', marginTop: 16, fontSize: '4rem',
          }}
        >
          plasticity
        </motion.span>
      </motion.div>
    </main>
  );
}
