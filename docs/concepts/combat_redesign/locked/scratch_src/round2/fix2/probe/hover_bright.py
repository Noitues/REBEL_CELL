"""bright clusters (L* >= thr) of the Z__hover class (minus FOCUS / pencil) on a hover plate: box, px, max L*, median colour"""
import sys, os
import numpy as np
from scipy import ndimage as ndi
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/round2/gate1')
import glib as G
H, W = 1080, 1920
thr = float(sys.argv[1])
def m(z, k):
    return np.unpackbits(z[k])[:H * W].reshape(H, W).astype(bool) if k in z.files else np.zeros((H, W), bool)
for f in sys.argv[2:]:
    nm = os.path.basename(f)[:-4]
    z = np.load('D:/rc_scratch/combat_redesign/locked/round2/hover/chk/%s.npz' % nm)
    rgb = G.load(f)
    L = G.Lstar(rgb)
    hv = m(z, 'Z__hover')
    pen = m(z, 'P__L6_all') | m(z, 'P__L5_all') | m(z, 'P__L5c_all') | m(z, 'P__L5h_all')
    foc = m(z, 'F__m')
    cut = ndi.binary_dilation(pen | foc, iterations=1)
    k = hv & ~cut & (L >= thr)
    lab, n = ndi.label(k)
    print(nm, 'clusters', n, 'px', int(k.sum()))
    if n:
        objs = ndi.find_objects(lab)
        sz = ndi.sum(k, lab, range(1, n + 1))
        for i in np.argsort(-sz)[:10]:
            sl = objs[i]
            mm = lab[sl] == i + 1
            c = np.median(rgb[sl][mm], 0).astype(int)
            print('   px %5d box x%d-%d y%d-%d maxL %.1f med #%02X%02X%02X' % (sz[i], sl[1].start, sl[1].stop - 1, sl[0].start, sl[0].stop - 1, L[sl][mm].max(), *c))
