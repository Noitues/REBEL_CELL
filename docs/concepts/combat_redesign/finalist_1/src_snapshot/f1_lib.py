"""sg_lib: the black-book hand.  Procedural marker, ballpoint, highlighter, paper, tape, lettering, torn edges.
All geometry is in 1x canvas px; the Canvas keeps a premultiplied float buffer at S x supersample."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
from scipy import ndimage as ndi

FD = 'D:/rc_art/art-pass/assets/fonts/'
MARKER_F = FD + 'PermanentMarker-Regular.ttf'
ANTON_F = FD + 'Anton-Regular.ttf'
MONO_F = FD + 'ShareTechMono-Regular.ttf'
HAND_F = 'C:/Windows/Fonts/Inkfree.ttf'
PRINT_F = 'C:/Windows/Fonts/segoepr.ttf'

PINK = (255, 61, 168)
PINK_D = (214, 28, 134)
PINK_L = (255, 150, 208)
PAPER = (242, 238, 228)
INK = (17, 17, 17)
BLUE = (44, 62, 158)
GAIN = (123, 224, 123)
HARM = (255, 68, 51)
SOAK = (70, 78, 255)
CYAN = (92, 225, 255)
VIOLET = (160, 60, 255)
WHITE = (250, 250, 246)

_fc = {}


def font(path, px):
    k = (path, int(px))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, int(px))
    return _fc[k]


def smooth(h, w, scale, r):
    """smooth noise, std ~ 1, feature size ~ scale px"""
    gh, gw = max(2, int(h / scale) + 2), max(2, int(w / scale) + 2)
    n = r.standard_normal((gh, gw)).astype(np.float32)
    im = Image.fromarray(n, 'F').resize((w, h), Image.BICUBIC)
    a = np.asarray(im, np.float32)
    return a / (a.std() + 1e-6)


def resample(P, step):
    P = np.asarray(P, float)
    if len(P) < 2:
        return P
    d = np.hypot(*np.diff(P, axis=0).T)
    s = np.concatenate([[0], np.cumsum(d)])
    n = max(2, int(s[-1] / step) + 1)
    t = np.linspace(0, s[-1], n)
    return np.stack([np.interp(t, s, P[:, 0]), np.interp(t, s, P[:, 1])], 1)


def wobble_path(P, amp, wl, r):
    if amp <= 0 or len(P) < 3:
        return P
    d = np.hypot(*np.diff(P, axis=0).T)
    s = np.concatenate([[0], np.cumsum(d)])
    ph = r.uniform(0, 6.28, 3)
    off = amp * (0.6 * np.sin(s / wl * 6.283 + ph[0]) + 0.3 * np.sin(s / (wl * 0.41) * 6.283 + ph[1]) + 0.1 * np.sin(s / (wl * 0.13) * 6.283 + ph[2]))
    tg = np.gradient(P, axis=0)
    nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
    nr /= (np.hypot(nr[:, 0], nr[:, 1])[:, None] + 1e-9)
    return P + nr * off[:, None]


def arc_pts(c, r, a0, a1, step=1.0):
    """angles in deg, 0 = up, clockwise"""
    n = max(3, int(abs(a1 - a0) * math.pi / 180 * r / step))
    a = np.radians(np.linspace(a0, a1, n))
    return np.stack([c[0] + r * np.sin(a), c[1] - r * np.cos(a)], 1)


def pol(c, r, a):
    a = math.radians(a)
    return (c[0] + r * math.sin(a), c[1] - r * math.cos(a))


class Canvas:
    def __init__(s, w, h, S=4, seed=1):
        s.w, s.h, s.S = w, h, S
        s.W, s.H = int(w * S), int(h * S)
        s.P = np.zeros((s.H, s.W, 3), np.float32)
        s.A = np.zeros((s.H, s.W), np.float32)
        s.r = np.random.default_rng(seed)

    # --- compositing (m is a float 0..1 local mask, (x0,y0) its SS-px offset)
    def _clip(s, m, x0, y0):
        h, w = m.shape
        xa, ya = max(0, x0), max(0, y0)
        xb, yb = min(s.W, x0 + w), min(s.H, y0 + h)
        if xb <= xa or yb <= ya:
            return None
        return m[ya - y0:yb - y0, xa - x0:xb - x0], xa, ya, xb, yb

    def over(s, m, col, alpha=1.0, x0=0, y0=0):
        c = s._clip(m, x0, y0)
        if c is None:
            return
        m, xa, ya, xb, yb = c
        a = (m * alpha)[..., None]
        col = np.asarray(col, np.float32)
        s.P[ya:yb, xa:xb] = col * a + s.P[ya:yb, xa:xb] * (1 - a)
        s.A[ya:yb, xa:xb] = a[..., 0] + s.A[ya:yb, xa:xb] * (1 - a[..., 0])

    def over_rgb(s, m, rgb, x0=0, y0=0):
        """rgb: local (h,w,3) float colours"""
        c = s._clip(m, x0, y0)
        if c is None:
            return
        mm, xa, ya, xb, yb = c
        rr = rgb[ya - y0:yb - y0, xa - x0:xb - x0]
        a = mm[..., None]
        s.P[ya:yb, xa:xb] = rr * a + s.P[ya:yb, xa:xb] * (1 - a)
        s.A[ya:yb, xa:xb] = mm + s.A[ya:yb, xa:xb] * (1 - mm)

    def mult(s, m, col, alpha=1.0, x0=0, y0=0):
        """highlighter: multiply over what is there (alpha buffer unchanged)"""
        c = s._clip(m, x0, y0)
        if c is None:
            return
        m, xa, ya, xb, yb = c
        a = (m * alpha)[..., None]
        col = np.asarray(col, np.float32) / 255.0
        s.P[ya:yb, xa:xb] = s.P[ya:yb, xa:xb] * (1 - a + a * col)

    def erase(s, m, x0=0, y0=0):
        c = s._clip(m, x0, y0)
        if c is None:
            return
        m, xa, ya, xb, yb = c
        s.P[ya:yb, xa:xb] *= (1 - m)[..., None]
        s.A[ya:yb, xa:xb] *= (1 - m)

    def paste(s, im, x, y, alpha=1.0):
        """straight RGBA PIL at 1x position (x,y) of an already-SS image"""
        a = np.asarray(im, np.float32) / 255.0
        m = a[..., 3] * alpha
        s.over_rgb(m, a[..., :3] * 255.0, int(round(x * s.S)), int(round(y * s.S)))

    def rgba(s):
        a = np.clip(s.A, 0, 1)
        rgb = s.P / np.maximum(a, 1e-4)[..., None]
        out = np.dstack([np.clip(rgb, 0, 255), a * 255.0]).astype(np.uint8)
        return Image.fromarray(out, 'RGBA')

    def down(s):
        im = s.rgba()
        # premultiplied-safe downsample
        P = Image.fromarray(np.clip(s.P, 0, 255).astype(np.uint8), 'RGB')
        A = Image.fromarray(np.clip(s.A * 255, 0, 255).astype(np.uint8), 'L')
        P2 = np.asarray(P.resize((s.w, s.h), Image.LANCZOS), np.float32)
        A2 = np.asarray(A.resize((s.w, s.h), Image.LANCZOS), np.float32) / 255.0
        # P is premultiplied-ish (colour*alpha) stored as 0..255: resizing P and A separately keeps ratio
        rgb = P2 / np.maximum(A2, 1e-4)[..., None]
        return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), A2 * 255]).astype(np.uint8), 'RGBA')

    # --- masks from PIL drawing at SS scale
    def new_mask(s):
        return Image.new('L', (s.W, s.H), 0)

    def poly_mask(s, pts, blur=0.0):
        im = s.new_mask()
        ImageDraw.Draw(im).polygon([(x * s.S, y * s.S) for x, y in pts], fill=255)
        a = np.asarray(im, np.float32) / 255.0
        if blur:
            a = ndi.gaussian_filter(a, blur * s.S)
        return a

    def circle_mask(s, c, r):
        im = s.new_mask()
        ImageDraw.Draw(im).ellipse([(c[0] - r) * s.S, (c[1] - r) * s.S, (c[0] + r) * s.S, (c[1] + r) * s.S], fill=255)
        return np.asarray(im, np.float32) / 255.0

    def band_mask(s, c, r0, r1, a0, a1, step=1.0):
        o = arc_pts(c, r1, a0, a1, step)
        i = arc_pts(c, r0, a1, a0, step)
        return s.poly_mask(np.concatenate([o, i]))


# ---------------------------------------------------------------- marker / ballpoint strokes
def _profile(n, taper):
    t = np.linspace(0, 1, n)
    p = np.ones(n)
    a, b = taper
    if a > 0:
        p = np.minimum(p, 0.35 + 0.65 * np.clip(t / a, 0, 1))
    if b > 0:
        p = np.minimum(p, 0.35 + 0.65 * np.clip((1 - t) / b, 0, 1))
    return p


def stroke_mask(cv, pts, w, nib='round', ang=35, wob=0.6, wl=40, taper=(0.1, 0.1), press=0.0, step=0.45):
    """returns local float mask + (x0,y0) offset in SS px"""
    S = cv.S
    P = resample(pts, step)
    P = wobble_path(P, wob, wl, cv.r)
    n = len(P)
    wid = w * _profile(n, taper)
    if press:
        wid = wid * (1 + press * np.sin(np.linspace(0, cv.r.uniform(2, 6), n) + cv.r.uniform(0, 6)))
    pad = w * S + 6
    Ps = P * S
    x0, y0 = int(Ps[:, 0].min() - pad), int(Ps[:, 1].min() - pad)
    x1, y1 = int(Ps[:, 0].max() + pad), int(Ps[:, 1].max() + pad)
    im = Image.new('L', (x1 - x0, y1 - y0), 0)
    d = ImageDraw.Draw(im)
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    for i in range(n):
        x, y = Ps[i, 0] - x0, Ps[i, 1] - y0
        hw = wid[i] * S / 2
        if nib == 'round':
            d.ellipse([x - hw, y - hw, x + hw, y + hw], fill=255)
        else:
            L, T = hw, max(1.0, hw * 0.32)
            poly = [(x + ca * L - (-sa) * T, y + sa * L - ca * T), (x + ca * L + (-sa) * T, y + sa * L + ca * T),
                    (x - ca * L + (-sa) * T, y - sa * L + ca * T), (x - ca * L - (-sa) * T, y - sa * L - ca * T)]
            d.polygon(poly, fill=255)
    return np.asarray(im, np.float32) / 255.0, x0, y0


def finish_mask(cv, m, grain=0.14, rough=0.22, pool=0.28, soft=0.55):
    """ragged ink edge, streak grain, pooled edge"""
    S = cv.S
    h, w = m.shape
    b = ndi.gaussian_filter(m, soft * S / 4 * 1.4)
    n_hi = smooth(h, w, 1.3 * S / 4 * 1.6, cv.r)
    e = np.clip((b - 0.5 + n_hi * rough * 0.25) * 4 + 0.5, 0, 1)
    n_lo = smooth(h, w, 5 * S / 4, cv.r)
    g = 1 - grain * np.clip(n_lo * 0.5 + 0.5, 0, 1) * (0.6 + 0.4 * np.abs(n_hi))
    inner = ndi.gaussian_filter(e, 2.2 * S / 4)
    edge = np.clip(e - inner, 0, 1)
    return np.clip(e * g + edge * pool, 0, 1)


def marker(cv, pts, col, w=6, nib='round', ang=35, alpha=0.92, wob=0.6, wl=40, taper=(0.1, 0.1), grain=0.14, rough=0.22, pool=0.28, mode='over', press=0.0):
    m, x0, y0 = stroke_mask(cv, pts, w, nib, ang, wob, wl, taper, press)
    m = finish_mask(cv, m, grain, rough, pool)
    if mode == 'mult':
        cv.mult(m, col, alpha, x0, y0)
    else:
        cv.over(m, col, alpha, x0, y0)
    return m, x0, y0


def ballpoint(cv, pts, col=BLUE, w=0.9, alpha=0.85, wob=0.5, wl=30, taper=(0.12, 0.12), step=0.4):
    """thin pressure-varied pen line"""
    m, x0, y0 = stroke_mask(cv, pts, w, 'round', 0, wob, wl, taper, press=0.35, step=step)
    b = ndi.gaussian_filter(m, 0.5)
    n = smooth(*b.shape, 1.2 * cv.S / 4 * 1.5, cv.r)
    b = np.clip(b * (0.88 + 0.12 * n), 0, 1)
    cv.over(b, col, alpha, x0, y0)


def sketch_circle(cv, c, r, col=BLUE, w=0.9, passes=2, a0=None, alpha=0.8, over=14, wob=0.6):
    for k in range(passes):
        s0 = (cv.r.uniform(0, 360) if a0 is None else a0 + cv.r.uniform(-4, 4))
        n = 1.0 + over / 360.0 + 0.0
        rr = r * (1 + cv.r.uniform(-0.012, 0.012))
        pts = []
        for a in np.linspace(0, 360 + over, 90):
            drift = 1 + 0.012 * (a / 360.0) * (1 if k % 2 else -1)
            pts.append(pol(c, rr * drift, s0 + a))
        ballpoint(cv, pts, col, w, alpha, wob=wob, wl=r * 1.5, taper=(0.08, 0.1))


def sketch_line(cv, p0, p1, col=BLUE, w=0.9, passes=1, alpha=0.8, over=3.0, wob=0.4):
    for k in range(passes):
        a = np.array(p0, float); b = np.array(p1, float)
        d = b - a
        L = np.hypot(*d) + 1e-9
        u = d / L
        a2 = a - u * over * cv.r.uniform(0.2, 1.0) + cv.r.normal(0, 0.4, 2)
        b2 = b + u * over * cv.r.uniform(0.2, 1.0) + cv.r.normal(0, 0.4, 2)
        ballpoint(cv, [a2, (a2 + b2) / 2 + cv.r.normal(0, 0.5, 2), b2], col, w, alpha, wob=wob, wl=max(8, L / 2))


# ---------------------------------------------------------------- region fill / hatch (strokes clipped by a region)
def _rot_strokes(cv, region, box, ang, pitch, width, col_a, over, jit, nib_lines=True, slope=0.01, seed_off=0):
    """region: float mask (h,w) local; draws horizontal strokes in the rotated frame, returns (acc mask, same shape).
    pitch/width in SS px.  Strokes follow the region's chords, ends jittered by `over` px SS."""
    h, w = region.shape
    im = Image.fromarray((np.clip(region, 0, 1) * 255).astype(np.uint8), 'L')
    R = im.rotate(ang, resample=Image.BILINEAR, expand=True)
    Rm = np.asarray(R) > 110
    Hr, Wr = Rm.shape
    E = Image.new('L', (Wr, Hr), 0)
    O = Image.new('L', (Wr, Hr), 0)
    de, do = ImageDraw.Draw(E), ImageDraw.Draw(O)
    y = pitch * 0.6
    i = 0
    r = cv.r
    while y < Hr:
        row = Rm[int(y)]
        if row.any():
            edges = np.diff(np.concatenate([[0], row.astype(np.int8), [0]]))
            st = np.where(edges == 1)[0]
            en = np.where(edges == -1)[0]
            for a, b in zip(st, en):
                if b - a < 3:
                    continue
                x0 = a - r.uniform(-over * 0.3, over)
                x1 = b + r.uniform(-over * 0.3, over)
                yy = y + r.normal(0, jit)
                sl = r.normal(0, slope) * (x1 - x0)
                v = int(np.clip(r.normal(col_a, 22), 120, 255))
                dd = de if i % 2 == 0 else do
                dd.line([(x0, yy), ((x0 + x1) / 2, yy + sl / 2 + r.normal(0, jit * 0.5)), (x1, yy + sl)], fill=v, width=max(1, int(width)))
        y += pitch * r.uniform(0.9, 1.1)
        i += 1
    e = np.asarray(E, np.float32) / 255.0
    o = np.asarray(O, np.float32) / 255.0
    acc = 1 - (1 - e * 0.88) * (1 - o * 0.88)
    A = Image.fromarray((acc * 255).astype(np.uint8), 'L').rotate(-ang, resample=Image.BILINEAR, expand=True)
    A = np.asarray(A, np.float32) / 255.0
    Ha, Wa = A.shape
    cy, cx = Ha // 2, Wa // 2
    return A[cy - h // 2:cy - h // 2 + h, cx - w // 2:cx - w // 2 + w]


def fill_region(cv, region, x0, y0, col, ang=35, nib=9, over=4, alpha=0.93, grain=0.16, miss=(0, 0), highlight=None, jit=0.6, clip=1.0):
    """marker zig-zag fill of a region (local mask at box x0,y0 in SS px).  nib in 1x px.  miss: (dx,dy) 1x px the region is shifted."""
    S = cv.S
    reg = region
    if miss != (0, 0):
        reg = np.roll(np.roll(reg, int(miss[1] * S), 0), int(miss[0] * S), 1)
    acc = _rot_strokes(cv, reg, None, ang, nib * S * 0.80, nib * S, 235, over * S, jit * S)
    acc = np.clip(acc, 0, 1)
    n_lo = smooth(*acc.shape, 6 * S / 4 * 1.5, cv.r)
    n_hi = smooth(*acc.shape, 1.2 * S / 4 * 1.5, cv.r)
    b = ndi.gaussian_filter(acc, 0.5 * S / 4 * 1.5)
    # clip to region + overshoot allowance, ragged edge
    e = np.clip((b - 0.5 + n_hi * 0.05) * 5 + 0.5, 0, 1)
    clipm = ndi.gaussian_filter(ndi.binary_dilation(reg > 0.5, iterations=max(1, int(clip * S))).astype(np.float32), 0.5 * S / 4 * 1.5)
    e = e * clipm
    g = 1 - grain * np.clip(n_lo * 0.5 + 0.5, 0, 1) * (0.6 + 0.4 * np.abs(n_hi))
    core = ndi.binary_erosion(reg > 0.5, iterations=max(1, int(nib * S * 0.55))).astype(np.float32)
    core = ndi.gaussian_filter(core, 1.2 * S)
    cv.over(core * g, col, alpha * 0.62, x0, y0)
    cv.over(e * g, col, alpha, x0, y0)
    return e


def hatch_region(cv, region, x0, y0, col, ang=45, pitch=5, w=1.6, alpha=0.9, over=1.5, jit=0.4, cross=False, wob=0.0):
    S = cv.S
    for k, a in enumerate((ang, ang + 90) if cross else (ang,)):
        acc = _rot_strokes(cv, region, None, a, pitch * S, w * S, 230, over * S, jit * S, slope=0.004)
        b = ndi.gaussian_filter(acc, 0.45 * S / 4 * 1.5)
        n = smooth(*b.shape, 1.2 * S / 4 * 1.5, cv.r)
        b = np.clip(b * (0.9 + 0.1 * n), 0, 1)
        cv.over(b, col, alpha, x0, y0)


def outline_mask(region, S, width, inner=0.0):
    """ring of `width` px (1x) outside the region (dilate - region)"""
    k = max(1, int(width * S))
    d = ndi.binary_dilation(region > 0.5, structure=ndi.generate_binary_structure(2, 1), iterations=k)
    if inner:
        er = ndi.binary_erosion(region > 0.5, iterations=max(1, int(inner * S)))
        return (d & ~er).astype(np.float32)
    return (d & ~(region > 0.5)).astype(np.float32)


def edge_ring(region, S, width):
    """ring centred on the region edge"""
    k = max(1, int(width * S / 2))
    reg = region > 0.5
    d = ndi.binary_dilation(reg, iterations=k)
    e = ndi.binary_erosion(reg, iterations=k)
    return (d & ~e).astype(np.float32)


def warp(m, amp, scale, r, S=4):
    """displace a mask by smooth noise (amp, scale in SS px)"""
    h, w = m.shape
    nx = smooth(h, w, scale, r) * amp
    ny = smooth(h, w, scale, r) * amp
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    return ndi.map_coordinates(m, [yy + ny, xx + nx], order=1, mode='constant')


def ink_edge(cv, region, x0, y0, col=INK, width=1.8, alpha=0.95, wob=1.0, rough=True):
    """ballpoint / marker-pen outline around a region: ring on the edge, warped so it wobbles"""
    ring = outline_mask(region, cv.S, width) if rough == 'out' else edge_ring(region, cv.S, width)
    ring = warp(ring, wob * cv.S, 10 * cv.S, cv.r)
    b = ndi.gaussian_filter(ring, 0.5 * cv.S / 4 * 1.5)
    n = smooth(*b.shape, 1.2 * cv.S / 4 * 1.5, cv.r)
    b = np.clip((b + n * 0.05 - 0.4) * 3, 0, 1) * (0.9 + 0.1 * n)
    cv.over(np.clip(b, 0, 1), col, alpha, x0, y0)
    return b


# ---------------------------------------------------------------- paper, tape, torn edges
def paper_rgb(cv, kind='dot', tint=PAPER, size=None, pitch=11.0, strength=1.0):
    """float RGB array (SS size) of a paper sheet"""
    W, H = (cv.W, cv.H) if size is None else size
    r = cv.r
    S = cv.S
    base = np.empty((H, W, 3), np.float32)
    base[:] = np.asarray(tint, np.float32)
    n1 = smooth(H, W, 40 * S / 4, r) * 3.0 * strength
    n2 = smooth(H, W, 6 * S / 4, r) * 1.8 * strength
    n3 = smooth(H, W, 1.4 * S / 4, r) * 1.8 * strength
    # fibres: elongated noise
    fib = ndi.gaussian_filter(r.standard_normal((H, W)).astype(np.float32), (0.7 * S / 4, 5.0 * S / 4)) * 14 * strength
    t = (n1 + n2 + n3 + fib)[..., None]
    base += t * np.array([1.0, 1.0, 1.05], np.float32)
    if kind in ('dot', 'graph', 'ruled'):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        p = pitch * S
        gx = np.abs(((xx + p / 2) % p) - p / 2)
        gy = np.abs(((yy + p / 2) % p) - p / 2)
        if kind == 'dot':
            d = np.sqrt(gx ** 2 + gy ** 2)
            m = np.clip(1 - d / (0.55 * S), 0, 1) * 0.55
        elif kind == 'graph':
            m = np.maximum(np.clip(1 - gx / (0.4 * S), 0, 1), np.clip(1 - gy / (0.4 * S), 0, 1)) * 0.26
        else:
            m = np.clip(1 - gy / (0.4 * S), 0, 1) * 0.3
        gc = np.array([96, 118, 170], np.float32)
        base = base * (1 - m[..., None]) + gc * m[..., None]
    return np.clip(base, 0, 255)


def torn_mask(cv, shape, rough=1.6, fringe=1.2):
    """shape: float mask (SS).  returns (mask, fringe_mask): ragged torn outline + a lighter fibre rim"""
    S = cv.S
    h, w = shape.shape
    m = warp(shape, rough * S * 0.9, 9 * S, cv.r)
    n = smooth(h, w, 1.5 * S / 4 * 2, cv.r)
    n2 = smooth(h, w, 5 * S / 4, cv.r)
    b = ndi.gaussian_filter(m, 0.8 * S / 4 * 1.5)
    t = np.clip((b - 0.5 + n * 0.10 + n2 * 0.05) * 6 + 0.5, 0, 1)
    inner = ndi.gaussian_filter(t, fringe * S)
    rim = np.clip(t - np.clip((inner - 0.55) * 4, 0, 1), 0, 1)
    return t, rim


def drop_shadow(rgba_img, off=(3, 4), blur=5, alpha=0.5, S=1):
    a = rgba_img.split()[3]
    sh = Image.new('L', rgba_img.size, 0)
    sh.paste(a, (int(off[0] * S), int(off[1] * S)))
    sh = sh.filter(ImageFilter.GaussianBlur(blur * S))
    sh = sh.point(lambda v: int(v * alpha))
    out = Image.new('RGBA', rgba_img.size, (8, 6, 14, 0))
    out.putalpha(sh)
    return out


def tape(cv, c, w, h, ang, col=(236, 226, 190), alpha=0.74):
    """translucent masking tape piece centred at c (1x), zigzag torn ends"""
    S = cv.S
    r = cv.r
    pts = []
    n = 7
    for i in range(n + 1):  # left edge zigzag
        pts.append((-w / 2 + (1.6 if i % 2 else -0.4) * r.uniform(0.7, 1.4), -h / 2 + h * i / n))
    for i in range(n, -1, -1):
        pts.append((w / 2 + (-1.6 if i % 2 else 0.4) * r.uniform(0.7, 1.4), -h / 2 + h * i / n))
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    P = [(c[0] + x * ca - y * sa, c[1] + x * sa + y * ca) for x, y in pts]
    m = cv.poly_mask(P)
    m = ndi.gaussian_filter(m, 0.4 * S)
    # soft shadow first
    sh = ndi.gaussian_filter(np.roll(np.roll(m, int(1.6 * S), 0), int(0.8 * S), 1), 1.8 * S)
    cv.over(sh, (10, 8, 16), 0.28)
    n1 = smooth(cv.H, cv.W, 2.5 * S / 4 * 1.5, r)
    cv.over(np.clip(m * (0.9 + 0.1 * n1), 0, 1), col, alpha)
    # sheen: two faint lighter bands along the length
    for k, f in enumerate((-0.22, 0.28)):
        L = [(c[0] + (x) * ca - (f * h) * sa, c[1] + x * sa + (f * h) * ca) for x in (-w / 2 + 3, w / 2 - 3)]
        sm = cv.poly_mask([(L[0][0] - sa * 0.7, L[0][1] + ca * 0.7), (L[1][0] - sa * 0.7, L[1][1] + ca * 0.7), (L[1][0] + sa * 0.7, L[1][1] - ca * 0.7), (L[0][0] + sa * 0.7, L[0][1] - ca * 0.7)])
        cv.over(sm * m, (255, 252, 235), 0.28)
    return m


def staple(cv, c, ang=0, L=11):
    S = cv.S
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    p0 = (c[0] - ca * L / 2, c[1] - sa * L / 2)
    p1 = (c[0] + ca * L / 2, c[1] + sa * L / 2)
    marker(cv, [(p0[0] + 0.7, p0[1] + 1.2), (p1[0] + 0.7, p1[1] + 1.2)], (20, 18, 24), w=2.4, alpha=0.35, wob=0, grain=0, rough=0.05)
    marker(cv, [p0, p1], (170, 178, 190), w=2.0, alpha=0.95, wob=0, grain=0.05, rough=0.05)
    marker(cv, [(p0[0], p0[1] - 0.5 * ca), (p1[0], p1[1] - 0.5 * ca)], (236, 240, 248), w=0.7, alpha=0.9, wob=0, grain=0, rough=0)


# ---------------------------------------------------------------- lettering
def text_mask(cv, text, fnt, px, rot=0.0, spacing=0.0, anchor_size=None):
    """returns (mask, w, h) of text at SS scale, tight crop + pad"""
    S = cv.S
    f = font(fnt, px * S)
    pad = int(px * S * 0.4) + 6
    # measure
    tmp = Image.new('L', (4, 4))
    d0 = ImageDraw.Draw(tmp)
    if spacing:
        ws = [d0.textlength(ch, font=f) for ch in text]
        tw = int(sum(ws) + spacing * S * (len(text) - 1))
    else:
        tw = int(d0.textlength(text, font=f))
    asc, desc = f.getmetrics()
    th = asc + desc
    im = Image.new('L', (tw + pad * 2, th + pad * 2), 0)
    d = ImageDraw.Draw(im)
    if spacing:
        x = pad
        for ch, wch in zip(text, ws):
            d.text((x, pad), ch, font=f, fill=255)
            x += wch + spacing * S
    else:
        d.text((pad, pad), text, font=f, fill=255)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    return np.asarray(im, np.float32) / 255.0


def letters(cv, text, c, px, fnt=MARKER_F, fill=PINK, ink=INK, rot=0.0, spacing=0.0, extrude=0, ext_col=INK, ink_w=1.4, miss=(1.3, 1.0), wob=0.5,
            fill_mode='flat', hatch_ext=True, outline=True, glow=None, alpha=1.0, fill_alpha=0.96):
    """hand-lettered text centred at c (1x): extruded block shadow, ballpoint/marker outline, marker fill that misses the line."""
    S = cv.S
    m = text_mask(cv, text, fnt, px, rot, spacing)
    h, w = m.shape
    m = warp(m, wob * S * 0.5, 6 * S, cv.r)
    x0 = int(c[0] * S - w / 2)
    y0 = int(c[1] * S - h / 2)
    mb = ndi.gaussian_filter(m, 0.5 * S / 4 * 1.5)
    solid = np.clip((mb - 0.45) * 6, 0, 1)
    if glow is not None:
        gl = ndi.gaussian_filter(solid, 2.4 * S)
        cv.over(np.clip(gl * 1.4, 0, 1), glow, 0.35, x0, y0)
    if extrude:
        ex = np.zeros_like(solid)
        for k in range(1, int(extrude * S) + 1):
            ex = np.maximum(ex, np.roll(np.roll(solid, int(k * 0.8), 0), int(k * 0.8), 1))
        ex = np.clip(ex - solid, 0, 1)
        cv.over(ex, ext_col, 0.97 * alpha, x0, y0)
        if hatch_ext:
            hatch_region(cv, ex, x0, y0, (240, 236, 226), ang=135, pitch=3.0, w=0.9, alpha=0.55, over=0.3, jit=0.2)
    if outline:
        ring = outline_mask(solid, S, ink_w)
        ring = np.clip(ndi.gaussian_filter(ring, 0.35 * S / 4 * 1.5) * 1.6, 0, 1)
        cv.over(ring, ink, 0.98 * alpha, x0, y0)
    fm = np.roll(np.roll(solid, int(miss[1] * S), 0), int(miss[0] * S), 1)
    if fill_mode == 'marker':
        fill_region(cv, fm, x0, y0, fill, ang=-20, nib=max(3.0, px / 5), over=1.2, alpha=fill_alpha * alpha, grain=0.15, jit=0.25)
    elif fill is not None:
        n = smooth(*fm.shape, 3 * S / 4 * 1.5, cv.r)
        cv.over(np.clip(fm * (0.93 + 0.07 * n), 0, 1), fill, fill_alpha * alpha, x0, y0)
    return x0, y0, solid


def tag_text(cv, text, c, px, fnt=HAND_F, col=BLUE, alpha=0.92, rot=0.0, spacing=0.0, wob=0.25, bold=0.0):
    """handwritten ballpoint text, no outline"""
    S = cv.S
    m = text_mask(cv, text, fnt, px, rot, spacing)
    h, w = m.shape
    m = warp(m, wob * S, 5 * S, cv.r)
    if bold:
        m = ndi.maximum_filter(m, size=int(bold * S) | 1)
    x0 = int(c[0] * S - w / 2)
    y0 = int(c[1] * S - h / 2)
    b = ndi.gaussian_filter(m, 0.4 * S / 4 * 1.5)
    n = smooth(h, w, 1.2 * S / 4 * 1.5, cv.r)
    b = np.clip(b * (0.9 + 0.1 * n), 0, 1)
    cv.over(b, col, alpha, x0, y0)
    return x0, y0, b


# ---------------------------------------------------------------- doodles (ballpoint / marker)
def doodle_star(cv, c, r, col=BLUE, w=0.9, n=5, alpha=0.85, rot=-18):
    pts = []
    for i in range(n * 2 + 1):
        rr = r if i % 2 == 0 else r * 0.42
        pts.append(pol(c, rr, rot + i * 180 / n))
    ballpoint(cv, pts, col, w, alpha, wob=0.3, wl=10, taper=(0.02, 0.02))


def doodle_arrow(cv, p0, p1, col=BLUE, w=0.9, curve=6, alpha=0.85, head=5):
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    mid = (p0 + p1) / 2
    d = p1 - p0
    nrm = np.array([-d[1], d[0]]) / (np.hypot(*d) + 1e-9)
    ctrl = mid + nrm * curve
    t = np.linspace(0, 1, 24)[:, None]
    pts = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * ctrl + t ** 2 * p1
    ballpoint(cv, pts, col, w, alpha, wob=0.25, wl=14)
    tg = p1 - pts[-4]
    tg /= (np.hypot(*tg) + 1e-9)
    for sgn in (1, -1):
        a = math.radians(26 * sgn)
        ca, sa = math.cos(a), math.sin(a)
        v = np.array([tg[0] * ca - tg[1] * sa, tg[0] * sa + tg[1] * ca])
        ballpoint(cv, [p1, p1 - v * head], col, w, alpha, wob=0.1, wl=6, taper=(0, 0.2))


def doodle_spark(cv, c, r, col=BLUE, w=0.9, n=8, alpha=0.85):
    for i in range(n):
        a = i * 360 / n + cv.r.uniform(-6, 6)
        ballpoint(cv, [pol(c, r * 0.35, a), pol(c, r * cv.r.uniform(0.8, 1.0), a)], col, w, alpha, wob=0.1, wl=5, taper=(0.05, 0.3))


def doodle_zig(cv, p0, p1, col=BLUE, w=0.9, n=5, amp=2.5, alpha=0.85):
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    d = p1 - p0
    nrm = np.array([-d[1], d[0]]) / (np.hypot(*d) + 1e-9)
    pts = [p0 + d * i / (n * 2) + nrm * (amp if i % 2 else -amp) * (0 if i in (0, n * 2) else 1) for i in range(n * 2 + 1)]
    ballpoint(cv, pts, col, w, alpha, wob=0.2, wl=8)


def doodle_cross(cv, c, r, col=BLUE, w=0.9, alpha=0.85):
    ballpoint(cv, [(c[0] - r, c[1] - r), (c[0] + r, c[1] + r)], col, w, alpha, wob=0.15, wl=6)
    ballpoint(cv, [(c[0] + r, c[1] - r), (c[0] - r, c[1] + r)], col, w, alpha, wob=0.15, wl=6)


def doodle_crown(cv, c, r, col=INK, w=1.0, alpha=0.9):
    pts = [(c[0] - r, c[1] + r * 0.5), (c[0] - r * 1.05, c[1] - r * 0.6), (c[0] - r * 0.45, c[1] + r * 0.05), (c[0], c[1] - r * 0.9),
           (c[0] + r * 0.45, c[1] + r * 0.05), (c[0] + r * 1.05, c[1] - r * 0.6), (c[0] + r, c[1] + r * 0.5), (c[0] - r, c[1] + r * 0.5)]
    ballpoint(cv, pts, col, w, alpha, wob=0.2, wl=8, taper=(0.02, 0.02))
