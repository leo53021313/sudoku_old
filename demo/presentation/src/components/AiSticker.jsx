export function AiSticker({ src, alt = '', width = 280, rotation = -3, shadow = 8 }) {
  return (
    <div style={{
      display: 'inline-block',
      border: '4px solid #000',
      boxShadow: `${shadow}px ${shadow}px 0 0 #000`,
      transform: `rotate(${rotation}deg)`,
      background: '#FFFDF5',
      lineHeight: 0,
    }}>
      <img
        src={src}
        alt={alt}
        loading="lazy"
        style={{ display: 'block', width, height: 'auto' }}
      />
    </div>
  );
}
