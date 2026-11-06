"""geo_dump2.py <chk json>: geometry keys and compact cell list (dep, s, uid, kind, state, angular span, radial span)."""
import sys, json, math
d = json.load(open(sys.argv[1]))
g = d['rb']['geometry']
print('geometry keys', list(g.keys()))
C = (536.0, 540.0)
for k, v in g.items():
    if k == 'cells':
        for c in v:
            pts = c['poly']
            rs = [math.hypot(x - C[0], y - C[1]) for x, y in pts]
            an = [math.degrees(math.atan2(x - C[0], -(y - C[1]))) % 360 for x, y in pts]
            print('cell', {kk: vv for kk, vv in c.items() if kk != 'poly'}, 'r %.0f-%.0f' % (min(rs), max(rs)), 'ang', round(an[0], 1), round(an[len(an) // 2 - 1], 1))
    else:
        print('--', k, json.dumps(v)[:700])
print('cards', json.dumps(d['rb']['cards']))
