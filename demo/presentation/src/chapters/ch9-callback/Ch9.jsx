import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch9Step1 from './Ch9Step1.jsx';
import Ch9Step2 from './Ch9Step2.jsx';
import Ch9Step3 from './Ch9Step3.jsx';
import Ch9Step4 from './Ch9Step4.jsx';
import Ch9Step5 from './Ch9Step5.jsx';
import Ch9Step6 from './Ch9Step6.jsx';
import Ch9Step7 from './Ch9Step7.jsx';
import Ch9Step8 from './Ch9Step8.jsx';
import Ch9Step9 from './Ch9Step9.jsx';
import Ch9Step10 from './Ch9Step10.jsx';

const STEPS = {
  1: Ch9Step1,
  2: Ch9Step2,
  3: Ch9Step3,
  4: Ch9Step4,
  5: Ch9Step5,
  6: Ch9Step6,
  7: Ch9Step7,
  8: Ch9Step8,
  9: Ch9Step9,
  10: Ch9Step10,
};

export function Ch9() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 9 · step {stepId}</div></main>;
  return <Step key={stepId} />;
}
