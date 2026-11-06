"""fan_view.py tag o0,o1,o2,o3 [lift_slot cy]: the hand alone (rb_lift.draw_hand's rest cards at REST_V, the lifted card on top) on a dark
canvas at the given per-slot x offsets from the unshifted fan (LEFT 1035, STEP 168), open 36 for the cards right of the lifted one.
-> ../crops/fan_<tag>.png (x 900-1720, y 740-1080, 1x)"""
import sys, os
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
os.environ.setdefault('CORP', 'neutral')
import numpy as np
from PIL import Image
import lw_render as LW
import f1_hand as FH
import rb_lift as RL
import card_render as CR
tag = sys.argv[1]
off = [float(v) for v in sys.argv[2].split(',')]
lift = int(sys.argv[3]) if len(sys.argv) > 3 else None
cy = float(sys.argv[4]) if len(sys.argv) > 4 else None
J = LW.R.A.J
hand = list(J['f1']['hand'])
n = len(hand)
sl = FH.slots(n)
for i, s in enumerate(sl):
    s['cx'] = RL.FAN0['left'] + i * RL.FAN0['step'] + off[i]
if lift is not None:
    for k in range(lift + 1, n):
        sl[k]['cx'] += RL.OPEN_PX
base = Image.new('RGBA', (1920, 1080), (20, 22, 30, 255))
for i, nm in enumerate(hand):
    if i == lift:
        continue
    ci = FH.card_hi(nm, False)
    a_ = np.asarray(ci).astype(np.float32)
    a_[..., :3] *= FH.REST_V
    FH.put(base, Image.fromarray(a_.astype(np.uint8), 'RGBA'), sl[i]['cx'], sl[i]['cy'], sl[i]['ang'], FH.CARD_SCALE)
if lift is not None:
    im = FH.card_hi(hand[lift], False, 'hover')
    FH.put(base, im, sl[lift]['cx'], cy, 0, RL.LIFT_ZOOM * FH.CARD_SCALE, shadow=True, **RL.LIFT_SHADOW)
out = 'D:/rc_scratch/combat_redesign/locked/round2/fix3/crops/fan_%s.png' % tag
base.convert('RGB').crop((900, 740, 1720, 1080)).save(out)
print(out, [round(s['cx'], 1) for s in sl])
