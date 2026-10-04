"""Round 16 glyphs: RECON, SPOOF, NUDGE, JUDGEMENT, SANDBOX redone after the round 15 review.

Resolution order: CHOICE -> round 16 shapes (NEW / OPTIONS) -> glyphs15 (its own picks) -> 14 -> 13 -> round 6/10.
glyphs15.py is kept verbatim (the "old" reference for glyph_changes.png).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import glyphs13 as G13
import glyphs15 as G15
from glyphs13 import _new, _rot, _arrow_arc
from glyphs14 import _paste, _two_head_arc

S = 512
BYPASS = set()


# 1. RECON: lens rings + a flat-topped cone eyepiece on each (top edge of a square, sides down to the
#    lens circle's outer edges), a bar between the lenses
def recon():
    m, d = _new()
    cy, r = 330, 108
    for cx in (138, 374):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=255, width=34)
        top = 70
        tw = 44
        d.line([(cx - tw, top), (cx + tw, top)], fill=255, width=34)
        d.line([(cx - tw, top), (cx - r + 17, cy)], fill=255, width=34)
        d.line([(cx + tw, top), (cx + r - 17, cy)], fill=255, width=34)
        for (x, y) in ((cx - tw, top), (cx + tw, top)):
            d.ellipse([x - 17, y - 17, x + 17, y + 17], fill=255)
    d.rectangle([246, 300, 266, 360], fill=255)
    d.rectangle([232, 312, 280, 348], fill=255)
    return m


# 2. SPOOF: a thin outline + a real-looking loop print: ridges that end and fork, slightly irregular
def fingerprint():
    m, d = _new()
    d.ellipse([84, 16, 428, 496], outline=255, width=18)
    R = Image.new("L", (S, S), 0)
    dr = ImageDraw.Draw(R)
    rng = np.random.default_rng(7)
    cx, cy = 236, 236  # loop core
    W = 12

    def wob(x, y, k, a=6.0):
        return x + a * math.sin(y * 0.045 + k * 1.7), y + a * 0.6 * math.cos(x * 0.05 + k)

    # loop ridges: a U turned over (round top), legs sweeping down-right (a right-slant loop)
    for k in range(1, 9):
        rr = 20 + k * 26
        pts = []
        for i in range(0, 41):
            a = math.pi + math.pi * i / 40  # top half, left -> right
            x, y = cx + rr * math.cos(a), cy + rr * 1.15 * math.sin(a)
            pts.append(wob(x, y, k))
        # legs: left leg drops down then sweeps right; right leg goes down-right
        lx, ly = pts[0]
        for i in range(1, 12):
            pts.insert(0, wob(lx + i * 5 + i * i * 0.6, ly + i * 18, k))
        rx, ry = pts[-1]
        for i in range(1, 12):
            pts.append(wob(rx + i * 4 + i * i * 0.5, ry + i * 18, k))
        # break the ridge in one or two places (ridge endings)
        cut = rng.integers(8, len(pts) - 8)
        segs = [pts[:cut], pts[cut + 2:]] if k % 3 != 0 else [pts]
        for sgm in segs:
            if len(sgm) > 1:
                dr.line(sgm, fill=255, width=W, joint="curve")
        if k in (3, 6):  # a fork: a short branch splitting off a ridge
            bx, by = pts[len(pts) // 3]
            dr.line([(bx, by), (bx - 26, by + 26), (bx - 40, by + 58)], fill=255, width=W, joint="curve")
    # the core: a short rod inside the innermost loop
    dr.line([wob(cx, cy - 6, 0), wob(cx + 4, cy + 46, 0)], fill=255, width=W)
    # lower ridges flowing across under the loop
    for k in range(4):
        y0 = 400 + k * 26
        pts = [wob(90 + i * 22, y0 - 30 * math.sin(i / 16 * math.pi), k + 10) for i in range(17)]
        dr.line(pts, fill=255, width=W, joint="curve")
    clip = Image.new("L", (S, S), 0)
    ImageDraw.Draw(clip).ellipse([112, 44, 400, 468], fill=255)
    _paste(m, ImageChops.multiply(R, clip))
    return m


# 3. NUDGE: the +-1 arc with the spinner needle on TOP pointing DOWN, crossing through the arc
def nudge():
    m, d = _new()
    _two_head_arc(d, (256, 500), 300, 56, 238, 302)
    N = Image.new("L", (S, S), 0)
    dn = ImageDraw.Draw(N)
    dn.polygon([(256, 380), (300, 110), (212, 110)], fill=255)  # needle pointing down
    dn.ellipse([196, 30, 316, 150], fill=255)  # pivot on top
    _paste(m, N.filter(ImageFilter.MaxFilter(23)), 0)
    _paste(m, N)
    d.ellipse([234, 68, 278, 112], fill=0)
    return m


# 4. JUDGEMENT: the gavel raised above its strike block, a clear gap between head and block
def judgement():
    m, d = _new()
    c = (310, 226)  # head centre: raised, its strike face aimed at the block
    hd = (-0.94, 0.35)  # handle direction (out to the left)
    ax = (0.35, 0.94)  # head axis: its lower end faces the block
    L2, T2 = 136, 50

    def P(a, b):
        return (c[0] + ax[0] * a + hd[0] * b, c[1] + ax[1] * a + hd[1] * b)
    d.polygon([P(-L2, -T2), P(L2, -T2), P(L2, T2), P(-L2, T2)], fill=255)
    for e in (-1, 1):  # end bands
        d.polygon([P(e * (L2 - 34), -T2 - 14), P(e * (L2 - 10), -T2 - 14), P(e * (L2 - 10), T2 + 14), P(e * (L2 - 34), T2 + 14)], fill=255)
    d.line([P(0, T2 - 4), P(0, T2 + 230)], fill=255, width=44)  # handle
    d.rounded_rectangle([236, 424, 500, 470], radius=14, fill=255)  # strike block, a clear gap below the head
    d.rectangle([270, 470, 470, 500], fill=255)
    return m


# 5. SANDBOX: a pile of sand, a pail behind it, a shovel partly sticking out (blade showing)
def _pile(d, box, grains, seed=3):
    x0, y0, x1, y1 = box
    pts = []
    for i in range(41):
        f = i / 40
        x = x0 + (x1 - x0) * f
        h = math.sin(math.pi * f) ** 0.8
        h *= 1 + 0.06 * math.sin(f * 23)  # lumpy top
        pts.append((x, y1 - (y1 - y0) * h))
    d.polygon(pts + [(x1, y1), (x0, y1)], fill=255)
    rng = np.random.default_rng(seed)
    for k in range(grains):
        f = 0.15 + 0.7 * rng.random()
        x = x0 + (x1 - x0) * f
        top = y1 - (y1 - y0) * math.sin(math.pi * f) ** 0.8
        y = top + 26 + rng.random() * (y1 - top - 46)
        r = 6 + rng.random() * 5
        d.ellipse([x - r, y - r, x + r, y + r], fill=0)


def _pail(m, box, gap=22):
    x0, y0, x1, y1 = box
    P = Image.new("L", (S, S), 0)
    dp = ImageDraw.Draw(P)
    ins = (x1 - x0) * 0.14
    dp.polygon([(x0, y0), (x1, y0), (x1 - ins, y1), (x0 + ins, y1)], fill=255)
    dp.arc([x0 + 10, y0 - (x1 - x0) * 0.55, x1 - 10, y0 + (x1 - x0) * 0.35], 195, 345, fill=255, width=20)
    _paste(m, P)
    ImageDraw.Draw(m).line([(x0 + 4, y0 + 30), (x1 - 4, y0 + 30)], fill=0, width=16)  # rim band


def _shovel(m, tip, ang, length=300, blade=(70, 120)):
    """A sand shovel: handle + rounded blade; tip = blade end, ang = direction from tip to handle (deg)."""
    S2 = Image.new("L", (S, S), 0)
    ds = ImageDraw.Draw(S2)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    bw, bl = blade
    tx, ty = tip
    bx, by = tx + ux * bl, ty + uy * bl
    ds.polygon([(tx + nx * bw * 0.55, ty + ny * bw * 0.55), (tx - nx * bw * 0.55, ty - ny * bw * 0.55),
                (bx - nx * bw, by - ny * bw), (bx + nx * bw, by + ny * bw)], fill=255)
    ds.ellipse([tx - bw * 0.55, ty - bw * 0.55, tx + bw * 0.55, ty + bw * 0.55], fill=255)
    hx, hy = bx + ux * length, by + uy * length
    ds.line([(bx, by), (hx, hy)], fill=255, width=30)
    ds.line([(hx + nx * 40, hy + ny * 40), (hx - nx * 40, hy - ny * 40)], fill=255, width=30)
    return S2


def _regrain(m, box, n=9, seed=3):
    d = ImageDraw.Draw(m)
    x0, y0, x1, y1 = box
    rng = np.random.default_rng(seed)
    for k in range(n):
        f = 0.15 + 0.7 * rng.random()
        x = x0 + (x1 - x0) * f
        top = y1 - (y1 - y0) * math.sin(math.pi * f) ** 0.8
        y = top + 30 + rng.random() * max(1, (y1 - top - 50))
        r = 6 + rng.random() * 5
        d.ellipse([x - r, y - r, x + r, y + r], fill=0)
    return m


def _compose(pail_box, pile_box, shovel_tip, shovel_ang, shovel_len, grains=9):
    """pail (back) -> shovel (middle, its lower part buried) -> sand pile (front)."""
    m, d = _new()
    _pail(m, pail_box)
    Sh = _shovel(m, shovel_tip, shovel_ang, shovel_len)
    _paste(m, Sh.filter(ImageFilter.MaxFilter(21)), 0)
    _paste(m, Sh)
    pile = Image.new("L", (S, S), 0)
    _pile(ImageDraw.Draw(pile), pile_box, 0)
    _paste(m, pile.filter(ImageFilter.MaxFilter(23)), 0)  # dark gap where the pile overlaps
    _paste(m, pile)
    return _regrain(m, pile_box, grains)


def sandbox_a():  # pail behind right, shovel stuck in the pile leaning left, blade half out
    return _compose((276, 96, 476, 320), (20, 240, 440, 486), (176, 300), -62, 230)


def sandbox_b():  # pail behind left, shovel lying across the pile's right flank, blade sticking out top-right
    return _compose((40, 90, 230, 300), (60, 230, 492, 486), (420, 196), 140, 260)


def sandbox_c():  # pail behind centre, shovel planted blade-up on the right of the pile
    return _compose((150, 60, 360, 270), (20, 250, 470, 486), (400, 150), 72, 170)


OPTIONS = {"SANDBOX@A": sandbox_a, "SANDBOX@B": sandbox_b, "SANDBOX@C": sandbox_c}
NEW = {"RECON": recon, "FINGERPRINT": fingerprint, "PI_NUDGE": nudge, "JUDGEMENT": judgement}
CHOICE = dict(G15.CHOICE)
CHOICE["SANDBOX"] = "SANDBOX@C"
SMALL = {}
_cache = {}


def resolve(name, px=None):
    return CHOICE.get(name, name)


def mask(name):
    if name in BYPASS:
        return None
    name = resolve(name)
    f = NEW.get(name) or OPTIONS.get(name)
    if f is None:
        f = G15.NEW.get(name) or G15.G14.NEW.get(name) or G15.G14.OPTIONS.get(name)
    if f is None:
        if name == "INERTIA":
            return None
        return G13.mask(name)
    if name not in _cache:
        _cache[name] = f()
    return _cache[name].copy()


tick_mask = G15.tick_mask
