import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch2Step5() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
    }}>
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '5rem', lineHeight: 1.1,
          textAlign: 'center', maxWidth: 1200,
        }}
      >
        那 ChatGPT 跟 Claude · 又是哪一招？
      </motion.div>

      {/* Yellow ? sticker — drops in from top with 720° spin */}
      <motion.div
        initial={{ y: -300, rotate: 0, scale: 0, opacity: 0 }}
        animate={{ y: 0, rotate: 720, scale: 1.1, opacity: 1 }}
        transition={{ duration: 0.9, delay: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ marginTop: 48 }}
      >
        <Sticker
          variant="sat-md"
          bg="secondary"
          border={6}
          shadow="massive"
          style={{
            width: 200, height: 200, borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 120, padding: 0,
          }}
        >
          ?
        </Sticker>
      </motion.div>
    </div>
  );
}
