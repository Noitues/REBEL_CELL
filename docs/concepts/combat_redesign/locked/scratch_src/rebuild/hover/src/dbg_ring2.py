"""why a hero ring does not fit: candidate rings against each forbidden part (labels, hero, YOU strip, bill frame)"""
import sys, os
sys.dont_write_bytecode = True
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
import hv_plates as P
import hv_core as V
import hv_comp as K

hand = ['Brace', 'Spin3', 'Trigger', 'Twist']
import sys as _s
f_live, f_plan = P.frames([('Spin3', 3)], hand)
K.reset_all()
bg = K.board('p1', f_plan, f_plan, P.ftag(f_plan, V.CORP), True)
Z, MASKS = V.Z, V.MASKS
xy = V.hud2.R.get('_hero_xy')
print('hero_xy', xy, 'room T/B', V.HERO_ROOM_T, V.HERO_ROOM_B)
bx = V.hud_box('bill')
print('bill', bx)
hm = MASKS['hud_hero']
parts = dict(labels=ndi.binary_dilation(MASKS['hud_labels'], iterations=1), hero=ndi.binary_dilation(hm, iterations=1),
             you=ndi.binary_dilation(V.YOU_MASK['you'], iterations=1))
inside = np.zeros((1080, 1920), bool)
inside[int(bx[1]) + 3:int(bx[3]) - 3, int(bx[0]) + 3:int(bx[2]) - 3] = True
parts['frame'] = ~inside
cy = xy['y']
lab = MASKS['hud_labels']
for key in ('lands', 'through'):
    x0, wd = xy[key]
    sub = hm[int(cy - 44):int(cy + 44), int(x0 - 4):int(x0 + wd + 4)]
    ys_, xs_ = np.nonzero(sub)
    box = (x0 - 4 + xs_.min(), cy - 44 + ys_.min(), x0 - 4 + xs_.max() + 1, cy - 44 + ys_.max() + 1)
    print(key, 'glyph box', box, 'size', box[2] - box[0], box[3] - box[1])
    col = lab[:, int(box[0]) - 14:int(box[2]) + 14]
    rows = np.nonzero(col.any(1))[0]
    above = rows[rows < box[1]]
    below = rows[rows > box[3]]
    print('  label rows above', above.max() if above.size else None, 'below', below.min() if below.size else None,
          'room above', box[1] - (above.max() + 2) if above.size else None, 'room below', (below.min() - 2) - box[3] if below.size else None)
    for n in V.RING_N:
        for ex in (2, 3, 4, 5, 7):
            rx, ry = V.ring_axes(*box, n, ex)
            pts = V.ring_pts((box[0] + box[2]) / 2, (box[1] + box[3]) / 2, rx, ry, 3, n=n)
            T_ = V.L2()
            V.wax_stroke(T_, pts, seed=3, cap=True)
            m = np.asarray(T_.done().split()[3]) >= 40
            ys, xs = np.nonzero(m)
            hits = {k: int((m & v).sum()) for k, v in parts.items() if (m & v).any()}
            print('   n', n, 'ex', ex, 'rx %.1f ry %.1f' % (rx, ry), 'ring y', ys.min(), ys.max(), 'x', xs.min(), xs.max(), 'hits', hits)
img = np.asarray(bg.convert('RGB')).copy()
for k, col in (('labels', (255, 0, 0)), ('hero', (0, 255, 0)), ('you', (0, 0, 255))):
    img[parts[k]] = col
Image.fromarray(img[60:340, 1060:1910]).save(V.HERE + 'dbg/ring_forbid.png')
