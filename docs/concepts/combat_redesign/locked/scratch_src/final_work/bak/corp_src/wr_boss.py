"""Adjuster (boss) element drawings: adjuster_cell, adjuster_diamond, adjuster_hp_bar, ward_arc, adjuster_armor_strike (latent)."""
import math
import wr_state as ST
from wr_state import opt
from wr_geo import *
import e8lib as _E8
from e10lib import adjuster_body, REG, REDC
import wr_units as WU

GOLD_HI = (255, 226, 120)
GOLD_DK = (150, 108, 14)


# ----------------------------------------------------------------------------- ward_arc
def ward_arc(L, f):
    o = opt('ward_arc')
    a = f['adj']
    if o in ('R', 'V'):
        import wr2_boss as W2B
        return W2B.ward_arc(L, f)
    if o == 'E':
        return _E8.ward_arc(L, f)
    if a['hp'] <= 0:
        return
    s = a['s']
    b0, b1 = 60 * s - 30, 60 * s + 30
    ri, ro = CB.ring_geom(0)
    if o == 'A':        # engraved strip: a 4 px gold line in the ring-NOW inner gutter (between the HP ring and ring 0), end ticks into the cell
        r = ri + 2.0
        pts = L.arc_pts(C, r, b0 + 2.5, b1 - 2.5, 40)
        L.line(pts, INK_, 8.2)
        L.line(pts, GOLD, 4.0)
        for ang in (b0 + 2.5, b1 - 2.5):
            x0, y0 = ppx(C, ri - 1, ang); x1, y1 = ppx(C, ri + 9, ang)
            L.line([(x0, y0), (x1, y1)], INK_, 7)
            L.line([(x0, y0), (x1, y1)], GOLD, 3.2)
    elif o == 'B':      # ward field: a row of gold studs along the same inner gutter (a dotted field, quieter than a line)
        r = ri + 2.0
        n = int(math.radians(b1 - b0 - 5) * r / 9)
        for i in range(n + 1):
            x, y = ppx(C, r, b0 + 2.5 + (b1 - b0 - 5) * i / n)
            L.ellipse([x - 3.6, y - 3.6, x + 3.6, y + 3.6], fill=GOLD, outline=INK_, w=1.6)
        for ang in (b0 + 2.5, b1 - 2.5):
            x, y = ppx(C, r, ang)
            L.ellipse([x - 5.4, y - 5.4, x + 5.4, y + 5.4], fill=GOLD, outline=INK_, w=2.0)
    else:               # C wedge: the warded sector is outlined in gold across the whole NOW ring (both spokes + a closing arc), so it reads as 'this sector'
        for ang in (b0, b1):
            x0, y0 = ppx(C, ri, ang); x1, y1 = ppx(C, ro, ang)
            L.line([(x0, y0), (x1, y1)], INK_, 7.4)
            L.line([(x0, y0), (x1, y1)], GOLD, 3.0)
        pts = L.arc_pts(C, ri + 1.5, b0, b1, 40)
        L.line(pts, INK_, 6.4)
        L.line(pts, GOLD, 2.6)


