"""Browser-demo video: an agent drives a real browser with Playwright, and the footage is composed with
HyperFrames effects, brand tokens, captions and voiceover.  Run:  python3 build.py && npm run render

Inputs:  script.json (lines), vo/*.wav (voice), capture/clips/<name>/ (Playwright frames), brand/brand.json (optional)
"""
import json, re, html, os, subprocess, pathlib

W, H = 1920, 1080
HERE = pathlib.Path(__file__).parent
script = json.load(open('script.json'))
LEAD, TAIL, END_HOLD = 0.3, 0.3, 0.8
if os.path.exists('vo/timing.json'):            # written by split-voiceover.py for one continuous recording
    tm = json.load(open('vo/timing.json')); LEAD, TAIL, END_HOLD = tm.get('lead', 0), tm.get('tail', 0), tm.get('end_hold', 1.0)

def probe(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode())

HAS_VO, T, t = {}, {}, 0.0
for sid, title, text in script:
    wav = f'vo/{sid}.wav'; HAS_VO[sid] = os.path.exists(wav)
    d = LEAD + (probe(wav) if HAS_VO[sid] else len(text.split()) / 2.5 + .3) + TAIL
    if sid == script[-1][0]: d += END_HOLD
    T[sid] = (round(t, 3), round(d, 3)); t += d
TOTAL = round(t, 3)
S = {k: v[0] for k, v in T.items()}; D = {k: v[1] for k, v in T.items()}

# ---------- capture → video segments fitted to the voice ----------
def find_capture():
    for dd in [HERE.resolve(), *HERE.resolve().parents]:
        if (dd / 'capture' / 'capture.mjs').exists(): return dd / 'capture'
    raise SystemExit('capture/ folder not found: run from inside the repo')
CAP = find_capture()
CLIP = CAP / 'clips' / os.environ.get('CLIP', 'board')
if not (CLIP / 'frames.json').exists():
    raise SystemExit(f'No capture at {CLIP}. Run: node capture/capture.mjs capture/board.shots.json')
meta = json.load(open(CLIP / 'frames.json')); marks = meta['marks']
os.makedirs('media', exist_ok=True)
def segment(out, a, b, dur):
    subprocess.run(['python3', str(CAP / 'clip_to_video.py'), str(CLIP), out, '--from', str(a), '--to', str(b), '--duration', f'{dur:.3f}'], check=True)
A_LEN, B_LEN = D['s3'] - .2, D['s4'] - .2
segment('media/board-a.mp4', 0, 'drag', A_LEN)
segment('media/board-b.mp4', 'drag', 'end', B_LEN)
def gt(clip_t):  # clip time -> film time
    if clip_t < marks['drag']:
        return S['s3'] + .1 + clip_t * A_LEN / marks['drag']
    return S['s4'] + .1 + (clip_t - marks['drag']) * B_LEN / (meta['length'] - marks['drag'])

# ---------- GSAP helpers ----------
JS = []
def J(s): JS.append(s)
def ft(sel, a, b, at): J(f'tl.fromTo({json.dumps(sel)}, {json.dumps(a)}, {json.dumps(b)}, {round(at, 3)});')
def to(sel, v, at): J(f'tl.to({json.dumps(sel)}, {json.dumps(v)}, {round(at, 3)});')
def st(sel, v, at): J(f'tl.set({json.dumps(sel)}, {json.dumps(v)}, {round(at, 3)});')
def cut(sel, s, d):
    if s > 0.001: st(sel, {'autoAlpha': 0}, 0)
    st(sel, {'autoAlpha': 1}, s); st(sel, {'autoAlpha': 0}, s + d)
def typing(sel, text, at, secs):
    J(f'(function(){{var o={{n:0}},el=document.querySelector({json.dumps(sel)}),s={json.dumps(text)};'
      f'tl.fromTo(o,{{n:0}},{{n:s.length,duration:{secs:.2f},ease:"none",onUpdate:function(){{el.textContent=s.slice(0,Math.round(o.n));}}}},{at:.3f});}})();')

