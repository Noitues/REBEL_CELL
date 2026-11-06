"""R2 cell painters: ring_separators (INK gutters + interior hairlines), empty_cell (void tint), unit_cell_screen (CRT bowl on the shared 3 px mesh).
unit_screen_bezel, unit_screen_code_text, screen_motif_skull are 'removed / none' (R1 option A everywhere) so nothing is drawn for them."""
import math
from wr_state import opt
from wr_geo import *
from wr2_lib import *
import wr_cells as WC


def gutters(L, f):
    """ring_separators R: the gutter bed is INK itself.  Every cell is inset G/2 = 4 px on every side, so every gutter (between rings and between sectors) is exactly 8 px,
    the same as the 8 px INK slice spokes.  V = a bed one step lighter than the back plate (the R1 pick B)."""
    bed = INKC if opt('ring_separators') == 'R' else GUT_FILL
    for dep in range(3):
        ri, ro = CB.ring_geom(dep)
        L.poly(L.band(C, ri, ro, 0, 359.9), fill=bed + (255,))


def interior_hairlines(L, f):
    """wide cells keep ONE body: 1.4 px interior hairlines at 30 percent in the lane colour at every interior sector boundary (R); V = the R1 notched spoke"""
    o = opt('ring_separators')
    for u in WC.live_units(f):
        if u['w'] < 2 or u['w'] == 6:
            continue
        ra, rb = radial_ext(u['dep'])
        wash = kind_wash(u['kind'], u['dep'])
        for q in range(1, u['w']):
            a = 60 * (u['s'] + q) - 30
            x0, y0 = ppx(C, ra + 1, a)
            x1, y1 = ppx(C, rb - 1, a)
            if o == 'R':
                L.line([(x0, y0), (x1, y1)], mix(wash, LANE_COL[u['dep']], 0.30), 1.4)
            else:
                L.line([(x0, y0), (x1, y1)], mix(wash, (6, 4, 18), 0.55), 1.6)
                for (r0, r1) in ((ra, ra + 12), (rb - 12, rb)):
                    xa, ya = ppx(C, r0, a)
                    xb, yb = ppx(C, r1, a)
                    L.line([(xa, ya), (xb, yb)], INKC, 6.5)


def empty_cell(L, dep, s):
    """R: void tint (one step lifted dark glass), ONE 1.4 px lane hairline at 30 percent, no orange edge, a faint sheen on the outer edge.  V: no sheen, darker glass."""
    o = opt('empty_cell')
    lane = LANE_COL[dep]
    b0, b1 = 60 * s - 30, 60 * s + 30
    fill = (17, 24, 40) if o == 'R' else (13, 18, 32)
    poly = cell_poly(dep, b0, b1, kind='empty')
    L.poly(poly, fill=fill + (255,))
    L.line(poly + [poly[0]], mix(fill, lane, 0.30), 1.4)
    if o == 'R':
        ra, rb = radial_ext(dep, 4, 4)
        L.line(L.arc_pts(C, rb, b0 + 5, b1 - 5), mix(fill, (150, 180, 230), 0.14), 1.6)


def screen(L, u):
    """unit_cell_screen R: CRT bowl: dark inner edge (where the chevrons sit) rising to a lit outer edge (the HP tray), mauve values kept (PL10),
    plus the shared 3 px mesh (max 8 percent lift).  V: a gentler bowl with the mesh at 5 percent."""
    o = opt('unit_cell_screen')
    wash = kind_wash(u['kind'], u['dep'], ramp=(-0.08, 0.12, 0.32))
    dark = mix(wash, (6, 4, 18), 0.55 if o == 'R' else 0.38)
    WC._gradient_fill(L, u, lambda t: mix(dark, wash, min(1.0, t * 1.15) ** 0.9))
    b0, b1 = unit_bounds(u)
    mesh(L, cell_poly(u['dep'], b0, b1, kind='unit'), 0.08 if o == 'R' else 0.05)
