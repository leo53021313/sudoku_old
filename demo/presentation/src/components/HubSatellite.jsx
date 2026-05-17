import { Children, isValidElement } from 'react';
import { stage } from '../tokens/stage.js';

// Each satellite wrapper anchors to a HUB EDGE and sits OUTSIDE the hub
// container, offset by `gap`. Uses `bottom: 100%` / `top: 100%` etc. so the
// satellite's edge meets the hub's edge with no overlap; margins push it
// further by `gap`.
function getAnchorStyle(position, gap) {
  switch (position) {
    case 'tl': return { bottom: '100%', right: '100%', marginBottom: gap, marginRight: gap };
    case 't':  return { bottom: '100%', left: '50%',   marginBottom: gap, transform: 'translateX(-50%)' };
    case 'tr': return { bottom: '100%', left: '100%',  marginBottom: gap, marginLeft: gap };
    case 'l':  return { top: '50%',     right: '100%', marginRight: gap,  transform: 'translateY(-50%)' };
    case 'r':  return { top: '50%',     left: '100%',  marginLeft: gap,   transform: 'translateY(-50%)' };
    case 'bl': return { top: '100%',    right: '100%', marginTop: gap,    marginRight: gap };
    case 'b':  return { top: '100%',    left: '50%',   marginTop: gap,    transform: 'translateX(-50%)' };
    case 'br': return { top: '100%',    left: '100%',  marginTop: gap,    marginLeft: gap };
    default:   return null;
  }
}

const KNOWN_POSITIONS = ['tl', 't', 'tr', 'l', 'r', 'bl', 'b', 'br'];

function Hub({ children }) {
  return <>{children}</>;
}
Hub.displayName = 'HubSatellite.Hub';

function Satellite({ children }) {
  return <>{children}</>;
}
Satellite.displayName = 'HubSatellite.Satellite';

export function HubSatellite({ children, gap = stage.cluster.hubToSatelliteGap, style = {} }) {
  let hub = null;
  const satellites = [];

  Children.forEach(children, (child) => {
    if (!isValidElement(child)) return;
    if (child.type === Hub) {
      hub = child;
    } else if (child.type === Satellite) {
      const pos = child.props.position;
      if (!KNOWN_POSITIONS.includes(pos)) {
        throw new Error(`HubSatellite: unknown position "${pos}". Allowed: ${KNOWN_POSITIONS.join(', ')}`);
      }
      if (satellites.some(s => s.props.position === pos)) {
        throw new Error(`HubSatellite: duplicate position "${pos}" — each anchor can only be used once`);
      }
      satellites.push(child);
    }
  });

  if (!hub) {
    throw new Error('HubSatellite: requires a Hub child (<HubSatellite.Hub>)');
  }

  return (
    <div
      style={{
        position: 'relative',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        maxWidth: stage.cluster.maxWidth,
        maxHeight: stage.cluster.maxHeight,
        margin: '0 auto',
        ...style,
      }}
    >
      {hub.props.children}
      {satellites.map((sat) => {
        const anchor = getAnchorStyle(sat.props.position, gap);
        return (
          <div
            key={sat.props.position}
            style={{
              position: 'absolute',
              ...anchor,
            }}
          >
            {sat.props.children}
          </div>
        );
      })}
    </div>
  );
}

HubSatellite.Hub = Hub;
HubSatellite.Satellite = Satellite;
