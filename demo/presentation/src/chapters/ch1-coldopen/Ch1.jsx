import { usePresentationContext } from '../../state/PresentationContext.jsx';

// Step component lookup — each step file exports default component.
// Placeholder mapping; real Ch1StepN files added in later tasks.
const STEPS = {
  // Filled in by later tasks
};

export function Ch1() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) {
    return (
      <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk' }}>
        <div style={{ fontSize: 24, fontWeight: 900 }}>ch 1 · step {stepId}</div>
        <div style={{ marginTop: 16, color: '#666' }}>(component not yet implemented)</div>
      </main>
    );
  }
  return <Step key={stepId} />;
}
