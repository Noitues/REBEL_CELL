"""probe_plates.py: independent probes on the PUBLISHED PNGs for the round-2 docs pass (CIE L* of sRGB luminance, dE76 in CIE Lab D65).
Reads only; prints.  usage: python probe_plates.py"""
import numpy as np
from PIL import Image

LOCK = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/'
CX, CY = 536, 540


def load(p):
    return np.asarray(Image.open(LOCK + p).convert('RGB')).astype(np.float64)


def lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lab(rgb):
    l = lin(rgb)
    M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = l @ M.T
    xyz = xyz / np.array([0.95047, 1.0, 1.08883])
    e = 216 / 24389
    k = 24389 / 27
    f = np.where(xyz > e, np.cbrt(xyz), (k * xyz + 16) / 116)
    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], -1)


def hexrgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float64)


def de(img_lab, h):
    t = lab(hexrgb(h)[None, None, :])[0, 0]
    return np.sqrt(((img_lab - t) ** 2).sum(-1))


def lstar(rgb):
    return lab(rgb)[..., 0]


def radius(shape):
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    return np.hypot(xx - CX, yy - CY)


# 1. the UNDO / SEND IT column: bbox of the bright button plates (L* >= 90) right of x 1550, below y 820
print('# 1. button column (bbox of L* >= 90 px, x >= 1550, y >= 820)')
for p in ('final/p1_decide.png', 'final/p2_preview.png', 'final/p2b_hover.png', 'final/p3_resolve.png', 'hover/h01_tower_turn.png',
          'hover/h02_brace.png', 'hover/h03_trigger.png', 'hover/h11_unit.png', 'backdrop/p1_bio.png'):
    im = load(p)
    L = lstar(im)
    # column profile of the SEND IT band (y 930-1000) and the UNDO band (y 860-890): the rightmost column whose mean L*
    # is at least half of the band's peak column mean is the plate's right edge
    out = []
    for (y0, y1) in ((930, 1000), (860, 890)):
        col = L[y0:y1, 1600:1920].mean(0)
        pk = col.max()
        xs = np.nonzero(col >= 0.5 * pk)[0]
        out.append('y %d-%d peak col L* %.1f right edge x %d' % (y0, y1, pk, 1600 + xs.max()))
    print('  %-28s %s' % (p, ' | '.join(out)))

# 2. FOCUS and the old lime on the plates with FOCUS
print('\n# 2. FOCUS #D4FF00 vs the old lime #96FE46 (px within dE76 8)')
for p in ('final/p2b_hover.png', 'final/p2b_hover_solace.png', 'final/p2b_hover_meridian.png', 'hover/h03_trigger.png', 'hover/h05_strike.png',
          'hover/h02_brace_solace.png', 'hover/h11_unit.png'):
    Lb = lab(load(p))
    f = de(Lb, '#D4FF00') < 8
    o = de(Lb, '#96FE46') < 8
    Lf = Lb[..., 0][f]
    print('  %-30s FOCUS px %5d (L* p50 %.1f p99 %.1f) | old lime px %d' % (p, f.sum(), np.median(Lf) if f.any() else -1,
                                                                        np.percentile(Lf, 99) if f.any() else -1, o.sum()))

# 3. Solace rim r 491-498: median colour, dE to GAIN and the hub HP green; Meridian and neutral for reference
print('\n# 3. rim band r 491-498, median sRGB and dE76')
for p in ('final/p1_decide.png', 'final/p1_decide_solace.png', 'final/p1_decide_meridian.png', 'final/p2_preview_solace.png'):
    im = load(p)
    r = radius(im.shape)
    band = (r >= 491) & (r <= 498)
    med = np.median(im[band], 0)
    ml = lab(med[None, None, :])[0, 0]
    g = lab(hexrgb('#7BE07B')[None, None, :])[0, 0]
    hp = lab(hexrgb('#7BD37B')[None, None, :])[0, 0]
    L = lstar(im)[band]
    print('  %-30s median #%02X%02X%02X L %.1f | dE GAIN %.1f | dE hub HP green %.1f | band mean L* %.1f' % (
        p, *[int(round(v)) for v in med], ml[0], np.sqrt(((ml - g) ** 2).sum()), np.sqrt(((ml - hp) ** 2).sum()), L.mean()))
    # share of band px that are 'green' (LCh hue 110-160, C > 20)
    lb = lab(im[band])
    C = np.hypot(lb[:, 1], lb[:, 2])
    h = np.degrees(np.arctan2(lb[:, 2], lb[:, 1])) % 360
    print('      band px %d, green-hue share (h 110-160, C>20) %.3f, teal share (h 170-210, C>10) %.3f' % (
        band.sum(), ((h > 110) & (h < 160) & (C > 20)).mean(), ((h > 170) & (h < 210) & (C > 10)).mean()))

# 4. pencil on board p2 / p2b and hover: PLAN-yellow wax px (dE < 30 of PLAN, L* >= 60)
print('\n# 4. PLAN wax px (dE76 < 30 of #FFE200)')
for p in ('final/p1_decide.png', 'final/p2_preview.png', 'final/p2b_hover.png', 'final/p3_resolve.png', 'hover/h04_twist.png'):
    Lb = lab(load(p))
    w = de(Lb, '#FFE200') < 30
    r = radius(Lb.shape)
    print('  %-28s wax px %6d | inside r480 %6d | r 480-500 %5d | outside r500 (x<1060) %d' % (
        p, w.sum(), (w & (r < 480)).sum(), (w & (r >= 480) & (r <= 500)).sum(), (w & (r > 500) & (np.mgrid[0:1080, 0:1920][1] < 1060)).sum()))

# 5. the reviewer's bright-blob holes: px at L* >= 95 inside r < 480 (SEND IT / HOT live outside the wheel or are classed)
print('\n# 5. very bright px inside r 480 (L* >= 95), and the bezel cube-disc box x 970-1000, y 555-585 p99')
for p in ('final/p1_decide.png', 'final/p2_preview.png', 'final/p3_resolve.png', 'final/p1_decide_solace.png'):
    im = load(p)
    L = lstar(im)
    r = radius(im.shape)
    print('  %-30s L*>=95 in r<480: %d px | L*>=98: %d | cube box p99 %.1f max %.1f' % (
        p, ((L >= 95) & (r < 480)).sum(), ((L >= 98) & (r < 480)).sum(), np.percentile(L[555:586, 970:1001], 99), L[555:586, 970:1001].max()))
