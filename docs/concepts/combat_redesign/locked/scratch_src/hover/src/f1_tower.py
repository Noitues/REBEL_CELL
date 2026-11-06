"""f1_tower: the BLACK-BOOK BURNER tower (F1).  The Cell drew its board in its black book, then pasted it up on the wall.
Tower r196: dot-grid page (multiplied to 72 percent value), torn rim, 2 kraft tape strips (30 and 210 deg); six pink chisel-marker slices that miss a
ballpoint construction line by 2 px, single-direction ballpoint hatch shadow, 5 px tapered ink outline + 3x4 block drop; E10 silhouettes re-inked;
G1 throw-up hub with chrome highlight; player HP ring wrapping the hub (r52-64, 15 blocks in 3 x 5); slice pips; threat trim r200-210 (T family, time grammar).
render_tower(f, opt) -> (RGBA image TW x TW at 1x, centre CT).  Game data = the E10 sim frame, unchanged."""
import math, sys, json
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from f1_lib import *
import f1_icons as FI

TW = 470
CT = (TW / 2.0, TW / 2.0)
S_DEF = 3
R_PAGE = 192.0
R_HUB = 46.0
R_HP0, R_HP1 = 52.0, 64.0
R_IN, R_OUT = 71.0, 177.0
ICON_R, ICON_PX = 120.0, 48
PIP_R, PIP_W = 167.0, 8.0
TRIM0, TRIM1 = 200.0, 210.0

CELL_PINK = PINK
BALL = (44, 62, 158)
PAGE_V = 0.72
PAGE_TINT = tuple(int(c * PAGE_V) for c in (242, 238, 228))
KRAFT = (198, 154, 98)
CHROME = (201, 211, 224)
SOAKC = (58, 126, 243)
HARMC = (255, 68, 51)
COLD_HARM = (217, 135, 124)
FAR_HARM = (140, 104, 100)
TMID = (175, 192, 214)
GAINC = (123, 224, 123)
SHADOW_DIR = (0.62, 0.78)          # light from the top left: shadow side is bottom right


def bbox(m, pad, thr=0.02):
    ys, xs = np.nonzero(m > thr)
    if len(ys) == 0:
        return None
    y0, y1 = max(0, ys.min() - pad), min(m.shape[0], ys.max() + 1 + pad)
    x0, x1 = max(0, xs.min() - pad), min(m.shape[1], xs.max() + 1 + pad)
    return y0, y1, x0, x1


def solidify(m, S):
    return np.clip((ndi.gaussian_filter(m, 0.5 * S / 4 * 1.5) - 0.45) * 6, 0, 1)


def tapered_outline(cv, solid, wmin, wmax, col=INK, alpha=0.98, seed_shift=0.0):
    """ink outline whose width runs wmin..wmax: heavy on the shadow side (bottom right), thin on the lit side.  Works on a local crop."""
    S = cv.S
    bb = bbox(solid, int((wmax + 6) * S))
    if bb is None:
        return
    y0, y1, x0, x1 = bb
    sub = solid[y0:y1, x0:x1]
    inside = sub > 0.5
    d = ndi.distance_transform_edt(~inside) / S
    ds = ndi.gaussian_filter(d, 1.2 * S)
    gy, gx = np.gradient(ds)
    nrm = np.hypot(gx, gy) + 1e-6
    dot = (gx * SHADOW_DIR[0] + gy * SHADOW_DIR[1]) / nrm
    wid = wmin + (wmax - wmin) * np.clip(0.5 + 0.62 * dot, 0, 1)
    ring = np.clip((wid - d) * S + 0.5, 0, 1) * (1 - np.clip(sub, 0, 1))
    ring = ndi.gaussian_filter(ring, 0.35 * S / 4 * 1.5)
    cv.over(np.clip(ring * 1.2, 0, 1), col, alpha, x0, y0)


def block_drop(cv, solid, dx=3.0, dy=4.0, col=INK, alpha=0.96):
    S = cv.S
    ex = np.zeros_like(solid)
    n = int(max(dx, dy) * S)
    for k in range(1, n + 1):
        ex = np.maximum(ex, np.roll(np.roll(solid, int(round(k * dy / max(dx, dy))), 0), int(round(k * dx / max(dx, dy))), 1))
    ex = np.clip(ex - solid, 0, 1)
    cv.over(ex, col, alpha)
    return ex


