import json
g=json.load(open('D:/rc_scratch/combat_redesign/locked/fx_cdhl/work/geom.json'))
print(g['ring_geom'])
for k in ('f1','f2'):
    print(k, 'adj', g[k]['adj'])
    for uid,u in g[k]['units'].items():
        xs=[p[0] for p in u['poly']]; ys=[p[1] for p in u['poly']]
        print(' ',uid,u['kind'],'dep',u['dep'],'s',u['s'],'w',u['w'],'hp',u['hp'],u['mx'],'tok',[round(v) for v in u['tok']],'bbox',round(min(xs)),round(min(ys)),round(max(xs)),round(max(ys)),'ward',u['warded'],'grown',u['grown'],'hit',u['hit'],u['fate'],u['lose'])
    for a in g[k]['arcs']: print('   arc',a)
for k,v in g['pips_p1'].items(): print('pips',k,[[round(x,1) for x in p[:4]]+[p[4]] for p in v])
