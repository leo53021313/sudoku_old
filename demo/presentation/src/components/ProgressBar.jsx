import { useState, useEffect } from 'react';
import { usePresentationContext } from '../state/PresentationContext.jsx';

export function ProgressBar() {
  const { globalBeatIdx, totalBeats, progressVisible } = usePresentationContext();
  const [hover, setHover] = useState(false);
  const visible = hover || progressVisible;
  const pct = ((globalBeatIdx + 1) / totalBeats) * 100;

  useEffect(() => {
    const onMove = (e) => setHover(e.clientY > window.innerHeight - 32);
    window.addEventListener('mousemove', onMove);
    return () => window.removeEventListener('mousemove', onMove);
  }, []);

  return (
    <div
      style={{
        position: 'fixed', left: 0, right: 0, bottom: 0,
        height: 24, zIndex: 90,
        opacity: visible ? 0.8 : 0,
        transition: visible ? 'opacity 0.6s' : 'opacity 1s',
        background: 'rgba(255,253,245,0.6)',
        borderTop: '2px solid #000',
        display: 'flex', alignItems: 'center', padding: '0 16px',
        fontFamily: 'Space Grotesk', fontWeight: 700, fontSize: 11,
      }}
    >
      <div style={{ flex: 1, height: 6, background: '#fff', border: '1px solid #000', position: 'relative' }}>
        <div style={{ position: 'absolute', left: 0, top: 0, height: '100%', width: `${pct}%`, background: '#FF6B6B' }} />
      </div>
      <div style={{ marginLeft: 12 }}>{globalBeatIdx + 1} / {totalBeats}</div>
    </div>
  );
}
