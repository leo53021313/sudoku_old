// Per-chapter signature transitions — dispatches by entering chapterId.
// Chapters without a custom gesture fall back to the original cream cross-fade.
import { useEffect, useState } from 'react';
import { motion } from 'motion/react';

const BIG_TRANSITIONS = new Set(['1-2', '4-5', '8-9']);

export function FadeBridge({ chapterId }) {
  const [active, setActive] = useState(false);
  const [prevChapter, setPrevChapter] = useState(null);  // null on first mount → initial entry triggers transition
  const [animKey, setAnimKey] = useState(0);

  useEffect(() => {
    if (chapterId !== prevChapter) {
      const key = `${prevChapter}-${chapterId}`;
      const duration = BIG_TRANSITIONS.has(key) ? 1500 : 1000;
      setActive(true);
      setAnimKey(k => k + 1);
      const t = setTimeout(() => {
        setActive(false);
        setPrevChapter(chapterId);
      }, duration);
      return () => clearTimeout(t);
    }
  }, [chapterId, prevChapter]);

  if (!active) return null;
  const transitionKey = `${prevChapter}-${chapterId}`;
  const duration = BIG_TRANSITIONS.has(transitionKey) ? 1500 : 1000;
  return <ChapterEntryGesture key={animKey} chapterId={chapterId} duration={duration} />;
}

function ChapterEntryGesture({ chapterId, duration }) {
  switch (chapterId) {
    case 1: return <Ch1PaperUnfold duration={duration} />;
    case 2: return <Ch2GridDrawIn duration={duration} />;
    case 3: return <Ch3SplitScreen duration={duration} />;
    case 4: return <Ch4TierSnap duration={duration} />;
    case 5: return <Ch5FaultLineShear duration={duration} />;
    case 6: return <Ch6PinkRedSweep duration={duration} />;
    case 7: return <Ch7LatticeLock duration={duration} />;
    case 8: return <Ch8BoardMaterialize duration={duration} />;
    case 9: return <Ch9GhostCollage duration={duration} />;
    default: return <DefaultCreamFade duration={duration} />;
  }
}

// ch1 · cream 紙從中間 unfold —— 兩半 cream 滑入合攏 (300ms) → hold (200ms) → 對開展開 (500ms)
function Ch1PaperUnfold({ duration }) {
  const d = duration / 1000;
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none' }}>
      <motion.div
        initial={{ y: '-100%' }}
        animate={{ y: ['-100%', '0%', '0%', '-100%'] }}
        transition={{
          duration: d,
          times: [0, 0.3, 0.5, 1],
          ease: ['easeIn', 'linear', [0.65, 0, 0.35, 1]],
        }}
        style={{
          position: 'absolute', top: 0, left: 0, right: 0, height: '50%',
          background: '#FFFDF5',
          borderBottom: '4px solid #000',
        }}
      />
      <motion.div
        initial={{ y: '100%' }}
        animate={{ y: ['100%', '0%', '0%', '100%'] }}
        transition={{
          duration: d,
          times: [0, 0.3, 0.5, 1],
          ease: ['easeIn', 'linear', [0.65, 0, 0.35, 1]],
        }}
        style={{
          position: 'absolute', bottom: 0, left: 0, right: 0, height: '50%',
          background: '#FFFDF5',
          borderTop: '4px solid #000',
        }}
      />
    </div>
  );
}

// ch2 · graph-paper 格線從邊角繪入 —— SVG 的橫豎 line 用 pathLength 真正一筆一筆畫
function Ch2GridDrawIn({ duration }) {
  const d = duration / 1000;
  const grid = 40;
  const cols = 50;   // 2000 / 40
  const rows = 30;   // 1200 / 40
  const drawDelay = d * 0.2;
  const drawDur = d * 0.45;
  const colStagger = d * 0.004;
  const rowStagger = d * 0.006;

  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none' }}>
      <motion.div
        animate={{ opacity: [0, 1, 1, 0] }}
        transition={{ duration: d, times: [0, 0.15, 0.75, 1] }}
        style={{ position: 'absolute', inset: 0, background: '#FFFDF5' }}
      />
      <motion.svg
        animate={{ opacity: [0, 0, 1, 1, 0] }}
        transition={{ duration: d, times: [0, 0.15, 0.35, 0.75, 1] }}
        viewBox="0 0 2000 1200"
        preserveAspectRatio="xMidYMid slice"
        style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}
      >
        {Array.from({ length: cols }).map((_, i) => (
          <motion.line
            key={`v-${i}`}
            x1={i * grid} y1={0} x2={i * grid} y2={1200}
            stroke="#000" strokeWidth={1.5} strokeOpacity={0.35}
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: drawDur, delay: drawDelay + i * colStagger, ease: 'easeOut' }}
          />
        ))}
        {Array.from({ length: rows }).map((_, i) => (
          <motion.line
            key={`h-${i}`}
            x1={0} y1={i * grid} x2={2000} y2={i * grid}
            stroke="#000" strokeWidth={1.5} strokeOpacity={0.35}
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: drawDur, delay: drawDelay + i * rowStagger, ease: 'easeOut' }}
          />
        ))}
      </motion.svg>
    </div>
  );
}

