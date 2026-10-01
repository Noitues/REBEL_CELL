"""Round 4 shared pieces: Cv2 palette, slice data, flat glyphs (no outlines), layers, sheet helpers."""
import math
import os
import random
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageOps, ImageFilter, ImageChops
from lowpoly import (SS, W, H, R, hexc, mix, ramp, hsh, toner, facet, bil, polar, panel, skew_rect, tri, gem, gradient,
                     text, text_w, font, finalize, NEON, line2, catenary, layer, composite, rain, smog, poly_fpos)

OUT = os.path.dirname(HERE)
FONTS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(OUT))), 'assets', 'fonts')
ANTON = os.path.join(FONTS, 'Anton-Regular.ttf')
MONO = os.path.join(FONTS, 'ShareTechMono-Regular.ttf')
PLEX = os.path.join(FONTS, 'IBMPlexSansCondensed-Medium.ttf')
MARKER = os.path.join(FONTS, 'PermanentMarker-Regular.ttf')
BAHN = 'C:/Windows/Fonts/bahnschrift.ttf'

INK = hexc('#0b0a0e')
CREAM = hexc('#ece4d2')
SHEET_BG = hexc('#141318')


def ramp_of(c, dark=0.82, light=0.55):
    """A 7-stop deep -> pale ramp around a key colour (the key sits at ~0.55)."""
    c = hexc(c) if isinstance(c, str) else c
    k = (0, 0, 0)
    w = (255, 255, 255)
    return [mix(c, k, dark), mix(c, k, 0.62), mix(c, k, 0.38), mix(c, k, 0.16), c, mix(c, w, 0.28), mix(c, w, light)]


# slice colours (kept from the spec)
SLICE_HEX = {'attack': '#FF3DA8', 'crit': '#FF3DA8', 'defend': '#5CE1FF', 'shield': '#5CE1FF', 'evade': '#7BE07B',
             'heal': '#7BE07B', 'afflict': '#C85AFF', 'deploy': '#B08CFF', 'miss': '#6A6A6A'}
SLICE = {k: ramp_of(v) for k, v in SLICE_HEX.items()}
SHORT = {'attack': 'ATK', 'crit': 'CRIT', 'defend': 'DEF', 'shield': 'SHLD', 'evade': 'EVD', 'heal': 'HEAL',
         'afflict': 'AFF', 'deploy': 'DPL', 'miss': 'MISS'}
METAL = R('#0a0a0c', '#18181b', '#29282a', '#403d3a', '#5c5850', '#837d70', '#b2a998')
STEEL = R('#06080c', '#10161e', '#1a2430', '#283646', '#3c4e62', '#5c7086', '#94a6b8')
RUST = R('#120806', '#2a1209', '#481e0f', '#683217', '#884a26', '#a46a42', '#c49068')
DARK = R('#040406', '#09090c', '#101016', '#18181f', '#22222a', '#2e2e38', '#3e3e4a')
MER = R('#1a0a02', '#4a1c04', '#8a3a08', '#c8600e', '#f08a24', '#f8b45a', '#fcdca0')
BOSSR = R('#12020a', '#300614', '#580c22', '#8a1430', '#c02a40', '#e65a5a', '#f8a090')
SODIUM = NEON['sodium']
HAZ = R('#2a1c02', '#6a4606', '#b07a0c', '#e8a818', '#ffc83a', '#ffe08a', '#fff4cc')
CYAN = NEON['cyan']
TYPE_HEX = {'WHEEL': '#FFC23D', 'HACK': '#FF3DA8', 'SYSTEM': '#5CE1FF'}
TYPE = {k: ramp_of(v) for k, v in TYPE_HEX.items()}
RARITY_HEX = {'Common': '#8E9AA6', 'Uncommon': '#7FD6FF', 'Rare': '#F2C14E', 'Boss': '#FF4656'}

# a player wheel and a Meridian enemy wheel (30 ticks)
PLAYER = [(5, 'attack', 6), (4, 'defend', 4), (3, 'heal', 3), (6, 'attack', 8), (2, 'miss', None),
          (4, 'afflict', 2), (3, 'shield', 5), (3, 'evade', 3)]
ENEMY = [(6, 'attack', 7), (3, 'miss', None), (5, 'defend', 6), (4, 'deploy', 1), (2, 'miss', None),
         (6, 'crit', 12), (4, 'afflict', 3)]
BOSS = [(4, 'crit', 14), (4, 'attack', 9), (3, 'shield', 8), (4, 'afflict', 4), (3, 'deploy', 2), (4, 'attack', 9),
        (4, 'defend', 10), (4, 'miss', None)]
