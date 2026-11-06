"""cards_quick.py out.jpg [scale]: one row of 11 normal cards + played row, on the bio cutaway grey, plus icon numbers"""
import sys, os
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/cards/src')
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
import card_render as C
out = sys.argv[1]
s = float(sys.argv[2]) if len(sys.argv) > 2 else 1.15
w = int(round(176 * s * 1.5))
cells = []
for nm in C.ORDER:
    cells.append((C.draw_card(nm, w, 'normal'), C.draw_card(nm, w, 'played'), C.draw_card(nm, w, 'nowords')))
cw, ch = cells[0][0].size
im = Image.new('RGBA', (cw * 11, ch * 3), (34, 38, 48, 255))
for i, (a, b, c) in enumerate(cells):
    im.alpha_composite(a, (i * cw, 0)); im.alpha_composite(b, (i * cw, ch)); im.alpha_composite(c, (i * cw, 2 * ch))
im.convert('RGB').save(out, quality=90)
r = C.ratio
for nm in (C.ORDER if '--checks' in sys.argv else []):
    A = C.ART[nm]
    card = C.draw_card(nm, 176 * 4, 'normal')
    arr = np.asarray(card.convert('RGB')).astype(np.float32) / 255.0
    mg = C.MARGIN; k = 4.0
    cx, cy = (C.IC[0] + mg) * k, (C.IC[1] + mg) * k
    yy, xx = np.mgrid[0:arr.shape[0], 0:arr.shape[1]]
    rr = np.hypot(xx - cx, yy - cy) / k
    m = (rr >= 41) & (rr < 47) & (yy < (126 + mg) * k) & (yy > (10 + mg) * k) & (xx < (166 + mg) * k)
    around = arr[m].mean(0)
    print(nm, 'disc_vs_around %.2f glyph_vs_disc %.2f' % (r(C.hx(A['disc']), around), r(C.WHITE, C.hx(A['disc']))))
for k_, v in C.TYPES.items():
    print(k_, 'text/plate %.2f plate/paper %.2f' % (r(v['text'], v['col']), r(v['col'], C.CREAM)))