// ch3 · split-screen 從中間切開 —— 雙半合攏 → 黑線劈下 → 紅 flash → 用 easeIn 彈開
function Ch3SplitScreen({ duration }) {
  const d = duration / 1000;
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none' }}>
      <motion.div
        initial={{ x: '-100%' }}
        animate={{ x: ['-100%', '0%', '0%', '-100%'] }}
        transition={{
          duration: d,
          times: [0, 0.15, 0.5, 1],
          ease: ['easeOut', 'linear', [0.7, 0, 0.84, 0]],
        }}
        style={{
          position: 'absolute', top: 0, left: 0, bottom: 0, width: '50%',
          background: '#FFFDF5',
        }}
      />
      <motion.div
        initial={{ x: '100%' }}
        animate={{ x: ['100%', '0%', '0%', '100%'] }}
        transition={{
          duration: d,
          times: [0, 0.15, 0.5, 1],
          ease: ['easeOut', 'linear', [0.7, 0, 0.84, 0]],
        }}
        style={{
          position: 'absolute', top: 0, right: 0, bottom: 0, width: '50%',
          background: '#FFFDF5',
        }}
      />
      {/* 黑色垂直「劈下」線 — scaleY 0→1 from top, holds, fades */}
      <motion.div
        initial={{ scaleY: 0, opacity: 1 }}
        animate={{ scaleY: [0, 0, 1, 1, 1], opacity: [1, 1, 1, 1, 0] }}
        transition={{
          duration: d,
          times: [0, 0.18, 0.35, 0.85, 1],
          ease: ['linear', 'easeIn', 'linear', 'easeOut'],
        }}
        style={{
          position: 'absolute', top: 0, left: '50%', bottom: 0,
          width: 6, marginLeft: -3, background: '#000',
          transformOrigin: 'top',
        }}
      />
      {/* 紅 flash —— 劈完瞬間在切口上閃一下 */}
      <motion.div
        animate={{ opacity: [0, 0, 0.75, 0, 0] }}
        transition={{
          duration: d,
          times: [0, 0.32, 0.36, 0.46, 1],
          ease: 'linear',
        }}
        style={{
          position: 'absolute', top: 0, left: '50%', bottom: 0,
          width: 24, marginLeft: -12, background: '#FF6B6B',
        }}
      />
    </div>
  );
}

// ch4 · tier-list 硬橫條 snap —— 3 黑橫條 + 1 黃 accent 從左滑入、hold、easeIn 彈出右側
function Ch4TierSnap({ duration }) {
  const d = duration / 1000;
  const bars = [
    { top: '25%', inAt: 0.20, outAt: 0.85 },
    { top: '50%', inAt: 0.25, outAt: 0.87 },
    { top: '75%', inAt: 0.30, outAt: 0.89 },
  ];
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none' }}>
      <motion.div
        animate={{ opacity: [0, 1, 1, 0] }}
        transition={{ duration: d, times: [0, 0.15, 0.85, 1], ease: 'linear' }}
        style={{ position: 'absolute', inset: 0, background: '#FFFDF5' }}
      />
      {bars.map((bar, i) => (
        <motion.div
          key={i}
          initial={{ x: '-100vw' }}
          animate={{ x: ['-100vw', '0vw', '0vw', '100vw'] }}
          transition={{
            duration: d,
            times: [0, bar.inAt, 0.6, bar.outAt],
            ease: ['easeOut', 'linear', 'easeIn'],
          }}
          style={{
            position: 'absolute', top: bar.top, left: 0, right: 0, height: 8,
            background: '#000',
          }}
        />
      ))}
      {/* 黃色 Kaggle accent — 比黑條晚進、跟黑條同時離 */}
      <motion.div
        initial={{ x: '-100vw' }}
        animate={{ x: ['-100vw', '0vw', '0vw', '100vw'] }}
        transition={{
          duration: d,
          times: [0, 0.45, 0.6, 0.9],
          ease: ['easeOut', 'linear', 'easeIn'],
        }}
        style={{
          position: 'absolute', top: '62%', left: 0, width: '35%', height: 16,
          background: '#FFD93D',
        }}
      />
    </div>
  );
}