scenes, labels = [], []
def scene(sid_from, sid_to, body, label, cls='paper', idx=None):
    s = S[sid_from]; d = S[sid_to] + D[sid_to] - s
    i = f'sc-{sid_from}'
    scenes.append(f'<section class="fx {cls}" id="{i}">{body}</section>'); cut(f'#{i}', s, d)
    labels.append(f'<div class="fxlabel" id="fl-{sid_from}">{label}</div>'); cut(f'#fl-{sid_from}', s, d)
    return i, s, d

# s1 — kinetic caption slam
words = [('YOUR DEMO,', .15), ('RECORDED', .65), ('BY AN', 1.15), ('<span class="serif it acc" style="font-weight:400;text-transform:none;font-size:300px">agent.</span>', 1.6)]
k = D['s1'] / 2.9
h = ''.join(f'<div class="w{n}" style="position:absolute;font-weight:900;font-size:210px;letter-spacing:-.045em;line-height:1">{w}</div>' for n, (w, _) in enumerate(words))
i, s, d = scene('s1', 's1', f'<div class="stage center">{h}</div>', '<b>01</b>Kinetic caption slam', 'dark')
for n, (_, a) in enumerate(words):
    ft(f'#{i} .w{n}', {'scale': 1.6, 'autoAlpha': 0}, {'scale': 1, 'autoAlpha': 1, 'duration': .2, 'ease': 'back.out(2)'}, s + a * k)
    if n < len(words) - 1: st(f'#{i} .w{n}', {'autoAlpha': 0}, s + words[n + 1][1] * k)

# s2 — typed prompt
PROMPT = 'Record a demo of Boards: add a task, move it to Done, then share the board.'
i, s, d = scene('s2', 's2', '<div class="stage center" style="flex-direction:column;align-items:flex-start;padding:0 260px">'
                '<div class="kicker">Prompt</div>'
                '<div style="margin-top:22px;width:1400px;background:var(--card);border:1.5px solid var(--line);border-radius:26px;padding:44px 52px;box-shadow:0 30px 60px -40px rgba(20,20,20,.35)">'
                '<div style="display:flex;gap:22px;font-size:50px;line-height:1.3;font-weight:500;letter-spacing:-.02em"><span class="acc mono">›</span>'
                '<span><span class="pt"></span><span class="caret"></span></span></div></div></div>', '<b>02</b>Typed prompt')
ft(f'#{i} .stage > div:nth-child(2)', {'y': 40, 'autoAlpha': 0}, {'y': 0, 'autoAlpha': 1, 'duration': .4, 'ease': 'power3.out'}, s)
typing(f'#{i} .pt', PROMPT, s + .3, max(1.2, d - .7))

# s3 + s4 — agent panel + live browser capture, punch-in then pull-back
STEPS = [('open', 'demo-app/index.html', 'navigate'), ('click', '"New task"', 'new'), ('type', '"Record product demo"', 'type'),
         ('drag', 'card → Done', 'drag'), ('click', '"Share"', 'share')]
rows = ''.join(f'<div class="stp st{n}" style="display:flex;gap:16px;align-items:baseline;padding:16px 18px;border-radius:12px;margin-bottom:6px;color:var(--muted)">'
               f'<span class="mono ic" style="width:26px;font-size:20px">{n + 1}</span><span class="mono" style="font-size:22px;font-weight:600;width:70px;color:inherit">{a}</span>'
               f'<span class="mono" style="font-size:21px">{html.escape(b)}</span></div>' for n, (a, b, _) in enumerate(STEPS))
panel = ('<div style="position:absolute;left:70px;top:150px;width:520px">'
         '<div style="display:flex;align-items:center;gap:12px;margin-bottom:22px"><i class="rec" style="width:12px;height:12px;border-radius:50%;background:var(--signal)"></i>'
         '<span class="kicker" style="color:var(--ink)">Agent · browser control</span></div>'
         f'<div style="background:var(--card);border:1.5px solid var(--line);border-radius:20px;padding:16px">{rows}</div>'
         '<div class="mono" style="font-size:18px;color:var(--muted);margin-top:18px">playwright · chromium · 1960×1102 frames</div></div>')
