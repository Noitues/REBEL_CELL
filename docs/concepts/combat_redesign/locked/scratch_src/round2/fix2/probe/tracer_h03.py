"""the gun-tracer px d2 measures on a hover plate (lit, off the hover marks): bbox, top colour bins, pigment, and the same px on the same-state
board image; writes a crop of the bbox"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/round2/hover/src')
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image
import hv_checks as HC
import rb_checks_r2 as R2
import rb_tokens as T
name = sys.argv[1]
rep, M, lit, rgb, bg, probe = HC.load(name)
Mr = HC.r2_masks(M)
L_ = HC._lit(lit)
hov = HC.dil(R2.pen_all(Mr) | HC.g(Mr, 'focus') | HC.g(Mr, 'hover') | HC.g(Mr, 'ghost') | HC.g(Mr, 'inset'), 1) | HC.changed_px(rgb, bg, lit)
over = HC.g(Mr, 'hud') | HC.g(Mr, 'hand') | HC.g(Mr, 'send') | HC.g(Mr, 'undo')
m = HC.g(Mr, 'guns') & L_ & ~hov & ~over
ys, xs = np.nonzero(m)
print('px', m.sum(), 'bbox', xs.min(), ys.min(), xs.max(), ys.max())
pg = R2.pigment(rgb, m)
print('pigment', pg, 'dE', T.de76(pg[0], R2._token('CELL_PINK')))
px = rgb[m].astype(int)
lab = T.lab(px.astype(np.float64))
ch = np.hypot(lab[:, 1], lab[:, 2])
sel = ch > 25
b = (px[sel] // 6)
key = b[:, 0] * 1000000 + b[:, 1] * 1000 + b[:, 2]
u, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
for i in np.argsort(-cnt)[:8]:
    s = px[sel][inv == i]
    print('   bin share %.3f n %d median %s' % (cnt[i] / sel.sum(), cnt[i], np.median(s, 0)))
print('median chromatic', np.median(px[sel], 0), 'dE', T.de76(tuple(np.median(px[sel], 0)), R2._token('CELL_PINK')))
if bg is not None:
    pgb = R2.pigment(bg, m)
    print('same px on the board image: pigment', pgb, 'dE', T.de76(pgb[0], R2._token('CELL_PINK')))
ysel, xsel = ys[sel], xs[sel]
top = np.argmax(cnt)
tb = inv == top
print('top-bin px positions x %d-%d y %d-%d' % (xsel[tb].min(), xsel[tb].max(), ysel[tb].min(), ysel[tb].max()))
for k in sorted(Mr):
    if k.startswith('Pv') or k in ('guns',):
        continue
    v = Mr[k]
    if v.dtype != bool:
        continue
    o = int(v[ysel[tb], xsel[tb]].sum())
    if o:
        print('   top-bin px also in', k, o)
adjm = HC.g(Mr, 'adj_hp') | HC.g(Mr, 'adj')
print('guns px under adj / adj_hp (1 px grown)', int((m & HC.dil(adjm, 1)).sum()))
m2 = m & ~HC.dil(adjm, 1)
pg2 = R2.pigment(rgb, m2)
print('pigment off the Adjuster', pg2, 'dE', T.de76(pg2[0], R2._token('CELL_PINK')), 'px', int(m2.sum()))
# components
from scipy import ndimage as ndi
lab_, n = ndi.label(m)
objs = ndi.find_objects(lab_)
sz = ndi.sum(m, lab_, range(1, n + 1))
for i in np.argsort(-sz)[:8]:
    sl = objs[i]
    mm = lab_[sl] == i + 1
    pgi = R2.pigment(rgb[sl[0], sl[1]], mm) if mm.sum() >= 10 else None
    print('  comp px %d box x%d-%d y%d-%d pigment %s' % (sz[i], sl[1].start, sl[1].stop, sl[0].start, sl[0].stop, pgi))
