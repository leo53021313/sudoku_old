import { useState } from 'react';
import { AiSticker } from '../components/AiSticker.jsx';
import { AssetPlaceholder } from '../components/AssetPlaceholder.jsx';

// 奶茶 — img2img 角色（奶茶髮色 + 韓式鍋蓋頭）。
// 四個情緒 variant：normal（中性）/ happy（心動）/ crashed（崩潰）/ question（困惑、ch7 s7 用）。
// PNG 尚未生成時，img onError → 改顯示 AssetPlaceholder，避免破圖。
const VARIANT_SRC = {
  normal: '/images/ai/ch6/milk-tea.png',
  happy: '/images/ai/ch6/milk-tea-happy.png',
  crashed: '/images/ai/ch6/milk-tea-crashed.png',
  question: '/images/ai/ch6/milk-tea-question.png',
};

const VARIANT_TODO = {
  normal: 'ch6-milk-tea',
  happy: 'ch6-milk-tea-happy',
  crashed: 'ch6-milk-tea-crashed',
  question: 'ch6-milk-tea-question',
};

export function MilkTea({ width = 300, rotation = -3, shadow = 12, variant = 'normal', ...rest }) {
  const [errored, setErrored] = useState(false);

  if (errored) {
    return <AssetPlaceholder type="[AI]" width={width} height={width} todo={VARIANT_TODO[variant] ?? VARIANT_TODO.normal} />;
  }

  return (
    <AiSticker
      src={VARIANT_SRC[variant] ?? VARIANT_SRC.normal}
      alt="奶茶"
      width={width}
      rotation={rotation}
      shadow={shadow}
      onError={() => setErrored(true)}
      {...rest}
    />
  );
}
