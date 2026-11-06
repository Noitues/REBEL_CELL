import json,sys
J=json.load(open('D:/rc_scratch/combat_polish/E7_waves/E10/state_e10.json'))
print(list(J.keys()))
for k in ('f1','f2'):
    f=J[k]; print(k, list(f.keys()))
    for kk,v in f.items():
        s=json.dumps(v); print('  ',kk, s[:600])
for k in J:
    if k not in('f1','f2'): print(k, json.dumps(J[k])[:500])
