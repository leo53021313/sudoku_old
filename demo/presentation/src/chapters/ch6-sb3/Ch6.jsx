import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch6Step1 from './Ch6Step1.jsx';

const STEPS = { 1: Ch6Step1 };

export function Ch6() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 6 · step {stepId}</div></main>;
  return <Step key={stepId} />;
}