TICK = 2 * math.pi / 30


def slice_angles(slices, rot_ticks=0.0):
    """Yield (index, a0, a1, kind, value) with tick 0 at 12 o'clock, clockwise, wheel turned by rot_ticks."""
    a = -math.pi / 2 - rot_ticks * TICK
    out = []
    for n, (t, k, v) in enumerate(slices):
        out.append((n, a, a + t * TICK, k, v))
        a += t * TICK
    return out


def active_index(slices, rot_ticks=0.0):
    for n, a0, a1, k, v in slice_angles(slices, rot_ticks):
        top = -math.pi / 2
        x = (top - a0) % (2 * math.pi)
        if x < (a1 - a0):
            return n
    return 0


# ------------------------------------------------------------------ flat glyphs (no outlines, Cv2 style)
def U(cx, cy, s, ang=0.0):
    ca, sa = math.cos(ang), math.sin(ang)
    return lambda pts: [(cx + (x * ca - y * sa) * s, cy + (x * sa + y * ca) * s) for x, y in pts]


def fpoly(d, pts, col):
    pp = [(p[0] * SS, p[1] * SS) for p in pts]
    d.polygon(pp, fill=col, outline=col)


def circ(cx, cy, r, n=20, a0=0.0, ry=None):
    ry = r if ry is None else ry
    return [(cx + r * math.cos(a0 + 2 * math.pi * k / n), cy + ry * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)]


def glyph(d, kind, cx, cy, s, fg, bg=None, ang=0.0):
    """Flat silhouette glyph for a slice type, ~s px across. Shape alone carries the meaning."""
    p = U(cx, cy, s, ang)
    if kind in ('attack', 'crit'):
        q = U(cx, cy, s, ang + math.radians(45))
        fpoly(d, q([(0, -0.5), (0.1, -0.34), (0.09, 0.14), (-0.09, 0.14), (-0.1, -0.34)]), fg)
        fpoly(d, q([(-0.26, 0.14), (0.26, 0.14), (0.24, 0.23), (-0.24, 0.23)]), fg)
        fpoly(d, q([(-0.055, 0.23), (0.055, 0.23), (0.055, 0.42), (-0.055, 0.42)]), fg)
        fpoly(d, q([(0, 0.4), (0.09, 0.46), (0, 0.52), (-0.09, 0.46)]), fg)
        if kind == 'crit':
            st = []
            for k in range(8):
                rr = 0.2 if k % 2 == 0 else 0.08
                a = -math.pi / 2 + k * math.pi / 4
                st.append((0.28 + rr * math.cos(a), -0.28 + rr * math.sin(a)))
            fpoly(d, p(st), fg)
    elif kind == 'defend':
        fpoly(d, p([(-0.4, -0.42), (0.4, -0.42), (0.38, 0.06), (0, 0.48), (-0.38, 0.06)]), fg)
        if bg:
            fpoly(d, p([(-0.06, -0.34), (0.06, -0.34), (0.06, 0.34), (-0.06, 0.34)]), bg)
    elif kind == 'shield':
        fpoly(d, circ(cx, cy, s * 0.48, 6, math.pi / 6), fg)
        if bg:
            fpoly(d, circ(cx, cy, s * 0.3, 6, math.pi / 6), bg)
            fpoly(d, circ(cx, cy, s * 0.16, 6, math.pi / 6), fg)
    elif kind == 'evade':
        for dx in (-0.22, 0.12):
            fpoly(d, p([(dx - 0.14, -0.4), (dx + 0.06, -0.4), (dx + 0.3, 0), (dx + 0.06, 0.4), (dx - 0.14, 0.4),
                        (dx + 0.1, 0)]), fg)
    elif kind == 'heal':
        a, b = 0.15, 0.44
        fpoly(d, p([(-a, -b), (a, -b), (a, -a), (b, -a), (b, a), (a, a), (a, b), (-a, b), (-a, a), (-b, a), (-b, -a),
                    (-a, -a)]), fg)
    elif kind == 'afflict':
        pts = [(0, -0.5)] + [(0.32 * math.cos(a), 0.14 + 0.32 * math.sin(a)) for a in
                             [math.radians(x) for x in range(-30, 211, 20)]]
        fpoly(d, p(pts), fg)
        if bg:
            fpoly(d, p([(-0.14, 0.04), (-0.04, 0.04), (-0.09, 0.14)]), bg)
            fpoly(d, p([(0.04, 0.04), (0.14, 0.04), (0.09, 0.14)]), bg)
    elif kind == 'deploy':
        fpoly(d, circ(cx, cy + s * 0.06, s * 0.22, 6), fg)
        for sx in (-1, 1):
            fpoly(d, p([(sx * 0.12, -0.02), (sx * 0.44, -0.2), (sx * 0.46, -0.12), (sx * 0.14, 0.08)]), fg)
            fpoly(d, p([(sx * 0.44 - 0.16, -0.27), (sx * 0.44 + 0.16, -0.29), (sx * 0.44 + 0.16, -0.22),
                        (sx * 0.44 - 0.16, -0.2)]), fg)
        if bg:
            fpoly(d, circ(cx, cy + s * 0.08, s * 0.07, 6), bg)
    elif kind == 'miss':
        ring = circ(cx, cy, s * 0.44, 20)
        inner = circ(cx, cy, s * 0.28, 20)
        for k in range(20):
            fpoly(d, [ring[k], ring[(k + 1) % 20], inner[(k + 1) % 20], inner[k]], fg)
        fpoly(d, p([(-0.38, 0.3), (0.3, -0.38), (0.38, -0.3), (-0.3, 0.38)]), fg)


