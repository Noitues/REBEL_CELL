"""bd2_hues.py <room> : hue histogram of the saturated, lit pixels inside the room box of a bare render (for the corp light window)"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/backdrop/src')
import numpy as np
import bd2_lib as L
import bd_grade as BG

room = sys.argv[1]
a = L.bare(room) / 255.0
poly = [[1195, 488], [1465, 338], [1792, 523], [1792, 672], [1512, 808], [1195, 632]]
inside = BG.poly_sdf(poly) < 0
h = BG.hue(a)
mx, mn = a.max(-1), a.min(-1)
S = (mx - mn) / np.maximum(mx, 1e-4)
sel = inside & (S > 0.25) & (mx > 0.25)
hist, edges = np.histogram(h[sel], bins=36, range=(0, 360))
tot = sel.sum()
for i, c in enumerate(hist):
    if c > tot * 0.01:
        print('%3d-%3d  %5.1f %%  %s' % (edges[i], edges[i + 1], 100 * c / tot, '#' * int(60 * c / tot)))
print('share of box px saturated+lit', round(float(sel.sum() / inside.sum()), 3))
