"""gate1: FOCUS corner pixels (dE76 < 10 of #D4FF00) that touch (8-neighbour) other coloured marks: BOSS_GOLD ward / Adjuster (dE < 25 of
#D69A1A or #F0BE46), K type / HP ticks (L* >= 75, C* < 12), HARM.  Per plate, with bbox of touching px.  usage: focus_touch.py <png> ..."""
import sys
import numpy as np
from scipy import ndimage as ndi
import glib as G
for f in sys.argv[1:]:
    rgb = G.load(f); lab = G.lab(rgb); L = lab[..., 0]; C = np.hypot(lab[..., 1], lab[..., 2])
    F = G.de(lab, '#D4FF00') < 10
    Fd = ndi.binary_dilation(F, structure=np.ones((3, 3)), iterations=1)
    out = []
    for nm, m in (('gold', (G.de(lab, '#D69A1A') < 25) | (G.de(lab, '#F0BE46') < 25)), ('neutral bright', (L >= 75) & (C < 12)),
                  ('harm', (G.de(lab, '#FF4433') < 25) | (G.de(lab, '#FF6452') < 25))):
        t = Fd & m & ~F
        ys, xs = np.nonzero(t)
        out.append('%s %d%s' % (nm, t.sum(), ' (x %d-%d y %d-%d)' % (xs.min(), xs.max(), ys.min(), ys.max()) if len(xs) else ''))
    print('%-40s FOCUS px %d | touching: %s' % (f.split('/')[-1], F.sum(), '; '.join(out)))
