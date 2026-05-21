import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';

// 夯爆了 / 拉完了 tier-list meme — 把 supervised vs RL 兩條路線丟進排行榜。
// 5 rows top→bottom: 夯 顶级 人上人 NPC 拉完了 (簡體中文以還原迷因原版)
const TIERS = [
  { key: '夯',     bg: '#E84545' },
  { key: '顶级',   bg: '#F2A93B' },
  { key: '人上人', bg: '#FFEB3B' },
  { key: 'NPC',    bg: '#FCEED9' },
  { key: '拉完了', bg: '#FFFFFF' },
];

const ROW_H = 124;
const DIVIDER = 3;       // borderTop on rows 1..4 (content-box → adds to total height)
const LABEL_W = 240;
const SLOT_W = 880;
const TABLE_W = LABEL_W + SLOT_W;
const TABLE_H = ROW_H * TIERS.length + DIVIDER * (TIERS.length - 1);

const ROW_HANG = 0;   // 夯  (頂 — RL 的 dock)
const ROW_TRASH = 4;  // 拉完了 (底 — supervised 的 dock)

const OVERSHOOT = [0.34, 1.56, 0.64, 1];
const STICKER_TR = { duration: 0.6, ease: OVERSHOOT };
const TABLE_TR   = { duration: 0.4, ease: 'easeOut' };

const SHOWCASE_SCALE = 1.8;
const DOCK_INSET = 16;   // sticker 視覺左緣 相對 slot 左緣 的 px

const STICKER_BASE = {
  position: 'absolute',
  background: '#FFD93D',
  color: '#000',
  padding: '12px 26px',
  border: '5px solid #000',
  boxShadow: '6px 6px 0 0 #000',
  fontWeight: 900,
  fontSize: 30,
  whiteSpace: 'nowrap',
};

// row i 的 slot 垂直中軸 (相對 table 左上角)
const rowCenterY = (rowIdx) => rowIdx * (ROW_H + DIVIDER) + ROW_H / 2;

// 「showcase 大」 — 置中 table 容器、scale 1.8。
// 用 transformOrigin: 'center center' 配 x:'-50%', y:'-50%' 達成水平垂直居中。
function showcaseAnim(rotate) {
  return {
    opacity: 1,
    scale: SHOWCASE_SCALE,
    top: TABLE_H / 2,
    left: TABLE_W / 2,
    x: '-50%',
    y: '-50%',
    rotate,
    filter: 'blur(0px)',
    transformOrigin: 'center center',
  };
}

// 「dock 小」 — sticker 視覺左緣 = LABEL_W + DIVIDER + DOCK_INSET。
// transformOrigin: 'left center' + x:0 → left 座標即視覺左緣。
function dockAnim(rowIdx, rotate, dim) {
  return {
    opacity: dim ? 0.35 : 1,
    scale: 1,
    top: rowCenterY(rowIdx),
    left: LABEL_W + DIVIDER + DOCK_INSET,
    x: 0,
    y: '-50%',
    rotate,
    filter: dim ? 'blur(3px)' : 'blur(0px)',
    transformOrigin: 'left center',
  };
}

// 「隱藏」 — 縮在 showcase 位置外、opacity 0。給 RL beat<2 用，beat 2 可平順 morph 成 showcase。
function hiddenAnim() {
  return {
    opacity: 0,
    scale: 0.2,
    top: TABLE_H / 2,
    left: TABLE_W / 2,
    x: '-50%',
    y: '-50%',
    rotate: 0,
    filter: 'blur(0px)',
    transformOrigin: 'center center',
  };
}

// tier-table 容器自己的 dim 狀態 — 跟 parked sticker 的 dim 狀態同步、但這裡單獨算
// 因為 sticker 是 motion 平級兄弟、不靠 CSS 繼承 (避免 filter inheritance 不可預期)。
function tableState(beatIndex) {
  if (beatIndex <= 0) return { opacity: 0,    filter: 'blur(0px)' };
  if (beatIndex === 2) return { opacity: 0.35, filter: 'blur(3px)' };
  return { opacity: 1, filter: 'blur(0px)' };
}

function supervisedState(beatIndex) {
  if (beatIndex === 0) return showcaseAnim(0);
  // beat ≥ 1: dock 在 拉完了；只在 beat 2 dim。
  return dockAnim(ROW_TRASH, -3, beatIndex === 2);
}

function rlState(beatIndex) {
  if (beatIndex < 2)  return hiddenAnim();
  if (beatIndex === 2) return showcaseAnim(0);
  // beat ≥ 3: dock 在 夯；不會 dim (table 此時 crisp)。
  return dockAnim(ROW_HANG, 3, false);
}

export default function Ch4Step2() {
  const { beatIndex } = usePresentationContext();

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <div style={{
        position: 'relative',
        width: TABLE_W,
        height: TABLE_H,
      }}>
        {/* Tier table — 用 motion.div 包，opacity + blur 由 tableState 控 */}
        <motion.div
          initial={{ opacity: 0, filter: 'blur(0px)' }}
          animate={tableState(beatIndex)}
          transition={TABLE_TR}
          style={{
            position: 'absolute', inset: 0,
            border: '6px solid #000',
            boxShadow: '14px 14px 0 0 #000',
            background: '#000',
          }}
        >
          {TIERS.map((t, i) => (
            <div key={t.key} style={{
              display: 'flex',
              height: ROW_H,
              borderTop: i === 0 ? 'none' : `${DIVIDER}px solid #000`,
              background: '#D0D0D0',
            }}>
              <div style={{
                width: LABEL_W,
                background: t.bg,
                borderRight: `${DIVIDER}px solid #000`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 900,
                fontSize: t.key === 'NPC' ? 56 : 64,
                color: '#000',
                letterSpacing: t.key === 'NPC' ? 0 : 2,
              }}>
                {t.key}
              </div>
              <div style={{ width: SLOT_W }} />
            </div>
          ))}
        </motion.div>

        {/* supervised — beat 0 showcase、beat 1+ dock 在 拉完了 (beat 2 dim) */}
        <motion.div
          initial={hiddenAnim()}
          animate={supervisedState(beatIndex)}
          transition={STICKER_TR}
          style={{ ...STICKER_BASE, zIndex: 10 }}
        >
          supervised
        </motion.div>

        {/* RL 增強式訓練 — beat<2 hidden、beat 2 showcase、beat 3+ dock 在 夯 */}
        <motion.div
          initial={hiddenAnim()}
          animate={rlState(beatIndex)}
          transition={STICKER_TR}
          style={{ ...STICKER_BASE, zIndex: 11 }}
        >
          RL 增強式訓練
        </motion.div>
      </div>
    </main>
  );
}
