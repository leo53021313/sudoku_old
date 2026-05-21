# ch3 step1 — 背景 Scanline 掃描 + 偶發 Inhale 吸入 設計

**日期:** 2026-05-21
**範圍:** `demo/presentation/src/chapters/ch3-llm-vs-rl/Ch3Step1.jsx` 及兩個新元件
**相關:** ch3 step1 目前的「詞彙交替版」背景（50 行隨機 AI 術語、opacity 0.08、每 2.5s 替換 4 行）保留作為靜態底層；本 spec 在其上疊加兩層動態效果。

## 目標

讓 ch3 step1 的背景從目前的「安靜詞彙網格」升級到「LLM 正在主動讀取資料」的視覺敘事，呼應 tagline「把整個人類網路寫過的東西全部讀一遍」，同時不搶 LLM hero / supervised+RLHF sticker / tagline 的注意力。

策略：兩層疊加
- **Scanline**：恆定環境感（持續掃描動作 = LLM 在處理）
- **Inhale**：偶發戲劇高潮（個別詞被「吸入」LLM hero = 資料被消化）

## 整體層級

```
z=0  既有 grid 容器 (motion.div with clipPath wipe)
     ├─ 既有: 50 行詞彙交替 grid                 (opacity 0.08, static positioning)
     ├─ 【新】<ScanlineOverlay />               (絕對定位、pointer-events:none、純 CSS 動畫)
     ├─ 【新】<InhaleLayer />                   (絕對定位、pointer-events:none、motion 粒子)
     ├─ 既有: LLM hero (10rem)                  (z-index:1)
     ├─ 既有: 紫色 sticker (supervised + RLHF)   (z-index:1)
     └─ 既有: tagline                            (z-index:1)
```

兩個新元件加在既有 grid 之後、hero 之前（DOM 順序），靠 `z-index` 確保 hero/sticker/tagline 蓋在上面。Scanline 與 Inhale 都用 `pointer-events: none`，不干擾互動（雖然本頁沒互動）。

## Scanline 細節

### 視覺
- 一條對角線方向的紫色漸層帶（中段亮、兩側淡出），慢速從畫面一側掃到另一側並無限循環。
- 顏色：紫色 `#C4B5FD`（跟 sticker 同色系），alpha 中段約 `0.18`、兩端 `0`。
- 亮段寬度：用 `linear-gradient` 的 stops 控制（範例：`45% / 50% / 55%`，亮段佔長條總寬的 10%）；視覺寬度依長條尺寸決定，實作時可調 stops 調寬窄。
- 行進方向：左下→右上，角度約 `-20°`（即 `rotate(-20deg)`）。

### 結構
單一 `<div>` 元素，絕對定位 `inset: 0`，內含一條更大的傾斜長條（用 `transform: rotate(-20deg)` 加 `linear-gradient` 寬度 220px）。
- 為了讓掃描帶完整掃過畫面後消失再從另一側進場，內部長條的寬度遠大於父容器（例如 `width: 200%`），起點 `translateX(-100%)`，終點 `translateX(100%)`。

### 動畫
- CSS `@keyframes`：`translateX(-100%) → translateX(100%)`，`linear` easing。
- 週期：**7s**（夠慢，不會搶戲；夠快，使用者在一張投影片內能看到至少一輪）。
- 無限循環 (`animation-iteration-count: infinite`)。
- 用 CSS 而非 motion 是為了效能（GPU 合成，無 React render）。

### 啟動延遲
Step1 既有的入場動畫（grid clipPath wipe + LLM stamp + sticker + tagline）約在 1.9s 結束。Scanline 加 `animation-delay: 1.8s`，避開干擾。

### 簡寫實作預期
```jsx
// ScanlineOverlay.jsx
<div aria-hidden style={{
  position: 'absolute', inset: 0, overflow: 'hidden',
  pointerEvents: 'none', zIndex: 0,
}}>
  <div style={{
    position: 'absolute', top: '-50%', left: 0, width: '200%', height: '200%',
    transform: 'rotate(-20deg)',
    background: 'linear-gradient(90deg, transparent 0%, rgba(196,181,253,0) 45%, rgba(196,181,253,0.18) 50%, rgba(196,181,253,0) 55%, transparent 100%)',
    animation: 'ch3s1-scanline 7s linear 1.8s infinite',
  }} />
</div>
```

`@keyframes ch3s1-scanline` 定義 `0% { transform: rotate(-20deg) translateX(-100%); } 100% { transform: rotate(-20deg) translateX(100%); }`。注意 `translateX` 是在旋轉後的座標系移動，視覺上是沿「-20°」方向的對角線位移。

