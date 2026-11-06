"""mp_bases.py <skin> <kind> [<kind> ...]
Base plates for the M / P / S / T effects on the rebuilt board (2026-11-03 rebuild + stage 2 + gate 1), rendered from corp/src
(imported read-only; the tower cache is redirected to this folder).  f1_render.SPLIT is on, so every kind is saved twice:
  work/bases/<skin>_<kind>_below.png   the board layer (room, scrim, board, tower, units, arcs, guns, labels, tags, digits): RGB
  work/bases/<skin>_<kind>_above.png   everything from the HUD up (HUD, YOU strip, hand, UNDO, nameplate, SEND IT): RGBA
so an effect is composited between them: board -> effect -> HUD and hand (review 1.6, ART_BIBLE 6.4 layer order).
kinds (state E10):
  p1 p2 p3        the stock beats
  p1_empty        f1 with no units (guns kept, so the p1 - p1_empty difference is the unit layer without the gun marks)
  p1_noguns       f1 without the gun marks (spin: the guns re-solve after the turn)
  p1_hold         f1 with schedule [0, 2, 0] (the end state of Hold)
  p1_after        f1 after GUNS and LANDS: ring 0 units gone, no gun marks, no landing arcs (the start of rings step)
  p1_clean        f1 with no units, no gun marks, no arcs (the ground the moving cells slide over)
  p3_pre          f2 resolve board before TRIGGER resolves: Trace 3, RAM 2, no refund (HUD row and board coin)
  p3_mid          f2 after the Trace add: Trace 4, RAM 2, no refund
  p3_kill         f2 after the gun kill: Worm 2 gone, the sector 0 gun marks spent
  p3_after        f2 after LANDS: ring 0 empty, no gun marks, no arcs, the board refund coin gone (HUD as p3)
  p3_clean        f2 with no units, no gun marks, no arcs, no board coin (HUD as p3)
"""
import sys, os, copy, time, json
sys.dont_write_bytecode = True
skin = sys.argv[1]
kinds = sys.argv[2:]
os.environ['CORP'] = skin
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
ME = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/'
sys.path.insert(0, SRC)
os.chdir(SRC)
CW = ME + 'work/tower_cache_%s/' % skin
os.makedirs(CW, exist_ok=True)
os.makedirs(ME + 'work/bases', exist_ok=True)
import lw_render as LW
import bd_grade as BG
from PIL import Image
import numpy as np
R = LW.R
R.WORK = CW                      # never write the shared tower cache
A = R.A
# the published plates come from asm_render.py with its checks on; rendering without them drew a different HUD chain TWIST glyph on p3
# (a spiral instead of the kglyph2 ring arrow).  So the same capture hooks are installed here (into a local mask dict, nothing written).
SFX = os.environ.get('MP_SFX', '')
if os.environ.get('MP_ASM', '1') == '1':
    import card_render as _CR
    import rb_capture as _RBC
    _RBC.install(R, A, R.FH, {}, 'p3' if any(k.startswith('p3') for k in kinds) else kinds[0].split('_')[0])
ROOM = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_%s_bare.png' % BG.CORP_ROOM.get(skin, 'bio')


def no_guns():
    og = R.FG.make_guns
    R.FG.make_guns = lambda f, k, w: (Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)), None)
    return og


def go(beat, frame=None, tag=None, hud_frame=None, arcs_skip=(), guns=True):
    og = None if guns else no_guns()
    R.SPLIT.clear()
    R.SPLIT['on'] = True
    try:
        im = R.render(beat, room=ROOM, frame=frame, tag=tag, hud_frame=hud_frame, arcs_skip=arcs_skip)
    finally:
        if og is not None:
            R.FG.make_guns = og
    below, above = R.SPLIT['below'].convert('RGB'), R.SPLIT['above']
    R.SPLIT.clear()
    return im, below, above


J = A.J
for kind in kinds:
    t = time.time()
    f1, f2 = copy.deepcopy(J['f1']), copy.deepcopy(J['f2'])
    allids1 = tuple(u['id'] for u in f1['units'])
    allids2 = tuple(u['id'] for u in f2['units'])
    if kind in ('p1', 'p2', 'p3'):
        res = go(kind)
    elif kind == 'p1_empty':
        f1['units'] = []
        res = go('p1', f1, 'mp_f1empty')
    elif kind == 'p1_noguns':
        res = go('p1', guns=False)
    elif kind == 'p1_hold':
        f1['schedule'] = [0, 2, 0]
        res = go('p1', f1, 'mp_f1hold')
    elif kind == 'p1_after':
        f1['units'] = [u for u in f1['units'] if u['dep'] != 0]
        res = go('p1', f1, 'mp_f1after', arcs_skip=allids1, guns=False)
    elif kind == 'p1_clean':
        f1['units'] = []
        res = go('p1', f1, 'mp_f1clean', arcs_skip=allids1, guns=False)
    elif kind in ('p3_pre', 'p3_mid'):
        f2['trace'] = 3 if kind == 'p3_pre' else 4
        f2['ram'] = 2
        f2['refunds'] = 0
        res = go('p3', f2, 'mp_' + kind)
    elif kind == 'p3_kill':
        f2['units'] = [u for u in f2['units'] if u['id'] != 2]
        f2['guns'] = [g for g in f2['guns'] if g['sector'] != 0]
        res = go('p3', f2, 'mp_p3kill', hud_frame=copy.deepcopy(J['f2']))
    elif kind == 'p3_after':
        f2['units'] = [u for u in f2['units'] if u['dep'] != 0]
        f2['refunds'] = 0
        res = go('p3', f2, 'mp_p3after', hud_frame=copy.deepcopy(J['f2']), arcs_skip=allids2, guns=False)
    elif kind == 'p3_clean':
        f2['units'] = []
        f2['refunds'] = 0
        res = go('p3', f2, 'mp_p3clean', hud_frame=copy.deepcopy(J['f2']), arcs_skip=allids2, guns=False)
    else:
        raise SystemExit('unknown kind ' + kind)
    im, below, above = res
    pre = ME + 'work/bases/%s_%s%s' % (skin, kind, SFX)
    im.save(pre + '_full.png')
    below.save(pre + '_below.png')
    above.save(pre + '_above.png')
    # the split must rebuild the plate exactly
    chk = below.convert('RGBA')
    chk.alpha_composite(above)
    d = np.abs(np.asarray(chk.convert('RGB'), np.int16) - np.asarray(im, np.int16)).max()
    print('ok', skin, kind, round(time.time() - t, 1), 's  split max diff', int(d), flush=True)
