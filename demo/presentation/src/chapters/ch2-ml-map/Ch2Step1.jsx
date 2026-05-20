import { motion } from 'motion/react';

// ch2 s1 — 機器學習三大分支總覽（樹狀分支圖）
// 對應腳本 L43-49 的 lead-in：「先帶大家看機器學習的世界長什麼樣 / 主要分三塊」。
// 單 beat：根節點落下 → 三條 SVG 連線 draw-on → 三張卡 stagger 進場，RL 進場即黃色高亮。

// 三張卡在 960 寬容器內等寬排列（300 寬 + 30 gap），卡中心 x = 150 / 480 / 810。
// SVG 從根節點底部 (480,0) 連到三卡頂端 (cx,120)，座標與卡片中心對齊。
const BRANCHES = [
  { id: 'supervised', label: 'supervised', cx: 150, highlight: false },
  { id: 'unsupervised', label: 'unsupervised', cx: 480, highlight: false },
  { id: 'rl', label: 'Reinforcement learning', cx: 810, highlight: true },
];

export default function Ch2Step1() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Kicker top */}
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{
          background: '#000', color: '#FFFDF5',
          padding: '12px 28px',
          fontWeight: 900, fontSize: 18, letterSpacing: '0.1em',
          marginBottom: 56,
        }}
      >
        機器學習 · 三大分支
      </motion.div>

      {/* Tree container — fixed 960 width so SVG coords match card centers */}
      <div style={{ position: 'relative', width: 960 }}>
        {/* Root node */}
        <motion.div
          initial={{ y: -30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.45, ease: 'easeOut' }}
          style={{
            width: 'fit-content', margin: '0 auto',
            background: '#FFFDF5', color: '#000',
            border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
            padding: '20px 48px', textAlign: 'center',
          }}
        >
          <div style={{ fontWeight: 900, fontSize: '3rem', lineHeight: 1 }}>機器學習</div>
          <div style={{ fontWeight: 700, fontSize: '1.1rem', opacity: 0.75, marginTop: 6, letterSpacing: '0.04em' }}>
            Machine Learning
          </div>
        </motion.div>

        {/* Connector lines */}
        <svg
          viewBox="0 0 960 120" width="960" height="120"
          style={{ display: 'block', overflow: 'visible' }}
        >
          {BRANCHES.map((b, i) => (
            <motion.path
              key={b.id}
              d={`M480 0 C 480 60, ${b.cx} 60, ${b.cx} 120`}
              fill="none" stroke="#000" strokeWidth={4} strokeLinecap="round"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.45 + i * 0.08, ease: 'easeInOut' }}
            />
          ))}
        </svg>

        {/* Three branch cards */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'stretch' }}>
          {BRANCHES.map((b, i) => (
            <motion.div
              key={b.id}
              initial={{ y: 30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.45, delay: 0.85 + i * 0.15, ease: 'easeOut' }}
              style={{
                width: 300, minHeight: 120,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                textAlign: 'center', padding: '20px 16px',
                background: b.highlight ? '#FFD93D' : '#FFFDF5',
                border: '4px solid #000',
                boxShadow: b.highlight ? '10px 10px 0 0 #000' : '8px 8px 0 0 #000',
                fontWeight: 900, fontSize: b.highlight ? '1.7rem' : '2rem',
                lineHeight: 1.1, color: '#000',
              }}
            >
              {b.label}
            </motion.div>
          ))}
        </div>
      </div>
    </main>
  );
}
