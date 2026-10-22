"""Solace THE BLOOM concept stills: shared helpers (noise, value metrics, glyphs, chips, gauges).

Pure numpy / PIL. Nothing here touches Godot. Colours: Solace pink #FF4696 on thin lines only, plum body ~#24101C.
Noise is hash based and seeded by integer ids only (no render-time RNG).
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "D:/rc_art/art-pass"
FONTS = os.path.join(REPO, "assets", "fonts")
MONO = os.path.join(FONTS, "ShareTechMono-Regular.ttf")
SCRATCH = "D:/rc_scratch/solace_v1/bloom"
OUT = os.path.join(REPO, "docs", "concepts", "solace_vertical", "bloom")

PINK = np.array([1.0, 0.275, 0.588], np.float32)         # #FF4696
PINK8 = (255, 70, 150)
PLUM = np.array([0.141, 0.063, 0.110], np.float32)       # #24101C
PLUM8 = (36, 16, 28)
WHITE_PINK = np.array([1.0, 0.86, 0.93], np.float32)


def font(px):
    return ImageFont.truetype(MONO, int(px))


def luma(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def metrics(a):
    """a: float RGB 0..1. median luma, share < 0.10, share > 0.85."""
    L = luma(a)
    return dict(median=round(float(np.median(L)), 4), under10=round(float((L < 0.10).mean()), 4),
                over85=round(float((L > 0.85).mean()), 4))


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _hash(ix, iy, seed):
    h = (ix * 374761393 + iy * 668265263 + seed * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    h = h ^ (h >> 16)
    return (h & 0xFFFF).astype(np.float32) / 65535.0


def vnoise(x, y, seed=1):
    """Smooth value noise 0..1 on float arrays."""
    x = np.asarray(x, np.float64)
    y = np.asarray(y, np.float64)
    x0 = np.floor(x).astype(np.int64)
    y0 = np.floor(y).astype(np.int64)
    fx = (x - x0).astype(np.float32)
    fy = (y - y0).astype(np.float32)
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    a, b = _hash(x0, y0, seed), _hash(x0 + 1, y0, seed)
    c, d = _hash(x0, y0 + 1, seed), _hash(x0 + 1, y0 + 1, seed)
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def fbm(x, y, seed=1, octaves=4):
    s, amp, tot, f = 0.0, 0.5, 0.0, 1.0
    for o in range(octaves):
        s = s + amp * vnoise(x * f, y * f, seed + o * 17)
        tot += amp
        amp *= 0.5
        f *= 2.03
    return s / tot


# ------------------------------------------------------------------ 2D overlay drawing (supersampled)
SS = 2


def canvas(size):
    return Image.new("RGBA", (size[0] * SS, size[1] * SS), (0, 0, 0, 0))


def flatten(base_rgb01, layer):
    """Composite an RGBA overlay layer (supersampled) over float RGB 0..1 base. Returns float RGB 0..1."""
    h, w = base_rgb01.shape[:2]
    lay = layer.resize((w, h), Image.LANCZOS)
    a = np.asarray(lay, np.float32) / 255.0
    al = a[..., 3:4]
    # premultiplied resize would be cleaner; the glyphs are opaque-ish so this is fine
    return base_rgb01 * (1 - al) + a[..., :3] * al


def spore(d, cx, cy, r, col, w=2, notch=26, rot=-90):
    """SPORE glyph: a ring with three notches (coordinates in output px; d is a supersampled draw)."""
    s = SS
    box = [(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s]
    for k in range(3):
        a0 = rot + k * 120 + notch / 2
        a1 = rot + (k + 1) * 120 - notch / 2
        d.arc(box, a0, a1, fill=col, width=int(w * s))
    d.ellipse([(cx - r * 0.18) * s, (cy - r * 0.18) * s, (cx + r * 0.18) * s, (cy + r * 0.18) * s], fill=col)


def chip(d, x, y, text, col=PINK8, size=14, glyph=True, anchor="lm", alpha=235, pad=7):
    """A small terminal chip with an optional SPORE glyph. Returns its box in output px."""
    s = SS
    f = font(size * s)
    tw = f.getlength(text) / s
    gw = (size + 6) if glyph else 0
    hh = size + 12
    w = tw + 2 * pad + gw
    if anchor == "lm":
        x0, y0 = x, y - hh / 2
    elif anchor == "rm":
        x0, y0 = x - w, y - hh / 2
    else:
        x0, y0 = x - w / 2, y - hh / 2
    box = (x0, y0, x0 + w, y0 + hh)
    d.rectangle([c * s for c in box], fill=(18, 6, 14, alpha), outline=col + (230,), width=s)
    tx = x0 + pad
    if glyph:
        spore(d, tx + size / 2 - 1, y0 + hh / 2, size * 0.42, col, w=1.4)
        tx += gw
    d.text((tx * s, (y0 + hh / 2) * s), text, font=f, fill=col + (255,), anchor="lm")
    return box


def hatch(h, w, pitch=9, width=2, angle=45):
    """45 degree hatch field 0..1 (screen space)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    v = ((xx + yy) % pitch)
    return (v < width).astype(np.float32)


def blur(a, r):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(r))
    return np.asarray(im, np.float32) / 255.0


def poly_mask(h, w, polys, grow=0.0, feather=2.0):
    """Union of polygons (each a list of (x, y)); `grow` is the 10 % margin as a fraction of the bbox size."""
    m = Image.new("L", (w, h), 0)
    dr = ImageDraw.Draw(m)
    for p in polys:
        xs, ys = [q[0] for q in p], [q[1] for q in p]
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        bw, bh = max(xs) - min(xs), max(ys) - min(ys)
        x0, x1, y0, y1 = min(xs) - bw * grow, max(xs) + bw * grow, min(ys) - bh * grow, max(ys) + bh * grow
        dr.rectangle([x0, y0, x1, y1], fill=255)
    a = np.asarray(m, np.float32) / 255.0
    return blur(a, feather) if feather else a


def save_png(a, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).save(path)


def boxblur(a, r, passes=2):
    """Separable float box blur (edge replicate) for coordinate fields."""
    a = np.asarray(a, np.float32)
    for _ in range(passes):
        for ax in (0, 1):
            pad = [(0, 0)] * a.ndim
            pad[ax] = (r + 1, r)
            p = np.pad(a, pad, mode="edge")
            c = np.cumsum(p, axis=ax, dtype=np.float64)
            n = a.shape[ax]
            hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=ax)
            lo = np.take(c, np.arange(0, n), axis=ax)
            a = ((hi - lo) / (2 * r + 1)).astype(np.float32)
    return a
