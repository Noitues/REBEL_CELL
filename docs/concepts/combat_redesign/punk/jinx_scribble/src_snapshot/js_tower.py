"""js_tower: the JINX SCRIBBLE tower (player wheel).  The Cell's wall: a dark painterly disc, neon chalk / marker scribbles, doodled stars and X marks,
spray mist, Spider-Verse glitch misregistration (cyan and pink plates shifted off the key).  Same geometry and game information as f1_tower
(tower r196, six slices r71-177, icons r120, slice pips r167, HP ring r52-64 around the hub, trim r200-210), so every grammar element carries over.
Two variants (set js_tower.VAR[0]):  A = dark wedges drawn in neon line,  B = hot-pink painted wedges with a cyan misregistered plate.
Everything else (HP blocks, pips, break state, trim, hover arcs) is f1_tower's, reused unchanged: the grammar is the plan's, not this style's."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from scipy import ndimage as ndi
from f1_lib import *
import f1_tower as FT
import f1_icons as FI
import js_doodle as D
from f1_tower import CT, R_PAGE, R_HUB, R_IN, R_OUT, ICON_R, ICON_PX, solidify, wedge_mask, bbox

VAR = ['A']

NP = (255, 46, 154)         # neon pink (ours)
NP_L = (255, 140, 205)
NP_D = (150, 14, 92)
NC = (46, 235, 255)         # neon cyan (chalk)
NC_L = (200, 252, 255)
CHALKC = (246, 242, 255)
INKB = (10, 7, 22)
PAL = [(27, 58, 120), (90, 26, 110), (60, 42, 148), (14, 90, 122), (122, 26, 96), (36, 21, 82), (20, 14, 56)]


def placed(cv, m, x0, y0):
    out = np.zeros((cv.H, cv.W), np.float32)
    c = cv._clip(m, x0, y0)
    if c is not None:
        mm, xa, ya, xb, yb = c
        out[ya:yb, xa:xb] = mm
    return out


def neon(cv, pts, col, w=3.0, alpha=0.95, glow=0.0, wob=0.5, taper=(0.1, 0.2), clip=None, wl=34, grain=0.3, shift=(0, 0)):
    """a chalk / paint-pen stroke: ragged edge, speckled grain, optional neon glow"""
    S = cv.S
    if shift != (0, 0):
        pts = [(p[0] + shift[0], p[1] + shift[1]) for p in pts]
    m, x0, y0 = stroke_mask(cv, pts, w, 'round', 0, wob, wl, taper)
    m = finish_mask(cv, m, grain=grain, rough=0.35, pool=0.1)
    n = smooth(*m.shape, 0.9 * S / 4 * 1.6, cv.r)
    m = np.clip(m * (0.86 + 0.34 * n), 0, 1)
    full = placed(cv, m, x0, y0)
    if clip is not None:
        full = full * clip
    if glow > 0:
        g = ndi.gaussian_filter(full, 2.0 * S)
        cv.over(np.clip(g * 2.0, 0, 1), col, glow)
    cv.over(full, col, alpha)
    return full


def neon_lines(cv, lines, col, w=2.4, alpha=0.95, glow=0.3, wob=0.3, clip=None, shift=(0, 0), taper=(0.1, 0.2)):
    for ln in lines:
        if len(ln) >= 2:
            neon(cv, ln, col, w, alpha, glow, wob, taper, clip, wl=14, shift=shift)


def splat(cv, c, r, col, alpha, n=30, clip=None):
    S = cv.S
    rr = cv.r
    m = np.zeros((cv.H, cv.W), np.float32)
    for _ in range(n):
        a = rr.uniform(0, 6.283)
        d = abs(rr.normal(0, r))
        p = (c[0] + d * math.cos(a), c[1] + d * math.sin(a))
        rad = rr.uniform(0.5, 1.6) * (1.2 - min(1, d / (3 * r)))
        m = np.maximum(m, cv.circle_mask(p, rad))
    if clip is not None:
        m = m * clip
    cv.over(m, col, alpha)


# ------------------------------------------------------------------ the page: a dark painted wall disc
def page_disc(cv):
    S = cv.S
    r = cv.r
    disc = cv.circle_mask(CT, R_PAGE)
    disc = warp(disc, 1.1 * S, 18 * S, r)
    t = np.clip((ndi.gaussian_filter(disc, 0.6 * S) - 0.5) * 5 + 0.5, 0, 1)
    yy, xx = np.mgrid[0:cv.H, 0:cv.W].astype(np.float32)
    rr = np.hypot(xx / S - CT[0], yy / S - CT[1])
    k = np.clip(rr / R_PAGE, 0, 1)[..., None]
    c0 = np.array((38, 22, 88), np.float32)
    c1 = np.array((14, 8, 38), np.float32)
    base = c0 * (1 - k) + c1 * k
    n = smooth(cv.H, cv.W, 30 * S / 4, r)[..., None]
    base = base * (1 + 0.14 * n)
    cv.over(ndi.gaussian_filter(np.roll(np.roll(t, int(4 * S), 0), int(5 * S), 1), 3.0 * S), (4, 3, 10), 0.7)
    cv.over(np.clip(ndi.gaussian_filter(t, 2.4 * S) * 0 + 0, 0, 1), INKB, 0.0)
    cv.over_rgb(t, base)
    # painterly: wide dry-brush strokes in nearby dark tones, sweeping round the hub and across
    for i in range(110):
        a = r.uniform(0, 360)
        rad = r.uniform(30, 190)
        c = pol(CT, rad, a)
        if r.random() < 0.55:       # tangential sweep
            a2 = a + r.choice([-1, 1]) * r.uniform(8, 26) * 100 / max(60, rad)
            pts = [c, pol(CT, rad + r.uniform(-6, 6), (a + a2) / 2), pol(CT, rad + r.uniform(-8, 8), a2)]
        else:
            ang = math.radians(r.choice([-55, -38, 32, 48, -70]) + r.uniform(-10, 10))
            L = r.uniform(26, 80)
            pts = [c, (c[0] + L * 0.5 * math.cos(ang) + r.uniform(-5, 5), c[1] + L * 0.5 * math.sin(ang)), (c[0] + L * math.cos(ang), c[1] + L * math.sin(ang))]
        w = r.uniform(7, 24)
        m, x0, y0 = stroke_mask(cv, pts, w, 'round', 0, 1.0, 40, (0.25, 0.4))
        nz = smooth(*m.shape, 1.1 * S / 4 * 1.6, r)
        m = np.clip(m * np.clip(nz * 0.9 + 0.35, 0, 1) * 1.4, 0, 1)
        cc = PAL[int(r.integers(0, len(PAL)))]
        cv.over(placed(cv, m, x0, y0) * t, cc, r.uniform(0.3, 0.6))
    # spray mist at the rim: pink low left, cyan top right (the wall around the Cell's tag)
    for (a, col, al) in ((205, NP, 0.42), (140, NP, 0.25), (320, NC, 0.30), (30, NC, 0.22), (262, NP, 0.2)):
        c = pol(CT, 170, a)
        mist = ndi.gaussian_filter(cv.circle_mask(c, 34), 15 * S)
        cv.over(np.clip(mist * 3.2, 0, 1) * t, col, al)
        splat(cv, c, 18, col, 0.8, n=60, clip=t)
    # paint grain and a few drips from the rim
    g = smooth(cv.H, cv.W, 1.0 * S / 4, r)
    cv.over(np.clip(g * 0.14, 0, 1) * t, CHALKC, 0.5)
    cv.over(np.clip(-g * 0.18, 0, 1) * t, INKB, 0.5)
    # the page rim: a ragged neon chalk circle, cyan plate shifted off the pink key
    for sh, col, w_, gl in (((2.2, -1.6), NC, 2.6, 0.5), ((0, 0), NP, 3.0, 0.7)):
        for k in range(2):
            a0 = r.uniform(0, 360)
            pts = [pol(CT, R_PAGE - 3.0 + 0.5 * math.sin(math.radians(a * 3 + k)), a0 + a) for a in np.linspace(0, 372, 120)]
            neon(cv, pts, col, w_, 0.95, gl, wob=0.7, taper=(0.04, 0.06), wl=50, shift=sh)
    return t


def construction(cv):
    """faint cyan chalk construction: the circles and spokes the Cell scratched in first (about 25 percent)"""
    col = NC
    for r_, a_, w_ in ((R_HUB + 3, 0.30, 1.1), (R_IN - 3.0, 0.28, 1.1), (R_OUT + 3.4, 0.30, 1.1), (150.0, 0.14, 1.0)):
        s0 = cv.r.uniform(0, 360)
        pts = [pol(CT, r_ * (1 + 0.004 * math.sin(math.radians(a * 2))), s0 + a) for a in np.linspace(0, 380, 100)]
        neon(cv, pts, col, w_, a_, 0.0, wob=0.5, taper=(0.05, 0.1), wl=60, grain=0.5)
    for k in range(6):
        a = 60 * k + 30
        neon(cv, [pol(CT, 18, a), pol(CT, R_PAGE - 6, a)], col, 1.0, 0.2, 0.0, wob=0.4, grain=0.5)


def tape_strips(cv):
    return


# ------------------------------------------------------------------ doodles
def doodle_on(cv, lines, col, w=2.3, glow=0.3, shift=(0, 0), alpha=0.95):
    neon_lines(cv, lines, col, w + 0.5, alpha, glow, 0.25, shift=shift)


def _g(kind, c, r):
    r = r * 1.3
    x, y = c
    if kind == 'x':
        return D.xmark(x, y, r)
    if kind == 'star':
        return D.star5(x, y, r)
    if kind == 'star4':
        return D.star4(x, y, r)
    if kind == 'tally':
        return D.tally(x, y, 5, r * 2)
    if kind == 'bolt':
        return D.bolt(x, y, r * 2.4)
    if kind == 'spiral':
        return D.spiral(x, y, r, 2.0)
    if kind == 'face':
        return D.face(x, y, r)
    if kind == 'crown':
        return D.crown(x, y, r * 2.2, r * 1.4)
    if kind == 'arrow':
        return D.arrow((x - r, y + r * 0.5), (x + r, y - r * 0.5))
    return D.zig((x - r, y), (x + r, y), 4, r * 0.35)


MARG = ['star', 'x', 'tally', 'bolt', 'star4', 'spiral']


def doodles(cv):
    """margin of the page (between the slice rim and the page edge, in the gaps between slices) and the dead corners of each wedge: never over a pip, an HP block, an icon, a ring cell or a threat mark"""
    r_ = 184.6
    gaps = [30, 90, 150, 210, 270, 330]
    kinds = ['star', 'x', 'tally', 'bolt', 'star4', 'x']
    cols = [NC, NP, NC, NP, NC, NC] if VAR[0] == 'A' else [NC, NC, NC_L, NC, NC_L, NC]
    for g, k, c in zip(gaps, kinds, cols):
        pos = pol(CT, r_, g)
        doodle_on(cv, _g(k, pos, 4.8), c, 1.8, 0.4)
    # wedge corners (inner, hub side) : one doodle per slice, rotating
    inn = ['x', 'tally', 'star4', 'bolt', 'spiral', 'star']
    for s in range(6):
        am = 60 * s
        side = -1 if s % 2 == 0 else 1
        pos = pol(CT, 85.0, am + side * 14.0)
        c = (NC if VAR[0] == 'A' else INKB)
        doodle_on(cv, _g(inn[s], pos, 5.6), c, 2.0, 0.4 if VAR[0] == 'A' else 0.0)
        pos = pol(CT, 86.0, am - side * 15.0)
        doodle_on(cv, _g(inn[(s + 2) % 6], pos, 5.0), NP_L if VAR[0] == 'A' else NC_L, 1.9, 0.4 if VAR[0] == 'A' else 0.0)
    # a crude face, tiny, on the hub side of sector 3 and a crown on sector 1 (the Cell's mark)
    out = ['spiral', 'x', 'star4', 'x', 'tally', 'star4']
    for s in range(6):
        am = 60 * s
        side = 1 if s % 2 == 0 else -1
        pos = pol(CT, 152.0, am + side * 15.5)
        c = (NP_L if VAR[0] == 'A' else NC_L)
        doodle_on(cv, _g(out[s], pos, 4.8), c, 1.9, 0.4 if VAR[0] == 'A' else 0.0)
        pos = pol(CT, 150.0, am - side * 4.0)
        doodle_on(cv, _g(['face', 'arrow', 'crown', 'face', 'arrow', 'crown'][s], pos, 4.6 if s % 3 == 0 else 5.0), NC if VAR[0] == 'A' else CHALKC, 1.7, 0.4 if VAR[0] == 'A' else 0.0)


# ------------------------------------------------------------------ wedges
def draw_wedge(cv, w, cons=True):
    S = cv.S
    r = cv.r
    s = w['sector']
    am = 60 * s
    A = VAR[0] == 'A'
    reg = wedge_mask(cv, s, R_IN, R_OUT, 26.0, jit=0.9)
    solid = solidify(reg, S)
    y0, y1, x0, x1 = bbox(solid, 14 * S)
    sub = solid[y0:y1, x0:x1]
    yy, xx = np.mgrid[0:cv.H, 0:cv.W].astype(np.float32)
    rr = np.hypot(xx / S - CT[0], yy / S - CT[1])
    tt = np.clip((rr - R_IN) / (R_OUT - R_IN), 0, 1)[..., None]
    # neon halo + ink key shadow (a hard offset drop, the cut-out look)
    halo = ndi.gaussian_filter(solid, 3.4 * S)
    cv.over(np.clip(halo * 1.5, 0, 1) * (1 - solid), NP if A else NC, 0.42 if A else 0.28)
    drop = np.roll(np.roll(solid, int(3.0 * S), 0), int(4.0 * S), 1)
    cv.over(np.clip(drop - solid, 0, 1), INKB, 0.97)
    if A:
        # dark violet painted wedge, lighter toward the outer rim, dry-brush strokes in the same family
        c0 = np.array((40, 18, 104), np.float32)
        c1 = np.array((96, 38, 168), np.float32)
        cv.over_rgb(solid, c0 * (1 - tt) + c1 * tt)
        for i in range(12):
            a = am + r.uniform(-24, 24)
            rad = r.uniform(R_IN + 8, R_OUT - 8)
            ang = math.radians(r.choice([-50, 40, -30, 60]) + r.uniform(-12, 12))
            L = r.uniform(18, 46)
            c = pol(CT, rad, a)
            pts = [c, (c[0] + L * math.cos(ang), c[1] + L * math.sin(ang))]
            m, mx0, my0 = stroke_mask(cv, pts, r.uniform(5, 12), 'round', 0, 1.0, 30, (0.3, 0.4))
            nz = smooth(*m.shape, 1.1 * S / 4 * 1.6, r)
            m = np.clip(m * np.clip(nz * 0.9 + 0.4, 0, 1) * 1.3, 0, 1)
            cv.over(placed(cv, m, mx0, my0) * solid, PAL[int(r.integers(0, 6))] if r.random() < 0.7 else NP_D, r.uniform(0.35, 0.6))
        # pink scribble fill: loose zig-zag hatching (two passes, different angles), the Jinx scribble
        # scribble texture: loose loops and squiggles at random angles (never parallel runs: parallel runs are the hatch of pending loss)
        for q in range(7):
            cc = pol(CT, r.uniform(R_IN + 10, R_OUT - 12), am + r.uniform(-20, 20))
            ln = D.circle_s(cc[0], cc[1], r.uniform(3, 7), a0=r.uniform(0, 360), over=r.uniform(120, 300), n=22, squash=r.uniform(0.6, 1.0))
            neon(cv, ln[0], NP if q % 3 else NC, 2.0, 0.6, 0.0, wob=0.3, wl=10, clip=solid, grain=0.4)
        for q in range(4):
            cc = pol(CT, r.uniform(R_IN + 12, R_OUT - 14), am + r.uniform(-18, 18))
            ln = D.zig((cc[0] - 7, cc[1] - 3), (cc[0] + 7, cc[1] + 3), 4, 3.2)
            neon(cv, ln[0], NP_L, 2.0, 0.55, 0.0, wob=0.2, wl=8, clip=solid, grain=0.4)
        # inner neon edge glow
        inner = ndi.binary_erosion(solid > 0.5, iterations=int(2.0 * S)).astype(np.float32)
        edge = np.clip(solid - inner, 0, 1)
        cv.over(ndi.gaussian_filter(edge, 1.6 * S) * 1.6, NP, 0.35)
    else:
        cv.over_rgb(solid, np.array((255, 46, 154), np.float32) * (1 - tt * 0.18) + np.array((255, 110, 190), np.float32) * (tt * 0.18))
        fill_region(cv, sub, x0, y0, NP, ang=34 + r.uniform(-8, 8), nib=7.5, over=1.8, miss=(r.choice([-1, 1]) * 1.7, r.choice([-1, 1]) * 1.4), jit=0.5, clip=0.6, alpha=0.5)
        for i in range(10):
            a = am + r.uniform(-24, 24)
            rad = r.uniform(R_IN + 8, R_OUT - 8)
            ang = math.radians(r.choice([-50, 40, -30, 60]) + r.uniform(-12, 12))
            L = r.uniform(16, 40)
            c = pol(CT, rad, a)
            m, mx0, my0 = stroke_mask(cv, [c, (c[0] + L * math.cos(ang), c[1] + L * math.sin(ang))], r.uniform(4, 10), 'round', 0, 1.0, 30, (0.3, 0.4))
            nz = smooth(*m.shape, 1.1 * S / 4 * 1.6, r)
            m = np.clip(m * np.clip(nz * 0.9 + 0.4, 0, 1) * 1.3, 0, 1)
            cv.over(placed(cv, m, mx0, my0) * solid, NP_L if r.random() < 0.5 else NP_D, r.uniform(0.3, 0.55))
        strip = np.clip(sub - np.roll(np.roll(sub, int(-10 * S), 0), int(-8 * S), 1), 0, 1)
        hatch_region(cv, strip, x0, y0, (60, 8, 70), ang=135, pitch=3.2, w=1.2, alpha=0.6, over=0.3, jit=0.25, cross=False)
        for q in range(6):
            cc = pol(CT, r.uniform(R_IN + 10, R_OUT - 12), am + r.uniform(-20, 20))
            ln = D.circle_s(cc[0], cc[1], r.uniform(3, 7), a0=r.uniform(0, 360), over=r.uniform(120, 300), n=22, squash=r.uniform(0.6, 1.0))
            neon(cv, ln[0], NC, 2.0, 0.7, 0.0, wob=0.3, wl=10, clip=solid, grain=0.4)
    # outline: hand-scribbled, corners overshoot; a cyan plate first (misregistered), the key on top
    a0, a1 = am - 25.6, am + 25.6
    edges = [lambda: arc_pts(CT, R_OUT, a0 - 1.5, a1 + 1.5, 0.8), lambda: [pol(CT, R_OUT + 3, a1), pol(CT, R_IN - 3, a1)],
             lambda: arc_pts(CT, R_IN, a1 + 1.8, a0 - 1.8, 0.8), lambda: [pol(CT, R_IN - 3, a0), pol(CT, R_OUT + 3, a0)]]
    for pass_, (col, wd, sh, gl) in enumerate(((NC if A else NC, 2.2, (2.6, -1.9), 0.0), (NP if A else INKB, 4.2 if A else 4.8, (0, 0), 0.6 if A else 0.0))):
        for e in edges:
            neon(cv, [(p[0], p[1]) for p in e()], col, wd, 0.96, gl, wob=0.55, taper=(0.03, 0.06), wl=24, grain=0.22, shift=sh)
    if not A:
        for e in edges:      # a thin cyan plate off to the key's lower right on B: the print is slightly off
            neon(cv, [(p[0], p[1]) for p in e()], NC, 1.6, 0.9, 0.0, wob=0.5, taper=(0.03, 0.06), wl=24, grain=0.22, shift=(3.0, 2.4))
    # highlight chalk strokes near the upper-left of the wedge
    for q in range(2):
        p0 = pol(CT, R_IN + 12 + q * 5, am - 22 + q * 2)
        p1 = pol(CT, R_OUT - 24 - q * 6, am - 18 + q * 3)
        neon(cv, [p0, p1], NP_L if A else CHALKC, 2.2, 0.55, 0.0, wob=0.4, taper=(0.15, 0.45), clip=solid)
    # glitch tear on a slice that loses something this turn: two sheared slivers in cyan and pink
    hp, ha = w['hp'], w.get('hp_after', w['hp'])
    if ha < hp:
        rrg = np.random.default_rng(40 + s)
        for q in range(3):
            ya = (CT[1] + rrg.uniform(-55, 55)) * S
            hh = int(rrg.uniform(1.4, 2.8) * S)
            band = np.zeros((cv.H, cv.W), np.float32)
            band[int(ya):int(ya) + hh, :] = 1.0
            sh = int(rrg.choice([-1, 1]) * rrg.uniform(5, 9) * S)
            moved = np.roll(solid, sh, 1)
            cv.over(band * moved * solid, NC if q % 2 == 0 else NP_L, 0.9)
            cv.over(band * np.clip(moved - solid, 0, 1), NC if q % 2 == 0 else NP, 0.75)
    return solid


def draw_icon(cv, w, solid):
    """E10 silhouettes, chalk white with a cyan and a pink plate shifted off the key (misregistration) and an ink keyline"""
    S = cv.S
    t = w['t']
    am = 60 * w['sector']
    c = pol(CT, ICON_R, am)
    white, dark = FI.mask_for(t, ICON_PX, S)
    n = white.shape[0]
    x0, y0 = int(c[0] * S - n / 2), int(c[1] * S - n / 2)
    wm = solidify(white, S)
    full = np.clip(wm + dark, 0, 1)
    ring = np.clip(ndi.gaussian_filter(outline_mask(full, S, 2.2), 0.3 * S / 4 * 1.5) * 1.6, 0, 1)
    A = VAR[0] == 'A'
    sh = lambda m, dx, dy: np.roll(np.roll(m, int(dy * S), 0), int(dx * S), 1)
    cv.over(np.clip(sh(full, 3.0, 2.2) - full, 0, 1), NP if A else INKB, 0.97, x0, y0)
    cv.over(np.clip(sh(full, -2.6, -1.6) - full, 0, 1), NC, 0.97, x0, y0)
    cv.over(ring, INKB, 0.99, x0, y0)
    if dark.max() > 0:
        cv.over(np.clip(dark, 0, 1), INKB, 0.98, x0, y0)
        hatch_region(cv, np.clip(dark, 0, 1), x0, y0, (236, 232, 255), ang=45, pitch=3.0, w=0.8, alpha=0.5, over=0.0, jit=0.1)
    cv.over(np.clip(wm, 0, 1), CHALKC, 0.99, x0, y0)
    # one thin glitch slice through the icon
    yy = int(n * (0.38 + 0.08 * (w['sector'] % 3)))
    bandm = np.zeros_like(wm)
    bandm[yy:yy + int(2.2 * S), :] = 1
    cv.over(np.clip(np.roll(wm, int(6 * S), 1), 0, 1) * bandm, NC_L, 0.95, x0, y0)
    return x0, y0, full


def draw_brace_plate(cv, s):
    """L10 double line: a clamp on the page margin along the slice's outer rim: two neon chalk lines 3 px apart, jaw ticks, two rivets, ink strip under"""
    S = cv.S
    am = 60 * s
    a0, a1 = am - 26.5, am + 26.5
    strip = cv.band_mask(CT, 177.0, 191.0, a0, a1, step=0.6)
    strip = warp(strip, 0.7 * S, 8 * S, cv.r)
    solid = solidify(strip, S)
    cv.over(np.clip(ndi.gaussian_filter(solid, 2.0 * S) * 1.5, 0, 1), NC, 0.35)
    cv.over(solid, INKB, 0.98)
    for rr in (181.4, 186.6):
        neon(cv, arc_pts(CT, rr, a0 + 2.5, a1 - 2.5, 0.8), NC_L, 2.0, 1.0, 0.5, wob=0.35, taper=(0.04, 0.04), wl=40)
    for sg in (-1, 1):
        neon(cv, [pol(CT, 176.0, am + sg * 24.0), pol(CT, 192.0, am + sg * 24.0)], NP, 3.0, 1.0, 0.5, wob=0.15, taper=(0, 0))
        x, y = pol(CT, 184.0, am + sg * 20.5)
        cv.over(cv.circle_mask((x, y), 2.0), NP, 1.0)


