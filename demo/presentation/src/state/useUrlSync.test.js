import { describe, it, expect } from 'vitest';
import { parseUrl, buildUrl } from './useUrlSync.js';

describe('useUrlSync helpers', () => {
  it('parseUrl returns default when no params', () => {
    expect(parseUrl('http://localhost/')).toEqual({ chapterId: 1, stepId: 1, beatIndex: 0, presenter: false });
  });

  it('parseUrl reads ?ch=6&step=6&beat=2', () => {
    expect(parseUrl('http://localhost/?ch=6&step=6&beat=2')).toEqual({
      chapterId: 6, stepId: 6, beatIndex: 2, presenter: false,
    });
  });

  it('parseUrl reads ?presenter=1', () => {
    expect(parseUrl('http://localhost/?presenter=1').presenter).toBe(true);
  });

  it('buildUrl serializes state', () => {
    expect(buildUrl({ chapterId: 6, stepId: 6, beatIndex: 2 })).toBe('?ch=6&step=6&beat=2');
  });

  it('buildUrl preserves presenter flag', () => {
    expect(buildUrl({ chapterId: 1, stepId: 1, beatIndex: 0, presenter: true })).toBe('?ch=1&step=1&beat=0&presenter=1');
  });

  it('parseUrl ignores invalid values', () => {
    const r = parseUrl('http://localhost/?ch=foo&step=-1&beat=abc');
    expect(r.chapterId).toBe(1);
    expect(r.stepId).toBe(1);
    expect(r.beatIndex).toBe(0);
  });
});