VW, VH = 1210, round(1210 * 551 / 980)
browser = (f'<div class="cam" style="position:absolute;left:640px;top:120px;width:{VW}px;height:{VH + 52}px">'
           f'<div class="win" style="left:0;top:0;width:{VW}px;height:{VH + 52}px"><div class="winbar" style="height:52px"><i></i><i></i><i></i><div class="url" style="height:32px">demo-app/index.html</div></div>'
           f'<div style="position:relative;width:{VW}px;height:{VH}px;overflow:hidden"><div class="zoom" style="position:absolute;inset:0">'
           f'<video src="media/board-a.mp4" data-start="{S["s3"] + .1:.3f}" data-duration="{A_LEN:.3f}" muted playsinline style="position:absolute;inset:0;width:100%;height:100%"></video>'
           f'<video src="media/board-b.mp4" data-start="{S["s4"] + .1:.3f}" data-duration="{B_LEN:.3f}" muted playsinline style="position:absolute;inset:0;width:100%;height:100%"></video>'
           '</div></div></div></div>')
i, s, d = scene('s3', 's4', f'<div class="stage">{panel}{browser}</div>', '<b>03</b>Browser capture with Playwright')
ft(f'#{i} .cam', {'y': 80, 'autoAlpha': 0}, {'y': 0, 'autoAlpha': 1, 'duration': .5, 'ease': 'power3.out'}, s)
ft(f'#{i} .rec', {'opacity': 1}, {'opacity': .25, 'duration': .5, 'repeat': int(d / .5), 'yoyo': True, 'ease': 'none'}, s)
for n, (_, _, mk) in enumerate(STEPS):
    a = gt(marks[mk])
    to(f'#{i} .st{n}', {'backgroundColor': '#DADFFF', 'color': '#141414', 'duration': .15}, a)
    nxt = gt(marks[STEPS[n + 1][2]]) if n + 1 < len(STEPS) else gt(meta['length'] - .4)
    to(f'#{i} .st{n}', {'backgroundColor': 'rgba(0,0,0,0)', 'color': '#1C8C4E', 'duration': .15}, nxt)
    st(f'#{i} .st{n} .ic', {'textContent': '✓'}, nxt)
# punch in on the drag (towards Done), pull back for the share toast
labels.append('<div class="fxlabel" id="fl-s4"><b>04</b>Camera punch-in, then pull-back reveal</div>')
cut('#fl-s4', S['s4'], D['s4']); st('#fl-s3', {'autoAlpha': 0}, S['s4'])
ft(f'#{i} .zoom', {'scale': 1}, {'scale': 1.6, 'transformOrigin': '80% 30%', 'duration': .7, 'ease': 'power3.inOut'}, S['s4'] + .05)
to(f'#{i} .zoom', {'scale': 1, 'duration': .8, 'ease': 'power3.inOut'}, gt(marks['share']) - .1)

# s5 — brand swap (strikethrough replace)
code = ('<div class="mono" style="font-size:28px;line-height:1.7;color:var(--ink-2)">{<br>'
        '&nbsp;&nbsp;"name": <span class="acc2">"Boards"</span>,<br>'
        '&nbsp;&nbsp;"accent": <span style="position:relative;display:inline-block"><span class="old">"#2F45FF"</span>'
        '<i class="sk" style="position:absolute;left:-4px;right:-4px;top:52%;height:5px;background:var(--signal);transform-origin:left;transform:scaleX(0)"></i></span> <span class="new" style="color:#C2410C">"#C2410C"</span>,<br>'
        '&nbsp;&nbsp;"display": "Instrument Serif",<br>&nbsp;&nbsp;"sans": "Geist"<br>}</div>')
