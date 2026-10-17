"""Search smarter in 60 seconds — 16:9, one design system, all 31 effects from the creator effects pack
re-built natively (Cloud Dancer palette, Instrument Serif + Geist). Run: python3 build.py && npm run render"""
import json, re, html, subprocess

W, H = 1920, 1080
LEAD, TAIL, END_HOLD = 0.2, 0.2, 0.0
import os as _os
if _os.path.exists('vo/timing.json'):  # written by split_voiceover.py for a continuous human recording
    _tm = json.load(open('vo/timing.json'))
    LEAD, TAIL, END_HOLD = _tm.get('lead', LEAD), _tm.get('tail', TAIL), _tm.get('end_hold', 0.0)
script = json.load(open('script.json'))

def dur(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode())

import os
HAS_VO = {}
T, t = {}, 0.0
for sid, title, text in script:
    wav = f'vo/{sid}.wav'
    HAS_VO[sid] = os.path.exists(wav)
    # no recording yet: estimate from word count (~150 words a minute) so the cut can be previewed silently
    d = LEAD + (dur(wav) if HAS_VO[sid] else len(text.split()) / 2.5 + .3) + TAIL
    if sid == script[-1][0]:
        d += END_HOLD
    T[sid] = (round(t, 3), round(d, 3), text)
    t += d
TOTAL = round(t, 3)

# ---------------- JS helpers (Python -> GSAP calls) ----------------
JS = []
def J(s): JS.append(s)
def ft(sel, frm, to, at):  J(f'tl.fromTo({json.dumps(sel)}, {json.dumps(frm)}, {json.dumps(to)}, {round(at, 3)});')
def to(sel, v, at):        J(f'tl.to({json.dumps(sel)}, {json.dumps(v)}, {round(at, 3)});')
def st(sel, v, at):        J(f'tl.set({json.dumps(sel)}, {json.dumps(v)}, {round(at, 3)});')
def typing(sel, text, at, secs, wrap=None):
    """Deterministic typing via a proxy tween; wrap(slice)->html optional."""
    w = 'function(x){return x.replace(/&/g,"&amp;").replace(/</g,"&lt;");}' if not wrap else wrap
    J(f'(function(){{var o={{n:0}},el=document.querySelector({json.dumps(sel)}),s={json.dumps(text)},w={w};'
      f'tl.fromTo(o,{{n:0}},{{n:s.length,duration:{secs:.2f},ease:"none",onUpdate:function(){{el.innerHTML=w(s.slice(0,Math.round(o.n)));}}}},{at:.3f});}})();')

def cut(sel, s, d):
    if s > 0.001:
        st(sel, {'autoAlpha': 0}, 0)
    st(sel, {'autoAlpha': 1}, s)
    st(sel, {'autoAlpha': 0}, s + d)

SB = lambda inner, extra='', style='': f'<div class="sbox {extra}" style="{style}"><span class="mag"></span><span class="q">{inner}</span></div>'
CURSOR = '<svg class="cur" viewBox="0 0 24 24" style="position:absolute;width:44px;height:44px;z-index:20"><path d="M4 2l6.5 19 2.4-7.8 7.8-2.4z" fill="#141414" stroke="#FAF9F6" stroke-width="1.4" stroke-linejoin="round"/></svg>'

RESULTS3 = '''<div class="res"><div class="d">example.org › guides</div><div class="t">The <mark>onboarding checklist</mark> every new hire needs</div></div>
<div class="res"><div class="d">example.com › blog</div><div class="t">A simple <mark>onboarding checklist</mark> for week one</div></div>
<div class="res"><div class="d">sample.net › hr</div><div class="t">Printable <mark>onboarding checklist</mark></div></div>'''

# ---------------- the 30 scene effects (grain overlay is #31, global) ----------------
FX = []  # (beat, key, label, builder)
def fx(beat, key, label):
    def deco(fn):
        FX.append((beat, key, label, fn)); return fn
    return deco

@fx('s1', 'caption-kinetic-slam', 'Kinetic caption slam')
def e(i, s, d):
    words = [('STILL', .1), ('SEARCHING', .55), ('THE <span class="serif it acc" style="font-weight:400;text-transform:none">slow</span>', 1.15), ('WAY?', 1.85)]
    h = ''.join(f'<div class="ks w{k}" style="position:absolute;font-weight:900;font-size:230px;letter-spacing:-.04em;line-height:1">{w}</div>' for k, (w, _) in enumerate(words))
    for k, (_, a) in enumerate(words):
        ft(f'#{i} .w{k}', {'scale': 1.7, 'autoAlpha': 0}, {'scale': 1, 'autoAlpha': 1, 'duration': .2, 'ease': 'back.out(2)'}, s + a)
        if k < len(words) - 1:
            st(f'#{i} .w{k}', {'autoAlpha': 0}, s + words[k + 1][1])
    return f'<div class="stage center">{h}</div>', 'dark'

@fx('s1', 'gravity-drop', 'Gravity drop')
def e(i, s, d):
    ft(f'#{i} .card', {'y': -900}, {'y': 0, 'duration': .85, 'ease': 'bounce.out'}, s + .05)
    ft(f'#{i} .bar', {'y': -1100, 'rotation': -6}, {'y': 0, 'rotation': -2, 'duration': .8, 'ease': 'bounce.out'}, s + .9)
    ft(f'#{i} .card', {'scaleY': 1}, {'scaleY': .95, 'duration': .08, 'yoyo': True, 'repeat': 1, 'transformOrigin': '50% 100%'}, s + 1.25)
    return (f'<div class="stage center" style="flex-direction:column">'
            f'<div class="bar" style="margin-bottom:-6px;z-index:2">{SB("how do i make my laptop battery last longer", style="width:1060px;font-size:28px")}</div>'
            f'<div class="card" style="width:1180px;padding:70px 80px;background:var(--card);border:1.5px solid var(--line);border-radius:28px">'
            f'<div class="kicker">The usual way</div><div class="serif" style="font-size:150px;line-height:1;margin-top:16px">The <i>slow</i> way.</div></div></div>'), ''

@fx('s2', 'strikethrough-replace', 'Strikethrough replace')
def e(i, s, d):
    ft(f'#{i} .strike', {'scaleX': 0}, {'scaleX': 1, 'duration': .45, 'ease': 'power2.inOut'}, s + .45)
    to(f'#{i} .old', {'color': '#A7A29A', 'duration': .3}, s + .7)
    ft(f'#{i} .new', {'y': 40, 'autoAlpha': 0}, {'y': 0, 'autoAlpha': 1, 'duration': .45, 'ease': 'power3.out'}, s + 1.0)
    return ('<div class="stage center" style="flex-direction:column;align-items:flex-start;padding-left:300px">'
            '<div class="kicker">What slows you down</div>'
            '<div style="position:relative;margin-top:24px"><div class="old" style="font-size:110px;font-weight:700;letter-spacing:-.03em">Typing the whole question</div>'
            '<i class="strike" style="position:absolute;left:-12px;right:-12px;top:54%;height:12px;background:var(--signal);transform-origin:left center;border-radius:6px"></i></div>'
            '<div class="new serif it acc" style="font-size:150px;line-height:1.1;margin-top:10px">Typing the key words.</div></div>'), ''

