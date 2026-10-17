---
name: brand-intake
description: "Interview the person about their brand, then write brand/brand.json and a reusable brand skill (skills/brand/SKILL.md). Use before making any video, post or design in this repo when no brand file exists, or when the person wants to change their brand."
license: MIT
---

# Brand intake

Collect just enough about the brand to make on-brand videos, then save it so no one has to answer these questions again.

## Round 1: identity (ask together, no more than 6)

1. **Name:** what should appear as the wordmark? (A person's name is fine.)
2. **Audience:** who is this for, in one line?
3. **Voice:** pick 3 words for the tone (for example: plain, warm, direct). Anything to avoid?
4. **Colours:** do you have brand hex codes? If not, say "default" (Cloud Dancer paper, near-black ink, cobalt accent) or name a mood and I'll propose a palette.
5. **Fonts:** do you have brand fonts on Google Fonts? If not, say "default" (Instrument Serif + Geist + Geist Mono).
6. **Logo:** is there a logo file I should use? If yes, put it in `brand/` and tell me the file name. If not, I'll use a text wordmark.

## Round 2: rules (only if Round 1 left gaps)

- Main platforms (LinkedIn, YouTube, Instagram, TikTok)?
- Things the brand always does (for example "always end with one clear takeaway")?
- Things the brand never does (for example "no stock-photo people", "no slang")?
- Words or claims that legal or compliance won't allow?
- Any sample post or video whose style the person likes? Describe it; don't copy it.

## Proposing a palette (when the person says "default" or gives a mood)

- Use one light base, one ink, one accent, one soft accent and one signal colour (for corrections and warnings).
- Check text contrast: ink on paper and white on accent must both be at least 4.5:1. If either fails, darken the accent.
- Show the five hex codes and ask "Use these?" before saving.

## Outputs

1. `brand/brand.json`, following the keys in `brand/brand.example.json`. Keep every key; use `null` when unknown.
2. `skills/brand/SKILL.md`, made from `templates/brand-SKILL.template.md` by filling every `{{…}}` placeholder. Remove lines whose value is empty.
3. Copy `skills/brand/` to `.claude/skills/brand/` (project) so other agents load it.
4. Show the person a short summary: name, the five colours, the fonts and three voice words.

## Rules

- Ask; don't guess. If an answer is unclear, ask one follow-up question.
- Never invent a logo or trademark, and never imitate another company's brand.
- Never store personal data beyond the brand name the person gives you.
