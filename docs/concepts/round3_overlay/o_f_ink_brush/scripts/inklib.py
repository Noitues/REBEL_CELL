"""inklib: a small Pillow-only sumi-ink / watercolour / washi engine (seeded, deterministic).

All drawing happens on a supersampled canvas (SS x the 1920x1080 frame); coordinates passed
in are always in 1x screen pixels and are scaled internally.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont, ImageOps

SS = 2
W, H = 1920, 1080
CW, CH = W * SS, H * SS
FONTS = "C:/Windows/Fonts/"

# palette --------------------------------------------------------------------------
SUMI_THIN = (44, 38, 46)
SUMI_DENSE = (11, 9, 14)
PINK_INK_THIN = (255, 92, 168)
PINK_INK_DENSE = (236, 24, 122)
PINK_WASH_LIGHT = (255, 112, 178)
PINK_WASH_DEEP = (214, 16, 108)
ACID_WASH_LIGHT = (240, 244, 120)
ACID_WASH_DEEP = (196, 214, 40)
USUMI_LIGHT = (176, 170, 172)
USUMI_DEEP = (64, 58, 68)
SEAL_RED = (212, 44, 34)
SEAL_RED_DEEP = (176, 26, 28)
PAPER = (236, 229, 212)


def clamp(v, a, b):
    return a if v < a else b if v > b else v


def smooth(t):
    t = clamp(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


# geometry -------------------------------------------------------------------------
def catmull(pts, n=14):
    if len(pts) < 3:
        return list(pts)
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(
                0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                       + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(tuple(pts[-1]))
    return out


def round_corners(pts, r):
    if len(pts) < 3:
        return list(pts)
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, v, b = pts[i - 1], pts[i], pts[i + 1]
        la = math.hypot(a[0] - v[0], a[1] - v[1]) or 1e-6
        lb = math.hypot(b[0] - v[0], b[1] - v[1]) or 1e-6
        ra, rb = min(r, la * 0.4), min(r, lb * 0.4)
        pin = (v[0] + (a[0] - v[0]) * ra / la, v[1] + (a[1] - v[1]) * ra / la)
        pout = (v[0] + (b[0] - v[0]) * rb / lb, v[1] + (b[1] - v[1]) * rb / lb)
        for k in range(9):
            t = k / 8
            out.append(((1 - t) ** 2 * pin[0] + 2 * (1 - t) * t * v[0] + t * t * pout[0],
                        (1 - t) ** 2 * pin[1] + 2 * (1 - t) * t * v[1] + t * t * pout[1]))
    out.append(pts[-1])
    return out


def resample(pts, spacing):
    out = [(pts[0][0], pts[0][1], 0.0)]
    s_total = 0.0
    carry = 0.0
    for a, b in zip(pts[:-1], pts[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        if seg < 1e-9:
            continue
        d = spacing - carry
        while d <= seg:
            t = d / seg
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, s_total + d))
            d += spacing
        carry = seg - (d - spacing)
        s_total += seg
    if s_total - out[-1][2] > spacing * 0.3:
        out.append((pts[-1][0], pts[-1][1], s_total))
    return out


def path_length(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:]))


class VNoise:
    """1-D cosine value noise."""

    def __init__(self, rng, length, period):
        self.period = max(period, 1e-3)
        self.k = [rng.random() for _ in range(int(length / self.period) + 4)]

    def __call__(self, s):
        x = s / self.period
        i = int(x)
        f = x - i
        f = (1 - math.cos(f * math.pi)) * 0.5
        i = clamp(i, 0, len(self.k) - 2)
        return self.k[i] * (1 - f) + self.k[i + 1] * f


# 2-D noise helpers ------------------------------------------------------------------
def noise(w, h, cell, rng, contrast=True):
    cell = max(1, int(cell))
    sw, sh = w // cell + 4, h // cell + 4
    small = Image.frombytes("L", (sw, sh), rng.randbytes(sw * sh))
    big = small.resize((sw * cell, sh * cell), Image.BICUBIC).crop((cell, cell, cell + w, cell + h))
    if contrast:
        big = ImageOps.autocontrast(big, cutoff=1)
    return big


def white(w, h, rng, blur=0.0):
    img = Image.frombytes("L", (w, h), rng.randbytes(w * h))
    if blur > 0:
        img = img.filter(ImageFilter.GaussianBlur(blur))
        img = ImageOps.autocontrast(img, cutoff=0.5)
    return img


def ramp(img, lo, hi, top=255):
    lut = []
    for v in range(256):
        if v <= lo:
            lut.append(0)
        elif v >= hi:
            lut.append(top)
        else:
            lut.append(int((v - lo) * top / (hi - lo)))
    return img.point(lut)


def scale_l(img, k, off=0):
    return img.point([int(clamp(v * k + off, 0, 255)) for v in range(256)])


def addn(m, n, k):
    nk = n.point([int(clamp(128 + k * (v - 128), 0, 255)) for v in range(256)])
    return ImageChops.add(m, nk, 1.0, -128)


def blur(img, r):
    return img.filter(ImageFilter.GaussianBlur(r)) if r > 0 else img


def shift(img, dx, dy):
    out = Image.new(img.mode, img.size, 0)
    out.paste(img, (int(dx), int(dy)))
    return out


def solid(color, size):
    return Image.new("RGB", size, color)


# ink ------------------------------------------------------------------------------
class Ink:
    """Coverage + pooled-ink density for one ink colour, full canvas at SS."""

    def __init__(self):
        self.a = Image.new("L", (CW, CH), 0)
        self.pool = Image.new("L", (CW, CH), 0)
        self.da = ImageDraw.Draw(self.a)
        self.dp = ImageDraw.Draw(self.pool)

    def blob(self, x, y, r, rng, val=255, to_pool=True):
        for _ in range(5):
            ox, oy = rng.gauss(0, 0.18 * r), rng.gauss(0, 0.18 * r)
            rr = r * rng.uniform(0.62, 0.92)
            box = (x + ox - rr, y + oy - rr * rng.uniform(0.85, 1.1), x + ox + rr, y + oy + rr * rng.uniform(0.85, 1.1))
            self.da.ellipse(box, fill=255)
            if to_pool:
                self.dp.ellipse(box, fill=val)


def _normals(pts, k=4):
    n = len(pts)
    out = []
    for i in range(n):
        a = pts[max(0, i - k)]
        b = pts[min(n - 1, i + k)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1e-6
        out.append((dx / l, dy / l, -dy / l, dx / l))
    return out


def brush_stroke(ink, path, width, seed, end="f", dry=0.55, wet=0.5, splat=0.4, cut=None,
                 mode="c", corner=None, entry=1.0, head=True, bristle_scale=1.0, pvar=0.14, pperiod=70, round_entry=False):
    """Paint one dry-brush sumi stroke. path in 1x px. Returns stroke length (1x px).

    end: 'f' flick (tapers, bristles split, splatter) or 's' stop (ink pools).
    cut: if given, only the first `cut` px (1x) of the stroke are painted (for animation);
         the brush head then sits there as a wet pool.
    """
    rng = random.Random(seed)
    S = SS
    raw = [(x * S, y * S) for x, y in path]
    if mode == "c":
        raw = catmull(raw, 16)
    else:
        raw = round_corners(raw, corner if corner is not None else width * S * 0.9)
    pts = resample(raw, 1.5 * S)
    if len(pts) < 2:
        return 0.0
    L = pts[-1][2]
    limit = L if cut is None else cut * S
    if limit <= 0:
        return L / S
    nrm = _normals(pts)
    Wd = width * S
    att = min(0.16, 1.4 * Wd / L)
    rel = min(0.42, 3.0 * Wd / L) if end == "f" else min(0.14, 1.0 * Wd / L)
    pn = VNoise(rng, L, pperiod * S)

    def press(t, s):
        p = 0.93 + pvar * (pn(s) - 0.5)
        if t < att:
            u = t / att
            p *= 0.80 + 0.32 * entry * (1 - u) * (1 - u) + 0.2 * smooth(u)
        if end == "f" and t > 1 - rel:
            u = (t - (1 - rel)) / rel
            p *= max(0.0, 1 - u) ** 1.1 * 0.96 + 0.04
        if end == "s" and t > 1 - rel:
            p *= 1.0 + 0.12 * smooth((t - (1 - rel)) / rel)
        return p

    nb = int(clamp(Wd / (1.4 * S) * bristle_scale, 12, 72))
    dry_eff = dry if end == "f" else dry * 0.3
    bristles = []
    for i in range(nb):
        o = -1 + 2 * (i + 0.5) / nb + rng.uniform(-1, 1) / nb
        th = max(1.0, Wd / nb * rng.uniform(1.15, 1.9))
        load = rng.uniform(0.85, 1.25) - 0.36 * abs(o) ** 2.2
        bristles.append((o, th, load, VNoise(rng, L, rng.uniform(16, 50) * S),
                         VNoise(rng, L, rng.uniform(4, 9) * S), rng.uniform(-1, 1)))

    for (o, th, load, nz, nz2, spl) in bristles:
        run = []
        for k, (x, y, s) in enumerate(pts):
            if s > limit:
                break
            t = s / L
            p = press(t, s)
            tx, ty, nx, ny = nrm[k]
            w = Wd * p * (0.70 + 0.30 * abs(ty) + 0.08 * max(0.0, tx * ty))
            spread = 1.0
            if end == "f" and t > 1 - rel:
                u = (t - (1 - rel)) / rel
                spread += 1.6 * u * u
            off = o * w * 0.5 * spread + spl * Wd * 0.05 * (1 if t > 0.9 else 0) * (t - 0.9) * 10
            v = load - dry_eff * max(0.0, t - wet) / max(1e-3, 1 - wet) * 1.25 * (1 + 0.9 * abs(o)) \
                + 0.62 * (nz(s) - 0.5) + 0.25 * (nz2(s) - 0.5)
            if t < att * 1.3:
                v += 0.6
            if v > 0.32:
                run.append((x + nx * off, y + ny * off))
            else:
                if len(run) > 1:
                    ink.da.line(run, fill=255, width=int(round(th)), joint="curve")
                run = []
        if len(run) > 1:
            ink.da.line(run, fill=255, width=int(round(th)), joint="curve")

    def wfac(k):
        ty = nrm[k][1]
        tx = nrm[k][0]
        return 0.70 + 0.30 * abs(ty) + 0.08 * max(0.0, tx * ty)

    def edge_poly(k0, k1, cut_l, cut_r, hw):
        left, right = [], []
        s0 = pts[k0][2]
        for k in range(k0, k1 + 1):
            x, y, s = pts[k]
            _, _, nx, ny = nrm[k]
            w = Wd * press(s / L, s) * wfac(k) * hw
            if s - s0 >= cut_l(k):
                left.append((x + nx * w, y + ny * w))
            if s - s0 >= cut_r(k):
                right.append((x - nx * w, y - ny * w))
        return left + right[::-1]

    # pressed entry: a solid wedge with an angled (diagonal) cut, like a brush landing at 45 deg
    kmax = 0
    while kmax < len(pts) - 1 and pts[kmax][2] < min(limit, Wd * 0.75):
        kmax += 1
    if kmax > 2 and round_entry:
        for k in range(0, kmax + 1, 2):
            x, y, s_ = pts[k]
            u = s_ / (Wd * 0.75)
            r = Wd * 0.5 * press(s_ / L, s_) * wfac(k) * (0.55 + 0.45 * smooth(u * 1.4))
            ink.da.ellipse((x - r, y - r, x + r, y + r), fill=255)
    elif kmax > 2:
        side = 1 if rng.random() < 0.5 else -1
        cl = (lambda k: 0.0) if side > 0 else (lambda k: Wd * 0.32)
        cr = (lambda k: Wd * 0.32) if side > 0 else (lambda k: 0.0)
        poly = edge_poly(0, kmax, cl, cr, 0.46)
        if len(poly) > 2:
            ink.da.polygon(poly, fill=255)
        x, y, _ = pts[min(3, kmax)]
        rp = Wd * 0.22
        ink.dp.ellipse((x - rp, y - rp, x + rp, y + rp), fill=int(70 + 50 * entry))

    # corner pools: the brush hesitates on turns
    last = -99
    for k in range(6, len(pts) - 6):
        if pts[k][2] > limit:
            break
        a = nrm[k - 6]
        b = nrm[k + 6]
        dot = a[0] * b[0] + a[1] * b[1]
        if dot < 0.35 and k - last > 14:
            ink.blob(pts[k][0], pts[k][1], Wd * 0.36, rng, val=110)
            last = k

    if cut is not None and limit < L:
        # wet brush head where the brush currently is
        k = max(0, min(len(pts) - 1, int(limit / (1.5 * S))))
        if head:
            ink.blob(pts[k][0], pts[k][1], Wd * 0.42 * press(limit / L, limit), rng, val=255)
        return L / S

    xe, ye, _ = pts[-1]
    tx, ty, nx, ny = nrm[-1]
    if end == "s":
        # blunt stop: brush pauses and lifts straight up, ink pools at the heel
        k0 = len(pts) - 1
        while k0 > 0 and L - pts[k0][2] < Wd * 0.6:
            k0 -= 1
        poly = edge_poly(k0, len(pts) - 1, lambda k: 0.0, lambda k: 0.0, 0.47)
        if len(poly) > 2:
            ink.da.polygon(poly, fill=255)
        xe2, ye2 = xe + tx * Wd * 0.05, ye + ty * Wd * 0.05
        r = Wd * 0.33 * wfac(len(pts) - 1)
        ink.da.ellipse((xe2 - tx * r * 0.6 - r, ye2 - ty * r * 0.6 - r, xe2 - tx * r * 0.6 + r, ye2 - ty * r * 0.6 + r), fill=255)
        rp = Wd * 0.2
        cxp, cyp = xe - tx * Wd * 0.22, ye - ty * Wd * 0.22
        ink.dp.ellipse((cxp - rp, cyp - rp * 1.3, cxp + rp, cyp + rp * 1.3), fill=140)
    if splat > 0:
        cnt = int(splat * rng.uniform(5, 15)) if end == "f" else int(splat * rng.uniform(1, 5))
        for _ in range(cnt):
            d = rng.uniform(0.1, 2.4) * Wd
            spread = rng.gauss(0, 0.45 * Wd)
            px, py = xe + tx * d + nx * spread, ye + ty * d + ny * spread
            r = clamp(rng.expovariate(1 / (0.05 * Wd + 0.5 * S)), 0.6 * S, 0.16 * Wd + S)
            ink.da.ellipse((px - r, py - r, px + r, py + r), fill=255)
            if rng.random() < 0.4:
                ln = r * rng.uniform(2, 5)
                ink.da.line([(px - tx * ln, py - ty * ln), (px, py)], fill=255, width=max(1, int(r * 0.9)))
            if r > 2.5 * S:
                ink.dp.ellipse((px - r * 0.7, py - r * 0.7, px + r * 0.7, py + r * 0.7), fill=200)
    return L / S


def ink_layers(ink, thin, dense, sheen=0.0, bleed=0.0, matte=0.0, bleed_seed=7):
    """Turn an Ink into (rgb, alpha, sheen_alpha)."""
    a = blur(ink.a, 0.55 * SS)
    pool = blur(ink.pool, 1.1 * SS)
    dens = blur(ink.a, 5 * SS)
    tone = ImageChops.lighter(pool, dens.point([int(v * v / 255) for v in range(256)]))
    if matte > 0:
        tone = scale_l(tone, 1 - 0.35 * matte)
    col = Image.composite(solid(dense, (CW, CH)), solid(thin, (CW, CH)), tone)
    alpha = ImageChops.lighter(scale_l(a, 0.97), pool)
    if bleed > 0:
        rng = random.Random(bleed_seed)
        halo = blur(ink.a.filter(ImageFilter.MaxFilter(5)), (2 + 7 * bleed) * SS)
        fib = noise(CW // 4, CH // 4, 3, rng).resize((CW, CH), Image.BILINEAR)
        halo = ImageChops.multiply(halo, scale_l(fib, 1.0, 40))
        alpha = ImageChops.lighter(alpha, scale_l(halo, 0.55 * bleed))
    sh = None
    if sheen > 0:
        A = blur(ImageChops.lighter(pool, scale_l(ink.a, 0.35)), 1.4 * SS)
        d = ImageChops.subtract(A, shift(A, int(1.5 * SS), int(1.5 * SS)), 0.4)
        wetmask = ramp(blur(pool, 1.5 * SS), 60, 180)
        sh = scale_l(ImageChops.multiply(d, wetmask), sheen)
        sh = blur(sh, 0.5 * SS)
    return col, alpha, sh


# watercolour ------------------------------------------------------------------------
class Pigment:
    def __init__(self):
        self.m = Image.new("L", (CW, CH), 0)


def wash(pig, draw_fn, bbox, seed, rough=1.0, bloom=0.6, gran=0.6, edge=1.0, body=150, soft=5):
    """Watercolour wash. draw_fn(draw, ox, oy) draws the wet area in SS coords minus (ox, oy)."""
    rng = random.Random(seed)
    pad = 50 * SS
    x0, y0 = int(bbox[0] * SS) - pad, int(bbox[1] * SS) - pad
    x1, y1 = int(bbox[2] * SS) + pad, int(bbox[3] * SS) + pad
    w, h = x1 - x0, y1 - y0
    if isinstance(draw_fn, Image.Image):
        M = draw_fn.crop((x0, y0, x1, y1))
    else:
        M = Image.new("L", (w, h), 0)
        draw_fn(ImageDraw.Draw(M), x0, y0)
    n1 = noise(w, h, 34 * SS, rng)
    n2 = noise(w, h, 9 * SS, rng)
    n3 = noise(w, h, 60 * SS, rng)
    hf = white(w, h, rng, 0.7 * SS)
    m = blur(M, soft * SS)
    e = addn(addn(m, n1, 0.9 * rough), n2, 0.45 * rough)
    E = ramp(e, 118, 138)
    mb = blur(M, 16 * SS)
    eb = addn(mb, n2, 0.9)
    Eb = scale_l(blur(ramp(eb, 96, 150), 1.5 * SS), 0.2 * bloom)
    D = n3.point([int(clamp(body + (v - 128) * 0.85, 0, 255)) for v in range(256)])
    band = ImageChops.subtract(E, blur(E, 3.5 * SS), 0.45)
    pg = ImageChops.add(ImageChops.multiply(E, D), scale_l(band, 0.85 * edge))
    hf2 = white(w, h, rng, 0.45 * SS)
    speck = ImageChops.multiply(ramp(hf2, 170, 255, int(110 * gran)), E)
    pg = ImageChops.add(ImageChops.multiply(pg, scale_l(hf2, 0.22 * gran, 255 - 56 * gran)), speck)
    pg = ImageChops.lighter(pg, Eb)
    region = pig.m.crop((x0, y0, x1, y1))
    pig.m.paste(ImageChops.lighter(region, pg), (x0, y0))


def swash_fn(path, r, taper=0.25, seed=1, mode="c"):
    """Broad wet brush sweep (wash shape)."""
    rng = random.Random(seed)

    def fn(d, ox, oy):
        raw = [(x * SS - ox, y * SS - oy) for x, y in path]
        raw = catmull(raw, 16) if mode == "c" else raw
        pts = resample(raw, 2 * SS)
        L = pts[-1][2] or 1
        nz = VNoise(rng, L, 40 * SS)
        for x, y, s in pts:
            t = s / L
            k = min(1.0, t / taper, (1 - t) / taper) if taper > 0 else 1.0
            rr = r * SS * (0.35 + 0.65 * smooth(k)) * (0.85 + 0.3 * nz(s))
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=255)
    return fn


def disc_fn(cx, cy, r):
    def fn(d, ox, oy):
        d.ellipse((cx * SS - r * SS - ox, cy * SS - r * SS - oy, cx * SS + r * SS - ox, cy * SS + r * SS - oy), fill=255)
    return fn


def pigment_layers(pig, light, deep, gain=1.15):
    curve = ramp(pig.m, 70, 255)
    col = Image.composite(solid(deep, (CW, CH)), solid(light, (CW, CH)), curve)
    alpha = scale_l(pig.m, gain)
    return col, alpha


# paper, tape --------------------------------------------------------------------------
def torn_poly(w, h, rng, amp=4.0, step=3.0, tear=0.05):
    pts = []

    def edge(p0, p1):
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        n = max(2, int(L / step))
        nx, ny = -(p1[1] - p0[1]) / L, (p1[0] - p0[0]) / L
        off = 0.0
        out = []
        for i in range(n):
            t = i / n
            off = clamp(off + rng.gauss(0, amp * 0.45), -amp, amp)
            big = rng.gauss(0, amp * 1.2) if rng.random() < tear else 0.0
            o = off + big
            out.append((p0[0] + (p1[0] - p0[0]) * t + nx * o, p0[1] + (p1[1] - p0[1]) * t + ny * o))
        return out
    corners = [(0, 0), (w, 0), (w, h), (0, h)]
    for i in range(4):
        pts += edge(corners[i], corners[(i + 1) % 4])
    return pts


def paper_patch(w, h, seed, tone=PAPER, fibre=1.0, alpha=238, amp=3.5):
    """Torn washi/rice paper sheet, w,h in 1x px. Returns RGBA at SS."""
    rng = random.Random(seed)
    S = SS
    pad = 14 * S
    PW, PH = int(w * S) + 2 * pad, int(h * S) + 2 * pad
    poly = [(x + pad, y + pad) for x, y in torn_poly(w * S, h * S, rng, amp=amp * S, step=3 * S)]
    mask = Image.new("L", (PW, PH), 0)
    md = ImageDraw.Draw(mask)
    md.polygon(poly, fill=alpha)
    # fibre hairs along the torn edge
    hair = Image.new("L", (PW, PH), 0)
    hd = ImageDraw.Draw(hair)
    for i, (x, y) in enumerate(poly):
        if rng.random() < 0.55 * fibre:
            cx, cy = PW / 2, PH / 2
            dx, dy = x - cx, y - cy
            l = math.hypot(dx, dy) or 1
            ang = math.atan2(dy, dx) + rng.gauss(0, 0.9)
            ln = rng.uniform(2, 10) * S
            pts = [(x, y)]
            for j in range(3):
                ang += rng.gauss(0, 0.4)
                pts.append((pts[-1][0] + math.cos(ang) * ln / 3, pts[-1][1] + math.sin(ang) * ln / 3))
            hd.line(pts, fill=rng.randint(110, 200), width=1)
    mask = ImageChops.lighter(mask, hair)
    mask = blur(mask, 0.5 * S)
    # body tone
    n1 = noise(PW, PH, 40 * S, rng)
    n2 = noise(PW, PH, 6 * S, rng)
    base = Image.new("RGB", (PW, PH), tone)
    dark = Image.new("RGB", (PW, PH), tuple(int(c * 0.9) for c in tone))
    lite = Image.new("RGB", (PW, PH), tuple(min(255, int(c * 1.04 + 6)) for c in tone))
    col = Image.composite(dark, base, scale_l(n1, 0.35, -20))
    col = Image.composite(lite, col, scale_l(n2, 0.25, -10))
    # internal fibres (kozo strands)
    fl = Image.new("L", (PW, PH), 0)
    fd_ = Image.new("L", (PW, PH), 0)
    dl, dd = ImageDraw.Draw(fl), ImageDraw.Draw(fd_)
    nf = int(w * h / 90 * fibre)
    for _ in range(nf):
        x, y = rng.uniform(0, PW), rng.uniform(0, PH)
        ang = rng.uniform(0, math.tau)
        ln = rng.uniform(8, 50) * S
        pts = [(x, y)]
        for j in range(5):
            ang += rng.gauss(0, 0.35)
            pts.append((pts[-1][0] + math.cos(ang) * ln / 5, pts[-1][1] + math.sin(ang) * ln / 5))
        (dl if rng.random() < 0.7 else dd).line(pts, fill=rng.randint(60, 150), width=1 if rng.random() < 0.8 else 2)
    col = Image.composite(Image.new("RGB", (PW, PH), (252, 250, 244)), col, blur(fl, 0.4 * S))
    col = Image.composite(Image.new("RGB", (PW, PH), tuple(int(c * 0.82) for c in tone)), col, scale_l(blur(fd_, 0.4 * S), 0.6))
    # inclusions: tiny dark specks
    sp = Image.new("L", (PW, PH), 0)
    sd = ImageDraw.Draw(sp)
    for _ in range(int(w * h / 1800)):
        x, y = rng.uniform(0, PW), rng.uniform(0, PH)
        r = rng.uniform(0.4, 1.4) * S
        sd.ellipse((x - r, y - r, x + r, y + r), fill=rng.randint(60, 160))
    col = Image.composite(Image.new("RGB", (PW, PH), (120, 110, 100)), col, blur(sp, 0.4 * S))
    out = col.convert("RGBA")
    out.putalpha(mask)
    return out


def tape_patch(w, h, seed, color=(232, 226, 208), alpha=190):
    rng = random.Random(seed)
    S = SS
    PW, PH = int(w * S) + 8 * S, int(h * S) + 8 * S
    poly = []
    n = 7
    ox, oy = 4 * S, 4 * S
    # zig-zag torn short ends
    for i in range(n + 1):
        poly.append((ox + rng.uniform(-2, 2) * S + (2 * S if i % 2 else 0), oy + i * h * S / n))
    poly = poly[::-1]
    right = []
    for i in range(n + 1):
        right.append((ox + w * S + rng.uniform(-2, 2) * S - (2 * S if i % 2 else 0), oy + i * h * S / n))
    poly = [(ox, oy)] + [(ox + w * S, oy)] + right + [(ox, oy + h * S)] + poly
    poly = [(ox + w * S * 0.0, oy)] + [(ox + w * S, oy)] + right + list(reversed(
        [(ox + rng.uniform(-2, 2) * S + (2 * S if i % 2 else 0), oy + i * h * S / n) for i in range(n + 1)]))
    mask = Image.new("L", (PW, PH), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=alpha)
    n1 = noise(PW, PH, 10 * S, rng)
    mask = ImageChops.multiply(mask, scale_l(n1, 0.18, 210))
    col = Image.new("RGB", (PW, PH), color)
    crease = Image.new("L", (PW, PH), 0)
    cd = ImageDraw.Draw(crease)
    for _ in range(4):
        x = rng.uniform(0, PW)
        cd.line([(x, 0), (x + rng.uniform(-20, 20) * S, PH)], fill=rng.randint(40, 90), width=S)
    col = Image.composite(Image.new("RGB", (PW, PH), (255, 255, 255)), col, blur(crease, 1.2 * S))
    out = col.convert("RGBA")
    out.putalpha(blur(mask, 0.4 * S))
    return out


class Place:
    """Maps patch-local 1x coords (origin at patch centre, y down) to screen 1x coords."""

    def __init__(self, cx, cy, ang_deg):
        self.cx, self.cy = cx, cy
        self.a = math.radians(ang_deg)
        self.deg = ang_deg

    def __call__(self, x, y):
        c, s = math.cos(self.a), math.sin(self.a)
        return (self.cx + x * c - y * s, self.cy + x * s + y * c)

    def pts(self, pts):
        return [self(x, y) for x, y in pts]


def paste_patch(canvas, patch, place, shadow=0.55, sh_off=(3, 6), sh_blur=6):
    """canvas: RGBA SS. patch rotated by place.deg (screen y down => rotate by -deg in PIL)."""
    rot = patch.rotate(-place.deg, resample=Image.BICUBIC, expand=True)
    x = int(place.cx * SS - rot.width / 2)
    y = int(place.cy * SS - rot.height / 2)
    if shadow > 0:
        a = rot.getchannel("A")
        sh = blur(a, sh_blur * SS)
        sh = scale_l(sh, shadow)
        shimg = Image.new("RGBA", rot.size, (6, 4, 10, 0))
        shimg.putalpha(sh)
        canvas.alpha_composite(shimg, (x + int(sh_off[0] * SS), y + int(sh_off[1] * SS)))
    canvas.alpha_composite(rot, (x, y))


# text with a font, inked ---------------------------------------------------------------
def font_ink(ink, text_lines, place, size, seed, font="Inkfree.ttf", lead=1.18, x0=0, y0=0, rough=0.5):
    """Write lines of handwriting into an Ink layer, on a placed patch (local x0,y0 = top-left)."""
    rng = random.Random(seed)
    f = ImageFont.truetype(FONTS + font, int(size * SS))
    lines = text_lines
    tw = max(int(f.getlength(l)) for l in lines) + 20 * SS
    th = int(size * SS * lead * len(lines)) + 20 * SS
    img = Image.new("L", (tw, th), 0)
    d = ImageDraw.Draw(img)
    for i, l in enumerate(lines):
        d.text((10 * SS + rng.uniform(-2, 2) * SS, 10 * SS + i * size * SS * lead), l, font=f, fill=255)
    # ink texture: soak + dry edge
    soak = blur(img.filter(ImageFilter.MaxFilter(3)), 0.8 * SS)
    tex = white(tw, th, rng, 0.6 * SS)
    img = ImageChops.lighter(img, scale_l(soak, 0.5))
    img = ImageChops.multiply(img, scale_l(tex, 0.35 * rough, 255 - 90 * rough))
    rot = img.rotate(-place.deg, resample=Image.BICUBIC, expand=True)
    # local top-left -> centre of the text image in local coords
    lcx = x0 + tw / SS / 2 - 10
    lcy = y0 + th / SS / 2 - 10
    cx, cy = place(lcx, lcy)
    px, py = int(cx * SS - rot.width / 2), int(cy * SS - rot.height / 2)
    region = ink.a.crop((px, py, px + rot.width, py + rot.height))
    ink.a.paste(ImageChops.lighter(region, rot), (px, py))


def comp(canvas_rgba, col_rgb, alpha_l):
    layer = col_rgb.convert("RGBA")
    layer.putalpha(alpha_l)
    canvas_rgba.alpha_composite(layer)


def finish(canvas_rgba):
    return canvas_rgba.convert("RGB").resize((W, H), Image.LANCZOS)


def load_base(path):
    return Image.open(path).convert("RGB").resize((CW, CH), Image.BICUBIC).convert("RGBA")


def darken_under(canvas, alpha_l, amount=0.35, radius=14):
    m = scale_l(blur(alpha_l, radius * SS), amount)
    sh = Image.new("RGBA", canvas.size, (8, 6, 12, 0))
    sh.putalpha(m)
    canvas.alpha_composite(sh)


def stroke_mask(path, width, seed, end="f", dry=0.85, wet=0.3, mode="c", splat=0.15):
    """Coverage of one big brush sweep, for use as a wash shape (keeps dry-brush streaks)."""
    tmp = Ink()
    brush_stroke(tmp, path, width, seed, end=end, dry=dry, wet=wet, splat=splat, mode=mode,
                 pvar=0.2, pperiod=170, round_entry=True)
    return tmp.a
