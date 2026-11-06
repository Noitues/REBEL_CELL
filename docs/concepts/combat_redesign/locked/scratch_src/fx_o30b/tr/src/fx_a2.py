"""Option A (inked glyph bits + keylines riding the ring paths), recoloured for the final locked board.
T5: the spinner (tower layer) flies in; the three enemy rings and the frame band are drawn from the room by glyph streams
in the corp skin colours, each behind a keyline head; the guns (player pink) arm at the lock; HUD, WPAP cards (glyph trail in
the card type colour) and SEND IT slide in.  T6: the cards break into glyphs in their type colours, the keyline eats the
frame, rings 2, 1, 0 (corp colours) and then the spinner (player-pink keyline, glyphs in the slice spot inks)."""
from fx2lib import *

TAU = 2 * math.pi
PHI0 = -math.pi / 2 + 0.10          # sweep start just right of 12 o'clock (screen angle, y down)
RINGS = CORP_INK['rings']
ACC = CORP_INK['acc']
# (r_lo, r_hi, path radius, colour, T5 start, direction, glyph count, T6 start, source index)
BANDS = [
    (0.0, R0, 121, RINGS[0], 0.56, +1, 54, 0.22, 0),
    (R0, R1, 150, RINGS[1], 0.61, -1, 70, 0.16, 1),
    (R1, R2, 178, RINGS[2], 0.66, +1, 86, 0.10, 2),
    (R2, R3 + 2, 204, SILVER, 0.71, -1, 96, 0.04, 3),
]
CORE_BAND = (0.0, 112.0, 62, PINK, None, -1, 40, 0.26, 0)
DUR5 = 0.28; DUR6 = 0.26; FL5 = 0.24; FL6 = 0.26
_u = np.linspace(0, 1, 401); _e = eio(_u)
def einv(e): return np.interp(e, _e, _u)

def band_maps(bands):
    out = []
    for (lo, hi, rp, col, t0, dr, n, t6s, si) in bands:
        m = ((R >= lo) & (R < hi)).astype(np.float32)
        delta = np.mod((TH - PHI0) * dr, TAU)
        out.append((m, delta))
    return out
BM5 = band_maps(BANDS)
BM6 = band_maps(BANDS + [CORE_BAND])
WHEEL_A = cl((RD + 1.0 - R) / 2.0)

TW = LY['tower']
def spot_at(x, y):
    """the slice spot ink under a hub glyph (sampled from the tower layer), else player pink"""
    xi, yi = int(np.clip(x, 0, W - 1)), int(np.clip(y, 0, H - 1))
    c = TW[yi, xi, :3]
    best, bd = PINK, 1e9
    for k, s in SPOT.items():
        d = float(((c - np.array(s)) ** 2).sum())
        if d < bd: best, bd = s, d
    return best if bd < 9000 else PINK

def glyph_set(band, bi, seed):
    lo, hi, rp, col, t0, dr, n, t6s, si = band
    r = np.random.RandomState(seed + bi)
    alpha_s = (np.arange(n) + r.rand(n)) / n * TAU
    ang = PHI0 + dr * alpha_s
    gx = CX + rp * np.cos(ang); gy = CY + rp * np.sin(ang)
    sx, sy = sources(n, seed * 3 + bi, si)
    off = (r.rand(n) * 0.8 + 0.4) * 90 * np.where(r.rand(n) < 0.5, 1, -1)
    chars = r.choice(['0', '1', '0', '1', '10', '01'], n)          # a few 1-0 pair clusters for variety
    acc = r.rand(n) < 0.2
    cols = []
    for i in range(n):
        if band is CORE_BAND:
            cols.append(spot_at(gx[i], gy[i]))
        else:
            cols.append(ACC if acc[i] else col)
    return dict(alpha=alpha_s, gx=gx, gy=gy, sx=sx, sy=sy, off=off, ch=chars, col=cols, n=n)
G5 = [glyph_set(b, i, 11) for i, b in enumerate(BANDS)]
G6 = [glyph_set(b, i, 23) for i, b in enumerate(BANDS + [CORE_BAND])]

# the W4-W6 tickets (corp layer, top left, outside the wheel): their own short glyph stream, landing as the frame band locks
_rt = np.random.RandomState(31)
NTK = 30
TK = dict(gx=15 + _rt.rand(NTK) * 130, gy=13 + _rt.rand(NTK) * 30, off=(_rt.rand(NTK) * 0.8 + 0.4) * 90 * np.where(_rt.rand(NTK) < 0.5, 1, -1),
          ch=_rt.choice(['0', '1', '10'], NTK), land=0.86 + _rt.rand(NTK) * 0.12)
