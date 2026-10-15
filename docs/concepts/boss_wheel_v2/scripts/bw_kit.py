"""Boss Wheel v2: shared 2D paint kit (PIL + numpy only, every random draw seeded).

Units: a wheel is laid out in MASTER units (R_OUT = 360, the round 13/41 convention). A render uses a scale S
(pixels per master unit). Canvas helpers place the wheel centre at the canvas centre.
"""
import math
import os

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

WT = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass"
OUTDIR = os.path.join(WT, "docs", "concepts", "boss_wheel_v2")
SCR = r"D:\rc_scratch\boss_wheel_v2"
os.makedirs(SCR, exist_ok=True)
GLYPHS = os.path.join(WT, "docs", "concepts", "round17_slice_system", "glyphs")
FONTS = os.path.join(WT, "assets", "fonts")
WINF = "C:/Windows/Fonts/"

INK = (12, 10, 22)
TEXT_HI = (242, 246, 255)
LIME = (212, 255, 0)
# slice colour = type (ART_BIBLE 2.3)
TYPE_COL = {
    "SHIM": (255, 61, 168), "OVERFLOW": (255, 120, 215), "DEFRAG": (92, 225, 255), "SANDBOX": (70, 226, 205),
    "DETOUR": (123, 224, 123), "HOTFIX": (170, 240, 110), "INFECT": (200, 90, 255), "TROJAN": (176, 140, 255),
    "NULL": (106, 106, 106),
}
TYPE_GLYPH = {"SHIM": "slice_exploit", "OVERFLOW": "slice_zero_day", "DEFRAG": "slice_firewall", "SANDBOX": "slice_sandbox",
              "DETOUR": "slice_proxy", "HOTFIX": "slice_patch", "INFECT": "slice_virus", "TROJAN": "slice_trojan",
              "NULL": "slice_null"}
PERFECT_GOLD = (255, 210, 77)


# ------------------------------------------------------------------ fonts
_fc = {}


def font(name, px, var=None):
    key = (name, int(px), var)
    if key not in _fc:
        path = os.path.join(FONTS, name) if os.path.exists(os.path.join(FONTS, name)) else WINF + name
        f = ImageFont.truetype(path, max(4, int(px)))
        if var:
            f.set_variation_by_name(var)
        _fc[key] = f
    return _fc[key]


def f_num(px):
    return font("bahnschrift.ttf", px, b"Bold Condensed")


def f_ui(px, var=b"SemiBold Condensed"):
    return font("bahnschrift.ttf", px, var)


def f_mono(px):
    return font("ShareTechMono-Regular.ttf", px)


def f_anton(px):
    return font("Anton-Regular.ttf", px)


def f_plex(px):
    return font("IBMPlexSansCondensed-Medium.ttf", px)


# ------------------------------------------------------------------ colour helpers
def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def mul(c, k):
    return tuple(int(max(0, min(255, v * k))) for v in c)


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------ RNG
def rng(seed):
    return np.random.default_rng(seed)


# ------------------------------------------------------------------ smooth shapes
def catmull(pts, n=10, closed=True):
    """Catmull-Rom spline through pts -> dense polyline."""
    P = list(pts)
    if len(P) < 3:
        return P
    out = []
    m = len(P)
    rng_ = range(m) if closed else range(m - 1)
    for i in rng_:
        p0 = P[(i - 1) % m] if closed or i > 0 else P[0]
        p1 = P[i]
        p2 = P[(i + 1) % m]
        p3 = P[(i + 2) % m] if closed or i + 2 < m else P[-1]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    if not closed:
        out.append(P[-1])
    return out


