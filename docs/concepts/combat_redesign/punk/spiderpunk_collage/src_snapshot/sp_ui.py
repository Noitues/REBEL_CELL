"""sp_ui: SEND IT, the nameplate and the YOU strip in Spider-Punk collage (cut paper, white cut edge, black drop, one yellow/magenta title style)."""
import math
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from st_gfx import *
import st_tower as T
import sp_cards as SC
from sp_cards import cut, scissor, paper_tex, ht, bolt_poly, C_MAG, C_MAG_D, C_MAG_L, C_YEL, C_YEL_D, C_COB, C_BLK, C_CUT, C_NEWS, C_PUR


def tape(cv, x, y, w, h, rot, seed, col=None, op=0.9):
    ss = cv.ss
    c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    r = np.random.default_rng(seed)
    n = 6
    right = [(w / 2 + (1.4 if i % 2 else -0.4) * (0.6 + 0.8 * r.random()), (i / n - 0.5) * h) for i in range(n + 1)]
    left = [(-w / 2 - (1.4 if i % 2 else -0.4) * (0.6 + 0.8 * r.random()), (i / n - 0.5) * h) for i in range(n, -1, -1)]
    P = [(x + px * c - py * s_, y + px * s_ + py * c) for (px, py) in right + left]
    m = poly(cv, P)
    cv.paint(blur(shift(m, 0.8 * ss, 1.6 * ss), 1.0 * ss), C_BLK, 0.4)
    cv.paint(blur(m, 0.3 * ss), C_YEL if col is None else col, op)
    cv.paint(blur(m * (vnoise(cv.H, cv.W, 1.7 * ss, seed, 1) > 0.55), 0.4 * ss), WHITE, 0.10)


def title(cv, txt, x, y, px, rot, A, seed, off=(2.0, 2.2), skew=0.14, track=1.0):
    ss = cv.ss
    m = text_mask(cv, txt, x, y, ANTON, px, 'mm', skew, rot, track, 0.25, seed)
    cv.paint(blur(shift(m, off[0] * ss, off[1] * ss), 0.3 * ss), C_MAG if A else C_COB)
    cv.paint(blur(m, 0.3 * ss), C_BLK)


def you_strip(f, V='A', ss=3, nw=False):
    A = V == 'A'
    x0, y0, w, h = 1068, 96, 346, 52
    cv = Cv(x0, y0, w, h, ss)
    X, Y = cv.grid()
    strip = scissor(cv, [(x0 + 8, y0 + 6), (x0 + w - 8, y0 + 5), (x0 + w - 9, y0 + h - 5), (x0 + 9, y0 + h - 4)], 0.9, 17)
    cut(cv, strip, paper_tex(cv, C_NEWS if A else hx('EDE8D8'), 4, 0.05), edge=1.4, drop=(1.8, 3.0), edge_col=C_CUT)
    # YOU tile: a yellow cut scrap with black letters and the magenta/cobalt offset print
    tile = scissor(cv, [(x0 + 12, y0 + 9), (x0 + 66, y0 + 8), (x0 + 67, y0 + 44), (x0 + 13, y0 + 45)], 0.6, 5)
    cut(cv, tile, paper_tex(cv, C_YEL, 6, 0.03), edge=0.9, drop=(1.2, 1.8), edge_col=C_BLK)
    if nw:
        for q in range(3):
            st_ = stroke_mask(cv, [(x0 + 24 + q * 10, y0 + 15), (x0 + 24.5 + q * 10, y0 + 38)], 4.4, 3.8, wob=0.2, seed=60 + q, taper=(0.05, 0.08))
            cv.paint(blur(st_, 0.3 * ss), C_BLK)
    else:
        title(cv, 'YOU', x0 + 39.5, y0 + 27, 30, -3, A, 2, off=(1.6, 1.8), track=0.6)
    xs = x0 + 74
    wseg, hseg, pitch = 12.6, 17, 15.6
    n_pend = f['hp'] - f['pv']['hp_after']
    n_lit = f['pv']['hp_after']
    segs = []
    for g in range(3):
        for k in range(5):
            segs.append(xs + g * (5 * pitch + 8) + k * pitch)
    for i, xx in enumerate(segs):
        m = poly(cv, [(xx, y0 + 27 - hseg / 2), (xx + wseg, y0 + 27 - hseg / 2), (xx + wseg, y0 + 27 + hseg / 2), (xx, y0 + 27 + hseg / 2)])
        m = grow(shrink(m, 2.2 * ss), 2.2 * ss)
        m = warp(m, 0.3 * ss, 6 * ss, 200 + i)
        ring = grow(m, 1.5 * ss)
        lit = i < n_lit
        cv.paint(blur(ring, 0.3 * ss), C_BLK)
        if lit:
            cv.paint(blur(m, 0.3 * ss), GAIN)
            g = np.clip(m - shift(m, 0.8 * ss, 1.2 * ss), 0, 1) * m
            cv.paint(blur(g, 0.25 * ss), WHITE, 0.85)
        elif i < n_lit + n_pend:
            cv.paint(blur(m, 0.3 * ss), hx('2A0F16'))
            hm = hatch_mask(cv, m, (45, 135), 3.7, 1.15, 0.2, seed=300 + i)
            cv.paint(blur(hm, 0.25 * ss), HARM)
            cv.paint(blur(np.clip(m - shrink(m, 1.4 * ss), 0, 1), 0.2 * ss), HARM)
    tape(cv, x0 + 10, y0 + 6, 32, 14, -32, 3)
    tape(cv, x0 + w - 12, y0 + h - 7, 32, 14, -28, 4)
    return cv.to_image(), (x0, y0)


