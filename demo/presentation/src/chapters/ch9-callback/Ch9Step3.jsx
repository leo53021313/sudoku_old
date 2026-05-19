import { motion } from 'motion/react';
import { NeuralNet } from '../../motifs/NeuralNet.jsx';

export default function Ch9Step3() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      fontFamily: 'Space Grotesk', display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      {/* Left: brain (RL 腦科學) — cream card now, AI brain illustration */}
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)' }}
        animate={{ clipPath: 'inset(0 0 0 0)' }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        style={{
          flex: '0 0 40%', background: '#FFFDF5', color: '#000',
          height: '60vh',
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          padding: 32, gap: 16,
          border: '6px solid #000',
        }}
      >
        <img
          src="/images/ai/ch9/brain-reward.png"
          alt="大腦與獎懲 token"
          style={{ width: '70%', height: 'auto', display: 'block' }}
        />
        <div style={{
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '8px 20px',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          fontWeight: 900, fontSize: '2rem',
        }}>腦科學 RL</div>
      </motion.div>

      {/* Center: "=" yellow circle stamp (preserved) */}
      <motion.div
        initial={{ scale: 0, rotate: 0 }}
        animate={{ scale: 1, rotate: -10 }}
        transition={{ duration: 0.5, delay: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FFD93D', color: '#000',
          width: 120, height: 120, borderRadius: '50%',
          border: '8px solid #000', boxShadow: '12px 12px 0 0 #000',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontWeight: 900, fontSize: 64, margin: '0 -40px', zIndex: 5,
        }}
      >
        =
      </motion.div>

      {/* Right: neural net (AI 訓練) — AI neural network illustration */}
      <motion.div
        initial={{ clipPath: 'inset(0 0 0 100%)' }}
        animate={{ clipPath: 'inset(0 0 0 0)' }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        style={{
          flex: '0 0 40%', background: '#FFFDF5', color: '#000',
          height: '60vh',
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          padding: 32, gap: 16,
          border: '6px solid #000',
        }}
      >
        <div style={{ width: '70%', height: 260, display: 'block' }}>
          <NeuralNet active />
        </div>
        <div style={{
          background: '#000', color: '#FFFDF5',
          padding: '8px 20px',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          fontWeight: 900, fontSize: '2rem',
        }}>AI 訓練 RL</div>
      </motion.div>

      {/* Hero below (preserved) */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0 }}
        style={{
          position: 'absolute', bottom: 80, left: 0, right: 0, textAlign: 'center',
          fontWeight: 900, fontSize: '2.5rem',
        }}
      >
        其實是 <span style={{ background: '#FFD93D', padding: '4px 16px', border: '4px solid #000' }}>同一件事</span>
      </motion.div>
    </main>
  );
}