@fx('s2', 'scroll-feed', 'Scroll feed')
def e(i, s, d):
    rows = ''.join(f'<div style="background:var(--card);border:1px solid var(--line);border-radius:18px;padding:26px 32px;margin-bottom:18px">'
                   f'<div class="mono" style="font-size:18px;color:var(--muted)">result-{k + 1:02d}.example.com</div>'
                   f'<div style="height:22px;width:{60 + (k * 37) % 35}%;background:var(--paper-2);border-radius:6px;margin-top:14px"></div>'
                   f'<div style="height:16px;width:{45 + (k * 53) % 40}%;background:var(--paper-2);border-radius:6px;margin-top:10px"></div></div>' for k in range(16))
    ft(f'#{i} .feed', {'y': 0}, {'y': -1650, 'duration': d, 'ease': 'power2.in'}, s)
    return ('<div class="stage" style="-webkit-mask-image:linear-gradient(transparent,#000 18%,#000 82%,transparent)">'
            f'<div class="feed" style="position:absolute;left:560px;width:800px;top:120px">{rows}</div></div>'
            '<div style="position:absolute;left:120px;top:400px"><div class="kicker">Page 1 of</div><div class="serif" style="font-size:120px;line-height:1">a lot.</div></div>'), ''

@fx('s2', 'three-orbiting-cards', 'Orbiting cards')
def e(i, s, d):
    cards = ''.join(f'<div class="oc" style="position:absolute;left:-170px;top:-105px;width:340px;height:210px;background:var(--card);border:1.5px solid var(--line);border-radius:16px;'
                    f'transform:rotateY({k * 36}deg) translateZ(470px);backface-visibility:hidden;padding:18px 20px">'
                    f'<div style="display:flex;gap:7px"><i style="width:9px;height:9px;border-radius:50%;background:var(--line)"></i><i style="width:9px;height:9px;border-radius:50%;background:var(--line)"></i></div>'
                    f'<div class="mono" style="font-size:17px;color:var(--muted);margin-top:16px">tab {k + 1}</div><div style="font-size:24px;font-weight:600;margin-top:6px">site-{k + 1}.example</div>'
                    f'<div style="height:12px;width:70%;background:var(--paper-2);border-radius:6px;margin-top:16px"></div></div>' for k in range(10))
    ft(f'#{i} .ring', {'rotationY': 0}, {'rotationY': -150, 'duration': d, 'ease': 'none'}, s)
    return ('<div class="stage" style="perspective:1700px"><div class="ring" style="position:absolute;left:1270px;top:470px;transform-style:preserve-3d;transform:rotateX(-8deg)">' + cards + '</div></div>'
            '<div style="position:absolute;left:120px;top:360px"><div class="serif" style="font-size:150px;line-height:.95">Ten<br>open tabs.</div>'
            '<div style="font-size:30px;color:var(--muted);margin-top:26px">Still no clear answer.</div></div>'), ''

@fx('s2', 'mk-clone-wall-transition', 'Clone-wall transition')
def e(i, s, d):
    rows = ''.join(f'<div class="r{k}" style="white-space:nowrap;font-weight:900;font-size:150px;letter-spacing:-.04em;line-height:1.02;color:{"var(--paper)" if k % 2 else "#3A3936"}">'
                   + ('3 TRICKS · ' * 8) + '</div>' for k in range(8))
    for k in range(8):
        ft(f'#{i} .r{k}', {'x': -400 if k % 2 else -1400}, {'x': -1400 if k % 2 else -400, 'duration': d, 'ease': 'none'}, s)
    ft(f'#{i} .wipe', {'clipPath': 'inset(50% 50% 50% 50% round 30px)'}, {'clipPath': 'inset(0% 0% 0% 0% round 0px)', 'duration': .6, 'ease': 'power3.inOut'}, s + d - .75)
    return (f'<div style="position:absolute;inset:-40px 0 0 0">{rows}</div>'
            '<div class="wipe center" style="position:absolute;inset:0;background:var(--paper);color:var(--ink)"><div class="serif" style="font-size:200px">Three tricks.</div></div>'), 'dark'

@fx('s3', 'zoom-through-transition', 'Zoom-through transition')
def e(i, s, d):
    ft(f'#{i} .z', {'scale': 1}, {'scale': 42, 'duration': d - .5, 'ease': 'power4.in'}, s + .35)
    ft(f'#{i} .z', {'autoAlpha': 1}, {'autoAlpha': 0, 'duration': .15}, s + d - .2)
    big = 'font-weight:900;font-size:300px;letter-spacing:-.05em;line-height:1;position:absolute;top:50%;transform:translateY(-55%)'
    return ('<div class="stage"><div class="kicker" style="position:absolute;left:0;right:0;top:250px;text-align:center">Step 1</div>'
            '<div class="z" style="position:absolute;inset:0;transform-origin:960px 470px">'
            f'<div style="{big};right:1050px">Key w</div>'
            '<div style="position:absolute;left:870px;top:380px;width:180px;height:180px;border-radius:50%;border:44px solid var(--accent)"></div>'
            f'<div style="{big};left:1062px">rds</div></div></div>'), ''

@fx('s3', 'browser-device-stage', 'Browser device stage')
def e(i, s, d):
    ft(f'#{i} .win', {'y': 120, 'scale': .94, 'autoAlpha': 0}, {'y': 0, 'scale': 1, 'autoAlpha': 1, 'duration': .55, 'ease': 'power3.out'}, s)
    typing(f'#{i} .url', 'search.example', s + .35, .45)
    ft(f'#{i} .cur', {'x': 1250, 'y': 760}, {'x': 760, 'y': 470, 'duration': .5, 'ease': 'power2.inOut'}, s + .7)
    to(f'#{i} .sbox', {'borderColor': '#2F45FF', 'boxShadow': '0 0 0 6px #DADFFF', 'duration': .15}, s + 1.2)
    return ('<div class="win" style="left:260px;top:110px;width:1400px;height:720px"><div class="winbar"><i></i><i></i><i></i><div class="url"></div></div>'
            '<div class="center" style="flex-direction:column;height:660px;gap:46px"><div style="font-size:64px;font-weight:600;letter-spacing:-.03em">Search</div>'
            + SB('<span class="caret"></span>', style='width:900px') + '</div>' + CURSOR + '</div>'), ''

