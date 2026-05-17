import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useClimax } from './useClimax.js';

describe('useClimax', () => {
  it('returns an object with play/active/setActive', () => {
    const { result } = renderHook(() => useClimax(['A', 'C']));
    expect(typeof result.current.play).toBe('function');
    expect(result.current.activeFX).toEqual({ A: false, B: false, C: false, E: false, G: false });
  });

  it('activates fx codes on play()', async () => {
    const { result } = renderHook(() => useClimax(['A', 'B', 'G']));
    await act(async () => { await result.current.play(); });
    expect(result.current.activeFX.A).toBe(true);
    expect(result.current.activeFX.B).toBe(true);
    expect(result.current.activeFX.G).toBe(true);
    expect(result.current.activeFX.C).toBe(false);
    expect(result.current.activeFX.E).toBe(false);
  });

  it('reset() clears all activeFX', async () => {
    const { result } = renderHook(() => useClimax(['A', 'B']));
    await act(async () => { await result.current.play(); });
    expect(result.current.activeFX.A).toBe(true);
    act(() => result.current.reset());
    expect(result.current.activeFX.A).toBe(false);
    expect(result.current.activeFX.B).toBe(false);
  });
});
