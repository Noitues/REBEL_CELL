"""Independent occupied-vs-empty cell read on the published plates (final reviewer).
Geometry: centre (536,540); ring NOW r 218-267, +1 275-324, +2 332-381; sector s centred on 60*s deg clockwise from up.
Each cell is inset 6 px radially and 4 deg angularly; the token disc (r 34 around the cell centroid of lit pixels is not
known, so) is excluded by dropping pixels with Lab C* > 28 or L* > 60 or L* < 6 (marks, discs, ink keylines).
Glass value = L* of the MEDIAN luminance of the remaining pixels (robust to leftover marks).
Occupancy comes from final/checks.json rb_checks a rows (ring, sector, state) only.
Reports, per plate: occupied glass per ring, brightest EMPTY cell on the plate per ring, min live ratio (luminance)."""
import json, sys
import numpy as np
from PIL import Image

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
C = (536, 540)
RINGS = [(218, 267), (275, 324), (332, 381)]

def lin(rgb):
    c = rgb / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

def lab(rgb):
    c = lin(rgb)
    X = (0.4124 * c[..., 0] + 0.3576 * c[..., 1] + 0.1805 * c[..., 2]) / 0.95047
    Y = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    Z = (0.0193 * c[..., 0] + 0.1192 * c[..., 1] + 0.9505 * c[..., 2]) / 1.08883
    f = lambda t: np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
    L = 116 * f(Y) - 16
    return L, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z)), Y

def Ls(y):
    return float(116 * np.cbrt(y) - 16 if y > 0.008856 else 903.3 * y)

yy, xx = np.mgrid[0:1080, 0:1920]
RHO = np.hypot(xx - C[0], yy - C[1])
ANG = (np.degrees(np.arctan2(xx - C[0], -(yy - C[1]))) + 360) % 360

def cell(dep, s):
    r0, r1 = RINGS[dep]
    a = (ANG - 60 * s + 180) % 360 - 180
    return (RHO >= r0 + 6) & (RHO <= r1 - 6) & (np.abs(a) <= 26)

def main():
    chk = json.load(open(FINAL + 'checks.json', encoding='utf-8'))['rb_checks']
    plates = sys.argv[1:] or list(chk.keys())
    for p in plates:
        rows = chk[p]['a_cell_contrast']['rows']
        occ = {(r['ring'], r['sector']): r['state'] for r in rows}
        rgb = np.asarray(Image.open(FINAL + p + '.png').convert('RGB')).astype(float)
        L, a, b, Y = lab(rgb)
        Cst = np.hypot(a, b)
        glass_ok = (Cst <= 28) & (L <= 60) & (L >= 6)
        res = {}
        for dep in range(3):
            for s in range(6):
                m = cell(dep, s) & glass_ok
                st = occ.get((dep, s), 'empty')
                res[(dep, s)] = (st, float(np.median(Y[m])) if m.sum() > 50 else None, int(m.sum()))
        out = []
        for dep in range(3):
            empt = [v[1] for k, v in res.items() if k[0] == dep and v[0] == 'empty' and v[1]]
            live = [(k[1], v[0], v[1]) for k, v in res.items() if k[0] == dep and v[0] in ('live', 'dying') and v[1]]
            ref = max(empt) if empt else None
            occL = [round(Ls(v), 1) for _, _, v in live]
            ratio = round(min(v for _, _, v in live) / ref, 2) if (ref and live) else None
            out.append(f'ring{dep}: occ L* {occL} | brightest empty L* {round(Ls(ref),1) if ref else "none on plate"} | min ratio {ratio}')
        print(p, ' ; '.join(out))

if __name__ == '__main__':
    main()
