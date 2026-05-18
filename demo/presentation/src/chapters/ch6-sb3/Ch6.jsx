import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch6Step1 from './Ch6Step1.jsx';
import Ch6Step2 from './Ch6Step2.jsx';
import Ch6Step3 from './Ch6Step3.jsx';
import Ch6Step4 from './Ch6Step4.jsx';
import Ch6Step5 from './Ch6Step5.jsx';
import Ch6Step6 from './Ch6Step6.jsx';

const STEPS = { 1: Ch6Step1, 2: Ch6Step2, 3: Ch6Step3, 4: Ch6Step4, 5: Ch6Step5, 6: Ch6Step6 };

export function Ch6() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 6 · step {stepId}</div></main>;
  return <Step key={stepId} />;
}
