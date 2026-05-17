import { PresentationProvider, usePresentationContext } from './state/PresentationContext.jsx';
import { ChapterRouter } from './chapters/index.jsx';
import { ProgressBar } from './components/ProgressBar.jsx';
import { ChapterNav } from './components/ChapterNav.jsx';
import { BeatIndicator } from './components/BeatIndicator.jsx';
import { PresenterPanel } from './components/PresenterPanel.jsx';
import { Stage } from './components/Stage.jsx';
import { SafeArea } from './components/SafeArea.jsx';
import { FadeBridge } from './layers/FadeBridge.jsx';
import { GlobalGrain } from './layers/GlobalGrain.jsx';
import { HalftoneBg } from './layers/HalftoneBg.jsx';
import { ChapterTint } from './layers/ChapterTint.jsx';
import { AmbientShapes } from './layers/AmbientShapes.jsx';
import { ScreenShake } from './motifs/ScreenShake.jsx';

function Frame() {
  const { chapterId, shakeRef } = usePresentationContext();
  return (
    <ScreenShake ref={shakeRef}>
      <Stage>
        <GlobalGrain />
        <HalftoneBg />
        <ChapterTint chapterId={chapterId} />
        <AmbientShapes chapterId={chapterId} />
        <SafeArea>
          <ChapterRouter />
        </SafeArea>
        <FadeBridge chapterId={chapterId} />
      </Stage>
      {/* Chrome stays outside the scaled canvas — pinned to viewport corners */}
      <BeatIndicator />
      <ProgressBar />
      <ChapterNav />
      <PresenterPanel />
    </ScreenShake>
  );
}

export default function App() {
  return (
    <PresentationProvider>
      <Frame />
    </PresentationProvider>
  );
}
