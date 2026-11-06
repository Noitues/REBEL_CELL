"""geom.py <chk.json> -- print ring radii and unit layout from the capture geometry."""
import sys, json, math
import numpy as np

chk = json.load(open(sys.argv[1]))
g = chk['rb']['geometry']
C = (536, 540)
for c in g['cells']:
    p = np.array(c["poly"]).reshape(-1, 2)
    if len(p) == 0:
        print("empty poly", c["dep"], c["s"], c.get("state")); continue
    r = np.hypot(p[:, 0] - C[0], p[:, 1] - C[1])
    a = (np.degrees(np.arctan2(p[:, 0] - C[0], -(p[:, 1] - C[1]))) + 360) % 360
    print('cell dep %d s %d uid %s %-8s %-7s r %.1f-%.1f  ang %.0f-%.0f' % (c['dep'], c['s'], c['uid'], c['kind'], c['state'], r.min(), r.max(), a.min(), a.max()))
for u in g['units']:
    print('unit', {k: u[k] for k in u})
for c in g['probe'][:3]:
    p = np.array(c["poly"]).reshape(-1, 2)
    if len(p) == 0:
        print("empty poly", c["dep"], c["s"], c.get("state")); continue
    r = np.hypot(p[:, 0] - C[0], p[:, 1] - C[1])
    print('probe dep %d s %d r %.1f-%.1f' % (c['dep'], c['s'], r.min(), r.max()))
print('info', chk['rb'].get('info'))
print('mask_px', chk.get('mask_px'))
