"""L* p95 / p99 of the Z__hover class (minus FOCUS and pencil, 1 px grown) and of the changed px on hover plates"""
import sys, glob, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/round2/gate1')
import glib as G
H, W = 1080, 1920
def m(z, k):
    return np.unpackbits(z[k])[:H * W].reshape(H, W).astype(bool) if k in z.files else np.zeros((H, W), bool)
for f in sys.argv[1:]:
    nm = os.path.basename(f)[:-4]
    z = np.load('D:/rc_scratch/combat_redesign/locked/round2/hover/chk/%s.npz' % nm)
    L = G.Lstar(G.load(f))
    hv = m(z, 'Z__hover')
    pen = m(z, 'P__L6_all') | m(z, 'P__L5_all') | m(z, 'P__L5c_all') | m(z, 'P__L5h_all')
    foc = m(z, 'F__m')
    cut = ndi.binary_dilation(pen | foc, iterations=1)
    r, th, xx, yy = G.polar()
    k = hv & ~cut & (r < 480)
    print('%-26s hover-class px %6d p95 %.1f p99 %.1f max %.1f' % (nm, k.sum(), np.percentile(L[k], 95) if k.any() else -1, np.percentile(L[k], 99) if k.any() else -1, L[k].max() if k.any() else -1))
