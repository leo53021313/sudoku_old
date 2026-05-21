import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { YellowHighlight } from '../../motifs/YellowHighlight.jsx';

const KEYWORDS = ['架構', '演算法', '自己', '分工'];

export default function Ch5Step4() {
  const [activeKw, setActiveKw] = useState(-1);
  const [aftermath, setAftermath] = useState(false);

  // Stagger keyword reveal every 250ms after initial mask
  useEffect(() => {
    KEYWORDS.forEach((_, i) => {
      setTimeout(() => setActiveKw(i), 1200 + i * 250);
    });
    // Aftermath fires 700ms after the LAST keyword highlight lands
    const lastAt = 1200 + (KEYWORDS.length - 1) * 250;
    const t = setTimeout(() => setAftermath(true), lastAt + 700);
    return () => clearTimeout(t);
  }, []);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 24,
    }}>
      {/* Hero — mask-reveal */}
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 1.2, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '3rem', textAlign: 'center', lineHeight: 1.9,
          maxWidth: 1200,
        }}
      >
        <KeywordSpan idx={0} active={activeKw >= 0} pulse={aftermath} text="架構" />、
        <KeywordSpan idx={1} active={activeKw >= 1} pulse={aftermath} text="演算法" />都得
        <KeywordSpan idx={2} active={activeKw >= 2} pulse={aftermath} text="自己" />先想清楚
        <br />
        再請 AI 來
        <KeywordSpan idx={3} active={activeKw >= 3} pulse={aftermath} text="分工" />
      </motion.div>

      {/* Footer transition hint */}
      <motion.div
        initial={{ y: 40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 2.4 }}
        style={{
          position: 'absolute', bottom: 64,
          fontWeight: 700, fontSize: '1.25rem', color: '#666',
        }}
      >
        轉而當個套皮仔 →
      </motion.div>
    </main>
  );
}

function KeywordSpan({ idx, active, pulse, text }) {
  return (
    <motion.span
      animate={pulse ? { scale: [1, 1.05, 1] } : { scale: 1 }}
      transition={pulse
        ? { duration: 0.2, delay: idx * 0.08, ease: 'easeOut' }
        : { duration: 0 }}
      style={{ position: 'relative', display: 'inline-block' }}
    >
      <YellowHighlight active={active} padding="2px 12px" style={{ lineHeight: 1.1 }}>{text}</YellowHighlight>
    </motion.span>
  );
}
