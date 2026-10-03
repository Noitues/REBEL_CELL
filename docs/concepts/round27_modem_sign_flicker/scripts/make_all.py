"""Round 27: build sign textures, render facade backdrops, composite stills, flicker GIFs, storyboard, compare.

python make_all.py            (everything; ~6 min)
python make_all.py --no-bg    (reuse scratch/bg_*.png)
"""
import functools
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import flicker_sign as FS   # noqa: E402
import render_bg            # noqa: E402

OUT = os.path.abspath(os.path.join(HERE, '..'))
SCR = os.path.join(OUT, 'scratch')
SPILL = '#5cff6a'                         # Cell lime spill (greener, so it doesn't go yellow on the brick)
PLATE_PX = (52, 26, 212)                  # plate x0, y0, x1 on the 1920x1080 facade (round 12 layout)
S = (PLATE_PX[2] - PLATE_PX[0]) / FS.PW   # canvas scale onto the facade
OFF = (PLATE_PX[0] - FS.MARGIN * S, PLATE_PX[1] - FS.MARGIN * S)
CROP = (0, 0, 600, 1080)                  # GIF / storyboard crop (sign, foyer, alley mouth)
GIF_SCALE = 0.5
FONT = 'C:/Windows/Fonts/bahnschrift.ttf'

OPTIONS = [  # key, layout, sequence, label
    ('market', 'market', 'market', 'MARKET NEON  (primary)'),
    ('market_more', 'market', 'market_more', 'MARKET NEON  (variant: partial A = o)'),
    ('neonmodem', 'neonmodem', 'neonmodem', 'NEON MODEM / REPAIR & MAINTENANCE'),
    ('repairs', 'repairs', 'repairs', 'REPAIRS / SECURE UPGRADES'),
    ('techhelp', 'techhelp', 'techhelp', 'TECH HELP / CELL / REPAIR  (own idea)'),
]


def f32(p):
    return np.asarray(Image.open(p).convert('RGB'), np.float32) / 255.0


def composite(bgs, a, b, res):
    """bgs = (dark, normal, take) float images; a = normal light, b = takeover light; res = sign render."""
    dark, nor, tak = bgs
    bg = np.clip(dark + a * (nor - dark) + b * (tak - dark), 0, 1)
    w, h = FS.CW * S, FS.CH * S
    size = (int(round(w)), int(round(h)))
    plate = Image.fromarray((np.clip(res['plate'], 0, 1) * 255).astype(np.uint8)).resize(size, Image.LANCZOS)
    alpha = Image.fromarray((np.clip(res['alpha'], 0, 1) * 255).astype(np.uint8)).resize(size, Image.LANCZOS)
    glow = np.stack([np.asarray(Image.fromarray(res['glow'][..., c].astype(np.float32), 'F').resize(size, Image.BILINEAR))
                     for c in range(3)], -1)
    ox, oy = int(round(OFF[0])), int(round(OFF[1]))
    x0, y0 = max(0, ox), max(0, oy)
    x1, y1 = min(1920, ox + size[0]), min(1080, oy + size[1])
    sx, sy = x0 - ox, y0 - oy
    reg = bg[y0:y1, x0:x1]
    p = np.asarray(plate, np.float32)[sy:sy + (y1 - y0), sx:sx + (x1 - x0)] / 255.0
    al = np.asarray(alpha, np.float32)[sy:sy + (y1 - y0), sx:sx + (x1 - x0), None] / 255.0
    g = glow[sy:sy + (y1 - y0), sx:sx + (x1 - x0)]
    reg = reg * (1 - al) + p * al
    reg = 1 - (1 - reg) * (1 - np.clip(g * 0.35, 0, 1))
    bg[y0:y1, x0:x1] = reg
    return bg


def to_img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


