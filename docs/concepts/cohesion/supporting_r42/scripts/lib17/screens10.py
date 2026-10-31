"""Round 10 screen content for the reworked VIRUS (afflict / poison) and PROXY (evade) slices.

Same contract as programs.py: texture(ctx, option) -> PIL RGB, W x H, y = 0 at the outer rim,
x = W/2 on the slice midline, t in [0, 1) loops. All randomness is seeded.
Brightness is held below the neighbouring programs (slicelib adds glow on top).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from slicelib import f_mono, f_ui
import programs as PR

VIOLET = np.array([200, 90, 255], np.float32) / 255
LAVENDER = np.array([0.52, 0.40, 0.66], np.float32)
GREEN = (123, 224, 123)


def _u8(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def _lowres_noise(rng, h, w, cell):
    n = rng.random((h // cell + 2, w // cell + 2)).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).resize(((w // cell + 2) * cell, (h // cell + 2) * cell), Image.BICUBIC)
    return np.asarray(im, np.float32)[:h, :w] / 255


# ------------------------------------------------------------------ VIRUS
def hex_layer(ctx, k=0.36, seed=19):
    ss, W, H = ctx.ss, ctx.W, ctx.H
    im = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(seed)
    fnt = f_mono(9 * ss)
    lh = 11 * ss
    off = (ctx.t * 4 * lh) % lh
    for r in range(-1, H // lh + 2):
        y = r * lh - off + 3 * ss
        txt = "%04X " % (0x7A00 + (r % 32) * 16) + " ".join("%02X" % v for v in rng.integers(0, 256, int(W / fnt.getlength("00 ")) + 1))
        d.text((5 * ss, y), txt, font=fnt, fill=PR.mul(ctx.col, k))
    return np.asarray(im, np.float32) / 255


def virus_infect(ctx):
    """A: violet blotches spread across a hex dump and eat it; the front glows, drips run down."""
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    rng = np.random.default_rng(41)
    txt = hex_layer(ctx)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    grow = 0.55 + 0.6 * min(1.0, t / 0.85)
    seeds = [(0.30, 0.22, 1.0), (0.68, 0.55, 0.85), (0.42, 0.86, 0.7), (0.80, 0.15, 0.55)]
    f = np.zeros((H, W), np.float32)
    for sx, sy, w in seeds:
        hx = W / 2 + (sx * 2 - 1) * ctx.halfw(sy * H) * 0.85
        r = (0.16 * max(W, H)) * w * grow
        f += np.exp(-(((xx - hx) ** 2 + (yy - sy * H) ** 2) / (r * r)))
    f += (_lowres_noise(rng, H, W, int(10 * ss)) - 0.5) * 0.5
    inf = f > 0.62
    front = np.abs(f - 0.62) < 0.05
    cs = int(5 * ss)
    gh, gw = H // cs + 1, W // cs + 1
    shade = rng.random((gh, gw)).astype(np.float32)
    blk = np.kron(shade, np.ones((cs, cs), np.float32))[:H, :W]
    rot = np.kron((rng.random((gh, gw)) < 0.16).astype(np.float32), np.ones((cs, cs), np.float32))[:H, :W]
    cell = VIOLET[None, None] * (0.14 + 0.26 * blk[..., None] ** 1.5)
    cell = cell * (1 - 0.8 * rot[..., None])
    out = txt.copy()
    out[inf] = cell[inf]
    out[front] = LAVENDER * 0.95
    # drips running down from the infected rim
    im = _u8(out)
    d = ImageDraw.Draw(im)
    for k, (u, L) in enumerate(((-0.45, 0.42), (-0.05, 0.62), (0.38, 0.35), (0.62, 0.5))):
        x = W / 2 + u * ctx.halfw(0) * 0.8
        ln = H * L * (0.6 + 0.4 * ((t * 1.3 + k * 0.27) % 1.0))
        w = (3.2 + (k % 2) * 1.6) * ss
        c = tuple(int(v * 255 * 0.5) for v in VIOLET)
        d.rectangle([x - w / 2, 0, x + w / 2, ln], fill=c)
        d.ellipse([x - w * 0.95, ln - w * 0.9, x + w * 0.95, ln + w * 1.0], fill=c)
    return im


def virus_ooze(ctx):
    """B: poison ooze slides down from the rim, drips hang and pool; data cells it touches go violet."""
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    rng = np.random.default_rng(57)
    cs = int(6 * ss)
    gh, gw = H // cs + 1, W // cs + 1
    bits = (rng.random((gh, gw)) < 0.4).astype(np.float32)
    base = np.kron(bits, np.ones((cs, cs), np.float32))[:H, :W]
    grid = np.zeros((H, W, 3), np.float32) + VIOLET * 0.035
    grid += base[..., None] * VIOLET * 0.11
    # gridlines
    grid[::cs, :] *= 0.4
    grid[:, ::cs] *= 0.4
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    band = H * 0.16
    pts = [(0, 0), (W, 0)]
    for i in range(41):
        x = W - i * W / 40
        pts.append((x, band + 6 * ss * math.sin(i * 0.9 + t * 6.28)))
    d.polygon(pts, fill=255)
    drips = [(-0.55, 0.30), (-0.25, 0.55), (0.05, 0.40), (0.30, 0.72), (0.58, 0.46)]
    tip_pts = []
    for k, (u, L) in enumerate(drips):
        x = W / 2 + u * ctx.halfw(band) * 0.85
        ln = band + (H * L - band) * (0.55 + 0.45 * ((t + k * 0.21) % 1.0))
        w = (3 + (k % 3) * 1.2) * ss
        tip_pts.append((x, ln + w * 2, w))
        d.polygon([(x - w * 1.6, band - 2 * ss), (x + w * 1.6, band - 2 * ss), (x + w / 2, band + 8 * ss), (x + w / 2, ln), (x - w / 2, ln), (x - w / 2, band + 8 * ss)], fill=255)
        d.ellipse([x - w * 0.9, ln - w * 0.8, x + w * 0.9, ln + w], fill=255)
        dy = ln + w * 2.2 + ((t * 2 + k * 0.3) % 1.0) * H * 0.2  # falling drop
        if dy < H:
            d.ellipse([x - w * 0.55, dy - w * 0.7, x + w * 0.55, dy + w * 0.6], fill=255)
    ooze = np.asarray(m, np.float32) / 255
    # cells near the ooze get infected (blurred reach)


    tips = Image.new("L", (W, H), 0)
    dt = ImageDraw.Draw(tips)
    for (tx, ty, tw) in tip_pts:  # pools where each drip lands
        dt.ellipse([tx - tw * 3, ty - tw * 0.5, tx + tw * 3, ty + tw * 3.5], fill=255)
    reach = np.asarray(tips.filter(ImageFilter.GaussianBlur(4 * ss)), np.float32) / 255
    inf = np.kron((rng.random((gh, gw)) < 0.75).astype(np.float32), np.ones((cs, cs), np.float32))[:H, :W] * (reach > 0.3)
    out = grid * (1 - inf[..., None]) + inf[..., None] * VIOLET * (0.16 + 0.12 * base[..., None])
    # glossy ooze: darker body, a lavender rim light along its lower edge and down each drip
    edge = np.clip(ooze - np.asarray(m.filter(ImageFilter.MinFilter(int(4 * ss) | 1)), np.float32) / 255, 0, 1)
    out = out * (1 - ooze[..., None]) + ooze[..., None] * VIOLET * 0.30
    out = out + edge[..., None] * LAVENDER * 0.8
    im = _u8(out)
    d2 = ImageDraw.Draw(im)
    for k in range(6):  # bubbles in the ooze band
        x = W / 2 + (rng.random() * 2 - 1) * ctx.halfw(band * 0.5) * 0.8
        y = band * (0.25 + 0.5 * rng.random())
        r = (2 + rng.random() * 3) * ss
        d2.ellipse([x - r, y - r, x + r, y + r], outline=tuple(int(v * 255 * 0.62) for v in VIOLET), width=max(1, ss))
    return im


def virus_cells(ctx):
    """C: the round 6 toned spreading-cell screen, kept as the conservative option."""
    return PR.virus(ctx)


# ------------------------------------------------------------------ PROXY
NODES = {"S": (0.0, 0.95), "a": (-0.55, 0.72), "b": (0.5, 0.74), "c": (-0.15, 0.5), "e": (0.7, 0.42),
         "f": (-0.7, 0.3), "g": (0.25, 0.25), "h": (-0.25, 0.12), "D": (0.0, 0.04)}
EDGES = [("S", "a"), ("S", "b"), ("a", "c"), ("b", "c"), ("b", "e"), ("a", "f"), ("c", "g"),
         ("c", "h"), ("e", "g"), ("f", "h"), ("g", "D"), ("h", "D"), ("f", "c")]


def _P(ctx, k, dx=0.0):
    x, y = NODES[k]
    ss, H, W = ctx.ss, ctx.H, ctx.W
    yy = y * (H - 10 * ss) + 5 * ss
    return (W / 2 + x * ctx.halfw(yy) * 0.8 + dx, yy)


def _along(pts, u):
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    L = sum(seg) * u
    for (a, b), s in zip(zip(pts, pts[1:]), seg):
        if L <= s:
            k = L / s if s else 0
            return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
        L -= s
    return pts[-1]


def proxy_hop(ctx):
    """A: the packet hops node to node; each hop leaves offset ghost copies of the route (dodge trail)."""
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    im = PR.base(ctx, 0.04)
    d = ImageDraw.Draw(im)
    for a, b in EDGES:
        d.line([_P(ctx, a), _P(ctx, b)], fill=PR.mul(ctx.col, 0.22), width=max(1, ss))
    dead = ["S", "b", "e", "g", "D"]
    live = ["S", "a", "c", "g", "D"]
    PR._dash_polyline(d, [_P(ctx, n) for n in dead], 5 * ss, 5 * ss, 0, (140, 40, 55), int(2.2 * ss))
    x, y = _P(ctx, "e")
    s_ = 7 * ss
    d.line([(x - s_, y - s_), (x + s_, y + s_)], fill=(230, 70, 90), width=int(3 * ss))
    d.line([(x - s_, y + s_), (x + s_, y - s_)], fill=(230, 70, 90), width=int(3 * ss))
    # ghost trail: the route repeated, stepped sideways and fading (the afterimage of the dodge)
    for k, kk in ((3, 0.16), (2, 0.26), (1, 0.4)):
        dx = -k * 7 * ss
        d.line([_P(ctx, n, dx) for n in live], fill=PR.mul(ctx.col, kk), width=int(3 * ss), joint="curve")
    pts = [_P(ctx, n) for n in live]
    d.line(pts, fill=PR.mul(ctx.col, 0.42), width=int(8 * ss), joint="curve")
    PR._dash_polyline(d, pts, 12 * ss, 5 * ss, t * 54 * ss, (225, 255, 215), int(4.5 * ss))
    for n in NODES:
        x, y = _P(ctx, n)
        on = n in live
        r = 5.5 * ss if on else 3 * ss
        if on:
            d.ellipse([x - r - 2 * ss, y - r - 2 * ss, x + r + 2 * ss, y + r + 2 * ss], fill=PR.mul(ctx.col, 0.7))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(240, 255, 235) if on else PR.mul(ctx.col, 0.5))
    # packet + its stepped afterimages
    u = (t * 1.0) % 1.0
    for k, kk in ((3, 0.18), (2, 0.3), (1, 0.48), (0, 1.0)):
        px, py = _along(pts, max(0.0, u - k * 0.035))
        px -= k * 7 * ss
        r = 5 * ss
        c = (255, 255, 255) if k == 0 else PR.mul(ctx.col, kk)
        d.rectangle([px - r, py - r, px + r, py + r], fill=c)
    return im


def proxy_sidestep(ctx):
    """B: a red trace beam locks straight down the screen; the green route sidesteps it,
    leaving hollow afterimages on the beam where the packet used to be."""
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    im = PR.base(ctx, 0.04)
    d = ImageDraw.Draw(im)
    cx = W / 2
    # grid of hosts
    for gy in range(int(8 * ss), H, int(16 * ss)):
        hw = ctx.halfw(gy) * 0.85
        for gx in np.arange(cx - hw, cx + hw, 16 * ss):
            d.rectangle([gx - 1 * ss, gy - 1 * ss, gx + 1 * ss, gy + 1 * ss], fill=PR.mul(ctx.col, 0.25))
    # trace beam
    d.rectangle([cx - 5 * ss, 0, cx + 5 * ss, H], fill=(70, 14, 24))
    PR._dash_polyline(d, [(cx, 0), (cx, H)], 8 * ss, 4 * ss, t * 36 * ss, (220, 60, 80), int(2.5 * ss))
    # lock reticle on the beam where the packet should have been
    ry = H * 0.5
    rr = 13 * ss
    d.ellipse([cx - rr, ry - rr, cx + rr, ry + rr], outline=(230, 70, 90), width=int(2.2 * ss))
    d.line([(cx - rr - 6 * ss, ry), (cx + rr + 6 * ss, ry)], fill=(230, 70, 90), width=int(1.6 * ss))
    # afterimages on the beam
    for k, y in enumerate((0.36, 0.5, 0.64)):
        yy = y * H
        r = 6 * ss
        d.rectangle([cx - r, yy - r, cx + r, yy + r], outline=PR.mul(ctx.col, 0.55 - k * 0.12), width=max(1, int(1.6 * ss)))
    # sidestep route: S-bend around the beam
    pts = []
    for i in range(30):
        v = i / 29
        y = H * (0.96 - 0.92 * v)
        bump = math.sin(math.pi * (v - 0.18) / 0.64) if 0.18 < v < 0.82 else 0.0
        pts.append((cx + bump ** 0.6 * ctx.halfw(y) * 0.62 if bump > 0 else cx, y))
    d.line(pts, fill=PR.mul(ctx.col, 0.42), width=int(8 * ss), joint="curve")
    PR._dash_polyline(d, pts, 12 * ss, 5 * ss, t * 54 * ss, (225, 255, 215), int(4.5 * ss))
    px, py = _along(pts, t % 1.0)
    r = 5 * ss
    d.rectangle([px - r, py - r, px + r, py + r], fill=(255, 255, 255))
    return im


def proxy_relay(ctx):
    """C: three relay hops (onion rings) with hop IPs; the tracker crosshair lags a hop behind: TRACE LOST."""
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    im = PR.base(ctx, 0.04)
    d = ImageDraw.Draw(im)
    fnt = f_mono(8 * ss)
    hops = [(-0.45, 0.82), (0.42, 0.56), (-0.3, 0.3), (0.25, 0.08)]
    pts = []
    for u, v in hops:
        y = v * H
        pts.append((W / 2 + u * ctx.halfw(y) * 0.8, y))
    for i, (x, y) in enumerate(pts):
        for rr, kk in ((13, 0.25), (9, 0.4), (5, 0.9)):
            d.ellipse([x - rr * ss, y - rr * ss, x + rr * ss, y + rr * ss], outline=PR.mul(ctx.col, kk), width=max(1, int(1.6 * ss)))
        lab = "HOP%d 185.%d.%d.%d" % (i + 1, 20 + i * 37, 11 + i * 50, 3 + i * 61)
        lx = x + (16 * ss if hops[i][0] < 0 else -16 * ss - fnt.getlength(lab))
        d.text((lx, y - 5 * ss), lab, font=fnt, fill=PR.mul(ctx.col, 0.6))
    d.line(pts, fill=PR.mul(ctx.col, 0.42), width=int(7 * ss), joint="curve")
    PR._dash_polyline(d, pts, 10 * ss, 5 * ss, t * 45 * ss, (225, 255, 215), int(4 * ss))
    # tracker crosshair stuck at hop 1
    x, y = pts[0]
    c = (220, 60, 80)
    r = 15 * ss
    d.ellipse([x - r, y - r, x + r, y + r], outline=c, width=int(2 * ss))
    d.line([(x - r - 5 * ss, y), (x + r + 5 * ss, y)], fill=c, width=max(1, int(1.4 * ss)))
    d.line([(x, y - r - 5 * ss), (x, y + r + 5 * ss)], fill=c, width=max(1, int(1.4 * ss)))
    s = "TRACE LOST"
    d.text((W / 2 - fnt.getlength(s) / 2, H * 0.93), s, font=fnt, fill=c)
    px, py = _along(pts, 0.35 + 0.65 * (t % 1.0))
    for k, kk in ((2, 0.25), (1, 0.45), (0, 1.0)):
        qx, qy = _along(pts, max(0.0, 0.35 + 0.65 * (t % 1.0) - k * 0.05))
        rr = 5 * ss
        d.rectangle([qx - rr, qy - rr, qx + rr, qy + rr], fill=(255, 255, 255) if k == 0 else PR.mul(ctx.col, kk))
    return im


# ------------------------------------------------------------------ round 11
def proxy_turn(ctx):
    """EVADE (round 11): a road-sign detour. A bold white route arrow runs up the screen, hits a striped
    barrier and turns hard 90 degrees; the packet takes the turn, its afterimages trailing on the bend."""
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    im = PR.base(ctx, 0.05)
    d = ImageDraw.Draw(im)
    # faint street grid behind the sign
    for gy in range(int(10 * ss), H, int(22 * ss)):
        d.line([(0, gy), (W, gy)], fill=PR.mul(ctx.col, 0.13), width=int(3 * ss))
    for gx in np.arange(W / 2 - 3 * 22 * ss, W, 22 * ss):
        d.line([(gx, 0), (gx, H)], fill=PR.mul(ctx.col, 0.10), width=int(3 * ss))
    hw = ctx.halfw(H * 0.5)
    # sign panel: rounded road-sign plate with a white border
    px0, px1 = W / 2 - hw * 0.78, W / 2 + hw * 0.78
    py0, py1 = H * 0.06, H * 0.97
    d.rounded_rectangle([px0, py0, px1, py1], radius=int(10 * ss), fill=PR.mul(ctx.col, 0.16))
    # route arrow: up the left lane (beside the value block), hard right turn along the top, arrowhead
    sw = 12 * ss
    xs = W / 2 - hw * 0.62
    yt = H * 0.15
    xe = W / 2 + hw * 0.66
    white = (222, 242, 222)
    d.rectangle([xs - sw / 2, yt - sw / 2, xs + sw / 2, py1 - 6 * ss], fill=white)
    d.rectangle([xs - sw / 2, yt - sw / 2, xe - 10 * ss, yt + sw / 2], fill=white)
    d.polygon([(xe - 14 * ss, yt - sw * 1.5), (xe + 8 * ss, yt), (xe - 14 * ss, yt + sw * 1.5)], fill=white)
    # the road it left: a struck-out stub carrying on down-right from the shaft (road closed)
    by = H * 0.80
    bx0, bx1 = xs + sw * 1.2, xs + sw * 5.2
    d.rectangle([bx0, by - 4 * ss, bx1, by + 4 * ss], fill=(235, 235, 235))
    n = 6
    for k in range(n):
        if k % 2 == 0:
            a = bx0 + (bx1 - bx0) * k / n
            d.polygon([(a, by - 4 * ss), (a + (bx1 - bx0) / n, by - 4 * ss), (a + (bx1 - bx0) / n - 4 * ss, by + 4 * ss), (a - 4 * ss, by + 4 * ss)], fill=(225, 60, 70))
    # packet taking the turn + afterimages
    path = [(xs, py1 - 10 * ss), (xs, yt), (xe - 12 * ss, yt)]
    u = 0.15 + 0.8 * (t % 1.0)
    for k, kk in ((3, 0.25), (2, 0.42), (1, 0.62), (0, 1.0)):
        qx, qy = _along(path, max(0.0, u - k * 0.06))
        r = 5.5 * ss
        if k == 0:
            d.rectangle([qx - r - 2 * ss, qy - r - 2 * ss, qx + r + 2 * ss, qy + r + 2 * ss], fill=PR.mul(ctx.col, 0.9))
            d.rectangle([qx - r, qy - r, qx + r, qy + r], fill=(255, 255, 255))
        else:
            d.rectangle([qx - r, qy - r, qx + r, qy + r], outline=PR.mul(ctx.col, kk), width=max(1, int(2 * ss)))
    return im


MASK_COL = (196, 204, 226)


def _mask_img(size):
    import glyphs10
    m = glyphs10.mask_guy().resize((int(size), int(size)), Image.LANCZOS)
    return m


def mask_big(ctx):
    """Mask backdrop A: one large faint mask on the CRT, with a glitch band and RGB split."""
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    rng = np.random.default_rng(int(t * 24) + 300)
    base = np.zeros((H, W, 3), np.float32) + np.array(MASK_COL, np.float32) / 255 * 0.05
    s = int(min(W * 0.95, H * 1.25))
    m = np.asarray(_mask_img(s), np.float32) / 255
    lay = np.zeros((H, W), np.float32)
    x0, y0 = (W - s) // 2, int(H * 0.5 - s * 0.5)
    ys0, ys1 = max(0, y0), min(H, y0 + s)
    xs0, xs1 = max(0, x0), min(W, x0 + s)
    lay[ys0:ys1, xs0:xs1] = m[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0]
    col = np.array(MASK_COL, np.float32) / 255
    out = base + lay[..., None] * col * 0.30
    for _ in range(3):  # glitch bands
        y = int(rng.integers(0, H - 8 * ss))
        hgt = int(rng.integers(3 * ss, 9 * ss))
        out[y:y + hgt] = np.roll(out[y:y + hgt], int(rng.integers(-12, 13) * ss), axis=1)
    sh = int(2.5 * ss)
    out[..., 0] = np.roll(out[..., 0], sh, axis=1)
    out[..., 2] = np.roll(out[..., 2], -sh, axis=1)
    return _u8(out)


def mask_crowd(ctx):
    """Mask backdrop B: a crowd of small masks (anonymous), one of them lit."""
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    im = Image.new("RGB", (W, H), tuple(int(v * 0.05) for v in MASK_COL))
    s = int(26 * ss)
    m = _mask_img(s)
    dim = Image.new("RGB", (s, s), tuple(int(v * 0.22) for v in MASK_COL))
    hot = Image.new("RGB", (s, s), tuple(int(v * 0.75) for v in MASK_COL))
    lit = (int(t * 7) % 5, 2)
    for r, y in enumerate(range(int(2 * ss), H, int(s * 1.05))):
        off = (s // 2) if r % 2 else 0
        for c, x in enumerate(range(-s + off, W, int(s * 0.95))):
            im.paste(hot if (c % 5, r % 4) == lit else dim, (x, y), m)
    return im


SCREENS = {("VIRUS", "A"): virus_infect, ("VIRUS", "B"): virus_ooze, ("VIRUS", "C"): virus_cells,
           ("PROXY", "A"): proxy_hop, ("PROXY", "B"): proxy_sidestep, ("PROXY", "C"): proxy_relay,
           ("PROXY", "OLD"): PR.proxy, ("VIRUS", "OLD"): PR.virus,
           # round 11 picks
           ("PROXY", "TURN"): proxy_turn, ("VIRUS", "OOZE"): virus_ooze, ("VIRUS", "BURN"): virus_infect,
           ("MASKBG", "BIG"): mask_big, ("MASKBG", "CROWD"): mask_crowd}
GLYPHS = {("VIRUS", "A"): "VIAL", ("VIRUS", "B"): "SKULLDROP", ("VIRUS", "C"): "BIOHAZ",
          ("PROXY", "A"): "MASK", ("PROXY", "B"): "DODGE", ("PROXY", "C"): "MASK",
          ("VIRUS", "OLD"): "VIRUS", ("PROXY", "OLD"): "PROXY",
          ("PROXY", "TURN"): "PROXY", ("VIRUS", "OOZE"): "BIOHAZ", ("VIRUS", "BURN"): "VIRUS",
          ("MASKBG", "BIG"): "MASKBG", ("MASKBG", "CROWD"): "MASKBG"}


def texture(ctx, option):
    return SCREENS[(ctx.prog, option)](ctx)


def select(virus=None, proxy=None, maskbg=None):
    """Pick the rework options used by the next renders (clears the glyph cache)."""
    import slicelib as SL
    for prog, opt in (("VIRUS", virus), ("PROXY", proxy), ("MASKBG", maskbg)):
        if opt is None:
            PR.TEX_VARIANT.pop(prog, None)
            SL.GLYPH_OVERRIDE.pop(prog, None)
        else:
            PR.TEX_VARIANT[prog] = opt
            if GLYPHS[(prog, opt)] == prog:
                SL.GLYPH_OVERRIDE.pop(prog, None)
            else:
                SL.GLYPH_OVERRIDE[prog] = GLYPHS[(prog, opt)]
    SL._glyph_cache.clear()


