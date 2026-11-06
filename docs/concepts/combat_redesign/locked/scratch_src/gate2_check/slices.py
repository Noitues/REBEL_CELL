"""slices.py -- tower slice ink L* on the published plates (independent of the capture masks).

Slice k is centred on 60*k deg (clockwise from up).  Region: r 72-186, |angle - centre| <= 25 deg, minus the icon disc (r <= 48 around the
disc centre, found as the brightest 48 px disc along the slice axis).  Pixels are classed by nearest colour: ink (the slice's ink hex),
texture (its texture hex), or other (hatch, pips, paper sliver, keyline).  Reports the L* of the ink pixels (median, L* of mean luminance),
the ink share, and the whole-region mean L* (L* of mean luminance) with the icon disc cut."""
import sys
import numpy as np
from PIL import Image

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
C = (536, 540)
hx = lambda s: np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], float)
INK = {'BURST': hx('F06EAE'), 'SHIELD': hx('5E9BE0'), 'TURRET': hx('AEB24E'), 'REPAIR': hx('3FB59A')}
TEX = {'BURST': hx('9E2A66'), 'SHIELD': hx('234E8C'), 'TURRET': hx('5A5E1A'), 'REPAIR': hx('1D6656')}
ORDER = ['BURST', 'SHIELD', 'TURRET', 'SHIELD', 'BURST', 'REPAIR']   # slice 0 at the top, clockwise (from the plates)


def srgb_lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_lab(rgb):
    c = srgb_lin(np.asarray(rgb, float))
    X = (0.4124 * c[..., 0] + 0.3576 * c[..., 1] + 0.1805 * c[..., 2]) / 0.95047
    Y = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    Z = (0.0193 * c[..., 0] + 0.1192 * c[..., 1] + 0.9505 * c[..., 2]) / 1.08883
    f = lambda t: np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
    return np.stack([116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))], -1), Y


def lstar(y):
    y = np.asarray(y, float)
    return np.where(y > 0.008856, 116 * np.cbrt(y) - 16, 903.3 * y)


yy, xx = np.mgrid[0:1080, 0:1920]
RHO = np.hypot(xx - C[0], yy - C[1])
ANG = (np.degrees(np.arctan2(xx - C[0], -(yy - C[1]))) + 360) % 360
for k, v in INK.items():
    lab, Y = to_lab(v)
    print('token ink %-7s L* %.1f   texture L* %.1f' % (k, lab[0], to_lab(TEX[k])[0][0]))
plates = sys.argv[1:] or ['p1_decide', 'p2_preview', 'p2b_hover', 'p3_resolve', 'p1_nowords', 'p1_decide_solace', 'p1_decide_meridian',
                          'p2_preview_solace', 'p2_preview_meridian', 'p2b_hover_solace', 'p2b_hover_meridian', 'p3_resolve_solace', 'p3_resolve_meridian',
                          'p1_nowords_solace', 'p1_nowords_meridian']
for name in plates:
    rgb = np.asarray(Image.open(FINAL + name + '.png').convert('RGB')).astype(float)
    lab, Y = to_lab(rgb)
    Ls = lab[..., 0]
    print('==', name)
    allink = []
    for s in range(6):
        typ = ORDER[s]
        a = (ANG - 60 * s + 180) % 360 - 180
        reg = (RHO >= 72) & (RHO <= 186) & (np.abs(a) <= 25)
        # icon disc: brightest mean along the axis, r 100-140
        best = None
        for rr in range(96, 146, 2):
            cx = C[0] + rr * np.sin(np.radians(60 * s))
            cy = C[1] - rr * np.cos(np.radians(60 * s))
            m = np.hypot(xx - cx, yy - cy) <= 30
            v = float(Ls[m].mean())
            if best is None or v > best[0]:
                best = (v, rr, cx, cy)
        _, rr, cx, cy = best
        reg &= np.hypot(xx - cx, yy - cy) > 48
        lab_ink = to_lab(INK[typ])[0]
        lab_tex = to_lab(TEX[typ])[0]
        d_ink = np.linalg.norm(lab - lab_ink, axis=-1)
        d_tex = np.linalg.norm(lab - lab_tex, axis=-1)
        ink = reg & (d_ink < 20) & (d_ink <= d_tex)
        tex = reg & (d_tex < 20) & (d_tex < d_ink)
        n = reg.sum()
        print('  s%d %-7s icon r %3d  ink share %4.0f%%  ink median L* %5.1f  ink mean L* %5.1f | texture share %4.0f%% | region mean L* %5.1f  region p95 %5.1f' % (
            s, typ, rr, 100 * ink.sum() / n, float(np.median(Ls[ink])) if ink.any() else -1, float(lstar(Y[ink].mean())) if ink.any() else -1,
            100 * tex.sum() / n, float(lstar(Y[reg].mean())), float(np.percentile(Ls[reg], 95))))
