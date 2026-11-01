"""R2 ring_unit_wide6: a seamed band, square lane-colour end caps at the seam, the token at the start cap (the token_placement rule), HP per sector axis."""
import math
from wr_state import opt
from wr_geo import *
from wr2_lib import *
import wr2_units as W2U


def wide6(L, u, f):
    o = opt('ring_unit_wide6')
    dep = u['dep']
    ra, rb = radial_ext(dep)
    b0, b1 = unit_bounds(u)
    wash = kind_wash(u['kind'], dep, ramp=(-0.08, 0.12, 0.32))
    dark = mix(wash, (6, 4, 18), 0.55)
    n = int((rb - ra) / 2.0) + 1
    for i in range(n):
        t = (i + 0.5) / n
        r0 = ra + (rb - ra) * i / n
        r1 = min(rb, ra + (rb - ra) * (i + 1) / n + 0.8)
        L.poly(band_poly(dep, b0, b1, r0, r1), fill=mix(dark, wash, min(1.0, t * 1.15) ** 0.9) + (255,))
    poly = cell_poly(dep, b0, b1, kind='unit', n=170)
    mesh(L, poly, 0.08)
    W2U.chevrons(L, u, u['hit'], 0)
    W2U.outline(L, u)
    lane = LANE_COL[dep]
    for a_, sg in ((b0 + dA(ra, 8), 1), (b0 + 360 - dA(ra, 8), -1)):      # square end caps: the seam reads as a start (token side) and an end
        cap = [ppx(C, ra + 1, a_), ppx(C, rb - 1, a_), ppx(C, rb - 1, a_ + sg * math.degrees(7 / rb)), ppx(C, ra + 1, a_ + sg * math.degrees(7 / ra))]
        L.poly(cap, fill=lane + (255,), outline=INKC, w=1.8)
    if o == 'V':     # a head chevron at the clockwise end: the way it travels
        a = b0 + 360 - dA(ra, 8) - 9
        tip = [ppx(C, ra + 6, a - 4), ppx(C, (ra + rb) / 2, a + 3), ppx(C, rb - 6, a - 4)]
        L.line(tip, INKC, 8.5)
        L.line(tip, lane, 4.5)
    W2U.hp_row(L, u, u['hp'], u['mx'], lose=u['lose'][1])
    W2U.token(L, u)
