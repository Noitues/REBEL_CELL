import json
J = json.load(open('D:/rc_scratch/combat_polish/E7_waves/E10/state_e10.json'))
for key in ('f1', 'f2'):
    f = J[key]
    print(key, 'adj', f['adj'], 'sched', f['schedule'], 'twr', f['twr'], 'twist', f['twist'], 'rot', f['rot'])
    for g in f['guns']: print('  gun', g)
    print('  wheel', [(w['sector'], w['t'], w['hp'], w['hp_after'], w['brace'], w['soak'], w['soaked']) for w in f['wheel']])
    print('  kills', f.get('kills'), 'refunds', f.get('refunds'), 'tlog', f['tlog'])
    for u in f['units']: print('  unit', u['id'], u['kind'], u['dep'], u['s'], u['w'], 'hp', u['hp'], u['mx'], 'sh', u['sh'], 'grown', u['grown'], u['df'], 'warded', u['warded'], 'lose', u['lose'], 'consumed', u['consumed'], 'trigdead', u['trigdead'])
print(J['trigs'])
print(J['f1']['challenges'], J['f1']['interf'], J['f1']['lineup'], J['f1']['nfut'], J['f1']['rings_wave'])
