p='D:/rc_scratch/combat_redesign/locked/fx_cdhl/src/base_render.py'
s=open(p).read()
s=s.replace("""    R.KEY['p3'] = 'f2'
im = R.render""","""    R.KEY['p3'] = 'f2'
if var == 'p3grow':
    f = copy.deepcopy(A.J['f2'])
    for u in f['units']:
        if u['id'] == 5:
            u['land_hit'] = u['hit'] + 1
    kw = dict(frame=f, tag='f2_fxgrow')
im = R.render""")
open(p,'w').write(s)
