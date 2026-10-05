"""Round 32: finish the Blender passes into the painted Cv2 + E look (round 30 backdrop pipeline, night only).

python finish.py <srcdir> <tag> <out.png> [W H]
  ink from id / normal / depth discontinuities (wobbly, lighter with distance), painted grime, bloom + light spill
  of the glow pass, violet depth haze, rain. Seeded.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

M = dict(ink=(0.05, 0.04, 0.09), haze=(0.09, 0.07, 0.17), haze_k=0.5, bloom=0.75, spill=0.45, rain=(0.75, 0.82, 1.0), rain_a=0.14, grime=0.16)


def load(path):
    im = Image.open(path)
    if im.mode.startswith("I;16") or im.mode == "I":
        return np.asarray(im, np.float32) / 65535.0
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


def blur(a, r):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255.0


def blur_f(a, r, down=4):
    h, w = a.shape[:2]
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((max(1, w // down), max(1, h // down)), Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(r / down)).resize((w, h), Image.BILINEAR)
    return np.asarray(im, np.float32) / 255.0


def noise(h, w, cell, seed):
    rng = np.random.default_rng(seed)
    n = rng.random((h // cell + 2, w // cell + 2)).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).resize(((w // cell + 2) * cell, (h // cell + 2) * cell), Image.BICUBIC)
    return np.asarray(im, np.float32)[:h, :w] / 255.0


def diff_edges(a, thr):
    e = np.zeros(a.shape[:2], np.float32)
    for dy, dx in ((0, 1), (1, 0), (1, 1)):
        b = np.roll(np.roll(a, -dy, 0), -dx, 1)
        d = np.abs(a - b)
        d = d.sum(axis=2) if d.ndim == 3 else d
        e = np.maximum(e, (d > thr).astype(np.float32))
    return e


def warp(mask, seed, amp=1.6):
    h, w = mask.shape
    ox = (noise(h, w, 48, seed) - 0.5) * 2 * amp
    oy = (noise(h, w, 48, seed + 1) - 0.5) * 2 * amp
    yy, xx = np.mgrid[0:h, 0:w]
    xs = np.clip(np.round(xx + ox).astype(np.int32), 0, w - 1)
    ys = np.clip(np.round(yy + oy).astype(np.int32), 0, h - 1)
    return mask[ys, xs]


def finish(src, tag, size=(1920, 1080), rain_n=2600, seed=7):
    beauty = load(os.path.join(src, "%s_beauty_night.png" % tag))
    glow = load(os.path.join(src, "%s_glow_night.png" % tag))
    nrm = load(os.path.join(src, "%s_normal.png" % tag))
    ids = load(os.path.join(src, "%s_id.png" % tag))
    dep = load(os.path.join(src, "%s_depth.png" % tag))
    if dep.ndim == 3:
        dep = dep[..., 0]
    dep = ((dep + 0.055) / 1.055) ** 2.4
    h, w = dep.shape
    sc = w / 2880.0
    e_id = diff_edges(ids, 0.03)
    e_n = diff_edges(nrm, 0.42)
    rel = np.abs(dep - np.roll(dep, -1, 1)) + np.abs(dep - np.roll(dep, -1, 0))
    e_d = (rel / np.maximum(dep, 1e-3) > 0.09).astype(np.float32)
    ink = np.maximum(np.maximum(e_id, e_n), e_d)
    ink = warp(ink, seed, 1.6 * sc)
    thick = np.asarray(Image.fromarray((ink * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) / 255
    near = np.clip(1.25 - dep * 2.2, 0.35, 1.0)
    ink_a = np.clip(thick * near, 0, 1) * 0.9
    ink_a = blur(ink_a, 0.7 * sc)
    blot = noise(h, w, int(90 * sc) or 1, 31) * 0.6 + noise(h, w, int(22 * sc) or 1, 32) * 0.4
    speck = np.random.default_rng(33).random((h, w)).astype(np.float32)
    g = 1 - M["grime"] * (blot - 0.5) * 1.4 - 0.05 * (speck > 0.985)
    g = np.where(dep > 0.97, 1.0, g)
    emis = glow.max(axis=2)
    img = beauty * (g[..., None] * (1 - np.clip(emis * 2, 0, 1))[..., None] + np.clip(emis * 2, 0, 1)[..., None])
    ink_a = ink_a * (1 - np.clip(emis * 1.6 - 0.4, 0, 1))
    img = img * (1 - ink_a[..., None]) + np.array(M["ink"], np.float32) * ink_a[..., None]
    b1 = blur_f(glow, 10 * sc, 2)
    b2 = blur_f(glow, 36 * sc, 4)
    b3 = blur_f(glow, 110 * sc, 8)
    img = img * (1 + M["spill"] * (b2 * 0.8 + b3 * 1.0)) + M["bloom"] * (b1 * 0.55 + b2 * 0.4 + b3 * 0.12)
    hz = np.clip((dep - 0.32) / 0.55, 0, 1) ** 1.2 * M["haze_k"]
    img = img * (1 - hz[..., None]) + np.array(M["haze"], np.float32) * hz[..., None]
    rng = np.random.default_rng(41)
    rain = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(rain)
    for _ in range(int(rain_n * sc)):
        x, y = rng.uniform(-100, w), rng.uniform(-100, h)
        L = rng.uniform(30, 90) * sc
        d.line([(x, y), (x + L * 0.22, y + L)], fill=int(rng.uniform(90, 255)), width=1 if rng.random() < 0.8 else 2)
    r = np.asarray(rain.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255 * M["rain_a"]
    img = img * (1 - r[..., None]) + np.array(M["rain"], np.float32) * r[..., None]
    return Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).resize(size, Image.LANCZOS)


if __name__ == "__main__":
    src, tag, out = sys.argv[1], sys.argv[2], sys.argv[3]
    size = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (1920, 1080)
    finish(src, tag, size).save(out)
    print("wrote", out)
