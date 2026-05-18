import { AiSticker } from '../components/AiSticker.jsx';

export function GirlNew({ width = 280, rotation = -4, shadow = 10, ...rest }) {
  return (
    <AiSticker
      src="/images/ai/ch6/girl-new.png"
      alt="剛認識的新女生"
      width={width}
      rotation={rotation}
      shadow={shadow}
      {...rest}
    />
  );
}
