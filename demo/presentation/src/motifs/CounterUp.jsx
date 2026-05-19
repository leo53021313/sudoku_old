import { useEffect, useState, useRef } from 'react';

export function CounterUp({
  from = 0,
  to,
  duration = 1200,
  prefix = '',
  suffix = '',
  onComplete = () => {},
}) {
  const [value, setValue] = useState(from);
  const completedRef = useRef(false);
  // 使用 latest-ref 模式：保存最新的 onComplete，避免父層每次 re-render 傳入新的
  // inline arrow 導致 useEffect 依賴改變、動畫重啟、onComplete 重複觸發（無窮迴圈）。
  const onCompleteRef = useRef(onComplete);

  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

  useEffect(() => {
    completedRef.current = false;
    const start = performance.now();
    let raf;
    const tick = (t) => {
      const elapsed = t - start;
      const pct = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - pct, 2);
      setValue(Math.round(from + (to - from) * eased));
      if (pct < 1) {
        raf = requestAnimationFrame(tick);
      } else if (!completedRef.current) {
        completedRef.current = true;
        onCompleteRef.current();
      }
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [from, to, duration]);

  return (
    <div style={{
      background: '#FFD93D', color: '#000',
      padding: '32px 96px', border: '8px solid #000', boxShadow: '16px 16px 0 0 #000',
      fontFamily: 'Space Grotesk', fontWeight: 900, fontSize: '8rem',
      transform: 'rotate(-3deg)',
      display: 'inline-block', lineHeight: 1,
    }}>
      {prefix}{value}{suffix}
    </div>
  );
}
