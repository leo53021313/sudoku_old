import { describe, it, expect, vi } from 'vitest';
import { render, act } from '@testing-library/react';
import { CounterUp } from './CounterUp.jsx';

describe('CounterUp', () => {
  it('renders initial value with prefix', () => {
    const { container } = render(<CounterUp from={20} to={50} prefix="+" duration={1200} />);
    expect(container.textContent).toContain('+20');
  });

  it('renders without prefix when not provided', () => {
    const { container } = render(<CounterUp from={0} to={10} duration={500} />);
    expect(container.textContent).toMatch(/^0/);
  });

  it('calls onComplete after animation ends', async () => {
    vi.useFakeTimers();
    const onComplete = vi.fn();
    render(<CounterUp from={0} to={5} duration={100} onComplete={onComplete} />);
    await act(async () => {
      vi.advanceTimersByTime(200);
    });
    expect(onComplete).toHaveBeenCalledTimes(1);
    vi.useRealTimers();
  });
});
