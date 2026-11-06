import json
st = json.load(open('D:/rc_scratch/combat_polish/E7_waves/E10/state_e10.json'))
for f in ['f1', 'f2', 'f2t', 'f2b']:
    for u in st[f]['units']:
        print(f, u['id'], u['kind'], 'consumed', u['consumed'], 'trigdead', u['trigdead'], 'lose', u['lose'], 'wear', u.get('wear'), 'jam', u.get('jam'))
