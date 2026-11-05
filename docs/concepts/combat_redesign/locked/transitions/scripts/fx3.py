"""fx3 (2026-11-04 rebuild): T5 room to combat and T6 combat to netrun, bits option A on the rebuilt board, rendered at 1920x1080.
T5: the room (as T4 left it) dims to the plate's grade; the spinner (its own generator layer) flies in; the enemy rings, the frame band
and the W4-W6 tickets are drawn out of the lab as bits, each ring behind a keyline head; the guns arm at the lock; the HUD, the cards
(each with a trail of its own bits) and SEND IT come in.  T6: the cards shed their bits, the keyline eats the frame band, rings +2, +1,
NOW and then the spinner (player-pink keyline), the bits draining round the rim into the lab; the room comes back as T4 left it.
Every bit is the colour of its source (fx3lib.sample on the generator layer it belongs to).
Round 2 (2026-11-04, call C13): the bit density over the dark city is lowered (far_keep below) so the worst 120 px tile flashes at most 2
times in any 1 s in T5 and T6."""
from fx3lib import *

PHI0 = -math.pi / 2 + 0.10          # sweep start just right of 12 o'clock (screen angle, y down)
# (r_lo, r_hi, path radius, T5 start, direction, glyph count, T6 start, source index, landing radii)
BANDS = [
    (0.0, R0, 242, 0.56, +1, 54, 0.22, 0, (222, 263)),
    (R0, R1, 300, 0.61, -1, 70, 0.16, 1, (279, 320)),
    (R1, R2, 356, 0.66, +1, 86, 0.10, 2, (336, 377)),
    (R2, RD + 4, 408, 0.71, -1, 96, 0.04, 3, (394, 494)),
]
CORE = (0.0, 224.0, 124, None, -1, 40, 0.26, 0, (40, 186))
DUR5 = 0.28; DUR6 = 0.26
T6_BITS_END = 0.70
BIT_A = float(os.environ.get("BIT_A", "0.85"))     # a bit in flight is drawn at 85 % (flash margin on the dark city tiles)
_u = np.linspace(0, 1, 401); _e = eio(_u)
def einv(e): return np.interp(e, _e, _u)

WHEEL_A = cl((RD + 2.0 - R) / 4.0)


def band_maps(bands):
    out = []
    for (lo, hi, rp, t0, dr, n, t6s, si, lr) in bands:
        m = ((R >= lo) & (R < hi)).astype(np.float32)
        delta = np.mod((TH - PHI0) * dr, TAU).astype(np.float32)
        out.append((m, delta))
    return out


BM5 = band_maps(BANDS)
BM6 = band_maps(BANDS + [CORE])

# ---- what a bit's colour is read from: the board as the generator draws it (no tower, no guns), the tower, the tickets, each card
BOARD = flat(['base', 'enemy1', 'enemy2', 'tickets', 'enemy3'])
TOWER = lay(BOARD, LY['tower'])
TICK = lay(BGD, LY['tickets'])
CARDS = [lay(BGD, LY['card%d' % i]) for i in range(NCARD)]


