"""s_e_wildcards: spinner slices as programs, three premium mini-styles.

Pure Pillow + numpy. Every texture is a procedural function of slice-local coordinates
(lx = tangential, ly = radial along the slice centre line, in master units where the
wheel's outer radius is 360), so the same code renders a tile at any size and rotation.
That is also how the Godot shader works (see NOTES.md): the fragment shader gets the
same local coordinates from a wedge mesh's UV/vertex data.

Styles:  'holo'   holographic trading-card foil, embossed emblem, tilt-driven shift
         'enamel' hard-enamel pin, gold cloisonne walls, glossy dome, specular sweep
         'cv2'    faceted Cv2 neon (gritty triangulated low-poly), facets light in sequence
         'meridian' the Cv2 enemy family in Meridian orange (one material, accent per type)
Deterministic: all randomness from numpy default_rng seeded by crc32 of names.
"""
import math
import zlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_PATH = 'C:/Windows/Fonts/bahnschrift.ttf'
MONO_PATH = 'C:/Windows/Fonts/consola.ttf'

RIN, ROUT = 130.0, 360.0
TICK = 2.0 * math.pi / 30.0
R_ICON = RIN + 0.6 * (ROUT - RIN)  # 268
INK = np.array([0.055, 0.040, 0.085], np.float32)  # dark outline colour
LIGHT = np.array([-0.45, -0.65, 0.62]); LIGHT = LIGHT / np.linalg.norm(LIGHT)
LIGHT_FLAT = LIGHT[2]


def font(size, var='Bold Condensed'):
    f = ImageFont.truetype(FONT_PATH, max(4, int(round(size))))
    try:
        f.set_variation_by_name(var)
    except Exception:
        pass
    return f


def mono(size):
    return ImageFont.truetype(MONO_PATH, max(4, int(round(size))))


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32)


def seed_of(*parts):
    return zlib.crc32(':'.join(str(p) for p in parts).encode())


PROGS = {
    'EXPLOIT':  dict(col='#FF3DA8', glyph='dagger',  val='6',  slice='ATTACK'),
    'ZERO-DAY': dict(col='#FF55C8', glyph='burst',   val='12', slice='CRITICAL'),
    'FIREWALL': dict(col='#5CE1FF', glyph='shield',  val='5',  slice='DEFEND'),
    'SANDBOX':  dict(col='#36D8C6', glyph='sandbox', val='4',  slice='SHIELD'),
    'PROXY':    dict(col='#7BE07B', glyph='chevron', val='3',  slice='EVADE'),
    'PATCH':    dict(col='#46D98C', glyph='plus',    val='4',  slice='HEAL'),
    'VIRUS':    dict(col='#C85AFF', glyph='virus',   val='3',  slice='AFFLICT'),
    'TROJAN':   dict(col='#B08CFF', glyph='knight',  val='2',  slice='DEPLOY'),
    'NULL':     dict(col='#6A6A6A', glyph='null',    val='',   slice='MISS'),
}
ORDER = ['EXPLOIT', 'ZERO-DAY', 'FIREWALL', 'SANDBOX', 'PROXY', 'PATCH', 'VIRUS', 'TROJAN', 'NULL']
for _k, _v in PROGS.items():
    _v['c'] = hexc(_v['col'])

MERIDIAN = dict(main=hexc('#FF8A1F'), light=hexc('#FFB547'), dark=hexc('#B4430E'),
                shard=np.array([0.11, 0.055, 0.03], np.float32))


# ----------------------------------------------------------------------------- helpers
def frac(x):
    return x - np.floor(x)


def hash2(x, y, s=0.0):
    v = np.sin(np.asarray(x, np.float64) * 127.1 + np.asarray(y, np.float64) * 311.7 + s * 74.7) * 43758.5453
    return (v - np.floor(v)).astype(np.float32)


def vnoise(x, y, s=0.0):
    ix, iy = np.floor(x), np.floor(y)
    fx, fy = x - ix, y - iy
    u = fx * fx * (3 - 2 * fx); v = fy * fy * (3 - 2 * fy)
    a = hash2(ix, iy, s); b = hash2(ix + 1, iy, s); c = hash2(ix, iy + 1, s); d = hash2(ix + 1, iy + 1, s)
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v


def hsv(h, s, v):
    h = np.asarray(h, np.float32)
    s = np.broadcast_to(np.asarray(s, np.float32), h.shape)
    v = np.broadcast_to(np.asarray(v, np.float32), h.shape)
    k = np.array([0.0, 2.0 / 3.0, 1.0 / 3.0], np.float32)
    p = np.clip(np.abs(frac(h[..., None] + k) * 6.0 - 3.0) - 1.0, 0, 1)
    return v[..., None] * (1.0 - s[..., None] + s[..., None] * p)


def mix(a, b, t):
    return a + (b - a) * t


def blur1(a, r, axis):
    if r < 1:
        return a
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    p = np.pad(a, pad, mode='edge')
    c = np.cumsum(p, axis=axis, dtype=np.float64)
    n = a.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def box_blur(a, r, passes=3):
    r = int(round(r))
    for _ in range(passes):
        a = blur1(blur1(a, r, 0), r, 1)
    return a


def edges_of(idarr):
    m = np.zeros(idarr.shape, bool)
    m[:, :-1] |= idarr[:, :-1] != idarr[:, 1:]
    m[:-1, :] |= idarr[:-1, :] != idarr[1:, :]
    return m


def dilate(m, rad):
    rad = int(round(rad))
    if rad < 1:
        return m
    out = m.copy()
    H, W = m.shape
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if dx * dx + dy * dy > rad * rad or (dx == 0 and dy == 0):
                continue
            ys0, ys1 = max(0, dy), H + min(0, dy)
            xs0, xs1 = max(0, dx), W + min(0, dx)
            out[ys0:ys1, xs0:xs1] |= m[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    return out


def shade_from_height(h, k):
    """Lambert shade (1.0 on flat) from a height field h (screen-space array)."""
    gy, gx = np.gradient(h)
    nx, ny, nz = -gx * k, -gy * k, np.ones_like(h)
    inv = 1.0 / np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx * inv, ny * inv, nz * inv
    lam = (nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]) / LIGHT_FLAT
    return lam, (nx, ny, nz)


def spec_from_normal(n, power):
    hv = LIGHT + np.array([0, 0, 1.0]); hv = hv / np.linalg.norm(hv)
    d = np.clip(n[0] * hv[0] + n[1] * hv[1] + n[2] * hv[2], 0, 1)
    return d ** power


def chord(ticks, r=R_ICON):
    return 2.0 * r * math.sin(ticks * TICK / 2.0)


