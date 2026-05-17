import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';

export default function Ch1Step7() {
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

      {/* NEW: 沒手機·解數獨 sticker bottom-right */}
      <motion.div
        initial={{ x: 200, y: 100, scale: 0.7, opacity: 0 }}
        animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: '14%', right: '8%',
          background: '#FF6B6B', color: '#FFFDF5',
          border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
          padding: '16px 28px', rotate: 2,
          fontWeight: 900, fontSize: 24,
        }}
      >
        沒手機·解數獨
      </motion.div>
    </main>
  );
}
