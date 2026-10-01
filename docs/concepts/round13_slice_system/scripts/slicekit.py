"""Round 13 slice kit: one slice = screen (slicelib) -> TIER bezel/screen pass -> STATE overlay layer
-> upright read block (glyph + value) -> overlay front marks (status badge, chips).

The order mirrors the Godot build in NOTES.md: the slice's own ShaderMaterial does the tier
(uniform `tier`), the overlay is a separate CanvasItem with its own shader, and the read block is
the topmost child, so no overlay can ever cover the value.
"""
import math
import numpy as np
from PIL import Image, ImageDraw

import slicelib as SL
from slicelib import R_OUT, R_IN, PROGRAMS, c01, round_min, smooth, paste_rgba

GOLD = np.array([1.0, 0.80, 0.36], np.float32)
TIER_GAIN = {1: 0.70, 2: 1.0, 3: 1.22}

_ready = False


def setup():
    """Round 11 choices: VIRUS = ooze + biohazard, PROXY = road-sign turn + double chevron."""
    global _ready
    if not _ready:
        import screens10
        screens10.select(virus="OOZE", proxy="TURN")
        _ready = True


# ------------------------------------------------------------------ noise (deterministic, loopable)
def _hash(ix, iy, seed):
    h = np.sin(ix * 127.1 + iy * 311.7 + seed * 74.7) * 43758.5453
    return h - np.floor(h)


def vnoise(x, y, seed=0):
    ix, iy = np.floor(x), np.floor(y)
    fx, fy = x - ix, y - iy
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    a = _hash(ix, iy, seed)
    b = _hash(ix + 1, iy, seed)
    c = _hash(ix, iy + 1, seed)
    d = _hash(ix + 1, iy + 1, seed)
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def fbm(x, y, seed=0, octaves=4):
    v, amp, tot = 0.0, 0.5, 0.0
    for o in range(octaves):
        v = v + amp * vnoise(x, y, seed + o * 13)
        tot += amp
        x, y, amp = x * 2.03, y * 2.03, amp * 0.5
    return v / tot


def loop_off(t, r=3.0):
    """Offset on a circle: sampling noise at p + loop_off(t) makes a seamless loop over t in [0,1)."""
    return r * math.cos(2 * math.pi * t), r * math.sin(2 * math.pi * t)


# ------------------------------------------------------------------ geometry (same as render_slice)
class Geom:
    pass


def geom(shape, cx, cy, a0, span, ss, pad_out=0.0):
    g = Geom()
    Ro, Ri = R_OUT * ss, R_IN * ss
    gap, bw = 1.6 * ss, 8.5 * ss
    mid, half = a0 + span / 2, span / 2
    R = Ro + pad_out
    angs = np.radians(np.linspace(a0 - 4, a0 + span + 4, 40))
    pts = [(cx + r * np.sin(a), cy - r * np.cos(a)) for r in (Ri * 0.9, R) for a in angs]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    g.x0, g.x1 = int(max(0, min(xs) - 2)), int(min(shape[1], max(xs) + 3))
    g.y0, g.y1 = int(max(0, min(ys) - 2)), int(min(shape[0], max(ys) + 3))
    yy, xx = np.mgrid[g.y0:g.y1, g.x0:g.x1].astype(np.float32)
    g.xx, g.yy = xx, yy
    dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
    g.rho = np.hypot(dx, dy)
    g.th = np.degrees(np.arctan2(dx, -dy)) % 360
    g.d = ((g.th - mid + 180) % 360) - 180
    e_side = g.rho * np.sin(np.radians(np.clip(half - np.abs(g.d), -90, 90))) - gap
    e_out = Ro - gap - g.rho
    e_in = g.rho - Ri - gap
    g.e_side, g.e_out, g.e_in = e_side, e_out, e_in
    g.e_tile = round_min(round_min(e_side, e_out, 4 * ss), e_in, 4 * ss)
    g.e_scr = round_min(round_min(e_side - bw, e_out - bw, 11 * ss), e_in - bw * 0.85, 9 * ss)
    g.a_tile = np.clip(g.e_tile, 0, 1)
    g.a_scr = np.clip(g.e_scr + 0.5, 0, 1)
    g.bez = g.a_tile * (1 - g.a_scr)
    g.r_out_s = Ro - gap - bw
    g.r_in_s = Ri + gap + bw * 0.85
    g.Hs = g.r_out_s - g.r_in_s
    g.u = g.rho * np.radians(g.d)
    g.v = g.r_out_s - g.rho
    g.halfw = g.rho * np.sin(np.radians(half))  # lateral half width at this radius (approx)
    g.cx, g.cy, g.mid, g.half, g.span, g.ss, g.bw, g.gap, g.Ro, g.Ri = cx, cy, mid, half, span, ss, bw, gap, Ro, Ri
    g.inside_wedge = (np.abs(g.d) <= half).astype(np.float32)
    return g


