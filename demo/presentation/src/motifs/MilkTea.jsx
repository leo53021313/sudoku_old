import { useState } from 'react';
import { AiSticker } from '../components/AiSticker.jsx';
import { AssetPlaceholder } from '../components/AssetPlaceholder.jsx';

// 奶茶 — img2img 角色（奶茶髮色 + 韓式鍋蓋頭）。
// PNG 尚未生成時，img onError → 改顯示 AssetPlaceholder，避免破圖；
// 使用者把檔案放到 public/images/ai/ch6/milk-tea.png 後自動顯示真圖。
export function MilkTea({ width = 300, rotation = -3, shadow = 12, ...rest }) {
  const [errored, setErrored] = useState(false);

  if (errored) {
    return <AssetPlaceholder type="[AI]" width={width} height={width} todo="ch6-milk-tea" />;
  }

  return (
    <AiSticker
      src="/images/ai/ch6/milk-tea.png"
      alt="奶茶"
      width={width}
      rotation={rotation}
      shadow={shadow}
      onError={() => setErrored(true)}
      {...rest}
    />
  );
}
