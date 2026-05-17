import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

const BRANCHES = [
  { id: 1, label: 'supervised',   sub: '看著答案抄筆記', bg: 'secondary', rotation: -3 },
  { id: 2, label: 'unsupervised', sub: '自己分類整理',   bg: 'muted',     rotation: 2 },
  { id: 3, label: 'RL',           sub: '試錯加獎懲',     bg: 'accent', textColor: 'cream', rotation: -2 },
];

export default function Ch2Step1() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', gap: 32,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
      >
        <Sticker variant="kicker" bg="ink" textColor="cream">在開始之前 · 先講個背景</Sticker>
      </motion.div>

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.4, ease: 'easeOut' }}
        style={{ fontWeight: 900, fontSize: '6rem', lineHeight: 1.05, letterSpacing: '0.05em' }}
      >
        機器學習
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0 }}
        style={{ fontWeight: 700, fontSize: '1.5rem' }}
      >
        底下總共分成{' '}
        <span style={{
          background: '#FFD93D', padding: '2px 14px',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          fontWeight: 900,
        }}>三大分支</span>
      </motion.div>

      <motion.svg
        width="640" height="60" viewBox="0 0 640 60"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3, delay: 1.4 }}
        style={{ overflow: 'visible' }}
      >
        <motion.path
          d="M 320 0 L 320 20 M 110 50 L 110 30 L 530 30 L 530 50 M 320 30 L 320 50"
          fill="none" stroke="#000" strokeWidth="4" strokeLinecap="square"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.5, delay: 1.4, ease: 'easeOut' }}
        />
      </motion.svg>

      <div style={{ display: 'flex', gap: 64, alignItems: 'flex-start' }}>
        {BRANCHES.map((b, i) => (
          <motion.div
            key={b.id}
            initial={{ y: -30, scale: 0.8, opacity: 0 }}
            animate={{ y: 0, scale: 1, opacity: 1 }}
            transition={{
              duration: 0.4, delay: 1.7 + i * 0.18,
              ease: [0.34, 1.56, 0.64, 1],
            }}
          >
            <Sticker variant="sat-lg" bg={b.bg} textColor={b.textColor} rotation={b.rotation}>
              <div style={{ fontSize: 14, letterSpacing: '0.1em', opacity: 0.7 }}>{`(${i + 1})`}</div>
              <div style={{ marginTop: 4, fontSize: 28 }}>{b.label}</div>
              <div style={{ fontSize: 16, marginTop: 8, fontWeight: 700 }}>{b.sub}</div>
            </Sticker>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 2.6 }}
        style={{ position: 'absolute', bottom: 0, fontWeight: 700, fontSize: 18, color: '#666' }}
      >
        一個一個來看 →
      </motion.div>
    </div>
  );
}
