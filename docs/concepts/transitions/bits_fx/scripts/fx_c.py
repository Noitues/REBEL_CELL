# Option C: scanline / cut-paper strip peel. The ring layer is cut into 6 px paper strips (printed flat, ink edge,
# paper shadow). Strips peel off the room's lab floor, slide out along a short arc, slot into the wheel.
from fxlib import *

SH = 10
NS = H // SH
r = np.random.RandomState(31)
J = np.arange(NS)
ORDER = (J * 0.6180339) % 1.0                      # golden shuffle so neighbours do not move together
S5 = 0.50 + 0.20 * ORDER
DUR5 = 0.34
DX0 = 470 + 90 * r.rand(NS)                         # strip start offset: toward the building at x ~ 745
WOB = np.where(J % 2 == 0, 1, -1) * (8 + 8 * r.rand(NS))
DIG = [''.join(r.choice(['0', '1'], 6)) for _ in range(NS)]
S6 = 0.08 + 0.26 * (J / NS) + 0.04 * r.rand(NS)
DUR6 = 0.34
_F = font(8)

def _post(rgb, lev=5):
    q = 255.0 / (lev - 1)
    return np.round(rgb / q) * q

def _strip_rgba(src_rgb, src_alpha, j, flat):
    y0, y1 = j * SH, (j + 1) * SH
    rgb = src_rgb[y0:y1].copy(); a = src_alpha[y0:y1].copy()
    if flat < 1:
        pr = _post(rgb); pr = pr * 0.97                       # flat cel print, a touch darker (paper in shadow)
        rgb = rgb + (pr - rgb) * (1 - flat)
    return rgb, a

def _compose_strips(base, t, alpha_src, rgb_src, states, ov_d):
    """states: dict j -> (dx, dy, vis, flat, shadow) ; paste shifted strips with ink edge + shadow."""
    for j in sorted(states, key=lambda k: states[k][1]):
        dx, dy, vis, flat, shad = states[j]
        if vis <= 0.01: continue
        rgb, a = _strip_rgba(rgb_src, alpha_src, j, flat)
        y0 = j * SH + int(round(dy)); dxi = int(round(dx))
        if y0 < 0 or y0 + SH > H: continue
        # shifted copy
        ra = np.zeros((SH, W), np.float32); rc = np.zeros((SH, W, 3), np.float32)
        if dxi >= 0: ra[:, dxi:] = a[:, :W - dxi]; rc[:, dxi:] = rgb[:, :W - dxi]
        else: ra[:, :W + dxi] = a[:, -dxi:]; rc[:, :W + dxi] = rgb[:, -dxi:]
        ra = ra * vis
        if shad > 0:                                           # paper drop shadow
            sh = np.zeros_like(ra); sh[:, 3:] = ra[:, :-3]
            ys = min(y0 + 3, H - SH)
            base[ys:ys + SH] = base[ys:ys + SH] * (1 - sh[..., None] * 0.45 * shad) + np.array(INK, np.float32) * sh[..., None] * 0.45 * shad
        base[y0:y0 + SH] = base[y0:y0 + SH] * (1 - ra[..., None]) + rc * ra[..., None]
        if flat < 0.98:                                        # ink cut edges, fade as the strip is printed in
            e = (1 - flat) * ra
            top = y0; bot = y0 + SH - 1
            for yy_ in (top,):
                base[yy_] = base[yy_] * (1 - e[0 if yy_ == top else SH - 1][:, None] * 0.7) + np.array(INK, np.float32) * e[0 if yy_ == top else SH - 1][:, None] * 0.7
    return base