> 註：keyframe 的 transform 必須完整重述 `rotate(-20deg)`，否則旋轉會被覆寫。

## Inhale 細節

### 視覺
- 每隔 6 秒 ± 1.5s（隨機）出現一個「被點亮」的詞，從 grid 範圍內某處飛向 LLM hero 中心，並在飛行過程中縮小+淡出，像「被吸進去消化」。
- 顏色：紫色 `#C4B5FD`、alpha `0.7`（比 grid 的 0.08 明顯）。
- 字型：14px monospace bold（跟 grid 同字級、字體一致；用 bold 與 alpha 0.7 讓它在飛行時可辨識，但不大到搶戲）。
- 文字來源：從現有 `TERMS` 隨機抽一個詞。

### 起點選擇
- 在視窗範圍內任意取 (x, y)，但避開 hero 中央區域：以畫面中心為原點的 **320×240 px** 禁區內的座標不採用。
- 演算法：rejection sampling — 隨機產生 (x, y)，若落在禁區內就重抽，最多 5 次；超過上限就用最後一次的值（極不可能：禁區只佔視窗約 5-10% 面積）。
- 因為 ch3 step1 已置中、grid 容器寬度 100%，直接用 `window.innerWidth`/`window.innerHeight` 作為視窗尺寸即可，不需要 `containerRef`。

### 終點
- LLM hero 螢幕中央。固定使用 `window.innerWidth / 2, window.innerHeight / 2` — Step1 hero 是置中佈局，不需要 `getBoundingClientRect` 動態追。
- 不處理 resize（簡報固定螢幕尺寸演講）。

### 動畫
- 持續時間：1.2s。
- Easing：`ease-in`（[0.4, 0, 1, 1]）— 起初慢、越接近 LLM 越快，模擬重力吸引。
- 屬性：
  - `x`, `y` 從起點 → 終點（用 motion 的 `x`, `y` props，數值為相對起點的像素位移）
  - `scale`：1 → 0.2
  - `opacity`：0.7 → 0

### 觸發機制
- `setTimeout` 遞迴排程，每次完成後計算下一個 `6000 + (Math.random() * 3000 - 1500)` ms。
- 用 `useState` 管理 `particles` 陣列；每個粒子有 `id` (incrementing counter)、`text`、`startX/startY`、`endX/endY`。
- 每個粒子 motion 元件用 `onAnimationComplete` 回呼從 state 移除自己，避免無限累積。

### 啟動延遲
- 第一個粒子在 Step1 mount 後 **3.0s** 出現（讓 scanline 先跑半輪、營造氛圍後再來高潮）。

### 簡寫實作預期
```jsx
// InhaleLayer.jsx
function InhaleLayer({ terms }) {
  const [particles, setParticles] = useState([]);
  const counter = useRef(0);

  useEffect(() => {
    let timeoutId;
    let alive = true;
    const spawn = () => {
      if (!alive) return;
      const id = counter.current++;
      const { startX, startY } = pickStart();
      const endX = window.innerWidth / 2;
      const endY = window.innerHeight / 2;
      const text = terms[(Math.random() * terms.length) | 0];
      setParticles(p => [...p, { id, text, startX, startY, endX, endY }]);
      timeoutId = setTimeout(spawn, 4500 + Math.random() * 3000); // 6s ± 1.5s
    };
    timeoutId = setTimeout(spawn, 3000); // 第一發
    return () => { alive = false; clearTimeout(timeoutId); };
  }, [terms]);

  return (
    <div aria-hidden style={{ position: 'absolute', inset: 0, pointerEvents: 'none', zIndex: 0 }}>
      {particles.map(p => (
        <motion.div
          key={p.id}
          initial={{ x: p.startX, y: p.startY, scale: 1, opacity: 0.7 }}
          animate={{ x: p.endX, y: p.endY, scale: 0.2, opacity: 0 }}
          transition={{ duration: 1.2, ease: [0.4, 0, 1, 1] }}
          onAnimationComplete={() => setParticles(s => s.filter(q => q.id !== p.id))}
          style={{
            position: 'absolute', top: 0, left: 0,
            fontFamily: 'monospace', fontWeight: 700, fontSize: 14,
            color: '#C4B5FD', whiteSpace: 'nowrap',
          }}
        >
          {p.text}
        </motion.div>
      ))}
    </div>
  );
}
```

`pickStart()` 拒絕落在中央 forbidden box 的點，最多 retry 5 次。Forbidden box：`{ x0: w/2 - 160, y0: h/2 - 120, x1: w/2 + 160, y1: h/2 + 120 }`。