def wedge_mask(cv, s, r0, r1, half, jit=1.0):
    reg = cv.band_mask(CT, r0, r1, 60 * s - half, 60 * s + half, step=0.7)
    return warp(reg, jit * cv.S, 24 * cv.S, cv.r)


# ------------------------------------------------------------------ page, construction, tape
def page_disc(cv):
    S = cv.S
    disc = cv.circle_mask(CT, R_PAGE)
    t, rim = torn_mask(cv, disc, rough=2.0, fringe=1.0)
    pap = paper_rgb(cv, 'dot', PAGE_TINT, pitch=11.0, strength=0.9)
    yy, xx = np.mgrid[0:cv.H, 0:cv.W].astype(np.float32)
    rr = np.hypot(xx / S - CT[0], yy / S - CT[1])
    pap *= (1 - 0.07 * np.clip((rr - 120) / 70, 0, 1))[..., None]
    # block drop of the page itself (it is pasted up on the wall)
    sh = np.roll(np.roll(t, int(4 * S), 0), int(5 * S), 1)
    cv.over(ndi.gaussian_filter(sh, 3.0 * S), (6, 4, 12), 0.62)
    cv.over(np.clip(sh - t, 0, 1), INK, 0.55)
    cv.over_rgb(t, pap)
    # the dot grid: ballpoint-blue dots on an 11 px grid so the page reads as dot paper even after the 72 percent multiply
    p_ = 11.0 * S
    yy, xx = np.mgrid[0:cv.H, 0:cv.W].astype(np.float32)
    gx = np.abs(((xx + p_ / 2) % p_) - p_ / 2)
    gy = np.abs(((yy + p_ / 2) % p_) - p_ / 2)
    dots = np.clip(1 - np.hypot(gx, gy) / (0.75 * S), 0, 1) * 0.6
    cv.over(dots * t, (60, 78, 140), 0.55)
    cv.over(np.clip(rim, 0, 1) * 0.45, (226, 222, 214), 1.0)
    return t


def construction(cv):
    col = BALL
    for r_, a_, w_ in ((R_HUB + 2, 0.34, 0.8), (R_IN - 3.0, 0.28, 0.8), (R_OUT + 3.0, 0.30, 0.8), (150.0, 0.18, 0.7)):
        sketch_circle(cv, CT, r_, col, w_, passes=1, alpha=a_, over=10)
    for k in range(6):
        a = 60 * k + 30
        sketch_line(cv, pol(CT, 20, a), pol(CT, R_PAGE - 4, a), col, 0.8, passes=1, alpha=0.26, over=2.0)
    # compass pivot cross
    sketch_line(cv, (CT[0] - 5, CT[1]), (CT[0] + 5, CT[1]), col, 0.8, alpha=0.3)
    sketch_line(cv, (CT[0], CT[1] - 5), (CT[0], CT[1] + 5), col, 0.8, alpha=0.3)


def tape_strips(cv):
    for a in (30, 210):
        c = pol(CT, R_PAGE - 6, a)
        rot = a - 90 + cv.r.uniform(-5, 5)
        tape(cv, c, 34, 13, rot + 90, col=KRAFT, alpha=0.88)


DOODLES = ('star', 'spark', 'arrow', 'cross')


def doodles(cv):
    """at most 4, on the disc margin only (between the slice rim and the page edge), in the gaps between slices: never over a pip, an HP block, a ring cell or a threat mark"""
    c = BALL
    r_ = 184.0
    doodle_star(cv, pol(CT, r_, 90), 6.0, c, 1.1, alpha=0.9)
    doodle_spark(cv, pol(CT, r_, 150), 6.6, c, 1.1, n=7, alpha=0.9)
    doodle_cross(cv, pol(CT, r_, 270), 4.4, c, 1.2, alpha=0.9)
    doodle_zig(cv, pol(CT, r_, 322), pol(CT, r_, 338), c, 1.1, n=4, amp=2.6, alpha=0.9)


