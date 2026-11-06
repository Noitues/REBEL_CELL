from common import *
w = World('default')
for sid, s in w.sites.items():
    print(sid, s['state'], s['tier'], s.get('exploit'), np.round(s['B']), 'crown', np.round(s['crown']))
print('home', w.home, 'hq', w.hq)
for r, R in w.routes.items():
    print(r, R['typ'], R['sites'], plen(R['path']))
for h in w.hunters:
    print('hunter', h['typ'], h['sites'], plen(h['path']))
print([ (b['name'], b['type'], b['role']) for b in w.f['beams']])
print(w.d.keys())
