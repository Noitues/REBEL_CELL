import json
J = json.load(open('D:/rc_scratch/combat_redesign/locked/corp/state_e10.json'))
print(list(J.keys()))
for k in ('f1', 'f2'):
    f = J[k]
    print(k, list(f.keys()))
    for u in f['units']:
        print('  ', {kk: u[kk] for kk in ('id', 'kind', 'dep', 's', 'w', 'hp', 'mx', 'hit', 'consumed', 'trigdead', 'warded', 'df', 'lose') if kk in u}, u.get('fate'))
    print('  adj', f.get('adj'))
    print('  sched', f.get('schedule'), 'rings_wave', f.get('rings_wave'))
