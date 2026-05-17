import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch1Step3() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
    }}>
      <motion.div
        initial={{ x: -200, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{ marginBottom: 48 }}
      >
        <Sticker variant="kicker" bg="ink" textColor="cream">期中主題</Sticker>
      </motion.div>

      <motion.div
        initial={{ scale: 0.85, letterSpacing: '0.1em', opacity: 0 }}
        animate={{ scale: 1, letterSpacing: '-0.04em', opacity: 1 }}
        transition={{ duration: 0.72, delay: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          fontWeight: 900, fontSize: '6rem', lineHeight: 1.05,
          display: 'flex', alignItems: 'center', gap: 16,
          textAlign: 'center',
        }}
      >
        <span style={{ color: '#000', fontWeight: 900 }}>訓 練</span>
        <span style={{
          background: '#FF6B6B', color: '#FFFDF5',
          border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
          padding: '0 24px', transform: 'rotate(-2deg)', display: 'inline-block',
        }}>AI</span>
        <span style={{
          background: '#FFD93D', color: '#000',
          border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
          padding: '0 24px', transform: 'rotate(2deg)', display: 'inline-block',
        }}>解 數 獨</span>
      </motion.div>
    </div>
  );
}
