import { motion } from 'motion/react';
import { useEffect, useState } from 'react';
import ScanlineOverlay from './ScanlineOverlay.jsx';
import InhaleLayer from './InhaleLayer.jsx';

const TERMS = [
  // 模型 / 技術
  '人工智慧', '語言模型', '神經網路', '深度學習', '機器學習',
  'Transformer', 'Token', 'Prompt', 'RAG', 'Embedding',
  // 訓練流程
  '提示詞', '訓練資料', '監督式學習', '強化學習', '微調',
  '預訓練', '對齊', '人類回饋', '梯度', '反向傳播',
  // 模型內部
  '詞元', '上下文', '注意力機制', '推理', '生成',
  '損失函數', '嵌入向量', '詞彙表', '機率分布', '取樣',
  '思維鏈', '解碼', '溫度', '演算法',
  // 資料來源 (呼應 tagline「讀完整個網路」)
  '網路文章', '維基百科', '對話紀錄', '程式碼', '論文',
  '故事', '新聞', '部落格', '評論', '翻譯',
  '留言', '小說', '教科書', '文件', '字典',
  // 人類動作
  '理解', '預測', '學習', '記憶', '推論',
];

const LINE_COUNT = 50;
const TERMS_PER_LINE_MIN = 7;
const TERMS_PER_LINE_MAX = 11;

function makeLine() {
  const n = TERMS_PER_LINE_MIN + Math.floor(Math.random() * (TERMS_PER_LINE_MAX - TERMS_PER_LINE_MIN + 1));
  const out = [];
  for (let i = 0; i < n; i++) out.push(TERMS[(Math.random() * TERMS.length) | 0]);
  return out.join('  ');
}

export default function Ch3Step1() {
  const [lines, setLines] = useState(() => Array.from({ length: LINE_COUNT }, makeLine));

  useEffect(() => {
    const id = setInterval(() => {
      setLines((prev) => {
        const next = prev.slice();
        // 每 tick 替換 ~4 行 (8%) — 緩慢交替的「資料持續流入」感
        for (let i = 0; i < 4; i++) {
          next[(Math.random() * next.length) | 0] = makeLine();
        }
        return next;
      });
    }, 2500);
    return () => clearInterval(id);
  }, []);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      fontFamily: 'Space Grotesk', overflow: 'hidden',
    }}>
      {/* Left column wipe-in from left, 60% width */}
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)' }}
        animate={{ clipPath: 'inset(0 0 0 0)' }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        style={{
          position: 'absolute', top: 0, bottom: 0, left: 0, width: '100%',
          background: 'transparent', padding: 64,
          display: 'flex', flexDirection: 'column',
          justifyContent: 'center', alignItems: 'center', textAlign: 'center',
        }}
      >
        {/* Background scrolling text grid (subtle low-density) */}
        <div
          aria-hidden="true"
          style={{
            position: 'absolute', inset: 0, overflow: 'hidden',
            opacity: 0.08, fontSize: 14, fontFamily: 'monospace',
            lineHeight: 1.6, padding: 12, color: '#000',
          }}
        >
          {lines.map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </div>

        <ScanlineOverlay />
        <InhaleLayer terms={TERMS} />

        {/* "LLM" hero with overshoot stamp */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            fontWeight: 900, fontSize: '10rem', lineHeight: 1, color: '#000',
            position: 'relative', zIndex: 1,
          }}
        >
          LLM
        </motion.div>

        {/* Purple sub-label */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 1.0 }}
          style={{
            background: '#C4B5FD', color: '#000',
            padding: '8px 20px', alignSelf: 'center',
            border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
            fontWeight: 900, fontSize: 22, marginTop: 16, rotate: -2,
            position: 'relative', zIndex: 1,
          }}
        >
          supervised + RLHF
        </motion.div>

        {/* Tagline */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 1.4 }}
          style={{
            marginTop: 32, fontWeight: 700, fontSize: '1.5rem', maxWidth: 600,
            position: 'relative', zIndex: 1,
          }}
        >
          把整個人類網路寫過的東西全部讀一遍
        </motion.div>
      </motion.div>
    </main>
  );
}
