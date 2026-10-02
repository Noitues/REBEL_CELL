"""Round 19: the locked card-play PREVIEW (round 17 corp wheels, preview17.py) drawn on the D4 boss in screen
space: one chevron chase outside the rim from the top needle to its landing, a ghost blade at the landing
(dashed, with its index tab and the value it will read) and a dashed outline of the landing slice.

Angles are degrees clockwise from the top (the wheel convention); the slices turn clockwise with a spin, so
the top needle reads the slice that is N ticks ANTICLOCKWISE of it.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import plates as P
from slicelib import f_num, f_ui, PROGRAMS

YEL = (255, 214, 64)
WHITE = (255, 255, 255)
INK = (10, 8, 16)
C = P.BOSS["c"]
R = P.BOSS["r"]


def pt(r, a, c=C):
    return (c[0] + r * math.sin(math.radians(a)), c[1] - r * math.cos(math.radians(a)))


def chevron(d, a, r, size, alpha, direction=-1):
    """A large chevron at angle a on radius r, pointing along the travel direction (anticlockwise = -1)."""
    w = size
    da = math.degrees(w / r)
    tip = pt(r, a + direction * da * 0.55)
    l0, l1 = pt(r + w * 0.62, a - direction * da * 0.45), pt(r - w * 0.62, a - direction * da * 0.45)
    m0, m1 = pt(r + w * 0.62, a - direction * da * 1.0), pt(r - w * 0.62, a - direction * da * 1.0)
    notch = pt(r, a)
    poly = [l0, tip, l1, m1, notch, m0]
    col = tuple(int(WHITE[i] * (1 - alpha) + YEL[i] * alpha) for i in range(3))
    d.polygon(poly, fill=col + (int(50 + 205 * alpha),), outline=INK + (int(90 + 165 * alpha),), width=3)


def dashed(d, pts, col, width, dash=12, gap=8, closed=True):
    seq = pts + ([pts[0]] if closed else [])
    carry = 0.0
    on = True
    for (x0, y0), (x1, y1) in zip(seq, seq[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        s = 0.0
        while s < L:
            step = (dash if on else gap) - carry
            e = min(L, s + step)
            if on:
                d.line([(x0 + (x1 - x0) * s / L, y0 + (y1 - y0) * s / L), (x0 + (x1 - x0) * e / L, y0 + (y1 - y0) * e / L)], fill=col, width=width)
            if e - s < step:
                carry += e - s
                break
            carry = 0.0
            s = e
            on = not on


def wedge(a0, a1, r0, r1, n=30):
    o = [pt(r1, a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    o += [pt(r0, a1 - (a1 - a0) * i / n) for i in range(n + 1)]
    return o


def ghost_blade(img, a, alpha, value, prog_col, index=1):
    """Dashed ghost of the D4 blade at angle a: tip on the rim, window outside with the value it will read."""
    s = Image.new("RGBA", (120, 170), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    cx = 60
    blade = [(cx, 168), (cx - 24, 92), (cx - 30, 92), (cx - 30, 10), (cx + 30, 10), (cx + 30, 92), (cx + 24, 92)]
    d.polygon(blade, fill=prog_col + (70,))
    dashed(d, blade, WHITE + (255,), 4, dash=10, gap=6)
    f = f_num(40)
    tw = f.getlength(value)
    d.text((cx - tw / 2, 26), value, font=f, fill=WHITE + (255,), stroke_width=2, stroke_fill=INK + (255,))
    d.rounded_rectangle([cx + 16, 0, cx + 40, 22], radius=4, fill=YEL + (255,), outline=INK + (255,), width=2)
    d.text((cx + 23, -1), str(index), font=f_ui(18, b"Bold Condensed"), fill=INK + (255,))
    if alpha < 1:
        s.putalpha(s.split()[3].point(lambda v: int(v * alpha)))
    s = s.resize((int(s.width * 1.3), int(s.height * 1.3)), Image.BICUBIC)
    s = s.rotate(-a, resample=Image.BICUBIC, expand=True)
    mid = pt(R * 1.0 + 85 * 1.3 * 0.94, a)  # sprite centre: tip (y=168) sits on the rim
    img.alpha_composite(s, (int(mid[0] - s.width / 2), int(mid[1] - s.height / 2)))


def label(d, xy, text, sub=None, col=YEL, size=24, anchor="lm"):
    f = f_num(size)
    fs = f_ui(15, b"Bold SemiCondensed")
    tw = max(f.getlength(text), fs.getlength(sub) if sub else 0)
    h = size + (20 if sub else 0) + 12
    x, y = xy
    x0 = x if anchor == "lm" else x - tw - 20
    y0 = y - h / 2
    d.rounded_rectangle([x0, y0, x0 + tw + 20, y0 + h], radius=7, fill=(10, 9, 16, 235), outline=col + (255,), width=2)
    d.text((x0 + 10, y0 + 4), text, font=f, fill=col + (255,))
    if sub:
        d.text((x0 + 10, y0 + size + 8), sub, font=fs, fill=(200, 200, 215, 255))


def draw(img, chase=None, ghosts=0.0, rot=0.0, n=9, labels=False, chev_alpha=1.0, landing=("EXPLOIT", 14, 4)):
    """chase: 0..1 chevron chase (None = off; >=1 = held, all ghosted); ghosts: 0..1 ghost fade;
    rot: the wheel's current spin (the ghost rides with the slices and meets the real blade at rot = 12 n)."""
    a_land = -12.0 * n
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if chase is not None and chev_alpha > 0.01:
        R_ch = R * 1.40
        head = chase * (n + 1.5)
        for j in range(n):
            a = -12 * (j + 0.6)
            if chase >= 1.0:
                al = 0.5
            else:
                dist = head - (j + 1)
                al = 0.18 + 0.82 * math.exp(-(dist / 1.1) ** 2) if dist > -1.5 else 0.10
                if dist > 1.5:
                    al = max(al, 0.5)
            chevron(d, a, R_ch, 46, al * chev_alpha)
        lay.putalpha(lay.split()[3].point(lambda v: int(v * chev_alpha)))
    if ghosts > 0.01:
        prog, val, slot = landing
        pc = PROGRAMS[prog]["col"]
        a0 = slot * 60 - 30 + rot
        g = Image.new("RGBA", img.size, (0, 0, 0, 0))
        gl = Image.new("RGBA", img.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        wp = wedge(a0 + 1.2, a0 + 60 - 1.2, R * 0.39, R * 0.97)
        ImageDraw.Draw(gl).line(wp + [wp[0]], fill=pc + (255,), width=10)
        dashed(gd, wp, pc + (255,), 4, dash=12, gap=8)
        ghost_blade(g, a_land + rot, 1.0, str(val), pc, 1)
        g.alpha_composite(gl.filter(ImageFilter.GaussianBlur(6)), (0, 0))
        g.putalpha(g.split()[3].point(lambda v: int(v * ghosts)))
        lay.alpha_composite(g)
        if labels:
            p = pt(R * 1.55, a_land + rot)
            label(ImageDraw.Draw(lay), (p[0] - 20, p[1] + 34), "1 LANDS HERE", "%s %d after SPIN 9" % (prog, val), anchor="rm", size=22)
    if labels:
        label(ImageDraw.Draw(lay), (C[0] - 250, C[1] - R * 1.42), "SPIN 9: the wheel turns 9 ticks", "chevrons = the needle's path to its landing", anchor="rm", size=20)
    img.alpha_composite(lay)
    return img
