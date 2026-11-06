"""arcs_view.py: h02's landing-marks mask (Z__arcs) over the published h02 plate near the slot-0 card, with the resting Brace outline and
the upright lifted Brace at a given cy (print under): 3x crop -> ../crops/arcs_view_<cy>.png.  Read only.
python arcs_view.py <cy>"""
import sys, os
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
os.environ.setdefault('CORP', 'neutral')
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import lw_render as LW
import f1_hand as FH
import rb_capture as RBC
import rb_lift as RL
import card_render as CR

H, W = 1080, 1920
cy = float(sys.argv[1])
J = LW.R.A.J
z = np.load('D:/rc_scratch/combat_redesign/locked/round2/hover/chk/h02_brace.npz')
ARCS = np.unpackbits(z['Z__arcs'])[:H * W].reshape(H, W).astype(bool)
pub = np.asarray(Image.open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/hover/h02_brace.png').convert('RGB')).astype(np.float32)
hand = list(J['f1']['hand'])
s0 = FH.slots(len(hand))[0]
rest = RBC._placed_alpha(FH.card_hi(hand[0], False), s0['cx'], s0['cy'], s0['ang'], FH.CARD_SCALE)
CR.HOVER_PRINT_OFF[0], CR.HOVER_PRINT_OFF[1] = (0, 0)
CR.HOVER_DROP_OFF[0], CR.HOVER_DROP_OFF[1] = (0, 0)
FH._mem.clear()
lift = RBC._placed_alpha(FH.card_hi(hand[0], False, 'hover'), s0['cx'], cy, 0.0, RL.LIFT_ZOOM * FH.CARD_SCALE)
img = pub * 0.55
img[ARCS] = [255, 0, 255]
ed_r = rest & ~ndi.binary_erosion(rest)
ed_l = lift & ~ndi.binary_erosion(lift)
img[ed_r] = [0, 255, 255]
img[ed_l] = [255, 255, 0]
x0, y0, x1, y1 = 860, 700, 1180, 900
c = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).crop((x0, y0, x1, y1)).resize(((x1 - x0) * 3, (y1 - y0) * 3), Image.NEAREST)
fp = 'D:/rc_scratch/combat_redesign/locked/round2/fix4/crops/arcs_view_%d.png' % int(cy)
c.save(fp)
print(fp, 'arcs px in crop', int(ARCS[y0:y1, x0:x1].sum()))
