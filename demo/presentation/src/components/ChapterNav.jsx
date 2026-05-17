import { useState, useEffect } from 'react';
import { usePresentationContext } from '../state/PresentationContext.jsx';
import { chapters } from '../tokens/chapters.js';

export function ChapterNav() {
  const { chapterId, jumpTo } = usePresentationContext();
  const [hoverZone, setHoverZone] = useState(false);
  const [hoverNav, setHoverNav] = useState(false);
  const visible = hoverZone || hoverNav;

  useEffect(() => {
    // Trigger zone wide enough to cover the full nav (~320px) so all 9 buttons stay reachable
    const onMove = (e) => setHoverZone(e.clientX > window.innerWidth - 360 && e.clientY < 80);
    window.addEventListener('mousemove', onMove);
    return () => window.removeEventListener('mousemove', onMove);
  }, []);

  return (
    <nav
      onMouseEnter={() => setHoverNav(true)}
      onMouseLeave={() => setHoverNav(false)}
      style={{
        position: 'fixed', top: 8, right: 8, zIndex: 90,
        opacity: visible ? 0.95 : 0,
        transition: visible ? 'opacity 0.4s' : 'opacity 0.8s',
        pointerEvents: visible ? 'auto' : 'none',
        background: '#FFFDF5', border: '4px solid #000', padding: 8,
        display: 'flex', gap: 4, fontFamily: 'Space Grotesk', fontWeight: 900,
      }}
    >
      {chapters.map(c => (
        <button
          key={c.id}
          onClick={() => jumpTo({ chapterId: c.id, stepId: 1, beatIndex: 0 })}
          style={{
            width: 28, height: 28,
            background: c.id === chapterId ? '#FF6B6B' : '#fff',
            color: '#000', border: '2px solid #000', cursor: 'pointer',
            fontFamily: 'inherit', fontWeight: 'inherit', fontSize: 14,
          }}
        >{c.id}</button>
      ))}
    </nav>
  );
}
