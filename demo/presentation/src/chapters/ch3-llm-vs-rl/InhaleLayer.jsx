// Central forbidden zone half-width / half-height — keeps inhale particles
// from spawning on top of the LLM hero (which sits at viewport center).
const FORBIDDEN_HALF_W = 160;
const FORBIDDEN_HALF_H = 120;
const MAX_ATTEMPTS = 6;

export function pickStart(viewportW, viewportH) {
  const fx0 = viewportW / 2 - FORBIDDEN_HALF_W;
  const fx1 = viewportW / 2 + FORBIDDEN_HALF_W;
  const fy0 = viewportH / 2 - FORBIDDEN_HALF_H;
  const fy1 = viewportH / 2 + FORBIDDEN_HALF_H;
  let startX = 0, startY = 0;
  for (let i = 0; i < MAX_ATTEMPTS; i++) {
    startX = Math.random() * viewportW;
    startY = Math.random() * viewportH;
    const inX = startX >= fx0 && startX <= fx1;
    const inY = startY >= fy0 && startY <= fy1;
    if (!(inX && inY)) return { startX, startY };
  }
  return { startX, startY }; // all MAX_ATTEMPTS landed in the forbidden box — return the last sample
}
