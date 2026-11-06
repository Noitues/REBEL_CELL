# Independent occupied-vs-empty glass probe. Cells: ring k annulus, sector s centred at 60 s deg.
import sys, json, numpy as np
from lab import *
RINGS = {0: (214, 271), 1: (271, 328), 2: (328, 385)}
# occupancy from state_e10 f1 (p1, p2b, nowords); f2 for p2/p3 (same positions; u1 killed in f2)
OCC = {0: {1: 'u3 Worm', 2: 'u3 Worm', 3: 'u1 Packet', 4: 'u1 Packet', 5: 'u2 Worm(dying)', 0: 'u2 Worm(dying)'},
       1: {0: 'u5 Packet', 2: 'Adjuster', 3: 'u4 Payload', 4: 'u4 Payload'},
       2: {2: 'u6 Packet', 3: 'u6 Packet', 4: 'u6 Packet', 5: 'u7 Packet'}}
STARTS = {(0, 1), (0, 3), (0, 5), (1, 0), (1, 3), (1, 2), (2, 2), (2, 5)}  # first sector of each unit (token there)
plates = sys.argv[1:] or ['p1_decide']
out = {}
for p in plates:
    im = load(p); y = Y(im); Lp = Ls(y)
    sat = im.max(axis=2) - im.min(axis=2)
    res = {}
    for k, (r0, r1) in RINGS.items():
        for s in range(6):
            a0 = 60 * s - 30 + 3; a1 = 60 * s + 30 - 3
            if (k, s) in STARTS: a0 += 15          # skip the token disc
            m = polar_mask(r0 + 6, r1 - 6, a0, a1)
            raw = y[m]
            med = np.median(raw)
            # glass filter: drop saturated marks, bright marks (ticks, enamel), ink lines
            keep = m & (sat < 0.22) & (Lp < 62) & (Lp > 6)
            g = y[keep]
            res['r%d s%d' % (k, s)] = dict(occ=OCC[k].get(s, 'empty'), med=round(float(Ls(med)), 1), glass_mean=round(float(Ls(g.mean())), 1) if g.size else None, keep_frac=round(float(keep.sum() / m.sum()), 2), n=int(m.sum()))
    out[p] = res
    print('==', p)
    for k in RINGS:
        row = []
        emp = [v for kk, v in res.items() if kk.startswith('r%d' % k) and v['occ'] == 'empty']
        eY = max([Yof(v['glass_mean']) for v in emp]) if emp else None
        for s in range(6):
            v = res['r%d s%d' % (k, s)]
            ratio = (Yof(v['glass_mean']) / eY) if eY else float('nan')
            row.append('s%d %-14s med %4.1f gl %4.1f (keep %.2f) Yratio %.2f' % (s, v['occ'][:14], v['med'], v['glass_mean'], v['keep_frac'], ratio))
        print('  ring', k, 'empty ref L*', None if eY is None else round(float(Ls(eY)), 1))
        for rr in row: print('    ' + rr)
json.dump(out, open('cells_out.json', 'w'), indent=1)
