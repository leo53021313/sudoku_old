// Beat manifest — encodes all 85 beats across 9 chapters / 57 steps.
// Source of truth: demo/outline.md per-step descriptions.

export const manifest = {
  totalChapters: 9,
  totalSteps: 57,
  totalBeats: 85,
  chapters: [
    {
      id: 1, name: 'coldopen', narrative: '心虛→心理學系→主題→捷運→Code Bullet→繼續發呆→當兵→BOOM',
      steps: [
        { id: 1, title: '心虛開場', duration: 10, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L1' }] },
        { id: 2, title: '心理學系畢業', duration: 8, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L5' }] },
        { id: 3, title: '主題揭曉', duration: 10, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L9' }] },
        { id: 4, title: '捷運看正妹', duration: 10, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L15' }] },
        { id: 5, title: 'Code Bullet flappy bird', duration: 8, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L19' }] },
        { id: 6, title: '繼續發呆', duration: 6, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L21' }] },
        { id: 7, title: '當兵沒手機解數獨', duration: 8, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L25' }] },
        { id: 8, title: 'BOOM', duration: 12, punchline: true, motifs: ['boom-double-ring', 'yellow-highlight'], climax: ['A', 'C'],
          beats: [
            { id: 'boom-burst',       type: 'click',              cue: 'Boom——', wait: null,         scriptLines: 'L29' },
            { id: 'boom-card',        type: 'auto', autoDelayMs: 400, cue: null,    wait: null,         scriptLines: 'L29' },
            { id: 'punchline-reveal', type: 'click',              cue: '靈感就是這麼', wait: '1-2s 觀眾消化', climax: ['A', 'C'], scriptLines: 'L35-37' },
          ],
        },
      ],
    },
    {
      id: 2, name: 'ml-map', narrative: 'supervised→unsupervised→RL+AlphaGo→cliffhanger',
      steps: [
        { id: 1, title: 'supervised',   duration: 14, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L49-55' }] },
        { id: 2, title: 'unsupervised', duration: 13, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L57-61' }] },
        { id: 3, title: 'RL+AlphaGo',   duration: 15, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L63-67' }] },
        { id: 4, title: 'cliffhanger',  duration: 8,  polish: true, motifs: ['yellow-highlight'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L71' }] },
      ],
    },
    {
      id: 3, name: 'llm-vs-rl', narrative: 'LLM→VS→OK純RL',
      steps: [
        { id: 1, title: 'LLM 路線',     duration: 14, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L75-77' }] },
        { id: 2, title: 'VS 對比',      duration: 14, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L81-89' }] },
        { id: 3, title: 'OK 純 RL',     duration: 7,  polish: true, motifs: ['halftone-burst'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L93-95' }] },
      ],
    },
    {
      id: 4, name: 'data-hunt', narrative: 'Kaggle→拒絕→受害者→封IP+proxy',
      steps: [
        { id: 1, title: 'Kaggle',                duration: 12, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L99-103' }] },
        { id: 2, title: 'supervised 拒絕',       duration: 11, polish: true, motifs: ['red-stamp'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L105-107' }] },
        { id: 3, title: '受害者', duration: 14, punchline: true, motifs: ['red-stamp'], climax: ['A', 'C'],
          beats: [
            { id: 'kicker',       type: 'click', cue: '我的終極目標是把我訓練好的 AI 拿去每個數獨網站...', wait: null, scriptLines: 'L111-115' },
            { id: 'url-sticker',  type: 'click', cue: '於是我找到了 websudoku.com...', wait: null, scriptLines: 'L117' },
            { id: 'victim-stamp', type: 'click', cue: '...（直接念出「這個受害者」當下點）', wait: '1-2s 笑點', climax: ['A', 'C'], scriptLines: 'L119-121' },
            { id: 'subtitle',     type: 'auto', autoDelayMs: 200, cue: null, wait: null, scriptLines: 'L121' },
          ],
        },
        { id: 4, title: '封 IP + proxy', duration: 13, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L125-133' }] },
      ],
    },
    {
      id: 5, name: 'legacy', narrative: '天真→prompt→我錯了→838行→debug→第一件學到',
      steps: [
        { id: 1, title: '結果我錯了', duration: 14, punchline: true, motifs: ['crash-line'], climax: ['A', 'C'],
          beats: [
            { id: 'kicker',            type: 'click', cue: '我那時候還很天真、覺得——', wait: null,    scriptLines: 'L141' },
            { id: 'prompt-box',        type: 'click', cue: '不如我丟一句『幫我寫一個訓練 AI 解數獨的程式』給 Claude？', wait: null, scriptLines: 'L143' },
            { id: 'placeholder-frame', type: 'click', cue: '⋯⋯', wait: '1s 留白', scriptLines: 'L145' },
            { id: 'crash-fill',        type: 'click', cue: '結果我錯了', wait: '2s 觀眾消化', climax: ['A', 'C'], scriptLines: 'L145-147' },
          ],
        },
        { id: 2, title: '838 行單檔',     duration: 8,  beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L151' }] },
        { id: 3, title: 'debug 爆炸',     duration: 7,  beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L153' }] },
        { id: 4, title: '第一件學到',     duration: 15, polish: true, motifs: [], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L157-163' }] },
      ],
    },
    {
      id: 6, name: 'sb3', narrative: '我又錯了→套皮仔→新女生→曲線→卡平段→備胎★★★→偷吃步',
      steps: [
        { id: 1, title: '我又錯了', duration: 11, punchline: true, motifs: ['crash-line'], climax: ['A', 'C'],
          beats: [
            { id: 'kicker',            type: 'click', cue: '正當我以為成了套皮仔...', wait: null, scriptLines: 'L171' },
            { id: 'placeholder-frame', type: 'click', cue: '⋯⋯', wait: '0.8s', scriptLines: 'L173' },
            { id: 'crash-fill',        type: 'click', cue: '我又錯了', wait: '1-2s', climax: ['A', 'C'], scriptLines: 'L173' },
          ],
        },
        { id: 2, title: '套皮仔策略',   duration: 9,  beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L167-177' }] },
        { id: 3, title: '新女生加分',   duration: 12, motifs: ['girl-new'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L181-185' }] },
        { id: 4, title: '曲線爬升',     duration: 10, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L181' }] },
        { id: 5, title: '卡平段',       duration: 12, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L187' }] },
        { id: 6, title: '備胎 ★★★',     duration: 12, punchline: true, starLevel: 3, motifs: ['red-stamp'], climax: ['A', 'B', 'C', 'G'],
          beats: [
            { id: 'flash',                   type: 'click', cue: '結果後面開始遇到瓶頸——AI 只拿那些必拿的固定分數就不思進取了...', wait: '0.5s', scriptLines: 'L189' },
            { id: 'subtitle-and-placeholder', type: 'click', cue: '換句話說、這個女生只把你當——', wait: '1-2s 留懸念', scriptLines: 'L189' },
            { id: 'bei-tai-fill',            type: 'click', cue: '備胎', wait: '3-4s 笑聲', climax: ['A', 'B', 'C', 'G'], scriptLines: 'L189' },
          ],
        },
        { id: 7, title: '偷吃步',       duration: 7, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L195-199' }] },
      ],
    },
    {
      id: 7, name: 'reasoner', narrative: '重寫→顛倒→13招→舊vs新→Action擴增→機率0→老油條★★★→死結',
      steps: [
        { id: 1, title: '重寫宣告',    duration: 11, polish: true, motifs: ['screen-shake'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L201-205' }] },
        { id: 2, title: '顛倒驗證',    duration: 14, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L201-205' }] },
        { id: 3, title: '13 招階梯',   duration: 19, motifs: ['13-stairs'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L209-211' }] },
        { id: 4, title: '舊 vs 新',    duration: 17, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L215-225' }] },
        { id: 5, title: 'Action 擴增', duration: 13, motifs: ['sudoku-board'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L229-233' }] },
        { id: 6, title: '機率 0',      duration: 16, punchline: true, motifs: ['red-stamp'], climax: ['A', 'B', 'C'],
          beats: [
            { id: 'count-up',            type: 'click', cue: '結果呢——練了兩千多萬次...', wait: '0.5s', scriptLines: 'L237' },
            { id: 'subtitle-placeholder', type: 'click', cue: '完整解出一道題的機率還是——', wait: '1-2s 留懸念', scriptLines: 'L237' },
            { id: 'zero-drop',           type: 'click', cue: '零', wait: '2-3s 嘆息/笑聲', climax: ['A', 'B', 'C'], scriptLines: 'L237' },
          ],
        },
        { id: 7, title: '老油條 ★★★',  duration: 26, punchline: true, starLevel: 3, motifs: ['girl-veteran', 'yellow-highlight'], climax: ['A', 'G', 'B'],
          beats: [
            { id: 'hero',             type: 'click', cue: '這個感覺就是、你剛開始學習如何跟女生互動...', wait: '0.5s', scriptLines: 'L241' },
            { id: 'trap-1',           type: 'click', cue: '但是那些女生都是老油條...例如——和你媽一起掉進水裡你會先救誰？', wait: '2s 觀眾笑', scriptLines: 'L243-247' },
            { id: 'trap-2-question',  type: 'click', cue: '每道都是陷阱題。舉個例子，『你覺得我該不該去運動？』', wait: '1s', scriptLines: 'L249-251' },
            { id: 'answer-a-fill',    type: 'click', cue: '你回答要去運動——那就是你嫌那個女生胖', wait: '2s 笑點', climax: ['A', 'G'], scriptLines: 'L253-255' },
            { id: 'answer-b-fill',    type: 'click', cue: '你回答不用去運動——那就是你不關心那個女生的身體健康', wait: '2s 笑點', climax: ['A', 'G'], scriptLines: 'L255-257' },
            { id: 'both-flash',       type: 'auto', autoDelayMs: 400, cue: null, wait: null, climax: ['B', 'B'], scriptLines: 'L257' },
          ],
        },
        { id: 8, title: '死結',        duration: 20, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L265-269' }] },
      ],
    },
    {
      id: 8, name: 'apprentice', narrative: '反向思考→3格空→3→10動畫→+20→+50→光講不夠看→visualizer按鈕',
      steps: [
        { id: 1, title: '反向思考',          duration: 10, polish: true, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L273-275' }] },
        { id: 2, title: '3 格空',            duration: 12, motifs: ['sudoku-board'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L277-279' }] },
        { id: 3, title: '反向課程動畫',      duration: 12, motifs: ['sudoku-board'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L281-285' }] },
        { id: 4, title: '+20 → +50 翻牌',    duration: 10, motifs: ['flip-20-to-50'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L287-291' }] },
        { id: 5, title: '光講不夠看',        duration: 9,  beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L297-299' }] },
        { id: 6, title: 'visualizer 按鈕',  duration: 10, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L299' }] },
      ],
    },
    {
      id: 9, name: 'callback', narrative: 'tensorboard→金句→RL=→飛機鳥→戀愛a→4考題→plasticity→三欄→機制→MBTI→警語★★→祝福→電費小偷★★★',
      steps: [
        { id: 1, title: 'tensorboard + 磨合期', duration: 12, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L303-307' }] },
        { id: 2, title: '核心金句',             duration: 14, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L309' }] },
        { id: 3, title: 'RL 對等',              duration: 12, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L313-317' }] },
        { id: 4, title: '飛機 + 鳥',            duration: 10, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L319' }] },
        { id: 5, title: '戀愛 a callback', duration: 18, punchline: true, motifs: ['girl-new'], climax: ['A', 'C'],
          beats: [
            { id: 'bg-callback',    type: 'click', cue: '追一個人的時候——', wait: null, scriptLines: 'L323' },
            { id: 'left-positive',  type: 'click', cue: '對方回訊息你就被加分', wait: '1s', scriptLines: 'L325' },
            { id: 'right-negative', type: 'click', cue: '已讀不回你就被扣分', wait: '1.5s', scriptLines: 'L325' },
            { id: 'punchline-hero', type: 'click', cue: '你的大腦根據這些 reward 反覆重塑要不要繼續當舔狗的判斷——跟 AI 訓練', wait: '2s', climax: ['A', 'C'], scriptLines: 'L327-329' },
          ],
        },
        { id: 6, title: '戀愛 b 4 考題',        duration: 18, motifs: ['girl-veteran'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L333-343' }] },
        { id: 7, title: 'plasticity 引出',      duration: 8,  beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L347-349' }] },
        { id: 8, title: 'plasticity 三欄',      duration: 12, motifs: ['13-stairs'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L351' }] },
        { id: 9, title: 'plasticity 機制',      duration: 12, motifs: ['flip-20-to-50', 'yellow-highlight'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L353-355' }] },
        { id: 10, title: 'MBTI + 業務工作',     duration: 22, composite: true, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L359-365' }] },
        { id: 11, title: '警語 ★★', duration: 18, punchline: true, starLevel: 2, motifs: ['crash-line'], climax: ['A', 'C', 'G'],
          beats: [
            { id: 'kicker-and-frame', type: 'click', cue: '所以遇到不會回答的魔王陷阱題沒有關係...', wait: '1s', scriptLines: 'L367' },
            { id: 'subtitle',         type: 'click', cue: '但是不要停滯不前——', wait: '1s', scriptLines: 'L369' },
            { id: 'warn-line-a-fill', type: 'click', cue: '跟一個女生聊天、結果——人生第一次的外向', wait: '1-1.5s', scriptLines: 'L369' },
            { id: 'warn-line-b-fill', type: 'click', cue: '換來一輩子的內向', wait: '3-4s', climax: ['A', 'C', 'G'], scriptLines: 'L369' },
          ],
        },
        { id: 12, title: '職場祝福',            duration: 12, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L371-373' }] },
        { id: 13, title: '電費小偷 ★★★', duration: 28, punchline: true, starLevel: 3, motifs: ['boom-double-ring', 'red-stamp', 'yellow-highlight'], climax: ['A', 'B', 'C', 'G'],
          beats: [
            { id: 'kicker',            type: 'click', cue: '最後再補個笑話——', wait: '1s', scriptLines: 'L375' },
            { id: 'salary-thief',      type: 'click', cue: '想必大家未來出職場後都是薪水小偷...', wait: '1.5-2s', scriptLines: 'L375' },
            { id: 'power-thief-fill',  type: 'click', cue: '但我不一樣、我是——電費小偷', wait: '5-7s 大笑', climax: ['A', 'B', 'C', 'G'], scriptLines: 'L375' },
            { id: 'footer-and-end',    type: 'click', cue: '我這兩個月一直用班上的電腦瘋狂訓練我的 AI', wait: '5s+', scriptLines: 'L375' },
          ],
        },
      ],
    },
  ],
};

// Flatten beats for indexed advance/retreat
export function flattenBeats(manifestRoot = manifest) {
  const flat = [];
  for (const ch of manifestRoot.chapters) {
    for (const step of ch.steps) {
      for (const beat of step.beats) {
        flat.push({ chapterId: ch.id, stepId: step.id, beatId: beat.id, beat, step, chapter: ch });
      }
    }
  }
  return flat;
}
