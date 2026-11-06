"""f1_board: the F1 board grammar on top of the grammar-stream patches (gram.py): dot ration, time marks, ticket queue, ring tags, cold chevrons.
Import AFTER f1_geo and gram_render."""
import sys, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
import gram as G
import gram_render as GR
from gram import *
from gramlib import *
import wr_units as WU
import wr2_units as W2U
import r2_misc as M2
import r2_glyphs as RG
import o_misc as OM
import cv_board as CB
from cv_lib import C, ppx, NOW

COLD_CHEV = (217, 135, 124)          # #D9877C, R51 review: lifted so cold chevrons never read brown
_orig_grade = G.grade


def grade2(c, k, bed=BED):
    if k == 1 and tuple(c[:3]) == tuple(HARM_UP):
        return COLD_CHEV
    return _orig_grade(c, k, bed)


G.grade = grade2
GR.grade = grade2


# ------------------------------------------------------------------ cell outline (E): solid, time by value; never dotted
def outline(L, u, col=None, w=None):
    if col is not None:
        return G.ORIG['outline'](L, u, col, w)
    k = u['dep']
    poly = WU.u_poly(u)
    pp = poly + [poly[0]]
    c = grade2(ENAMEL, k)
    ww = (4.0, 2.4, 1.6)[k]
    L.line(pp, INK, ww + 4.5 if k < 2 else 5.4)
    if k == HOT:
        glow_line(L, pp, ENAMEL, ww + 3, blur=4, strength=0.40)
    L.line(pp, ENAMEL if k == HOT else c, ww)
    (x, y), a = G.cell_marker_pos(u)
    if k == HOT:
        end_notch(L, x, y, 0, col=ENAMEL, s=5.6)
    else:
        pips(L, x - (5 * (k - 1)), y, k, 90, 10.0, 3.0)


def tok_ring(L, x, y, R, dep, dead=False):
    col = (150, 150, 160) if dead else grade2(ENAMEL, dep)
    w = (3.0, 2.4, 1.8)[dep]
    WU._ring_full(L, x, y, R - w / 2, w, col)


W2U.outline = outline
W2U.ring = tok_ring


# ------------------------------------------------------------------ landing arc frame: HOT bold + glow + notch, COLD thin solid, FAR dotted (a mark, allowed)
def a2_frame(L, r, a0, a1, lane, opt):
    k = G.CUR['k']
    HALF = G.A2.HALF
    da = 57.3 / r
    cap = HALF * da
    n = max(8, int((a1 - a0) / 3))
    ae = a1 - 0.9 * HALF * da
    outer = [ppx(C, r + HALF, a0 + cap + (ae - a0 - cap) * i / n) for i in range(n + 1)]
    inner = [ppx(C, r - HALF, ae - (ae - a0 - cap) * i / n) for i in range(n + 1)]
    tipp = [ppx(C, r, a1)]
    start = [ppx(C, r + HALF * math.cos(math.radians(t)), a0 + cap - cap * math.sin(math.radians(t))) for t in range(0, 181, 20)]
    pts = outer + tipp + inner + start
    L.poly(pts, fill=(7, 9, 17, 214))
    c = grade2(ENAMEL, k)
    ww = (3.0, 2.0, 1.6)[k]
    L.line(pts + [pts[0]], INK, 6.4 if k < 2 else 5.4)
    if True:
        if k == HOT:
            glow_line(L, pts + [pts[0]], ENAMEL, 5, blur=4, strength=0.35)
        L.line(pts + [pts[0]], ENAMEL if k == HOT else c, ww)


G.a2_frame = a2_frame
G.A2.frame = a2_frame


