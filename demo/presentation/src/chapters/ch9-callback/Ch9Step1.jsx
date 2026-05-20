import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';

export default function Ch9Step1() {
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
        AI 還在訓練中⋯⋯<span style={{ color: '#000', fontWeight: 900 }}>我跟對方還在磨合期</span>
      </motion.div>

      <div style={{ display: 'flex', gap: 32 }}>
        <motion.div
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          style={{ border: '6px solid #000', boxShadow: '12px 12px 0 0 #000', padding: 4, background: '#FFF' }}
        >
          <AssetPlaceholder type="[✓]" width={420} height={260} todo="success_rate 曲線截圖 (export from tensorboard, save to public/images/tensorboard/success-rate.png)" />
        </motion.div>
        <motion.div
          initial={{ x: 100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          style={{ border: '6px solid #000', boxShadow: '12px 12px 0 0 #000', padding: 4, background: '#FFF' }}
        >
          <AssetPlaceholder type="[✓]" width={420} height={260} todo="curriculum target_empty 截圖 (save to public/images/tensorboard/curriculum-target-empty.png)" />
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0 }}
        style={{ fontWeight: 700, fontSize: '1.25rem' }}
      >
        但你可以看到 · <span style={{ background: '#FFD93D', padding: '2px 12px', border: '3px solid #000' }}>AI 是有在進步的</span>
      </motion.div>

      <motion.div
        initial={{ scale: 0.85, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.9, delay: 1.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          marginTop: 16, fontWeight: 900, fontSize: '3rem',
          background: '#FFFDF5', color: '#000',
          padding: '12px 32px', border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
        }}
      >
        最後我想跟大家講一件事
      </motion.div>
    </main>
  );
}
