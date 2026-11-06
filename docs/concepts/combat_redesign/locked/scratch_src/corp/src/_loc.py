import numpy as np, sys
sys.dont_write_bytecode = True
W = 'D:/rc_scratch/combat_redesign/locked/assembled/work/'
def load(sfx):
    z = np.load(W + 'masks_%s.npz' % sfx)
    return {k: np.unpackbits(z[k])[:1080 * 1920].reshape(1080, 1920).astype(bool) for k in z.files}
for sfx, a, b in (('p1', 'digits', 'labels'), ('p2b', 'badges', 'tags')):
    m = load(sfx)
    o = m[a] & m[b]
    ys, xs = np.nonzero(o)
    print(sfx, a, b, o.sum(), 'x', xs.min(), xs.max(), 'y', ys.min(), ys.max())
    for k in (a, b):
        ys, xs = np.nonzero(m[k][max(0, ys.min() - 40):ys.max() + 40, max(0, xs.min() - 60):xs.max() + 60])
