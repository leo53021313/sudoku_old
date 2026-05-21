import { describe, it, expect } from 'vitest';
import { pickStart } from './InhaleLayer.jsx';

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
    // After 5 retries the probability of all attempts landing in the 320x240
    // forbidden box of a 1920x1080 viewport is roughly (0.037)^6 ≈ 2.6e-9.
    // Allow up to 1 outlier across 200 samples for safety.
    expect(insideCount).toBeLessThanOrEqual(1);
  });
});