def send_it(V='A', ss=3, scale=1, nw=False):
    A = V == 'A'
    x0, y0, w, h = 1640, 880, 275, 150
    cv = Cv(x0, y0, w, h, ss)
    X, Y = cv.grid()
    # a yellow lightning shard cut behind the slab, poking out of both ends
    zz = [(1650, 990), (1700, 944), (1760, 975), (1830, 936), (1900, 958)]
    shard = poly(cv, bolt_poly(zz, 24.0, 10.0))
    shard = warp(shard, 0.5 * ss, 14 * ss, 3)
    cut(cv, shard, C_YEL if A else C_MAG, edge=1.6, drop=(3.0, 4.0))
    slab = scissor(cv, [(1664, 921), (1884, 915), (1893, 936), (1883, 952), (1895, 972), (1888, 1004), (1668, 1007), (1659, 984), (1671, 964), (1660, 942)], 1.0, 9)
    base = np.empty((cv.H, cv.W, 3), np.float32)
    t = np.clip((Y - 915) / 92.0, 0, 1)
    if A:
        base = lerp(C_MAG[None, None, :], hx('E01580')[None, None, :], t[..., None])
        hh = ht(cv, np.clip((t - 0.25) * 1.2, 0, 1), 3.8, 45)
        base = base * (1 - hh[..., None] * 0.85) + C_MAG_D[None, None, :] * hh[..., None] * 0.85
        edge_col = C_CUT
    else:
        base = lerp(C_YEL[None, None, :], hx('FFB400')[None, None, :], t[..., None])
        hh = ht(cv, np.clip((t - 0.25) * 1.2, 0, 1), 3.8, 45)
        base = base * (1 - hh[..., None] * 0.8) + C_YEL_D[None, None, :] * hh[..., None] * 0.8
        edge_col = C_CUT
    cut(cv, slab, base, edge=2.4, drop=(4.0, 5.2), edge_col=edge_col)
    if nw:
        Pa = [(1735, 946), (1790, 946), (1790, 930), (1830, 959), (1790, 988), (1790, 972), (1735, 972)]
        am = poly(cv, Pa)
        cv.paint(blur(grow(am, 3.0 * ss), 0.4 * ss), C_BLK)
        cv.paint(blur(am, 0.4 * ss), WHITE)
    else:
        ms = text_mask(cv, 'SEND IT', 1777, 960, ANTON, 66, 'mm', 0.14, -2.2, 1.5, 0.3, 5)
        if A:
            cv.paint(blur(shift(grow(ms, 3.0 * ss), 4.0 * ss, 4.6 * ss), 0.4 * ss), C_BLK)
            cv.paint(blur(shift(ms, 3.0 * ss, 3.4 * ss), 0.4 * ss), C_YEL)
            cv.paint(blur(grow(ms, 3.0 * ss), 0.4 * ss), C_BLK)
            cv.paint(blur(ms, 0.35 * ss), WHITE)
        else:
            cv.paint(blur(shift(ms, 3.4 * ss, 3.8 * ss), 0.4 * ss), C_MAG)
            cv.paint(blur(ms, 0.35 * ss), C_BLK)
    tape(cv, 1670, 922, 36, 14, -35, 8)
    tape(cv, 1884, 1003, 36, 14, -32, 9)
    return cv.to_image(scale=scale), (x0, y0)


