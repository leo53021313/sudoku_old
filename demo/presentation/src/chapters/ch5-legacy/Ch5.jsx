import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch5Step1 from './Ch5Step1.jsx';

const STEPS = { 1: Ch5Step1 };

export function Ch5() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 5 · step {stepId}</div></main>;
  return <Step key={stepId} />;
}
