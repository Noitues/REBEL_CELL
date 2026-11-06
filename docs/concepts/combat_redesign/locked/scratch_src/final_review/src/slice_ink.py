"""Slice ink value on the tower (p1 neutral and skins): per sector (6 wedges, 60 deg each, sector s centred on 60*s deg clockwise
from up), pixels at r 75-185 from (536,540) whose hue is within dE76 18 of the published slice ink hex; reports L* of the mean
luminance and the median L* (the ink, not the texture, the paper sliver or the icon disc)."""
import sys
import numpy as np
from PIL import Image

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
INKS = {'BURST': '#F06EAE', 'SHIELD': '#5E9BE0', 'TURRET': '#AEB24E', 'REPAIR': '#3FB59A'}

def lab(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    X = (0.4124 * c[..., 0] + 0.3576 * c[..., 1] + 0.1805 * c[..., 2]) / 0.95047
    Y = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    Z = (0.0193 * c[..., 0] + 0.1192 * c[..., 1] + 0.9505 * c[..., 2]) / 1.08883
    f = lambda t: np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
    return np.stack([116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))], -1), Y

def hexrgb(h):
    return np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)]], float)

def main():
    for name in sys.argv[1:]:
        rgb = np.asarray(Image.open(FINAL + name + '.png').convert('RGB')).astype(float)
        L, Y = lab(rgb)
        yy, xx = np.mgrid[0:1080, 0:1920]
        r = np.hypot(xx - 536, yy - 540)
        band = (r >= 75) & (r <= 185)
        print('==', name)
        for k, h in INKS.items():
            ref = lab(hexrgb(h))[0][0]
            m = band & (np.linalg.norm(L - ref, axis=-1) < 18)
            if m.sum() < 50:
                print(f'   {k:7s} {h} too few px ({int(m.sum())})')
                continue
            ym = Y[m].mean()
            print(f'   {k:7s} {h}  px {int(m.sum()):6d}  L* of mean {116*np.cbrt(ym)-16:5.1f}  median L* {np.median(L[m][:,0]):5.1f}  (token L* {ref[0]:.1f})')

if __name__ == '__main__':
    main()
