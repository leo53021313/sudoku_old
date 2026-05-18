import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { AiBackdrop } from '../../components/AiBackdrop.jsx';
import Ch1Step1 from './Ch1Step1.jsx';
import Ch1Step2 from './Ch1Step2.jsx';
import Ch1Step3 from './Ch1Step3.jsx';
import Ch1Step4 from './Ch1Step4.jsx';
import Ch1Step5 from './Ch1Step5.jsx';
import Ch1Step6 from './Ch1Step6.jsx';
import Ch1Step7 from './Ch1Step7.jsx';
import Ch1Step8 from './Ch1Step8.jsx';

const STEPS = {
  1: Ch1Step1,
  2: Ch1Step2,
  3: Ch1Step3,
  4: Ch1Step4,
  5: Ch1Step5,
  6: Ch1Step6,
  7: Ch1Step7,
  8: Ch1Step8,
};

export function Ch1() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  const showMrtBackdrop = stepId >= 4 && stepId <= 7;
  return (
    <>
      {showMrtBackdrop && (
        <AiBackdrop src="/images/ai/ch1/mrt-window.png" alt="台北捷運車廂內視" />
      )}
      {Step ? (
        <Step key={stepId} />
      ) : (
        <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk' }}>
          <div style={{ fontSize: 24, fontWeight: 900 }}>ch 1 · step {stepId}</div>
          <div style={{ marginTop: 16, color: '#666' }}>(component not yet implemented)</div>
        </main>
      )}
    </>
  );
}