def region(canvas, g):
    return canvas[g.y0:g.y1, g.x0:g.x1]


def over(reg, rgb, a):
    """Premultiplied 'over' of colour rgb (H,W,3 or 3) with alpha a (H,W)."""
    a = np.clip(a, 0, 1)[..., None]
    reg[..., :3] = reg[..., :3] * (1 - a) + rgb * a
    reg[..., 3:] = reg[..., 3:] * (1 - a) + a


def add(reg, rgb, a):
    a = np.clip(a, 0, None)[..., None]
    reg[..., :3] = reg[..., :3] + rgb * a
    reg[..., 3:] = np.maximum(reg[..., 3:], np.clip(a * 0.9, 0, 1))


def polar(g, rho, ang_deg):
    return g.cx + rho * math.sin(math.radians(ang_deg)), g.cy - rho * math.cos(math.radians(ang_deg))


def local_to_xy(g, u, v):
    """Tile-local (u = arc length from the midline, v = depth from the outer screen edge) -> canvas xy."""
    rho = g.r_out_s - v
    ang = g.mid + math.degrees(u / max(rho, 1))
    return polar(g, rho, ang)


# ------------------------------------------------------------------ tiers
def tier_pass(canvas, g, tier, col, t, seed=0):
    """Tier I plain / II trimmed steel / III gilded holo-circuit. Screen activity scales with tier."""
    reg = region(canvas, g)
    ss = g.ss
    scr = g.a_scr * g.a_tile
    rgb = reg[..., :3]
    if tier == 1:  # quieter screen: a little desaturated
        lum = rgb.mean(axis=2, keepdims=True)
        mix = (0.30 * scr)[..., None]
        reg[..., :3] = rgb * (1 - mix) + lum * mix
    light = 0.80 + 0.35 * np.cos(np.radians(g.th - 315))
    tang = g.u / ss  # along the bezel
    if tier == 2:
        n = vnoise(tang * 0.9, g.rho / ss * 0.05, seed + 3)  # brushed steel
        steel = (0.40 + 0.12 * n)[..., None] * np.array([0.92, 0.96, 1.04], np.float32) * light[..., None]
        over(reg, steel, g.bez * 0.92)
        trim = np.exp(-((g.e_scr + g.bw * 0.5) / (1.3 * ss)) ** 2) * g.bez
        add(reg, col * 1.15, trim)
        # corner brackets: brighter, thicker trim near the four corners
        near_side = np.clip(1 - (g.e_side - g.bw * 0.5) / (22 * ss), 0, 1)
        near_rad = np.clip(1 - np.minimum(g.e_out, g.e_in) / (34 * ss), 0, 1)
        corner = (near_side > 0) & (near_rad > 0)
        br = np.exp(-((g.e_scr + g.bw * 0.5) / (2.0 * ss)) ** 2) * g.bez * corner
        add(reg, np.array([1, 1, 1], np.float32) * 0.6 + col * 0.6, br)
        lip = np.exp(-(g.e_tile / (1.0 * ss)) ** 2) * g.a_tile
        add(reg, np.array([0.9, 0.95, 1.0], np.float32), lip * 0.35)
    if tier == 3:
        gold = GOLD[None, None, :] * (0.42 + 0.30 * light)[..., None]
        sheen = np.exp(-(((g.th - 300) % 360 - 180) / 40) ** 2)  # broad specular band
        gold = gold + sheen[..., None] * 0.25
        over(reg, gold, g.bez * 0.95)
        # etched circuit: a trace along the band with vias and stubs
        mid_band = g.e_scr + g.bw * 0.52
        trace = np.exp(-(mid_band / (0.75 * ss)) ** 2)
        per = 24.0 * ss
        ph = (g.u + 1000 * ss) % per
        gaps = ((ph > per * 0.62) & (ph < per * 0.72))
        trace = trace * (~gaps)
        via = np.exp(-((np.hypot(ph - per * 0.6, mid_band)) / (1.5 * ss)) ** 2)
        etch = np.clip(trace + via, 0, 1) * g.bez
        over(reg, np.array([0.30, 0.18, 0.04], np.float32), etch * 0.8)
        # holo lip: hue walks around the rim and drifts with t
        hue = (g.th / 60.0 + t * 1.0) % 1.0
        holo = np.stack([0.5 + 0.5 * np.cos(2 * np.pi * (hue + k / 3)) for k in range(3)], -1)
        lip = np.exp(-(g.e_tile / (1.4 * ss)) ** 2) * g.a_tile
        add(reg, holo.astype(np.float32), lip * 1.1)
        hair = np.exp(-((g.e_scr + 1.3 * ss) / (0.9 * ss)) ** 2) * g.a_tile
        add(reg, np.array([1.0, 0.9, 0.6], np.float32), hair * 0.7)
        # screen: a diagonal holo sweep + data sparkles (activity)
        sw = (g.u / ss * 0.6 + g.v / ss) / 260.0 - (t % 1.0) * 1.6 + 0.3
        band = np.exp(-(sw / 0.05) ** 2) * scr
        add(reg, col * 0.5 + 0.25, band * 0.35)
        sp = vnoise(g.u / (3 * ss), g.v / (3 * ss), seed + int(t * 12) * 7)
        add(reg, col * 0.9 + 0.2, np.clip((sp - 0.93) * 14, 0, 1) * scr * 0.8)
    if tier == 1:  # plain: matte, the hairline dimmed
        over(reg, np.array([0.07, 0.065, 0.085], np.float32) * light[..., None], g.bez * 0.55)
    # tier tab: a small plate notched into the top of the screen, carrying 1 / 2 / 3 pips
    metal = {1: np.array([0.45, 0.45, 0.5], np.float32), 2: col * 0.6 + 0.4, 3: GOLD * 1.1}[tier]
    pc = {1: np.array([0.80, 0.80, 0.85], np.float32), 2: col * 0.45 + 0.6, 3: np.array([1.0, 0.95, 0.75], np.float32)}[tier]
    sp = 9.0 * ss
    tw = (tier - 1) * sp / 2 + 7.5 * ss
    vt0, vt1 = -g.bw * 0.6, 7.0 * ss
    du_t = np.abs(g.u) - tw
    dv_t = np.maximum(vt0 - g.v, g.v - vt1)
    e_tab = np.maximum(du_t, dv_t)
    tab = np.clip(-e_tab / (0.8 * ss) + 0.5, 0, 1) * g.a_tile
    over(reg, np.array([0.035, 0.03, 0.05], np.float32), tab * 0.96)
    rim_t = np.exp(-((e_tab + 0.8 * ss) / (0.8 * ss)) ** 2) * (g.v > vt0 + 1.5 * ss) * g.a_tile
    over(reg, metal, rim_t)
    vc = (vt0 + vt1) / 2 + 0.6 * ss
    for k in range(tier):
        off = (k - (tier - 1) / 2) * sp
        dm = (np.abs(g.u - off) + np.abs(g.v - vc)) - 3.6 * ss
        over(reg, pc, np.clip(-dm / (0.8 * ss) + 0.5, 0, 1) * g.a_tile)
        add(reg, pc * 0.5, np.exp(-(np.maximum(dm, 0) / (2.5 * ss)) ** 2) * g.a_tile * (0.25 if tier == 1 else 0.5))