# ------------------------------------------------------------------ HP block (shared grammar)
def hp_region(cv, rc, w, a0, a1, bulge=0.0):
    reg = cv.band_mask(CT, rc - w / 2 - bulge / 2, rc + w / 2 + bulge / 2, a0, a1, step=0.5)
    reg = warp(reg, 0.4 * cv.S, 6 * cv.S, cv.r)
    return solidify(reg, cv.S)


def draw_block(cv, rc, w, a0, a1, state, ink_w=1.6, pitch=None, crossh=None, glow=True):
    """one painted HP block.  state: lit | harm | soak | ours | mend | gone | cold_harm | cold_soak.
    pending (harm/soak/ours) = L7 hatch in the cause colour, a solid 2 px edge, and the block bulges 2 px thicker than a lit one"""
    S = cv.S
    pend = state in ('harm', 'soak', 'ours')
    solid = hp_region(cv, rc, w, a0, a1, bulge=2.0 if pend else 0.0)
    ring = np.clip(ndi.gaussian_filter(outline_mask(solid, S, ink_w), 0.3 * S / 4 * 1.5) * 1.6, 0, 1)
    if state == 'gone':
        cv.over(solid, (14, 16, 22), 0.95)
        cv.over(np.clip(ndi.gaussian_filter(outline_mask(solid, S, 0.9), 0.3) * 1.5, 0, 1), (120, 126, 140), 0.9)
        return solid
    col = {'harm': HARMC, 'soak': SOAKC, 'ours': CELL_PINK}.get(state)
    if pend and glow:
        gl = ndi.gaussian_filter(solid, 2.4 * S)
        cv.over(np.clip(gl * 1.5, 0, 1), col, 0.30)
    cv.over(ring, INK, 0.98)
    if state == 'lit':
        fm = np.roll(np.roll(solid, int(0.6 * S), 0), int(0.5 * S), 1)
        n = smooth(*fm.shape, 3 * S / 4 * 1.5, cv.r)
        cv.over(np.clip(fm * (0.94 + 0.06 * n), 0, 1), GAINC, 0.97)
        a_mid = (a0 + a1) / 2
        pts = [pol(CT, rc - w * 0.2, a0 + (a1 - a0) * 0.14), pol(CT, rc - w * 0.2, a0 + (a1 - a0) * 0.6)]
        marker(cv, pts, (214, 255, 214), w=1.3, alpha=0.5, wob=0.1, grain=0, rough=0, taper=(0.1, 0.4))
    elif pend:
        cv.over(solid, (14, 14, 22), 0.97)
        inner = ndi.binary_erosion(solid > 0.5, iterations=max(1, int(1.1 * S))).astype(np.float32)
        thick = min(w, (R_HP1 - R_HP0)) if crossh is None else (14 if crossh else 8)
        cross = (w >= 12) if crossh is None else crossh
        hatch_region(cv, inner, 0, 0, col, ang=45, pitch=pitch or (4.4 if cross else 4.0), w=1.6, alpha=0.96, over=0.0, jit=0.08, cross=cross)
        cv.over(np.clip(ndi.gaussian_filter(outline_mask(inner, S, 1.0, inner=1.0), 0.3) * 1.6, 0, 1), col, 0.99)
        if state == 'soak':     # 5 px chevron notch cut into the outer edge
            am = (a0 + a1) / 2
            x, y = pol(CT, rc + w / 2 + 1.0, am)
            x2, y2 = pol(CT, rc - w * 0.05, am)
            tg = (math.cos(math.radians(am)), math.sin(math.radians(am)))
            p = [(x + tg[0] * 4.4, y + tg[1] * 4.4), (x2, y2), (x - tg[0] * 4.4, y - tg[1] * 4.4)]
            ballpoint(cv, p, INK, 2.4, 1.0, wob=0.0, wl=9, taper=(0, 0))
    elif state == 'mend':
        cv.over(solid, (14, 22, 16), 0.97)
        inner = ndi.binary_erosion(solid > 0.5, iterations=max(1, int(1.1 * S))).astype(np.float32)
        cv.over(np.clip(ndi.gaussian_filter(outline_mask(inner, S, 1.2, inner=1.2), 0.3) * 1.6, 0, 1), GAINC, 0.98)
        am = (a0 + a1) / 2
        x, y = pol(CT, rc, am)
        ballpoint(cv, [(x - 3.4, y), (x + 3.4, y)], GAINC, 1.6, 1.0, wob=0, taper=(0, 0))
        ballpoint(cv, [(x, y - 3.4), (x, y + 3.4)], GAINC, 1.6, 1.0, wob=0, taper=(0, 0))
    return solid


