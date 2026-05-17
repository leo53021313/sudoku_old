import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';

export default function Ch1Step4() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Caption from top */}
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3, ease: 'easeOut' }}
        style={{
          position: 'absolute', top: 64, left: 0, right: 0,
          textAlign: 'center',
          fontWeight: 900, fontSize: '2rem', color: '#000',
        }}
      >
        靈感哪來呢？某天捷運上⋯
      </motion.div>

      {/* MRT window centered (placeholder for [E] SVG) */}
      <motion.div
        initial={{ scale: 0.85, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.7, ease: [0.34, 1.56, 0.64, 1] }}
      >
        <AssetPlaceholder
          type="[E]"
          width={720}
          height={400}
          todo="ch1 s4-s7 捷運窗景 SVG (紫底窗 + 黑邊 + 車廂線條 backdrop)"
        />
      </motion.div>

      {/* 正妹 sticker bottom-left cloud-style */}
      <motion.div
        initial={{ x: -200, y: 100, scale: 0.7, opacity: 0 }}
        animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: '14%', left: '8%',
          background: '#FFD93D', color: '#000',
          border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
          padding: '16px 28px', rotate: -4,
          fontWeight: 900, fontSize: 24,
          borderRadius: 24,
        }}
      >
        正妹發呆中
      </motion.div>
    </main>
  );
}
