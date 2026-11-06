import json, collections, sys
d = json.load(open('D:/rc_scratch/netrun_cel/city/lots_city.json'))
print(d['camera'])
P = d['prisms']; print('prisms', len(P), 'streets', len(d['streets']), 'plazas', len(d['plazas']), 'parks', len(d['parks']), 'hqs', d['hqs'])
print(P[0]); print(d['streets'][:3]); print(d['plazas'][:3])
print(collections.Counter(p['terr'] for p in P).most_common())
hs = sorted(p['h'] for p in P); print('h min/med/max', hs[0], hs[len(hs)//2], hs[-1])
print(collections.Counter(p['key'] for p in P).most_common(8)); print(collections.Counter(p['ak'] for p in P).most_common(8))
import math
w = [ (max(q[0] for q in p['poly'])-min(q[0] for q in p['poly'])) for p in P]; print('width sample', sorted(w)[len(w)//2])