# ----------------------------------------------------------------------------- adjuster
def cell(L, a, ang):
    o = opt('adjuster_cell')
    ri, ro = CB.ring_geom(min(a['ring'], 2))
    if o == 'E':
        L.poly(L.band(C, ri + 4, ro - 4, ang - 27, ang + 27), fill=(32, 26, 8, 190))
        pts = L.band(C, ri + 4, ro - 4, ang - 27, ang + 27)
        L.line(pts + [pts[0]], INK, 7)
        L.line(pts + [pts[0]], GOLD, 4)
        return
    poly = cell_poly(a['ring'], ang - 30, ang + 30, kind='unit')
    ra, rb = radial_ext(a['ring'])
    b0, b1 = ang - 30, ang + 30
    if o == 'A':        # gold glass plate: warm brass gradient (never olive-black), one 3 px gold edge with ink, a hairline gold inner edge
        n = int((rb - ra) / 2.0) + 1
        for i in range(n):
            t = (i + 0.5) / n
            r0 = ra + (rb - ra) * i / n
            r1 = min(rb, ra + (rb - ra) * (i + 1) / n + 0.8)
            col = mix((70, 52, 14), (34, 26, 8), t)
            L.poly(band_poly(a['ring'], b0, b1, r0, r1), fill=col + (255,))
        L.line(poly + [poly[0]], INK_, 7.5)
        L.line(poly + [poly[0]], GOLD, 3.0)
        inner = cell_poly(a['ring'], b0, b1, 5, 5, kind='unit', tin=5)
        L.line(inner + [inner[0]], mix((50, 38, 10), GOLD, 0.55), 1.2)
    elif o == 'B':      # lock-on: dark brass glass, a hairline gold edge, heavy gold corner brackets (the boss is 'targeted', not 'a lane')
        L.poly(poly, fill=(38, 30, 10, 255))
        L.line(poly + [poly[0]], INK_, 4.6)
        L.line(poly + [poly[0]], mix((38, 30, 10), GOLD, 0.7), 1.6)
        from wr_cells import corner_ticks
        corner_ticks(L, poly, GOLD, 5.0, 20, ink=True)
    else:               # C hazard rails: gold/ink stripes along the inner and outer arc edges, plain gold on the sides
        L.poly(poly, fill=(44, 34, 10, 255))
        for (r0_, r1_) in ((ra, ra + 5.5), (rb - 5.5, rb)):
            band = arc_band(r0_, r1_, b0 + dA(r0_, 8) + 0.5, b1 - dA(r1_, 8) - 0.5)
            L.poly(band, fill=(12, 10, 22, 255))
            WU.hatch(L, band, GOLD, 6.0, 3.0, 45)
        for aa in (b0, b1):
            sg = 1 if aa == b0 else -1
            x0, y0 = ppx(C, ra + 5, aa + sg * dA(ra + 5, 8)); x1, y1 = ppx(C, rb - 5, aa + sg * dA(rb - 5, 8))
            L.line([(x0, y0), (x1, y1)], INK_, 6.2)
            L.line([(x0, y0), (x1, y1)], GOLD, 2.4)


def hp_bar(L, a, ang):
    o = opt('adjuster_hp_bar')
    ri, ro = CB.ring_geom(min(a['ring'], 2))
    n = a['mx']
    ha = a.get('hp_after', a['hp'])
    if o == 'E':
        a0, a1 = ang - 22, ang + 22
        r0, r1 = ro - 15, ro - 7
        _E8.socket(L, r0 - 2.5, r1 + 2.5, a0 - 1, a1 + 1)
        sw = (a1 - a0) / n
        gap = 3.0 / ((r0 + r1) / 2) * 57.3
        for i in range(n):
            if i < a['hp']:
                L.poly(L.band(C, r0, r1, a0 + i * sw + gap / 2, a0 + (i + 1) * sw - gap / 2), fill=CREAM, outline=INK, w=1.0)
                if i >= ha:
                    m = a0 + (i + 0.5) * sw
                    L.line([ppx(C, r0 - 1, m - sw * 0.35), ppx(C, r1 + 1, m + sw * 0.35)], RED, 2.6)
        return
    ra, rb = radial_ext(a['ring'])
    r1 = rb - 5.5
    r0 = r1 - 8.5
    rm = (r0 + r1) / 2
    seg = 17.0                  # px per pip (arc)
    gp = 3.2
    grp = 9.0                   # extra gap between the two groups of 5
    tot = n * seg + (n - 1) * gp + grp
    a_start = ang - math.degrees(tot / 2 / rm)
    pos = []
    x = 0.0
    for i in range(n):
        if i == 5:
            x += grp
        pos.append((a_start + math.degrees(x / rm), a_start + math.degrees((x + seg) / rm)))
        x += seg + gp
    L.poly(arc_band(r0 - 2.4, r1 + 2.4, pos[0][0] - math.degrees(3 / rm), pos[-1][1] + math.degrees(3 / rm)), fill=(10, 8, 6, 255) if o != 'B' else (24, 18, 6, 255),
           outline=INK_ if o != 'B' else GOLD, w=1.6 if o != 'B' else 2.0)
    for i, (p0, p1) in enumerate(pos):
        if i >= a['hp']:
            L.poly(arc_band(r0 + 1, r1 - 1, p0, p1), fill=(24, 20, 12, 255))
            continue
        lost = i >= ha
        if o == 'A':
            L.poly(arc_band(r0, r1, p0, p1), fill=GOLD + (255,), outline=INK_, w=1.2)
        elif o == 'B':
            L.poly(arc_band(r0, r1, p0, p1), fill=CREAM + (255,), outline=INK_, w=1.2)
        else:
            L.poly(arc_band(r0, r1, p0, p1 + math.degrees(gp / rm) * (0 if i in (4, 9) else 1)), fill=(GOLD if not lost else REDC) + (255,))
            if i not in (4, 9):
                x0, y0 = ppx(C, r0 - 1, p1 + math.degrees(gp / 2 / rm)); x1, y1 = ppx(C, r1 + 1, p1 + math.degrees(gp / 2 / rm))
                L.line([(x0, y0), (x1, y1)], INK_, 1.8)
        if lost:
            m = (p0 + p1) / 2
            sl = [ppx(C, r0 - 1.5, m - math.degrees(5 / rm)), ppx(C, r1 + 1.5, m + math.degrees(5 / rm))]
            if o == 'C':
                WU.hatch(L, arc_band(r0, r1, p0, p1), INK_, 4.5, 1.8, 45)
            else:
                L.line(sl, INK_, 6.8)
                L.line(sl, REDC, 3.8)
    if o == 'B':        # gold end caps: the tray is gold-capped (boss family) even though the pips stay cream
        for (aa, sg) in ((pos[0][0], -1), (pos[-1][1], 1)):
            x0, y0 = ppx(C, r0 - 3, aa + sg * math.degrees(1.5 / rm)); x1, y1 = ppx(C, r1 + 3, aa + sg * math.degrees(1.5 / rm))
            L.line([(x0, y0), (x1, y1)], INK_, 7)
            L.line([(x0, y0), (x1, y1)], GOLD, 3.4)


