// 4-6 floating shapes per chapter — per outline-visual.md §9.6
import { getChapter } from '../tokens/chapters.js';

const POSITION_STYLE = {
  tl: { top: '5%',  left: '5%'  },
  tr: { top: '5%',  right: '5%' },
  bl: { bottom: '8%', left: '5%' },
  br: { bottom: '8%', right: '5%' },
  ml: { top: '50%', left: '3%',  transform: 'translateY(-50%)' },
  mr: { top: '50%', right: '3%', transform: 'translateY(-50%)' },
  mc: { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' },
};

const COLOR_MAP = {
  accent:    '#FF6B6B',
  secondary: '#FFD93D',
  muted:     '#C4B5FD',
  ink:       '#000000',
};

function Shape({ shape, color, outline }) {
  const fill = COLOR_MAP[color] ?? color;
  const border = outline ? `4px solid ${fill}` : 'none';
  const bg = outline ? 'transparent' : fill;
  if (shape === 'star') {
    return <svg width="48" height="48" viewBox="0 0 48 48" style={{ overflow: 'visible' }}>
      <polygon points="24,2 30,18 47,18 33,28 38,46 24,36 10,46 15,28 1,18 18,18"
        fill={outline ? 'transparent' : fill} stroke="#000" strokeWidth="3" strokeLinejoin="miter" />
    </svg>;
  }
  if (shape === 'triangle') {
    return <svg width="48" height="48" viewBox="0 0 48 48">
      <polygon points="24,4 44,44 4,44" fill={outline ? 'transparent' : fill} stroke="#000" strokeWidth="3" strokeLinejoin="miter" />
    </svg>;
  }
  if (shape === 'circle') {
    return <div style={{ width: 48, height: 48, borderRadius: '50%', background: bg, border: outline ? border : '3px solid #000' }} />;
  }
  if (shape === 'pill') {
    return <div style={{ width: 72, height: 28, borderRadius: 9999, background: bg, border: outline ? border : '3px solid #000' }} />;
  }
  if (shape === 'outline-question') {
    return <div style={{
      width: 48, height: 48, display: 'flex', alignItems: 'center', justifyContent: 'center',
      border: '3px solid #000', background: 'transparent', fontFamily: 'Space Grotesk', fontWeight: 900, fontSize: 32,
    }}>?</div>;
  }
  // default: square
  return <div style={{ width: 48, height: 48, background: bg, border: outline ? border : '3px solid #000' }} />;
}

export function AmbientShapes({ chapterId }) {
  const ch = getChapter(chapterId);
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none' }}>
      {ch.ambientShapes.map((s, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            ...POSITION_STYLE[s.position],
            transform: `${POSITION_STYLE[s.position]?.transform ?? ''} rotate(${s.rotation}deg)`,
            animation: `ambient-float ${4 + (i % 4)}s ease-in-out infinite`,
            animationDelay: `${i * 0.3}s`,
          }}
        >
          <Shape shape={s.shape} color={s.color} outline={s.outline} />
        </div>
      ))}
    </div>
  );
}
