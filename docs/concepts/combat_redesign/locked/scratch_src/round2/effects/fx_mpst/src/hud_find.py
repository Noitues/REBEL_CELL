"""hud_find.py: locate the HUD marks the S / L effects target on the published plates (TRACE pips, RAM coins, REFUND tab)."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'


def comps(mask, minpx=30):
    lab, n = ndi.label(mask)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) >= minpx:
            out.append((int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()), len(ys)))
    return sorted(out)


for nm in ('p1_decide', 'p2_preview', 'p3_resolve'):
    a = np.asarray(Image.open(FINAL + nm + '.png').convert('RGB'), np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    hud = np.zeros(r.shape, bool)
    hud[300:700, 1070:1900] = True
    vio = hud & (b > 180) & (r > 110) & (r < 200) & (g < 110)
    print(nm, 'violet pips', comps(vio))
    cy = hud & (b > 200) & (g > 180) & (r < 140)
    print(nm, 'cyan blobs', comps(cy, 60))