@fx('s3', 'cursor-drag-drop', 'Cursor drag and drop')
def e(i, s, d):
    def card(txt, cls=''):
        return f'<div class="{cls}" style="background:var(--card);border:1.5px solid var(--line);border-radius:16px;padding:22px 24px;font-size:26px;font-weight:500;margin-bottom:16px">{txt}</div>'
    cols = (f'<div style="position:absolute;left:330px;top:190px;width:560px;height:620px;background:var(--paper-2);border-radius:24px;padding:28px">'
            f'<div class="kicker" style="margin-bottom:22px">Full sentence</div>{card("how do i make my laptop battery last longer")}{card("why does my phone get hot when charging")}</div>'
            f'<div style="position:absolute;left:1030px;top:190px;width:560px;height:620px;background:var(--accent-soft);border-radius:24px;padding:28px">'
            f'<div class="kicker" style="margin-bottom:22px;color:var(--accent)">Key words</div>'
            f'<div style="height:84px;border:2px dashed #9AA6FF;border-radius:16px"></div></div>')
    mover = f'<div class="mv mono" style="position:absolute;left:358px;top:560px;width:504px;background:var(--card);border:2px solid var(--accent);border-radius:16px;padding:22px 24px;font-size:26px;z-index:5">laptop battery tips</div>'
    ft(f'#{i} .cur', {'x': 1400, 'y': 820}, {'x': 820, 'y': 595, 'duration': .45, 'ease': 'power2.out'}, s + .05)
    ft(f'#{i} .mv', {'scale': 1, 'rotation': 0}, {'scale': 1.04, 'rotation': 2, 'boxShadow': '0 30px 60px -20px rgba(20,20,20,.35)', 'duration': .15}, s + .55)
    to(f'#{i} .mv', {'x': 700, 'y': -270, 'duration': .65, 'ease': 'power2.inOut'}, s + .7)
    to(f'#{i} .cur', {'x': 1520, 'y': 325, 'duration': .65, 'ease': 'power2.inOut'}, s + .7)
    to(f'#{i} .mv', {'scale': 1, 'rotation': 0, 'boxShadow': '0 0 0 0 rgba(0,0,0,0)', 'duration': .2, 'ease': 'back.out(2)'}, s + 1.37)
    return f'<div class="stage">{cols}{mover}{CURSOR}</div>', ''

@fx('s3', 'device-frame-stage', 'Device frame stage')
def e(i, s, d):
    ft(f'#{i} .ph', {'rotationY': -28, 'y': 80, 'autoAlpha': 0}, {'rotationY': -10, 'y': 0, 'autoAlpha': 1, 'duration': .7, 'ease': 'power3.out'}, s)
    to(f'#{i} .ph', {'rotationY': -4, 'duration': d - .7, 'ease': 'sine.inOut'}, s + .7)
    screen = ('<div style="padding:70px 22px 0">' + SB('laptop battery tips', style='height:58px;font-size:18px;padding:0 18px;gap:12px') +
              ''.join(f'<div style="padding:18px 4px;border-bottom:1px solid var(--line)"><div class="mono" style="font-size:13px;color:var(--muted)">{dm}</div><div style="font-size:20px;font-weight:600;margin-top:4px">{tt}</div></div>'
                      for dm, tt in [('example.org › guides', '12 laptop battery tips that work'), ('example.com › how-to', 'Make your battery last longer'), ('sample.net › tech', 'Battery myths, tested')]) + '</div>')
    return ('<div class="stage" style="perspective:1600px"><div style="position:absolute;left:150px;top:380px"><div class="kicker">Result</div>'
            '<div class="serif" style="font-size:120px;line-height:1">Straight to<br><i>the point.</i></div></div>'
            f'<div class="ph" style="position:absolute;left:1150px;top:60px;width:420px;height:840px;border-radius:60px;background:var(--ink);padding:14px">'
            f'<div style="width:100%;height:100%;border-radius:48px;background:var(--card);overflow:hidden">{screen}</div></div></div>'), ''

@fx('s4', 'typed-prompt', 'Typed prompt')
def e(i, s, d):
    wrap = 'function(x){return x.replace(/"/g,\'<span style="color:#2F45FF;font-weight:600">"</span>\')+\'<span class="caret"></span>\';}'
    typing(f'#{i} .q', '"onboarding checklist"', s + .25, 1.3, wrap)
    return ('<div class="stage center" style="flex-direction:column;gap:40px"><div class="kicker">Step 2 · exact phrase</div>'
            + SB('', style='width:1240px;height:120px;border-radius:60px;font-size:50px') + '</div>'), ''

@fx('s4', 'caption-editorial-emphasis', 'Editorial caption emphasis')
def e(i, s, d):
    for k, a in enumerate([.1, .4, .9, 1.2]):
        ft(f'#{i} .l{k}', {'yPercent': 110}, {'yPercent': 0, 'duration': .45, 'ease': 'power3.out'}, s + a)
    ft(f'#{i} .hl', {'scaleX': 0}, {'scaleX': 1, 'duration': .4, 'ease': 'power2.out'}, s + 1.55)
    m = lambda k, inner, st_: f'<div style="overflow:hidden;display:inline-block;vertical-align:bottom;margin-right:.22em"><div class="l{k}" style="{st_}">{inner}</div></div>'
    return ('<div class="stage center" style="flex-direction:column;align-items:flex-start;padding-left:260px">'
            f'<div>{m(0, "Same", "font-size:150px;font-weight:600;letter-spacing:-.04em")} {m(1, "words,", "font-size:150px;font-weight:600;letter-spacing:-.04em")}</div>'
            f'<div style="position:relative">{m(2, "same", "font-size:150px;font-weight:600;letter-spacing:-.04em")} '
            f'<span style="position:relative;display:inline-block"><i class="hl" style="position:absolute;left:-10px;right:-10px;bottom:30px;height:60px;background:var(--accent-soft);transform-origin:left;z-index:0"></i>'
            f'{m(3, "order.", "font-family:var(--serif);font-style:italic;font-size:220px;color:var(--accent);position:relative;z-index:1;line-height:1")}</span></div></div>'), ''

@fx('s4', 'eyedropper-grade', 'Eyedropper sample')
def e(i, s, d):
    ft(f'#{i} .lp', {'x': -200, 'y': 420}, {'x': 300, 'y': 62, 'duration': .8, 'ease': 'power3.inOut'}, s + .1)
    ft(f'#{i} .lpi', {'x': 380, 'y': -798}, {'x': -570, 'y': -118, 'duration': .8, 'ease': 'power3.inOut'}, s + .1)
    ft(f'#{i} .sw', {'scale': .6, 'autoAlpha': 0}, {'scale': 1, 'autoAlpha': 1, 'duration': .3, 'ease': 'back.out(2)'}, s + .95)
    base = f'<div style="width:1100px">{RESULTS3}</div>'
    return ('<div class="stage"><div style="position:absolute;left:410px;top:230px">' + base +
            '<div class="lp" style="position:absolute;left:-110px;top:-110px;width:220px;height:220px;border-radius:50%;border:5px solid var(--ink);overflow:hidden;background:var(--paper);box-shadow:0 20px 40px -10px rgba(0,0,0,.35)">'
            f'<div class="lpi" style="position:absolute;left:110px;top:110px;transform-origin:0 0"><div style="transform:scale(1.9);transform-origin:0 0;width:1100px">{RESULTS3}</div></div></div></div>'
            '<div class="sw mono" style="position:absolute;left:1180px;top:170px;background:var(--ink);color:var(--paper);border-radius:14px;padding:16px 22px;font-size:24px">'
            'sample <span style="color:#A9B4FF">"onboarding checklist"</span><br><span style="color:#9a958e">match: exact</span></div></div>'), ''

