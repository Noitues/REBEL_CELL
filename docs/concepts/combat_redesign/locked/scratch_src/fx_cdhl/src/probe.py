import sys, os, json, time, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_env as GE
R, A = GE.R, GE.A
import wr2_units as W2U, wr_units as WU, e8lib as E8, r2_arcs as A2
import numpy as np
from PIL import Image
t = time.time()
im = R.render('p1')
print('render', round(time.time() - t, 1))
im.save('D:/rc_scratch/combat_redesign/locked/fx_cdhl/work/probe_p1.png')
ref = np.asarray(Image.open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/p1_decide.png').convert('RGB')).astype(int)
print('diff vs final', np.abs(np.asarray(im).astype(int) - ref).mean())
out = {}
for key in ('f1', 'f2'):
    f = A.J[key]
    d = {}
    for u in f['units']:
        x, y = E8.token_pos(u)
        b = WU.unit_bounds(u) if hasattr(WU, 'unit_bounds') else None
        d[u['id']] = dict(kind=u['kind'], dep=u['dep'], s=u['s'], w=u['w'], hp=u['hp'], mx=u['mx'], tok=[x, y],
                          poly=[list(p) for p in WU.u_poly(u)], warded=u['warded'], grown=u['grown'], hit=u['hit'], fate=u['fate']['kind'], lose=u.get('lose'))
    items = A2.layout_items(f, None, None)
    arcs = [dict(uid=it['u']['id'], k=it['k'], lane=it['lane'], a0=it['a0'], a1=it['a1']) for it in items]
    out[key] = dict(units=d, arcs=arcs, adj=f['adj'])
out['pips_p1'] = {str(k): v for k, v in W2U.ST.PIPS.items()}
import cv_board as CB
out['ring_geom'] = [CB.ring_geom(i) for i in range(3)]
json.dump(out, open('D:/rc_scratch/combat_redesign/locked/fx_cdhl/work/geom.json', 'w'), indent=1, default=str)
print('ok')
