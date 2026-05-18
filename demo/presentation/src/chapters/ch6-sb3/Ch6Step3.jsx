import { motion } from 'motion/react';
import { useState, useEffect } from 'react';

export default function Ch6Step3() {
  const [plusses, setPlusses] = useState([]);
  useEffect(() => {
    let id = 0;
    const t = setInterval(() => {
      setPlusses(prev => [
        ...prev,
        { id: id++, x: Math.random() * 80 + 10, delay: 0 },
      ].slice(-15));
    }, 400);
    return () => clearInterval(t);
  }, []);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* 剛認識的新女生 sticker — pink + rotation */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FFB6C1', color: '#000',
          padding: '32px 56px', border: '6px solid #000', boxShadow: '14px 14px 0 0 #000',
          fontWeight: 900, fontSize: '2.5rem', rotate: -4, lineHeight: 1.3,
          textAlign: 'center',
        }}
      >
        剛認識的<br/>新女生 ✨
      </motion.div>

      {/* +/+/+ floating plus symbols */}
      {plusses.map(p => (
        <motion.div
          key={p.id}
          initial={{ y: 0, opacity: 1 }}
          animate={{ y: -300, opacity: 0 }}
          transition={{ duration: 2, ease: 'easeOut' }}
          style={{
            position: 'absolute', left: `${p.x}%`, bottom: '20%',
            fontSize: 48, fontWeight: 900, color: '#10B981',
            WebkitTextStroke: '2px black',
            pointerEvents: 'none',
          }}
        >
          +
        </motion.div>
      ))}

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.8 }}
        style={{
          marginTop: 48, fontWeight: 700, fontSize: '1.5rem', color: '#000',
        }}
      >
        聊天都覺得對方也喜歡你
      </motion.div>
    </main>
  );
}
