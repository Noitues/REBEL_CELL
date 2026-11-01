# Option B: pixel / byte blocks in each ring cell's own colour fly out of the room, snap into ring cells.
from fxlib import *

F = (CELL_R - RCORE) / (RD - RCORE)          # 0 inner .. 1 outer
RING = ~CELL_CORE
# T5 timing per cell
S5 = 0.50 + 0.08 * F + 0.14 * CELL_RND
DUR5 = 0.32
# T6 timing per cell (outer first, whole disc incl. hub)
FF = np.clip((CELL_R) / RD, 0, 1)
S6 = 0.06 + 0.20 * (1 - FF) + 0.10 * CELL_RND
DUR6 = 0.36

def _blocks(img, d, x, y, size, col, alpha, trail=None):
    """draw ink-edged flat blocks (size in px) at snapped 2 px grid."""
    for i in range(len(x)):
        s = size[i]; a = int(255 * alpha[i])
        if a <= 8: continue
        bx = round(x[i] / 2) * 2; by = round(y[i] / 2) * 2
        h = s / 2
        if trail is not None:
            d.line([(trail[0][i], trail[1][i]), (bx, by)], fill=tuple(int(c) for c in col[i]) + (a // 3,), width=1)
        d.rectangle([bx - h - 1, by - h - 1, bx + h, by + h], fill=INK + (a,))
        d.rectangle([bx - h, by - h, bx + h - 1, by + h - 1], fill=tuple(int(c) for c in col[i]) + (a,))

def t5(t):
    if t >= 1.2: return P.copy()
    base = bg_at(dim_w(t))
    base = core_layer(base, t)
    # real ring pixels: salient cells appear when their block lands; bed cells fade in by radius
    arrive = S5 + DUR5
    ra = cl((t - (arrive - 0.03)) / 0.09)
    bed = cl((t - (0.60 + 0.30 * F)) / 0.10)
    bed = np.round(bed * 2) / 2                                  # stepped, blocky
    ca = np.where(CELL_SAL, ra, bed)
    ca = np.where(RING, ca, 0.0)
    a = pix_alpha_from_cells(ca) * RING_A
    base = over(base, P, a)
    # flying blocks
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    u = (t - S5) / DUR5
    sel = np.flatnonzero(RING & CELL_SAL & (u > 0) & (u < 1.0 + 0.30 / DUR5))
    if len(sel):
        p = eio(u[sel]); pp = eio(u[sel] - 0.045)
        x, y = bezier(SRC_X[sel], SRC_Y[sel], CELL_X[sel], CELL_Y[sel], SWIRL[sel], p)
        x0, y0 = bezier(SRC_X[sel], SRC_Y[sel], CELL_X[sel], CELL_Y[sel], SWIRL[sel], pp)
        size = 3 + 3 * p                                           # 3 px bits grow to the 6 px cell
        al = (1 - ra[sel]) * cl(u[sel] * 8)                          # block hands over to the real cell
        _blocks(img=None, d=d, x=x, y=y, size=size, col=CELL_COL[sel], alpha=al, trail=(x0, y0))
    base = over_rgba(base, ov)
    # 90 ms lock snap: a thin ink + cream keyline around the finished ring set
    k = float(cl(1 - abs(t - 1.00) / 0.045))
    if k > 0:
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        rr = RD + 2 + 5 * (1 - k)
        d.ellipse([CX - rr, CY - rr, CX + rr, CY + rr], outline=INK + (int(220 * k),), width=4)
        d.ellipse([CX - rr, CY - rr, CX + rr, CY + rr], outline=CREAM + (int(170 * k),), width=1)
        base = over_rgba(base, ov)
    return hud_in(base, t)

def t6(t):
    if t <= 0.0: return P.copy()
    base = bg_at(1 - float(smooth((t - 0.12) / 0.62)))
    u = (t - S6) / DUR6
    cellalpha = 1 - cl(u * DUR6 / 0.07)                              # real cell hands over to the block
    bedfade = 1 - np.round(cl(u * DUR6 / 0.12) * 2) / 2
    ca = np.where(CELL_SAL, cellalpha, bedfade)
    a = pix_alpha_from_cells(ca) * WHEEL_A
    base = over(base, P, a)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    sel = np.flatnonzero(CELL_SAL & (u > 0) & (u < 1.0))
    if len(sel):
        p = eic(u[sel]); pp = eic(u[sel] - 0.05)
        # run the flight backwards: target cell -> room source
        x, y = bezier(CELL_X[sel], CELL_Y[sel], SRC_X[sel], SRC_Y[sel], -SWIRL[sel], p)
        x0, y0 = bezier(CELL_X[sel], CELL_Y[sel], SRC_X[sel], SRC_Y[sel], -SWIRL[sel], pp)
        size = 6 - 3.5 * p
        al = 1 - cl((u[sel] - 0.82) / 0.18)
        _blocks(img=None, d=d, x=x, y=y, size=size, col=CELL_COL[sel], alpha=al, trail=(x0, y0))
    base = over_rgba(base, ov)
    return hud_out(base, t)
