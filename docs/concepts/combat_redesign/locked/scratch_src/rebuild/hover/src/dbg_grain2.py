"""dbg_grain2.py <name> : L* percentiles of the L6 wax core (as check_grain takes it) and where the darkest core pixels are"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
import hv_checks as HC
g, dil = HC.g, HC.dil
name = sys.argv[1]
rep, M, lit, rgb, bg, probe = HC.load(name)
pen_all, pen_wax, focus, hover, ghost, inset, hand, stick = HC.board_mask_sets(M)
top = dil(hand | stick | inset | g(M, 'Z__digits') | g(M, 'Z__labels') | g(M, 'Z__tags') | g(M, 'Z__badges') | g(M, 'Z__tickets') | g(M, 'Z__tape')
          | g(M, 'Z__plates') | g(M, 'Z__leader') | g(M, 'Z__hud_labels') | g(M, 'Y__you') | focus, 2)
core = ndi.binary_erosion(g(M, 'P__L6_wax'), iterations=1) & ~top
Ls = HC.T.lstar(HC.T.lum(rgb))
v = Ls[core]
print('core px', core.sum(), 'L* p1/p5/p25/p50/p95/p99', np.round(np.percentile(v, [1, 5, 25, 50, 95, 99]), 1))
dark = core & (Ls < 60)
lb, n = ndi.label(dark)
sizes = ndi.sum(dark, lb, range(1, n + 1))
for i in np.argsort(sizes)[::-1][:6]:
    ys, xs = np.nonzero(lb == i + 1)
    print('dark cluster %d px at (%d,%d)-(%d,%d) mean L* %.1f' % (sizes[i], xs.min(), ys.min(), xs.max(), ys.max(), Ls[lb == i + 1].mean()))