# ------------------------------------------------------------------ the read window (overlays thin out over it)
def read_window(g, blk, px, py, k=1.0):
    bcx, bcy = px + blk.width / 2, py + blk.height / 2
    ax, ay = blk.width * 0.44 + 4 * g.ss, blk.height * 0.42 + 3 * g.ss
    q = ((g.xx + 0.5 - bcx) / ax) ** 2 + ((g.yy + 0.5 - bcy) / ay) ** 2
    return np.clip(1.6 - q, 0, 1) * k


# ------------------------------------------------------------------ one slice
def draw_slice(canvas, cx, cy, prog, a0, span, value, t, ss=2, tier=2, state=None, seed=0, badge=None):
    import overlays
    setup()
    defer = []
    opts = dict(upright=True, defer=defer, tex_gain=TIER_GAIN[tier])
    SL.render_slice(canvas, cx, cy, prog, a0, span, value, t, "player", ss, opts, seed, badge=badge)
    col = c01(PROGRAMS[prog]["col"])
    g = geom(canvas.shape, cx, cy, a0, span, ss, pad_out=(34 * ss if state else 0))
    tier_pass(canvas, g, tier, col, t, seed)
    blk, px, py = defer[0]
    win = read_window(g, blk, px, py)
    if state:
        overlays.apply(canvas, g, state, col, t, seed, win)
    paste_rgba(canvas, blk, px, py)
    if state:
        overlays.front(canvas, g, state, t, seed)


