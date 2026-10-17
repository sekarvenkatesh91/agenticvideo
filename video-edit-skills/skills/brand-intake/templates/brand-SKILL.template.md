---
name: brand
description: "{{name}} brand rules: voice, palette, fonts and do/don't list. Load before writing copy, scripts or designing frames for {{name}}."
---

# {{name}} brand

**Audience:** {{audience}}
**Platforms:** {{platforms}}

## Voice

- Tone: {{tone_words}}
- Always: {{always}}
- Never: {{never}}
- Words to avoid: {{avoid_words}}

## Visual system

| Token | Hex | Use |
|---|---|---|
| paper | {{colors.paper}} | Background |
| ink | {{colors.ink}} | Text |
| accent | {{colors.accent}} | One highlight per frame |
| accent_soft | {{colors.accent_soft}} | Highlight fills |
| signal | {{colors.signal}} | Strike-throughs, warnings |

- Display font: {{fonts.display}} · Body: {{fonts.sans}} · Code/queries: {{fonts.mono}}
- Logo: {{logo}}

## Rules for every video

- Use one accent colour per frame. No emoji, glow or gradient blobs.
- Use example data only (example.com, sample names).
- Put the CTA in the last 8 seconds; at most one call to action.
- Compliance notes: {{compliance}}

The source of truth is `brand/brand.json`. When the brand changes, update that file and regenerate this skill.
