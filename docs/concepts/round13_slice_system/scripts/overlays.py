"""Round 13 slice-STATE overlays. Each one is a separate layer drawn over ANY slice (between the
screen and the read block), plus front marks (status badge, chips) drawn after the read block.

Real statuses (rc.gd Status): CORRUPTED, OVERCLOCKED, ENCRYPTED, PARASITE.
Placeholders (not in game as per-slice states): FROZEN, LOCKED, BURNING, EMPOWERED.
Rules: the overlay thins to <= 35 % inside the read window; nothing covers the value; every state has
a mark badge (circle = helps, diamond = hurts, notched circle = mixed, square = neutral) in the
outer-right corner, so the state reads without colour.  All motion loops over t in [0, 1).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import slicelib as SL
from slicekit import fbm, vnoise, loop_off, region, over, add, local_to_xy, polar

STATE_INFO = {
    #  state         mark glyph        badge kind  badge colour       real?
    "FROZEN": ("ST_FROZEN", "hurt", (150, 220, 255), False),
    "LOCKED": ("ST_LOCKED", "neutral", (200, 200, 215), False),
    "BURNING": ("ST_BURNING", "hurt", (255, 120, 40), False),
    "EMPOWERED": ("ST_EMPOWERED", "help", (255, 214, 64), False),
    "CORRUPTED": ("ST_CORRUPTED", "hurt", (255, 77, 77), True),
    "OVERCLOCKED": ("ST_OVERCLOCKED", "mixed", (255, 190, 60), True),
    "ENCRYPTED": ("ST_ENCRYPTED", "help", (92, 225, 255), True),
    "PARASITE": ("ST_PARASITE", "hurt", (170, 255, 80), True),
}
ORDER = ["CORRUPTED", "OVERCLOCKED", "ENCRYPTED", "PARASITE", "FROZEN", "LOCKED", "BURNING", "EMPOWERED"]


def C(*v):
    return np.array(v, np.float32)


def _thin(a, win, keep=0.35):
    return a * (1 - (1 - keep) * win)


def _layer_draw(g, fn, blur=0.0):
    """Draw with PIL in canvas coordinates of g's bbox; returns float (H,W,4) straight rgba."""
    W, H = g.x1 - g.x0, g.y1 - g.y0
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fn(d, lambda x, y: (x - g.x0, y - g.y0))
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im, np.float32) / 255.0


def _put(reg, lay, k=1.0, mask=None):
    a = lay[..., 3] * k
    if mask is not None:
        a = a * mask
    over(reg, lay[..., :3], a)


# ======================================================================== the overlays
def frozen(reg, g, col, t, seed, win):
    ss = g.ss
    tile = g.a_tile
    scr = g.a_scr * tile
    # cold glass: tint everything toward ice blue
    rgb = reg[..., :3]
    cold = rgb * C(0.62, 0.80, 1.0) + C(0.03, 0.07, 0.12)
    m = (tile * 0.85)[..., None]
    reg[..., :3] = rgb * (1 - m) + cold * m
    # crust grows in from the bezel; its edge breathes
    ox, oy = loop_off(t, 0.6)
    n = fbm(g.u / (16 * ss) + ox, g.v / (16 * ss) + oy, seed + 1)
    reach = 26 * ss * (1 + 0.10 * math.sin(2 * math.pi * t))
    edge = np.where(g.e_scr < 0, 1.0, np.exp(-np.maximum(g.e_scr, 0) / reach))
    crust = np.clip((n * 0.75 + edge * 0.75 - 0.78) * 6, 0, 1) * tile
    over(reg, C(0.80, 0.92, 1.0), _thin(crust * 0.88, win, 0.15))
    # crystal ridges at the crust front
    r2 = 1 - np.abs(2 * fbm(g.u / (7 * ss), g.v / (7 * ss), seed + 9, 3) - 1)
    front = np.exp(-((n * 0.75 + edge * 0.75 - 0.74) / 0.07) ** 2)
    ridge = np.clip((r2 - 0.86) * 9, 0, 1) * front * tile
    add(reg, C(0.9, 0.97, 1.0), _thin(ridge * 0.9, win, 0.2))
    # glass crack lines (static) across the screen
    def cracks(d, P):
        rng = np.random.default_rng(seed + 77)
        for k in range(3):
            u0 = (rng.random() - 0.5) * 2 * 90 * ss
            v0 = rng.random() * g.Hs * 0.25
            pts = []
            u, v = u0, v0
            for s in range(9):
                pts.append(P(*local_to_xy(g, u, v)))
                u += (rng.random() - 0.5) * 34 * ss
                v += g.Hs * 0.09
            d.line(pts, fill=(235, 248, 255, 200), width=max(1, int(1.1 * ss)))
    lay = _layer_draw(g, cracks)
    _put(reg, lay, 0.7, _thin(scr, win, 0.0))
    # glints twinkle in the crust
    def glints(d, P):
        rng = np.random.default_rng(seed + 5)
        for k in range(9):
            u = (rng.random() - 0.5) * 2 * 120 * ss
            v = rng.random() * g.Hs
            ph = rng.random()
            a = max(0.0, math.sin(2 * math.pi * (t * 2 + ph)))
            if a < 0.25:
                continue
            x, y = P(*local_to_xy(g, u, v * 0.3 if k % 2 else g.Hs - v * 0.25))
            L = (3 + 7 * a) * ss
            c = (255, 255, 255, int(255 * a))
            d.line([(x - L, y), (x + L, y)], fill=c, width=max(1, int(ss)))
            d.line([(x, y - L), (x, y + L)], fill=c, width=max(1, int(ss)))
    lay = _layer_draw(g, glints)
    _put(reg, lay, 1.0, tile)