def to_rgba(canvas):
    return Image.fromarray((np.clip(canvas, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")


def tile(prog, value, t=0.5, tier=2, state=None, ss=2, scale=0.6, span=60, seed=3):
    """Hero tile pointing up (with headroom for flames), RGBA at master*scale."""
    pad_top = 40 if state else 8
    pad = 10
    Ro = R_OUT * ss
    half = math.radians(span / 2)
    w = int(2 * Ro * math.sin(half) + 2 * pad * ss + 40 * ss)
    h = int(Ro - R_IN * ss * math.cos(half) + (pad + pad_top) * ss)
    cx, cy = w / 2, Ro + pad_top * ss
    canvas = np.zeros((h, w, 4), np.float32)
    draw_slice(canvas, cx, cy, prog, -span / 2, span, value, t, ss, tier, state, seed)
    im = to_rgba(canvas)
    return im.resize((int(w / ss * scale), int(h / ss * scale)), Image.LANCZOS)


def wheel(slices, t=0.5, ss=2, r_px=60, seed=5):
    """slices: list of 6 (prog, value, tier, state). Plain backing ring + hub (the frame is another agent's)."""
    setup()
    M = 48
    Ro = R_OUT * ss
    S = int(2 * (Ro + M * ss))
    c = S / 2
    canvas = np.zeros((S, S, 4), np.float32)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([c - Ro - 8 * ss, c - Ro - 8 * ss, c + Ro + 8 * ss, c + Ro + 8 * ss], fill=(16, 14, 22, 255), outline=(70, 66, 90, 255), width=int(3 * ss))
    canvas[:] = np.asarray(im, np.float32) / 255
    n = len(slices)
    span = 360 / n
    for i, (prog, val, tier, state) in enumerate(slices):
        draw_slice(canvas, c, c, prog, i * span - span / 2, span, val, t, ss, tier, state, seed + i)
    out = to_rgba(canvas)
    d = ImageDraw.Draw(out)
    hr = R_IN * ss - 6 * ss
    d.ellipse([c - hr, c - hr, c + hr, c + hr], fill=(14, 12, 20, 255), outline=(90, 84, 120, 255), width=int(4 * ss))
    k = r_px / R_OUT / ss
    return out.resize((int(S * k), int(S * k)), Image.LANCZOS)
