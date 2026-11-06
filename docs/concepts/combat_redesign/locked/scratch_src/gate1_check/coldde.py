import sys, numpy as np
from lab import *
cold = lab(hex2rgb('D9877C')); far = lab(hex2rgb('96767A')); hot = lab(hex2rgb('FF6452'))
for p in sys.argv[1:]:
    im = load(p); Lb = lab(im); L = Lb[..., 0]
    ch = np.hypot(Lb[..., 1], Lb[..., 2])
    out = []
    for nm, ring, (r0, r1), sct, ref in [('COLD r1 s0', 1, (276, 306), 0, cold), ('COLD r1 s3', 1, (276, 306), 3, cold), ('FAR r2 s5', 2, (333, 362), 5, far), ('HOT r0 s1', 0, (221, 250), 1, hot)]:
        z = polar_mask(r0, r1, 60 * sct - 7, 60 * sct + 7)
        mk = z & (np.linalg.norm(Lb - ref, axis=-1) < 14)
        cellz = polar_mask(r0, r1 + 15, 60 * sct + 10, 60 * sct + 25) & (ch < 12) & (L > 20) & (L < 55)
        if mk.sum() < 10 or cellz.sum() < 10: out.append('%s n/a' % nm); continue
        m = np.median(Lb[mk], axis=0); c = np.median(Lb[cellz], axis=0)
        Ym = Yof(m[0]); Yc = Yof(c[0])
        out.append('%s mark L* %.1f vs cell L* %.1f (C* %.1f) dE76 %.1f lum ratio %.2f' % (nm, m[0], c[0], np.hypot(c[1], c[2]), np.linalg.norm(m - c), Ym / Yc))
    print(p); [print('   ' + o) for o in out]
    # cell glass chroma (skin tint) on occupied + empty cells
    for nm, (r0, r1, a0, a1) in {'r1 s5 empty': (277, 322, 273, 327), 'r2 s0 empty': (334, 379, 333, 27), 'r0 s1 occ': (220, 265, 50, 87), 'r2 s3 occ': (334, 379, 153, 207)}.items():
        z = polar_mask(r0, r1, a0, a1) & (L > 6) & (L < 62)
        c = np.median(Lb[z], axis=0)
        print('   glass %-12s L* %.1f a %.1f b %.1f C* %.1f' % (nm, c[0], c[1], c[2], np.hypot(c[1], c[2])))
