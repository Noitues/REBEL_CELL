import numpy as np
from PIL import Image
H = 'D:/rc_scratch/combat_redesign/locked/transitions_work/layers/'
F = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
for corp, pub in (('neutral', 'p1_decide.png'), ('solace', 'p1_decide_solace.png')):
    a = np.asarray(Image.open(H + corp + '_p1_real.png').convert('RGB')).astype(int)
    b = np.asarray(Image.open(F + pub).convert('RGB')).astype(int)
    d = np.abs(a - b).max(-1)
    ys, xs = np.nonzero(d > 8)
    print(corp, 'max', d.max(), 'px>8', len(ys), 'bbox', (xs.min(), ys.min(), xs.max(), ys.max()) if len(ys) else None)
    Image.fromarray((np.clip(d * 4, 0, 255)).astype(np.uint8)).save(H + corp + '_diff_pub.png')
