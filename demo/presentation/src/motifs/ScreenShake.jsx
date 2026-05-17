// Wraps children and applies a random shake to the wrapper via imperative ref
// Per outline-visual.md §8.1 climax A
import { useAnimate } from 'motion/react';
import { forwardRef, useImperativeHandle } from 'react';

export const ScreenShake = forwardRef(function ScreenShake({ children, light = false }, ref) {
  const [scope, animate] = useAnimate();

  useImperativeHandle(ref, () => ({
    play: async () => {
      // Motion v11+ `animate(el, values, options)` expects values = object with arrays per prop
      // (`{ x: [0, 5, -5, 0], y: [0, 3, -3, 0] }`). NOT an array of objects — that signature
      // is for animation SEQUENCES (e.g. `[[el, vals, opts], [el2, vals2, opts2]]`) and using
      // it incorrectly causes renderHTML to set numeric keys on CSSStyleDeclaration, throwing
      // "Failed to set an indexed property [0]" and breaking ALL motion components on the page.
      const intensity = light ? 2 : 5;
      const cycles = light ? 1 : 3;
      const x = [0];
      const y = [0];
      for (let i = 0; i < cycles; i++) {
        x.push((Math.random() - 0.5) * intensity * 2);
        y.push((Math.random() - 0.5) * intensity * 2);
      }
      x.push(0); y.push(0);
      await animate(scope.current, { x, y }, { duration: light ? 0.08 : 0.15 });
    },
  }), [animate, scope, light]);

  // Use full-viewport positioned div so:
  // 1. transform applied to it visibly shakes all contained children
  // 2. position:fixed children (like SpotlightVignette) still attach to viewport correctly during shake
  // 3. position:absolute children using ICB still work (they look up to ICB if no positioned ancestor)
  return (
    <div ref={scope} style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      {children}
    </div>
  );
});
