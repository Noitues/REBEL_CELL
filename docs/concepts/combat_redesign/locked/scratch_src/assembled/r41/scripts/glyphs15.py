"""Round 15 glyph set: the designer's round 14 picks applied + the redone glyphs.

Resolution order: CHOICE -> round 15 shapes (NEW) -> glyphs14 shapes/options -> glyphs13 -> round 6/10.
glyphs14.py is kept verbatim (it is also the "old" reference for glyph_changes.png).
"""
import math
from PIL import Image, ImageDraw, ImageFilter

import glyphs13 as G13
import glyphs14 as G14
from glyphs13 import _new, _rot, _arrow_arc
from glyphs14 import _text_mask, _paste, _keycap, _two_head_arc

S = 512
BYPASS = set()


# 5. RECON: binoculars as two thin lens rings, a bar between them, two thin eyepiece rectangles above
def recon():
    m, d = _new()
    for cx in (130, 382):
        d.ellipse([cx - 112, 210, cx + 112, 434], outline=255, width=40)
        d.rectangle([cx - 52, 74, cx + 52, 190], outline=255, width=30)
    d.rectangle([242, 300, 270, 344], fill=255)
    d.rectangle([230, 296, 282, 348], fill=255)
    return m


# 6. NULL: 1/0 (glyphs14 option C)
# 9. SPOOF: white outline, dark inside, THIN white ridges
def fingerprint():
    m, d = _new()
    d.ellipse([70, 14, 442, 498], outline=255, width=36)
    cx, cy = 256, 250
    for k, r in enumerate(range(34, 190, 38)):
        ry = r * 1.2
        a0, a1 = (200, 520) if k % 2 == 0 else (160, 480)
        d.arc([cx - r, cy - ry + k * 5, cx + r, cy + ry + k * 5], a0, a1, fill=255, width=14)
    d.line([(256, 228), (256, 276)], fill=255, width=14)
    return m


# 10. CLEANSE: a single ESC keycap (all sizes) ; KILL PROCESS: the power symbol
def cleanse_esc():
    m, d = _new()
    _keycap(m, (40, 60, 472, 452), "ESC")
    return m


def power():
    m, d = _new()
    d.arc([46, 66, 466, 486], -50, 230, fill=255, width=64)
    d.rounded_rectangle([222, 10, 290, 270], radius=30, fill=255)
    return m


# 12. MOMENTUM: the spin arrow; the two numbers (big = will execute) are drawn by the pictogram renderer
def momentum():
    return G13.spin_cw()


# 13. NUDGE INNER: symmetric (unlike SPIN): full rings, middle ring highlighted, two heads pointing apart on top
def nudge_inner():
    m, d = _new()
    c = (256, 290)
    d.ellipse([c[0] - 210, c[1] - 210, c[0] + 210, c[1] + 210], outline=255, width=20)
    d.ellipse([c[0] - 140, c[1] - 140, c[0] + 140, c[1] + 140], outline=255, width=56)
    d.ellipse([c[0] - 40, c[1] - 40, c[0] + 40, c[1] + 40], fill=255)
    # +-1 marker on top of the middle ring: a short bar with heads both ends, like a tiny NUDGE
    d.rectangle([150, 52, 362, 92], fill=255)
    d.polygon([(70, 72), (170, 10), (170, 134)], fill=255)
    d.polygon([(442, 72), (342, 10), (342, 134)], fill=255)
    d.rectangle([236, 92, 276, 160], fill=255)  # stem onto the ring
    return m


# 14. NUDGE: short two-headed arc over a spinner NEEDLE
def nudge():
    m, d = _new()
    _two_head_arc(d, (256, 470), 300, 56, 238, 302)
    d.polygon([(256, 236), (306, 400), (206, 400)], fill=255)  # needle, pointing up at the arc
    d.ellipse([196, 370, 316, 490], fill=255)  # pivot
    d.ellipse([234, 408, 278, 452], fill=0)
    return m


NEW = {"RECON": recon, "FINGERPRINT": fingerprint, "ST_CLEANSE": cleanse_esc, "POWER": power,
       "PI_MOMENTUM": momentum, "PI_NUDGE_INNER": nudge_inner, "PI_NUDGE": nudge,
       "ST_PARASITE": lambda: tick_mask(0.0)}
CHOICE = dict(G14.CHOICE)
CHOICE.update({"WEIGHT": "WEIGHT@A", "NULL": "NULL@C", "ST_EMPOWERED": "ST_EMPOWERED@A"})
for k in ("ST_CLEANSE", "PI_MOMENTUM", "PI_NUDGE"):
    CHOICE.pop(k, None)
SMALL = {}
OPTIONS = G14.OPTIONS
_cache = {}


def resolve(name, px=None):
    name = CHOICE.get(name, name)
    if px is not None and px <= 48 and name in SMALL:
        name = SMALL[name]
    return name


def mask(name):
    if name in BYPASS:
        return None
    name = resolve(name)
    f = NEW.get(name) or G14.NEW.get(name) or G14.OPTIONS.get(name)
    if f is None:
        if name == "INERTIA":
            return None
        return G13.mask(name)
    if name not in _cache:
        _cache[name] = f()
    return _cache[name].copy()


def tick_mask(phase=0.0):
    """The PARASITE tick with animated legs (phase 0..1) for the overlay; same design as the glyph."""
    m, d = _new()
    d.ellipse([126, 40, 386, 380], fill=255)
    d.ellipse([186, 330, 326, 450], fill=255)
    d.polygon([(226, 430), (256, 506), (286, 430)], fill=255)
    for s in (-1, 1):
        for k, (yy, dx, dy) in enumerate(((150, 118, -70), (220, 130, -10), (290, 124, 50), (350, 100, 110))):
            w = math.sin(2 * math.pi * (phase + k * 0.25 + (0.5 if s > 0 else 0)))
            x0 = 256 + s * 110
            dy2 = dy + 26 * w
            d.line([(x0, yy), (x0 + s * dx * 0.55, yy + dy2 * 0.2 - 30), (x0 + s * dx, yy + dy2)], fill=255, width=30, joint="curve")
    for y in (150, 230, 300):  # body segments only (no face-like cut-outs)
        d.line([(150, y), (362, y)], fill=0, width=14)
    d.line([(170, 362), (342, 362)], fill=0, width=20)  # neck
    return m
