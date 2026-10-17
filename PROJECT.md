# agenticvideo: project overview

## The idea

Product demo videos are slow to make. Someone screen-records, re-records when they misclick, edits in a timeline tool, adds captions by hand, and redoes it all when the UI changes.

This project lets an AI coding agent do the whole thing:

1. **It drives the product.** Playwright controls a real Chromium browser from a JSON shot list (click, type, drag, scroll), with a visible cursor and click ripples.
2. **It films deterministically.** Every step is captured as sharp 2× frames with exact timings, so a re-take is one command.
3. **It edits in code.** HyperFrames turns HTML, CSS and GSAP into video. The template adds an agent step panel that ticks as the browser acts, camera punch-ins and pull-backs, captions and brand tokens.
4. **It follows your voice.** Record the script in one take. The splitter finds the line breaks, times captions to your words, and the scenes stretch to match.

When the UI changes, update the shot list and re-run. No re-editing.

## Showcase: "Product demos, recorded by an agent"

`demos/browser-demo/` is a ~32-second 16:9 video in which the agent records a walkthrough of a sample task-board app:

| Beat | On screen | Technique |
|---|---|---|
| Hook | "Your demo, recorded by an agent." | Kinetic caption slam |
| Prompt | The instruction being typed | Typed prompt |
| Browser control | Agent step list ticking beside the live browser capture | Playwright capture |
| Polish | Zoom on the drag into Done, pull back for the share toast | Camera punch-in, pull-back reveal |
| Brand | `brand.json` accent swapped; preview updates | Strikethrough replace |
| How it works | Shot list → Playwright → HyperFrames | Storyboard deck |
| CTA | "Point it at your product." | Calm title card |

`demos/effects-reel/` shows all 31 motion effects in one design system and is the reference for adding more motion to a product video.

## How a video is made

```
 brand/brand.json ───────────────────────────────┐
 capture/<slug>.shots.json ─▶ capture.mjs ─▶ clips/<slug>/ (frames + marks)
                                                   │
 videos/<slug>/script.json ─▶ voice (vo/*.wav) ─▶ build.py ─▶ index.html ─▶ npm run render ─▶ MP4
                                                   ▲
                           clip_to_video.py fits each segment to its voiceover line
```

## Design system (default)

- **Palette:** Cloud Dancer base (Pantone's 2026 Color of the Year), near-black ink, one cobalt accent, an orange-red signal colour for corrections.
- **Type:** Instrument Serif for display, Geist for UI, Geist Mono for code and commands.
- **Rules:** no emoji, glow or gradient blobs; one accent per frame; motion only where it explains something.

All of it can be overridden per brand in `brand/brand.json`.

## Principles

- **Plug and play:** one setup script, one playbook (`AGENTS.md`), and any agent can run it.
- **Local first:** capture and render on your machine, with no uploads.
- **Safe by default:** demo data only, no credentials in shot lists, and only automate what you're allowed to.
- **Reproducible:** the same inputs produce the same frames.

## Roadmap ideas

- 9:16 template for reels and shorts
- Auto-generated shot lists from a URL plus a sentence
- Multi-clip timelines (several flows in one video)
- Background music bed with automatic ducking under the voice

## Credits

HyperFrames (HeyGen), Playwright (Microsoft), GSAP, Instrument Serif and Geist (SIL OFL), and the community `content-skills` skill (MIT). See `THIRD_PARTY_NOTICES.md`.
