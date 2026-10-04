"""Round 11: finish the Blender target renders into the painted backdrop (Pillow + numpy).

python backdrop.py            -> ../target_building_day.png, ../target_building_night.png (boss target)
                                 and ../scratch/backdrops/<variant>_<mode>.png (all, 1920 x 1080)
Input: ../scratch/bl/<variant>_{beauty_day,beauty_night,glow_day,glow_night,normal,id,depth}.png (2880 x 1620).

Steps (all seeded):
  1. ink: wobbly dark lines from part-id, normal and depth discontinuities (E's hand-drawn ink),
     thinner and lighter with distance;
  2. painted grime: low-frequency blotches + speckle multiplied over the surfaces, rust streaks under
     roof edges;
  3. glow: bloom of the emissive pass (two radii) + light spill (the blurred glow multiplied into nearby
     surfaces, so neon lights the walls and street);
  4. depth haze toward the horizon (violet at night, grey-blue by day);
  5. rain streaks;
  6. downsample to 1920 x 1080.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
SRC = os.path.join(OUT, "scratch", "bl")
DST = os.path.join(OUT, "scratch", "backdrops")
W, H = 1920, 1080

MODE = {
    # round 11b cool day: clearer air (haze 0.36 -> 0.22), cooler haze/rain, same bloom/spill/grime as day
    "daycool": dict(ink=(0.08, 0.08, 0.11), haze=(0.60, 0.67, 0.78), haze_k=0.22, bloom=0.4, spill=0.3, rain=(0.82, 0.88, 0.96),
                    rain_a=0.11, grime=0.26),
    "night": dict(ink=(0.05, 0.04, 0.09), haze=(0.09, 0.07, 0.17), haze_k=0.5, bloom=0.9, spill=0.75, rain=(0.75, 0.82, 1.0),
                  rain_a=0.16, grime=0.16),
    "day": dict(ink=(0.10, 0.08, 0.08), haze=(0.62, 0.63, 0.67), haze_k=0.36, bloom=0.4, spill=0.3, rain=(0.85, 0.87, 0.92),
                rain_a=0.12, grime=0.26),
}


def load(name, mode="RGB"):
    im = Image.open(os.path.join(SRC, name))
    if im.mode.startswith("I;16") or im.mode == "I":
        a = np.asarray(im, np.float32) / 65535.0
        return a
    return np.asarray(im.convert(mode), np.float32) / 255.0


def blur(a, r):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255.0


def blur_f(a, r, down=4):
    """Blur a float RGB array at reduced resolution (big radii)."""
    h, w = a.shape[:2]
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((w // down, h // down), Image.BILINEAR)
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


def finish(variant, mode):
    M = MODE[mode]
    beauty = load("%s_beauty_%s.png" % (variant, mode))
    glow = load("%s_glow_%s.png" % (variant, mode))
    nrm = load("%s_normal.png" % variant)
    ids = load("%s_id.png" % variant)
    dep = load("%s_depth.png" % variant)
    if dep.ndim == 3:
        dep = dep[..., 0]
    dep = ((dep + 0.055) / 1.055) ** 2.4  # the Standard view transform stored it sRGB-encoded
    h, w = dep.shape
    # ---- ink
    e_id = diff_edges(ids, 0.03)
    e_n = diff_edges(nrm, 0.42)
    rel = np.abs(dep - np.roll(dep, -1, 1)) + np.abs(dep - np.roll(dep, -1, 0))
    e_d = (rel / np.maximum(dep, 1e-3) > 0.09).astype(np.float32)
    ink = np.maximum(np.maximum(e_id, e_n), e_d)
    ink = warp(ink, 7 if mode == "night" else 7)
    thick = np.asarray(Image.fromarray((ink * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) / 255
    near = np.clip(1.25 - dep * 2.2, 0.35, 1.0)  # far lines lighter (haze)
    ink_a = np.clip(thick * near, 0, 1) * 0.9
    ink_a = blur(ink_a[..., None].repeat(3, 2), 0.7)[..., 0]
    # ---- painted grime on surfaces (not on emissives)
    blot = noise(h, w, 90, 31) * 0.6 + noise(h, w, 22, 32) * 0.4
    speck = np.random.default_rng(33).random((h, w)).astype(np.float32)
    g = 1 - M["grime"] * (blot - 0.5) * 1.4 - 0.05 * (speck > 0.985)
    # rust/water streaks: pull down the ink edges under roof lines with a vertical blur
    streak = Image.fromarray((thick * 255).astype(np.uint8)).resize((w, h // 6)).filter(ImageFilter.BoxBlur(1)).resize((w, h))
    streak = np.asarray(streak.filter(ImageFilter.GaussianBlur(1)), np.float32) / 255
    streak = np.roll(streak, 6, 0) * noise(h, w, 6, 34)
    g = g - 0.10 * streak
    emis = glow.max(axis=2)
    img = beauty * (g[..., None] * (1 - np.clip(emis * 2, 0, 1))[..., None] + np.clip(emis * 2, 0, 1)[..., None])
    # ---- ink over everything except the brightest emissives
    ink_a = ink_a * (1 - np.clip(emis * 1.6 - 0.4, 0, 1))
    img = img * (1 - ink_a[..., None]) + np.array(M["ink"], np.float32) * ink_a[..., None]
    # ---- glow: bloom + light spill
    b1 = blur_f(glow, 10, 2)
    b2 = blur_f(glow, 36, 4)
    b3 = blur_f(glow, 110, 8)
    img = img * (1 + M["spill"] * (b2 * 0.8 + b3 * 1.0)) + M["bloom"] * (b1 * 0.55 + b2 * 0.4 + b3 * 0.12)
    # ---- depth haze
    hz = np.clip((dep - 0.32) / 0.55, 0, 1) ** 1.2 * M["haze_k"]
    img = img * (1 - hz[..., None]) + np.array(M["haze"], np.float32) * hz[..., None]
    # ---- rain
    rng = np.random.default_rng(41 if mode == "night" else 42)
    rain = Image.new("L", (w, h), 0)
    from PIL import ImageDraw
    d = ImageDraw.Draw(rain)
    for _ in range(2600):
        x, y = rng.uniform(-100, w), rng.uniform(-100, h)
        L = rng.uniform(30, 90)
        d.line([(x, y), (x + L * 0.22, y + L)], fill=int(rng.uniform(90, 255)), width=1 if rng.random() < 0.8 else 2)
    r = np.asarray(rain.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255 * M["rain_a"]
    img = img * (1 - r[..., None]) + np.array(M["rain"], np.float32) * r[..., None]
    if mode in ("daycool", "day"):  # round 24: day IS the approved cool day; slight cool grade on top of the cooler render
        img = img * np.array([0.96, 0.99, 1.05], np.float32)
    if mode in ("day", "daycool"):  # a touch more contrast and colour so the day city is not washed out
        lum = img.mean(axis=2, keepdims=True)
        img = (lum + (img - lum) * 1.18 - 0.5) * 1.1 + 0.5
    out = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    os.makedirs(DST, exist_ok=True)
    out.save(os.path.join(DST, "%s_%s.png" % (variant, mode)))
    # keep the 1920 depth too (combat composition uses it for calm pools)
    Image.fromarray((np.clip(dep, 0, 1) * 255).astype(np.uint8)).resize((W, H)).save(os.path.join(DST, "%s_depth.png" % variant))
    print("backdrop", variant, mode, flush=True)
    return out


MODE["day"] = dict(MODE["daycool"])  # round 24: the approved round 11b cool day is the day look for every corp
CORPS4 = ["solace", "halcyon", "orbital", "rebel_cell"]

if __name__ == "__main__":
    jobs = [("%s_boss" % c, m) for c in CORPS4 for m in ("night", "day")] + [("%s_regular" % c, "night") for c in CORPS4]
    if len(sys.argv) > 1:
        jobs = [j for j in jobs if j[0].startswith(sys.argv[1])]
    for v, m in jobs:
        im = finish(v, m)
        corp, kind = v.rsplit("_", 1)
        im.save(os.path.join(OUT, "target_%s_%s_%s.png" % (corp, kind, m)))