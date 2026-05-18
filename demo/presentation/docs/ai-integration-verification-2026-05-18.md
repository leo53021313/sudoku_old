# AI 素材整合驗收紀錄 · 2026-05-18

> **Plan**: [docs/superpowers/plans/2026-05-18-ai-asset-integration.md](../../../docs/superpowers/plans/2026-05-18-ai-asset-integration.md)
> **Spec**: [docs/superpowers/specs/2026-05-18-ai-asset-integration-design.md](../../../docs/superpowers/specs/2026-05-18-ai-asset-integration-design.md)
> **執行**: subagent-driven、15 task、commit-per-task

## 14 個 commit 序列

| Task | SHA | 描述 |
| --- | --- | --- |
| 1 | a00edb9 | feat(presentation): add 10 AI-generated Neo-brutalism illustrations |
| 2 | aa68bed | feat(presentation): add AiBackdrop component for cinema-mode backgrounds |
| 3 | 1193a66 | feat(presentation): add AiSticker component for AI illustration wrapping |
| 4 | 2185622 | feat(presentation): lift MRT backdrop to Ch1 chapter level |
| 5 | cd2cfd5 | feat(presentation): ch1 s4 use AiSticker for girl-daydream, drop MRT placeholder |
| 6 | 0b675ec | feat(presentation): ch1 s5 use AiSticker for girl + flappy, drop placeholder |
| 7 | 5aca0ef | feat(presentation): ch1 s6 swap placeholders for AiSticker, keep ellipsis |
| 8 | b55b7eb | feat(presentation): ch1 s7 add soldier AiSticker, drop placeholder + text |
| 9 | a62a5d6 | feat(presentation): ch2 s1 right-side text stack → AI teacher-notes illustration |
| 10 | 839f6a0 | feat(presentation): ch2 s2 emoji clothes pile → AI folding-clothes illustration |
| 11 | e80b76e | feat(presentation): ch2 s3 dog/handshake emoji → AI dog-handshake illustration |
| 12 | ac5943f | feat(presentation): ch9 s3 brain/network emoji → AI illustrations |
| 13 | 2a8a445 | feat(presentation): ch9 s4 emoji ✈️🐦 → AI airplane-bird single illustration |
| 14 | b055c86 | feat(presentation): ch9 s5 center 🧠 emoji → AI brain-reward sticker |

## 視覺驗收（playwright 截圖、1920×1080 viewport）

| step | 截圖 | 通過 | 觀察 |
| --- | --- | --- | --- |
| ch1 s4 | ch1-s4-mrt-girl.png | ✓ | MRT full-bleed + 「靈感哪來呢」caption + girl AiSticker bottom-left |
| ch1 s5 | ch1-s5-mrt-flappy.png | ✓ | girl persisted + Code Bullet flappy bird top-right |
| ch1 s6 | ch1-s6-ellipsis.png | ✓ | ⋯⋯ ellipsis bubble above girl + 「然後我繼續發呆」caption |
| ch1 s7 | ch1-s7-soldier.png | ✓ | 3 stickers (girl + flappy + soldier) on MRT |
| ch2 s1 | ch2-s1-teacher.png | ✓ | supervised + teacher-notes AI 右側 |
| ch2 s2 | ch2-s2-clothes.png | ✓ | unsupervised + folding-clothes AI 右側 |
| ch2 s3 | ch2-s3-dog-alphago.png | ✓ | RL hero + dog-handshake AI 左下 + AlphaGo 紅 stamp 右下 |
| ch9 s3 | ch9-s3-brain-neural.png | ✓ | 兩 cream 卡（brain 紅 label / neural-net 黑 label）+ 中央黃 = stamp |
| ch9 s4 | ch9-s4-airplane-bird.png | ✓⚠ | airplane-bird AI 整圖 + hero。中央 SVG 箭頭被鳥/飛機接近處遮住、辨識度可後續強化 |
| ch9 s5 b0 | ch9-s5-brain-center.png | ✓ | beat 0 central brain-reward AiSticker |

⚠ **唯一觀察**: ch9 s4 中央雙向箭頭視覺被原 PNG 中飛機螺旋槳 / 鳥喙交會處遮蓋、辨識度低。建議後續 polish：把 SVG 箭頭加 cream 半透明背板或縮小放在「飛機 → 鳥」連線下方。

## ch1 MRT backdrop 重 mount 檢查

DevTools Network filter `mrt-window`：跨 ch1 s4→s5→s6→s7 全頁導航後、
- 請求次數：**1 個 GET**（第一次 200、後續導航因瀏覽器 cache 為 304 Not Modified）
- 真實 SPA 內 step 切換（無 reload）：Ch1.jsx 把 `<AiBackdrop>` render 為 `<Step key={stepId} />` 的 **sibling**、不是 child；React reconciler 看到 `<AiBackdrop>` 同 type 同 props 不會 unmount。code review confirmed (Task 4)。

## 紅線通過

