#!/usr/bin/env node
// Browser capture with Playwright: turns a shot list into a crisp, deterministic frame sequence.
//
//   node capture.mjs shots.json [more-shots.json ...]
//
// Shot list (JSON):
//   {
//     "name": "board",                     // output folder: clips/<name>/
//     "url": "demo-app/index.html",        // file path (relative to the shot list) or http(s) URL
//     "viewport": { "width": 980, "height": 551 },
//     "scale": 2,                          // device pixel ratio, 2 = sharp when shown at 1.4x
//     "steps": [
//       { "snap": 0.5 },                                  // hold the current frame (seconds)
//       { "move": "#new" },                               // glide the cursor to an element
//       { "click": "#new", "hold": 0.2 },                 // click (shows a ripple)
//       { "type": "#title", "text": "Hello", "per": 0.05 },
//       { "press": "#title", "key": "Enter", "hold": 0.4 },
//       { "drag": "#card", "to": "[data-col=done]", "dy": -80, "steps": 16 },  // drop point = target centre + dx/dy
//       { "scroll": 300, "steps": 10 },
//       { "mark": "added" },                              // named time marker for syncing the video
//       { "wait": 300 }                                   // wait ms without capturing (for real apps)
//     ]
//   }
//
// Output: clips/<name>/f0000.png … and clips/<name>/frames.json { viewport, frames:[{file,dur}], marks:{name:seconds} }
// Real apps: only record your own product or test accounts. Don't automate sites whose terms forbid it.
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import url from 'node:url';

const CURSOR = `
(() => {
  const add = () => {
    if (document.getElementById('__pw_cursor')) return;
    const s = document.createElement('div');
    s.innerHTML = '<svg id="__pw_cursor" viewBox="0 0 24 24" style="position:fixed;left:0;top:0;width:24px;height:24px;z-index:2147483647;pointer-events:none;transform:translate(-100px,-100px)"><path d="M4 2l6.5 19 2.4-7.8 7.8-2.4z" fill="#18181B" stroke="#fff" stroke-width="1.4" stroke-linejoin="round"/></svg>'
      + '<div id="__pw_ripple" style="position:fixed;left:0;top:0;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;border:3px solid rgba(47,69,255,.65);z-index:2147483646;pointer-events:none;opacity:0"></div>';
    document.documentElement.append(...s.childNodes);
  };
  window.__pwCursor = (x, y) => { add(); document.getElementById('__pw_cursor').style.transform = 'translate(' + x + 'px,' + y + 'px)'; };
  window.__pwRipple = (x, y, k) => { add(); const r = document.getElementById('__pw_ripple'); r.style.left = x + 'px'; r.style.top = y + 'px'; r.style.opacity = String(1 - k); r.style.transform = 'scale(' + (0.5 + k) + ')'; };
})();`;

const browser = await chromium.launch();
const files = process.argv.slice(2);
if (!files.length) { console.error('Usage: node capture.mjs shots.json [...]'); process.exit(1); }

for (const file of files) {
  const shot = JSON.parse(fs.readFileSync(file, 'utf8'));
  const base = path.dirname(path.resolve(file));
  const target = /^https?:/.test(shot.url) ? shot.url : url.pathToFileURL(path.resolve(base, shot.url)).href;
  const dir = path.resolve(base, 'clips', shot.name);
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });

  const ctx = await browser.newContext({ viewport: shot.viewport, deviceScaleFactor: shot.scale ?? 2 });
  await ctx.addInitScript(CURSOR);
  const page = await ctx.newPage();
  await page.goto(target, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts && document.fonts.ready);

  const frames = [], marks = {};
  let t = 0, n = 0;
  let cur = { x: shot.viewport.width * 0.8, y: shot.viewport.height * 0.85 };
  const snap = async (dur) => {
    const f = `f${String(n++).padStart(4, '0')}.png`;
    await page.screenshot({ path: path.join(dir, f) });
    frames.push({ file: f, dur }); t += dur;
  };
  const setCursor = async (x, y) => { cur = { x, y }; await page.evaluate(([a, b]) => window.__pwCursor(a, b), [x, y]); };
  const center = async (sel) => { const b = await page.locator(sel).first().boundingBox(); return { x: b.x + b.width / 2, y: b.y + b.height / 2 }; };
  const glide = async (to, steps = 10, per = 0.035, mouse = true) => {
    const from = { ...cur };
    for (let i = 1; i <= steps; i++) {
      const k = i / steps, e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      const x = from.x + (to.x - from.x) * e, y = from.y + (to.y - from.y) * e;
      await setCursor(x, y);
      if (mouse) await page.mouse.move(x, y);
      await snap(per);
    }
  };
  const ripple = async () => { for (const k of [0, .35, .7, 1]) { await page.evaluate(([x, y, k]) => window.__pwRipple(x, y, k), [cur.x, cur.y, k]); await snap(0.04); } };

  await setCursor(cur.x, cur.y);
  for (const s of shot.steps) {
    if ('snap' in s) await snap(s.snap);
    else if ('mark' in s) marks[s.mark] = +t.toFixed(3);
    else if ('wait' in s) await page.waitForTimeout(s.wait);
    else if ('move' in s) await glide(await center(s.move), s.steps ?? 10, s.per ?? 0.035);
    else if ('click' in s) {
      const c = await center(s.click);
      if (Math.hypot(c.x - cur.x, c.y - cur.y) > 4) await glide(c, s.steps ?? 10);
      await page.mouse.click(c.x, c.y); await ripple(); await snap(s.hold ?? 0.15);
    }
    else if ('type' in s) { for (const ch of s.text) { await page.locator(s.type).first().press(ch === ' ' ? 'Space' : ch); await snap(s.per ?? 0.05); } }
    else if ('press' in s) { await page.locator(s.press).first().press(s.key); await snap(s.hold ?? 0.3); }
    else if ('drag' in s) {
      const a = await center(s.drag), b = await center(s.to);
      if (Math.hypot(a.x - cur.x, a.y - cur.y) > 4) await glide(a, 8);
      await page.mouse.down(); await snap(0.12);
      await glide({ x: b.x + (s.dx ?? 0), y: b.y + (s.dy ?? 0) }, s.steps ?? 16, s.per ?? 0.04);
      await page.mouse.up(); await snap(s.hold ?? 0.3);
    }
    else if ('scroll' in s) { const k = s.steps ?? 10; for (let i = 0; i < k; i++) { await page.mouse.wheel(0, s.scroll / k); await page.waitForTimeout(30); await snap(s.per ?? 0.05); } }
  }
  fs.writeFileSync(path.join(dir, 'frames.json'), JSON.stringify({ viewport: shot.viewport, scale: shot.scale ?? 2, frames, marks, length: +t.toFixed(3) }, null, 1));
  console.log(`${shot.name}: ${frames.length} frames · ${t.toFixed(2)}s · marks ${JSON.stringify(marks)}`);
  await ctx.close();
}
await browser.close();
