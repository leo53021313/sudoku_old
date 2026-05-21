export default function ScanlineOverlay() {
  return (
    <div
      aria-hidden="true"
      style={{
        position: 'absolute', inset: 0, overflow: 'hidden',
        pointerEvents: 'none', zIndex: 0,
      }}
    >
      <div
        style={{
          position: 'absolute', top: '-50%', left: 0,
          width: '200%', height: '200%',
          // rgba(196,181,253) is the channel form of --color-neo-muted (#C4B5FD).
          background: 'linear-gradient(90deg, rgba(196,181,253,0) 0%, rgba(196,181,253,0) 45%, rgba(196,181,253,0.18) 50%, rgba(196,181,253,0) 55%, rgba(196,181,253,0) 100%)',
          animation: 'ch3s1-scanline 7s linear 1.8s infinite',
          transform: 'rotate(-20deg)',
        }}
      />
    </div>
  );
}
