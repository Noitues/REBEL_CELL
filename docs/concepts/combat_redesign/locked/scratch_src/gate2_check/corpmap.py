"""corpmap.py <plate> <corp> <out.png> -- paint pixels within dE76 18 of the corp inks magenta over a 35 % grey copy of the plate (board half)."""
import sys
import numpy as np
from PIL import Image

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
hx = lambda s: np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], float)
SKIN = {'solace': [hx('96FF46'), hx('4FA83A'), hx('B8DCCC')], 'meridian': [hx('B0602C'), hx('D88A4E')]}


def to_lab(rgb):
    c = np.asarray(rgb, float) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    X = (0.4124 * c[..., 0] + 0.3576 * c[..., 1] + 0.1805 * c[..., 2]) / 0.95047
    Y = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    Z = (0.0193 * c[..., 0] + 0.1192 * c[..., 1] + 0.9505 * c[..., 2]) / 1.08883
    f = lambda t: np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
    return np.stack([116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))], -1)


plate, corp, out = sys.argv[1], sys.argv[2], sys.argv[3]
rgb = np.asarray(Image.open(FINAL + plate + '.png').convert('RGB')).astype(float)
lab = to_lab(rgb)
near = np.zeros(rgb.shape[:2], bool)
for v in SKIN[corp]:
    near |= np.linalg.norm(lab - to_lab(v), axis=-1) < 18
g = rgb.mean(2, keepdims=True) * 0.35
o = np.repeat(g, 3, 2)
o[near] = (255, 0, 255)
Image.fromarray(o[:, :1060].astype(np.uint8)).save(out)
print(out, int(near[:, :1060].sum()))
