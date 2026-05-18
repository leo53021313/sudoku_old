import { motion } from 'motion/react';
import { RedStamp } from '../../motifs/RedStamp.jsx';

export default function Ch4Step2() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      gap: 64, fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <RedStamp active rotation={-5} size="large">supervised 路線 · 拒絕</RedStamp>

      {/* Right comparison */}
      <motion.div
        initial={{ x: 60, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.8 }}
        style={{
          background: '#FFD93D', color: '#000',
          padding: '24px 40px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          fontWeight: 900, fontSize: 32, rotate: 3,
        }}
      >
        我要 AI · 自己摸出規則
      </motion.div>
    </main>
  );
}
