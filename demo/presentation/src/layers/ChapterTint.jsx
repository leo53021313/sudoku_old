// Per-chapter diagonal background gradient — per outline-visual.md §9.1
import { getChapter } from '../tokens/chapters.js';

export function ChapterTint({ chapterId }) {
  const ch = getChapter(chapterId);
  return (
    <div
      aria-hidden="true"
      style={{
        position: 'fixed', inset: 0, zIndex: 10, pointerEvents: 'none',
        background: `linear-gradient(135deg, #FFFDF5 0%, ${ch.tint} 100%)`,
        transition: 'background 500ms ease-out',
      }}
    />
  );
}
