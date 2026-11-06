"""wp_ui: YOU strip, SEND IT, nameplate in WPAP FACETED (same positions and information as st_ui)."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from st_gfx import Cv, poly, circle, blur, grow, shrink, shift, extrude, hatch_mask, ANTON, MONO
import st_tower as T
import wp_lib as L
from wp_lib import WINK, facet_assign
from wp_cards import wtext, plate, c01, FD_PLEX


def facets_in(cv, m, ramp, seed, **kw):
    ys, xs = np.nonzero(m > 0.5)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sub = m[y0:y1, x0:x1]
    rgb, ids, n = facet_assign(sub, cv.ss, ramp, seed, **kw)
    full = np.zeros((cv.H, cv.W, 3), np.float32)
    full[y0:y1, x0:x1] = rgb / 255.0
    cv.paint(m, full)


def you_strip(f, ss=3, nw=False):
    P = L.P()
    x0, y0, w, h = 1068, 96, 346, 52
    cv = Cv(x0, y0, w, h, ss)
    pl = poly(cv, [(1074, 100), (1409, 97), (1405, 146), (1071, 149)])
    ex = extrude(pl, 3.0 * ss, 3.4 * ss)
    cv.paint(blur(ex, 0.3 * ss) * (1 - pl), c01(L.PINK_))
    cv.paint(blur(grow(pl, 1.8 * ss), 0.3 * ss), c01(WINK))
    cv.paint(blur(pl, 0.3 * ss), c01((34, 12, 58)))
    if nw:
        for q in range(3):
            cv.paint(blur(poly(cv, [(1086 + q * 9, 112), (1091 + q * 9, 112), (1091 + q * 9, 136), (1086 + q * 9, 136)]), 0.3 * ss), c01(L.PINK_))
    else:
        wtext(cv, 'YOU', x0 + 39, y0 + 26, 30, ANTON, fill=(255, 255, 255), drop=(2.0, 2.4), dcol=L.PINK_, rot=-2, track=0.6)
    xs = x0 + 72
    wseg, hseg, pitch = 12.6, 17, 15.6
    n_pend = f['hp'] - f['pv']['hp_after']
    n_lit = f['pv']['hp_after']
    segs = [xs + g * (5 * pitch + 8) + k * pitch for g in range(3) for k in range(5)]
    cy = y0 + 27
    for i, xx in enumerate(segs):
        m = poly(cv, [(xx + 2.2, cy - hseg / 2), (xx + wseg + 2.2, cy - hseg / 2), (xx + wseg - 2.2, cy + hseg / 2), (xx - 2.2, cy + hseg / 2)])
        cv.paint(blur(grow(m, 1.5 * ss), 0.3 * ss), c01(WINK))
        if i < n_lit:
            cv.paint(blur(m, 0.3 * ss), c01((123, 224, 123)))
            top = poly(cv, [(xx + 2.2, cy - hseg / 2), (xx + wseg + 2.2, cy - hseg / 2), (xx + wseg, cy - 1.5), (xx + 0.2, cy - 1.5)]) * m
            cv.paint(blur(top, 0.3 * ss), c01((196, 250, 196)))
        elif i < n_lit + n_pend:
            cv.paint(blur(m, 0.3 * ss), c01((34, 12, 24)))
            hm = hatch_mask(cv, m, (45, 135), 3.7, 1.15, 0.0, seed=300 + i)
            cv.paint(blur(hm, 0.25 * ss), c01((255, 68, 51)))
            cv.paint(blur(np.clip(m - shrink(m, 1.3 * ss), 0, 1), 0.2 * ss), c01((255, 68, 51)))
        else:
            cv.paint(blur(m, 0.3 * ss), c01((20, 12, 34)))
    return cv.to_image(), (x0, y0)


def send_it(variant='A', ss=3, scale=1, nw=False):
    P = L.P()
    x0, y0, w, h = 1640, 880, 275, 150
    cv = Cv(x0, y0, w, h, ss)
    slab = poly(cv, [(1672, 918), (1880, 913), (1892, 930), (1890, 1000), (1676, 1006), (1662, 990), (1664, 930)])
    ex = extrude(grow(slab, 3.0 * ss), 6.0 * ss, 7.0 * ss)
    cv.paint(blur(ex, 0.3 * ss), c01(L.PINK_))
    cv.paint(blur(extrude(grow(slab, 3.0 * ss), 9.0 * ss, 10.5 * ss) * (1 - extrude(grow(slab, 3.0 * ss), 6.0 * ss, 7.0 * ss)), 0.3 * ss), c01(WINK))
    cv.paint(blur(grow(slab, 3.2 * ss), 0.3 * ss), c01(WINK))
    cv.paint(blur(grow(slab, 1.4 * ss), 0.3 * ss), c01(L.WHITE_))
    facets_in(cv, slab, P['slab'], seed=77, k=5, accent=P['accent'], accent_max=0.2, glint=P['glint'], glint_max=0.1, minfrac=0.06, spread=0.4)
    # white chevrons
    for (ax, ay, sg) in ((1686, 960, 1), (1870, 960, -1)):
        pts = [(ax + sg * 4, ay - 11), (ax + sg * 15, ay), (ax + sg * 4, ay + 11), (ax + sg * 0, ay + 11), (ax + sg * 11, ay), (ax + sg * 0, ay - 11)]
        m = poly(cv, pts)
        cv.paint(blur(grow(m, 1.4 * ss), 0.3 * ss), c01(WINK))
        cv.paint(blur(m, 0.3 * ss), c01(L.WHITE_))
    if nw:
        Pa = [(1735, 946), (1790, 946), (1790, 930), (1830, 959), (1790, 988), (1790, 972), (1735, 972)]
        m = poly(cv, Pa)
        cv.paint(blur(grow(m, 2.6 * ss), 0.3 * ss), c01(WINK))
        cv.paint(blur(m, 0.3 * ss), c01(L.WHITE_))
    else:
        wtext(cv, 'SEND IT', 1777, 959, 64, ANTON, fill=(255, 255, 255), ink=WINK, ink_w=2.8, drop=(4.6, 5.2), dcol=WINK, rot=-2.2, track=1.5)
    return cv.to_image(scale=scale), (x0, y0)


def nameplate(variant='A', ss=3, scale=1, nw=False):
    P = L.P()
    x0, y0, w, h = 14, 948, 250, 126
    cv = Cv(x0, y0, w, h, ss)
    pl = poly(cv, [(36, 975), (236, 968), (244, 1000), (240, 1050), (44, 1057), (32, 1030)])
    ex = extrude(pl, 4.0 * ss, 5.0 * ss)
    cv.paint(blur(ex, 0.3 * ss) * (1 - pl), c01(L.PINK_))
    cv.paint(blur(grow(pl, 2.2 * ss), 0.3 * ss), c01(WINK))
    cv.paint(blur(pl, 0.3 * ss), c01((34, 12, 58)))
    # accent underline plane
    ul = poly(cv, [(34, 1040), (242, 1033), (240, 1050), (44, 1057), (32, 1048)]) * pl
    cv.paint(blur(ul, 0.3 * ss), c01(P['accent']))
    cx_, cy_ = 60, 1008
    def octa(r, rot=22.5):
        return [(cx_ + r * math.cos(math.radians(rot + 45 * k)), cy_ + r * math.sin(math.radians(rot + 45 * k))) for k in range(8)]
    seat = poly(cv, octa(25))
    cv.paint(blur(extrude(grow(seat, 2.0 * ss), 2.4 * ss, 3.0 * ss), 0.3 * ss), c01(WINK))
    cv.paint(blur(grow(seat, 2.2 * ss), 0.3 * ss), c01(WINK))
    facets_in(cv, seat, P['hub'], seed=19, k=3, accent=P['accent'], accent_max=0.3, glint=P['glint'], glint_max=0.2, minfrac=0.1)
    cm_ = T.glyph_mask('WC2_CREST', 31, cv, cx_, cy_)
    cv.paint(blur(shift(cm_, 1.6 * ss, 1.8 * ss), 0.3 * ss), c01(L.PINK_))
    cv.paint(blur(grow(cm_, 1.3 * ss), 0.3 * ss), c01(WINK))
    cv.paint(blur(cm_, 0.3 * ss), c01(L.WHITE_))
    if nw:
        for q in range(9):
            xq = 100 + q * 9 + (q // 5) * 8
            cv.paint(blur(poly(cv, [(xq, 984), (xq + 4, 984), (xq + 4, 1006), (xq, 1006)]), 0.3 * ss), c01(L.PINK_))
    else:
        wtext(cv, 'CELL-9', 155, 995, 36, ANTON, fill=(255, 255, 255), drop=(2.6, 3.0), dcol=L.PINK_, rot=-2, track=0.8)
        wtext(cv, '// BREAKER', 160, 1027, 21, FD_PLEX, fill=(246, 240, 228), rot=-1.6, track=0.6)
    return cv.to_image(scale=scale), (x0, y0)
