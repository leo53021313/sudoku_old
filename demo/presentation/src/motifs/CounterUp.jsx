import { useEffect, useState, useRef } from 'react';

export function CounterUp({
  from = 0,
  to,
  duration = 1200,
  prefix = '',
  suffix = '',
  onComplete = () => {},
}) {
  const [value, setValue] = useState(from);
  const completedRef = useRef(false);

  useEffect(() => {
    completedRef.current = false;
    const start = performance.now();
    let raf;
    const tick = (t) => {
      const elapsed = t - start;
      const pct = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - pct, 2);
      setValue(Math.round(from + (to - from) * eased));
      if (pct < 1) {
        raf = requestAnimationFrame(tick);
      } else if (!completedRef.current) {
        completedRef.current = true;
        onComplete();
      }
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [from, to, duration, onComplete]);

  return (
    <div style={{
      background: '#FFD93D', color: '#000',
      padding: '32px 96px', border: '8px solid #000', boxShadow: '16px 16px 0 0 #000',
      fontFamily: 'Space Grotesk', fontWeight: 900, fontSize: '8rem',
      transform: 'rotate(-3deg)',
      display: 'inline-block', lineHeight: 1,
    }}>
      {prefix}{value}{suffix}
    </div>
  );
}