def locked(reg, g, col, t, seed, win):
    ss = g.ss
    tile = g.a_tile
    scr = g.a_scr * tile
    reg[..., :3] *= (1 - 0.30 * scr)[..., None]
    # roller shutter down to the read block: slats of constant radius
    sh_end = g.Hs * 0.27
    inside = (g.v > -g.bw) & (g.v < sh_end)
    slat = (g.v % (7 * ss)) / (7 * ss)
    shade = 0.20 + 0.16 * np.sin(slat * math.pi) - 0.10 * (slat > 0.86)
    steel = shade[..., None] * C(0.95, 1.0, 1.08)
    sweep = np.exp(-(((g.u / ss) / 140 - ((t * 1.0) % 1.0) * 2.4 + 1.2) / 0.08) ** 2)
    steel = steel + sweep[..., None] * 0.18
    over(reg, steel, inside * tile * 0.97)
    # hazard edge on the bottom slat
    hz = (g.v >= sh_end - 4 * ss) & (g.v < sh_end)
    stripe = (((g.u + g.v) / (6 * ss)) % 2) < 1
    over(reg, np.where(stripe[..., None], C(1.0, 0.78, 0.1), C(0.06, 0.05, 0.05)), hz * tile)
    over(reg, C(0, 0, 0), np.exp(-((g.v - sh_end - 2 * ss) / (2.5 * ss)) ** 2) * tile * 0.6)
    # two cage bars down the sides of the read block (never across it)
    for s in (-1, 1):
        uc = s * g.halfw * 0.70
        bar = np.clip(1 - np.abs(g.u - uc) / (3.2 * ss), 0, 1)
        m = bar * (g.v > sh_end) * scr
        over(reg, C(0.16, 0.17, 0.2) + 0.25 * np.clip(1 - np.abs(g.u - uc + s * ss) / (1.2 * ss), 0, 1)[..., None], m)
    # lock LED on the shutter: blinks red
    on = 1.0 if (t * 4) % 1.0 < 0.5 else 0.25
    x, y = local_to_xy(g, 0, sh_end * 0.5)
    dd = np.hypot(g.xx - x, g.yy - y)
    over(reg, C(0.05, 0.04, 0.05), np.clip(4.5 * ss - dd, 0, 1))
    add(reg, C(1.0, 0.12, 0.1), (np.clip(2.6 * ss - dd, 0, 1) + np.exp(-(dd / (6 * ss)) ** 2) * 0.6) * on)


