"""chk_bases.py: compare fresh base plates with the published final plates (same beat) and with the old bases."""
import os, sys
import numpy as np
from PIL import Image
FIN = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
B = 'D:/rc_scratch/combat_redesign/locked/fx_o30b/'
OLD = 'D:/rc_scratch/combat_redesign/locked/'
pairs = [
    (B + 'cdhl/work/base_neutral_p3.png', FIN + 'p3_resolve.png'),
    (B + 'mpst/work/base_solace_p2.png', None),
    (B + 'mpst/work/base_meridian_p2.png', None),
]
def L(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)
def st(a, b):
    d = np.abs(a - b).max(-1)
    return 'max %d  px>8 %d  mean %.3f' % (d.max(), int((d > 8).sum()), d.mean())
for p, ref in pairs:
    if not os.path.exists(p):
        print('missing', p); continue
    a = L(p)
    if ref:
        print(os.path.basename(p), 'vs final', st(a, L(ref)))
    oldp = p.replace(B + 'cdhl/', OLD + 'fx_cdhl/').replace(B + 'mpst/', OLD + 'fx_mpst/')
    if os.path.exists(oldp):
        print(os.path.basename(p), 'vs old base', st(a, L(oldp)))
    # room zone mean luma (right of board)
    z = a[200:900, 1150:1900].astype(float) / 255
    print('  room zone mean luma %.3f' % (0.2126 * z[..., 0] + 0.7152 * z[..., 1] + 0.0722 * z[..., 2]).mean())
