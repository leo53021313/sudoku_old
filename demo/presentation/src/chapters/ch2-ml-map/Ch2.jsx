import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch2Step1 from './Ch2Step1.jsx';

const STEPS = {
  1: Ch2Step1,
};

export function Ch2() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) {
    return (
      <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk' }}>
        <div style={{ fontSize: 24, fontWeight: 900 }}>ch 2 · step {stepId}</div>
        <div style={{ marginTop: 16, color: '#666' }}>(not yet implemented)</div>
      </main>
    );
  }
  return <Step key={stepId} />;
}