# ----------------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, W, H, SS=2):
        self.W, self.H, self.SS = W, H, SS
        self.w, self.h = W * SS, H * SS
        self.rgb = np.zeros((self.h, self.w, 3), np.float32)
        self.glow = np.zeros((self.h // 4, self.w // 4, 3), np.float32)
        self.ov = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))
        self.ovd = ImageDraw.Draw(self.ov)
        self.ovglow = Image.new('RGB', (self.w // 4, self.h // 4), (0, 0, 0))
        self.ovgd = ImageDraw.Draw(self.ovglow)

    def bbox(self, x0, y0, x1, y1):
        x0 = max(0, int(math.floor(x0 / 4)) * 4); y0 = max(0, int(math.floor(y0 / 4)) * 4)
        x1 = min(self.w, int(math.ceil(x1 / 4)) * 4); y1 = min(self.h, int(math.ceil(y1 / 4)) * 4)
        return x0, y0, x1, y1

    def add_glow(self, box, src):
        x0, y0, x1, y1 = box
        h, w = src.shape[:2]
        if h < 4 or w < 4:
            return
        s = src.reshape(h // 4, 4, w // 4, 4, 3).mean(axis=(1, 3))
        self.glow[y0 // 4:y1 // 4, x0 // 4:x1 // 4] += s

    def finish(self, glow_r=None, glow_k=1.6, grey=False):
        out = self.rgb
        r = glow_r if glow_r is not None else max(2, int(4 * self.SS / 2))
        g = box_blur(self.glow, r, 3) + 0.5 * box_blur(self.glow, max(1, r // 3), 2)
        og = np.asarray(self.ovglow, np.float32) / 255.0
        g = g + box_blur(og, max(1, r // 2), 3) * 1.2
        gu = np.stack([np.asarray(Image.fromarray(g[..., i]).resize((self.w, self.h), Image.BILINEAR))
                       for i in range(3)], -1)
        out = out + gu * glow_k
        ov = np.asarray(self.ov, np.float32) / 255.0
        a = ov[..., 3:4]
        out = out * (1 - a) + ov[..., :3] * a
        out = np.clip(out, 0, 1)
        SS = self.SS
        out = out.reshape(self.H, SS, self.W, SS, 3).mean(axis=(1, 3))
        img = Image.fromarray((out * 255 + 0.5).astype(np.uint8), 'RGB')
        if grey:
            img = img.convert('L').convert('RGB')
        return img


def background(cv, seed=7, tint=(0.05, 0.045, 0.075)):
    rng = np.random.default_rng(seed)
    h, w = cv.h, cv.w
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    top = np.array(tint, np.float32); bot = top * 0.55
    cv.rgb[:] = top * (1 - yy) + bot * yy
    sw, sh = w // 4, h // 4
    small = Image.new('RGB', (sw, sh), (0, 0, 0))
    d = ImageDraw.Draw(small, 'RGBA')
    for _ in range(90):
        cx, cy = rng.uniform(-0.1, 1.1) * sw, rng.uniform(-0.1, 1.1) * sh
        s = rng.uniform(0.05, 0.22) * sw
        pts = [(cx + rng.uniform(-s, s), cy + rng.uniform(-s, s)) for _ in range(3)]
        tone = rng.choice([0, 1, 2, 3])
        colr = [(70, 40, 30), (40, 40, 55), (60, 30, 55), (30, 45, 50)][tone]
        d.polygon(pts, fill=colr + (int(rng.uniform(10, 34)),))
    for _ in range(140):  # faint rain
        x = rng.uniform(0, sw); y = rng.uniform(0, sh); L = rng.uniform(6, 22)
        d.line([(x, y), (x - L * 0.12, y + L)], fill=(120, 130, 150, int(rng.uniform(8, 22))), width=1)
    up = np.asarray(small.resize((w, h), Image.BILINEAR), np.float32) / 255.0
    cv.rgb += up
    xx = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
    yv = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
    vig = 1.0 - 0.45 * np.clip(xx * xx * 0.6 + yv * yv * 0.8, 0, 1)
    cv.rgb *= vig[..., None]


def caption(cv, title, sub, x=0, y=None, accent=(255, 61, 168)):
    SS = cv.SS
    y = cv.H - 84 if y is None else y
    f1 = font(34 * SS); f2 = mono(19 * SS)
    tw = max(cv.ovd.textlength(title, font=f1), cv.ovd.textlength(sub, font=f2)) / SS
    cv.ovd.rectangle([x * SS, y * SS, (x + tw + 44) * SS, (y + 84) * SS], fill=(10, 8, 14, 235))
    cv.ovd.rectangle([x * SS, y * SS, (x + 6) * SS, (y + 84) * SS], fill=accent + (255,))
    cv.ovd.text(((x + 20) * SS, (y + 8) * SS), title, font=f1, fill=(255, 255, 255, 255))
    cv.ovd.text(((x + 20) * SS, (y + 52) * SS), sub, font=f2, fill=(200, 200, 210, 255))


def label(cv, x, y, text, size=28, fill=(255, 255, 255), anchor='mt', var='Bold Condensed', fnt=None):
    SS = cv.SS
    f = fnt if fnt is not None else font(size * SS, var)
    cv.ovd.text((x * SS, y * SS), text, font=f, fill=tuple(fill) + (255,), anchor=anchor)


# ----------------------------------------------------------------------------- glyphs
def _thick_line(d, N, x0, y0, x1, y1, w, fill=255):
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    d.polygon([((x0 + nx) * N, (y0 + ny) * N), ((x1 + nx) * N, (y1 + ny) * N),
               ((x1 - nx) * N, (y1 - ny) * N), ((x0 - nx) * N, (y0 - ny) * N)], fill=fill)


def _rot(pts, deg, sc=1.0, c=(0.5, 0.5)):
    a = math.radians(deg); ca, sa = math.cos(a), math.sin(a)
    out = []
    for x, y in pts:
        x, y = (x - c[0]) * sc, (y - c[1]) * sc
        out.append((c[0] + x * ca - y * sa, c[1] + x * sa + y * ca))
    return out


_GLYPH_CACHE = {}


def glyph_mask(kind, px):
    """Filled glyph silhouette, px x px float mask (0..1). Shapes are original designs."""
    key = (kind, px)
    if key in _GLYPH_CACHE:
        return _GLYPH_CACHE[key]
    N = px * 4
    im = Image.new('L', (N, N), 0)
    d = ImageDraw.Draw(im)

    def poly(pts, fill=255):
        d.polygon([(x * N, y * N) for x, y in pts], fill=fill)

    def circ(cx, cy, r, fill=255):
        d.ellipse([(cx - r) * N, (cy - r) * N, (cx + r) * N, (cy + r) * N], fill=fill)

    if kind == 'dagger':
        parts = [
            [(0.5, 0.0), (0.585, 0.13), (0.585, 0.60), (0.415, 0.60), (0.415, 0.13)],
            [(0.22, 0.60), (0.78, 0.60), (0.78, 0.69), (0.22, 0.69)],
            [(0.44, 0.69), (0.56, 0.69), (0.56, 0.87), (0.44, 0.87)],
        ]
        for p in parts:
            poly(_rot(p, 38, 1.06))
        (px_, py_), = _rot([(0.5, 0.925)], 38, 1.06)
        circ(px_, py_, 0.07)
    elif kind == 'burst':
        pts = []
        for k in range(16):
            a = k * math.pi / 8 + 0.12
            rr = [0.5, 0.2, 0.40, 0.2][k % 4]
            pts.append((0.5 + rr * math.sin(a), 0.5 - rr * math.cos(a)))
        poly(pts)
    elif kind == 'shield':
        poly([(0.10, 0.10), (0.5, 0.0), (0.90, 0.10), (0.88, 0.50), (0.73, 0.78), (0.5, 0.99),
              (0.27, 0.78), (0.12, 0.50)])
        for yy in (0.36, 0.60):  # firewall courses
            _thick_line(d, N, 0.16, yy, 0.84, yy, 0.07, 0)
        _thick_line(d, N, 0.5, 0.12, 0.5, 0.36, 0.07, 0)
        _thick_line(d, N, 0.32, 0.36, 0.32, 0.60, 0.07, 0)
        _thick_line(d, N, 0.68, 0.36, 0.68, 0.60, 0.07, 0)
        _thick_line(d, N, 0.5, 0.60, 0.5, 0.84, 0.07, 0)
    elif kind == 'sandbox':
        poly([(0.04, 0.04), (0.96, 0.04), (0.96, 0.96), (0.04, 0.96)])
        poly([(0.20, 0.20), (0.80, 0.20), (0.80, 0.80), (0.20, 0.80)], 0)
        poly([(0.5, 0.31), (0.69, 0.5), (0.5, 0.69), (0.31, 0.5)])
        for (x0, y0, x1, y1) in [(0.40, 0.0, 0.60, 0.20), (0.40, 0.80, 0.60, 1.0)]:
            poly([(x0, y0 + 0.04), (x1, y0 + 0.04), (x1, y1 - 0.04), (x0, y1 - 0.04)], 0)
    elif kind == 'chevron':
        ch = [(0.02, 0.08), (0.30, 0.08), (0.62, 0.5), (0.30, 0.92), (0.02, 0.92), (0.34, 0.5)]
        poly(ch)
        poly([(x + 0.36, y) for x, y in ch])
    elif kind == 'plus':
        poly([(0.33, 0.03), (0.67, 0.03), (0.67, 0.97), (0.33, 0.97)])
        poly([(0.03, 0.33), (0.97, 0.33), (0.97, 0.67), (0.03, 0.67)])
    elif kind == 'virus':
        circ(0.5, 0.5, 0.27)
        for k in range(8):
            a = k * math.pi / 4 + math.pi / 8
            sx, sy = math.sin(a), -math.cos(a)
            _thick_line(d, N, 0.5 + 0.2 * sx, 0.5 + 0.2 * sy, 0.5 + 0.41 * sx, 0.5 + 0.41 * sy, 0.075)
            circ(0.5 + 0.43 * sx, 0.5 + 0.43 * sy, 0.065)
        circ(0.43, 0.44, 0.06, 0); circ(0.58, 0.57, 0.045, 0); circ(0.56, 0.38, 0.03, 0)
    elif kind == 'knight':
        poly([(0.22, 0.97), (0.82, 0.97), (0.82, 0.86), (0.72, 0.82), (0.70, 0.62), (0.78, 0.44),
              (0.76, 0.24), (0.64, 0.11), (0.52, 0.07), (0.47, 0.0), (0.40, 0.09), (0.31, 0.15),
              (0.20, 0.33), (0.08, 0.48), (0.12, 0.59), (0.24, 0.60), (0.40, 0.50), (0.31, 0.69),
              (0.26, 0.83), (0.22, 0.87)])
        circ(0.47, 0.26, 0.045, 0)
        _thick_line(d, N, 0.30, 0.90, 0.74, 0.90, 0.035, 0)
    elif kind == 'null':
        circ(0.5, 0.5, 0.42); circ(0.5, 0.5, 0.27, 0)
        _thick_line(d, N, 0.13, 0.87, 0.87, 0.13, 0.13)
    m = np.asarray(im.resize((px, px), Image.LANCZOS), np.float32) / 255.0
    _GLYPH_CACHE[key] = m
    return m


def glyph_rgba(kind, px, ow):
    """White glyph, dark outline ow px, soft drop shadow. Returns float RGBA (H,W,4)."""
    pad = ow + 3
    m = glyph_mask(kind, px)
    M = np.zeros((px + 2 * pad, px + 2 * pad), np.float32)
    M[pad:pad + px, pad:pad + px] = m
    mi = Image.fromarray((M * 255).astype(np.uint8), 'L')
    k = 2 * ow + 1
    out = np.asarray(mi.filter(ImageFilter.MaxFilter(k)) if k > 1 else mi, np.float32) / 255.0
    out = np.asarray(Image.fromarray((out * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)),
                     np.float32) / 255.0
    rgb = np.ones(M.shape + (3,), np.float32) * INK
    rgb = rgb * (1 - M[..., None]) + M[..., None] * 1.0
    return np.dstack([rgb, np.maximum(out, M)])


def number_rgba(text, h_px, ow):
    f100 = font(100)
    bb = f100.getbbox('0')
    cap = (bb[3] - bb[1]) / 100.0
    f = font(h_px / cap)
    tb = f.getbbox(text, stroke_width=ow)
    W, H = tb[2] - tb[0] + 6, tb[3] - tb[1] + 6
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((3 - tb[0], 3 - tb[1]), text, font=f, fill=(255, 255, 255, 255), stroke_width=ow,
           stroke_fill=tuple(int(c * 255) for c in INK) + (255,))
    return np.asarray(im, np.float32) / 255.0


def paste_over(dst, src, cx, cy):
    h, w = src.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    H, W = dst.shape[:2]
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(W, x0 + w), min(H, y0 + h)
    if dx1 <= dx0 or dy1 <= dy0:
        return
    s = src[sy0:sy0 + (dy1 - dy0), sx0:sx0 + (dx1 - dx0)]
    d = dst[dy0:dy1, dx0:dx1]
    a = s[..., 3:4]
    d[..., :3] = d[..., :3] * (1 - a) + s[..., :3] * a
    d[..., 3:4] = d[..., 3:4] * (1 - a) + a


ICON_LX = 130.0
ICON_LY0, ICON_LY1 = 160.0, 362.0
_ICON_CACHE = {}


def icon_layout(prog, ticks, lod=1.0):
    """Glyph/number sizes (units) and centres. Returns dict."""
    ch = chord(ticks)
    g = float(np.clip(0.36 * ch, 30, 64)) * lod
    nh = g * 1.08
    if prog == 'NULL':
        return dict(g=g * 1.3, gc=(0.0, R_ICON), num=None)
    if ticks >= 5:
        return dict(g=g, gc=(-g * 0.62, R_ICON), num=(nh, (g * 0.55, R_ICON)))
    gap = 7.0 * lod
    return dict(g=g, gc=(0.0, R_ICON + (nh + gap) / 2), num=(nh, (0.0, R_ICON - (g + gap) / 2)))


def icon_local(prog, ticks, res, lod=1.0, value=None):
    key = (prog, ticks, round(res, 3), lod, value)
    if key in _ICON_CACHE:
        return _ICON_CACHE[key]
    Wp = int(2 * ICON_LX * res); Hp = int((ICON_LY1 - ICON_LY0) * res)
    img = np.zeros((Hp, Wp, 4), np.float32)
    L = icon_layout(prog, ticks, lod)
    gpx = max(6, int(round(L['g'] * res)))
    ow = max(1, int(round(gpx * 0.085 * (1.25 if lod > 1 else 1.0))))
    G = glyph_rgba(PROGS[prog]['glyph'], gpx, ow)
    gx, gy = L['gc']
    paste_over(img, G, (gx + ICON_LX) * res, (ICON_LY1 - gy) * res)
    val = PROGS[prog]['val'] if value is None else value
    if L['num'] is not None and val:
        nh, (nx, ny) = L['num']
        npx = max(6, int(round(nh * res)))
        nw = max(1, int(round(npx * 0.085 * (1.25 if lod > 1 else 1.0))))
        T = number_rgba(val, npx, nw)
        # keep wide two-digit numbers inside the wedge
        maxw = (0.62 if ticks < 5 else 0.42) * chord(ticks, ny) * res
        if T.shape[1] > maxw:
            s = maxw / T.shape[1]
            T = np.asarray(Image.fromarray((T * 255).astype(np.uint8), 'RGBA').resize(
                (max(1, int(T.shape[1] * s)), max(1, int(T.shape[0] * s))), Image.LANCZOS), np.float32) / 255.0
        paste_over(img, T, (nx + ICON_LX) * res, (ICON_LY1 - ny) * res)
    # soft drop shadow under the whole icon (darkens the texture -> readability)
    a = img[..., 3]
    sh = box_blur(a, max(1, int(3 * res)), 2)
    _ICON_CACHE[key] = (img, sh)
    return img, sh


def bilinear(img, fx, fy):
    H, W = img.shape[:2]
    x0 = np.clip(np.floor(fx).astype(np.int32), 0, W - 2)
    y0 = np.clip(np.floor(fy).astype(np.int32), 0, H - 2)
    wx = np.clip(fx - x0, 0, 1)[..., None]; wy = np.clip(fy - y0, 0, 1)[..., None]
    if img.ndim == 2:
        img = img[..., None]
    out = (img[y0, x0] * (1 - wx) * (1 - wy) + img[y0, x0 + 1] * wx * (1 - wy) +
           img[y0 + 1, x0] * (1 - wx) * wy + img[y0 + 1, x0 + 1] * wx * wy)
    inside = ((fx >= 0) & (fx < W - 1) & (fy >= 0) & (fy < H - 1))[..., None]
    return out * inside


# emblem (embossed big glyph for holo foil)
_EMB_CACHE = {}


def emblem_local(prog, ticks):
    key = (prog, ticks)
    if key in _EMB_CACHE:
        return _EMB_CACHE[key]
    res = 1.0
    Wp = int(2 * ICON_LX * res) + 40; Hp = int((ROUT - 100) * res) + 40
    img = np.zeros((Hp, Wp), np.float32)
    size = int(min(0.95 * chord(ticks, 290), 205))
    m = glyph_mask(PROGS[prog]['glyph'], size)
    cx, cy = (0 + ICON_LX + 20) * res, (ROUT + 20 - 282) * res
    x0, y0 = int(cx - size / 2), int(cy - size / 2)
    img[max(0, y0):y0 + size, max(0, x0):x0 + size] = m[max(0, -y0):, max(0, -x0):][:Hp - max(0, y0), :Wp - max(0, x0)]
    img = box_blur(img, 2, 2)
    _EMB_CACHE[key] = img
    return img


def sample_emblem(prog, ticks, lx, ly):
    img = emblem_local(prog, ticks)
    fx = lx + ICON_LX + 20; fy = (ROUT + 20) - ly
    return bilinear(img, fx, fy)[..., 0]


# ----------------------------------------------------------------------------- facets
FACET = {
    'EXPLOIT':  dict(nr=3, ns=6, jit=0.55, diag='rand', dark=0.16, light=0.12, lit=0.20, phase='radial'),
    'ZERO-DAY': dict(mode='fan', k=14, dark=0.06, light=0.0, lit=0.25, phase='angle'),
    'FIREWALL': dict(nr=7, ns=4, jit=0.08, diag='row', dark=0.05, light=0.10, lit=0.16, phase='radial'),
    'SANDBOX':  dict(nr=4, ns=4, jit=0.05, diag='sym', dark=0.08, light=0.10, lit=0.20, phase='center'),
    'PROXY':    dict(nr=5, ns=6, jit=0.20, diag='col', dark=0.10, light=0.12, lit=0.18, phase='lateral'),
    'PATCH':    dict(nr=5, ns=5, jit=0.14, diag='alt', dark=0.05, light=0.16, lit=0.16, phase='center'),
    'VIRUS':    dict(nr=6, ns=6, jit=0.50, diag='rand', dark=0.22, light=0.08, lit=0.16, phase='seed'),
    'TROJAN':   dict(nr=5, ns=5, jit=0.30, diag='rand', dark=0.10, light=0.10, lit=0.14, phase='inward', shell=True),
    'NULL':     dict(nr=2, ns=2, jit=0.25, diag='rand', dark=0.0, light=0.0, lit=0.0, phase='rand'),
}
FACET_ENEMY = dict(nr=4, ns=5, jit=0.18, diag='rand', dark=0.07, light=0.16, lit=0.16, phase='radial')
FLX = 230.0; FLY0, FLY1 = 60.0, 400.0
_MESH_CACHE = {}


def _pol(r, a):
    return (r * math.sin(a), r * math.cos(a))


def facet_mesh(prog, ticks, res, enemy=False):
    key = (prog, ticks, round(res, 3), enemy)
    if key in _MESH_CACHE:
        return _MESH_CACHE[key]
    p = FACET_ENEMY if enemy else FACET[prog]
    rng = np.random.default_rng(seed_of('mesh', prog, ticks, enemy))
    half = ticks * TICK / 2
    ex = 0.12
    tris = []
    if p.get('mode') == 'fan':
        C = (rng.uniform(-6, 6), R_ICON + rng.uniform(-8, 8))
        n_out = max(5, int(p['k'] * ticks / 3))
        bnd = [_pol(ROUT + 30, a) for a in np.linspace(-half - ex, half + ex, n_out)]
        bnd += [_pol(rr, half + ex) for rr in np.linspace(ROUT + 30, RIN - 30, 4)[1:-1]]
        bnd += [_pol(RIN - 30, a) for a in np.linspace(half + ex, -half - ex, max(3, n_out // 2))]
        bnd += [_pol(rr, -half - ex) for rr in np.linspace(RIN - 30, ROUT + 30, 4)[1:-1]]
        n = len(bnd)
        for k in range(n):
            B0, B1 = bnd[k], bnd[(k + 1) % n]
            m = ((B0[0] + B1[0]) / 2 + rng.uniform(-6, 6), (B0[1] + B1[1]) / 2 + rng.uniform(-6, 6))
            f = rng.uniform(0.35, 0.6)
            q = (C[0] + f * (m[0] - C[0]) + rng.uniform(-5, 5), C[1] + f * (m[1] - C[1]) + rng.uniform(-5, 5))
            tris += [(C, B0, q), (C, q, B1), (q, B0, m), (q, m, B1)]
    else:
        nr = p['nr']; ns = max(2, int(round(p['ns'] * ticks / 3)))
        radii = np.linspace(RIN - 30, ROUT + 30, nr + 1)
        phis = np.linspace(-half - ex, half + ex, ns + 1)
        drs, dps = radii[1] - radii[0], phis[1] - phis[0]
        P = [[None] * (ns + 1) for _ in range(nr + 1)]
        for i in range(nr + 1):
            for j in range(ns + 1):
                r, a = radii[i], phis[j]
                if 0 < i < nr and 0 < j < ns:
                    r += drs * p['jit'] * rng.uniform(-0.5, 0.5)
                    a += dps * p['jit'] * rng.uniform(-0.5, 0.5)
                P[i][j] = _pol(r, a)
        for i in range(nr):
            for j in range(ns):
                a_, b_, c_, d_ = P[i][j], P[i + 1][j], P[i + 1][j + 1], P[i][j + 1]
                mode = p['diag']
                dg = {'rand': rng.random() < 0.5, 'row': i % 2 == 0, 'col': j % 2 == 0,
                      'sym': j < ns / 2, 'alt': (i + j) % 2 == 0, 'same': True}[mode]
                if dg:
                    tris += [(a_, b_, c_), (a_, c_, d_)]
                else:
                    tris += [(a_, b_, d_), (b_, c_, d_)]
    # raster in local space
    Wp = int(2 * FLX * res); Hp = int((FLY1 - FLY0) * res)
    im = Image.new('I', (Wp, Hp), 0)
    d = ImageDraw.Draw(im)
    for k, tr in enumerate(tris):
        d.polygon([((x + FLX) * res, (FLY1 - y) * res) for x, y in tr], fill=k + 1)
    ids = np.asarray(im, np.int32) - 1
    ids[ids < 0] = 0
    # attributes
    n = len(tris)
    cen = np.array([[sum(v[0] for v in tr) / 3, sum(v[1] for v in tr) / 3] for tr in tris], np.float32)
    rr = np.hypot(cen[:, 0], cen[:, 1])
    col = np.zeros((n, 3), np.float32)
    if enemy:
        pal = MERIDIAN
        main, light, dark, shard = pal['main'], pal['light'], pal['dark'], pal['shard']
    else:
        pc = PROGS[prog]['c']
        main, light, dark = pc, mix(pc, np.ones(3, np.float32), 0.28), pc * 0.40
        shard = np.array([0.07, 0.06, 0.09], np.float32) + pc * 0.07
    for k in range(n):
        u = rng.random()
        if u < p['dark']:
            c = shard * rng.uniform(0.8, 1.4)
        elif u < p['dark'] + p['light']:
            c = light * rng.uniform(0.85, 1.0)
        elif u < p['dark'] + p['light'] + 0.25:
            c = mix(dark, main, rng.uniform(0.2, 0.7))
        else:
            c = main * rng.uniform(0.62, 1.0)
        nv = np.array([rng.normal(0, 0.35), rng.normal(0, 0.35), 1.0]); nv /= np.linalg.norm(nv)
        lam = float(nv @ LIGHT) / LIGHT_FLAT
        col[k] = np.clip(c * (0.72 + 0.32 * lam), 0, 1.2)
    if not enemy and prog == 'ZERO-DAY':
        pc = PROGS[prog]['c']
        for k in range(n):
            ang = math.atan2(cen[k, 0], cen[k, 1] - R_ICON)
            band = int((ang + math.pi) / (2 * math.pi) * 14) % 2
            base = mix(pc, np.ones(3, np.float32), 0.62) if band else pc * rng.uniform(0.7, 1.0)
            nv = rng.normal(0, 0.3)
            col[k] = np.clip(base * (0.8 + 0.25 * nv), 0, 1.2)
    if not enemy and prog == 'NULL':
        for k in range(n):
            col[k] = np.array([0.30, 0.30, 0.31]) * rng.uniform(0.55, 0.95)
    if not enemy and p.get('shell'):
        pc = PROGS[prog]['c']
        for k in range(n):
            inner = abs(cen[k, 0]) < 0.42 * chord(ticks, rr[k]) / 2 * 1.2 and RIN + 45 < rr[k] < ROUT - 40
            if inner:
                col[k] = col[k] * 0.45 if rng.random() > 0.25 else mix(pc, np.ones(3), 0.55)
    # plate: darken facets around the icon
    dx = cen[:, 0] / (0.42 * chord(ticks)); dy = (cen[:, 1] - R_ICON) / 85.0
    plate = np.exp(-(dx * dx + dy * dy) ** 1.5)
    col *= (1 - 0.30 * plate)[:, None]
    lit = rng.random(n) < p['lit']
    # phases
    ph = p['phase']
    if ph == 'radial':
        phase = (rr - RIN) / (ROUT - RIN)
    elif ph == 'inward':
        phase = 1 - (rr - RIN) / (ROUT - RIN)
    elif ph == 'angle':
        phase = (np.arctan2(cen[:, 0], cen[:, 1] - R_ICON) + math.pi) / (2 * math.pi)
    elif ph == 'center':
        phase = np.hypot(cen[:, 0], cen[:, 1] - R_ICON) / 170.0
    elif ph == 'lateral':
        phase = cen[:, 0] / (2 * ROUT * math.sin(half) + 1) + 0.5
    elif ph == 'seed':
        phase = np.hypot(cen[:, 0] + 40, cen[:, 1] - 320) / 260.0
    else:
        phase = rng.random(n)
    phase = (phase + rng.uniform(-0.04, 0.04, n)).astype(np.float32)
    out = dict(ids=ids, col=col, lit=lit, phase=phase, n=n)
    _MESH_CACHE[key] = out
    return out


# ----------------------------------------------------------------------------- context
class Ctx:
    pass


def program_pre(c):
    """Per-program coordinate effects (shader flavour)."""
    t = c.t
    c.tx, c.ty = c.lx.copy(), c.ly.copy()
    c.glitch = np.zeros_like(c.lx)
    if c.prog == 'EXPLOIT' and c.fx:
        band = np.floor(c.ly / 9.0)
        bucket = math.floor(t * 16)
        active = 1.0 if (bucket % 8) in (1, 2, 5) else 0.0
        on = (hash2(band, bucket, 3.0) > 0.72).astype(np.float32) * active
        off = (hash2(band, bucket, 5.0) - 0.5) * 34.0 * on
        c.tx = c.lx + off
        c.glitch = on
    elif c.prog == 'PROXY' and c.fx:
        c.tx = c.lx - 11.0 * math.sin(2 * math.pi * t)


def program_post(c, col):
    if not c.fx:
        return col
    t = c.t; pc = c.pc
    if c.prog == 'EXPLOIT':
        g = c.glitch[..., None]
        col = col * (1 - 0.45 * g) + 0.45 * g * np.stack([col[..., 2], col[..., 0] * 0.6, col[..., 1] + 0.5], -1)
    elif c.prog == 'ZERO-DAY':
        f = math.exp(-frac(t * 2) * 7.0)
        col = col + (1 - col) * 0.42 * f
    elif c.prog == 'FIREWALL':
        scan = 0.5 + 0.5 * np.cos(2 * math.pi * (c.ly / 7.0 - t * 6))
        col = col * (0.86 + 0.14 * scan[..., None])
        pos = RIN + (ROUT - RIN) * frac(t)
        col = col + pc * 0.45 * np.exp(-((c.ly - pos) / 6.0) ** 2)[..., None]
    elif c.prog == 'SANDBOX':
        p = 0.5 + 0.5 * math.sin(2 * math.pi * t)
        col = col + pc * (0.25 + 0.6 * p) * np.exp(-np.maximum(c.e, 0) / 4.0)[..., None]
    elif c.prog == 'PATCH':
        col = col * (1 + 0.16 * (0.5 + 0.5 * math.sin(2 * math.pi * t)))
        d = np.hypot(c.lx, c.ly - R_ICON); R = 40 + 200 * frac(t)
        col = col + pc * 0.35 * np.exp(-((d - R) / 7.0) ** 2)[..., None]
    elif c.prog == 'VIRUS':
        d = np.hypot(c.lx + 40, c.ly - 320); R = 270 * frac(t)
        brk = (vnoise(c.lx / 9, c.ly / 9, 4.0) > 0.35).astype(np.float32)
        col = col + pc * 0.55 * (np.exp(-((d - R) / 9.0) ** 2) * brk)[..., None]
    elif c.prog == 'TROJAN':
        w = 34 * (0.5 - 0.5 * math.cos(2 * math.pi * t))
        inside = (np.abs(c.lx) < w).astype(np.float32)
        seam = np.exp(-((np.abs(c.lx) - w) / 2.0) ** 2) * (w > 1)
        col = col * (1 - 0.35 * inside[..., None]) + mix(pc, np.ones(3), 0.5) * (0.3 * inside + 0.8 * seam)[..., None]
    elif c.prog == 'NULL':
        b = math.floor(t * 10)
        f = 0.62 if hash2(b, 1.0, 9.0) > 0.55 else 1.0
        col = col * f + 0.07 * (hash2(np.floor(c.lx / 2), np.floor(c.ly / 2), float(b)) - 0.5)[..., None]
    return col


def plate_field(c, sx_k=0.40, sy=82.0):
    sx = sx_k * chord(c.ticks)
    if c.ticks >= 5:
        sx *= 0.9
    dx = c.lx / sx; dy = (c.ly - R_ICON) / sy
    return np.exp(-(dx * dx + dy * dy) ** 1.5)


# ----------------------------------------------------------------------------- styles
def holo_pattern(c):
    lx, ly, prog = c.tx, c.ty, c.prog
    if prog == 'EXPLOIT':  # diffraction lines
        u = lx * 0.8 - ly * 0.6
        P = (0.5 + 0.5 * np.sin(u * 0.55)) ** 3 + 0.35 * (0.5 + 0.5 * np.sin(u * 0.11 + ly * 0.02))
    elif prog == 'ZERO-DAY':  # prism stars
        cs = 30.0
        row = np.floor(ly / cs)
        cu = (frac(lx / cs + 0.5 * (row % 2)) - 0.5) * cs
        cv = (frac(ly / cs) - 0.5) * cs
        sz = 0.6 + 0.6 * hash2(np.floor(lx / cs + 0.5 * (row % 2)), row, 2.0)
        star = np.clip(1 - (np.abs(cu) * np.abs(cv)) / (10 * sz) - (np.abs(cu) + np.abs(cv)) / (30 * sz), 0, 1)
        rays = 0.5 + 0.5 * np.cos(10 * np.arctan2(lx, ly - R_ICON))
        P = np.maximum(star ** 0.7, 0.45 * rays)
    elif prog == 'FIREWALL':  # brick holo
        bh, bw = 16.0, 34.0
        row = np.floor(ly / bh)
        fx = frac((lx + (row % 2) * bw / 2) / bw); fy = frac(ly / bh)
        mort = np.minimum(np.minimum(fx, 1 - fx) * bw, np.minimum(fy, 1 - fy) * bh)
        P = np.where(mort < 1.6, 0.08, 0.45 + 0.45 * fy + 0.2 * hash2(np.floor((lx + (row % 2) * bw / 2) / bw), row, 1.0))
    elif prog == 'SANDBOX':  # nested squares
        dd = np.maximum(np.abs(lx) * 1.15, np.abs(ly - R_ICON))
        P = (0.5 + 0.5 * np.cos(dd * 2 * math.pi / 14.0)) ** 2
    elif prog == 'PROXY':  # chevron diffraction
        P = (0.5 + 0.5 * np.sin((ly + np.abs(lx) * 0.9) * 2 * math.pi / 18.0)) ** 2
    elif prog == 'PATCH':  # hex holo
        s = 15.0
        px, py = lx / s, ly / s
        rx, ry = 1.0, 1.7320508
        ax = np.mod(px, rx) - rx / 2; ay = np.mod(py, ry) - ry / 2
        bx = np.mod(px - rx / 2, rx) - rx / 2; by = np.mod(py - ry / 2, ry) - ry / 2
        usea = (ax * ax + ay * ay) < (bx * bx + by * by)
        gx = np.where(usea, ax, bx); gy = np.where(usea, ay, by)
        cxi = np.floor(np.where(usea, px, px - rx / 2) / rx); cyi = np.floor(np.where(usea, py, py - ry / 2) / ry)
        q = np.abs(gx), np.abs(gy)
        hd = np.maximum(q[0] * 0.5 + q[1] * 0.866, q[0])
        P = 0.25 + 0.75 * np.exp(-(0.5 - hd) * 14) + 0.25 * hash2(cxi, cyi + 100 * usea, 6.0)
    elif prog == 'VIRUS':  # cellular
        rng = np.random.default_rng(seed_of('worley', c.ticks))
        pts = np.stack([rng.uniform(-220, 220, 60), rng.uniform(100, 380, 60)], 1).astype(np.float32)
        d1 = np.full(lx.shape, 1e9, np.float32)
        for (qx, qy) in pts:
            d1 = np.minimum(d1, (lx - qx) ** 2 + (ly - qy) ** 2)
        d1 = np.sqrt(d1)
        P = np.clip(1 - d1 / 24, 0, 1) ** 0.8 + 0.35 * (0.5 + 0.5 * np.sin(d1 * 0.7))
    elif prog == 'TROJAN':  # diamond lattice
        a = frac(lx / 22 + ly / 22) - 0.5; b = frac(lx / 22 - ly / 22) - 0.5
        P = np.clip(1 - 2 * np.maximum(np.abs(a), np.abs(b)), 0, 1) ** 0.6
    else:  # NULL: dead foil
        P = 0.25 + 0.2 * vnoise(lx / 12, ly / 12, 1.0)
    return np.clip(P, 0, 1.3).astype(np.float32)


def style_holo(c):
    t = c.t
    P = holo_pattern(c)
    em = sample_emblem(c.prog, c.ticks, c.tx, c.ty)
    em_hi = sample_emblem(c.prog, c.ticks, c.tx - 1.6, c.ty + 1.6)
    em_lo = sample_emblem(c.prog, c.ticks, c.tx + 1.6, c.ty - 1.6)
    emb = em_hi - em_lo
    th = 0.8 * math.sin(2 * math.pi * t)
    hue = frac(0.55 * P + 0.0032 * (c.tx * math.cos(th) + c.ty * math.sin(th)) + t + 0.33 * em + c.hue_off)
    sat = 0.07 if c.prog == 'NULL' else 0.66
    rain = hsv(hue, sat, np.ones_like(hue))
    foil = rain * 0.55 + c.pc * 0.45
    col = foil * (0.32 + 0.9 * P)[..., None]
    col = col * (1 - 0.25 * em)[..., None] + (0.55 + 0.45 * rain) * (1.1 * np.clip(emb, 0, 1))[..., None] \
        - 0.6 * np.clip(-emb, 0, 1)[..., None]
    gp = 120 + 250 * (0.5 + 0.5 * math.sin(2 * math.pi * t))
    gl = np.exp(-((c.tx * 0.45 + c.ty * 0.9 - gp) / 22.0) ** 2)
    col = col + (gl * (0.35 + 0.5 * P))[..., None] * (rain * 0.5 + 0.5)
    sp = (hash2(np.floor(c.tx / 2.2), np.floor(c.ty / 2.2), 3.0) > 0.992).astype(np.float32)
    col = col + sp[..., None] * (0.5 + 0.5 * math.sin(2 * math.pi * (t * 2)))
    if c.prog == 'NULL':
        col = col * 0.55
    pl = plate_field(c)
    col = col * (1 - (0.55 if c.lod <= 1 else 0.7) * pl)[..., None]
    frame = np.clip(1.5 - c.e / 3.0, 0, 1)[..., None]
    col = mix(col, 0.62 + 0.38 * rain, frame * 0.85)
    h = np.clip(c.e / 5.0, 0, 1)
    lam, _ = shade_from_height(h, 5.0 * c.S * 0.9)
    col = col * (0.85 + 0.15 * lam)[..., None]
    return col, None


def enamel_labels(c):
    lx, ly, prog = c.tx, c.ty, c.prog
    z = np.zeros(lx.shape, np.int32)
    if prog == 'EXPLOIT':
        lab = (np.floor((lx * 0.8 + ly * 0.6) / 38) % 2).astype(np.int32)
        lab[c.r > 334] = 2
    elif prog == 'ZERO-DAY':
        lab = (np.floor((np.arctan2(lx, ly - R_ICON) + math.pi) / (2 * math.pi) * 12) % 2).astype(np.int32)
        lab[c.r > 336] = 2
    elif prog == 'FIREWALL':
        bh, bw = 22.0, 46.0
        row = np.floor(ly / bh); colm = np.floor((lx + (row % 2) * bw / 2) / bw)
        lab = (hash2(colm, row, 2.0) > 0.5).astype(np.int32)
        lab = lab + (row * 1000 + colm).astype(np.int32) * 10  # unique id per brick -> mortar walls
    elif prog == 'SANDBOX':
        dd = np.maximum(np.abs(lx) / 0.9, np.abs(ly - R_ICON))
        lab = (np.floor(dd / 26) % 2).astype(np.int32)
    elif prog == 'PROXY':
        lab = (np.floor((ly + np.abs(lx) * 0.9) / 30) % 2).astype(np.int32)
    elif prog == 'PATCH':
        band = np.abs(lx * 0.6 - (ly - R_ICON) * 0.8) < 34
        lab = band.astype(np.int32)
        dots = (np.hypot(frac(lx / 16) - 0.5, frac(ly / 16) - 0.5) < 0.17) & band
        lab[dots] = 2
    elif prog == 'VIRUS':
        rng = np.random.default_rng(seed_of('spores', c.ticks))
        pts = np.stack([rng.uniform(-220, 220, 26), rng.uniform(120, 380, 26)], 1)
        rad = rng.uniform(9, 20, 26)
        lab = z.copy()
        for (qx, qy), rr in zip(pts, rad):
            d = np.hypot(lx - qx, ly - qy)
            lab[d < rr] = 1
            lab[d < rr * 0.45] = 2
    elif prog == 'TROJAN':
        lab = (np.floor(lx / 26) % 2).astype(np.int32)
        lab[c.r > 326] = 2
    else:
        lab = z
    return lab


def style_enamel(c):
    t = c.t
    lab = enamel_labels(c)
    # cartouche plate behind the icon
    L = icon_layout(c.prog, c.ticks, c.lod)
    if c.ticks >= 5:
        hw = 0.40 * chord(c.ticks); hh = 52.0 * c.lod
    else:
        hw = min(0.40 * chord(c.ticks), 74.0 * c.lod); hh = 80.0 * c.lod
    if c.prog == 'NULL':
        hh = 58.0 * c.lod
    rr = min(18.0, hw * 0.5)
    qx = np.abs(c.tx) - (hw - rr); qy = np.abs(c.ty - R_ICON) - (hh - rr)
    sd = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - rr
    lab = np.where(sd < 0, -1, lab)
    pc = c.pc
    if c.prog == 'NULL':
        pal = {0: np.array([0.36, 0.36, 0.37]), 1: np.array([0.30, 0.30, 0.31]), 2: np.array([0.24, 0.24, 0.25])}
    else:
        pal = {0: pc, 1: mix(pc, np.ones(3), 0.40), 2: pc * 0.50}
    navy = np.array([0.075, 0.06, 0.13], np.float32)
    base = np.empty(lab.shape + (3,), np.float32)
    base[:] = navy
    kind = np.where(lab < 0, -1, lab % 10 if c.prog == 'FIREWALL' else lab)
    for k, v in pal.items():
        base[kind == k] = v
    walls = dilate(edges_of(lab), 1.6 * c.S)
    metal = walls | (c.e < 4.8)
    mf = metal.astype(np.float32)
    mh = box_blur(mf, max(1, int(1.2 * c.S)), 2)
    lam_m, n_m = shade_from_height(mh, 2.5 * c.S)
    gold = np.array([0.98, 0.78, 0.38], np.float32) if c.prog != 'NULL' else np.array([0.62, 0.63, 0.66], np.float32)
    metal_col = gold * (0.40 + 0.62 * np.clip(lam_m, 0, 2))[..., None] + spec_from_normal(n_m, 30)[..., None] * 0.7
    ao = box_blur(mf, max(1, int(3 * c.S)), 2)
    enamel = base * (1 - 0.32 * ao)[..., None]
    # glossy dome over the whole pin
    hd = np.sqrt(np.clip(c.e / 55.0, 0, 1))
    lam_d, n_d = shade_from_height(hd, 55.0 * c.S * 0.35)
    gloss = 0.3 if c.prog == 'NULL' else 1.0
    col = np.where(metal[..., None], metal_col, enamel * (0.86 + 0.14 * lam_d)[..., None])
    col = col + (spec_from_normal(n_d, 50) * 0.55 * gloss)[..., None]
    soft = np.exp(-(((c.tx + 30) / 70.0) ** 2 + ((c.ty - 330) / 40.0) ** 2))
    col = col + (0.10 * gloss * soft)[..., None]
    sw = (c.rx + c.ry) * 0.70710678
    pos = -560 + 1120 * frac(t)
    band = np.exp(-((sw - pos) / 16.0) ** 2) + 0.45 * np.exp(-((sw - pos + 36) / 5.0) ** 2)
    col = col + (band * 0.75 * gloss)[..., None]
    return col, None


def style_facet(c, enemy=False):
    t = c.t
    M = facet_mesh(c.prog, c.ticks, c.S, enemy)
    ids_img = M['ids']
    Hm, Wm = ids_img.shape
    ix = np.clip(((c.tx + FLX) * c.S).astype(np.int32), 0, Wm - 1)
    iy = np.clip(((FLY1 - c.ty) * c.S).astype(np.int32), 0, Hm - 1)
    ids = ids_img[iy, ix]
    col = M['col'][ids].copy()
    neon = MERIDIAN['main'] if False else c.pc
    if enemy:
        neon = c.pc
    # facet sequence (shader): each facet flares when the sweep reaches its phase
    boost = np.clip(1 - frac(t - M['phase'][ids]) / 0.2, 0, 1) ** 2
    if c.fx:
        lit_amt = 0.55 if c.prog != 'NULL' else 0.15
        flare = MERIDIAN['light'] if enemy else mix(neon, np.ones(3), 0.25)
        col = col + boost[..., None] * flare * lit_amt
    # plate vignette
    pl = plate_field(c)
    col = col * (1 - (0.22 if c.lod <= 1 else 0.4) * pl)[..., None]
    # gritty facet seams
    e_all = dilate(edges_of(ids), 0.35 * c.S)
    col = col * (1 - 0.28 * e_all)[..., None]
    lit = M['lit'][ids]
    neon_edge = dilate(edges_of(lit.astype(np.int32)) & lit, 0.7 * c.S) & (c.e > 1.5)
    col = np.where(neon_edge[..., None], mix(neon, np.ones(3), 0.35), col)
    # grit
    gr = hash2(np.floor(c.tx / 1.6), np.floor(c.ty / 1.6), 11.0)
    col = col * (0.9 + 0.1 * gr)[..., None]
    rng = np.random.default_rng(seed_of('scratch', c.prog, c.ticks, enemy))
    for _ in range(5):
        a = rng.uniform(0, math.pi); ox, oy = rng.uniform(-80, 80), rng.uniform(170, 340)
        dd = np.abs((c.tx - ox) * math.sin(a) - (c.ty - oy) * math.cos(a))
        along = np.abs((c.tx - ox) * math.cos(a) + (c.ty - oy) * math.sin(a))
        sc = (dd < 0.5) & (along < rng.uniform(20, 70))
        col = col + sc[..., None] * 0.14
    # neon rim on the outer arc + accent band on the inner arc
    outer = np.clip(1 - np.abs(ROUT - 2.2 - c.r) / 1.8, 0, 1) * (c.e > -0.5)
    col = mix(col, mix(neon, np.ones(3), 0.4), outer[..., None])
    if enemy:
        band = ((c.r > RIN + 3) & (c.r < RIN + 12) & (c.e > 1)).astype(np.float32)
        col = mix(col, neon * 0.95, band[..., None])
    h = np.clip(c.e / 4.0, 0, 1)
    lam, _ = shade_from_height(h, 4.0 * c.S * 0.9)
    col = col * (0.8 + 0.2 * lam)[..., None]
    glow = (neon_edge[..., None] * 0.3 + outer[..., None] * 0.6) * neon
    if enemy:
        glow = glow + band[..., None] * neon * 0.4
    if c.fx:
        glow = glow + (boost * 0.3)[..., None] * neon * M['lit'][ids][..., None]
    return col, glow


STYLES = {'holo': style_holo, 'enamel': style_enamel, 'cv2': style_facet,
          'meridian': lambda c: style_facet(c, enemy=True)}


# ----------------------------------------------------------------------------- slice render
def render_slice(cv, prog, ticks, a_center, cx, cy, S, style='cv2', t=0.0, lod=1.0, gap=3.0,
                 fx=True, value=None, icon=True):
    """cx, cy, S in OUTPUT pixels (before supersampling)."""
    SS = cv.SS
    cxs, cys, Ss = cx * SS, cy * SS, S * SS
    half = ticks * TICK / 2
    angs = np.linspace(a_center - half, a_center + half, 24)
    xs, ys = [], []
    for R in (RIN, ROUT + 28):
        xs += list(cxs + R * Ss * np.sin(angs)); ys += list(cys - R * Ss * np.cos(angs))
    pad = 30 * Ss
    box = cv.bbox(min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)
    x0, y0, x1, y1 = box
    if x1 - x0 < 8 or y1 - y0 < 8:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32) + 0.5
    rx = (xx - cxs) / Ss; ry = (yy - cys) / Ss
    sa, ca = math.sin(a_center), math.cos(a_center)
    c = Ctx()
    c.lx = rx * ca + ry * sa
    c.ly = rx * sa - ry * ca
    c.rx, c.ry = rx, ry
    c.r = np.hypot(c.lx, c.ly)
    c.phi = np.arctan2(c.lx, c.ly)
    side = c.r * np.sin(half - np.abs(c.phi)) - gap / 2
    c.e = np.minimum(np.minimum(c.r - RIN, ROUT - c.r), side)
    c.half, c.ticks, c.prog, c.t, c.S, c.lod, c.fx = half, ticks, prog, t, Ss, lod, fx
    c.pc = PROGS[prog]['c']
    c.hue_off = (ORDER.index(prog) * 0.11) % 1.0
    alpha = np.clip(c.e * Ss + 0.5, 0, 1)[..., None]
    program_pre(c)
    col, glow = STYLES[style](c)
    col = program_post(c, col)
    if icon:
        img, sh = icon_local(prog, ticks, Ss, lod, value)
        fxp = (c.lx + ICON_LX) * Ss - 0.5
        fyp = (ICON_LY1 - c.ly) * Ss - 0.5
        shv = bilinear(sh, fxp, fyp)[..., 0]
        col = col * (1 - 0.55 * np.clip(shv * 1.6, 0, 1))[..., None]
        ic = bilinear(img, fxp, fyp)
        ia = ic[..., 3:4]
        col = col * (1 - ia) + ic[..., :3] * ia
    region = cv.rgb[y0:y1, x0:x1]
    region[:] = region * (1 - alpha) + np.clip(col, 0, 1.4) * alpha
    if glow is not None:
        cv.add_glow(box, glow * np.clip(c.e * Ss + 3, 0, 1)[..., None] + 0)
    return box


# ----------------------------------------------------------------------------- wheel parts
def _wheel_box(cv, cx, cy, S, R):
    SS = cv.SS
    box = cv.bbox((cx - R * S) * SS, (cy - R * S) * SS, (cx + R * S) * SS, (cy + R * S) * SS)
    x0, y0, x1, y1 = box
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32) + 0.5
    rx = (xx - cx * SS) / (S * SS); ry = (yy - cy * SS) / (S * SS)
    r = np.hypot(rx, ry)
    th = np.mod(np.arctan2(rx, -ry), 2 * math.pi)
    return box, rx, ry, r, th


def _ring_alpha(r, r0, r1, Ss):
    return np.clip(np.minimum(r - r0, r1 - r) * Ss + 0.5, 0, 1)


def wheel_base(cv, cx, cy, S, bezel='cv2', accent=(1.0, 0.24, 0.66), t=0.0, seed=3):
    """Backing disc + bezel ring. bezel in cv2 | cv2_enemy | holo | enamel."""
    Ss = S * cv.SS
    RB0, RB1 = ROUT + 6, ROUT + 46
    box, rx, ry, r, th = _wheel_box(cv, cx, cy, S, RB1 + 40)
    x0, y0, x1, y1 = box
    reg = cv.rgb[y0:y1, x0:x1]
    # drop shadow
    sh = np.clip(1 - (r - RB1) / 30, 0, 1) * (r > RB1 - 2)
    reg *= (1 - 0.6 * sh)[..., None]
    a_disc = _ring_alpha(r, -1, RB0 + 1, Ss)[..., None]
    reg[:] = reg * (1 - a_disc) + np.array([0.035, 0.03, 0.05], np.float32) * a_disc
    ar = _ring_alpha(r, RB0, RB1, Ss)
    glow = np.zeros(reg.shape, np.float32)
    acc = np.array(accent, np.float32)
    if bezel in ('cv2', 'cv2_enemy'):
        rng = np.random.default_rng(seed)
        ns = 90
        Pp = []
        for i, rad in enumerate([RB0 - 4, (RB0 + RB1) / 2, RB1 + 4]):
            row = []
            for j in range(ns):
                a = j * 2 * math.pi / ns + (rng.uniform(-0.3, 0.3) * 2 * math.pi / ns if i == 1 else 0)
                rr = rad + (rng.uniform(-5, 5) if i == 1 else 0)
                row.append((cx * cv.SS + rr * Ss * math.sin(a) - x0, cy * cv.SS - rr * Ss * math.cos(a) - y0))
            Pp.append(row)
        im = Image.new('I', (x1 - x0, y1 - y0), 0)
        d = ImageDraw.Draw(im)
        k = 0
        cols = []
        for i in range(2):
            for j in range(ns):
                j2 = (j + 1) % ns
                a_, b_, c_, d_ = Pp[i][j], Pp[i + 1][j], Pp[i + 1][j2], Pp[i][j2]
                for tr in ((a_, b_, c_), (a_, c_, d_)) if rng.random() < 0.5 else ((a_, b_, d_), (b_, c_, d_)):
                    k += 1
                    d.polygon(tr, fill=k)
                    g = rng.uniform(0.13, 0.36)
                    if bezel == 'cv2_enemy':
                        cols.append(np.array([g * 0.9, g * 0.8, g * 0.72]))
                    else:
                        cols.append(np.array([g, g * 0.97, g * 1.05]))
        ids = np.asarray(im, np.int32)
        ctab = np.vstack([np.zeros((1, 3)), np.array(cols)]).astype(np.float32)
        bc = ctab[ids]
        bc *= (1 - 0.3 * dilate(edges_of(ids), 0.4 * Ss))[..., None]
        if bezel == 'cv2_enemy':
            s_t = th * (RB0 + RB1) / 2
            stripe = (frac((s_t + (r - RB0) * 1.0) / 18.0) < 0.5)
            band = (r > RB0 + 9) & (r < RB1 - 9)
            haz = np.where(stripe[..., None], MERIDIAN['main'] * 0.95, np.array([0.06, 0.04, 0.03]))
            bc = np.where(band[..., None], haz * (0.75 + 0.25 * hash2(np.floor(th * 200), 1.0)[..., None]), bc)
            teeth = (frac(th / (2 * TICK)) < 0.55) & (r > RB1 - 1) & (r < RB1 + 9)
            ar = np.maximum(ar, _ring_alpha(r, RB1 - 1, RB1 + 9, Ss) * teeth)
            bc = np.where(teeth[..., None], MERIDIAN['main'] * 0.85, bc)
        reg[:] = reg * (1 - ar[..., None]) + bc * ar[..., None]
        rim = np.clip(1 - np.abs(r - (RB1 - 1.5)) / 1.6, 0, 1)
        if bezel == 'cv2_enemy':
            rim = np.clip(1 - np.abs(r - (RB0 + 1.5)) / 1.6, 0, 1)
        reg[:] = mix(reg, mix(acc, np.ones(3), 0.4), rim[..., None])
        glow += rim[..., None] * acc * 1.1
    elif bezel == 'holo':
        hue = frac(th / (2 * math.pi) * 3 + (r - RB0) / 80 + t)
        rain = hsv(hue, 0.55 * np.ones_like(hue), np.ones_like(hue))
        h = np.clip(np.minimum(r - RB0, RB1 - r) / 12, 0, 1)
        lam, n = shade_from_height(h, 12 * Ss * 0.8)
        chrome = (0.35 + 0.35 * np.cos(th * 2 + 1.0))[..., None] * 0.8 + 0.2
        bc = (chrome * 0.6 + rain * 0.4) * (0.6 + 0.45 * lam)[..., None] + spec_from_normal(n, 30)[..., None] * 0.6
        reg[:] = reg * (1 - ar[..., None]) + bc * ar[..., None]
        glow += (np.clip(1 - np.abs(r - RB1) / 2, 0, 1))[..., None] * rain * 0.4
    elif bezel == 'enamel':
        h = np.clip(np.minimum(r - RB0, RB1 - r) / 6, 0, 1)
        lam, n = shade_from_height(h, 6 * Ss)
        gold = np.array([0.98, 0.78, 0.38], np.float32)
        bc = gold * (0.4 + 0.6 * lam)[..., None] + spec_from_normal(n, 30)[..., None] * 0.6
        inset = (r > RB0 + 8) & (r < RB1 - 8)
        enamel = np.array([0.08, 0.06, 0.14], np.float32) * np.ones_like(bc)
        dots = np.hypot((frac(th / TICK) - 0.5) * TICK * (RB0 + RB1) / 2, r - (RB0 + RB1) / 2) < 4.5
        enamel = np.where(dots[..., None], gold * 0.9, enamel)
        bc = np.where(inset[..., None], enamel, bc)
        sw = (rx + ry) * 0.7071
        pos = -560 + 1120 * frac(t)
        bc = bc + (np.exp(-((sw - pos) / 16.0) ** 2) * 0.6)[..., None]
        reg[:] = reg * (1 - ar[..., None]) + bc * ar[..., None]
    cv.add_glow(box, glow)


def wheel_hub(cv, cx, cy, S, accent=(1.0, 0.24, 0.66), enemy=False):
    Ss = S * cv.SS
    RH = RIN - 6
    box, rx, ry, r, th = _wheel_box(cv, cx, cy, S, RH + 4)
    x0, y0, x1, y1 = box
    reg = cv.rgb[y0:y1, x0:x1]
    sec = np.floor(th / (2 * math.pi / 8))
    thc = (sec + 0.5) * 2 * math.pi / 8
    nx, ny = np.sin(thc) * 0.5, -np.cos(thc) * 0.5
    lam = (nx * LIGHT[0] + ny * LIGHT[1] + LIGHT[2]) / LIGHT_FLAT
    base = np.array([0.15, 0.14, 0.16], np.float32) if not enemy else np.array([0.16, 0.13, 0.11], np.float32)
    col = base * (0.55 + 0.6 * lam)[..., None]
    inner = r < RH - 26
    col = np.where(inner[..., None], np.array([0.05, 0.045, 0.07], np.float32) * (1 + 0.15 * np.cos(r * 0.6))[..., None], col)
    a = _ring_alpha(r, -1, RH, Ss)[..., None]
    reg[:] = reg * (1 - a) + col * a
    acc = np.array(accent, np.float32)
    rim = np.clip(1 - np.abs(r - (RH - 26)) / 1.5, 0, 1)
    reg[:] = mix(reg, acc, rim[..., None] * 0.9)
    cv.add_glow(box, rim[..., None] * acc * 0.7)


def wheel_pointer(cv, cx, cy, S, colA=(255, 240, 245), colB=(255, 61, 168)):
    SS = cv.SS; Ss = S * SS
    tip = (cx * SS, (cy - (ROUT - 24) * S) * SS)
    top = (cy - (ROUT + 62) * S) * SS
    w = 22 * Ss
    L = [(cx * SS - w, top), (cx * SS, top + 6 * Ss), tip]
    R = [(cx * SS + w, top), (cx * SS, top + 6 * Ss), tip]
    sh = [(x + 4 * Ss, y + 5 * Ss) for x, y in L + R[::-1]]
    cv.ovd.polygon(sh, fill=(0, 0, 0, 110))
    cv.ovd.polygon(L, fill=tuple(colA) + (255,))
    cv.ovd.polygon(R, fill=tuple(colB) + (255,))
    cv.ovd.line(L + [L[0]], fill=(20, 12, 24, 255), width=max(1, int(1.5 * Ss)))
    cv.ovd.line(R + [R[0]], fill=(20, 12, 24, 255), width=max(1, int(1.5 * Ss)))
    cv.ovgd.line([(p[0] / 4, p[1] / 4) for p in R], fill=tuple(colB), width=max(1, int(Ss)))


def wheel_ticks(cv, cx, cy, S, col=(225, 225, 230)):
    SS = cv.SS; Ss = S * SS
    for k in range(30):
        a = k * TICK
        r0, r1 = ROUT + 9, ROUT + (18 if k % 3 == 0 else 14)
        w = (3.2 if k % 3 == 0 else 2.2) * math.pi / 180
        pts = [(cx * SS + r0 * Ss * math.sin(a), cy * SS - r0 * Ss * math.cos(a)),
               (cx * SS + r1 * Ss * math.sin(a - w), cy * SS - r1 * Ss * math.cos(a - w)),
               (cx * SS + r1 * Ss * math.sin(a + w), cy * SS - r1 * Ss * math.cos(a + w))]
        cv.ovd.polygon(pts, fill=tuple(col) + (220,))


def hp_arc(cv, cx, cy, S, hp, hpmax, col=(123, 224, 123), text=True):
    SS = cv.SS; Ss = S * SS
    n = 26
    a0, a1 = math.radians(232), math.radians(128)
    filled = round(n * hp / hpmax)
    R0, R1 = ROUT + 62, ROUT + 84
    for k in range(n):
        aa = a0 + (a1 - a0) * (k + 0.12) / n
        ab = a0 + (a1 - a0) * (k + 0.88) / n
        pts = [(cx * SS + R0 * Ss * math.sin(aa), cy * SS - R0 * Ss * math.cos(aa)),
               (cx * SS + R1 * Ss * math.sin(aa), cy * SS - R1 * Ss * math.cos(aa)),
               (cx * SS + R1 * Ss * math.sin(ab), cy * SS - R1 * Ss * math.cos(ab)),
               (cx * SS + R0 * Ss * math.sin(ab), cy * SS - R0 * Ss * math.cos(ab))]
        if k < filled:
            cv.ovd.polygon(pts, fill=tuple(col) + (255,))
            cv.ovgd.polygon([(x / 4, y / 4) for x, y in pts], fill=tuple(int(v * 0.6) for v in col))
        else:
            cv.ovd.polygon(pts, fill=(40, 46, 44, 255))
    if text:
        f = font(62 * Ss)
        p = (cx * SS, (cy + (ROUT + 108) * S) * SS)
        cv.ovd.text(p, f'{hp}/{hpmax}', font=f, fill=tuple(col) + (255,), anchor='mt',
                    stroke_width=max(1, int(2 * Ss)), stroke_fill=(10, 30, 12, 255))
        cv.ovgd.text((p[0] / 4, p[1] / 4), f'{hp}/{hpmax}', font=font(62 * Ss / 4), fill=tuple(int(v * 0.5) for v in col), anchor='mt')


def hub_text(cv, cx, cy, S, name, sub, accent=(255, 61, 168), mark=None):
    SS = cv.SS; Ss = S * SS
    f1 = font(34 * Ss); f2 = font(15 * Ss, 'SemiBold')
    lines = name.split('\n')
    y = cy * SS - (len(lines) - 1) * 17 * Ss - (6 * Ss if mark else 0)
    if mark == 'meridian':
        mx, my = cx * SS, y - 34 * Ss
        cv.ovd.polygon([(mx - 16 * Ss, my + 10 * Ss), (mx, my - 12 * Ss), (mx + 16 * Ss, my + 10 * Ss),
                        (mx + 6 * Ss, my + 10 * Ss), (mx, my + 1 * Ss), (mx - 6 * Ss, my + 10 * Ss)],
                       fill=(255, 138, 31, 255))
    elif mark == 'cell':
        mx, my = cx * SS, y - 34 * Ss
        cv.ovd.polygon([(mx - 13 * Ss, my - 11 * Ss), (mx + 13 * Ss, my - 11 * Ss), (mx + 13 * Ss, my + 11 * Ss),
                        (mx - 13 * Ss, my + 11 * Ss)], outline=tuple(accent) + (255,), width=max(1, int(3 * Ss)))
        cv.ovd.ellipse([mx - 5 * Ss, my - 7 * Ss, mx + 5 * Ss, my + 3 * Ss], fill=tuple(accent) + (255,))
    for i, ln in enumerate(lines):
        cv.ovd.text((cx * SS, y + i * 34 * Ss), ln, font=f1, fill=(255, 255, 255, 255), anchor='mm')
    cv.ovd.text((cx * SS, y + (len(lines) - 1) * 34 * Ss + 34 * Ss), sub, font=f2, fill=(190, 190, 205, 255), anchor='mm')


def sticker(kind, size, rng):
    """Vinyl die-cut sticker (the game's sticker overlay), RGBA PIL image."""
    N = size * 2
    im = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if kind == 'tape':
        pts = []
        w, h = N * 0.9, N * 0.32
        x0, y0 = (N - w) / 2, (N - h) / 2
        for i in range(9):
            pts.append((x0 + w * i / 8, y0 + rng.uniform(-2, 2)))
        for i in range(6):
            pts.append((x0 + w + rng.uniform(-6, 2), y0 + h * i / 5))
        for i in range(9):
            pts.append((x0 + w - w * i / 8, y0 + h + rng.uniform(-2, 2)))
        for i in range(6):
            pts.append((x0 + rng.uniform(-2, 6), y0 + h - h * i / 5))
        d.polygon(pts, fill=(238, 232, 222, 235))
        d.text((N / 2, N / 2), 'CELL-9 // OPS', font=font(h * 0.55), fill=(30, 26, 34, 255), anchor='mm')
    elif kind == 'star':
        pts = []
        for k in range(10):
            a = k * math.pi / 5
            rr = (0.46 if k % 2 == 0 else 0.22) * N
            pts.append((N / 2 + rr * math.sin(a), N / 2 - rr * math.cos(a)))
        mask = Image.new('L', (N, N), 0)
        ImageDraw.Draw(mask).polygon(pts, fill=255)
        big = mask.filter(ImageFilter.MaxFilter(9))
        yy, xx = np.mgrid[0:N, 0:N] / N
        rain = hsv(frac(xx * 1.3 + yy * 0.7).astype(np.float32), 0.6 * np.ones((N, N), np.float32), np.ones((N, N), np.float32))
        holo = Image.fromarray((rain * 255).astype(np.uint8), 'RGB')
        im.paste((255, 255, 255, 255), (0, 0), big)
        im.paste(holo, (0, 0), mask)
    elif kind == 'tag':
        w, h = N * 0.86, N * 0.42
        x0, y0 = (N - w) / 2, (N - h) / 2
        d.rounded_rectangle([x0 - 5, y0 - 5, x0 + w + 5, y0 + h + 5], radius=h * 0.3, fill=(255, 255, 255, 255))
        d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=h * 0.26, fill=(255, 61, 168, 255))
        d.text((N / 2, N / 2), 'SEND IT', font=font(h * 0.62), fill=(255, 255, 255, 255), anchor='mm',
               stroke_width=2, stroke_fill=(40, 10, 30, 255))
    elif kind == 'skull':
        d.ellipse([N * 0.18, N * 0.12, N * 0.82, N * 0.70], fill=(255, 255, 255, 255))
        d.rectangle([N * 0.32, N * 0.55, N * 0.68, N * 0.86], fill=(255, 255, 255, 255))
        d.ellipse([N * 0.24, N * 0.18, N * 0.76, N * 0.64], fill=(92, 225, 255, 255))
        d.rectangle([N * 0.37, N * 0.58, N * 0.63, N * 0.80], fill=(92, 225, 255, 255))
        d.ellipse([N * 0.32, N * 0.32, N * 0.47, N * 0.47], fill=(20, 14, 30, 255))
        d.ellipse([N * 0.53, N * 0.32, N * 0.68, N * 0.47], fill=(20, 14, 30, 255))
    return im


def place_sticker(cv, kind, size, cx, cy, rot, seed):
    rng = np.random.default_rng(seed)
    st = sticker(kind, int(size * cv.SS / 2), rng)
    st = st.rotate(rot, resample=Image.BICUBIC, expand=True)
    shadow = Image.new('RGBA', st.size, (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 120), (0, 0), st.split()[3])
    shadow = shadow.filter(ImageFilter.GaussianBlur(3 * cv.SS))
    x, y = int(cx * cv.SS - st.size[0] / 2), int(cy * cv.SS - st.size[1] / 2)
    cv.ov.alpha_composite(shadow, (x + 3 * cv.SS, y + 4 * cv.SS))
    cv.ov.alpha_composite(st, (x, y))


def render_wheel(cv, cx, cy, S, slices, style='cv2', t=0.0, rot=0.0, bezel='cv2', accent=(255, 61, 168),
                 name='CELL-9', sub='Salvaged Rig', hp=(36, 50), stickers=False, lod=1.0, mini=False,
                 enemy=False, mark='cell', fx=True):
    """slices: list of (prog, ticks[, value]); style: str or dict prog->style."""
    acc = np.array(accent, np.float32) / 255.0
    wheel_base(cv, cx, cy, S, bezel=bezel, accent=acc, t=t)
    a = rot
    for s in slices:
        prog, ticks = s[0], s[1]
        value = s[2] if len(s) > 2 else None
        st = style[prog] if isinstance(style, dict) else style
        render_slice(cv, prog, ticks, a + ticks * TICK / 2, cx, cy, S, st, t, lod=lod, fx=fx, value=value)
        a += ticks * TICK
    wheel_hub(cv, cx, cy, S, accent=acc, enemy=enemy)
    if not mini:
        wheel_ticks(cv, cx, cy, S)
    pa = (255, 236, 220) if enemy else (255, 240, 248)
    wheel_pointer(cv, cx, cy, S, colA=pa, colB=tuple(int(v) for v in accent))
    if not mini:
        hub_text(cv, cx, cy, S, name, sub, accent=tuple(int(v) for v in accent), mark=mark)
        if hp:
            hp_arc(cv, cx, cy, S, hp[0], hp[1])
    if stickers:
        R = ROUT + 26
        for k, (kind, ang, sz, rotd) in enumerate([('tape', -52, 120, 40), ('star', 62, 58, -12),
                                                    ('tag', 128, 96, -38), ('skull', 236, 54, 18)]):
            aa = math.radians(ang)
            place_sticker(cv, kind, sz * S, cx + R * S * math.sin(aa), cy - R * S * math.cos(aa), rotd, seed_of('st', k))


def render_tile(cv, prog, ticks, cx, top, S, style, t=0.0, lod=1.0, fx=True, value=None):
    """A single wedge tile pointing up, its outer arc touching y=top."""
    cy = top + ROUT * S
    render_slice(cv, prog, ticks, 0.0, cx, cy, S, style, t, lod=lod, fx=fx, value=value)
    return cy
