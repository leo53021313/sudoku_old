import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { usePresentation } from './usePresentation.js';

describe('usePresentation', () => {
  it('starts at chapter 1 step 1 beat 0', () => {
    const { result } = renderHook(() => usePresentation());
    expect(result.current.chapterId).toBe(1);
    expect(result.current.stepId).toBe(1);
    expect(result.current.beatIndex).toBe(0);
  });

  it('advances to next beat within a multi-beat step', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 1, stepId: 8 })); // BOOM 3 beats
    expect(result.current.beatIndex).toBe(0);
    act(() => result.current.advance());
    expect(result.current.beatIndex).toBe(1);
    act(() => result.current.advance());
    expect(result.current.beatIndex).toBe(2);
  });

  it('advances across step boundary', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 1, stepId: 1 }));
    act(() => result.current.advance()); // step 1 only has 1 beat → move to step 2
    expect(result.current.stepId).toBe(2);
    expect(result.current.beatIndex).toBe(0);
  });

  it('advances across chapter boundary', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 1, stepId: 8, beatIndex: 2 }));
    act(() => result.current.advance());
    expect(result.current.chapterId).toBe(2);
    expect(result.current.stepId).toBe(1);
  });

  it('retreats to previous beat', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 1, stepId: 8, beatIndex: 2 }));
    act(() => result.current.retreat());
    expect(result.current.beatIndex).toBe(1);
  });

  it('retreats across step boundary', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 1, stepId: 2 }));
    act(() => result.current.retreat());
    expect(result.current.stepId).toBe(1);
    expect(result.current.beatIndex).toBe(0);
  });

  it('jumpTo sets state directly', () => {
    const { result } = renderHook(() => usePresentation());
    act(() => result.current.jumpTo({ chapterId: 6, stepId: 6, beatIndex: 0 }));
    expect(result.current.chapterId).toBe(6);
    expect(result.current.stepId).toBe(6);
  });

  it('does not advance past the last beat', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 9, stepId: 13, beatIndex: 3 }));
    act(() => result.current.advance());
    expect(result.current.chapterId).toBe(9);
    expect(result.current.stepId).toBe(13);
    expect(result.current.beatIndex).toBe(3);
  });

  it('does not retreat past the first beat', () => {
    const { result } = renderHook(() => usePresentation());
    act(() => result.current.retreat());
    expect(result.current.chapterId).toBe(1);
    expect(result.current.stepId).toBe(1);
    expect(result.current.beatIndex).toBe(0);
  });

  it('ch6 step3 has 4 beats then crosses to step 4', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 6, stepId: 3 }));
    expect(result.current.beatIndex).toBe(0);            // milk-tea-enter
    act(() => result.current.advance());
    expect(result.current.stepId).toBe(3);
    expect(result.current.beatIndex).toBe(1);            // name-tag
    act(() => result.current.advance());
    expect(result.current.beatIndex).toBe(2);            // girl-enter
    act(() => result.current.advance());
    expect(result.current.beatIndex).toBe(3);            // reply-plus
    act(() => result.current.advance());
    expect(result.current.stepId).toBe(4);               // 第 4 個 beat 後跨到 step 4
    expect(result.current.beatIndex).toBe(0);
  });

  it('ch7 step7 has 7 beats then crosses to step 8', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 7, stepId: 7 }));
    expect(result.current.beatIndex).toBe(0);
    for (let i = 1; i <= 6; i++) {
      act(() => result.current.advance());
      expect(result.current.stepId).toBe(7);
      expect(result.current.beatIndex).toBe(i);
    }
    act(() => result.current.advance());      // 第 7 個 beat 後跨到 step 8
    expect(result.current.stepId).toBe(8);
    expect(result.current.beatIndex).toBe(0);
  });

  it('ch9 step 6 has 3 beats then crosses to step 7', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 9, stepId: 6 }));
    expect(result.current.beatIndex).toBe(0);
    for (let i = 1; i <= 2; i++) {
      act(() => result.current.advance());
      expect(result.current.stepId).toBe(6);
      expect(result.current.beatIndex).toBe(i);
    }
    act(() => result.current.advance());      // 第 3 個 beat 後跨到 step 7
    expect(result.current.chapterId).toBe(9);
    expect(result.current.stepId).toBe(7);
    expect(result.current.beatIndex).toBe(0);
  });

  it('reports totalBeats = 102', () => {
    const { result } = renderHook(() => usePresentation());
    expect(result.current.totalBeats).toBe(102);
  });
});
