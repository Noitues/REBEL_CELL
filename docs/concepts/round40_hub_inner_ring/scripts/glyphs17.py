"""Round 17 (final) glyphs: three tweaks on the locked round 16 set.

1. RECON: shorter cone eyepieces, filled solid; lens circles stay thin rings.
2. SPOOF: the horizontal ridges at the bottom removed.
3. SOLAR FLARE: the lower bar removed; only the horizon line under the sun.
Resolution order: CHOICE -> round 17 NEW -> glyphs16 (its picks) -> 15 -> 14 -> 13 -> round 6/10.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageChops

import glyphs13 as G13
import glyphs16 as G16
from glyphs13 import _new
from glyphs14 import _paste

S = 512
BYPASS = set()


def recon():
    m, d = _new()
    cy, r, w = 318, 112, 34
    for cx in (138, 374):
        top, tw = 150, 50  # shorter cone than round 16 (top 150 vs 70)
        d.polygon([(cx - tw, top), (cx + tw, top), (cx + r - 4, cy), (cx - r + 4, cy)], fill=255)
        d.rounded_rectangle([cx - tw, top - 14, cx + tw, top + 24], radius=10, fill=255)
        d.ellipse([cx - r + w, cy - r + w, cx + r - w, cy + r - w], fill=0)  # keep the lens open
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=255, width=w)
    d.rectangle([232, 300, 280, 340], fill=255)
    return m


def fingerprint():
    m, d = _new()
    d.ellipse([84, 16, 428, 496], outline=255, width=18)
    R = Image.new("L", (S, S), 0)
    dr = ImageDraw.Draw(R)
    rng = np.random.default_rng(7)
    cx, cy = 236, 236
    W = 12

    def wob(x, y, k, a=6.0):
        return x + a * math.sin(y * 0.045 + k * 1.7), y + a * 0.6 * math.cos(x * 0.05 + k)

    for k in range(1, 9):
        rr = 20 + k * 26
        pts = []
        for i in range(0, 41):
            a = math.pi + math.pi * i / 40
            x, y = cx + rr * math.cos(a), cy + rr * 1.15 * math.sin(a)
            pts.append(wob(x, y, k))
        lx, ly = pts[0]
        for i in range(1, 12):
            pts.insert(0, wob(lx + i * 5 + i * i * 0.6, ly + i * 18, k))
        rx, ry = pts[-1]
        for i in range(1, 12):
            pts.append(wob(rx + i * 4 + i * i * 0.5, ry + i * 18, k))
        cut = rng.integers(8, len(pts) - 8)
        segs = [pts[:cut], pts[cut + 2:]] if k % 3 != 0 else [pts]
        for sgm in segs:
            if len(sgm) > 1:
                dr.line(sgm, fill=255, width=W, joint="curve")
        if k in (3, 6):
            bx, by = pts[len(pts) // 3]
            dr.line([(bx, by), (bx - 26, by + 26), (bx - 40, by + 58)], fill=255, width=W, joint="curve")
    dr.line([wob(cx, cy - 6, 0), wob(cx + 4, cy + 46, 0)], fill=255, width=W)
    # (round 17: the horizontal ridges across the bottom are gone)
    clip = Image.new("L", (S, S), 0)
    ImageDraw.Draw(clip).ellipse([112, 44, 400, 468], fill=255)
    _paste(m, ImageChops.multiply(R, clip))
    return m


def flare():
    m, d = _new()
    c = (256, 380)
    d.pieslice([c[0] - 150, c[1] - 150, c[0] + 150, c[1] + 150], 180, 360, fill=255)
    for k in range(5):
        a = math.radians(-162 + k * 36)
        d.line([(c[0] + 196 * math.cos(a), c[1] + 196 * math.sin(a)), (c[0] + 270 * math.cos(a), c[1] + 270 * math.sin(a))],
               fill=255, width=50)
    d.rounded_rectangle([16, c[1] + 14, 496, c[1] + 62], radius=18, fill=255)  # the horizon, only
    d.arc([c[0] - 104, c[1] - 104, c[0] + 104, c[1] + 104], 200, 250, fill=0, width=28)
    return m


NEW = {"RECON": recon, "FINGERPRINT": fingerprint, "FLARE": flare}
CHOICE = dict(G16.CHOICE)
SMALL = {}
_cache = {}


def resolve(name, px=None):
    return CHOICE.get(name, name)


def mask(name):
    if name in BYPASS:
        return None
    name = resolve(name)
    f = NEW.get(name)
    if f is None:
        return G16.mask(name)
    if name not in _cache:
        _cache[name] = f()
    return _cache[name].copy()


tick_mask = G16.tick_mask
