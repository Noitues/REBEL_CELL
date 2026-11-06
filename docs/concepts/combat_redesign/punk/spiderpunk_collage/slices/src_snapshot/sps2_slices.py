"""sps2_slices: ART CALL 52 slice pass 2.  Every slice TYPE gets its own colour AND texture (no colour is reserved).
BURST / SHIELD / TURRET / REPAIR.  Patches sp_tower.draw_wedge / draw_icon / draw_break_state / bolts."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from scipy import ndimage as ndi
import sp_tower as T
from sp_tower import *
import f1_icons as FI
import f1_tower as F1

TAPE = (238, 230, 204)
SPEC = {
    'A': {   # POSTER: purple page, white cut edges, bone shards
        'BURST':  dict(name='HOT MAGENTA', c0=(255, 45, 150), c1=(236, 22, 128), tex='dots',    tc=(160, 6, 92),    ta=0.88, edge=CUT, line=(120, 8, 70),  plate=YEL, ring=2.0, key=INK, wash=0.30),
        'SHIELD': dict(name='COBALT',      c0=(44, 92, 246),  c1=(28, 62, 212),  tex='scales',  tc=(10, 22, 120),   ta=0.90, edge=CUT, line=(8, 16, 100),  plate=YEL, ring=2.0, key=(14, 10, 56), wash=0.10),
        'TURRET': dict(name='PRINT YELLOW', c0=(255, 208, 0), c1=(255, 178, 0),  tex='rings',   tc=(176, 84, 0),    ta=0.90, edge=CUT, line=(130, 70, 0),  plate=MAG, ring=3.0, key=INK, wash=0.40),
        'REPAIR': dict(name='MINT GREEN',  c0=(70, 224, 130), c1=(34, 196, 104), tex='plus',    tc=(6, 96, 52),     ta=0.92, edge=CUT, line=(8, 84, 44),   plate=MAG, ring=2.8, key=INK, wash=0.35),
    },
    'B': {   # GIG FLYER: newsprint page, yellow cut edges, ink shards
        'BURST':  dict(name='TANGERINE',   c0=(255, 116, 24), c1=(240, 84, 8),   tex='dots',    tc=(150, 36, 0),    ta=0.88, edge=YEL, line=(110, 30, 0),  plate=COB, ring=2.4, key=INK, wash=0.42),
        'SHIELD': dict(name='AQUA',        c0=(8, 158, 184), c1=(0, 126, 158),  tex='scales',  tc=(2, 44, 80),     ta=0.90, edge=YEL, line=(4, 62, 90),   plate=MAG, ring=2.6, key=INK, wash=0.32),
        'TURRET': dict(name='ACID LIME',   c0=(172, 238, 20), c1=(138, 218, 8),  tex='rings',   tc=(52, 98, 0),     ta=0.90, edge=YEL, line=(48, 90, 0),   plate=COB, ring=3.0, key=INK, wash=0.40),
        'REPAIR': dict(name='VIOLET',      c0=(156, 88, 255), c1=(122, 58, 238), tex='plus',    tc=(250, 236, 255), ta=0.85, edge=YEL, line=(60, 18, 130), plate=YEL, ring=2.2, key=(14, 10, 56), wash=0.10),
    },
}
TEXNAME = {'dots': 'coarse staggered Ben-Day dots', 'scales': 'overlapping fish-scale plates', 'rings': 'concentric target rings', 'plus': 'bold plus crosses'}


def spec(w):
    return SPEC[T.V()][w['t']]


def local(cv, am):
    xx, yy = grids(cv)
    dx, dy = xx - CT[0], yy - CT[1]
    a = math.radians(am)
    return dx * math.sin(a) - dy * math.cos(a), dx * math.cos(a) + dy * math.sin(a)


def texture(cv, kind, am, t, ic):
    S = cv.S
    u, v = local(cv, am)
    cl = lambda x: np.clip(x * S + 0.5, 0, 1).astype(np.float32)
    if kind == 'dots':
        pitch = 6.6
        fu = ((u + 3.3) % pitch) - pitch / 2
        fv = ((v + 3.3 + (np.floor((u + 3.3) / pitch) % 2) * pitch / 2) % pitch) - pitch / 2
        return cl(1.5 + 1.5 * t - np.hypot(fu, fv))
    if kind == 'scales':
        p = 9.0
        out = np.zeros_like(u)
        rr = p * 0.5
        k0 = np.floor(u / (p / 2))
        for dk in (-1, 0, 1, 2):
            k = k0 + dk
            uc = k * (p / 2)
            vc = (np.floor(v / p - (k % 2) * 0.5) + 0.5 + (k % 2) * 0.5) * p
            du, dv = u - uc, v - vc
            d = np.hypot(du, dv)
            m = cl(1.0 + 0.5 * t - np.abs(d - rr)) * (du > -0.2)
            out = np.maximum(out, m)
        return out
    if kind == 'rings':
        xx, yy = grids(cv)
        r = np.hypot(xx - ic[0], yy - ic[1])
        ph = ((r - 31.0) % 9.0) - 4.5
        return cl(1.1 + 0.5 * t - np.abs(ph)) * (r > 31)
    if kind == 'plus':
        pitch = 9.0
        xx, yy = grids(cv)
        fu = ((xx + (np.floor(yy / pitch) % 2) * pitch / 2) % pitch) - pitch / 2
        fv = (yy % pitch) - pitch / 2
        arm, wd = 3.0, 0.95
        h = np.minimum(cl(arm - abs(fu)), cl(wd - abs(fv)))
        vv = np.minimum(cl(arm - abs(fv)), cl(wd - abs(fu)))
        return np.maximum(h, vv)
    raise ValueError(kind)


def draw_wedge(cv, w):
    S = cv.S
    s = w['sector']
    am = 60 * s
    sp = spec(w)
    m = solid(warp(cv.poly_mask(wedge_poly(s, s)), 0.35 * S, 22 * S, cv.r), S)
    ic = pol(CT, ICON_R, am)
    d = np.array(SHADOW_DIR, np.float32)
    t = linear_field(cv, (ic[0] - d[0] * 75, ic[1] - d[1] * 75), (ic[0] + d[0] * 75, ic[1] + d[1] * 75))
    n = smooth(cv.H, cv.W, 2.0 * S / 4, cv.r)
    c0, c1 = np.array(sp['c0'], np.float32), np.array(sp['c1'], np.float32)
    fill = c0 + (c1 - c0) * t[..., None] + n[..., None] * 2.2
    tx = texture(cv, sp['tex'], am, t, ic)
    xx, yy = grids(cv)
    clear = np.clip((np.hypot(xx - ic[0], yy - ic[1]) - 24) / 7, 0, 1)
    tx = tx * clear
    fill = fill * (1 - tx[..., None] * sp['ta']) + np.asarray(sp['tc'], np.float32) * tx[..., None] * sp['ta']
    dark = np.asarray(sp['c1'], np.float32) * 0.52
    ht = halftone(cv, np.clip((t - 0.45) * 1.4, 0, 1) * 0.8, 3.6, 45 + 9 * s)
    fill = fill * (1 - ht[..., None] * 0.5 * clear[..., None]) + dark * ht[..., None] * 0.5 * clear[..., None]
    cut_layer(cv, m, fill, edge=2.1 if T.V() == 'A' else 2.5, drop=(3.0, 4.2), edge_col=sp['edge'])
    sc = pol(CT, 160.0, am - 19.5)
    scrap_text(cv, (sc[0], sc[1], 18, 10), am - 19.5 + 90 - 8, tint=NEWS if T.V() == 'A' else (236, 230, 214), seed=s + 7)
    tp = pol(CT, 79.0, am + 18.5)
    tape(cv, tp, 18, 8, am + 18.5 + 90 + 20, col=TAPE, alpha=0.92)
    inner = ndi.binary_erosion(m > 0.5, iterations=max(1, int(1.6 * S))).astype(np.float32)
    ring = np.clip(ndi.gaussian_filter(outline_mask(inner, S, 0.9, inner=0.9), 0.3) * 1.5, 0, 1)
    cv.over(ring, sp['line'], 0.6)
    return m


def draw_icon(cv, w, sol):
    S = cv.S
    t = w['t']
    sp = spec(w)
    am = 60 * w['sector']
    c = pol(CT, ICON_R, am)
    white, dark = FI.mask_for(t, ICON_PX, S)
    n = white.shape[0]
    x0, y0 = int(c[0] * S - n / 2), int(c[1] * S - n / 2)
    wm = solidify(white, S)
    full = np.clip(wm + dark, 0, 1)
    rw = sp['ring']
    ring = np.clip(ndi.gaussian_filter(outline_mask(full, S, rw), 0.3 * S / 4 * 1.5) * 1.6, 0, 1)
    plate = np.roll(np.roll(dilate(full, rw, S), int(2.4 * S), 0), int(2.6 * S), 1)
    cv.over(np.clip(plate - np.clip(full + ring, 0, 1), 0, 1), sp['plate'], 0.97, x0, y0)
    cv.over(ring, INK, 0.99, x0, y0)
    if dark.max() > 0:
        cv.over(np.clip(dark, 0, 1), INK, 0.98, x0, y0)
        hatch_region(cv, np.clip(dark, 0, 1), x0, y0, (236, 232, 222), ang=45, pitch=3.0, w=0.8, alpha=0.5, over=0.0, jit=0.1)
    fm = np.roll(np.roll(wm, int(0.5 * S), 0), int(0.5 * S), 1)
    cv.over(np.clip(fm, 0, 1), WHITE, 0.99, x0, y0)
    return x0, y0, full


def draw_break_state(cv, w, solid_):
    """pending loss: same grammar (red cross-hatch + X), but the hatch carries a per-slice keyline (ink on light/hot slices, cream on dark ones) so it never melts into the slice"""
    sp = spec(w) if w['t'] in SPEC[T.V()] else None
    hp, ha = w['hp'], w.get('hp_after', w['hp'])
    if not (hp > 0 and ha == 0 and sp):
        return F1.draw_break_state(cv, w, solid_)
    S = cv.S
    am = 60 * w['sector']
    col = F1.SOAKC if w.get('soaked') else F1.HARMC
    ix, iy = pol(CT, ICON_R, am)
    clear = 1 - np.clip(cv.circle_mask((ix, iy), 31), 0, 1)
    reg = solid_ * clear
    cv.over(reg, (20, 8, 28), sp['wash'] * 0.55)
    y0, y1, x0, x1 = bbox(reg, 2)
    sub = reg[y0:y1, x0:x1]
    hatch_region(cv, sub, x0, y0, sp['key'], ang=45, pitch=6.0, w=3.0, alpha=0.92, over=0.0, jit=0.0, cross=True)
    hatch_region(cv, sub, x0, y0, col, ang=45, pitch=6.0, w=1.7, alpha=1.0, over=0.0, jit=0.0, cross=True)
    edge = np.clip(ndi.gaussian_filter(outline_mask(solid_, S, 2.2, inner=2.2), 0.4) * 1.5, 0, 1)
    edge_k = np.clip(ndi.gaussian_filter(outline_mask(solid_, S, 3.6, inner=3.6), 0.4) * 1.5, 0, 1)
    cv.over(edge_k, sp['key'], 0.95)
    cv.over(edge, col, 1.0)
    x, y = pol(CT, R_OUT - 22, am + 17)
    for sg in (1, -1):
        p = [(x - 7, y - sg * 7), (x + 7, y + sg * 7)]
        ballpoint(cv, p, INK, 7.6, 1.0, wob=0.3, wl=9, taper=(0, 0))
    for sg in (1, -1):
        p = [(x - 7, y - sg * 7), (x + 7, y + sg * 7)]
        marker(cv, p, col, w=4.6, alpha=1.0, wob=0.3, grain=0.05, taper=(0, 0))


T.draw_wedge = draw_wedge
T.draw_icon = draw_icon
T.draw_break_state = draw_break_state

_bolts0 = T.bolts


def _bolts(cv, m):
    """A: bone shards (yellow is now a slice colour).  B: ink shards."""
    if T.V() == 'B':
        old = T.COB
        T.COB = (26, 22, 36)
        try:
            return _bolts0(cv, m)
        finally:
            T.COB = old
    old = (T.YEL, T.YEL_D)
    T.YEL, T.YEL_D = (246, 240, 224), (170, 160, 140)
    try:
        return _bolts0(cv, m)
    finally:
        T.YEL, T.YEL_D = old


T.bolts = _bolts