TK['sx'], TK['sy'] = sources(NTK, 77, 3)
TK['col'] = [ACC if _rt.rand() < 0.3 else RINGS[1] for _ in range(NTK)]
TK_T6 = 0.04 + _rt.rand(NTK) * 0.12

def ticket_glyphs5(d, t):
    for i in range(NTK):
        u = (t - (TK['land'][i] - FL5)) / FL5
        if u <= 0: continue
        if u < 1:
            p = float(eio(u))
            x, y = bezier(TK['sx'][i], TK['sy'][i], TK['gx'][i], TK['gy'][i], TK['off'][i], p)
            glyph(d, x, y, TK['ch'][i], TK['col'][i], 8 + 6 * p, float(cl(u * 6)))
        else:
            k = (t - TK['land'][i]) / 0.12
            if k < 1: glyph(d, TK['gx'][i], TK['gy'][i], TK['ch'][i], TK['col'][i], 14 * (1 - k), 1 - k)

def ticket_glyphs6(d, t):
    for i in range(NTK):
        u = (t - TK_T6[i]) / FL6
        if u <= 0 or u >= 1: continue
        p = float(eic(u))
        x, y = bezier(TK['gx'][i], TK['gy'][i], TK['sx'][i], TK['sy'][i], -TK['off'][i], p)
        glyph(d, x, y, TK['ch'][i], TK['col'][i], 14 - 7 * p, 1 - float(cl((u - 0.8) / 0.2)))

SS = 2
def arc(d, rp, a0, a1, col, wink, wcol, alpha=255):
    n = max(int(abs(a1 - a0) / 0.03), 2)
    ang = np.linspace(a0, a1, n)
    pts = [((CX + rp * math.cos(a)) * SS, (CY + rp * math.sin(a)) * SS) for a in ang]
    d.line(pts, fill=INK + (alpha,), width=int(wink * SS), joint='curve')
    d.line(pts, fill=tuple(int(c) for c in col) + (alpha,), width=max(1, int(wcol * SS)), joint='curve')

PAPER = (241, 234, 214)       # the WPAP card paper: the keyline of the dark card glyphs (cobalt, violet) so they read on the night room

def card_glyph(d, x, y, ch, col, size, alpha):
    glyph(d, x, y, ch, col, size, alpha, stroke=PAPER if sum(col) < 450 else INK)

def glyph(d, x, y, ch, col, size, alpha, stroke=INK):
    if size < 3 or alpha <= 0.03: return
    f = font(size * SS)
    d.text((x * SS, y * SS), ch, font=f, fill=tuple(int(c) for c in col) + (int(255 * alpha),), anchor='mm',
           stroke_width=max(2, int(size * SS * 0.18)), stroke_fill=tuple(stroke) + (int(255 * alpha),))

def ghost(d, rp, col, a):
    """destination hint: one solid hairline per path (no dashes: designer rule)"""
    if a <= 0.02: return
    arc(d, rp, 0, TAU, col, 3.0, 1.2, int(120 * a))

def canvas():
    ov = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
    return ov, ImageDraw.Draw(ov)

def finish(ov):
    return ov.resize((W, H), Image.LANCZOS)

# ---- the spinner sprite (tower layer): 1.35x -> 1.0, 4 % overshoot, 7 degree spin settle, 0.25-0.55 s
_tw_img = Image.fromarray(np.clip(TW, 0, 255).astype(np.uint8), 'RGBA')
def core_state(t):
    u = float(cl((t - 0.25) / 0.30))
    s = 1 + 0.35 * (1 - float(eoc(u)))
    s -= 0.014 * math.sin(math.pi * float(cl((u - 0.55) / 0.45)))
    rot = 7.0 * (1 - float(eoc(u)))
    a = float(cl(u * 2.2))
    return s, rot, a

def core_layer(base, t):
    if t < 0.25: return base
    s, rot, a = core_state(t)
    B = 130
    c = _tw_img.crop((int(CX - B), int(CY - B), int(CX + B), int(CY + B)))
    n = int(2 * B * s)
    c = c.resize((n, n), Image.BICUBIC).rotate(rot, resample=Image.BICUBIC)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    L.paste(c, (int(round(CX - n / 2)), int(round(CY - n / 2))))
    arr = np.asarray(L).astype(np.float32)
    return over(base, arr[..., :3], arr[..., 3] / 255 * a)

# ---- HUD / cards in and out
def group(base, names, dx, dy, u, fade):
    for k in names:
        L = shift(LY[k], dx, dy)
        base = lay(base, L, fade)
    return base

