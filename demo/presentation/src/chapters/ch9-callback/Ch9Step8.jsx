import { motion } from 'motion/react';

export default function Ch9Step8() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 24,
    }}>
      {/* Background callback: faint 13-stairs grid (mini tile pattern) */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute', inset: 0, pointerEvents: 'none',
          opacity: 0.08, filter: 'grayscale(1)',
          backgroundImage: 'radial-gradient(#000 2px, transparent 2.5px)',
          backgroundSize: '20px 20px',
        }}
      />

      <div style={{ display: 'flex', gap: 32, alignItems: 'flex-start', marginBottom: 32 }}>
        {[
          { label: '解數獨', sub: 'AI 沒天生會 ·', color: '#FF6B6B', textColor: '#FFF' },
          { label: '講話', sub: '你 出生不會 ·', color: '#FFD93D', textColor: '#000' },
          { label: '跟人相處', sub: '你 不是天生會 ·', color: '#C4B5FD', textColor: '#000' },
        ].map((col, i) => (
          <motion.div
            key={i}
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.3 + i * 0.2 }}
            style={{
              background: col.color, color: col.textColor,
              padding: '24px 32px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
              fontWeight: 900, fontSize: 24, textAlign: 'center', minWidth: 200,
            }}
          >
            <div style={{ fontSize: 18, marginBottom: 8 }}>{col.sub}</div>
            <div style={{ fontSize: 32 }}>{col.label}</div>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          fontWeight: 900, fontSize: '8rem',
          background: '#FFFDF5', color: '#000',
          padding: '24px 64px', border: '8px solid #000', boxShadow: '16px 16px 0 0 #000',
          rotate: -2,
        }}
      >
        一樣
      </motion.div>
    </main>
  );
}
