import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch8Step1 from './Ch8Step1.jsx';
import Ch8Step2 from './Ch8Step2.jsx';
import Ch8Step3 from './Ch8Step3.jsx';
import Ch8Step4 from './Ch8Step4.jsx';

const STEPS = { 1: Ch8Step1, 2: Ch8Step2, 3: Ch8Step3, 4: Ch8Step4 };

export function Ch8() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 8 · step {stepId}</div></main>;
  return <Step key={stepId} />;
}
