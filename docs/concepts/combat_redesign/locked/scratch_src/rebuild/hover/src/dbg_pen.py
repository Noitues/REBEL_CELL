import sys, numpy as np
sys.dont_write_bytecode = True
import hv_checks as HC
name = sys.argv[1]
rep, M, lit, rgb, bg, probe = HC.load(name)
for k in ('P__L6_all', 'P__L6_wax'):
    m = HC.g(M, k)
    ys, xs = np.nonzero(m)
    print(k, m.sum(), 'bbox', xs.min(), ys.min(), xs.max(), ys.max())
    # vertical run lengths at columns near the top of the rim (x 500-580) and horizontal runs at rows near y 540 on the right
    runs = []
    for x in range(xs.min(), xs.max() + 1, 7):
        col = m[:, x]
        if not col.any():
            continue
        r = np.nonzero(col)[0]
        # split into runs
        br = np.nonzero(np.diff(r) > 1)[0]
        seg = np.split(r, br + 1)
        runs += [len(s_) for s_ in seg]
    print('  vertical runs (sampled cols)', sorted(runs)[:10], '... median', np.median(runs), 'n', len(runs))
    print('  hist', np.bincount(runs)[:20])
    print('  stroke_width', HC.stroke_width(m))
