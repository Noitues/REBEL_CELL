"""R2 unit drawings (options 'R' = AD-directed pick, 'V' = the one variant).  One function per element:
 outline            unit_cell_outline          token_halo / token_disc / token_ring / token_glyph / armor_cue   (token_halo, token_disc, token_lane_base, armor_cap on the token)
 hp_row             unit_hp_row (+ shield_bracket)                          armour_rails   armor_cap (tiles)
 chevrons           chev_solid_stack / chev_hollow / chev_sector_column     warded         warded_mark
 gone_overlay + dead_badge   dead_x / unit_gone_state                       ghost          consumed_unit / trigger_killed_unit
 draw_unit          the R2 order of one unit: screen (cells painter) -> chevrons -> outline (sheathed) -> [gone dim] -> HP tray -> armour -> token -> badges
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw
import importlib.util, sys
import wr_state as ST
from wr_state import opt
from wr_geo import *
from wr2_lib import *
import e8lib as E8
import wr_units as WU
from e10lib import REG

_LIB = {}


def library():
    """the glyph master library (cards owns kglyph; imported read-only, KA_* names)"""
    if 'k' not in _LIB:
        spec = importlib.util.spec_from_file_location('kglyph_lib', 'D:/rc_scratch/e10_design/cards/src/kglyph.py')
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _LIB['k'] = m
    return _LIB['k']


BED = (7, 9, 18)         # ring bed colour under the cells (dim target for the unit_gone_state)


def gly(L, name, px, xy, fill=(255, 255, 255), edge=INKC):
    WU.gly(L, name, px, xy, fill, edge)


# ----------------------------------------------------------------------------- unit_cell_outline
def outline(L, u, col=None, w=None):
    """R: one ink-sheathed line drawn after chevrons / tray / armour (nothing hides it).  NOW 4 px HARM, +1 3 px LANE_PLUS1, +2 3 px LANE_PLUS2 dash 12/8.
    V: the same ladder with a heavier 6.5 px sheath and the dash drawn 14/8."""
    o = opt('unit_cell_outline')
    dep = u['dep']
    c = col or LANE_COL[dep]
    ww = w or LW[dep]
    poly = WU.u_poly(u)
    pp = poly + [poly[0]]
    sheath = ww + (4.5 if o != 'V' else 7.0)
    L.line(pp, INKC, sheath)
    if dep < 2 or col is not None:
        L.line(pp, c, ww)
    else:
        d_ = (12, 8) if o != 'V' else (14, 8)
        dash_path(L, poly, c, ww, d_[0], d_[1], True)


# ----------------------------------------------------------------------------- token pieces
def halo(L, x, y, R):
    o = opt('token_halo')
    k = L.k
    if o == 'V':     # a hard sticker keyline 1.5 px plus a lighter pool
        L.glow(lambda dd: dd.ellipse([(x - R - 3) * k, (y - R - 3) * k, (x + R + 3) * k, (y + R + 3) * k], fill=(12, 10, 22, 150)), blur=4)
        L.ellipse([x - R - 1.5, y - R - 1.5, x + R + 1.5, y + R + 1.5], fill=INKC)
    else:            # tight INK pool 1.5 px past the disc, blur 4, 75 percent
        L.glow(lambda dd: dd.ellipse([(x - R - 1.5) * k, (y - R - 1.5) * k, (x + R + 1.5) * k, (y + R + 1.5) * k], fill=(12, 10, 22, 191)), blur=4)


KC_WASH = {}      # filled by wr2_sets (kind_colour_set): the one table the token disc, the cells and the arc disc read


def disc(L, x, y, R, kind, dead=False):
    o = opt('token_disc')
    kc = KCOL[kind]
    if dead:
        L.ellipse([x - R, y - R, x + R, y + R], fill=(58, 54, 66))
        return
    f = 0.26 if o != 'V' else 0.36
    L.ellipse([x - R, y - R, x + R, y + R], fill=tuple(int(v * f) for v in kc))


def ring(L, x, y, R, dep, dead=False):
    """R: the lane ring ON the rim, ladder 4 / 3 / 3 in the lane colour with ink; +2 = six long dashes (40 deg on, 20 off).  V: ring inset 2 px inside an ink rim."""
    o = opt('token_lane_base')
    col = (150, 150, 160) if dead else LANE_COL[dep]
    w = LW[dep]
    rr = R - w / 2 - (0.0 if o != 'V' else 2.0)
    if o == 'V':
        L.ellipse([x - R, y - R, x + R, y + R], outline=INKC, w=2.4)
    if dep < 2:
        WU._ring_full(L, x, y, rr, w, col)
    else:
        WU._ring_dashes(L, x, y, rr, w, col, 6, 40, 10)


def armor_cue(L, x, y, R, ang):
    """armor_cap B on the token: a steel cap over the outer 150 deg (STEEL, STEEL_HI edge) with two rivets; R is 5.5 px, V 4 px with one rivet"""
    o = opt('armor_cap')
    a_c = math.degrees(math.atan2(-math.cos(math.radians(ang)), math.sin(math.radians(ang))))
    wd = 5.5 if o != 'V' else 4.0
    pts = L.arc_pts((x, y), R + 3.0, a_c - 75, a_c + 75, 18)
    L.line(pts, INKC, wd + 3.5)
    L.line(pts, STEELC, wd)
    L.line(L.arc_pts((x, y), R + 3.0 + wd / 2 - 1.0, a_c - 70, a_c + 70, 18), STEELC_HI, 1.4)
    for a_ in ((a_c - 52, a_c + 52) if o != 'V' else (a_c,)):
        px, py = ppx_xy(x, y, R + 3.0, a_)
        L.ellipse([px - 1.4, py - 1.4, px + 1.4, py + 1.4], fill=STEELC_DK)


def ppx_xy(x, y, r, a_deg):
    return (x + r * math.cos(math.radians(a_deg)), y + r * math.sin(math.radians(a_deg)))


def token(L, u, dead=False):
    x, y = E8.token_pos(u)
    R = TOK_R
    halo(L, x, y, R)
    disc(L, x, y, R, u['kind'], dead)
    ring(L, x, y, R, u['dep'], dead)
    gly(L, KIND[u['kind']][1], 37, (x, y), (150, 150, 160) if dead else (255, 255, 255))
    if u.get('df') == 'armor' and not dead:
        ang = math.degrees(math.atan2(x - C[0], -(y - C[1])))
        armor_cue(L, x, y, R, ang)
    return x, y


# ----------------------------------------------------------------------------- unit_hp_row (+ shield_bracket)
def tray_extent(u, q, per, wp=18.0, gp=4.0):
    ly = cell_layout(u)
    rm = (ly['r0'] + ly['r1']) / 2
    axis = 60 * (u['s'] + q)
    tot = per * wp + (per - 1) * gp
    return axis - math.degrees(tot / 2 / rm), tot, rm


def hp_row(L, u, hp, mx, lose=0, shield=0, shmx=0):
    """HP grammar (BRIEF 3.11 #6): rounded segment r3; kept = CREAM (enemy); lost now = HARM + white 2 px slash + ink; gone = dark socket + solid 1.4 px hairline.
    The capacity tray is exactly one sector's capacity, centred on the sector axis.  V = pips 14 px, no tray body (only the slots)."""
    o = opt('unit_hp_row')
    ly = cell_layout(u)
    r0, r1 = ly['r0'], ly['r1']
    wp, gp = (18.0, 4.0) if o != 'V' else (13.0, 4.0)
    ST.PIPS[u['id']] = []
    w = u['w']
    per = max(1, mx // w)
    idx = 0
    for q in range(w):
        a_start, tot, rm = tray_extent(u, q, per, wp, gp)
        if o != 'V':
            tray = arc_band(ly['t_in'], ly['t_out'], a_start - math.degrees(2.2 / rm), a_start + math.degrees((tot + 2.2) / rm))
            L.poly(tray, fill=(8, 10, 20, 255), outline=INKC, w=1.4)
        for i in range(per):
            lit = idx < hp
            lost = lit and idx >= hp - lose
            aa = a_start + math.degrees(i * (wp + gp) / rm)
            ab = aa + math.degrees(wp / rm)
            if lit and not lost:
                rseg(L, r0, r1, aa, ab, CREAMC, 3.0)
            elif lost:
                rseg(L, r0, r1, aa, ab, HARM, 3.0)
                am = (aa + ab) / 2
                sl = [ppx(C, r0 - 1.8, am - math.degrees(4.6 / rm)), ppx(C, r1 + 1.8, am + math.degrees(4.6 / rm))]
                L.line(sl, INKC, 4.6)
                L.line(sl, (255, 255, 255), 2.0)
            else:      # gone: dark socket + a solid 1.4 px hairline (HP grammar)
                rseg(L, r0, r1, aa, ab, (84, 92, 120), 3.0, ink=True, ow=0.8)
                da_ = math.degrees(1.4 / rm)
                rseg(L, r0 + 1.4, r1 - 1.4, aa + da_, ab - da_, (14, 16, 30), 1.6, ink=False)
            ST.PIPS[u['id']].append((aa, ab, r0, r1, lit))
            idx += 1
    if shmx:
        shield_bracket(L, u, r0, r1, shield, shmx)


def shield_bracket(L, u, r0, r1, shield, shmx):
    """NET_CYAN 3 px under-bar (toward the tower) under the shielded pips; a lost shield point = the gone form (dark socket + solid 1.4 px cyan hairline), never dashed"""
    pips = ST.PIPS.get(u['id'])
    if not pips:
        return
    first = pips[:shmx]
    ra, rb = r0 - 6.0, r0 - 3.0
    o = opt('shield_bracket')
    for i, p in enumerate(first):
        a0_, a1_ = p[0], p[1]
        if i < shield:
            rseg(L, ra, rb, a0_, a1_, NETC, 1.4, ink=True, ow=1.2)
        else:
            rseg(L, ra, rb, a0_, a1_, (8, 12, 24), 1.4, ink=True, ow=0.8)
            L.line(arc_band(ra + 0.5, rb - 0.5, a0_ + 0.3, a1_ - 0.3) + [arc_band(ra + 0.5, rb - 0.5, a0_ + 0.3, a1_ - 0.3)[0]], alpha_mix(NETC, (8, 12, 24), 0.7), 1.4)


# ----------------------------------------------------------------------------- armor_cap (the tray's steel rails) and the cap on the token above
def rails(L, a_s, a_e, t_in, t_out, rm):
    """the steel tray frame: an outer and an inner 2.5 px rail of ~30 px plates (STEEL, STEEL_HI top edge, 1.8 px seams, rivets at the seams); V (armor_cap) = outer rail only"""
    o = opt('armor_cap')
    rl = [(t_out - 2.5, t_out), (t_in, t_in + 2.5)] if o != 'V' else [(t_out - 2.5, t_out)]
    length = math.radians(a_e - a_s) * rm
    n = max(2, int(round(length / 30.0)))
    step = (a_e - a_s) / n
    for (ra_, rb_) in rl:
        for i in range(n):
            aa, ab = a_s + i * step + math.degrees(0.9 / rm), a_s + (i + 1) * step - math.degrees(0.9 / rm)
            L.poly(arc_band(ra_, rb_, aa, ab), fill=(128, 140, 162, 255), outline=INKC, w=1.2)
            L.poly(arc_band(rb_ - 1.0, rb_ - 0.2, aa + 0.4, ab - 0.4), fill=STEELC_HI + (255,))
    for i in range(n + 1):
        x, y = ppx(C, (rl[0][0] + rl[0][1]) / 2, a_s + i * step)
        L.ellipse([x - 1.5, y - 1.5, x + 1.5, y + 1.5], fill=STEELC_DK, outline=STEELC_HI, w=0.7)


def armour_rails(L, u):
    """armor_cap B refined: ARMOUR TILES as the tray's frame (see rails), so armour costs no extra radial band: the 4-chevron Payload needs every pixel."""
    ly = cell_layout(u)
    per = max(1, u['mx'] // u['w'])
    for q in range(u['w']):
        a_start, tot, rm = tray_extent(u, q, per)
        rails(L, a_start - math.degrees(2.4 / rm), a_start + math.degrees((tot + 2.4) / rm), ly['t_in'], ly['t_out'], rm)


# ----------------------------------------------------------------------------- chevrons
def stack(L, u, ang, n_solid, n_hollow, dim=0.0):
    """chev_solid_stack A: stem-less V, HARM 6 px on 10.5 px ink.  chev_hollow B: the growth chevrons are DASHED V (dashed = growth), stacked outward.
    chev_sector_column A: a 1.4 px baseline tick under each unit's stack (the outer side) so stacks of neighbouring rings never chain."""
    ri, ro = CB.ring_geom(u['dep'])
    n = n_solid + n_hollow
    st = chev_params(u, n)
    wash = kind_wash(u['kind'], u['dep'])
    col = HARM if not dim else mix(HARM, BED, dim)
    ink = INKC
    def cp(i):
        r = ri + st['start'] + i * st['pitch']
        return [pt(r + st['depth'], ang, -st['half']), pt(r, ang, 0), pt(r + st['depth'], ang, st['half'])]
    for i in range(n_hollow):
        p = cp(n_solid + i)
        L.line(p, ink, st['w'] + 4.5)
        dash_path(L, p, col, st['w'], 8.5, 5.5, closed=False)
    for col_, w in ((ink, st['ink']), (col, st['w'])):
        for i in range(n_solid):
            L.line(cp(i), col_, w)
    r = ri + st['start'] + (n - 1) * st['pitch'] + st['depth'] + 5.25 + 1.2
    a, b = pt(r, ang, -15), pt(r, ang, 15)
    L.line([a, b], ink, 3.8)
    L.line([a, b], mix(col, BED, 0.1) if not dim else col, 1.4)


def chevrons(L, u, hit, grow, dim=0.0):
    REG['bodies'].append(dict(uid=u['id'], solid=hit, hollow=grow, sectors=u['w']))
    for q in range(u['w']):
        stack(L, u, 60 * (u['s'] + q), hit, grow, dim)


# ----------------------------------------------------------------------------- warded_mark / dead_x / unit_gone_state
def _side(u, dist, mode='cw'):
    """a point beside the token on its clockwise side at `dist` px (tangent), radial middle of the cell"""
    tx, ty = E8.token_pos(u)
    rt = math.hypot(tx - C[0], ty - C[1])
    ang_t = math.degrees(math.atan2(tx - C[0], -(ty - C[1])))
    return ppx(C, rt, ang_t + math.degrees(dist / rt))


def warded(L, u):
    """A: the boss lozenge in small, gold with a skull >= 16 px, docked on the token's clockwise shoulder (tucked 3 px over the rim)"""
    o = opt('warded_mark')
    Rr = 17 if o != 'V' else 15
    bx, by = _side(u, TOK_R + Rr - 3)
    L.glow(lambda dd: dd.polygon([((bx) * L.k, (by - Rr - 2) * L.k), ((bx + Rr + 2) * L.k, by * L.k), (bx * L.k, (by + Rr + 2) * L.k), ((bx - Rr - 2) * L.k, by * L.k)], fill=(12, 10, 22, 170)), blur=2)
    dia = [(bx, by - Rr), (bx + Rr, by), (bx, by + Rr), (bx - Rr, by)]
    L.poly(dia, fill=BOSSG, outline=INKC, w=4.0)
    ins = 5.5
    L.poly([(bx, by - Rr + ins), (bx + Rr - ins, by), (bx, by + Rr - ins), (bx - Rr + ins, by)], fill=(46, 34, 6))
    gly(L, 'X_SKULL', 17 if o != 'V' else 16, (bx, by + 0.5), BOSSG, (30, 22, 4))


def gone_overlay(L, u):
    """unit_gone_state: the cell, its outline and chevrons dimmed to 38 percent (a 62 percent bed-coloured veil over the cell incl. the sheath)"""
    ra, rb = radial_ext(u['dep'])
    b0, b1 = unit_bounds(u)
    veil = band_poly(u['dep'], b0, b1, ra - 4, rb + 4, tin=-4)
    tint(L, veil, BED, 158)             # 62 percent veil (true composite)


def dead_badge(L, u):
    """dead_x A: a GAIN X badge beside the token (28 px disc, ink rim, 4 px X), never over it.  V: a 34 px capsule on the cell's start gutter side."""
    o = opt('dead_x')
    bx, by = _side(u, TOK_R + 14 + 1)
    r = 14 if o != 'V' else 17
    L.ellipse([bx - r - 2.5, by - r - 2.5, bx + r + 2.5, by + r + 2.5], fill=INKC)
    L.ellipse([bx - r, by - r, bx + r, by + r], fill=(10, 30, 14), outline=GAINC, w=3.0)
    s = 5.4 if o != 'V' else 6.8
    for a_, b_ in (((bx - s, by - s), (bx + s, by + s)), ((bx + s, by - s), (bx - s, by + s))):
        L.line([a_, b_], INKC, 7.2)
    for a_, b_ in (((bx - s, by - s), (bx + s, by + s)), ((bx + s, by - s), (bx - s, by + s))):
        L.line([a_, b_], GAINC, 3.6)


# ----------------------------------------------------------------------------- ghosts (p2)
def wax_outline(L, poly, col, w=4.0, seed=3):
    """the outline redrawn in WAX PENCIL (same material as trigger_path): an ink-dark under-stroke, a wobbling 4 px wax line, a lighter grain streak, and
    the stroke closes with a 7 px overshoot like a hand-drawn loop"""
    rnd = random.Random(seed)
    pts = resample(poly + [poly[0]], 2.0)
    n = len(pts)
    loop = pts + pts[:4]
    out = []
    ph = rnd.random() * 6
    for i, (x, y) in enumerate(loop):
        dx = 0.55 * math.sin(i * 0.31 + ph) + 0.25 * math.sin(i * 0.9)
        dy = 0.55 * math.cos(i * 0.27 + ph) + 0.25 * math.cos(i * 0.8)
        out.append((x + dx, y + dy))
    L.line(out, (6, 3, 8), w + 4.0)
    L.line(out, col, w)
    grain = [(x + 0.7, y - 0.7) for (x, y) in out]
    L.line(grain, mix(col, (255, 255, 255), 0.45), 1.2)


def ghost(L, u, kind, beat='p2'):
    """consumed_unit A: ghost at 40 percent (the shared ghost: the cell wash mixed 62 percent to the bed), PENCIL_PLAN 3 px outline, grey token, the Trigger stamp from the library beside it.
    trigger_killed_unit A: same ghost, a small GAIN X beside the token, the outline redrawn in wax pencil.  V (killed): the wax outline in PENCIL_THREAT.  V (consumed): outline 4 px + stamp 30 px."""
    o = opt('consumed_unit') if kind == 'consumed' else opt('trigger_killed_unit')
    poly = WU.u_poly(u)
    wash = kind_wash(u['kind'], u['dep'])
    ghostc = mix(wash, BED, 0.62)
    L.poly(poly, fill=ghostc + (255,))
    pp = poly + [poly[0]]
    if kind == 'consumed':
        ww = 3.0 if o != 'V' else 4.0
        L.line(pp, INKC, ww + 4.5)
        L.line(pp, PLAN, ww)
    else:
        wax_outline(L, poly, PLAN if o != 'V' else PLAN_THREAT, 4.0, seed=u['id'] * 7 + 1)
    x, y = E8.token_pos(u)
    R = TOK_R
    L.ellipse([x - R - 1.5, y - R - 1.5, x + R + 1.5, y + R + 1.5], fill=INKC)
    L.ellipse([x - R, y - R, x + R, y + R], fill=(58, 54, 66))
    ring(L, x, y, R, u['dep'], dead=True)
    gly(L, KIND[u['kind']][1], 34, (x, y), (176, 172, 186))
    bx, by = _side(u, TOK_R + 14)
    if kind == 'consumed':
        r = 14 if o != 'V' else 17
        L.ellipse([bx - r - 2.5, by - r - 2.5, bx + r + 2.5, by + r + 2.5], fill=INKC)
        L.ellipse([bx - r, by - r, bx + r, by + r], fill=(30, 26, 6), outline=PLAN, w=2.4)
        library()
        gly(L, 'KA_trigger', 20 if o != 'V' else 24, (bx, by), PLAN)
    else:
        r = 11
        L.ellipse([bx - r - 2.5, by - r - 2.5, bx + r + 2.5, by + r + 2.5], fill=INKC)
        L.ellipse([bx - r, by - r, bx + r, by + r], fill=(10, 30, 14), outline=GAINC, w=2.2)
        s = 4.2
        for a_, b_ in (((bx - s, by - s), (bx + s, by + s)), ((bx + s, by - s), (bx - s, by + s))):
            L.line([a_, b_], INKC, 5.6)
        for a_, b_ in (((bx - s, by - s), (bx + s, by + s)), ((bx + s, by - s), (bx - s, by + s))):
            L.line([a_, b_], GAINC, 2.8)


# ----------------------------------------------------------------------------- one unit, R2 order
def draw_unit(L, u, f, beat):
    """R2 order: [cell screen is already under] -> warded lozenge (under the threat) -> chevrons -> sheathed outline -> [gone veil] -> HP tray -> armour rails -> token -> dead badge"""
    dying = u['fate']['kind'] == 'dies'
    grow = max(0, u['land_hit'] - u['hit']) if (u['fate']['kind'] == 'lands' and 'land_hit' in u) else 0
    if u['warded']:
        warded(L, u)
    chevrons(L, u, u['hit'], grow, dim=0.0)
    outline(L, u)
    if dying:
        gone_overlay(L, u)
    hp_row(L, u, u['hp'], u['mx'], lose=u['lose'][1], shield=u['sh'], shmx=u['shmx'])
    if u['df'] == 'armor':
        armour_rails(L, u)
    token(L, u)
    if dying:
        dead_badge(L, u)


def active():
    return opt('unit_hp_row') in ('R', 'V')
