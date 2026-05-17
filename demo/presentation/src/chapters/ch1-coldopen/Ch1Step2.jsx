import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch1Step2() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      gap: 32, fontFamily: 'Space Grotesk',
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
      >
        <Sticker variant="kicker" bg="ink" textColor="cream">先簡單自我介紹</Sticker>
      </motion.div>

      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
      >
        <Sticker variant="hub-md" bg="cream" rotation={-2}>
          心 理 學 系
          <div style={{ fontSize: '1.75rem', marginTop: 16, letterSpacing: '0.1em' }}>· 畢 業 ·</div>
        </Sticker>
      </motion.div>

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.7, delay: 1.1, ease: 'easeOut' }}
        style={{ marginTop: 16, fontSize: 22, fontWeight: 700, textAlign: 'center', lineHeight: 1.5, maxWidth: 760 }}
      >
        跨領域來資展會學 AI ·{' '}
        <span style={{
          background: '#FFD93D', padding: '2px 12px',
          border: '3px solid #000', boxShadow: '4px 4px 0 0 #000',
          marginLeft: 4,
        }}>非本科生</span>
      </motion.div>
    </div>
  );
}
