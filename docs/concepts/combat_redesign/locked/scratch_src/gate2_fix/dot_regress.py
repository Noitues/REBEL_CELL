"""dot_regress.py: dot_audit with the 2026-11-04 ridge rule (RIDGE_GAP 0.80) vs without it (the O-30 detector), on the first-pass plates
(which hold real bead rows), the O-30 / stage-2 published plates, synthetic dotted lines, and the rebuilt plates"""
import sys, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image, ImageDraw
import dot_audit as DA

LOCK = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/'
B = 'D:/rc_scratch/combat_redesign/locked/rebuild/board/'
files = sorted(glob.glob(LOCK + 'assembled/*.png')) + sorted(glob.glob(LOCK + 'corp/*.png'))[:4] + sorted(glob.glob(B + '*.png'))


def synth():
    out = []
    for r, gap, v, bg in ((2.0, 7, 200, 30), (3.0, 10, 160, 30), (1.6, 6, 120, 40), (2.5, 8, 90, 20), (2.0, 6, 230, 60)):
        im = Image.new('RGB', (400, 120), (bg, bg + 4, bg + 10))
        d = ImageDraw.Draw(im)
        for i in range(12):
            x = 40 + i * gap
            d.ellipse([x - r, 60 - r, x + r, 60 + r], fill=(v, v, v))
        out.append(('synthetic dots r%.1f gap %d v%d' % (r, gap, v), im))
    return out


diff = 0
for name, im in [(f.replace('\\', '/').split('/')[-2] + '/' + f.replace('\\', '/').split('/')[-1], Image.open(f)) for f in files] + synth():
    g0 = DA.RIDGE_GAP
    DA.RIDGE_GAP = 1e9
    old = DA.audit(im)['n_runs']
    DA.RIDGE_GAP = g0
    new = DA.audit(im)['n_runs']
    diff += old != new
    print('%-48s old %d  new %d%s' % (name, old, new, '   <-- changed' if old != new else ''))
print('plates changed:', diff)
