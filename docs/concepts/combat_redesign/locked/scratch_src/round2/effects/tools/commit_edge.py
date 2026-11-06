"""commit_edge.py <skin>: look only.  How far the p2 pencil footprint (ink edge, shadow) reaches past the yellow wax: for each distance d
from the kept yellow, the px that differ p2 vs p3 (max channel > 22) and are not in the burn mask, and their mean dE76 p2 vs p3."""
import sys, os
sys.dont_write_bytecode = True
MS = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_mpst/src/'
sys.path.insert(0, MS)
os.chdir(MS)
import numpy as np
from scipy import ndimage as ndi
import mp_eff as E
from mp_lib import *
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import rb_tokens as RT
skin = sys.argv[1] if len(sys.argv) > 1 else 'neutral'
s = E.FX['fx_commit']
box = s['_box']
a2, a3 = box.crop(E.below(skin, 'p2')), box.crop(E.below(skin, 'p3'))
marks, nd, endp, rest = E.commit_data(('c', skin), a2, a3, box, s['seed'])
h2, s2, v2 = E.hsv_np(a2)
yel = (h2 > 40) & (h2 < 66) & (s2 > 0.55) & (v2 > 0.55)
onb = (box.RHO > 205) & (box.RHO < 500)
m = yel & onb & (np.abs(a2 - a3).max(2) > 40)
dist = ndi.distance_transform_edt(~m)
de = np.linalg.norm(RT.lab(np.clip(a2, 0, 255).astype(np.float64)) - RT.lab(np.clip(a3, 0, 255).astype(np.float64)), axis=-1)
diff = np.abs(a2 - a3).max(2) > 22
for d in range(1, 13):
    ring = (dist > d - 1) & (dist <= d) & onb
    out = ring & ~marks & (de > 5)
    print('d %2d  ring px %6d  in marks %6d  outside marks with dE>5 %6d  mean dE %5.1f' % (d, int(ring.sum()), int((ring & marks).sum()), int(out.sum()),
          float(de[out].mean()) if out.any() else 0.0))
