import { motion } from 'motion/react';
import { useState, useEffect } from 'react';

export default function Ch4Step4() {
  const [highlightIdx, setHighlightIdx] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setHighlightIdx(i => (i + 1) % 30), 200);
    return () => clearInterval(id);
  }, []);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* 紅警示 hero phase 1 */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '24px 48px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          fontWeight: 900, fontSize: '3rem', rotate: -3, marginBottom: 32,
        }}
      >
        才爬 20 題就被封 IP
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.8 }}
        style={{ fontWeight: 900, fontSize: '1.5rem', marginBottom: 24 }}
      >
        proxy 池 · 類似 VPN · 好幾萬個 IP
      </motion.div>

      {/* IP grid */}
      <motion.div
        initial="hidden"
        animate="visible"
        variants={{
          hidden: { opacity: 0 },
          visible: { opacity: 1, transition: { staggerChildren: 0.03 } },
        }}
        style={{
          display: 'grid', gridTemplateColumns: 'repeat(10, 1fr)', gap: 8,
          maxWidth: 800,
        }}
      >
        {Array.from({ length: 30 }).map((_, i) => (
          <motion.div
            key={i}
            variants={{
              hidden: { scale: 0, opacity: 0 },
              visible: { scale: 1, opacity: i === highlightIdx ? 1 : 0.4 },
            }}
            transition={{ duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
            style={{
              background: i === highlightIdx ? '#FFD93D' : '#FFFDF5',
              border: '3px solid #000',
              boxShadow: i === highlightIdx ? '4px 4px 0 0 #000' : '2px 2px 0 0 #000',
              padding: '8px 4px',
              fontFamily: 'monospace', fontWeight: 700, fontSize: 12,
              textAlign: 'center', transform: `rotate(${(i * 7) % 5 - 2}deg)`,
              transition: 'background 0.15s, opacity 0.15s',
            }}
          >
            {`${(i * 17 + 23) % 256}.${(i * 31) % 256}`}
          </motion.div>
        ))}
      </motion.div>
    </main>
  );
}
