"""ART-1 1D spike (b): the finish of the baked district (port of art-concepts-r43 round 40 `post40.finish`).

python post_bake.py <district.json> <bakedir> <view>[,<view>...]   -> <bakedir>/<view>_final.png

Per view: see-through buildings over the ground-only pass (raid / netrun band: opacity, x0.86, chroma x1.35), lane glow
at 28 % at management zooms, wobbly ink from id / normal / depth edges (thickened), grime, light spill and bloom from
the emission pass, low fog patches, depth haze, rain and the night grade. Deterministic (seeded noise).
Never run from stdin (machine rule): run this file.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

MODE = dict(ink=(0.05, 0.04, 0.09), haze=(0.08, 0.06, 0.16), haze_k=0.34, bloom=0.75, spill=0.5, rain=(0.75, 0.82, 1.0),
            rain_a=0.11, grime=0.15, fog=(0.20, 0.17, 0.33), grade=(0.94, 0.92, 1.04))
SEE = dict(dark=0.86, chroma=1.35, win=0.15)


def load(p):
    im = Image.open(p)
    a = np.asarray(im)
    if a.dtype == np.uint16 or im.mode.startswith("I"):
        a = a.astype(np.float32) / 65535.0
    else:
        a = np.asarray(im.convert("RGB"), np.float32) / 255.0
    if a.ndim == 2:
        a = a[..., None].repeat(3, 2)
    return a[..., :3]


def to_lin(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def to_srgb(a):
    a = np.clip(a, 0, 1)
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - 0.055)


def _box(a, r, axis):
    n = a.shape[axis]
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode="edge"), axis=axis)
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return (hi - lo) / (2 * r + 1)


def blur(a, sigma):
    """Gaussian blur (three box passes per axis, sigma in px)."""
    if sigma <= 0.3:
        return a
    r = max(1, int(round(math.sqrt(12 * sigma * sigma / 3 + 1) / 2)))
    out = a.astype(np.float32)
    for _ in range(3):
        out = _box(out, r, 0)
        out = _box(out, r, 1)
    return out


def blur_down(a, r, k):
    h, w = a.shape[:2]
    k = max(1, int(k))
    small = np.stack([np.asarray(Image.fromarray(a[..., c].astype(np.float32), mode="F").resize((max(1, w // k), max(1, h // k)),
                                                                                                    Image.BILINEAR)) for c in range(3)], 2)
    small = blur(small, r / k)
    return np.stack([np.asarray(Image.fromarray(small[..., c], mode="F").resize((w, h), Image.BILINEAR)) for c in range(3)], 2)


def noise(h, w, cell, seed):
    rng = np.random.default_rng(seed)
    g = rng.random((h // cell + 2, w // cell + 2)).astype(np.float32)
    return np.asarray(Image.fromarray(g, mode="F").resize((w + cell * 2, h + cell * 2), Image.BICUBIC))[:h, :w]


def diff_edges(a, thr):
    d = np.abs(a - np.roll(a, -1, 1)).sum(axis=2) + np.abs(a - np.roll(a, -1, 0)).sum(axis=2)
    return (d > thr).astype(np.float32)


def warp(e, cell, amp, seed=5):
    h, w = e.shape
    dx = (noise(h, w, cell, seed) - 0.5) * 2 * amp
    dy = (noise(h, w, cell, seed + 1) - 0.5) * 2 * amp
    yy, xx = np.mgrid[0:h, 0:w]
    xs = np.clip((xx + dx).round().astype(int), 0, w - 1)
    ys = np.clip((yy + dy).round().astype(int), 0, h - 1)
    return e[ys, xs]


def maxf(e, n):
    return np.asarray(Image.fromarray((e * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(n)), np.float32) / 255.0


def finish(D, base, view, seed=1):
    v = D["views"][view]
    ortho, op, lod = v["ortho"], v["opacity"], v["lod"]
    beauty, glow = load(base + "beauty.png"), load(base + "glow.png")
    nrm, ids = load(base + "normal.png"), load(base + "id.png")
    depth = load(base + "depth.png")[..., 0] * 6000.0
    h, w = depth.shape
    sc = w / 2880.0
    bld = (ids.sum(axis=2) > 0.003).astype(np.float32)[..., None]
    city = v["city"]
    lk = 1.0 - 0.72 * (1 - city)
    lane = 1 - (1 - lk) * (1 - bld)
    beauty = beauty * lane
    glow = glow * lane
    if op < 0.999 and os.path.exists(base + "gbeauty.png"):
        gb = load(base + "gbeauty.png") * lk
        gg = load(base + "gglow.png") * lk * 0.7
        lum = beauty.mean(axis=2, keepdims=True)
        pb = np.clip(lum + (beauty - lum) * SEE["chroma"], 0, None)
        beauty = beauty * (1 - bld) + (gb * (1 - op) + pb * op * SEE["dark"]) * bld
        glow = glow * (1 - bld) + (gg * (1 - op) + glow * op * (0.45 + SEE["win"])) * bld
    e_id = diff_edges(ids, 0.03)
    e_n = diff_edges(nrm, 0.42)
    dd = np.abs(depth - np.roll(depth, -1, 1)) + np.abs(depth - np.roll(depth, -1, 0))
    e_d = (dd > 1.2 * (ortho / 300.0) / max(sc, 0.34)).astype(np.float32)
    ink = warp(np.maximum(np.maximum(e_id, e_n), e_d), 7, amp=1.4 * max(sc, 0.5))
    thick = maxf(ink, 3) if sc > 0.5 else ink
    ink_a = blur(thick[..., None], 0.7)[..., 0] * (0.85 if ortho < 400 else 0.6)
    ink_a = ink_a * (1 - (1 - op) * 0.55 * bld[..., 0])
    blot = noise(h, w, max(8, int(90 * sc)), 31) * 0.6 + noise(h, w, max(4, int(22 * sc)), 32) * 0.4
    g = 1 - MODE["grime"] * (blot - 0.5) * 1.4
    emis = np.clip(glow.max(axis=2) * 2, 0, 1)
    img = beauty * (g[..., None] * (1 - emis[..., None]) + emis[..., None])
    ink_a = ink_a * (1 - np.clip(emis * 1.6 - 0.4, 0, 1))
    img = img * (1 - ink_a[..., None]) + np.array(MODE["ink"], np.float32) * ink_a[..., None]
    b1 = blur_down(glow, 8 * sc, 2)
    b2 = blur_down(glow, 30 * sc, 4 if sc > 0.5 else 2)
    b3 = blur_down(glow, 90 * sc, 8 if sc > 0.5 else 4)
    img = img * (1 + MODE["spill"] * (b2 * 0.8 + b3 * 1.0)) + MODE["bloom"] * (b1 * 0.5 + b2 * 0.4 + b3 * 0.12)
    dep = depth - D["distance"]
    fog = 0.22
    fn = noise(h, w, max(16, int(160 * sc)), 70 + seed) * 0.6 + noise(h, w, max(8, int(60 * sc)), 71 + seed) * 0.4
    low = 0.4 * city + 0.6 * (bld[..., 0] < 0.5)
    fa = np.clip((fn - 0.5) * 2.6, 0, 1) * low * fog
    img = img * (1 - fa[..., None]) + (np.array(MODE["fog"], np.float32) + b3 * 1.2) * fa[..., None]
    far = np.clip((dep - 0.05 * ortho) / (1.2 * ortho), 0, 1) ** 1.2
    img = img * (1 - far[..., None] * MODE["haze_k"]) + np.array(MODE["haze"], np.float32) * far[..., None] * MODE["haze_k"]
    rng = np.random.default_rng(41 + seed)
    rl = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(rl)
    for _ in range(int(2200 * sc * sc) + 200):
        x, y = rng.uniform(-100, w), rng.uniform(-100, h)
        Ln = rng.uniform(30, 80) * sc
        d.line([(x, y), (x + Ln * 0.2, y + Ln)], fill=int(rng.uniform(80, 255)), width=1)
    r = np.asarray(rl.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255 * MODE["rain_a"]
    img = img * (1 - r[..., None]) + np.array(MODE["rain"], np.float32) * r[..., None]
    img = img * np.array(MODE["grade"], np.float32)
    return img


def main():
    D = json.load(open(sys.argv[1]))
    for view in sys.argv[3].split(","):
        base = os.path.join(sys.argv[2], view + "_")
        img = finish(D, base, view)
        out = base + "final.png"
        im = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))
        if im.size != (1920, 1080):
            im = im.resize((1920, 1080), Image.LANCZOS)  # post40: rendered at 2880, finished, then 1080p
        im.save(out)
        print("FINAL", out, flush=True)


if __name__ == "__main__":
    main()
