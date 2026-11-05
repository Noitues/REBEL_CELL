"""C14: what the old kglyph library does to the glyph registry.  Snapshot crests15.CUSTOM after the corp/src import, call
wr2_units.library() (what the consumed ghost does mid-render), and list every registry key it replaced; save the KA_twist mask before /
after side by side.  python c14_glyphs.py <outdir>"""
import sys, os
sys.dont_write_bytecode = True
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
os.environ.setdefault('CORP', 'solace')
import lw_render as LW  # noqa  (installs every patch, as a render does)
import crests15 as C15
import wr2_units as W2U
import numpy as np
from PIL import Image
before = dict(C15.CUSTOM)
m0 = {k: np.asarray(before[k]().convert('L').resize((128, 128))) for k in before if k.startswith('KA_')}
W2U.library()
after = dict(C15.CUSTOM)
changed = sorted(k for k in before if after.get(k) is not before[k])
added = sorted(k for k in after if k not in before)
print('replaced keys', len(changed), changed[:40])
print('added keys', len(added), added[:12], '...')
for k in sorted(m0):
    m1 = np.asarray(after[k]().convert('L').resize((128, 128)))
    d = np.abs(m1.astype(int) - m0[k].astype(int))
    print('%-14s mean abs diff %.1f  px > 64: %d' % (k, d.mean(), int((d > 64).sum())))
a = before['KA_twist']().convert('L').resize((256, 256))
b = after['KA_twist']().convert('L').resize((256, 256))
o = Image.new('L', (520, 256), 40)
o.paste(a, (0, 0))
o.paste(b, (264, 0))
o.save(OUT + '/ka_twist_master_vs_old.png')
print('saved', OUT + '/ka_twist_master_vs_old.png')
