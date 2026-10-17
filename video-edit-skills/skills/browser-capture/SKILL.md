---
name: browser-capture
description: "Record a product walkthrough by driving a real browser with Playwright from a JSON shot list, then fit the footage to a voiceover and compose it into a branded video. Use when someone asks for a product demo, feature walkthrough, onboarding clip or 'record my app'."
license: MIT
---

# Browser capture → product video

You drive the browser; the person never has to screen-record. Output is crisp (2× pixel density), deterministic and easy to redo.

## 1. Agree the walkthrough

Ask:

1. **URL:** a local file, `http://localhost:…` or a staging URL.
2. **Account:** a test or demo account with fake data only. Never record real customer data, and never type real passwords into a shot list.
3. **The story:** the 3 to 6 actions to show, in order (for example "create a task, move it to Done, share the board").
4. **Length and aspect:** 30 to 60s, 16:9 (default) or 9:16.

Only record products the person owns or is allowed to record. Don't automate third-party sites whose terms forbid automation.

## 2. Write the shot list

Create `capture/<name>.shots.json` (copy `capture/board.shots.json`):

| Step | Example | Notes |
|---|---|---|
| `snap` | `{ "snap": 0.8 }` | Hold the frame (seconds). Start and end with a hold. |
| `move` | `{ "move": "#new", "steps": 18, "per": 0.05 }` | Cursor glides with easing. |
| `click` | `{ "click": "#share", "hold": 0.6 }` | Glides there first, shows a ripple. |
| `type` | `{ "type": "#title", "text": "Hello", "per": 0.08 }` | One frame per key. |
| `press` | `{ "press": "#title", "key": "Enter", "hold": 1 }` | |
| `drag` | `{ "drag": "#card", "to": "[data-col=done]", "dy": -90 }` | Mouse down → glide → up. |
| `scroll` | `{ "scroll": 400, "steps": 12 }` | |
| `mark` | `{ "mark": "drag" }` | Named timestamp. Use it to split clips and sync captions and agent steps. |
| `wait` | `{ "wait": 500 }` | Waits for real apps without adding frames. |

Tips:

- Prefer stable selectors (`data-testid`, ids, roles) over CSS that changes with styling.
- Pace for viewers: about 0.08s per typed character and 0.6 to 1s holds after anything changes. It's easier to speed footage up than to slow it down.
- Viewport `980×551` at `scale: 2` looks sharp inside a 16:9 frame. Use `390×844` for a phone.

## 3. Record

```bash
node capture/capture.mjs capture/<name>.shots.json
```

This writes `capture/clips/<name>/` (PNG frames plus `frames.json` with durations and marks). Look at 3 or 4 frames before moving on: check the cursor position, that the app is in the right state, and that there's no stray text selection.

## 4. Fit to the voiceover and compose

- Cut and retime segments: `python3 capture/clip_to_video.py capture/clips/<name> media/a.mp4 --from navigate --to drag --duration 7.5`
- `demos/browser-demo/build.py` already does this per voiceover line: segment A plays during line 3, segment B during line 4, and the agent step list ticks at each mark.
- Scene ideas: punch in on where the action is, pull back for the result, and keep one caption per sentence.

## 5. Check and render

`python3 build.py && npm run check`, then snapshot 4 frames, then `npm run render`. Renders stay local.