def nameplate(V='A', ss=3, scale=1, nw=False):
    A = V == 'A'
    x0, y0, w, h = 14, 948, 250, 126
    cv = Cv(x0, y0, w, h, ss)
    X, Y = cv.grid()
    sheet = scissor(cv, [(x0 + 28, y0 + 26), (x0 + 232, y0 + 22), (x0 + 233, y0 + 104), (x0 + 29, y0 + 106)], 1.2, 44)
    cut(cv, sheet, paper_tex(cv, C_NEWS if A else hx('EDE8D8'), 14, 0.05), edge=1.6, drop=(2.4, 4.0), edge_col=C_CUT)
    cx_, cy_ = 28 + 24, 948 + 24 + 41
    disc = circle(cv, cx_ + 8, cy_, 24)
    disc = warp(disc, 0.4 * ss, 8 * ss, 3)
    cut(cv, disc, C_MAG, edge=1.6, drop=(1.6, 2.4))
    cv.paint(ht(cv, np.clip((Y - (cy_ - 24)) / 48 * 1.1 - 0.2, 0, 1), 3.4, 45) * disc, C_MAG_D, 0.9)
    cm_ = T.glyph_mask('WC2_CREST', 32, cv, cx_ + 8, cy_)
    cv.paint(blur(grow(cm_, 1.4 * ss), 0.3 * ss), C_BLK)
    cv.paint(blur(cm_, 0.3 * ss), WHITE)
    # the name: black Anton on a yellow cut strip, magenta offset print
    ts = scissor(cv, [(x0 + 90, y0 + 36), (x0 + 224, y0 + 33), (x0 + 225, y0 + 72), (x0 + 91, y0 + 75)], 0.7, 21)
    cut(cv, ts, paper_tex(cv, C_YEL if A else C_CUT, 22, 0.03), edge=0.9, drop=(1.4, 2.0), edge_col=C_BLK)
    if nw:
        for q in range(9):
            xq = 128 + q * 9 + (q // 5) * 8
            st_ = stroke_mask(cv, [(xq - 20, cy_ - 22), (xq - 19.4, cy_ - 2)], 4.4, 3.8, wob=0.2, seed=60 + q, taper=(0.05, 0.08))
            cv.paint(blur(st_, 0.3 * ss), C_BLK)
        bar = stroke_mask(cv, [(106, cy_ + 16), (150, cy_ + 15), (212, cy_ + 17)], 6, 5, wob=0.3, seed=61, taper=(0.05, 0.05))
        cv.paint(blur(bar, 0.3 * ss), C_BLK, 0.85)
    else:
        title(cv, 'CELL-9', x0 + 157, y0 + 54.5, 36, -2, A, 2, off=(1.8, 2.0), track=0.8)
        m = text_mask(cv, '// BREAKER', x0 + 154, y0 + 90, MARKER, 19, 'mm', 0.0, -1.2, 0.0, 0.2, 3)
        cv.paint(blur(m, 0.3 * ss), C_BLK)
    tape(cv, 38, 962, 38, 14, -38, 5)
    tape(cv, 238, 1059, 38, 14, -34, 6)
    return cv.to_image(scale=scale), (x0, y0)
