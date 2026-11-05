"""rb_pencil (round 2, 2026-11-04, call C1): THE grease pencil (VISUAL_PLAN A.5 / B L6) for the board AND the hover set.
7 px PLAN wax, a 3 px ink edge each side, wax grain (8 % value noise, darkens only) with drag streaks and a ragged wax edge, round caps, no glow.

The stroke code is the hover set's drawer (locked/rebuild/hover/src/hv_core.py wax_stroke / _stamp / _wax_layer / wax_fill, 2026-11-04),
moved here so that one file draws every pencil mark: the board's p2 trigger path and its X caps, the p2b hover path and its open arrowhead,
the bill's plan underline, and the hover plates (hv_core may import this module instead of its own copy; the numbers are the same).

Every stroke is recorded for the checks: its class, centre line and 1x coverage (STROKES, COV); the layer it is drawn on is flagged so that
its pencil pixels are reduced to 1x with a BOX filter (rb4_patch: LANCZOS rings at the wax / ink edge and lifts the wax over its pigment)."""
import math, hashlib, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import hv_lib_h2 as HL
import rb_tokens as T

W, H = 1920, 1080
PLAN = T.TOKENS['PLAN']
INKC = (12, 10, 22)
PEN_W, PEN_INK = 7.0, 3.0             # VISUAL_PLAN A.5 / B L6: 7 px wax, 3 px ink edge (each side)
PEN_GRAIN = 0.08                      # wax grain: value noise, 8 percent
PEN_GRAIN_SIGMA = 0.9                 # grain blob size, 1x px
PEN_DRAG = 0.15                       # drag streaks along the stroke (wax drawn on glass): value drop
PEN_DRAG_N = 3                        # streaks per stroke
PEN_DRAG_W = 0.9                      # streak width, 1x px
PEN_EDGE_JIT = 0.45                   # ragged wax edge, 1x px
X_ARM = 13.0                          # half length of an X cap stroke (the board trigger path's target X)
V_ARM = 19.0                          # open arrowhead stroke length (hover path)
MASKS = {}                            # cls_wax / cls_all -> bool (H, W), 50 % coverage
COV = {}                              # the same classes as 1x coverage (0-1)
STROKES = []                          # per stroke: cls, colour, centre line length, w, ink


def reset():
    MASKS.clear()
    COV.clear()
    STROKES.clear()


def _add(cls, m, cov, x0, y0):
    full = MASKS.setdefault(cls, np.zeros((H, W), bool))
    fc = COV.setdefault(cls, np.zeros((H, W), np.float32))
    h, w = m.shape
    xa, ya = max(0, x0), max(0, y0)
    xb, yb = min(W, x0 + w), min(H, y0 + h)
    if xb > xa and yb > ya:
        full[ya:yb, xa:xb] |= m[ya - y0:yb - y0, xa - x0:xb - x0]
        np.maximum(fc[ya:yb, xa:xb], cov[ya - y0:yb - y0, xa - x0:xb - x0], out=fc[ya:yb, xa:xb])


def pen_mask(im):
    """the BOX-reduction footprint attached to a 2x layer image (rb4_patch: L2.done and Image.alpha_composite carry it)"""
    pm = getattr(im, '_pen_mask', None)
    if pm is None:
        pm = Image.new('L', im.size, 0)
        im._pen_mask = pm
    return pm


def _flag(L, mi, x0, y0, k):
    """remember the pencil footprint (2x, ink included) on the layer image: rb4_patch's L2.done reduces these pixels with BOX"""
    pen_mask(L.im).paste(255, (x0 * k, y0 * k), mi.point(lambda v: 255 if v > 0 else 0))


