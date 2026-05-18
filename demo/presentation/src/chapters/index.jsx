import { usePresentationContext } from '../state/PresentationContext.jsx';
import { Ch1 } from './ch1-coldopen/Ch1.jsx';
import { Ch2 } from './ch2-ml-map/Ch2.jsx';
import { Ch3 } from './ch3-llm-vs-rl/Ch3.jsx';
import { Ch4 } from './ch4-data-hunt/Ch4.jsx';
import { Ch5 } from './ch5-legacy/Ch5.jsx';
import { Ch6 } from './ch6-sb3/Ch6.jsx';
import { Ch7 } from './ch7-reasoner/Ch7.jsx';
import { Ch8 } from './ch8-apprentice/Ch8.jsx';
import { Ch9 } from './ch9-callback/Ch9.jsx';

const CHAPTERS = {
  1: Ch1,
  2: Ch2,
  3: Ch3,
  4: Ch4,
  5: Ch5,
  6: Ch6,
  7: Ch7,
  8: Ch8,
  9: Ch9,
};

export function ChapterRouter() {
  const { chapterId } = usePresentationContext();
  const Chapter = CHAPTERS[chapterId];
  if (!Chapter) {
    return (
      <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk' }}>
        <div style={{ fontSize: 24, fontWeight: 900 }}>ch {chapterId} (not implemented)</div>
        <div style={{ marginTop: 16, color: '#666' }}>Implemented: ch 1, ch 2, ch 3, ch 4, ch 5, ch 6, ch 7, ch 8, ch 9. Other chapters incoming.</div>
      </main>
    );
  }
  return <Chapter />;
}
