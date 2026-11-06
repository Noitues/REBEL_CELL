"""xf_ui: the other player-owned pieces in the XEROX FLYER style: YOU strip (a photocopied strip pasted on the HUD), SEND IT (a magenta slab), the nameplate.
Same screen boxes and signatures as st_ui, so f1_hand can swap them in."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from xf_gfx import *
import st_tower as T
import xf_tower as XT
import xf_cards as XC
from xf_cards import rect, PLEX

VAR = XT.VAR
WH = hx('FBFAF4')


def isB():
    return VAR[0] == 'B'


def pasted(cv, m, seed, drop=(3.0, 4.0), border=0.0):
    ss = cv.ss
    cv.paint(blur(shift(m, drop[0] * ss, drop[1] * ss), 2.0 * ss), hx('08060C'), 0.6)


def you_strip(f, ss=3, nw=False):
    x0, y0, w, h = 1068, 96, 346, 52
    cv = Cv(x0, y0, w, h, ss)
    B = isB()
    strip = rough(rect(cv, x0 + 7, y0 + 5, x0 + w - 7, y0 + h - 5, -0.4), cv, 0.9, 8.0, 17)
    pasted(cv, strip, 17)
    if B:
        cv.paint(grow(strip, 2.4 * ss), SHEET * 0.95)
        cv.paint(strip, TONER)
    else:
        cv.paint(grow(strip, 2.0 * ss), TONER)
        cv.paint(strip, SHEET * 0.97)
        cl = copier_edge(cv, strip, 5, 3.0, 0.9, (0.0, 1.0))
        cv.paint(cl, TONER)
    gcol = SHEET if B else TONER
    if nw:
        cv.paint(rect(cv, x0 + 18, y0 + 16, x0 + 58, y0 + 36), MAG)
    else:
        xtext(cv, 'YOU', x0 + 40, y0 + 27, 31, ANTON, fill=MAG if B else TONER, off=(1.8, 1.8), off_col=MAG if not B else SHEET, wob=0.2, track=0.6, rot=-2, seed=2)
    n_pend = f['hp'] - f['pv']['hp_after']
    n_lit = f['pv']['hp_after']
    xs = x0 + 72
    wseg, hseg, pitch = 12.6, 17, 15.6
    hf = hatch_field(cv, (45, 135), 3.7, 1.15, 301, 0.2)
    for i in range(15):
        g, k = divmod(i, 5)
        xx = xs + g * (5 * pitch + 8) + k * pitch
        m = rough(rect(cv, xx, y0 + 27 - hseg / 2, xx + wseg, y0 + 27 + hseg / 2), cv, 0.3, 6.0, 200 + i)
        cv.paint(grow(m, 1.5 * ss), TONER if not B else TONER)
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
    B = isB()
    X, Y = cv.grid()
    slab = poly(cv, [(1666, 920), (1888, 914), (1893, 1003), (1664, 1007)])
    slab = rough(slab, cv, 1.0, 14.0, 9)
    cv.paint(blur(shift(slab, 4 * ss, 6 * ss), 3.5 * ss), hx('08060C'), 0.65)
    # black key block drop, white border, then the colour plate
    cv.paint(extrude(grow(slab, 3.0 * ss), 6.0 * ss, 7.0 * ss), TONER)
    cv.paint(grow(slab, 3.0 * ss), WH * 0.95)
    cv.paint(grow(slab, 0.5 * ss), TONER)
    if B:
        ink(cv, slab, WH * 0.97, 0.03, 3)
        mg = plate_shift(slab, cv, 3.0, 2.6)
        cov = ramp(cv, (0, 940), (0, 1004), 0.0, 0.5, 1.1)
        ht = halftone(cov, 7.0 * ss, 45, 0, 0, aa=1.0 * ss)
        cv.paint(ht * slab, MAG, 0.95)
        tcol, tgh = TONER, MAG
    else:
        cv.paint(plate_shift(slab, cv, -4.0, 3.0), CYN)
        ink(cv, plate_shift(slab, cv, 2.0, -1.6) * slab if False else slab, MAG, 0.05, 3)
        cov = ramp(cv, (0, 944), (0, 1004), 0.0, 0.62, 1.1)
        ht = halftone(cov, 7.0 * ss, 45, 0, 0, aa=1.0 * ss)
        cv.paint(ht * slab, TONER, 0.95)
        tcol, tgh = WH, TONER
    # speed stripes at both ends
    for sgn, ax in ((1, 1686), (-1, 1872)):
        for q in range(3):
            yy = 944 + q * 14
            cv.paint(rect(cv, ax - 8 if sgn > 0 else ax - 2, yy, ax + 8 if sgn < 0 else ax + 14, yy + 4.4, 0), TONER if B else WH, 0.95)
    if nw:
        Pa = [(1735, 946), (1790, 946), (1790, 930), (1830, 959), (1790, 988), (1790, 972), (1735, 972)]
        am = poly(cv, Pa)
        cv.paint(extrude(grow(am, 2.6 * ss), 4.0 * ss, 4.8 * ss), TONER)
        cv.paint(grow(am, 2.6 * ss), TONER)
        cv.paint(am, WH)
    else:
        xtext(cv, 'SEND IT', 1777, 960, 68, ANTON, fill=tcol, off=None, edge=TONER if not B else None, edge_w=3.4 if not B else 0.0,
              skew=0.14, rot=-2.2, track=1.5, wob=0.3, seed=5, grain=0.0)
        if not B:
            m = text_mask(cv, 'SEND IT', 1777, 960, ANTON, 68, 'mm', 0.14, -2.2, 1.5, 0.3, 5)
            cv.paint(plate_shift(np.clip((blur(m, 0.3 * ss) - 0.5) * 3 + 0.5, 0, 1), cv, 3.6, 3.8) * (1 - np.clip((blur(m, 0.3 * ss) - 0.5) * 3 + 0.5, 0, 1)) * 0.0, TONER)
        else:
            m = text_mask(cv, 'SEND IT', 1777, 960, ANTON, 68, 'mm', 0.14, -2.2, 1.5, 0.3, 5)
            m = np.clip((blur(m, 0.3 * ss) - 0.5) * 3 + 0.5, 0, 1)
            cv.paint(plate_shift(m, cv, 3.2, 3.4) * (1 - m), MAG)
    return cv.to_image(scale=scale), (x0, y0)


def nameplate(variant='A', ss=3, scale=1, nw=False):
    x0, y0, w, h = 14, 948, 250, 126
    cv = Cv(x0, y0, w, h, ss)
    B = isB()
    pl = rough(rect(cv, x0 + 26, y0 + 24, x0 + 26 + 204, y0 + 24 + 82, -1.0), cv, 1.0, 9.0, 44)
    cv.paint(blur(shift(pl, 3 * ss, 5 * ss), 3 * ss), hx('08060C'), 0.65)
    if B:
        cv.paint(grow(pl, 2.6 * ss), SHEET * 0.95)
        cv.paint(pl, TONER)
    else:
        cv.paint(extrude(grow(pl, 2.4 * ss), 3.0 * ss, 3.6 * ss), TONER)
        cv.paint(grow(pl, 2.4 * ss), TONER)
        cv.paint(plate_shift(pl, cv, -3.6, 3.0), CYN)
        cv.paint(pl, SHEET * 0.97)
        cl = copier_edge(cv, pl, 6, 3.5, 0.9, (-0.3, 1.0))
        cv.paint(cl, TONER)
    cx_, cy_ = 28 + 24 + 8, 948 + 24 + 41
    disc = rough(circle(cv, cx_, cy_, 24), cv, 0.6, 6.0, 3)
    cv.paint(extrude(grow(disc, 2.0 * ss), 2.6 * ss, 3.0 * ss), TONER)
    cv.paint(grow(disc, 2.0 * ss), TONER)
    ink(cv, plate_shift(disc, cv, 2.4, 2.0), MAG, 0.03, 3)
    ink(cv, disc, MAG, 0.03, 4)
    cm_ = T.glyph_mask('WC2_CREST', 32, cv, cx_, cy_)
    cv.paint(extrude(grow(cm_, 1.2 * ss), 1.8 * ss, 2.0 * ss), TONER)
    cv.paint(grow(cm_, 1.2 * ss), TONER)
    cv.paint(cm_, WH)
    gcol = SHEET if B else TONER
    if nw:
        for q in range(9):
            xq = 128 + q * 9 + (q // 5) * 8
            cv.paint(rect(cv, xq, cy_ - 22, xq + 4.4, cy_ - 2), MAG)
        cv.paint(rect(cv, 126, cy_ + 13, 212, cy_ + 19), gcol, 0.85)
    else:
        xtext(cv, 'CELL-9', 160, cy_ - 11, 40, ANTON, fill=gcol if not B else WH, off=(2.2, 2.2), off_col=MAG, rot=-1.5, wob=0.2, track=0.8, seed=2)
        xtext(cv, '// BREAKER', 160, cy_ + 20, 22, PLEX, fill=gcol, rot=-1.0, wob=0.1, seed=3, grain=0.0)
    return cv.to_image(scale=scale), (x0, y0)
