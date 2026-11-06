"""hand-drawn icon set (white silhouette + ink outline) for the slices and the cards.  Each icon is built as a mask in unit space
then wobbled and inked by the Canvas.  unit space: [-1, 1], y down."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from sg_lib import *


def _tf(pts, c, sc, rot=0.0):
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    return [(c[0] + (x * ca - y * sa) * sc, c[1] + (x * sa + y * ca) * sc) for x, y in pts]


def _rocket(tilt=0.0, off=(0, 0), k=1.0):
    nose = [(0, -1.0), (0.14, -0.78), (0.2, -0.45), (0.2, 0.4), (-0.2, 0.4), (-0.2, -0.45), (-0.14, -0.78)]
    finl = [(-0.2, 0.0), (-0.48, 0.66), (-0.2, 0.5)]
    finr = [(0.2, 0.0), (0.48, 0.66), (0.2, 0.5)]
    noz = [(-0.14, 0.4), (-0.1, 0.58), (0.1, 0.58), (0.14, 0.4)]
    polys = [nose, finl, finr, noz]
    out = []
    for p in polys:
        out.append(_tf([(x * k + off[0], y * k + off[1]) for x, y in p], (0, 0), 1.0, tilt))
    return out


def _rocket_det(tilt, off, k):
    def T(pts):
        return _tf([(x * k + off[0], y * k + off[1]) for x, y in pts], (0, 0), 1.0, tilt)
    win = [(0.1 * math.cos(math.radians(a)), -0.28 + 0.1 * math.sin(math.radians(a))) for a in np.linspace(0, 360, 14)]
    return [T([(-0.2, -0.02), (0.2, -0.02)]), T(win), T([(-0.07, 0.66), (-0.1, 0.98)]), T([(0.0, 0.66), (0.0, 1.12)]), T([(0.07, 0.66), (0.1, 0.98)])]


def icon_polys(name):
    """list of polygons in unit space (white silhouette), plus ink detail strokes [(pts...)]"""
    if name == 'BURST':
        polys = _rocket(32, (-0.5, 0.0), 0.86) + _rocket(32, (0.5, 0.0), 0.86)
        return polys, _rocket_det(32, (-0.5, 0.0), 0.86) + _rocket_det(32, (0.5, 0.0), 0.86)
    if name == 'TURRET':
        polys = _rocket(32, (0.0, 0.0), 1.05)
        return polys, _rocket_det(32, (0.0, 0.0), 1.05)
    if name == 'SHIELD':
        top = [(-0.85, -0.9), (0.0, -1.0), (0.85, -0.9), (0.85, 0.05)]
        curve = [(0.85 * math.cos(math.radians(a)), 0.05 + 0.95 * math.sin(math.radians(a))) for a in np.linspace(0, 90, 10)]
        curve += [(-0.85 * math.cos(math.radians(a)), 0.05 + 0.95 * math.sin(math.radians(a))) for a in np.linspace(90, 0, 10)]
        poly = top + curve + [(-0.85, 0.05)]
        return [poly], [[(0, -0.97), (0, 0.98)]]
    if name == 'REPAIR':
        cap = []
        for a in np.linspace(-90, 90, 12):
            cap.append((0.78 + 0.34 * math.cos(math.radians(a)), 0.34 * math.sin(math.radians(a))))
        for a in np.linspace(90, 270, 12):
            cap.append((-0.78 + 0.34 * math.cos(math.radians(a)), 0.34 * math.sin(math.radians(a))))
        cap = _tf(cap, (0, 0), 1.0, -32)
        return [cap], [_tf([(-0.28, -0.3), (0.28, -0.3), (0.28, 0.3), (-0.28, 0.3), (-0.28, -0.3)], (0, 0), 1.0, -32)]
    # ---- card icons (unit space)
    if name == 'BRACE':       # clamp plate: slab with a V notch and two bolts
        plate = [(-0.85, -0.8), (0.85, -0.8), (0.85, 0.8), (-0.85, 0.8)]
        return [plate], [[(-0.4, -0.5), (0, 0.45), (0.4, -0.5)], [(-0.66, -0.58), (-0.64, -0.56)], [(0.66, -0.58), (0.64, -0.56)], [(-0.66, 0.6), (-0.64, 0.58)], [(0.66, 0.6), (0.64, 0.58)]]
    if name == 'TRIGGER':     # crosshair
        ring = [(0.62 * math.cos(math.radians(a)), 0.62 * math.sin(math.radians(a))) for a in np.linspace(0, 360, 36)]
        bars = [[(-0.12, -1.0), (0.12, -1.0), (0.12, -0.3), (-0.12, -0.3)], [(-0.12, 1.0), (0.12, 1.0), (0.12, 0.3), (-0.12, 0.3)],
                [(-1.0, -0.12), (-1.0, 0.12), (-0.3, 0.12), (-0.3, -0.12)], [(1.0, -0.12), (1.0, 0.12), (0.3, 0.12), (0.3, -0.12)]]
        return [ring] + bars, ['hole0.30']
    if name in ('SPIN', 'TWIST'):  # circular arrow(s): thick arc with a head
        polys = []
        n = 3 if name == 'SPIN' else 1
        span = 88 if n == 3 else 285
        for k in range(n):
            a0 = k * 120 + 12 if n == 3 else 20
            a1 = a0 + span
            outer = [(0.95 * math.sin(math.radians(a)), -0.95 * math.cos(math.radians(a))) for a in np.linspace(a0, a1, 14)]
            inner = [(0.52 * math.sin(math.radians(a)), -0.52 * math.cos(math.radians(a))) for a in np.linspace(a1, a0, 14)]
            ah = a1 + (20 if n == 3 else 22)
            head = [(1.18 * math.sin(math.radians(a1 - 2)), -1.18 * math.cos(math.radians(a1 - 2))),
                    (0.735 * math.sin(math.radians(ah)), -0.735 * math.cos(math.radians(ah))),
                    (0.30 * math.sin(math.radians(a1 - 2)), -0.30 * math.cos(math.radians(a1 - 2)))]
            polys.append(outer + head + inner)
        return polys, []
    raise KeyError(name)


def icon_mask(cv, name, c, size, rot=0.0):
    """white silhouette mask on a local box (SS).  returns mask, x0, y0 (box)."""
    S = cv.S
    polys, det = icon_polys(name)
    pad = int(size * S * 0.25)
    n = int(size * S * 2.0 / 2) + pad * 2
    ext = int(size * S) + pad * 2
    im = Image.new('L', (ext, ext), 0)
    d = ImageDraw.Draw(im)
    cc = (ext / 2, ext / 2)
    hole = None
    for p in polys:
        d.polygon(_tf(p, cc, size * S / 2, rot), fill=255)
    for dt in det:
        if isinstance(dt, str) and dt.startswith('hole'):
            r = float(dt[4:]) * size * S / 2
            d.ellipse([cc[0] - r, cc[1] - r, cc[0] + r, cc[1] + r], fill=0)
    m = np.asarray(im, np.float32) / 255.0
    m = warp(m, 0.55 * S, 7 * S, cv.r)
    x0 = int(c[0] * S - ext / 2)
    y0 = int(c[1] * S - ext / 2)
    return m, x0, y0


def draw_icon(cv, name, c, size, rot=0.0, fill=WHITE, ink=INK, ink_w=1.7, miss=(0.9, 0.7), detail=True, shadow=None):
    S = cv.S
    m, x0, y0 = icon_mask(cv, name, c, size, rot)
    solid = np.clip((ndi.gaussian_filter(m, 0.5 * S / 4 * 1.5) - 0.45) * 6, 0, 1)
    if shadow:
        sh = np.roll(np.roll(solid, int(2.6 * S), 0), int(2.6 * S), 1)
        cv.over(np.clip(sh - solid, 0, 1), shadow[0], shadow[1], x0, y0)
    ring = outline_mask(solid, S, ink_w)
    ring = np.clip(ndi.gaussian_filter(ring, 0.3 * S / 4 * 1.5) * 1.6, 0, 1)
    cv.over(ring, ink, 0.98, x0, y0)
    fm = np.roll(np.roll(solid, int(miss[1] * S), 0), int(miss[0] * S), 1)
    n = smooth(*fm.shape, 3 * S / 4 * 1.5, cv.r)
    cv.over(np.clip(fm * (0.95 + 0.05 * n), 0, 1), fill, 0.98, x0, y0)
    if detail:
        polys, det = icon_polys(name)
        ext = m.shape[0]
        cc = (x0 / S + ext / S / 2, y0 / S + ext / S / 2)
        for dt in det:
            if isinstance(dt, str):
                continue
            pts = _tf(dt, cc, size / 2, rot)
            ballpoint(cv, pts, ink, 1.35, 0.95, wob=0.25, wl=10, taper=(0.04, 0.04))
        if name == 'SHIELD':   # hand hatch on the right half
            reg = np.clip(solid, 0, 1).copy()
            h, w = reg.shape
            half = reg.copy()
            half[:, :w // 2 + int(0.5 * S)] = 0
            hatch_region(cv, half, x0, y0, ink, ang=45, pitch=3.0, w=0.9, alpha=0.75, over=0.0, jit=0.2)
    return x0, y0, solid
