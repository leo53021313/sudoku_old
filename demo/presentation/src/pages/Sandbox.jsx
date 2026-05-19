import { useRef, useState } from 'react';
import { motion } from 'motion/react';
import { GlobalGrain } from '../layers/GlobalGrain.jsx';
import { HalftoneBg } from '../layers/HalftoneBg.jsx';
import { ChapterTint } from '../layers/ChapterTint.jsx';
import { AmbientShapes } from '../layers/AmbientShapes.jsx';
import { Sticker } from '../components/Sticker.jsx';
import { Hero } from '../components/Hero.jsx';
import { BoomDoubleRing } from '../motifs/BoomDoubleRing.jsx';
import { CrashLine } from '../motifs/CrashLine.jsx';
import { RedStamp } from '../motifs/RedStamp.jsx';
import { YellowHighlight } from '../motifs/YellowHighlight.jsx';
import { SpotlightVignette } from '../motifs/SpotlightVignette.jsx';
import { HalftoneBurst } from '../motifs/HalftoneBurst.jsx';
import { ScreenShake } from '../motifs/ScreenShake.jsx';
import { GirlNew } from '../motifs/GirlNew.jsx';
import { GirlVeteran } from '../motifs/GirlVeteran.jsx';
import { ThirteenStairs } from '../motifs/ThirteenStairs.jsx';
import { FlipTwentyToFifty } from '../motifs/FlipTwentyToFifty.jsx';
import { SudokuBoard } from '../motifs/SudokuBoard.jsx';
import { SudokuBoardLive } from '../motifs/SudokuBoardLive.jsx';
import { NeuralNet } from '../motifs/NeuralNet.jsx';
import { CounterUp } from '../motifs/CounterUp.jsx';
import { useClimax } from '../climax/useClimax.js';

