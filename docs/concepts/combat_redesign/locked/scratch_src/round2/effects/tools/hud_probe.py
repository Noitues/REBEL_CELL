"""hud_probe.py: where the HUD marks the effects use sit on the round-1 and the round-2 plates (published PNGs).
RAM coins (NET_CYAN discs), TRACE pips (TRACE_VIOLET squares), the REFUND tab (its keyline box), the YOU strip's hatched HARM segments."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import rb_tokens as RT
FIN = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
R1 = 'D:/rc_scratch/combat_redesign/locked/round2/effects/work/r1/'


def blobs(m, minpx=20):
    lab, n = ndi.label(m)
    out = []
    for i, sl in enumerate(ndi.find_objects(lab)):
        k = int((lab[sl] == i + 1).sum())
        if k >= minpx:
            ys, xs = np.nonzero(lab[sl] == i + 1)
            out.append((round(float(xs.mean() + sl[1].start), 1), round(float(ys.mean() + sl[0].start), 1), sl[1].start, sl[0].start, sl[1].stop, sl[0].stop, k))
    return sorted(out, key=lambda b: (b[1] // 20, b[0]))


def near(a, col, tol):
    lab = RT.lab(a.astype(np.float64))
    return np.linalg.norm(lab - RT.lab(np.array(col, np.float64)), axis=2) < tol


for tag, d in (('r1', R1), ('r2', FIN)):
    for p in ('p1_decide', 'p2_preview', 'p3_resolve'):
        a = np.asarray(Image.open(d + p + '.png').convert('RGB')).astype(np.float64)
        hud = np.zeros(a.shape[:2], bool)
        hud[:, 1060:] = True
        hud[740:, :] = False
        cy = near(a, RT.TOKENS['NET_CYAN'], 12) & hud
        vi = near(a, RT.TOKENS.get('TRACE_VIOLET', (160, 60, 255)), 18) & hud
        hr = (a[..., 0] > 180) & (a[..., 1] < 120) & (a[..., 2] < 110)
        hr[:, :1070] = False
        hr[180:, :] = False
        hr[:90, :] = False
        print('==', tag, p)
        print('  cyan discs', [b for b in blobs(cy, 60) if b[1] > 380][:8])
        print('  violet', [b[:2] + (b[6],) for b in blobs(vi, 40)][:8])
        yb = blobs(hr, 20)
        print('  YOU harm segs', [(b[2], b[3], b[4], b[5]) for b in yb][:8])
