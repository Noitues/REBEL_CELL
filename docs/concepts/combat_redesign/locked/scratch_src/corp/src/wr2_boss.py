"""R2 Adjuster (boss) drawings: adjuster_cell (drawn INSTEAD of the empty cell: no underlay), adjuster_diamond, adjuster_hp_bar, ward_arc, adjuster_armor_strike."""
import math
from wr_state import opt
from wr_geo import *
from wr2_lib import *
import wr2_units as W2U
import wr_units as WU


def ward_arc(L, f):
    """R: a 3 px BOSS_GOLD strip in the ring-NOW inner gutter (gutter is 8 px INK: ink sheath 7 px, gold 3 px).  V: 4.4 px."""
    o = opt('ward_arc')
    a = f['adj']
    if a['hp'] <= 0:
        return
    s = a['s']
    b0, b1 = 60 * s - 30, 60 * s + 30
    ri, ro = CB.ring_geom(0)
    r = ri + 1.5
    w = 3.0 if o == 'R' else 4.4
    pts = L.arc_pts(C, r, b0 + 2.8, b1 - 2.8, 40)
    L.line(pts, INKC, w + 4.0)
    L.line(pts, BOSSG, w)


def cell(L, a, ang):
    """R: brass gradient glass, a 3 px BOSS_GOLD edge with ink, a hairline inner edge; drawn instead of the empty cell, so no orange outline, no programme art underneath.
    V: the gradient lit from the outer edge, edge 2.4 px, no inner hairline."""
    o = opt('adjuster_cell')
    poly = cell_poly(a['ring'], ang - 30, ang + 30, kind='unit')
    ra, rb = radial_ext(a['ring'])
    b0, b1 = ang - 30, ang + 30
    n = int((rb - ra) / 2.0) + 1
    for i in range(n):
        t = (i + 0.5) / n
        r0 = ra + (rb - ra) * i / n
        r1 = min(rb, ra + (rb - ra) * (i + 1) / n + 0.8)
        col = mix((70, 52, 14), (34, 26, 8), t) if o == 'R' else mix((36, 28, 8), (74, 56, 16), t)
        L.poly(band_poly(a['ring'], b0, b1, r0, r1), fill=col + (255,))
    ew = 3.0 if o == 'R' else 2.4
    L.line(poly + [poly[0]], INKC, ew + 4.5)
    L.line(poly + [poly[0]], BOSSG, ew)
    if o == 'R':
        inner = cell_poly(a['ring'], b0, b1, 5, 5, kind='unit', tin=5)
        L.line(inner + [inner[0]], mix((50, 38, 10), BOSSG, 0.5), 1.2)


def hp_bar(L, a, ang):
    """HP grammar for the boss: kept = BOSS_GOLD rounded r3 segments in two groups of 5 (a 9 px gap), the pip lost this END TURN = HARM + white 2 px slash + ink,
    a gone pip = dark socket + hairline.  R: 17 px pips.  V: 15 px pips on an INK tray."""
    o = opt('adjuster_hp_bar')
    n = a['mx']
    ha = a.get('hp_after', a['hp'])
    ra, rb = radial_ext(a['ring'])
    r1 = rb - 1.5 - 4.5
    r0 = r1 - 7.5
    rm = (r0 + r1) / 2
    seg = 17.0 if o == 'R' else 15.0
    gp = 3.4
    grp = 9.0
    tot = n * seg + (n - 1) * gp + grp
    a_start = ang - math.degrees(tot / 2 / rm)
    pos = []
    x = 0.0
    for i in range(n):
        if i == 5:
            x += grp
        pos.append((a_start + math.degrees(x / rm), a_start + math.degrees((x + seg) / rm)))
        x += seg + gp
    if o == 'V':
        L.poly(arc_band(r0 - 2, r1 + 2, pos[0][0] - math.degrees(2.5 / rm), pos[-1][1] + math.degrees(2.5 / rm)), fill=(10, 8, 6, 255), outline=INKC, w=1.4)
    for i, (p0, p1) in enumerate(pos):
        if i >= a['hp']:
            rseg(L, r0, r1, p0, p1, (84, 92, 120), 3.0, ink=True, ow=0.8)
            da_ = math.degrees(1.4 / rm)
            rseg(L, r0 + 1.4, r1 - 1.4, p0 + da_, p1 - da_, (14, 16, 30), 1.6, ink=False)
            continue
        if i >= ha:
            rseg(L, r0, r1, p0, p1, HARM, 3.0)
            m = (p0 + p1) / 2
            sl = [ppx(C, r0 - 1.8, m - math.degrees(4.6 / rm)), ppx(C, r1 + 1.8, m + math.degrees(4.6 / rm))]
            L.line(sl, INKC, 4.6)
            L.line(sl, (255, 255, 255), 2.0)
        else:
            rseg(L, r0, r1, p0, p1, BOSSG, 3.0)