// ch5 · 斷層撕裂 —— cream 沿反對角剪兩半、鋸齒黑裂縫 pathLength 描入 + 紅光、兩半 shear 滑出
function Ch5FaultLineShear({ duration }) {
  const d = duration / 1000;
  const crack = 'M2000,0 L1500,360 L1180,200 L760,560 L420,360 L0,1200';
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none' }}>
      {/* 左上三角 cream，hold 後往左上 shear 出 */}
      <motion.div
        animate={{ x: ['0%', '0%', '0%', '-60%'], y: ['0%', '0%', '0%', '-60%'], opacity: [0, 1, 1, 0] }}
        transition={{ duration: d, times: [0, 0.12, 0.62, 1], ease: ['easeOut', 'linear', [0.7, 0, 0.84, 0]] }}
        style={{ position: 'absolute', inset: 0, background: '#FFFDF5', clipPath: 'polygon(0 0, 100% 0, 0 100%)' }}
      />
      {/* 右下三角 cream，往右下 shear 出 */}
      <motion.div
        animate={{ x: ['0%', '0%', '0%', '60%'], y: ['0%', '0%', '0%', '60%'], opacity: [0, 1, 1, 0] }}
        transition={{ duration: d, times: [0, 0.12, 0.62, 1], ease: ['easeOut', 'linear', [0.7, 0, 0.84, 0]] }}
        style={{ position: 'absolute', inset: 0, background: '#FFFDF5', clipPath: 'polygon(100% 0, 100% 100%, 0 100%)' }}
      />
      <svg viewBox="0 0 2000 1200" preserveAspectRatio="none" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}>
        {/* 鋸齒黑裂縫 —— pathLength 0→1 描入 */}
        <motion.path
          d={crack} fill="none" stroke="#000" strokeWidth={10}
          initial={{ pathLength: 0 }}
          animate={{ pathLength: [0, 1, 1, 1], opacity: [1, 1, 1, 0] }}
          transition={{ duration: d, times: [0, 0.42, 0.62, 1], ease: ['easeIn', 'linear', 'easeOut'] }}
        />
        {/* 紅光 flash 沿裂縫 */}
        <motion.path
          d={crack} fill="none" stroke="#FF6B6B" strokeWidth={22}
          animate={{ opacity: [0, 0, 0.85, 0, 0] }}
          transition={{ duration: d, times: [0, 0.42, 0.5, 0.62, 1], ease: 'linear' }}
        />
      </svg>
    </div>
  );
}

// ch6 · 粉轉紅 —— 粉紅面溫柔掃入 hold、紅 streak 橫掃（崩盤）、粉面滑出
function Ch6PinkRedSweep({ duration }) {
  const d = duration / 1000;
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none' }}>
      {/* 粉紅面：左→右掃入、hold、再往右掃出 */}
      <motion.div
        initial={{ x: '-100%' }}
        animate={{ x: ['-100%', '0%', '0%', '0%', '100%'] }}
        transition={{ duration: d, times: [0, 0.38, 0.5, 0.7, 1], ease: ['easeOut', 'linear', 'linear', [0.7, 0, 0.84, 0]] }}
        style={{ position: 'absolute', inset: 0, background: '#FFB6C1', borderRight: '6px solid #000' }}
      />
      {/* 紅 streak：橫向快速掃過粉面 */}
      <motion.div
        initial={{ x: '-120%' }}
        animate={{ x: ['-120%', '-120%', '120%'] }}
        transition={{ duration: d, times: [0, 0.5, 0.72], ease: ['linear', 'easeIn'] }}
        style={{ position: 'absolute', top: 0, bottom: 0, left: 0, width: '45%', background: '#FF6B6B', boxShadow: '12px 0 0 0 #000' }}
      />
    </div>
  );
}

