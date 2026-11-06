"""xf_gfx: the XEROX FLYER toolkit.  One hand for the Cell: a black photocopy with a coarse halftone, flat spot-colour blocks
slapped on off-register, stencil-posterized shadows, toner grain, smears, copier-lid edge shadows.
Works on the st_gfx Cv canvas (screen coords, supersample ss).  Everything here is plain numpy / scipy / PIL."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from st_gfx import *

# ---- the three spot inks (the flyer's whole palette) + black + paper
MAG = hx('FF3DA8')          # CELL_PINK: ours
MAG_D = hx('D41C86')
CYN = hx('12A9E6')          # process cyan: the off-register plate (never NET_CYAN meaning)
TONER = hx('15121A')        # copier black (never pure)
SHEET = hx('F2EEE4')        # copier paper
HARMC = hx('FF4433')
GAINC = hx('7BE07B')
SOAKC = hx('3A7EF3')


def mult(cv, alpha, color, op=1.0):
    """multiply ink over what is there (print overprint): rgb *= 1 - a*(1-col); alpha channel untouched"""
    a = (np.clip(alpha, 0, 1) * op)[..., None].astype(np.float32)
    col = np.asarray(color, np.float32)
    cv.a[..., :3] = cv.a[..., :3] * (1 - a * (1 - col))


def halftone(val, pitch, ang=45.0, ox=0.0, oy=0.0, aa=1.0, maxr=0.74):
    """a dot screen. val: coverage 0..1 per pixel (H,W); pitch in canvas px; returns AA mask.  Dot area = coverage."""
    H, W = val.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    th = math.radians(ang)
    c, s = math.cos(th), math.sin(th)
    u = ((xx - ox) * c + (yy - oy) * s) / pitch
    v = (-(xx - ox) * s + (yy - oy) * c) / pitch
    fu = u - np.round(u)
    fv = v - np.round(v)
    d = np.hypot(fu, fv) * pitch
    v_ = np.clip(val, 0, 1)
    r = np.minimum(pitch * np.sqrt(v_ / math.pi), pitch * maxr)
    m = np.clip((r - d) / aa + 0.5, 0, 1) * (v_ > 0.015)
    return np.maximum(m, (v_ > 0.93).astype(np.float32))


def ramp(cv, p0, p1, lo=0.0, hi=1.0, gamma=1.0):
    """linear coverage ramp from screen point p0 (value lo) to p1 (value hi)"""
    X, Y = cv.grid()
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    t = ((X - p0[0]) * dx + (Y - p0[1]) * dy) / (dx * dx + dy * dy)
    return (lo + (hi - lo) * np.clip(t, 0, 1) ** gamma).astype(np.float32)


def radial(cv, c, r0, r1, lo=0.0, hi=1.0, gamma=1.0):
    X, Y = cv.grid()
    t = (np.hypot(X - c[0], Y - c[1]) - r0) / (r1 - r0)
    return (lo + (hi - lo) * np.clip(t, 0, 1) ** gamma).astype(np.float32)


def toner_noise(cv, seed, cell=1.1, thr=0.80):
    """high-frequency toner speckle mask (1 = a speck)"""
    return (vnoise(cv.H, cv.W, cell * cv.ss, seed, 1) > thr).astype(np.float32)


def dropout(cv, seed, amount=0.10):
    """paper showing through solid ink: a mask of 'missing toner' specks and a few streaks"""
    n = vnoise(cv.H, cv.W, 1.0 * cv.ss, seed, 1)
    n2 = vnoise(cv.H, cv.W, 5.0 * cv.ss, seed + 9, 2)
    return np.clip((n - (1 - amount * 1.3)) * 9, 0, 1) * np.clip(0.6 + n2, 0.4, 1)


def rough(m, cv, amp=0.8, scale=5.0, seed=1):
    """cut / copied edge: a wobbly, slightly fuzzy edge with a hard threshold (1-bit look)"""
    w = warp(m, amp * cv.ss, scale * cv.ss, seed)
    return np.clip((blur(w, 0.55 * cv.ss) - 0.5) * 3.2 + 0.5, 0, 1)


def ink(cv, m, color, grain=0.07, seed=3, op=1.0):
    """flat spot ink with a little toner dropout (never perfectly solid)"""
    d = dropout(cv, seed, grain)
    cv.paint(m * (1 - d * 0.85), color, op)


def keyline(m, cv, w):
    return np.clip(grow(m, w * cv.ss) - m, 0, 1)


def plate_shift(m, cv, dx, dy):
    return shift(m, dx * cv.ss, dy * cv.ss)


def smear(cv, m, ang=20.0, length=14.0, op=0.35, color=None, seed=1):
    """a toner smear: the mask dragged along a direction and faded"""
    n = max(3, int(length * cv.ss))
    th = math.radians(ang)
    out = m.copy()
    for i in range(1, n, max(1, n // 12)):
        out = np.maximum(out, shift(m, math.cos(th) * i, math.sin(th) * i) * (1 - i / n))
    return out


def hatch_field(cv, angles=(45,), pitch=4.4, width=1.5, seed=0, jit=0.25):
    """a straight, hard hatch field over the whole canvas (L7: cross-hatch = lost at this END TURN)"""
    ss = cv.ss
    r = np.random.default_rng(seed)
    im = Image.new('L', (cv.W, cv.H), 0)
    d = ImageDraw.Draw(im)
    diag = math.hypot(cv.w, cv.h)
    cx, cy = cv.w / 2, cv.h / 2
    for ang in angles:
        th = math.radians(ang)
        dx, dy = math.cos(th), math.sin(th)
        nx, ny = -dy, dx
        k = -diag / 2
        while k < diag / 2:
            kk = k + r.normal(0, jit)
            ox, oy = cx + nx * kk, cy + ny * kk
            d.line([((ox - dx * diag) * ss, (oy - dy * diag) * ss), ((ox + dx * diag) * ss, (oy + dy * diag) * ss)], fill=255, width=max(1, int(round(width * ss))))
            k += pitch
    return np.asarray(im, np.float32) / 255.0


def xtext(cv, txt, x, y, px, fontname=ANTON, fill=TONER, off=None, off_col=MAG, off2=None, off2_col=CYN, edge=None, edge_w=0.0, skew=0.0, rot=0.0, track=0.0, wob=0.25, seed=0, anchor='mm', op=1.0, grain=0.05):
    """flyer lettering: up to two off-register ghost plates (spot colours, multiplied), a hard black or paper edge, then the fill.  Returns the fill mask."""
    ss = cv.ss
    m = text_mask(cv, txt, x, y, fontname, px, anchor, skew, rot, track, wob, seed)
    m = np.clip((blur(m, 0.3 * ss) - 0.5) * 3 + 0.5, 0, 1)
    if off2 is not None:
        cv.paint(plate_shift(m, cv, *off2), off2_col, op)
    if off is not None:
        cv.paint(plate_shift(m, cv, *off), off_col, op)
    if edge is not None and edge_w > 0:
        cv.paint(grow(m, edge_w * ss), edge, op)
    ink(cv, m, fill, grain, seed + 5, op)
    return m


def starburst_mask(cv, c, r_out, r_in, n=14, seed=0, ang0=0.0):
    r = np.random.default_rng(seed)
    pts = []
    for k in range(n * 2):
        rr = (r_out if k % 2 == 0 else r_in) * (1 + r.uniform(-0.08, 0.08))
        a = math.radians(ang0 + k * 180.0 / n)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    return poly(cv, pts)


def band_poly(cv, c, r0, r1, a0, a1, step=1.0):
    n = max(2, int(abs(a1 - a0) / step) + 1)
    out = [(c[0] + r1 * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1))), c[1] - r1 * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1)))) for i in range(n)]
    inn = [(c[0] + r0 * math.sin(math.radians(a1 + (a0 - a1) * i / (n - 1))), c[1] - r0 * math.cos(math.radians(a1 + (a0 - a1) * i / (n - 1)))) for i in range(n)]
    return poly(cv, out + inn)


def copier_edge(cv, page, seed=2, width=6.0, dark=0.85, side=(0.7, 0.7)):
    """the copier-lid shadow: a black, ragged, uneven band along the page edge, heavier toward `side`"""
    X, Y = cv.grid()
    d = ndi.distance_transform_edt(page > 0.5) / cv.ss
    n = vnoise(cv.H, cv.W, 14 * cv.ss, seed, 2)
    n2 = vnoise(cv.H, cv.W, 2.5 * cv.ss, seed + 4, 1)
    tcx, tcy = cv.x0 + cv.w / 2, cv.y0 + cv.h / 2
    dirn = ((X - tcx) * side[0] + (Y - tcy) * side[1]) / (0.5 * math.hypot(cv.w, cv.h))
    wd = width * np.clip(0.12 + 0.95 * n + 0.5 * dirn, 0, 1.5)
    band = np.clip((wd * (0.7 + 0.6 * n2) - d) * 2.0, 0, 1) * (page > 0.5)
    return band * dark


def to_cv_array(cv, local, x0, y0):
    """blit a local float mask (made at the canvas ss) with its top-left at canvas-px (x0,y0) into a full canvas array"""
    out = np.zeros((cv.H, cv.W) + local.shape[2:], np.float32)
    h, w = local.shape[:2]
    xa, ya = max(0, x0), max(0, y0)
    xb, yb = min(cv.W, x0 + w), min(cv.H, y0 + h)
    if xb > xa and yb > ya:
        out[ya:yb, xa:xb] = local[ya - y0:yb - y0, xa - x0:xb - x0]
    return out
