// 漫畫集中線：黑色放射狀楔形從中心炸開，中央留洞給印章。
// 呼應全片粗黑線條美學，snap 入場帶來吐槽笑點的瞬間衝擊。
import { motion } from 'motion/react';

export function ComicSpeedLines({ active = false, size = 1100, count = 36, delay = 0, receded = false }) {
  const cx = size / 2;
  const cy = size / 2;
  const rIn = size * 0.21;   // 中央留洞半徑（給印章）
  const rOut = size * 0.72;  // 集中線外緣
  const wedges = [];
  for (let i = 0; i < count; i++) {
    const a = (i / count) * Math.PI * 2;
    const half = (Math.PI / count) * 0.40; // 楔形角寬的一半
    const x1 = cx + rIn * Math.cos(a - half);
    const y1 = cy + rIn * Math.sin(a - half);
    const x2 = cx + rOut * Math.cos(a);
    const y2 = cy + rOut * Math.sin(a);
    const x3 = cx + rIn * Math.cos(a + half);
    const y3 = cy + rIn * Math.sin(a + half);
    wedges.push(`${x1.toFixed(1)},${y1.toFixed(1)} ${x2.toFixed(1)},${y2.toFixed(1)} ${x3.toFixed(1)},${y3.toFixed(1)}`);
  }
  return (
    <motion.svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      initial={false}
      animate={
        !active
          ? { scale: 0.4, opacity: 0, rotate: -8 }
          : receded
            // 爆點過後收束成圍繞印章的緊湊放射，讓出下方給結尾文字
            ? { scale: 0.5, opacity: 1, rotate: 0 }
            : { scale: 1, opacity: 1, rotate: 0 }
      }
      transition={receded
        ? { duration: 0.4, ease: [0.4, 0, 0.2, 1] }
        : { duration: 0.35, ease: [0.34, 1.56, 0.64, 1], delay: active ? delay : 0 }}
      style={{ display: 'block', overflow: 'visible' }}
    >
      {wedges.map((pts, i) => (
        <polygon key={i} points={pts} fill="#000" />
      ))}
    </motion.svg>
  );
}
