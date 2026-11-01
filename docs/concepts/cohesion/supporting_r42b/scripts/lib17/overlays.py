"""Round 14 slice-STATE overlays (CORRUPTED, ENCRYPTED, PARASITE, LOCKED, EMPOWERED redone; OVERCLOCKED at 45 %). Each one is a separate layer drawn over ANY slice (between the
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


def _overclocked_r13(reg, g, col, t, seed, win):
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


# ======================================================================== round 14 replacements
def overclocked(reg, g, col, t, seed, win):
    """Round 14: the round 13 look, composited at 45 % so the slice shows through."""
    before = reg.copy()
    _overclocked_r13(reg, g, col, t, seed, win)
    k = 0.45
    reg[:] = before * (1 - k) + reg * k


def corrupted(reg, g, col, t, seed, win):
    """Full-slice glitch shader, pink + green: the whole slice (bezel included) tears sideways in bands,
    its outline and bright content split into a pink and a green ghost, scanlines flicker."""
    ss = g.ss
    tile = g.a_tile
    scr = g.a_scr * tile
    frame = int(t * 12) % 12
    rng = np.random.default_rng(seed * 31 + frame)
    H, W = reg.shape[:2]
    src = reg.copy()
    PINK, GREEN = C(1.0, 0.16, 0.62), C(0.18, 1.0, 0.50)
    # 1. tear bands: whole rows of the slice (alpha too) slide sideways
    for k in range(5):
        y0 = int(rng.random() * H)
        hh = int((3 + rng.random() * 12) * ss)
        dx = int((rng.random() - 0.5) * 2 * (6 + 14 * rng.random()) * ss)
        rows = slice(max(0, y0), min(H, y0 + hh))
        reg[rows] = np.roll(src[rows], dx, axis=1)
    cur = reg.copy()
    # 2. pink / green split of the outline and the bright content
    A = cur[..., 3]
    gy, gx = np.gradient(A)
    edge = np.clip(np.hypot(gx, gy) * 2.5, 0, 1)
    lum = cur[..., :3].max(axis=2)
    sig = np.clip(edge + np.clip(lum - 0.45, 0, 1) * 0.9, 0, 1)
    k = int((3 + 2 * math.sin(2 * math.pi * t * 3)) * ss)
    pk = np.roll(sig, k, axis=1)
    gr = np.roll(sig, -k, axis=1)
    add(reg, PINK, _thin(pk * 0.85, win, 0.2))
    add(reg, GREEN, _thin(gr * 0.75, win, 0.2))
    # 3. the screen: pink/green colour bands + scanline flicker
    band = np.sin(g.yy / (5 * ss) + frame * 1.7) * np.sin(g.yy / (17 * ss) - frame * 0.9)
    tint = np.where((band > 0.35)[..., None], PINK, np.where((band < -0.45)[..., None], GREEN, C(0, 0, 0)))
    add(reg, tint, _thin(scr * 0.22 * (np.abs(band) > 0.35), win, 0.0))
    scan = (np.floor(g.yy / (2 * ss)) % 2 == 0) * scr
    reg[..., :3] *= (1 - 0.18 * _thin(scan, win, 0.0))[..., None]
    # 4. a bright tear line sweeping down
    ty = (t % 1.0) * H
    tear = np.exp(-((g.yy - g.y0 - ty) / (1.0 * ss)) ** 2) * np.clip(A + scr, 0, 1)
    add(reg, PINK * 0.6 + GREEN * 0.4, tear * 0.9)


def encrypted(reg, g, col, t, seed, win):
    """A field of * characters scrolling radially OUTWARD (up the wedge) behind the value."""
    ss = g.ss
    tile = g.a_tile
    scr = g.a_scr * tile
    cyan = C(0.45, 0.92, 1.0)
    over(reg, C(0.02, 0.10, 0.16), scr * 0.35)
    rs, cs = 22 * ss, 19 * ss
    shift = t * 2 * rs  # two rows per loop (rows alternate their stagger): seamless

    def stars(d, P):
        f = SL.f_mono(int(30 * ss))
        nrow = int((g.Hs + 2 * rs) / rs) + 2
        for r in range(-1, nrow):
            vv = r * rs - shift + 2 * rs
            if vv < -rs or vv > g.Hs + rs:
                continue
            ridx = r + int(round(2 * t * 0))
            stag = (r % 2) * cs * 0.5
            rho = g.r_out_s - vv
            hw = rho * math.radians(g.half)
            n = int(hw / cs) + 1
            fade = math.sin(math.pi * min(1, max(0, vv / g.Hs))) ** 0.6
            for c in range(-n, n + 1):
                u = c * cs + stag
                h = (math.sin((r * 7.31 + c * 3.17 + seed) * 12.9898) * 43758.5453) % 1.0
                a = int(255 * fade * (0.35 + 0.65 * h))
                x, y = P(*local_to_xy(g, u, vv))
                d.text((x, y), "*", font=f, fill=(150, 240, 255, a), anchor="mm")
    lay = _layer_draw(g, stars)
    glow = _layer_draw(g, stars, blur=2.5 * ss)
    add(reg, cyan, _thin(glow[..., 3] * scr * 0.6, win, 0.2))
    add(reg, lay[..., :3], _thin(lay[..., 3] * scr * 0.85, win, 0.25))
    rim = np.exp(-((g.e_scr + 1.3 * ss) / (1.0 * ss)) ** 2) * tile
    add(reg, cyan, rim * 1.1)
    over(reg, C(0.10, 0.30, 0.40), g.bez * 0.35)


def parasite(reg, g, col, t, seed, win):
    """The parasite itself latched onto the slice: large, translucent, gently pumping."""
    ss = g.ss
    tile = g.a_tile
    scr = g.a_scr * tile
    lum = reg[..., :3].mean(axis=2, keepdims=True)
    low = np.clip((g.v / g.Hs - 0.35) / 0.5, 0, 1) * scr
    reg[..., :3] = reg[..., :3] * (1 - 0.45 * low[..., None]) + lum * 0.25 * low[..., None]
    sick = C(0.66, 1.0, 0.32)
    pump = math.sin(2 * math.pi * t)
    size = int(g.Hs * 0.95 * (1 + 0.035 * pump))
    import glyphs15
    m = glyphs15.tick_mask(t * 2).resize((size, size), Image.LANCZOS)  # legs crawl twice per loop
    m = m.rotate(-g.mid + 18 + 4 * math.sin(2 * math.pi * t * 2), resample=Image.BICUBIC)
    edge = m.filter(ImageFilter.MaxFilter(max(3, int(2.5 * ss) | 1)))
    cx, cy = local_to_xy(g, g.halfw.max() * 0.18, g.Hs * 0.50)

    def body(d, P):
        pass
    W, H = g.x1 - g.x0, g.y1 - g.y0
    lay_e = Image.new("L", (W, H), 0)
    lay_b = Image.new("L", (W, H), 0)
    ox, oy = int(cx - g.x0 - size / 2), int(cy - g.y0 - size / 2)
    lay_e.paste(edge, (ox, oy))
    lay_b.paste(m, (ox, oy))
    e = np.asarray(lay_e, np.float32) / 255 * tile
    b = np.asarray(lay_b, np.float32) / 255 * tile
    over(reg, C(0.05, 0.08, 0.02), _thin(e * 0.55, win, 0.3))
    over(reg, sick * (0.75 + 0.15 * pump), _thin(b * 0.42, win, 0.25))
    inner = np.exp(-np.maximum(g.e_in - g.gap, 0) / (8 * ss)) * tile
    add(reg, sick * 0.5, inner * 0.6 * (0.7 + 0.3 * pump))


def locked(reg, g, col, t, seed, win):
    """Rows of padlocks scrolling left -> right across the slice."""
    ss = g.ss
    tile = g.a_tile
    scr = g.a_scr * tile
    reg[..., :3] *= (1 - 0.35 * scr)[..., None]
    over(reg, C(0.22, 0.23, 0.27), g.bez * 0.5)
    sp = 44 * ss
    sz = int(26 * ss)
    import make_glyphs as MG
    lockimg = SL.glyph_rgba("ST_LOCKED", sz, max(1.0, sz * 0.08))
    rows = (0.16, 0.50, 0.84)

    def locks(d, P):
        pass
    W, H = g.x1 - g.x0, g.y1 - g.y0
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for ri, f in enumerate(rows):
        vv = g.Hs * f
        rho = g.r_out_s - vv
        hw = rho * math.radians(g.half)
        off = (t * sp + ri * sp * 0.5) % sp
        n = int(hw / sp) + 2
        for c in range(-n, n + 1):
            u = c * sp + off
            x, y = local_to_xy(g, u, vv)
            fade = max(0.0, 1 - abs(u) / (hw + 1))
            im = lockimg.rotate(-g.mid if abs(g.mid) > 1 else 0, resample=Image.BICUBIC, expand=True)
            a = im.split()[3].point(lambda v, k=fade: int(v * (0.25 + 0.55 * k)))
            im.putalpha(a)
            lay.alpha_composite(im, (int(x - g.x0 - im.width / 2), int(y - g.y0 - im.height / 2)))
    arr = np.asarray(lay, np.float32) / 255
    over(reg, arr[..., :3], _thin(arr[..., 3] * scr, win, 0.2))


def empowered(reg, g, col, t, seed, win):
    """HUGE translucent gold chevrons rising radially outward behind the value, rim glow + halo."""
    ss = g.ss
    tile = g.a_tile
    scr = g.a_scr * tile
    gold = C(1.0, 0.84, 0.30)
    reg[..., :3] *= (1 + 0.12 * scr)[..., None]
    pulse = 0.75 + 0.25 * math.sin(2 * math.pi * t)
    lip = np.exp(-(np.abs(g.e_tile) / (2.2 * ss)) ** 2) * np.clip(g.e_tile + 4 * ss, 0, 1)
    add(reg, gold * 0.9 + 0.1, lip * 0.9 * pulse)
    halo = np.exp(-(np.maximum(-g.e_tile, 0) / (8 * ss))) * (g.e_tile < 0) * (g.rho > g.Ro - 3 * g.gap) * np.clip(1 - (np.abs(g.d) - g.half), 0, 1)
    add(reg, gold, halo * 0.55 * pulse)
    period = g.Hs * 0.55
    AH = g.Hs * 0.70
    WW = (g.r_out_s - g.Hs * 0.5) * math.radians(g.half) * 0.80

    def arrows(d, P):
        for k in range(-1, 3):
            vt = k * period - (t * period) % period  # tip position; moves outward (v decreasing)
            TH = AH * 0.30  # a huge CHEVRON (round 15), not an arrow
            pts = [(0, vt), (WW, vt + AH * 0.52), (WW, vt + AH * 0.52 + TH), (0, vt + TH),
                   (-WW, vt + AH * 0.52 + TH), (-WW, vt + AH * 0.52)]
            dense = []
            for i in range(len(pts)):
                a, b = pts[i], pts[(i + 1) % len(pts)]
                for s in range(8):
                    f = s / 8
                    dense.append(P(*local_to_xy(g, a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)))
            d.polygon(dense, fill=(255, 220, 110, 255))
    lay = _layer_draw(g, arrows)
    a = lay[..., 3]
    gy, gx = np.gradient(a)
    edge = np.clip(np.hypot(gx, gy) * 1.6, 0, 1)
    fade = np.clip(g.v / (g.Hs * 0.15), 0, 1) * np.clip((g.Hs - g.v) / (g.Hs * 0.15), 0, 1)
    add(reg, gold * 0.75, _thin(a * scr * fade * 0.42, win, 0.6))
    add(reg, gold + 0.2, _thin(edge * scr * fade * 0.9, win, 0.4))


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
