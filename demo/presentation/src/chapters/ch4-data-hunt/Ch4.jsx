import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch4Step1 from './Ch4Step1.jsx';
import Ch4Step2 from './Ch4Step2.jsx';
import Ch4Step3 from './Ch4Step3.jsx';

const STEPS = { 1: Ch4Step1, 2: Ch4Step2, 3: Ch4Step3 };

export function Ch4() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 4 · step {stepId}</div></main>;
  return <Step key={stepId} />;
}
