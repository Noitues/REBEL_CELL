"""prep_refund.py : the refund pre-state base 'p3rf' per skin (pure image edit of the rendered p3 layers, no generator call).
below = p3 below (the wheel keeps its refund coin at the kill); above = p3 above with the refunded RAM coin replaced by an empty slot (the
4th slot, shifted 32 px left) and the REFUND tab with its hairline removed (they appear when the coin lands)."""
import sys
import numpy as np
from PIL import Image
W = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_cdhl/work/'
SLOT_DX = 32                      # RAM slot pitch on the rebuilt HUD (coins at x 1155, 1187, 1219, 1251)
DY = 33                           # round 2 (C8 HUD rows): the p3 RAM row sits 33 px lower (coin centres y 645.5, were 612.5)
DST = (1205, 590 + DY, 1240, 636 + DY)      # the refunded coin and its rays
LEFT = (1202, 588 + DY, 1205, 640 + DY)     # the left ray tips: filled from plate background right of the 4th slot
LEFT_SRC_X = 1268
EDGES = ((1213, 585 + DY, 1227, 592 + DY), (1213, 633 + DY, 1227, 640 + DY))     # the top ray tip on the plate edge, the hairline joint on the bottom edge
EDGE_DX = 72
TAB = (1158, 640 + DY, 1284, 682 + DY)      # the hairline and the REFUND tab (96 px in round 2), hung under the RAM plate
for skin in sys.argv[1:] or ['neutral', 'solace', 'meridian']:
    b = Image.open(W + 'base_%s_p3_below.png' % skin)
    a = np.asarray(Image.open(W + 'base_%s_p3_above.png' % skin).convert('RGBA')).copy()
    x0, y0, x1, y1 = DST
    a[y0:y1, x0:x1] = a[y0:y1, x0 + SLOT_DX:x1 + SLOT_DX]
    x0, y0, x1, y1 = LEFT
    a[y0:y1, x0:x1] = a[y0:y1, LEFT_SRC_X:LEFT_SRC_X + (x1 - x0)]
    for x0, y0, x1, y1 in EDGES:
        a[y0:y1, x0:x1] = a[y0:y1, x0 + EDGE_DX:x1 + EDGE_DX]
    x0, y0, x1, y1 = TAB
    a[y0:y1, x0:x1] = 0
    b.save(W + 'base_%s_p3rf_below.png' % skin)
    Image.fromarray(a, 'RGBA').save(W + 'base_%s_p3rf_above.png' % skin)
    full = np.asarray(b.convert('RGB')).astype(np.float32)
    al = a[:, :, 3:4] / 255.0
    Image.fromarray((full * (1 - al) + a[:, :, :3] * al).astype(np.uint8), 'RGB').save(W + 'base_%s_p3rf.png' % skin)
    print('ok', skin)
