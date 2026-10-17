#!/usr/bin/env python3
"""Turn a captured frame sequence into an MP4 segment.

  python3 clip_to_video.py clips/board out.mp4 [--from MARK|SECONDS] [--to MARK|SECONDS] [--duration SECONDS] [--fps 30]

--from/--to cut a segment using the marks written by capture.mjs (or plain seconds).
--duration stretches or squeezes that segment to an exact length so it fits a voiceover line.
"""
import argparse, json, pathlib, subprocess, tempfile

ap = argparse.ArgumentParser()
ap.add_argument('clip'); ap.add_argument('out')
ap.add_argument('--from', dest='a'); ap.add_argument('--to', dest='b')
ap.add_argument('--duration', type=float); ap.add_argument('--fps', type=int, default=30)
o = ap.parse_args()

clip = pathlib.Path(o.clip).resolve()
meta = json.load(open(clip / 'frames.json'))
marks = meta.get('marks', {})
def when(v, default):
    if v is None: return default
    return float(marks[v]) if v in marks else float(v)
a, b = when(o.a, 0.0), when(o.b, meta['length'])

# collect frames overlapping [a, b)
seg, t = [], 0.0
for f in meta['frames']:
    s, e = t, t + f['dur']; t = e
    lo, hi = max(s, a), min(e, b)
    if hi - lo > 1e-6:
        seg.append([f['file'], hi - lo])
if not seg:
    raise SystemExit('Empty segment: check --from/--to')
total = sum(d for _, d in seg)
k = (o.duration / total) if o.duration else 1.0
lst = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False)
for name, d in seg:
    lst.write(f"file '{clip / name}'\nduration {d * k:.4f}\n")
lst.write(f"file '{clip / seg[-1][0]}'\n"); lst.close()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst.name,
                '-vf', f'fps={o.fps},format=yuv420p', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium',
                '-movflags', '+faststart', '-an', o.out], check=True)
pathlib.Path(lst.name).unlink()
print(f'{o.out}: {a:.2f}–{b:.2f}s of {clip.name} → {total * k:.2f}s ({len(seg)} frames, x{1 / k:.2f} speed)')
