import { PresentationProvider, usePresentationContext } from './state/PresentationContext.jsx';
import { Sandbox } from './pages/Sandbox.jsx';
import { ProgressBar } from './components/ProgressBar.jsx';
import { ChapterNav } from './components/ChapterNav.jsx';
import { BeatIndicator } from './components/BeatIndicator.jsx';
import { PresenterPanel } from './components/PresenterPanel.jsx';
import { FadeBridge } from './layers/FadeBridge.jsx';

function Frame() {
  const { chapterId } = usePresentationContext();
  // Phase 0: route always shows Sandbox. Phase 1+ will switch on chapterId/stepId.
  return (
    <>
      <Sandbox />
      <FadeBridge chapterId={chapterId} />
      <BeatIndicator />
      <ProgressBar />
      <ChapterNav />
      <PresenterPanel />
    </>
  );
}

export default function App() {
  return (
    <PresentationProvider>
      <Frame />
    </PresentationProvider>
  );
}
