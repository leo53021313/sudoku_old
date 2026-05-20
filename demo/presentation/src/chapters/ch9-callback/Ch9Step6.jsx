import { motion } from 'motion/react';
import { GirlVeteran } from '../../motifs/GirlVeteran.jsx';

const QUESTIONS = [
  { text: '前女友跟我比 · 誰比較好？', bg: '#FFD93D', color: '#000', rotate: -2 },
  { text: '你心中的女神是誰？', bg: '#C4B5FD', color: '#000', rotate: 3 },
  { text: '你喜歡我哪裡？', bg: '#FF6B6B', color: '#FFFDF5', rotate: -3 },
  { text: '猜猜看 · 今天我哪裡不一樣？', bg: '#FFFDF5', color: '#000', rotate: 2 },
];

export default function Ch9Step6() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        style={{ fontWeight: 900, fontSize: '2.5rem' }}
      >
        以為穩了 · <span style={{ background: '#FF6B6B', color: '#FFF', padding: '4px 16px' }}>結果魔王關卡</span>
      </motion.div>

      {/* Callback: same 'asker' character from ch7 s7 — peeks in top-right */}
      <motion.div
        initial={{ scale: 0, opacity: 0, rotate: 0 }}
        animate={{ scale: 1, opacity: 1, rotate: 4 }}
        transition={{ duration: 0.5, delay: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', top: 48, right: 48, zIndex: 15,
        }}
      >
        <GirlVeteran width={200} rotation={0} shadow={10} />
      </motion.div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 32 }}>
        {QUESTIONS.map((q, i) => (
          <motion.div
            key={i}
            initial={{ scale: 0, opacity: 0, rotate: q.rotate }}
            animate={{
              scale: 1, opacity: 1, rotate: q.rotate,
              transition: { duration: 0.4, delay: 0.4 + i * 0.15, ease: [0.34, 1.56, 0.64, 1] },
            }}
            transition={{ type: 'spring', stiffness: 900, damping: 26 }}
            whileHover={{
              scale: 1.1,
              rotate: q.rotate,
              boxShadow: '16px 16px 0 0 #000',
              transition: { duration: 0.2, ease: 'easeOut' },
            }}
            style={{
              background: q.bg, color: q.color,
              padding: '28px 36px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
              fontWeight: 900, fontSize: 24, textAlign: 'center', maxWidth: 360,
              cursor: 'pointer',
            }}
          >
            {q.text}
          </motion.div>
        ))}
      </div>
    </main>
  );
}