def burning(reg, g, col, t, seed, win):
    ss = g.ss
    tile = g.a_tile
    scr = g.a_scr * tile
    # heat tint
    add(reg, C(0.35, 0.10, 0.0), scr * 0.20)
    # reserved BURN effect: char blotches eat in from the screen edge, ember rim
    ox, oy = loop_off(t, 0.35)
    n = fbm(g.u / (22 * ss) + ox, g.v / (22 * ss) + oy, seed + 21)
    edge = np.exp(-np.maximum(g.e_scr, 0) / (30 * ss))
    b = n * 0.7 + edge * 0.6
    char = np.clip((b - 0.80) * 10, 0, 1) * scr
    over(reg, C(0.05, 0.02, 0.01), _thin(char * 0.92, win, 0.0))
    rim = np.exp(-((b - 0.78) / 0.025) ** 2) * scr
    add(reg, C(1.0, 0.45, 0.08), _thin(rim * 1.2, win, 0.0))
    # flames: rise outward from the rim and lick along the bezel
    flow = t * 1.0
    fx = g.u / (16 * ss)
    fy = (g.Ro - g.rho) / (14 * ss)
    nn = fbm(fx + 0.0, fy + flow * 4.0, seed + 33, 4)  # flow loops: 4 lattice cells per loop
    nn2 = fbm(fx + 7.3, fy + flow * 4.0 - 4.0, seed + 33, 4)
    nf = nn * (1 - t) + nn2 * t  # cross-fade keeps the loop seamless
    out_d = np.maximum(-g.e_tile, 0)  # distance outside the tile
    in_d = np.maximum(g.e_tile, 0)
    beyond_rim = (g.rho > g.Ro - 2 * g.gap) * np.clip(1 - (np.abs(g.d) - g.half) / 1.0, 0, 1)
    F = nf * 1.7 + 0.05 - in_d / (12 * ss) - out_d / (40 * ss) * (beyond_rim > 0) - (out_d > 0) * (beyond_rim <= 0) * 5
    F = F + 0.25 * np.exp(-np.maximum(g.e_scr + g.bw * 0.5, 0) / (6 * ss)) * (g.e_tile > 0)
    heat = np.clip((F - 0.42) / 0.5, 0, 1)
    colr = (C(0.9, 0.12, 0.02)[None, None, :] * (1 - heat[..., None]) + C(1.0, 0.62, 0.12) * heat[..., None])
    colr = np.where((heat > 0.75)[..., None], colr * 0.5 + C(1.0, 0.95, 0.65) * 0.5, colr)
    a = np.clip((F - 0.40) * 5, 0, 1)
    a = _thin(a, win, 0.0)
    add(reg, colr, a * 0.95)
    # embers drifting outward
    def embers(d, P):
        rng = np.random.default_rng(seed + 8)
        for k in range(14):
            u = (rng.random() - 0.5) * 2 * g.halfw.max() * 0.9
            ph = (rng.random() + t) % 1.0
            v = -ph * 34 * ss + 6 * ss
            x, y = P(*local_to_xy(g, u + math.sin(ph * 6 + k) * 6 * ss, v))
            r = (1.6 - ph) * ss
            a = int(255 * (1 - ph))
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 190, 80, a))
    lay = _layer_draw(g, embers)
    add(reg, lay[..., :3], lay[..., 3])


def empowered(reg, g, col, t, seed, win):
    ss = g.ss
    tile = g.a_tile
    scr = g.a_scr * tile
    gold = C(1.0, 0.84, 0.30)
    reg[..., :3] *= (1 + 0.18 * scr)[..., None]
    # rim glow + halo past the rim, pulsing
    pulse = 0.75 + 0.25 * math.sin(2 * math.pi * t)
    lip = np.exp(-(np.abs(g.e_tile) / (2.2 * ss)) ** 2) * np.clip(g.e_tile + 4 * ss, 0, 1)
    add(reg, gold * 0.9 + 0.1, lip * 0.9 * pulse)
    halo = np.exp(-(np.maximum(-g.e_tile, 0) / (8 * ss))) * (g.e_tile < 0) * (g.rho > g.Ro - 3 * g.gap) * np.clip(1 - (np.abs(g.d) - g.half), 0, 1)
    add(reg, gold, halo * 0.55 * pulse)
    # upward (outward) chevrons climbing two side lanes
    for s in (-1, 1):
        uc = s * g.halfw * 0.66
        for k in range(3):
            vc = g.Hs * (1 - ((k / 3 + t) % 1.0))
            fade = math.sin(math.pi * (1 - vc / g.Hs)) ** 1.2
            w = 13 * ss
            du = np.abs(g.u - uc)
            dist = np.abs((g.v - vc) + du * 0.85)
            chev = np.clip(3.0 * ss - dist, 0, 1) * (du < w)
            glow = np.exp(-(dist / (5 * ss)) ** 2) * (du < w + 3 * ss)
            add(reg, gold, _thin(glow * scr * fade * 0.5, win, 0.0))
            add(reg, gold * 0.6 + 0.45, _thin(chev * scr * fade, win, 0.0))
    # light rising through the screen
    band = np.exp(-((g.v / g.Hs - (1 - t)) / 0.08) ** 2) * scr
    add(reg, gold * 0.6, _thin(band * 0.25, win, 0.3))