# ------------------------------------------------------------------ ring tags: solid hairlines (the dot ration)
def ring_tags(L, f, opt):
    if not NOW['words']:
        return GR.ORIG_TAGS(L, f, opt)
    for d in range(3):
        w_ = f['rings_wave'][d]
        x, y, wd, depth, wv = M2.tag_geom(L, d, w_, opt)
        c = grade2(ENAMEL, d)
        box = [x - wd / 2, y - 13, x + wd / 2, y + 13]
        L.rect(box, fill=(8, 10, 18, 250), outline=INK, w=5.0, r=6)
        if d == 0:
            glow_line(L, [(box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3]), (box[0], box[1])], ENAMEL, 5, blur=3, strength=0.3)
        L.rect(box, outline=ENAMEL if d == 0 else c, w=(2.6, 1.8, 1.4)[d], r=6)
        tx0 = x - wd / 2 + 9
        if depth.startswith('+'):
            OM.plus_glyph(L, tx0 + 3, y, c, 4.2, 2.4)
            tx0 += 10
            txt = depth[1:] + ((' ' + wv) if wv else '')
        else:
            txt = depth + ((' ' + wv) if wv else '')
        L.text((tx0, y + 1), txt, 20, 'anton', fill=c, anchor='lm', stroke=1.4)
        if d == 0:
            end_notch(L, box[0] - 9, y, 90, col=ENAMEL, s=5.2)
        else:
            for i in range(d):
                xx = box[0] - 8 - 10 * i
                L.ellipse([xx - 4.6, y - 4.6, xx + 4.6, y + 4.6], fill=INK)
                L.ellipse([xx - 3.0, y - 3.0, xx + 3.0, y + 3.0], fill=TMID)


M2.ring_tags = ring_tags
GR.A.M2.ring_tags = ring_tags


# ------------------------------------------------------------------ wave queue: 84 x 64 tickets, 24 px glyphs, solid edges, time by value + pips, one neutral L5 feed
def ticket(L, box, edge, cut, fill=GUN_A):
    x0, y0, x1, y1 = box
    if cut:
        pts = [(x0 + 3, y0), (x1 - 16, y0), (x1, y0 + 16), (x1, y1 - 3), (x1 - 3, y1), (x0 + 3, y1), (x0, y1 - 3), (x0, y0 + 3)]
    else:
        pts = [(x0 + 4, y0), (x1 - 4, y0), (x1, y0 + 4), (x1, y1 - 4), (x1 - 4, y1), (x0 + 4, y1), (x0, y1 - 4), (x0, y0 + 4)]
    L.poly(pts, fill=fill + (255,))
    L.line(pts + [pts[0]], INK, 4.6)
    L.line(pts + [pts[0]], edge, 1.6)                                       # solid edge, never dotted
    L.line([(x0 + 6, y0 + 3.5), (x1 - (18 if cut else 6), y0 + 3.5)], (10, 12, 16), 1.4)      # L4 engraved groove
    L.line([(x0 + 6, y0 + 4.9), (x1 - (18 if cut else 6), y0 + 4.9)], GUN_HI, 1.0)


def queue_tickets(L, f, arcs):
    fut = [a for a in arcs if a['state'] == 'future']
    order = list(reversed(fut))             # W6 (far) left ... W4 (next) right
    x = 24
    tw_, th_ = 84, 64
    y0 = 24
    vals = {0: 1.0, 1: 0.70, 2: 0.50}
    for i, a in enumerate(order):
        n = a['wave'] + 1
        j = len(order) - 1 - i                # 0 = next to enter
        val = vals.get(j, 0.5)
        sc = lambda c: tuple(int(BED[q] + (c[q] - BED[q]) * val) for q in range(3))
        box = [x, y0, x + tw_, y0 + th_]
        ticket(L, box, sc((217, 225, 234)), bool(a.get('climax')))
        if NOW['words']:
            L.text((x + 9, y0 + 17), 'W%d' % n, 16, 'mono', fill=sc((235, 240, 248)), anchor='lm')
        units = a['units']
        slot = (tw_ - 10) / max(1, len(units))
        for ui, (kind, wd) in enumerate(units):
            cx = x + 5 + slot * ui + slot / 2
            RG.kind_glyph(L, kind, 24, (cx, y0 + 36), sc((235, 240, 248)))
            bw = 4
            bx0 = cx - (wd * bw + (wd - 1) * 1.6) / 2
            for b in range(wd):
                L.rect([bx0 + b * (bw + 1.6), y0 + 51, bx0 + b * (bw + 1.6) + bw, y0 + 54.4], fill=sc((226, 233, 242)) + (255,), r=1)
        for p in range(j):                    # turn pips: +1 one, +2 two
            px = x + tw_ - 12 - p * 10
            L.ellipse([px - 4.6, y0 + 17 - 4.6, px + 4.6, y0 + 17 + 4.6], fill=INK)
            L.ellipse([px - 3.0, y0 + 17 - 3.0, px + 3.0, y0 + 17 + 3.0], fill=TMID)
        if a.get('climax'):
            for t in range(3):
                bx = x + 9 + t * 9
                L.poly([(bx, y0 + th_ - 3), (bx + 4, y0 + th_ - 3), (bx + 7, y0 + th_ - 8.5), (bx + 3, y0 + th_ - 8.5)], fill=SCHED, outline=INK_, w=1.0)
        x += tw_ + 8
    return x