def hp_states(hp, hp_after, mx):
    taken = max(0, hp - hp_after)
    out = []
    for i in range(mx):
        out.append('harm' if i < taken else ('lit' if i < taken + hp_after else 'gone'))
    return out


def draw_hp_ring(cv, f):
    """wraps the hub: r52-64, 15 blocks in 3 groups of 5; the pending run starts at the needle and runs clockwise"""
    S = cv.S
    mx = f['maxhp']
    sts = hp_states(f['hp'], f['pv']['hp_after'], mx)
    rc, w = (R_HP0 + R_HP1) / 2, R_HP1 - R_HP0
    ngrp, per = 3, 5
    g2, g1 = 9.0, 2.6
    seg = (360 / ngrp - g2 - (per - 1) * g1) / per
    # marker band under the ring: black page ink so the blocks read on the paper
    for g in range(ngrp):
        a0 = g * 120 + g2 / 2 - 1.2
        a1 = a0 + 120 - g2 + 2.4
        pts = arc_pts(CT, rc, a0, a1, 1.0)
        marker(cv, pts, INK, w=w + 5.6, alpha=0.96, wob=0.3, wl=60, taper=(0.02, 0.02), grain=0.06)
    for i, st in enumerate(sts):
        grp, j = divmod(i, per)
        a0 = grp * 120 + g2 / 2 + j * (seg + g1)
        draw_block(cv, rc, w, a0, a0 + seg, st)


# ------------------------------------------------------------------ slices
def pip_states(w):
    mx, hp, ha, sk = w['mx'], w['hp'], w.get('hp_after', w['hp']), w.get('soaked', 0)
    out = []
    for i in range(mx):
        if i < ha and i < hp:
            out.append('lit')
        elif i < ha:
            out.append('mend')
        elif i < hp:
            out.append('soak' if (hp - 1 - i) < sk else 'harm')
        else:
            out.append('gone')
    return out


def draw_pips(cv, w):
    s = w['sector']
    sts = pip_states(w)
    n = len(sts)
    bl, bg = 36.0, 6.0
    tot = n * bl + (n - 1) * bg
    cr = lambda px: math.degrees(px / PIP_R)
    a = 60 * s - cr(tot) / 2
    for i, st in enumerate(sts):
        a0 = a + cr(i * (bl + bg))
        draw_block(cv, PIP_R, PIP_W, a0, a0 + cr(bl), st, ink_w=1.5, pitch=4.0, crossh=False, glow=False)


