"""Shared helpers for the H6 sheets."""
import math, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cb
from heads6 import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
PLATE = Image.open('D:/rc_scratch/tide_concepts/plates/clean/default/plan_placed.png').convert('RGBA')
PLATE_NET = Image.open('D:/rc_scratch/tide_concepts/plates/clean/default/plan_placed_net.png').convert('RGBA')
COORDS = json.load(open('D:/rc_scratch/tide_concepts/plates/coords/default_forecast.json'))
FONT_T = os.path.join(HERE, 'Anton-Regular.ttf')
FONT_M = 'C:/Windows/Fonts/consola.ttf'
VIS = ('normal', 'deutan', 'tritan')
BG = (10, 6, 20)
BONE = (236, 228, 208)
CHOSEN = 44
K1280 = 1280 / 1920
CROP_GAME = (40, 745)
CROP_RIB = (20, 640)


def F(p, s):
    return ImageFont.truetype(p, int(s))


def vis(im, mode):
    if mode == 'normal':
        return im.convert('RGB')
    return cb.sim(im, cb.DEUT if mode == 'deutan' else cb.TRIT)


def plate_at(k=1.0):
    return PLATE if k == 1.0 else PLATE.resize((int(1920 * k), int(1080 * k)), Image.LANCZOS)


def crop(pl, x, y, w, h):
    return pl.crop((x, y, x + w, y + h)).copy()


def squint(im, r=4):
    return im.filter(ImageFilter.GaussianBlur(r))


def up(im, s):
    return im.resize((im.width * s, im.height * s), Image.NEAREST)


def label_row(txt, W, h=28):
    im = Image.new('RGB', (W, h), (22, 16, 40))
    ImageDraw.Draw(im).text((14, 6), txt, font=F(FONT_M, 15), fill=(130, 220, 255))
    return im


def stack(rows, W):
    h = sum(r.height for r in rows)
    out = Image.new('RGB', (W, h), BG)
    y = 0
    for r in rows:
        out.paste(r, (0, y))
        y += r.height
    return out