def corrupted(reg, g, col, t, seed, win):
    ss = g.ss
    tile = g.a_tile
    scr = g.a_scr * tile
    frame = int(t * 12) % 12
    rng = np.random.default_rng(seed * 31 + frame)
    src = reg.copy()
    H, W = reg.shape[:2]
    # displaced slabs with an RGB split (in Godot: hint_screen_texture sampling)
    for k in range(4):
        y0 = int(rng.random() * H)
        hh = int((4 + rng.random() * 14) * ss)
        dx = int((rng.random() - 0.5) * 30 * ss)
        rows = slice(max(0, y0), min(H, y0 + hh))
        sh = np.roll(src[rows], dx, axis=1)
        r = np.roll(src[rows, :, 0], dx + int(3 * ss), axis=1)
        b = np.roll(src[rows, :, 2], dx - int(3 * ss), axis=1)
        sh[..., 0], sh[..., 2] = r, b
        m = (tile[rows] * (1 - 0.8 * win[rows]))[..., None]
        reg[rows, :, :3] = reg[rows, :, :3] * (1 - m) + sh[..., :3] * m
    # macroblocks: magenta / green dead squares, quantised to a grid
    q = 6 * ss
    gx, gy = np.floor(g.xx / q), np.floor(g.yy / q)
    hsh = (np.sin(gx * 12.9898 + gy * 78.233 + frame * 3.1 + seed) * 43758.5453) % 1.0
    blk = (hsh > 0.93) * scr
    colb = np.where((hsh > 0.965)[..., None], C(1.0, 0.1, 0.65), C(0.1, 1.0, 0.45))
    over(reg, colb, _thin(blk * 0.75, win, 0.0))
    # static grain + a tear line
    grain = vnoise(g.xx / (1.2 * ss), g.yy / (1.2 * ss), seed + frame * 11)
    add(reg, C(0.6, 0.6, 0.7), (grain > 0.8) * scr * 0.25)
    ty = (t * 1.0 % 1.0) * H
    tear = np.exp(-((g.yy - g.y0 - ty) / (1.2 * ss)) ** 2) * tile
    add(reg, C(1.0, 0.3, 0.6), tear * 0.8)
    # red hazard pulse on the bezel
    hl = np.exp(-((g.e_scr + 1.3 * ss) / (1.2 * ss)) ** 2) * tile
    add(reg, C(1.0, 0.12, 0.2), hl * (0.6 + 0.4 * (frame % 3 == 0)))
    over(reg, C(0.45, 0.02, 0.08), g.bez * 0.35)


