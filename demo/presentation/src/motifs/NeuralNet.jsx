import { motion } from 'motion/react';

const LAYERS = [4, 6, 6, 3];
const VB_W = 320;
const VB_H = 200;
const COLS = LAYERS.length;

function nodeXY(layerIdx, nodeIdx, layerSize) {
  const x = ((layerIdx + 0.5) / COLS) * VB_W;
  const y = ((nodeIdx + 0.5) / layerSize) * VB_H;
  return { x, y };
}

function buildEdges() {
  const edges = [];
  for (let l = 0; l < LAYERS.length - 1; l++) {
    for (let a = 0; a < LAYERS[l]; a++) {
      for (let b = 0; b < LAYERS[l + 1]; b++) {
        const p1 = nodeXY(l, a, LAYERS[l]);
        const p2 = nodeXY(l + 1, b, LAYERS[l + 1]);
        edges.push({ p1, p2, key: `${l}-${a}-${b}` });
      }
    }
  }
  return edges;
}

const EDGES = buildEdges();

export function NeuralNet({
  active = false,
  pulseInterval = 500,
  colors = { pulsePos: '#FFD93D', pulseNeg: '#FF6B6B' },
}) {
  const nodes = LAYERS.flatMap((sz, l) =>
    Array.from({ length: sz }, (_, n) => ({ ...nodeXY(l, n, sz), key: `n${l}-${n}` }))
  );

  return (
    <svg viewBox={`0 0 ${VB_W} ${VB_H}`} preserveAspectRatio="xMidYMid meet" width="100%" height="100%">
      {EDGES.map(e => (
        <line
          key={e.key}
          data-role="edge"
          x1={e.p1.x} y1={e.p1.y} x2={e.p2.x} y2={e.p2.y}
          stroke="#000" strokeWidth={2} opacity={0.35}
        />
      ))}
      {nodes.map(n => (
        <circle
          key={n.key}
          data-role="node"
          cx={n.x} cy={n.y} r={8}
          fill="#000" stroke="#000" strokeWidth={2}
        />
      ))}
      {active && EDGES.map((e, i) => (
        <motion.circle
          key={`p-${e.key}`}
          data-role="pulse"
          r={5}
          fill={i % 2 === 0 ? colors.pulsePos : colors.pulseNeg}
          initial={{ cx: e.p1.x, cy: e.p1.y, opacity: 0 }}
          animate={{ cx: [e.p1.x, e.p2.x], cy: [e.p1.y, e.p2.y], opacity: [0, 1, 0] }}
          transition={{
            duration: 0.8,
            ease: 'linear',
            repeat: Infinity,
            repeatDelay: pulseInterval / 1000 + (i * 0.05),
            delay: (i * 0.05) % 1.5,
          }}
        />
      ))}
    </svg>
  );
}