@fx('s4', 'frame-break', 'Frame break')
def e(i, s, d):
    ft(f'#{i} .fr', {'autoAlpha': 0, 'scale': .96}, {'autoAlpha': 1, 'scale': 1, 'duration': .35}, s)
    ft(f'#{i} .pop', {'y': 0, 'scale': 1, 'rotation': 0}, {'y': -250, 'x': 120, 'scale': 1.9, 'rotation': -3, 'boxShadow': '0 40px 70px -25px rgba(20,20,20,.45)', 'duration': .7, 'ease': 'back.out(1.6)'}, s + .55)
    return ('<div class="stage"><div class="fr" style="position:absolute;left:410px;top:300px;width:1100px;height:420px;border:2px solid var(--ink);border-radius:26px;overflow:hidden;background:var(--card);padding:40px 50px">'
            '<div class="res" style="border:0"><div class="d">example.org › guides</div><div class="t">The <span style="opacity:0">onboarding checklist</span> every new hire needs</div></div>'
            '<div class="res" style="border:0;opacity:.45"><div class="d">example.com › blog</div><div class="t">A simple guide for week one</div></div></div>'
            '<div class="pop" style="position:absolute;left:530px;top:383px;background:var(--accent);color:#fff;font-size:32px;font-weight:600;padding:0 10px;border-radius:8px;line-height:1.4">onboarding checklist</div>'
            '<div style="position:absolute;left:410px;top:760px" class="kicker">Quotes = no partial matches</div></div>'), ''

@fx('s5', 'torn-paper-rip', 'Torn paper rip')
def e(i, s, d):
    import random
    random.seed(4)
    ys = [k * 54 for k in range(19)] + [1080]
    pts = [(960 + random.randint(-40, 40), y) for y in ys]
    left = 'polygon(0 0,' + ','.join(f'{x}px {y}px' for x, y in pts) + ',0 1080px)'
    right = 'polygon(1920px 0,' + ','.join(f'{x}px {y}px' for x, y in pts) + ',1920px 1080px)'
    ft(f'#{i} .tl', {'x': 0, 'rotation': 0}, {'x': -1150, 'rotation': -5, 'duration': .9, 'ease': 'power3.in'}, s + .45)
    ft(f'#{i} .tr', {'x': 0, 'rotation': 0}, {'x': 1150, 'rotation': 5, 'duration': .9, 'ease': 'power3.in'}, s + .45)
    pg = '<div class="center" style="position:absolute;inset:0;background:var(--paper-2);flex-direction:column"><div class="kicker">Done</div><div class="serif" style="font-size:180px">Step two.</div></div>'
    return ('<div class="center dark" style="position:absolute;inset:0;flex-direction:column"><div class="kicker" style="color:#9a958e">Next</div>'
            '<div class="serif" style="font-size:180px">Step <i style="color:#A9B4FF">three.</i></div></div>'
            f'<div class="tl" style="position:absolute;inset:0;clip-path:{left};filter:drop-shadow(6px 0 6px rgba(0,0,0,.25))">{pg}</div>'
            f'<div class="tr" style="position:absolute;inset:0;clip-path:{right};filter:drop-shadow(-6px 0 6px rgba(0,0,0,.25))">{pg}</div>'), ''

@fx('s5', 'freeze-frame-dressing', 'Freeze-frame dressing')
def e(i, s, d):
    wrap = r'function(x){return x.replace(/site:/,"<b style=\"color:#2F45FF\">site:</b>").replace(/ -/," <b style=\"color:#FF5B36\">-</b>");}'
    typing(f'#{i} .q', 'onboarding checklist site:example.com -template', s + .05, .85, wrap)
    ft(f'#{i} .flash', {'autoAlpha': .9}, {'autoAlpha': 0, 'duration': .3}, s + 1.0)
    ft(f'#{i} .tint', {'autoAlpha': 0}, {'autoAlpha': 1, 'duration': .15}, s + 1.0)
    ft(f'#{i} .tape', {'scale': 1.25, 'autoAlpha': 0}, {'scale': 1, 'autoAlpha': 1, 'duration': .2, 'stagger': .1}, s + 1.1)
    ft(f'#{i} .an', {'x': 60, 'autoAlpha': 0}, {'x': 0, 'autoAlpha': 1, 'duration': .3, 'stagger': .15, 'ease': 'power3.out'}, s + 1.2)
    return ('<div class="win" style="left:260px;top:150px;width:1400px;height:640px"><div class="winbar"><i></i><i></i><i></i><div class="url">search.example/?q</div></div>'
            '<div style="padding:70px 70px">' + SB('', style='width:100%;font-size:32px') + '</div>'
            '<div class="tint" style="position:absolute;inset:0;background:rgba(240,238,233,.55)"></div>'
            '<div style="position:absolute;left:70px;top:330px;display:flex;gap:22px">'
            '<div class="an" style="background:var(--ink);color:var(--paper);font-size:32px;font-weight:600;padding:18px 26px;border-radius:14px"><span class="mono" style="color:#A9B4FF">site:</span> one website only</div>'
            '<div class="an" style="background:var(--ink);color:var(--paper);font-size:32px;font-weight:600;padding:18px 26px;border-radius:14px"><span class="mono" style="color:#FF8A6E">-word</span> leave it out</div></div></div>'
            '<div class="tape" style="position:absolute;left:220px;top:120px;width:220px;height:56px;background:rgba(214,210,202,.9);transform:rotate(-8deg)"></div>'
            '<div class="tape" style="position:absolute;left:1500px;top:760px;width:220px;height:56px;background:rgba(214,210,202,.9);transform:rotate(7deg)"></div>'
            '<div class="flash" style="position:absolute;inset:0;background:#fff;opacity:0"></div>'), ''

@fx('s5', 'green-screen', 'Green-screen key')
def e(i, s, d):
    tiles = ''.join(f'<div style="background:rgba(255,255,255,.16);border-radius:12px;padding:16px 18px;font-family:var(--mono);font-size:19px;color:#fff">site-{k + 1}.example</div>' for k in range(30))
    ft(f'#{i} .plate', {'clipPath': 'inset(0 0% 0 0)'}, {'clipPath': 'inset(0 0% 0 100%)', 'duration': .8, 'ease': 'power2.inOut'}, s + .55)
    ft(f'#{i} .one', {'scale': .9, 'autoAlpha': 0}, {'scale': 1, 'autoAlpha': 1, 'duration': .4, 'ease': 'power3.out'}, s + .9)
    return ('<div class="stage center"><div class="one" style="width:760px;background:var(--card);border:1.5px solid var(--line);border-radius:24px;padding:44px 52px">'
            '<div class="kicker">site:example.com</div><div style="font-size:54px;font-weight:700;letter-spacing:-.03em;margin-top:14px">example.com</div>'
            '<div style="font-size:26px;color:var(--muted);margin-top:10px">Only this website. Everything else keyed out.</div></div></div>'
            f'<div class="plate" style="position:absolute;inset:0;background:#22B455;padding:120px 120px;display:grid;grid-template-columns:repeat(6,1fr);gap:18px;align-content:start">'
            f'<div class="mono" style="grid-column:1/-1;color:#fff;font-size:20px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:10px">All of the web</div>{tiles}</div>'), ''