def draw_wedge(cv, w, cons=True):
    S = cv.S
    r = cv.r
    s = w['sector']
    am = 60 * s
    reg = wedge_mask(cv, s, R_IN, R_OUT, 26.0, jit=0.9)
    solid = solidify(reg, S)
    # 1. block drop (3 x 4 px toward bottom right): the wedge reads as a letter piece
    block_drop(cv, solid, 3.0, 4.0)
    # 2. heavier tapered ink outline
    tapered_outline(cv, solid, 2.6, 5.0)
    # 3. ballpoint construction edge (exact), then the marker fill that misses it by 2 px
    bb = bbox(solid, 6 * S)
    y0, y1, x0, x1 = bb
    sub = solid[y0:y1, x0:x1]
    # construction: the exact wedge outline in ballpoint, drawn BEFORE the fill so the pink misses it
    for rr in (R_IN, R_OUT):
        ballpoint(cv, arc_pts(CT, rr, am - 25.4, am + 25.4, 0.8), BALL, 0.9, 0.55, wob=0.35, wl=30)
    for sg in (-1, 1):
        ballpoint(cv, [pol(CT, R_IN, am + sg * 25.4), pol(CT, R_OUT, am + sg * 25.4)], BALL, 0.9, 0.55, wob=0.35, wl=30)
    miss = (r.choice([-1, 1]) * r.uniform(1.6, 2.2), r.choice([-1, 1]) * r.uniform(1.4, 2.0))
    fill_region(cv, sub, x0, y0, CELL_PINK, ang=34 + r.uniform(-8, 8), nib=7.5, over=1.8, miss=miss, jit=0.5, clip=0.6, alpha=0.96)
    # 4. single-direction ballpoint hatch shadow (never cross-hatch) on the bottom right band
    strip = np.clip(sub - np.roll(np.roll(sub, int(-9 * S), 0), int(-7 * S), 1), 0, 1)
    hatch_region(cv, strip, x0, y0, (112, 14, 70), ang=135, pitch=3.2, w=1.0, alpha=0.7, over=0.3, jit=0.2, cross=False)
    # 5. two light-pink brush strokes near the upper left (the marker highlight)
    for q in range(2):
        p0 = pol(CT, R_IN + 12 + q * 5, am - 22 + q * 2)
        p1 = pol(CT, R_OUT - 24 - q * 6, am - 18 + q * 3)
        marker(cv, [p0, p1], PINK_L, w=2.6, nib='chisel', ang=30, alpha=0.5, wob=0.5, taper=(0.15, 0.45))
    return solid


def draw_icon(cv, w, solid):
    """E10 silhouettes re-inked (ink outline, white marker fill that misses by 1 px)"""
    S = cv.S
    t = w['t']
    am = 60 * w['sector']
    c = pol(CT, ICON_R, am)
    white, dark = FI.mask_for(t, ICON_PX, S)
    n = white.shape[0]
    x0, y0 = int(c[0] * S - n / 2), int(c[1] * S - n / 2)
    wm = solidify(white, S)
    full = np.clip(wm + dark, 0, 1)
    ring = np.clip(ndi.gaussian_filter(outline_mask(full, S, 2.0), 0.3 * S / 4 * 1.5) * 1.6, 0, 1)
    sh = np.roll(np.roll(full, int(2.0 * S), 0), int(2.0 * S), 1)
    cv.over(np.clip(sh - full, 0, 1), (60, 8, 36), 0.55, x0, y0)
    cv.over(ring, INK, 0.99, x0, y0)
    if dark.max() > 0:
        cv.over(np.clip(dark, 0, 1), INK, 0.98, x0, y0)
        hatch_region(cv, np.clip(dark, 0, 1), x0, y0, (236, 232, 222), ang=45, pitch=3.0, w=0.8, alpha=0.5, over=0.0, jit=0.1)
    fm = np.roll(np.roll(wm, int(0.7 * S), 0), int(0.6 * S), 1)
    cv.over(np.clip(fm, 0, 1), WHITE, 0.99, x0, y0)
    return x0, y0, full


def draw_break_state(cv, w, solid):
    """pending loss of a whole slice: L7 cross-hatch wash over the wedge (clear disc around the icon) + a stencil X in the outer corner; hatch colour = cause"""
    S = cv.S
    hp, ha = w['hp'], w.get('hp_after', w['hp'])
    am = 60 * w['sector']
    if hp > 0 and ha == 0:
        col = SOAKC if w.get('soaked') else HARMC
        ix, iy = pol(CT, ICON_R, am)
        clear = 1 - np.clip(cv.circle_mask((ix, iy), 31), 0, 1)
        reg = solid * clear
        cv.over(reg, (20, 8, 28), 0.28)
        bb = bbox(reg, 2)
        y0, y1, x0, x1 = bb
        hatch_region(cv, reg[y0:y1, x0:x1], x0, y0, col, ang=45, pitch=5.4, w=1.9, alpha=0.93, over=1.0, jit=0.5, cross=True)
        edge = np.clip(ndi.gaussian_filter(outline_mask(solid, S, 2.2, inner=2.2), 0.4) * 1.5, 0, 1)
        cv.over(edge, col, 0.98)
        x, y = pol(CT, R_OUT - 22, am + 17)
        for sg in (1, -1):
            p = [(x - 7, y - sg * 7), (x + 7, y + sg * 7)]
            ballpoint(cv, p, INK, 7.6, 1.0, wob=0.3, wl=9, taper=(0, 0))
        for sg in (1, -1):
            p = [(x - 7, y - sg * 7), (x + 7, y + sg * 7)]
            marker(cv, p, col, w=4.6, alpha=1.0, wob=0.3, grain=0.05, taper=(0, 0))
    elif hp == 0:           # gone: dark socket
        cv.over(solid, (10, 10, 16), 0.9)
    elif hp < w['mx'] and ha == hp:      # cracked: white zig-zag beside the rim corner, off the icon
        pts = [pol(CT, R_OUT - 6, am + 20), pol(CT, R_OUT - 14, am + 17), pol(CT, R_OUT - 19, am + 22), pol(CT, R_OUT - 27, am + 18.5), pol(CT, R_OUT - 33, am + 23.5)]
        ballpoint(cv, pts, INK, 5.0, 1.0, wob=0.2, wl=8, taper=(0, 0))
        ballpoint(cv, pts, WHITE, 1.9, 1.0, wob=0.2, wl=8, taper=(0, 0))


