"""base_render.py <skin> <variant>   variant: p3 | p3alt | p1  -> work/base_<skin>_<variant>.png (+ geometry json, trigger path layers for p3)"""
import sys, os, json, time, copy
skin, var = sys.argv[1], sys.argv[2]
os.environ['CORP'] = skin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_env as GE
R, A = GE.R, GE.A
import wr2_units as W2U, e8lib as E8, a_plan as PL, a2_plan as P2
from PIL import Image
OUTD = 'D:/rc_scratch/combat_redesign/locked/fx_cdhl/work/'
t = time.time()
beat = 'p1' if var == 'p1' else 'p3'
kw = {}
if var == 'p3alt':
    f = copy.deepcopy(A.J['f2'])
    for u in f['units']:
        if u['id'] == 5:
            u['grown'] = 0
        if u['id'] == 6:
            u['warded'] = False
    kw = dict(frame=f, tag='f2_fxalt', hide_units=(2,), arcs_skip=(2,))
    R.KEY['p3'] = 'f2'
if var == 'p3grow':
    f = copy.deepcopy(A.J['f2'])
    for u in f['units']:
        if u['id'] == 5:
            u['land_hit'] = u['hit'] + 1
    kw = dict(frame=f, tag='f2_fxgrow')
if var == 'p3kill':
    f = copy.deepcopy(A.J['f2'])
    f['units'] = [u for u in f['units'] if u['id'] != 2]
    for g in f['guns']:
        g['shots'] = [sh for sh in g['shots'] if sh['uid'] != 2]
    f['guns'] = [g for g in f['guns'] if g['shots']]
    kw = dict(frame=f, tag='f2_fxkill')
    R.KEY['p3'] = 'f2'
im = R.render(beat, **kw)
im.save(OUTD + 'base_%s_%s.png' % (skin, var))
geo = dict(pips={str(k): v for k, v in W2U.ST.PIPS.items()})
if var == 'p3' and skin == 'neutral':
    f = A.J['f2']
    for col, nm in (((255, 226, 0), 'yel'), ((255, 61, 168), 'pink')):
        old = P2.YEL
        P2.YEL = col
        import wr2_units as _W
        oldp = _W.PLAN
        _W.PLAN = col
        L = R.L2()
        for tr in A.J['trigs']:
            PL.trigger_path(L, f, dict(tr, entries=[e for e in tr['entries'] if e[0] != 'refund']), 'A')
        L.done().save(OUTD + 'trig_%s.png' % nm)
        P2.YEL = old
        _W.PLAN = oldp
    geo['wheel_f1'] = A.J['f1']['wheel']
    geo['wheel_f2'] = A.J['f2']['wheel']
json.dump(geo, open(OUTD + 'geo_%s_%s.json' % (skin, var), 'w'), indent=0)
print('ok', skin, var, round(time.time() - t, 1), flush=True)
