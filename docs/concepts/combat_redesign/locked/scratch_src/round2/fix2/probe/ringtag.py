"""the ring-tag boxes on a board plate: per tag component (asm_render 'tags' mask), its bbox, the box line L* (the px of the box's line band:
from 1 to 5 px inside the component's outer edge, L* > 40, i.e. the line, not the dark fill) p50 / p95 / max, and the type's p99
python ringtag.py <plate.png> <masks.npz>"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/round2/gate1')
import glib as G
H, W = 1080, 1920
rgb = G.load(sys.argv[1])
L = G.Lstar(rgb)
z = np.load(sys.argv[2])
m = np.unpackbits(z['tags'])[:H * W].reshape(H, W).astype(bool)
lab, n = ndi.label(ndi.binary_closing(m, iterations=2))
for i, sl in enumerate(ndi.find_objects(lab)):
    c = lab == i + 1
    if c.sum() < 300:
        continue
    x0, x1, y0, y1 = sl[1].start, sl[1].stop, sl[0].start, sl[0].stop
    if x0 > 1000:
        continue                                   # the board's ring tags only (left of the HUD)
    filled = ndi.binary_fill_holes(c)
    inner = ndi.binary_erosion(filled, iterations=5)
    band = filled & ~inner & ~ndi.binary_erosion(filled, iterations=1) | (filled & ~ndi.binary_erosion(filled, iterations=1))
    band = filled & ~inner
    line = band & (L > 40)
    core = inner & (L > 40)
    print('tag box x%d-%d y%d-%d: line px %d L* p50 %.1f p95 %.1f max %.1f | inside (type) px %d p99 %.1f' % (
        x0, x1, y0, y1, line.sum(), np.percentile(L[line], 50) if line.any() else -1, np.percentile(L[line], 95) if line.any() else -1,
        L[line].max() if line.any() else -1, core.sum(), np.percentile(L[core], 99) if core.any() else -1))
