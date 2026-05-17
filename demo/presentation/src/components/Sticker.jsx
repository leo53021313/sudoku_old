const COLOR_MAP = {
  accent:    '#FF6B6B',
  secondary: '#FFD93D',
  muted:     '#C4B5FD',
  cream:     '#FFFDF5',
  ink:       '#000000',
};

export const STICKER_VARIANTS = {
  'hub-md': {
    fontSize: '4rem',
    padding: '48px 64px',
    border: 6,
    shadow: 'massive',
  },
  'hub-lg': {
    fontSize: '6rem',
    padding: '56px 72px',
    border: 6,
    shadow: 'massive',
  },
  'hub-mega': {
    fontSize: '8rem',
    padding: '64px 96px',
    border: 8,
    shadow: 'burst',
  },
  'sat-lg': {
    fontSize: '1.75rem',
    padding: '20px 32px',
    border: 4,
    shadow: 'lg',
    minWidth: 160,
  },
  'sat-md': {
    fontSize: '1.5rem',
    padding: '16px 24px',
    border: 4,
    shadow: 'md',
    minWidth: 140,
  },
  'sat-sm': {
    fontSize: '1.25rem',
    padding: '12px 20px',
    border: 3,
    shadow: 'md',
    minWidth: 80,
  },
  kicker: {
    fontSize: '1.25rem',
    padding: '12px 28px',
    border: 3,
    shadow: 'sm',
  },
};

const SHADOW_MAP = {
  sm:      '4px 4px 0 0 #000',
  md:      '8px 8px 0 0 #000',
  lg:      '12px 12px 0 0 #000',
  massive: '16px 16px 0 0 #000',
  burst:   '20px 20px 0 0 #000',
};

export function Sticker({
  variant = 'sat-lg',
  bg = 'cream',
  textColor,
  rotation = 0,
  children,
  className = '',
  style = {},
  // legacy overrides — kept for incremental migration
  border, padding, shadow,
}) {
  const v = STICKER_VARIANTS[variant];
  if (!v) {
    throw new Error(`Sticker: unknown variant "${variant}". Allowed: ${Object.keys(STICKER_VARIANTS).join(', ')}`);
  }
  // `border` must be a pixel integer (e.g. 4 → "4px solid #000")
  const effBorder = border ?? v.border;
  const effPadding = padding != null
    ? (typeof padding === 'number' ? `${padding}px` : padding)
    : v.padding;
  const effShadow = shadow ?? v.shadow;

  return (
    <div
      className={className}
      style={{
        display: 'inline-block',
        background: COLOR_MAP[bg] ?? bg,
        color: textColor ? (COLOR_MAP[textColor] ?? textColor) : '#000',
        border: `${effBorder}px solid #000`,
        boxShadow: SHADOW_MAP[effShadow] ?? effShadow,
        padding: effPadding,
        fontSize: v.fontSize,
        minWidth: v.minWidth,
        transform: `rotate(${rotation}deg)`,
        fontFamily: 'Space Grotesk',
        fontWeight: 900,
        lineHeight: 1.2,
        textAlign: 'center',
        ...style,
      }}
    >
      {children}
    </div>
  );
}
