import { usePresentationContext } from '../state/PresentationContext.jsx';
import { Ch1 } from './ch1-coldopen/Ch1.jsx';
import { Ch2 } from './ch2-ml-map/Ch2.jsx';

const CHAPTERS = {
  1: Ch1,
  2: Ch2,
};

export function ChapterRouter() {
  const { chapterId } = usePresentationContext();
  const Chapter = CHAPTERS[chapterId];
  if (!Chapter) {
    return (
      <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk' }}>
        <div style={{ fontSize: 24, fontWeight: 900 }}>ch {chapterId} (not implemented)</div>
        <div style={{ marginTop: 16, color: '#666' }}>Implemented: ch 1, ch 2. Other chapters incoming.</div>
      </main>
    );
  }
  return <Chapter />;
}