@fx('s5', 'grade-split-reveal', 'Split reveal')
def e(i, s, d):
    def lst(rows, op=1):
        return ''.join(f'<div class="res" style="opacity:{o}"><div class="d">{dm}</div><div class="t">{tt}</div></div>' for dm, tt, o in rows)
    a = lst([('example.org › guides', 'Onboarding checklist for new hires', 1), ('templates.example › free', 'Free onboarding checklist template', 1), ('example.com › blog', 'Onboarding checklist: week one', 1), ('docs.example › template', 'Checklist template (download)', 1)])
    b = lst([('example.org › guides', 'Onboarding checklist for new hires', 1), ('example.com › blog', 'Onboarding checklist: week one', 1), ('example.com › people', 'What a good first week looks like', 1), ('example.com › hr', 'Manager checklist for day one', 1)])
    ft(f'#{i} .top', {'clipPath': 'inset(0 0 0 88%)'}, {'clipPath': 'inset(0 0 0 50%)', 'duration': .8, 'ease': 'power3.inOut'}, s + .2)
    ft(f'#{i} .div', {'x': 730}, {'x': 0, 'duration': .8, 'ease': 'power3.inOut'}, s + .2)
    box = 'position:absolute;inset:0;padding:120px 160px 0'
    return (f'<div style="{box};background:var(--paper)"><div class="kicker" style="margin-bottom:16px">Without minus</div><div style="width:1600px;color:var(--muted)">{a}</div></div>'
            f'<div class="top" style="{box};background:var(--card)"><div class="kicker" style="margin-bottom:16px;text-align:right;color:var(--signal)">-template</div><div style="width:1600px">{b}</div></div>'
            '<div class="div" style="position:absolute;left:959px;top:80px;bottom:150px;width:3px;background:var(--ink)"></div>'), ''

@fx('s5', 'camera-dolly-zoom', 'Dolly zoom')
def e(i, s, d):
    rings = ''
    for k in range(6):
        w, h = 1700 - k * 230, 860 - k * 120
        rings += (f'<div class="rg r{k}" style="position:absolute;left:{960 - w / 2}px;top:{465 - h / 2}px;width:{w}px;height:{h}px;border:2px solid {"var(--line)" if k % 2 else "#BDB8AE"};border-radius:28px">'
                  f'<span class="mono" style="position:absolute;left:20px;top:12px;font-size:18px;color:var(--muted)">site-{k + 3}.example</span></div>')
        ft(f'#{i} .r{k}', {'scale': 1}, {'scale': 1.25 + k * .2, 'autoAlpha': .0 if k < 2 else 1, 'duration': d, 'ease': 'power2.inOut'}, s)
    return ('<div class="stage">' + rings +
            '<div class="center" style="position:absolute;left:660px;top:345px;width:600px;height:240px;background:var(--ink);color:var(--paper);border-radius:24px;flex-direction:column">'
            '<div class="mono" style="font-size:20px;color:#A9B4FF">site:</div><div style="font-size:60px;font-weight:700;letter-spacing:-.03em">example.com</div></div></div>'), ''

TOOLBAR = ('<div style="display:flex;gap:34px;align-items:center;font-size:30px;color:var(--muted);border-bottom:1px solid var(--line);padding-bottom:20px">'
           '<span style="color:var(--ink);font-weight:600;border-bottom:3px solid var(--ink);padding-bottom:16px;margin-bottom:-23px">All</span><span>Images</span><span>News</span><span>Videos</span>'
           '<span class="tools" style="margin-left:auto;background:var(--ink);color:var(--paper);padding:10px 22px;border-radius:12px;font-weight:600">Tools</span></div>')

@fx('s6', 'yt-camera-move', 'Camera punch-in')
def e(i, s, d):
    ft(f'#{i} .cam', {'scale': 1, 'rotationX': 0}, {'scale': 2.3, 'rotationX': 4, 'x': -980, 'y': 520, 'duration': 1.0, 'ease': 'power3.inOut'}, s + .3)
    ft(f'#{i} .vig', {'autoAlpha': 0}, {'autoAlpha': 1, 'duration': .5, 'yoyo': True, 'repeat': 1}, s + .3)
    return ('<div class="stage" style="perspective:1800px"><div class="cam" style="position:absolute;left:210px;top:120px;width:1500px;transform-origin:50% 50%">'
            + SB('onboarding checklist', style='width:1100px;font-size:30px;height:80px') + f'<div style="margin-top:40px">{TOOLBAR}</div>'
            f'<div style="margin-top:10px">{RESULTS3}</div></div></div>'
            '<div class="vig" style="position:absolute;inset:0;box-shadow:inset 0 0 240px 80px rgba(20,20,20,.35)"></div>'), ''

MENU = ('<div style="width:520px;background:var(--card);border:1.5px solid var(--line);border-radius:18px;padding:12px 0;font-size:32px;box-shadow:0 30px 60px -30px rgba(20,20,20,.3)">'
        + ''.join(f'<div style="padding:14px 30px">{x}</div>' for x in ['Any time', 'Past hour', 'Past 24 hours', 'Past week', 'Past month'])
        + '<div class="py" style="padding:14px 30px;background:var(--accent);color:#fff;font-weight:600">Past year</div></div>')

@fx('s6', 'pull-back-reveal', 'Pull-back reveal')
def e(i, s, d):
    ft(f'#{i} .pb', {'scale': 3.4}, {'scale': 1, 'duration': 1.2, 'ease': 'power3.inOut'}, s + .25)
    return ('<div class="stage"><div class="pb" style="position:absolute;left:300px;top:110px;width:1320px;transform-origin:430px 600px">'
            '<div style="display:flex;gap:18px"><span style="background:var(--ink);color:var(--paper);padding:12px 24px;border-radius:12px;font-size:30px;font-weight:600">Tools</span>'
            '<span style="background:var(--paper-2);padding:12px 24px;border-radius:12px;font-size:30px">Any time ▾</span></div>'
            f'<div style="margin:16px 0 0 150px">{MENU}</div></div>'
            '<div style="position:absolute;left:1180px;top:330px"><div class="kicker">Pro tip</div><div class="serif" style="font-size:110px;line-height:1">Fresh results<br><i>only.</i></div></div></div>'), ''

