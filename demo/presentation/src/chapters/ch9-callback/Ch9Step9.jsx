import { motion } from 'motion/react';

export default function Ch9Step9() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
    }}>
      {/* Background: flipping +20/+50 callback at opacity 0.06 */}
      <motion.div
        aria-hidden="true"
        animate={{ rotateY: [0, 360] }}
        transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
        style={{
          position: 'absolute', inset: 0, opacity: 0.06,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          filter: 'grayscale(1)', pointerEvents: 'none',
        }}
      >
        <div style={{ fontWeight: 900, fontSize: '20rem' }}>+50</div>
      </motion.div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, fontWeight: 700, fontSize: '1.5rem', color: '#666' }}>
        {['每改一次 reward function', '每談一場戀愛', '每學一個新東西'].map((line, i) => (
          <motion.div
            key={i}
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.3 + i * 0.24 }}
          >
            · {line}
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 1.0, delay: 1.4, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '3rem', textAlign: 'center', lineHeight: 1.4,
        }}
      >
        每次都把我們
        <br/>
        <span style={{
          background: '#FFD93D', padding: '4px 24px',
          border: '6px solid #000', boxShadow: '10px 10px 0 0 #000', display: 'inline-block', marginTop: 16,
        }}>
          重新塑造一次
        </span>
      </motion.div>
    </main>
  );
}
