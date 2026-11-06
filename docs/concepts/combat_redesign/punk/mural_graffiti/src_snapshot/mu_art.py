"""mu_art: MURAL GRAFFITI tower.  The Cell painted its wheel as a mural on a wall: a brick (A) or concrete (B) roundel with sprayed wedges,
soft airbrushed warm/cool light, wildstyle outlines (ink + white keyline + cast shadow), paint drips, overspray, brick showing through the paint.
install(module) overrides the F1 black-book draw functions in f1_tower.  No needle, no tape, no ballpoint."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from scipy import ndimage as ndi
from f1_lib import *

VAR = ['A']
_WC = {}
ORANGE = (255, 150, 52)
YELLOW = (255, 214, 72)
CYAN_S = (70, 214, 250)
TEAL = (24, 190, 176)
VIOL = (122, 70, 214)
DEEPV = (58, 22, 112)
NAVY_I = (14, 12, 34)

STOPS = {
    'A': [(0.0, (255, 150, 84)), (0.22, (255, 88, 142)), (0.44, (255, 61, 168)), (0.80, (206, 38, 166)), (1.0, (124, 30, 158))],
    'B': [(0.0, (255, 150, 84)), (0.26, (255, 80, 150)), (0.5, (255, 61, 168)), (0.82, (190, 50, 208)), (1.0, (124, 66, 226))],
}


def bigblur(m, sig):
    """large gaussian on a down-sampled copy (a sigma of tens of px is far too slow at SS)"""
    k = 4
    h, w = m.shape
    sm = m[:h // k * k, :w // k * k].reshape(h // k, k, w // k, k).mean((1, 3))
    sm = ndi.gaussian_filter(sm, sig / k)
    out = np.kron(sm, np.ones((k, k), np.float32))
    res = np.zeros_like(m)
    res[:out.shape[0], :out.shape[1]] = out
    return res


def v():
    return VAR[0]


def stops_rgb(t, stops):
    pos = [s[0] for s in stops]
    return np.stack([np.interp(t, pos, [s[1][c] for s in stops]) for c in range(3)], -1).astype(np.float32)


def spray_a(cv, m, grain=0.5, soft=0.9, seed=0):
    """soft airbrush edge + grain; m local float mask"""
    S = cv.S
    core = ndi.gaussian_filter(m, soft * S * 0.8)
    n = ndi.gaussian_filter(cv.r.standard_normal(m.shape).astype(np.float32), 0.55 * S)
    n = n / (n.std() + 1e-6)
    edge = core * (1 - core) * 4
    return np.clip(core + grain * 0.18 * n * (0.15 + edge), 0, 1)


def overspray(cv, m, col, reach=5.0, dens=0.5, alpha=0.7, clipout=None):
    """speckle dots falling off outside a mask; (full local array)"""
    S = cv.S
    od = np.clip(ndi.gaussian_filter(m, reach * S) * 2.6, 0, 1) * (1 - np.clip(m * 1.2, 0, 1))
    rr = cv.r.random(m.shape)
    dots = (rr < od * dens * 0.55 / (S * S) * 3.0).astype(np.float32)
    dots = np.clip(ndi.gaussian_filter(dots, 0.5 * S) * 5.0, 0, 1) * (0.45 + 0.55 * cv.r.random(m.shape))
    if clipout is not None:
        dots = dots * clipout
    return dots * alpha


def lightg(cv, x0, y0, shape, cx, cy, scale):
    """light-direction coordinate: +1 on the lit (top left) side, -1 on the shadow side, around (cx,cy) 1x"""
    S = cv.S
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    x = (xx + x0) / S
    y = (yy + y0) / S
    return ((x - cx) * -0.62 + (y - cy) * -0.78) / scale


# ------------------------------------------------------------------ the wall
def wall_tex(cv):
    key = (v(), cv.S, cv.W)
    if key in _WC:
        return _WC[key]
    S, H, W = cv.S, cv.H, cv.W
    r = np.random.default_rng(7 if v() == 'A' else 9)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    x, y = xx / S, yy / S
    if v() == 'A':
        bh, bw = 10.6, 23.5
        row = np.floor(y / bh).astype(int)
        off = (row % 2) * bw / 2
        colx = np.floor((x + off) / bw).astype(int)
        fx = (x + off) % bw
        fy = y % bh
        ids = r.random((row.max() + 3, colx.max() + 4)).astype(np.float32)
        rid = ids[row, colx]
        mort = ((fx < 1.5) | (fy < 1.4)).astype(np.float32)
        mort = ndi.gaussian_filter(mort, 0.45 * S)
        lo, hi = np.array([118, 40, 40], np.float32), np.array([186, 88, 60], np.float32)
        base = lo + (hi - lo) * rid[..., None]
        base += (smooth(H, W, 1.4 * S, r) * 7)[..., None] + (smooth(H, W, 7 * S, r) * 5)[..., None]
        bev = np.clip((fy - 1.4) / 1.4, 0, 1) * (1 - np.clip((fy - 1.4) / 1.4, 0, 1)) * 0
        top = ((fy > 1.4) & (fy < 3.0)).astype(np.float32) * 16
        left = ((fx > 1.5) & (fx < 3.0)).astype(np.float32) * 9
        bot = (fy > bh - 1.3).astype(np.float32) * -16
        base += (ndi.gaussian_filter(top + left + bot, 0.5 * S))[..., None]
        mc = np.array([100, 88, 84], np.float32) + (smooth(H, W, 1.2 * S, r) * 6)[..., None]
        tex = base * (1 - mort[..., None]) + mc * mort[..., None]
        seam = mort
    else:
        n1 = smooth(H, W, 50 * S, r)
        n2 = smooth(H, W, 6 * S, r)
        n3 = smooth(H, W, 1.2 * S, r)
        base = np.array([84, 92, 124], np.float32)
        tex = base[None, None, :] * (1 + 0.07 * n1 + 0.05 * n2 + 0.035 * n3)[..., None]
        px = 92.0
        fx = (x + 20) % px
        fy = (y + 14) % px
        seam = ((fx < 1.3) | (fy < 1.3)).astype(np.float32)
        seam = ndi.gaussian_filter(seam, 0.45 * S)
        lite = ((fx > 1.3) & (fx < 2.6) | (fy > 1.3) & (fy < 2.6)).astype(np.float32)
        lite = ndi.gaussian_filter(lite, 0.5 * S)
        tex = tex * (1 - seam[..., None] * 0.55) + lite[..., None] * 9
        hx_ = ((px / 2 - np.abs(fx - px / 2)) < 0)  # unused
        hole = np.hypot(((x + 20 + px / 2) % px) - px / 2, ((y + 14 + px / 2) % px) - px / 2)
        tex = tex * (1 - np.clip(1.8 - hole, 0, 1)[..., None] * 0.55)
        st = ndi.gaussian_filter(r.standard_normal((H, W)).astype(np.float32), (16 * S, 1.3 * S))
        st = st / (st.std() + 1e-6)
        tex = tex * (1 - np.clip(st - 0.6, 0, 1.5)[..., None] * 0.18)
    _WC[key] = (np.clip(tex, 0, 255), seam)
    return _WC[key]


def page_disc(cv):
    from f1_tower import CT, R_PAGE
    S = cv.S
    disc = cv.circle_mask(CT, R_PAGE)
    t, rim = torn_mask(cv, disc, rough=2.4, fringe=1.0)
    tex, seam = wall_tex(cv)
    H, W = cv.H, cv.W
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = ((xx / S - CT[0]) * -0.62 + (yy / S - CT[1]) * -0.78) / R_PAGE
    warm = np.clip(g, 0, 1)[..., None]
    cool = np.clip(-g, 0, 1)[..., None]
    if v() == 'A':
        pap = tex * (0.86 + 0.50 * warm - 0.04 * cool)
        pap = pap + warm * np.array([54, 26, 0], np.float32) * 0.9 + cool * np.array([6, 0, 34], np.float32)
        pap = pap * (1 - 0.05 * np.clip((np.hypot(xx / S - CT[0], yy / S - CT[1]) - 130) / 62, 0, 1))[..., None]
    else:
        pap = tex * (0.92 + 0.50 * warm - 0.04 * cool)
        pap = pap + warm * np.array([48, 20, 8], np.float32) + cool * np.array([0, 10, 46], np.float32)
        pap = pap * (1 - 0.06 * np.clip((np.hypot(xx / S - CT[0], yy / S - CT[1]) - 130) / 62, 0, 1))[..., None]
    # the wall casts onto the board: a hard block shadow and a soft one
    sh = np.roll(np.roll(t, int(4 * S), 0), int(5 * S), 1)
    cv.over(ndi.gaussian_filter(sh, 3.0 * S), (6, 4, 12), 0.62)
    cv.over(np.clip(sh - t, 0, 1), INK, 0.55)
    cv.over_rgb(t, np.clip(pap, 0, 255))
    # chipped plaster rim: a light line where the wall breaks off
    cv.over(np.clip(rim, 0, 1) * 0.5, (210, 196, 180) if v() == 'A' else (176, 188, 214), 1.0)
    # sun-faded old paint-overs: big buffed blocks of colour, and ghost tags
    r = cv.r
    blobs = [((CT[0] - 120, CT[1] - 128), 92, (255, 150, 60), 0.30), ((CT[0] + 128, CT[1] + 120), 100, (70, 70, 220), 0.30),
             ((CT[0] + 150, CT[1] - 90), 60, (24, 190, 176), 0.22), ((CT[0] - 130, CT[1] + 100), 64, (160, 60, 200), 0.20)]
    for (c_, rad, col, a_) in blobs:
        b = bigblur(cv.circle_mask(c_, rad), 26 * S) * t
        cv.over(np.clip(b * 2.4, 0, 1), col, a_)
    return t


def construction(cv):
    """no ballpoint guides in a mural: faint buffed ghost tags on the wall instead"""
    from f1_tower import CT
    cols = [(255, 200, 90), (80, 220, 240), (255, 120, 190)]
    for k in range(5):
        a = 40 + k * 72
        p0 = pol(CT, 176.0, a)
        p1 = pol(CT, 188.0, a + 14)
        marker(cv, [p0, ((p0[0] + p1[0]) / 2 + 3, (p0[1] + p1[1]) / 2 - 2), p1], cols[k % 3], w=3.4, alpha=0.10, wob=1.0, grain=0.2)


def tape_strips(cv):
    return


def doodles(cv):
    """spray doodles in the page-margin gaps: star, spark, cross, zig, in cyan / yellow / white with an ink edge"""
    from f1_tower import CT
    r_ = 184.0
    for fn in (lambda c, **k: doodle_star(cv, pol(CT, r_, 90), 6.4, c, 2.0, alpha=1.0),
               lambda c, **k: doodle_spark(cv, pol(CT, r_, 150), 7.0, c, 2.0, n=7, alpha=1.0),
               lambda c, **k: doodle_cross(cv, pol(CT, r_, 270), 4.6, c, 2.2, alpha=1.0),
               lambda c, **k: doodle_zig(cv, pol(CT, r_, 322), pol(CT, r_, 338), c, 2.0, n=4, amp=2.6, alpha=1.0)):
        pass
    cs = [CYAN_S, YELLOW, (255, 255, 255), CYAN_S]
    for (c_, fn) in zip(cs, range(4)):
        pass
    # ink edge pass then colour pass
    for pas, (w_, col_list) in enumerate(((3.8, [INK] * 4), (1.9, cs))):
        doodle_star(cv, pol(CT, r_, 90), 6.4, col_list[0], w_, alpha=1.0)
        doodle_spark(cv, pol(CT, r_, 150), 7.0, col_list[1], w_, n=7, alpha=1.0)
        doodle_cross(cv, pol(CT, r_, 270), 4.8, col_list[2], w_, alpha=1.0)
        doodle_zig(cv, pol(CT, r_, 322), pol(CT, r_, 338), col_list[3], w_, n=4, amp=2.6, alpha=1.0)


# ------------------------------------------------------------------ wedges
def draw_wedge(cv, w, cons=True):
    import f1_tower as T
    CT, R_IN, R_OUT = T.CT, T.R_IN, T.R_OUT
    S = cv.S
    r = cv.r
    s = w['sector']
    am = 60 * s
    reg = T.wedge_mask(cv, s, R_IN, R_OUT, 26.0, jit=0.9)
    solid = T.solidify(reg, S)
    y0, y1, x0, x1 = T.bbox(solid, 14 * S)
    sub = solid[y0:y1, x0:x1]
    A = v() == 'A'
    # cast shadow of the paint on the wall (soft violet) and the block drop
    sh = np.roll(np.roll(sub, int(5 * S), 0), int(4 * S), 1)
    cv.over(np.clip(ndi.gaussian_filter(sh, 3.2 * S) * 1.3, 0, 1), (20, 6, 40), 0.55, x0, y0)
    if A:
        T.block_drop(cv, solid, 3.0, 4.0, INK)
    else:
        T.block_drop(cv, solid, 5.0, 6.0, DEEPV)
    # wildstyle outline: ink outside, white keyline, then the paint
    ink = np.clip(ndi.gaussian_filter(outline_mask(sub, S, 5.4), 0.35 * S) * 1.5, 0, 1)
    cv.over(ink, INK, 0.99, x0, y0)
    key = np.clip(ndi.gaussian_filter(outline_mask(sub, S, 2.4), 0.3 * S) * 1.5, 0, 1)
    cv.over(key, (255, 252, 244), 0.98, x0, y0)
    halo = np.clip(ndi.gaussian_filter(sub, 5.0 * S) * 1.5, 0, 1)
    cv.over(halo, (255, 128, 150) if A else (150, 110, 255), 0.36, x0, y0)
    # overspray first (under the fill), pink speckle onto the wall around the wedge
    od = overspray(cv, sub, PINK, reach=6.0, dens=0.55, alpha=0.8)
    cv.over(od, PINK, 0.8, x0, y0)
    # the paint: gradient by warm/cool light (A) or by radius sunset (B)
    h, ww = sub.shape
    cxw, cyw = pol(CT, (R_IN + R_OUT) / 2, am)
    yy, xx = np.mgrid[0:h, 0:ww].astype(np.float32)
    px_, py_ = (xx + x0) / S, (yy + y0) / S
    if A:
        gl = ((px_ - cxw) * -0.62 + (py_ - cyw) * -0.78) / 62.0
        t = np.clip(0.50 - 0.34 * gl, 0, 1)
    else:
        rr = np.hypot(px_ - CT[0], py_ - CT[1])
        gl = ((px_ - cxw) * -0.62 + (py_ - cyw) * -0.78) / 62.0
        t = np.clip((rr - R_IN) / (R_OUT - R_IN) * 0.62 + 0.22 - 0.10 * gl, 0, 1)
    rgb = stops_rgb(t, STOPS[v()])
    a = spray_a(cv, sub, grain=0.45, soft=0.8)
    cv.over_rgb(a, rgb, x0, y0)
    inner = ndi.binary_erosion(sub > 0.5, iterations=int(2.5 * S)).astype(np.float32)
    if A:
        # airbrushed warm glow near the lit edge, cool shade on the shadow side (soft, painterly light)
        hl = np.clip(inner - np.roll(np.roll(inner, int(10 * S), 0), int(8 * S), 1), 0, 1)
        cv.over(np.clip(ndi.gaussian_filter(hl, 4.0 * S) * 1.9, 0, 1) * inner, YELLOW, 0.40, x0, y0)
        cv.over(np.clip(ndi.gaussian_filter(np.clip(inner - np.roll(np.roll(inner, int(-12 * S), 0), int(-10 * S), 1), 0, 1), 4.5 * S) * 1.9, 0, 1) * inner,
                (74, 28, 160), 0.42, x0, y0)
    else:
        # cel-painted light: a hard-edged violet shadow plate, a cyan rim on the shadow edge, a hard warm sliver on the lit edge (comic print, no blur)
        sm = ndi.gaussian_filter(inner, 0.5 * S)
        shd = np.clip(sm - np.roll(np.roll(sm, int(-13 * S), 0), int(-10 * S), 1), 0, 1)
        shd = np.clip((shd - 0.4) * 8, 0, 1) * inner
        cv.over(shd, (96, 34, 176), 0.70, x0, y0)
        rim = np.clip(sm - np.roll(np.roll(sm, int(-3.0 * S), 0), int(-2.4 * S), 1), 0, 1)
        rim = np.clip((rim - 0.4) * 8, 0, 1) * inner
        cv.over(rim, (80, 226, 255), 0.95, x0, y0)
        lit = np.clip(sm - np.roll(np.roll(sm, int(7 * S), 0), int(6 * S), 1), 0, 1)
        lit = np.clip((lit - 0.4) * 8, 0, 1) * inner
        cv.over(lit, (255, 205, 110), 0.85, x0, y0)
    # broad brush strokes in the wet paint (lighter and darker pink), along the radius
    for q in range(4):
        aa = am + r.uniform(-18, 18)
        p0 = pol(CT, R_IN + 8 + r.uniform(0, 14), aa)
        p1 = pol(CT, R_OUT - 10 - r.uniform(0, 20), aa + r.uniform(-4, 4))
        col = (255, 148, 214) if q % 2 == 0 else (190, 22, 120)
        m_, mx0, my0 = stroke_mask(cv, [p0, p1], 6.0 + r.uniform(0, 3), 'chisel', 30, 0.7, 40, (0.2, 0.4))
        m_ = ndi.gaussian_filter(m_, 0.6 * S) * 0.0 + m_
        # clip to the wedge interior
        yy0, xx0 = max(0, my0), max(0, mx0)
        sm = np.zeros_like(solid)
        sm[yy0:yy0 + 0, xx0:xx0 + 0] = 0
        loc = np.zeros((cv.H, cv.W), np.float32)
        hh, wd = m_.shape
        ya, xa = max(0, my0), max(0, mx0)
        yb, xb = min(cv.H, my0 + hh), min(cv.W, mx0 + wd)
        if yb > ya and xb > xa:
            loc[ya:yb, xa:xb] = m_[ya - my0:yb - my0, xa - mx0:xb - mx0]
            clipm = np.zeros((cv.H, cv.W), np.float32)
            clipm[y0:y1, x0:x1] = inner
            cv.over(loc * clipm, col, 0.20 + 0.06 * (q % 2))
    # specular streak: a thin white-pink sheen on the lit edge
    p0 = pol(CT, R_IN + 14, am - 21.5)
    p1 = pol(CT, R_OUT - 20, am - 20.0)
    marker(cv, [p0, p1], (255, 235, 245), w=2.2, alpha=0.5, wob=0.5, taper=(0.15, 0.5), grain=0.2)
    # the brick / panel seams show through the paint
    tex, seam = wall_tex(cv)
    cv.mult(seam[y0:y1, x0:x1] * inner * 0.0 + seam[y0:y1, x0:x1] * sub, (120, 80, 120), 0.20, x0, y0)
    # drips off the outer edge on the wedges that face down
    drips(cv, am, r)
    return solid


def drips(cv, am, r):
    import f1_tower as T
    CT, R_OUT = T.CT, T.R_OUT
    cand = [a for a in np.arange(am - 22, am + 23, 4.0) if 108 <= (a % 360) <= 252]
    if not cand:
        return
    n = 2 if len(cand) > 3 else 1
    picks = list(r.choice(cand, size=min(n, len(cand)), replace=False))
    for a in picks:
        x, y = pol(CT, R_OUT - 1.0, a)
        ln = r.uniform(10, 19)
        pts = [(x, y - 1), (x + r.uniform(-0.4, 0.4), y + ln * 0.5), (x + r.uniform(-0.5, 0.5), y + ln)]
        marker(cv, pts, INK, w=7.4, alpha=1.0, wob=0.2, taper=(0.0, 0.0), grain=0.0, rough=0.1)
        cv.over(cv.circle_mask((pts[-1][0], pts[-1][1] + 0.8), 4.2), INK, 1.0)
        marker(cv, pts, (255, 61, 168), w=5.0, alpha=1.0, wob=0.1, taper=(0.0, 0.0), grain=0.05, rough=0.1)
        cv.over(cv.circle_mask((pts[-1][0], pts[-1][1] + 0.8), 3.0), (255, 61, 168), 1.0)
        marker(cv, [(pts[0][0] - 1.1, pts[0][1] + 2), (pts[-1][0] - 1.1, pts[-1][1] - 1)], (255, 214, 236), w=1.1, alpha=0.9, wob=0.05, taper=(0.1, 0.3), grain=0.0, rough=0.0)


def draw_icon(cv, w, solid):
    """E10 silhouettes as a white stencil: ink outline, offset paint drop (orange A / cyan B), spray-white fill with a warm lower shade"""
    import f1_tower as T
    import f1_icons as FI
    CT = T.CT
    S = cv.S
    t = w['t']
    am = 60 * w['sector']
    c = pol(CT, T.ICON_R, am)
    white, dark = FI.mask_for(t, T.ICON_PX, S)
    n = white.shape[0]
    x0, y0 = int(c[0] * S - n / 2), int(c[1] * S - n / 2)
    wm = T.solidify(white, S)
    full = np.clip(wm + dark, 0, 1)
    A = v() == 'A'
    dropc = (255, 150, 40) if A else (60, 200, 245)
    ex = np.zeros_like(full)
    for k in range(1, int(3.4 * S) + 1):
        ex = np.maximum(ex, np.roll(np.roll(full, k, 0), k, 1))
    ex = np.clip(ex - full, 0, 1)
    ring = np.clip(ndi.gaussian_filter(outline_mask(np.clip(full + ex, 0, 1), S, 2.2), 0.3 * S) * 1.6, 0, 1)
    cv.over(ring, INK, 0.99, x0, y0)
    cv.over(ex, dropc, 1.0, x0, y0)
    if dark.max() > 0:
        cv.over(np.clip(dark, 0, 1), INK, 0.98, x0, y0)
        hatch_region(cv, np.clip(dark, 0, 1), x0, y0, (255, 252, 244), ang=45, pitch=3.0, w=0.8, alpha=0.5, over=0.0, jit=0.1)
    yy = np.mgrid[0:n, 0:n][0].astype(np.float32) / n
    wcol = np.stack([np.full((n, n), 255.0), 255 - 26 * yy ** 2, 255 - 90 * yy ** 2], -1)
    cv.over_rgb(np.clip(wm, 0, 1) * 0.99, wcol, x0, y0)
    return x0, y0, full


def draw_brace_plate(cv, s):
    """L10 double line: a chrome plate bolted over the wall along the slice rim: two ink lines, jaw ticks, rivets"""
    import f1_tower as T
    CT = T.CT
    S = cv.S
    am = 60 * s
    a0, a1 = am - 26.5, am + 26.5
    strip = cv.band_mask(CT, 177.0, 191.0, a0, a1, step=0.6)
    strip = warp(strip, 0.5 * S, 8 * S, cv.r)
    solid = T.solidify(strip, S)
    T.block_drop(cv, solid, 2.0, 3.0)
    T.tapered_outline(cv, solid, 1.8, 3.2)
    yy, xx = np.mgrid[0:cv.H, 0:cv.W].astype(np.float32)
    g = ((xx / S - CT[0]) * -0.62 + (yy / S - CT[1]) * -0.78) / 190.0
    ch = stops_rgb(np.clip(0.5 - g * 0.6, 0, 1), [(0, (240, 246, 255)), (0.5, (190, 202, 224)), (1, (118, 132, 164))])
    cv.over_rgb(solid, ch)
    for rr in (181.4, 186.6):
        pts = arc_pts(CT, rr, a0 + 3.0, a1 - 3.0, 0.8)
        marker(cv, pts, INK, w=2.6, alpha=0.98, wob=0.3, wl=40, taper=(0.04, 0.04), grain=0.05)
    for sg in (-1, 1):
        p0 = pol(CT, 176.0, am + sg * 24.0)
        p1 = pol(CT, 192.0, am + sg * 24.0)
        marker(cv, [p0, p1], INK, w=3.2, alpha=1.0, wob=0.15, taper=(0, 0), grain=0.05)
        x, y = pol(CT, 184.0, am + sg * 20.5)
        cv.over(cv.circle_mask((x, y), 2.4), INK, 1.0)
        cv.over(cv.circle_mask((x, y), 1.3), (240, 246, 255), 1.0)


# ------------------------------------------------------------------ hub
def draw_hub(cv, name='BREAKER'):
    import f1_tower as T
    CT, R_HUB, CELL_PINK = T.CT, T.R_HUB, T.CELL_PINK
    S = cv.S
    c = CT
    A = v() == 'A'
    pts = []
    nb = 12
    for i in range(nb * 14 + 1):
        a = i / (nb * 14) * 360
        bump = 1 + 0.06 * abs(math.sin(math.radians(a * nb / 2)))
        pts.append(pol(c, (R_HUB - 2.4) * bump, a))
    reg = cv.poly_mask(pts)
    reg = warp(reg, 0.5 * S, 9 * S, cv.r)
    solid = T.solidify(reg, S)
    cv.over(np.clip(ndi.gaussian_filter(np.roll(np.roll(solid, 5 * S, 0), 4 * S, 1), 3 * S) * 1.3, 0, 1), (20, 6, 40), 0.5)
    T.block_drop(cv, solid, 3.0, 4.0, INK if A else DEEPV)
    cv.over(np.clip(ndi.gaussian_filter(outline_mask(solid, S, 5.0), 0.35 * S) * 1.5, 0, 1), INK, 0.99)
    cv.over(np.clip(ndi.gaussian_filter(outline_mask(solid, S, 2.2), 0.3 * S) * 1.5, 0, 1), (255, 252, 244), 0.98)
    yy, xx = np.mgrid[0:cv.H, 0:cv.W].astype(np.float32)
    px_, py_ = xx / S, yy / S
    rr = np.hypot(px_ - c[0], py_ - c[1]) / R_HUB
    gl = ((px_ - c[0]) * -0.62 + (py_ - c[1]) * -0.78) / R_HUB
    if A:
        # a painted sun: pale yellow core to orange to magenta at the rim
        rgb = stops_rgb(np.clip(rr * 0.9 - gl * 0.28, 0, 1), [(0, (255, 244, 150)), (0.35, (255, 196, 70)), (0.7, (255, 120, 64)), (1.0, (232, 50, 130))])
    else:
        rgb = stops_rgb(np.clip(rr * 0.9 - gl * 0.28, 0, 1), [(0, (214, 252, 255)), (0.35, (92, 225, 255)), (0.7, (50, 150, 240)), (1.0, (110, 64, 214))])
    a = spray_a(cv, solid, grain=0.4, soft=0.8)
    cv.over_rgb(a, rgb)
    # rays of the sun, sprayed fat-cap lines just inside the rim
    for k in range(16):
        ang = k * 22.5 + 6
        p0, p1 = pol(c, R_HUB - 12, ang), pol(c, R_HUB - 5.5, ang)
        marker(cv, [p0, p1], (255, 252, 244) if A else (255, 255, 255), w=1.8, alpha=0.55, wob=0.2, taper=(0.1, 0.3), grain=0.1)
    inner = ndi.binary_erosion(solid > 0.5, iterations=int(3.0 * S)).astype(np.float32)
    hi = np.clip(inner - np.roll(np.roll(inner, int(5 * S), 0), int(5 * S), 1), 0, 1)
    cv.over(ndi.gaussian_filter(hi, 0.8 * S), (255, 255, 255), 0.85)
    # tag emblem: the Breaker's bolt above the name
    ex, ey = c[0], c[1] - 14.5
    bolt = [(ex + 2.5, ey - 9), (ex - 5.0, ey + 1.0), (ex - 0.5, ey + 1.0), (ex - 3.0, ey + 9.5), (ex + 5.5, ey - 2.0), (ex + 0.5, ey - 2.0)]
    bm = cv.poly_mask(bolt)
    cv.over(np.clip(ndi.gaussian_filter(outline_mask(bm, S, 1.6), 0.4) * 1.5, 0, 1), INK, 0.99)
    cv.over(np.roll(np.roll(bm, int(0.5 * S), 0), int(0.5 * S), 1), (255, 61, 168), 1.0)
    if name:
        letters(cv, name, (c[0], c[1] + 10.5), 15.5, fnt=MARKER_F, fill=(255, 255, 255), ink=INK, extrude=1.8, ext_col=(214, 28, 134) if A else DEEPV, ink_w=2.0, outline=True, miss=(0.3, 0.3), wob=0.2, spacing=0.3, hatch_ext=False)


def draw_hp_ring_band(cv, g, rc, w, a0, a1):
    pts = arc_pts(__import__('f1_tower').CT, rc, a0, a1, 1.0)
    marker(cv, pts, INK, w=w + 5.6, alpha=0.97, wob=0.3, wl=60, taper=(0.02, 0.02), grain=0.06)


def install(T):
    T.page_disc = page_disc
    T.construction = construction
    T.tape_strips = tape_strips
    T.doodles = doodles
    T.draw_wedge = draw_wedge
    T.draw_icon = draw_icon
    T.draw_brace_plate = draw_brace_plate
    T.draw_hub = draw_hub
