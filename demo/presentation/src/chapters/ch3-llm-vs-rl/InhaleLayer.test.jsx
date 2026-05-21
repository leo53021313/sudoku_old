import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { vi, beforeEach, afterEach } from 'vitest';
import { pickStart, useInhaleSpawn } from './InhaleLayer.jsx';

describe('pickStart', () => {
  it('returns a coordinate within the viewport bounds', () => {
    const { startX, startY } = pickStart(1920, 1080);
    expect(startX).toBeGreaterThanOrEqual(0);
    expect(startX).toBeLessThanOrEqual(1920);
    expect(startY).toBeGreaterThanOrEqual(0);
    expect(startY).toBeLessThanOrEqual(1080);
  });

  it('avoids the central 320x240 forbidden box across 200 samples', () => {
    const w = 1920, h = 1080;
    const fx0 = w / 2 - 160, fx1 = w / 2 + 160;
    const fy0 = h / 2 - 120, fy1 = h / 2 + 120;
    let insideCount = 0;
    for (let i = 0; i < 200; i++) {
      const { startX, startY } = pickStart(w, h);
      const inX = startX >= fx0 && startX <= fx1;
      const inY = startY >= fy0 && startY <= fy1;
      if (inX && inY) insideCount++;
    }
    // After 6 attempts the probability of every one landing in the 320x240
    // forbidden box of a 1920x1080 viewport is roughly (0.037)^6 ≈ 2.6e-9.
    // Allow up to 1 outlier across 200 samples for safety.
    expect(insideCount).toBeLessThanOrEqual(1);
  });
});

describe('useInhaleSpawn', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 1920 });
    Object.defineProperty(window, 'innerHeight', { writable: true, configurable: true, value: 1080 });
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it('starts with empty particles', () => {
    const { result } = renderHook(() => useInhaleSpawn(['AI', 'LLM']));
    expect(result.current.particles).toEqual([]);
  });

  it('spawns first particle after 3000ms', () => {
    const { result } = renderHook(() => useInhaleSpawn(['AI', 'LLM']));
    act(() => { vi.advanceTimersByTime(3000); });
    expect(result.current.particles.length).toBe(1);
    expect(['AI', 'LLM']).toContain(result.current.particles[0].text);
    expect(result.current.particles[0].endX).toBe(960);
    expect(result.current.particles[0].endY).toBe(540);
  });

  it('spawns subsequent particles every ~6000ms (allow 4500-7500ms window)', () => {
    const { result } = renderHook(() => useInhaleSpawn(['AI']));
    act(() => { vi.advanceTimersByTime(3000); });
    expect(result.current.particles.length).toBe(1);
    act(() => { vi.advanceTimersByTime(7500); }); // worst-case next window
    expect(result.current.particles.length).toBe(2);
  });

  it('removeParticle drops the matching id', () => {
    const { result } = renderHook(() => useInhaleSpawn(['AI']));
    act(() => { vi.advanceTimersByTime(3000); });
    const id = result.current.particles[0].id;
    act(() => { result.current.removeParticle(id); });
    expect(result.current.particles).toEqual([]);
  });

  it('cleans up timer on unmount without crashing further timer advance', () => {
    const { result, unmount } = renderHook(() => useInhaleSpawn(['AI']));
    act(() => { vi.advanceTimersByTime(3000); });
    expect(result.current.particles.length).toBe(1);
    unmount();
    // advancing timers after unmount should not spawn more or throw
    expect(() => {
      act(() => { vi.advanceTimersByTime(10000); });
    }).not.toThrow();
  });
});