def draw_brace_plate(cv, s):
    """L10 double line: a taped paper clamp strip laid on the page margin along the slice's outer rim (the Brace card's clamp): torn paper, two marker lines, jaw ticks, two ink rivets"""
    S = cv.S
    am = 60 * s
    a0, a1 = am - 26.5, am + 26.5
    strip = cv.band_mask(CT, 177.0, 191.0, a0, a1, step=0.6)
    strip = warp(strip, 0.7 * S, 8 * S, cv.r)
    t, rim = torn_mask(cv, strip, rough=0.6, fringe=0.6)
    solid = solidify(t, S)
    block_drop(cv, solid, 2.0, 3.0)
    tapered_outline(cv, solid, 1.6, 3.0)
    cv.over(solid, (246, 242, 232), 1.0)
    for rr in (181.4, 186.6):                                   # the double line: two solid marker strokes, 3 px apart
        pts = arc_pts(CT, rr, a0 + 3.0, a1 - 3.0, 0.8)
        marker(cv, pts, INK, w=2.6, alpha=0.98, wob=0.35, wl=40, taper=(0.04, 0.04), grain=0.05)
    for sg in (-1, 1):                                          # clamp jaws: ink ticks across both lines + rivets
        p0 = pol(CT, 176.0, am + sg * 24.0)
        p1 = pol(CT, 192.0, am + sg * 24.0)
        marker(cv, [p0, p1], INK, w=3.2, alpha=1.0, wob=0.15, taper=(0, 0), grain=0.05)
        x, y = pol(CT, 184.0, am + sg * 20.5)
        cv.over(cv.circle_mask((x, y), 1.9), INK, 1.0)
    tape(cv, pol(CT, 184.0, am + 0.0), 18, 8, am + 90, col=KRAFT, alpha=0.85)


def draw_soak_mark(cv, s):
    """SOAK: an inward chevron funnel on the hub side of the wedge, under the icon, never over it"""
    am = 60 * s
    p = [pol(CT, R_IN + 20, am - 12), pol(CT, R_IN + 11, am), pol(CT, R_IN + 20, am + 12)]
    ballpoint(cv, p, INK, 10.0, 1.0, wob=0.2, wl=20, taper=(0, 0))
    marker(cv, p, SOAKC, w=5.4, alpha=1.0, wob=0.25, wl=20, taper=(0, 0), grain=0.06)