def diamond(L, a, ang):
    o = opt('adjuster_diamond')
    ri, ro = CB.ring_geom(min(a['ring'], 2))
    x, y = ppx(C, (ri + ro) / 2 - 3, ang)
    k = L.k
    if o == 'E':
        L.glow(lambda dd: dd.ellipse([(x - 34) * k, (y - 34) * k, (x + 34) * k, (y + 34) * k], fill=(4, 6, 14, 200)), blur=4)
        R = 30
        dia = [(x, y - R), (x + R, y), (x, y + R), (x - R, y)]
        L.poly(dia, fill=(52, 40, 10, 255), outline=INK, w=8)
        L.poly(dia, fill=None, outline=GOLD, w=4.2)
        r2 = 21
        L.poly([(x, y - r2), (x + r2, y), (x, y + r2), (x - r2, y)], fill=None, outline=(255, 226, 120), w=1.6)
        L.glyph('X_SKULL', 24, (x, y), WHITE)
        return
    R = 36
    L.glow(lambda dd: dd.polygon([((x) * k, (y - R - 3) * k), ((x + R + 3) * k, y * k), (x * k, (y + R + 3) * k), ((x - R - 3) * k, y * k)], fill=(4, 6, 14, 190)), blur=2.6)
    dia = [(x, y - R), (x + R, y), (x, y + R), (x - R, y)]
    if o == 'A':        # double-edge diamond: ink, 5 px gold, a clean 2.4 px pale-gold inner edge at 8 px inset, white skull 28 px
        L.poly(dia, fill=(52, 40, 10, 255), outline=INK_, w=10)
        L.poly(dia, fill=None, outline=GOLD, w=5)
        r2 = R - 9
        L.poly([(x, y - r2), (x + r2, y), (x, y + r2), (x - r2, y)], fill=None, outline=GOLD_HI, w=2.4)
        gly = WU.gly
        gly(L, 'X_SKULL', 27, (x, y + 0.5), (255, 255, 255))
    elif o == 'B':      # faceted gem: four lit facets, an ink skull cut into the gold plate (high contrast, no white blob)
        L.poly(dia, fill=GOLD, outline=INK_, w=10)
        L.poly([(x, y - R + 2), (x, y), (x - R + 3, y)], fill=GOLD_HI)
        L.poly([(x, y - R + 2), (x + R - 3, y), (x, y)], fill=GOLD)
        L.poly([(x, y), (x + R - 3, y), (x, y + R - 2)], fill=(206, 150, 20))
        L.poly([(x, y), (x, y + R - 2), (x - R + 3, y)], fill=(228, 172, 28))
        L.poly(dia, fill=None, outline=INK_, w=2.2)
        WU.gly(L, 'X_SKULL', 27, (x, y + 0.5), (36, 26, 6), GOLD_HI)
    else:               # C crowned: a smaller diamond with four gold spikes and corner studs, white skull on a dark core
        Rr = R - 5
        d2 = [(x, y - Rr), (x + Rr, y), (x, y + Rr), (x - Rr, y)]
        for (dx, dy) in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            sp = [(x + dx * (Rr + 9) + dy * 6, y + dy * (Rr + 9) + dx * 6), (x + dx * (Rr + 9) - dy * 6, y + dy * (Rr + 9) - dx * 6), (x + dx * (Rr - 6), y + dy * (Rr - 6))]
            L.poly(sp, fill=GOLD, outline=INK_, w=4)
        L.poly(d2, fill=(52, 40, 10, 255), outline=INK_, w=10)
        L.poly(d2, fill=None, outline=GOLD, w=5)
        L.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(20, 15, 4), outline=GOLD_HI, w=2)
        WU.gly(L, 'X_SKULL', 24, (x, y + 0.5), (255, 255, 255))


