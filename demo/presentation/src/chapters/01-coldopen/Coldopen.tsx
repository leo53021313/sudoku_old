import type { ChapterStepProps } from "../../registry/types";
import "./Coldopen.css";

export default function ColdopenChapter({ step }: ChapterStepProps) {
  /* step 0 — 心虛開場 · cinematic sticker takeover */
  if (step === 0) {
    return (
      <div className="cd-scene">
        <div className="cd-stage cd-step0">
          <div style={{ position: "relative" }}>
            <div className="cd-anxious-sticker">心 虛</div>
            <div className="cd-anxious-tag">期中報告</div>
          </div>
          <p className="cd-anxious-sub">
            報告太不正經、請各位同學和老師 <em>多 · 包 · 涵</em>
          </p>
        </div>
      </div>
    );
  }

  /* step 1 — 心理學系背景 · sticker card with promise */
  if (step === 1) {
    return (
      <div className="cd-scene">
        <div className="cd-stage cd-step1">
          <div className="cd-major-card">
            <div className="cd-major-kicker">my major / 我的背景</div>
            <div className="cd-major-title">心 理 學 系</div>
            <div className="cd-major-en">Psychology · 畢業</div>
          </div>
          <div className="cd-major-promise">
            <svg viewBox="0 0 24 24" fill="none" strokeLinecap="round" strokeLinejoin="round">
              <path d="M5 12h14M13 5l7 7-7 7" />
            </svg>
            <span>結合心理學 · <b>敬請期待</b></span>
          </div>
        </div>
      </div>
    );
  }

  /* step 2 — 主題揭曉 · cinematic hero takeover */
  if (step === 2) {
    return (
      <div className="cd-scene">
        <div className="cd-stage cd-step2">
          <div className="cd-topic-decor cd-d1" />
          <div className="cd-topic-decor cd-d2">★</div>
          <div className="cd-topic-decor cd-d3" />
          <div className="cd-topic-decor cd-d4">?</div>

          <span className="cd-topic-kicker">期中主題</span>
          <h1 className="cd-topic-hero">
            訓 練 <span className="cd-em">A I</span>
            <br />
            <span className="cd-em-yellow">解 數 獨</span>
          </h1>
        </div>
      </div>
    );
  }

  /* step 3 — 捷運靈感 · parallax depth scene + 1st sticker */
  if (step === 3) {
    return (
      <div className="cd-scene">
        <div className="cd-train-bg" />
        <div className="cd-train-window" />

        <div className="cd-prompt-text">
          靈感是怎麼來的呢？<em>某天捷運上⋯</em>
        </div>

        <div className="cd-thought-cloud cd-girl cd-enter-1">
          <div className="cd-cloud-label">scene #1 · 正大光明</div>
          <div className="cd-cloud-body">
            看著對面 <em>正妹</em> 發呆
          </div>
        </div>
      </div>
    );
  }

  /* step 4 — 三個 sticker 串聯 (Code Bullet + 當兵) */
  if (step === 4) {
    return (
      <div className="cd-scene">
        <div className="cd-train-bg" />
        <div className="cd-train-window" />

        <div className="cd-prompt-text">
          腦袋突然冒出 <em>兩個畫面</em>
        </div>

        {/* sticker #1 — 正妹 (持續) */}
        <div className="cd-thought-cloud cd-girl cd-enter-1">
          <div className="cd-cloud-label">scene #1 · 持續發呆中</div>
          <div className="cd-cloud-body">
            看著對面 <em>正妹</em> 發呆
          </div>
        </div>

        {/* sticker #2 — Code Bullet flappy bird */}
        <div className="cd-thought-cloud cd-flappy cd-enter-2">
          <div className="cd-cloud-label">scene #2 · Code Bullet</div>
          <div className="cd-cloud-body">
            訓練 AI 玩 <em>flappy bird</em>
          </div>
        </div>

        {/* sticker #3 — 當兵 解數獨 */}
        <div className="cd-thought-cloud cd-army cd-enter-3">
          <div className="cd-cloud-label">scene #3 · 當兵記憶</div>
          <div className="cd-cloud-body">
            沒手機 · 只能 <em>解 · 數 · 獨</em>
          </div>
        </div>
      </div>
    );
  }

  /* step 5 — Boom · 兩個想法撞在一起 + punchline 收尾 */
  return (
    <div className="cd-scene">
      <div className="cd-stage cd-step5">
        <div className="cd-boom-burst" />

        <div className="cd-boom-card">
          <div className="cd-boom-kicker">B · O · O · M</div>
          <h1 className="cd-boom-title">
            訓練 <span className="cd-em-red">A I</span>
            <br />解 數 獨
          </h1>
        </div>

        <p className="cd-boom-punchline">
          靈感就是這麼 <em>莫名其妙</em> 地蹦出來
        </p>
      </div>
    </div>
  );
}
