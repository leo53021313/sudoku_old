import { AiSticker } from '../components/AiSticker.jsx';

export function GirlVeteran({ width = 280, rotation = 3, shadow = 10, ...rest }) {
  return (
    <AiSticker
      src="/images/ai/ch7/girl-veteran.png"
      alt="老油條女生"
      width={width}
      rotation={rotation}
      shadow={shadow}
      {...rest}
    />
  );
}
