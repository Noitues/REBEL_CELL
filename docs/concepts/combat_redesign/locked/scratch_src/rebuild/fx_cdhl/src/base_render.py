"""base_render.py <skin> <variant> [<variant> ...]    variants: p1 | p3 | p3alt | p3grow | p3kill
Renders each base on the rebuilt board (corp/src, read-only) with f1_render.SPLIT on, and saves
  work/base_<skin>_<var>_below.png  (RGB: room, scrim, board, tower, units, arcs, guns, tags, digits)
  work/base_<skin>_<var>_above.png  (RGBA: HUD, YOU strip, hand, UNDO, nameplate, SEND IT)
  work/base_<skin>_<var>.png        (below + above, the plate as published)
  work/geo_<skin>_<var>.json        (unit tokens, HP tick geometry, tower pips, frame key)
and, for p1 / p3, the pixel difference against the published locked/final plate."""
import sys, os, json, time, copy
skin = sys.argv[1]
os.environ['CORP'] = skin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_env as GE
R, A = GE.R, GE.A
import numpy as np
from PIL import Image
import wr2_units as W2U, e8lib as E8, a_plan as PL, a2_plan as P2
OUTD = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_cdhl/work/'
FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
PLATE = {'p1': 'p1_decide', 'p3': 'p3_resolve'}


def frame_kw(var):
    kw = {}
    if var == 'p3alt':                       # ward_on pre-state: Packet 6 not yet warded
        f = copy.deepcopy(A.J['f2'])
        for u in f['units']:
            if u['id'] == 6:
                u['warded'] = False
        kw = dict(frame=f, tag='f2_fxalt')
    if var == 'p3grow':                      # grow post-state: Packet 5 lands one more hit (the board's hollow growth chevron)
        f = copy.deepcopy(A.J['f2'])
        for u in f['units']:
            if u['id'] == 5:
                u['land_hit'] = u['hit'] + 1
        kw = dict(frame=f, tag='f2_fxgrow')
    if var == 'p3kill':                      # kill post-state: Worm 2 and its shots removed (empty cell)
        f = copy.deepcopy(A.J['f2'])
        f['units'] = [u for u in f['units'] if u['id'] != 2]
        for g in f['guns']:
            g['shots'] = [sh for sh in g['shots'] if sh['uid'] != 2]
        f['guns'] = [g for g in f['guns'] if g['shots']]
        kw = dict(frame=f, tag='f2_fxkill')
    return kw


for var in sys.argv[2:]:
    t = time.time()
    beat = 'p1' if var == 'p1' else 'p3'
    kw = frame_kw(var)
    R.SPLIT.clear()
    R.SPLIT['on'] = True
    W2U.ST.PIPS.clear()
    im = R.render(beat, room=GE.ROOM, **kw)
    below, above = R.SPLIT['below'].convert('RGB'), R.SPLIT['above']
    R.SPLIT.clear()
    pips = {str(k): [list(p) for p in v] for k, v in W2U.ST.PIPS.items()}
    below.save(OUTD + 'base_%s_%s_below.png' % (skin, var))
    above.save(OUTD + 'base_%s_%s_above.png' % (skin, var))
    im.save(OUTD + 'base_%s_%s.png' % (skin, var))
    f = kw.get('frame') or A.J['f1' if beat == 'p1' else 'f2']
    geo = dict(var=var, beat=beat, skin=skin, pips=pips,
               tokens={str(u['id']): list(E8.token_pos(u)) for u in f['units']},
               units={str(u['id']): dict(kind=u['kind'], dep=u['dep'], s=u['s'], w=u['w'], hp=u['hp'], mx=u['mx'], hit=u['hit'],
                                         warded=u['warded'], grown=u['grown'], fate=u['fate']['kind'], lose=u.get('lose')) for u in f['units']},
               adj=f['adj'], wheel=f['wheel'], hud_bottom=A.INFO.get('hud_bottom'))
    if var in PLATE:
        fp = FINAL + PLATE[var] + ('' if skin == 'neutral' else '_' + skin) + '.png'
        if os.path.exists(fp):
            ref = np.asarray(Image.open(fp).convert('RGB')).astype(int)
            d = np.abs(np.asarray(im.convert('RGB')).astype(int) - ref).max(axis=2)
            geo['vs_final'] = dict(plate=os.path.basename(fp), mean_abs=round(float(d.mean()), 4), px_over_8=int((d > 8).sum()), max=int(d.max()))
    # the Trigger route layers (trig_yel.png / trig_pink.png) are written by trig_layers.py
    json.dump(geo, open(OUTD + 'geo_%s_%s.json' % (skin, var), 'w'), indent=0, default=str)
    print('ok', skin, var, round(time.time() - t, 1), geo.get('vs_final'), flush=True)
