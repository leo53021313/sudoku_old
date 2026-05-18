export function AiBackdrop({ src, alt = '' }) {
  return (
    <img
      src={src}
      alt={alt}
      loading="eager"
      style={{
        position: 'absolute',
        inset: 0,
        width: '100vw',
        height: '100vh',
        objectFit: 'cover',
        objectPosition: 'center',
        zIndex: 5,
        pointerEvents: 'none',
      }}
    />
  );
}
