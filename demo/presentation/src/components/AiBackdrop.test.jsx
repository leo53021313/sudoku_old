import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AiBackdrop } from './AiBackdrop.jsx';

describe('AiBackdrop', () => {
  it('renders an img with src and alt', () => {
    render(<AiBackdrop src="/images/ai/ch1/mrt-window.png" alt="MRT" />);
    const img = screen.getByAltText('MRT');
    expect(img.tagName).toBe('IMG');
    expect(img.getAttribute('src')).toBe('/images/ai/ch1/mrt-window.png');
  });

  it('applies full-bleed positioning style with z-index 5', () => {
    render(<AiBackdrop src="/x.png" alt="x" />);
    const img = screen.getByAltText('x');
    expect(img).toHaveStyle({
      position: 'absolute',
      width: '100vw',
      height: '100vh',
      zIndex: '5',
      objectFit: 'cover',
    });
  });

  it('defaults alt to empty string when not provided', () => {
    const { container } = render(<AiBackdrop src="/x.png" />);
    const img = container.querySelector('img');
    expect(img.getAttribute('alt')).toBe('');
  });
});
