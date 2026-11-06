"""LATENT elements (not in the E10 state, designed in a lab frame): shield_bracket, ring_unit_wide6; plus lab-frame builders."""
import math, copy
import wr_state as ST
from wr_state import opt
from wr_geo import *

CYANC = (92, 225, 255)


def shield_bracket(L, u, r0, r1, shield, shmx):
    """cyan shield layer over the first shmx pips; it empties before the HP pips"""
    o = opt('shield_bracket')
    pips = ST.PIPS.get(u['id'])
    if o == 'E' or not pips:
        return
    first = pips[:shmx]
    if not first:
        return
    aa, ab = first[0][0], first[-1][1]
    rm = (r0 + r1) / 2
    live = shield
    if o == 'A':        # under-bar: a 4 px cyan bar under the first shmx pips; lost shield = a dashed hollow bar (the HP pips never move)
        ra, rb = r0 - 7.0, r0 - 2.6
        for i, p in enumerate(first):
            a0_, a1_ = p[0], p[1]
            if i < live:
                L.poly(arc_band(ra, rb, a0_, a1_), fill=CYANC + (255,), outline=INK_, w=1.2)
            else:
                dash_path(L, arc_band(ra, rb, a0_, a1_), CYANC, 1.6, 3.5, 2.5)
    elif o == 'B':      # sheath: a cyan ring around each shielded pip; a lost shield pip keeps a dashed ring
        for i, p in enumerate(first):
            a0_, a1_ = p[0], p[1]
            big = arc_band(r0 - 2.4, r1 + 2.4, a0_ - math.degrees(1.6 / rm), a1_ + math.degrees(1.6 / rm))
            if i < live:
                L.line(big + [big[0]], INK_, 5.8)
                L.line(big + [big[0]], CYANC, 2.4)
            else:
                dash_path(L, big, CYANC, 1.8, 3.2, 2.6)
    else:               # C second row: small cyan pips in their own tray under the HP row, one per shield point; lost = empty slot
        ra, rb = r0 - 9.0, r0 - 2.6
        for i, p in enumerate(first):
            a0_, a1_ = p[0], p[1]
            L.poly(arc_band(ra - 1.4, rb + 1.4, a0_ - 0.6, a1_ + 0.6), fill=(6, 12, 24, 255), outline=INK_, w=1.4)
            if i < live:
                L.poly(arc_band(ra, rb, a0_, a1_), fill=CYANC + (255,))


def lab_unit(uid, kind, dep, s, w, hp, mx, **kw):
    u = dict(id=uid, kind=kind, dep=dep, s=s, w=w, hp=hp, mx=mx, lose=[0, 0], sh=0, shmx=0, hit=2, df='plain', warded=False, consumed=False, trigdead=False,
             fate={'kind': 'waits', 'k': 1}, land_hit=None)
    u.update(kw)
    return u


def lab_frame(J, which):
    f = copy.deepcopy(J['f1'])
    f['_lab'] = True
    f['guns'] = []
    f['log'] = []
    if which == 'shield':
        f['units'] = [lab_unit(11, 'Jammer', 1, 4, 1, 3, 3, hit=2, sh=2, shmx=2),
                      lab_unit(12, 'Jammer', 2, 0, 1, 3, 3, hit=1, sh=1, shmx=2),
                      lab_unit(13, 'Jammer', 0, 2, 2, 5, 6, hit=2, sh=2, shmx=2, lose=[0, 1]),
                      lab_unit(14, 'Packet', 2, 3, 2, 6, 6, hit=2)]
        f['adj'] = dict(f['adj'], ring=1, s=0)
    elif which == 'wide6':
        f['units'] = [lab_unit(21, 'Ring', 1, 0, 6, 10, 12, hit=2, lose=[0, 2]), lab_unit(22, 'Packet', 0, 3, 1, 3, 3, hit=2)]
        f['adj'] = dict(f['adj'], ring=2, s=3)
    elif which == 'strike':
        f['units'] = [lab_unit(31, 'Packet', 0, 4, 2, 5, 6, hit=2), lab_unit(32, 'Worm', 2, 5, 1, 3, 3, hit=2)]
        f['adj'] = dict(f['adj'], ring=1, s=2, df='armor', strike=True, hit=3, phase=2, hp_after=10)
    elif which == 'place':
        f['units'] = [lab_unit(51, 'Packet', 0, 0, 1, 3, 3, hit=2), lab_unit(52, 'Worm', 0, 1, 2, 5, 6, hit=2, lose=[0, 1]), lab_unit(53, 'Payload', 0, 3, 3, 9, 9, hit=2),
                      lab_unit(54, 'Ring', 1, 0, 6, 10, 12, hit=2, lose=[0, 1]), lab_unit(55, 'Packet', 2, 1, 1, 3, 3, hit=2), lab_unit(56, 'Jammer', 2, 3, 2, 5, 6, hit=3)]
        f['adj'] = dict(f['adj'], ring=2, s=5)
    elif which == 'kinds':
        f['units'] = [lab_unit(61, 'Packet', 0, 0, 1, 3, 3, hit=2), lab_unit(62, 'Worm', 0, 1, 1, 3, 3, hit=2), lab_unit(63, 'Payload', 0, 2, 1, 4, 4, hit=2, df='armor'),
                      lab_unit(64, 'Jammer', 0, 3, 1, 3, 3, hit=2, sh=2, shmx=2),
                      lab_unit(65, 'Jammer', 1, 0, 1, 3, 3, hit=2), lab_unit(66, 'Payload', 1, 1, 1, 4, 4, hit=2), lab_unit(67, 'Worm', 1, 2, 1, 3, 3, hit=2), lab_unit(68, 'Packet', 1, 3, 1, 3, 3, hit=2),
                      lab_unit(69, 'Ring', 2, 0, 6, 12, 12, hit=2)]
        f['adj'] = dict(f['adj'], ring=1, s=4)
    elif which == 'glyphs':
        f['units'] = [lab_unit(41, 'Jammer', 0, 0, 1, 3, 3, hit=2), lab_unit(42, 'Ring', 1, 1, 6, 12, 12) if False else lab_unit(42, 'Packet', 1, 2, 1, 3, 3),
                      lab_unit(43, 'Worm', 2, 4, 1, 3, 3), lab_unit(44, 'Payload', 0, 3, 1, 4, 4, df='armor')]
        f['adj'] = dict(f['adj'], ring=2, s=1)
    return f