def armor_and_strike(L, a, ang):
    """latent: the Adjuster's armour (same steel as unit armour) and its strike chevrons"""
    pseudo = dict(id=-1, kind='Packet', dep=a['ring'], s=a['s'], w=1, df='armor', warded=False, hit=a.get('hit', 2))
    if a['df'] == 'armor':
        WU.armor_cap(L, pseudo)
    if a.get('strike'):
        o = opt('adjuster_armor_strike')
        n = a['hit']
        if o in ('E',):
            return _E8.chev_stack(L, RS['bz1'] - 30, ang, n, RED)
        if o == 'A':        # the same body chevrons every unit uses, on the boss cell (one grammar for every attacker)
            WU.stack(L, pseudo, ang, n, 0)
        elif o == 'B':      # a lane of chevrons through the NOW ring at the boss's sector: the strike visibly crosses the rings to the slice
            ri0, ro0 = CB.ring_geom(0)
            pseudo0 = dict(pseudo, dep=0)
            L.poly(arc_band(ri0 + 8, ro0 - 8, ang - 12, ang + 12), fill=(40, 12, 14, 255))
            WU.stack(L, pseudo0, ang, n, 0)
        else:               # C a dashed red beam from the diamond's inner point to the slice rim with a chevron pair at the slice
            ri1, ro1 = CB.ring_geom(min(a['ring'], 2))
            p0 = ppx(C, ri1 + 8, ang)
            p1 = ppx(C, RS['s1'] + 18, ang)
            L.line([p0, p1], INK_, 8.5)
            dash_path(L, [p0, p1], REDC, 4.6, 9, 6, closed=False)
            for i in range(n):
                p = [pt(RS['s1'] + 16 + i * 9, ang, -13), pt(RS['s1'] + 7 + i * 9, ang, 0), pt(RS['s1'] + 16 + i * 9, ang, 13)]
                L.line(p, INK_, 10.5)
                L.line(p, REDC, 6)


def adjuster(L, a, beat):
    if a['hp'] <= 0:
        return
    if all(opt(k) == 'E' for k in ('adjuster_cell', 'adjuster_hp_bar', 'adjuster_diamond', 'adjuster_armor_strike', 'armor_cap')) and not a.get('strike'):
        return adjuster_body(L, a)
    if opt('adjuster_cell') in ('R', 'V'):
        import wr2_boss as W2B
        return W2B.adjuster(L, a, beat)
    ang = 60 * a['s']
    cell(L, a, ang)
    ha = a.get('hp_after', a['hp'])
    REG['adj'] = dict(segments=a['hp'], lost=a['hp'] - ha, ring=a['ring'], sector=a['s'])
    hp_bar(L, a, ang)
    armor_and_strike(L, a, ang)
    diamond(L, a, ang)
