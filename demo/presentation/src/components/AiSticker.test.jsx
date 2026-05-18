import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AiSticker } from './AiSticker.jsx';

describe('AiSticker', () => {
  it('renders an img wrapped in bordered div', () => {
    render(<AiSticker src="/images/ai/ch2/teacher-notes.png" alt="Teacher" />);
    const img = screen.getByAltText('Teacher');
    expect(img.tagName).toBe('IMG');
    expect(img.parentElement.tagName).toBe('DIV');
    expect(img.parentElement).toHaveStyle({
      border: '4px solid #000',
    });
  });

  it('applies default rotation -3deg and 8px hard shadow', () => {
    render(<AiSticker src="/x.png" alt="x" />);
    const wrapper = screen.getByAltText('x').parentElement;
    expect(wrapper).toHaveStyle({
      transform: 'rotate(-3deg)',
      boxShadow: '8px 8px 0 0 #000',
    });
  });

  it('respects custom rotation, width, shadow props', () => {
    render(<AiSticker src="/x.png" alt="x" rotation={2} width={420} shadow={12} />);
    const img = screen.getByAltText('x');
    const wrapper = img.parentElement;
    expect(wrapper).toHaveStyle({
      transform: 'rotate(2deg)',
      boxShadow: '12px 12px 0 0 #000',
    });
    expect(img).toHaveStyle({ width: '420px' });
  });

  it('defaults alt to empty string when not provided', () => {
    const { container } = render(<AiSticker src="/x.png" />);
    const img = container.querySelector('img');
    expect(img.getAttribute('alt')).toBe('');
  });
});
