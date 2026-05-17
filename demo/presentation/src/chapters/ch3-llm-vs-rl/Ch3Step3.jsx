import { motion } from 'motion/react';
import { HalftoneBurst } from '../../motifs/HalftoneBurst.jsx';

export default function Ch3Step3() {
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
          fontWeight: 900, fontSize: '5rem', lineHeight: 1.2,
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16,
        }}
      >
        <div style={{ position: 'relative', display: 'inline-block' }}>
          <span style={{
            background: '#FF6B6B', color: '#FFFDF5',
            padding: '0 32px', border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
            rotate: -2, display: 'inline-block',
          }}>OK</span>
          {/* Halftone burst micro on OK highlight finish */}
          <div style={{ position: 'absolute', inset: 0 }}>
            <HalftoneBurst active size={120} centerX="50%" centerY="50%" />
          </div>
        </div>
        <div>所以我要走 <span style={{
          background: '#FFD93D', color: '#000',
          padding: '0 24px', border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
          rotate: 2, display: 'inline-block',
        }}>純 RL</span></div>
        <div style={{ fontSize: '3rem', marginTop: 32 }}>第一步是找資料</div>
      </motion.div>
    </main>
  );
}