// ch7 · 約束格鎖死 —— 3×3 sudoku 粗框 pathLength 描入 + scale snap 咬合、中央格閃紅轉黃
function Ch7LatticeLock({ duration }) {
  const d = duration / 1000;
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none' }}>
      <motion.div
        animate={{ opacity: [0, 1, 1, 0] }}
        transition={{ duration: d, times: [0, 0.15, 0.82, 1], ease: 'linear' }}
        style={{ position: 'absolute', inset: 0, background: '#FFFDF5' }}
      />
      <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}>
        <motion.svg
          viewBox="0 0 90 90"
          style={{ width: '62vh', height: '62vh', overflow: 'visible' }}
          animate={{ scale: [0.92, 0.92, 1.04, 1, 1], opacity: [0, 1, 1, 1, 0] }}
          transition={{ duration: d, times: [0, 0.2, 0.6, 0.82, 1], ease: ['linear', 'easeOut', 'easeOut', 'easeOut'] }}
        >
          {/* 外框 */}
          <motion.rect
            x="0" y="0" width="90" height="90" fill="none" stroke="#000" strokeWidth={3}
            initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
            transition={{ duration: d * 0.4, delay: d * 0.18, ease: 'easeOut' }}
          />
          {/* 直粗線 */}
          {[30, 60].map((x) => (
            <motion.line
              key={`v-${x}`} x1={x} y1={0} x2={x} y2={90} stroke="#000" strokeWidth={3}
              initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
              transition={{ duration: d * 0.35, delay: d * 0.25, ease: 'easeOut' }}
            />
          ))}
          {/* 橫粗線 */}
          {[30, 60].map((y) => (
            <motion.line
              key={`h-${y}`} x1={0} y1={y} x2={90} y2={y} stroke="#000" strokeWidth={3}
              initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
              transition={{ duration: d * 0.35, delay: d * 0.25, ease: 'easeOut' }}
            />
          ))}
          {/* 中央格閃紅轉黃 */}
          <motion.rect
            x="40" y="40" width="10" height="10" stroke="#000" strokeWidth={1.5}
            animate={{ fill: ['#FF6B6B', '#FF6B6B', '#FFD93D', '#FFD93D'], opacity: [0, 0, 1, 1] }}
            transition={{ duration: d, times: [0, 0.6, 0.66, 1], ease: 'linear' }}
          />
        </motion.svg>
      </div>
    </div>
  );
}

// ch8 · 9×9 sudoku 盤面從左上角 stagger 翻入 —— sudoku-board motif + 3 格黃色 (反向課程起點)
const CH8_YELLOW_CELLS = new Set([20, 44, 66]);  // 3 黃格代表「3 格空」反向課程起點
function Ch8BoardMaterialize({ duration }) {
  const d = duration / 1000;
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none' }}>
      <motion.div
        animate={{ opacity: [0, 1, 1, 0] }}
        transition={{ duration: d, times: [0, 0.15, 0.85, 1], ease: 'linear' }}
        style={{ position: 'absolute', inset: 0, background: '#FFFDF5' }}
      />
      <div style={{
        position: 'absolute', top: '50%', left: '50%',
        transform: 'translate(-50%, -50%)',
      }}>
      <motion.div
        animate={{
          scale: [0, 0, 1, 1, 1, 0.95, 0],
          opacity: [0, 0, 1, 1, 1, 1, 0],
          rotate: [-2, -2, -2, -2, -2, -2, -2],
        }}
        transition={{
          duration: d,
          times: [0, 0.15, 0.5, 0.55, 0.80, 0.93, 1],
          ease: ['linear', 'easeOut', 'linear', 'linear', 'easeIn', 'easeOut'],
        }}
        style={{
          width: '60vh', height: '60vh',
          display: 'grid',
          gridTemplateColumns: 'repeat(9, 1fr)',
          gridTemplateRows: 'repeat(9, 1fr)',
          background: '#FFFDF5',
          border: '6px solid #000',
          boxShadow: '12px 12px 0 0 #000',
          boxSizing: 'border-box',
        }}
      >
        {Array.from({ length: 81 }).map((_, i) => {
          const row = Math.floor(i / 9);
          const col = i % 9;
          const cellDelay = (row + col) * 0.008;
          const isYellow = CH8_YELLOW_CELLS.has(i);
          return (
            <motion.div
              key={i}
              animate={{
                scale: [0, 0, 1.15, 1, 1, 1, 1],
                opacity: [0, 0, 1, 1, 1, 1, 1],
              }}
              transition={{
                duration: d,
                times: [0, 0.15 + cellDelay, 0.20 + cellDelay, 0.24 + cellDelay, 0.5, 0.8, 1],
                ease: ['linear', [0.34, 1.56, 0.64, 1], 'easeOut', 'linear', 'linear', 'linear'],
              }}
              style={{
                background: isYellow ? '#FFD93D' : '#FFFDF5',
                borderRight: col % 3 === 2 && col !== 8 ? '2px solid #000' : '1px solid rgba(0,0,0,0.4)',
                borderBottom: row % 3 === 2 && row !== 8 ? '2px solid #000' : '1px solid rgba(0,0,0,0.4)',
                boxSizing: 'border-box',
              }}
            />
          );
        })}
      </motion.div>
      </div>
    </div>
  );
}

