"""lc_ui: the player-owned UI pieces in linocut: YOU strip, SEND IT slab, nameplate.  Same screen rects and game data as st_ui (the F1 versions)."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from f1_lib import Canvas, pol, smooth, outline_mask, font, ANTON_F
from lc_lib import *
import lc_tower as LT
import lc_cards as LC

GAIN = (123, 224, 123)
HARM = (255, 68, 51)
sh, text_m = LC.sh, LC.text_m


def _rect(cv, r, x0, y0, x1, y1, step=(9, 17), amp=1.0):
    a = jag_path((x0, y0), (x1, y0), r, step, amp)
    b = jag_path((x1, y0), (x1, y1), r, step, amp)[1:]
    c = jag_path((x1, y1), (x0, y1), r, step, amp)[1:]
    d = jag_path((x0, y1), (x0, y0), r, step, amp)[1:-1]
    return a + b + c + d


def _quad(cv, r, P, step=(9, 17), amp=1.0):
    out = []
    for i in range(4):
        seg = jag_path(P[i], P[(i + 1) % 4], r, step, amp)
        out += seg[:-1] if i < 3 else seg[:-1]
    return out


def _img(cv, x0, y0, seed):
    return print_texture(cv.down(), seed=seed, dens=0.006, pink_dens=0.004), (x0, y0)


def you_strip(f, ss=3, nw=False):
    x0, y0, w, h = 1068, 96, 346, 52
    cv = Canvas(w, h, 3, seed=17)
    S = 3
    r = cv.r
    v = LT.VARIANT[0]
    body = cv.poly_mask(_rect(cv, r, 8, 6, w - 8, h - 5, (9, 16), 1.0))
    cv.over(sh(ndi.binary_dilation(body > 0.5, iterations=int(1.8 * S)).astype(np.float32), -2.4, 2.0, S), HOT if v == 'A' else BONE, 1.0)
    cv.over(ink_grain(cv, body, 0.4), BONE if v == 'A' else KEY, 1.0)
    fg = KEY if v == 'A' else BONE
    if nw:
        for q in range(3):
            st = cv.poly_mask([(30 + q * 9, 14), (34 + q * 9, 14), (34 + q * 9, 38), (30 + q * 9, 38)])
            cv.over(st, HOT, 1.0)
    else:
        tm, _ = text_m(cv, 'YOU', (40, 27), 29, ANTON_F, 1.0, rot=2.0)
        cv.over(sh(tm, 1.8, 1.8, S), HOT, 1.0)
        cv.over(tm, fg, 1.0)
    xs = 72
    wseg, hseg, pitch = 12.6, 17, 15.6
    n_pend = f['hp'] - f['pv']['hp_after']
    n_lit = f['pv']['hp_after']
    yy, xx = np.mgrid[0:cv.H, 0:cv.W].astype(np.float32)
    i = 0
    for g in range(3):
        for k in range(5):
            bx = xs + g * (5 * pitch + 8) + k * pitch
            m = cv.poly_mask(jag_path((bx, 27 - hseg / 2), (bx + wseg, 27 - hseg / 2), r, (20, 30), 0.0)
                             + jag_path((bx + wseg, 27 - hseg / 2), (bx + wseg, 27 + hseg / 2), r, (20, 30), 0.0)[1:]
                             + jag_path((bx + wseg, 27 + hseg / 2), (bx, 27 + hseg / 2), r, (20, 30), 0.0)[1:]
                             + jag_path((bx, 27 + hseg / 2), (bx, 27 - hseg / 2), r, (20, 30), 0.0)[1:-1])
            ring = np.clip(outline_mask(m, S, 1.6), 0, 1)
            key_ring = KEY if v == 'A' else BONE
            lit = i < n_lit
            cv.over(ring, key_ring, 1.0)
            if lit:
                cv.over(m, GAIN, 1.0)
                inner = ndi.binary_erosion(m > 0.5, iterations=int(1.2 * S)).astype(np.float32)
                cv.over(ndi.gaussian_filter(np.clip(inner - sh(inner, 1.6, 1.6, S), 0, 1), 0.3 * S), (230, 255, 230), 0.8)
            elif i < n_lit + n_pend:
                cv.over(m, (40, 12, 16), 1.0)
                px = 4.2 * S
                hx = (((xx + yy) % px) < 1.3 * S) | (((xx - yy) % px) < 1.3 * S)
                inner = ndi.binary_erosion(m > 0.5, iterations=int(0.9 * S)).astype(np.float32)
                cv.over(hx.astype(np.float32) * inner, HARM, 1.0)
                cv.over(np.clip(m - inner, 0, 1), HARM, 1.0)
            else:
                cv.over(m, (30, 24, 36) if v == 'A' else (60, 52, 70), 0.9)
            i += 1
    return _img(cv, x0, y0, 31)


def send_it(variant='A', ss=3, scale=1, nw=False):
    x0, y0, w, h = 1640, 880, 275, 150
    cv = Canvas(w, h, 3, seed=9)
    S = 3
    r = cv.r
    v = LT.VARIANT[0]
    ox, oy = 1666 - x0, 918 - y0
    P = [(26, 40), (248, 36), (252, 122), (24, 126)]
    slab = cv.poly_mask(_quad(cv, r, P, (8, 15), 1.6))
    halo = sh(ndi.binary_dilation(slab > 0.5, iterations=int(4.0 * S)).astype(np.float32), -5.5, 5.0, S)
    cv.over(ndi.gaussian_filter(sh(slab, 4, 6, S), 3.0 * S), (6, 4, 12), 0.6)
    cv.over(halo, HOT if v == 'A' else BONE, 1.0)
    cv.over(ink_grain(cv, slab, 0.5), KEY if v == 'A' else HOT, 1.0)
    # carved rays out of the slab's end caps
    rays = []
    for q in range(34):
        side = -1 if q % 2 else 1
        cx = 36 if side < 0 else 240
        cy = 81
        a = math.radians(r.uniform(-75, 75) + (180 if side > 0 else 0))
        r0 = r.uniform(4, 14)
        r1 = r0 + r.uniform(12, 34)
        rays.append((cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + r1 * math.cos(a), cy + r1 * math.sin(a), r.uniform(1.6, 3.4), 0))
    cv.over(lens_mask(cv, rays) * slab, HOT if v == 'A' else KEY, 0.95)
    # frame line cut inside the slab
    fin = ndi.binary_erosion(slab > 0.5, iterations=int(5 * S)).astype(np.float32)
    fin2 = ndi.binary_erosion(slab > 0.5, iterations=int(7.4 * S)).astype(np.float32)
    cv.over(np.clip(fin - fin2, 0, 1), BONE if v == 'A' else KEY, 0.9)
    if nw:
        arrow = [(94, 70), (146, 70), (146, 54), (186, 82), (146, 110), (146, 94), (94, 94)]
        am = cv.poly_mask(arrow)
        cv.over(sh(am, 3.0, 3.0, S), HOT if v == 'A' else KEY, 1.0)
        cv.over(am, BONE, 1.0)
    else:
        tm, _ = text_m(cv, 'SEND IT', (137, 81), 62, ANTON_F, 2.0, rot=2.2)
        tm = np.clip(ndi.gaussian_filter(tm, 0.25 * S) * 1.2, 0, 1)
        cv.over(sh(tm, 3.2, 3.2, S), HOT if v == 'A' else KEY, 1.0)
        cv.over(tm, BONE, 1.0)
    return _img(cv, x0, y0, 33)


def nameplate(variant='A', ss=3, scale=1, nw=False):
    x0, y0, w, h = 14, 948, 250, 126
    cv = Canvas(w, h, 3, seed=44)
    S = 3
    r = cv.r
    v = LT.VARIANT[0]
    body = cv.poly_mask(_rect(cv, r, 26, 24, 230, 106, (9, 16), 1.3))
    cv.over(ndi.gaussian_filter(sh(body, 3, 5, S), 3.0 * S), (6, 4, 12), 0.6)
    cv.over(sh(ndi.binary_dilation(body > 0.5, iterations=int(2.6 * S)).astype(np.float32), -3.0, 2.6, S), HOT if v == 'A' else BONE, 1.0)
    cv.over(ink_grain(cv, body, 0.5), BONE if v == 'A' else KEY, 1.0)
    fg = KEY if v == 'A' else BONE
    # crest: scissor-cut pink disc with the crest glyph in black, bone offset
    cx_, cy_ = 60, 66
    disc = cv.poly_mask(jag_disc((cx_, cy_), 24.0, r, (8, 13), 1.2))
    cv.over(sh(disc, 2.4, 2.4, S), KEY if v == 'A' else BONE, 1.0)
    cv.over(ink_grain(cv, disc, 0.4), HOT, 1.0)
    gm = LC.glyph_np('WC2_CREST', 34 * S)
    gp = LC.place(cv, gm, cx_, cy_)
    gp = LC.FT_solid(gp, S)
    cv.over(sh(gp, 1.6, 1.6, S), HOT_D, 1.0)
    cv.over(gp, KEY, 1.0)
    if nw:
        for q in range(9):
            xq = 118 + q * 9 + (q // 5) * 8
            st = cv.poly_mask([(xq, 36), (xq + 4, 36), (xq + 4, 62), (xq, 62)])
            cv.over(st, HOT, 1.0)
        bar = cv.poly_mask([(116, 76), (214, 75), (214, 88), (116, 89)])
        cv.over(bar, fg, 0.9)
    else:
        tm, _ = text_m(cv, 'CELL-9', (146, 50), 38, ANTON_F, 1.2, rot=2.0)
        cv.over(sh(tm, 2.2, 2.2, S), HOT, 1.0)
        cv.over(tm, fg, 1.0)
        tm, _ = text_m(cv, '// BREAKER', (146, 86), 23, LC.PLEX, 0.5, rot=1.0)
        tm = np.clip(ndi.gaussian_filter(tm, 0.22 * S) * 1.25, 0, 1)
        cv.over(tm, fg, 1.0)
    return _img(cv, x0, y0, 35)
