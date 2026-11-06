"""prep_refund.py : the refund pre-state base 'p3rf' per skin (pure image edit of the rendered p3 layers, no generator call).
below = p3 below (the wheel keeps its refund coin at the kill); above = p3 above with the refunded RAM coin replaced by an empty slot (the
4th slot, shifted 32 px left) and the REFUND tab with its hairline removed (they appear when the coin lands)."""
import sys
import numpy as np
from PIL import Image
W = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_cdhl/work/'
SLOT_DX = 32                      # RAM slot pitch on the rebuilt HUD (coins at x 1155, 1187, 1219, 1251)
DST = (1205, 590, 1240, 636)      # the refunded coin and its rays
LEFT = (1202, 588, 1205, 640)     # the left ray tips: filled from plate background right of the 4th slot
LEFT_SRC_X = 1268
EDGES = ((1213, 585, 1227, 592), (1213, 633, 1227, 640))     # the top ray tip on the plate edge, the hairline joint on the bottom edge
EDGE_DX = 72
TAB = (1158, 640, 1284, 682)      # the hairline and the REFUND tab, hung under the RAM plate
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
