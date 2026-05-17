import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch3Step1 from './Ch3Step1.jsx';
import Ch3Step2 from './Ch3Step2.jsx';

const STEPS = { 1: Ch3Step1, 2: Ch3Step2 };

export function Ch3() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) {
    return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 3 · step {stepId}</div></main>;
  }
  return <Step key={stepId} />;
}
