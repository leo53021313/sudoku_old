import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch9Step1 from './Ch9Step1.jsx';
import Ch9Step2 from './Ch9Step2.jsx';
import Ch9Step3 from './Ch9Step3.jsx';
import Ch9Step4 from './Ch9Step4.jsx';

const STEPS = {
  1: Ch9Step1,
  2: Ch9Step2,
  3: Ch9Step3,
  4: Ch9Step4,
};

export function Ch9() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 9 · step {stepId}</div></main>;
  return <Step key={stepId} />;
}