def flipc(ch, a, ph):
    if int((a + ph) // FLIP_S) % 2 == 0:
        return ch
    return ''.join('1' if c == '0' else '0' for c in ch)


def hot(col, a):
    k = float(smooth(a / WHITE_HOT_S))
    return tuple(HOT_WHITE[i] + (col[i] - HOT_WHITE[i]) * k for i in range(3))


def glyph_set(band, bi, seed, img, alpha=None, kind='ring'):
    lo, hi, rp, t0, dr, n, t6s, si, lr = band
    r = np.random.RandomState(seed + bi)
    alpha_s = (np.arange(n) + r.rand(n)) / n * TAU
    ang = PHI0 + dr * alpha_s
    rl = lr[0] + r.rand(n) * (lr[1] - lr[0])
    gx = CX + rl * np.cos(ang); gy = CY + rl * np.sin(ang)
    sx, sy = sources(n, seed * 3 + bi, si)
    rorb = R_ORBIT[0] + r.rand(n) * (R_ORBIT[1] - R_ORBIT[0])
    chars = r.choice(['0', '1', '0', '1', '10', '01'], n)
    ph = r.rand(n) * FLIP_S
    spin = (200 + r.rand(n) * 400) * np.where(r.rand(n) < 0.5, 1, -1)
    a0 = r.rand(n) * 360
    raw, col = zip(*[sample(img, gx[i], gy[i], alpha=alpha) for i in range(n)])
    routes = [make_route(sx[i], sy[i], gx[i], gy[i], rorb[i]) for i in range(n)]
    return dict(alpha=alpha_s, gx=gx, gy=gy, ch=chars, ph=ph, spin=spin, a0=a0, raw=list(raw), col=list(col), routes=routes, n=n,
                bc=band_colour(col), kind=kind, bi=bi)


G5 = [glyph_set(b, i, 11, BOARD) for i, b in enumerate(BANDS)]
G6 = [glyph_set(b, i, 23, BOARD) for i, b in enumerate(BANDS)] + [glyph_set(CORE, 4, 23, TOWER, alpha=LY['tower'][..., 3], kind='core')]

# ---- round 2 (C13, review N4 / question 6): the bit density over the dark city.  A bit whose route goes further than DARK_D0 round the
# rim from the lab (the far side of the wheel, where the rim runs over the dark city at the frame edge) is kept with a probability that falls
# linearly to DARK_KEEP at the far point (180 degrees).  Its own stream (seed 1000 + ...), so every kept bit is the same bit as before.
# Round-2 values (round2/transitions/out/fd_*.txt, fdiag.py): T5 keeps every bit to 90 degrees and 50 % at the far point (worst tile 3 -> 2);
# T6 keeps 45 % to 90 degrees and 25 % at the far point, because in T6 the board is eaten first and the whole wheel then sits over the dark
# city (60 / 30 % and 50 / 25 % still gave 3).  Env overrides are for the sweeps only.
DARK_KEEP = float(os.environ.get('DARK_KEEP', '0.5'))           # T5: kept share at the far point
DARK_NEAR = float(os.environ.get('DARK_NEAR', '1.0'))           # T5: kept share up to DARK_D0 round the rim
DARK_KEEP6 = float(os.environ.get('DARK_KEEP6', '0.25'))        # T6: the board dissolves over the city, so the whole wheel is over it
DARK_NEAR6 = float(os.environ.get('DARK_NEAR6', '0.45'))
DARK_D0 = float(os.environ.get('DARK_D0', '90'))


def far_keep(routes, seed, near=None, far=None):
    near = DARK_NEAR if near is None else near
    far = DARK_KEEP if far is None else far
    r = np.random.RandomState(1000 + seed)
    u = r.rand(len(routes))
    d = np.degrees(np.abs(np.array([g['d'] for g in routes], np.float64)))
    p = near - (near - far) * np.clip((d - DARK_D0) / max(180.0 - DARK_D0, 1e-6), 0, 1)
    return u < p


for _k, _G in enumerate(G5):
    _G['keep'] = far_keep(_G['routes'], 50 + _k)
for _k, _G in enumerate(G6):
    _G['keep'] = far_keep(_G['routes'], 60 + _k, DARK_NEAR6, DARK_KEEP6)

# ---- the W4-W6 tickets (outside the wheel, top left): their own short stream, landing as the frame band locks
_rt = np.random.RandomState(31)
NTK = 30
_ty, _tx = np.nonzero(LY['tickets'][..., 3] > 0.9 * 255)
_pick = _rt.choice(len(_tx), NTK, replace=False)
TK = dict(gx=_tx[_pick].astype(float), gy=_ty[_pick].astype(float), ch=_rt.choice(['0', '1', '10'], NTK), land=0.86 + _rt.rand(NTK) * 0.12,
          ph=_rt.rand(NTK) * FLIP_S, spin=(200 + _rt.rand(NTK) * 400) * np.where(_rt.rand(NTK) < 0.5, 1, -1), a0=_rt.rand(NTK) * 360)
TK['sx'], TK['sy'] = sources(NTK, 77, 3)
TK['raw'], TK['col'] = map(list, zip(*[sample(TICK, TK['gx'][i], TK['gy'][i], alpha=LY['tickets'][..., 3]) for i in range(NTK)]))
TK['routes'] = [make_route(TK['sx'][i], TK['sy'][i], TK['gx'][i], TK['gy'][i], R_ORBIT[0] + _rt.rand() * (R_ORBIT[1] - R_ORBIT[0])) for i in range(NTK)]
TK_T6 = 0.04 + _rt.rand(NTK) * 0.12
TK['keep'] = far_keep(TK['routes'], 77)
TK['keep6'] = far_keep(TK['routes'], 78, DARK_NEAR6, DARK_KEEP6)

# ---- the cards' own bits: start points on each card's opaque body, coloured from the card
CG = []
for i in range(NCARD):
    rr = np.random.RandomState(40 + i)
    al = LY['card%d' % i][..., 3]
    # a card's bits leave from its coloured body (band art, type plate, cost hex: C*ab >= 20), the parts that carry the card's colour
    chroma = np.hypot(*np.moveaxis(lab(CARDS[i])[..., 1:], -1, 0))
    ys, xs = np.nonzero((al > 0.97 * 255) & (chroma >= 20))
    pk = rr.choice(len(xs), 26, replace=False)
    pts = [(float(xs[k]), float(ys[k])) for k in pk]
    raw, col = zip(*[sample(CARDS[i], x, y, alpha=al) for x, y in pts])
    CG.append(dict(pts=pts, raw=list(raw), col=list(col), ch=rr.choice(['0', '1', '10'], 26), ph=rr.rand(26) * FLIP_S, st=rr.rand(26) * 0.8,
                   dx=(rr.rand(26) - 0.5) * 80, spin=(200 + rr.rand(26) * 400) * np.where(rr.rand(26) < 0.5, 1, -1), a0=rr.rand(26) * 360,
                   tx=(rr.rand(9) - 0.5) * 140, ty=rr.rand(9)))


def tumble(g, i, a, settle):
    return (g['a0'][i] + g['spin'][i] * a) * settle


# ---- the spinner sprite (tower layer): 1.35x -> 1.0, 4 % overshoot, 7 degree spin settle, 0.25-0.55 s
_tw_img = Image.fromarray(np.clip(LY['tower'] + 0.5, 0, 255).astype(np.uint8), 'RGBA')


def core_state(t):
    u = float(cl((t - 0.25) / 0.30))
    s = 1 + 0.35 * (1 - float(eoc(u)))
    s -= 0.04 * math.sin(math.pi * float(cl((u - 0.55) / 0.45)))     # the storyboard's 4 % overshoot (the O-25 code had 1.4 %)
    rot = 7.0 * (1 - float(eoc(u)))
    a = float(cl(u * 2.2))
    return s, rot, a


def core_layer(base, t):
    if t < 0.25:
        return base
    s, rot, a = core_state(t)
    B = 260
    c = _tw_img.crop((int(CX - B), int(CY - B), int(CX + B), int(CY + B)))
    n = int(2 * B * s)
    c = c.resize((n, n), Image.BICUBIC).rotate(rot, resample=Image.BICUBIC)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    L.paste(c, (int(round(CX - n / 2)), int(round(CY - n / 2))))
    arr = np.asarray(L).astype(np.float32)
    return over(base, arr[..., :3], arr[..., 3] / 255 * a)


# ---- the room
def dim_w(t):
    """T5: the room dims from the T4 room to the plate's grade while the board builds (storyboard: 'dims behind the board from K2 on')"""
    return float(smooth((t - 0.25) / 0.75))


def room5(t):
    w = dim_w(t)
    return K1ROOM + (BGD - K1ROOM) * w


def room6(t):
    return BGD + (K1ROOM - BGD) * float(smooth((t - 0.12) / 0.62))


# ---- T5
def t5(t, log=None):
    if t >= 1.2:
        return PLATE.copy()
    base = room5(t)
    u0 = float(eoc((t - 1.05) / 0.11))
    if u0 > 0:
        base = lay(base, shift(LY['scrim'], 0, -80 * (1 - u0)), u0)
    ra = np.zeros((H, W), np.float32)
    ov = Overlay()
    gl = float(smooth((t - 0.28) / 0.2))
    for bi, (band, (m, delta), G) in enumerate(zip(BANDS, BM5, G5)):
        lo, hi, rp, t0, dr, n, _, si, lr = band
        col = G['bc']
        e = float(eio((t - t0) / DUR5))
        head = (TAU + 0.9) * e
        ra = np.maximum(ra, m * cl((head - delta - 0.35) / 0.5))
        if t < t0 + DUR5 + 0.05:
            ga = gl * (1 - float(cl((t - (t0 + DUR5 - 0.05)) / 0.1)))
            if ga > 0.02:
                ov.keyline(rp, 0, TAU, 1, col, 6.0, 2.4, 120 / 255 * ga)
        if 0 < e < 1.0 + 1e-6 or (e >= 1 and t < t0 + DUR5 + 0.09):
            a1 = PHI0 + dr * head
            if head > 0.02:
                ov.keyline(rp, PHI0 + dr * max(head - 1.0, 0), min(head, 1.0), dr, col, 16, 6.4, 1.0)
            if e < 1:
                ov.dot(CX + rp * math.cos(a1), CY + rp * math.sin(a1), 6, col, 6)
        Tl = t0 + DUR5 * einv(np.clip(G['alpha'] / (TAU + 0.9), 0, 1))
        for i in range(n):
            if not G['keep'][i]:
                continue
            g = G['routes'][i]
            a = t - (Tl[i] - g['fl'])
            if a <= 0:
                continue
            p = a / g['fl']
            if p < 1:
                pe = float(eio(p))
                x, y = route_xy(g, pe)
                ov.glyph(x, y, flipc(G['ch'][i], a, G['ph'][i]), hot(G['col'][i], a), 16 + 12 * pe, BIT_A * float(cl(a / 0.03)),
                         tumble(G, i, a, 1 - pe), tag=('t5', bi, g['tht']))
            else:
                k = (t - Tl[i]) / 0.12
                if k < 1:
                    ov.glyph(G['gx'][i], G['gy'][i], flipc(G['ch'][i], a, G['ph'][i]), G['col'][i], 28 * (1 - k), 1 - k, 0, tag=('t5', bi, g['tht']))
    # the tickets' stream
    for i in range(NTK):
        if not TK['keep'][i]:
            continue
        g = TK['routes'][i]
        a = t - (TK['land'][i] - g['fl'])
        if a <= 0:
            continue
        p = a / g['fl']
        if p < 1:
            pe = float(eio(p))
            x, y = route_xy(g, pe)
            ov.glyph(x, y, flipc(TK['ch'][i], a, TK['ph'][i]), hot(TK['col'][i], a), 16 + 12 * pe, BIT_A * float(cl(a / 0.03)),
                     tumble(TK, i, a, 1 - pe), tag=('t5', 'tk', g['tht']))
        else:
            k = (t - TK['land'][i]) / 0.12
            if k < 1:
                ov.glyph(TK['gx'][i], TK['gy'][i], TK['ch'][i], TK['col'][i], 28 * (1 - k), 1 - k, 0, tag=('t5', 'tk', g['tht']))
    ra = ra * WHEEL_A + float(smooth((t - 0.95) / 0.10)) * (1 - WHEEL_A)
    base = lay(base, LY['base'], ra)
    base = core_layer(base, t)
    base = lay(base, LY['enemy1'], ra)
    base = lay(base, LY['guns'], float(smooth((t - 0.98) / 0.12)))      # the guns (player pink) arm at the lock
    base = lay(base, LY['enemy2'], ra)
    base = lay(base, LY['tickets'], ra)
    base = lay(base, LY['enemy3'], ra)
    base = ov.onto(base)
    k = float(cl(1 - abs(t - 1.00) / 0.045))
    kh = float(cl(1 - abs(t - 0.56) / 0.045))                           # the spinner settles: one 90 ms pink keyline snap round the halo
    if k > 0 or kh > 0:
        ov2 = Overlay()
        if k > 0:
            for G, band in zip(G5, BANDS):
                ov2.keyline(band[2] + 6 * (1 - k), 0, TAU, 1, G['bc'], 10, 4, 150 / 255 * k)
        if kh > 0:
            ov2.keyline(216 + 6 * (1 - kh), 0, TAU, 1, PINK, 10, 4, 150 / 255 * kh)
        base = ov2.onto(base)
    ov4 = Overlay()
    base = ui_in(base, t, ov4)
    base = ov4.onto(base)
    if log is not None:
        log.extend(ov.log + ov4.log)
    return base


def ui_in(base, t, ov):
    """1.05-1.20 s: HUD from the top, nameplate from the left, cards deal from the bottom (30 ms stagger) with a trail of their own bits, SEND IT last"""
    for gi, (names, dx, dy) in enumerate(HUD_GROUPS):
        u = float(eoc((t - 1.05 - 0.02 * gi) / 0.11))
        if u > 0:
            for k in names:
                base = lay(base, shift(LY[k], dx * (1 - u), dy * (1 - u)), u)
    for i in range(NCARD):
        u = float(eoc((t - (1.05 + 0.03 * i)) / 0.09))
        if u <= 0:
            continue
        base = lay(base, shift(LY['card%d' % i], 0, 180 * (1 - u)), float(cl(u * 1.6)))
        if u < 1:
            cx, cy, ang = card_box(i)
            cy += 180 * (1 - u)
            C_ = CG[i]
            a = t - (1.05 + 0.03 * i)            # ART_BIBLE 1.2 on the deal trail too: white-hot for 80 ms, then the card's colour, flipping
            for j in range(9):
                gx = cx + C_['tx'][j]
                gy = cy + 80 + C_['ty'][j] * 120 * (1 - u)
                ov.glyph(gx, gy, flipc(C_['ch'][j], a, C_['ph'][j]), hot(C_['col'][j], a), 24 + 6 * C_['ty'][j], (1 - u) * 0.95,
                         tumble(C_, j, t, 1 - u), tag=('card', i, None))
    names, dx, dy = SEND_GROUP
    u = float(eoc((t - 1.11) / 0.09))
    if u > 0:
        for k in names:
            base = lay(base, shift(LY[k], dx * (1 - u), dy * (1 - u)), u)
    return base


# ---- T6
def t6(t, log=None):
    if t <= 0.0:
        return PLATE.copy()
    base = room6(t)
    u0 = float(eic(t / 0.2))
    if u0 < 1:
        base = lay(base, shift(LY['scrim'], 0, -80 * 0.6 * u0), 1 - u0)
    allb = BANDS + [CORE]
    keep = np.ones((H, W), np.float32)
    keep_core = np.ones((H, W), np.float32)
    keep_tw = np.ones((H, W), np.float32)    # the tower layer: its drop shadow reaches past r 224, so it goes with the core sweep everywhere
    ov = Overlay()
    ova = Overlay()                       # keylines ride above the bits, so the pink spinner keyline is never hidden
    for bi, (band, (m, delta), G) in enumerate(zip(allb, BM6, G6)):
        lo, hi, rp, t0, dr, n, t6s, si, lr = band
        core = band is CORE
        dur = DUR6 if not core else 0.22
        e = float(eio((t - t6s) / dur))
        head = (TAU + 0.9) * e
        if core:
            keep_tw = (1 - cl((head - delta) / 0.5)).astype(np.float32)
            keep_core = np.where(m > 0, keep_tw, keep_core)
            keep = np.where(m > 0, np.minimum(keep, keep_core), keep)
        else:
            keep = np.where(m > 0, np.minimum(keep, 1 - cl((head - delta) / 0.5)), keep)
        if 0 < e < 1.0:
            a1 = PHI0 + dr * head
            st = PHI0 + dr * max(head - 0.9, 0)
            if core:
                ova.keyline(200, st, min(head, 0.9), dr, PINK, 18, 9, 1.0)
            else:
                ova.keyline(rp, st, min(head, 0.9), dr, G['bc'], 16, 6.4, 1.0)
        Tl = t6s + dur * einv(np.clip(G['alpha'] / (TAU + 0.9), 0, 1))
        for i in range(n):
            if not G['keep'][i]:
                continue
            g = G['routes'][i]
            fl = min(g['fl'] + 0.04, T6_BITS_END - Tl[i])      # every bit is home before the T4 iris closes
            a = t - Tl[i]
            p = a / fl
            if p <= 0 or p >= 1:
                continue
            pe = float(eic(p))
            x, y = route_xy(g, 1 - pe)
            ov.glyph(x, y, flipc(G['ch'][i], a, G['ph'][i]), hot(G['col'][i], a), 28 - 12 * pe, BIT_A * (1 - float(cl((p - 0.8) / 0.2))),
                     tumble(G, i, a, pe), tag=('t6', bi, g['tht']))
    for i in range(NTK):
        if not TK['keep6'][i]:
            continue
        g = TK['routes'][i]
        fl = g['fl'] + 0.04
        a = t - TK_T6[i]
        p = a / fl
        if p <= 0 or p >= 1:
            continue
        pe = float(eic(p))
        x, y = route_xy(g, 1 - pe)
        ov.glyph(x, y, flipc(TK['ch'][i], a, TK['ph'][i]), hot(TK['col'][i], a), 28 - 12 * pe, BIT_A * (1 - float(cl((p - 0.8) / 0.2))),
                 tumble(TK, i, a, pe), tag=('t6', 'tk', g['tht']))
    kt = np.where(R < 224, keep_core, keep)
    kt = kt * WHEEL_A + (1 - float(smooth((t - 0.03) / 0.12))) * (1 - WHEEL_A)
    base = lay(base, LY['base'], kt)
    base = lay(base, LY['tower'], keep_tw)
    base = lay(base, LY['enemy1'], kt)
    base = lay(base, LY['guns'], kt * float(1 - smooth(t / 0.12)))
    base = lay(base, LY['enemy2'], kt)
    base = lay(base, LY['tickets'], kt)
    base = lay(base, LY['enemy3'], kt)
    base = ov.onto(base)
    base = ova.onto(base)
    ov2 = Overlay()
    base = ui_out(base, t, ov2)
    base = ov2.onto(base)
    if log is not None:
        log.extend(ov.log + ov2.log)
    return base


def ui_out(base, t, ov):
    """T6 0-0.2 s: panels fade up and out; each card drops 80 px and fades while it sheds its own bits, which fall away"""
    for gi, (names, dx, dy) in enumerate(HUD_GROUPS + [SEND_GROUP]):
        u = float(eic((t - 0.02 * gi) / 0.2))
        if u < 1:
            for k in names:
                base = lay(base, shift(LY[k], dx * 0.6 * u, dy * 0.6 * u), 1 - u)
    for i in range(NCARD):
        u = (t - 0.02 * i) / 0.20
        if u < 1:
            e = float(eic(u))
            base = lay(base, shift(LY['card%d' % i], 0, 80 * e), 1 - e)
        if 0 < u < 1.8:
            C_ = CG[i]
            for j in range(26):
                v = (u - C_['st'][j]) / 0.8
                if v <= 0 or v >= 1:
                    continue
                sx, sy = C_['pts'][j]
                drop = 80 * float(eic(min(C_['st'][j], 1.0)))
                gx = sx + C_['dx'][j] * v
                gy = sy + drop + 280 * float(eic(v))
                a = v * 0.16
                ov.glyph(gx, gy, flipc(C_['ch'][j], a, C_['ph'][j]), hot(C_['col'][j], a), 30 - 8 * v, 1 - v, tumble(C_, j, a, 1.0), tag=('card', i, None))
    return base