def _wax_layer(shape_k, wax_m, ink_m, col, seed, k, streaks):
    """RGBA (2x) of a wax stroke: ink where ink_m, wax colour x grain where wax_m.  wax_m / ink_m: float 0..1 at 2x."""
    rng = np.random.default_rng(seed)
    hh, ww = shape_k
    n = ndi.gaussian_filter(rng.standard_normal((hh, ww)), PEN_GRAIN_SIGMA * k)
    n = n / (n.std() + 1e-6)
    v = 1.0 - PEN_GRAIN * np.clip(0.5 + 0.5 * n, 0.0, 1.6)            # darkens only: no wax pixel is brighter than the pigment
    if streaks is not None:
        v = v * (1.0 - PEN_DRAG * streaks)
    out = np.zeros((hh, ww, 4), np.float32)
    out[..., :3] = np.array(INKC, np.float32)
    out[..., 3] = ink_m * 255.0
    wc = np.array(col, np.float32)[None, None, :] * v[..., None]
    a = wax_m[..., None]
    out[..., :3] = out[..., :3] * (1 - a) + wc * a
    out[..., 3] = np.maximum(out[..., 3], wax_m * 255.0)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')


def _stamp(im, P, r, butt):
    """the stroke of radius r along P (2x px) as a union of discs (PIL's wide polyline leaves scanline gaps between short segments)"""
    d = ImageDraw.Draw(im)
    q = r - 0.5
    step = max(0.5, q / 3.0)
    Q = [P[0]]
    for i in range(1, len(P)):
        (xa, ya), (xb, yb) = P[i - 1], P[i]
        n = max(1, int(math.ceil(math.hypot(xb - xa, yb - ya) / step)))
        Q += [(xa + (xb - xa) * j / n, ya + (yb - ya) * j / n) for j in range(1, n + 1)]
    for x, y in Q:
        d.ellipse([x - q, y - q, x + q, y + q], fill=255)
    if butt and len(P) > 1:
        for (ex, ey), (px_, py_) in ((P[0], P[1]), (P[-1], P[-2])):
            tx, ty = ex - px_, ey - py_
            tl = math.hypot(tx, ty) or 1.0
            tx, ty = tx / tl, ty / tl
            nx, ny = -ty, tx
            R = r + 4
            d.polygon([(ex + nx * R, ey + ny * R), (ex + nx * R + tx * R, ey + ny * R + ty * R), (ex - nx * R + tx * R, ey - ny * R + ty * R),
                       (ex - nx * R, ey - ny * R)], fill=0)


def wax_stroke(L, pts, w=PEN_W, ink=PEN_INK, col=PLAN, seed=1, cap=True, closed=False, cls='L6', streak=True):
    """N family grease pencil (L6): a w px wax stroke with an ink edge of `ink` px each side, wax grain and drag streaks, round caps, no glow"""
    if len(pts) < 2:
        return
    pts = HL.resample(HL.smooth(list(pts), 1), 1.5)
    if closed:
        pts = pts + [pts[0]]
    k = L.k
    pad = w / 2 + ink + 4
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, y0 = int(math.floor(min(xs) - pad)), int(math.floor(min(ys) - pad))
    x1, y1 = int(math.ceil(max(xs) + pad)), int(math.ceil(max(ys) + pad))
    ww, hh = (x1 - x0) * k, (y1 - y0) * k
    P = [((x - x0) * k, (y - y0) * k) for x, y in pts]
    mi = Image.new('L', (ww, hh), 0)
    mw = Image.new('L', (ww, hh), 0)
    butt = not cap and not closed
    _stamp(mi, P, (w / 2 + ink) * k, butt)
    _stamp(mw, P, (w / 2) * k, butt)
    rng = np.random.default_rng(seed + 7)
    wm = np.asarray(mw).astype(np.float32) / 255.0
    if PEN_EDGE_JIT > 0:
        jn = ndi.gaussian_filter(rng.standard_normal(wm.shape), 1.6 * k)
        jn = jn / (jn.std() + 1e-6)
        sm = ndi.gaussian_filter(wm, 0.5 * k)
        wm = np.clip((sm - 0.5 + 0.18 * PEN_EDGE_JIT * jn) * 4.0 + 0.5, 0, 1) * (wm > 0)
    im_ = np.asarray(mi).astype(np.float32) / 255.0
    streaks = None
    if streak and w >= 3.0:
        S = Image.new('L', (ww, hh), 0)
        ds = ImageDraw.Draw(S)
        nrm = HL.normals(pts)
        for j in range(PEN_DRAG_N):
            off = (rng.random() - 0.5) * (w - 2.0)
            n_ = len(pts)
            a_ = int(rng.random() * n_ * 0.35)
            b_ = n_ - int(rng.random() * n_ * 0.35)
            q = [((pts[i][0] + nrm[i][0] * off - x0) * k, (pts[i][1] + nrm[i][1] * off - y0) * k) for i in range(a_, max(a_ + 2, b_))]
            if len(q) > 1:
                ds.line(q, fill=255, width=max(1, int(round(PEN_DRAG_W * k))), joint='curve')
        streaks = ndi.gaussian_filter(np.asarray(S).astype(np.float32) / 255.0, 0.35 * k)
    lay = _wax_layer((hh, ww), wm, im_, col, seed, k, streaks)
    L.im.alpha_composite(lay, (x0 * k, y0 * k))
    _flag(L, mi, x0, y0, k)
    c1 = np.asarray(Image.fromarray((wm * 255).astype(np.uint8)).resize((x1 - x0, y1 - y0), Image.BOX)).astype(np.float32) / 255.0
    ci1 = np.asarray(mi.resize((x1 - x0, y1 - y0), Image.BOX)).astype(np.float32) / 255.0
    _add(cls + '_wax', c1 >= 0.5, c1, x0, y0)
    _add(cls + '_all', ci1 >= 0.5, ci1, x0, y0)
    ln = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:]))
    STROKES.append(dict(cls=cls, col='#%02X%02X%02X' % tuple(int(c) for c in col[:3]), length=round(ln, 1), w=w, ink=ink, cap=cap, closed=closed))


