"""disc_probe.py: around-the-halo luminance per card and the ratio against candidate disc inks"""
import sys
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/cards/src')
sys.dont_write_bytecode = True
import numpy as np
import card_render as C
CAND = ['FF3DA8', 'FF8AD0', '15121A', '1A1250', '2A1C8E', 'C81E78', 'FFD21F', 'F1EAD6', '7A2CFF', '0B1A14']
k = 2.0
for nm in (sys.argv[1:] or C.ORDER):
    card = C.draw_card(nm, int(176 * k), 'normal')
    arr = np.asarray(card.convert('RGB')).astype(np.float32) / 255.0
    mg = C.MARGIN
    cx, cy = (C.IC[0] + mg) * k, (C.IC[1] + mg) * k
    yy, xx = np.mgrid[0:arr.shape[0], 0:arr.shape[1]]
    rr = np.hypot(xx - cx, yy - cy) / k
    m = (rr >= 41) & (rr < 47) & (yy < (126 + mg) * k) & (yy > (10 + mg) * k) & (xx < (166 + mg) * k)
    around = arr[m].mean(0)
    la = C.lum(around)
    cur = C.ART[nm]['disc']
    s = ' '.join('%s:%.2f' % (c, C.ratio(C.hx(c), around)) for c in CAND)
    print('%-8s around_lum %.3f cur %s %.2f glyph %.2f | %s' % (nm, la, cur, C.ratio(C.hx(cur), around), C.ratio(C.WHITE, C.hx(cur)), s), flush=True)
