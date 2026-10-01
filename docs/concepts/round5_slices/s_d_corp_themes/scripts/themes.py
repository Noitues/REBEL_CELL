"""Corporation slice themes (texture + time-driven behaviour) and the neutral player theme.

Every tex_* function takes a slicelib.Ctx and returns (rgb, emis) float arrays (H, W, 3).
ctx.t in [0, 1) is the loop phase; all behaviours loop seamlessly at t = 1.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import slicelib as sl
from slicelib import hexrgb, smoothstep, frac, R_IN, R_OUT

# ----------------------------------------------------------------------------- shared helpers
_NOISE = {}


def noise_field(seed, cell):
    key = (seed, cell)
    if key not in _NOISE:
        rng = np.random.default_rng(seed * 7919 + cell)
        n = int(820 / cell) + 3
        small = rng.random((n, n)).astype(np.float32)
        img = Image.fromarray(small, "F").resize((n * cell, n * cell), Image.BICUBIC)
        _NOISE[key] = np.asarray(img, np.float32)[:820, :820]
    return _NOISE[key]


def sample(ctx, field):
    cols = np.clip((ctx.X + 410).astype(np.int32), 0, 819)
    rows = np.clip((410 - ctx.Y).astype(np.int32), 0, 819)
    return field[rows, cols]


def fbm(ctx, seed):
    return (0.5 * sample(ctx, noise_field(seed, 64)) + 0.3 * sample(ctx, noise_field(seed + 1, 22))
            + 0.2 * sample(ctx, noise_field(seed + 2, 7)))


def canvas(ctx):
    img = ctx.blank_L()
    return img, ImageDraw.Draw(img)


def arr(img):
    return np.asarray(img, np.float32) / 255.0


def zeros3(ctx):
    return np.zeros((ctx.H, ctx.W, 3), np.float32)


def put(rgb, mask, col, k=1.0):
    m = (mask * k)[..., None]
    return rgb * (1 - m) + np.asarray(col, np.float32) * m


def arc_s(ctx):
    """Arc length along the current radius (tangential coordinate)."""
    return ctx.r * ctx.th


def circuit_traces(ctx, seed, n=26, width=2, pad_r=4, region=(-390, 390, 120, 372)):
    """45-degree routed traces with pads (the MODEM-sign PCB language)."""
    rng = np.random.default_rng(seed)
    tr, dt = canvas(ctx)
    pd, dp = canvas(ctx)
    dirs = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    for _ in range(n):
        x = rng.uniform(region[0], region[1])
        y = rng.uniform(region[2], region[3])
        di = int(rng.integers(0, 8))
        pts = [(x, y)]
        for _s in range(int(rng.integers(2, 5))):
            L = rng.uniform(18, 60)
            dx, dy = dirs[di]
            k = L / math.hypot(dx, dy)
            x, y = x + dx * k, y + dy * k
            pts.append((x, y))
            di = (di + int(rng.choice([-1, 1]))) % 8
        dt.line([ctx.px(*p) for p in pts], fill=255, width=width, joint="curve")
        for p in (pts[0], pts[-1]):
            cx, cy = ctx.px(*p)
            dp.ellipse([cx - pad_r, cy - pad_r, cx + pad_r, cy + pad_r], outline=255, width=2)
    return arr(tr), arr(pd)


# ----------------------------------------------------------------------------- MERIDIAN FREIGHT
MERIDIAN = "#FF8C1A"


def tex_meridian(ctx):
    t = ctx.t
    P_CONV = 192.0
    scroll = t * P_CONV
    u = ctx.X + scroll                         # conveyor coordinate (tangential)
    n = fbm(ctx, ctx.seed % 5 + 11)
    paint_a = np.array([0.50, 0.22, 0.05], np.float32)
    paint_b = np.array([0.56, 0.26, 0.07], np.float32)
    rgb = paint_a + (paint_b - paint_a) * np.clip(n * 1.6 - 0.3, 0, 1)[..., None]
    # corrugation: trapezoid ridge profile (crest / slope / trough / slope), lit from the left
    p = frac(u / 24.0)
    up = smoothstep(0.00, 0.03, p) - smoothstep(0.13, 0.16, p)       # left-facing slope (lit)
    crest = smoothstep(0.13, 0.16, p) - smoothstep(0.47, 0.50, p)
    down = smoothstep(0.47, 0.50, p) - smoothstep(0.60, 0.63, p)     # right-facing slope (shadow)
    trough = 1 - up - crest - down
    shade = 1.28 * up + 1.0 * crest + 0.58 * down + 0.86 * trough
    rgb = rgb * shade[..., None]
    edge = np.exp(-((p - 0.145) / 0.012) ** 2)                        # crisp highlight on crest edge
    rgb = rgb + (edge * 0.16)[..., None] * np.array([1.0, 0.8, 0.6])
    # sparse rust and grime streaks (vertical drips)
    rust = smoothstep(0.76, 0.86, sample(ctx, noise_field(ctx.seed % 5 + 40, 18)))
    rgb = put(rgb, rust, (0.20, 0.07, 0.03), 0.6)
    drip = smoothstep(0.55, 0.9, sample(ctx, noise_field(45, 3)))     # fine speckle wear
    rgb = rgb * (1 - 0.18 * drip)[..., None]
    # rails (top/bottom of the container panel) with rivets
    for rr in (R_IN + 14, R_OUT - 22):
        band = np.exp(-((ctx.r - rr) / 3.2) ** 2)
        rgb = put(rgb, band, (0.12, 0.06, 0.03), 0.8)
        s = ctx.r * ctx.th + scroll
        riv = np.exp(-(((frac(s / 24.0) - 0.5) * 24) ** 2 + (ctx.r - rr) ** 2) / 3.0)
        rgb = rgb + (riv * 0.35)[..., None] * np.array([1.0, 0.7, 0.4])
    # stencilled cargo codes (scroll with the conveyor)
    st, ds = canvas(ctx)
    f1 = sl.mono(17)
    f2 = sl.mono(11)
    codes = ["MRDU 447102 3", "MRDU 880415 7", "MRDU 302961 1"]
    rng = np.random.default_rng(ctx.seed)
    for k in range(-4, 5):
        x = k * P_CONV - scroll
        code = codes[ctx.seed % 3]  # same on every conveyor period so the scroll loops
        ds.text(ctx.px(x - 70, 300 + 26), code, font=f1, fill=255)
        ds.text(ctx.px(x - 64, 214), "MAX GROSS 30480KG", font=f2, fill=255)
        ds.text(ctx.px(x - 64, 202), "TARE 2230KG  45G1", font=f2, fill=255)
    stm = arr(st)
    stm = stm * smoothstep(0.25, 0.55, sample(ctx, noise_field(77, 5)) + 0.25)   # worn stencil
    rgb = put(rgb, stm, (0.92, 0.88, 0.80), 0.45)
    # barcode label (a sticker riding the conveyor) on the inner band
    lab, dl = canvas(ctx)
    bars, db = canvas(ctx)
    for k in range(-4, 5):
        x0 = k * P_CONV - scroll - 50
        dl.rectangle([*ctx.px(x0, 190), *ctx.px(x0 + 100, 150)], fill=255)
        brng = np.random.default_rng(900 + ctx.seed % 3)
        bx = x0 + 6
        while bx < x0 + 94:
            w = float(brng.choice([1.5, 2.5, 3.5]))
            db.rectangle([*ctx.px(bx, 186), *ctx.px(bx + w, 160)], fill=255)
            bx += w + float(brng.choice([1.5, 2.5, 3.0]))
        db.text(ctx.px(x0 + 8, 159), "4 47102 88041", font=sl.mono(9, False), fill=255)
    labm = arr(lab)
    rgb = put(rgb, labm, (0.86, 0.82, 0.74), 0.95)
    rgb = put(rgb, arr(bars) * labm, (0.06, 0.05, 0.05), 1.0)
    # scan line sweeps the barcode band (fixed in the tile, not on the conveyor)
    emis = zeros3(ctx)
    hw = max(40.0, ctx.chord(170) / 2)
    sx = -hw + 2 * hw * frac(t * 2.0)
    beam = np.exp(-((ctx.X - sx) / 1.1) ** 2) * ((ctx.Y > 144) & (ctx.Y < 196))
    halo = np.exp(-((ctx.X - sx) / 4.0) ** 2) * ((ctx.Y > 140) & (ctx.Y < 200)) * 0.30
    halo = halo + np.exp(-((ctx.X - sx) / 1.5) ** 2) * 0.10                 # faint beam across the tile
    red = np.array([1.0, 0.25, 0.10], np.float32)
    rgb = rgb + red * (beam + halo)[..., None]
    emis = emis + red * (beam * 0.9 + halo)[..., None]
    return rgb, emis


# ----------------------------------------------------------------------------- SOLACE BIOSYSTEMS
SOLACE = "#3DFF8B"


def heartbeat(t):
    return float(math.exp(-((t - 0.10) / 0.035) ** 2) + 0.65 * math.exp(-((t - 0.25) / 0.04) ** 2))


def _cells(ctx, rich=False):
    rng = np.random.default_rng(4242 + ctx.seed % 3)
    N = 70
    rr = rng.uniform(R_IN + 14, R_OUT - 16, N)
    aa = rng.uniform(-0.62, 0.62, N)
    rad = rng.uniform(9, 19, N)
    ph = rng.uniform(0, 1, N)
    dirs = rng.uniform(0, math.pi, N)
    memb = np.zeros_like(ctx.r)
    fill = np.zeros_like(ctx.r)
    nuc = np.zeros_like(ctx.r)
    for i in range(N):
        cx, cy = rr[i] * math.sin(aa[i]), rr[i] * math.cos(aa[i])
        if cx < ctx.x0 - 40 or cx > ctx.x1 + 40 or cy < ctx.y0 - 40 or cy > ctx.y1 + 40:
            continue
        p = (ctx.t + ph[i]) % 1.0
        sep = 1.7 * rad[i] * float(smoothstep(0.15, 0.75, np.float32(p)))
        alpha = float(smoothstep(0.0, 0.08, np.float32(p)) * (1 - smoothstep(0.88, 1.0, np.float32(p))))
        dx, dy = math.cos(dirs[i]) * sep / 2, math.sin(dirs[i]) * sep / 2
        # local window for speed
        c0, r0 = ctx.px(cx, cy)
        R = int(rad[i] * 2.6 + 4)
        a0, a1 = max(0, int(r0) - R), min(ctx.H, int(r0) + R)
        b0, b1 = max(0, int(c0) - R), min(ctx.W, int(c0) + R)
        if a0 >= a1 or b0 >= b1:
            continue
        X = ctx.X[a0:a1, b0:b1]
        Y = ctx.Y[a0:a1, b0:b1]
        r2 = rad[i] ** 2
        d1 = (X - cx - dx) ** 2 + (Y - cy - dy) ** 2 + 1
        d2 = (X - cx + dx) ** 2 + (Y - cy + dy) ** 2 + 1
        f = 0.5 * (r2 / d1 + r2 / d2)
        memb[a0:a1, b0:b1] = np.maximum(memb[a0:a1, b0:b1], np.exp(-((f - 1) / 0.16) ** 2) * alpha)
        fill[a0:a1, b0:b1] = np.maximum(fill[a0:a1, b0:b1], smoothstep(0.9, 1.3, f) * alpha)
        nr = (rad[i] * 0.32) ** 2
        nuc[a0:a1, b0:b1] = np.maximum(nuc[a0:a1, b0:b1],
                                       (np.exp(-d1 / nr) + np.exp(-d2 / nr)) * alpha)
    return memb, fill, nuc


def tex_solace(ctx, rich=False):
    t = ctx.t
    hb = heartbeat(t)
    n = fbm(ctx, 21)
    k = smoothstep(R_IN, R_OUT, ctx.r)
    c0 = np.array([0.03, 0.13, 0.11], np.float32)
    c1 = np.array([0.09, 0.27, 0.22], np.float32)
    rgb = c0 + (c1 - c0) * k[..., None]
    rgb = rgb * (0.9 + 0.2 * n)[..., None]                                       # frosted glass
    # sterile glass streaks
    st = frac((ctx.X * 0.64 + ctx.Y * 0.77) / 110.0)
    rgb = rgb + (np.exp(-((st - 0.3) / 0.03) ** 2) * 0.07 + np.exp(-((st - 0.36) / 0.012) ** 2) * 0.05)[..., None]
    # microscope cells
    memb, fill, nuc = _cells(ctx)
    mint = hexrgb(SOLACE)
    rgb = put(rgb, fill, (0.12, 0.36, 0.28), 0.55)
    rgb = put(rgb, nuc, (0.05, 0.18, 0.20), 0.7)
    rgb = rgb + mint * (memb * (0.30 + 0.25 * hb))[..., None]
    emis = mint * (memb * 0.25 * hb)[..., None]
    # DNA helix etch on the outer band
    r0 = R_OUT - 28
    s = arc_s(ctx)
    ph = s / 13.0 + t * 2 * math.pi
    s1 = r0 + 7 * np.sin(ph)
    s2 = r0 - 7 * np.sin(ph)
    strands = np.exp(-((ctx.r - s1) / 1.1) ** 2) + np.exp(-((ctx.r - s2) / 1.1) ** 2) * 0.7
    rung = (np.abs(frac(s / 7.0) - 0.5) < 0.12) * (np.abs(ctx.r - r0) < 7 * np.abs(np.sin(ph)))
    helix = np.clip(strands + rung * 0.45, 0, 1)
    rgb = rgb + (helix * 0.28)[..., None] * np.array([0.75, 1.0, 0.88])
    # ECG trace on the inner band, flares with the beat
    r_e = R_IN + 26
    se = frac(s / 130.0)
    wave = (np.exp(-((se - 0.50) / 0.012) ** 2) * 13 - np.exp(-((se - 0.47) / 0.012) ** 2) * 5
            - np.exp(-((se - 0.535) / 0.015) ** 2) * 6 + np.exp(-((se - 0.72) / 0.05) ** 2) * 3.5)
    ecg = np.exp(-((ctx.r - (r_e + wave)) / 1.2) ** 2)
    rgb = rgb + mint * (ecg * (0.35 + 0.65 * hb))[..., None]
    emis = emis + mint * (ecg * (0.25 + 0.75 * hb))[..., None]
    # whole tile breathes with the pulse
    rgb = rgb * (1.0 + 0.10 * hb)
    if rich:
        emis = emis + mint * (helix * 0.2)[..., None]
    return rgb, emis


# ----------------------------------------------------------------------------- HALCYON CIVIC
HALCYON = "#8C7BFF"


def tex_halcyon(ctx, rich=False):
    t = ctx.t
    n = fbm(ctx, 31)
    base = np.array([0.055, 0.055, 0.19], np.float32)
    rgb = base * (0.85 + 0.3 * n)[..., None]
    rgb = rgb * (0.85 + 0.25 * smoothstep(R_IN, R_OUT, ctx.r))[..., None]
    pale = np.array([0.62, 0.60, 1.0], np.float32)
    vio = hexrgb(HALCYON)
    # blueprint grid (fine + major)
    gx = np.abs(frac(ctx.X / 12.0 + 0.5) - 0.5) * 12
    gy = np.abs(frac(ctx.Y / 12.0 + 0.5) - 0.5) * 12
    fine = np.maximum(np.exp(-(gx / 0.55) ** 2), np.exp(-(gy / 0.55) ** 2))
    Mx = np.abs(frac(ctx.X / 48.0 + 0.5) - 0.5) * 48
    My = np.abs(frac(ctx.Y / 48.0 + 0.5) - 0.5) * 48
    majx = np.exp(-(Mx / 0.8) ** 2)
    majy = np.exp(-(My / 0.8) ** 2)
    rgb = rgb + pale * (fine * 0.07 + np.maximum(majx, majy) * 0.16)[..., None]
    # concentric civic rings
    rings = np.exp(-((np.abs(frac((ctx.r - R_IN) / 30.0 + 0.5) - 0.5) * 30) / 0.7) ** 2)
    rings = rings * (ctx.r > R_IN + 20)
    rgb = rgb + vio * (rings * 0.22)[..., None]
    # municipal tiles (paving) in the inner band
    s = arc_s(ctx)
    tile_r = (ctx.r > R_IN + 10) & (ctx.r < R_IN + 46)
    row = np.floor((ctx.r - R_IN - 10) / 12.0)
    tu = frac(s / 15.0 + row * 0.5)
    tv = frac((ctx.r - R_IN - 10) / 12.0)
    tile = tile_r * (np.abs(tu - 0.5) < 0.40) * (np.abs(tv - 0.5) < 0.36)
    tilevar = sample(ctx, noise_field(33, 9))
    rgb = put(rgb, tile.astype(np.float32), (0.14, 0.14, 0.36), 0.55 + 0.3 * tilevar)
    # blueprint annotations
    an, da = canvas(ctx)
    f = sl.mono(10, False)
    rng = np.random.default_rng(ctx.seed)
    for k in range(-3, 4):
        x = k * 120 + 20
        da.text(ctx.px(x, 330), "SEC-%02d / H-CIV" % (abs(k) * 3 + 4), font=f, fill=255)
        da.line([ctx.px(x, 318), ctx.px(x + 70, 318)], fill=255, width=1)
        da.line([ctx.px(x, 314), ctx.px(x, 322)], fill=255, width=1)
        da.line([ctx.px(x + 70, 314), ctx.px(x + 70, 322)], fill=255, width=1)
    rgb = rgb + pale * (arr(an) * 0.30)[..., None]
    # behaviour: traffic / utility pulses flowing along the major grid and the rings
    P = 96.0
    fat_x = np.exp(-(Mx / 1.6) ** 2)
    fat_y = np.exp(-(My / 1.6) ** 2)
    flow_v = fat_x * np.exp(-((frac((ctx.Y - t * P) / P) - 0.5) / 0.08) ** 2)
    flow_h = fat_y * np.exp(-((frac((ctx.X + 23 - t * P) / P) - 0.5) / 0.08) ** 2)
    ring_s = frac((s - t * P * (1 if True else -1)) / P)
    flow_r = rings * np.exp(-((ring_s - 0.5) / 0.07) ** 2)
    flow = np.clip(flow_v + flow_h + flow_r, 0, 1.5)
    hot = np.array([0.80, 0.76, 1.0], np.float32)
    rgb = rgb + hot * (flow * 1.1)[..., None]
    emis = vio * (flow * 0.9)[..., None]
    if rich:
        # boss: second counter-flow layer + gilded halo rings
        flow2 = np.exp(-((np.abs(frac((ctx.r - R_IN) / 30.0 + 0.5) - 0.5) * 30) / 1.5) ** 2) * (ctx.r > R_IN + 20) * np.exp(-((frac((s + t * P * 2) / P) - 0.5) / 0.06) ** 2)
        gold = np.array([1.0, 0.82, 0.45], np.float32)
        rgb = rgb + gold * (flow2 * 0.7 + rings * 0.10)[..., None]
        emis = emis + gold * (flow2 * 0.7)[..., None]
        halo = np.exp(-((ctx.r - (R_OUT - 34)) / 1.3) ** 2)
        rgb = rgb + gold * (halo * 0.45)[..., None]
        emis = emis + gold * (halo * 0.35)[..., None]
    return rgb, emis


# ----------------------------------------------------------------------------- ORBITAL COMMONS
ORBITAL = "#7FA8FF"


def _orbit_pts(cx, cy, a, b, rot, n=180, phi0=0.0, phi1=2 * math.pi):
    pts = []
    cr, sr = math.cos(rot), math.sin(rot)
    for i in range(n + 1):
        ph = phi0 + (phi1 - phi0) * i / n
        x, y = a * math.cos(ph), b * math.sin(ph)
        pts.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return pts


def tex_orbital(ctx, rich=False):
    t = ctx.t
    ice = hexrgb(ORBITAL)
    neb = sample(ctx, noise_field(51, 80))
    rgb = np.array([0.012, 0.022, 0.055], np.float32) + (neb * 0.06)[..., None] * np.array([0.35, 0.5, 1.0])
    # stars
    rng = np.random.default_rng(5150)
    stars, dst = canvas(ctx)
    big, dbg = canvas(ctx)
    for i in range(420):
        x, y = rng.uniform(-400, 400), rng.uniform(-60, 400)
        b = int(rng.uniform(60, 255))
        cx, cy = ctx.px(x, y)
        if not (-4 < cx < ctx.W + 4 and -4 < cy < ctx.H + 4):
            continue
        rad = 0.6 if b < 200 else 1.2
        dst.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=b)
        if b > 240:
            dbg.line([(cx - 5, cy), (cx + 5, cy)], fill=180)
            dbg.line([(cx, cy - 5), (cx, cy + 5)], fill=180)
    sa = arr(stars) + arr(big) * 0.6
    rgb = rgb + (sa[..., None] * np.array([0.85, 0.92, 1.0]))
    # star-map graticule: dashed rings and spokes
    s = arc_s(ctx)
    grat = (np.exp(-((np.abs(frac((ctx.r - R_IN) / 40.0 + 0.5) - 0.5) * 40) / 0.6) ** 2) * (frac(s / 8.0) < 0.5))
    rgb = rgb + ice * (grat * 0.12)[..., None]
    # constellation lines
    con, dc = canvas(ctx)
    crng = np.random.default_rng(77 + ctx.seed % 4)
    for _c in range(3):
        x, y = crng.uniform(-200, 200), crng.uniform(170, 320)
        pts = [(x, y)]
        for _k in range(3):
            x += crng.uniform(-45, 45)
            y += crng.uniform(-30, 30)
            pts.append((x, y))
        dc.line([ctx.px(*p) for p in pts], fill=110, width=1)
        for p in pts:
            cx, cy = ctx.px(*p)
            dc.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=255)
    rgb = rgb + ice * (arr(con) * 0.45)[..., None]
    # orbit lines
    orb, do = canvas(ctx)
    O1 = (0, 255, 300, 70, math.radians(-14))
    O2 = (30, 220, 260, 120, math.radians(22))
    for O in (O1, O2):
        do.line([ctx.px(*p) for p in _orbit_pts(*O)], fill=255, width=1)
    orbm = arr(orb)
    rgb = rgb + ice * (orbm * 0.45)[..., None]
    # solar-panel cells on the inner band
    pr = (ctx.r > R_IN + 10) & (ctx.r < R_IN + 46)
    cu = frac(s / 13.0)
    cv = frac((ctx.r - R_IN - 10) / 12.0)
    cell = pr * (np.abs(cu - 0.5) < 0.42) * (np.abs(cv - 0.5) < 0.40)
    frame = pr & ~cell.astype(bool)
    rgb = put(rgb, frame.astype(np.float32), (0.42, 0.46, 0.55), 0.85)
    cellcol = np.array([0.05, 0.11, 0.32], np.float32) + np.array([0.04, 0.06, 0.12]) * (cu * cv)[..., None]
    rgb = rgb * (1 - cell[..., None]) + cellcol * cell[..., None]
    # behaviour 1: panels glint (a diagonal band sweeping once per loop)
    gpos = -200 + 700 * t                      # off-tile at both ends of the loop
    gl = np.exp(-(((ctx.X * 0.8 + ctx.Y * 0.6) - gpos) / 10.0) ** 2) * cell
    rgb = rgb + (gl * 0.9)[..., None] * np.array([0.85, 0.92, 1.0])
    emis = ice * (gl * 0.8)[..., None]
    # behaviour 2: a satellite crosses along orbit 1
    sat, dsat = canvas(ctx)
    trail, dtr = canvas(ctx)
    cx0, cy0, a, b, rot = O1
    ph = math.pi * (0.92 - 0.84 * t)           # right to left over the top of the ellipse
    P = _orbit_pts(cx0, cy0, a, b, rot, 1, ph, ph)[0]
    P2 = _orbit_pts(cx0, cy0, a, b, rot, 1, ph - 0.02, ph - 0.02)[0]
    ang = math.atan2(P[1] - P2[1], P[0] - P2[0])
    tr = _orbit_pts(cx0, cy0, a, b, rot, 30, ph, ph + 0.35)
    dtr.line([ctx.px(*p) for p in tr], fill=255, width=2)
    def R(dx, dy):
        return ctx.px(P[0] + dx * math.cos(ang) - dy * math.sin(ang), P[1] + dx * math.sin(ang) + dy * math.cos(ang))
    dsat.polygon([R(-4, -4), R(4, -4), R(4, 4), R(-4, 4)], fill=255)
    for sgn in (-1, 1):
        dsat.polygon([R(-3, sgn * 6), R(3, sgn * 6), R(3, sgn * 18), R(-3, sgn * 18)], fill=200)
    tm = arr(trail)
    tm = tm * (1 - smoothstep(0, 1, np.float32(0)))
    rgb = rgb + ice * (tm * 0.35)[..., None]
    sm = arr(sat)
    rgb = put(rgb, sm, (0.92, 0.95, 1.0), 1.0)
    emis = emis + ice * (sm * 0.9 + tm * 0.3)[..., None]
    if rich:
        emis = emis + ice * (orbm * 0.3)[..., None]
    return rgb, emis


# ----------------------------------------------------------------------------- REBEL_CELL / DISPATCH
REBEL = "#E8141E"
PLAYER_FRINGES = ["#FF3DA8", "#5CE1FF", "#7BE07B", "#C85AFF"]


def _inv_hex(d, cx, cy, R, width):
    pts = [(cx + R * math.cos(math.pi / 3 * i + math.pi / 2), cy + R * math.sin(math.pi / 3 * i + math.pi / 2)) for i in range(6)]
    d.polygon(pts, outline=255, width=width)
    return pts


def tear_rows(a, rng, strength):
    """Horizontal tear: shift bands of rows by random offsets."""
    H = a.shape[0]
    out = a.copy()
    nb = int(rng.integers(3, 7) * strength) + 1
    for _ in range(nb):
        y0 = int(rng.integers(0, H))
        h = int(rng.integers(3, 26))
        off = int(rng.integers(8, 46) * strength) * int(rng.choice([-1, 1]))
        out[y0:y0 + h] = np.roll(a[y0:y0 + h], off, axis=1)
    return out


def tex_rebel(ctx, rich=False):
    t = ctx.t
    red = hexrgb(REBEL)
    n = fbm(ctx, 61)
    rgb = np.array([0.075, 0.006, 0.016], np.float32) * (0.7 + 0.6 * n)[..., None]
    rgb = rgb * (0.85 + 0.35 * smoothstep(R_IN, R_OUT, ctx.r))[..., None]
    # corrupted player circuit board (borrowed from the Cell's own PCB language)
    tr, pads = circuit_traces(ctx, 600 + ctx.seed % 4, n=30)
    corrupt = smoothstep(0.35, 0.55, sample(ctx, noise_field(62, 10)))       # broken segments
    trm = np.clip(tr + pads, 0, 1) * corrupt
    rgb = rgb + red * (trm * 0.55)[..., None]
    # chromatic fringe in the player's colours: the same traces, displaced
    frng = np.random.default_rng(ctx.seed)
    col = hexrgb(PLAYER_FRINGES[int(frng.integers(0, 4))])
    shifted = np.roll(trm, 3, axis=1)
    rgb = rgb + col * (np.clip(shifted - trm, 0, 1) * 0.35)[..., None]
    rgb = rgb + hexrgb("#5CE1FF") * (np.clip(np.roll(trm, -3, axis=1) - trm, 0, 1) * 0.22)[..., None]
    # dead-pixel blocks in player colours
    bl, db = canvas(ctx)
    blocks = []
    brng = np.random.default_rng(700 + ctx.seed % 5)
    for i in range(26):
        x, y = brng.uniform(-380, 380), brng.uniform(130, 370)
        w, h = brng.uniform(4, 18), brng.uniform(3, 8)
        blocks.append((x, y, w, h, PLAYER_FRINGES[i % 4]))
    for (x, y, w, h, c) in blocks:
        img, d = canvas(ctx)
        d.rectangle([*ctx.px(x, y), *ctx.px(x + w, y - h)], fill=255)
        rgb = put(rgb, arr(img), hexrgb(c), 0.35)
    # scan-glitch bars
    gb, dg = canvas(ctx)
    grng = np.random.default_rng(800 + ctx.seed % 5)
    for i in range(30):
        x, y = grng.uniform(-400, 380), grng.uniform(120, 370)
        w, h = grng.uniform(20, 140), float(grng.choice([1, 2, 2, 3, 5]))
        dg.rectangle([*ctx.px(x, y), *ctx.px(x + w, y - h)], fill=int(grng.uniform(120, 255)))
    gbm = arr(gb)
    rgb = rgb + red * (gbm * 0.55)[..., None] + (gbm * 0.12)[..., None]
    # inverted hexagon emblem (inner band) + a large ghost hex outline
    hx, dh = canvas(ctx)
    cx, cy = ctx.px(0, R_IN + 32)
    _inv_hex(dh, cx, cy, 20, 4)
    _inv_hex(dh, cx, cy, 9, 3)
    ghost, dgh = canvas(ctx)
    gx, gy = ctx.px(0, sl.GROUP_R)
    _inv_hex(dgh, gx, gy, 92, 2)
    hm = arr(hx)
    rgb = put(rgb, hm, red * 1.1, 0.9)
    rgb = rgb + red * (arr(ghost) * 0.25)[..., None]
    emis = red * (hm * 0.6 + gbm * 0.35 + trm * 0.25)[..., None]
    # scanlines
    rows = np.arange(ctx.H)[:, None]
    scan = np.where((rows % 3) == 0, 0.72, 1.0).astype(np.float32)
    rgb = rgb * scan[..., None]
    # behaviour: aggressive horizontal tear (bursts on a 12-frame grid)
    f = int(math.floor(t * 24))
    burst = (f % 8) in (0, 1, 5)
    rng = np.random.default_rng(1000 + f * 13 + ctx.seed)
    strength = 1.0 if burst else 0.25
    rgb = tear_rows(rgb, np.random.default_rng(1000 + f * 13 + ctx.seed), strength)
    emis = tear_rows(emis, np.random.default_rng(1000 + f * 13 + ctx.seed), strength)
    if burst:
        # RGB split: red channel slips one way, blue the other
        rgb[..., 0] = np.roll(rgb[..., 0], 4, axis=1)
        rgb[..., 2] = np.roll(rgb[..., 2], -4, axis=1)
        y0 = int(rng.integers(0, ctx.H))
        rgb[y0:y0 + 6] = rgb[y0:y0 + 6] * 0.3 + red * 0.9
        emis[y0:y0 + 6] += red * 0.8
    return rgb, emis


# ----------------------------------------------------------------------------- PLAYER (neutral)
def tex_player(ctx, rich=False):
    col = ctx.accent
    if ctx.typ == "MISS":
        col = np.array([0.30, 0.30, 0.32], np.float32)
    k = smoothstep(R_IN, R_OUT, ctx.r)
    rgb = col * (0.42 + 0.22 * k)[..., None]
    n = fbm(ctx, 91)
    rgb = rgb * (0.92 + 0.14 * n)[..., None]
    tr, pads = circuit_traces(ctx, 300 + ctx.seed % 6, n=18)
    m = np.clip(tr + pads, 0, 1)
    rgb = rgb + (col * 0.5 + 0.18) * (m * 0.30)[..., None]
    # packet running a trace
    emis = (col * 0.6 + 0.2) * (m * 0.08)[..., None]
    return rgb, emis


THEMES = {
    "meridian": dict(name="MERIDIAN FREIGHT", col=MERIDIAN, tex=tex_meridian,
                     texture="Corrugated container steel, stencilled cargo codes, barcode label",
                     behaviour="Conveyor scroll; barcode scan line sweeps"),
    "solace": dict(name="SOLACE BIOSYSTEMS", col=SOLACE, tex=tex_solace,
                   texture="Sterile frosted glass, cells under a microscope, DNA helix etch",
                   behaviour="Cells slowly divide; heartbeat pulse (ECG + glass)"),
    "halcyon": dict(name="HALCYON CIVIC", col=HALCYON, tex=tex_halcyon,
                    texture="Blueprint civic grid, municipal paving tiles, concentric civic rings",
                    behaviour="Pulses flow along grid lines and rings like traffic/utilities"),
    "orbital": dict(name="ORBITAL COMMONS", col=ORBITAL, tex=tex_orbital,
                    texture="Star map + graticule, orbit lines, solar-panel cells",
                    behaviour="A satellite crosses on its orbit; panels glint"),
    "rebel": dict(name="REBEL_CELL / DISPATCH", col=REBEL, tex=tex_rebel,
                  texture="Corrupted red glitch over the Cell's own PCB, scan bars, inverted hexagon",
                  behaviour="Aggressive horizontal tear + RGB split bursts"),
    "player": dict(name="THE CELL (player, neutral)", col="#E8E8F0", tex=tex_player,
                   texture="Type-colour fill, circuit traces", behaviour="(player round)"),
}
