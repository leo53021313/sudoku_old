import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';

export default function Ch1Step6() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <div>
        <AssetPlaceholder type="[E]" width={720} height={400} todo="ch1 s4-s7 捷運窗景 SVG" />
      </div>

      <div style={{
        position: 'absolute', bottom: '14%', left: '8%',
        background: '#FFD93D', color: '#000',
        border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
        padding: '16px 28px', transform: 'rotate(-4deg)',
        fontWeight: 900, fontSize: 24,
        borderRadius: 24,
      }}>
        正妹發呆中
      </div>

      <div style={{
        position: 'absolute', top: '14%', right: '8%',
        background: '#C4B5FD', color: '#000',
        border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
        padding: '16px 28px', transform: 'rotate(3deg)',
        fontWeight: 900, fontSize: 22,
        lineHeight: 1.2,
      }}>
        Code Bullet
        <div style={{ fontSize: 16, marginTop: 4 }}>· flappy bird</div>
      </div>

      {/* NEW: ⋯⋯ ellipsis bubble above 正妹 — stamp-in + pulse */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: [0, 1, 1], opacity: 1 }}
        transition={{
          scale: { duration: 0.3, ease: [0.34, 1.56, 0.64, 1] },
          opacity: { duration: 0.3 },
        }}
        style={{
          position: 'absolute', bottom: '34%', left: '12%',
        }}
      >
        <motion.div
          animate={{ scale: [1, 1.08, 1] }}
          transition={{ duration: 1, ease: 'easeInOut', repeat: Infinity }}
          style={{
            background: '#FFFDF5', color: '#000',
            border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
            padding: '12px 24px', borderRadius: 32,
            fontWeight: 900, fontSize: 32, letterSpacing: '0.2em',
          }}
        >
          ⋯⋯
        </motion.div>
      </motion.div>

      {/* Bottom-right small caption */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        style={{
          position: 'absolute', bottom: 32, right: 32,
          fontSize: 18, fontWeight: 700, color: '#666',
        }}
      >
        然後我繼續發呆⋯
      </motion.div>
    </main>
  );
}
