# Option A: cel-inked 0/1 glyph bits (ink-outlined) ride bezier streams into the ring paths; an ink keyline arc
# draws the path and the ring art is revealed behind its head. T6 runs the same machine as a keyline that eats the board.
from fxlib import *

TAU = 2 * math.pi
PHI0 = 0.12
# (r_lo, r_hi, path radius, colour, T5 start, direction, glyph count, T6 start)
BANDS = [
    (RCORE, 150, 122, CREAM, 0.56, +1, 60, 0.20),
    (150, 205, 178, LANE1, 0.62, -1, 90, 0.14),
    (205, 261, 250, HARM, 0.68, +1, 120, 0.08),
]
CORE_BAND = (0, RCORE, 50, CYAN, None, -1, 30, 0.26)
DUR5 = 0.30; DUR6 = 0.26; FL5 = 0.24; FL6 = 0.26
_u = np.linspace(0, 1, 401); _e = eio(_u)
def einv(e): return np.interp(e, _e, _u)

def band_maps(bands):
    out = []
    for (lo, hi, rp, col, t0, dr, n, t6s) in bands:
        m = (R >= lo) & (R < hi)
        delta = np.mod((TH - PHI0) * dr, TAU)
        out.append((m, delta))
    return out
BM5 = band_maps(BANDS)
BM6 = band_maps(BANDS + [CORE_BAND])

def glyph_set(band, bi, seed):
    lo, hi, rp, col, t0, dr, n, t6s = band
    r = np.random.RandomState(seed + bi)
    alpha_s = (np.arange(n) + r.rand(n)) / n * TAU                # swept angle each glyph lands at
    ang = PHI0 + dr * alpha_s
    gx = CX + rp * np.cos(ang); gy = CY + rp * np.sin(ang)
    sx, sy = sources(n, seed * 3 + bi)
    off = (r.rand(n) * 0.8 + 0.4) * 90 * np.where(r.rand(n) < 0.5, 1, -1)
    chars = r.choice(['0', '1'], n)
    acc = r.rand(n) < 0.2
    return dict(alpha=alpha_s, gx=gx, gy=gy, sx=sx, sy=sy, off=off, ch=chars, acc=acc, col=col, n=n)
G5 = [glyph_set(b, i, 11) for i, b in enumerate(BANDS)]
G6 = [glyph_set(b, i, 23) for i, b in enumerate(BANDS + [CORE_BAND])]

SS = 2
def arc(d, rp, a0, a1, col, wink, wcol, alpha=255):
    n = max(int(abs(a1 - a0) / 0.03), 2)
    ang = np.linspace(a0, a1, n)
    pts = [((CX + rp * math.cos(a)) * SS, (CY + rp * math.sin(a)) * SS) for a in ang]
    d.line(pts, fill=INK + (alpha,), width=int(wink * SS), joint='curve')
    d.line(pts, fill=tuple(col) + (alpha,), width=int(wcol * SS), joint='curve')
    for q in (pts[0], pts[-1]):
        pass

def glyph(d, x, y, ch, col, size, alpha):
    if size < 3 or alpha <= 0.03: return
    f = font(size * SS)
    d.text((x * SS, y * SS), ch, font=f, fill=tuple(int(c) for c in col) + (int(255 * alpha),), anchor='mm',
           stroke_width=max(2, int(size * SS * 0.18)), stroke_fill=INK + (int(255 * alpha),))

def ghost(d, rp, col, a):
    if a <= 0.02: return
    k = 48
    for i in range(k):
        a0 = TAU * i / k; a1 = a0 + TAU / k * 0.5
        arc(d, rp, a0, a1, col, 4.5, 1.6, int(150 * a))

def finish(ov):
    return ov.resize((W, H), Image.LANCZOS)

