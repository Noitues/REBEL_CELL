"""gate1 C3: bright pixels on the enemy rings / bezel (212 <= r < 480, hand and HUD cut by colour-free geometry: x < 925 or y < 760)
above a threshold (default the tower p95 89.5), clustered; print each cluster with colour class.  usage: bright2.py <png> [thr]"""
import sys
import numpy as np
from scipy import ndimage as ndi
import glib as G
rgb = G.load(sys.argv[1])
thr = float(sys.argv[2]) if len(sys.argv) > 2 else 89.5
L = G.Lstar(rgb)
r_, th_, xx, yy = G.polar()
reg = (r_ >= 212) & (r_ < 480) & ((xx < 925) | (yy < 760))
bm = (L > thr) & reg
lb, n = ndi.label(ndi.binary_dilation(bm, iterations=2) & reg)
rows = []
for k, sl in enumerate(ndi.find_objects(lb)):
    m = (lb[sl] == k + 1) & bm[sl]
    if m.sum() == 0:
        continue
    px = rgb[sl][m]
    mr = px.mean(0)
    rr = r_[sl][m].mean()
    rows.append((int(m.sum()), int(sl[1].start), int(sl[0].start), int(sl[1].stop), int(sl[0].stop), float(L[sl][m].max()), G.hexof(mr), float(rr)))
rows.sort(key=lambda q: -q[0])
tot = sum(r[0] for r in rows)
print('total px above %.1f in 212<=r<480: %d in %d clusters' % (thr, tot, len(rows)))
for r in rows[:40]:
    print('  px %4d  x %4d-%4d y %4d-%4d  Lmax %5.1f  mean %s  r %.0f' % (r[0], r[1], r[3], r[2], r[4], r[5], r[6], r[7]))
