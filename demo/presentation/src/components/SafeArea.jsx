import { stage } from '../tokens/stage.js';

export function SafeArea({ children, style = {} }) {
  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        padding: `${stage.safePadding.y}px ${stage.safePadding.x}px`,
        boxSizing: 'border-box',
        ...style,
      }}
    >
      {children}
    </div>
  );
}
