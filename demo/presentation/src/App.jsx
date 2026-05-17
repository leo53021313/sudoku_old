import { PresentationProvider, usePresentationContext } from './state/PresentationContext.jsx';

function CurrentBeat() {
  const { chapterId, stepId, beatIndex, beat, totalBeats, globalBeatIdx } = usePresentationContext();
  return (
    <div className="p-8 font-grotesk">
      <div className="text-sm">beat {globalBeatIdx + 1} / {totalBeats}</div>
      <div className="text-3xl font-black mt-4">ch {chapterId} · step {stepId} · beat {beatIndex} ({beat.id})</div>
      <div className="mt-2 text-base">cue: {beat.cue ?? '—'}</div>
      <div className="text-base">wait: {beat.wait ?? '—'}</div>
      <div className="mt-4 text-sm text-gray-600">Left-click / Space / → advance · Right-click / ← retreat · Esc progress</div>
    </div>
  );
}

export default function App() {
  return (
    <PresentationProvider>
      <CurrentBeat />
    </PresentationProvider>
  );
}
