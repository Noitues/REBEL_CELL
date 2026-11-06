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


# ------------------------------------------------------------------------------------------------ L5 arrowed outline in pencil
# 2026-11-04 round 2, gate-1 fix (R1 gate: "p2b hover path grammar", "L5 edges read as dashes"): THE L5 drawer for the board (p2b hover path)
# and the hover set (hv_core.channel calls this).  Moved from round2/hover/src/hv_core.py (channel, wax_fill) with one change: the chevrons are
# drawn BEFORE the two edges, so the edges run continuous over the chevron tips (the chevrons' ink keyline used to cut each edge at a 24 px
# pitch, which read as a dashed edge at 1x, against DR-1).  Order: the floor, the edges with their ink keyline, the chevrons (with theirs), then
# the edges' wax again on top (same seed, no ink), so a chevron's keyline can touch an edge but never cut it; the chevron arm stays inside the
# edge wax (CHEV_ARM, capped at the half channel minus the edge wax and the chevron wax)
L5_EDGE, L5_INK = 3.0, 2.25           # B L5: two 3 px edges; L1 keyline 4.5 px (2.25 each side)
L5_CHEV_W, L5_CHEV_INK = 3.4, 1.5     # chevron stroke (10 px chevrons at a 24 px pitch)
L5_PITCH = 24.0
CHEV_ARM = 4.2                        # chevron half height (its arm's reach off the centre line)
L5_FILL = (10, 8, 20, 200)            # the channel floor


def wax_fill(L, poly, col=PLAN, seed=1, ink=L5_INK, cls='L5h'):
    """a filled wax shape (the L5 arrowhead) with the grain (the wax layer) and an ink keyline"""
    k = L.k
    pad = ink + 4
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    x0, y0 = int(math.floor(min(xs) - pad)), int(math.floor(min(ys) - pad))
    x1, y1 = int(math.ceil(max(xs) + pad)), int(math.ceil(max(ys) + pad))
    ww, hh = (x1 - x0) * k, (y1 - y0) * k
    P = [((x - x0) * k, (y - y0) * k) for x, y in poly]
    mw = Image.new('L', (ww, hh), 0)
    ImageDraw.Draw(mw).polygon(P, fill=255)
    mi = Image.new('L', (ww, hh), 0)
    di = ImageDraw.Draw(mi)
    di.polygon(P, fill=255)
    di.line(P + [P[0]], fill=255, width=max(1, int(round(2 * ink * k))), joint='curve')
    wm = np.asarray(mw).astype(np.float32) / 255.0
    lay = _wax_layer((hh, ww), wm, np.asarray(mi).astype(np.float32) / 255.0, col, seed, k, None)
    L.im.alpha_composite(lay, (x0 * k, y0 * k))
    _flag(L, mi, x0, y0, k)
    cw = np.asarray(mw.resize((x1 - x0, y1 - y0), Image.BOX)).astype(np.float32) / 255.0
    ci = np.asarray(mi.resize((x1 - x0, y1 - y0), Image.BOX)).astype(np.float32) / 255.0
    _add(cls + '_wax', cw >= 0.5, cw, x0, y0)
    _add(cls + '_all', ci >= 0.5, ci, x0, y0)


def channel(L, pts, col=PLAN, w=16.0, head=22.0, fill=L5_FILL, chev=True, tail_dot=False, seed=1, edge=L5_EDGE, chev_col=None):
    """L5 arrowed outline in the pencil material: a w px channel (dark floor), 10 px chevrons at a 24 px pitch pointing the way of travel,
    then two edge px wax edges with an L1 ink keyline over them (continuous), and a filled wax arrowhead"""
    P0 = HL.resample(HL.smooth(pts, 2), 3.0)
    if len(P0) < 4:
        P0 = HL.resample(pts, 3.0)
    tip = P0[-1]
    t = HL.tangent_at_end(P0, 5)
    cut = head * 0.78
    body = list(P0)
    acc, i = 0.0, len(body) - 1
    while i > 0 and acc < cut:
        acc += math.hypot(body[i][0] - body[i - 1][0], body[i][1] - body[i - 1][1])
        i -= 1
    body = body[:i + 1]
    ns = HL.normals(body)
    hw = w / 2
    left = [(p[0] + n[0] * hw, p[1] + n[1] * hw) for p, n in zip(body, ns)]
    right = [(p[0] - n[0] * hw, p[1] - n[1] * hw) for p, n in zip(body, ns)]
    L.poly(left + right[::-1], fill=fill)
    rails = [(left, seed), (right, seed + 31), ([left[0], right[0]], seed + 77)]
    for e, sd in rails:
        wax_stroke(L, e, edge, L5_INK, col, sd, cap=True, cls='L5', streak=False)
    if chev:
        arm = min(CHEV_ARM, hw - edge / 2 - L5_CHEV_W / 2)
        acc = 12.0
        for j in range(1, len(body)):
            acc += math.hypot(body[j][0] - body[j - 1][0], body[j][1] - body[j - 1][1])
            if acc >= L5_PITCH:
                acc = 0.0
                p, n = body[j], ns[j]
                tx, ty = n[1], -n[0]
                a = (p[0] - tx * 5 + n[0] * arm, p[1] - ty * 5 + n[1] * arm)
                b = (p[0] + tx * 4, p[1] + ty * 4)
                c = (p[0] - tx * 5 - n[0] * arm, p[1] - ty * 5 - n[1] * arm)
                wax_stroke(L, [a, b, c], L5_CHEV_W, L5_CHEV_INK, chev_col or col, seed + j, cap=True, cls='L5c', streak=False)
        for e, sd in rails:
            wax_stroke(L, e, edge, 0.0, col, sd, cap=True, cls='L5', streak=False)      # the edge wax over the chevron keylines
    nx, ny = -t[1], t[0]
    base = (tip[0] - t[0] * head, tip[1] - t[1] * head)
    hw2 = w * 0.95
    hp = [(base[0] + nx * hw2, base[1] + ny * hw2), tip, (base[0] - nx * hw2, base[1] - ny * hw2)]
    wax_fill(L, hp, col, seed + 5, cls='L5h')
    inner = [(base[0] + nx * hw2 * 0.46 + t[0] * 4, base[1] + ny * hw2 * 0.46 + t[1] * 4), (tip[0] - t[0] * 7, tip[1] - t[1] * 7),
             (base[0] - nx * hw2 * 0.46 + t[0] * 4, base[1] - ny * hw2 * 0.46 + t[1] * 4)]
    L.poly(inner, fill=(10, 8, 20, 230))
    if tail_dot:
        p = P0[0]
        L.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], fill=INKC)
        L.ellipse([p[0] - 3.6, p[1] - 3.6, p[0] + 3.6, p[1] + 3.6], fill=col)
