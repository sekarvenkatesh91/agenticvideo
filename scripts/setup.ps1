# One-time setup for Windows. Usage: powershell -ExecutionPolicy Bypass -File scripts/setup.ps1 [-WithTts] [-WithAlign] [-GlobalSkills]
param([switch]$WithTts, [switch]$WithAlign, [switch]$GlobalSkills)
$ErrorActionPreference = "Stop"
$HF = "hyperframes@0.8.164"
$Root = Split-Path -Parent $PSScriptRoot
$Missing = $false
function Ok($m) { Write-Host "  OK  $m" -ForegroundColor Green }
function Warn($m) { Write-Host "  !   $m" -ForegroundColor Yellow }
function Fail($m) { Write-Host "  X   $m" -ForegroundColor Red; $script:Missing = $true }
function Has($c) { [bool](Get-Command $c -ErrorAction SilentlyContinue) }
function TryWinget($id) { if (Has winget) { winget install -e --id $id --silent --accept-package-agreements --accept-source-agreements | Out-Null; return $true }; return $false }

Write-Host "Checking tools"
if ((Has node) -and ([int]((node -p "process.versions.node.split('.')[0]")) -ge 18)) { Ok "Node $(node -v)" }
elseif (TryWinget "OpenJS.NodeJS.LTS") { Ok "Node installed (restart the terminal)" } else { Fail "Node 18+ not found. Install from https://nodejs.org" }
if (Has ffmpeg) { Ok "FFmpeg" } elseif (TryWinget "Gyan.FFmpeg") { Ok "FFmpeg installed (restart the terminal)" } else { Fail "FFmpeg not found. winget install Gyan.FFmpeg" }
$py = if (Has python) { "python" } elseif (Has py) { "py" } else { $null }
if ($py) { Ok "Python" } elseif (TryWinget "Python.Python.3.12") { Ok "Python installed (restart the terminal)"; $py = "python" } else { Fail "Python 3 not found. Install from https://python.org" }
if ($Missing) { Write-Host "`nInstall the missing tools above, then run this script again."; exit 1 }

Write-Host "Preparing HyperFrames ($HF)"
try { npx --yes $HF --version | Out-Null; Ok "CLI cached" } catch { Warn "Could not pre-fetch the CLI" }
try { npx --yes $HF telemetry disable | Out-Null; Ok "Telemetry off" } catch { Warn "Could not turn telemetry off" }

if ($WithTts) {
  try { & $py -m pip install --quiet kokoro-onnx soundfile; Ok "kokoro-onnx + soundfile" } catch { Warn "Could not install TTS packages. Record your own voice instead." }
}

if ($WithAlign) {
  try { & $py -m pip install --quiet faster-whisper soundfile; Ok "faster-whisper + soundfile" } catch { Warn "Could not install faster-whisper. split-voiceover.py will use pause detection." }
}
Write-Host "Installing browser capture (Playwright + Chromium)"
try { Push-Location (Join-Path $Root "capture"); npm install --silent | Out-Null; npx --yes playwright install chromium | Out-Null; Pop-Location; Ok "Playwright + Chromium ready" } catch { Pop-Location; Warn "Playwright install failed. Run: cd capture; npm install; npx playwright install chromium" }
Write-Host "Installing skills for agents"
$Dest = if ($GlobalSkills) { Join-Path $env:USERPROFILE ".claude\skills" } else { Join-Path $Root ".claude\skills" }
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
Get-ChildItem (Join-Path $Root "skills") -Directory | ForEach-Object {
  $t = Join-Path $Dest $_.Name; if (Test-Path $t) { Remove-Item $t -Recurse -Force }
  Copy-Item $_.FullName $t -Recurse; Ok "$($_.Name) -> $Dest"
}
if (Test-Path (Join-Path $Root "brand\brand.json")) { Ok "Brand file found" } else { Warn "No brand yet. Your agent will ask a few questions first (see AGENTS.md)." }
Write-Host "Done. Open your agent in this folder and say: make a video about <topic>."