# ------------------------------------------------------------------ sequence (frame states)
def sequence(sign, seq_key, rng, loops=2, fps=12):
    """[(label, render_kwargs, a, b)] frames: normal -> stutter -> dead drop out -> words loop -> flash back."""
    keys = sign.keys
    words = sign.words(seq_key)
    used = sign.used_keys(seq_key)
    dead = set(keys) - used
    nref = max(len(mk) for _, mk in words)
    fr = []
    for i in range(12):                                   # normal, data pulses running
        fr.append(('NORMAL', dict(normal={k: 1.0 for k in keys}, frame=1.0, traces=1.0, pulse_t=i / fps), 1.0, 0.0))
    for i in range(10):                                   # stutter: the takeover virus hits the controller
        lv = {}
        for k in keys:
            r = rng.random()
            lv[k] = 1.0 if r < 0.45 else (0.0 if r < 0.7 else ('f', rng.uniform(0.3, 0.8)))
        a = np.mean([1.0 if v == 1.0 else (v[1] * 0.5 if isinstance(v, tuple) else 0.0) for v in lv.values()])
        fr.append(('STUTTER', dict(normal=lv, frame=rng.choice([0.0, 1.0, 0.4]), traces=rng.uniform(0.2, 1.0)), a, 0.0))
    order = sorted(keys, key=lambda k: (k in used, rng.random()))   # dead letters drop out first
    for i in range(4):
        n_off = int(len(order) * (i + 1) / 4)
        lv = {k: 1.0 for k in order[n_off:]}
        fr.append(('DROP OUT', dict(normal=lv, frame=0.0 if i > 1 else 0.5, traces=0.5 - 0.1 * i,
                                    broken=set(order[:n_off]) & dead), len(lv) / len(keys), 0.0))
    fr.append(('DARK', dict(frame=0.0, traces=0.1, trace_col=FS.TRACE_RED, broken=dead), 0.0, 0.0))
    fr.append(('DARK', dict(frame=0.0, traces=0.15, trace_col=FS.TRACE_RED, broken=dead), 0.0, 0.0))
    for lp in range(loops):
        for wi, (w, mk) in enumerate(words):
            for j in range(9):                            # word holds ~0.75 s, one tube hums
                lvl = 1.0
                hum = None
                if j in (3, 6) and rng.random() < 0.6:
                    hum = rng.choice(list(mk))
                m = dict(mk)
                kw = dict(msg=m, frame=0.0, traces=0.22, trace_col=FS.TRACE_RED, broken=dead, msg_level=lvl)
                if hum:   # a single letter of the word dips
                    kw['normal'] = {}
                    m2 = {k: v for k, v in m.items() if k != hum}
                    kw['msg'] = m2
                fr.append((w, kw, 0.0, len(kw['msg']) / nref))
            for j in range(3):                            # stutter between words
                cand = list(mk) + list(words[(wi + 1) % len(words)][1])
                m = {k: (mk.get(k) if k in mk else words[(wi + 1) % len(words)][1].get(k))
                     for k in cand if rng.random() < 0.35}
                fr.append(('STUTTER', dict(msg=m, frame=0.0, traces=0.15, trace_col=FS.TRACE_RED, broken=dead,
                                           msg_level=rng.uniform(0.3, 0.9)), 0.0, len(m) / nref * 0.6))
        if lp == loops - 1:
            for j, lvl in enumerate((1.0, 0.0, 0.8)):     # the old sign flickers back for a moment
                fr.append(('FLASH BACK', dict(normal={k: lvl for k in keys}, frame=lvl, traces=lvl), lvl, 0.0))
    return fr