def wide6(L, u, f):
    """a unit that covers the whole ring: ONE band with a clear start (token + HP start there) and clockwise travel"""
    import wr_units as WU
    o = opt('ring_unit_wide6')
    if o in ('R', 'V'):
        import wr2_latent as W2L
        return W2L.wide6(L, u, f)
    dep = u['dep']
    ri, ro = CB.ring_geom(dep)
    b0 = 60 * u['s'] - 30
    wash = kind_wash(u['kind'], dep)
    lane = LANE[dep]
    if o == 'E':
        lit_e = __import__('e10lib').lit_cell
        lit_e(L, u)
        E8.cell_outline(L, u)
        E8.token(L, u)
        E8.hp_row(L, u, u['hp'], u['mx'], lose=u['lose'][1])
        __import__('e10lib').chevrons_h(L, u, u['hit'], 0)
        return
    ra, rb = radial_ext(dep)
    gap = 14.0 if o == 'A' else (0.0 if o == 'B' else 10.0)
    if o == 'C':
        # tail end tapers to a point (clockwise travel), head end is square
        pass
    poly = cell_poly(dep, b0, b0 + 360, kind='unit', n=170) if o != 'B' else cell_poly(dep, b0 + 0.01, b0 + 359.99, kind='unit', n=170)
    if o == 'B':
        # B continuous annulus: two rings, no ends at all; a start TAB (a notch cut into the outer edge) marks the start
        outer = L.arc_pts(C, rb, b0, b0 + 360, 180)
        inner = L.arc_pts(C, ra, b0, b0 + 360, 180)
        L.poly(L.band(C, ra, rb, b0, b0 + 359.9), fill=wash + (255,))
        for rr in (ra, rb):
            pts = L.arc_pts(C, rr, b0, b0 + 360, 180)
            L.line(pts, INK_, lane['w'] + 4.5)
            L.line(pts, lane['col'], lane['w'])
        for q in range(6):                 # sector ticks on the outer edge (so the six sectors still count)
            a = b0 + 60 * q
            x0, y0 = ppx(C, rb - 7, a); x1, y1 = ppx(C, rb, a)
            L.line([(x0, y0), (x1, y1)], INK_, 3.2)
        a = b0
        tab = [ppx(C, ra - 1, a - 1.6), ppx(C, rb + 1, a - 1.6), ppx(C, rb + 1, a + 1.6), ppx(C, ra - 1, a + 1.6)]
        L.poly(tab, fill=lane['col'] + (255,), outline=INK_, w=1.8)
    else:
        L.poly(poly, fill=wash + (255,))
        L.line(poly + [poly[0]], INK_, lane['w'] + 4.5)
        L.line(poly + [poly[0]], lane['col'], lane['w'])
        if o == 'A':        # seam: square lane-colour end caps with a clear gap, token at the start cap
            for a, sg in ((b0 + dA(ra, 8), 1), (b0 + 360 - dA(ra, 8), -1)):
                cap = [ppx(C, ra, a), ppx(C, rb, a), ppx(C, rb, a + sg * math.degrees(7 / rb)), ppx(C, ra, a + sg * math.degrees(7 / ra))]
                L.poly(cap, fill=lane['col'] + (255,), outline=INK_, w=1.8)
        else:               # C: a head chevron at the clockwise end shows the way it travels
            a = b0 + 360 - dA(ra, 8)
            tip = [ppx(C, ra, a - 4), ppx(C, (ra + rb) / 2, a + 2.5), ppx(C, rb, a - 4)]
            L.line(tip, INK_, 8.5)
            L.line(tip, lane['col'], 4.5)
    WU.token(L, u)
    saved = ST.OPT.get('unit_hp_row', 'E')
    if saved == 'E':
        ST.OPT['unit_hp_row'] = 'A'
    WU.hp_row(L, u, u['hp'], u['mx'], lose=u['lose'][1])
    ST.OPT['unit_hp_row'] = saved
    WU.chevrons(L, u, u['hit'], 0)
