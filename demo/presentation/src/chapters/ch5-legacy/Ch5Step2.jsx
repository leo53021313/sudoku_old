import { useEffect, useState } from 'react';
import { motion } from 'motion/react';

const CODE_SNIPPET = `
class SudokuPPONet(nn.Module):
    def __init__(self, board_size=9, action_dim=729):
        super().__init__()
        self.board_size = board_size
        self.action_dim = action_dim
        self.encoder = nn.Sequential(...)
        self.policy_head = nn.Linear(...)
        self.value_head = nn.Linear(...)

    def forward(self, obs):
        ...

class RolloutBuffer:
    def __init__(self, n_steps=512):
        ...

def compute_gae(rewards, values, ...):
    ...

class TeacherEngine:
    def __init__(self, level=5):
        ...

    def naked_single(self, board):
        ...

    def hidden_single(self, board):
        ...

# 800+ more lines below
# everything stuffed into one file
`.trim();

export default function Ch5Step2() {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let raf, start;
    const animate = (t) => {
      if (!start) start = t;
      const elapsed = t - start;
      const pct = Math.min(elapsed / 600, 1);
      setCount(Math.floor(pct * 838));
      if (pct < 1) raf = requestAnimationFrame(animate);
    };
    raf = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(raf);
  }, []);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Code wall slide up from below */}
      <motion.pre
        initial={{ y: 600, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        style={{
          width: '70%', maxHeight: '70vh', overflow: 'hidden',
          background: '#FFFDF5', color: '#222',
          border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          padding: 24, fontFamily: 'monospace', fontSize: 13, lineHeight: 1.5,
          marginTop: 80,
        }}
      >
        {CODE_SNIPPET}
      </motion.pre>

      {/* Top-right count-up badge */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', top: 32, right: 32,
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '12px 24px', border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
          fontFamily: 'monospace', fontWeight: 900, fontSize: 24, rotate: 3,
        }}
      >
        torch_agent.py · {count} lines
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0 }}
        style={{
          marginTop: 16, fontWeight: 700, fontSize: '1.5rem', color: '#000',
        }}
      >
        什麼都塞在裡面
      </motion.div>
    </main>
  );
}
