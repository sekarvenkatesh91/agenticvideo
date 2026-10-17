#!/usr/bin/env python3
"""Split one continuous voiceover recording into vo/s1.wav … sN.wav, one per script line.

Usage:  python3 split_voiceover.py <recording.mp3|wav> [script.json] [vo_dir] [--cuts 6.3,14.0,...]

How it finds the line breaks (best first):
  1. --cuts: you give the cut times in seconds (one fewer than the number of lines).
  2. Word alignment: if faster-whisper is installed (pip install faster-whisper), the recording is
     transcribed locally and each cut goes in the gap after the last word of each script line.
  3. Pauses only: ffmpeg's silencedetect plus word counts. Fine for most reads; check the printout.
Writes vo/timing.json (lead/tail = 0) so the video follows the recording exactly.
"""
import json, re, subprocess, sys, pathlib

args = [a for a in sys.argv[1:]]
manual = None
if '--cuts' in args:
    i = args.index('--cuts'); manual = [float(x) for x in args[i + 1].split(',')]; del args[i:i + 2]
src = args[0]
script = json.load(open(args[1] if len(args) > 1 else 'script.json'))
out = pathlib.Path(args[2] if len(args) > 2 else 'vo')
out.mkdir(parents=True, exist_ok=True)

def probe(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode())

total = probe(src)
log = subprocess.run(['ffmpeg', '-hide_banner', '-i', src, '-af', 'silencedetect=noise=-38dB:d=0.3', '-f', 'null', '-'],
                     capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
gaps = [((a + b) / 2, b - a) for a, b in zip(starts, ends) if 0.2 < a < total - 0.2]

words = [len(t.split()) for _, _, t in script]
cum, acc = [], 0
for w in words[:-1]:
    acc += w
    cum.append(acc / sum(words) * total)

NUM = {'0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine', '10': 'ten'}
def toks(s):
    s = s.lower().replace('.com', ' dot com').replace(':', ' colon ')
    return [NUM.get(w, w) for w in re.findall(r"[a-z0-9']+", s)]

def align_cuts():
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    import difflib, tempfile, os
    tmp = tempfile.mktemp(suffix='.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-ar', '16000', '-ac', '1', tmp], check=True)
    import soundfile as sf
    audio, _ = sf.read(tmp, dtype='float32'); os.remove(tmp)
    segs, _ = WhisperModel('base.en', device='cpu', compute_type='int8').transcribe(audio, word_timestamps=True)
    W = []
    for s in segs:
        for w in s.words:
            for tk in toks(w.word):
                W.append((tk, w.start, w.end))
    S, last = [], []
    for _, _, line in script:
        S += toks(line); last.append(len(S) - 1)
    m = difflib.SequenceMatcher(a=S, b=[x[0] for x in W], autojunk=False)
    amap = {}
    for blk in m.get_matching_blocks():
        for k in range(blk.size):
            amap[blk.a + k] = blk.b + k
    # sentence-level caption timings
    global CAPS
    CAPS, pos = [], 0
    for _, _, line in script:
        for sent in [x.strip() for x in re.split(r'(?<=[.?!])\s+', line) if x.strip()]:
            n = len(toks(sent)); a_i, b_i = pos, pos + n - 1; pos += n
            ja = next((amap[x] for x in range(a_i, b_i + 1) if x in amap), None)
            jb = next((amap[x] for x in range(b_i, a_i - 1, -1) if x in amap), None)
            if ja is not None and jb is not None:
                CAPS.append([round(W[ja][1], 3), round(W[jb][2], 3), sent])
    res = []
    for li in last[:-1]:
        j = next((amap[x] for x in range(li, -1, -1) if x in amap), None)
        if j is None or j + 1 >= len(W):
            return None
        res.append((W[j][2] + W[j + 1][1]) / 2)
    return res

CAPS = None
cuts = manual or align_cuts()
method = 'manual' if manual else ('word alignment' if cuts else 'pauses')
if cuts is None:
    cuts = []
lo = 0.0
for k, target in (enumerate(cum) if method == 'pauses' else []):
    remaining = len(cum) - k - 1
    options = [g for g in gaps if g[0] > lo + 0.5]
    options = options[:len(options) - remaining] if remaining else options
    if not options:
        sys.exit(f'Could not find a pause for line {k + 1}. Leave a clear pause (~0.5s) between lines and try again.')
    # nearest pause to the expected position; longer pauses win ties
    best = min(options, key=lambda g: abs(g[0] - target) - 0.6 * g[1])
    cuts.append(best[0]); lo = best[0]

bounds = [0.0] + cuts + [total]
for k, (sid, title, _) in enumerate(script):
    a, b = bounds[k], bounds[k + 1]
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-ss', f'{a:.3f}', '-to', f'{b:.3f}', '-ac', '1', '-ar', '44100', str(out / f'{sid}.wav')], check=True)
    print(f'{sid}  {a:6.2f} – {b:6.2f}s  ({b - a:4.1f}s)  {title}')
json.dump({'lead': 0, 'tail': 0, 'end_hold': 1.0, 'source': pathlib.Path(src).name}, open(out / 'timing.json', 'w'), indent=1)
if CAPS:
    json.dump(CAPS, open(out / 'captions.json', 'w'), indent=1)
    print(f'Wrote {out}/captions.json ({len(CAPS)} timed captions)')
print(f'Cut by {method}.')
print(f'Wrote {len(script)} clips to {out}/ and {out}/timing.json')
