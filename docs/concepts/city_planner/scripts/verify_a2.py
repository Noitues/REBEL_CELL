"""Sanity-check city_A2.json (units, extents, clearances, completeness)."""
import json
import math
import os

p = os.path.join(os.path.dirname(__file__), '..', 'city_A2.json')
d = json.load(open(p, encoding='utf-8'))
print('top-level keys:', list(d.keys()))
allpts = []


def walk(o):
    if isinstance(o, list):
        if len(o) == 2 and all(isinstance(v, (int, float)) for v in o):
            allpts.append(o)
        else:
            for v in o:
                walk(v)
    elif isinstance(o, dict):
        for k, v in o.items():
            if k in ('hills',):
                continue
            walk(v)


walk(d)
xs = [q[0] for q in allpts]
ys = [q[1] for q in allpts]
print('points', len(allpts), 'x range', min(xs), max(xs), 'y range', min(ys), max(ys))
print('counts: roads', len(d['roads']), 'interchanges', len(d['interchanges']), 'rails', len(d['rails']),
      'stations', len(d['stations']), 'parks', len(d['parks']), 'neighbourhoods', len(d['neighbourhoods']),
      'checkpoints', len(d['checkpoints']), 'landmarks', len(d['landmarks']))
print('interchange types:', sorted(set(i['type'] for i in d['interchanges'])))
print('ratio', d['meta']['farthest_to_nearest_corp_ratio'])
hq = {l['district']: l['pos'] for l in d['landmarks'] if l['kind'] == 'hq'}


def mind(poly, pos):
    best = 1e18
    for a, b in zip(poly[:-1], poly[1:]):
        ax, ay = a
        bx, by = b
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy or 1.0
        t = max(0, min(1, ((pos[0] - ax) * dx + (pos[1] - ay) * dy) / L2))
        best = min(best, math.hypot(pos[0] - (ax + t * dx), pos[1] - (ay + t * dy)))
    return best


for k, pos in hq.items():
    r = min(mind(x['polyline'], pos) for x in d['roads'] if x['class'] in ('ring', 'motorway', 'truck'))
    t = min(mind(x['polyline'], pos) for x in d['rails'])
    print('HQ', k, 'nearest motorway-class %.0f m, nearest rail %.0f m' % (r, t))
print('Meridian rail ends (m from HQ):', [round(math.hypot(x['polyline'][-1][0] - hq['meridian'][0], x['polyline'][-1][1] - hq['meridian'][1])) for x in d['rails'] if 'Freight Main' in x['name']])
print('port keys:', list(d['port'].keys()))
print('drowned quarter dams:', d['drowned_quarter']['behind_dams'])
