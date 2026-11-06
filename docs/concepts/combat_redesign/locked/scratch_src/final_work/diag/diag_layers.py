"""which layer covers given screen points after the digits are drawn"""
import sys, os, inspect
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
os.chdir('D:/rc_scratch/combat_redesign/locked/corp/src')
sys.dont_write_bytecode = True
import lw_render as LW
import numpy as np
R = LW.R
from cv_lib import L2
PTS = [(536, 143), (536, 150), (536, 940), (536, 930), (530, 934)]
REC = []
_od = L2.done
def done(self, *a, **k):
    im = _od(self, *a, **k)
    fr = inspect.stack()[1]
    al = np.asarray(im.split()[3])
    REC.append((os.path.basename(fr.filename), fr.lineno, [int(al[y, x]) for x, y in PTS]))
    return im
L2.done = done
im = R.render('p1')
for r in REC:
    if any(v > 40 for v in r[2]):
        print(r)
