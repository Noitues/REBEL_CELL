import json
rows = json.load(open('D:/rc_scratch/netrun_cel/city/lots.json'))
cls = {(r[0], r[1]): r[4] for r in rows}
print('    ' + ''.join('%d' % (abs(i) // 10 % 10) if i % 10 == 0 else ' ' for i in range(-58, -28)))
for j in range(-44, -10):
    line = ''
    for i in range(-58, -28):
        c = cls.get((i, j))
        if c is None: ch = '?'
        elif 'P' in c: ch = 'P'
        elif 'B' in c: ch = 'B'
        elif 'S' in c: ch = '='
        elif 'K' in c: ch = 'k'
        elif 'W' in c: ch = '~'
        else: ch = '.'
        line += ch
    print('%4d %s' % (j, line))
