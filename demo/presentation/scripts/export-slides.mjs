#!/usr/bin/env node
// Export the click-driven presentation as a static PDF + PPTX.
// Walks every beat in beat-manifest, drives the running app via URL params,
// screenshots each beat at 1920x1080, then assembles the PNG sequence.

import { chromium } from 'playwright';
import { PDFDocument } from 'pdf-lib';
import pptxgen from 'pptxgenjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { manifest } from '../src/data/beat-manifest.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const OUT_DIR = path.join(ROOT, 'exports');
const PNG_DIR = path.join(OUT_DIR, 'pngs');

const BASE_URL = process.env.BASE_URL ?? 'http://localhost:4173/';
const VIEWPORT = { width: 1920, height: 1080 };

// Per-beat wait strategy. The single 'auto' beat (ch1/s8/b1) self-advances
// at 400ms — screenshot just before. Climax beats need extra time for
// stagger-list (up to 1440ms), climax FX (up to 1500ms), and spring settle.
const WAIT_AUTO_BEAT_MS = 350;
const WAIT_CLIMAX_MS = 3500;
const WAIT_DEFAULT_MS = 2500;

function pickWaitMs(beat) {
  if (beat.type === 'auto') return WAIT_AUTO_BEAT_MS;
  if (Array.isArray(beat.climax) && beat.climax.length > 0) return WAIT_CLIMAX_MS;
  return WAIT_DEFAULT_MS;
}

// Wait for fonts + all FINITE WAAPI animations to settle. Skipped for auto
// beats (they self-advance at 400ms; we have to take the shot at ~350ms).
// Infinite-iteration animations (GlobalGrain / HalftoneBg ambient layers)
// are filtered out — their `.finished` promise never resolves.
async function waitForSettle(page, isAuto) {
  if (isAuto) return;
  await page.evaluate(async () => {
    await document.fonts.ready;
    const anims = document.getAnimations().filter((a) => {
      const t = a.effect?.getTiming?.();
      const iters = t?.iterations;
      return iters !== Infinity && (typeof iters !== 'number' || iters < 1e6);
    });
    await Promise.race([
      Promise.all(anims.map((a) => a.finished.catch(() => undefined))),
      new Promise((r) => setTimeout(r, 4000)),
    ]);
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  });
}

function flatten() {
  const flat = [];
  for (const ch of manifest.chapters) {
    for (const step of ch.steps) {
      for (let bi = 0; bi < step.beats.length; bi++) {
        flat.push({ ch, step, beat: step.beats[bi], beatIdxInStep: bi });
      }
    }
  }
  return flat;
}

async function captureAll() {
  await fs.mkdir(PNG_DIR, { recursive: true });
  const flat = flatten();
  console.log(`[export] ${flat.length} beats to capture`);

  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    viewport: VIEWPORT,
    deviceScaleFactor: 1,
    reducedMotion: 'no-preference',
  });
  const page = await ctx.newPage();

  await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(800);

  const pngPaths = [];
  for (let i = 0; i < flat.length; i++) {
    const { ch, step, beat, beatIdxInStep } = flat[i];
    const url = `${BASE_URL}?ch=${ch.id}&step=${step.id}&beat=${beatIdxInStep}`;
    const filename =
      `${String(i + 1).padStart(3, '0')}_ch${ch.id}-s${step.id}-b${beatIdxInStep}_${beat.id}.png`;
    const fp = path.join(PNG_DIR, filename);

    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(pickWaitMs(beat));
    await waitForSettle(page, beat.type === 'auto');
    await page.screenshot({ path: fp, fullPage: false, type: 'png' });
    pngPaths.push(fp);
    console.log(`[export] ${i + 1}/${flat.length}  ${filename}`);
  }

  await browser.close();
  return pngPaths;
}

async function buildPdf(pngPaths) {
  console.log('[export] Building PDF...');
  const pdf = await PDFDocument.create();
  for (const fp of pngPaths) {
    const bytes = await fs.readFile(fp);
    const img = await pdf.embedPng(bytes);
    const page = pdf.addPage([VIEWPORT.width, VIEWPORT.height]);
    page.drawImage(img, { x: 0, y: 0, width: VIEWPORT.width, height: VIEWPORT.height });
  }
  const pdfBytes = await pdf.save();
  const pdfPath = path.join(OUT_DIR, 'presentation.pdf');
  await fs.writeFile(pdfPath, pdfBytes);
  console.log(`[export] PDF -> ${pdfPath} (${(pdfBytes.length / 1024 / 1024).toFixed(1)} MB)`);
}

async function buildPptx(pngPaths) {
  console.log('[export] Building PPTX...');
  const pptx = new pptxgen();
  pptx.defineLayout({ name: 'PRES_HD', width: 13.333, height: 7.5 });
  pptx.layout = 'PRES_HD';
  for (const fp of pngPaths) {
    const slide = pptx.addSlide();
    slide.addImage({ path: fp, x: 0, y: 0, w: 13.333, h: 7.5 });
  }
  const pptxPath = path.join(OUT_DIR, 'presentation.pptx');
  await pptx.writeFile({ fileName: pptxPath });
  console.log(`[export] PPTX -> ${pptxPath}`);
}

async function main() {
  const t0 = Date.now();
  const pngs = await captureAll();
  await buildPdf(pngs);
  await buildPptx(pngs);
  console.log(`[export] Done in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
