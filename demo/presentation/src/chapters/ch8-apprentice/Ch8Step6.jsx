import { motion } from 'motion/react';
import { useState } from 'react';

export default function Ch8Step6() {
  const [hover, setHover] = useState(false);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <motion.a
        href="sudoku-demo:run"
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{
          scale: hover ? 1.05 : 1,
          opacity: 1,
          boxShadow: hover ? '20px 20px 0 0 #000' : '16px 16px 0 0 #000',
        }}
        transition={{ duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: hover ? '#E25555' : '#FF6B6B',
          color: '#FFFDF5',
          padding: '48px 96px',
          border: '6px solid #000',
          fontWeight: 900, fontSize: '4rem', textDecoration: 'none',
          rotate: -2, cursor: 'pointer', display: 'inline-block',
        }}
      >
        點我看 AI 即時解數獨 →
      </motion.a>

      <div style={{
        position: 'absolute', bottom: 64,
        fontWeight: 700, fontSize: 14, color: '#999', textAlign: 'center', maxWidth: 600,
      }}>
        點擊後會自動啟動桌面 pygame 視窗（透過 Windows custom URL scheme），不需手動 Alt+Tab。<br/>
        詳細部署見 demo/visualizer-launch/README.md
      </div>
    </main>
  );
}
