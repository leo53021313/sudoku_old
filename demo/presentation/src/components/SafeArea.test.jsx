import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { stage } from '../tokens/stage.js';
import { SafeArea } from './SafeArea.jsx';

describe('<SafeArea>', () => {
  it('applies the safe padding from tokens', () => {
    const { container } = render(<SafeArea><div data-testid="x" /></SafeArea>);
    const root = container.firstChild;
    expect(root.style.padding).toBe(`${stage.safePadding.y}px ${stage.safePadding.x}px`);
  });

  it('fills the parent (absolute inset 0)', () => {
    const { container } = render(<SafeArea><div /></SafeArea>);
    const root = container.firstChild;
    expect(root.style.position).toBe('absolute');
    expect(root.style.inset).toBe('0px');
  });

  it('renders children', () => {
    const { getByTestId } = render(<SafeArea><div data-testid="x" /></SafeArea>);
    expect(getByTestId('x')).not.toBeNull();
  });
});
