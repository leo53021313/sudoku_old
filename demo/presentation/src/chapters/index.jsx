import { usePresentationContext } from '../state/PresentationContext.jsx';
import { Ch1 } from './ch1-coldopen/Ch1.jsx';

const CHAPTERS = {
  1: Ch1,
  // 2-9 added in later phases
};

export function ChapterRouter() {
  const { chapterId } = usePresentationContext();
  const Chapter = CHAPTERS[chapterId];
  if (!Chapter) {
    return (
      <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk' }}>
        <div style={{ fontSize: 24, fontWeight: 900 }}>ch {chapterId} (not implemented)</div>
        <div style={{ marginTop: 16, color: '#666' }}>Phase 1 implements ch 1 only. Use the chapter nav (hover top-right) to jump back to ch 1.</div>
      </main>
    );
  }
  return <Chapter />;
}