def xf(pts, ox=0.0, oy=0.0, s=1.0, ang=0.0, sx=None, sy=None, px=0.0, py=0.0):
    """Transform points: about pivot (px,py) rotate ang deg, scale, then translate."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    sx = s if sx is None else sx
    sy = s if sy is None else sy
    o = []
    for x, y in pts:
        x, y = (x - px) * sx, (y - py) * sy
        o.append((ox + px + x * ca - y * sa, oy + py + x * sa + y * ca))
    return o


def stroke_poly(cl, w0, w1=None):
    """A tapered stroke polygon along an open centre line."""
    w1 = w0 if w1 is None else w1
    L, R = [], []
    n = len(cl)
    for i in range(n):
        x, y = cl[i]
        xa, ya = cl[max(0, i - 1)]
        xb, yb = cl[min(n - 1, i + 1)]
        dx, dy = xb - xa, yb - ya
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        w = (w0 + (w1 - w0) * i / max(1, n - 1)) / 2
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    return L + R[::-1]


# ------------------------------------------------------------------ masks and paint
def L(size, fill=0):
    return Image.new("L", size, fill)


def rgba(size, col=(0, 0, 0), a=0):
    return Image.new("RGBA", size, tuple(col) + (a,))


def arr(im):
    return np.asarray(im, np.float32) / 255.0


def from_arr(a, mode="L"):
    return Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8), mode)


def solid(mask, col, k=1.0):
    lay = Image.new("RGBA", mask.size, tuple(col) + (0,))
    lay.putalpha(mask if k == 1.0 else mask.point(lambda v: int(v * k)))
    return lay


def blur(im, r):
    return im.filter(ImageFilter.GaussianBlur(r)) if r > 0 else im


def _morph(mask, r, F):
    """Dilate/erode by r px as repeated small rank filters (O(r) instead of O(r^2) per pixel)."""
    r = int(round(r))
    if r <= 0:
        return mask
    if r <= 3:
        return mask.filter(F(2 * r + 1))
    out = mask
    for _ in range(r // 2):
        out = out.filter(F(5))
    if r % 2:
        out = out.filter(F(3))
    return out


def grow(mask, r):
    return _morph(mask, r, ImageFilter.MaxFilter)


def shrink(mask, r):
    return _morph(mask, r, ImageFilter.MinFilter)


def mask_mul(a, b):
    return ImageChops.multiply(a, b)


def mask_sub(a, b):
    return ImageChops.subtract(a, b)


def shifted(mask, dx, dy):
    return ImageChops.offset(mask, int(round(dx)), int(round(dy)))


def rim_light(mask, dx, dy, width_blur=1.0):
    """Edge band of the mask facing direction (dx,dy) (light comes FROM that direction)."""
    inner = shifted(mask, -dx, -dy)
    e = ImageChops.subtract(mask, inner)
    return blur(e, width_blur)


def lin_grad(size, c0, c1, vertical=True, gamma=1.0):
    w, h = size
    t = np.linspace(0, 1, h if vertical else w) ** gamma
    c0, c1 = np.array(c0, np.float32), np.array(c1, np.float32)
    g = c0[None, :] + (c1 - c0)[None, :] * t[:, None]
    if vertical:
        a = np.repeat(g[:, None, :], w, axis=1)
    else:
        a = np.repeat(g[None, :, :], h, axis=0)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def rad_grad(size, cx, cy, r, c0, c1, gamma=1.0):
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = np.clip(np.hypot(xx - cx, yy - cy) / max(1e-3, r), 0, 1) ** gamma
    c0, c1 = np.array(c0, np.float32), np.array(c1, np.float32)
    a = c0 + (c1 - c0) * t[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def fill_grad(mask, c0, c1, y0, y1):
    """Fill a mask with a vertical gradient between y0 and y1 (pixel rows)."""
    w, h = mask.size
    t = np.clip((np.arange(h, dtype=np.float32) - y0) / max(1, (y1 - y0)), 0, 1)
    c0, c1 = np.array(c0, np.float32), np.array(c1, np.float32)
    g = c0[None, :] + (c1 - c0)[None, :] * t[:, None]
    a = np.repeat(g[:, None, :], w, axis=1)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    im.putalpha(mask)
    return im


_noise_cache = {}


def noise(size, scale, seed, octaves=3):
    """Smooth value noise in 0..1 (bilinear upsampled random grids). Memoised (pure function of its arguments)."""
    key = (tuple(size), int(scale), seed, octaves)
    if key not in _noise_cache:
        if len(_noise_cache) > 64:
            _noise_cache.clear()
        _noise_cache[key] = _noise(size, scale, seed, octaves)
    return _noise_cache[key]


def _noise(size, scale, seed, octaves=3):
    w, h = size
    r = rng(seed)
    acc = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        s = max(1, int(scale / (2 ** o)))
        gw, gh = w // s + 2, h // s + 2
        g = r.random((gh, gw)).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((gw * s, gh * s), Image.BICUBIC).crop((0, 0, w, h))
        acc += amp * (np.asarray(im, np.float32) / 255)
        tot += amp
        amp *= 0.5
    return acc / tot


def add_glow(base, mask_or_layer, col, r, k=1.0):
    """Additive-looking glow: blurred mask in colour composited with screen blend."""
    m = mask_or_layer.split()[3] if mask_or_layer.mode == "RGBA" else mask_or_layer
    g = blur(m, r)
    if k != 1.0:
        g = g.point(lambda v: int(min(255, v * k)))
    return screen(base, solid(g, col))


def screen(base, top):
    """Screen-blend an RGBA layer onto base (respects top alpha)."""
    b = np.asarray(base, np.float32) / 255
    t = np.asarray(top, np.float32) / 255
    ta = t[..., 3:4]
    rgb = 1 - (1 - b[..., :3]) * (1 - t[..., :3] * ta)
    out = np.concatenate([rgb, np.maximum(b[..., 3:4], ta * 0.0 + b[..., 3:4])], axis=2)
    return Image.fromarray(np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8), "RGBA")


def add(base, top, k=1.0):
    b = np.asarray(base, np.float32)
    t = np.asarray(top, np.float32)
    rgb = b[..., :3] + t[..., :3] * (t[..., 3:4] / 255) * k
    out = np.concatenate([np.clip(rgb, 0, 255), b[..., 3:4]], axis=2)
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def over(base, top, xy=(0, 0)):
    base.alpha_composite(top, (int(round(xy[0])), int(round(xy[1]))))
    return base


def masked(layer, mask):
    """Multiply layer alpha by mask."""
    out = layer.copy()
    a = ImageChops.multiply(out.split()[3], mask)
    out.putalpha(a)
    return out


def tone(layer, sat=1.0, val=1.0):
    """Desaturate/darken an RGBA layer."""
    a = np.asarray(layer, np.float32)
    rgb = a[..., :3]
    g = (rgb * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1, keepdims=True)
    rgb = (g + (rgb - g) * sat) * val
    a = np.concatenate([np.clip(rgb, 0, 255), a[..., 3:4]], axis=2)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def tone_map(layer, sat_map, val_map):
    """Per-pixel desaturate/darken (maps are float arrays HxW)."""
    a = np.asarray(layer, np.float32)
    rgb = a[..., :3]
    g = (rgb * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1, keepdims=True)
    rgb = (g + (rgb - g) * sat_map[..., None]) * val_map[..., None]
    a = np.concatenate([np.clip(rgb, 0, 255), a[..., 3:4]], axis=2)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def greyscale(im):
    return im.convert("L").convert("RGBA")


def keyline(img, w, col=INK, soft=0.6):
    a = img.split()[3]
    k = blur(grow(a, w), soft)
    lay = Image.new("RGBA", img.size, col + (0,))
    lay.putalpha(k)
    lay.alpha_composite(img)
    return lay


def drop_shadow(img, dx, dy, r, k=0.6, col=(0, 0, 0)):
    a = blur(img.split()[3], r).point(lambda v: int(v * k))
    lay = Image.new("RGBA", img.size, col + (0,))
    lay.putalpha(shifted(a, dx, dy))
    lay.alpha_composite(img)
    return lay


# ------------------------------------------------------------------ glyphs (locked atlas, round 17)
_gc = {}


def glyph_mask(name):
    if name in _gc:
        return _gc[name]
    p = os.path.join(GLYPHS, name + ".png")
    im = Image.open(p)
    if im.mode == "RGBA":
        m = im.split()[3]
    else:
        m = im.convert("L")
    _gc[name] = m
    return m


def glyph(name, px, outline=None, fill=(255, 255, 255), edge=INK, mask=None):
    """White glyph with a dark rounded outline (ART_BIBLE 3.5: outline width 0.075 x size)."""
    outline = max(1, int(round(px * 0.075))) if outline is None else outline
    m = (mask if mask is not None else glyph_mask(name)).resize((int(px), int(px)), Image.LANCZOS)
    pad = outline * 2 + 4
    big = L((int(px) + 2 * pad, int(px) + 2 * pad))
    big.paste(m, (pad, pad))
    o = blur(grow(big, outline), outline * 0.35).point(lambda v: min(255, int(v * 2.2)))
    out = Image.new("RGBA", big.size, edge + (0,))
    out.putalpha(o)
    out.paste(Image.new("RGBA", big.size, fill + (255,)), (0, 0), big)
    return out


def text_img(txt, f, fill=(255, 255, 255), stroke=0, edge=INK, track=0):
    bb = f.getbbox(txt, stroke_width=stroke)
    w = int(bb[2] - bb[0] + 8 + track * len(txt))
    h = int(bb[3] - bb[1] + 8)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if track:
        x = -bb[0] + 4
        for ch in txt:
            d.text((x, -bb[1] + 4), ch, font=f, fill=fill, stroke_width=stroke, stroke_fill=edge)
            x += f.getlength(ch) + track
    else:
        d.text((-bb[0] + 4, -bb[1] + 4), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=edge)
    return im


def paste_c(base, im, cx, cy):
    base.alpha_composite(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))))


def rot_c(im, ang, resample=Image.BICUBIC):
    """Rotate about centre, same size (ang deg, clockwise positive like screen angles)."""
    return im.rotate(-ang, resample=resample)


# ------------------------------------------------------------------ polar helpers (screen: 0 deg = up, clockwise)
def pol(cx, cy, r, ang):
    a = math.radians(ang)
    return (cx + r * math.sin(a), cy - r * math.cos(a))


def ring_mask(size, cx, cy, r0, r1, a0=None, a1=None, n=180):
    m = L(size)
    d = ImageDraw.Draw(m)
    if a0 is None:
        d.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], fill=255)
        if r0 > 0:
            d.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], fill=0)
        return m
    pts = [pol(cx, cy, r1, a0 + (a1 - a0) * k / n) for k in range(n + 1)]
    pts += [pol(cx, cy, r0, a1 - (a1 - a0) * k / n) for k in range(n + 1)]
    d.polygon(pts, fill=255)
    return m


def polar_field(size, cx, cy):
    """Return (r, ang_deg) arrays; ang 0 = up, clockwise, in [0,360)."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = xx - cx, yy - cy
    r = np.hypot(dx, dy)
    ang = (np.degrees(np.arctan2(dx, -dy)) + 360) % 360
    return r, ang