# ------------------------------------------------------------------ hub: a spiky neon badge, BREAKER in chalk
def draw_hub(cv, name='BREAKER'):
    S = cv.S
    c = CT
    A = VAR[0] == 'A'
    pts = []
    nb = 14
    for i in range(nb * 2 * 8 + 1):
        a = i / (nb * 2 * 8) * 360
        k = i % 16
        spike = 1.0 if k < 8 else 0.9
        pts.append(pol(c, (R_HUB - 2.0) * (0.92 + 0.10 * abs(math.sin(math.radians(a * nb / 2)))), a))
    reg = cv.poly_mask(pts)
    reg = warp(reg, 0.5 * S, 9 * S, cv.r)
    solid = solidify(reg, S)
    cv.over(np.clip(ndi.gaussian_filter(solid, 3.0 * S) * 1.8, 0, 1) * (1 - solid), NC, 0.45)
    drop = np.roll(np.roll(solid, int(3 * S), 0), int(4 * S), 1)
    cv.over(np.clip(drop - solid, 0, 1), INKB, 0.97)
    cv.over(np.clip(ndi.gaussian_filter(outline_mask(solid, S, 2.8), 0.4) * 1.5, 0, 1), INKB, 1.0)
    yy, xx = np.mgrid[0:cv.H, 0:cv.W].astype(np.float32)
    rr = np.hypot(xx / S - c[0], yy / S - c[1])
    k = np.clip(rr / R_HUB, 0, 1)[..., None]
    if A:
        col = np.array((70, 22, 120), np.float32) * (1 - k) + np.array((28, 12, 70), np.float32) * k
    else:
        col = np.array((255, 70, 170), np.float32) * (1 - k) + np.array((214, 28, 134), np.float32) * k
    cv.over_rgb(solid, col)
    cv.over(np.clip(ndi.gaussian_filter(solid, 0.1) - ndi.binary_erosion(solid > 0.5, iterations=int(2.2 * S)).astype(np.float32), 0, 1), NP if A else NC_L, 0.9)
    # cyan misregistered ring and chalk glints
    neon(cv, arc_pts(c, R_HUB - 7.5, 190, 300, 0.8), NC_L, 2.0, 0.85, 0.3, wob=0.2, taper=(0.2, 0.4))
    # lightning bolt (the Breaker), cyan plate offset
    ex, ey = c[0], c[1] - 14.5
    bolt = [(ex + 2.5, ey - 9), (ex - 5.0, ey + 1.0), (ex - 0.5, ey + 1.0), (ex - 3.0, ey + 9.5), (ex + 5.5, ey - 2.0), (ex + 0.5, ey - 2.0)]
    bm = cv.poly_mask(bolt)
    cv.over(np.clip(ndi.gaussian_filter(outline_mask(bm, S, 1.4), 0.4) * 1.5, 0, 1), INKB, 0.98)
    cv.over(np.roll(np.roll(bm, int(-1.2 * S), 0), int(-1.5 * S), 1), NC, 0.95)
    cv.over(np.roll(np.roll(bm, int(0.5 * S), 0), int(0.5 * S), 1), CHALKC, 0.99)
    if name:
        letters(cv, name, (c[0], c[1] + 10.5), 15.5, fnt=MARKER_F, fill=CHALKC, ink=INKB, extrude=1.8, ext_col=NP if not A else NC, ink_w=1.9, outline=True, miss=(0.4, 0.3), wob=0.2, spacing=0.3, hatch_ext=False)


# ------------------------------------------------------------------ assembler: f1_tower's, with this module's pieces
def install():
    for nm in ('page_disc', 'construction', 'tape_strips', 'doodles', 'draw_wedge', 'draw_icon', 'draw_brace_plate', 'draw_hub'):
        setattr(FT, nm, globals()[nm])


if __name__ == '__main__':
    import time, json
    from PIL import Image
    import asm_r2 as AA
    AA.setup()
    install()
    VAR[0] = sys.argv[1] if len(sys.argv) > 1 else 'A'
    key = sys.argv[2] if len(sys.argv) > 2 else 'f1'
    t = time.time()
    J = json.load(open('D:/rc_scratch/combat_redesign/punk/jinx_scribble/state_e10.json'))
    im, _ = FT.render_tower(J[key])
    bg = Image.new('RGBA', (560, 560), (28, 30, 44, 255))
    bg.alpha_composite(im, (45, 45))
    bg.save('D:/rc_scratch/combat_redesign/punk/jinx_scribble/out/tower_%s_%s.png' % (VAR[0], key))
    print(time.time() - t)
