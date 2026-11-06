"""measure_pub.py : L* (CIE) numbers measured on the PUBLISHED PNGs in locked/effects (for NOTES_CDHL.md)
  - the P-stock plate on fx_block_vs_break.png (block panel, colour): px within dE76 8 of #F6C8DE, their median L*, and the card bone's L*
  - the kill burst colour and the guard tokens: px within dE76 15 of FOCUS / lime on the D and H sheets' frame areas"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from fxk_lib import RT, P_STOCK, PINK, GAIN, FOCUS, LIME
PAPER = RT.NEUTRALS['PAPER']          # the card bone (rb_tokens #F2EEE4)
E = 'D:/rc_scratch/combat_redesign/locked/round2/effects/out/'


def lab(a):
    return RT.lab(np.asarray(a, np.float64))


def near(img, col, de):
    la = lab(np.asarray(img.convert('RGB')).astype(np.float64))
    d = np.linalg.norm(la - lab(np.array(col, np.float64)), axis=-1)
    return d < de, la


bvb = Image.open(E + 'fx_block_vs_break.png').convert('RGB')
W_, H_ = bvb.size
# the four top panels sit in the first ~600 px rows below the header; take the two colour panels (left half)
top = bvb.crop((0, 120, W_ // 2, 660))
m, la = near(top, P_STOCK, 8.0)
print('P stock #%02X%02X%02X: L* %.1f (token); on the published block|break panels: %d px, median L* %.1f' % (P_STOCK + (float(lab(np.array(P_STOCK, float))[0]), int(m.sum()), float(np.median(la[..., 0][m])) if m.any() else -1)))
print('card bone PAPER #%02X%02X%02X: L* %.1f; dE76 P stock vs card bone %.1f' % (PAPER + (float(lab(np.array(PAPER, float))[0]), float(np.linalg.norm(lab(np.array(P_STOCK, float)) - lab(np.array(PAPER, float)))))))
print('CELL_PINK L* %.1f, GAIN L* %.1f, FOCUS L* %.1f' % (lab(np.array(PINK, float))[0], lab(np.array(GAIN, float))[0], lab(np.array(FOCUS, float))[0]))
for sheet in ('fx_C_corp.png', 'fx_D_damage.png', 'fx_H_harm.png', 'fx_L_life.png', 'fx_block_vs_break.png'):
    im = Image.open(E + sheet).convert('RGB')
    a = np.asarray(im)
    la = lab(a.astype(np.float64))
    print('%-22s %dx%d  median L* %.1f  px >= L* 95: %d' % (sheet, im.width, im.height, float(np.median(la[..., 0])), int((la[..., 0] >= 95).sum())))
