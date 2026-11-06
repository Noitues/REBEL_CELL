import json
d = json.load(open('D:/rc_scratch/netrun_cel/city/lots_city.json'))
S = {(a[0], a[1]) for a in d['streets']}; PZ = {(a[0], a[1]) for a in d['plazas']}; K = {(a[0], a[1]) for a in d['parks']}
B = {}
for p in d['prisms']:
    c = p['cell']
    for i in range(c[0], c[0] + c[2]):
        for j in range(c[1], c[1] + c[3]): B[(i, j)] = max(B.get((i, j), 0), p['h'])
import sys
i0, i1, j0, j1 = [int(x) for x in sys.argv[1:5]]
print('     ' + ''.join(str(abs(i) // 10 % 10) if i % 10 == 0 else ' ' for i in range(i0, i1)))
for j in range(j0, j1):
    line = ''
    for i in range(i0, i1):
        t = (i, j)
        ch = 'P' if t in PZ else ('B' if t in B and B[t] >= 12 else ('b' if t in B else ('=' if t in S else ('k' if t in K else '.'))))
        line += ch
    print('%4d %s' % (j, line))
