import { useEffect } from 'react';

export function useKeyMouseControls({ advance, retreat, toggleProgress }) {
  useEffect(() => {
    const onMouseDown = (e) => {
      if (e.button === 0) advance();        // left
      else if (e.button === 2) retreat();   // right
    };
    const onContextMenu = (e) => e.preventDefault();
    const onKey = (e) => {
      if (e.key === ' ' || e.key === 'ArrowRight') {
        e.preventDefault();
        advance();
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        retreat();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        toggleProgress?.();
      }
    };
    document.addEventListener('mousedown', onMouseDown);
    document.addEventListener('contextmenu', onContextMenu);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onMouseDown);
      document.removeEventListener('contextmenu', onContextMenu);
      document.removeEventListener('keydown', onKey);
    };
  }, [advance, retreat, toggleProgress]);
}
