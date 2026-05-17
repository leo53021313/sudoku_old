// Render N squares (= flat.length) + chapter boundary yellow gaps — per outline-visual.md §9.5
// Actual count: 85 beats (was 88 in plan but manifest has 85)
import { useState, useEffect, useMemo } from 'react';
import { usePresentationContext } from '../state/PresentationContext.jsx';
import { flattenBeats } from '../data/beat-manifest.js';

export function BeatIndicator() {
  const { globalBeatIdx, chapterId, stepId, beatIndex } = usePresentationContext();
  const [hover, setHover] = useState(false);
  const flat = useMemo(() => flattenBeats(), []);

  useEffect(() => {
    const onMove = (e) => setHover(e.clientY > window.innerHeight - 32);
    window.addEventListener('mousemove', onMove);
    return () => window.removeEventListener('mousemove', onMove);
  }, []);

  return (
    <div
      style={{
        position: 'fixed', bottom: 26, left: 16, right: 16, zIndex: 88,
        height: 8, display: 'flex', alignItems: 'center', gap: 1,
        opacity: hover ? 0.7 : 0,
        transition: hover ? 'opacity 0.6s' : 'opacity 1s',
        pointerEvents: 'none',
      }}
    >
      {flat.map((f, i) => {
        const isChapterStart = i > 0 && f.chapterId !== flat[i - 1].chapterId;
        const isCurrent = i === globalBeatIdx;
        const isPast = i < globalBeatIdx;
        return (
          <div key={i} style={{ display: 'flex', alignItems: 'center' }}>
            {isChapterStart && <div style={{ width: 4, height: 6, background: '#FFD93D', marginRight: 2 }} />}
            <div style={{
              width: 8, height: 5,
              background: isCurrent ? '#FF6B6B' : isPast ? '#000' : 'transparent',
              border: isCurrent || isPast ? 'none' : '1px solid #000',
              transform: isCurrent ? 'scaleY(1.5)' : 'none',
            }} />
          </div>
        );
      })}
      <div style={{
        marginLeft: 'auto', fontSize: 11, fontFamily: 'Space Grotesk', fontWeight: 700, color: '#666',
      }}>
        step {flat.findIndex(f => f.chapterId === chapterId && f.stepId === stepId) + 1} / 57 · beat {beatIndex + 1} · ch {chapterId}
      </div>
    </div>
  );
}
