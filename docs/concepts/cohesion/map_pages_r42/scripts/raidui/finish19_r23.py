"""Round 19 post: the round 18 finish (ink, grime, bloom + spill, fog patches, tilt-shift, haze, rain) driven by a
`decorate(net)` callback that draws the street-plane grid state (netdecal19). Works for any district.py
render: full frames, close-up cameras and animation frames (prefix 'fNN_').
Day: no fog patches at this zoom (designer, round 19).
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
import finish as F0  # noqa: E402  (helpers: blur, blur_down, noise, diff_edges, warp, maxf, MODE)
import netdecal19 as ND  # noqa: E402

ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "scratch", "bl")
MODE = F0.MODE
CAM_DEFAULT = dict(LY.CAM)


def load(path):
    im = Image.open(path)
    a = np.asarray(im)
    if a.dtype == np.uint16 or im.mode.startswith("I"):
        return a.astype(np.float32) / 65535.0
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


class Passes:
    def __init__(self, tag, prefix=""):
        base = os.path.join(SRC, tag + "_" + prefix)
        self.base = base
        self.scene = json.load(open(os.path.join(SRC, tag + "_scene.json")))
        self.cam = self.scene.get("cam", CAM_DEFAULT)
        self.pos = np.load(base + "pos.npy").astype(np.float32)
        self.nrm = load(base + "normal.png")
        self.ids = load(base + "id.png")
        with_cam(self.cam)
        r, u, f = LY.cam_basis()
        t = LY.CAM["target"]
        self.dep = ((self.pos[..., 0] - t[0]) * f[0] + (self.pos[..., 1] - t[1]) * f[1] + (self.pos[..., 2] - t[2]) * f[2])
        self.h, self.w = self.dep.shape

    def beauty(self, mode):
        return load(self.base + "beauty_%s.png" % mode), load(self.base + "glow_%s.png" % mode)


def with_cam(cam):
    LY.CAM.update({k: (tuple(v) if isinstance(v, list) else v) for k, v in cam.items()})


_cache = {}


def passes(tag, prefix=""):
    k = (tag, prefix)
    if k not in _cache:
        if len(_cache) > 6:
            _cache.clear()
        _cache[k] = Passes(tag, prefix)
    P = _cache[k]
    with_cam(P.cam)
    return P


def finish(tag, mode="night", decorate=None, prefix="", frame=0, heat=1, fog=None, tilt=1.0, seed=1, creep=None,
           pools=None, link="lime", out_size=None, rain=True, focus=-12.0, box=None, net_cls=None):
    """Returns the finished float RGB image (1920 x 1080 for full renders)."""
    M = MODE[mode]
    P = passes(tag, prefix)
    sc = P.w / LY.RW
    fog = (1.0 if mode == "night" else 0.0) if fog is None else fog
    beauty, glow = P.beauty(mode)
    pos, nrm, ids, dep = P.pos, P.nrm, P.ids, P.dep
    if box is not None:   # round 20: finish only a crop (box in 1920 x 1080 frame px); fog off
        k = P.w / LY.W
        bx0, by0, bx1, by1 = (int(round(v * k)) for v in box)
        sl = (slice(by0, by1), slice(bx0, bx1))
        pos, nrm, ids, dep, beauty, glow = pos[sl], nrm[sl], ids[sl], dep[sl], beauty[sl], glow[sl]
        fog = 0.0
        out_size = out_size or (box[2] - box[0], box[3] - box[1])
    X, Y, Z = pos[..., 0], pos[..., 1], pos[..., 2]
    net = (net_cls or ND.Net)(pos, mode=mode, link=link)
    if decorate:
        decorate(net)
    em, dk = net.result()
    beauty = beauty * dk[..., None]
    glow = glow * dk[..., None] + em * 0.6
    # ink
    e_id = F0.diff_edges(ids, 0.03)
    e_n = F0.diff_edges(nrm, 0.42)
    dd = np.abs(dep - np.roll(dep, -1, 1)) + np.abs(dep - np.roll(dep, -1, 0))
    e_d = (dd > 1.6 * (LY.CAM["ortho"] / 440.0) / max(sc, 0.34)).astype(np.float32)
    ink = F0.warp(np.maximum(np.maximum(e_id, e_n), e_d), 7, amp=1.6 * max(sc, 0.5))
    thick = F0.maxf(ink, 3) if sc > 0.5 else ink
    ink_a = F0.blur(thick, 0.7) * 0.9
    h, w = dep.shape
    blot = F0.noise(h, w, max(8, int(90 * sc)), 31) * 0.6 + F0.noise(h, w, max(4, int(22 * sc)), 32) * 0.4
    g = 1 - M["grime"] * (blot - 0.5) * 1.4
    emis = np.clip(glow.max(axis=2) * 2, 0, 1) if mode == "night" else np.clip((glow.max(axis=2) - 0.16) * 2.6, 0, 1)
    img = beauty * (g[..., None] * (1 - emis[..., None]) + emis[..., None])
    img = img + em * (0.72 if mode == "night" else 0.6)
    ink_a = ink_a * (1 - np.clip(emis * 1.6 - 0.4, 0, 1))
    img = img * (1 - ink_a[..., None]) + np.array(M["ink"], np.float32) * ink_a[..., None]
    # heat light pools (choppers / drones) on whatever they hit
    frames = P.scene.get("frames") or [P.scene.get("pools", [])]
    pl = pools if pools is not None else frames[min(frame, len(frames) - 1)]
    for p in pl:
        tx, ty, rr, k = p[:4]
        d = np.hypot(X - tx, Y - ty)
        L = np.exp(-(d / rr) ** 2 * 1.6) * (Z < 40) * k
        jag = 0.85 + 0.15 * F0.noise(h, w, max(4, int(40 * sc)), int(tx * 7 + ty) % 9999)
        L = L * jag
        img = img * (1 + 1.5 * L[..., None]) + L[..., None] * np.array([0.32, 0.33, 0.36], np.float32)
        glow = glow + L[..., None] * np.array([0.25, 0.26, 0.3], np.float32)
    if creep:
        cm = np.zeros((h, w), np.float32)
        for e in LY.ENTRIES.values():
            cm = np.maximum(cm, np.exp(-(np.hypot(X - e[0], Y - e[1]) / creep[0]) ** 2))
        cm *= ((Z < 0.42) & (Z > -0.5)) * creep[1]
        img = img * (1 - cm[..., None] * 0.5) + cm[..., None] * np.array([0.55, 0.42, 1.0], np.float32) * 0.22
    b1 = F0.blur_down(glow, 8 * sc, 2)
    b2 = F0.blur_down(glow, 30 * sc, 4 if sc > 0.5 else 2)
    b3 = F0.blur_down(glow, 90 * sc, 8 if sc > 0.5 else 4)
    img = img * (1 + M["spill"] * (b2 * 0.8 + b3 * 1.0)) + M["bloom"] * (b1 * 0.5 + b2 * 0.4 + b3 * 0.12)
    if fog > 0:
        img = fog_patches(img, P, M, b3, seed, fog, sc)
    if tilt > 0:
        img = tilt_shift(img, dep, tilt, sc, focus)
    far = np.clip((dep - 60) / 240, 0, 1) ** 1.1
    img = img * (1 - far[..., None] * M["haze_k"]) + np.array(M["haze"], np.float32) * far[..., None] * M["haze_k"]
    if rain and M["rain_a"] > 0:
        rng = np.random.default_rng(41 + seed + frame)
        rl = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(rl)
        for _ in range(int(2200 * sc * sc) + 200):
            x, y = rng.uniform(-100, w), rng.uniform(-100, h)
            Ln = rng.uniform(30, 80) * sc
            d.line([(x, y), (x + Ln * 0.2, y + Ln)], fill=int(rng.uniform(80, 255)), width=1)
        r = np.asarray(rl.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255 * M["rain_a"]
        img = img * (1 - r[..., None]) + np.array(M["rain"], np.float32) * r[..., None]
    img = img * np.array(M["grade"], np.float32)
    if mode == "day":
        lum = img.mean(axis=2, keepdims=True)
        img = (lum + (img - lum) * 1.32 - 0.5) * 1.1 + 0.5
    if out_size is None:
        out_size = (LY.W, LY.H) if w == LY.RW else (w, h)
    out = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))
    if out.size != tuple(out_size):
        out = out.resize(out_size, Image.LANCZOS)
    LY.CAM.update(CAM_DEFAULT)
    return np.asarray(out, np.float32) / 255.0


def fog_patches(img, P, M, glowb, seed, k, sc):
    h, w = P.h, P.w
    rng = np.random.default_rng(500 + seed)
    acc = np.zeros((h, w), np.float32)
    nodes = [LY.project(n[0], n[1], 0, w, h) for n in LY.NODES.values()]
    placed = tries = 0
    while placed < 34 and tries < 400:
        tries += 1
        x, y, zz = rng.uniform(-300, 330), rng.uniform(-300, 320), rng.uniform(0, 14)
        px, py, pd = LY.project(x, y, zz, w, h)
        if not (-200 * sc < px < w + 200 * sc and -200 * sc < py < h + 200 * sc):
            continue
        near = min(math.hypot(px - q[0], py - q[1]) for q in nodes)
        a_max = rng.uniform(0.12, 0.4) * (0.35 if near < 160 * sc else 1.0)
        rw, rh = rng.uniform(140, 520) * sc, rng.uniform(50, 170) * sc
        sig = float(rng.choice([2, 4, 8, 14, 24, 40])) * sc
        x0, y0 = int(max(0, px - rw - 3 * sig)), int(max(0, py - rh - 3 * sig))
        x1, y1 = int(min(w, px + rw + 3 * sig)), int(min(h, py + rh + 3 * sig))
        if x1 - x0 < 8 or y1 - y0 < 8:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        ang = rng.uniform(-0.5, 0.5)
        u = ((xx - px) * math.cos(ang) + (yy - py) * math.sin(ang)) / rw
        v = (-(xx - px) * math.sin(ang) + (yy - py) * math.cos(ang)) / rh
        n = F0.noise(y1 - y0, x1 - x0, max(4, int(rng.integers(18, 60) * sc)), int(rng.integers(0, 10000)))
        m = np.clip((np.clip(1.15 - (u * u + v * v) - (n - 0.5) * 1.3, 0, 1) - 0.25) * 1.8, 0, 1)
        m = F0.blur(m, sig)
        nearer = P.dep[y0:y1, x0:x1] < pd - 6.0
        m = m * (1 - nearer) * a_max
        acc[y0:y1, x0:x1] = 1 - (1 - acc[y0:y1, x0:x1]) * (1 - m)
        placed += 1
    fogc = np.array(M["fog"], np.float32) + glowb * 1.2
    acc *= k
    return img * (1 - acc[..., None]) + fogc * acc[..., None]


def tilt_shift(img, dep, k, sc, focus):
    band_, ramp = 60.0, 150.0
    t = np.clip((np.abs(dep - focus) - band_) / ramp, 0, 1) * k
    levels = [0.0, 2.0 * sc, 4.5 * sc, 8.0 * sc, 13.0 * sc]
    stack = [img] + [F0.blur(img, s) for s in levels[1:]]
    f = t * (len(levels) - 1)
    i0 = np.clip(np.floor(f).astype(np.int32), 0, len(levels) - 2)
    fr = (f - i0)[..., None]
    out = np.zeros_like(img)
    for i in range(len(levels) - 1):
        m = (i0 == i)[..., None]
        out += m * (stack[i] * (1 - fr) + stack[i + 1] * fr)
    return out


def save(img, path):
    Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(path)


if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "setup_h1"
    mode = sys.argv[2] if len(sys.argv) > 2 else "night"
    img = finish(tag, mode, decorate=lambda n: ND.setup_state(n))
    os.makedirs(os.path.join(ROOT, "scratch", "test"), exist_ok=True)
    save(img, os.path.join(ROOT, "scratch", "test", "%s_%s.png" % (tag, mode)))
    print("ok")
