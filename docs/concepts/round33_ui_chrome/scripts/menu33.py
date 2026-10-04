"""Round 33 special stickers for the locked title option A.

- glitch_sticker: DISABLE with the CORRUPTED language (pink + green glitch lines, sliced and shifted
  bands) inside the die-cut; the cut line itself never glitches, so the word keeps its silhouette.
- fist_word_sticker: OVERTHROW in a readable blue with its last O replaced by a red rebel fist
  (REBEL_CELL red #E8141E), keyline and extrude like every other letter.
Same build as sticker_lib31 (Anton keyline + extrude + white die-cut, SS = 2).
"""
import math
import random

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageFilter

import sticker_lib31 as SL
import ui31 as U

FILL_BLUE = ('grad', (132, 200, 255), (34, 104, 232))
FIST_RED = (232, 20, 30)
GLITCH_PINK = (255, 61, 168)
GLITCH_GREEN = (60, 255, 140)


def fist_mask(w, h):
    """Raised rebel fist, front view, as an L mask w x h (SS px). The gaps between the fingers and
    around the thumb are left open so the ink keyline shows through them as drawing lines."""
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    g = max(2, int(w * 0.045))                      # gap = ink line width
    fw = w * 0.96
    x0 = (w - fw) / 2
    fh = h * 0.30                                   # finger row height
    kw = (fw - 3 * g) / 4
    for k in range(4):                              # four fingers, the middle two a touch higher
        lift = h * (0.035 if k in (1, 2) else 0.0)
        fx = x0 + k * (kw + g)
        d.rounded_rectangle([fx, h * 0.04 - lift, fx + kw, h * 0.04 + fh], kw * 0.45, fill=255)
    # palm block under the fingers (behind the thumb)
    d.rounded_rectangle([x0, h * 0.04 + fh * 0.6, x0 + fw, h * 0.60], fw * 0.10, fill=255)
    # thumb across the front, separated by a gap line
    ty0 = h * 0.04 + fh + g * 0.5
    d.rectangle([x0 + fw * 0.06, ty0, x0 + fw * 0.94, ty0 + g], fill=0)
    d.rounded_rectangle([x0 + fw * 0.06, ty0 + g, x0 + fw * 0.80, h * 0.56], (h * 0.56 - ty0) * 0.45, fill=255)
    d.line([(x0 + fw * 0.80 + g, ty0 + g), (x0 + fw * 0.80 + g, h * 0.56)], fill=0, width=g)
    # wrist + forearm, with a cuff line
    aw = fw * 0.66
    ax0 = (w - aw) / 2
    d.polygon([(ax0, h * 0.58), (ax0 + aw, h * 0.58), (ax0 + aw * 0.97, h), (ax0 + aw * 0.03, h)], fill=255)
    d.rectangle([x0, h * 0.60, x0 + fw, h * 0.60 + g], fill=0)
    return m


def lettering_sub(text, size, fill, sub=None, key_w=5, extrude=7, seed=7, jitter=2.0, track=-1, pad=90):
    """One line of sticker lettering; `sub` maps a character to (mask_fn(w, h), (r, g, b)) to draw a
    pictogram in that letter's slot with its own fill."""
    S = SL.SS
    rng = random.Random(seed)
    font = ImageFont.truetype(U.ANTON, int(size * S))
    asc, desc = font.getmetrics()
    kw = int(key_w * S)
    m = kw + 12 * S
    sub = sub or {}
    glyphs = []
    x = 0
    for ch in text:
        if ch in sub:
            ref = 'O'
            adv = font.getlength(ref) * 1.18
        else:
            adv = font.getlength(ch)
        bw, bh = int(adv + 2 * m), int(asc + desc + 2 * m)
        fm = Image.new('L', (bw, bh), 0)
        if ch in sub:
            bb = font.getbbox('O', anchor='ls')
            gh = int((bb[3] - bb[1]) * 1.16)
            gw = int(adv * 0.98)
            gm = sub[ch][0](gw, gh)
            fm.paste(gm, (int(m + (adv - gw) / 2), int(m + asc - gh + (bb[3] - bb[1]) * 0.06)))
        else:
            ImageDraw.Draw(fm).text((m, m + asc), ch, font=font, fill=255, anchor='ls')
        km = SL.dilate(fm, kw) if ch in sub else None
        if km is None:
            km = Image.new('L', (bw, bh), 0)
            ImageDraw.Draw(km).text((m, m + asc), ch, font=font, fill=255, anchor='ls', stroke_width=kw, stroke_fill=255)
        ang = rng.uniform(-jitter, jitter)
        dy = rng.uniform(-0.03, 0.03) * size * S
        glyphs.append((ch, fm.rotate(ang, Image.BICUBIC), km.rotate(ang, Image.BICUBIC), x - m, dy - m))
        x += adv + track * S
    W = int(x - track * S) + 2 * m
    P = int(pad * S)
    CW, CH = W + 2 * P, int(asc + desc + 2 * m) + 2 * P
    fill_main = Image.new('L', (CW, CH), 0)
    key_all = Image.new('L', (CW, CH), 0)
    subs = []
    for ch, fm, km, gx, gy in glyphs:
        ox, oy = int(P + m + gx), int(P + m + gy)
        t = Image.new('L', (CW, CH), 0)
        t.paste(km, (ox, oy))
        key_all = ImageChops.lighter(key_all, t)
        t = Image.new('L', (CW, CH), 0)
        t.paste(fm, (ox, oy))
        if ch in sub:
            subs.append((t, sub[ch][1]))
        else:
            fill_main = ImageChops.lighter(fill_main, t)
    art = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    ext = Image.new('L', (CW, CH), 0)
    for i in range(1, int(extrude * S) + 1, 2):
        ext = ImageChops.lighter(ext, SL.shift(key_all, i * 0.55, i))
    art = SL.over(art, SL.INK_DEEP, ext)
    art = SL.over(art, SL.INK, key_all)
    layers = [(fill_main, fill)] + [(t, c) for t, c in subs]
    for fmask, f in layers:
        if isinstance(f, tuple) and f and f[0] == 'grad':
            tex = SL.vgrad_tex(CW, CH, f[1], f[2])
        else:
            top = tuple(min(255, int(c * 1.15 + 20)) for c in f)
            tex = SL.vgrad_tex(CW, CH, top, tuple(f))
        lay = tex.copy()
        lay.putalpha(fmask)
        art = Image.alpha_composite(art, lay)
        hl = ImageChops.subtract(fmask, SL.shift(fmask, 0, 3 * S)).filter(ImageFilter.GaussianBlur(0.8 * S))
        art = SL.over(art, (255, 255, 255), SL.scale_mask(hl, 0.55))
        sh = ImageChops.subtract(fmask, SL.shift(fmask, 0, -3 * S)).filter(ImageFilter.GaussianBlur(0.8 * S))
        art = SL.over(art, (0, 0, 0), SL.scale_mask(sh, 0.28))
    return art, fill_main


