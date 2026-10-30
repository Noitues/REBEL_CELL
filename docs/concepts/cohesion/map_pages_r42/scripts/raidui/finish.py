"""Round 18: finish a district render into the painted raid map (Pillow + numpy, seeded).

finish(tag, mode, approach, statuses, ...) -> 1920 x 1080 float RGB (no UI)
Input (scratch/bl/): <tag>_beauty_<mode>.png, <tag>_glow_<mode>.png, <tag>_normal.png, <tag>_id.png,
<tag>_pos.npy, <tag>_scene.json from district.py.

Order (each step = one layer / pass in Godot):
  1. street-plane network decal (netdecal.Net) mixed into the beauty and the glow buffer;
  2. ink lines from id / normal / depth (E's hand-drawn line), grime;
  3. heat: searchlight pools on whatever they hit, corp creep tint on the streets;
  4. bloom + light spill (pads and neon light the asphalt and the units standing on them);
  5. fog PATCHES: noise-masked blobs at street level, each with its own blur, hidden behind
     nearer buildings (depth test), tinted by the neon under them;
  6. tilt-shift: depth-of-field blur from the depth pass, sharp band on the network;
  7. depth haze, rain (night), downsample.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as LY  # noqa: E402
import netdecal as ND  # noqa: E402

ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "scratch", "bl")

MODE = {
    "night": dict(ink=(0.05, 0.04, 0.09), haze=(0.08, 0.06, 0.16), haze_k=0.42, bloom=0.8, spill=0.55,
                  rain=(0.75, 0.82, 1.0), rain_a=0.12, grime=0.16, fog=(0.17, 0.15, 0.30), fog_k=1.0,
                  grade=(0.92, 0.9, 1.04), lift=0.0),
    "day": dict(ink=(0.09, 0.08, 0.11), haze=(0.62, 0.68, 0.80), haze_k=0.30, bloom=0.35, spill=0.25,
                rain=(0.85, 0.87, 0.92), rain_a=0.0, grime=0.26, fog=(0.80, 0.83, 0.90), fog_k=0.2,
                grade=(0.98, 1.0, 1.03), lift=0.0),
}


def load(name):
    im = Image.open(os.path.join(SRC, name))
    if im.mode.startswith("I;16") or im.mode == "I":
        return np.asarray(im, np.float32) / 65535.0
    a = np.asarray(im)
    if a.dtype == np.uint16:
        return a.astype(np.float32) / 65535.0
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


def boxblur(a, r, axis):
    if r < 1:
        return a
    r = int(r)
    c = np.cumsum(a, axis=axis, dtype=np.float32)
    n = a.shape[axis]
    pad_shape = list(a.shape)
    pad_shape[axis] = 1
    z = np.zeros(pad_shape, np.float32)
    c = np.concatenate([z, c], axis=axis)
    idx_hi = np.clip(np.arange(n) + r + 1, 0, n)
    idx_lo = np.clip(np.arange(n) - r, 0, n)
    out = (np.take(c, idx_hi, axis=axis) - np.take(c, idx_lo, axis=axis)) / (idx_hi - idx_lo).reshape(
        [-1 if i == axis else 1 for i in range(a.ndim)]).astype(np.float32)
    return out


def blur(a, sigma):
    """Gaussian-ish blur (3 box passes), float, any channels."""
    if sigma <= 0.3:
        return a
    r = max(1, int(round(sigma * 0.95)))
    for _ in range(3):
        a = boxblur(a, r, 0)
        a = boxblur(a, r, 1)
    return a


def blur_down(a, sigma, down=4):
    h, w = a.shape[:2]
    hh, ww = h // down * down, w // down * down
    small = a[:hh, :ww].reshape(hh // down, down, ww // down, down, *a.shape[2:]).mean((1, 3))
    small = blur(small, sigma / down)
    big = np.repeat(np.repeat(small, down, 0), down, 1)
    if hh < h or ww < w:
        big = np.pad(big, [(0, h - hh), (0, w - ww)] + [(0, 0)] * (a.ndim - 2), mode="edge")
    return big


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
    return mask[np.clip(np.round(yy + oy).astype(np.int32), 0, h - 1), np.clip(np.round(xx + ox).astype(np.int32), 0, w - 1)]


def maxf(a, k=3):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(k))
    return np.asarray(im, np.float32) / 255.0


def depth_of(pos):
    r, u, f = LY.cam_basis()
    t = LY.CAM["target"]
    return (pos[..., 0] - t[0]) * f[0] + (pos[..., 1] - t[1]) * f[1] + (pos[..., 2] - t[2]) * f[2]


class Passes:
    def __init__(self, tag):
        self.tag = tag
        self.pos = np.load(os.path.join(SRC, tag + "_pos.npy")).astype(np.float32)
        self.nrm = load(tag + "_normal.png")
        self.ids = load(tag + "_id.png")
        self.scene = json.load(open(os.path.join(SRC, tag + "_scene.json")))
        self.dep = depth_of(self.pos)
        self.h, self.w = self.dep.shape
        z = self.pos[..., 2]
        self.ground = (z < 0.1) & (z > -0.5)

    def beauty(self, mode):
        return load("%s_beauty_%s.png" % (self.tag, mode)), load("%s_glow_%s.png" % (self.tag, mode))


_cache = {}


def passes(tag):
    if tag not in _cache:
        _cache[tag] = Passes(tag)
    return _cache[tag]


FOCUS_DEPTH = -12.0    # the network's depth band (pads range about -45 .. +25 m)


def finish(tag, mode, approach, statuses, wave=False, heat=1, lanes=True, tilt=1.0, fog=1.0, seed=1, threats=None):
    M = MODE[mode]
    P = passes(tag)
    beauty, glow = P.beauty(mode)
    h, w = P.h, P.w
    X, Y = P.pos[..., 0], P.pos[..., 1]
    dep = P.dep
    # ---- 1. network decal on the street plane
    net = ND.Net(X, Y, P.ground, approach, statuses, mode=mode, wave=wave, heat=heat, threat_lanes=lanes)
    em, dk = net.build(threats)
    if mode == "day":
        em = em * 0.85
    beauty = beauty * dk[..., None]
    glow = glow * dk[..., None] + em * 0.6
    # ---- 2. ink
    e_id = diff_edges(P.ids, 0.03)
    e_n = diff_edges(P.nrm, 0.42)
    dd = np.abs(dep - np.roll(dep, -1, 1)) + np.abs(dep - np.roll(dep, -1, 0))
    e_d = (dd > 1.6).astype(np.float32)
    ink = np.maximum(np.maximum(e_id, e_n), e_d)
    ink = warp(ink, 7)
    thick = maxf(ink, 3)
    ink_a = blur(thick, 0.7) * 0.9
    # grime
    blot = noise(h, w, 90, 31) * 0.6 + noise(h, w, 22, 32) * 0.4
    speck = np.random.default_rng(33).random((h, w)).astype(np.float32)
    g = 1 - M["grime"] * (blot - 0.5) * 1.4 - 0.05 * (speck > 0.985)
    emis = np.clip(glow.max(axis=2) * 2, 0, 1) if mode == "night" else np.clip((glow.max(axis=2) - 0.16) * 2.6, 0, 1)
    img = beauty * (g[..., None] * (1 - emis[..., None]) + emis[..., None])
    img = img + em * (0.72 if mode == "night" else 0.6)
    ink_a = ink_a * (1 - np.clip(emis * 1.6 - 0.4, 0, 1))
    img = img * (1 - ink_a[..., None]) + np.array(M["ink"], np.float32) * ink_a[..., None]
    # ---- 3. heat: searchlight pools + corp creep
    z = P.pos[..., 2]
    for (tx, ty, rr, k) in P.scene.get("pools", []):
        d = np.hypot(X - tx, Y - ty)
        L = np.exp(-(d / rr) ** 2 * 1.6) * (z < 40) * k
        img = img * (1 + 1.5 * L[..., None]) + L[..., None] * np.array([0.32, 0.33, 0.36], np.float32)
        glow = glow + L[..., None] * np.array([0.25, 0.26, 0.3], np.float32)
    if heat >= 2:
        creep = np.zeros((h, w), np.float32)
        for e in LY.ENTRIES.values():
            creep = np.maximum(creep, np.exp(-(np.hypot(X - e[0], Y - e[1]) / (70 + 60 * (heat - 2))) ** 2))
        creep *= P.ground * (0.5 if heat == 2 else 0.75)
        tint = np.array([0.55, 0.42, 1.0], np.float32) if mode == "night" else np.array([0.75, 0.68, 1.0], np.float32)
        img = img * (1 - creep[..., None] * 0.5) + creep[..., None] * tint * 0.22
    # ---- 4. bloom + spill
    b1 = blur_down(glow, 8, 2)
    b2 = blur_down(glow, 30, 4)
    b3 = blur_down(glow, 90, 8)
    img = img * (1 + M["spill"] * (b2 * 0.8 + b3 * 1.0)) + M["bloom"] * (b1 * 0.5 + b2 * 0.4 + b3 * 0.12)
    # ---- 5. fog patches (varying blur, depth-tested)
    if fog > 0:
        img = fog_patches(img, P, M, b3, seed, fog)
    # ---- 6. tilt-shift
    if tilt > 0:
        img = tilt_shift(img, dep, tilt)
    # ---- 7. haze + rain + grade
    far = np.clip((dep - 60) / 240, 0, 1) ** 1.1
    img = img * (1 - far[..., None] * M["haze_k"]) + np.array(M["haze"], np.float32) * far[..., None] * M["haze_k"]
    if M["rain_a"] > 0:
        rng = np.random.default_rng(41 + seed)
        rain = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(rain)
        for _ in range(2200):
            x, y = rng.uniform(-100, w), rng.uniform(-100, h)
            L = rng.uniform(30, 80)
            d.line([(x, y), (x + L * 0.2, y + L)], fill=int(rng.uniform(80, 255)), width=1)
        r = np.asarray(rain.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255 * M["rain_a"]
        img = img * (1 - r[..., None]) + np.array(M["rain"], np.float32) * r[..., None]
    img = img * np.array(M["grade"], np.float32)
    if mode == "day":
        lum = img.mean(axis=2, keepdims=True)
        img = (lum + (img - lum) * 1.32 - 0.5) * 1.1 + 0.5
    out = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).resize((LY.W, LY.H), Image.LANCZOS)
    return np.asarray(out, np.float32) / 255.0


def fog_patches(img, P, M, glowb, seed, k):
    h, w = P.h, P.w
    rng = np.random.default_rng(500 + seed)
    acc_c = np.zeros((h, w, 3), np.float32)
    acc_a = np.zeros((h, w), np.float32)
    nodes = [LY.project(n[0], n[1], 0, w, h) for n in LY.NODES.values()]
    placed = 0
    tries = 0
    while placed < 34 and tries < 400:
        tries += 1
        x, y = rng.uniform(-300, 330), rng.uniform(-300, 320)
        zz = rng.uniform(0, 14)
        px, py, pd = LY.project(x, y, zz, w, h)
        if not (-200 < px < w + 200 and -200 < py < h + 200):
            continue
        near_node = min(math.hypot(px - q[0], py - q[1]) for q in nodes)
        a_max = rng.uniform(0.12, 0.4) * (0.35 if near_node < 160 else 1.0)
        rw, rh = rng.uniform(140, 520), rng.uniform(50, 170)
        sig = float(rng.choice([2, 4, 8, 14, 24, 40]))   # each patch its own softness
        x0, y0 = int(max(0, px - rw - 3 * sig)), int(max(0, py - rh - 3 * sig))
        x1, y1 = int(min(w, px + rw + 3 * sig)), int(min(h, py + rh + 3 * sig))
        if x1 - x0 < 8 or y1 - y0 < 8:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        ang = rng.uniform(-0.5, 0.5)
        u = ((xx - px) * math.cos(ang) + (yy - py) * math.sin(ang)) / rw
        v = (-(xx - px) * math.sin(ang) + (yy - py) * math.cos(ang)) / rh
        n = noise(y1 - y0, x1 - x0, int(rng.integers(18, 60)), int(rng.integers(0, 10000)))
        m = np.clip(1.15 - (u * u + v * v) - (n - 0.5) * 1.3, 0, 1)
        m = np.clip((m - 0.25) * 1.8, 0, 1)
        m = blur(m, sig)
        # depth test: hide behind buildings nearer than the patch
        nearer = P.dep[y0:y1, x0:x1] < pd - 6.0
        m = m * (1 - nearer) * a_max
        acc_a[y0:y1, x0:x1] = 1 - (1 - acc_a[y0:y1, x0:x1]) * (1 - m)
        placed += 1
    fogc = np.array(M["fog"], np.float32) + glowb * 1.2
    acc_a *= k
    return img * (1 - acc_a[..., None]) + fogc * acc_a[..., None]


def tilt_shift(img, dep, k):
    """Depth-of-field: sharp band at FOCUS_DEPTH, blur grows with |depth - focus|."""
    band, ramp = 60.0, 150.0
    t = np.clip((np.abs(dep - FOCUS_DEPTH) - band) / ramp, 0, 1) * k
    levels = [0.0, 2.0, 4.5, 8.0, 13.0]
    stack = [img] + [blur(img, s) for s in levels[1:]]
    f = t * (len(levels) - 1)
    i0 = np.clip(np.floor(f).astype(np.int32), 0, len(levels) - 2)
    fr = (f - i0)[..., None]
    out = np.zeros_like(img)
    for i in range(len(levels) - 1):
        m = (i0 == i)[..., None]
        out += m * (stack[i] * (1 - fr) + stack[i + 1] * fr)
    return out


if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "setup_h1"
    ap = sys.argv[2] if len(sys.argv) > 2 else "B"
    mode = sys.argv[3] if len(sys.argv) > 3 else "night"
    st = {k: v[4] for k, v in LY.NODES.items()}
    img = finish(tag, mode, ap, st)
    os.makedirs(os.path.join(ROOT, "scratch", "test"), exist_ok=True)
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(os.path.join(ROOT, "scratch", "test", "%s_%s_%s.png" % (tag, ap, mode)))
    print("ok")
