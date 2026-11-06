"""cmp_pub.py <skin> <kind> ...: compare a base render (_full) with the published final/ plate of the same beat."""
import sys
import numpy as np
from PIL import Image
ME = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/'
FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
PUB = {'p1': 'p1_decide', 'p2': 'p2_preview', 'p3': 'p3_resolve', 'p2b': 'p2b_hover', 'nowords': 'p1_nowords'}
skin = sys.argv[1]
for kind in sys.argv[2:]:
    a = np.asarray(Image.open(ME + 'work/bases/%s_%s_full.png' % (skin, kind)).convert('RGB'), np.int16)
    b = np.asarray(Image.open(FINAL + PUB[kind] + ('' if skin == 'neutral' else '_' + skin) + '.png').convert('RGB'), np.int16)
    d = np.abs(a - b).max(2)
    print(skin, kind, 'max', int(d.max()), 'px>2', int((d > 2).sum()), 'px>8', int((d > 8).sum()))
    if (d > 8).any():
        ys, xs = np.nonzero(d > 8)
        print('   bbox', xs.min(), ys.min(), xs.max(), ys.max())