def t5(t):
    if t >= 1.2: return P.copy()
    base = bg_at(dim_w(t))
    base = core_layer(base, t)
    ra = np.zeros((H, W), np.float32)
    ov = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    gl = float(smooth((t - 0.28) / 0.2))
    for bi, (band, (m, delta), G) in enumerate(zip(BANDS, BM5, G5)):
        lo, hi, rp, col, t0, dr, n, _ = band
        e = float(eio((t - t0) / DUR5))
        head = (TAU + 0.9) * e
        ra = np.maximum(ra, m * cl((head - delta - 0.35) / 0.5))
        if t < t0 + DUR5 + 0.05: ghost(d, rp, col, gl * (1 - float(cl((t - (t0 + DUR5 - 0.05)) / 0.1))))
        if 0 < e < 1.0 + 1e-6 or (e >= 1 and t < t0 + DUR5 + 0.09):
            a1 = PHI0 + dr * head; a0 = PHI0 + dr * max(head - 1.0, 0)
            if head > 0.02: arc(d, rp, a0, a1, col, 8, 3.2)
            hx_, hy_ = CX + rp * math.cos(a1), CY + rp * math.sin(a1)
            if e < 1: d.ellipse([(hx_ - 6) * SS, (hy_ - 6) * SS, (hx_ + 6) * SS, (hy_ + 6) * SS], fill=tuple(col) + (255,), outline=INK + (255,), width=3 * SS)
        # glyph stream
        Tl = t0 + DUR5 * einv(np.clip(G['alpha'] / (TAU + 0.9), 0, 1))
        for i in range(n):
            u = (t - (Tl[i] - FL5)) / FL5
            if u <= 0: continue
            if u < 1:
                p = float(eio(u))
                x, y = bezier(G['sx'][i], G['sy'][i], G['gx'][i], G['gy'][i], G['off'][i], p)
                size = 8 + 7 * p
                glyph(d, x, y, G['ch'][i], SCHED if G['acc'][i] else col, size, float(cl(u * 6)))
            else:
                k = (t - Tl[i]) / 0.12
                if k < 1:
                    glyph(d, G['gx'][i], G['gy'][i], G['ch'][i], SCHED if G['acc'][i] else col, 15 * (1 - k), 1 - k)
    base = over(base, P, ra * RING_A)
    base = over_rgba(base, finish(ov))
    k = float(cl(1 - abs(t - 1.00) / 0.045))
    if k > 0:
        ov = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for (lo, hi, rp, col, *_r) in BANDS:
            arc(d, rp + 3 * (1 - k), 0, TAU, col, 5, 2, int(150 * k))
        base = over_rgba(base, finish(ov))
    return hud_in(base, t)

def t6(t):
    if t <= 0.0: return P.copy()
    base = bg_at(1 - float(smooth((t - 0.12) / 0.62)))
    allb = BANDS + [CORE_BAND]
    keep = np.ones((H, W), np.float32)
    ov = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for bi, (band, (m, delta), G) in enumerate(zip(allb, BM6, G6)):
        lo, hi, rp, col, t0, dr, n, t6s = band
        dur = DUR6 if bi < 3 else 0.22
        e = float(eio((t - t6s) / dur))
        head = (TAU + 0.9) * e
        keep = np.where(m, np.minimum(keep, 1 - cl((head - delta) / 0.5)), keep)
        if 0 < e < 1.0:
            a1 = PHI0 + dr * head; a0 = PHI0 + dr * max(head - 0.9, 0)
            arc(d, rp, a0, a1, col, 8, 3.2)
        Tl = t6s + dur * einv(np.clip(G['alpha'] / (TAU + 0.9), 0, 1))
        for i in range(n):
            u = (t - Tl[i]) / FL6
            if u <= 0 or u >= 1: continue
            p = float(eic(u))
            x, y = bezier(G['gx'][i], G['gy'][i], G['sx'][i], G['sy'][i], -G['off'][i], p)
            glyph(d, x, y, G['ch'][i], SCHED if G['acc'][i] else col, 15 - 8 * p, 1 - float(cl((u - 0.8) / 0.2)))
    base = over(base, P, keep * WHEEL_A)
    base = over_rgba(base, finish(ov))
    return hud_out(base, t)
