import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { NeuralNet } from './NeuralNet.jsx';

describe('NeuralNet', () => {
  it('renders an SVG with 19 nodes (4+6+6+3)', () => {
    const { container } = render(<NeuralNet active={false} />);
    const svg = container.querySelector('svg');
    expect(svg).not.toBeNull();
    const nodes = container.querySelectorAll('circle[data-role="node"]');
    expect(nodes.length).toBe(19);
  });

  it('renders 4+6+6+3 layer-edge bipartite = 24+36+18 = 78 edges', () => {
    const { container } = render(<NeuralNet active={false} />);
    const edges = container.querySelectorAll('line[data-role="edge"]');
    expect(edges.length).toBe(4 * 6 + 6 * 6 + 6 * 3);
  });

  it('does not render any pulse circles when inactive', () => {
    const { container } = render(<NeuralNet active={false} />);
    const pulses = container.querySelectorAll('circle[data-role="pulse"]');
    expect(pulses.length).toBe(0);
  });

  it('renders pulse circles when active', () => {
    const { container } = render(<NeuralNet active={true} />);
    const pulses = container.querySelectorAll('circle[data-role="pulse"]');
    expect(pulses.length).toBeGreaterThan(0);
  });
});