# ------------------------------------------------------------------ hub (G1 throw-up bubble with chrome)
def draw_hub(cv, name='BREAKER'):
    S = cv.S
    r = cv.r
    c = CT
    pts = []
    nb = 12
    for i in range(nb * 14 + 1):
        a = i / (nb * 14) * 360
        bump = 1 + 0.07 * abs(math.sin(math.radians(a * nb / 2)))
        pts.append(pol(c, (R_HUB - 2.4) * bump, a))
    reg = cv.poly_mask(pts)
    reg = warp(reg, 0.5 * S, 9 * S, r)
    solid = solidify(reg, S)
    block_drop(cv, solid, 3.0, 4.0)
    tapered_outline(cv, solid, 2.6, 5.0)
    # pink fill, chrome highlight crescent top left, pink-dark shade bottom right
    fill_region(cv, solid, 0, 0, CELL_PINK, ang=-30, nib=6.0, over=1.0, miss=(1.0, 0.8), alpha=0.97, jit=0.3, clip=0.6)
    inner = ndi.binary_erosion(solid > 0.5, iterations=int(3.0 * S)).astype(np.float32)
    shade = np.clip(inner - np.roll(np.roll(inner, int(-6 * S), 0), int(-5 * S), 1), 0, 1)
    cv.over(ndi.gaussian_filter(shade, 1.2 * S), PINK_D, 0.7)
    hi = np.clip(inner - np.roll(np.roll(inner, int(5 * S), 0), int(5 * S), 1), 0, 1)
    cv.over(ndi.gaussian_filter(hi, 0.7 * S), CHROME, 0.9)
    marker(cv, arc_pts(c, R_HUB - 8.5, 205, 285, 0.8), (246, 250, 255), w=2.4, alpha=0.9, wob=0.2, taper=(0.2, 0.4), grain=0.0)
    # tag emblem: lightning bolt above the name (the Breaker)
    ex, ey = c[0], c[1] - 14.5
    bolt = [(ex + 2.5, ey - 9), (ex - 5.0, ey + 1.0), (ex - 0.5, ey + 1.0), (ex - 3.0, ey + 9.5), (ex + 5.5, ey - 2.0), (ex + 0.5, ey - 2.0)]
    bm = cv.poly_mask(bolt)
    cv.over(np.clip(ndi.gaussian_filter(outline_mask(bm, S, 1.4), 0.4) * 1.5, 0, 1), INK, 0.98)
    cv.over(np.roll(np.roll(bm, int(0.5 * S), 0), int(0.5 * S), 1), PAPER, 0.98)
    if name:
        letters(cv, name, (c[0], c[1] + 10.5), 15.5, fnt=MARKER_F, fill=PAPER, ink=INK, extrude=1.6, ext_col=INK, ink_w=1.9, outline=True, miss=(0.4, 0.3), wob=0.2, spacing=0.3, hatch_ext=False)


# ------------------------------------------------------------------ T family: threat trim (flat stencil, time grammar)
def trim_data(f, skip_units=None):
    seen = {}
    for u in f['units']:
        if skip_units and u['id'] in skip_units:
            continue
        fz = u['fate']
        if fz['kind'] != 'lands' or u['consumed'] or u['trigdead']:
            continue
        for (sec, sl, hit, tohp) in fz['hits']:
            seen.setdefault(sec, set()).add(fz['k'])
    return seen


