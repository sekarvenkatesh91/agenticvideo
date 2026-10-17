# video-edit-skills

**Product videos, recorded by an agent.** Tell your AI coding agent what to show. It drives a real browser with Playwright, captures every click and keystroke, and turns the footage into a branded 16:9 video with motion, captions and your voice. Everything is plain HTML, rendered locally with [HyperFrames](https://hyperframes.heygen.com).

```
prompt ─▶ shot list ─▶ Playwright capture ─▶ HyperFrames composition ─▶ MP4
                                   ▲ brand.json            ▲ your voiceover
```

## Quick start

```bash
git clone <repo-url> video-edit-skills && cd video-edit-skills
./scripts/setup.sh --with-align        # Windows: powershell -ExecutionPolicy Bypass -File scripts/setup.ps1 -WithAlign
```

Open Claude Code, Cursor, Codex or another agent in the folder and say:

> make a 30-second product video of my app at http://localhost:3000 — create a project, invite a teammate, share it

The agent follows [`AGENTS.md`](AGENTS.md):

1. **Brand.** It asks a few questions and writes `brand/brand.json`.
2. **Walkthrough.** It agrees the steps to show, using demo data only.
3. **Script.** It writes the script and voiceover script for your approval.
4. **Capture.** Playwright drives Chromium from a JSON shot list (`capture/capture.mjs`).
5. **Build.** HyperFrames composes the footage, an agent step panel, zooms, captions and your brand.
6. **Voice and render.** You record one take; it's split per line and captions are timed to your words.

## Try the demo

```bash
node capture/capture.mjs capture/board.shots.json     # records the sample "Boards" app
cd demos/browser-demo && python3 build.py && npm run render
```

`capture/demo-app/` is a small fictional task board, so the demo works offline.

## What's inside

| Path | What it is |
|---|---|
| `AGENTS.md` · `CLAUDE.md` | The playbook every agent follows |
| `capture/capture.mjs` | Playwright shot-list recorder (cursor, click ripples, drag, type, scroll, marks) |
| `capture/clip_to_video.py` | Cuts and retimes captured footage to fit a voiceover line |
| `capture/demo-app/` | Sample app for the demo |
| `demos/browser-demo/` | Product-video template: agent panel, live capture, punch-in and pull-back, brand swap |
| `demos/effects-reel/` | Reference reel: all 31 motion effects in one design system |
| `demo-project/compositions/components/` | The 31 original standalone effect components |
| `skills/browser-capture/` | How to plan, record and compose a walkthrough |
| `skills/brand-intake/` | Brand interview → `brand.json` + brand skill |
| `skills/content-skills/` | Script structures for short-form video |
| `scripts/` | `setup.sh`, `setup.ps1`, `new-video.sh`, `split-voiceover.py` |
| `brand/brand.example.json` | Brand token schema |

## Requirements

Node 18+, FFmpeg and Python 3. The setup script checks for them and installs Playwright + Chromium. Optional flags: `--with-align` installs faster-whisper for one-take voiceovers; `--with-tts` installs a local guide voice.

## Good to know

- Only record products you own or are allowed to record, using test accounts and fake data.
- Renders never leave your machine.
- See [`PROJECT.md`](PROJECT.md) for the full overview and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for credits.

## License

MIT for the original work here. Third-party parts keep their own licenses.
