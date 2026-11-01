import json
d = json.load(open('D:/rc_scratch/combat_polish/E7_waves/E9/state_e9.json'))
f = d['f2']
for u in f['units']:
    print(u['id'], u['kind'], u['dep'], u['s'], u['w'], 'hp', u['hp'], u['mx'], 'sh', u['sh'], 'g', u['grown'], 'hit', u['hit'], 'cons', u['consumed'], 'dead', u['trigdead'], u['fate'], u.get('land_hit'), u.get('land_sectors'), 'lose', u['lose'])
print('log'); [print(' ', e) for e in f['log']]
print('tlog'); [print(' ', e) for e in f['tlog']]
print('wheel', [(w['t'], w['hp'], w['hp_after'], w['brace'], w['soak'], w['soaked']) for w in f['wheel']], 'rot', f['rot'], 'sched', f['schedule'])
print('trigs'); [print(' ', t['uid'], t['kind'], t['dep'], t['s'], t['w'], t['entries']) for t in d['trigs']]
print('hover', d['hover'])
print('meta', d['meta']['lines'])
print('f1 guns', [(g['sector'], g['slice'], [s['result'] for s in g['shots']]) for g in d['f1']['guns']])
