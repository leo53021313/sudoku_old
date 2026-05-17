const COLOR_MAP = {
  accent:    '#FF6B6B',
  secondary: '#FFD93D',
  muted:     '#C4B5FD',
  cream:     '#FFFDF5',
  ink:       '#000000',
};
const SHADOW_MAP = {
  sm:      '4px 4px 0 0 #000',
  md:      '8px 8px 0 0 #000',
  lg:      '12px 12px 0 0 #000',
  massive: '16px 16px 0 0 #000',
  burst:   '20px 20px 0 0 #000',
};

export function Sticker({
  bg = 'accent', textColor, border = 4, shadow = 'md',
  rotation = 0, padding = 16, children, className = '', style = {},
}) {
  return (
    <div
      className={className}
      style={{
        display: 'inline-block',
        background: COLOR_MAP[bg] ?? bg,
        color: textColor ? (COLOR_MAP[textColor] ?? textColor) : '#000',
        border: `${border}px solid #000`,
        boxShadow: SHADOW_MAP[shadow] ?? shadow,
        padding,
        transform: `rotate(${rotation}deg)`,
        fontFamily: 'Space Grotesk',
        fontWeight: 900,
        ...style,
      }}
    >
      {children}
    </div>
  );
}
