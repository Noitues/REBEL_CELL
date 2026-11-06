"""trig_layers.py : the Trigger route on its own layer, as pencil (yellow, the plan) and as paint (pink, resolved).
a_plan.trigger_path draws with a_plan's own module-level YEL (from a_kit), so that name is swapped too
(base_render.py swapped only a2_plan.YEL and wr2_units.PLAN, which left the 'pink' layer yellow)."""
import sys, os
os.environ['CORP'] = 'neutral'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_env as GE
R, A = GE.R, GE.A
# round 2 (C1): the yellow layer is the board's one pencil (rb_pencil, installed by rb4_patch: 7 px wax, 3 px ink edge, wax grain), drawn
# through the published p2 plate's own hooks (rb_capture wraps a_plan.trigger_path), so it is the p2 plate's pencil to the pixel
sys.path.insert(1, 'D:/rc_scratch/combat_redesign/locked/round2/effects/tools')
import asm_hooks as _AH
_AH.install(R, A, 'p2')
import numpy as np
from PIL import Image
import wr2_units as W2U, a_plan as PL, a2_plan as P2
OUTD = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_cdhl/work/'
fr = A.J['f2']
for col, nm in (((255, 226, 0), 'yel'), ((255, 61, 168), 'pink')):
    old = (P2.YEL, W2U.PLAN, PL.YEL)
    P2.YEL, W2U.PLAN, PL.YEL = col, col, col
    L = R.L2()
    for tr in A.J['trigs']:
        PL.trigger_path(L, fr, dict(tr, entries=[e for e in tr['entries'] if e[0] != 'refund']), 'A')
    im = L.done()
    P2.YEL, W2U.PLAN, PL.YEL = old
    im.save(OUTD + 'trig_%s.png' % nm)
    a = np.asarray(im.convert('RGBA')).astype(int)
    m = a[..., 3] > 128
    print(nm, 'px', int(m.sum()), 'mean rgb', [round(float(a[..., c][m].mean()), 1) for c in range(3)], flush=True)
