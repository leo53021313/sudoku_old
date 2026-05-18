import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch5Step1 from './Ch5Step1.jsx';
import Ch5Step2 from './Ch5Step2.jsx';
import Ch5Step3 from './Ch5Step3.jsx';
import Ch5Step4 from './Ch5Step4.jsx';

const STEPS = { 1: Ch5Step1, 2: Ch5Step2, 3: Ch5Step3, 4: Ch5Step4 };

export function Ch5() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 5 · step {stepId}</div></main>;
  return <Step key={stepId} />;
}