INK_ = (12, 10, 22)


def queue_feed(L, x_end):
    p0 = (x_end + 4, 56)
    p1 = ppx(C, 492, -19.0)
    GR.arrowed(L, [p0, p1], w=12.0, col=ENAMEL, pitch=18.0, head=16.0)


def future(L, f, arcs, sel):
    xe = queue_tickets(L, f, arcs)
    queue_feed(L, xe - 8)
    return []


GR.A.M2.future = future
M2.future = future


# ------------------------------------------------------------------ E material: slate glass, enamel edge, a double-helix rule at ~7 percent, value by time
import wr2_cells as W2C
import wr_cells as WCL
from wr_geo import *
from wr2_lib import *

VAL = (1.0, 0.80, 0.62)           # R51 review: ring +1 glass at 80 percent value, +2 at 62 percent


def _mixc(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def helix(L, u_or_cell, wash, dep, b0, b1):
    ra, rb = radial_ext(dep)
    rm = (ra + rb) / 2
    amp = min(7.0, (rb - ra) * 0.17)
    col = _mixc(wash, (217, 225, 234), 0.13)
    n = 70
    for ph in (0.0, math.pi):
        pts = []
        for i in range(n + 1):
            t = i / n
            a = b0 + 7 + (b1 - b0 - 14) * t
            rr = rm + amp * math.sin(t * math.pi * 5 + ph)
            pts.append(ppx(C, rr, a))
        L.line(pts, col, 1.1)
    for i in range(1, 15):
        t = i / 15.0
        a = b0 + 7 + (b1 - b0 - 14) * t
        s1 = math.sin(t * math.pi * 5)
        r1, r2 = rm + amp * s1, rm - amp * s1
        L.line([ppx(C, r1, a), ppx(C, r2, a)], _mixc(wash, (217, 225, 234), 0.07), 0.9)


def screen(L, u):
    wash = G.kind_wash(u['kind'], u['dep'], ramp=(-0.06, 0.10, 0.26))
    lo = _mixc(wash, (6, 8, 18), 0.30)
    hi = tuple(min(255, int(c * 1.10)) for c in wash)
    WCL._gradient_fill(L, u, lambda t: _mixc(lo, hi, min(1.0, t * 1.1)))
    b0, b1 = unit_bounds(u)
    if u['w'] < 6:
        helix(L, u, wash, u['dep'], b0, b1)


def empty_cell(L, dep, s):
    b0, b1 = 60 * s - 30, 60 * s + 30
    v = VAL[dep]
    fill = tuple(int(BED[i] + ((38, 50, 70)[i] - BED[i]) * v) for i in range(3))
    poly = cell_poly(dep, b0, b1, kind='empty')
    L.poly(poly, fill=fill + (255,))
    L.line(poly + [poly[0]], _mixc(fill, (217, 225, 234), 0.22), 1.4)
    ra, rb = radial_ext(dep, 4, 4)
    L.line(L.arc_pts(C, rb, b0 + 5, b1 - 5), _mixc(fill, (170, 195, 230), 0.20), 1.6)
    helix(L, None, fill, dep, b0, b1)


W2C.screen = screen
W2C.empty_cell = empty_cell
GR.W2C.screen = screen
GR.W2C.empty_cell = empty_cell
