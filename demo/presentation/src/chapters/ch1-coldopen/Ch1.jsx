import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch1Step1 from './Ch1Step1.jsx';
import Ch1Step2 from './Ch1Step2.jsx';
import Ch1Step3 from './Ch1Step3.jsx';
import Ch1Step4 from './Ch1Step4.jsx';

const STEPS = {
  1: Ch1Step1,
  2: Ch1Step2,
  3: Ch1Step3,
  4: Ch1Step4,
};

export function Ch1() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) {
    return (
      <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk' }}>
        <div style={{ fontSize: 24, fontWeight: 900 }}>ch 1 · step {stepId}</div>
        <div style={{ marginTop: 16, color: '#666' }}>(component not yet implemented)</div>
      </main>
    );
  }
  return <Step key={stepId} />;
}
