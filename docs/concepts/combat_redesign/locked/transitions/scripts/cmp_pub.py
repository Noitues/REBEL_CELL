"""cmp_pub.py: compare the staged compose with the published plate (per skin); prints max / mean / px over 2 and 8, and where."""
import sys
import numpy as np
from PIL import Image
HERE = 'D:/rc_scratch/combat_redesign/locked/rebuild/transitions/'
FIN = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
for corp, pub in (('neutral', 'p1_decide.png'), ('solace', 'p1_decide_solace.png')):
    a = np.asarray(Image.open(HERE + 'layers/%s_p1_compose.png' % corp).convert('RGB')).astype(int)
    b = np.asarray(Image.open(FIN + pub).convert('RGB')).astype(int)
    d = np.abs(a - b).max(-1)
    ys, xs = np.nonzero(d > 8)
    box = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if len(xs) else None
    print(corp, 'max', int(d.max()), 'mean', round(float(np.abs(a - b).mean()), 4), 'px>2', int((d > 2).sum()), 'px>8', int((d > 8).sum()), 'box>8', box)