@fx('s6', 'animated-bar-chart', 'Animated bar chart')
def e(i, s, d):
    years = list(range(2016, 2027))
    hs = [62, 70, 58, 80, 74, 88, 66, 84, 78, 90, 96]
    bars = ''.join(f'<div style="display:flex;flex-direction:column;align-items:center;gap:12px;flex:1"><div class="b b{k}" style="width:100%;height:{h * 5}px;background:var(--ink);border-radius:10px 10px 4px 4px;transform-origin:50% 100%"></div>'
                   f'<span class="mono" style="font-size:18px;color:var(--muted)">{y}</span></div>' for k, (y, h) in enumerate(zip(years, hs)))
    ft(f'#{i} .b', {'scaleY': 0}, {'scaleY': 1, 'duration': .6, 'stagger': .04, 'ease': 'power3.out'}, s + .05)
    to(f'#{i} .b', {'backgroundColor': '#D6D2CA', 'duration': .3}, s + 1.0)
    to(f'#{i} .b10', {'backgroundColor': '#2F45FF', 'duration': .3}, s + 1.0)
    ft(f'#{i} .tag', {'y': 20, 'autoAlpha': 0}, {'y': 0, 'autoAlpha': 1, 'duration': .3}, s + 1.1)
    return ('<div class="stage"><div style="position:absolute;left:260px;top:130px"><div class="kicker">Results by year</div>'
            '<div style="font-size:56px;font-weight:700;letter-spacing:-.03em;margin-top:10px">Past year keeps only the newest.</div></div>'
            f'<div style="position:absolute;left:260px;right:260px;top:300px;height:540px;display:flex;align-items:flex-end;gap:22px">{bars}</div>'
            '<div class="tag" style="position:absolute;right:240px;top:228px;background:var(--accent);color:#fff;padding:10px 18px;border-radius:12px;font-size:26px;font-weight:600">Past year</div></div>'), ''

@fx('s6', 'hw-boil', 'Hand-drawn boil')
def e(i, s, d):
    paths = ['M150 60 C 380 10, 760 20, 850 120 C 930 220, 700 300, 420 300 C 170 300, 40 240, 60 150 C 80 80, 140 60, 220 52',
             'M160 64 C 390 18, 770 26, 846 126 C 920 226, 690 304, 410 296 C 160 292, 46 236, 66 146 C 86 76, 150 58, 230 50',
             'M146 56 C 370 14, 752 16, 856 116 C 936 214, 710 296, 426 304 C 176 306, 36 246, 56 154 C 76 84, 136 64, 214 56']
    svg = ''.join(f'<path class="p{k}" d="{p}" fill="none" stroke="#FF5B36" stroke-width="7" stroke-linecap="round" style="opacity:{1 if k == 0 else 0}"/>' for k, p in enumerate(paths))
    ft(f'#{i} .p0', {'strokeDasharray': 2400, 'strokeDashoffset': 2400}, {'strokeDashoffset': 0, 'duration': .55, 'ease': 'power2.out'}, s + .15)
    n = int((d - .8) / .12)
    for k in range(n):
        a = s + .75 + k * .12
        for j in range(3):
            st(f'#{i} .p{j}', {'opacity': 1 if j == k % 3 else 0}, a)
    ft(f'#{i} .note', {'autoAlpha': 0, 'y': 10}, {'autoAlpha': 1, 'y': 0, 'duration': .3}, s + .6)
    return ('<div class="stage center"><div style="position:relative">'
            '<div style="font-weight:800;font-size:200px;letter-spacing:-.05em;line-height:1;padding:60px 90px">Past year</div>'
            f'<svg viewBox="0 0 900 340" style="position:absolute;left:-30px;top:-10px;width:1060px;height:400px">{svg}</svg>'
            '<div class="note serif it" style="position:absolute;right:-260px;top:-40px;font-size:64px;color:var(--signal);transform:rotate(-4deg)">most people<br>miss this</div></div></div>'), ''

@fx('s7', 'marker-checklist-card', 'Marker checklist')
def e(i, s, d):
    items = ['Key words, not sentences', '"Quotes" for exact phrases', 'site: for one website', '- to leave words out', 'Tools › Past year']
    rows = ''.join(f'<div style="display:flex;align-items:center;gap:30px;padding:20px 0;border-bottom:1.5px dashed var(--line);font-size:44px;font-weight:600;letter-spacing:-.02em">'
                   f'<svg viewBox="0 0 60 60" style="width:58px;height:58px;flex:none"><rect x="4" y="4" width="52" height="52" rx="10" fill="none" stroke="#141414" stroke-width="3"/>'
                   f'<path class="tk tk{k}" d="M14 32 L26 44 L48 16" fill="none" stroke="#1C8C4E" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="60" stroke-dashoffset="60"/></svg>{x}</div>' for k, x in enumerate(items))
    ft(f'#{i} .cc', {'y': 80, 'rotation': -3, 'autoAlpha': 0}, {'y': 0, 'rotation': -1.2, 'autoAlpha': 1, 'duration': .4, 'ease': 'power3.out'}, s)
    for k in range(5):
        ft(f'#{i} .tk{k}', {'strokeDashoffset': 60}, {'strokeDashoffset': 0, 'duration': .2, 'ease': 'power2.out'}, s + .35 + k * .25)
    return (f'<div class="stage center"><div class="cc" style="width:1080px;background:var(--card);border:1.5px solid var(--line);border-radius:28px;padding:44px 60px">'
            f'<div class="kicker" style="margin-bottom:8px">Recap</div>{rows}</div></div>'), ''

@fx('s7', 'storyboard-deck', 'Storyboard deck')
def e(i, s, d):
    cards = [('01', 'Key words', 'laptop battery tips'), ('02', 'Quotes', '"onboarding checklist"'), ('03', 'site: + minus', 'site:example.com -template'), ('04', 'Time filter', 'Tools › Past year')]
    h = ''
    for k, (n, t1, t2) in enumerate(cards):
        h += (f'<div class="sc sc{k}" style="position:absolute;left:-380px;top:-250px;width:760px;height:500px;background:{"var(--ink)" if k == 0 else "var(--card)"};color:{"var(--paper)" if k == 0 else "var(--ink)"};'
              f'border:1.5px solid var(--line);border-radius:26px;padding:48px 54px;z-index:{10 - k}">'
              f'<div class="mono" style="font-size:22px;opacity:.6">Shot {n}</div><div class="serif" style="font-size:110px;line-height:1;margin-top:40px">{t1}</div>'
              f'<div class="mono" style="font-size:30px;margin-top:40px;opacity:.8">{t2}</div></div>')
    for k in range(4):
        st(f'#{i} .sc{k}', {'x': k * 22, 'y': k * 22, 'rotation': k * 2}, 0)
    for k in range(3):
        a = s + .15 + k * .5
        ft(f'#{i} .sc{k}', {'x': k * 22, 'rotation': k * 2}, {'x': 900, 'rotation': 14, 'duration': .3, 'ease': 'power2.in'}, a)
        st(f'#{i} .sc{k}', {'zIndex': 0}, a + .3)
        to(f'#{i} .sc{k}', {'x': 70, 'y': 70, 'rotation': 6, 'duration': .2, 'ease': 'power2.out'}, a + .3)
        for j in range(k + 1, 4):
            to(f'#{i} .sc{j}', {'x': (j - k - 1) * 22, 'y': (j - k - 1) * 22, 'rotation': (j - k - 1) * 2, 'duration': .25}, a + .1)
    return f'<div class="stage"><div style="position:absolute;left:960px;top:460px">{h}</div></div>', ''

