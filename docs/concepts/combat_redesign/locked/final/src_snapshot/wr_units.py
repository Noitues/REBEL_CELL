"""Unit-level element drawings (each element = its own function; opt('<id>') picks E / A / B / C).
E = the approved E10 drawing (e8lib / e10lib calls).  Geometry rule for A/B/C: cell edge = unit_poly, outline ON the edge, content inside it."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import wr_state as ST
from wr_state import opt
from wr_geo import *
import e8lib as E8
from e10lib import chevrons_h, REG, lit_cell
from wr_cells import corner_ticks, live_units
import wr_latent as WLT

REDC = (255, 68, 51)
STEEL_DK = (84, 96, 120)


def gly(L, name, px, xy, fill=(255, 255, 255), edge=INK_):
    g = glyph_rgba(name, int(px * L.k), max(2, int(px * L.k * 0.075)), fill=fill, edge=edge)
    L.im.alpha_composite(g, (int(xy[0] * L.k - g.width / 2), int(xy[1] * L.k - g.height / 2)))


def masked(L, poly, fn, pad=6):
    """run fn(draw, ox, oy, k) on a temp layer, clip it to poly, composite on L"""
    k = L.k
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    x0, y0 = int(min(xs)) - pad, int(min(ys)) - pad
    x1, y1 = int(max(xs)) + pad, int(max(ys)) + pad
    t = Image.new('RGBA', ((x1 - x0) * k, (y1 - y0) * k), (0, 0, 0, 0))
    fn(ImageDraw.Draw(t), x0, y0, k)
    m = Image.new('L', t.size, 0)
    ImageDraw.Draw(m).polygon([((x - x0) * k, (y - y0) * k) for x, y in poly], fill=255)
    t.putalpha(ImageChops.multiply(t.split()[3], m))
    L.im.alpha_composite(t, (x0 * k, y0 * k))


def hatch(L, poly, col, spacing=7, w=1.6, angle=45):
    def fn(d, ox, oy, k):
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        span_ = max(max(xs) - min(xs), max(ys) - min(ys)) + 20
        th = math.radians(angle)
        dx, dy = math.cos(th), math.sin(th)
        nx, ny = -dy, dx
        t = -span_
        cc = tuple(col) + ((255,) if len(col) == 3 else ())
        while t < span_:
            px, py = cx + nx * t, cy + ny * t
            d.line([((px - dx * span_ - ox) * k, (py - dy * span_ - oy) * k), ((px + dx * span_ - ox) * k, (py + dy * span_ - oy) * k)], fill=cc, width=max(1, int(w * k)))
            t += spacing
    masked(L, poly, fn)


def u_poly(u, rin=0.0, rout=0.0, tin=0.0):
    b0, b1 = unit_bounds(u)
    return cell_poly(u['dep'], b0, b1, rin, rout, 'unit', tin=tin)


def pline(L, poly, col, w):
    L.line(poly + [poly[0]], col, w)


# ----------------------------------------------------------------------------- unit_cell_outline
def outline(L, u, col=None, w=None):
    o = opt('unit_cell_outline')
    if o in ('R', 'V'):
        import wr2_units as W2U
        return W2U.outline(L, u, col, w)
    if o == 'E' or u['w'] == 6:
        E8.cell_outline(L, u, col=col, w=w)
        return
    lane = LANE[u['dep']]
    c = col or lane['col']
    ww = w or lane['w']
    poly = u_poly(u)
    dep = u['dep']
    if o == 'A':      # one clean ink-sheathed line, continuous 12/8 dash rhythm, drawn LAST so no socket or cap can hide it
        lane_line(L, poly, dep, w=ww, col=c)
    elif o == 'B':    # heavier ladder 5 / 3.5 / 3 and a dark moat just inside the line so red chevrons never touch the red outline
        ww = w or (5.0, 3.5, 3.0)[dep]
        d_ = ww / 2 + 2.6
        moat = u_poly(u, d_, d_, tin=d_)
        pline(L, moat, (9, 6, 16), 3.4)
        lane_line(L, poly, dep, w=ww, col=c)
    else:             # C +2 becomes four corner brackets (no dashes to fill in); NOW and +1 stay solid
        if dep < 2 or col is not None:
            pline(L, poly, INK_, ww + 4.5)
            pline(L, poly, c, ww)
        else:
            corner_ticks(L, poly, c, ww, 22, ink=True)


def outline_hover(Lh, u):
    outline(Lh, u, col=YEL, w=5)


# ----------------------------------------------------------------------------- token: halo, disc, lane base ring, glyph
def token_R():
    return 27 if opt('token_disc') != 'E' else 24


def halo(L, x, y, R):
    o = opt('token_halo')
    k = L.k
    if o == 'E':
        L.glow(lambda dd: dd.ellipse([(x - 32) * k, (y - 32) * k, (x + 32) * k, (y + 32) * k], fill=(4, 6, 14, 190)), blur=4)
    elif o == 'A':        # tight pool: 1.5 px past the disc, 2.2 px blur, 70 percent
        L.glow(lambda dd: dd.ellipse([(x - R - 1.5) * k, (y - R - 1.5) * k, (x + R + 1.5) * k, (y + R + 1.5) * k], fill=(4, 6, 14, 178)), blur=2.2)
    elif o == 'B':        # contact shadow from the cutaway light (-0.5,-0.3): offset down-right, tight
        L.glow(lambda dd: dd.ellipse([(x - R + 1.5) * k, (y - R + 2.8) * k, (x + R + 3.5) * k, (y + R + 4.8) * k], fill=(4, 6, 14, 200)), blur=2.6)
    else:                 # C hard ink keyline (3 px) + a very light pool: sticker edge, no mud
        L.glow(lambda dd: dd.ellipse([(x - R - 3) * k, (y - R - 3) * k, (x + R + 3) * k, (y + R + 3) * k], fill=(4, 6, 14, 110)), blur=3)
        L.ellipse([x - R - 3, y - R - 3, x + R + 3, y + R + 3], fill=INK_)


def disc(L, x, y, R, u, dead=False):
    o = opt('token_disc')
    kc = KCOL[u['kind']]
    if dead:
        L.ellipse([x - R, y - R, x + R, y + R], fill=(58, 54, 66))
        return
    if o == 'E':
        L.ellipse([x - R, y - R, x + R, y + R], fill=tuple(int(v * 0.72) for v in kc))
    elif o == 'A':        # darker than the cell: the kind colour at 26 percent, one clear value step below the mauve screen
        L.ellipse([x - R, y - R, x + R, y + R], fill=tuple(int(v * 0.26) for v in kc))
    elif o == 'B':        # neutral ink-navy disc for every kind (kind is the glyph's job), a 2 px kind-colour inner ring
        L.ellipse([x - R, y - R, x + R, y + R], fill=(13, 15, 30))
        L.ellipse([x - R + 4, y - R + 4, x + R - 4, y + R - 4], outline=tuple(int(v * 0.8) for v in kc), w=2)
    else:                 # C glass bowl: dark core rising to a lit rim, one soft top-left highlight (the cutaway light)
        n = 12
        for i in range(n):
            t = i / (n - 1)
            rr = R * (1 - t)
            col = tuple(int(v * (0.50 - 0.30 * t)) for v in kc)
            L.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col)
        L.ellipse([x - R * 0.62, y - R * 0.74, x - R * 0.12, y - R * 0.34], fill=tuple(int(v * 0.62) for v in kc))


def _ring_full(L, x, y, rr, w, col):
    pts = L.arc_pts((x, y), rr, 0, 360, 72)
    L.line(pts, INK_, w + 4.0)
    L.line(pts, col, w)


def _ring_dashes(L, x, y, rr, w, col, n, on, off_a):
    for pas in (0, 1):
        for i in range(n):
            a0 = 360 / n * i + off_a
            L.line(L.arc_pts((x, y), rr, a0, a0 + on, 10), INK_ if pas == 0 else col, w + 4.0 if pas == 0 else w)


def base_ring(L, x, y, R, dep, dead=False):
    o = opt('token_lane_base')
    lane = LANE[dep]
    col = (150, 150, 160) if dead else lane['col']
    if o == 'E':
        if lane['dash'] is None:
            L.ellipse([x - R, y - R, x + R, y + R], outline=col, w=lane['w'])
        else:
            n = 14
            for i in range(n):
                a0 = 360 * i / n
                L.line(L.arc_pts((x, y), R, a0, a0 + 360 / n * 0.55, 6), col, lane['w'])
        return
    w = (4.0, 3.0, 3.0)[dep]
    if o == 'A':          # ladder weights 4 / 3 / 3 on the disc rim; +2 = six long dashes (40 on, 20 off)
        rr = R - w / 2
        if dep < 2:
            _ring_full(L, x, y, rr, w, col)
        else:
            _ring_dashes(L, x, y, rr, w, col, 6, 40, 10)
    elif o == 'B':        # standoff ring: detached 4 px outside the disc, so a red ring never touches the red chevrons or the disc; +2 = eight dashes
        L.ellipse([x - R - 1.6, y - R - 1.6, x + R + 1.6, y + R + 1.6], outline=INK_, w=2)
        rr = R + 4.0
        if dep < 2:
            _ring_full(L, x, y, rr, w, col)
        else:
            _ring_dashes(L, x, y, rr, w, col, 8, 30, 6)
    else:                 # C inner ring: engraved 5 px inside the rim; +2 = four long arcs (the same four-bracket idea as the cell outline)
        L.ellipse([x - R - 0.5, y - R - 0.5, x + R + 0.5, y + R + 0.5], outline=INK_, w=2)
        rr = R - 5.5
        if dep < 2:
            _ring_full(L, x, y, rr, w, col)
        else:
            _ring_dashes(L, x, y, rr, w, col, 4, 62, 14)


def armor_cue(L, x, y, R, ang):
    o = opt('armor_cap')
    if o == 'E':
        return
    ox, oy = math.sin(math.radians(ang)), -math.cos(math.radians(ang))
    if o == 'A':        # four steel rivets on the ring
        for a in (0, 90, 180, 270):
            px, py = x + (R - 1) * math.cos(math.radians(a)), y + (R - 1) * math.sin(math.radians(a))
            L.ellipse([px - 3.6, py - 3.6, px + 3.6, py + 3.6], fill=STEEL_HI, outline=INK_, w=1.4)
    elif o == 'B':      # a steel cap over the outer 150 degrees of the token
        a_c = math.degrees(math.atan2(oy, ox))
        pts = L.arc_pts((x, y), R + 2.6, a_c - 75, a_c + 75, 18)
        L.line(pts, INK_, 8.5)
        L.line(pts, STEEL, 5)
        L.line(L.arc_pts((x, y), R + 3.8, a_c - 70, a_c + 70, 18), STEEL_HI, 1.6)
    else:               # C steel collar all round
        L.ellipse([x - R - 3.6, y - R - 3.6, x + R + 3.6, y + R + 3.6], outline=INK_, w=7)
        L.ellipse([x - R - 3, y - R - 3, x + R + 3, y + R + 3], outline=STEEL, w=4)


def token(L, u, dead=False):
    if all(opt(k) == 'E' for k in ('token_disc', 'token_lane_base', 'token_halo', 'armor_cap')) and not ST.GLYPH_MODE():
        return E8.token(L, u, dead=dead)
    x, y = E8.token_pos(u)
    R = token_R()
    halo(L, x, y, R)
    disc(L, x, y, R, u, dead)
    base_ring(L, x, y, R, u['dep'], dead)
    px = R * (1.55 if opt('token_disc') == 'E' else 1.42)
    gly(L, KIND[u['kind']][1], px, (x, y), (150, 150, 160) if dead else (255, 255, 255))
    if u.get('df') == 'armor' and not dead:
        ang = math.degrees(math.atan2(x - C[0], -(y - C[1])))
        armor_cue(L, x, y, R, ang)
    return x, y


# ----------------------------------------------------------------------------- unit_hp_row (+ shield_bracket inside)
def row_geom(u):
    ra, rb = radial_ext(u['dep'])
    lw = (4.0, 3.0, 3.0)[u['dep']]
    r1 = rb - lw / 2 - 3.0
    return r1 - 8.0, r1


def hp_row(L, u, hp, mx, lose=0, shield=0, shmx=0):
    o = opt('unit_hp_row')
    if o == 'E' or u['w'] == 6:
        if shmx and opt('shield_bracket') != 'E':
            E8.hp_row(L, u, hp, mx, lose=lose)
            ri, ro = CB.ring_geom(u['dep'])
            WLT.shield_bracket(L, u, ro - 14, ro - 6, shield, shmx)
            return
        return E8.hp_row(L, u, hp, mx, lose=lose, shield=shield, shmx=shmx)
    r0, r1 = row_geom(u)
    ST.PIPS[u['id']] = []
    rm = (r0 + r1) / 2
    w = u['w']
    per = max(1, mx // w)
    idx = 0
    for q in range(w):
        axis = 60 * (u['s'] + q)
        if o == 'A':        # fixed 13x8 px pips, centred on the sector axis in a tray that is exactly one sector's capacity (empty slots show)
            wp, gp = 20.0, 4.0
        elif o == 'B':      # round beads, 9 px
            wp, gp = 12.0, 7.0
        else:               # C one bar per sector, 14 px per HP, ink notch between
            wp, gp = 20.0, 0.0
        tot = per * wp + (per - 1) * gp
        a_start = axis - math.degrees(tot / 2 / rm)
        if o != 'B':
            tray = arc_band(r0 - 2.0, r1 + 2.0, a_start - math.degrees(3.0 / rm), a_start + math.degrees((tot + 3.0) / rm))
            L.poly(tray, fill=(8, 10, 20, 255), outline=INK_, w=1.6)
        for i in range(per):
            lit = idx < hp
            lost = lit and idx >= hp - lose
            aa = a_start + math.degrees(i * (wp + gp) / rm)
            ab = aa + math.degrees(wp / rm)
            am = (aa + ab) / 2
            if o == 'A':
                if lit:
                    L.poly(arc_band(r0, r1, aa, ab), fill=CREAM + (255,), outline=INK_, w=1.2)
                    if lost:
                        sl = [ppx(C, r0 - 1.5, am - math.degrees(4.5 / rm)), ppx(C, r1 + 1.5, am + math.degrees(4.5 / rm))]
                        L.line(sl, INK_, 6.6)
                        L.line(sl, REDC, 3.6)
                else:
                    L.poly(arc_band(r0 + 1, r1 - 1, aa, ab), fill=(22, 24, 38, 255))
            elif o == 'B':
                x, y = ppx(C, rm, am)
                if lit:
                    L.ellipse([x - 5.6, y - 5.6, x + 5.6, y + 5.6], fill=CREAM, outline=INK_, w=1.4)
                    if lost:       # half-red bead: the slash is the fill itself
                        L.poly([(x - 4.4, y + 4.4), (x + 4.4, y - 4.4), (x + 4.4, y + 4.4)], fill=REDC)
                        L.line([(x - 5.6, y + 5.6), (x + 5.6, y - 5.6)], INK_, 1.6)
                        L.ellipse([x - 4.8, y - 4.8, x + 4.8, y + 4.8], outline=INK_, w=1.4)
                else:
                    L.ellipse([x - 4.2, y - 4.2, x + 4.2, y + 4.2], fill=(18, 20, 34), outline=(60, 66, 90), w=1.2)
            else:
                if lit:
                    L.poly(arc_band(r0, r1, aa, ab), fill=(REDC if lost else CREAM) + (255,))
                    if lost:
                        hatch(L, arc_band(r0, r1, aa, ab), INK_, 4.5, 1.6, 45)
                if i > 0:
                    x0, y0 = ppx(C, r0 - 2, aa)
                    x1, y1 = ppx(C, r1 + 2, aa)
                    L.line([(x0, y0), (x1, y1)], INK_, 1.8)
            ST.PIPS[u['id']].append((aa, ab, r0, r1, lit))
            idx += 1
    if shmx:
        WLT.shield_bracket(L, u, r0, r1, shield, shmx)


# ----------------------------------------------------------------------------- armor_cap
def armor_cap(L, u):
    o = opt('armor_cap')
    if o == 'E' or u['w'] == 6:
        return E8.armor_cap(L, u)
    ra, rb = radial_ext(u['dep'])
    b0, b1 = unit_bounds(u)
    a0 = b0 + dA(rb, 8) + 0.5
    a1 = b1 - dA(rb, 8) - 0.5
    if o == 'A':          # gunmetal plate on the outer edge: dark body, bright specular edge, 5 px rivets every 16 px
        r_lo, r_hi = rb - 6.5, rb + 1.5
        L.poly(arc_band(r_lo, r_hi, a0, a1), fill=STEEL_DK + (255,), outline=INK_, w=1.8)
        L.poly(arc_band(r_hi - 2.6, r_hi - 0.8, a0 + 0.4, a1 - 0.4), fill=STEEL_HI + (255,))
        rm = (r_lo + r_hi) / 2 - 0.4
        n = int(math.radians(a1 - a0) * rm / 16)
        for i in range(1, n):
            x, y = ppx(C, rm, a0 + (a1 - a0) * i / n)
            L.ellipse([x - 2.5, y - 2.5, x + 2.5, y + 2.5], fill=(238, 244, 255), outline=INK_, w=1.2)
    elif o == 'B':        # separate plates (~30 px) with seams and two rivets each: armour tiles, not a stripe
        r_lo, r_hi = rb - 7.0, rb + 1.5
        rm = (r_lo + r_hi) / 2
        length = math.radians(a1 - a0) * rm
        n = max(2, int(length / 30))
        step = (a1 - a0) / n
        for i in range(n):
            aa, ab = a0 + i * step + math.degrees(1.6 / rm), a0 + (i + 1) * step - math.degrees(1.6 / rm)
            L.poly(arc_band(r_lo, r_hi, aa, ab), fill=(126, 138, 160, 255), outline=INK_, w=1.8)
            L.poly(arc_band(r_hi - 2.4, r_hi - 0.8, aa + 0.3, ab - 0.3), fill=STEEL_HI + (255,))
            for fr in (0.2, 0.8):
                x, y = ppx(C, rm - 0.6, aa + (ab - aa) * fr)
                L.ellipse([x - 2.0, y - 2.0, x + 2.0, y + 2.0], fill=(30, 36, 52), outline=STEEL_HI, w=1.0)
    else:                 # C steel tray: the HP row sits in a riveted steel frame (the armour IS the container of the HP)
        r0, r1 = row_geom(u)
        fr = arc_band(r0 - 4.5, r1 + 4.0, a0 + 0.5, a1 - 0.5)
        L.poly(fr, fill=STEEL + (255,), outline=INK_, w=1.8)
        rm = r0 - 2.2
        n = max(3, int(math.radians(a1 - a0) * rm / 22))
        for i in range(0, n + 1):
            x, y = ppx(C, rm, a0 + 1.5 + (a1 - a0 - 3) * i / n)
            L.ellipse([x - 1.8, y - 1.8, x + 1.8, y + 1.8], fill=(40, 48, 64), outline=STEEL_HI, w=0.9)


# ----------------------------------------------------------------------------- chevrons
CHS = {'A': dict(half=14, depth=9, w=6.0, ink=10.5, pitch=9.5),
       'B': dict(half=17, depth=7, w=5.6, ink=10.0, pitch=9.0),
       'C': dict(half=11, depth=11, w=6.0, ink=10.5, pitch=9.5)}


def _cpts(ri, ang, i, st, sc=1.0):
    r = ri + 10 + i * st['pitch'] * sc
    return [pt(r + st['depth'] * sc, ang, -st['half'] * sc), pt(r, ang, 0), pt(r + st['depth'] * sc, ang, st['half'] * sc)]


def stack(L, u, ang, n_solid, n_hollow, dim=0.0):
    ri, ro = CB.ring_geom(u['dep'])
    so = opt('chev_solid_stack')
    st = CHS['A' if so == 'E' else so]
    wash = kind_wash(u['kind'], u['dep'])
    col = REDC
    sc = 1.0
    col_o = opt('chev_sector_column')
    if col_o == 'B':
        col = mix(REDC, wash, (0.0, 0.16, 0.30)[u['dep']])
    if col_o == 'C' and u['dep'] > 0:
        sc = 0.82
    if dim:
        col = mix(col, wash, dim)
    hol = opt('chev_hollow')
    for i in range(n_hollow):
        p = _cpts(ri, ang, n_solid + i, st, sc)
        w = st['w'] * sc
        if hol in ('E', 'A'):     # outlined: red edges 2 px each side of a 4.6 px dark core
            L.line(p, INK_, w * 1.6 + 3.4)
            L.line(p, col, w * 1.5)
            L.line(p, (10, 6, 14), w * 0.78)
        elif hol == 'B':          # dashed: two dashes per arm, the gap is dark
            L.line(p, INK_, w + 4.5)
            dash_path(L, p, col, w, 8.5, 5.5, closed=False)
        else:                     # C hatched: red body with ink cross-bars every 6 px
            L.line(p, INK_, w + 4.5)
            L.line(p, col, w)
            rp = resample(p, 1.0)
            for j in range(3, len(rp) - 2, 6):
                (x0, y0), (x1, y1) = rp[j - 1], rp[j + 1]
                tx, ty = x1 - x0, y1 - y0
                nrm = math.hypot(tx, ty) or 1
                nx, ny = -ty / nrm, tx / nrm
                L.line([(rp[j][0] - nx * (w / 2 + 1), rp[j][1] - ny * (w / 2 + 1)), (rp[j][0] + nx * (w / 2 + 1), rp[j][1] + ny * (w / 2 + 1))], INK_, 2.0)
    for col_, w in ((INK_, st['ink'] * sc), (col, st['w'] * sc)):
        for i in range(n_solid):
            L.line(_cpts(ri, ang, i, st, sc), col_, w)
    if col_o == 'A':          # baseline tick: one short bar under each unit's stack, so stacks of neighbouring rings never chain
        tot = n_solid + n_hollow
        r = ri + 10 + (tot - 1) * st['pitch'] + st['depth'] + 6.5
        a, b = pt(r, ang, -11), pt(r, ang, 11)
        L.line([a, b], INK_, 6.0)
        L.line([a, b], mix(col, (20, 8, 14), 0.25), 3.0)


def chevrons(L, u, hit, grow, dim=0.0):
    if all(opt(k) == 'E' for k in ('chev_solid_stack', 'chev_hollow', 'chev_sector_column')) and not dim:
        return chevrons_h(L, u, hit, grow)
    REG['bodies'].append(dict(uid=u['id'], solid=hit, hollow=grow, sectors=u['w']))
    for q in range(u['w']):
        stack(L, u, 60 * (u['s'] + q), hit, grow, dim)


# ----------------------------------------------------------------------------- warded_mark
def warded(L, u):
    o = opt('warded_mark')
    if o == 'E':
        return E8.warded_mark(L, u)
    tx, ty = E8.token_pos(u)
    R = token_R()
    ang_t = math.degrees(math.atan2(tx - C[0], -(ty - C[1])))
    rt = math.hypot(tx - C[0], ty - C[1])
    ang_b = ang_t + math.degrees((R + 21) / rt)
    bx, by = ppx(C, rt, ang_b)
    if o == 'A':          # mini boss lozenge: gold diamond with a skull, the Adjuster's own pieces at badge size (32 px, skull 16 px)
        Rr = 16
        dia = [(bx, by - Rr), (bx + Rr, by), (bx, by + Rr), (bx - Rr, by)]
        L.poly(dia, fill=GOLD, outline=INK_, w=4.5)
        L.poly([(bx, by - Rr + 5), (bx + Rr - 5, by), (bx, by + Rr - 5), (bx - Rr + 5, by)], fill=(46, 34, 6))
        gly(L, 'X_SKULL', 15, (bx, by + 0.5), GOLD, (30, 22, 4))
    elif o == 'B':        # gold clasp: two bracket arcs hugging the token's outer side (the boss holds this unit), no new shape
        a_c = math.degrees(math.atan2(-math.cos(math.radians(ang_t)), math.sin(math.radians(ang_t))))
        for sgn in (-1, 1):
            pts = L.arc_pts((tx, ty), R + 8.5, a_c + sgn * 22, a_c + sgn * 82, 12)
            L.line(pts, INK_, 8.4)
            L.line(pts, GOLD, 4.2)
    else:                 # C pin: a round gold badge (30 px) with an ink skull, pinned on the token's outer shoulder
        ox, oy = math.sin(math.radians(ang_t)), -math.cos(math.radians(ang_t))
        px, py = tx + ox * (R - 1) + math.cos(math.radians(ang_t)) * 18, ty + oy * (R - 1) + math.sin(math.radians(ang_t)) * 18
        L.ellipse([px - 15, py - 15, px + 15, py + 15], fill=GOLD, outline=INK_, w=3)
        gly(L, 'X_SKULL', 17, (px, py + 0.5), (40, 30, 6), GOLD)


# ----------------------------------------------------------------------------- dead_x (+ the cell treatment of a unit our guns kill)
def dead_cell(L, u):
    o = opt('dead_x')
    if o == 'E':
        return
    poly = u_poly(u)
    L.poly(poly, fill=(6, 12, 8, 120))
    if o == 'B':
        hatch(L, poly, (60, 150, 70, 120), 8, 1.8, 45)


def _xmark(L, x, y, s, w):
    for a, b in (((x - s, y - s), (x + s, y + s)), ((x + s, y - s), (x - s, y + s))):
        L.line([a, b], INK_, w + 4)
    for a, b in (((x - s, y - s), (x + s, y + s)), ((x + s, y - s), (x - s, y + s))):
        L.line([a, b], GREEN, w)


def dead_x(L, u):
    o = opt('dead_x')
    if o == 'E':
        return E8.dead_x(L, u)
    tx, ty = E8.token_pos(u)
    R = token_R()
    ang_t = math.degrees(math.atan2(tx - C[0], -(ty - C[1])))
    rt = math.hypot(tx - C[0], ty - C[1])
    if o == 'A':          # badge: 32 px green X disc touching the token's clockwise shoulder
        bx, by = ppx(C, rt, ang_t + math.degrees((R + 14) / rt))
        L.ellipse([bx - 16, by - 16, bx + 16, by + 16], fill=(10, 30, 14), outline=INK_, w=7)
        L.ellipse([bx - 16, by - 16, bx + 16, by + 16], fill=(10, 30, 14), outline=GREEN, w=3.2)
        _xmark(L, bx, by, 6.5, 4)
    elif o == 'B':        # watermark: a big green X across the dimmed cell (clear of the token and the chevron axes)
        ra, rb = radial_ext(u['dep'])
        a_mid = 60 * (u['s'] + (u['w'] - 1) / 2) + (0 if u['w'] > 1 else 0)
        rm = (ra + rb) / 2
        half = math.degrees(22 / rm)
        p0, p1, p2, p3 = ppx(C, ra + 5, a_mid - half), ppx(C, rb - 5, a_mid + half), ppx(C, ra + 5, a_mid + half), ppx(C, rb - 5, a_mid - half)
        for (a, b) in ((p0, p1), (p2, p3)):
            L.line([a, b], INK_, 9)
        for (a, b) in ((p0, p1), (p2, p3)):
            L.line([a, b], GREEN, 4.6)
    else:                 # C tag: a green capsule with the X at the cell's inner edge on the sector axis, plus a green dashed inner line
        a_mid = 60 * (u['s'] + (u['w'] - 1) / 2)
        ra, rb = radial_ext(u['dep'])
        bx, by = ppx(C, rb - 20, a_mid)
        L.rect([bx - 26, by - 13, bx + 26, by + 13], fill=(10, 30, 14), outline=INK_, w=6, r=8)
        L.rect([bx - 26, by - 13, bx + 26, by + 13], fill=(10, 30, 14), outline=GREEN, w=2.6, r=8)
        _xmark(L, bx, by, 5.5, 3.6)
        d_ = u_poly(u, 6, 6, tin=6)
        dash_path(L, d_, GREEN, 2.2, 7, 5)


# ----------------------------------------------------------------------------- consumed / trigger-killed ghosts (p2)
def ghost(L, u, kind, beat='p2'):
    """kind = 'consumed' (plan yellow) | 'killed' (harm red).  E = approved: outline + 105-alpha dark poly + dead token."""
    o = opt('consumed_unit') if kind == 'consumed' else opt('trigger_killed_unit')
    if o == 'E':
        E8.cell_outline(L, u, col=YEL if kind == 'consumed' else RED, w=3)
        ri, ro = CB.ring_geom(u['dep'])
        L.poly(L.band(C, ri + 4, ro - 4, E8.span(u)[0] + 3, E8.span(u)[1] - 3), fill=(6, 3, 8, 105))
        E8.token(L, u, dead=True)
        return
    col = YEL if kind == 'consumed' else REDC
    poly = u_poly(u)
    wash = kind_wash(u['kind'], u['dep'])
    ghostc = mix(wash, (6, 4, 14), 0.62)         # ~40 percent of the live wash: one shared ghost treatment (also the hover dim)
    L.poly(poly, fill=ghostc + (255,))
    if o == 'B':
        hatch(L, poly, mix(ghostc, col, 0.30), 7, 1.8, 45)
    pline(L, poly, INK_, 7.4)
    if kind == 'consumed':
        if o == 'B':
            dash_path(L, poly, col, 3.0, 9, 6)
        else:
            pline(L, poly, col, 3.2)
    else:     # killed: never the solid NOW red line; dashed 5.5/5.5 (A, B) or dotted (C)
        dash_path(L, poly, col, 3.0, 5.5 if o != 'C' else 1.5, 5.5 if o != 'C' else 5.0)
    x, y = E8.token_pos(u)
    R = token_R()
    L.ellipse([x - R - 2.2, y - R - 2.2, x + R + 2.2, y + R + 2.2], fill=INK_)
    L.ellipse([x - R, y - R, x + R, y + R], fill=(58, 54, 66))
    base_ring(L, x, y, R, u['dep'], dead=True)
    gly(L, KIND[u['kind']][1], R * 1.42, (x, y), (176, 172, 186))
    ang_t = math.degrees(math.atan2(x - C[0], -(y - C[1])))
    rt = math.hypot(x - C[0], y - C[1])
    bx, by = ppx(C, rt, ang_t + math.degrees((R + 17) / rt))
    if kind == 'consumed':      # the used-up stamp: the Trigger glyph in plan yellow beside the token (C = also a big watermark)
        L.ellipse([bx - 13, by - 13, bx + 13, by + 13], fill=(30, 26, 6), outline=INK_, w=5)
        L.ellipse([bx - 13, by - 13, bx + 13, by + 13], fill=(30, 26, 6), outline=YEL, w=2.4)
        gly(L, 'C_TRIG', 17, (bx, by), YEL)
        if o == 'C':
            ra, rb = radial_ext(u['dep'])
            wx, wy = ppx(C, (ra + rb) / 2, 60 * (u['s'] + (u['w'] - 1) / 2) + 6)
            gly(L, 'C_TRIG', 46, (wx, wy), mix(ghostc, YEL, 0.32), mix(ghostc, (0, 0, 0), 0.4))
    else:                       # the dead-X family: the green X disc smaller (24 px), beside the token
        L.ellipse([bx - 12, by - 12, bx + 12, by + 12], fill=(10, 30, 14), outline=INK_, w=5)
        L.ellipse([bx - 12, by - 12, bx + 12, by + 12], fill=(10, 30, 14), outline=GREEN, w=2.4)
        for sg in ((1, 1), (1, -1)):
            L.line([(bx - 5 * sg[0], by - 5 * sg[1]), (bx + 5 * sg[0], by + 5 * sg[1])], GREEN, 3.2)


# ----------------------------------------------------------------------------- one unit
def draw_units(L, f, beat, only=None, skip=None):
    from wr_cells import painter_mode
    pm = painter_mode()
    for u in f['units']:
        if only is not None and u['id'] not in only:
            continue
        if skip is not None and u['id'] in skip:
            continue
        import wr2_units as W2U
        if u['consumed'] or u['trigdead']:
            if W2U.active():
                W2U.ghost(L, u, 'consumed' if u['consumed'] else 'killed', beat)
                continue
            ghost(L, u, 'consumed' if u['consumed'] else 'killed', beat)
            continue
        if u['w'] == 6:
            WLT.wide6(L, u, f)
            continue
        if W2U.active():
            W2U.draw_unit(L, u, f, beat)
            continue
        if not pm['units']:
            lit_cell(L, u)
        dying = u['fate']['kind'] == 'dies'
        if dying:
            dead_cell(L, u)
        late_outline = opt('unit_cell_outline') in ('A', 'C')
        if not late_outline:
            outline(L, u)
        token(L, u)
        hp_row(L, u, u['hp'], u['mx'], lose=u['lose'][1], shield=u['sh'], shmx=u['shmx'])
        if u['df'] == 'armor':
            armor_cap(L, u)
        grow = max(0, u['land_hit'] - u['hit']) if (u['fate']['kind'] == 'lands' and 'land_hit' in u) else 0
        chevrons(L, u, u['hit'], grow, dim=(0.5 if (dying and opt('dead_x') != 'E') else 0.0))
        if late_outline:
            outline(L, u)
        if u['warded']:
            warded(L, u)
        if dying:
            dead_x(L, u)