prev = ('<div style="background:var(--card);border:1.5px solid var(--line);border-radius:26px;padding:50px 56px;width:640px">'
        '<div class="kicker">Title card preview</div><div class="serif pv" style="font-size:130px;line-height:1;margin-top:16px;color:var(--accent)">Boards<span style="color:var(--ink)">.</span></div>'
        '<div class="bar pvb" style="height:10px;width:220px;border-radius:5px;background:var(--accent);margin-top:26px"></div></div>')
i, s, d = scene('s5', 's5', '<div class="stage center" style="gap:90px"><div style="background:var(--card);border:1.5px solid var(--line);border-radius:26px;padding:40px 48px">'
                f'<div class="kicker" style="margin-bottom:16px">brand/brand.json</div>{code}</div>{prev}</div>', '<b>05</b>Strikethrough replace')
ft(f'#{i} .new', {'autoAlpha': 0, 'x': -10}, {'autoAlpha': 1, 'x': 0, 'duration': .3}, s + d * .45)
ft(f'#{i} .sk', {'scaleX': 0}, {'scaleX': 1, 'duration': .3, 'ease': 'power2.inOut'}, s + d * .3)
to(f'#{i} .old', {'color': '#A7A29A', 'duration': .2}, s + d * .35)
to(f'#{i} .pv', {'color': '#C2410C', 'duration': .4}, s + d * .5)
to(f'#{i} .pvb', {'backgroundColor': '#C2410C', 'width': 380, 'duration': .5, 'ease': 'power3.out'}, s + d * .5)

# s6 — how it works (storyboard cards)
cards = [('01', 'Shot list', 'A JSON list of clicks,<br>typing and drags.'), ('02', 'Playwright', 'Drives Chromium and<br>captures every frame.'), ('03', 'HyperFrames', 'Adds motion, captions<br>and your voice. Renders MP4.')]
ch = ''.join(f'<div class="c c{n}" style="width:470px;background:{"var(--ink)" if n == 1 else "var(--card)"};color:{"var(--paper)" if n == 1 else "var(--ink)"};border:1.5px solid var(--line);border-radius:26px;padding:40px 44px">'
             f'<div class="mono" style="font-size:20px;opacity:.6">{a}</div><div class="serif" style="font-size:84px;line-height:1;margin-top:26px">{b}</div>'
             f'<div style="font-size:26px;line-height:1.4;margin-top:24px;opacity:.75">{c}</div></div>' for n, (a, b, c) in enumerate(cards))
i, s, d = scene('s6', 's6', f'<div class="stage center" style="gap:36px">{ch}</div>', '<b>06</b>Storyboard deck')
for n in range(3):
    ft(f'#{i} .c{n}', {'y': 70, 'rotation': -3 + n * 3, 'autoAlpha': 0}, {'y': 0, 'rotation': 0, 'autoAlpha': 1, 'duration': .45, 'ease': 'back.out(1.4)'}, s + .1 + n * min(.45, d * .14))

# s7 — calm title card
i, s, d = scene('s7', 's7', '<div class="stage center" style="flex-direction:column;align-items:flex-start;padding-left:260px">'
                '<div class="k kicker">Open source</div><div class="h serif" style="font-size:200px;line-height:.95">Point it at<br><i class="acc">your product.</i></div>'
                '<div class="cmd mono" style="margin-top:46px;background:var(--ink);color:var(--paper);border-radius:14px;padding:18px 26px;font-size:28px">'
                '<span style="color:#9a958e">$</span> ./scripts/setup.sh &amp;&amp; node capture/capture.mjs shots.json</div></div>', '<b>07</b>Calm title card')
ft(f'#{i} .k', {'autoAlpha': 0, 'y': 12}, {'autoAlpha': 1, 'y': 0, 'duration': .5}, s + .1)
ft(f'#{i} .h', {'autoAlpha': 0, 'y': 24}, {'autoAlpha': 1, 'y': 0, 'duration': .8, 'ease': 'power2.out'}, s + .25)
ft(f'#{i} .cmd', {'autoAlpha': 0, 'y': 16}, {'autoAlpha': 1, 'y': 0, 'duration': .5}, s + .9)

