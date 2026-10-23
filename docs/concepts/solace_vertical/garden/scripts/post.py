"""Post for the renders (numpy + PIL): cel map = glow/spill + far haze + vignette; night = a touch of bloom + vignette.
python post.py map|night in.png out.png"""
import sys
import numpy as np
from PIL import Image, ImageFilter

mode, src, dst = sys.argv[1:4]
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32) / 255.0
H, W = a.shape[:2]


def blur(x, r):
    img = Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8))
    return np.asarray(img.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255.0


lum = a.max(axis=2)
sat = a.max(axis=2) - a.min(axis=2)
if mode == "map":
    # light spill: the saturated bright pixels (windows, neon) bleed a soft glow
    m = np.clip((lum - 0.72) * 4.0, 0, 1)[..., None] * np.clip(sat * 2.5, 0, 1)[..., None]
    g = blur(a * m, W / 240.0) * 1.25 + blur(a * m, W / 70.0) * 1.0
    out = 1 - (1 - a) * (1 - np.clip(g, 0, 1) * 0.8)
    # haze: toward the top of the frame (the far side of the oblique ortho view) a cool violet-teal veil
    y = np.linspace(1, 0, H)[:, None, None]
    hz = np.array([0.20, 0.13, 0.36], dtype=np.float32)[None, None, :]
    k = (np.clip(1.0 - y * 1.0, 0, 1) ** 2.0) * 0.38
    out = out * (1 - k) + hz * k
elif mode == "mapraid":
    m = np.clip((lum - 0.72) * 4.0, 0, 1)[..., None] * np.clip(sat * 2.5, 0, 1)[..., None]
    g = blur(a * m, W / 240.0) * 0.9 + blur(a * m, W / 70.0) * 0.55
    out = 1 - (1 - a) * (1 - np.clip(g, 0, 1) * 0.7)
    y = np.linspace(1, 0, H)[:, None, None]
    hz = np.array([0.16, 0.11, 0.32], dtype=np.float32)[None, None, :]
    k = (np.clip(1.0 - y * 1.0, 0, 1) ** 2.0) * 0.18
    out = out * (1 - k) + hz * k
elif mode == "dayhaze":
    y = np.linspace(1, 0, H)[:, None, None]
    hz = np.array([0.74, 0.80, 0.92], dtype=np.float32)[None, None, :]
    k = (np.clip(1.0 - y * 1.0, 0, 1) ** 1.6) * float(sys.argv[4] if len(sys.argv) > 4 else 0.22)
    out = a * (1 - k) + hz * k
elif mode == "mapday":
    y = np.linspace(1, 0, H)[:, None, None]
    hz = np.array([0.70, 0.80, 0.95], dtype=np.float32)[None, None, :]
    k = (np.clip(1.0 - y * 1.0, 0, 1) ** 2.0) * 0.30
    out = a * (1 - k) + hz * k
else:
    m = np.clip((lum - 0.65) * 3.0, 0, 1)[..., None]
    bk = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    g = (blur(a * m, W / 200.0) * 0.8 + blur(a * m, W / 55.0) * 0.5) * bk
    out = 1 - (1 - a) * (1 - np.clip(g, 0, 1) * 0.6)
yy, xx = np.mgrid[0:H, 0:W]
d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
v = 1.0 - 0.28 * np.clip(d - 0.55, 0, 1) ** 1.5
out = out * v[..., None]
Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).save(dst)
