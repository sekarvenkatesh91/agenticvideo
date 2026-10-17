# Agent instructions

This file is for any AI coding agent working in this repo (Claude Code, Cursor, Codex, Antigravity and others). Follow the phases in order. Don't render until the person has approved the script.

**Goal:** the person says *"make a product video of &lt;my app&gt;"* and gets an on-brand 16:9 (or 9:16) MP4. The agent records the product by driving a real browser with Playwright, then composes the footage with motion, captions and voice.

---

## Phase 0 · Setup (once per machine)

```bash
./scripts/setup.sh --with-align                 # macOS / Linux
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1 -WithAlign   # Windows
```

The setup script:

- checks Node 18+, FFmpeg and Python 3, and installs any that are missing where it can
- installs **Playwright + Chromium** in `capture/`
- prepares the pinned HyperFrames CLI and turns its telemetry off
- copies `skills/*` into `.claude/skills/`

`--with-align` adds local word alignment for one-take voiceovers; `--with-tts` adds a local guide voice. If a required tool can't be installed, tell the person exactly what to install and stop.

## Phase 1 · Brand (ask, don't guess)

- If `brand/brand.json` exists, summarise it in two lines and ask *"Use this brand, or update it?"*
- Otherwise follow `skills/brand-intake/SKILL.md`: two short rounds of questions, then write `brand/brand.json` and `skills/brand/SKILL.md`, and confirm the palette before moving on.
- Never invent logos or trademarks, and never imitate another company's branding.

## Phase 2 · Walkthrough and content

Follow `skills/browser-capture/SKILL.md` §1. Confirm:

- the product URL and a **test or demo account** (fake data only)
- the 3 to 6 actions to show
- the audience, platform, aspect ratio and length

If the video needs facts beyond the product itself, research them and keep sources in `videos/<slug>/research.md`. Leave out anything you can't source.

## Phase 3 · Script

Use `skills/content-skills/SKILL.md` and the brand skill's voice rules.

1. Write `videos/<slug>/script.json` as `[["s1","Hook","line"], …]`. The template expects 7 beats: hook, prompt, browser control (part 1), polish (part 2), brand, how it works, call to action.
2. Write `videos/<slug>/voiceover-script.md` with a timing window, word count and on-screen cue per line (about 150 words a minute), plus a plain copy-paste version.
3. **Wait for approval.**

## Phase 4 · Capture

```bash
./scripts/new-video.sh <slug>                      # creates videos/<slug>/ and capture/<slug>.shots.json
node capture/capture.mjs capture/<slug>.shots.json
```

- Edit the shot list for the real product (selectors, text, drag targets) and add `mark`s at each step the agent panel should tick.
- Check 3 or 4 frames from `capture/clips/<slug>/` before going on: cursor position, app state, no stray text selection.
- Never put real passwords in a shot list. Log in once, manually or with a test account, before capturing.

## Phase 5 · Build

In `videos/<slug>/build.py`, update the agent step list (`STEPS`) and the scene text to match the product. Keep the scene mechanics. Brand colours and fonts come from `brand/brand.json` automatically; don't hard-code them.

## Phase 6 · Voice and render

1. Voice, pick one:
   - **One recording of the whole script** (ElevenLabs, phone, studio): run `python3 scripts/split-voiceover.py <file> videos/<slug>/script.json videos/<slug>/vo`. It cuts between lines and writes word-timed captions. Check the printed cut times; fix any with `--cuts`.
   - **Line by line:** `s1.wav … s7.wav` into `vo/`.
   - **Guide voice:** `npx hyperframes@0.8.164 tts "<line>" -v am_michael -o vo/s1.wav`.
2. Run `cd videos/<slug> && CLIP=<slug> python3 build.py && npm run check`, then snapshot 4 frames and look at them.
3. Run `npm run render`. The output lands in `videos/<slug>/renders/`.

## Phase 7 · Hand-off

Give the person the MP4 path, the voiceover script path and a one-line list of anything you weren't able to do.

---

## House rules

- **Plain design:** no emoji in frames, no glow, no gradient blobs, no fake logos. Use one accent colour.
- **Plain copy:** none of "delve", "game-changer", "unleash", "elevate".
- **Privacy:** use demo data only. No customer data, credentials, tokens or internal URLs in shot lists, scripts, frames or commits.
- **Publishing:** never run `hyperframes publish`, `hyperframes cloud` or any upload command. Never create public repos, gists or links on the person's behalf.
- **Determinism:** animate only on the paused GSAP timeline (`tl`). No `setTimeout`, no CSS keyframe animations, no randomness at render time.
- **Respect sites:** only automate products the person owns or may record. Don't automate sites whose terms forbid it.