def overclocked(reg, g, col, t, seed, win):
    ss = g.ss
    tile = g.a_tile
    scr = g.a_scr * tile
    pulse = 0.7 + 0.3 * math.sin(2 * math.pi * t * 2)
    # hot bezel: amber -> white at the screen lip
    hot = np.exp(-np.maximum(-(g.e_scr), 0) / (5 * ss)) * g.bez
    add(reg, C(1.0, 0.45, 0.06), g.bez * 0.30 * pulse)
    add(reg, C(1.0, 0.80, 0.4), hot * 0.30 * pulse)
    add(reg, C(0.3, 0.16, 0.0), scr * 0.12)
    # heat shimmer rising in the side lanes
    for s in (-1, 1):
        uc = s * g.halfw * 0.68
        wav = g.u - uc - 4 * ss * np.sin(g.v / (9 * ss) + 2 * math.pi * t * 2)
        line = np.exp(-(wav / (1.3 * ss)) ** 2) * scr * np.clip(g.v / (g.Hs * 0.2), 0, 1)
        add(reg, C(1.0, 0.75, 0.3), _thin(line * 0.45, win, 0.0))
    # electric arcs crawling along the bezel band (re-rolled 8x per loop)
    frame = int(t * 8) % 8
    def arcs(d, P):
        rng = np.random.default_rng(seed * 17 + frame)
        for k in range(3):
            side = k
            pts = []
            for i in range(10):
                f = i / 9
                if side == 0:  # outer band
                    u = (f - 0.5) * 2 * g.halfw.max() * 0.85
                    v = -g.bw * 0.5 + (rng.random() - 0.5) * 5 * ss
                    pts.append(P(*local_to_xy(g, u, v)))
                else:  # a side band
                    sg = -1 if side == 1 else 1
                    v = f * g.Hs
                    rho = g.r_out_s - v
                    ang = g.mid + sg * (g.half - math.degrees((g.bw * 0.5 + g.gap) / max(rho, 1)))
                    x, y = polar(g, rho, ang)
                    pts.append(P(x + (rng.random() - 0.5) * 6 * ss, y + (rng.random() - 0.5) * 6 * ss))
            d.line(pts, fill=(235, 245, 255, 255), width=max(1, int(1.8 * ss)))
    lay = _layer_draw(g, arcs)
    glow = _layer_draw(g, arcs, blur=4 * ss)
    add(reg, C(0.75, 0.85, 1.0), glow[..., 3] * 1.4)
    add(reg, lay[..., :3], lay[..., 3])


def encrypted(reg, g, col, t, seed, win):
    ss = g.ss
    tile = g.a_tile
    scr = g.a_scr * tile
    cyan = C(0.45, 0.92, 1.0)
    over(reg, C(0.02, 0.10, 0.16), scr * 0.25)
    # hex lattice in tile space
    s = 13 * ss
    x = g.u / s
    y = g.v / s
    # axial hex distance via 3 families of lines
    l1 = np.abs(((y * 1.1547) % 1.0) - 0.5)
    l2 = np.abs((((x + y * 0.57735) * 1.0) % 1.0) - 0.5)
    l3 = np.abs((((x - y * 0.57735) * 1.0) % 1.0) - 0.5)
    edge = np.clip((np.maximum(np.maximum(l1, l2), l3) - 0.44) * 18, 0, 1)
    sweep = ((g.u / ss) * 0.4 + g.v / ss) / (g.Hs / ss + 120) - t
    sweep = sweep - np.floor(sweep)
    shim = 0.30 + 0.9 * np.exp(-((sweep - 0.5) / 0.07) ** 2)
    add(reg, cyan, _thin(edge * shim * scr * 0.7, win, 0.25))
    # random cells lit (cipher churn)
    cid = np.floor(x * 1.0) + 37 * np.floor(y * 1.1547)
    lit = ((np.sin(cid * 91.7 + int(t * 10) * 5.3 + seed) * 43758.5) % 1.0) > 0.94
    add(reg, cyan * 0.6, _thin(lit * scr * 0.35, win, 0.0))
    # cold glass sheen + bright cipher rim on the bezel
    rim = np.exp(-((g.e_scr + 1.3 * ss) / (1.0 * ss)) ** 2) * tile
    add(reg, cyan, rim * 1.1)
    over(reg, C(0.10, 0.30, 0.40), g.bez * 0.35)
    # *** stamped on the outer band, scrolling
    def stars(d, P):
        f = SL.f_mono(int(9 * ss))
        n = 9
        for i in range(n):
            u = ((i / n + t / n * 3) % 1.0 - 0.5) * 2 * g.halfw.max() * 0.8
            x, y = P(*local_to_xy(g, u, -g.bw * 0.45))
            d.text((x, y), "*", font=f, fill=(170, 245, 255, 255), anchor="mm")
    lay = _layer_draw(g, stars)
    add(reg, lay[..., :3], lay[..., 3] * 0.9)


