// Halftone dots with 60s drift loop — per outline-visual.md §9.4
export function HalftoneBg() {
  return (
    <div
      aria-hidden="true"
      className="halftone-bg"
      style={{
        position: 'fixed', inset: 0, zIndex: 5, pointerEvents: 'none',
        backgroundImage: 'radial-gradient(#000 1.5px, transparent 1.5px)',
        backgroundSize: '20px 20px',
        opacity: 0.15,
        animation: 'halftone-drift 60s linear infinite',
      }}
    />
  );
}
