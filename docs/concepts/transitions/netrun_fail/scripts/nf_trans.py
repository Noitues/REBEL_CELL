"""Glitch-in transition: combat plate -> failure screen in 0.6 s (hard cut at 0.20 s, 0.3 s settle, panel opens 0.30 s).
Operates on any size (inputs are resized) so the same code runs at 1920x1080 for key frames and 480x270 for the flash analysis."""
import numpy as np
from PIL import Image

def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3

def _f(im, size):
    if im.size != size:
        im = im.resize(size, Image.LANCZOS)
    return np.asarray(im.convert('RGB'), np.float32) / 255.0

def tear(a, g, rng):
    if g <= 0.001:
        return a
    h, w = a.shape[:2]
    o = a.copy()
    nb = int(3 + 15 * g)
    for _ in range(nb):
        bh = int(rng.integers(max(2, h // 180), max(3, int(h * (0.02 + 0.06 * g)))))
        y = int(rng.integers(0, h - bh))
        dx = int(rng.integers(-1, 2) * rng.uniform(0.2, 1.0) * g * w * 0.10)
        o[y:y + bh] = np.roll(a[y:y + bh], dx, axis=1)
    px = int(round(g * w * 0.008))
    if px:
        o[..., 0] = np.roll(o[..., 0], px, axis=1)
        o[..., 2] = np.roll(o[..., 2], -px, axis=1)
    o = o + rng.normal(0, 0.035 * g, o.shape[:2]).astype(np.float32)[..., None]
    sl = np.ones(h, np.float32)
    sl[::3] = 1 - 0.12 * g
    return o * sl[:, None, None]

def frame(a, bg, full, t, size=(1920, 1080), seed=11):
    A = _f(a, size); BG = _f(bg, size); FU = _f(full, size)
    rng = np.random.default_rng(seed * 1000 + int(round(t * 60)))
    if t < 0.20:
        g = (t / 0.20) ** 1.6
        L = A.mean(2, keepdims=True)
        base = (A * (1 - 0.35 * g) + L * 0.35 * g) * (1 - 0.18 * g)      # desaturate and dim a little, never brighten
        out = tear(base, g, rng)
    else:
        g = 1 - ease_out((t - 0.20) / 0.30)
        rv = ease_out((t - 0.30) / 0.20)
        base = BG * (1 - rv) + FU * rv
        out = tear(base, 0.35 + 0.65 * g if t < 0.5 else g, rng) if g > 0 else base
    return Image.fromarray((np.clip(out, 0, 1) * 255 + .5).astype(np.uint8))

def reduced(a, full, t, size=(1920, 1080)):
    k = min(max(t / 0.25, 0), 1)
    A = _f(a, size); FU = _f(full, size)
    return Image.fromarray((np.clip(A * (1 - k) + FU * k, 0, 1) * 255 + .5).astype(np.uint8))
