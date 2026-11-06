import json
J = json.load(open('D:/rc_scratch/combat_polish/E7_waves/E10/state_e10.json'))
print('top keys', list(J.keys()))
for k in ('f1', 'f2'):
    f = J[k]
    print('====', k, 'keys', list(f.keys()))
    for kk, v in f.items():
        if kk == 'units':
            for u in v:
                print('  unit', json.dumps(u)[:400])
        else:
            s = json.dumps(v)
            print(' ', kk, s[:600])
for k in J:
    if k not in ('f1', 'f2', 'f2t', 'f2b'):
        print('##', k, json.dumps(J[k])[:800])