def make_gif(frames_img, path, fps=12, scale=GIF_SCALE):
    small = [im.crop(CROP).resize((int((CROP[2] - CROP[0]) * scale), int((CROP[3] - CROP[1]) * scale)),
                                  Image.LANCZOS) for im in frames_img]
    picks = small[::max(1, len(small) // 12)]          # palette from frames across the whole sequence
    mont = Image.new('RGB', (picks[0].width * len(picks), picks[0].height))
    for i, im in enumerate(picks):
        mont.paste(im, (i * picks[0].width, 0))
    pal = mont.quantize(colors=160, method=Image.MEDIANCUT)
    q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in small]
    q[0].save(path, save_all=True, append_images=q[1:], duration=int(1000 / fps), loop=0, optimize=True,
              disposal=1)
    return os.path.getsize(path)


def label(d, xy, text, size=26, fill=(235, 228, 220)):
    d.text(xy, text, font=ImageFont.truetype(FONT, size), fill=fill)


print = functools.partial(print, flush=True)   # noqa: A001  (log progress unbuffered)


def main():
    os.makedirs(SCR, exist_ok=True)
    signs = {}
    tex = {}
    for key, lay, seq, _ in OPTIONS:
        if lay not in signs:
            signs[lay] = FS.FlickerSign(lay)
        s = signs[lay]
        words = s.words(seq)
        wi = max(range(len(words)), key=lambda i: len(words[i][1]))
        pn = os.path.join(SCR, 'tex_%s_normal.png' % key)
        pt = os.path.join(SCR, 'tex_%s_take.png' % key)
        FS.save_rgba(s.state_normal(), pn)
        FS.save_rgba(s.state_word(seq, wi), pt)
        tex[key] = (pn, pt, len(words[wi][1]))
    pdark = os.path.join(SCR, 'tex_dark.png')
    sm = signs['market']
    FS.save_rgba(sm.render(frame=0.0, traces=0.12, trace_col=FS.TRACE_RED,
                           broken=set(sm.keys) - sm.used_keys('market')), pdark)
    if '--no-bg' not in sys.argv:
        take_only = '--take-only' in sys.argv
        if not take_only:
            render_bg.render('dark', pdark, '-', 0.0)
        for key, *_ in OPTIONS:
            pn, pt, n = tex[key]
            if not take_only:
                render_bg.render(key + '_normal', pn, '-', 1.0)
            render_bg.render(key + '_take', pt, SPILL, 0.025 + 0.01 * n)   # a few letters: a faint lime wash
    dark = f32(os.path.join(SCR, 'bg_dark.png'))
    font_rows = []
    for key, lay, seq, title in OPTIONS:
        s = signs[lay]
        bgs = (dark, f32(os.path.join(SCR, 'bg_%s_normal.png' % key)), f32(os.path.join(SCR, 'bg_%s_take.png' % key)))
        nref = tex[key][2]
        words = s.words(seq)
        used = s.used_keys(seq)
        dead = set(s.keys) - used
        stills = [('NORMAL', composite(bgs, 1.0, 0.0, s.state_normal()))]
        for wi, (w, mk) in enumerate(words):
            stills.append((w, composite(bgs, 0.0, len(mk) / nref, s.state_word(seq, wi))))
        primary = key.startswith('market')
        for name, im in stills:
            fn = '%s_%s' % (key, 'normal' if name == 'NORMAL' else 'takeover_' + name.lower())
            if primary:
                to_img(im).save(os.path.join(OUT, fn + '.png'), optimize=True)
            else:
                to_img(im).save(os.path.join(OUT, fn + '.jpg'), quality=90)
        font_rows.append((title, [(n, to_img(im)) for n, im in stills]))
        # flicker sequence GIF
        rng = random.Random('seq_' + key)
        seqf = sequence(s, seq, rng, loops=2 if primary else 1)
        frames = []
        for lab, kw, a, b in seqf:
            frames.append(to_img(composite(bgs, a, min(1.0, b), s.render(**kw))))
        gname = {'market': 'market_neon_sequence.gif', 'market_more': 'market_neon_more_sequence.gif'}.get(
            key, '%s_sequence.gif' % key)
        size = make_gif(frames, os.path.join(OUT, gname), scale=GIF_SCALE if primary else 0.42)
        print(gname, len(frames), 'frames', round(size / 1e6, 2), 'MB')
        if primary:   # storyboard strip
            picks, seen = [], set()
            for i, (lab, *_r) in enumerate(seqf):
                tag = lab if lab not in seen else None
                if tag and lab != 'DARK':
                    seen.add(lab)
                    picks.append((lab, frames[min(i + 2, len(frames) - 1)] if lab in ('STUTTER', 'DROP OUT') else frames[i]))
            tw, th = 300, 540
            strip = Image.new('RGB', (len(picks) * (tw + 10) + 10, th + 70), (18, 17, 22))
            d = ImageDraw.Draw(strip)
            for i, (lab, im) in enumerate(picks):
                strip.paste(im.crop(CROP).resize((tw, th), Image.LANCZOS), (10 + i * (tw + 10), 54))
                label(d, (14 + i * (tw + 10), 14), '%d  %s' % (i + 1, lab))
            strip.save(os.path.join(OUT, '%s_storyboard.jpg' % ('market_neon' if key == 'market' else 'market_neon_more')),
                       quality=88)
    # options compare: rows = options, cols = normal + words
    tw, th = 260, 468
    ncol = max(len(r[1]) for r in font_rows)
    W = 330 + ncol * (tw + 10) + 10
    Hh = 50 + len(font_rows) * (th + 60)
    sheet = Image.new('RGB', (W, Hh), (18, 17, 22))
    d = ImageDraw.Draw(sheet)
    for r, (title, ims) in enumerate(font_rows):
        y = 40 + r * (th + 60)
        label(d, (14, y + 4), title.replace('  (', '\n('), size=24)
        for c, (n, im) in enumerate(ims):
            x = 330 + c * (tw + 10)
            sheet.paste(im.crop((0, 0, 330, 594)).resize((tw, th), Image.LANCZOS), (x, y + 34))
            label(d, (x + 4, y + 4), n if n == 'NORMAL' else '%d. %s' % (c, n), size=24,
                  fill=(235, 228, 220) if n == 'NORMAL' else (170, 255, 90))
    sheet.save(os.path.join(OUT, 'signs_compare.jpg'), quality=88)
    print('signs_compare.jpg', sheet.size)


if __name__ == '__main__':
    main()
