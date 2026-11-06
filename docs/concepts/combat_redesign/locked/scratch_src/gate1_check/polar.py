# polar unwrap of the board: x = angle (0 at 12 o'clock, clockwise), y = radius (outward down)
import sys, numpy as np
from PIL import Image, ImageDraw
F = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
plate, out = sys.argv[1], sys.argv[2]
r0, r1 = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (196, 505)
im = np.asarray(Image.open(F + plate + '.png').convert('RGB')).astype(np.float32)
C = (536, 540)
W = 1440; H = int((r1 - r0) * 2)
th = np.radians(np.arange(W) * 360.0 / W)
rr = r0 + np.arange(H) / 2.0
T, R = np.meshgrid(th, rr)
X = C[0] + R * np.sin(T); Y = C[1] - R * np.cos(T)
x0 = np.floor(X).astype(int); y0 = np.floor(Y).astype(int); fx = X - x0; fy = Y - y0
def g(yy, xx): return im[np.clip(yy, 0, 1079), np.clip(xx, 0, 1919)]
o = (g(y0, x0) * ((1 - fx) * (1 - fy))[..., None] + g(y0, x0 + 1) * (fx * (1 - fy))[..., None] + g(y0 + 1, x0) * ((1 - fx) * fy)[..., None] + g(y0 + 1, x0 + 1) * (fx * fy)[..., None])
P = Image.fromarray(np.clip(o, 0, 255).astype(np.uint8))
d = ImageDraw.Draw(P)
for k in range(6):
    xa = int(((k * 60 - 30) % 360) * W / 360)
    d.line((xa, 0, xa, 6), fill=(255, 255, 0)); d.line((xa, H - 6, xa, H), fill=(255, 255, 0))
    d.text((int(k * 60 * W / 360) + 2, 0), 's%d' % k, fill=(255, 255, 0))
for rb in (214, 271, 328, 385, 417, 489, 500):
    yy = int((rb - r0) * 2)
    if 0 <= yy < H:
        d.line((0, yy, 8, yy), fill=(0, 255, 255)); d.text((10, yy - 5), str(rb), fill=(0, 255, 255))
P.save(out); print(out, P.size)
