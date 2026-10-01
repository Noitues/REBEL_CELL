"""Wheat-paste posters: photocopied content on wet-pasted, torn, peeling paper."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from spraylib import blur, fbm, IMPACT, COUR, PAPER, PINK


# ----------------------------------------------------------------- photocopy
def photocopy(gray, rng, cell=5, lo=0.30, hi=0.66, toner=0.06, streaks=True):
    """High-contrast photocopy: blacks crush, mids go to a coarse halftone, whites blow out.

    gray: float array 0..1 (1 = white). Returns float 0..1 ink coverage (1 = black toner).
    """
    h, w = gray.shape
    g = gray + (fbm(h, w, rng, scales=(60, 14), weights=(0.7, 0.3)) - 0.5) * 0.10
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = math.radians(45)
    u = (xx * math.cos(a) + yy * math.sin(a)) / cell
    v = (-xx * math.sin(a) + yy * math.cos(a)) / cell
    dot = (np.sin(u * math.pi) * np.sin(v * math.pi)) * 0.5 + 0.5  # 0..1 screen
    t = np.clip((g - lo) / (hi - lo), 0, 1)
    ink = (dot > t).astype(np.float32)
    ink = np.where(g < lo, 1.0, ink)
    ink = np.where(g > hi, 0.0, ink)
    ink = np.clip(blur(ink, 0.5) * 1.25 - 0.1, 0, 1)
    # toner speckle and dropout
    sp = (rng.random((h, w)) < toner * 0.08).astype(np.float32)
    ink = np.clip(ink + blur(sp, 0.5) * 2, 0, 1)
    drop = fbm(h, w, rng, scales=(30, 6), weights=(0.5, 0.5))
    ink *= np.clip(1.08 - drop * 0.16, 0, 1)
    if streaks:
        cols = rng.random(w) < 0.012
        st = np.zeros((h, w), np.float32)
        st[:, cols] = rng.uniform(0.15, 0.4)
        st = blur(st, 0.6) * (0.5 + fbm(h, w, rng, scales=(80,), weights=(1,)))
        ink = np.clip(ink + st * 0.5, 0, 1)
    # copier edge darkening
    vig = np.clip(1 - np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy)) / (0.07 * min(w, h)), 0, 1)
    ink = np.clip(ink + vig * 0.35 * rng.random((h, w)), 0, 1)
    return ink


# ----------------------------------------------------------------- portrait
def portrait_gray(w, h, rng, ss=4):
    """Hooded, bandana-masked operative drawn as tonal shapes (hard split lighting)."""
    W, Hh = w * ss, h * ss
    img = Image.new("L", (W, Hh), 205)
    d = ImageDraw.Draw(img)
    for y in range(0, Hh, 4):
        d.rectangle((0, y, W, y + 4), fill=int(236 - 50 * (y / Hh)))
    cx = W * 0.5
    # shoulders / jacket
    d.polygon([(0, Hh), (0, Hh * 0.90), (W * 0.16, Hh * 0.80), (W * 0.34, Hh * 0.77), (W * 0.66, Hh * 0.77),
               (W * 0.86, Hh * 0.81), (W, Hh * 0.92), (W, Hh)], fill=30)
    d.polygon([(W * 0.14, Hh * 0.82), (W * 0.32, Hh * 0.78), (W * 0.36, Hh * 0.88), (W * 0.20, Hh * 0.95)], fill=165)
    # hood
    d.ellipse((cx - W * 0.43, Hh * 0.02, cx + W * 0.43, Hh * 0.92), fill=26)
    d.arc((cx - W * 0.43, Hh * 0.02, cx + W * 0.43, Hh * 0.92), 150, 245, fill=150, width=int(W * 0.022))
    # face
    fx0, fy0, fx1, fy1 = cx - W * 0.27, Hh * 0.13, cx + W * 0.27, Hh * 0.79
    d.ellipse((fx0, fy0, fx1, fy1), fill=238)
    # split light: right of a contour line through brow ridge, nose and cheek
    shade = [(cx + W * 0.06, fy0 - 2), (fx1 + 4, fy0), (fx1 + 4, fy1), (cx + W * 0.04, fy1),
             (cx + W * 0.05, Hh * 0.58), (cx + W * 0.10, Hh * 0.50), (cx + W * 0.035, Hh * 0.40),
             (cx + W * 0.05, Hh * 0.33), (cx + W * 0.10, Hh * 0.28), (cx + W * 0.04, Hh * 0.20)]
    mask = Image.new("L", (W, Hh), 0)
    ImageDraw.Draw(mask).ellipse((fx0, fy0, fx1, fy1), fill=255)
    sh = Image.new("L", (W, Hh), 0)
    ImageDraw.Draw(sh).polygon(shade, fill=255)
    sh = Image.fromarray(np.minimum(np.asarray(sh), np.asarray(mask)))
    img.paste(Image.new("L", (W, Hh), 52), (0, 0), sh)
    # rim light along the shadowed jaw so the head reads against the hood
    d.arc((fx0, fy0, fx1, fy1), -40, 60, fill=205, width=int(W * 0.014))
    # hairline fringe under hood
    d.polygon([(fx0, fy0 + Hh * 0.10), (cx - W * 0.10, fy0 - 4), (cx + W * 0.20, fy0 - 4), (fx1, fy0 + Hh * 0.12),
               (cx + W * 0.10, fy0 + Hh * 0.06), (cx - W * 0.02, fy0 + Hh * 0.09), (cx - W * 0.14, fy0 + Hh * 0.07)], fill=20)
    # lit-side cheek turn
    d.ellipse((fx0 + W * 0.015, Hh * 0.42, fx0 + W * 0.10, Hh * 0.60), fill=175)
    # goggles pushed up on forehead
    gy = Hh * 0.215
    d.rounded_rectangle((fx0 - W * 0.04, gy - Hh * 0.012, fx1 + W * 0.04, gy + Hh * 0.016), radius=6, fill=18)
    for sx in (-1, 1):
        lx = cx + sx * W * 0.125
        d.rounded_rectangle((lx - W * 0.105, gy - Hh * 0.045, lx + W * 0.105, gy + Hh * 0.04), radius=int(W * 0.045), fill=12)
        d.rounded_rectangle((lx - W * 0.08, gy - Hh * 0.03, lx + W * 0.08, gy + Hh * 0.025), radius=int(W * 0.035), fill=200 if sx < 0 else 130)
        d.line((lx - W * 0.06, gy - Hh * 0.012, lx - W * 0.01, gy - Hh * 0.022), fill=250, width=int(W * 0.014))
    # brows (heavy, stencil-like)
    d.polygon([(cx - W * 0.20, Hh * 0.335), (cx - W * 0.05, Hh * 0.315), (cx - W * 0.04, Hh * 0.34), (cx - W * 0.19, Hh * 0.36)], fill=15)
    d.polygon([(cx + W * 0.05, Hh * 0.315), (cx + W * 0.20, Hh * 0.325), (cx + W * 0.19, Hh * 0.35), (cx + W * 0.04, Hh * 0.34)], fill=5)
    # eyes
    d.ellipse((cx - W * 0.18, Hh * 0.375, cx - W * 0.065, Hh * 0.415), fill=248)
    d.ellipse((cx - W * 0.145, Hh * 0.372, cx - W * 0.095, Hh * 0.418), fill=12)
    d.ellipse((cx - W * 0.132, Hh * 0.38, cx - W * 0.117, Hh * 0.392), fill=255)
    d.line((cx - W * 0.185, Hh * 0.378, cx - W * 0.06, Hh * 0.372), fill=8, width=int(W * 0.013))
    d.ellipse((cx + W * 0.085, Hh * 0.38, cx + W * 0.13, Hh * 0.41), fill=3)
    d.ellipse((cx + W * 0.10, Hh * 0.386, cx + W * 0.11, Hh * 0.394), fill=215)
    # nose shadow
    d.polygon([(cx + W * 0.01, Hh * 0.42), (cx + W * 0.04, Hh * 0.505), (cx - W * 0.035, Hh * 0.52), (cx - W * 0.055, Hh * 0.51)], fill=60)
    # bandana over lower face
    band = [(fx0 - W * 0.03, Hh * 0.52), (fx1 + W * 0.03, Hh * 0.515), (fx1 + W * 0.04, Hh * 0.66),
            (cx + W * 0.06, Hh * 0.86), (cx - W * 0.03, Hh * 0.88), (fx0 - W * 0.04, Hh * 0.68)]
    d.polygon(band, fill=34)
    d.polygon([(fx0 - W * 0.03, Hh * 0.52), (cx, Hh * 0.518), (cx - W * 0.015, Hh * 0.86), (fx0 - W * 0.04, Hh * 0.68)], fill=80)
    for k in range(5):
        y = Hh * (0.555 + k * 0.055)
        d.line((fx0 + W * 0.0, y, cx, y + Hh * 0.025, fx1 - W * 0.0, y), fill=205, width=int(W * 0.011))
    for k in range(26):
        px = rng.uniform(fx0, fx1)
        py = rng.uniform(Hh * 0.545, Hh * 0.80)
        if py < Hh * 0.87 - abs(px - cx) * 0.9:
            r = rng.uniform(W * 0.007, W * 0.014)
            d.ellipse((px - r, py - r, px + r, py + r), fill=225)
    d.line((cx - W * 0.15, Hh * 0.6, cx - W * 0.06, Hh * 0.78), fill=12, width=int(W * 0.012))
    img = img.filter(ImageFilter.GaussianBlur(ss * 0.6)).resize((w, h), Image.LANCZOS)
    return np.asarray(img, np.float32) / 255


# ----------------------------------------------------------------- paper
def torn_alpha(w, h, rng, peel=None, peel_size=0.3, bites=1, jag=2.5):
    """Paper alpha with ragged edges, bites torn out, and an optional removed peel corner.

    Returns (alpha, flap_alpha, flap_coords, rim) where rim marks fresh torn fibre edges.
    """
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    n1 = (fbm(h, w, rng, scales=(18, 5), weights=(0.6, 0.4)) - 0.5) * 2
    dist = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy))
    a = np.clip((dist - 3 - n1 * jag) / 1.2, 0, 1)
    rim = np.zeros((h, w), np.float32)
    for _ in range(bites):
        side = rng.integers(0, 4)
        r = rng.uniform(0.10, 0.18) * min(w, h)
        if side == 0:
            c = (rng.uniform(0.3, 0.8) * w, 0)
        elif side == 1:
            c = (w, rng.uniform(0.45, 0.8) * h)
        elif side == 2:
            c = (rng.uniform(0.2, 0.7) * w, h)
        else:
            c = (0, rng.uniform(0.3, 0.7) * h)
        n2 = (fbm(h, w, rng, scales=(10, 4), weights=(0.6, 0.4)) - 0.5) * 2
        dd = np.hypot((xx - c[0]) * 1.0, (yy - c[1]) * 1.4) - r - n2 * r * 0.25
        bite = np.clip(dd / 1.2, 0, 1)
        rim = np.maximum(rim, np.clip(1 - np.abs(dd - 3) / 3.5, 0, 1) * (dd > 0))
        a *= bite
    flap = np.zeros((h, w), np.float32)
    fold = None
    if peel:
        s = peel_size * min(w, h)
        if peel == "tr":
            cx, cy, sx, sy = w, 0, -1, 1
        elif peel == "br":
            cx, cy, sx, sy = w, h, -1, -1
        elif peel == "bl":
            cx, cy, sx, sy = 0, h, 1, -1
        else:
            cx, cy, sx, sy = 0, 0, 1, 1
        # distance along the corner diagonal
        u = ((xx - cx) * sx + (yy - cy) * sy) / math.sqrt(2)
        n3 = (fbm(h, w, rng, scales=(9,), weights=(1,)) - 0.5) * 3
        cut = np.clip((u - s / math.sqrt(2) - n3) / 1.2, 0, 1)
        a *= cut
        # flap = the removed triangle mirrored across the fold line
        fold = (cx, cy, sx, sy, s)
        # reflect: point p -> p' where u' = 2*s/sqrt2 - u ; along fold unchanged
        k = s / math.sqrt(2)
        up = 2 * k - u
        # for a target pixel with u in [k, k + curl], its source is the corner triangle u' < k
        curl = 0.82
        src_u = k - (u - k) / curl
        flap = ((u >= k) & (src_u >= 0) & (u <= k + k * curl)).astype(np.float32)
        # restrict to inside poster rect along fold direction
        v = ((xx - cx) * sx - (yy - cy) * sy) / math.sqrt(2)
        flap *= (np.abs(v) < (src_u)).astype(np.float32)
        flap = blur(flap, 0.7)
    return a, flap, fold, rim


def wheatpaste(content_rgb, rng, peel="tr", peel_size=0.28, bites=1, gloss=1.0, wrinkles=5):
    """Paper poster from a float RGB content array (white paper = 1). Returns RGBA PIL with margin."""
    h, w, _ = content_rgb.shape
    m = 26
    Hh, Ww = h + 2 * m, w + 2 * m
    paper = np.ones((h, w, 3), np.float32) * PAPER
    fib = fbm(h, w, rng, scales=(40, 6, 2), weights=(0.5, 0.3, 0.2))
    paper *= (0.94 + 0.08 * fib)[..., None]
    # yellowed toward one corner
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    paper *= (1 - 0.06 * (xx / w) * (yy / h))[..., None] * np.array([1, 0.99, 0.95], np.float32)
    col = paper * content_rgb
    # paste wrinkles: ridges shaded with a light from top-left
    hgt = np.zeros((h, w), np.float32)
    for _ in range(wrinkles):
        x0, y0 = rng.uniform(0, w), rng.uniform(0, h)
        ang = rng.uniform(0, math.pi)
        ln = rng.uniform(0.3, 0.8) * max(w, h)
        px = (xx - x0) * math.cos(ang) + (yy - y0) * math.sin(ang)
        py = -(xx - x0) * math.sin(ang) + (yy - y0) * math.cos(ang)
        hgt += np.exp(-(py ** 2) / (2 * rng.uniform(1.5, 3.5) ** 2)) * np.clip(1 - np.abs(px) / (ln / 2), 0, 1) * rng.uniform(0.5, 1)
    # paste bubbles
    for _ in range(3):
        x0, y0 = rng.uniform(0.15, 0.85) * w, rng.uniform(0.15, 0.85) * h
        r = rng.uniform(8, 18)
        hgt += np.exp(-(((xx - x0) ** 2 + (yy - y0) ** 2) / (2 * r * r))) * 0.8
    gy, gx = np.gradient(blur(hgt, 1.0))
    sh = np.clip(-(gx * -0.7 + gy * -0.7) * 9, -1, 1)
    col = col * (1 + 0.16 * sh[..., None])
    # wet paste sheen: brushed streaks
    br = fbm(h, w * 4, rng, scales=(80, 20), weights=(0.6, 0.4))[:, ::4]
    br = np.clip((br - 0.55) * 3, 0, 1) * (0.5 + 0.5 * np.clip(sh, 0, 1))
    col = col + br[..., None] * 0.10 * gloss
    a, flap, fold, rim = torn_alpha(w, h, rng, peel=peel, peel_size=peel_size, bites=bites)
    # torn fibres: lighter, uncoated paper core at the tear
    col = col * (1 - rim[..., None] * 0.4) + np.array([0.97, 0.96, 0.92]) * rim[..., None] * 0.4
    out = np.zeros((Hh, Ww, 4), np.float32)
    # contact shadow on the glass (thin), stronger under the flap
    A = np.zeros((Hh, Ww), np.float32)
    A[m:m + h, m:m + w] = a
    F = np.zeros((Hh, Ww), np.float32)
    F[m:m + h, m:m + w] = flap
    shadow = np.clip(blur(np.roll(np.roll(A, 2, 0), 2, 1), 2.5) * 0.45 + blur(np.roll(np.roll(F, 7, 0), 5, 1), 6) * 0.7, 0, 0.8)
    out[..., 3] = shadow
    out[..., :3] = 0.0
    # paper
    pa = A
    P = np.zeros((Hh, Ww, 3), np.float32)
    P[m:m + h, m:m + w] = np.clip(col, 0, 1)
    out[..., :3] = P * pa[..., None] + out[..., :3] * (1 - pa[..., None])
    out[..., 3] = pa + out[..., 3] * (1 - pa)
    # flap: back of the paper, curling (darker at fold, bright at tip), ink ghosting through
    if fold is not None:
        cx, cy, sx, sy, s = fold
        uu = (((xx - cx) * sx + (yy - cy) * sy) / math.sqrt(2))
        k = s / math.sqrt(2)
        tcurl = np.clip((uu - k) / (k * 0.82), 0, 1)
        back = np.array([0.80, 0.78, 0.72], np.float32) * (0.72 + 0.38 * tcurl)[..., None]
        back = back * (0.95 + 0.06 * fib[..., None])
        ghost = 1 - (1 - content_rgb[::-1, ::-1].mean(axis=2)) * 0.10
        back = back * ghost[..., None]
        # specular rolling edge near the fold
        edge = np.exp(-((uu - k - 4) ** 2) / 18)
        back = back + edge[..., None] * 0.18
        FB = np.zeros((Hh, Ww, 3), np.float32)
        FB[m:m + h, m:m + w] = np.clip(back, 0, 1)
        out[..., :3] = FB * F[..., None] + out[..., :3] * (1 - F[..., None])
        out[..., 3] = F + out[..., 3] * (1 - F)
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "RGBA")


def text_ink(w, h, items, ss=3):
    """Black ink content from text items [(text, font_path, size, (x,y), anchor, var)]."""
    img = Image.new("L", (w * ss, h * ss), 255)
    d = ImageDraw.Draw(img)
    for it in items:
        text, fp, size, (x, y), anchor = it[:5]
        f = ImageFont.truetype(fp, int(size * ss))
        if len(it) > 5 and it[5]:
            f.set_variation_by_name(it[5])
        d.text((x * ss, y * ss), text, font=f, fill=0, anchor=anchor)
    return np.asarray(img.resize((w, h), Image.LANCZOS), np.float32) / 255
