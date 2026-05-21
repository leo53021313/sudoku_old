import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { ImpactDust } from '../../motifs/ImpactDust.jsx';
import { StarburstShards } from '../../motifs/StarburstShards.jsx';

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

const CAPTION_TR = { duration: 0.45, ease: OVERSHOOT };          // 整塊 caption 進出
const CAPTION_TEXT_TR = { duration: 0.35, ease: 'easeOut' };     // 下方文字 fade-up

const CAPTION_TOP_OFFSET = 170;  // sticker 下方 ~170 px (避開 hard shadow + scale 1.8 邊緣)

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
  if (beatIndex <= 1) return { opacity: 0,    filter: 'blur(0px)' };
  if (beatIndex === 3 || beatIndex === 4) return { opacity: 0.35, filter: 'blur(3px)' };
  return { opacity: 1, filter: 'blur(0px)' };
}

function supervisedState(beatIndex) {
  if (beatIndex < 2) return showcaseAnim(0);
  // beat ≥ 2: dock 拉完了；dim 在 RL showcase 區段 (beat 3-4)
  return dockAnim(ROW_TRASH, -3, beatIndex === 3 || beatIndex === 4);
}

function rlState(beatIndex) {
  if (beatIndex < 3) return hiddenAnim();
  if (beatIndex < 5) return showcaseAnim(0);
  // beat ≥ 5: dock 夯
  return dockAnim(ROW_HANG, 3, false);
}

export default function Ch4Step2() {
  const { beatIndex, triggerShake } = usePresentationContext();

  // 著陸 shake 只在進入 dock beat 的「上升緣」觸發一次，避免來回切 beat 重打。
  const shakeFiredRef = useRef({ supervised: false, rl: false });

  useEffect(() => {
    if (beatIndex === 2 && !shakeFiredRef.current.supervised) {
      shakeFiredRef.current.supervised = true;
      triggerShake();
    } else if (beatIndex !== 2) {
      shakeFiredRef.current.supervised = false;
    }
    if (beatIndex === 5 && !shakeFiredRef.current.rl) {
      shakeFiredRef.current.rl = true;
      triggerShake();
    } else if (beatIndex !== 5) {
      shakeFiredRef.current.rl = false;
    }
  }, [beatIndex, triggerShake]);

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

        {/* ImpactDust — 拉完了 dock 著陸；wrapper 把 motif 內建的 (50%, 78%) 錨點移到 dock 中心 */}
        <div style={{
          position: 'absolute',
          left: LABEL_W + DIVIDER + DOCK_INSET,  // wrapper left = dock left edge; motif's built-in left:50% of 200px wrapper places origin at dock_left + 100 ≈ sticker visual center
          top: rowCenterY(ROW_TRASH) - 78,            // 78% of 100 = 78; offset 使 motif 中心對齊 row 中軸
          width: 200,
          height: 100,
          pointerEvents: 'none',
          zIndex: 5,
        }}>
          <ImpactDust active={beatIndex >= 2} />
        </div>

        {/* StarburstShards — 夯 dock 著陸；wrapper 把 motif 內建的 (50%, 50%) 錨點移到 dock 中心 */}
        <div style={{
          position: 'absolute',
          left: LABEL_W + DIVIDER + DOCK_INSET,
          top: rowCenterY(ROW_HANG) - 50,
          width: 200,
          height: 100,
          pointerEvents: 'none',
          zIndex: 5,
        }}>
          <StarburstShards active={beatIndex >= 5} />
        </div>

        {/* supervised — beat 0-1 showcase、beat ≥ 2 dock 在 拉完了 (beat 3-4 dim) */}
        <motion.div
          initial={hiddenAnim()}
          animate={supervisedState(beatIndex)}
          transition={STICKER_TR}
          style={{ ...STICKER_BASE, zIndex: 10 }}
        >
          supervised
        </motion.div>

        {/* RL 增強式訓練 — beat<3 hidden、beat 3-4 showcase、beat ≥ 5 dock 在 夯 */}
        <motion.div
          initial={hiddenAnim()}
          animate={rlState(beatIndex)}
          transition={STICKER_TR}
          style={{ ...STICKER_BASE, zIndex: 11 }}
        >
          RL 增強式訓練
        </motion.div>

        {/* supervised ❌ caption — beat 1 stamp-in、beat 其它 hidden */}
        <motion.div
          initial={false}
          animate={{
            opacity: beatIndex === 1 ? 1 : 0,
            top: TABLE_H / 2 + CAPTION_TOP_OFFSET,
            left: TABLE_W / 2,
            x: '-50%',
          }}
          transition={CAPTION_TR}
          style={{
            position: 'absolute',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 14,
            pointerEvents: 'none',
            zIndex: 12,
          }}
        >
          <motion.div
            initial={false}
            animate={beatIndex === 1
              ? { scale: [0, 1.4, 1], rotate: [-8, 2, 0], opacity: 1 }
              : { scale: 0, rotate: 0, opacity: 0 }}
            transition={CAPTION_TR}
            style={{
              fontSize: 96,
              fontWeight: 900,
              color: '#FF3B30',
              textShadow: '4px 4px 0 #000',
              lineHeight: 1,
            }}
          >
            ✕
          </motion.div>
          <motion.div
            initial={false}
            animate={beatIndex === 1 ? { y: 0, opacity: 1 } : { y: 12, opacity: 0 }}
            transition={{ ...CAPTION_TEXT_TR, delay: beatIndex === 1 ? 0.2 : 0 }}
            style={{
              background: '#000',
              color: '#FFFDF5',
              padding: '12px 28px',
              border: '4px solid #000',
              boxShadow: '6px 6px 0 0 #000',
              fontWeight: 900,
              fontSize: 30,
              whiteSpace: 'nowrap',
            }}
          >
            我不想要 AI 背答案
          </motion.div>
        </motion.div>

        {/* RL ✓ caption — beat 4 stamp-in、beat 其它 hidden */}
        <motion.div
          initial={false}
          animate={{
            opacity: beatIndex === 4 ? 1 : 0,
            top: TABLE_H / 2 + CAPTION_TOP_OFFSET,
            left: TABLE_W / 2,
            x: '-50%',
          }}
          transition={CAPTION_TR}
          style={{
            position: 'absolute',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 14,
            pointerEvents: 'none',
            zIndex: 12,
          }}
        >
          <motion.div
            initial={false}
            animate={beatIndex === 4
              ? { scale: [0, 1.4, 1], rotate: [-8, 2, 0], opacity: 1 }
              : { scale: 0, rotate: 0, opacity: 0 }}
            transition={CAPTION_TR}
            style={{
              fontSize: 96,
              fontWeight: 900,
              color: '#06B26F',
              textShadow: '4px 4px 0 #000',
              lineHeight: 1,
            }}
          >
            ✓
          </motion.div>
          <motion.div
            initial={false}
            animate={beatIndex === 4 ? { y: 0, opacity: 1 } : { y: 12, opacity: 0 }}
            transition={{ ...CAPTION_TEXT_TR, delay: beatIndex === 4 ? 0.2 : 0 }}
            style={{
              background: '#000',
              color: '#FFFDF5',
              padding: '12px 28px',
              border: '4px solid #000',
              boxShadow: '6px 6px 0 0 #000',
              fontWeight: 900,
              fontSize: 30,
              whiteSpace: 'nowrap',
            }}
          >
            讓 AI 從零自己學習規則
          </motion.div>
        </motion.div>
      </div>
    </main>
  );
}
