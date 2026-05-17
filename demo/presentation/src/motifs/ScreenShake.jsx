// Wraps children and applies a random shake to the wrapper via imperative ref
import { useAnimate } from 'motion/react';
import { forwardRef, useImperativeHandle } from 'react';

export const ScreenShake = forwardRef(function ScreenShake({ children, light = false }, ref) {
  const [scope, animate] = useAnimate();

  useImperativeHandle(ref, () => ({
    play: async () => {
      const intensity = light ? 2 : 5;
      const cycles = light ? 1 : 3;
      const keyframes = [];
      for (let i = 0; i < cycles; i++) {
        keyframes.push({ x: (Math.random() - 0.5) * intensity * 2, y: (Math.random() - 0.5) * intensity * 2 });
      }
      keyframes.push({ x: 0, y: 0 });
      await animate(scope.current, keyframes, { duration: light ? 0.08 : 0.15 });
    },
  }), [animate, scope, light]);

  return <div ref={scope} style={{ display: 'contents' }}>{children}</div>;
});
