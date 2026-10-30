"""Post for the netrun cel frames: bloom, glow haze, rain streaks, grain, vignette, tiny chroma split.
Usage: python nr_post.py <in.png> <out.png> <profile: f2|f3|f4> [seed]"""
import sys
import numpy as np
from PIL import Image, ImageFilter

src, dst, prof = sys.argv[1], sys.argv[2], sys.argv[3]
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 3
rng = np.random.default_rng(seed)
im = Image.open(src).convert('RGB')
W, H = im.size
a = np.asarray(im).astype(np.float32) / 255.0

def blur(arr, r):
    img = Image.fromarray(np.clip(arr * 255, 0, 255).astype(np.uint8))
    return np.asarray(img.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255.0

# bright pass bloom (two radii)
lum = a.max(axis=2)
bright = a * np.clip((lum - 0.62) / 0.38, 0, 1)[..., None]
bl = blur(bright, W / 160) * 0.55 + blur(bright, W / 48) * 0.45
a = a + bl
# hue-preserving soft clip: neon colours keep their hue (lime stays lime) with a small white-hot core
mx = a.max(axis=2, keepdims=True)
a = a / np.maximum(1.0, mx * 0.95) + np.clip(mx - 1.0, 0, 1) * 0.12
# low violet haze lift in the shadows (cel night grade)
a = a * (1.0 - 0.10) + np.array([0.075, 0.03, 0.11], dtype=np.float32) * 0.5
# contrast curve (gentle s)
a = np.clip(a, 0, 1.4)
a = np.where(a < 0.5, 0.5 * (2 * a) ** 1.08, 1 - 0.5 * (2 * (1 - np.minimum(a, 1))) ** 1.08)
# rain streaks
rain = np.zeros((H, W), np.float32)
n = int(W * H / 5200) if prof != 'f2' else int(W * H / 14000)
xs = rng.integers(0, W, n); ys = rng.integers(0, H, n); ln = rng.integers(14, 46, n); al = rng.uniform(0.05, 0.16, n)
for x, y, l, c in zip(xs, ys, ln, al):
    for k in range(l):
        yy = y + k; xx = x - int(k * 0.12)
        if 0 <= yy < H and 0 <= xx < W:
            rain[yy, xx] = max(rain[yy, xx], c * (1 - k / l))
a = a + rain[..., None] * np.array([0.8, 0.7, 1.0], dtype=np.float32)
# vignette
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
a = a * (1.0 - 0.22 * np.clip(d - 0.55, 0, 1) ** 1.5)[..., None]
# chroma split (1px at edges)
sh = max(1, W // 960)
r = np.roll(a[..., 0], sh, axis=1); b = np.roll(a[..., 2], -sh, axis=1)
a[..., 0] = r * 0.5 + a[..., 0] * 0.5; a[..., 2] = b * 0.5 + a[..., 2] * 0.5
# grain
a = a + rng.normal(0, 0.012, a.shape).astype(np.float32)
out = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
out.save(dst)
print('wrote', dst)
