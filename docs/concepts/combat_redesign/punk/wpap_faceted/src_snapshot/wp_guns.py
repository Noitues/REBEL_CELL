"""f1_guns: the Cell's guns.  Tapered pink marker strokes (ink keyline under) from the muzzle on the page rim to the struck cell, ending in a hand starburst.
armor = steel chevron ricochet, ward = gold chevron ricochet, shield = a pop of hex shards.  An idle gun is a short stroke ending in an open painted ring."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from f1_lib import *
import wc2
import cv_board as CB
import cv_lib as CL
import wp_lib as _WL
from wp_lib import poly_stroke_mask as _psm


def _quad(p0, p1, w0, w1):
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    d = p1 - p0
    n = np.array([-d[1], d[0]]) / (np.hypot(*d) + 1e-9)
    return [tuple(p0 + n * w0 / 2), tuple(p1 + n * w1 / 2), tuple(p1 - n * w1 / 2), tuple(p0 - n * w0 / 2)]


def marker(cv, pts, col, w=6, alpha=1.0, **k):
    """WPAP: straight, flat, tapered stroke (muzzle wide, tip narrow)"""
    pts = [tuple(p) for p in pts]
    if w < 2.0:
        return
    if len(pts) > 6:
        cv.over(cv.poly_mask(_quad(pts[0], pts[-1], w, w * 0.45)), col, 1.0)
    else:
        cv.over(_psm((cv.H, cv.W), cv.S, pts, w, cap=False), col, 1.0)


def ballpoint(cv, pts, col, w, alpha=1.0, **k):
    marker(cv, pts, col, w=w)

MUZ_R = 186.0
STEEL_HI = (226, 233, 246)
STEEL = (150, 162, 182)
BGOLD = (255, 196, 40)
PINK_C = PINK


def bez(p0, p1, bend=7.0, n=30):
    p0 = np.array(p0, float)
    p1 = np.array(p1, float)
    d = p1 - p0
    nrm = np.array([-d[1], d[0]]) / (np.hypot(*d) + 1e-9)
    mid = (p0 + p1) / 2 + nrm * bend
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * mid + t ** 2 * p1


def starburst(cv, x, y, r=11.0, core=PINK_C, n=16):
    pts = []
    for k in range(n):
        rr = r if k % 2 == 0 else r * 0.42
        pts.append(pol((x, y), rr, k * 360 / n + 0))
    m = cv.poly_mask(pts)
    cv.over(np.clip(ndi.gaussian_filter(outline_mask(m, cv.S, 1.9), 0.4) * 1.5, 0, 1), INK, 1.0)
    cv.over(m, WHITE, 1.0)
    cv.over(cv.circle_mask((x, y), r * 0.3), core, 1.0)


def hex_shards(cv, x, y, r=11.0):
    cv.over(cv.circle_mask((x, y), 4.6), INK, 1.0)
    cv.over(cv.circle_mask((x, y), 3.2), (6, 12, 22), 1.0)
    for i in range(6):
        a = i * 60 + 18
        cx_, cy_ = pol((x, y), r - 2.0, a)
        rr = 3.9 if i % 2 == 0 else 3.0
        hp = [pol((cx_, cy_), rr, 60 * j + 30 + i * 11) for j in range(6)]
        m = cv.poly_mask(hp)
        cv.over(np.clip(ndi.gaussian_filter(outline_mask(m, cv.S, 1.5), 0.4) * 1.5, 0, 1), INK, 1.0)
        cv.over(m, PINK_L, 1.0)


def chevron(cv, x, y, back, col, size=22):
    a = math.radians(back)
    ux, uy = math.sin(a), -math.cos(a)
    px_, py_ = -uy, ux
    h = size / 2
    tip = (x + ux * h * 0.6, y + uy * h * 0.6)
    p = [(x - ux * h * 0.5 + px_ * h, y - uy * h * 0.5 + py_ * h), tip, (x - ux * h * 0.5 - px_ * h, y - uy * h * 0.5 - py_ * h)]
    ballpoint(cv, p, INK, 8.6, 1.0, wob=0.2, wl=12, taper=(0, 0))
    marker(cv, p, col, w=4.6, alpha=1.0, wob=0.2, wl=12, taper=(0, 0), grain=0.04)


def gun_geom(i, n):
    return 24 + (i - (n - 1) / 2) * 9


def muzzle_pt(s, off):
    import e8lib as E8
    return E8.pt(MUZ_R, 60 * s, off)


def target_pt(f, sh, s, off):
    cc = wc2.cell_centre(f, sh['uid'])
    ri, ro = CB.ring_geom(sh['dep'])
    if cc is None:
        return wc2.pt((ri + ro) / 2, 60 * s, off * 0.6)
    return CL.ppx(CL.C, (ri + ro) / 2, cc[0])


def make_guns(f, alpha=1.0, words=True, S=2, results=True, idle=True, seed=5):
    cv = Canvas(1070, 1080, S, seed=seed)
    lay = Canvas(1070, 1080, S, seed=seed + 1)
    shots_out = []
    idle_out = []
    for gn in f['guns']:
        s = gn['sector']
        shots = [sh for sh in gn['shots'] if sh['uid'] is not None]
        n = len(shots)
        if not shots:
            idle_out.append(s)
            continue
        for i, sh in enumerate(shots):
            off = gun_geom(i, n)
            p0 = muzzle_pt(s, off)
            p1 = target_pt(f, sh, s, off)
            shots_out.append((p0, p1, sh))
    for p0, p1, sh in shots_out:
        pts = bez(p0, p1, 0.0)
        marker(cv, pts, INK, w=9.0, alpha=0.97, wob=0.5, wl=30, taper=(0.02, 0.25), grain=0.05)
        marker(cv, pts, PINK_C, w=5.2, alpha=1.0, wob=0.35, wl=30, taper=(0.02, 0.3), grain=0.14)
        marker(cv, pts[:18], PINK_L, w=1.4, alpha=0.6, wob=0.2, wl=30, taper=(0.1, 0.5), grain=0)
    for p0, p1, sh in shots_out:
        cv.over(cv.circle_mask(p0, 6.2), INK, 1.0)
        cv.over(cv.circle_mask(p0, 3.8), PINK_C, 1.0)
        if not results:
            continue
        x, y = p1
        r = sh['result']
        back = math.degrees(math.atan2(p0[0] - x, -(p0[1] - y)))
        if r == 'hit':
            starburst(cv, x, y, 11.5)
        elif r == 'armor':
            chevron(cv, x, y, back + 35, STEEL_HI)
        elif r == 'ward':
            chevron(cv, x, y, back + 35, BGOLD)
        elif r == 'shield':
            hex_shards(cv, x, y, 12)
    if idle:
        for s in idle_out:
            a = 60 * s
            p0, p1 = pol(CL.C, 188, a), pol(CL.C, 206, a)
            marker(cv, [p0, p1], INK, w=6.4, alpha=0.9, wob=0.3, taper=(0.05, 0.1), grain=0.05)
            marker(cv, [p0, p1], PINK_C, w=3.2, alpha=0.8, wob=0.3, taper=(0.05, 0.1), grain=0.1)
            x, y = pol(CL.C, 213, a)
            ring = cv.circle_mask((x, y), 5.2) - cv.circle_mask((x, y), 2.6)
            cv.over(np.clip(ndi.gaussian_filter(outline_mask(np.clip(ring + cv.circle_mask((x, y), 2.6), 0, 1), S, 1.4), 0.4) * 1.5, 0, 1), INK, 0.95)
            cv.over(np.clip(ring, 0, 1), PINK_C, 0.9)
    im = cv.down()
    if alpha < 1.0:
        a = im.split()[3].point(lambda v: int(v * alpha))
        im.putalpha(a)
    return im, idle_out
