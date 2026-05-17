// Stage / SafeArea / Cluster tokens — mirror of
// docs/superpowers/specs/2026-05-17-presentation-layout-system-design.md §Tokens
export const stage = {
  width: 1920,
  height: 1080,
  aspectRatio: 16 / 9,
  safePadding: { x: 144, y: 108 },   // 7.5% each side → safe area 1632 × 918
  cluster: {
    // Cluster auto-fits the hub child; these are upper bounds, not target sizes.
    // Step author is responsible for sizing the hub so the cluster (hub + satellite
    // extents) fits inside SafeArea.
    maxWidth: 1632,                  // safe area inner width — hub cap
    maxHeight: 918,                  // safe area inner height — hub cap
    hubToSatelliteGap: 48,           // <HubSatellite gap={48}> default
  },
  ambient: {
    outerBandPct: 15,                // outer 15% reserved for AmbientShapes
  },
};

// Pure function — extracted for unit testing.
// Returns the uniform scale factor that fits 1920×1080 inside the viewport
// while preserving aspect ratio (letterbox on mismatched ratios).
export function computeStageScale(viewportWidth, viewportHeight) {
  return Math.min(viewportWidth / stage.width, viewportHeight / stage.height);
}
