import { useState, useCallback } from 'react';

const ALL_FX = ['A', 'B', 'C', 'E', 'G'];

export function useClimax(variants = []) {
  const [activeFX, setActiveFX] = useState(
    Object.fromEntries(ALL_FX.map(k => [k, false]))
  );

  const play = useCallback(async () => {
    const next = Object.fromEntries(ALL_FX.map(k => [k, variants.includes(k)]));
    setActiveFX(next);
    // Hold for ~600ms then return; consumer can call reset() to hide overlays
    await new Promise(r => setTimeout(r, 600));
  }, [variants]);

  const reset = useCallback(() => {
    setActiveFX(Object.fromEntries(ALL_FX.map(k => [k, false])));
  }, []);

  return { activeFX, play, reset };
}
