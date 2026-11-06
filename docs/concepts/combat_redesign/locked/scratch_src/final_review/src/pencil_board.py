"""Board pencil (PLAN yellow) stroke width on the published board plates, plus FOCUS bracket colour.
PLAN-yellow px on the board half (x < 1060, r < 500 from (536,540)): R > 200, G > 170, B < 110, R >= G - 10.
Width = 2 x distance-transform value at local maxima (ridge) of each stroke, median over the ridge.
Ink edge = median L* of the ring 1-3 px outside the stroke.  FOCUS = px within dE76 12 of #D4FF00 vs of #96FF46."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'

def lab(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    X = (0.4124 * c[..., 0] + 0.3576 * c[..., 1] + 0.1805 * c[..., 2]) / 0.95047
    Y = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    Z = (0.0193 * c[..., 0] + 0.1192 * c[..., 1] + 0.9505 * c[..., 2]) / 1.08883
    f = lambda t: np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
    return np.stack([116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))], -1)

def hexlab(h):
    return lab(np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)]], float))[0]

def main():
    for name in sys.argv[1:]:
        rgb = np.asarray(Image.open(FINAL + name + '.png').convert('RGB')).astype(float)
        R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        yy, xx = np.mgrid[0:1080, 0:1920]
        board = (np.hypot(xx - 536, yy - 540) < 500) & (xx < 1060)
        m = (R > 200) & (G > 170) & (B < 110) & (R >= G - 10) & board
        print("    yellow px", int(m.sum()))
        L = lab(rgb)
        lab_img = ndi.label(m)[0]
        dt = ndi.distance_transform_edt(m)
        ridge = (dt == ndi.maximum_filter(dt, size=3)) & (dt >= 1)
        out = []
        for i, sl in enumerate(ndi.find_objects(lab_img), 1):
            comp = lab_img[sl] == i
            n = int(comp.sum())
            if n < 60:
                continue
            w = 2 * np.median(dt[sl][comp & ridge[sl]]) if (comp & ridge[sl]).any() else 0
            ring = ndi.binary_dilation(comp, iterations=3) & ~comp
            edgeL = float(np.median(L[sl][..., 0][ring])) if ring.any() else -1
            grain = float(np.std(L[sl][..., 0][ndi.binary_erosion(comp)])) if ndi.binary_erosion(comp).any() else 0
            out.append((n, round(float(w), 1), round(edgeL, 1), round(grain, 1), (sl[1].start, sl[0].start, sl[1].stop, sl[0].stop)))
        out.sort(reverse=True)
        print('==', name, 'PLAN-yellow strokes (px, ridge width px, ink-edge L* median 1-3 px out, wax L* std, bbox):')
        for o in out[:8]:
            print('   ', o)
        dF = np.linalg.norm(L - hexlab('#D4FF00'), axis=-1) < 12
        dS = np.linalg.norm(L - hexlab('#96FF46'), axis=-1) < 12
        print('    px near FOCUS #D4FF00:', int((dF & board).sum()), ' px near Solace leaf #96FF46 (board, r<500):', int((dS & board & (np.hypot(xx - 536, yy - 540) < 440)).sum()))

if __name__ == '__main__':
    main()
