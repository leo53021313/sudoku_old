import { useEffect, useState } from 'react';
import { stage, computeStageScale } from '../tokens/stage.js';

export function Stage({ children }) {
  const [scale, setScale] = useState(() =>
    typeof window === 'undefined'
      ? 1
      : computeStageScale(window.innerWidth, window.innerHeight)
  );

  useEffect(() => {
    const handle = () => setScale(computeStageScale(window.innerWidth, window.innerHeight));
    handle();
    window.addEventListener('resize', handle);
    return () => window.removeEventListener('resize', handle);
  }, []);

  return (
    <div
      style={{
        position: 'fixed', inset: 0,
        overflow: 'hidden',
        background: '#FFFDF5',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}
    >
      <div
        data-stage-canvas
        style={{
          width: stage.width,
          height: stage.height,
          transform: `scale(${scale})`,
          transformOrigin: 'center center',
          position: 'relative',
          flex: 'none',
        }}
      >
        {children}
      </div>
    </div>
  );
}
