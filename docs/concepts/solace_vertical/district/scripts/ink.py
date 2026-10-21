"""Ink lines for the cel map, from the id/facing/depth pass (mode ink): edge detect, thicken, wobble, composite.
python ink.py <map_raw.png> <ink_pass.png> <out.png> [thickness_px_at_1920]"""
import sys
import numpy as np
from PIL import Image, ImageFilter

raw, ink, dst = sys.argv[1:4]
thick = float(sys.argv[4]) if len(sys.argv) > 4 else 3.0
im = np.asarray(Image.open(raw).convert("RGB")).astype(np.float32) / 255.0
H, W = im.shape[:2]
p = np.asarray(Image.open(ink)).astype(np.float32)
p = p / (65535.0 if p.max() > 255 else 255.0)
p = p[..., :3]
R, G, B = p[..., 0], p[..., 1], p[..., 2]


def grad(c):
    gx = np.abs(np.diff(c, axis=1, prepend=c[:, :1]))
    gy = np.abs(np.diff(c, axis=0, prepend=c[:1, :]))
    return np.maximum(gx, gy)


# building / object id changes, big facing changes (creases), and depth jumps (silhouettes against what is behind)
e = (grad(R) > 0.03) | (grad(G) > 0.3) | (grad(B) > 0.012)
m = Image.fromarray((e * 255).astype(np.uint8))
k = max(1, int(round(thick * W / 1920.0)))
for _ in range(k // 2 + 0):
    m = m.filter(ImageFilter.MaxFilter(3))
m = np.asarray(m).astype(np.float32) / 255.0
# wobble: displace the line mask by two low-frequency sine fields (hand-inked wobble)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
s = W / 1920.0
dx = 1.7 * s * np.sin(yy / (23.0 * s) + 0.011 * xx) + 0.9 * s * np.sin(xx / (9.0 * s) + yy / (31.0 * s))
dy = 1.7 * s * np.sin(xx / (27.0 * s) + 0.013 * yy) + 0.9 * s * np.sin(yy / (11.0 * s) + xx / (29.0 * s))
xi = np.clip((xx + dx).astype(np.int32), 0, W - 1)
yi = np.clip((yy + dy).astype(np.int32), 0, H - 1)
m = m[yi, xi]
m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6 * s))).astype(np.float32) / 255.0
m = np.clip(m * 1.4, 0, 1)[..., None] * 0.93
ink_col = np.array([0.025, 0.012, 0.07], dtype=np.float32)
out = im * (1 - m) + ink_col * m
Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).save(dst)
print("ink ok", int((m > 0.5).sum()))