// ch9 · ghost-collage —— 前 8 章 iconic sticker 灰階 ghost、stagger flicker 回原色、退回灰階、淡出
function Ch9GhostCollage({ duration }) {
  const d = duration / 1000;
  const memories = [
    { ch: 1, x: '15%', y: '22%', rot: -2, bg: '#FFD93D', text: 'AI',    fontSize: '2rem',    padding: '12px 26px', flashAt: 0.30 },
    { ch: 2, x: '40%', y: '15%', rot: 3,  bg: '#FF6B6B', text: 'RL',    fontSize: '2rem',    padding: '12px 26px', flashAt: 0.34, lightText: true },
    { ch: 3, x: '68%', y: '24%', rot: -3, bg: '#FFFDF5', text: 'VS',    fontSize: '2.25rem', padding: '10px 24px', flashAt: 0.38 },
    { ch: 4, x: '85%', y: '48%', rot: 2,  bg: '#FF6B6B', text: '受害者', fontSize: '1.5rem',  padding: '10px 18px', flashAt: 0.42, lightText: true },
    { ch: 5, x: '76%', y: '72%', rot: -2, bg: '#FFFDF5', text: '錯',    fontSize: '2.5rem',  padding: '8px 22px',  flashAt: 0.46, redBorder: true },
    { ch: 6, x: '50%', y: '80%', rot: 3,  bg: '#FFB6C1', text: '+1',    fontSize: '2rem',    padding: '12px 26px', flashAt: 0.50 },
    { ch: 7, x: '22%', y: '72%', rot: -3, bg: '#FFD93D', text: '0',     fontSize: '2.5rem',  padding: '8px 28px',  flashAt: 0.54 },
    { ch: 8, x: '12%', y: '50%', rot: 2,  bg: '#FFD93D', text: '+50',   fontSize: '1.75rem', padding: '12px 22px', flashAt: 0.58 },
  ];
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none' }}>
      <motion.div
        animate={{ opacity: [0, 1, 1, 0] }}
        transition={{ duration: d, times: [0, 0.15, 0.85, 1], ease: 'linear' }}
        style={{ position: 'absolute', inset: 0, background: '#FFFDF5' }}
      />
      {memories.map((m) => (
        <div
          key={m.ch}
          style={{
            position: 'absolute',
            left: m.x, top: m.y,
            transform: 'translate(-50%, -50%)',
          }}
        >
          <motion.div
            animate={{
              opacity: [0, 0.35, 1, 1, 0.35, 0.35, 0],
              filter: ['grayscale(1)', 'grayscale(1)', 'grayscale(0)', 'grayscale(0)', 'grayscale(1)', 'grayscale(1)', 'grayscale(1)'],
              scale:  [0.9, 1, 1.08, 1, 1, 1, 0.9],
              rotate: [m.rot, m.rot, m.rot, m.rot, m.rot, m.rot, m.rot],
            }}
            transition={{
              duration: d,
              times: [0, Math.max(0.01, m.flashAt - 0.10), m.flashAt - 0.02, m.flashAt + 0.04, m.flashAt + 0.12, 0.80, 1],
              ease: 'linear',
            }}
            style={{
              background: m.bg,
              color: m.lightText ? '#FFFDF5' : '#000',
              border: m.redBorder ? '4px solid #FF6B6B' : '4px solid #000',
              boxShadow: '6px 6px 0 0 #000',
              padding: m.padding,
              fontFamily: 'Space Grotesk', fontWeight: 900, fontSize: m.fontSize,
              lineHeight: 1, textAlign: 'center', minWidth: 70,
            }}
          >
            {m.text}
          </motion.div>
        </div>
      ))}
    </div>
  );
}

// Default — existing cream cross-fade for chapters without a custom entry gesture.
function DefaultCreamFade({ duration }) {
  return (
    <div
      aria-hidden="true"
      style={{
        position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none',
        background: '#FFFDF5',
        animation: `fade-bridge ${duration}ms ease-out forwards`,
      }}
    />
  );
}
