"""V3 dynamic: finish the Blender passes into the locked world look (the parent's post.py: ink from id / normal /
depth, grime, bloom + light spill of the glow pass, violet depth haze, rain) plus what the moving camera needs:
  - haze and fog start relative to the shot's camera distance (so decision and overview grade alike);
  - a low height fog (wz pass) that pools at street level in the distance;
  - the background classes (mid row, far city) desaturated, darkened and softened, so the route leads;
  - the sky is a violet gradient PLUS the additive atmosphere already in the beauty (shafts, searchlights, trails);
  - rain catches light: its alpha follows the blurred glow; it falls with t in the video.
python post3.py <shot> [bl_dir] [t]  ->  ../scratch/plate_<shot>.png (+ glow_, sem_ at 1920 x 1080). Seeded.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.join(os.path.dirname(HERE), "scratch")
M = dict(ink=(0.05, 0.04, 0.09), haze_lo=(0.17, 0.07, 0.23), haze_hi=(0.06, 0.045, 0.13), bloom=0.75, spill=0.45,
         rain=(0.78, 0.84, 1.0), rain_a=0.10, grime=0.14, fog=(0.24, 0.13, 0.34))
BG_DESAT, BG_DARK, BG_SOFT = 0.4, 0.62, 1.4      # background classes: desaturate, multiply, blur (px at 2880)
HAZE_K0, HAZE_RAMP, HAZE_MAX = 1.18, 260.0, 0.72  # haze starts at 1.18 x the camera distance, ramps over 260 BU
FOG_H, FOG_MAX = 26.0, 0.42                       # height fog: thickest at street level, gone by 26 BU


def load(path):
    im = Image.open(path)
    if im.mode.startswith("I;16") or im.mode == "I":
        return np.asarray(im, np.float32) / 65535.0
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


def blur_f(a, r, down=4):
    h, w = a.shape[:2]
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((max(1, w // down), max(1, h // down)), Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(max(0.5, r / down))).resize((w, h), Image.BILINEAR)
    return np.asarray(im, np.float32) / 255.0


def blur(a, r):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255.0


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


def lum(a):
    return a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11


def finish(shot, bl, t=2.0, rain_n=2600, seed=7, out_size=(1920, 1080)):
    P = lambda k: os.path.join(bl, "%s_%s.png" % (shot, k))  # noqa: E731
    A = json.load(open(os.path.join(bl, "anchors_%s.json" % shot)))
    cam_d = A["cam"].get("dist", 120.0)
    beauty = load(P("beauty"))
    glow = load(P("glow"))
    nrm = load(P("normal"))
    ids = load(P("id"))
    dep = load(P("depth"))
    sem = load(P("sem"))
    wz = load(P("wz"))
    if dep.ndim == 3:
        dep = dep[..., 0]
    if wz.ndim == 3:
        wz = wz[..., 0]
    dep = ((dep + 0.055) / 1.055) ** 2.4
    dist = dep * 1500.0
    sky = dep > 0.999
    wzw = wz * 300.0 - 10.0
    cls = sem[..., 0] if sem.ndim == 3 else sem
    h, w = dep.shape
    sc = w / 2880.0
    bgm = ((np.abs(cls - 0.6) < 0.04) | (np.abs(cls - 0.85) < 0.04)).astype(np.float32)
    bgm = np.where(sky, 0, bgm)
    e_id = diff_edges(ids, 0.03)
    e_n = diff_edges(nrm, 0.42)
    rel = np.abs(dep - np.roll(dep, -1, 1)) + np.abs(dep - np.roll(dep, -1, 0))
    e_d = (rel / np.maximum(dep, 1e-3) > 0.012).astype(np.float32)
    ink = np.maximum(np.maximum(e_id, e_n), e_d)
    ink = warp(ink, seed, 1.6 * sc)
    thick = np.asarray(Image.fromarray((ink * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) / 255
    d0 = cam_d * HAZE_K0
    hz = np.clip((dist - d0) / HAZE_RAMP, 0, 1) ** 1.1 * HAZE_MAX
    near = 1.0 - hz * 1.2
    ink_a = np.clip(thick * np.clip(near, 0.25, 1), 0, 1) * 0.88 * (1 - 0.45 * bgm)
    ink_a = blur(ink_a, 0.7 * sc)
    blot = noise(h, w, int(90 * sc) or 1, 31) * 0.6 + noise(h, w, int(22 * sc) or 1, 32) * 0.4
    speck = np.random.default_rng(33).random((h, w)).astype(np.float32)
    g = 1 - M["grime"] * (blot - 0.5) * 1.4 - 0.05 * (speck > 0.985)
    g = np.where(sky, 1.0, g)
    emis = glow.max(axis=2)
    ek = np.clip(emis * 2, 0, 1)[..., None]
    img = beauty * (g[..., None] * (1 - ek) + ek)
    ink_a = ink_a * (1 - np.clip(emis * 1.6 - 0.4, 0, 1))
    ink_a = np.where(sky, 0, ink_a)
    img = img * (1 - ink_a[..., None]) + np.array(M["ink"], np.float32) * ink_a[..., None]
    # background classes: quieter (desaturated, darker, softer) before the light lands on them
    l3 = lum(img)[..., None]
    bg_img = (img * (1 - BG_DESAT) + l3 * BG_DESAT) * BG_DARK
    bg_img = blur(bg_img, BG_SOFT * sc)
    img = img * (1 - bgm[..., None]) + bg_img * bgm[..., None]
    b1 = blur_f(glow, 10 * sc, 2)
    b2 = blur_f(glow, 36 * sc, 4)
    b3 = blur_f(glow, 110 * sc, 8)
    img = img * (1 + M["spill"] * (b2 * 0.8 + b3 * 1.0)) + M["bloom"] * (b1 * 0.55 + b2 * 0.4 + b3 * 0.12)
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    top, bot = np.array((0.035, 0.025, 0.08), np.float32), np.array((0.22, 0.08, 0.27), np.float32)
    grad = top + (bot - top) * (yy ** 1.5)[..., None]
    grad = np.broadcast_to(grad, (h, w, 3))
    hcol = np.array(M["haze_hi"], np.float32) + (np.array(M["haze_lo"], np.float32) - np.array(M["haze_hi"], np.float32)) * (yy ** 1.2)[..., None]
    hz = np.where(sky, 0, hz)
    img = img * (1 - hz[..., None]) + hcol * hz[..., None]
    fog = np.clip(1 - wzw / FOG_H, 0, 1) ** 1.5 * np.clip((dist - cam_d * 0.95) / 160.0, 0, 1) * FOG_MAX
    fog = np.where(sky, 0, fog) * (0.75 + 0.5 * noise(h, w, int(160 * sc) or 1, 51))
    img = img * (1 - fog[..., None]) + np.array(M["fog"], np.float32) * fog[..., None]
    img = np.where(sky[..., None], grad + beauty * 1.0 + M["bloom"] * (b2 * 0.4 + b3 * 0.2), img)
    # rain: falls with t, lit by the spill around it
    rng = np.random.default_rng(41)
    rain = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(rain)
    fall = t * 1400 * sc
    for _ in range(int(rain_n * sc)):
        x, y = rng.uniform(-100, w), rng.uniform(-100, h)
        L = rng.uniform(30, 90) * sc
        y = (y + fall * rng.uniform(0.8, 1.2)) % (h + 100) - 100
        x = x + 0.22 * fall * 0.0
        d.line([(x, y), (x + L * 0.22, y + L)], fill=int(rng.uniform(90, 255)), width=1 if rng.random() < 0.8 else 2)
    r = np.asarray(rain.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255 * M["rain_a"]
    lit = np.clip(0.35 + 3.0 * lum(b3 + b2 * 0.5), 0.35, 2.2)
    r = r * lit
    img = img * (1 - np.clip(r, 0, 1)[..., None]) + np.array(M["rain"], np.float32) * r[..., None]
    out = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).resize(out_size, Image.LANCZOS)
    return out


def save_aux(shot, bl, out_size=(1920, 1080), dst=None):
    dst = dst or SCR
    Image.open(os.path.join(bl, "%s_glow.png" % shot)).convert("RGB").resize(out_size, Image.LANCZOS).save(
        os.path.join(dst, "glow_%s.png" % shot))
    sem = Image.fromarray((load(os.path.join(bl, "%s_sem.png" % shot)) * 255 + 0.5).astype(np.uint8))
    sem.resize(out_size, Image.NEAREST).save(os.path.join(dst, "sem_%s.png" % shot))


if __name__ == "__main__":
    shot = sys.argv[1]
    bl = sys.argv[2] if len(sys.argv) > 2 else os.path.join(SCR, "bl")
    t = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    finish(shot, bl, t).save(os.path.join(SCR, "plate_%s.png" % shot))
    save_aux(shot, bl)
    print("plate", shot)
