import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { HubSatellite } from './HubSatellite.jsx';
import { stage } from '../tokens/stage.js';

describe('<HubSatellite>', () => {
  it('renders the hub child and each satellite at named anchors', () => {
    const { getByTestId } = render(
      <HubSatellite gap={48}>
        <HubSatellite.Hub><div data-testid="hub" style={{ width: 200, height: 100 }}>H</div></HubSatellite.Hub>
        <HubSatellite.Satellite position="tl"><div data-testid="tl">tl</div></HubSatellite.Satellite>
        <HubSatellite.Satellite position="br"><div data-testid="br">br</div></HubSatellite.Satellite>
      </HubSatellite>
    );

    expect(getByTestId('hub')).toBeInTheDocument();
    // satellite wrapper sits outside the hub box at the correct anchor
    const tl = getByTestId('tl').parentElement;
    expect(tl.style.position).toBe('absolute');
    expect(tl.style.bottom).toBe('100%');   // sits ABOVE the hub container
    expect(tl.style.right).toBe('100%');    // sits LEFT of the hub container
    expect(tl.style.marginBottom).toBe('48px');
    expect(tl.style.marginRight).toBe('48px');

    const br = getByTestId('br').parentElement;
    expect(br.style.top).toBe('100%');
    expect(br.style.left).toBe('100%');
    expect(br.style.marginTop).toBe('48px');
    expect(br.style.marginLeft).toBe('48px');
  });

  it('caps the cluster container at safe-area dimensions', () => {
    const { container } = render(
      <HubSatellite>
        <HubSatellite.Hub><div /></HubSatellite.Hub>
      </HubSatellite>
    );
    const root = container.firstChild;
    expect(root.style.maxWidth).toBe(`${stage.cluster.maxWidth}px`);
    expect(root.style.maxHeight).toBe(`${stage.cluster.maxHeight}px`);
  });

  it('rejects unknown position values', () => {
    expect(() =>
      render(
        <HubSatellite>
          <HubSatellite.Hub><div /></HubSatellite.Hub>
          <HubSatellite.Satellite position="xx"><div /></HubSatellite.Satellite>
        </HubSatellite>
      )
    ).toThrow(/unknown position/i);
  });

  it('throws if no Hub child is provided', () => {
    expect(() =>
      render(
        <HubSatellite>
          <HubSatellite.Satellite position="tl"><div /></HubSatellite.Satellite>
        </HubSatellite>
      )
    ).toThrow(/requires a Hub/i);
  });
});