def fist_word_sticker(word='OVERTHR@W', size=60, seed=52, gloss_k=0.22, gloss_pos=0.32):
    art, _ = lettering_sub(word, size, FILL_BLUE, sub={'@': (fist_mask, FIST_RED)}, seed=seed)
    return SL.build_sticker(art, border=12, gloss_k=gloss_k, gloss_pos=gloss_pos, seed=seed)


def glitch_art(art, fill_mask, phase=0, strength=1.0):
    """CORRUPTED glitch on the lettering only: sliced horizontal bands shifted sideways, pink and
    green split copies of the letter fill, and thin pink/green scan lines across the letters."""
    S = SL.SS
    rng = random.Random(1000 + phase)
    w, h = art.size
    bb = fill_mask.getbbox()
    out = art.copy()
    if strength > 0:
        # pink / green split ghosts of the fill, offset sideways
        for col, dx in ((GLITCH_PINK, -3 * S * strength), (GLITCH_GREEN, 3 * S * strength)):
            g = SL.shift(fill_mask, dx, 0)
            g = ImageChops.subtract(g, fill_mask)
            out = SL.over(out, col, SL.scale_mask(g, 0.95))
        # shifted bands
        for _ in range(int(3 * strength - 0.5)):
            y0 = rng.randint(bb[1], bb[3] - 6 * S)
            bh = rng.randint(3 * S, 9 * S)
            dx = int(rng.choice([-1, 1]) * rng.randint(3, 7) * S * strength)
            band = out.crop((0, y0, w, y0 + bh))
            out.paste(band, (dx, y0), band)
        # thin pink / green lines over the letters only
        lines = Image.new('L', (w, h), 0)
        lg = Image.new('L', (w, h), 0)
        d1, d2 = ImageDraw.Draw(lines), ImageDraw.Draw(lg)
        for k in range(int(2 + 2 * strength)):
            y = rng.randint(bb[1], bb[3])
            (d1 if k % 2 == 0 else d2).rectangle([bb[0], y, bb[2], y + rng.randint(1, 2) * S], fill=255)
        letters = SL.dilate(fill_mask, 2 * S)
        out = SL.over(out, GLITCH_PINK, ImageChops.multiply(lines, letters))
        out = SL.over(out, GLITCH_GREEN, ImageChops.multiply(lg, letters))
    return out


def glitch_sticker_set(word='DISABLE', size=60, seed=51, phases=(0,)):
    """Returns {phase: sticker dict}. Phase -1 = calm frame (split ghosts only, strength 0.4)."""
    art, fm = lettering_sub(word, size, ('grad', (250, 250, 246), (206, 210, 220)), seed=seed)
    # die-cut from the un-glitched art so the cut line stays still
    base = SL.build_sticker(art, border=12, gloss_k=0.22, seed=seed)
    out = {}
    for ph in phases:
        st = 0.6 if ph < 0 else 1.0
        g = glitch_art(art, fm, phase=max(0, ph), strength=st)
        sd = SL.build_sticker(_pad(g), border=12, gloss_k=0.22, seed=seed, body=base['body'])
        out[ph] = sd
    return out


def _pad(art):
    """Pad like build_sticker does when it cuts its own body (border 12, close 1.6 x border)."""
    extra = int((12 + 12 * 1.6 + 12) * SL.SS)
    out = Image.new('RGBA', (art.size[0] + 2 * extra, art.size[1] + 2 * extra), (0, 0, 0, 0))
    out.paste(art, (extra, extra))
    return out