> 註：motion 的 `x`/`y` 對字串單位（如 `'50vw'`）支援不一致 — 用純數字（像素）。

## 編舞時序總覽

| 時間 | 事件 |
|------|------|
| 0.0s | Step1 mount（既有 60% → 100% wipe 等都不變） |
| 0.0s | 既有: 主容器 clipPath wipe-in 開始 |
| 0.6s | 既有: 主容器 wipe 完，LLM stamp 開始 |
| 1.0s | 既有: 紫色 sticker 從左滑入 |
| 1.4s | 既有: tagline 淡入 |
| **1.8s** | **【新】Scanline 第一輪開始**（CSS animation-delay） |
| **3.0s** | **【新】第一個 Inhale 粒子出現** |
| 後續 | 每 6 秒 ± 1.5s 一個 Inhale；Scanline 持續 7s 一輪循環 |

## 元件切分

```
demo/presentation/src/chapters/ch3-llm-vs-rl/
├─ Ch3Step1.jsx                 (改：import + 在 grid 內側插入兩個新元件)
├─ ScanlineOverlay.jsx          (新)
└─ InhaleLayer.jsx              (新)
```

**為何不放 `layers/` 或 `components/`**：這兩個效果是 ch3 s1 專屬敘事 — Scanline 顏色綁在紫色 sticker、Inhale 終點綁在 ch3 s1 hero 中心。先就近放，將來如果 ch4 也要用再 promote。

**為何不修改既有 grid**：grid 的 `useState`/`useEffect`（每 2.5s 替換 4 行）邏輯獨立、運作正常；本 spec 只是疊加層，避免動到其他人 review 過的程式碼。

## 不做的事（YAGNI）

- **不做「Scanline 經過時 grid 文字變亮」**：需要 `mix-blend-mode` 或 mask 操作 grid，跨瀏覽器表現不穩定；漸層帶本身已足夠搶眼。
- **不動態追蹤 LLM hero 位置**：Step1 hero 是 viewport 中央置中，硬編 `window.innerWidth/2, innerHeight/2` 即可。
- **不監聽 resize**：簡報固定螢幕尺寸演講。
- **不做粒子互相避讓**：每 6 秒一發，最大 2-3 個同時在飛，碰撞機率極低。
- **不做暫停/恢復**：簡報沒有此需求。
- **不擴張到 ch4-9 其他章節**：先解決 ch3 s1 的「眼前一亮」需求。

## 風險與緩解

| 風險 | 機率 | 緩解 |
|------|------|------|
| Scanline 跟 sticker 重疊時顏色撞色（紫疊紫） | 中 | Scanline 在 grid 容器內、z-index 0；sticker z-index 1。視覺上 sticker 完全蓋過。 |
| Inhale 粒子飛行軌跡穿過紫色 sticker / 紅色 LLM stamp | 低 | 粒子用 z-index 0、被 hero 元素遮蔽。穿越時看不見 — 也正好符合「被吸入」敘事。 |
| 粒子數量無上限累積 | 低 | `onAnimationComplete` 主動清理；間隔 6s、動畫 1.2s，恆定上限 ~1 個。 |
| `setTimeout` 在 React StrictMode 雙重啟動 | 低 | `useEffect` 的 cleanup 用 `alive` flag + `clearTimeout`，雙呼叫時第一個會被取消。 |
| keyframe 沒寫完整 `rotate(-20deg)` 導致掃描帶變水平 | 中 | spec 已標註；實作時必須在 keyframe 0% 和 100% 都寫 `rotate(-20deg) translateX(...)`。 |
| motion `x`/`y` 對字串單位不穩定 | 低 | spec 已標註；用純像素數字。 |

## 驗收條件

1. Ch3 step1 mount 後 1.8s 起，畫面上能看到一條紫色斜向掃描帶從畫面一側緩慢移動到另一側。
2. Scanline 跑完一輪約 7s，無限循環。
3. Ch3 step1 mount 後 3.0s 起，畫面上開始出現紫色的詞，從 grid 邊緣飛向畫面中央、邊飛邊縮小淡出。
4. Inhale 粒子間隔 6s ± 1.5s。
5. LLM hero、紫色 sticker、tagline 的進場動畫不受影響（時序 0.6s/1.0s/1.4s 不變）。
6. 既有 grid 的詞彙每 2.5s 替換 4 行的行為不受影響。
7. 切換到 ch3 step2 後，兩個新效果都隨 Step1 卸載而停止（`key={stepId}` 已保證）。
