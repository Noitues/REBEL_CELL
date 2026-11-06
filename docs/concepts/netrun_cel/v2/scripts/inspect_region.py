import json, collections
d = json.load(open('D:/rc_scratch/netrun_cel/city/lots_city.json'))
P = d['prisms']
reg = [p for p in P if -60 <= p['cell'][0] <= -28 and -44 <= p['cell'][1] <= -10]
print('prisms in region', len(reg))
print('y0 values', collections.Counter(round(p['y0'], 1) for p in reg).most_common(8))
print('terr', collections.Counter(p['terr'] for p in reg), 'ak', collections.Counter(p['ak'] for p in reg))
print('h dist', sorted(round(p['h']) for p in reg)[::max(1, len(reg)//20)])
print('taper', collections.Counter(round(p['taper'], 2) for p in reg).most_common(5), 'hq', sum(p['hq'] for p in reg))
print('cell sizes', collections.Counter((p['cell'][2], p['cell'][3]) for p in reg).most_common(6))
big = sorted(reg, key=lambda p: -p['h'])[:6]
for p in big: print(p['cell'], p['h'], p['ak'], p['terr'])
