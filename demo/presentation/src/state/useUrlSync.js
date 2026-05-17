import { useEffect } from 'react';

const intOr = (s, d) => {
  const n = parseInt(s, 10);
  return Number.isFinite(n) && n > 0 ? n : d;
};

export function parseUrl(href) {
  const u = new URL(href);
  return {
    chapterId: intOr(u.searchParams.get('ch'), 1),
    stepId:    intOr(u.searchParams.get('step'), 1),
    beatIndex: Math.max(0, parseInt(u.searchParams.get('beat'), 10) || 0),
    presenter: u.searchParams.get('presenter') === '1',
  };
}

export function buildUrl({ chapterId, stepId, beatIndex, presenter }) {
  const p = new URLSearchParams();
  p.set('ch', String(chapterId));
  p.set('step', String(stepId));
  p.set('beat', String(beatIndex));
  if (presenter) p.set('presenter', '1');
  return '?' + p.toString();
}

export function useUrlSync({ chapterId, stepId, beatIndex }, presenter) {
  useEffect(() => {
    const next = buildUrl({ chapterId, stepId, beatIndex, presenter });
    if (window.location.search !== next) {
      window.history.replaceState(null, '', next);
    }
  }, [chapterId, stepId, beatIndex, presenter]);
}
