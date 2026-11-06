"""o30_bases.py <kind>...  base plates for the O-30 resolve-beat sequence, rendered with a COPY of the locked generator
(fx_o30/gen_src = final/src_snapshot), caches in fx_o30/work/gen.  kinds:
  p3_empty   f2 (resolve) with no units: the ring material, marks, HUD, hand (unit layer = p3 - p3_empty)
  p3         stock resolve plate (check against final/p3_resolve.png)"""
import sys, os, copy, time
sys.dont_write_bytecode = True
os.environ['CORP'] = 'neutral'
GEN = 'D:/rc_scratch/combat_redesign/locked/fx_o30/gen_src'
OUT = 'D:/rc_scratch/combat_redesign/locked/fx_o30/work/'
sys.path.insert(0, GEN)
os.chdir(GEN)
kinds = sys.argv[1:]
sys.argv = [sys.argv[0], 'p3']
import lw_render as LW
LW.R.WORK = OUT + 'gen/'
LW.FH.CACHE = OUT + 'gen/'
R = LW.R
A = R.A
for kind in kinds:
    t = time.time()
    if kind == 'p3':
        im = R.render('p3')
    elif kind == 'p3_empty':
        f = copy.deepcopy(A.J['f2'])
        f['units'] = [u for u in f['units'] if u.get('trigdead')]      # Packet 1 is trigger-dead (not drawn); the refund tag needs it
        for g in f['guns']:
            g['shots'] = [s for s in g['shots'] if s['kind'] == 'Adjuster']
        f['guns'] = [g for g in f['guns'] if g['shots']]
        R.KEY['p3'] = 'f2'
        im = R.render('p3', frame=f, tag='f2_o30empty')
    im.save(OUT + 'base_neutral_%s.png' % kind)
    print('ok', kind, round(time.time() - t, 1), flush=True)