def arrow_ccw(d, cx, cy, r, w, col, sweep=(-20, 250)):
    a0, a1 = math.radians(sweep[0]), math.radians(sweep[1])
    n = 22
    pts = [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy - r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]
    for a, b in zip(pts, pts[1:]):
        line2(d, a, b, w, col)
    ex, ey = pts[-1]
    tx, ty = -math.sin(a1), -math.cos(a1)
    nx, ny = math.cos(a1), -math.sin(a1)
    h = w * 1.9
    fpoly(d, [(ex + tx * h, ey + ty * h), (ex + nx * h, ey + ny * h), (ex - nx * h, ey - ny * h)], col)


def bolt(d, cx, cy, s, col):
    p = U(cx, cy, s)
    fpoly(d, p([(0.14, -0.5), (-0.26, 0.06), (0.0, 0.06), (-0.14, 0.5), (0.28, -0.1), (0.02, -0.1)]), col)


# ------------------------------------------------------------------ layers + sheets
def new_layer(w, h):
    im = Image.new('RGBA', (int(w * SS), int(h * SS)), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def to1x(im):
    return im.convert('RGBa').resize((im.width // SS, im.height // SS), Image.LANCZOS).convert('RGBA')


def grey(im):
    a = im.getchannel('A')
    g = ImageOps.grayscale(im.convert('RGB')).convert('RGB').convert('RGBA')
    g.putalpha(a)
    return g


def paste_c(base, im, cx, cy):
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def sheet_bg():
    """Calm Cv2 backdrop: a few large dark facets."""
    im = Image.new('RGB', (W * SS, H * SS), SHEET_BG)
    d = ImageDraw.Draw(im)
    facet(d, bil([(0, 0), (W, 0), (W, H), (0, H)]), 8, 5,
          toner(R('#0c0b10', '#121118', '#18171f', '#1e1c26'), 0.5, gu=-0.2, gv=0.25, var=0.06, flip=0.06), 'sbg', 0.35)
    return finalize(im).convert('RGBA')


def label(d1, x, y, s, size=18, col=(200, 194, 182), anchor='mm', path=BAHN, style='SemiBold'):
    from PIL import ImageFont
    f = ImageFont.truetype(path, size)
    if path == BAHN:
        try:
            f.set_variation_by_name(style)
        except Exception:
            pass
    d1.text((x, y), s, font=f, fill=col, anchor=anchor)


def title(d1, code, name, sub):
    label(d1, 40, 40, code, 34, (236, 228, 210), 'lm', style='Bold')
    label(d1, 40 + 18 * len(code) + 26, 40, name, 30, (236, 228, 210), 'lm', style='Bold')
    label(d1, 40, 74, sub, 17, (150, 144, 134), 'lm')


def frame_panel(base, im, cx, cy, cap, pad=10):
    """Show a crop in a thin faceted frame with a caption below."""
    w, h = im.width + 2 * pad, im.height + 2 * pad
    fr = Image.new('RGBA', (w, h), (30, 28, 36, 255))
    fr.alpha_composite(im, (pad, pad))
    d = ImageDraw.Draw(fr)
    d.rectangle([0, 0, w - 1, h - 1], outline=(70, 66, 78), width=2)
    paste_c(base, fr, cx, cy)
    label(ImageDraw.Draw(base), cx, cy + h / 2 + 16, cap, 16)
