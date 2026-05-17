// Speaker mode overlay — per outline-visual.md §5.6
import { usePresentationContext } from '../state/PresentationContext.jsx';
import { flattenBeats } from '../data/beat-manifest.js';
import { useMemo } from 'react';

export function PresenterPanel() {
  const { presenter, globalBeatIdx, beat, chapter, step, beatIndex } = usePresentationContext();
  const flat = useMemo(() => flattenBeats(), []);
  if (!presenter) return null;

  const next = flat[globalBeatIdx + 1];

  return (
    <div
      style={{
        position: 'fixed', inset: 0, zIndex: 100, pointerEvents: 'none',
        display: 'flex', flexDirection: 'column',
        background: 'rgba(255,253,245,0.96)', padding: 24,
        fontFamily: 'Space Grotesk', color: '#000',
      }}
    >
      <div style={{ borderBottom: '4px solid #000', paddingBottom: 12, fontSize: 16, fontWeight: 700 }}>
        ch {chapter.id} / 9 · step {step.id} · beat {beatIndex + 1} / {step.beats.length}
        {step.starLevel === 3 && <span style={{ marginLeft: 12, color: '#FF6B6B' }}>★★★</span>}
        {step.starLevel === 2 && <span style={{ marginLeft: 12, color: '#FF6B6B' }}>★★</span>}
      </div>

      <div style={{ marginTop: 24, fontSize: 14, fontWeight: 700, color: '#666' }}>▣ Cue (該說):</div>
      <div style={{ marginTop: 8, fontSize: 24, fontWeight: 900, lineHeight: 1.4 }}>
        {beat.cue ?? <em style={{ color: '#999' }}>（無 cue）</em>}
      </div>

      <div style={{ marginTop: 24, fontSize: 14, fontWeight: 700, color: '#666' }}>▣ Wait:</div>
      <div style={{ marginTop: 8, fontSize: 18, fontWeight: 700 }}>
        {beat.wait ?? <em style={{ color: '#999' }}>—</em>}
      </div>

      {next && (
        <div style={{ marginTop: 'auto', borderTop: '4px solid #000', paddingTop: 12, fontSize: 14, fontWeight: 700 }}>
          下一 beat: ch{next.chapterId} step{next.stepId} · {next.beat.id}
          <div style={{ fontSize: 14, color: '#666', marginTop: 4 }}>cue: {next.beat.cue ?? '—'}</div>
        </div>
      )}
    </div>
  );
}
