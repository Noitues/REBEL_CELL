"""Shared helpers for the r2c_geo_vector concept stills.

Everything is drawn as flat, crisp triangles (Pillow polygons) on a 2x canvas and
downsampled once at the end. Tone per triangle comes from a colour ramp (deep ->
warm -> pale), offset by lighting, a gradient across the surface and seeded jitter.
All randomness is seeded (random.Random(str) is deterministic).
"""
import math
import random
import zlib
from PIL import Image, ImageDraw, ImageFont

SS = 2            # supersample factor
W, H = 1920, 1080  # output size


# ----------------------------------------------------------------- colour
def hexc(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def R(*hexes):
    return [hexc(h) for h in hexes]


def mix(a, b, t):
    return tuple(int(round(a[k] + (b[k] - a[k]) * t)) for k in range(len(a)))


def ramp(stops, t):
    t = max(0.0, min(1.0, t))
    n = len(stops) - 1
    x = t * n
    i = min(int(x), n - 1)
    return mix(stops[i], stops[i + 1], x - i)


def hsh(*vals):
    """Small deterministic hash -> [0,1)."""
    h = 2166136261
    for v in vals:
        if not isinstance(v, (int, float)):
            v = zlib.crc32(repr(v).encode())
        h ^= (int(v) & 0xffffffff)
        h = (h * 16777619) & 0xffffffff
        h ^= h >> 13
    return (h & 0xffff) / 65536.0


def toner(stops, base, gu=0.0, gv=0.0, var=0.07, flip=0.10, famt=0.16, alpha=None):
    """Colour function: ramp tone = base + gradient + jitter, occasional tone flip."""
    def f(u, v, i, j, k, rc):
        t = base + gu * (u - 0.5) + gv * (v - 0.5) + rc.uniform(-var, var)
        if rc.random() < flip:
            t += famt if rc.random() < 0.5 else -famt
        c = ramp(stops, t)
        if alpha is not None:
            a = alpha if not isinstance(alpha, tuple) else int(rc.uniform(*alpha))
            return c + (a,)
        return c
    return f


# ----------------------------------------------------------------- facets
def facet(draw, fpos, nu, nv, colfn, seed, jit=0.32, wrap_u=False):
    """Triangulate the unit square mapped through fpos(u,v)->(x,y) (1x coords).

    Interior vertices jitter freely, edge vertices slide only along their edge, so
    neighbouring surfaces meet without gaps. Geometry and colour use separate seeded
    streams, so a surface keeps its triangles when only its colours change.
    """
    rg = random.Random(str(seed) + 'g')
    rc = random.Random(str(seed) + 'c')
    uv = {}
    for j in range(nv + 1):
        for i in range(nu + 1):
            if wrap_u and i == nu:
                u0, v0 = uv[(0, j)]
                uv[(i, j)] = (u0 + 1.0, v0)
                continue
            u, v = i / nu, j / nv
            du = rg.uniform(-jit, jit) / nu
            dv = rg.uniform(-jit, jit) / nv
            if 0 < i < nu or (wrap_u and i == 0):
                u += du
            if 0 < j < nv:
                v += dv
            uv[(i, j)] = (u, v)
    diag = [[rg.random() < 0.5 for _ in range(nu)] for _ in range(nv)]
    P = {}
    for key, (u, v) in uv.items():
        x, y = fpos(u, v)
        P[key] = (x * SS, y * SS)
    for j in range(nv):
        for i in range(nu):
            a, b, c, d = (i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)
            tris = [(a, b, c), (a, c, d)] if diag[j][i] else [(a, b, d), (b, c, d)]
            for k, t in enumerate(tris):
                uc = sum(uv[p][0] for p in t) / 3.0
                vc = sum(uv[p][1] for p in t) / 3.0
                col = colfn(uc, vc, i, j, k, rc)
                if col is None:
                    continue
                pts = [P[p] for p in t]
                if len(col) == 4:
                    draw.polygon(pts, fill=col)
                else:
                    draw.polygon(pts, fill=col, outline=col)


def bil(q):
    """Bilinear map of a screen quad [p00, p10, p11, p01]."""
    def f(u, v):
        x = (1 - u) * (1 - v) * q[0][0] + u * (1 - v) * q[1][0] + u * v * q[2][0] + (1 - u) * v * q[3][0]
        y = (1 - u) * (1 - v) * q[0][1] + u * (1 - v) * q[1][1] + u * v * q[2][1] + (1 - u) * v * q[3][1]
        return x, y
    return f


def polar(cx, cy, rx, ry, a0, a1, r0, r1):
    """u = angle (a0..a1 radians), v = radius (r0..r1, fraction of rx/ry)."""
    def f(u, v):
        a = a0 + (a1 - a0) * u
        r = r0 + (r1 - r0) * v
        return cx + r * rx * math.cos(a), cy + r * ry * math.sin(a)
    return f


def panel(draw, q, stops, base, seed, nu=6, nv=2, gu=0.0, gv=-0.2, var=0.06, flip=0.08, jit=0.3):
    facet(draw, bil(q), nu, nv, toner(stops, base, gu, gv, var, flip), seed, jit)


def skew_rect(x, y, w, h, sk=0.0):
    """Parallelogram, [top-left, top-right, bottom-right, bottom-left] (v runs top->bottom)."""
    return [(x + sk, y), (x + w + sk, y), (x + w, y + h), (x, y + h)]


def tri(draw, pts, col):
    pp = [(p[0] * SS, p[1] * SS) for p in pts]
    if len(col) == 4:
        draw.polygon(pp, fill=col)
    else:
        draw.polygon(pp, fill=col, outline=col)


def gem(draw, cx, cy, rx, ry, stops, seed, n=6, rot=-math.pi / 2, base=0.55):
    """Faceted polygon 'gem': a fan of n sectors, each split light/dark."""
    rc = random.Random(str(seed))
    pts = [(cx + rx * math.cos(rot + 2 * math.pi * k / n), cy + ry * math.sin(rot + 2 * math.pi * k / n)) for k in range(n)]
    inner = [(cx + 0.45 * rx * math.cos(rot + 2 * math.pi * (k + 0.5) / n),
              cy + 0.45 * ry * math.sin(rot + 2 * math.pi * (k + 0.5) / n)) for k in range(n)]
    for k in range(n):
        a, b = pts[k], pts[(k + 1) % n]
        m = inner[k]
        # light from upper-left: sectors facing up-left brighter
        ang = rot + 2 * math.pi * (k + 0.5) / n
        lam = 0.5 + 0.5 * (-math.cos(ang) * 0.6 - math.sin(ang) * 0.8)
        t = base - 0.3 + 0.55 * lam
        tri(draw, [a, b, m], ramp(stops, t + rc.uniform(-0.05, 0.05)))
        tri(draw, [a, m, (cx, cy)], ramp(stops, t + 0.12 + rc.uniform(-0.05, 0.05)))
        tri(draw, [m, b, (cx, cy)], ramp(stops, t - 0.1 + rc.uniform(-0.05, 0.05)))


# ----------------------------------------------------------------- canvas
def gradient(fn, cols=96, rows=54):
    small = Image.new('RGB', (cols, rows))
    px = small.load()
    for y in range(rows):
        for x in range(cols):
            px[x, y] = fn(x / (cols - 1), y / (rows - 1))
    return small.resize((W * SS, H * SS), Image.BICUBIC)


def finalize(img):
    return img.convert('RGB').resize((W, H), Image.LANCZOS)


_fonts = {}


def font(size, style='Bold', path='C:/Windows/Fonts/bahnschrift.ttf'):
    key = (size, style, path)
    if key not in _fonts:
        f = ImageFont.truetype(path, int(size * SS))
        try:
            f.set_variation_by_name(style)
        except Exception:
            pass
        _fonts[key] = f
    return _fonts[key]


HAND = 'C:/Windows/Fonts/Inkfree.ttf'


def text(draw, x, y, s, size, fill, anchor='la', style='Bold', shadow=None, sh=2, path='C:/Windows/Fonts/bahnschrift.ttf'):
    f = font(size, style, path)
    if shadow is not None:
        draw.text(((x + sh) * SS, (y + sh) * SS), s, font=f, fill=shadow, anchor=anchor)
    draw.text((x * SS, y * SS), s, font=f, fill=fill, anchor=anchor)


def text_w(s, size, style='Bold'):
    f = font(size, style)
    b = f.getbbox(s)
    return (b[2] - b[0]) / SS


# ----------------------------------------------------------------- palettes
# Harsh, sparing neon: sickly magenta, acid green, cold cyan, sodium orange.
NEON = {
    'magenta': R('#2e0626', '#7a0e56', '#c8287e', '#ec5aa8', '#ffc0e0'),
    'cyan': R('#04222c', '#0a6078', '#1cb8d8', '#78eaff', '#e0ffff'),
    'acid': R('#162404', '#3e6a08', '#8ad010', '#c8fa3a', '#f2ffc0'),
    'sodium': R('#321404', '#803a08', '#d86e10', '#ffa436', '#ffe0a0'),
    'amber': R('#321404', '#803a08', '#d86e10', '#ffa436', '#ffe0a0'),
    'lime': R('#162404', '#3e6a08', '#8ad010', '#c8fa3a', '#f2ffc0'),
    'red': R('#2e0406', '#7a0a12', '#d0182a', '#ff4848', '#ffc0b0'),
    'blue': R('#040a30', '#0a2080', '#1a48e0', '#6a90ff', '#d8e4ff'),
    'violet': R('#1a0a3a', '#3e1880', '#6a3ac8', '#a080f0', '#e0d4ff'),
    'white': R('#303034', '#6a6a70', '#a8a8ae', '#d8d8dc', '#ffffff'),
}


# ----------------------------------------------------------------- grit helpers
def line2(draw, a, b, w, col):
    """A thin quad (two triangles) between screen points a and b (1x coords)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    pts = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
    pp = [(p[0] * SS, p[1] * SS) for p in pts]
    if len(col) == 4:
        draw.polygon(pp, fill=col)
    else:
        draw.polygon(pp, fill=col, outline=col)


def catenary(draw, a, b, sag, w, col, n=12):
    pts = []
    for k in range(n + 1):
        t = k / n
        pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + sag * 4 * t * (1 - t)))
    for k in range(n):
        line2(draw, pts[k], pts[k + 1], w, col)
    return pts


def layer(img):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    return lay, ImageDraw.Draw(lay)


def composite(img, lay):
    return Image.alpha_composite(img.convert('RGBA'), lay).convert('RGB')


def rain(img, seed, n=900, col=(170, 180, 200), alpha=(40, 90), length=(40, 110), slant=0.18, width=(1.2, 2.2),
         region=(0, 0, W, H)):
    """Rain as long, thin, translucent triangle slivers."""
    lay, d = layer(img)
    rng = random.Random(str(seed))
    x0, y0, x1, y1 = region
    for _ in range(n):
        x = rng.uniform(x0 - 100, x1)
        y = rng.uniform(y0 - 100, y1)
        L = rng.uniform(*length)
        w = rng.uniform(*width)
        a = rng.randint(*alpha)
        c = tuple(min(255, int(ch * rng.uniform(0.85, 1.1))) for ch in col) + (a,)
        tip = (x + slant * L, y + L)
        pts = [(x - w / 2, y), (x + w / 2, y), tip]
        d.polygon([(p[0] * SS, p[1] * SS) for p in pts], fill=c)
    return composite(img, lay)


def smog(img, seed, bands, stops):
    """Translucent triangle bands: bands = [(y_top, height, alpha_lo, alpha_hi)]."""
    lay, d = layer(img)
    for n, (y, h, a0, a1) in enumerate(bands):
        def cf(u, v, i, j, k, rc, a0=a0, a1=a1):
            edge = 1.0 - abs(v - 0.5) * 2
            a = int((a0 + (a1 - a0) * rc.random()) * (0.35 + 0.65 * edge))
            return ramp(stops, 0.3 + 0.5 * rc.random()) + (a,)
        facet(d, bil([(-40, y), (W + 40, y - h * 0.15), (W + 40, y + h * 0.85), (-40, y + h)]), 16, 3, cf,
              ('smog', seed, n), 0.4)
    return composite(img, lay)


def poly_fpos(pts, center=None):
    """Map (u = around the outline, v = centre->outline) for a star-shaped polygon."""
    n = len(pts)
    if center is None:
        center = (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)

    def f(u, v):
        s = (u % 1.0) * n
        k = int(s) % n
        t = s - int(s)
        a, b = pts[k], pts[(k + 1) % n]
        bx, by = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        return center[0] + (bx - center[0]) * v, center[1] + (by - center[1]) * v
    return f
