"""lw_ui: the player-owned pieces in the locked player style (xerox paper + toner, black key line, pink scissor-cut halo, off-register spot ink).
nameplate(), you_strip(), send_it(), undo()  -- same screen boxes and signatures as xf_ui / st_ui so f1_hand and the stack layer can swap them in.
Shared helpers: jag_rect() (scissor-cut outline), sticker() (shadow, halo, key, drop, paper)."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from xf_gfx import *
import st_tower as T
from xf_cards import rect, PLEX
from lw_tower import jag_path, jag_ring

WH = hx('FBFAF4')


def jag_rect(cv, x0, y0, x1, y1, rot=0.0, seed=1, seg=(8, 16), amp=0.8):
    rng = np.random.default_rng(seed)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    R = lambda x, y: (cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c)
    P = [R(x0, y0), R(x1, y0), R(x1, y1), R(x0, y1)]
    pts = []
    for i in range(4):
        pts += jag_path(P[i], P[(i + 1) % 4], rng, seg, amp)[:-1]
    return poly(cv, pts)


def sticker(cv, m, seed, halo=4.0, key=2.6, drop=(3.4, 4.2), paper=0.97, halo_col=None):
    """shadow, pink scissor halo, black key + block drop, paper body"""
    ss = cv.ss
    cv.paint(blur(shift(m, 3 * ss, 5 * ss), 3 * ss), hx('08060C'), 0.6)
    if halo:
        h = rough(grow(m, (key + halo) * ss), cv, 1.0, 9.0, seed + 6)
        ink(cv, h, halo_col if halo_col is not None else MAG, 0.09, seed + 7)
    cv.paint(extrude(grow(m, key * ss), drop[0] * ss, drop[1] * ss), TONER)
    cv.paint(grow(m, key * ss), TONER)
    cv.paint(m, SHEET * paper)


def you_strip(f, ss=3, nw=False):
    x0, y0, w, h = 1068, 96, 346, 52
    cv = Cv(x0, y0, w, h, ss)
    strip = jag_rect(cv, x0 + 8, y0 + 6, x0 + w - 8, y0 + h - 6, -0.4, 17)
    sticker(cv, strip, 17, halo=3.2, key=2.2)
    cv.paint(copier_edge(cv, strip, 5, 2.4, 0.5, (0.0, 1.0)), TONER)
    if nw:
        cv.paint(rect(cv, x0 + 18, y0 + 16, x0 + 58, y0 + 36), MAG)
    else:
        xtext(cv, 'YOU', x0 + 40, y0 + 27, 31, ANTON, fill=TONER, off=(1.8, 1.8), off_col=MAG, wob=0.2, track=0.6, rot=-2, seed=2)
    n_pend = f['hp'] - f['pv']['hp_after']
    n_lit = f['pv']['hp_after']
    xs = x0 + 72
    wseg, hseg, pitch = 12.6, 17, 15.6
    hf = hatch_field(cv, (45, 135), 3.7, 1.15, 301, 0.2)
    for i in range(15):
        g, k = divmod(i, 5)
        xx = xs + g * (5 * pitch + 8) + k * pitch
        m = rough(rect(cv, xx, y0 + 27 - hseg / 2, xx + wseg, y0 + 27 + hseg / 2), cv, 0.3, 6.0, 200 + i)
        cv.paint(grow(m, 1.5 * ss), TONER)
        if i < n_lit:
            cv.paint(m, GAINC)
            cv.paint(np.clip(m - shift(m, 0.8 * ss, 1.2 * ss), 0, 1) * m, WH, 0.8)
        elif i < n_lit + n_pend:
            cv.paint(m, hx('1A0E12'))
            inner = shrink(m, 1.2 * ss)
            cv.paint(hf * inner, HARMC)
            cv.paint(np.clip(inner - shrink(inner, 1.3 * ss), 0, 1), HARMC)
    return cv.to_image(), (x0, y0)


def send_it(variant='A', ss=3, scale=1, nw=False):
    x0, y0, w, h = 1640, 880, 275, 150
    cv = Cv(x0, y0, w, h, ss)
    rng = np.random.default_rng(9)
    P = [(1666, 920), (1888, 914), (1893, 1003), (1664, 1007)]
    pts = []
    for i in range(4):
        pts += jag_path(P[i], P[(i + 1) % 4], rng, (9, 17), 0.9)[:-1]
    slab = poly(cv, pts)
    cv.paint(blur(shift(slab, 4 * ss, 6 * ss), 3.5 * ss), hx('08060C'), 0.65)
    cv.paint(extrude(grow(slab, 3.0 * ss), 6.0 * ss, 7.0 * ss), TONER)
    cv.paint(grow(slab, 3.0 * ss), WH * 0.95)
    cv.paint(grow(slab, 0.5 * ss), TONER)
    ink(cv, shift(slab, -3.0 * ss, -2.4 * ss) * grow(slab, 1.2 * ss), MAG, 0.07, 3)
    cov = ramp(cv, (0, 944), (0, 1004), 0.0, 0.62, 1.1)
    ht = halftone(cov, 7.0 * ss, 45, 0, 0, aa=1.0 * ss)
    cv.paint(ht * slab, TONER, 0.95)
    for sgn, ax in ((1, 1686), (-1, 1872)):
        for q in range(3):
            yy = 944 + q * 14
            cv.paint(rect(cv, ax - 8 if sgn > 0 else ax - 2, yy, ax + 8 if sgn < 0 else ax + 14, yy + 4.4, 0), WH, 0.95)
    if nw:
        Pa = [(1735, 946), (1790, 946), (1790, 930), (1830, 959), (1790, 988), (1790, 972), (1735, 972)]
        am = poly(cv, Pa)
        cv.paint(extrude(grow(am, 2.6 * ss), 4.0 * ss, 4.8 * ss), TONER)
        cv.paint(grow(am, 2.6 * ss), TONER)
        cv.paint(am, WH)
    else:
        xtext(cv, 'SEND IT', 1777, 960, 68, ANTON, fill=WH, off=None, edge=TONER, edge_w=3.4, skew=0.14, rot=-2.2, track=1.5, wob=0.3, seed=5, grain=0.0)
    return cv.to_image(scale=scale), (x0, y0)


def nameplate(variant='A', ss=3, scale=1, nw=False):
    x0, y0, w, h = 14, 948, 250, 126
    cv = Cv(x0, y0, w, h, ss)
    pl = jag_rect(cv, x0 + 26, y0 + 24, x0 + 26 + 204, y0 + 24 + 82, -1.0, 44)
    sticker(cv, pl, 44, halo=4.0, key=2.4)
    cv.paint(copier_edge(cv, pl, 6, 3.0, 0.8, (-0.3, 1.0)), TONER)
    cx_, cy_ = 28 + 24 + 8, 948 + 24 + 41
    rng = np.random.default_rng(3)
    disc = poly(cv, jag_ring((cx_, cy_), 24, rng, (6, 10), 0.5))
    cv.paint(extrude(grow(disc, 2.0 * ss), 2.6 * ss, 3.0 * ss), TONER)
    cv.paint(grow(disc, 2.0 * ss), TONER)
    ink(cv, disc, WH * 0.97, 0.0, 3)
    ink(cv, shift(disc, -2.2 * ss, -1.9 * ss) * grow(disc, 1.0 * ss), MAG, 0.03, 3)
    cm_ = T.glyph_mask('WC2_CREST', 32, cv, cx_, cy_)
    cv.paint(extrude(grow(cm_, 1.2 * ss), 1.8 * ss, 2.0 * ss), TONER)
    cv.paint(grow(cm_, 1.2 * ss), TONER)
    cv.paint(cm_, WH)
    if nw:
        for q in range(9):
            xq = 128 + q * 9 + (q // 5) * 8
            cv.paint(rect(cv, xq, cy_ - 22, xq + 4.4, cy_ - 2), MAG)
        cv.paint(rect(cv, 126, cy_ + 13, 212, cy_ + 19), TONER, 0.85)
    else:
        xtext(cv, 'CELL-9', 160, cy_ - 11, 40, ANTON, fill=TONER, off=(2.2, 2.2), off_col=MAG, rot=-1.5, wob=0.2, track=0.8, seed=2)
        xtext(cv, '// BREAKER', 160, cy_ + 20, 22, PLEX, fill=TONER, rot=-1.0, wob=0.1, seed=3, grain=0.0)
    return cv.to_image(scale=scale), (x0, y0)


def undo(nw=False, ss=3):
    """UNDO: a small paper tab, black key, pink halo; the Z key as a black keycap.  Tab 1676..1880 x 861..895 (inside the stack mask)."""
    x0, y0, w, h = 1660, 846, 250, 60
    cv = Cv(x0, y0, w, h, ss)
    tab = jag_rect(cv, 1676, 861, 1880, 895, -0.6, 71)
    sticker(cv, tab, 71, halo=2.6, key=2.0, drop=(2.4, 3.0))
    cv.paint(copier_edge(cv, tab, 8, 2.0, 0.5, (0.0, 1.0)), TONER)
    if nw:
        cv.paint(rect(cv, 1690, 872, 1760, 886), TONER, 0.9)
    else:
        xtext(cv, 'UNDO', 1740, 878.5, 25, ANTON, fill=TONER, off=(1.4, 1.4), off_col=MAG, rot=-0.6, wob=0.12, track=1.4, seed=8, grain=0.0)
    key = rect(cv, 1840, 866, 1870, 891, -0.6)
    cv.paint(extrude(grow(key, 1.2 * ss), 1.6 * ss, 2.0 * ss), TONER)
    cv.paint(grow(key, 1.2 * ss), TONER)
    cv.paint(key, TONER)
    if nw:
        cv.paint(poly(cv, [(1862, 872), (1847, 879), (1862, 886), (1862, 882.5), (1854.5, 879), (1862, 875.5)]), WH)      # nowords: an undo chevron on the keycap, no letter
    else:
        xtext(cv, 'Z', 1855, 879, 19, ANTON, fill=WH, rot=-0.6, wob=0.05, seed=9, grain=0.0)
    return cv.to_image(), (x0, y0)
