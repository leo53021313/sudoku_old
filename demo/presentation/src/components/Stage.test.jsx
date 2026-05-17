import { describe, it, expect, vi } from 'vitest';
import { render, act } from '@testing-library/react';
import { computeStageScale, stage } from '../tokens/stage.js';
import { Stage } from './Stage.jsx';

describe('computeStageScale', () => {
  it('returns 1.0 at native 1080p', () => {
    expect(computeStageScale(1920, 1080)).toBe(1);
  });

  it('returns ~1.333 at 2K (2560×1440)', () => {
    expect(computeStageScale(2560, 1440)).toBeCloseTo(1.333, 2);
  });

  it('returns 2.0 at 4K (3840×2160)', () => {
    expect(computeStageScale(3840, 2160)).toBe(2);
  });

  it('letterboxes on 4:3 by picking the smaller dimension', () => {
    // 1600×1200 (4:3): width-fit = 0.833, height-fit = 1.111 → pick 0.833
    expect(computeStageScale(1600, 1200)).toBeCloseTo(0.833, 2);
  });
});

describe('<Stage>', () => {
  it('renders children inside a 1920×1080 inner canvas', () => {
    const { container } = render(<Stage><div data-testid="child" /></Stage>);
    const canvas = container.querySelector('[data-stage-canvas]');
    expect(canvas).not.toBeNull();
    expect(canvas.style.width).toBe(`${stage.width}px`);
    expect(canvas.style.height).toBe(`${stage.height}px`);
    expect(canvas.querySelector('[data-testid="child"]')).not.toBeNull();
  });

  it('updates scale when window resizes', () => {
    // jsdom default viewport is 1024×768 — pick a target that produces a distinct scale
    const { container } = render(<Stage><div /></Stage>);
    const canvas = container.querySelector('[data-stage-canvas]');
    const initialTransform = canvas.style.transform;

    // Resize viewport to 3840×2160 (4K) → scale 2.0
    Object.defineProperty(window, 'innerWidth',  { value: 3840, configurable: true });
    Object.defineProperty(window, 'innerHeight', { value: 2160, configurable: true });
    act(() => { window.dispatchEvent(new Event('resize')); });

    expect(canvas.style.transform).toBe('scale(2)');
    expect(canvas.style.transform).not.toBe(initialTransform);
  });

  it('removes the resize listener on unmount', () => {
    const spy = vi.spyOn(window, 'removeEventListener');
    const { unmount } = render(<Stage><div /></Stage>);
    unmount();
    expect(spy).toHaveBeenCalledWith('resize', expect.any(Function));
    spy.mockRestore();
  });
});