def ui_in(base, t, d=None):
    """1.05-1.20 s: top panels from the top, nameplate from the left, cards deal from the bottom (30 ms stagger), SEND IT last"""
    for gi, (names, dx, dy) in enumerate(HUD_GROUPS):
        u = float(eoc((t - 1.05 - 0.02 * gi) / 0.11))
        if u > 0: base = group(base, names, dx * (1 - u), dy * (1 - u), u, u)
    for i in range(NCARD):
        t0 = 1.05 + 0.03 * i
        u = float(eoc((t - t0) / 0.09))
        if u <= 0: continue
        base = group(base, ['card%d' % i], 0, 90 * (1 - u), u, float(cl(u * 1.6)))
        if d is not None and u < 1:          # glyph trail in the card's type colour (Trace violet sparks on a +Trace card)
            cx, cy, ang = card_box(i)
            cy += 90 * (1 - u)
            col = card_colour(i)
            rr = np.random.RandomState(40 + i)
            for j in range(9):
                gx = cx + (rr.rand() - 0.5) * 70
                gy = cy + 40 + rr.rand() * 60 * (1 - u)
                c = VIOLET if (META['hand'][i] in CARD_TRACE and j % 3 == 0) else col
                card_glyph(d, gx, gy, rr.choice(['0', '1']), c, 12 + 3 * rr.rand(), (1 - u) * 0.95)
    names, dx, dy = SEND_GROUP
    u = float(eoc((t - 1.11) / 0.09))
    if u > 0: base = group(base, names, dx * (1 - u), dy * (1 - u), u, u)
    return base

def ui_out(base, t, d=None):
    """T6 0-0.2 s: panels fade up and out; each card breaks into glyphs in its type colour that fall away"""
    for gi, (names, dx, dy) in enumerate(HUD_GROUPS + [SEND_GROUP]):
        u = float(eic((t - 0.02 * gi) / 0.2))
        if u < 1: base = group(base, names, dx * 0.6 * u, dy * 0.6 * u, u, 1 - u)
    for i in range(NCARD):
        t0 = 0.02 * i
        u = (t - t0) / 0.20                    # unclamped: the glyphs keep falling after the card is gone
        cx, cy, ang = card_box(i)
        if u < 1:
            # the card drops 40 px and fades (ease-in) while it sheds its glyphs; no pixel-block dissolve (that was option B's look)
            e = float(eic(u))
            base = group(base, ['card%d' % i], 0, 40 * e, e, 1 - e)
        if d is not None and 0 < u < 1.8:
            col = card_colour(i)
            rr = np.random.RandomState(90 + i)
            for j in range(26):
                st = rr.rand() * 0.8
                v = (u - st) / 0.8
                if v <= 0 or v >= 1: continue
                gx = cx + (rr.rand() - 0.5) * 150 + (rr.rand() - 0.5) * 40 * v
                gy = cy + (rr.rand() - 0.5) * 190 + 140 * eic(v)
                c = VIOLET if (META['hand'][i] in CARD_TRACE and j % 4 == 0) else col
                card_glyph(d, gx, gy, rr.choice(['0', '1', '10']), c, 15 - 4 * v, 1 - v)
    return base