def draw_trim(cv, f, skip_units=None, state_hot=True):
    """HOT: bold, full chroma, glow, END notch (8 px wedge on the tower-facing end).  COLD: thinner, #D9877C solid, one pip.  FAR: dotted, 50 percent, two pips."""
    S = cv.S
    zones = {2: (-26.5, -9.5), 1: (-8.5, 8.5), 0: (9.5, 26.5)}
    for sec, ks in trim_data(f, skip_units).items():
        mm = 60 * sec
        for k in sorted(ks):
            a0, a1 = zones[k]
            a0 += mm
            a1 += mm
            if k == 0:
                reg = cv.band_mask(CT, TRIM0, TRIM1, a0, a1, step=0.5)
                if state_hot:
                    gl = ndi.gaussian_filter(reg, 3.2 * S)
                    cv.over(np.clip(gl * 1.7, 0, 1), HARMC, 0.42)
                cv.over(np.clip(ndi.gaussian_filter(outline_mask(reg, S, 2.3), 0.4) * 1.5, 0, 1), INK, 1.0)
                cv.over(reg, HARMC, 1.0)
                am = (a0 + a1) / 2
                tip = pol(CT, TRIM0 - 8.5, am)
                b0 = pol(CT, TRIM0 + 0.5, am - 3.4)
                b1 = pol(CT, TRIM0 + 0.5, am + 3.4)
                tri = cv.poly_mask([b0, b1, tip])
                cv.over(np.clip(ndi.gaussian_filter(outline_mask(tri, S, 1.8), 0.4) * 1.5, 0, 1), INK, 1.0)
                cv.over(tri, HARMC, 1.0)
            elif k == 1:
                reg = cv.band_mask(CT, TRIM0 + 2.0, TRIM1 - 2.0, a0, a1, step=0.5)
                cv.over(np.clip(ndi.gaussian_filter(outline_mask(reg, S, 1.8), 0.4) * 1.5, 0, 1), INK, 0.97)
                cv.over(reg, COLD_HARM, 1.0)
                bx, by = pol(CT, TRIM1 + 6.5, a0 + 1.6)
                cv.over(cv.circle_mask((bx, by), 3.1), INK, 1.0)
                cv.over(cv.circle_mask((bx, by), 2.0), TMID, 1.0)
            else:
                rc = (TRIM0 + TRIM1) / 2
                n = int(math.radians(a1 - a0) * rc / 7.4)
                for i in range(n + 1):
                    a = a0 + (a1 - a0) * i / max(1, n)
                    p = pol(CT, rc, a)
                    cv.over(cv.circle_mask(p, 3.5), INK, 0.97)
                    cv.over(cv.circle_mask(p, 2.2), FAR_HARM, 1.0)
                for j in range(2):
                    bx, by = pol(CT, TRIM1 + 6.5, a0 + 1.6 + j * 3.6)
                    cv.over(cv.circle_mask((bx, by), 3.1), INK, 1.0)
                    cv.over(cv.circle_mask((bx, by), 2.0), TMID, 1.0)


# ------------------------------------------------------------------ N family: grease-pencil hover arcs on the slices a hovered unit lands on
PLAN_Y = (255, 226, 0)


def pencil(cv, pts, w=6.0, alpha=0.97, grain=0.32):
    """L6 grease pencil: PLAN yellow, 7 px with a 3 px ink edge, wax grain, no glow"""
    ballpoint(cv, pts, INK, w + 3.6, 1.0, wob=0.35, wl=40, taper=(0.04, 0.04))
    marker(cv, pts, PLAN_Y, w=w, alpha=alpha, wob=0.35, wl=40, taper=(0.04, 0.04), grain=grain, rough=0.35, pool=0.0)


def draw_hover_arcs(cv, sectors):
    for sec in sectors:
        a0, a1 = 60 * sec - 24, 60 * sec + 24
        pencil(cv, arc_pts(CT, R_OUT + 8.0, a0, a1, 0.8), 5.4)


# ------------------------------------------------------------------ assembler
def render_tower(f, name='BREAKER', S=S_DEF, seed=11, skip_trim_units=None, hot=True, with_trim=True, ghost=None):
    """returns (RGBA image TW x TW, canvas).  ghost: optional dict(rot=N) is handled by the caller."""
    cv = Canvas(TW, TW, S, seed=seed)
    page_disc(cv)
    construction(cv)
    wedges = []
    for w in f['wheel']:
        wedges.append((w, draw_wedge(cv, w)))
    for w, solid in wedges:
        draw_break_state(cv, w, solid)
    for w, solid in wedges:
        draw_icon(cv, w, solid)
    for w, solid in wedges:
        if w.get('brace'):
            draw_brace_plate(cv, w['sector'])
        if w.get('soak'):
            draw_soak_mark(cv, w['sector'])
    for w, solid in wedges:
        draw_pips(cv, w)
    doodles(cv)
    tape_strips(cv)
    draw_hp_ring(cv, f)
    draw_hub(cv, name)
    if with_trim:
        draw_trim(cv, f, skip_trim_units, hot)
    return cv.down(), cv


if __name__ == '__main__':
    import time
    sys.path.insert(0, '.')
    t = time.time()
    J = json.load(open('D:/rc_scratch/combat_redesign/locked/hover/state_e10.json'))
    key = sys.argv[1] if len(sys.argv) > 1 else 'f1'
    im, _ = render_tower(J[key])
    bg = Image.new('RGBA', im.size, (20, 18, 32, 255))
    bg.alpha_composite(im)
    bg.save('D:/rc_scratch/combat_redesign/locked/hover/out/tower_%s.png' % key)
    print(time.time() - t)
