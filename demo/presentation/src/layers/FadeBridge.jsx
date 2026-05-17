// 0.8-1.2s auto fade-bridge between chapters — per outline-visual.md §10
import { useEffect, useState } from 'react';

const BIG_TRANSITIONS = new Set(['1-2', '4-5', '8-9']);

export function FadeBridge({ chapterId }) {
  const [active, setActive] = useState(false);
  const [prevChapter, setPrevChapter] = useState(chapterId);

  useEffect(() => {
    if (chapterId !== prevChapter) {
      const key = `${prevChapter}-${chapterId}`;
      const duration = BIG_TRANSITIONS.has(key) ? 1500 : 1000;
      setActive(true);
      const t = setTimeout(() => {
        setActive(false);
        setPrevChapter(chapterId);
      }, duration);
      return () => clearTimeout(t);
    }
  }, [chapterId, prevChapter]);

  if (!active) return null;
  return (
    <div
      aria-hidden="true"
      style={{
        position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none',
        background: '#FFFDF5',
        animation: 'fade-bridge 1000ms ease-out forwards',
      }}
    />
  );
}
