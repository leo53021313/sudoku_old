import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import ScanlineOverlay from './ScanlineOverlay.jsx';

describe('ScanlineOverlay', () => {
  it('renders a non-interactive overlay container with zero z-index', () => {
    const { container } = render(<ScanlineOverlay />);
    const outer = container.firstChild;
    expect(outer.getAttribute('aria-hidden')).toBe('true');
    expect(outer).toHaveStyle({
      position: 'absolute',
      pointerEvents: 'none',
      overflow: 'hidden',
      zIndex: '0',
    });
  });

  it('renders an inner bar with the scanline animation and purple gradient', () => {
    const { container } = render(<ScanlineOverlay />);
    const bar = container.firstChild.firstChild;
    const style = bar.getAttribute('style') || '';
    expect(style).toContain('animation');
    expect(style).toContain('ch3s1-scanline');
    expect(style).toContain('rgba(196, 181, 253'); // C4B5FD encoded as rgba channels
  });
});
