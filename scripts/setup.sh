#!/usr/bin/env bash
# One-time setup: checks tools, warms the pinned HyperFrames CLI, installs skills for agents.
# Usage: bash scripts/setup.sh [--with-tts] [--with-align] [--global-skills]
set -euo pipefail

HF="hyperframes@0.8.164"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WITH_TTS=0; GLOBAL=0; WITH_ALIGN=0
for a in "$@"; do
  case "$a" in
    --with-tts) WITH_TTS=1 ;;
    --global-skills) GLOBAL=1 ;;
    --with-align) WITH_ALIGN=1 ;;
    -h|--help) sed -n '2,3p' "$0"; exit 0 ;;
  esac
done

ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$1"; }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; MISSING=1; }
MISSING=0
OS="$(uname -s)"

try_install() { # $1 = package name
  if [ "$OS" = "Darwin" ] && command -v brew >/dev/null; then brew install "$1" >/dev/null && return 0; fi
  if command -v apt-get >/dev/null && [ "$(id -u)" = 0 ]; then apt-get update -qq && apt-get install -y -qq "$1" >/dev/null && return 0; fi
  return 1
}

echo "Checking tools"
if command -v node >/dev/null && [ "$(node -p 'process.versions.node.split(".")[0]')" -ge 18 ]; then ok "Node $(node -v)"
else
  if try_install node; then ok "Node installed"; else fail "Node 18+ not found. Install it from https://nodejs.org"; fi
fi
if command -v ffmpeg >/dev/null; then ok "FFmpeg"
else
  if try_install ffmpeg; then ok "FFmpeg installed"; else fail "FFmpeg not found. macOS: brew install ffmpeg · Ubuntu: sudo apt install ffmpeg"; fi
fi
if command -v python3 >/dev/null; then ok "Python $(python3 -V | cut -d' ' -f2)"; else fail "Python 3 not found. Install it from https://python.org"; fi

if [ "$MISSING" = 1 ]; then echo; echo "Install the missing tools above, then run this script again."; exit 1; fi

echo "Preparing HyperFrames ($HF)"
npx --yes "$HF" --version >/dev/null 2>&1 && ok "CLI cached" || warn "Could not pre-fetch the CLI (it will download on first render)"
npx --yes "$HF" telemetry disable >/dev/null 2>&1 && ok "Telemetry off" || warn "Could not turn telemetry off"
npx --yes "$HF" doctor >/dev/null 2>&1 && ok "Doctor passed" || warn "hyperframes doctor reported optional items missing (usually fine)"

if [ "$WITH_TTS" = 1 ]; then
  echo "Installing local text-to-speech (guide voice)"
  PIP="python3 -m pip install --quiet kokoro-onnx soundfile"
  if $PIP 2>/dev/null || $PIP --user 2>/dev/null || $PIP --break-system-packages 2>/dev/null; then ok "kokoro-onnx + soundfile"
  else warn "Could not install TTS packages. Record your own voice instead (see AGENTS.md)."; fi
fi

if [ "$WITH_ALIGN" = 1 ]; then
  echo "Installing word alignment (splits one long recording, times captions)"
  PIP="python3 -m pip install --quiet faster-whisper soundfile"
  if $PIP 2>/dev/null || $PIP --user 2>/dev/null || $PIP --break-system-packages 2>/dev/null; then ok "faster-whisper + soundfile"
  else warn "Could not install faster-whisper. split-voiceover.py will fall back to pause detection."; fi
fi

echo "Installing browser capture (Playwright + Chromium)"
if (cd "$ROOT/capture" && npm install --silent >/dev/null 2>&1 && npx --yes playwright install chromium >/dev/null 2>&1); then ok "Playwright + Chromium ready"
else warn "Playwright install failed. Run: cd capture && npm install && npx playwright install chromium"; fi

echo "Installing skills for agents"
DEST="$ROOT/.claude/skills"; [ "$GLOBAL" = 1 ] && DEST="$HOME/.claude/skills"
mkdir -p "$DEST"
for d in "$ROOT"/skills/*/; do
  name="$(basename "$d")"; rm -rf "${DEST:?}/$name"; cp -R "$d" "$DEST/$name"; ok "$name → ${DEST/#$HOME/~}"
done

echo
if [ -f "$ROOT/brand/brand.json" ]; then ok "Brand file found: brand/brand.json"; else warn "No brand yet. Your agent will ask a few questions first (see AGENTS.md)."; fi
echo "Done. Open your agent in this folder and say: make a video about <topic>."
