import { useEffect, useState } from 'react';
import { motion } from 'motion/react';

export default function Ch5Step3() {
  const [xs, setXs] = useState([]);
  useEffect(() => {
    let id = 0;
    const spawn = setInterval(() => {
      setXs(prev => [
        ...prev,
        {
          id: id++,
          x: Math.random() * 90 + 5,
          y: Math.random() * 60 + 20,
          rotate: Math.random() * 60 - 30,
          size: Math.random() * 40 + 60,
        },
      ].slice(-12));  // keep last 12
    }, 200);
    return () => clearInterval(spawn);
  }, []);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, overflow: 'hidden',
    }}>
      {/* Hero */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
        style={{
          fontWeight: 900, fontSize: '4rem', textAlign: 'center', zIndex: 2, position: 'relative',
        }}
      >
        每改一個地方都東倒西歪
      </motion.div>

      {/* Chaotic X spawning */}
      {xs.map(x => (
        <motion.div
          key={x.id}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 0 }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
          style={{
            position: 'absolute', left: `${x.x}%`, top: `${x.y}%`,
            fontWeight: 900, fontSize: x.size, color: '#FF6B6B',
            WebkitTextStroke: '3px black',
            transform: `rotate(${x.rotate}deg)`,
            pointerEvents: 'none', zIndex: 1,
          }}
        >
          ✗
        </motion.div>
      ))}

      <motion.div
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        style={{
          marginTop: 32,
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '20px 40px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          fontWeight: 900, fontSize: '2.5rem', rotate: -2, zIndex: 2, position: 'relative',
        }}
      >
        debug 成本爆炸
      </motion.div>
    </main>
  );
}