def resample(poly, step=1.0):
    pts = [tuple(p) for p in poly]
    out = [pts[0]]
    carry = 0.0
    for a, b in zip(pts[:-1], pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 1e-6:
            continue
        s = step - carry
        while s <= L:
            out.append((a[0] + (b[0] - a[0]) * s / L, a[1] + (b[1] - a[1]) * s / L))
            s += step
        carry = L - (s - step)
    return out


def offset_poly(pts, d):
    """lateral offset of a dense polyline by d px (miter-free, sampled)."""
    out = []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        a = pts[max(i - 6, 0)]
        b = pts[min(i + 6, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        out.append((x - dy / L * d, y + dx / L * d))
    return out


def heading_at(pts, i, back=12):
    a = pts[max(i - back, 0)]
    b = pts[i]
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def draw_ribbon(d, pts, t, S, width, ink_w=None):
    """ribbon with a type pattern (second channel): D dark cross-cuts, N braid dots, E chevrons, X ticks. d draws on an S-times canvas."""
    ink_w = ink_w or width * 1.55
    d.line(pts, fill=INK + (255,), width=int(ink_w * S), joint='curve')
    d.line(pts, fill=HUE[t] + (255,), width=int(width * S), joint='curve')
    L = [0]
    for a, b in zip(pts[:-1], pts[1:]):
        L.append(L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    k = width / 11.0
    step = {'D': 9, 'N': 7, 'E': 12, 'X': 14}[t] * k * S
    s = step
    while s < L[-1] - 14 * k * S:
        i = max(j for j in range(len(L) - 1) if L[j] <= s)
        a, b = pts[i], pts[min(i + 1, len(pts) - 1)]
        seg = (L[i + 1] - L[i]) or 1
        f = (s - L[i]) / seg
        x, y = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        dx, dy = (b[0] - a[0]) / seg, (b[1] - a[1]) / seg
        nx, ny = -dy, dx
        if t == 'D':
            d.line([(x - nx * 5 * k * S, y - ny * 5 * k * S), (x + nx * 5 * k * S, y + ny * 5 * k * S)], fill=INK + (200,), width=max(1, int(1.6 * k * S)))
        elif t == 'N':
            sg = 1 if int(s / step) % 2 else -1
            r = 1.7 * k * S
            cx, cy = x + nx * 2.4 * k * S * sg, y + ny * 2.4 * k * S * sg
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 190, 245, 255))
        elif t == 'E':
            p = [(x - nx * 4.5 * k * S - dx * 3 * k * S, y - ny * 4.5 * k * S - dy * 3 * k * S), (x + dx * 3 * k * S, y + dy * 3 * k * S),
                 (x + nx * 4.5 * k * S - dx * 3 * k * S, y + ny * 4.5 * k * S - dy * 3 * k * S)]
            d.line(p, fill=INK + (230,), width=max(1, int(1.8 * k * S)))
        else:
            d.line([(x - nx * 3 * k * S, y - ny * 3 * k * S), (x + nx * 3 * k * S, y + ny * 3 * k * S)], fill=(90, 96, 120, 230), width=max(1, int(1.6 * k * S)))
        s += step


def head_on_ribbon_panel(base, size, k=1.0, heads=None, ribbon_w=None):
    """4 zig-zag ribbons (one per type) with heads leading, painted onto base (RGBA). size = head px in this canvas."""
    S = 3
    W, H = base.size
    rw = ribbon_w or size * .35
    lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    hd = []
    n = len(TYPES)
    for j, t in enumerate(TYPES):
        y0 = H * (j + .5) / n + 8 * k
        step = 1.0
        segs = [(-26, 52 * k), (26, 44 * k), (-26, 70 * k)]
        pts = [(8 * k + 4, y0 + 10 * k)]
        for ang, Lg in segs:
            a = math.radians(ang)
            x, y = pts[-1]
            pts.append((x + Lg * math.cos(a), y + Lg * math.sin(a)))
        dense = resample(pts, 1.0)
        draw_ribbon(d, [(x * S, y * S) for x, y in dense], t, S, rw)
        hd.append((t, dense[-1][0], dense[-1][1], heading_at(dense, len(dense) - 1)))
    glow = lay.filter(ImageFilter.GaussianBlur(5 * S)).resize((W, H), Image.LANCZOS)
    lay = lay.resize((W, H), Image.LANCZOS)
    base.alpha_composite(glow)
    base.alpha_composite(lay)
    for t, x, y, a in hd:
        paste_head(base, head(t), x, y, size, a, t)
    return base


def card_panel(size_glyph=22, W=300, H=128, k=1.0, base_pl=None):
    pl = base_pl if base_pl is not None else PLATE
    im = crop(pl, int((CROP_GAME[0] + 20) * k), int((CROP_GAME[1] + 10) * k), W, H)
    im = Image.alpha_composite(im, Image.new('RGBA', im.size, (10, 6, 20, 150)))
    d = ImageDraw.Draw(im)
    for i, t in enumerate(TYPES):
        cx = 40 + i * 74
        x0, y0, x1, y1 = cx - 30, 8, cx + 30, 118
        d.rounded_rectangle([x0 - 1.5, y0 - 1.5, x1 + 1.5, y1 + 1.5], 6, fill=INK + (255,))
        d.rounded_rectangle([x0, y0, x1, y1], 5, fill=BONE + (255,))
        d.rounded_rectangle([x0, y0, x1, y0 + 28], 5, fill=HUE[t] + (255,))
        d.rectangle([x0, y0 + 20, x1, y0 + 28], fill=HUE[t] + (255,))
        for r in range(3):
            d.rectangle([cx - 16 + (r % 2) * 5, y0 + 44 + r * 14, cx + 12 + (r % 2) * 5, y0 + 53 + r * 14], outline=INK + (255,), width=2)
        paste_head(im, head(t), cx, y0 + 14, size_glyph, 0, t, fill=INK, ow=0, detail=HUE[t], shade=False, mot_min=20)
    return im
