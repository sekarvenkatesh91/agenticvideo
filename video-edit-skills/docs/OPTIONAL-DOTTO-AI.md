# Optional: installing the dotto-ai skill

This pack does **not** include `dotto-ai`. Install it separately only if you need the features below.

## What it adds

| Feature | Without dotto-ai | With dotto-ai |
|---|---|---|
| Hook writing | `content-skills` hook beat | 3 scored hooks per reel (outlier score) |
| Structure | `content-skills` 60-second reel beats | 5-stage 30-second retention curve with a 0:18 re-hook |
| CTA | Generic save/share prompts | Keyword "comment-drop" CTA for DM automation |
| Production handoff | Manual | Beat sheet (time, visual, on-screen text, VO, SFX) that names effect components (`frame-break`, `pull-back-reveal`, `grade-split-reveal`, `caption-kinetic-slam`) |
| Safe margins | Not covered | Keeps text out of the bottom 20% / right 15% reel UI zones |

If you only need scripts, carousels or general hooks, `content-skills` is enough.

## Install

1. Get the `dotto-ai` skill from its original publisher. Check its license before using or redistributing it.
   <!-- TODO: add the verified source link here -->
2. Copy the folder (it contains a `SKILL.md`) into your skills directory:

   ```bash
   # macOS / Linux, global
   cp -r dotto-ai ~/.claude/skills/

   # or per project
   mkdir -p .claude/skills && cp -r dotto-ai .claude/skills/
   ```

   ```powershell
   # Windows
   Copy-Item -Path "dotto-ai" -Destination "$env:USERPROFILE\.claude\skills\" -Recurse -Force
   ```

3. Restart your AI assistant session, then ask for a reel script, e.g. *"Write a 30-second reel about X with a beat sheet."*

## Notes

- `dotto-ai` is a third-party skill. This repo is not affiliated with or endorsed by its author or any company of that name.
- Its component IDs match the files in `demo-project/compositions/components/`, so its beat sheets plug straight into the demo project.
