"""Boss Wheel v2: the VERDICT hand, an original emoji-STYLE thumbs-down (Aurelian Concord boss emblem).

One drawing, used twice: the boss emblem and the needle rig's hand (the emperor's arm in the royal box).
Chunky cartoon fist, thumb down, flat shading with one highlight, a thick ink outline, a gold laurel cuff and an
imperial-purple sleeve edge. Drawn procedurally (no platform emoji art is copied).

hand_rgba(px, gesture) -> RGBA (px x px). gesture: -1 = thumb down (rest of the drawing), 0 = sideways, 1 = up.
The wrist pivot is at unit (200, 96) of the 400-unit box; rotation turns the whole hand about it (a wrist roll).
"""
import math

from PIL import Image, ImageChops, ImageDraw

import bw_kit as K
from shapes import Pen

SKIN = (255, 204, 140)
SKIN_SH = (226, 150, 96)
INK = (26, 14, 22)
PURPLE = (112, 34, 120)
PURPLE_SH = (78, 18, 86)
GOLD = (246, 196, 70)
GOLD_SH = (196, 132, 30)
PIVOT = (200, 96)


def _parts(k, size):
    P = {n: Pen(size, k) for n in ("sleeve", "stripe", "cuff", "leaves", "palm", "fingers", "thumb", "nail", "lines", "leaf_lines", "hi")}
    # sleeve edge (toga) with a gold stripe
    P["sleeve"].rrect(112, 6, 288, 84, 18)
    P["stripe"].rrect(112, 60, 288, 72, 3)
    # gold laurel cuff: leaves overlapping round the wrist
    P["cuff"].rrect(116, 80, 284, 130, 14)
    for j in range(4):                        # big laurel leaves round the wrist, two rows, tips to the right
        for row, (yy, ang) in enumerate(((95, -22), (116, 22))):
            x = 140 + j * 38 + row * 10
            P["leaves"].ell(x, yy, 25, 11, ang=ang)
            P["leaf_lines"].line([(x - 16 * math.cos(math.radians(ang)), yy - 16 * math.sin(math.radians(ang))),
                                  (x + 16 * math.cos(math.radians(ang)), yy + 16 * math.sin(math.radians(ang)))], 3.0)
    # palm block + four finger rolls stacked on the right + the thumb pointing down on the left
    P["palm"].rrect(104, 118, 268, 300, 54)
    for j in range(4):
        y0 = 124 + j * 44
        P["fingers"].rrect(196, y0, 322, y0 + 50, 25)
        if j < 3:
            P["lines"].line([(214, y0 + 49), (314, y0 + 49)], 7)
    P["thumb"].rrect(104, 230, 186, 386, 41)
    P["nail"].rrect(118, 330, 172, 374, 18)
    P["lines"].line([(110, 270), (180, 270)], 6)        # thumb knuckle crease
    P["hi"].ell(150, 170, 26, 34, ang=-20)
    return {n: p.m for n, p in P.items()}


