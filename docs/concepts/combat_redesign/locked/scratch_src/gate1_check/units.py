import json
st = json.load(open('D:/rc_scratch/combat_polish/E7_waves/E10/state_e10.json'))
for f in ['f1', 'f2', 'f2t', 'f2b']:
    if f not in st: continue
    F = st[f]
    print('==', f, 'turn', F.get('turn'), 'hp', F.get('hp'), 'ram', F.get('ram'), 'trace', F.get('trace'), 'hand', F.get('hand'), 'played', F.get('played'), 'kills', F.get('kills'), 'refunds', F.get('refunds'))
    for u in F['units']:
        print('  id%d %-8s dep%d s%d w%d hp %d/%d hit %d grown %s df %s warded %s fate %s land_hit %s land_sectors %s through %s' % (u['id'], u['kind'], u['dep'], u['s'], u['w'], u['hp'], u['mx'], u['hit'], u['grown'], u['df'], u['warded'], u['fate'], u.get('land_hit'), u.get('land_sectors'), u.get('land_through')))
    print('  adj', F['adj'])
    print('  pv', F['pv'])
    print('  schedule', F['schedule'], 'twr', F['twr'], 'lineup', F['lineup'], 'rings_wave', F['rings_wave'], 'waves_left', F['waves_left'])
    print('  challenges', F['challenges'])
    print('  wheel', [(w['sector'], w['t'], w['hp'], w['mx'], w['hp_after']) for w in F['wheel']])
    print('  guns', F['guns'])
print(list(st.keys()))
