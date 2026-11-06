import json
J = json.load(open('D:/rc_scratch/combat_polish/E7_waves/E10/state_e10.json'))
for key in ('f1', 'f2', 'f2t', 'f2b'):
    f = J[key]
    print(key)
    for u in f['units']:
        if u.get('land_hit') is None:
            print('  ', u['id'], u['kind'], 'ring', u['dep'], 'no landing', u['fate']['kind'], 'consumed', u['consumed'], 'trigdead', u['trigdead'])
            continue
        print('  ', u['id'], u['kind'], 'ring', u['dep'], 's', u['s'], 'w', u['w'], 'k', u['fate']['k'], 'land_sectors', u['land_sectors'], 'hit', u['land_hit'], 'cur hit', u['hit'], 'through', u['land_through'], 'soak', u['land_soak'], 'brace', u['land_brace'])
