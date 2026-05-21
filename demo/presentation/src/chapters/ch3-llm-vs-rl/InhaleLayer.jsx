import { useCallback, useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';

// Central forbidden zone half-width / half-height — keeps inhale particles
// from spawning on top of the LLM hero (which sits at viewport center).
const FORBIDDEN_HALF_W = 160;
const FORBIDDEN_HALF_H = 120;
const MAX_ATTEMPTS = 6;

export function pickStart(viewportW, viewportH) {
  const fx0 = viewportW / 2 - FORBIDDEN_HALF_W;
  const fx1 = viewportW / 2 + FORBIDDEN_HALF_W;
  const fy0 = viewportH / 2 - FORBIDDEN_HALF_H;
  const fy1 = viewportH / 2 + FORBIDDEN_HALF_H;
  let startX = 0, startY = 0;
  for (let i = 0; i < MAX_ATTEMPTS; i++) {
    startX = Math.random() * viewportW;
    startY = Math.random() * viewportH;
    const inX = startX >= fx0 && startX <= fx1;
    const inY = startY >= fy0 && startY <= fy1;
    if (!(inX && inY)) return { startX, startY };
  }
  return { startX, startY }; // all MAX_ATTEMPTS landed in the forbidden box — return the last sample
}

// Inhale spawn schedule.
const FIRST_DELAY_MS = 2200;
const INTERVAL_BASE_MS = 4000;
const INTERVAL_JITTER_MS = 1000;

export function useInhaleSpawn(terms) {
  const [particles, setParticles] = useState([]);
  const counterRef = useRef(0);

  useEffect(() => {
    let alive = true;
    let timeoutId;

    const spawn = () => {
      if (!alive) return;
      const id = counterRef.current++;
      const { startX, startY } = pickStart(window.innerWidth, window.innerHeight);
      const endX = window.innerWidth / 2;
      const endY = window.innerHeight / 2;
      const text = terms[(Math.random() * terms.length) | 0];
      setParticles(p => [...p, { id, text, startX, startY, endX, endY }]);
      // jitter is uniform in [-INTERVAL_JITTER_MS, +INTERVAL_JITTER_MS]
      const nextDelay = INTERVAL_BASE_MS + (Math.random() * 2 - 1) * INTERVAL_JITTER_MS;
      timeoutId = setTimeout(spawn, nextDelay);
    };

    timeoutId = setTimeout(spawn, FIRST_DELAY_MS);
    return () => { alive = false; clearTimeout(timeoutId); };
  }, [terms]);

  const removeParticle = useCallback((id) => {
    setParticles(p => p.filter(q => q.id !== id));
  }, []);

  return { particles, removeParticle };
}

export default function InhaleLayer({ terms }) {
  const { particles, removeParticle } = useInhaleSpawn(terms);

  return (
    <div
      aria-hidden="true"
      style={{
        position: 'absolute', inset: 0,
        pointerEvents: 'none', zIndex: 0,
      }}
    >
      {particles.map(p => (
        <motion.div
          key={p.id}
          initial={{ x: p.startX, y: p.startY, scale: 1, opacity: 0.7 }}
          animate={{ x: p.endX, y: p.endY, scale: 0.2, opacity: 0 }}
          transition={{ duration: 0.9, ease: [0.4, 0, 1, 1] }}
          onAnimationComplete={() => removeParticle(p.id)}
          style={{
            position: 'absolute', top: 0, left: 0,
            fontFamily: 'monospace', fontWeight: 700, fontSize: 14,
            color: '#C4B5FD', whiteSpace: 'nowrap',
          }}
        >
          {p.text}
        </motion.div>
      ))}
    </div>
  );
}