def parasite(reg, g, col, t, seed, win):
    ss = g.ss
    tile = g.a_tile
    scr = g.a_scr * tile
    # drain: the lower (hub-side) half loses light and colour
    lum = reg[..., :3].mean(axis=2, keepdims=True)
    low = np.clip((g.v / g.Hs - 0.35) / 0.5, 0, 1) * scr
    reg[..., :3] = reg[..., :3] * (1 - 0.5 * low[..., None]) + lum * 0.6 * (0.5 * low[..., None])
    sick = C(0.66, 1.0, 0.32)
    # veins climb from the inner bezel; pulses travel DOWN them to the hub (output being drained)
    rng = np.random.default_rng(seed + 404)
    paths = []
    for k in range(5):
        u = (k - 2) * 14 * ss + (rng.random() - 0.5) * 8 * ss
        v = g.Hs + g.bw * 0.6
        pts = [(u, v)]
        top = g.Hs * (0.18 + 0.25 * rng.random())
        while v > top:
            v -= 8 * ss
            u += (rng.random() - 0.5) * 12 * ss + (u * 0.12 if abs(u) < g.halfw.max() * 0.5 else -u * 0.05)
            pts.append((u, v))
        paths.append(pts)

    def veins(d, P, core=False):
        for pts in paths:
            n = len(pts)
            for i in range(n - 1):
                f = i / (n - 1)
                w = (5.0 * (1 - f) + 1.2) * ss * (0.55 if core else 1)
                if core:
                    br = 0.5 + 0.5 * math.sin(2 * math.pi * (f * 3 + t * 2))
                    c = (int(170 + 85 * br), 255, int(80 + 60 * br), int(255 * (0.35 + 0.65 * br)))
                else:
                    c = (24, 30, 14, 230)
                a, b = P(*local_to_xy(g, *pts[i])), P(*local_to_xy(g, *pts[i + 1]))
                d.line([a, b], fill=c, width=max(1, int(w)))
    lay = _layer_draw(g, lambda d, P: veins(d, P, False))
    _put(reg, lay, 0.95, _thin(tile, win, 0.15))
    lay = _layer_draw(g, lambda d, P: veins(d, P, True))
    glow = _layer_draw(g, lambda d, P: veins(d, P, True), blur=3 * ss)
    add(reg, sick, _thin(glow[..., 3] * 0.7, win, 0.1))
    add(reg, lay[..., :3], _thin(lay[..., 3] * 0.9, win, 0.15))
    # the inner bezel goes sick green
    inner = np.exp(-np.maximum(g.e_in - g.gap, 0) / (8 * ss)) * tile
    add(reg, sick * 0.5, inner * 0.6 * (0.7 + 0.3 * math.sin(2 * math.pi * t)))


FUN = {"FROZEN": frozen, "LOCKED": locked, "BURNING": burning, "EMPOWERED": empowered,
       "CORRUPTED": corrupted, "OVERCLOCKED": overclocked, "ENCRYPTED": encrypted, "PARASITE": parasite}
CHIP = {"OVERCLOCKED": "x1.5", "PARASITE": "x0.5"}


def apply(canvas, g, state, col, t, seed, win):
    reg = region(canvas, g)
    FUN[state](reg, g, col, t, seed, win)


_badge_cache = {}


def front(canvas, g, state, t, seed):
    """Status badge in the outer-right corner (upright) + the rule chip near the inner edge."""
    import make_glyphs as MG
    gid, kind, bcol, real = STATE_INFO[state]
    ss = g.ss
    px = int(34 * ss)
    key = (state, px)
    if key not in _badge_cache:
        _badge_cache[key] = MG.badge(gid, px, bcol, kind)
    b = _badge_cache[key]
    rho = g.Ro - g.bw - 24 * ss
    ang = g.mid + g.half * 0.66
    x, y = polar(g, rho, ang)
    SL.paste_rgba(canvas, b, x - b.width / 2, y - b.height / 2)
    if state in CHIP:
        c = SL.badge_rgba(CHIP[state], 12, ss, col=bcol)
        x, y = polar(g, g.Ri + 22 * ss, g.mid)
        SL.paste_rgba(canvas, c, x - c.width / 2, y - c.height / 2)
