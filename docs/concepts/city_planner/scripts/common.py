"""Shared build steps for the design scripts."""
import math
import random

from citymap import COL, SLUM, TEXT, tint
from geom import blob

NEU = (150, 162, 182)


def mblob(cx, cy, rx, ry, seed, amp=0.08, n=18):
    return blob(cx, cy, rx, ry, random.Random(seed), amp, n)


def fabric(m, grid_poly, grid_angle, suburb_poly, suburb_c, suburb_r, hinterland_angle=14, seed=2):
    """Rail-era grid + mid-century suburbs + rural hinterland, filling whatever is still free."""
    f1, _ = m.free_mask(grid_poly, True)
    m.img.paste(NEU, mask=f1.point(lambda v: int(v * 0.10)))
    m.tex_grid(f1, grid_angle, 9, jitter=0.08, major=5, color=NEU, a_minor=0.34, a_major=0.5, seed=seed, gap=0.04)
    f2, _ = m.free_mask(suburb_poly, True)
    m.img.paste(NEU, mask=f2.point(lambda v: int(v * 0.07)))
    m.tex_curvi(f2, suburb_c, suburb_r[0], suburb_r[1], 7.5, 0, 6.2832, 0.28, 20, NEU, 0.40, cul=140, seed=seed + 1)
    f3, _ = m.free_mask([(0, 0), (1000, 0), (1000, 1000), (0, 1000)], False)
    m.img.paste((88, 110, 78), mask=f3.point(lambda v: int(v * 0.12)))
    m.tex_grid(f3, hinterland_angle, 26, 22, jitter=0.2, warp_amp=14, warp_wl=180, gap=0.35, seg=(40, 120), major=0,
               color=(120, 140, 108), a_minor=0.35, seed=seed + 3)
    m.tex_dots(f3, 500, (50, 90, 54), 0.5, 1.4, seed=seed + 7)


def slums(m, polys, density=0.55, seed=0):
    for i, poly in enumerate(polys):
        mk, pts = m.free_mask(poly, True)
        m.fill_mask(mk, SLUM, 0.12)
        m.tex_slum(mk, density, SLUM, 0.62, seed=seed + i)
        m.line(pts + [pts[0]], SLUM, 0.8, 0.5, clip=m.dry)


def corp_walls(m, keys):
    for key in keys:
        pts = m.z[key]['poly']
        w = m.wall(pts, COL[key], closed=True)
        m.gates_on(w)


def glyphs(m, items, r=7.4):
    for (x, y, k) in items:
        m.glyph(k, x, y, r)


def district_labels(m, items):
    """items: (key, x, y, text, size, angle)"""
    for key, x, y, text, size, ang in items:
        m.text(x, y, text, size, tint(COL[key], 0.4), spacing=5 if size >= 20 else 4, angle=ang)


def small_labels(m, items, size=8.5):
    for (x, y, t) in items:
        m.text(x, y, t, size, (214, 220, 232), spacing=1, weight='SemiBold')


def shields(m, items):
    for (x, y, t) in items:
        m.shield(x, y, t)


def wind(m, x, y, ang=0.0, label='PREVAILING WIND'):
    L = 60
    p0 = (x - L / 2 * math.cos(ang), y - L / 2 * math.sin(ang))
    p1 = (x + L / 2 * math.cos(ang), y + L / 2 * math.sin(ang))
    m.line([p0, p1], (200, 215, 235), 1.6, 0.9)
    m.poly([p1, (p1[0] - 11 * math.cos(ang - 0.45), p1[1] - 11 * math.sin(ang - 0.45)),
            (p1[0] - 11 * math.cos(ang + 0.45), p1[1] - 11 * math.sin(ang + 0.45))], (200, 215, 235), 0.9)
    m.text(x, y - 14, label, 9, (200, 215, 235), spacing=1.5, weight='SemiBold')


def era_rings(m, c, specs, seed=5):
    from geom import catmull
    for (rx, ry, label, lx, ly) in specs:
        d = catmull(mblob(c[0], c[1], rx, ry, seed), closed=True, step=3)
        m.line(d + [d[0]], (240, 220, 180), 0.9, 0.6, dash=(3, 2.5), clip=m.dry)
        m.text(lx, ly, label, 7.5, (240, 220, 180), weight='Regular')
