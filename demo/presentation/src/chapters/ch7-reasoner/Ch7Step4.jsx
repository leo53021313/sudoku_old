import { motion } from 'motion/react';

export default function Ch7Step4() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      fontFamily: 'Space Grotesk', display: 'flex',
    }}>
      <div style={{ flex: '0 0 60%', padding: 64, borderRight: '6px solid #000' }}>
        <motion.div
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          style={{ fontWeight: 900, fontSize: '2.5rem', marginBottom: 32 }}
        >
          舊：<span style={{ background: '#999', color: '#FFF', padding: '4px 16px' }}>填對給分</span>
        </motion.div>
        {/* one tech glow + single +1 */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.4, delay: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            background: '#FFD93D', color: '#000',
            padding: '20px 36px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            fontWeight: 900, fontSize: 28, display: 'inline-block', rotate: -3,
          }}
        >
          Naked Single
        </motion.div>
        <motion.div
          initial={{ y: 0, opacity: 0 }}
          animate={{ y: -60, opacity: [0, 1, 0] }}
          transition={{ duration: 1.2, delay: 1.0 }}
          style={{ fontWeight: 900, fontSize: 36, color: '#10B981', marginLeft: 200 }}
        >
          +1
        </motion.div>
      </div>

      <div style={{ flex: '0 0 40%', padding: 64, position: 'relative' }}>
        <motion.div
          initial={{ x: 100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          style={{ fontWeight: 900, fontSize: '2rem', marginBottom: 24 }}
        >
          新：<span style={{ background: '#FFD93D', padding: '4px 12px', border: '4px solid #000', fontSize: '1.5rem' }}>哪一招解釋？</span>
        </motion.div>
        {[
          { name: 'Naked Single', score: '+1', y: 0, delay: 0.6, color: '#FFD93D' },
          { name: 'Naked Pair', score: '+2', y: 80, delay: 0.8, color: '#C4B5FD' },
          { name: 'X-Wing', score: '+3', y: 160, delay: 1.0, color: '#FF6B6B' },
          { name: 'XYZ-Wing', score: '+3', y: 240, delay: 1.2, color: '#FF6B6B' },
        ].map((t, i) => (
          <motion.div
            key={i}
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.4, delay: t.delay }}
            style={{
              position: 'absolute', top: 160 + t.y, left: 64,
              display: 'flex', alignItems: 'center', gap: 16,
            }}
          >
            <span style={{
              background: t.color, color: '#000',
              padding: '8px 16px', border: '4px solid #000', boxShadow: '4px 4px 0 0 #000',
              fontWeight: 900, fontSize: 18,
            }}>{t.name}</span>
            <span style={{ fontWeight: 900, fontSize: 28, color: '#10B981' }}>{t.score}</span>
          </motion.div>
        ))}
      </div>
    </main>
  );
}
