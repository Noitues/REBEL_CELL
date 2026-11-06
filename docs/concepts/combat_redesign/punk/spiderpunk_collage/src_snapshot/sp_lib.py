"""sp_lib: the Spider-Punk collage kit on top of f1_lib.Canvas.
cut-paper layers (white scissor edge + black offset drop), Ben-Day halftone, jagged lightning shards, newsprint scraps, ransom-note letter tiles, safety pins, tape."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from f1_lib import *

# ---- palette (Spider-Punk collage)
MAG = (255, 45, 150)          # CELL_PINK family, slightly hotter for print
MAG_D = (178, 10, 104)
MAG_L = (255, 140, 200)
YEL = (255, 204, 0)           # print yellow (warmer than the PLAN grease-pencil yellow 255,226,0)
YEL_D = (214, 150, 0)
COB = (40, 60, 245)           # cobalt
COB_D = (20, 28, 140)
PUR = (74, 32, 138)           # poster purple
PUR_D = (38, 14, 84)
NEWS = (226, 220, 204)        # newsprint
NEWS_D = (186, 178, 160)
BLK = (14, 12, 20)
CUT = (252, 250, 244)         # white cut edge


def lerp3(a, b, t):
    a = np.asarray(a, np.float32)
    b = np.asarray(b, np.float32)
    return a + (b - a) * t[..., None]


def grids(cv):
    """1x-unit pixel coordinate grids of the canvas (cached on the canvas)"""
    if not hasattr(cv, '_g'):
        yy, xx = np.mgrid[0:cv.H, 0:cv.W].astype(np.float32)
        cv._g = (xx / cv.S, yy / cv.S)
    return cv._g


def shiftm(m, dx, dy, S):
    return np.roll(np.roll(m, int(round(dy * S)), 0), int(round(dx * S)), 1)


def dilate(m, px, S):
    """round dilation of a (soft) mask by px (1x)"""
    d = ndi.distance_transform_edt(m < 0.5)
    return np.clip((px * S - d) + 0.5, 0, 1).astype(np.float32)


def solid(m, S):
    return np.clip((ndi.gaussian_filter(m, 0.5 * S / 4 * 1.5) - 0.45) * 6, 0, 1)


def halftone(cv, dens, pitch, ang, gain=1.0, x0=0.0, y0=0.0):
    """Ben-Day dots: a mask (SS) whose dot radius follows dens (0..1, SS array).  pitch in 1x px."""
    xx, yy = grids(cv)
    a = math.radians(ang)
    u = (xx - x0) * math.cos(a) + (yy - y0) * math.sin(a)
    v = -(xx - x0) * math.sin(a) + (yy - y0) * math.cos(a)
    fu = (u % pitch) - pitch / 2
    fv = (v % pitch) - pitch / 2
    d = np.hypot(fu, fv)
    rad = np.sqrt(np.clip(dens, 0, 1)) * pitch * 0.62 * gain
    return np.clip((rad - d) * cv.S + 0.5, 0, 1).astype(np.float32)


def linear_field(cv, p0, p1):
    xx, yy = grids(cv)
    d = np.array(p1, np.float32) - np.array(p0, np.float32)
    L2 = float(d @ d) + 1e-6
    return np.clip(((xx - p0[0]) * d[0] + (yy - p0[1]) * d[1]) / L2, 0, 1)


def radial_field(cv, c, r0, r1):
    xx, yy = grids(cv)
    return np.clip((np.hypot(xx - c[0], yy - c[1]) - r0) / (r1 - r0), 0, 1)


def cut_layer(cv, mask, fill, edge=2.2, drop=(3.0, 4.0), drop_a=0.92, edge_col=CUT):
    """a scissor-cut paper layer: black offset drop, white cut edge, then the fill ((h,w,3) rgb or a colour)."""
    S = cv.S
    e = dilate(mask, edge, S) if edge else mask
    if drop:
        cv.over(shiftm(e, drop[0], drop[1], S), BLK, drop_a)
    if edge:
        cv.over(e, edge_col, 1.0)
    fill = np.asarray(fill, np.float32)
    if fill.ndim == 3:
        cv.over_rgb(mask, fill)
    else:
        cv.over(mask, fill, 1.0)
    return mask


def scissor(cv, pts, rough=0.5):
    """polygon with a very slight hand-cut wobble on its edges"""
    m = cv.poly_mask(pts)
    return solid(warp(m, rough * cv.S, 26 * cv.S, cv.r), cv.S)


def paper_fill(cv, tint, strength=0.5):
    return paper_rgb(cv, 'plain', tint, strength=strength)


def lightning(cv, a_deg, r0, r1, c, w0=7.0, w1=2.0, zig=4.0, n=5, phase=1):
    """a jagged lightning shard along the radius at angle a_deg: zig-zag centre line (lateral px = zig), thick near r0, tapering to a point at r1."""
    L, R = [], []
    for k in range(n + 1):
        r = r0 + (r1 - r0) * k / n
        lat = 0.0 if k in (0, n) else zig * (phase if k % 2 else -phase)
        t = k / n
        w = (w0 + (w1 - w0) * t) * (1 if k < n else 0.0)
        ang = a_deg + math.degrees(lat / max(r, 1))
        L.append(pol(c, r, ang - math.degrees(w / 2 / max(r, 1))))
        R.append(pol(c, r, ang + math.degrees(w / 2 / max(r, 1))))
    return cv.poly_mask(L + R[::-1])


def burst_pts(c, r_in, r_out, n, rot=0.0, jit=0.0, r=None):
    pts = []
    for i in range(n * 2):
        rr = r_out if i % 2 == 0 else r_in
        if r is not None and i % 2 == 0:
            rr *= 1 + r.uniform(-jit, jit)
        pts.append(pol(c, rr, rot + i * 180.0 / n))
    return pts


def scrap_text(cv, box, rot, tint=NEWS, col=(70, 66, 60), seed=0):
    """newsprint scrap with tiny grey 'text' lines.  box = (cx, cy, w, h) 1x.  returns the paper mask"""
    cx, cy, w, h = box
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    P = [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
    m = scissor(cv, P, 0.35)
    cut_layer(cv, m, paper_rgb(cv, 'plain', tint, strength=0.35), edge=1.0, drop=(1.6, 2.2))
    r = np.random.default_rng(seed)
    rows = int(h / 3.0)
    for i in range(rows):
        y = -h / 2 + 2.0 + i * 3.0
        L = r.uniform(0.55, 0.95) * (w - 4)
        p0 = (cx + (-w / 2 + 2) * ca - y * sa, cy + (-w / 2 + 2) * sa + y * ca)
        p1 = (cx + (-w / 2 + 2 + L) * ca - y * sa, cy + (-w / 2 + 2 + L) * sa + y * ca)
        ballpoint(cv, [p0, p1], col, 1.15, 0.7, wob=0.1, wl=6, taper=(0.02, 0.02))
    return m


def ransom(cv, text, c, px, rot=0.0, spacing=0.0, seed=0, palette=None, fnt=ANTON_F, tile_h=None):
    """ransom-note letters: each letter on its own tilted tile (paper / yellow / magenta / black), cut edge + drop.  centred at c (1x)"""
    r = np.random.default_rng(seed)
    pal = palette or [((250, 248, 240), BLK), (YEL, BLK), (BLK, (250, 248, 240)), (MAG, BLK), ((250, 248, 240), MAG_D)]
    f = font(fnt, px * 4)
    ws = [f.getlength(ch) / 4.0 for ch in text]
    th = tile_h or px * 1.22
    tws = [max(px * 0.55, wch + px * 0.28) for wch in ws]
    tot = sum(tws) + spacing * (len(text) - 1)
    x = -tot / 2
    a0 = math.radians(rot)
    for i, ch in enumerate(text):
        tw = tws[i]
        tc = x + tw / 2
        x += tw + spacing
        jy = r.uniform(-1.3, 1.3)
        tilt = r.uniform(-7, 7)
        cx = c[0] + tc * math.cos(a0) - jy * math.sin(a0)
        cy = c[1] + tc * math.sin(a0) + jy * math.cos(a0)
        bg, fg = pal[(i + seed) % len(pal)]
        ang = math.radians(rot + tilt)
        ca, sa = math.cos(ang), math.sin(ang)
        hh = th * r.uniform(0.92, 1.05)
        P = [(cx + xx * ca - yy * sa, cy + xx * sa + yy * ca) for xx, yy in ((-tw / 2, -hh / 2), (tw / 2, -hh / 2 + r.uniform(-0.5, 0.5)), (tw / 2 + r.uniform(-0.4, 0.4), hh / 2), (-tw / 2, hh / 2 + r.uniform(-0.5, 0.5)))]
        m = cv.poly_mask(P)
        cut_layer(cv, m, bg, edge=0.9, drop=(1.2, 1.6), drop_a=0.85, edge_col=(250, 248, 240) if bg != (250, 248, 240) else (200, 196, 186))
        tm = text_mask(cv, ch, fnt, px, rot + tilt)
        h_, w_ = tm.shape
        tmb = ndi.gaussian_filter(tm, 0.4 * cv.S / 4 * 1.5)
        cv.over(np.clip((tmb - 0.4) * 4, 0, 1), fg, 1.0, int(cx * cv.S - w_ / 2), int(cy * cv.S - h_ / 2))


def safety_pin(cv, c, ang, L=30, col=(200, 208, 220)):
    """an open safety pin: coil head, long needle, short guard, clasp cap.  ink keyline under steel."""
    a = math.radians(ang)
    u = np.array([math.cos(a), math.sin(a)])
    v = np.array([-u[1], u[0]])
    c = np.array(c, float)
    head = c - u * L / 2
    tip = c + u * L / 2
    g0 = head + v * 7.0
    g1 = tip - u * 8 + v * 7.0
    for w, colr in ((5.6, INK), (2.6, col)):
        for pts in ([head, tip], [g0, g1], [head, head + v * 7.0 + u * 1.5]):
            marker(cv, pts, colr, w=w, alpha=1.0, wob=0.0, grain=0.0, rough=0.0, taper=(0, 0))
        marker(cv, arc_pts(head - u * 1.6 + v * 3.5, 4.6, 0, 359, 20), colr, w=w * 0.8, alpha=1.0, wob=0.0, grain=0.0, rough=0.0, taper=(0, 0))
    cap = [tip - u * 11 - v * 3.0, tip + u * 3.0 - v * 3.0, tip + u * 3.0 + v * 10.0, tip - u * 11 + v * 10.0]
    cm = cv.poly_mask(cap)
    cv.over(dilate(cm, 1.1, cv.S), INK, 1.0)
    cv.over(cm, col, 1.0)
    cv.over(cv.poly_mask([tip - u * 10 + v * 8.0, tip + u * 2.0 + v * 8.0, tip + u * 2.0 + v * 9.2, tip - u * 10 + v * 9.2]), (110, 118, 136), 0.95)
