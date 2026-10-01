"""Screen textures: one function per program (player) plus the Meridian dashboard set.

Every function gets a Ctx (W, H, t in [0,1) looping, ss, span, col, ...) and returns
a PIL RGB image W x H. y = 0 is the outer rim, x = W/2 is the slice midline.
All randomness is seeded (numpy default_rng with fixed seeds).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from slicelib import f_mono, f_ui, f_num, glyph_mask, MERIDIAN, MERIDIAN_DIM, PROGRAMS


def mul(c, k):
    return tuple(int(max(0, min(255, v * k))) for v in c)


def mix(a, b, k):
    return tuple(int(a[i] * (1 - k) + b[i] * k) for i in range(3))


def base(ctx, k=0.07):
    return Image.new("RGB", (ctx.W, ctx.H), mul(ctx.col, k))


def tri(x):
    x = x % 1.0
    return 1 - abs(2 * x - 1)


# ================================================================== player programs
def exploit(ctx):
    ss, t = ctx.ss, ctx.t
    im = base(ctx, 0.06)
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(11)
    lh = 11 * ss
    fnt = f_mono(9 * ss)
    N = 16
    lines = []
    for i in range(N):
        addr = 0x3F00 + i * 16
        bytes_ = " ".join("%02X" % v for v in rng.integers(0, 256, 8))
        lines.append(("%04X" % addr, bytes_))
    inject = 5
    off = t * N * lh
    base_i = int(off // lh)
    frac = off - base_i * lh
    flash = 0.5 + 0.5 * math.cos(2 * math.pi * (t * 4))  # 4 flashes per loop
    rows = ctx.H // lh + 2
    for r in range(-1, rows):
        i = (r + base_i) % N
        y = r * lh - frac + 3 * ss
        a, b = lines[i]
        if i == inject:
            bar = mix((255, 40, 90), (255, 200, 230), flash * 0.35)
            d.rectangle([0, y - 1 * ss, ctx.W, y + lh - 2 * ss], fill=mul(bar, 0.55 + 0.45 * flash))
            d.text((6 * ss, y), a + "  JMP 0xDEAD ;inj", font=fnt, fill=(255, 245, 250))
        else:
            d.text((6 * ss, y), a, font=fnt, fill=mul(ctx.col, 0.45))
            d.text((6 * ss + fnt.getlength(a + "  "), y), b, font=fnt, fill=mul(ctx.col, 0.85))
    # whole-screen red-pink code flash
    if flash > 0.85:
        ov = Image.new("RGB", im.size, (255, 30, 90))
        im = Image.blend(im, ov, 0.18 * (flash - 0.85) / 0.15)
    return im


def skull_mask(W, H, cx, cy, s):
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([cx - s, cy - s * 1.05, cx + s, cy + s * 0.75], fill=255)
    d.rounded_rectangle([cx - s * 0.62, cy + s * 0.35, cx + s * 0.62, cy + s * 1.15], radius=s * 0.15, fill=255)
    for ex in (-0.42, 0.42):
        d.ellipse([cx + ex * s - s * 0.3, cy - s * 0.25, cx + ex * s + s * 0.3, cy + s * 0.3], fill=0)
    d.polygon([(cx, cy + s * 0.38), (cx - s * 0.14, cy + s * 0.62), (cx + s * 0.14, cy + s * 0.62)], fill=0)
    for tx in (-0.36, -0.12, 0.12, 0.36):
        d.line([(cx + tx * s, cy + s * 0.8), (cx + tx * s, cy + s * 1.15)], fill=0, width=max(1, int(s * 0.08)))
    return np.asarray(m, np.float32) / 255


def zero_day(ctx):
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    frame = int(t * 24)
    rng = np.random.default_rng(1000 + frame)
    cell = 2 * ss
    nz = rng.random((H // cell + 1, W // cell + 1)).astype(np.float32)
    nz = np.kron(nz, np.ones((cell, cell), np.float32))[:H, :W]
    # resolve curve: noise -> skull (0..0.55), hold, then a hard glitch tear back
    if t < 0.55:
        r = (t / 0.55) ** 1.5
    elif t < 0.8:
        r = 1.0
    else:
        r = max(0.0, 1 - (t - 0.8) / 0.2 * 1.3)
    sk = skull_mask(W, H, W / 2, H * 0.47, min(W * 0.3, H * 0.33))
    hot = np.array([255, 120, 215], np.float32) / 255
    white = np.array([1, 1, 1], np.float32)
    lum = nz * (1 - r) * 0.75 + sk * r
    rgb = lum[..., None] * (white * 0.55 + hot * 0.45)
    rgb += (sk * r)[..., None] * hot * 0.3
    # glitch: band offsets + RGB split, strongest while unresolved
    g = (1 - r) * 0.8 + 0.2 + (0.6 if 0.8 <= t < 0.86 else 0)
    out = rgb.copy()
    shift = int(g * 6 * ss) + 1
    out[..., 0] = np.roll(rgb[..., 0], shift, axis=1)
    out[..., 2] = np.roll(rgb[..., 2], -shift, axis=1)
    nb = 5
    for i in range(nb):
        y0 = int(rng.integers(0, H - 4 * ss))
        hgt = int(rng.integers(2 * ss, 10 * ss))
        dx = int(rng.integers(-14, 15) * ss * g)
        out[y0:y0 + hgt] = np.roll(out[y0:y0 + hgt], dx, axis=1)
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def firewall(ctx):
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    im = base(ctx, 0.05)
    d = ImageDraw.Draw(im)
    fnt = f_mono(10 * ss)
    brick = "[#]"
    bw = fnt.getlength(brick)
    lh = 12 * ss
    wall_rows = int(H * 0.58 // lh)
    y_wall = wall_rows * lh + 2 * ss
    packets = [(-0.32, 0.0), (0.05, 0.33), (0.28, 0.66), (-0.1, 0.5)]
    hits = []
    for px, ph in packets:
        u = (t * 2 + ph) % 1.0
        y = y_wall + (H - y_wall) * (1 - tri(u)) * 0.95 + 3 * ss
        x = W / 2 + px * W * 0.5
        hits.append((x, max(0.0, 1 - abs(y - y_wall) / (16 * ss))))
    for r in range(wall_rows):
        y = r * lh + 2 * ss
        off = (bw / 2) if r % 2 else 0
        n = int(W // bw) + 2
        for k in range(-1, n):
            x = k * bw + off
            heat = 0.0
            if r >= wall_rows - 2:
                for hx, hk in hits:
                    if abs(x + bw / 2 - hx) < bw * 1.2:
                        heat = max(heat, hk * (1.0 if r == wall_rows - 1 else 0.5))
            c = mix(mul(ctx.col, 0.7 - 0.06 * (r % 3)), (255, 255, 255), heat)
            d.text((x, y), brick, font=fnt, fill=c)
    # floor line of the wall
    d.line([(0, y_wall - 1 * ss), (W, y_wall - 1 * ss)], fill=mul(ctx.col, 0.9), width=max(1, ss))
    for (x, hk), (px, ph) in zip(hits, packets):
        u = (t * 2 + ph) % 1.0
        y = y_wall + (H - y_wall) * (1 - tri(u)) * 0.95 + 3 * ss
        for k in range(4):  # trail
            yy = y + k * 4 * ss * (1 if (u % 1) < 0.5 else -1)
            d.rectangle([x - 2 * ss, yy - 2 * ss, x + 2 * ss, yy + 2 * ss], fill=mul((255, 70, 120), 1 - k * 0.25))
        if hk > 0.3:
            d.line([(x - 8 * ss * hk, y_wall + 2 * ss), (x + 8 * ss * hk, y_wall + 2 * ss)], fill=(255, 255, 255), width=ss)
    return im


def sandbox(ctx):
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    im = base(ctx, 0.05)
    d = ImageDraw.Draw(im)
    br = 0.5 + 0.5 * math.sin(2 * math.pi * t)
    cx, cy = W / 2, H * 0.48
    w, h = W * 0.92, H * 0.92
    step = 0.80 + 0.04 * br
    fnt = f_mono(8 * ss)
    for lvl in range(6):
        k = 1.0 - lvl * 0.12
        c = mul(ctx.col, (0.55 + 0.45 * br) * k)
        x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
        d.rounded_rectangle([x0, y0, x1, y1], radius=4 * ss, outline=c, width=max(1, int(1.6 * ss)))
        tb = max(4 * ss, h * 0.07)
        d.rectangle([x0, y0, x1, y0 + tb], fill=mul(c, 0.45))
        for j in range(3):
            r = tb * 0.22
            ex = x0 + tb * 0.6 + j * tb * 0.65
            d.ellipse([ex - r, y0 + tb / 2 - r, ex + r, y0 + tb / 2 + r], fill=c)
        if lvl < 3:
            d.text((x0 + 3 * ss, y1 - 11 * ss), "$ run ./box%d" % lvl, font=fnt, fill=mul(c, 0.8))
        w *= step
        h *= step
        cy += tb * 0.35
    # breathing core
    r = 4 * ss * (1 + br)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=mix(ctx.col, (255, 255, 255), 0.5 * br))
    return im


def _dash_polyline(d, pts, dash, gap, off, fill, width):
    period = dash + gap
    acc = -off % period - period
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        s = acc
        while s < L:
            a, b = max(0, s), min(L, s + dash)
            if b > a:
                d.line([(x0 + (x1 - x0) * a / L, y0 + (y1 - y0) * a / L),
                        (x0 + (x1 - x0) * b / L, y0 + (y1 - y0) * b / L)], fill=fill, width=width)
            s += period
        acc = s - L - period


def proxy(ctx):
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    im = base(ctx, 0.05)
    d = ImageDraw.Draw(im)
    # node layout in normalised coords (x in -1..1 of the local half-width, y 0..1)
    N = {
        "S": (0.0, 0.95), "a": (-0.55, 0.72), "b": (0.5, 0.74), "c": (-0.15, 0.5),
        "e": (0.7, 0.42), "f": (-0.7, 0.3), "g": (0.25, 0.25), "h": (-0.25, 0.12), "D": (0.0, 0.04),
    }

    def P(k):
        x, y = N[k]
        yy = y * (H - 10 * ss) + 5 * ss
        return (W / 2 + x * ctx.halfw(yy) * 0.8, yy)

    edges = [("S", "a"), ("S", "b"), ("a", "c"), ("b", "c"), ("b", "e"), ("a", "f"), ("c", "g"),
             ("c", "h"), ("e", "g"), ("f", "h"), ("g", "D"), ("h", "D"), ("f", "c")]
    for a, b in edges:
        d.line([P(a), P(b)], fill=mul(ctx.col, 0.28), width=max(1, ss))
    route1 = ["S", "a", "c", "g", "D"]
    route2 = ["S", "b", "e", "g", "D"]
    route3 = ["S", "a", "f", "h", "D"]
    phase = t * 3
    k = int(phase) % 3
    route = [route1, route2, route3][k]
    local = phase - int(phase)
    off = local * 3 * 18 * ss
    dead = [route3, route1, route2][k]  # the route just abandoned
    # round 6: bolder reroute. The abandoned path stays as a red broken trace with an X,
    # the live path is a thick glowing underlay + bright marching dashes + arrowheads.
    _dash_polyline(d, [P(n) for n in dead], 5 * ss, 5 * ss, 0, (150, 40, 60), int(2.2 * ss))
    dd = dead[2]
    x, y = P(dd)
    s_ = 7 * ss
    d.line([(x - s_, y - s_), (x + s_, y + s_)], fill=(255, 70, 90), width=int(3 * ss))
    d.line([(x - s_, y + s_), (x + s_, y - s_)], fill=(255, 70, 90), width=int(3 * ss))
    pts = [P(n) for n in route]
    d.line(pts, fill=mul(ctx.col, 0.45), width=int(8 * ss), joint="curve")
    _dash_polyline(d, pts, 12 * ss, 5 * ss, off, (225, 255, 215), int(4.5 * ss))
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        L = math.hypot(x1 - x0, y1 - y0) or 1
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        a = 7 * ss
        d.polygon([(mx + ux * a, my + uy * a), (mx - ux * a * 0.6 - uy * a * 0.8, my - uy * a * 0.6 + ux * a * 0.8),
                   (mx - ux * a * 0.6 + uy * a * 0.8, my - uy * a * 0.6 - ux * a * 0.8)], fill=(255, 255, 255))
    for n in N:
        x, y = P(n)
        r = 5.5 * ss if n in route else 3 * ss
        c = (240, 255, 235) if n in route else mul(ctx.col, 0.55)
        if n in route:
            d.ellipse([x - r - 2 * ss, y - r - 2 * ss, x + r + 2 * ss, y + r + 2 * ss], fill=mul(ctx.col, 0.7))
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    return im


def patch(ctx):
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    im = base(ctx, 0.05)
    d = ImageDraw.Draw(im)
    fill = min(1.0, t / 0.8)
    done = t >= 0.8
    fnt = f_mono(9 * ss)
    hw = ctx.halfw(14 * ss) * 0.8
    x0, x1 = W / 2 - hw, W / 2 + hw
    y0 = 8 * ss
    d.text((x0, y0 - 1 * ss), "PATCH v3.%d" % int(fill * 9), font=fnt, fill=mul(ctx.col, 0.8))
    yb = y0 + 13 * ss
    d.rectangle([x0, yb, x1, yb + 9 * ss], outline=mul(ctx.col, 0.8), width=max(1, ss))
    segs = 14
    sw = (x1 - x0 - 4 * ss) / segs
    for i in range(int(fill * segs + 1e-6)):
        c = (230, 255, 210) if done and int(t * 40) % 2 else ctx.col
        d.rectangle([x0 + 2 * ss + i * sw, yb + 2 * ss, x0 + 2 * ss + (i + 1) * sw - 1 * ss, yb + 7 * ss], fill=c)
    diff = [("+", "heap.free(p)"), ("-", "leak(p)"), ("+", "hp += 3"), ("+", "seal(0x3F)"),
            ("-", "trust(*)"), ("+", "verify()"), ("-", "goto fail"), ("+", "return ok")]
    lh = 11 * ss
    shown = int(fill * len(diff) + 0.999)
    for i, (s, txt) in enumerate(diff[:shown]):
        y = yb + 16 * ss + i * lh
        xl = W / 2 - ctx.halfw(y + lh) * 0.85
        c = ctx.col if s == "+" else (255, 95, 110)
        if s == "+":
            d.rectangle([xl - 2 * ss, y - 1 * ss, W, y + lh - 2 * ss], fill=mul(ctx.col, 0.15))
        d.text((xl, y), s + " " + txt, font=fnt, fill=c if s == "+" else mul(c, 0.7))
    return im


def virus(ctx):
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    cs = 6 * ss
    gw, gh = W // cs + 1, H // cs + 1
    rng = np.random.default_rng(77)
    jitter = rng.random((gh, gw)) * 0.35
    yy, xx = np.mgrid[0:gh, 0:gw].astype(np.float32)
    seeds = [(gw * 0.3, gh * 0.25), (gw * 0.7, gh * 0.7)]
    dist = np.min([np.hypot(xx - sx, (yy - sy) * 1.0) for sx, sy in seeds], axis=0) / max(gw, gh)
    grow = (t / 0.85) * 0.95 if t < 0.85 else 0.95
    inf = (dist + jitter * 0.4) < grow
    shade = rng.random((gh, gw))
    col = np.array(ctx.col, np.float32) / 255
    alt = np.array([255, 60, 200], np.float32) / 255
    rgb = np.zeros((gh, gw, 3), np.float32)
    # healthy data: dim violet bit pattern
    bits = rng.random((gh, gw)) < 0.35
    rgb[bits] = col * 0.10
    infected = col[None, None, :] * (0.16 + 0.30 * shade[..., None] ** 2)
    infected = np.where((shade > 0.94)[..., None], alt[None, None, :] * 0.55, infected)
    rgb = np.where(inf[..., None], infected, rgb)
    # front glow
    front = np.abs(dist + jitter * 0.4 - grow) < 0.035
    rgb[front] = np.array([0.62, 0.45, 0.75], np.float32)
    img = np.kron(rgb, np.ones((cs, cs, 1), np.float32))[:H, :W]
    # datamosh: smear random blocks of infected rows sideways
    frame = int(t * 24)
    r2 = np.random.default_rng(500 + frame)
    for _ in range(7):
        by = int(r2.integers(0, gh)) * cs
        bh = int(r2.integers(1, 4)) * cs
        bx = int(r2.integers(0, gw)) * cs
        bwid = int(r2.integers(3, 9)) * cs
        src = img[by:by + bh, bx:bx + cs].copy()
        if src.size:
            img[by:by + bh, bx:bx + bwid] = np.repeat(src, max(1, bwid // cs), axis=1)[:, :img[by:by + bh, bx:bx + bwid].shape[1]]
    if t >= 0.92:  # end-of-loop purge flash
        img = img * (1 - (t - 0.92) / 0.08) + col * 0.4 * (1 - (t - 0.92) / 0.08)
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))


def trojan(ctx):
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    im = base(ctx, 0.05)
    d = ImageDraw.Draw(im)
    frame = int(t * 24)
    flick = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0]
    payload = flick[frame % 24] == 1
    cx, cy = W / 2, H * 0.42
    s = min(W * 0.28, H * 0.3)
    fnt = f_mono(8 * ss)
    if not payload:
        c = ctx.col
        d.ellipse([cx - s, cy - s, cx + s, cy + s], outline=c, width=int(3 * ss))
        for ex in (-0.35, 0.35):
            d.ellipse([cx + ex * s - s * 0.1, cy - s * 0.35, cx + ex * s + s * 0.1, cy - s * 0.1], fill=c)
        d.arc([cx - s * 0.55, cy - s * 0.5, cx + s * 0.55, cy + s * 0.6], 20, 160, fill=c, width=int(3 * ss))
        cap = "free_gift.exe"
        d.text((cx - fnt.getlength(cap) / 2, cy + s + 6 * ss), cap, font=fnt, fill=mul(c, 0.8))
    else:
        c = (255, 80, 150)
        d.ellipse([cx - s, cy - s, cx + s, cy + s], outline=c, width=int(3 * ss))
        for ex in (-1, 1):
            x = cx + ex * 0.35 * s
            d.polygon([(x - s * 0.18, cy - s * 0.38), (x + s * 0.18, cy - s * 0.38 + ex * s * 0.12), (x, cy - s * 0.05)], fill=c)
        for i in range(5):
            x = cx - s * 0.5 + i * s * 0.25
            d.polygon([(x, cy + s * 0.3), (x + s * 0.125, cy + s * 0.55), (x + s * 0.25, cy + s * 0.3)], fill=c)
        rng = np.random.default_rng(frame)
        for i in range(9):
            y = int(rng.integers(0, H))
            txt = "".join(rng.choice(list("01#$%&@PAYLOAD")) for _ in range(14))
            d.text((int(rng.integers(-20, 40)) * ss, y), txt, font=fnt, fill=mul(c, 0.5))
        cap = "payload.bin"
        d.text((cx - fnt.getlength(cap) / 2, cy + s + 6 * ss), cap, font=fnt, fill=(255, 220, 235))
    if payload or flick[(frame - 1) % 24] != flick[frame % 24]:
        arr = np.asarray(im).copy()
        sh = 3 * ss
        arr[..., 0] = np.roll(arr[..., 0], sh, axis=1)
        arr[..., 2] = np.roll(arr[..., 2], -sh, axis=1)
        im = Image.fromarray(arr)
    return im


def null(ctx):
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    im = Image.new("RGB", (W, H), (9, 9, 10))
    d = ImageDraw.Draw(im)
    cx, cy = W / 2, H * 0.86
    # collapsed-beam afterimage: faint horizontal line + dot
    k = 0.55 + 0.45 * math.cos(2 * math.pi * t)
    d.line([(cx - W * 0.3, cy), (cx + W * 0.3, cy)], fill=mul((140, 140, 150), 0.25 * k), width=ss)
    r = 2.2 * ss
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=mul((235, 235, 245), 0.35 + 0.6 * k))
    im = im.filter(ImageFilter.GaussianBlur(0.6 * ss))
    return im


PLAYER = {"EXPLOIT": exploit, "ZERO-DAY": zero_day, "FIREWALL": firewall, "SANDBOX": sandbox,
          "PROXY": proxy, "PATCH": patch, "VIRUS": virus, "TROJAN": trojan, "NULL": null}


# ================================================================== Meridian dashboard set
def corp(ctx):
    """Sterile orange dashboard widget. Type = glyph + a thin accent strip only."""
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    p = ctx.prog
    acc = PROGRAMS[p]["col"]
    im = Image.new("RGB", (W, H), (15, 17, 21))
    d = ImageDraw.Draw(im)
    g = 10 * ss
    for x in range(0, W, g):
        d.line([(x, 0), (x, H)], fill=(22, 25, 30))
    for y in range(0, H, g):
        d.line([(0, y), (W, y)], fill=(22, 25, 30))
    O, Od = MERIDIAN, MERIDIAN_DIM
    fnt = f_mono(8 * ss, bold=False)
    fb = f_ui(15 * ss, b"Bold SemiCondensed")
    # header: uniform for all slices
    d.rectangle([0, 0, W, 3 * ss], fill=acc)  # type accent strip (the only colour cue)
    hw0 = ctx.halfw(12 * ss) * 0.8
    d.text((W / 2 - hw0, 6 * ss), "MRD-%02d" % (list(PROGRAMS).index(p) + 1), font=fnt, fill=Od)
    d.rectangle([W / 2 + hw0 - 6 * ss, 7 * ss, W / 2 + hw0, 13 * ss], fill=acc)
    top, bot = 20 * ss, H - 6 * ss
    yb = bot - 4 * ss

    def X(u, y):  # u in -1..1 across the visible width at row y
        return W / 2 + u * ctx.halfw(y) * 0.78

    kind = PROGRAMS[p]["kind"]
    if kind == "ATTACK":  # bar chart
        n = 7
        y_base = H * 0.62
        for i in range(n):
            u0 = -1 + 2 * i / n + 0.06
            u1 = -1 + 2 * (i + 1) / n - 0.06
            hgt = (0.3 + 0.6 * ((i * 37) % 10) / 10) * (y_base - top) * (0.4 + 0.6 * min(1, t * 2 + i * 0.05) if t < 0.5 else 1)
            d.rectangle([X(u0, y_base), y_base - hgt, X(u1, y_base), y_base], fill=O if i == n - 1 else Od)
        d.line([(X(-1, y_base), y_base), (X(1, y_base), y_base)], fill=O, width=ss)
    elif kind == "CRITICAL":  # big KPI
        v = "%.1f%%" % (97.0 + 2.9 * min(1, t * 1.5))
        tw = fb.getlength(v)
        d.text((W / 2 - tw / 2, top + 4 * ss), v, font=fb, fill=O)
        d.polygon([(W / 2, top + 26 * ss), (W / 2 - 6 * ss, top + 34 * ss), (W / 2 + 6 * ss, top + 34 * ss)], fill=O)
        d.text((X(-0.6, H * 0.8), H * 0.8), "KPI  UPTIME", font=fnt, fill=Od)
    elif kind == "DEFEND":  # compliance checklist
        items = ["ISO-27001", "SOC-2", "GDPR", "PCI-DSS", "AUDIT", "POLICY"]
        for i, s in enumerate(items):
            y = top + i * 14 * ss
            x = X(-0.85, y + 10 * ss)
            ok = (t * 8) > i or t > 0.75
            d.rectangle([x, y + 2 * ss, x + 8 * ss, y + 10 * ss], outline=O, width=ss)
            if ok:
                d.line([(x + 1.5 * ss, y + 6 * ss), (x + 3.5 * ss, y + 8.5 * ss), (x + 7 * ss, y + 3 * ss)], fill=O, width=int(1.6 * ss))
            d.text((x + 12 * ss, y + 2 * ss), s, font=fnt, fill=O if ok else Od)
    elif kind == "SHIELD":  # donut gauge
        cx, cy = W / 2, H * 0.42
        r = min(ctx.halfw(cy) * 0.75, H * 0.3)
        d.arc([cx - r, cy - r, cx + r, cy + r], 135, 405, fill=Od, width=int(6 * ss))
        frac = 0.82 + 0.06 * math.sin(2 * math.pi * t)
        d.arc([cx - r, cy - r, cx + r, cy + r], 135, 135 + 270 * frac, fill=O, width=int(6 * ss))
        d.text((X(-0.5, H * 0.82), H * 0.82), "COVERAGE", font=fnt, fill=Od)
    elif kind == "EVADE":  # scrolling line chart
        pts = []
        for i in range(40):
            x = i / 39
            y = 0.5 + 0.25 * math.sin(x * 9 + t * 2 * math.pi) + 0.1 * math.sin(x * 23)
            yy = top + y * (H * 0.55)
            pts.append((W / 2 + (x * 2 - 1) * ctx.halfw(H * 0.6) * 0.95, yy))
        d.line(pts, fill=O, width=int(1.8 * ss))
        d.line([(0, H * 0.62), (W, H * 0.62)], fill=Od, width=ss)
    elif kind == "HEAL":  # SLA bar
        y = top + 10 * ss
        x0, x1 = X(-0.9, y + 10 * ss), X(0.9, y + 10 * ss)
        d.rectangle([x0, y, x1, y + 8 * ss], outline=Od, width=ss)
        d.rectangle([x0 + 2 * ss, y + 2 * ss, x0 + 2 * ss + (x1 - x0 - 4 * ss) * min(1, t * 1.25), y + 6 * ss], fill=O)
        d.text((x0, y + 13 * ss), "SLA RESTORE", font=fnt, fill=Od)
        for i in range(4):
            yy = y + 30 * ss + i * 12 * ss
            d.line([(X(-0.7, yy), yy), (X(0.2 + 0.15 * i, yy), yy)], fill=Od, width=int(3 * ss))
    elif kind == "AFFLICT":  # heatmap
        cs = 9 * ss
        for gy in range(int(top), int(H * 0.75), cs):
            for gx in range(0, W, cs):
                v = 0.5 + 0.5 * math.sin(gx * 0.05 / ss + gy * 0.08 / ss + t * 2 * math.pi)
                d.rectangle([gx + ss, gy + ss, gx + cs - ss, gy + cs - ss], fill=mix((25, 22, 20), O, v * 0.85))
    elif kind == "DEPLOY":  # pie
        cx, cy = W / 2, H * 0.42
        r = min(ctx.halfw(cy) * 0.7, H * 0.28)
        a = -90 + 360 * t
        d.pieslice([cx - r, cy - r, cx + r, cy + r], a, a + 110, fill=O)
        d.pieslice([cx - r, cy - r, cx + r, cy + r], a + 110, a + 360, fill=Od)
        d.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45], fill=(15, 17, 21))
    elif kind == "MISS":  # NO DATA
        y = H * 0.45
        d.line([(0, y), (W, y)], fill=Od, width=int(1.5 * ss))
        s = "NO DATA"
        d.text((W / 2 - fnt.getlength(s) / 2, H * 0.75), s, font=fnt, fill=Od)
    return im


def texture(ctx):
    im = _texture(ctx)
    o = getattr(ctx, "opts", {}) or {}
    if o.get("art"):
        import icons8
        im = icons8.screen(ctx, im)
    elif o.get("mascot"):
        import mascots
        im = mascots.apply(ctx, im)
    return im


def _texture(ctx):
    import skins
    if ctx.theme == "player":
        if ctx.prog == "SANDBOX":  # round 6: C's breathing windows replaced by A's guard-ring PCB
            return skins.sandbox_pcb(ctx)
        return PLAYER[ctx.prog](ctx)
    if ctx.theme in skins.SKINS:
        return skins.corp_texture(ctx)
    return corp(ctx)
