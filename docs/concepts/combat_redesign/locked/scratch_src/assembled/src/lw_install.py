"""cs_run: render the REBEL_CELL combat plate (linocut A) with a CORP SKIN on the enemy layers.   python cs_run.py solace|meridian|none [beat]"""
import sys, os, math, time
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
import f1_render as R
import cs_skin as CS
from cs_skin import region_apply, polar, Acc
from cv_lib import C, L2, ppx

A = R.A
ROOT = 'D:/rc_scratch/combat_redesign/locked/assembled/'
SK = [None]


def circle_poly(r, n=360):
    return [ppx(C, r, 360.0 * i / n) for i in range(n)]


def _over_img(base, rgb, a, x0, y0):
    out = np.dstack([np.clip(rgb, 0, 255), np.clip(a, 0, 1) * 255]).astype(np.uint8)
    base.alpha_composite(Image.fromarray(out, 'RGBA'), (x0, y0))


# --------------------------------------------------------------------------------------------- ring cells
_orig_paint = R.paint_cells
_orig_gut = A.W2C.gutters


def gutters(L, f):
    s = SK[0]
    for dep in range(3):
        ri, ro = A.CB9.ring_geom(dep)
        L.poly(L.band(C, ri, ro, 0, 359.9), fill=s.pal['bed'] + (255,))


def paint_cells(L, f, beat, which=None, with_base=True):
    s = SK[0]
    _orig_paint(L, f, beat, which=which, with_base=with_base)
    from wr_geo import cell_poly, unit_bounds
    polys_e, polys_u = [], []
    if with_base:
        cov = A.WCL.covered(f)
        for dep in range(3):
            for sc in range(6):
                if (dep, sc) not in cov:
                    polys_e.append((dep, cell_poly(dep, 60 * sc - 30, 60 * sc + 30, kind='empty')))
    for u in A.WCL.live_units(f):
        if which is not None and u['id'] not in which:
            continue
        if u['w'] == 6:
            continue
        b0, b1 = unit_bounds(u)
        polys_u.append((u['dep'], cell_poly(u['dep'], b0, b1, kind='unit')))
    allp = [p for _, p in polys_e + polys_u]
    if allp:
        region_apply(L, allp, s.cell)
    for (dep, p) in polys_e:
        s.cell_detail(L, p, dep, True, 0)
    for (dep, p) in polys_u:
        s.cell_detail(L, p, dep, False, 0)
    if hasattr(s, 'empty_marks') and polys_e:
        s.empty_marks(L, polys_e)


# --------------------------------------------------------------------------------------------- tokens
_orig_halo = A.W2U.halo


def halo(L, x, y, R_):
    _orig_halo(L, x, y, R_)
    SK[0].token_frame(L, x, y, R_, None, None)


_orig_disc = A.A2.disc


def a2_disc(L, r, th, px, u, lane, opt):
    s = SK[0]
    fr = A.A2.Fr(r, th, px)
    R_ = 13.5 if opt == 'P' else 12.0
    s.disc_frame(L, fr.x, fr.y, R_)
    return _orig_disc(L, r, th, px, u, lane, opt)


_orig_frame = A.A2.frame


def a2_frame(L, r, a0, a1, lane, opt):
    _orig_frame(L, r, a0, a1, lane, opt)
    HALF = A.A2.HALF
    ins = 3.4
    da = 57.3 / r
    cap = HALF * da
    n = max(8, int((a1 - a0) / 3))
    ae = a1 - 0.9 * HALF * da
    outer = [ppx(C, r + HALF - ins, a0 + cap + (ae - a0 - cap) * i / n) for i in range(n + 1)]
    inner = [ppx(C, r - HALF + ins, ae - (ae - a0 - cap) * i / n) for i in range(n + 1)]
    region_apply(L, [outer + inner], SK[0].arcframe)


# --------------------------------------------------------------------------------------------- schedule tape: hue remap + material
_orig_sched = A.S2.schedule
_orig_labels = A.S2.labels


