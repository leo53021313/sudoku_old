import { motion } from 'motion/react';

export default function Ch6Step4() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      gap: 64, fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Persisted 新女生 sticker on left */}
      <div style={{
        background: '#FFB6C1', color: '#000',
        padding: '24px 40px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
        fontWeight: 900, fontSize: '1.5rem', transform: 'rotate(-4deg)', lineHeight: 1.3,
        textAlign: 'center',
      }}>
        剛認識的<br/>新女生 ✨
      </div>

      {/* SVG curve climbing */}
      <svg viewBox="0 0 400 240" width="500" height="300" style={{ overflow: 'visible' }}>
        {/* axis */}
        <line x1="20" y1="220" x2="380" y2="220" stroke="#000" strokeWidth="3" />
        <line x1="20" y1="220" x2="20" y2="20" stroke="#000" strokeWidth="3" />

        {/* climbing curve */}
        <motion.path
          d="M 20 200 L 80 180 L 140 140 L 200 90 L 260 50 L 380 40"
          fill="none" stroke="#000" strokeWidth="4" strokeLinecap="square"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2, ease: 'easeOut' }}
        />

        {/* +/+/+ markers on curve */}
        {[
          { x: 80, y: 180 }, { x: 140, y: 140 }, { x: 200, y: 90 }, { x: 260, y: 50 },
        ].map((p, i) => (
          <motion.text
            key={i}
            x={p.x} y={p.y - 10}
            fill="#10B981" fontFamily="Space Grotesk" fontSize="24" fontWeight="900"
            stroke="#000" strokeWidth="0.5"
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.5 + i * 0.4, ease: [0.34, 1.56, 0.64, 1] }}
          >+</motion.text>
        ))}
      </svg>
    </main>
  );
}