@fx('s7', 'nle-timeline', 'Edit timeline')
def e(i, s, d):
    def clip(x, w, txt, bg, fg='#141414'):
        return f'<div style="position:absolute;left:{x}px;width:{w}px;top:8px;bottom:8px;background:{bg};color:{fg};border-radius:8px;font-family:var(--mono);font-size:20px;display:flex;align-items:center;padding:0 16px;white-space:nowrap;overflow:hidden">{txt}</div>'
    tracks = [('Q1', clip(0, 520, 'onboarding checklist', '#F0EEE9') + clip(530, 400, 'site:example.com', '#A9B4FF')),
              ('Q2', clip(940, 300, '-template', '#FF8A6E')),
              ('F', clip(260, 1000, 'Tools › Past year', '#7FD1A3'))]
    rows = ''.join(f'<div style="display:flex;height:76px;border-top:1px solid #2E2D2B"><div class="mono" style="width:80px;color:#8d887f;font-size:18px;display:flex;align-items:center;padding-left:18px">{n}</div>'
                   f'<div style="position:relative;flex:1">{c}</div></div>' for n, c in tracks)
    ruler = ''.join(f'<span class="mono" style="position:absolute;left:{80 + k * 140}px;font-size:16px;color:#8d887f">00:{k * 2:02d}</span>' for k in range(10))
    ft(f'#{i} .ph', {'x': 0}, {'x': 1240, 'duration': d - .1, 'ease': 'none'}, s)
    J(f'(function(){{var o={{v:0}},el=document.querySelector("#{i} .tc");tl.fromTo(o,{{v:0}},{{v:{(d - .1) * 30:.0f},duration:{d - .1:.2f},ease:"none",onUpdate:function(){{var f=Math.round(o.v);el.textContent="00:00:"+String(Math.floor(f/30)).padStart(2,"0")+":"+String(f%30).padStart(2,"0");}}}},{s:.3f});}})();')
    return ('<div class="stage center"><div style="width:1460px;background:#1C1B1A;border:1px solid #2E2D2B;border-radius:22px;overflow:hidden">'
            '<div style="display:flex;justify-content:space-between;padding:20px 24px;font-family:var(--mono);font-size:20px"><span style="color:var(--paper)">Your search, edited</span><span class="tc" style="color:#A9B4FF">00:00:00:00</span></div>'
            f'<div style="position:relative;height:30px">{ruler}</div><div style="position:relative">{rows}'
            '<div class="ph" style="position:absolute;left:80px;top:-30px;bottom:0;width:3px;background:#FF5B36"></div></div></div></div>'), 'dark'

@fx('s8', 'titlecard-calm', 'Calm title card')
def e(i, s, d):
    ft(f'#{i} .k', {'autoAlpha': 0, 'y': 12}, {'autoAlpha': 1, 'y': 0, 'duration': .6, 'ease': 'power2.out'}, s + .1)
    ft(f'#{i} .h', {'autoAlpha': 0, 'y': 24}, {'autoAlpha': 1, 'y': 0, 'duration': .9, 'ease': 'power2.out'}, s + .3)
    return ('<div class="stage center" style="flex-direction:column;align-items:flex-start;padding-left:260px">'
            '<div class="k kicker">Before your next search</div><div class="h serif" style="font-size:280px;line-height:1">Save <i>this.</i></div></div>'), ''

