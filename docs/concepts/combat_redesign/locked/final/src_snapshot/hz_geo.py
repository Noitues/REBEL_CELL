"""probe: unit sector -> screen angle on the final board"""
import sys, math
sys.dont_write_bytecode = True
import hz_core as Z
from hz_core import *
f = A.J['f1']
for u in f['units']:
    x, y = AU.token_pos(u)
    a = math.degrees(math.atan2(x - C[0], -(y - C[1]))) % 360
    poly = HL.cell_poly_unit(u)
    angs = [math.degrees(math.atan2(px - C[0], -(py - C[1]))) % 360 for px, py in poly]
    print(u['id'], u['kind'], 'dep', u['dep'], 's', u['s'], 'w', u['w'], 'token', round(x), round(y), 'ang', round(a), 'poly ang range', round(min(angs)), round(max(angs)), 'r', round(math.hypot(x - C[0], y - C[1])))
print('adj', f['adj'])
print('ring_geom', [CB.ring_geom(d) for d in range(3)])
