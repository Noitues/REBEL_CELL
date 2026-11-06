import json
J=json.load(open('../state_e10.json'))
for k in ('f1','f2'):
    f=J[k]
    print(k,[(u['id'],u['kind'],u['dep'],u['s'],u['w']) for u in f['units']])