def polar_wrap(strip, size, cx, cy, r0, r1, ang0=0.0, span=360.0, inner_bottom=True):
    """Wrap a flat strip (x = angle, y = radius, row 0 = OUTER edge) into an annulus. numpy nearest/bilinear."""
    sw, sh = strip.size
    r, ang = polar_field(size, cx, cy)
    a = ((ang - ang0) % 360) / span
    u = a * sw
    v = (r1 - r) / max(1e-3, (r1 - r0)) * sh
    valid = (r >= r0) & (r <= r1) & (a <= 1.0)
    src = np.asarray(strip.convert("RGBA"), np.float32)
    u0 = np.clip(np.floor(u).astype(np.int32), 0, sw - 1)
    v0 = np.clip(np.floor(v).astype(np.int32), 0, sh - 1)
    u1 = np.clip(u0 + 1, 0, sw - 1) if span < 360 else (u0 + 1) % sw
    v1 = np.clip(v0 + 1, 0, sh - 1)
    fu = (u - np.floor(u))[..., None]
    fv = (v - np.floor(v))[..., None]
    c = (src[v0, u0] * (1 - fu) * (1 - fv) + src[v0, u1] * fu * (1 - fv) + src[v1, u0] * (1 - fu) * fv + src[v1, u1] * fu * fv)
    c[~valid] = 0
    return Image.fromarray(np.clip(c, 0, 255).astype(np.uint8), "RGBA")


# ------------------------------------------------------------------ misc
def vignette(size, cx, cy, r, k=0.8, gamma=2.0):
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = np.clip(np.hypot(xx - cx, yy - cy) / r, 0, 1.5) ** gamma
    a = np.clip(t * k, 0, 1)
    return from_arr(a)


def particles(size, n, seed, rmin, rmax, col, alpha=(80, 220), area=None, blur_r=0.0):
    w, h = size
    r_ = rng(seed)
    lay = rgba(size)
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        if area:
            x, y = r_.uniform(area[0], area[2]), r_.uniform(area[1], area[3])
        else:
            x, y = r_.uniform(0, w), r_.uniform(0, h)
        rr = r_.uniform(rmin, rmax)
        a = int(r_.uniform(*alpha))
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=tuple(col) + (a,))
    return blur(lay, blur_r) if blur_r else lay


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def ease_out(t, p=3):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** p


def ease_in(t, p=2):
    t = max(0.0, min(1.0, t))
    return t ** p


def label(d, xy, txt, f, fill=TEXT_HI, anchor="la"):
    d.text(xy, txt, font=f, fill=fill, anchor=anchor)
