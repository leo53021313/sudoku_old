// SVG noise overlay — fixed full-viewport, multiply blend, opacity 0.5
// Per outline-visual.md §9.2
export function GlobalGrain() {
  const svgUrl = `data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.15 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E`;
  return (
    <div
      aria-hidden="true"
      style={{
        position: 'fixed', inset: 0, zIndex: 1, pointerEvents: 'none',
        backgroundImage: `url("${svgUrl}")`,
        mixBlendMode: 'multiply',
        opacity: 0.5,
      }}
    />
  );
}
