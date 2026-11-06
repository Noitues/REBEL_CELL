import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
J = json.load(open('D:/rc_scratch/e10_design/wave_rings/state_e10.json'))
for b in ('f1', 'f2'):
    f = J[b]
    print(b)
    for u in f['units']:
        print({k: u[k] for k in ('id', 'kind', 'dep', 's', 'w', 'hp', 'mx', 'lose', 'sh', 'shmx', 'hit', 'df', 'warded', 'consumed', 'trigdead', 'fate', 'land_hit') if k in u})
    print('adj', f['adj'])
print(J['hover'], [t['uid'] for t in J['trigs']])
