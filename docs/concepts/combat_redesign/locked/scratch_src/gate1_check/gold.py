import sys, numpy as np
from lab import *
def lab_px(im, m): return lab(im[m])
for p in sys.argv[1:]:
    im = load(p)
    Lb = lab(im)
    turret_ink = lab(hex2rgb('D6A33A')); gold = lab(hex2rgb('D69A1A'))
    # TURRET slice region (sector 2 of the tower)
    zt = polar_mask(78, 182, 96, 144)
    dt = np.linalg.norm(Lb[zt] - turret_ink, axis=1)
    tp = Lb[zt][dt < 12]
    # Adjuster cell (ring 1 sector 2), gold pixels
    za = polar_mask(271, 328, 92, 148)
    dg = np.linalg.norm(Lb[za] - gold, axis=1)
    gp = Lb[za][dg < 12]
    tm = np.median(tp, axis=0) if len(tp) else None; gm = np.median(gp, axis=0) if len(gp) else None
    print(p, 'turret ink px', len(tp), 'median Lab', None if tm is None else np.round(tm, 1), '| adjuster gold px', len(gp), 'median Lab', None if gm is None else np.round(gm, 1), '| dE76 rendered', None if (tm is None or gm is None) else round(float(np.linalg.norm(tm - gm)), 1))
    # the gap between them: nearest pixel distance tower turret ink to adjuster gold
