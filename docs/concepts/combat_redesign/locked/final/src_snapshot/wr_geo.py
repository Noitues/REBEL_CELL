"""Shared geometry for the wave-ring designs: constant-width gutters, continuous dash rhythm, lane styles."""
import math
import e8lib as E8
from e8lib import *
import cv_board as CB
from wr_state import opt

G_STD = 8.0                 # uniform gutter (radial and tangential), the ring_separators standard
INK_ = (12, 10, 22)
GUT_FILL = (15, 18, 30)     # gutter bed: one step lighter than the back plate (5, 6, 9)


def dA(r, g):
    return math.degrees((g / 2.0) / r)


def sep_mode():
    return opt('ring_separators')


def sep_G():
    return {'A': 8.0, 'B': 8.0, 'C': 10.0, 'R': 8.0, 'V': 8.0}.get(sep_mode(), None)


def cell_poly(dep, b0, b1, rin=0.0, rout=0.0, kind='unit', n=None, tin=0.0):
    """polygon of a cell between sector boundaries b0..b1 (deg, 60*s-30 ..).  E gutters: unit 4 px radial / 3 deg, empty 3 px / 1.5 deg.
    Standard gutters (ring_separators A/B/C): constant G px both ways (angular inset = G/2 at each radius)."""
    ri, ro = CB.ring_geom(dep)
    G = sep_G()
    if G is None:
        rad, ang = (4.0, 3.0) if kind == 'unit' else (3.0, 1.5)
        r_i, r_o = ri + rad + rin, ro - rad - rout
        a_in = a_out = ang
        a_in = a_out = ang + math.degrees(tin / ((r_i + r_o) / 2))
    else:
        r_i, r_o = ri + G / 2 + rin, ro - G / 2 - rout
        a_in, a_out = dA(r_i, G + 2 * tin), dA(r_o, G + 2 * tin)
    n = n or max(8, int((b1 - b0) / 2.2))
    out = [ppx(C, r_o, b0 + a_out + (b1 - b0 - 2 * a_out) * i / n) for i in range(n + 1)]
    inn = [ppx(C, r_i, b1 - a_in - (b1 - b0 - 2 * a_in) * i / n) for i in range(n + 1)]
    return out + inn


def unit_bounds(u):
    return 60 * u['s'] - 30, 60 * (u['s'] + u['w'] - 1) + 30


def unit_poly(u, rin=0.0, rout=0.0):
    b0, b1 = unit_bounds(u)
    if u['w'] == 6:
        ri, ro = CB.ring_geom(u['dep'])
        return None
    return cell_poly(u['dep'], b0, b1, rin, rout, 'unit')


def arc_band(r0, r1, a0, a1):
    n = max(6, int(abs(a1 - a0) / 2.0))
    return [ppx(C, r1, a0 + (a1 - a0) * i / n) for i in range(n + 1)] + [ppx(C, r0, a1 - (a1 - a0) * i / n) for i in range(n + 1)]


def resample(pts, step=2.0):
    out = [pts[0]]
    carry = 0.0
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg == 0:
            continue
        t = step - carry
        while t <= seg:
            out.append((x0 + (x1 - x0) * t / seg, y0 + (y1 - y0) * t / seg))
            t += step
        carry = seg - (t - step)
    out.append(pts[-1])
    return out


def dash_path(L, pts, col, w, dash, gap, closed=True, start=0.0):
    """continuous-rhythm dashes along a path (the dash phase never resets at polygon vertices); each dash is one smooth polyline"""
    if closed:
        pts = list(pts) + [pts[0]]
    rp = resample(pts, 1.0)
    period = dash + gap
    cur = []
    for i, p in enumerate(rp):
        ph = (i + start) % period
        if ph < dash:
            cur.append(p)
        else:
            if len(cur) > 1:
                L.line(cur, col, w)
            cur = []
    if len(cur) > 1:
        L.line(cur, col, w)


def lane_line(L, pts, dep, w=None, col=None, keyline=True, dash=None, closed=True):
    """one clean lane outline: ink keyline (+4.5 px) under the coloured line; +2 gets a continuous 12/8 rhythm"""
    lane = LANE[dep]
    c = col or lane['col']
    ww = w or lane['w']
    pp = list(pts) + ([pts[0]] if closed else [])
    if lane['dash'] is None and dash is None:
        if keyline:
            L.line(pp, INK_, ww + 4.5)
        L.line(pp, c, ww)
    else:
        dd = dash or (12, 8)
        if keyline:
            L.line(pp, INK_, ww + 4.5)
        dash_path(L, pts, c, ww, dd[0], dd[1], closed)


KIND_TABLE = {}


def kind_wash(kind, dep, ramp=None):
    base = KIND_TABLE.get(kind) or {'Packet': (128, 62, 104), 'Worm': (102, 66, 138), 'Jammer': (84, 86, 146), 'Payload': (126, 66, 92), 'Ring': (116, 70, 116)}[kind]
    k = (0.0, 0.20, 0.38)[dep] if ramp is None else ramp[dep]
    return tuple(int(round(v + ((10, 8, 30)[i] - v) * k)) for i, v in enumerate(base))


def mix(c0, c1, t):
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c0[:3], c1[:3]))


def band_poly(dep, b0, b1, ra, rb, G=None, kind='unit', tin=0.0):
    """cell sub-band between absolute radii ra..rb with the same side gutters as cell_poly"""
    Gx = sep_G()
    if Gx is None:
        ang = 3.0 if kind == 'unit' else 1.5
        a_in = ang + math.degrees(tin / ra); a_out = ang + math.degrees(tin / rb)
    else:
        a_in, a_out = dA(ra, Gx + 2 * tin), dA(rb, Gx + 2 * tin)
    n = max(8, int((b1 - b0) / 2.2))
    out = [ppx(C, rb, b0 + a_out + (b1 - b0 - 2 * a_out) * i / n) for i in range(n + 1)]
    inn = [ppx(C, ra, b1 - a_in - (b1 - b0 - 2 * a_in) * i / n) for i in range(n + 1)]
    return out + inn


def radial_ext(dep, rin=0.0, rout=0.0):
    ri, ro = CB.ring_geom(dep)
    G = sep_G()
    h = 4.0 if G is None else G / 2
    return ri + h + rin, ro - h - rout
