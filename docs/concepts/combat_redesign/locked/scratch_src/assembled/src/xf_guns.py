"""xf_guns: the Cell's guns in the XEROX FLYER hand: a black key stroke with a magenta stroke slapped on 1.6 px off-register,
ending in a jagged paper-white burst with a magenta core.  Geometry is f1_guns' (same muzzles, same targets, same results)."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import f1_guns as FG
from f1_lib import Canvas, pol, outline_mask
import cv_lib as CL

INKC = (21, 18, 26)
MAGC = (255, 61, 168)
PAPERC = (251, 250, 244)
VAR = ['A']


def stroke(cv, pts, w0, w1, S):
    im = cv.new_mask()
    d = ImageDraw.Draw(im)
    n = len(pts)
    for i in range(n - 1):
        t = i / max(1, n - 2)
        w = w0 + (w1 - w0) * t
        d.line([(pts[i][0] * S, pts[i][1] * S), (pts[i + 1][0] * S, pts[i + 1][1] * S)], fill=255, width=max(1, int(w * S)))
        r = w * S / 2
        d.ellipse([pts[i][0] * S - r, pts[i][1] * S - r, pts[i][0] * S + r, pts[i][1] * S + r], fill=255)
    return np.asarray(im, np.float32) / 255.0


def burst(cv, x, y, r, S, seed):
    rr = np.random.default_rng(seed)
    pts = []
    n = 9
    for k in range(n * 2):
        q = r if k % 2 == 0 else r * 0.44
        q *= 1 + rr.uniform(-0.12, 0.12)
        a = math.radians(k * 180.0 / n + 10)
        pts.append((x + q * math.cos(a), y + q * math.sin(a)))
    m = cv.poly_mask(pts)
    big = cv.poly_mask([(x + (px - x) * 1.0 + 2.6 * math.copysign(1, px - x) * 0, y + (py - y) * 1.0) for px, py in pts])
    ring = np.clip(ndi.gaussian_filter(outline_mask(m, S, 2.2), 0.4) * 1.5, 0, 1)
    cv.over(np.roll(np.roll(m, int(2.4 * S), 0), int(2.6 * S), 1), INKC, 1.0)
    cv.over(ring, INKC, 1.0)
    cv.over(m, PAPERC, 1.0)
    core = cv.circle_mask((x + 1.4, y + 1.2), r * 0.32)
    cv.over(core, MAGC, 1.0)


def make_guns(f, alpha=1.0, words=True, S=2, results=True, idle=True, seed=5):
    cv = Canvas(1070, 1080, S, seed=seed)
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
            off = FG.gun_geom(i, n)
            p0 = FG.muzzle_pt(s, off)
            p1 = FG.target_pt(f, sh, s, off)
            shots_out.append((p0, p1, sh))
    for p0, p1, sh in shots_out:
        pts = FG.bez(p0, p1, 7.0)
        k = stroke(cv, pts, 9.4, 6.0, S)
        cv.over(k, INKC, 1.0)
        pts2 = [(x + 1.6, y - 1.4) for x, y in pts]
        m = stroke(cv, pts2, 5.2, 3.2, S)
        cv.over(m, MAGC, 1.0)
        cv.over(np.clip(m - np.roll(np.roll(m, int(1.2 * S), 0), int(1.2 * S), 1), 0, 1), PAPERC, 0.55)
    for i, (p0, p1, sh) in enumerate(shots_out):
        cv.over(cv.circle_mask(p0, 6.4), INKC, 1.0)
        cv.over(cv.circle_mask((p0[0] + 1, p0[1] - 1), 4.0), MAGC, 1.0)
        if not results:
            continue
        x, y = p1
        r = sh['result']
        back = math.degrees(math.atan2(p0[0] - x, -(p0[1] - y)))
        if r == 'hit':
            burst(cv, x, y, 12.5, S, 50 + i)
        elif r == 'armor':
            FG.chevron(cv, x, y, back + 35, FG.STEEL_HI)
        elif r == 'ward':
            FG.chevron(cv, x, y, back + 35, FG.BGOLD)
        elif r == 'shield':
            FG.hex_shards(cv, x, y, 12)
    if idle:
        for s in idle_out:
            a = 60 * s
            q0, q1 = pol(CL.C, 188, a), pol(CL.C, 206, a)
            cv.over(stroke(cv, [q0, q1], 6.6, 6.0, S), INKC, 1.0)
            cv.over(stroke(cv, [(q0[0] + 1.2, q0[1] - 1.0), (q1[0] + 1.2, q1[1] - 1.0)], 3.2, 3.0, S), MAGC, 1.0)
            x, y = pol(CL.C, 213, a)
            ring = cv.circle_mask((x, y), 5.4) - cv.circle_mask((x, y), 2.6)
            cv.over(np.clip(cv.circle_mask((x, y), 7.0), 0, 1), INKC, 1.0)
            cv.over(np.clip(ring, 0, 1) + cv.circle_mask((x, y), 2.6) * 0, MAGC, 1.0)
            cv.over(cv.circle_mask((x, y), 2.6), INKC, 1.0)
    im = cv.down()
    if alpha < 1.0:
        a = im.split()[3].point(lambda v: int(v * alpha))
        im.putalpha(a)
    return im, idle_out
