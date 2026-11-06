"""keyline probe: per row y0..y1, the columns x 1072-1081 that pass the rb_checks_r2.check_hud_rows lit test (L* > 55, C* > 25), for two PNGs.
python keyline_probe.py <png_a> <png_b> y0 y1"""
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import rb_tokens as T

a, b, y0, y1 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
for p in (a, b):
    rgb = np.asarray(Image.open(p).convert('RGB')).astype(np.float64)
    lab = T.lab(rgb[:, 1066:1086])
    lit = (lab[..., 0] > 55) & (np.hypot(lab[..., 1], lab[..., 2]) > 25)
    print(p)
    for y in range(y0, y1 + 1):
        row = ''.join('#' if v else '.' for v in lit[y])
        cols = ' '.join('%02X%02X%02X' % tuple(int(c) for c in rgb[y, x]) for x in range(1070, 1078))
        print('%4d %s  |%s|  %s' % (y, row[:6] + '|' + row[6:16] + '|' + row[16:], 'any' if lit[y, 6:16].any() else '   ', cols))
