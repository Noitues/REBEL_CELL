"""hot_strokes (round 2, C11): per connected HOT core stroke on a published board plate: px, medial width, box.
python hot_strokes.py <plate name> <sfx>"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import rb_checks as RC
import rb_checks_r2 as R2
import rb_tokens as T

nm, sfx = sys.argv[1], sys.argv[2]
rgb = np.asarray(Image.open('D:/rc_scratch/combat_redesign/locked/rebuild/board/%s.png' % nm).convert('RGB')).astype(np.float64)
M = RC.load_masks(sfx)
hot = R2._get(M, 'chev0') | R2._get(M, 'arcT0')
hot &= ~R2.over_marks(M)
lab = T.lab(rgb)
core = hot & (np.linalg.norm(lab - T.lab(np.array(T.HOT_CORE, np.float64)), axis=-1) < 14)
lab_, n = ndi.label(core)
objs = ndi.find_objects(lab_)
rows = []
for i in range(1, n + 1):
    m = lab_ == i
    if m.sum() < 8:
        continue
    sl = objs[i - 1]
    w = R2._width(m)
    inc = 'chev0' if (m & R2._get(M, 'chev0')).any() else 'arcT0'
    rows.append((w, int(m.sum()), inc, [sl[1].start, sl[0].start, sl[1].stop - 1, sl[0].stop - 1]))
for r in sorted(rows, key=lambda r: (r[0] or 0)):
    print(r)
