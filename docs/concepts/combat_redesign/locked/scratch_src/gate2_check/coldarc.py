"""coldarc.py -- COLD landing-arc trims (arcT1 mask) vs their surroundings, per skin (review 1.4: COLD lost in the Meridian rings).
Fill = arcT1 pixels with L* > 45; surround = pixels 5-10 px outside the arcT1 mask (past the keyline); dE76 of the medians, luminance ratio,
and the nearest-corp-ink dE of the surround."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
WORK = 'D:/rc_scratch/combat_redesign/locked/corp/work/'


def to_lab(rgb):
    c = np.asarray(rgb, float) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    X = (0.4124 * c[..., 0] + 0.3576 * c[..., 1] + 0.1805 * c[..., 2]) / 0.95047
    Y = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    Z = (0.0193 * c[..., 0] + 0.1192 * c[..., 1] + 0.9505 * c[..., 2]) / 1.08883
    f = lambda t: np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
    return np.stack([116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))], -1), Y


for n, s in (('p1_decide', 'p1'), ('p1_decide_solace', 'p1_solace'), ('p1_decide_meridian', 'p1_meridian'), ('p2_preview_meridian', 'p2_meridian'),
             ('p3_resolve_meridian', 'p3_meridian'), ('p1_nowords_meridian', 'nowords_meridian')):
    rgb = np.asarray(Image.open(FINAL + n + '.png').convert('RGB')).astype(float)
    lab, Y = to_lab(rgb)
    z = np.load(WORK + 'masks_%s.npz' % s)
    get = lambda k: np.unpackbits(z[k])[:1080 * 1920].reshape(1080, 1920).astype(bool) if k in z.files else np.zeros((1080, 1920), bool)
    for cls in ('arcT1', 'chev1'):
        m = get(cls)
        fill = m & (lab[..., 0] > 45)
        sur = ndi.binary_dilation(m, iterations=10) & ~ndi.binary_dilation(m, iterations=5)
        others = np.zeros((1080, 1920), bool)
        for k in z.files:
            if k not in (cls, 'scrim', 'hud'):
                others |= get(k)
        sur &= ~others
        if fill.sum() < 30 or sur.sum() < 30:
            continue
        fm, sm = np.median(rgb[fill], 0), np.median(rgb[sur], 0)
        lf, yf = to_lab(fm)
        lsur, ysur = to_lab(sm)
        print('%-22s %-6s fill #%02X%02X%02X L* %.1f | surround #%02X%02X%02X L* %.1f | dE76 %.1f | lum ratio %.2f' % (
            n, cls, *fm.astype(int), lf[0], *sm.astype(int), lsur[0], float(np.linalg.norm(lf - lsur)), float(yf / max(ysur, 1e-4))))