- [x] 10 個 step 中無 emoji 殘留（✈️🐦🧠🕸️🐕🤝👕👖👔 全部清除）
- [x] 10 個 step 中無 `<AssetPlaceholder>` 殘留
- [x] 所有 AiSticker 有 4px 黑邊 + 8px hard shadow + 微旋轉
- [x] MRT backdrop 無黑邊框、full-bleed cinema mode
- [x] `npm run test:run` 26 pass（既有 3 hook tests + AiBackdrop 3 + AiSticker 4 + 既有 16 = 26）
- [x] `npm run lint`: 0 new errors（6 pre-existing 在我未動過的檔案：ChapterTint / FadeBridge / CrashLine / PresentationContext / usePresentation）

## 改動範圍 summary

- 新增 component (2): `AiBackdrop.jsx`, `AiSticker.jsx`（含 test = 4 個檔案）
- 新增 asset (10): `public/images/ai/ch{1,2,9}/*.png`
- 修改 step (10): `ch1-coldopen/Ch1Step{4,5,6,7}.jsx`, `ch2-ml-map/Ch2Step{1,2,3}.jsx`, `ch9-callback/Ch9Step{3,4,5}.jsx`
- 修改 chapter (1): `ch1-coldopen/Ch1.jsx`（升 MRT backdrop 跨 step 共用）
- 不動: `AssetPlaceholder.jsx`（其他 motif shells 仍用）+ `Sticker.jsx` / `Hero.jsx`

## 後續延伸（不在本次範圍）

- 更新 [demo/asset-production.md](../../asset-production.md) 加 `[AI]` 路線、把通過的素材標 `[AI]`

## v2 延伸（2026-05-18 同日）

> v2 把 AI 路線擴張到 2 個全片最重要的「戀愛 hook」character sticker（girl-new + girl-veteran）+ 4 處跨章節 callback。

### v2 commit 序列

| # | SHA | 描述 |
| --- | --- | --- |
| 0 | 79f2327 | fix: ch9 s4 wrap arrow in Neo-brutalism cream backplate (polish 自 v1 觀察) |
| 0 | 36fb03d | docs: v2 prompts for ch6-girl-new + ch7-girl-veteran |
| 1 | 8173dc1 | feat: add ch6 girl-new + ch7 girl-veteran AI illustrations |
| 2 | 81f3fc3 | feat: GirlNew motif wraps AI girl-new illustration |
| 3 | 9f92cf0 | feat: GirlVeteran motif wraps AI girl-veteran illustration |
| 4 | de2d9eb | feat: ch6 s3 pink text sticker → GirlNew AI character |
| 5 | a67b119 | feat: ch7 s7 add GirlVeteran in top-right as 'the asker' |
| 6 | ce1f96d | feat: ch9 s5 grayscale ghost uses GirlNew motif |
| 7 | a6597d0 | feat: ch9 s6 add GirlVeteran callback in top-right |

### v2 視覺驗收（playwright 截圖、1920×1080）

| step | 截圖 | 通過 | 觀察 |
| --- | --- | --- | --- |
| ch6 s3 | v2-ch6-s3-girl-new.png | ✓ | GirlNew 中央 (width 340 hero) + 副標「聊天都覺得對方也喜歡你」+ +/+/+ 浮動（捕捉到時機可能符號剛飄出畫面） |
| ch7 s7 b0 | v2-ch7-s7-veteran.png | ✓ | 「老油條女生陷阱題」黃 hero + GirlVeteran 右上角 peek（width 200, rotate 4°）|
| ch9 s5 b0 | v2-ch9-s5-girl-ghost.png | ✓⚠ | Brain sticker 主體 + GirlNew grayscale ghost（opacity 0.3 + grayscale、設計上的潛意識 callback、與 v1 原本粉紅文字 sticker 行為一致）|
| ch9 s6 | v2-ch9-s6-veteran-callback.png | ✓ | 「以為穩了 · 結果魔王關卡」hero + GirlVeteran 右上 callback（**同 ch7 s7 位置 + 同 width 200** = 觀眾自動識別「同一個人」）+ 4 魔王考題 grid |

### v2 紅線通過

- [x] 4 個受影響 step 全部通過 spec compliance + code quality review（每 task 雙段審）
- [x] `npm run test:run` 26 pass（既有 + 新增）
- [x] 跨章節 character 識別連續性：ch6 s3 GirlNew → ch9 s5 同 width 340 + grayscale；ch7 s7 GirlVeteran → ch9 s6 同 width 200 + 同位置
- [x] 視覺差異化：GirlNew 紅衣 +4° tilt vs GirlVeteran 紫衣 −3° tilt（避免混淆是同一角色）

### v2 改動範圍

- 新增 asset (2): `public/images/ai/ch6/girl-new.png`, `ch7/girl-veteran.png`
- 修改 motif (2): `motifs/GirlNew.jsx`, `GirlVeteran.jsx`（從 AssetPlaceholder shell → AiSticker 包裝）
- 修改 step (4): `Ch6Step3.jsx`, `Ch7Step7.jsx`, `Ch9Step5.jsx`, `Ch9Step6.jsx`

### v2 後續延伸

- ch9 s5 grayscale ghost 視覺可進一步增強：把 grayscale ghost 從 opacity 0.3 提升到 0.5 + 加 outline halo、讓觀眾更明顯辨識（trade-off：太顯眼會搶 brain sticker 焦點）
- 其餘節點視覺 AI 化已盡（reasoner / apprentice 章節結構性內容 [E] SVG 更合適、不適合 AI 路線）
