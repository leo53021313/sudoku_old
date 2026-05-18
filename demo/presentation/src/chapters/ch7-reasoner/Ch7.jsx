import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch7Step1 from './Ch7Step1.jsx';
import Ch7Step2 from './Ch7Step2.jsx';
import Ch7Step3 from './Ch7Step3.jsx';
import Ch7Step4 from './Ch7Step4.jsx';
import Ch7Step5 from './Ch7Step5.jsx';

const STEPS = { 1: Ch7Step1, 2: Ch7Step2, 3: Ch7Step3, 4: Ch7Step4, 5: Ch7Step5 };

export function Ch7() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 7 · step {stepId}</div></main>;
  return <Step key={stepId} />;
}
