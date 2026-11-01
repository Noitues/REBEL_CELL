"""asm_units: the wave-ring unit token with the Y9 badge rule.
Warded lozenge and dead-X badge sit ON THE TOKEN RIM: centre 31 px from the token centre at 45 deg between the start cap (counter-clockwise end of the cell) and the outer
radius (the side away from the chevron column).  Draw order: halo, disc, ring, badge, glyph, armour cue.  The badge never lies under the glyph silhouette:
the overlap is measured and the badge steps down 2 px until its alpha over the glyph mask is 0 (BADGE_LOG records every unit)."""
import sys, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import e8lib as E8
import wr_units as WU
import wr2_units as W2U
from wr2_lib import *
from wr_geo import *
import asm_glyphs as AG
import kglyph2 as KG
from e10lib import REG

BADGE_LOG = []
BADGE_D = 31.0
GLYPH_PX = 37
SS = 4          # overlap grid px per screen px


def badge_dir(u):
    """unit vector from the token centre toward the badge: 45 deg between 'back to the start cap' (-tangent, tangent = clockwise) and 'outward' (+radial)"""
    x, y = E8.token_pos(u)
    a = math.atan2(x - C[0], -(y - C[1]))        # angle from 12 o'clock, clockwise
    t = (math.cos(a), math.sin(a))               # clockwise tangent
    n = (math.sin(a), -math.cos(a))              # outward radial
    vx, vy = -t[0] + n[0], -t[1] + n[1]
    d = math.hypot(vx, vy)
    return vx / d, vy / d


def badge_xy(u, dist=BADGE_D):
    x, y = E8.token_pos(u)
    dx, dy = badge_dir(u)
    return x + dx * dist, y + dy * dist


def _glyph_grid(kind):
    m = KG.mask(AG.KIND_ID[kind]).resize((GLYPH_PX * SS, GLYPH_PX * SS), Image.LANCZOS)
    half = 64
    g = Image.new('L', (2 * half * SS, 2 * half * SS), 0)
    g.paste(m, (half * SS - GLYPH_PX * SS // 2, half * SS - GLYPH_PX * SS // 2))
    g = g.filter(ImageFilter.MaxFilter(2 * SS + 1))        # + the 7.5 percent ink outline (about 2 px)
    return np.asarray(g) > 10, half


def _shape_mask(shape, off, size, half):
    im = Image.new('L', (2 * half * SS, 2 * half * SS), 0)
    d = ImageDraw.Draw(im)
    cx, cy = (half + off[0]) * SS, (half + off[1]) * SS
    r = (size + 2.5) * SS            # ink rim
    if shape == 'dia':
        d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=255)
    else:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    return np.asarray(im) > 10


def fit_badge(u, shape, size0, min_size):
    """largest size (stepping down 2 px) whose alpha over the glyph mask is exactly 0.  returns (size, overlap_px_at_final)"""
    g, half = _glyph_grid(u['kind'])
    dx, dy = badge_dir(u)
    off = (dx * BADGE_D, dy * BADGE_D)
    size = size0
    while True:
        ov = int((g & _shape_mask(shape, off, size, half)).sum())
        if ov == 0 or size - 2 < min_size:
            return size, ov
        size -= 2


def warded_badge(L, u, size):
    bx, by = badge_xy(u)
    Rr = size
    L.glow(lambda dd: dd.polygon([((bx) * L.k, (by - Rr - 2) * L.k), ((bx + Rr + 2) * L.k, by * L.k), (bx * L.k, (by + Rr + 2) * L.k), ((bx - Rr - 2) * L.k, by * L.k)], fill=(12, 10, 22, 170)), blur=2)
    dia = [(bx, by - Rr), (bx + Rr, by), (bx, by + Rr), (bx - Rr, by)]
    L.poly(dia, fill=BOSSG, outline=INKC, w=4.0)
    ins = 5.5 * Rr / 15.0
    L.poly([(bx, by - Rr + ins), (bx + Rr - ins, by), (bx, by + Rr - ins), (bx - Rr + ins, by)], fill=(46, 34, 6))
    W2U.gly(L, 'X_SKULL', 16 * Rr / 15.0, (bx, by + 0.5), BOSSG, (30, 22, 4))


def dead_badge(L, u, r):
    bx, by = badge_xy(u)
    L.ellipse([bx - r - 2.5, by - r - 2.5, bx + r + 2.5, by + r + 2.5], fill=INKC)
    L.ellipse([bx - r, by - r, bx + r, by + r], fill=(10, 30, 14), outline=GAINC, w=3.0)
    s = 5.4 * r / 14.0
    for a_, b_ in (((bx - s, by - s), (bx + s, by + s)), ((bx + s, by - s), (bx - s, by + s))):
        L.line([a_, b_], INKC, 7.2)
    for a_, b_ in (((bx - s, by - s), (bx + s, by + s)), ((bx + s, by - s), (bx - s, by + s))):
        L.line([a_, b_], GAINC, 3.6)


def token(L, u, dead=False, badges=True):
    x, y = E8.token_pos(u)
    R = TOK_R
    W2U.halo(L, x, y, R)
    W2U.disc(L, x, y, R, u['kind'], dead)
    W2U.ring(L, x, y, R, u['dep'], dead)
    dying = u['fate']['kind'] == 'dies'
    if badges and not dead:
        if u['warded']:
            size, ov = fit_badge(u, 'dia', 15, 11)       # 30 px lozenge, 16 px skull
            BADGE_LOG.append(dict(uid=u['id'], kind=u['kind'], badge='warded', size=size * 2, overlap_px=ov))
            warded_badge(L, u, size)
        if dying:
            size, ov = fit_badge(u, 'disc', 13, 9)       # 26 px badge
            BADGE_LOG.append(dict(uid=u['id'], kind=u['kind'], badge='dead', size=size * 2, overlap_px=ov))
            dead_badge(L, u, size)
    W2U.gly(L, KIND[u['kind']][1], 37, (x, y), (150, 150, 160) if dead else (255, 255, 255))
    if u.get('df') == 'armor' and not dead:
        ang = math.degrees(math.atan2(x - C[0], -(y - C[1])))
        W2U.armor_cue(L, x, y, R, ang)
    return x, y


def draw_unit(L, u, f, beat):
    """wr2_units.draw_unit order (chevrons -> outline -> [gone veil] -> HP tray -> armour -> token) with the badges inside the token (Y9)"""
    dying = u['fate']['kind'] == 'dies'
    grow = max(0, u['land_hit'] - u['hit']) if (u['fate']['kind'] == 'lands' and 'land_hit' in u) else 0
    W2U.chevrons(L, u, u['hit'], grow, dim=0.0)
    W2U.outline(L, u)
    if dying:
        W2U.gone_overlay(L, u)
    W2U.hp_row(L, u, u['hp'], u['mx'], lose=u['lose'][1], shield=u['sh'], shmx=u['shmx'])
    if u['df'] == 'armor':
        W2U.armour_rails(L, u)
    token(L, u)