export function Sandbox() {
  const [chapterId, setChapterId] = useState(1);
  const [boomActive, setBoomActive] = useState(false);
  const [crashFilled, setCrashFilled] = useState(false);
  const [stampActive, setStampActive] = useState(false);
  const [highlightActive, setHighlightActive] = useState(false);
  const [neuralActive, setNeuralActive] = useState(true);
  const shakeRef = useRef(null);

  const climaxAC = useClimax(['A', 'C']);
  const climaxFull = useClimax(['A', 'B', 'C', 'G']);

  const triggerShake = () => shakeRef.current?.play();

  return (
    <ScreenShake ref={shakeRef}>
      <AmbientShapes chapterId={chapterId} />
      <GlobalGrain />
      <HalftoneBg />
      <ChapterTint chapterId={chapterId} />

      <SpotlightVignette active={climaxFull.activeFX.G || climaxAC.activeFX.G} />
      <HalftoneBurst active={climaxFull.activeFX.B || climaxAC.activeFX.B} />

      <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk', overflowY: 'auto', height: '100vh' }}>
        <h1 style={{ fontSize: '3rem', fontWeight: 900, margin: 0 }}>Sandbox · 風格驗證</h1>

        <section style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>Chapter palette (切換看 tint + ambient shapes)</h2>
          <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
            {[1,2,3,4,5,6,7,8,9].map(i => (
              <button key={i} onClick={() => setChapterId(i)}
                style={{ width: 40, height: 40, border: '3px solid #000',
                  background: chapterId === i ? '#FF6B6B' : '#fff', fontWeight: 900, fontFamily: 'inherit', cursor: 'pointer' }}>
                {i}
              </button>
            ))}
          </div>
        </section>

        <section style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>Sticker primitive</h2>
          <div style={{ display: 'flex', gap: 32, marginTop: 16, alignItems: 'flex-start', flexWrap: 'wrap' }}>
            <Sticker bg="accent" rotation={-3} shadow="lg" padding={24}>心 虛</Sticker>
            <Sticker bg="secondary" rotation={2}>期中報告</Sticker>
            <Sticker bg="muted" rotation={-5}>敬請期待</Sticker>
            <Sticker bg="cream" rotation={1} shadow="md">cream sticker</Sticker>
          </div>
        </section>

        <section style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>Motif Library — 4 full visual</h2>
          <div style={{ display: 'flex', gap: 24, marginTop: 16, alignItems: 'center' }}>
            <div>
              <BoomDoubleRing active={boomActive} size={120} />
              <button onClick={() => setBoomActive(v => !v)} style={btn}>BoomRing toggle</button>
            </div>
            <div>
              <CrashLine active filled={crashFilled} width={360} />
              <button onClick={() => setCrashFilled(v => !v)} style={btn}>CrashLine fill toggle</button>
            </div>
            <div>
              <RedStamp active={stampActive} rotation={-3} size="medium">受害者</RedStamp>
              <button onClick={() => setStampActive(v => !v)} style={btn}>RedStamp toggle</button>
            </div>
            <div>
              重新塑造 <YellowHighlight active={highlightActive}>關鍵字</YellowHighlight>
              <button onClick={() => setHighlightActive(v => !v)} style={btn}>YellowHighlight toggle</button>
            </div>
          </div>
        </section>

        <section style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>Climax FX (overlays + screen shake)</h2>
          <p style={{ marginTop: 8, fontSize: 14, fontWeight: 500, color: '#555' }}>
            A = screen shake · B = halftone burst (center flash) · C = overshoot scale on target sticker · G = spotlight vignette (edges darken)
          </p>
          <div style={{ display: 'flex', gap: 16, marginTop: 16, flexWrap: 'wrap', alignItems: 'center' }}>
            <button onClick={() => { climaxAC.play(); triggerShake(); }} style={btn}>輕量 A+C (shake + overshoot)</button>
            <button onClick={() => { climaxFull.play(); triggerShake(); }} style={btn}>★★★ 全套 A+B+C+G</button>
            <button onClick={() => { climaxAC.reset(); climaxFull.reset(); }} style={btn}>reset overlays</button>
            <motion.div
              animate={(climaxAC.activeFX.C || climaxFull.activeFX.C) ? { scale: [0.85, 1.4, 1.0, 0.95, 1.0] } : { scale: 1 }}
              transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
              style={{
                marginLeft: 16, padding: '12px 24px',
                background: '#FF6B6B', color: '#FFFDF5',
                border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
                fontFamily: 'Space Grotesk', fontWeight: 900, fontSize: 18,
              }}
            >
              C target
            </motion.div>
          </div>
        </section>

        <section style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>Motif shells (placeholders)</h2>
          <div style={{ display: 'flex', gap: 16, marginTop: 16, flexWrap: 'wrap' }}>
            <GirlNew />
            <GirlVeteran />
            <FlipTwentyToFifty />
          </div>
          <div style={{ display: 'flex', gap: 16, marginTop: 16, flexWrap: 'wrap' }}>
            <ThirteenStairs />
            <SudokuBoard />
          </div>
        </section>

        <section style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>NeuralNet (live)</h2>
          <div style={{ width: 480, height: 240, border: '4px solid #000', background: '#FFFDF5' }}>
            <NeuralNet active={neuralActive} />
          </div>
          <button onClick={() => setNeuralActive(v => !v)} style={btn}>NeuralNet toggle</button>
        </section>

        <section style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>SudokuBoardLive</h2>
          <SudokuBoardLive
            cells={[
              [5,3,4, 6,7,8, 9,1,2],
              [6,7,0, 1,9,5, 3,4,8],
              [1,9,8, 3,4,2, 5,6,7],
              [8,5,9, 7,6,1, 4,2,3],
              [4,2,6, 8,5,3, 7,9,1],
              [7,1,3, 9,2,4, 8,5,6],
              [9,6,1, 5,3,7, 2,8,4],
              [2,8,7, 4,1,9, 6,3,5],
              [3,4,5, 2,8,6, 1,7,9],
            ]}
            highlights={[[1,2]]}
            active
          />
        </section>

        <section style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>CounterUp</h2>
          <CounterUp from={20} to={50} prefix="+" duration={1200} />
        </section>

        <section style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>.anim-stagger-list (CSS utility)</h2>
          <ul className="anim-stagger-list" style={{ listStyle: 'none', padding: 0, marginTop: 16 }}>
            {['填', '消', '對', '錯', '快', '慢', '深', '淺'].map((t, i) => (
              <li key={i} style={{
                background: '#FFFDF5', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
                padding: '8px 16px', marginBottom: 8, fontWeight: 900, display: 'inline-block', marginRight: 8,
              }}>{t}</li>
            ))}
          </ul>
        </section>

        <section style={{ marginTop: 48 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>Hero primitive</h2>
          <div style={{ position: 'relative', height: 240, marginTop: 16, border: '4px solid #000', background: '#FFFDF5' }}>
            <Hero size="hero" stroke>訓 練 AI 解 數 獨</Hero>
          </div>
        </section>
      </main>
    </ScreenShake>
  );
}

const btn = {
  marginTop: 8, padding: '8px 16px', border: '3px solid #000', background: '#fff',
  fontFamily: 'Space Grotesk', fontWeight: 900, cursor: 'pointer',
};
