import numpy as np
import p1lib as L
w = L.load_world()
for sid, s in w.sites.items():
    print(sid, s['tier'], np.round(s['B']).tolist())
print('home', w.home)
for k, r in w.routes.items():
    print(k, r['typ'], r.get('sites'), len(r['path']), 'ext', r['ext'])
