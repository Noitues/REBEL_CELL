"""New corps: the 'real night' finish for a linear render (npy from nc_blend.render). Identical copy in both folders.

exposure -> soft shoulder tone curve -> multi-scale bloom from the hot parts -> media layer (rain for the night city,
marine snow + bubbles for the deep) -> grade (lift / tint) -> vignette -> grain. All randomness seeded.
python nc_post.py <in.npy> <out.png> [look=night|deep] [exposure=1.0] [rain=1.0]
"""
import math
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def tone(x, white=6.0):
    x = np.maximum(x, 0)
    y = x * (1 + x / (white * white)) / (1 + x)
    return np.clip(y, 0, 1)


def blur(a, r):
    im = Image.fromarray(np.clip(a * 255 / max(1e-6, a.max()), 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255 * a.max()


def bloom(lin, thresh=0.9, k=0.22):
    hot = np.maximum(lin - thresh, 0)
    out = np.zeros_like(lin)
    h, w = lin.shape[:2]
    for r, wgt in ((h / 180, 0.5), (h / 60, 0.3), (h / 20, 0.2)):
        for c in range(3):
            out[..., c] += blur(hot[..., c], r) * wgt
    return lin + out * k


def to_srgb(x):
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(np.maximum(x, 0), 1 / 2.4) - 0.055)


def rain(img, seed=41, n=2600, k=1.0):
    w, h = img.size
    lay = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(seed)
    for _ in range(int(n * k)):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        L = rng.uniform(10, 34) * h / 1440
        a = rng.integers(18, 70)
        d.line([(x, y), (x - L * 0.12, y + L)], fill=int(a), width=1)
    lay = lay.filter(ImageFilter.GaussianBlur(0.6))
    a = np.asarray(img, np.float32)
    m = np.asarray(lay, np.float32)[..., None] / 255
    a = a + m * (np.array([200, 210, 230], np.float32) - a * 0.4) * 0.6
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def snow(img, seed=43, n=5200, k=1.0):
    """Marine snow + a few bubble rings: soft pale specks, bigger and blurrier near the lens."""
    w, h = img.size
    lay = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(seed)
    for _ in range(int(n * k)):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.choice([0.6, 0.8, 1.0, 1.4, 2.2], p=[0.35, 0.3, 0.2, 0.1, 0.05]) * h / 1440
        d.ellipse([x - r, y - r, x + r, y + r], fill=int(rng.integers(50, 150)))
    near = Image.new("L", (w, h), 0)
    dn = ImageDraw.Draw(near)
    for _ in range(int(60 * k)):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.uniform(3, 9) * h / 1440
        dn.ellipse([x - r, y - r, x + r, y + r], fill=int(rng.integers(40, 90)))
    near = near.filter(ImageFilter.GaussianBlur(3 * h / 1440))
    a = np.asarray(img, np.float32)
    m = (np.asarray(lay.filter(ImageFilter.GaussianBlur(0.5)), np.float32) + np.asarray(near, np.float32))[..., None] / 255
    a = a + m * (np.array([190, 225, 235], np.float32) - a) * 0.55
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def finish(src, dst, look="night", exposure=1.0, media=1.0, seed=7):
    lin = np.load(src).astype(np.float32)[..., :3] * exposure
    lin = bloom(lin, 0.85 if look == "night" else 0.7, 0.26 if look == "night" else 0.32)
    t = tone(lin)
    s = to_srgb(t)
    h, w = s.shape[:2]
    if look == "night":
        s = s * np.array([1.0, 0.97, 1.02]) + np.array([0.012, 0.008, 0.02])
    else:
        s = s * np.array([0.92, 1.0, 1.04]) + np.array([0.004, 0.012, 0.03])
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    v = 1 - 0.38 * (((x / w - 0.5) * 1.3) ** 2 + ((y / h - 0.5) * 1.1) ** 2) ** 1.2 * 2
    s = s * np.clip(v, 0.45, 1)[..., None]
    img = Image.fromarray(np.clip(s * 255, 0, 255).astype(np.uint8))
    if media > 0:
        img = rain(img, k=media * w * h / (2560 * 1440)) if look == "night" else snow(img, k=media * w * h / (2560 * 1440))
    rng = np.random.default_rng(seed)
    a = np.asarray(img, np.float32) + rng.normal(0, 2.4, (h, w, 1))
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    img.save(dst)
    print("post", dst, img.size)
    return img


if __name__ == "__main__":
    kw = dict(a.split("=", 1) for a in sys.argv[3:] if "=" in a)
    finish(sys.argv[1], sys.argv[2], kw.get("look", "night"), float(kw.get("exposure", 1.0)), float(kw.get("media", 1.0)))