def hand_rgba(px, gesture=-1.0, outline=13.0, ss=2, pivot_centre=False, pivot=None, swing=1.0):
    """The emoji hand at px. gesture rotates the hand about the wrist: -1 down (0 deg), 0 sideways, 1 up (180 deg).
    pivot_centre=True returns a 2x canvas with the wrist pivot at its centre (no clipping when rotated)."""
    W_ = px * ss
    k = W_ / 400
    size = (W_, W_)
    m = _parts(k, size)
    body = m["palm"]
    for n in ("fingers", "thumb", "cuff", "sleeve"):
        body = ImageChops.lighter(body, m[n])
    out = K.rgba(size)
    out.alpha_composite(K.solid(K.grow(body, outline * k), INK))

    def flat(mask, base, shade, dx=-10, dy=-12):
        lay = K.solid(mask, base)
        sh = ImageChops.subtract(mask, K.shifted(mask, dx * k, dy * k))
        lay.alpha_composite(K.solid(sh, shade))
        return lay
    out.alpha_composite(flat(m["sleeve"], PURPLE, PURPLE_SH))
    out.alpha_composite(K.solid(m["stripe"], GOLD))
    out.alpha_composite(K.solid(m["cuff"], GOLD_SH))
    lv = K.mask_mul(m["leaves"], K.grow(m["cuff"], 4 * k))
    out.alpha_composite(K.solid(K.grow(lv, 3.5 * k), INK))
    out.alpha_composite(flat(lv, GOLD, GOLD_SH, dx=-4, dy=-5))
    out.alpha_composite(K.solid(K.mask_mul(m["leaf_lines"], lv), GOLD_SH))
    # palm first, then the thumb, then the finger rolls each with its own ink edge so they stack
    out.alpha_composite(flat(m["palm"], SKIN, SKIN_SH))
    th_edge = ImageChops.subtract(K.grow(m["thumb"], 6 * k), m["thumb"])
    out.alpha_composite(K.solid(K.mask_mul(th_edge, m["palm"]), INK))
    out.alpha_composite(flat(m["thumb"], SKIN, SKIN_SH))
    out.alpha_composite(K.solid(m["nail"], (255, 232, 214)))
    nail_edge = ImageChops.subtract(K.grow(m["nail"], 4 * k), m["nail"])
    out.alpha_composite(K.solid(nail_edge, SKIN_SH))
    f_edge = ImageChops.subtract(K.grow(m["fingers"], 7 * k), m["fingers"])
    out.alpha_composite(K.solid(K.mask_mul(f_edge, ImageChops.lighter(m["palm"], m["thumb"])), INK))
    out.alpha_composite(flat(m["fingers"], SKIN, SKIN_SH, dx=-6, dy=-10))
    out.alpha_composite(K.solid(m["lines"], INK))
    out.alpha_composite(K.solid(m["hi"], (255, 255, 255), 0.55))
    # sleeve / cuff separation line
    d = ImageDraw.Draw(out)
    d.line([(116 * k, 80 * k), (284 * k, 80 * k)], fill=INK + (255,), width=max(1, int(6 * k)))
    ang = (gesture + 1) * 90.0 * swing  # -1 -> 0 deg, 1 -> 180 deg (swing -1 turns the other way)
    pv = pivot or PIVOT
    if pivot_centre:
        big = K.rgba((W_ * 2, W_ * 2))
        big.alpha_composite(out, (int(W_ - pv[0] * k), int(W_ - pv[1] * k)))
        if ang:
            big = big.rotate(-ang, resample=Image.BICUBIC)
        return big.resize((px * 2, px * 2), Image.LANCZOS)
    if ang:
        out = out.rotate(-ang, resample=Image.BICUBIC, center=(PIVOT[0] * k, PIVOT[1] * k))
    return out.resize((px, px), Image.LANCZOS)


def emblem(px, gesture=-1.0, ring=(41, 219, 166), bg=(58, 20, 38), border=True):
    """The boss emblem: the hand on a porphyry roundel with a verdigris ring and a white die-cut border."""
    ss = 2
    W_ = px * ss
    out = K.rgba((W_, W_))
    d = ImageDraw.Draw(out)
    c = W_ / 2
    if border:
        d.ellipse([0, 0, W_ - 1, W_ - 1], fill=(250, 248, 244, 255))
        r = W_ * 0.455
    else:
        r = W_ * 0.5
    d.ellipse([c - r, c - r, c + r, c + r], fill=INK + (255,))
    r2 = r * 0.93
    d.ellipse([c - r2, c - r2, c + r2, c + r2], fill=ring + (255,))
    r3 = r * 0.84
    d.ellipse([c - r3, c - r3, c + r3, c + r3], fill=bg + (255,))
    h = hand_rgba(int(W_ * 0.74), gesture, outline=14)
    out.alpha_composite(h, (int(c - h.width / 2 + W_ * 0.0), int(c - h.height / 2 + W_ * 0.035)))
    return out.resize((px, px), Image.LANCZOS)
