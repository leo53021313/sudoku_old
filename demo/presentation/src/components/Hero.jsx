const SIZE_MAP = {
  mega: '8rem',
  hero: '6rem',
  h1:   '3.75rem',
  h2:   '3rem',
};

export function Hero({ size = 'hero', children, color, stroke = false, className = '', style = {} }) {
  return (
    <div
      className={className}
      style={{
        position: 'absolute', inset: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: 'Space Grotesk',
        fontWeight: 900,
        fontSize: SIZE_MAP[size] ?? size,
        lineHeight: 1.05,
        textAlign: 'center',
        color: stroke ? 'transparent' : (color ?? '#000'),
        WebkitTextStroke: stroke ? '2px black' : 'initial',
        ...style,
      }}
    >
      {children}
    </div>
  );
}
