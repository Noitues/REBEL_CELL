"""Round 6 screen content: the SANDBOX guard-ring PCB (from family A), the five corporation
skins (from family D), and the boss signature effects with their phase-2 variants.

All drawn in C's screen texture space: W x H, y = 0 at the outer rim, x = W/2 on the slice
midline, so every material bends into C's polar CRT. Randomness is seeded per slice.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from slicelib import f_mono, f_ui, f_num, CORPS, PROGRAMS


def mul(c, k):
    return tuple(int(max(0, min(255, v * k))) for v in c)


def mix(a, b, k):
    return tuple(int(a[i] * (1 - k) + b[i] * k) for i in range(3))


def edge_x(ctx, y, inset=0.0):
    """Half-width of the visible screen at texture row y, minus an inset."""
    return max(0.0, ctx.halfw(y) - 10 * ctx.ss - inset)


def screen_poly(ctx, inset):
    ss, W, H = ctx.ss, ctx.W, ctx.H
    y0, y1 = inset, H - 4 * ss - inset
    ys = np.linspace(y0, y1, 24)
    left = [(W / 2 - edge_x(ctx, y, inset), y) for y in ys]
    right = [(W / 2 + edge_x(ctx, y, inset), y) for y in ys[::-1]]
    return left + right


# ================================================================== SANDBOX (replaces C's)
def sandbox_pcb(ctx):
    """Guard-ring PCB, boxed in: cross-hatched ground plane inside a via-stitched ring."""
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    col = ctx.col
    im = Image.new("RGB", (W, H), mul(col, 0.05))
    d = ImageDraw.Draw(im)
    g = 9 * ss
    poly = screen_poly(ctx, g)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    hatch = Image.new("RGB", (W, H), mul(col, 0.10))
    dh = ImageDraw.Draw(hatch)
    sp = 7 * ss
    for k in range(-H, W + H, sp):
        dh.line([(k, 0), (k + H, H)], fill=mul(col, 0.42), width=max(1, ss))
        dh.line([(k, H), (k + H, 0)], fill=mul(col, 0.42), width=max(1, ss))
    im.paste(hatch, (0, 0), mask)
    # guard ring: bold outer trace + thin inner trace
    d.line(poly + [poly[0]], fill=mul(col, 1.0), width=int(4 * ss), joint="curve")
    poly2 = screen_poly(ctx, g + 7 * ss)
    d.line(poly2 + [poly2[0]], fill=mul(col, 0.6), width=max(1, int(1.4 * ss)))
    # stitching vias along the ring, lit in sequence
    pts = poly + [poly[0]]
    acc = 0.0
    step = 13 * ss
    vias = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        s = (step - acc) % step
        while s < L:
            vias.append((x0 + (x1 - x0) * s / L, y0 + (y1 - y0) * s / L))
            s += step
        acc = (acc + L) % step
    n = len(vias)
    for i, (x, y) in enumerate(vias):
        lit = ((i / max(1, n) - t) % 1.0) < 0.12
        r = 3.2 * ss
        d.ellipse([x - r, y - r, x + r, y + r], fill=(235, 255, 250) if lit else mul(col, 0.9))
        d.ellipse([x - r * 0.4, y - r * 0.4, x + r * 0.4, y + r * 0.4], fill=mul(col, 0.15))
    # corner brackets: "boxed in"
    for (x, y), sx, sy in ((poly[0], 1, 1), (poly[-1], -1, 1), (poly[23], 1, -1), (poly[24], -1, -1)):
        L = 12 * ss
        d.line([(x - sx * 3 * ss, y - sy * 3 * ss), (x - sx * 3 * ss + sx * L, y - sy * 3 * ss)], fill=(235, 255, 250), width=int(2 * ss))
        d.line([(x - sx * 3 * ss, y - sy * 3 * ss), (x - sx * 3 * ss, y - sy * 3 * ss + sy * L)], fill=(235, 255, 250), width=int(2 * ss))
    return im


# ================================================================== corporation skins
def meridian(ctx, rng):
    ss, W, H = ctx.ss, ctx.W, ctx.H
    x = np.arange(W, dtype=np.float32)
    period = 24 * ss
    u = (x % period) / period
    prof = np.clip(np.where(u < 0.18, u / 0.18, np.where(u < 0.5, 1.0, np.where(u < 0.68, 1 - (u - 0.5) / 0.18, 0.0))), 0, 1)
    light = 0.62 + 0.38 * prof - 0.18 * (np.abs(u - 0.18) < 0.03)
    base = np.array([112, 50, 16], np.float32) / 255
    arr = np.tile((base[None, :] * light[:, None])[None, :, :], (H, 1, 1))
    crest = (np.abs(u - 0.2) < 0.02).astype(np.float32)
    arr += crest[None, :, None] * np.array([0.22, 0.12, 0.05])[None, None, :]
    # rust specks
    nz = rng.random((H // (3 * ss) + 1, W // (3 * ss) + 1))
    nz = np.kron(nz, np.ones((3 * ss, 3 * ss)))[:H, :W]
    arr *= (1 - 0.25 * (nz > 0.93))[..., None]
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    # top rail with rivets
    d.rectangle([0, 0, W, 9 * ss], fill=(95, 44, 14))
    for xx in range(int(6 * ss), W, int(22 * ss)):
        d.ellipse([xx - 2 * ss, 3 * ss, xx + 2 * ss, 7 * ss], fill=(210, 120, 50))
    fm = f_mono(11 * ss)
    code = "MRDU %06d %d" % (rng.integers(100000, 999999), rng.integers(0, 9))
    y = 14 * ss
    d.text((W / 2 - edge_x(ctx, y + 10 * ss) * 0.9, y), code, font=fm, fill=(70, 30, 8))
    fs = f_mono(7 * ss)
    y2 = 30 * ss
    d.text((W / 2 + edge_x(ctx, y2 + 20 * ss) * 0.15, y2), "MAX GROSS 30480 KG\nTARE      2220 KG", font=fs, fill=(80, 36, 10))
    # barcode sticker on the inner band
    yb = H - 46 * ss
    hw = min(edge_x(ctx, yb + 30 * ss) * 0.75, 70 * ss)
    if hw > 12 * ss:
        d.rectangle([W / 2 - hw, yb, W / 2 + hw, yb + 30 * ss], fill=(228, 222, 205))
        xx = W / 2 - hw + 4 * ss
        while xx < W / 2 + hw - 4 * ss:
            bw = int(rng.integers(1, 4)) * ss * 0.8
            d.rectangle([xx, yb + 3 * ss, xx + bw, yb + 22 * ss], fill=(20, 18, 16))
            xx += bw + int(rng.integers(1, 3)) * ss * 0.9
        d.text((W / 2 - hw + 4 * ss, yb + 22 * ss), "4 47102 88041", font=fs, fill=(30, 28, 25))
        d.line([(W / 2 - hw - 4 * ss, yb + 14 * ss), (W / 2 + hw + 4 * ss, yb + 14 * ss)], fill=(255, 40, 40), width=max(1, ss))
    return im


def solace(ctx, rng):
    ss, W, H = ctx.ss, ctx.W, ctx.H
    yy = np.linspace(0, 1, H)[:, None, None]
    top = np.array([24, 52, 12], np.float32) / 255
    bot = np.array([10, 26, 6], np.float32) / 255
    arr = top + (bot - top) * yy
    arr = np.tile(arr, (1, W, 1))
    im = Image.fromarray((arr * 255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    mint = CORPS["solace"]["col"]
    # specular streaks
    for k in range(5):
        x0 = rng.integers(0, W)
        d.line([(x0, 0), (x0 - H * 0.6, H)], fill=(230, 255, 190, 18), width=int(rng.integers(4, 14) * ss))
    # cells
    for k in range(int(W * H / (1500 * ss * ss))):
        cx, cy = rng.random() * W, rng.random() * H
        r = (8 + rng.random() * 14) * ss
        split = rng.random() < 0.25
        cells = [(cx, cy, r)] if not split else [(cx - r * 0.45, cy, r * 0.75), (cx + r * 0.45, cy, r * 0.75)]
        for (x, y, rr) in cells:
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(70, 120, 20, 70), outline=mul(mint, 0.55) + (200,), width=max(1, int(1.4 * ss)))
            n = rr * 0.32
            d.ellipse([x - n, y - n * 0.9, x + n, y + n * 0.9], fill=(40, 80, 12, 220), outline=mul(mint, 0.4) + (160,))
    # DNA helix along the outer band
    xs = np.arange(0, W, 2 * ss)
    for k in range(2):
        pts = [(x, 14 * ss + 7 * ss * math.sin(x / (14 * ss) + k * math.pi)) for x in xs]
        d.line(pts, fill=mul(mint, 0.85) + (255,), width=max(1, int(1.6 * ss)))
    for x in range(0, W, int(9 * ss)):
        a = 7 * ss * math.sin(x / (14 * ss))
        d.line([(x, 14 * ss + a), (x, 14 * ss - a)], fill=mul(mint, 0.45) + (255,), width=max(1, ss))
    # ECG on the inner band
    y = H - 22 * ss
    hw = edge_x(ctx, y)
    pts = []
    x = W / 2 - hw
    while x < W / 2 + hw:
        u = ((x - (W / 2 - hw)) / (34 * ss)) % 1.0
        v = 0
        if 0.30 < u < 0.34:
            v = -14
        elif 0.34 < u < 0.38:
            v = 10
        elif 0.55 < u < 0.65:
            v = -3
        pts.append((x, y + v * ss))
        x += 1.5 * ss
    if len(pts) > 1:
        d.line(pts, fill=mul(mint, 1.0) + (255,), width=max(1, int(1.6 * ss)))
    return im


def halcyon(ctx, rng):
    ss, W, H = ctx.ss, ctx.W, ctx.H
    im = Image.new("RGB", (W, H), (30, 12, 54))
    d = ImageDraw.Draw(im)
    for x in range(0, W, int(12 * ss)):
        d.line([(x, 0), (x, H)], fill=(52, 26, 92), width=1)
    for y in range(0, H, int(12 * ss)):
        d.line([(0, y), (W, y)], fill=(52, 26, 92), width=1)
    for x in range(int(W / 2) % int(48 * ss), W, int(48 * ss)):
        d.line([(x, 0), (x, H)], fill=(96, 50, 160), width=max(1, ss))
    # concentric civic rings (rows of constant radius)
    for y in range(int(18 * ss), H, int(30 * ss)):
        d.line([(0, y), (W, y)], fill=(150, 90, 230), width=max(1, ss))
    # pulses on the grid
    for k in range(6):
        y = int(18 * ss + rng.integers(0, H // int(30 * ss)) * 30 * ss)
        x = rng.random() * W
        d.line([(x, y), (x + 16 * ss, y)], fill=(255, 176, 60), width=int(2 * ss))
    # municipal paving tiles on the inner band
    yb = H - 30 * ss
    for row in range(3):
        y0 = yb + row * 9 * ss
        off = (row % 2) * 7 * ss
        for x in range(-20 * ss, W, int(14 * ss)):
            d.rectangle([x + off, y0, x + off + 12 * ss, y0 + 7 * ss], outline=(110, 60, 170), width=1)
    # annotations
    fm = f_mono(8 * ss, bold=False)
    y = 36 * ss
    xl = W / 2 - edge_x(ctx, y + 10 * ss) * 0.85
    d.text((xl, y), "SEC-%02d / H-CIV" % rng.integers(1, 40), font=fm, fill=(255, 176, 60))
    d.line([(xl, y + 13 * ss), (xl + 70 * ss, y + 13 * ss)], fill=(255, 176, 60), width=1)
    for xx in (xl, xl + 70 * ss):
        d.line([(xx, y + 10 * ss), (xx, y + 16 * ss)], fill=(255, 176, 60), width=1)
    return im


def orbital(ctx, rng):
    """Brighter than D's: denser, larger stars, a lit nebula, bold constellation lines."""
    ss, W, H = ctx.ss, ctx.W, ctx.H
    arr = np.zeros((H, W, 3), np.float32)
    arr[:] = np.array([4, 5, 14], np.float32) / 255
    neb = Image.new("RGB", (W, H), (0, 0, 0))
    dn = ImageDraw.Draw(neb)
    for k in range(4):
        x, y = rng.random() * W, rng.random() * H
        r = (40 + rng.random() * 60) * ss
        c = [(40, 60, 130), (70, 90, 170), (150, 160, 200), (30, 40, 90)][k]
        dn.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=c)
    neb = np.asarray(neb.filter(ImageFilter.GaussianBlur(30 * ss)), np.float32) / 255
    arr += neb * 0.55
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    # dashed graticule
    for y in range(int(20 * ss), H, int(40 * ss)):
        for x in range(0, W, int(10 * ss)):
            d.line([(x, y), (x + 5 * ss, y)], fill=(70, 90, 140), width=1)
    for x in range(int(W / 2) % int(50 * ss), W, int(50 * ss)):
        for y in range(0, H, int(10 * ss)):
            d.line([(x, y), (x, y + 5 * ss)], fill=(70, 90, 140), width=1)
    # orbit ellipses
    d.ellipse([-W * 0.2, H * 0.15, W * 1.1, H * 0.7], outline=(200, 215, 255), width=max(1, ss))
    d.ellipse([W * 0.1, -H * 0.2, W * 1.3, H * 0.45], outline=(150, 170, 230), width=max(1, ss))
    # stars
    stars = []
    for k in range(int(W * H / (220 * ss * ss))):
        x, y = rng.random() * W, rng.random() * H
        b = rng.random() ** 2
        r = (0.6 + 1.6 * b) * ss
        c = mix((200, 210, 255), (255, 255, 255), b)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
        if b > 0.75:
            stars.append((x, y))
            L = 7 * ss * b
            d.line([(x - L, y), (x + L, y)], fill=c, width=max(1, ss // 2))
            d.line([(x, y - L), (x, y + L)], fill=c, width=max(1, ss // 2))
    # constellation
    if len(stars) >= 3:
        st = sorted(stars, key=lambda p: p[0])[:5]
        d.line(st, fill=(230, 236, 255), width=max(1, int(1.2 * ss)))
    # satellite on orbit 1
    sx, sy = W * 0.62, H * 0.66
    d.rectangle([sx - 3 * ss, sy - 3 * ss, sx + 3 * ss, sy + 3 * ss], fill=(240, 240, 255))
    d.rectangle([sx - 14 * ss, sy - 2 * ss, sx - 5 * ss, sy + 2 * ss], fill=(90, 220, 255))
    d.rectangle([sx + 5 * ss, sy - 2 * ss, sx + 14 * ss, sy + 2 * ss], fill=(90, 220, 255))
    # solar-panel cells on the inner band
    yb = H - 28 * ss
    for x in range(0, W, int(10 * ss)):
        for row in range(2):
            y0 = yb + row * 10 * ss
            d.rectangle([x, y0, x + 9 * ss, y0 + 9 * ss], fill=(30, 40, 96), outline=(210, 216, 240))
    d.line([(W * 0.3, yb), (W * 0.45, yb + 20 * ss)], fill=(220, 235, 255), width=int(3 * ss))
    return im


PLAYER_RGB = [(255, 61, 168), (92, 225, 255), (123, 224, 123), (200, 90, 255)]


def rebel_cell(ctx, rng):
    """The Cell's own PCB, corrupted: red traces, player-colour fringes, dead pixels, tears."""
    ss, W, H = ctx.ss, ctx.W, ctx.H
    im = Image.new("RGB", (W, H), (20, 4, 7))
    tr = Image.new("L", (W, H), 0)
    dt = ImageDraw.Draw(tr)
    for k in range(int(W * H / (2600 * ss * ss))):
        x, y = rng.random() * W, rng.random() * H
        pts = [(x, y)]
        for s in range(int(rng.integers(2, 5))):
            dirn = rng.choice([(1, 0), (0, 1), (1, 1), (-1, 1), (1, -1)])
            L = (10 + rng.random() * 40) * ss
            x, y = x + dirn[0] * L, y + dirn[1] * L
            pts.append((x, y))
        dt.line(pts, fill=255, width=max(1, int(1.6 * ss)))
        for (px, py) in (pts[0], pts[-1]):
            dt.ellipse([px - 2.6 * ss, py - 2.6 * ss, px + 2.6 * ss, py + 2.6 * ss], fill=255)
    # break traces up with noise blocks
    nz = rng.random((H // (6 * ss) + 1, W // (6 * ss) + 1))
    keep = np.kron((nz > 0.22).astype(np.float32), np.ones((6 * ss, 6 * ss)))[:H, :W]
    trv = np.asarray(tr, np.float32) / 255 * keep
    arr = np.asarray(im, np.float32) / 255
    red = np.array([0.80, 0.08, 0.12], np.float32)
    arr += trv[..., None] * red
    # chromatic fringe in the player's colours (shifted copies)
    for k, c in enumerate(PLAYER_RGB[:2]):
        sh = np.roll(trv, (2 + k) * ss * (1 if k == 0 else -1), axis=1)
        arr += sh[..., None] * (np.array(c, np.float32) / 255) * 0.28
    # dead pixel blocks in player colours
    for k in range(10):
        x, y = int(rng.integers(0, W - 8 * ss)), int(rng.integers(0, H - 8 * ss))
        c = np.array(PLAYER_RGB[k % 4], np.float32) / 255
        arr[y:y + int(rng.integers(3, 7)) * ss, x:x + int(rng.integers(3, 10)) * ss] = c * 0.6
    # scan-glitch bars + row tears
    for k in range(4):
        y = int(rng.integers(0, H - 6 * ss))
        h = int(rng.integers(2, 6)) * ss
        arr[y:y + h] = np.roll(arr[y:y + h], int(rng.integers(-30, 30)) * ss, axis=1)
        arr[y:y + max(1, ss)] += np.array([0.5, 0.03, 0.05], np.float32)
    arr[::3 * ss] *= 0.6
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    # inverted hexagon emblem on the inner band
    cx, cy, r = W / 2, H - 22 * ss, 11 * ss
    hexp = [(cx + r * math.cos(math.radians(90 + 60 * i)), cy + r * math.sin(math.radians(90 + 60 * i))) for i in range(6)]
    d.polygon(hexp, outline=(255, 40, 50), width=int(2 * ss))
    d.ellipse([cx - 3 * ss, cy - 3 * ss, cx + 3 * ss, cy + 3 * ss], fill=(255, 60, 70))
    return im


SKINS = {"meridian": meridian, "solace": solace, "halcyon": halcyon, "orbital": orbital, "rebel_cell": rebel_cell}


# ================================================================== boss signatures
def _panel(d, box, fill=(0, 0, 0, 150)):
    d.rectangle(box, fill=fill)


def boss_meridian(ctx, im, phase, rng):
    ss, W, H = ctx.ss, ctx.W, ctx.H
    d = ImageDraw.Draw(im, "RGBA")
    fm = f_mono(8 * ss)
    y0 = 44 * ss
    hw = edge_x(ctx, y0 + 50 * ss) * 0.8
    _panel(d, [W / 2 - hw, y0, W / 2 + hw, y0 + 52 * ss])
    for i in range(4):
        y = y0 + 3 * ss + i * 12 * ss
        ok = "OK" if (i + ctx.seed) % 3 else ">>"
        d.text((W / 2 - hw + 4 * ss, y), "PKG#%04d LANE %d %s" % (rng.integers(0, 9999), i % 2 + 1, ok), font=fm, fill=(255, 170, 70, 255))
    if phase == 1:
        d.line([(0, H * 0.33), (W, H * 0.33)], fill=(255, 40, 40, 255), width=int(2 * ss))
        d.line([(0, H * 0.33), (W, H * 0.33)], fill=(255, 120, 120, 90), width=int(7 * ss))
    else:  # PEAK SEASON: hazard stripes and a hot second lane
        band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        db = ImageDraw.Draw(band)
        for x in range(-H, W + H, int(22 * ss)):
            db.polygon([(x, 0), (x + 11 * ss, 0), (x + 11 * ss + 24 * ss, 24 * ss), (x + 24 * ss, 24 * ss)], fill=(20, 16, 10, 230))
        db.rectangle([0, 0, W, 24 * ss], fill=(255, 150, 20, 90))
        im.paste(band, (0, 0), band)
        ov = Image.new("RGB", im.size, (255, 40, 20))
        im = Image.blend(im, ov, 0.18)
        d = ImageDraw.Draw(im, "RGBA")
        fb = f_ui(13 * ss, b"Bold Condensed")
        s = "PEAK SEASON"
        d.text((W / 2 - fb.getlength(s) / 2, H - 62 * ss), s, font=fb, fill=(255, 220, 120, 255))
        d.line([(0, H * 0.33), (W, H * 0.33)], fill=(255, 40, 40, 255), width=int(2 * ss))
        d.line([(0, H * 0.66), (W, H * 0.66)], fill=(255, 40, 40, 255), width=int(2 * ss))
    return im


def boss_solace(ctx, im, phase, rng):
    ss, W, H = ctx.ss, ctx.W, ctx.H
    d = ImageDraw.Draw(im, "RGBA")
    mint = CORPS["solace"]["col"]
    if phase == 2:
        ov = Image.new("RGB", im.size, (255, 30, 90))
        im = Image.blend(im, ov, 0.22)
        d = ImageDraw.Draw(im, "RGBA")
        for k in range(14):  # infected cells
            x, y, r = rng.random() * W, rng.random() * H, (6 + rng.random() * 12) * ss
            d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 70, 150, 230), width=int(2 * ss), fill=(120, 0, 40, 90))
    # big heartbeat across the screen
    y = H * 0.38
    pts = []
    for x in np.arange(0, W, 1.5 * ss):
        u = (x / (90 * ss) + ctx.seed * 0.3) % 1.0
        v = 0
        if phase == 1:
            if 0.40 < u < 0.44:
                v = -30
            elif 0.44 < u < 0.48:
                v = 22
        else:
            v = (rng.random() - 0.5) * 30 if rng.random() < 0.3 else 0
        pts.append((x, y + v * ss))
    d.line(pts, fill=(mint if phase == 1 else (255, 90, 160)) + (255,), width=int(2.4 * ss))
    fb = f_ui(12 * ss, b"Bold Condensed")
    s = "RENEWS IN 00:%02d" % (59 - ctx.seed * 7) if phase == 1 else "PAYMENT OVERDUE"
    yy = H - 62 * ss
    w = fb.getlength(s)
    _panel(d, [W / 2 - w / 2 - 4 * ss, yy - 2 * ss, W / 2 + w / 2 + 4 * ss, yy + 16 * ss],
           (0, 30, 20, 190) if phase == 1 else (90, 0, 30, 220))
    d.text((W / 2 - w / 2, yy), s, font=fb, fill=(220, 255, 235, 255) if phase == 1 else (255, 200, 220, 255))
    return im


def boss_halcyon(ctx, im, phase, rng):
    ss, W, H = ctx.ss, ctx.W, ctx.H
    d = ImageDraw.Draw(im, "RGBA")
    gold = (255, 200, 90)
    # district block map
    for k in range(10):
        x, y = rng.random() * W, (0.15 + rng.random() * 0.55) * H
        s = (6 + rng.random() * 10) * ss
        d.rectangle([x, y, x + s, y + s * 0.8], fill=(110, 120, 255, 90), outline=(170, 180, 255, 200))
    if phase == 1:  # gold counter-flow on the rings
        for y in range(int(18 * ss), H, int(30 * ss)):
            for x in range(int(rng.integers(0, 40)) * ss, W, int(40 * ss)):
                d.line([(x, y), (x + 14 * ss, y)], fill=gold + (255,), width=int(2 * ss))
        d.line([(0, 4 * ss), (W, 4 * ss)], fill=gold + (255,), width=int(2 * ss))
    else:  # state of emergency: red grid, siren bars
        ov = Image.new("RGB", im.size, (255, 20, 40))
        im = Image.blend(im, ov, 0.28)
        d = ImageDraw.Draw(im, "RGBA")
        for x in range(-H, W + H, int(30 * ss)):
            d.line([(x, H * 0.62), (x + 30 * ss, H * 0.62 - 30 * ss)], fill=(255, 255, 255, 90), width=int(6 * ss))
        fb = f_ui(12 * ss, b"Bold Condensed")
        s = "STATE OF EMERGENCY"
        w = fb.getlength(s)
        yy = H - 64 * ss
        _panel(d, [W / 2 - w / 2 - 4 * ss, yy - 2 * ss, W / 2 + w / 2 + 4 * ss, yy + 16 * ss], (120, 0, 10, 230))
        d.text((W / 2 - w / 2, yy), s, font=fb, fill=(255, 230, 230, 255))
    return im


def boss_orbital(ctx, im, phase, rng):
    ss, W, H = ctx.ss, ctx.W, ctx.H
    d = ImageDraw.Draw(im, "RGBA")
    gold = (255, 215, 120)
    pts = [(rng.random() * W, (0.1 + rng.random() * 0.6) * H) for _ in range(6)]
    pts.sort()
    d.line(pts, fill=gold + (255,), width=int(2 * ss))
    for (x, y) in pts:
        d.ellipse([x - 4 * ss, y - 4 * ss, x + 4 * ss, y + 4 * ss], fill=(255, 250, 230, 255))
    if phase == 2:  # solar flare whiteout sweeping from one side
        arr = np.asarray(im, np.float32) / 255
        x = np.linspace(0, 1, W)[None, :, None]
        side = 1 - x if ctx.seed % 2 else x
        wave = np.clip((side - 0.25) / 0.75, 0, 1) ** 1.4
        hot = np.array([1.0, 0.82, 0.55], np.float32)
        arr = arr * (1 - wave * 0.75) + hot * wave * 0.95
        im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
        d = ImageDraw.Draw(im, "RGBA")
        for k in range(5):
            y = rng.random() * H
            d.line([(0, y), (W, y + (rng.random() - 0.5) * 40 * ss)], fill=(255, 255, 240, 120), width=int(2 * ss))
    return im


def boss_rebel(ctx, im, phase, rng):
    ss, W, H = ctx.ss, ctx.W, ctx.H
    if phase == 2:
        # DISPATCH runs the Cell's own programs: the player's C screen for this type, red-shifted
        import programs
        own = programs.PLAYER[ctx.prog](ctx)
        a = np.asarray(own, np.float32) / 255
        lum = a.max(axis=2, keepdims=True)
        red = np.concatenate([lum * 1.0, lum * 0.12, lum * 0.16], axis=2)
        mixd = red * 0.75 + a * 0.25
        for k in range(7):
            y = int(rng.integers(0, H - 6 * ss))
            h = int(rng.integers(3, 14)) * ss
            mixd[y:y + h] = np.roll(mixd[y:y + h], int(rng.integers(-40, 40)) * ss, axis=1)
        sh = 4 * ss
        mixd[..., 0] = np.roll(mixd[..., 0], sh, axis=1)
        mixd[..., 2] = np.roll(mixd[..., 2], -sh, axis=1)
        im = Image.fromarray((np.clip(mixd, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    fm = f_mono(8 * ss)
    y = 40 * ss
    hw = edge_x(ctx, y + 40 * ss) * 0.85
    lines = ["> ORDER 0x%02X ISSUED" % (17 + ctx.seed), "> CELL COMPLIANT", "> SCHEDULED."] if phase == 1 else \
        ["> YOUR CODE", "> MY ORDERS", "> THANK YOU"]
    for i, s in enumerate(lines):
        d.text((W / 2 - hw, y + i * 11 * ss), s, font=fm, fill=(255, 90, 100, 230))
    return im


BOSS = {"meridian": boss_meridian, "solace": boss_solace, "halcyon": boss_halcyon, "orbital": boss_orbital,
        "rebel_cell": boss_rebel}


def rebel_program(ctx):
    """Round 15: REBEL_CELL runs the PLAYER's own C programs (same screens and animations), recoloured red."""
    import programs
    import screens10
    if ctx.prog in programs.TEX_VARIANT:
        own = screens10.texture(ctx, programs.TEX_VARIANT[ctx.prog])
    elif ctx.prog == "SANDBOX":
        own = sandbox_pcb(ctx)
    else:
        own = programs.PLAYER[ctx.prog](ctx)
    a = np.asarray(own.convert("RGB"), np.float32) / 255
    lum = a.max(axis=2, keepdims=True)
    red = np.concatenate([np.clip(lum * 1.15, 0, 1), lum * 0.10 + lum ** 3 * 0.55, lum * 0.16 + lum ** 3 * 0.45], axis=2)
    return red


def corp_texture(ctx):
    rng = np.random.default_rng(1000 + ctx.seed * 17 + sum(map(ord, ctx.theme)) % 97)
    o = getattr(ctx, "opts", {}) or {}
    phase = o.get("phase", 1)
    mat = SKINS[ctx.theme](ctx, rng)
    if o.get("boss"):
        mat = BOSS[ctx.theme](ctx, mat, min(phase, 2), np.random.default_rng(77 + ctx.seed))
    gain = o.get("skin_gain", 0.85) * (1.18 if ctx.theme == "orbital" else 1.0)
    arr = np.asarray(mat.convert("RGB"), np.float32) / 255 * gain
    if ctx.theme == "rebel_cell" and ctx.prog not in ("SANDBOX", "FIREWALL"):  # the player's programs in red
        red = rebel_program(ctx)
        arr = np.clip(arr * 0.45 + red * 0.95, 0, 1)
    else:  # round 16: the corp animation is drawn upright in screen space by slicelib (ctx.scene_req)
        import scenes18 as scenes
        kind = o.get("scene_kind") or ("SPECIAL" if getattr(ctx, "special", None) else PROGRAMS[ctx.prog]["kind"])
        sc = scenes.scene(ctx, ctx.theme, kind, ctx.t)
        arr = arr * 0.5
        cut = (ctx.H - 50 * ctx.ss) if ctx.theme == "meridian" else None
        ctx.scene_req = (sc, scenes.YC.get(ctx.theme, 0.5), cut)
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    if o.get("boss") and phase >= 3:
        import motifs
        im = motifs.overdrive(im, ctx, ctx.theme, np.random.default_rng(31 + ctx.seed))
    d = ImageDraw.Draw(im)
    tcol = PROGRAMS[ctx.prog]["col"]
    d.rectangle([0, 0, ctx.W, int(3.5 * ctx.ss)], fill=tcol)
    return im