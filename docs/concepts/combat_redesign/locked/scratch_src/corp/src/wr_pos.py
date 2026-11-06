import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import json, math
import e8lib as E8
from cv_lib import C, ppx
import cv_board as CB
J = json.load(open('D:/rc_scratch/e10_design/wave_rings/state_e10.json'))
f = J['f1']
for u in f['units']:
    x, y = E8.token_pos(u)
    ri, ro = CB.ring_geom(u['dep'])
    ax = [ppx(C, (ri + ro) / 2, 60 * (u['s'] + q)) for q in range(u['w'])]
    print(u['id'], u['kind'], 'dep', u['dep'], 's', u['s'], 'w', u['w'], 'token', round(x), round(y), 'axes', [(round(a), round(b)) for a, b in ax])
a = f['adj']
ri, ro = CB.ring_geom(a['ring'])
print('adj', [round(v) for v in ppx(C, (ri + ro) / 2 - 3, 60 * a['s'])])
for s in range(6):
    print('sector', s, [tuple(round(v) for v in ppx(C, r, 60 * s)) for r in (193, 257, 321)])
print(J['hover']['id'], [ (e[0]) for e in J['trigs'][0]['entries']], J['trigs'][0]['uid'], f.get('kills'), J['f2']['kills'])
