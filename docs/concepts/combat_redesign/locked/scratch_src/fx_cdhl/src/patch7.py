p='D:/rc_scratch/combat_redesign/locked/fx_cdhl/src/base_render.py'
s=open(p).read()
s=s.replace("""im = R.render""","""if var == 'p3kill':
    f = copy.deepcopy(A.J['f2'])
    f['units'] = [u for u in f['units'] if u['id'] != 2]
    for g in f['guns']:
        g['shots'] = [sh for sh in g['shots'] if sh['uid'] != 2]
    f['guns'] = [g for g in f['guns'] if g['shots']]
    kw = dict(frame=f, tag='f2_fxkill')
    R.KEY['p3'] = 'f2'
im = R.render""",1)
open(p,'w').write(s)
