"""W6 ticket: count SCHEDULE-orange hazard-tick px that touch light width-pip px (L* > 70) in the W6 strip
x 28-80, y 78-92, on every final plate (and the 090ad870 plate for reference)."""
import glob, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
BEFORE = 'D:/rc_scratch/combat_redesign/locked/final_review/before/final_p1_decide.png'

def read(p):
    rgb = np.asarray(Image.open(p).convert('RGB')).astype(float)[78:92, 28:80]
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    Y = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    L = np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    orange = (R > 200) & (G > 90) & (G < 190) & (B < 90)
    pip = (L > 70) & ~orange & (np.abs(R - B) < 40)
    touch = ndi.binary_dilation(orange, iterations=1) & pip
    return int(orange.sum()), int(pip.sum()), int(touch.sum())

for p in [BEFORE] + sorted(glob.glob(FINAL + 'p*.png')):
    o, pp, t = read(p)
    print(f'{os.path.basename(p):28s} orange {o:3d}  pip {pp:3d}  pip px touching orange {t:3d}')