@fx('s8', 'cover-story', 'Cover story')
def e(i, s, d):
    ft(f'#{i} .mast', {'yPercent': 100}, {'yPercent': 0, 'duration': .5, 'ease': 'power3.out'}, s + .05)
    ft(f'#{i} .cl', {'x': -30, 'autoAlpha': 0}, {'x': 0, 'autoAlpha': 1, 'duration': .3, 'stagger': .12}, s + .45)
    lines = [('Key words', 'beat full sentences'), ('Quotes', 'the exact-match trick'), ('site: and minus', 'explained in 9 seconds'), ('Made with', 'content-skills + 31 effects')]
    cl = ''.join(f'<div class="cl" style="border-top:2px solid var(--ink);padding-top:14px"><div style="font-size:40px;font-weight:700;letter-spacing:-.02em">{a}</div><div class="serif it" style="font-size:40px;color:var(--muted)">{b}</div></div>' for a, b in lines)
    return ('<div style="position:absolute;left:150px;right:150px;top:90px;bottom:150px">'
            '<div style="display:flex;justify-content:space-between;font-family:var(--mono);font-size:20px;border-bottom:2px solid var(--ink);padding-bottom:10px"><span>Vol. 01</span><span>A 60-second guide</span><span>October 2026</span></div>'
            '<div style="overflow:hidden"><div class="mast" style="font-weight:900;font-size:300px;letter-spacing:-.06em;line-height:.95">SEARCH<span class="serif it acc" style="font-weight:400;letter-spacing:-.02em"> smarter</span></div></div>'
            f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:40px;margin-top:40px">{cl}</div></div>'), ''

@fx('s8', 'orbit-couch-wall', 'Orbit camera')
def e(i, s, d):
    ft(f'#{i} .orb', {'rotationY': -26}, {'rotationY': 22, 'duration': d, 'ease': 'sine.inOut'}, s)
    tag = lambda txt, x, y, z, acc=False: (f'<div style="position:absolute;left:{x}px;top:{y}px;transform:translateZ({z}px);background:{"var(--accent)" if acc else "var(--card)"};color:{"#fff" if acc else "var(--ink)"};'
                                           f'border:1.5px solid var(--line);border-radius:999px;padding:16px 30px;font-size:34px;font-weight:600;white-space:nowrap">{txt}</div>')
    return ('<div class="stage" style="perspective:1500px"><div class="orb" style="position:absolute;left:360px;top:120px;width:1200px;height:700px;transform-style:preserve-3d">'
            '<div class="center" style="position:absolute;inset:0;background:var(--paper-2);border-radius:30px;flex-direction:column;transform:translateZ(-120px)">'
            '<div class="kicker">The pack</div><div class="serif" style="font-size:130px;line-height:1">Creator skills</div></div>'
            + tag('content-skills', 80, 90, 160, True) + tag('script beats', 820, 160, 240) + tag('31 motion effects', 200, 560, 200) + tag('HyperFrames demo', 820, 520, 120) + '</div></div>'), ''

@fx('s8', 'glass-hero', 'Glass lens')
def e(i, s, d):
    hero = ('<div class="center" style="position:absolute;left:0;top:0;width:1920px;height:930px;flex-direction:column">'
            '<div style="font-weight:900;font-size:250px;letter-spacing:-.06em;line-height:.9;text-align:center">SEARCH<br><span class="serif it acc" style="font-weight:400;letter-spacing:-.02em">smarter.</span></div>'
            '<div class="mono" style="font-size:24px;color:var(--muted);margin-top:40px">content-skills · 31 motion effects</div></div>')
    x0, x1, y0, y1 = 120, 1360, 180, 240
    ft(f'#{i} .lens', {'x': x0, 'y': y0}, {'x': x1, 'y': y1, 'duration': d, 'ease': 'sine.inOut'}, s)
    ft(f'#{i} .inner', {'x': -x0, 'y': -y0}, {'x': -x1, 'y': -y1, 'duration': d, 'ease': 'sine.inOut'}, s)
    return ('<div class="stage">' + hero +
            '<div class="lens" style="position:absolute;left:0;top:0;width:440px;height:440px;border-radius:50%;overflow:hidden;background:var(--card);'
            'box-shadow:inset 0 0 0 1.5px rgba(20,20,20,.18),inset 0 8px 30px rgba(255,255,255,.9),0 40px 70px -30px rgba(20,20,20,.4)">'
            '<div style="position:absolute;inset:0;transform:scale(1.18);transform-origin:220px 220px"><div class="inner" style="position:absolute;left:0;top:0">' + hero + '</div></div>'
            '<div style="position:absolute;left:70px;top:40px;width:160px;height:60px;border-radius:50%;background:rgba(255,255,255,.55);filter:blur(10px)"></div></div></div>'), ''

PLAN = {}
for beat, key, label, fn in FX:
    PLAN.setdefault(beat, []).append((key, label, fn))
assert sum(len(v) for v in PLAN.values()) == 30, sum(len(v) for v in PLAN.values())

SKILL = {
    's1': ('content-skills', 'Beat 1 · Hook'),
    's2': ('content-skills', 'Beat 2 · Problem'),
    's3': ('content-skills', 'Beat 3 · Solution'),
    's4': ('content-skills', 'Beat 3 · Solution'),
    's5': ('content-skills', 'Beat 3 · Solution'),
    's6': ('content-skills', 'Beat 4 · Pro tip'),
    's7': ('content-skills', 'Recap'),
    's8': ('content-skills', 'Beat 5 · CTA'),
}

scenes, labels, n = [], [], 0
for sid, items in PLAN.items():
    s0, d0, _ = T[sid]
    for k, (key, label, fn) in enumerate(items):
        n += 1
        s = round(s0 + d0 * k / len(items), 3)
        d = round(d0 / len(items), 3)
        i = f'e{n:02d}'
        body, mode = fn(i, s, d)
        scenes.append(f'<section class="fx {"dark" if mode == "dark" else "paper"}" id="{i}">{body}</section>')
        cut(f'#{i}', s, d)
        labels.append(f'<div class="fxlabel" id="fl{n:02d}"><b>{n:02d}/31</b>{label}</div>')
        cut(f'#fl{n:02d}', s, d)
    a, b = SKILL[sid]
    labels.append(f'<div class="skill" id="sk-{sid}"><b>{a}</b> {b}</div>')
    cut(f'#sk-{sid}', s0, d0)

# captions, one sentence at a time
caps = []
ci = 0
CAPFILE = 'vo/captions.json'
if os.path.exists(CAPFILE) and all(HAS_VO.values()):
    CL = json.load(open(CAPFILE))
    for k, (a, b, p) in enumerate(CL):
        ci += 1
        a0 = max(0.0, a - .05)
        b0 = min(b + .25, CL[k + 1][0] - .06) if k + 1 < len(CL) else min(b + .6, TOTAL)
        caps.append(f'<div class="cap" id="cap{ci}"><span>{html.escape(p)}</span></div>')
        cut(f'#cap{ci}', a0, b0 - a0)
    script_for_caps = []
else:
    script_for_caps = script
for sid, title, text in script_for_caps:
    s0, d0, _ = T[sid]
    parts = [p.strip() for p in re.split(r'(?<=[.?!])\s+', text) if p.strip()]
    vo = d0 - LEAD - TAIL
    tot = sum(len(p) for p in parts)
    c = s0 + LEAD
    for p in parts:
        pd = vo * len(p) / tot
        ci += 1
        caps.append(f'<div class="cap" id="cap{ci}"><span>{html.escape(p)}</span></div>')
        cut(f'#cap{ci}', c, pd - .05)
        c += pd

# grain overlay (#31) for the whole film, stepped so every frame is deterministic
J(f'tl.fromTo(".grain", {{x: 0, y: 0}}, {{x: -40, y: 30, duration: {TOTAL}, ease: "steps({int(TOTAL * 12)})"}}, 0);')
J(f'tl.fromTo(".progress i", {{scaleX: 0}}, {{scaleX: 1, duration: {TOTAL}, ease: "none"}}, 0);')

audio = ''.join(f'<audio id="vo-{sid}" src="vo/{sid}.wav" data-start="{round(T[sid][0] + LEAD, 3)}" data-duration="{round(dur(f'vo/{sid}.wav'), 3)}" data-volume="1"></audio>' for sid, _, _ in script if HAS_VO[sid])
css = open('style.css').read()

# ---- brand tokens: brand/brand.json (repo root) overrides the default palette and fonts ----
import os, pathlib
def find_brand():
    env = os.environ.get('BRAND_FILE')
    if env and pathlib.Path(env).exists():
        return pathlib.Path(env)
    for d in [pathlib.Path.cwd(), *pathlib.Path.cwd().parents]:
        f = d / 'brand' / 'brand.json'
        if f.exists():
            return f
    return None
BF = find_brand()
if BF:
    B = json.load(open(BF))
    c, f = B.get('colors', {}), B.get('fonts', {})
    keys = {'paper': '--paper', 'paper_2': '--paper-2', 'card': '--card', 'ink': '--ink', 'ink_2': '--ink-2', 'muted': '--muted',
            'line': '--line', 'accent': '--accent', 'accent_soft': '--accent-soft', 'signal': '--signal', 'ok': '--ok'}
    over = ''.join(f'{v}:{c[k]};' for k, v in keys.items() if c.get(k))
    fam = lambda name, fb: f"'{name}',{fb}" if name else None
    for k, v, fb in [('display', '--serif', 'Georgia,serif'), ('sans', '--sans', 'system-ui,sans-serif'), ('mono', '--mono', 'ui-monospace,monospace')]:
        if f.get(k):
            over += f'{v}:{fam(f[k], fb)};'
    imp = f"@import url('{f['google_fonts_css']}');" if f.get('google_fonts_css') else ''
    css = imp + css + ':root{' + over + '}'
    print('brand:', BF, '·', B.get('name', '?'))
WORDMARK = html.escape(json.load(open(BF)).get('name', '')) if BF and json.load(open(BF)).get('name') else 'Search <b>smarter</b>'
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<title>Search smarter in 60 seconds</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{css}</style>
</head>
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
</body>
</html>'''
open('index.html', 'w').write(page)

def mmss(x): return f'{int(x // 60)}:{x % 60:04.1f}'
L = ['# Search smarter in 60 seconds: voiceover transcript (16:9)', '',
     f'Length {TOTAL:.1f}s · 1920×1080 · voice: Kokoro TTS `am_michael`, generated locally · all 31 pack effects', '',
     '| Time | Beat | Voiceover | Skill guidance | Effects on screen |', '|---|---|---|---|---|']
for sid, title, text in script:
    s0, d0, _ = T[sid]
    a, b = SKILL[sid]
    L.append(f'| {mmss(s0)}–{mmss(s0 + d0)} | {title} | {text} | {a}: {b} | {", ".join(x[0] for x in PLAN[sid])} |')
L += ['', 'Under the whole video: grain-overlay (effect 31).', '', '## Plain transcript', ''] + [x[2] for x in script]
open('transcript.md', 'w').write('\n'.join(L) + '\n')
print('TOTAL', TOTAL, 'effects', n + 1)
