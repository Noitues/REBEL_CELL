"""caps.py -- cap height measured on the published pixels (not font metrics).

For each search box holding one all-caps label (no descenders), text pixels = L* above the midpoint of the box's p5 and p99.5 L*.  The ink
height is the number of rows whose text-pixel count is >= 2, refined to sub-pixel by the edge rows' coverage (the max L* in the edge row,
interpolated between the background and text level).  Boxes are hand-placed from the 1x plates; each prints its row span so a misplaced box
shows."""
import sys
import numpy as np
from PIL import Image

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'


def lstar_img(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    Y = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    return np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)


BOXES = {
    'p1_decide': {
        'RAW': (1166, 148, 1210, 178), 'SHOT': (1346, 150, 1400, 173), 'BRACE': (1464, 150, 1534, 173), 'RIDER': (1596, 150, 1666, 173),
        'LANDS (eq)': (1770, 148, 1836, 178), 'LANDS (hdr)': (1420, 81, 1488, 100), 'THROUGH': (1536, 81, 1630, 100),
        'ABSORBED': (1186, 205, 1294, 232), 'SOAK': (1348, 205, 1402, 232), 'SPLIT': (1092, 229, 1160, 256), 'NEXT': (1102, 262, 1158, 288),
        'WIN': (1136, 328, 1182, 356), 'SLICES KEPT': (1316, 308, 1462, 334), 'TRACE LOW': (1316, 350, 1436, 376), 'KILL ADJUSTER': (1592, 308, 1764, 334),
        'RAM': (1090, 404, 1132, 430), 'TRACE': (1346, 404, 1414, 430), 'ENDS': (1670, 404, 1726, 430), 'NOW W1 tag': (630, 309, 694, 333),
        'UNDO': (1710, 864, 1772, 894),
    },
    'p3_resolve': {
        'log TWIST': (1150, 305, 1218, 333), 'log TRIGGER': (1150, 335, 1244, 363), 'log BRACE': (1150, 365, 1230, 393), 'log GUNS': (1150, 395, 1204, 423),
        'log LANDS': (1150, 425, 1220, 453), 'log RINGS STEP': (1150, 455, 1284, 483), 'slot TWIST': (1166, 926, 1240, 954), 'slot PLAYED': (1158, 955, 1246, 983),
        'slot TRIGGER': (1320, 926, 1420, 954),
    },
    'p2_preview': {'TRIG': (1344, 148, 1400, 178), 'BEST LINE': (1748, 85, 1864, 103), 'TRIGGER ONLY': (1270, 306, 1432, 332), 'WITHOUT TWIST': (1628, 262, 1798, 288),
                   'REFUND': (1178, 586, 1262, 610)},
}
names = sys.argv[1:] or list(BOXES)
for nm in names:
    rgb = np.asarray(Image.open(FINAL + nm + '.png').convert('RGB')).astype(float)
    L = lstar_img(rgb)
    print('==', nm)
    for k, (x0, y0, x1, y1) in BOXES[nm].items():
        b = L[y0:y1, x0:x1]
        lo, hi = np.percentile(b, 5), np.percentile(b, 99.5)
        thr = (lo + hi) / 2
        cnt = (b > thr).sum(1)
        rows = np.nonzero(cnt >= 2)[0]
        if rows.size == 0:
            print('  %-14s no ink' % k)
            continue
        r0, r1 = rows.min(), rows.max()
        h = r1 - r0 + 1
        # sub-pixel: coverage of the row just outside each end
        def cov(r):
            if r < 0 or r >= b.shape[0]:
                return 0.0
            return float(np.clip((b[r].max() - lo) / max(hi - lo, 1), 0, 1))
        hs = (h - 1) + 0.5 + 0.5 + cov(r0 - 1) * 0.5 + cov(r1 + 1) * 0.5 - 0.5 * (1 - cov(r0)) - 0.5 * (1 - cov(r1))
        print('  %-14s rows y %d-%d  ink height %d px (sub-px %.1f)  text L* p99.5 %.1f  bg %.1f' % (k, y0 + r0, y0 + r1, h, hs, hi, lo))