def t5(t):
    if t >= 1.2: return PLATE.copy()
    base = bg_at(dim_w(t))
    ra = np.zeros((H, W), np.float32)
    ov, d = canvas()
    gl = float(smooth((t - 0.28) / 0.2))
    for bi, (band, (m, delta), G) in enumerate(zip(BANDS, BM5, G5)):
        lo, hi, rp, col, t0, dr, n, _, si = band
        e = float(eio((t - t0) / DUR5))
        head = (TAU + 0.9) * e
        ra = np.maximum(ra, m * cl((head - delta - 0.35) / 0.5))
        if t < t0 + DUR5 + 0.05: ghost(d, rp, col, gl * (1 - float(cl((t - (t0 + DUR5 - 0.05)) / 0.1))))
        if 0 < e < 1.0 + 1e-6 or (e >= 1 and t < t0 + DUR5 + 0.09):
            a1 = PHI0 + dr * head; a0 = PHI0 + dr * max(head - 1.0, 0)
            if head > 0.02: arc(d, rp, a0, a1, col, 8, 3.2)
            hx_, hy_ = CX + rp * math.cos(a1), CY + rp * math.sin(a1)
            if e < 1: d.ellipse([(hx_ - 6) * SS, (hy_ - 6) * SS, (hx_ + 6) * SS, (hy_ + 6) * SS], fill=tuple(col) + (255,), outline=INK + (255,), width=3 * SS)
        Tl = t0 + DUR5 * einv(np.clip(G['alpha'] / (TAU + 0.9), 0, 1))
        for i in range(n):
            u = (t - (Tl[i] - FL5)) / FL5
            if u <= 0: continue
            if u < 1:
                p = float(eio(u))
                x, y = bezier(G['sx'][i], G['sy'][i], G['gx'][i], G['gy'][i], G['off'][i], p)
                glyph(d, x, y, G['ch'][i], G['col'][i], 8 + 7 * p, float(cl(u * 6)))
            else:
                k = (t - Tl[i]) / 0.12
                if k < 1: glyph(d, G['gx'][i], G['gy'][i], G['ch'][i], G['col'][i], 15 * (1 - k), 1 - k)
    ticket_glyphs5(d, t)
    ra = ra * WHEEL_A + float(smooth((t - 0.95) / 0.10)) * (1 - WHEEL_A)
    base = lay(base, LY['base'], ra)
    base = core_layer(base, t)
    base = lay(base, LY['enemy1'], ra)
    base = lay(base, LY['guns'], float(smooth((t - 0.98) / 0.12)))      # the guns (player pink) arm at the lock
    base = lay(base, LY['enemy2'], ra)
    base = over_rgba(base, finish(ov))
    k = float(cl(1 - abs(t - 1.00) / 0.045))
    if k > 0:
        ov2, d2 = canvas()
        for (lo, hi, rp, col, *_r) in BANDS:
            arc(d2, rp + 3 * (1 - k), 0, TAU, col, 5, 2, int(150 * k))
        base = over_rgba(base, finish(ov2))
    kh = float(cl(1 - abs(t - 0.56) / 0.045))                           # the spinner settles: one 90 ms pink keyline snap round the halo
    if kh > 0:
        ov3, d3 = canvas()
        arc(d3, 108 + 3 * (1 - kh), 0, TAU, PINK, 5, 2, int(150 * kh))
        base = over_rgba(base, finish(ov3))
    ov4, d4 = canvas()
    base = ui_in(base, t, d4)
    return over_rgba(base, finish(ov4))

def t6(t):
    if t <= 0.0: return PLATE.copy()
    base = bg_at(1 - float(smooth((t - 0.12) / 0.62)))
    allb = BANDS + [CORE_BAND]
    keep = np.ones((H, W), np.float32)
    keep_core = np.ones((H, W), np.float32)
    ov, d = canvas()
    ova, da = canvas()                       # keylines ride above the glyphs, so the pink spinner keyline is never hidden
    for bi, (band, (m, delta), G) in enumerate(zip(allb, BM6, G6)):
        lo, hi, rp, col, t0, dr, n, t6s, si = band
        core = band is CORE_BAND
        dur = DUR6 if not core else 0.22
        e = float(eio((t - t6s) / dur))
        head = (TAU + 0.9) * e
        if core:
            keep_core = np.where(m > 0, 1 - cl((head - delta) / 0.5), keep_core)
            keep = np.where(m > 0, np.minimum(keep, keep_core), keep)
        else:
            keep = np.where(m > 0, np.minimum(keep, 1 - cl((head - delta) / 0.5)), keep)
        if 0 < e < 1.0:
            a1 = PHI0 + dr * head; a0 = PHI0 + dr * max(head - 0.9, 0)
            if core: arc(da, 100, a0, a1, col, 9, 4.5)
            else: arc(da, rp, a0, a1, col, 8, 3.2)
        Tl = t6s + dur * einv(np.clip(G['alpha'] / (TAU + 0.9), 0, 1))
        for i in range(n):
            u = (t - Tl[i]) / FL6
            if u <= 0 or u >= 1: continue
            p = float(eic(u))
            x, y = bezier(G['gx'][i], G['gy'][i], G['sx'][i], G['sy'][i], -G['off'][i], p)
            glyph(d, x, y, G['ch'][i], G['col'][i], 15 - 8 * p, 1 - float(cl((u - 0.8) / 0.2)))
    # the spinner: everything inside the halo goes with the pink keyline; ring 0's band (r < 135.5) holds the halo edge
    ticket_glyphs6(d, t)
    kt = np.where(R < 112, keep_core, keep)
    kt = kt * WHEEL_A + (1 - float(smooth((t - 0.03) / 0.12))) * (1 - WHEEL_A)
    base = lay(base, LY['base'], kt)
    base = lay(base, LY['tower'], keep_core)
    base = lay(base, LY['enemy1'], kt)
    base = lay(base, LY['guns'], kt * float(1 - smooth(t / 0.12)))
    base = lay(base, LY['enemy2'], kt)
    base = over_rgba(base, finish(ov))
    base = over_rgba(base, finish(ova))
    ov2, d2 = canvas()
    base = ui_out(base, t, d2)
    return over_rgba(base, finish(ov2))
