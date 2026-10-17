#!/usr/bin/env bash
# Start a new product video from the browser-demo template. Usage: ./scripts/new-video.sh <slug>
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SLUG="${1:-}"
[[ "$SLUG" =~ ^[a-z0-9][a-z0-9-]*$ ]] || { echo "Usage: $0 <slug>  (lowercase letters, numbers, dashes)"; exit 1; }
SRC="$ROOT/demos/browser-demo"
DST="$ROOT/videos/$SLUG"
[ -e "$DST" ] && { echo "videos/$SLUG already exists"; exit 1; }
mkdir -p "$DST/vo" "$DST/renders"
cp "$SRC"/{build.py,style.css,package.json,hyperframes.json} "$DST/"
cat > "$DST/script.json" <<'JSON'
[
 ["s1", "Hook", "Replace with your hook line."],
 ["s2", "Prompt", "Replace with what the viewer will see."],
 ["s3", "Browser control", "Replace with the first half of the walkthrough."],
 ["s4", "Polish", "Replace with the second half of the walkthrough."],
 ["s5", "Brand", "Replace with a line about your brand or product."],
 ["s6", "How it works", "Replace with the three-step summary."],
 ["s7", "CTA", "Replace with the call to action."]
]
JSON
sed "s/\"name\": \"board\"/\"name\": \"$SLUG\"/" "$ROOT/capture/board.shots.json" > "$ROOT/capture/$SLUG.shots.json"
sed -i.bak "s/browser-demo/$SLUG/g" "$DST/package.json" && rm -f "$DST/package.json.bak"
printf '# Research: %s\n\n| Fact | Source |\n|---|---|\n' "$SLUG" > "$DST/research.md"
echo "Created videos/$SLUG"
echo "Next:"
echo "  1. Edit capture/$SLUG.shots.json for your product, then: node capture/capture.mjs capture/$SLUG.shots.json"
echo "  2. Write videos/$SLUG/script.json and add your voice (one recording: python3 scripts/split-voiceover.py rec.mp3 videos/$SLUG/script.json videos/$SLUG/vo)"
echo "  3. cd videos/$SLUG && CLIP=$SLUG python3 build.py && npm run check && npm run render"
