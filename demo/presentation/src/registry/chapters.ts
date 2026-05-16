import type { ChapterDef } from "./types";
import ColdopenChapter from "../chapters/01-coldopen/Coldopen";
import { narrations as coldopenNarrations } from "../chapters/01-coldopen/narrations";

/**
 * Order = order of presentation.
 *
 * Each chapter MUST provide a `narrations: Narration[]` array. Its length
 * is the chapter's step count — there is no `totalSteps` to maintain
 * separately. This guarantees the audio synthesis pipeline, the runtime
 * stepper, and the chapter `.tsx` switch on `step` cannot drift apart.
 *
 * Visual styling (color, fonts) comes entirely from the active theme
 * (Neo-brutalism override in src/styles/tokens.css).
 */
export const CHAPTERS: ChapterDef[] = [
  {
    id: "coldopen",
    title: "心虛開場 · 心理學系 · 捷運靈感",
    narrations: coldopenNarrations,
    Component: ColdopenChapter,
  },
];
