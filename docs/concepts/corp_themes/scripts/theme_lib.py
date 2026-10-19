"""Corp theme concept stills: shared helpers on top of solace_lib (noise, metrics, glyph/chip drawing, hatch, flatten).

Adds: per-corp output dirs, median gain fitting, patterned lines (dotted / solid / dashed), eye / trace glyphs,
text panels, the Grid capture base, and the per-corp contact sheet (<= 1280 px).
Pure numpy / PIL. Heavy scratch goes to D:/rc_scratch/themes.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import solace_lib as L

REPO = L.REPO
ROUTE = os.path.join(REPO, "docs", "concepts", "route_map_graph")
STILLS = os.path.join(REPO, "docs", "concepts", "corp_themes", "stills")
SCRATCH = "D:/rc_scratch/themes"
GRID = "D:/Godot/rebel_cell/docs/art_review/PLAN2/GRID_VIEW_current.jpg"
W, H = 1920, 1080
SS = L.SS
GRID_MAP = (0, 96, 1469, 1087)      # map area of the Grid capture at 2.4x (left of the legend panel, under the top bar)


def out_dir(corp):
    p = os.path.join(STILLS, corp)
    os.makedirs(p, exist_ok=True)
    os.makedirs(SCRATCH, exist_ok=True)
    return p


def load_rgb(path, size=(W, H)):
    im = Image.open(path).convert("RGB")
    if im.size != size:
        im = im.resize(size, Image.LANCZOS)
    return np.asarray(im, np.float32) / 255.0


def grid_base():
    """The Grid capture (800 x 453) upscaled 2.4x and cropped to 1920 x 1080 (same as solace_raid)."""
    im = Image.open(GRID).convert("RGB").resize((int(800 * 2.4), int(453 * 2.4)), Image.LANCZOS)
    im = im.crop((0, 0, W, H)).filter(ImageFilter.UnsharpMask(1.6, 70, 2))
    return np.asarray(im, np.float32) / 255.0


def grid_protect(base):
    """Links, nodes, labels, text of the Grid capture: 1 = never touched (same recipe as solace_raid.protect)."""
    r, g, b = base[..., 0], base[..., 1], base[..., 2]
    Lm = L.luma(base)
    bright = L.smoothstep(0.42, 0.6, Lm)
    green = L.smoothstep(0.08, 0.2, g - np.maximum(r, b) * 0.95) * L.smoothstep(0.3, 0.5, g)
    m = np.maximum(bright, green)
    im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.0))
    return np.asarray(im, np.float32) / 255.0


def map_mask(feather=1.5):
    x0, y0, x1, y1 = GRID_MAP
    yy, xx = np.mgrid[0:H, 0:W]
    m = ((xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)).astype(np.float32)
    return L.blur(m, feather)


def save(a, path):
    L.save_png(a, path)


def vals(a):
    return L.metrics(a)


def fit_median(out, target, free, lo=0.5, hi=2.5, tol=0.002):
    """Bisect a gain on pixels weighted by `free` (0..1, HxW) so the frame median equals target."""
    free = free[..., None] if free.ndim == 2 else free
    if abs(float(np.median(L.luma(out))) - target) <= tol:
        return out
    a, b = lo, hi
    for _ in range(14):
        m = (a + b) / 2
        t = float(np.median(L.luma(np.clip(out * (1 + (m - 1) * free), 0, 1))))
        if t < target:
            a = m
        else:
            b = m
    return np.clip(out * (1 + ((a + b) / 2 - 1) * free), 0, 1)


def canvas():
    return L.canvas((W, H))


def flat(img, lay):
    return L.flatten(img, lay)


def pattern_line(d, pts, col, width, pattern="solid", dot=(2, 8), dash=(12, 6), phase=0.0):
    """Polyline in output px on a supersampled draw. pattern: solid | dotted | dashed."""
    s = SS
    pts = [(float(x), float(y)) for x, y in pts]
    if pattern == "solid":
        d.line([(x * s, y * s) for x, y in pts], fill=col, width=int(width * s), joint="curve")
        return
    on, off = (dot[0], dot[1] - dot[0]) if pattern == "dotted" else dash
    per = on + off
    t = -phase
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg < 1e-6:
            continue
        ux, uy = (x1 - x0) / seg, (y1 - y0) / seg
        p = 0.0
        while p < seg:
            ph = (t + p) % per
            if ph < on:
                ln = min(on - ph, seg - p)
                if pattern == "dotted":
                    cx, cy = x0 + ux * (p + ln / 2), y0 + uy * (p + ln / 2)
                    r = width / 2
                    d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], fill=col)
                else:
                    d.line([((x0 + ux * p) * s, (y0 + uy * p) * s), ((x0 + ux * (p + ln)) * s, (y0 + uy * (p + ln)) * s)],
                           fill=col, width=int(width * s))
                p += max(ln, 0.5)
            else:
                p += per - ph
        t += seg


def triline(d, x, y, size, col, w=2):
    """TRILINE glyph: dotted, solid, dashed strokes whose right ends meet at a dot. (x, y) = left middle."""
    gap = size * 0.28
    for k, pat in enumerate(("dotted", "solid", "dashed")):
        yy = y + (k - 1) * gap
        pattern_line(d, [(x, yy), (x + size * 0.8, yy)], col, w, pat, dot=(w, w * 4), dash=(size * 0.3, size * 0.15))
        d.line([((x + size * 0.8) * SS, yy * SS), ((x + size * 0.95) * SS, y * SS)], fill=col, width=int(w * SS))
    d.ellipse([(x + size * 0.95 - 2.5) * SS, (y - 2.5) * SS, (x + size * 0.95 + 2.5) * SS, (y + 2.5) * SS], fill=col)


def eye_glyph(d, cx, cy, r, rim, iris, lw=2, pupil=True):
    """Almond with an iris dot; rim = outline colour, iris = iris colour (RGBA tuples)."""
    s = SS
    top, bot = [], []
    for i in range(0, 41):
        t = i / 40.0
        x = (t - 0.5) * 2 * r * 1.25
        yv = r * 0.62 * (1 - ((t - 0.5) * 2) ** 2) ** 0.9
        top.append((cx + x, cy - yv))
        bot.append((cx + x, cy + yv))
    d.polygon([(x * s, y * s) for x, y in top + bot[::-1]], outline=rim, fill=(8, 14, 18, 200), width=int(lw * s))
    ir = r * 0.34
    d.ellipse([(cx - ir) * s, (cy - ir) * s, (cx + ir) * s, (cy + ir) * s], fill=iris)
    if pupil:
        pr = ir * 0.4
        d.ellipse([(cx - pr) * s, (cy - pr) * s, (cx + pr) * s, (cy + pr) * s], fill=(6, 10, 12, 255))


def panel(d, box, fill=(8, 12, 16, 215), outline=(120, 150, 160, 230), w=1):
    d.rectangle([c * SS for c in box], fill=fill, outline=outline, width=int(w * SS))


def text(d, x, y, s, size, col, anchor="lm"):
    d.text((x * SS, y * SS), s, font=L.font(size * SS), fill=col, anchor=anchor)


def tw(s, size):
    return L.font(size * SS).getlength(s) / SS


def chipbox(d, x, y, s, col, size=14, anchor="lm", fill=(8, 12, 16, 230), pad=7):
    f = L.font(size * SS)
    w = f.getlength(s) / SS + 2 * pad
    h = size + 12
    x0 = x if anchor == "lm" else (x - w if anchor == "rm" else x - w / 2)
    y0 = y - h / 2
    d.rectangle([x0 * SS, y0 * SS, (x0 + w) * SS, (y0 + h) * SS], fill=fill, outline=col, width=SS)
    d.text(((x0 + pad) * SS, y * SS), s, font=f, fill=col, anchor="lm")
    return (x0, y0, x0 + w, y0 + h)


def shape_mask(shape_fn, blur_r=0.0):
    """Draw with shape_fn(ImageDraw) on an L mask (output px), optional blur, return float 0..1 (H, W)."""
    m = Image.new("L", (W, H), 0)
    shape_fn(ImageDraw.Draw(m))
    if blur_r:
        m = m.filter(ImageFilter.GaussianBlur(blur_r))
    return np.asarray(m, np.float32) / 255.0


def sheet(corp, names, cols=3, tw_=416, th=234, accent=(200, 200, 210), bg=(10, 10, 14), out=None):
    """Contact sheet <= 1280 px wide: tiles of the PNGs in stills/<corp>."""
    m = 8
    rows = (len(names) + cols - 1) // cols
    sh = Image.new("RGB", (cols * tw_ + (cols + 1) * m, rows * (th + 22) + m), bg)
    d = ImageDraw.Draw(sh)
    for i, n in enumerate(names):
        im = Image.open(os.path.join(STILLS, corp, n + ".png")).convert("RGB").resize((tw_, th), Image.LANCZOS)
        x, y = m + (i % cols) * (tw_ + m), m + (i // cols) * (th + 22)
        sh.paste(im, (x, y + 18))
        d.text((x, y + 9), n, font=L.font(14), fill=accent, anchor="lm")
    p = out or os.path.join(STILLS, corp, corp + "_sheet.jpg")
    sh.save(p, quality=88)
    return sh.size
