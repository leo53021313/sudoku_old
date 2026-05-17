// Pure animation values for A (shake) and C (overshoot) — used by hooks
export const SHAKE_KEYFRAMES = {
  light: { x: [0, 2, -2, 0], y: [0, 1, -1, 0], duration: 0.08 },
  full:  { x: [0, 5, -5, 3, -3, 0], y: [0, 3, -3, 2, -2, 0], duration: 0.15 },
};

export const OVERSHOOT_KEYFRAMES = {
  scale: [0, 1.4, 1.0, 0.95, 1.0],
  duration: 0.6,
  ease: [0.34, 1.56, 0.64, 1],
};