def diamond(L, a, ang):
    """R: 72 px double-edge diamond (ink, 5 px gold, a clean 2.4 px pale-gold inner edge) with the white skull at 24 px.  V: the skull sits on a dark core disc."""
    o = opt('adjuster_diamond')
    ri, ro = CB.ring_geom(min(a['ring'], 2))
    x, y = ppx(C, (ri + ro) / 2 - 3, ang)
    k = L.k
    R = 36
    L.glow(lambda dd: dd.polygon([((x) * k, (y - R - 3) * k), ((x + R + 3) * k, y * k), (x * k, (y + R + 3) * k), ((x - R - 3) * k, y * k)], fill=(12, 10, 22, 191)), blur=4)
    dia = [(x, y - R), (x + R, y), (x, y + R), (x - R, y)]
    L.poly(dia, fill=(52, 40, 10, 255), outline=INKC, w=10)
    L.poly(dia, fill=None, outline=BOSSG, w=5)
    r2 = R - 9
    L.poly([(x, y - r2), (x + r2, y), (x, y + r2), (x - r2, y)], fill=None, outline=BOSSG_HI, w=2.4)
    if o == 'V':
        L.ellipse([x - 20, y - 20, x + 20, y + 20], fill=(20, 15, 4), outline=BOSSG_HI, w=1.6)
    WU.gly(L, 'X_SKULL', 24, (x, y + 0.5), (255, 255, 255))


def armor_and_strike(L, a, ang):
    """latent.  R: the Adjuster's armour = the same steel rails round its HP bar + steel strips on the diamond's outer edges; the strike = the unit chevron grammar on the boss cell.
    V: strike chevrons without the diamond strips."""
    o = opt('adjuster_armor_strike')
    pseudo = dict(id=-1, kind='Packet', dep=a['ring'], s=a['s'], w=1, df='armor', warded=False, hit=a.get('hit', 2), mx=3)
    if a['df'] == 'armor':
        ra, rb = radial_ext(a['ring'])
        r1 = rb - 1.5 - 4.5
        r0 = r1 - 7.5
        rm = (r0 + r1) / 2
        half = math.degrees(105 / rm)
        W2U.rails(L, ang - half, ang + half, r0 - 2.5, r1 + 2.5, rm)
        if o == 'R':
            ri, ro = CB.ring_geom(min(a['ring'], 2))
            x, y = ppx(C, (ri + ro) / 2 - 3, ang)
            R = 36
            for (p, q) in (((x, y - R), (x + R, y)), ((x - R, y), (x, y - R))):
                L.line([p, q], INKC, 8.5)
            for (p, q) in (((x, y - R), (x + R, y)), ((x - R, y), (x, y - R))):
                L.line([p, q], STEELC, 5.0)
    if a.get('strike'):
        W2U.stack(L, pseudo, ang, a['hit'], 0)


def adjuster(L, a, beat):
    if a['hp'] <= 0:
        return
    from e10lib import REG
    ang = 60 * a['s']
    cell(L, a, ang)
    ha = a.get('hp_after', a['hp'])
    REG['adj'] = dict(segments=a['hp'], lost=a['hp'] - ha, ring=a['ring'], sector=a['s'])
    hp_bar(L, a, ang)
    armor_and_strike(L, a, ang)
    diamond(L, a, ang)
