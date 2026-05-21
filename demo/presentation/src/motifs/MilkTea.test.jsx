import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MilkTea } from './MilkTea.jsx';

describe('MilkTea', () => {
  it('預設渲染奶茶 AI sticker', () => {
    render(<MilkTea />);
    const img = screen.getByAltText('奶茶');
    expect(img.tagName).toBe('IMG');
    expect(img.getAttribute('src')).toBe('/images/ai/ch6/milk-tea.png');
  });

  it('圖片載入失敗時 fallback 到 AssetPlaceholder', () => {
    render(<MilkTea />);
    fireEvent.error(screen.getByAltText('奶茶'));
    expect(screen.getByLabelText('TODO: ch6-milk-tea')).toBeInTheDocument();
  });
});
