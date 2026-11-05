"""rb_focus (round 2, 2026-11-04, call C2): THE FOCUS drawer (VISUAL_PLAN E / H) for the board AND the hover set.
FOCUS #D4FF00 as four separate 12 px corner brackets (2 px legal, 3.5 px aimed) on a 3.2 px ink keyline: never joined, never a full outline,
never the old a_kit lime #96FF46 (it is the Solace leaf hue, dE76 0.6 from the corp rim).
The geometry is the hover set's (corp/src hz_core.focus_cell -> safe_corners, hv_lib_h2.band_corners / rect_corners); hz_core / hv_core can
call cell() / band() / rect() here.  Every stroke is recorded (MASK, CALLS) for the checks; its layer is flagged for the BOX reduction (rb4)."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
import rb_tokens as T
from cv_lib import C, ppx, L2

FOCUS = T.TOKENS['FOCUS']
INKC = (12, 10, 22)
LEG = 12.0                 # bracket leg (each arm), px
W_LEGAL, W_AIM = 2.0, 3.5  # legal target / aimed target
INK_EXTRA = 3.2            # ink keyline: stroke + 3.2 px (1.6 each side)
CELL_IN_R, CELL_IN_A = 3.5, 2.5      # the corners sit 3.5 px inside the cell's radial edges and 2.5 deg inside its sides (hz_core.focus_cell)
MASK = {}
CALLS = []


def reset():
    MASK.clear()
    CALLS.clear()


def band_polys(ri, ro, a0, a1, leg=LEG):
    polys = []
    for r, dr in ((ri, 1), (ro, -1)):
        for a, da in ((a0, 1), (a1, -1)):
            polys.append([ppx(C, r + dr * leg, a), ppx(C, r, a)] + [ppx(C, r, a + da * math.degrees(leg / r) * i / 4) for i in range(1, 5)])
    return polys


def rect_polys(box, leg=LEG, pad=3.0):
    x0, y0, x1, y1 = box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad
    leg = min(leg, (x1 - x0) / 2 - 2, (y1 - y0) / 2 - 2)
    return [[(x + dx * leg, y), (x, y), (x, y + dy * leg)] for (x, y, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1))]


def draw(L, polys, aimed=False, tag=''):
    w = W_AIM if aimed else W_LEGAL
    Tl = L2(L.k)
    for p in polys:
        Tl.line(p, INKC, w + INK_EXTRA)
    for p in polys:
        Tl.line(p, FOCUS, w)
    a = Tl.im.split()[3]
    import rb_pencil as _PEN
    _PEN.pen_mask(Tl.im).paste(255, (0, 0), a.point(lambda v: 255 if v > 0 else 0))
    L.im.alpha_composite(Tl.im)                    # rb4_patch's alpha_composite hook carries the BOX footprint onto L
    m = np.asarray(a.resize((1920, 1080), Image.BOX)) >= 96
    MASK['m'] = MASK.get('m', np.zeros((1080, 1920), bool)) | m
    CALLS.append(dict(tag=tag, n_corners=len(polys), w=w, leg=LEG))


def band(L, ri, ro, a0, a1, aimed=False, tag=''):
    draw(L, band_polys(ri, ro, a0, a1), aimed, tag)


def rect(L, box, aimed=False, pad=3.0, tag=''):
    draw(L, rect_polys(box, LEG, pad), aimed, tag)


def cell(L, u, aimed=True):
    """FOCUS on a unit's cell (the hover set's focus_cell geometry)"""
    import cv_board as CB
    ri, ro = CB.ring_geom(u['dep'])
    a0 = 60 * u['s'] - 30
    a1 = 60 * (u['s'] + u['w'] - 1) + 30
    band(L, ri + CELL_IN_R, ro - CELL_IN_R, a0 + CELL_IN_A, a1 - CELL_IN_A, aimed, tag='unit %d' % u['id'])


def brackets_compat(L, shape, g, opt='A', w=None, arm=None, grow=4.0, col=None):
    """a2_kit.focus_brackets signature, every caller: four FOCUS corners at the spec (the old arm / width / colour arguments are retired)"""
    aimed = (w or 0) >= 3.5
    if shape == 'band':
        band(L, g['ri'], g['ro'], g['a0'], g['a1'], aimed, tag='band')
    else:
        if shape == 'circle':
            (cx, cy), r = g['c'], g['r']
            box = (cx - r, cy - r, cx + r, cy + r)
        else:
            box = g['box']
        rect(L, box, aimed, pad=grow, tag='rect')
