"""C14 repro (round 2): render p3 <skin> alone, then p1_clean (f1 with no units, no gun marks, no arcs), then p3 <skin> again, in ONE process,
and report the pixel difference.  Also traces the glyph registry entry KA_twist (crests15.CUSTOM) and the old cards library load
(wr2_units._LIB) after each render.
python c14_order.py <skin> <outdir> [order]      order: comma list of p3,p1_clean (default p3,p1_clean,p3)"""
import sys, os, copy, time
sys.dont_write_bytecode = True
skin = sys.argv[1]
OUT = sys.argv[2]
order = (sys.argv[3] if len(sys.argv) > 3 else 'p3,p1_clean,p3').split(',')
os.environ['CORP'] = skin
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
os.makedirs(OUT, exist_ok=True)
CW = OUT + '/tower_cache/'
os.makedirs(CW, exist_ok=True)
import lw_render as LW
import bd_grade as BG
import numpy as np
from PIL import Image
R = LW.R
R.WORK = CW
A = R.A
import card_render as _CR  # noqa
import rb_capture as RBC
RBC.install(R, A, R.FH, {}, 'p3')
import crests15
import wr2_units as W2U
ROOM = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_%s_bare.png' % BG.CORP_ROOM.get(skin, 'bio')


def trace(tag):
    f = crests15.CUSTOM.get('KA_twist')
    print(tag, 'KA_twist fn', getattr(f, '__module__', None), getattr(f, '__qualname__', None), id(f), 'old lib loaded', 'k' in W2U._LIB, flush=True)


trace('start')
J = A.J
ims = []
for i, kind in enumerate(order):
    t = time.time()
    if kind == 'p3':
        im = R.render('p3', room=ROOM)
    elif kind == 'p1_clean':
        f1 = copy.deepcopy(J['f1'])
        ids = tuple(u['id'] for u in f1['units'])
        f1['units'] = []
        og = R.FG.make_guns
        R.FG.make_guns = lambda f, k, w: (Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)), None)
        try:
            im = R.render('p1', room=ROOM, frame=f1, tag='r2_f1clean', arcs_skip=ids)
        finally:
            R.FG.make_guns = og
    else:
        raise SystemExit('kind ' + kind)
    im.save(OUT + '/%d_%s_%s.png' % (i, kind, skin))
    trace('after %d %s %.0fs' % (i, kind, time.time() - t))
    if kind == 'p3':
        ims.append((i, np.asarray(im.convert('RGB'), np.int16)))
if len(ims) >= 2:
    a, b = ims[0][1], ims[-1][1]
    d = np.abs(a - b).max(axis=2)
    ys, xs = np.nonzero(d)
    print('p3 vs p3 after: max diff', int(d.max()), 'px differing', int((d > 0).sum()),
          'bbox', (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if len(xs) else None, flush=True)