# captions (word-timed if split-voiceover.py wrote vo/captions.json)
caps, ci = [], 0
if os.path.exists('vo/captions.json') and all(HAS_VO.values()):
    CL = json.load(open('vo/captions.json'))
    for n, (a, b, p) in enumerate(CL):
        ci += 1; a0 = max(0, a - .05); b0 = min(b + .25, CL[n + 1][0] - .06) if n + 1 < len(CL) else min(b + .6, TOTAL)
        caps.append(f'<div class="cap" id="cap{ci}"><span>{html.escape(p)}</span></div>'); cut(f'#cap{ci}', a0, b0 - a0)
else:
    for sid, title, text in script:
        parts = [p.strip() for p in re.split(r'(?<=[.?!])\s+', text) if p.strip()]
        vo = D[sid] - LEAD - TAIL - (END_HOLD if sid == script[-1][0] else 0); tot = sum(len(p) for p in parts); c = S[sid] + LEAD
        for p in parts:
            pd = vo * len(p) / tot; ci += 1
            caps.append(f'<div class="cap" id="cap{ci}"><span>{html.escape(p)}</span></div>'); cut(f'#cap{ci}', c, pd - .05); c += pd

J(f'tl.fromTo(".grain", {{x: 0, y: 0}}, {{x: -40, y: 30, duration: {TOTAL}, ease: "steps({int(TOTAL * 12)})"}}, 0);')
J(f'tl.fromTo(".progress i", {{scaleX: 0}}, {{scaleX: 1, duration: {TOTAL}, ease: "none"}}, 0);')
audio = ''.join(f'<audio src="vo/{sid}.wav" data-start="{S[sid] + LEAD:.3f}" data-duration="{probe(f"vo/{sid}.wav"):.3f}" data-volume="1"></audio>' for sid, _, _ in script if HAS_VO[sid])

# ---------- brand tokens ----------
css = open('style.css').read() + '.fxlabel{visibility:hidden;opacity:0}'
WORDMARK = 'video-edit-<b>skills</b>'
def find_brand():
    env = os.environ.get('BRAND_FILE')
    if env and os.path.exists(env): return pathlib.Path(env)
    for dd in [pathlib.Path.cwd(), *pathlib.Path.cwd().parents]:
        if (dd / 'brand' / 'brand.json').exists(): return dd / 'brand' / 'brand.json'
BF = find_brand()
if BF:
    B = json.load(open(BF)); c, f = B.get('colors', {}), B.get('fonts', {})
    keys = {'paper': '--paper', 'paper_2': '--paper-2', 'card': '--card', 'ink': '--ink', 'ink_2': '--ink-2', 'muted': '--muted', 'line': '--line', 'accent': '--accent', 'accent_soft': '--accent-soft', 'signal': '--signal', 'ok': '--ok'}
    over = ''.join(f'{v}:{c[k]};' for k, v in keys.items() if c.get(k))
    for k, v, fb in [('display', '--serif', 'Georgia,serif'), ('sans', '--sans', 'system-ui,sans-serif'), ('mono', '--mono', 'ui-monospace,monospace')]:
        if f.get(k): over += f"{v}:'{f[k]}',{fb};"
    css = (f"@import url('{f['google_fonts_css']}');" if f.get('google_fonts_css') else '') + css + ':root{' + over + '}'
    if B.get('name'): WORDMARK = html.escape(B['name'])
    print('brand:', BF)

page = f'''<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width={W}, height={H}" />
<title>Product demos, recorded by an agent</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{css}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
{''.join(scenes)}
<div class="grain"></div>
<div class="meta"><span class="brand">{WORDMARK}</span></div>
{''.join(labels)}
{''.join(caps)}
<div class="progress"><i></i></div>
{audio}
</div>
<script>
(function(){{
const tl = gsap.timeline({{paused: true}});
tl.to({{}}, {{duration: {TOTAL}}}, 0);
{chr(10).join(JS)}
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
tl.seek(0);
}})();
</script>
</body></html>'''
open('index.html', 'w').write(page)
print('TOTAL', TOTAL)
