"""s0_dist.py: the hovered slot-0 card's distance to h02's landing marks (Z__arcs) and to r 455 / 459, for the rest pose and the upright
straight-up poses (print / drop under the card), against the resting Brace's own distance.  Read only.
python s0_dist.py -> prints a table, ../work/s0_dist.json"""
import sys, os, json
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
os.environ.setdefault('CORP', 'neutral')
import numpy as np
from scipy import ndimage as ndi
import lw_render as LW
import f1_hand as FH
import rb_capture as RBC
import rb_lift as RL
import card_render as CR

H, W = 1080, 1920
J = LW.R.A.J
z = np.load('D:/rc_scratch/combat_redesign/locked/round2/hover/chk/h02_brace.npz')
ARCS = np.unpackbits(z['Z__arcs'])[:H * W].reshape(H, W).astype(bool)
DIST = ndi.distance_transform_edt(~ARCS)
yy, xx = np.mgrid[0:H, 0:W]
rho = np.hypot(xx - 536, yy - 540)
hand = list(J['f1']['hand'])
sl = FH.slots(len(hand))
s0 = sl[0]
rest_im = FH.card_hi(hand[0], False)


def lift_im(po, do):
    CR.HOVER_PRINT_OFF[0], CR.HOVER_PRINT_OFF[1] = po
    CR.HOVER_DROP_OFF[0], CR.HOVER_DROP_OFF[1] = do
    FH._mem.clear()
    return FH.card_hi(hand[0], False, 'hover')


def stats(m):
    d = DIST[m]
    return dict(px=int(m.sum()), on_marks=int((d == 0).sum()), within1=int((d <= 1).sum()), within2=int((d <= 2).sum()), within3=int((d <= 3).sum()),
                min_dist=round(float(d.min()), 2), min_r=round(float(rho[m].min()), 2), lowest_y=int(np.nonzero(m.any(1))[0].max()))


out = {}
m = RBC._placed_alpha(rest_im, s0['cx'], s0['cy'], s0['ang'], FH.CARD_SCALE)
out['rest Brace (rest pose, rest image)'] = stats(m)
for pn, po in (('under', (0, 0)), ('right', (0, 9))):
    li = lift_im(po, po)
    m = RBC._placed_alpha(li, s0['cx'], s0['cy'], s0['ang'], RL.LIFT_ZOOM * FH.CARD_SCALE)
    out['hover image, rest pose, print %s' % pn] = stats(m)
    for cy in (900, 904, 905, 906, 908, 910, 913.9, 918, 922):
        m = RBC._placed_alpha(li, s0['cx'], cy, 0.0, RL.LIFT_ZOOM * FH.CARD_SCALE)
        out['hover image, upright cy %s, print %s' % (cy, pn)] = stats(m)
for k, v in out.items():
    print('%-48s %s' % (k, v), flush=True)
json.dump(out, open('D:/rc_scratch/combat_redesign/locked/round2/fix4/work/s0_dist.json', 'w'), indent=1)
