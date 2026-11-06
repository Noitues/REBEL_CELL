"""probe_paths.py -- the board pixels of a plain lw_render p1 (work/plain_path/fg_<corp>.npz, R.render without the asm_render capture hooks)
vs the hook path (work/fg_<corp>.npz, the path the published plates take): F (flat-0 render) difference per skin, px over 2/255, max,
the radius band of the differing pixels and the largest clusters."""
import sys, json
sys.dont_write_bytecode = True
import numpy as np
from scipy import ndimage as ndi
W = 'D:/rc_scratch/combat_redesign/locked/round2/backdrop/work/'
yy, xx = np.mgrid[0:1080, 0:1920]
rho = np.hypot(xx - 536, yy - 540)
out = {}
for corp in ('neutral', 'solace', 'meridian'):
    a = np.load(W + 'plain_path/fg_%s.npz' % corp)['F'].astype(np.int16)
    b = np.load(W + 'fg_%s.npz' % corp)['F'].astype(np.int16)
    d = np.abs(a - b).max(-1)
    m = d > 2
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=4))
    objs = ndi.find_objects(lab)
    cl = []
    for i, sl in enumerate(objs):
        mm = (lab[sl] == i + 1) & m[sl]
        if mm.any():
            cl.append(dict(px=int(mm.sum()), box=[sl[1].start, sl[0].start, sl[1].stop, sl[0].stop], max=int(d[sl][mm].max())))
    cl.sort(key=lambda c: -c['px'])
    r = rho[m]
    hist = np.histogram(r, bins=[0, 200, 400, 430, 445, 460, 480, 500, 600, 2300])[0].tolist() if m.any() else []
    out[corp] = dict(px_over_2=int(m.sum()), max=int(d.max()), plain_minus_hook_mean_in_diff=round(float((a - b).max(-1)[m].mean()), 1) if m.any() else None,
                     r_hist_bins='0 200 400 430 445 460 480 500 600 2300', r_hist=hist, clusters=cl[:8])
    print(corp, json.dumps(out[corp]))
json.dump(out, open(W + 'paths_diff.json', 'w'), indent=1)
