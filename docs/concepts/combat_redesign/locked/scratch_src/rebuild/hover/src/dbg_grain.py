import sys, numpy as np
sys.dont_write_bytecode = True
import hv_checks as HC
from scipy import ndimage as ndi
name = sys.argv[1]
rep, M, lit, rgb, bg, probe = HC.load(name)
T = HC.T
Ls = T.lstar(T.lum(rgb))
keep = np.zeros((1080, 1920), bool)
for k in ('digits', 'labels', 'tags', 'badges', 'tickets', 'leader', 'tape', 'plates', 'hud_labels', 'hand', 'inset'):
    keep |= HC.g(M, 'Z__' + k)
keep |= HC.g(M, 'Y__you')
wax = HC.g(M, 'P__L6_wax')
for er in (1, 2):
    core = ndi.binary_erosion(wax, iterations=er) & ~HC.dil(keep, 2)
    v = Ls[core]
    print('erode', er, 'px', core.sum(), 'p99 %.1f max %.1f mean %.1f std %.2f' % (np.percentile(v, 99), v.max(), v.mean(), v.std()))
    hi = core & (Ls > 91)
    ys, xs = np.nonzero(hi)
    print('  bright px', hi.sum(), 'sample', list(zip(xs[:8], ys[:8])))
    if hi.any():
        print('  colours', rgb[hi][:6].astype(int).tolist())