def t5(t):
    if t >= 1.2: return P.copy()
    base = bg_at(dim_w(t))
    base = core_layer(base, t)
    states = {}
    u = (t - S5) / DUR5
    rowdig = []
    for j in range(NS):
        if u[j] <= 0: continue
        p = float(eoc(u[j]))
        dx = DX0[j] * (1 - p)
        dy = WOB[j] * math.sin(math.pi * p) * (1 - p) * 1.4
        vis = float(cl(u[j] * 4))
        flat = float(cl((u[j] - 0.82) / 0.18))               # printed flat while in transit, true pixels on landing
        shad = 1 - float(cl((u[j] - 0.8) / 0.2))
        states[j] = (dx, dy, vis, flat, shad)
        if u[j] < 1.05 and RING_A[j * SH:(j + 1) * SH].max() > 0:
            rowdig.append((j, dx, dy, u[j]))
    base = _compose_strips(base, t, RING_A, P, states, None)
    # trailing digits behind each moving strip (bits streaming off the strip's room-side end)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for (j, dx, dy, uj) in rowdig:
        if uj >= 1.0: continue
        cols = np.where(RING_A[j * SH:(j + 1) * SH].max(0) > 0.5)[0]
        if len(cols) == 0: continue
        xr = cols.max() + dx
        y = j * SH + SH / 2 + dy
        al = int(255 * float(cl(uj * 5)) * (1 - float(cl((uj - 0.7) / 0.3))))
        rowcol = P[j * SH:(j + 1) * SH][:, cols].reshape(-1, 3)
        sat = rowcol.max(1) - rowcol.min(1)
        c = rowcol[np.argsort(sat)[-1]]
        c = tuple(int(v) for v in np.clip(c * 1.25, 0, 255))
        for k in range(5):
            ch = DIG[j][k]
            d.text((xr + 8 + k * 9, y), ch, font=_F, fill=c + (int(al * (1 - k / 6)),), anchor='lm', stroke_width=1, stroke_fill=INK + (int(al * (1 - k / 6)),))
    base = over_rgba(base, ov)
    k = float(cl(1 - abs(t - 1.00) / 0.045))
    if k > 0:                                                    # lock: ink keyline snaps round the board
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        rr = RD + 2 + 5 * (1 - k)
        d.ellipse([CX - rr, CY - rr, CX + rr, CY + rr], outline=INK + (int(220 * k),), width=4)
        d.ellipse([CX - rr, CY - rr, CX + rr, CY + rr], outline=SCHED + (int(190 * k),), width=1)
        base = over_rgba(base, ov)
    return hud_in(base, t)

def t6(t):
    if t <= 0.0: return P.copy()
    base = bg_at(1 - float(smooth((t - 0.12) / 0.62)))
    states = {}
    u = (t - S6) / DUR6
    rowdig = []
    for j in range(NS):
        if u[j] < 0 or u[j] >= 1: 
            if u[j] < 0: states[j] = (0, 0, 1.0, 1.0, 0)
            continue
        p = float(eic(u[j]))
        dx = DX0[j] * p
        dy = WOB[j] * math.sin(math.pi * p) * 1.4
        vis = 1 - float(cl((u[j] - 0.75) / 0.25))
        flat = 1 - float(cl(u[j] * 5))
        states[j] = (dx, dy, vis, flat, float(cl(u[j] * 5)))
        rowdig.append((j, dx, dy, u[j]))
    # wheel strips (hub included): alpha from WHEEL_A
    base = _compose_strips(base, t, WHEEL_A, P, states, None)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for (j, dx, dy, uj) in rowdig:
        cols = np.where(WHEEL_A[j * SH:(j + 1) * SH].max(0) > 0.5)[0]
        if len(cols) == 0: continue
        xr = cols.max() + dx; y = j * SH + SH / 2 + dy
        al = int(255 * float(cl(uj * 6)) * (1 - float(cl((uj - 0.6) / 0.4))))
        rowcol = P[j * SH:(j + 1) * SH][:, cols].reshape(-1, 3); sat = rowcol.max(1) - rowcol.min(1)
        c = tuple(int(v) for v in np.clip(rowcol[np.argsort(sat)[-1]] * 1.25, 0, 255))
        for k in range(5):
            d.text((xr + 8 + k * 9, y), DIG[j][k], font=_F, fill=c + (int(al * (1 - k / 6)),), anchor='lm', stroke_width=1, stroke_fill=INK + (int(al * (1 - k / 6)),))
    base = over_rgba(base, ov)
    return hud_out(base, t)
