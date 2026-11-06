import json
J=json.load(open('D:/rc_scratch/e10_design/wave_rings/state_e10.json'))
print(J.keys())
for key in ('f1','f2'):
    f=J[key]
    print(key, [k for k in f.keys()])
    for u in f['units']:
        print(u['id'],u['kind'],'dep',u['dep'],'s',u['s'],'w',u['w'],'hp',u['hp'],'/',u['mx'],'lose',u['lose'],'sh',u['sh'],u['shmx'],'hit',u['hit'],'df',u['df'],'warded',u['warded'],'cons',u['consumed'],'tdead',u['trigdead'],'fate',u['fate']['kind'], 'landhit',u.get('land_hit'))
    print('adj',f['adj'])
print(J['hover']['id'], J.get('trigs') and [ (t.get('uid'), t.keys()) for t in J['trigs']])
