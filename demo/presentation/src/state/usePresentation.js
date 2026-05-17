import { useState, useCallback } from 'react';
import { manifest, flattenBeats } from '../data/beat-manifest.js';

const FLAT = flattenBeats();
const TOTAL = FLAT.length;

function findIndex(chapterId, stepId, beatIndex) {
  for (let i = 0; i < FLAT.length; i++) {
    const f = FLAT[i];
    if (f.chapterId === chapterId && f.stepId === stepId) {
      return i + beatIndex;
    }
  }
  return 0;
}

export function usePresentation(initial = {}) {
  const startIdx = findIndex(
    initial.chapterId ?? 1,
    initial.stepId ?? 1,
    initial.beatIndex ?? 0,
  );
  const [globalBeatIdx, setGlobalBeatIdx] = useState(startIdx);

  const current = FLAT[globalBeatIdx];

  const advance = useCallback(() => {
    setGlobalBeatIdx(idx => Math.min(idx + 1, TOTAL - 1));
  }, []);

  const retreat = useCallback(() => {
    setGlobalBeatIdx(idx => Math.max(idx - 1, 0));
  }, []);

  const jumpTo = useCallback(({ chapterId, stepId, beatIndex = 0 }) => {
    setGlobalBeatIdx(findIndex(chapterId, stepId, beatIndex));
  }, []);

  // Compute beatIndex within current step: walk backwards to find the
  // first beat of the current step, then beatIndex = globalBeatIdx - stepStart.
  let stepStart = globalBeatIdx;
  for (let i = globalBeatIdx - 1; i >= 0; i--) {
    if (FLAT[i].chapterId === current.chapterId && FLAT[i].stepId === current.stepId) {
      stepStart = i;
    } else {
      break;
    }
  }
  const beatIndex = globalBeatIdx - stepStart;

  return {
    chapterId: current.chapterId,
    stepId: current.stepId,
    beatIndex,
    beat: current.beat,
    step: current.step,
    chapter: current.chapter,
    globalBeatIdx,
    totalBeats: TOTAL,
    advance,
    retreat,
    jumpTo,
  };
}