def seed_of(*a):
    return int(hashlib.md5(repr(a).encode()).hexdigest()[:8], 16)


# ------------------------------------------------------------------------------------------------ the board's pencil callers, one spec
def wax(L, pts, col=PLAN, w=PEN_W, seed=1, wobble=0.8, ink=True, grain=1.0, taper=False):
    """a_kit.wax signature: every board L6 stroke is 7 px wax + 3 px ink (the caller's widths are retired, VISUAL_PLAN A.5)"""
    wax_stroke(L, list(pts), PEN_W, PEN_INK, tuple(col[:3]), seed, cap=True, cls=_cls(col))


def _cls(col):
    return 'L6' if tuple(col[:3]) == tuple(PLAN) else 'L6t'      # L6t: the trigger path's threat pencil (its own colour, the same spec)


def wax_x(L, x, y, r=X_ARM, col=PLAN, seed=3, w=PEN_W, circle=False):
    """the X cap on a pencil target: two crossing L6 strokes at the spec width (a_kit.wax_x signature; r is kept, w is retired)"""
    import random
    rng = random.Random(seed)
    j = lambda: rng.uniform(-1.0, 1.0)
    r = max(r, X_ARM)
    wax(L, [(x - r + j(), y - r * 0.92 + j()), (x + r * 1.04 + j(), y + r * 1.02 + j())], col, PEN_W, seed)
    wax(L, [(x + r * 0.96 + j(), y - r * 1.0 + j()), (x - r * 1.04 + j(), y + r * 0.96 + j())], col, PEN_W, seed + 1)
    if circle:
        pts = [(x + (r + 11) * math.cos(math.radians(a)), y + (r + 11) * math.sin(math.radians(a))) for a in range(-40, 345, 10)]
        wax(L, pts, col, PEN_W, seed + 2)


def wax_v(L, tip, ang, size=V_ARM, col=PLAN, seed=5, w=PEN_W):
    """open arrowhead: two L6 strokes back from the tip (a_plan.wax_v signature; ang in radians = direction of travel)"""
    for sgn in (1, -1):
        a = ang + math.pi + sgn * 0.52
        p = (tip[0] + size * math.cos(a), tip[1] + size * math.sin(a))
        wax(L, [p, tip], col, PEN_W, seed + int(sgn))


def hud_wax(L, pts, col, w=PEN_W, seed=3, ink=True, wob=0.9):
    """hud2.wax signature (the bill's plan underline)"""
    wax(L, pts, col, PEN_W, seed)
