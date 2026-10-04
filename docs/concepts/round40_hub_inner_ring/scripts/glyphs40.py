"""Round 40 glyphs: the Breaker core as a spiderweb of glass cracks (no pane, no fill)."""
import math
import numpy as np
from PIL import Image, ImageDraw

import glyphs39 as G39
from glyphs13 import _new
from glyphs38 import _gap, _layer

BYPASS = set()


def core_breaker():  # the crowbar's strike point opens a spiderweb of cracks across the glass
    m, d = _new()
    hit = (300, 200)
    rng = np.random.default_rng(4)
    spokes = []
    for k in range(9):
        a = math.radians(k * 40 + rng.random() * 14)
        L = 150 + rng.random() * 110
        pts = [hit]
        for s in range(1, 5):
            aa = a + (rng.random() - 0.5) * 0.25
            pts.append((hit[0] + math.cos(aa) * L * s / 4, hit[1] + math.sin(aa) * L * s / 4))
        spokes.append(pts)
        d.line(pts, fill=255, width=13, joint="curve")
    for ring in (1, 2, 3):  # web rings: join the spokes at the same step, a little irregular
        poly = [sp[ring] for sp in spokes]
        for i in range(len(poly)):
            if rng.random() < 0.3:  # glass: the concentric cracks are broken, not a closed web
                continue
            a, b = poly[i], poly[(i + 1) % len(poly)]
            j = (rng.random() - 0.5) * 28  # a jagged kink outward, not a web's inward sag
            mid = ((a[0] + b[0]) / 2 - (hit[0] - (a[0] + b[0]) / 2) * 0.08 + j, (a[1] + b[1]) / 2 - (hit[1] - (a[1] + b[1]) / 2) * 0.08 - j)
            d.line([a, mid, b], fill=255, width=11 if ring < 3 else 9)
    d.ellipse([hit[0] - 22, hit[1] - 22, hit[0] + 22, hit[1] + 22], fill=255)
    L, dl = _layer()
    dl.line([(50, 490), (262, 238)], fill=255, width=50)
    dl.arc([214, 168, 324, 278], 150, 330, fill=255, width=40)
    dl.polygon([(26, 506), (40, 436), (96, 476)], fill=255)
    _gap(m, L, 25)
    return m


NEW = {"CORE_breaker_core": core_breaker}
CHOICE = G39.CHOICE
SMALL = {}
_cache = {}


def resolve(name, px=None):
    return CHOICE.get(name, name)


def mask(name):
    if name in BYPASS:
        return G39.mask(name)
    f = NEW.get(name)
    if f is None:
        return G39.mask(name)
    if name not in _cache:
        _cache[name] = f()
    return _cache[name].copy()


tick_mask = G39.tick_mask