def _remap(L, mk):
    """the THIS TURN tape: one neutral treatment, applied for every corp (lw_skin.NeutralTape); the skin is not consulted"""
    from lw_skin import NeutralTape
    L.im.load()
    L.im.paste(NeutralTape.remap(L.im))


def ndi_open(b):
    from scipy import ndimage as ndi
    return ndi.binary_opening(b, iterations=1)


def schedule(L, sched, sel):
    T = L2()
    _orig_sched(T, sched, sel)
    _remap(T, True)
    L.im.alpha_composite(T.im)


def labels(L, sched, sel={}):
    T = L2()
    _orig_labels(T, sched, sel)
    _remap(T, False)
    L.im.alpha_composite(T.im)


# --------------------------------------------------------------------------------------------- plate (landing annulus), bezel, rim
_orig_plate = A.G2.plate
_orig_bezel = A.G2.bezel_layer


def _band_fn(skin_fn, r0, r1, feather=0.8):
    def fn(X, Y, RHO, TH):
        rgb, a = skin_fn(X, Y, RHO, TH)
        band = np.clip((RHO - r0) / feather + 0.5, 0, 1) * np.clip((r1 - RHO) / feather + 0.5, 0, 1)
        return rgb, a * band
    return fn


def _overlay(im, polys, fn, k=2):
    """composite fn() over a 1x RGBA PIL image via a 2x temp layer"""
    T = L2()
    region_apply(T, polys, fn, k=k)
    im.alpha_composite(T.done())


def plate(opt):
    s = SK[0]
    im = _orig_plate(opt).convert('RGBA')
    sq = circle_poly(500.0, 180)
    _overlay(im, [circle_poly(488.0, 180)], _band_fn(s.annulus, 424, 488))
    T = L2()
    region_apply(T, [circle_poly(501.0, 180)], _band_fn(s.rim, 489.0, 500.0, 0.5))
    # keylines + crests (vector)
    s.rim_vector(T)
    # ink edges of the rim
    for r in (488.4, 500.4):
        T.line(T.arc_pts(C, r, 0, 360, 360), (8, 8, 8, 255), 1.5)
    s.rim_vector_after(T) if hasattr(s, 'rim_vector_after') else None
    im.alpha_composite(T.done())
    return im


def bezel_layer(opt, rim='P'):
    s = SK[0]
    im = _orig_bezel(opt, rim).convert('RGBA')
    arr = np.asarray(im).astype(np.float32)
    # keep the original ink at the six spokes and the outer ink edge: skin only the enamel body (where the original is neither ink nor transparent)
    T = L2()
    region_apply(T, [circle_poly(423.0, 180)], _band_fn(s.bezel, 388.0, 422.0, 0.6))
    skin = T.done()
    import o_ground as OG
    sp = OG.RHO * 0
    from r2_ground import spoke_mask
    spm = spoke_mask(386, 424, 4.0)[..., None]
    sa = np.asarray(skin).astype(np.float32)
    k = (sa[..., 3:4] / 255.0) * (1 - spm)
    arr[..., :3] = arr[..., :3] * (1 - k) + sa[..., :3] * k
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')


# --------------------------------------------------------------------------------------------- tickets (future-wave plates)
import gram_render as GR
_orig_plate_fn = GR.engraved_plate


def engraved_plate(L, box, col_edge, dotted_edge=False, cut=False, fill=None):
    SK[0].ticket(L, box, sum(col_edge) > 560, cut)


def install(skin):
    SK[0] = skin
    A.W2C.gutters = gutters
    R.paint_cells = paint_cells
    A.W2U.halo = halo
    A.A2.disc = a2_disc
    A.A2.frame = a2_frame
    A.S2.schedule = schedule
    A.S2.labels = labels
    A.G2.plate = plate
    A.G2.bezel_layer = bezel_layer
    GR.engraved_plate = engraved_plate
    import f1_board as FB
    if skin.name != 'solace':
        FB.helix = lambda *a, **k: None     # the base E material's double-helix rule is Solace's own; other corps drop it
    FB.ticket = lambda L, box, edge, cut, fill=None: SK[0].ticket(L, box, sum(edge) > 560, cut)


