"""xf_tower: the XEROX FLYER tower (the player wheel).  The Cell photocopied its own board: a flyer pasted on the wall.
A = paper flyer: a dirty-white photocopy page, six flat magenta blocks slapped on off-register of a black key line, coarse black halftone shade,
    cyan misprint plate, registration marks, copier-lid shadow, black starburst hub.
B = black toner page: the same board photocopied on black: die-cut white sticker edge, white keylines, magenta blocks with white stencil highlights.
render_tower(f, name, skip_trim_units, hot, with_trim) -> (RGBA TW x TW at 1x, canvas).  Game data = the E10 sim frame, unchanged."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from xf_gfx import *
import xf_slices as XS
from f1_lib import pol, arc_pts
import f1_tower as FT
import f1_icons as FI

VAR = ['A']
TW = FT.TW
CT = FT.CT
R_PAGE = 192.0
R_HUB = 46.0
R_HP0, R_HP1 = 52.0, 64.0
R_IN, R_OUT = 71.0, 177.0
ICON_R, ICON_PX = 120.0, 48
PIP_R, PIP_W = 167.0, 8.0
WHITE_ = hx('FBFAF4')
WH_ = WHITE_


def rect_rot(cv, x0, y0, x1, y1, rot):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return poly(cv, [(cx + (x - cx) * c - (y - cy) * s_, cy + (x - cx) * s_ + (y - cy) * c) for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))])
PAGE_V = 0.80


def isB():
    return VAR[0] == 'B'


def keycol():
    """the keyline / ground ink and the contrast ink"""
    return (SHEET, TONER) if isB() else (TONER, SHEET)


_hf = {}


def hatch_cached(cv, angles, pitch, width, seed):
    k = (cv.W, angles, pitch, width, seed)
    if k not in _hf:
        _hf[k] = hatch_field(cv, angles, pitch, width, seed)
    return _hf[k]


def wedge(cv, s, r0=R_IN, r1=R_OUT, half=26.0, seed=0, amp=0.9):
    m = band_poly(cv, CT, r0, r1, 60 * s - half, 60 * s + half, 0.6)
    return rough(m, cv, amp, 11.0, seed + 3 * s)


# ------------------------------------------------------------------ page
def page(cv, seed):
    ss = cv.ss
    disc = circle(cv, CT[0], CT[1], R_PAGE)
    pg = rough(disc, cv, 2.2, 9.0, seed)
    # ragged paper fibre on the edge
    fibre = np.clip(blur(warp(disc, 1.6 * ss, 2.4 * ss, seed + 2), 0.4 * ss) * 1.05 - 0.02, 0, 1)
    if isB():
        edge = grow(pg, 5.0 * ss)
        edge = rough(np.maximum(edge, pg), cv, 1.2, 6.0, seed + 5)
        cv.paint(blur(shift(edge, 3.5 * ss, 5.0 * ss), 3.0 * ss) * 0.0, TONER)
        cv.paint(edge, WHITE_ * 0.86)                     # die-cut white sticker border
        cv.paint(np.clip(pg, 0, 1), TONER)
        n = vnoise(cv.H, cv.W, 28 * ss, seed + 1, 2)
        cv.paint(pg * np.clip((n - 0.55) * 1.4, 0, 1), hx('26222E'), 0.8)      # uneven toner density
        sp = toner_noise(cv, seed + 7, 1.0, 0.88)
        cv.paint(blur(sp, 0.3 * ss) * pg, WHITE_ * 0.8, 0.45)                  # dust on the black copy
        return pg, edge
    cv.paint(fibre, SHEET * PAGE_V * 0.94)
    n = vnoise(cv.H, cv.W, 40 * ss, seed + 1, 3)
    X, Y = cv.grid()
    rr = np.hypot(X - CT[0], Y - CT[1])
    shade = (0.93 + 0.07 * n) * (1 - 0.06 * np.clip((rr - 120) / 70, 0, 1))
    cv.paint(pg, SHEET[None, None, :] * PAGE_V * shade[..., None])
    sp = toner_noise(cv, seed + 7, 0.9, 0.86)
    cv.paint(blur(sp, 0.3 * ss) * pg, TONER, 0.32)
    cl = copier_edge(cv, pg, seed + 3, 7.0, 0.92, (0.75, 0.66))
    cv.paint(rough(cl, cv, 0.6, 3.0, seed + 8), TONER, 1.0)
    return pg, None


def reg_mark(cv, p, r=6.0, col=None):
    """a registration target: ring + cross, in black (A) or paper (B)"""
    col = col if col is not None else keycol()[0]
    ss = cv.ss
    ring = circle(cv, p[0], p[1], r) - circle(cv, p[0], p[1], r - 1.5)
    h = poly(cv, [(p[0] - r - 3, p[1] - 0.7), (p[0] + r + 3, p[1] - 0.7), (p[0] + r + 3, p[1] + 0.7), (p[0] - r - 3, p[1] + 0.7)])
    v = poly(cv, [(p[0] - 0.7, p[1] - r - 3), (p[0] + 0.7, p[1] - r - 3), (p[0] + 0.7, p[1] + r + 3), (p[0] - 0.7, p[1] + r + 3)])
    cv.paint(np.clip(ring + h + v, 0, 1), col)


def margin_marks(cv, seed):
    """punk marks and print marks on the page margin, in the gaps between slices (never on a slice, pip, HP block, ring cell or trim)"""
    k = keycol()[0]
    ss = cv.ss
    r = 184.5
    reg_mark(cv, pol(CT, r, 30), 4.4)
    reg_mark(cv, pol(CT, r, 210), 4.4)
    # lightning bolt at 150
    c = pol(CT, r, 150)
    bolt = [(c[0] + 2.5, c[1] - 8), (c[0] - 4.5, c[1] + 1), (c[0] - 0.3, c[1] + 1), (c[0] - 2.8, c[1] + 8.5), (c[0] + 4.8, c[1] - 2), (c[0] + 0.4, c[1] - 2)]
    bm = poly(cv, bolt)
    cv.paint(plate_shift(bm, cv, 1.8, 1.6), MAG, 0.95)
    ink(cv, bm, k, 0.02, seed + 11)
    # star at 90
    c = pol(CT, r, 90)
    pts = []
    for q in range(10):
        rr = 7.0 if q % 2 == 0 else 3.0
        a = math.pi / 5 * q - math.pi / 2
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    sm = poly(cv, pts)
    cv.paint(plate_shift(sm, cv, 1.8, 1.6), MAG, 0.95)
    ink(cv, sm, k, 0.02, seed + 12)
    # X at 270
    c = pol(CT, r, 270)
    xm = np.zeros((cv.H, cv.W), np.float32)
    for sg in (1, -1):
        xm = np.maximum(xm, poly(cv, [(c[0] - 6, c[1] - sg * 6 - 1.6), (c[0] - 6, c[1] - sg * 6 + 1.6), (c[0] + 6, c[1] + sg * 6 + 1.6), (c[0] + 6, c[1] + sg * 6 - 1.6)]))
    ink(cv, xm, k, 0.02, seed + 13)
    # zig-zag at 330
    pts = [pol(CT, r + (3.6 if i % 2 else -3.6), 322 + i * 3.8) for i in range(6)]
    zm = np.zeros((cv.H, cv.W), np.float32)
    for p0, p1 in zip(pts[:-1], pts[1:]):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy)
        nx, ny = -dy / L * 1.0, dx / L * 1.0
        zm = np.maximum(zm, poly(cv, [(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny), (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)]))
    ink(cv, zm, k, 0.02, seed + 14)


def cyan_fringe(cv, pg, seed):
    """the misprinted cyan plate: a coarse halftone ring on the page margin, shifted off the key"""
    ss = cv.ss
    X, Y = cv.grid()
    rr = np.hypot(X - CT[0], Y - CT[1])
    ring = np.clip((rr - 178.5) / 4.0, 0, 1) * np.clip((191.0 - rr) / 3.0, 0, 1)
    cov = ring * (0.18 + 0.5 * np.clip((rr - 178.5) / 12.0, 0, 1))
    ht = halftone(cov, 6.2 * ss, 15.0, 3, 5, aa=1.0 * ss)
    if isB():
        cv.paint(ht * (1 - 0.0), WHITE_ * 0.82, 0.9)
    else:
        mult(cv, ht * ring, CYN, 0.95)


# ------------------------------------------------------------------ hp blocks
def block_mask(cv, rc, w, a0, a1, bulge=0.0):
    m = band_poly(cv, CT, rc - w / 2 - bulge / 2, rc + w / 2 + bulge / 2, a0, a1, 0.5)
    return rough(m, cv, 0.35, 6.0, int(a0 * 7) & 255)


def draw_block(cv, rc, w, a0, a1, state, kw=1.5, cross=None, seed=0):
    ss = cv.ss
    pend = state in ('harm', 'soak', 'ours')
    m = block_mask(cv, rc, w, a0, a1, 2.0 if pend else 0.0)
    kcol, ccol = keycol()
    inkc = TONER
    ring = np.clip(grow(m, kw * ss) - m, 0, 1)
    if state == 'gone':
        cv.paint(grow(m, 0.9 * ss) - m * 0, hx('4A4652') if not isB() else hx('55505E'))
        cv.paint(m, hx('0E1016'))
        return m
    col = {'harm': HARMC, 'soak': SOAKC, 'ours': MAG}.get(state)
    if state == 'lit':
        cv.paint(ring, TONER if not isB() else TONER)
        cv.paint(m, GAINC)
        cv.paint(blur(np.clip(m - shift(m, 1.0 * ss, 1.2 * ss), 0, 1), 0.25 * ss) * m, WHITE_, 0.7)
        sh = np.clip(m - shift(m, -1.2 * ss, -1.4 * ss), 0, 1) * m
        cv.paint(sh, hx('2E8A3A'), 0.55)
    elif pend:
        cv.paint(ring, TONER)
        cv.paint(m, hx('120E16'))
        cr = (w >= 12) if cross is None else cross
        hf = hatch_cached(cv, (45, 135) if cr else (45,), 4.4 if cr else 3.8, 1.5 if cr else 1.5, 31)
        inner = shrink(m, 1.2 * ss)
        cv.paint(hf * inner, col)
        edge = np.clip(inner - shrink(inner, 1.2 * ss), 0, 1)
        cv.paint(edge, col)
        if state == 'soak':
            am = (a0 + a1) / 2
            x, y = pol(CT, rc + w / 2 + 1.0, am)
            x2, y2 = pol(CT, rc - w * 0.05, am)
            tg = (math.cos(math.radians(am)), math.sin(math.radians(am)))
            pts = [(x + tg[0] * 4.4, y + tg[1] * 4.4), (x2, y2), (x - tg[0] * 4.4, y - tg[1] * 4.4)]
            for p0, p1 in zip(pts[:-1], pts[1:]):
                dx, dy = p1[0] - p0[0], p1[1] - p0[1]
                L = math.hypot(dx, dy) + 1e-6
                nx, ny = -dy / L * 1.3, dx / L * 1.3
                cv.paint(poly(cv, [(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny), (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)]), TONER)
    elif state == 'mend':
        cv.paint(ring, TONER)
        cv.paint(m, hx('10201A'))
        cv.paint(np.clip(m - shrink(m, 1.2 * ss), 0, 1), GAINC)
        am = (a0 + a1) / 2
        x, y = pol(CT, rc, am)
        for (dx, dy) in ((3.6, 0.0), (0.0, 3.6)):
            cv.paint(poly(cv, [(x - dx - (0 if dx else 0.8), y - dy - (0.8 if dx else 0)), (x + dx + (0 if dx else 0.8), y + dy - (0.8 if dx else 0)), (x + dx + (0 if dx else 0.8), y + dy + (0.8 if dx else 0)), (x - dx - (0 if dx else 0.8), y - dy + (0.8 if dx else 0))]), GAINC)
    return m


def hp_states(hp, hp_after, mx):
    return FT.hp_states(hp, hp_after, mx)


def draw_hp_ring(cv, f):
    mx = f['maxhp']
    sts = hp_states(f['hp'], f['pv']['hp_after'], mx)
    rc, w = (R_HP0 + R_HP1) / 2, R_HP1 - R_HP0
    ngrp, per = 3, 5
    g2, g1 = 9.0, 2.6
    seg = (360 / ngrp - g2 - (per - 1) * g1) / per
    if not isB():
        for g in range(ngrp):
            a0 = g * 120 + g2 / 2 - 1.3
            a1 = a0 + 120 - g2 + 2.6
            bm = band_poly(cv, CT, rc - w / 2 - 2.8, rc + w / 2 + 2.8, a0, a1, 0.6)
            cv.paint(rough(bm, cv, 0.4, 7.0, 40 + g), TONER)
    for i, st in enumerate(sts):
        grp, j = divmod(i, per)
        a0 = grp * 120 + g2 / 2 + j * (seg + g1)
        draw_block(cv, rc, w, a0, a0 + seg, st)


def pip_states(w):
    return FT.pip_states(w)


def draw_pips(cv, w):
    s = w['sector']
    sts = pip_states(w)
    n = len(sts)
    bl, bg = 36.0, 6.0
    tot = n * bl + (n - 1) * bg
    cr = lambda px: math.degrees(px / PIP_R)
    a = 60 * s - cr(tot) / 2
    bm = band_poly(cv, CT, PIP_R - PIP_W / 2 - 2.8, PIP_R + PIP_W / 2 + 2.8, a - 1.0, a + cr(tot) + 1.0, 0.6)
    cv.paint(rough(bm, cv, 0.4, 7.0, 90 + s), TONER, 0.97)
    for i, st in enumerate(sts):
        a0 = a + cr(i * (bl + bg))
        draw_block(cv, PIP_R, PIP_W, a0, a0 + cr(bl), st, kw=1.3, cross=False)


# ------------------------------------------------------------------ slices
def draw_wedge(cv, w, seed):
    ss = cv.ss
    s = w['sector']
    am = 60 * s
    kcol, ccol = keycol()
    m = wedge(cv, s, seed=seed)
    # 1. the key plate: heavy black (A) / paper (B) outline + block drop toward the shadow side
    drop = extrude(grow(m, 1.8 * ss), 3.4 * ss, 4.2 * ss)
    kd = np.clip(drop - grow(m, 1.8 * ss) * 0, 0, 1)
    if isB():
        cv.paint(blur(shift(drop, 2 * ss, 3 * ss), 2.5 * ss) * 0.0, TONER)
        cv.paint(grow(m, 2.6 * ss), WHITE_ * 0.9)
        cv.paint(m, TONER)
    else:
        cv.paint(drop, TONER)
        cv.paint(grow(m, 2.5 * ss), TONER)
        cv.paint(m * 0 + 0, TONER)
    # 2. the magenta plate, slapped on 2.5 px off the key (a sliver of paper shows on one side, ink spills on the other)
    mg = plate_shift(m, cv, -2.4, -2.0) if not isB() else plate_shift(shrink(m, 0.4 * ss), cv, 1.2, 1.4)
    if isB():
        cv.paint(m, TONER)
    fillc, texc, texop = XS.palette(VAR[0], w['t'])
    ink(cv, mg, fillc, 0.07, seed + 21)
    mg_in = mg
    # 3. black halftone shade: coarse screen, heavier toward the hub end and the shadow side
    ic = pol(CT, ICON_R, am)
    X, Y = cv.grid()
    to_icon = np.hypot(X - ic[0], Y - ic[1])
    rr = np.hypot(X - CT[0], Y - CT[1])
    # per-type texture, tone-on-tone, cleared around the icon and kept off the key edge
    tx = XS.texture(XS.TEXKIND[w['t']], cv, am, CT)
    tx = tx * np.clip((to_icon - 28.0) / 8.0, 0, 1) * shrink(mg_in, 3.2 * ss)
    ink(cv, tx, texc, 0.0, seed + 22, texop)
    # 4. stencil highlight on the lit edge: the posterize cut-out (paper white) a sliver wide
    hl = np.clip(m - shift(m, 5.0 * ss, 5.4 * ss), 0, 1) * mg
    hl = hl * np.clip((to_icon - 29.0) / 8.0, 0, 1)
    cv.paint(rough(hl, cv, 0.5, 5.0, seed + 23), WHITE_ * (0.88 if not isB() else 0.8), 0.92)
    return m


def icon_masks(w, S):
    white, dark = FI.mask_for(w['t'], ICON_PX, S)
    return white, dark


def draw_icon(cv, w):
    ss = cv.ss
    am = 60 * w['sector']
    c = pol(CT, ICON_R, am)
    white, dark = icon_masks(w, ss)
    n = white.shape[0]
    x0, y0 = int(round(c[0] * ss - n / 2)), int(round(c[1] * ss - n / 2))
    wm = np.clip((ndi.gaussian_filter(white, 0.5 * ss * 0.5) - 0.45) * 6, 0, 1)
    wf = to_cv_array(cv, wm, x0, y0)
    df = to_cv_array(cv, np.clip(dark, 0, 1), x0, y0)
    full = np.clip(wf + df, 0, 1)
    kcol, ccol = keycol()
    # cyan misprint ghost, then the black key shadow, then the outline, then the white fill
    mult(cv, plate_shift(grow(full, 1.3 * ss), cv, -2.6, 2.2), CYN, 0.95 if not isB() else 0.0)
    cv.paint(extrude(grow(full, 1.6 * ss), 2.0 * ss, 2.2 * ss), TONER)
    cv.paint(grow(full, 1.8 * ss), TONER)
    if df.max() > 0:
        cv.paint(df, TONER)
        hf = hatch_cached(cv, (45,), 3.0, 0.8, 5)
        cv.paint(hf * df, SHEET, 0.5)
    cv.paint(wf, WHITE_)
    return full


def draw_break_state(cv, w, m, seed):
    ss = cv.ss
    hp, ha = w['hp'], w.get('hp_after', w['hp'])
    am = 60 * w['sector']
    if hp > 0 and ha == 0:
        col = SOAKC if w.get('soaked') else HARMC
        ix, iy = pol(CT, ICON_R, am)
        X, Y = cv.grid()
        clear = np.clip((np.hypot(X - ix, Y - iy) - 31.0) * ss * 0.5, 0, 1)
        reg = m * clear
        cv.paint(reg, TONER, XS.PAL[VAR[0]][w['t']].get('dim', 0.24))
        hf = hatch_cached(cv, (45, 135), 6.4, 1.6, 77)
        cv.paint(np.clip(grow(hf, 0.85 * ss), 0, 1) * reg, TONER, 0.92)       # black casing so the red reads on every slice ink
        cv.paint(hf * reg, col, 1.0)
        edge = np.clip(m - shrink(m, 2.4 * ss), 0, 1)
        cv.paint(edge, col)
        x, y = pol(CT, R_OUT - 22, am + 17)
        xm = np.zeros((cv.H, cv.W), np.float32)
        for sg in (1, -1):
            xm = np.maximum(xm, poly(cv, [(x - 7, y - sg * 7 - 2.4), (x - 7, y - sg * 7 + 2.4), (x + 7, y + sg * 7 + 2.4), (x + 7, y + sg * 7 - 2.4)]))
        cv.paint(grow(xm, 1.6 * ss), TONER)
        cv.paint(xm, col)
    elif hp == 0:
        cv.paint(m, hx('0A0A10'), 0.9)
    elif hp < w['mx'] and ha == hp:
        pts = [pol(CT, R_OUT - 6, am + 20), pol(CT, R_OUT - 14, am + 17), pol(CT, R_OUT - 19, am + 22), pol(CT, R_OUT - 27, am + 18.5), pol(CT, R_OUT - 33, am + 23.5)]
        zm = np.zeros((cv.H, cv.W), np.float32)
        for p0, p1 in zip(pts[:-1], pts[1:]):
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            L = math.hypot(dx, dy) + 1e-6
            nx, ny = -dy / L * 1.0, dx / L * 1.0
            zm = np.maximum(zm, poly(cv, [(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny), (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)]))
        cv.paint(grow(zm, 1.6 * ss), TONER)
        cv.paint(zm, WHITE_)


def draw_brace_plate(cv, s):
    """L10 double line: a pasted paper clamp strip on the page margin: two black rules, jaw ticks, two rivets, magenta tab"""
    ss = cv.ss
    am = 60 * s
    a0, a1 = am - 26.5, am + 26.5
    strip = rough(band_poly(cv, CT, 177.0, 191.0, a0, a1, 0.6), cv, 0.5, 8.0, 5 + s)
    cv.paint(extrude(grow(strip, 1.2 * ss), 2.0 * ss, 3.0 * ss), TONER)
    cv.paint(grow(strip, 1.4 * ss), TONER)
    cv.paint(strip, WHITE_ * 0.95)
    for rr in (181.4, 186.6):
        cv.paint(band_poly(cv, CT, rr - 1.2, rr + 1.2, a0 + 3.0, a1 - 3.0, 0.6), TONER)
    for sg in (-1, 1):
        cv.paint(band_poly(cv, CT, 176.5, 191.5, am + sg * 24.0 - 1.1, am + sg * 24.0 + 1.1, 0.6), TONER)
        x, y = pol(CT, 184.0, am + sg * 20.5)
        cv.paint(circle(cv, x, y, 1.9), TONER)
    tb = band_poly(cv, CT, 178.5, 189.5, am - 3.8, am + 3.8, 0.6)
    cv.paint(plate_shift(tb, cv, 1.3, 1.0), MAG)
    cv.paint(tb, TONER)


def draw_soak_mark(cv, s):
    am = 60 * s
    p = [pol(CT, R_IN + 20, am - 12), pol(CT, R_IN + 11, am), pol(CT, R_IN + 20, am + 12)]
    ss = cv.ss
    cm = np.zeros((cv.H, cv.W), np.float32)
    for p0, p1 in zip(p[:-1], p[1:]):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy) + 1e-6
        nx, ny = -dy / L * 2.6, dx / L * 2.6
        cm = np.maximum(cm, poly(cv, [(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny), (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)]))
    cv.paint(grow(cm, 1.8 * ss), TONER)
    cv.paint(cm, SOAKC)


# ------------------------------------------------------------------ hub
def draw_hub(cv, name='BREAKER', seed=0):
    ss = cv.ss
    c = CT
    kcol, ccol = keycol()
    pts = []
    n = 13
    r = np.random.default_rng(seed + 5)
    for k in range(n * 2):
        rr = (R_HUB - 0.8) if k % 2 == 0 else (R_HUB - 6.0)
        rr *= 1 + r.uniform(-0.03, 0.03)
        a = math.radians(k * 180.0 / n + 3)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    burst = poly(cv, pts)
    if isB():
        cv.paint(grow(burst, 2.4 * ss), WHITE_ * 0.92)
        cv.paint(burst, TONER)
        mg = plate_shift(burst, cv, 2.6, 2.4)
        ink(cv, mg, MAG, 0.04, seed + 2)
        disc = circle(cv, c[0], c[1], 37.5)
        disc = rough(disc, cv, 0.7, 6.0, seed + 3)
        cv.paint(grow(disc, 2.4 * ss), TONER)
        cv.paint(disc, WHITE_ * 0.94)
        tcol = TONER
    else:
        mg = plate_shift(burst, cv, 3.0, 2.6)
        ink(cv, mg, MAG, 0.04, seed + 2)
        cv.paint(grow(burst, 0.0), TONER, 0.0)
        disc = circle(cv, c[0], c[1], 40.0)
        disc = rough(disc, cv, 0.7, 6.0, seed + 3)
        cv.paint(grow(disc, 2.2 * ss), TONER)
        cv.paint(disc, TONER)
        # a 1-bit posterized highlight: paper-white crescent top left, then dots
        inner = circle(cv, c[0], c[1], 36.0)
        ringm = np.clip(inner - circle(cv, c[0], c[1], 34.6), 0, 1)
        cv.paint(ringm, WHITE_ * 0.9)
        tcol = WHITE_
    # lightning bolt (the Breaker)
    ex, ey = c[0], c[1] - 14.0
    bolt = [(ex + 2.5, ey - 9), (ex - 5.0, ey + 1.0), (ex - 0.5, ey + 1.0), (ex - 3.0, ey + 9.5), (ex + 5.5, ey - 2.0), (ex + 0.5, ey - 2.0)]
    bm = poly(cv, bolt)
    cv.paint(plate_shift(bm, cv, 1.6, 1.4), MAG)
    ink(cv, bm, tcol, 0.0, seed + 4)
    if name:
        # ransom-note tiles: every letter cut from a different scrap, tilted, dropped
        n_ = len(name)
        tw_ = 9.9 if not isB() else 9.5
        r2 = np.random.default_rng(seed + 31)
        if isB():
            cols = [(TONER, WH_), (MAG, TONER), (TONER, WH_), (CYN, TONER), (TONER, WH_), (MAG, TONER), (TONER, WH_)]
        else:
            cols = [(WH_, TONER), (MAG, TONER), (WH_, TONER), (CYN, TONER), (WH_, TONER), (MAG, TONER), (WH_, TONER)]
        for i, ch in enumerate(name):
            tx = c[0] + (i - (n_ - 1) / 2) * (tw_ + 0.5)
            ty = c[1] + 11.0 + r2.uniform(-1.3, 1.3)
            rot = r2.uniform(-6, 6)
            t = rect_rot(cv, tx - tw_ / 2, ty - 8.2, tx + tw_ / 2, ty + 8.2, rot)
            t = rough(t, cv, 0.25, 4.0, seed + 40 + i)
            cv.paint(shift(t, 1.2 * ss, 1.4 * ss), TONER if not isB() else TONER, 1.0)
            cv.paint(grow(t, 0.8 * ss), TONER if not isB() else WH_ * 0.9)
            ink(cv, t, cols[i % len(cols)][0], 0.02, seed + 50 + i)
            xtext(cv, ch, tx, ty + 0.4, 15.0, ANTON, fill=cols[i % len(cols)][1], rot=rot, wob=0.1, seed=seed + 60 + i, grain=0.0)


# ------------------------------------------------------------------ assembler
def render_tower(f, name='BREAKER', S=int(__import__('os').environ.get('XF_SS', '3')), seed=11, skip_trim_units=None, hot=True, with_trim=True, ghost=None):
    cv = Cv(0, 0, TW, TW, S)
    pg, edge = page(cv, seed)
    cyan_fringe(cv, pg, seed)
    wedges = []
    for w in f['wheel']:
        m = draw_wedge(cv, w, seed)
        wedges.append((w, m))
    for w, m in wedges:
        draw_break_state(cv, w, m, seed)
    for w, m in wedges:
        draw_icon(cv, w)
    for w, m in wedges:
        if w.get('brace'):
            draw_brace_plate(cv, w['sector'])
        if w.get('soak'):
            draw_soak_mark(cv, w['sector'])
    for w, m in wedges:
        draw_pips(cv, w)
    margin_marks(cv, seed)
    draw_hp_ring(cv, f)
    draw_hub(cv, name, seed)
    im = cv.to_image()
    if with_trim:
        tc = FT.Canvas(TW, TW, 3, seed=seed)
        FT.draw_trim(tc, f, skip_trim_units, hot)
        im.alpha_composite(tc.down())
    return im, cv


if __name__ == '__main__':
    import time, json, os
    t = time.time()
    import asm_r2 as A
    A.setup()
    VAR[0] = sys.argv[2] if len(sys.argv) > 2 else 'A'
    J = json.load(open('D:/rc_scratch/combat_redesign/locked/wheel/state_e10.json'))
    key = sys.argv[1] if len(sys.argv) > 1 else 'f1'
    im, _ = render_tower(J[key])
    bg = Image.new('RGBA', im.size, (24, 22, 36, 255))
    bg.alpha_composite(im)
    bg.save('D:/rc_scratch/combat_redesign/locked/wheel/out/tower_%s_%s.png' % (key, VAR[0]))
    bg.resize((bg.width * 2, bg.height * 2), Image.LANCZOS).save('D:/rc_scratch/combat_redesign/locked/wheel/out/tower_%s_%s_2x.png' % (key, VAR[0]))
    print(time.time() - t)
