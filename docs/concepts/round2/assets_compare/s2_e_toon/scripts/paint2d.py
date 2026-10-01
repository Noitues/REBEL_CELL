"""Pillow side of S2: painted-toon 2D helpers (ink outlines, painted paper, grime, stamps, icons).
Everything is drawn at 2-4x and downsampled. Seeded randomness only.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops, ImageEnhance

BG = (0x2A, 0x2A, 0x2E)
INK = (28, 18, 16)
CREAM = (244, 232, 208)
FD = "C:/Windows/Fonts/"
_F = {}


def font(name, size):
    key = (name, size)
    if key not in _F:
        f = {"title": "GILLUBCD.TTF", "slab": "ROCKEB.TTF", "marker": "segoescb.ttf", "ink": "Inkfree.ttf",
             "stencil": "STENCIL.TTF", "body": "segoeuib.ttf", "bodyr": "segoeui.ttf"}[name]
        _F[key] = ImageFont.truetype(FD + f, size)
    return _F[key]


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def mix(a, b, t):
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


# ------------------------------------------------------------------ texture
def noise(size, seed, scale=6, soft=2.0):
    rng = random.Random(seed)
    w, h = size
    sm = Image.new("L", (max(2, w // scale), max(2, h // scale)))
    sm.putdata([rng.randint(0, 255) for _ in range(sm.width * sm.height)])
    return sm.resize(size, Image.BICUBIC).filter(ImageFilter.GaussianBlur(soft))


def painted(size, base, seed, amt=0.16, streak=True, grime=0.25):
    """Hand-painted fill: blotches, brush streaks, bottom grime, a few rust runs."""
    w, h = size
    col = Image.new("RGB", size, hx(base) if isinstance(base, str) else base)
    n = noise(size, seed, 10, 3)
    light = Image.new("RGB", size, mix(col.getpixel((0, 0)), (255, 240, 210), 0.35))
    dark = Image.new("RGB", size, shade(col.getpixel((0, 0)), 0.62))
    out = Image.composite(light, col, n.point(lambda v: int(max(0, v - 150) * 2.0 * amt * 3)))
    out = Image.composite(dark, out, n.point(lambda v: int(max(0, 110 - v) * 2.0 * amt * 3)))
    if streak:
        s = Image.new("L", (max(2, w // 40), h))
        rng = random.Random(seed + 1)
        s.putdata([rng.randint(0, 255) for _ in range(s.width * s.height)])
        s = s.resize(size, Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2))
        out = Image.composite(dark, out, s.point(lambda v: int(max(0, v - 190) * 1.2)))
    if grime:
        g = Image.linear_gradient("L").resize(size)
        g = ImageChops.multiply(g, noise(size, seed + 2, 5, 2).point(lambda v: min(255, v + 60)))
        out = Image.composite(shade(dark.getpixel((0, 0)), 0.8) and Image.new("RGB", size, shade(col.getpixel((0, 0)), 0.45)),
                              out, g.point(lambda v: int(v * grime)))
        rng = random.Random(seed + 3)
        dr = ImageDraw.Draw(out)
        for _ in range(int(w * h / 9000 * grime) + 1):          # rust runs
            x = rng.uniform(0, w)
            y0 = rng.uniform(0, h * 0.6)
            dr.line([(x, y0), (x + rng.uniform(-2, 2), y0 + rng.uniform(10, h * 0.3))],
                    fill=mix(col.getpixel((0, 0)), (110, 52, 28), 0.55), width=rng.choice((1, 2)))
    return out


def wobble_poly(pts, amt, seed, closed=True, step=8):
    """Densify a polygon and jitter it a little (hand-inked edge)."""
    rng = random.Random(seed)
    out = []
    n = len(pts)
    for i in range(n if closed else n - 1):
        a, b = pts[i], pts[(i + 1) % n]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(L / step))
        for j in range(k):
            t = j / k
            out.append((a[0] + (b[0] - a[0]) * t + rng.uniform(-amt, amt), a[1] + (b[1] - a[1]) * t + rng.uniform(-amt, amt)))
    if not closed:
        out.append(pts[-1])
    return out


def rrect_pts(x0, y0, x1, y1, r, n=6):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def mask_poly(size, pts):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


def ink_shape(img, pts, fill, seed=0, ink=6, wob=1.6, tex=True, amt=0.16, grime=0.2, ink_col=INK):
    """Painted fill + wobbly thick ink outline for a polygon on an RGBA image."""
    pts = wobble_poly(pts, wob, seed)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, y0 = int(min(xs)) - ink, int(min(ys)) - ink
    x1, y1 = int(max(xs)) + ink + 1, int(max(ys)) + ink + 1
    w, h = max(2, x1 - x0), max(2, y1 - y0)
    loc = [(x - x0, y - y0) for x, y in pts]
    m = mask_poly((w, h), loc)
    face = painted((w, h), fill, seed, amt=amt, grime=grime) if tex else Image.new("RGB", (w, h), hx(fill) if isinstance(fill, str) else fill)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer.paste(face, (0, 0), m)
    d = ImageDraw.Draw(layer)
    if ink:
        d.line(loc + [loc[0]], fill=ink_col + (255,), width=ink, joint="curve")
    img.alpha_composite(layer, (x0, y0))


def text_ink(img, xy, s, fnt, fill=CREAM, ink=INK, stroke=4, anchor="mm", shadow=True):
    d = ImageDraw.Draw(img)
    if shadow:
        d.text((xy[0] + stroke * 0.6, xy[1] + stroke * 0.9), s, font=fnt, fill=ink + (200,), anchor=anchor,
               stroke_width=stroke, stroke_fill=ink + (200,))
    d.text(xy, s, font=fnt, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=ink)


def distress(img, seed, amt=0.35, scale=4):
    """Knock random holes in a stamp/print (alpha)."""
    a = img.getchannel("A")
    n = noise(img.size, seed, scale, 1.0)
    holes = n.point(lambda v: 0 if v > 255 * (1 - amt * 0.6) else 255)
    img.putalpha(ImageChops.multiply(a, holes))
    return img


def fit(tile, w, h):
    t = tile.copy()
    bb = t.getbbox()
    if bb:
        t = t.crop(bb)
    t.thumbnail((w, h), Image.LANCZOS)
    return t


def paste_c(img, tile, cx, cy):
    img.alpha_composite(tile, (int(cx - tile.width / 2), int(cy - tile.height / 2)))


def drop_shadow(img, tile, cx, cy, off=(6, 9), blur=6, a=0.5):
    sh = Image.new("RGBA", tile.size, (8, 4, 6, 0))
    sh.putalpha(tile.getchannel("A").filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * a)))
    img.alpha_composite(sh, (int(cx - tile.width / 2 + off[0]), int(cy - tile.height / 2 + off[1])))


# ------------------------------------------------------------------ sheet frame
def new_sheet(num, title, sub=None):
    img = Image.new("RGBA", (1920, 1080), BG + (255,))
    text_ink(img, (40, 38), "%s  %s" % (num, title), font("title", 40), anchor="lm", stroke=3)
    if sub:
        ImageDraw.Draw(img).text((44, 72), sub, font=font("bodyr", 18), fill=(170, 164, 150), anchor="lm")
    ImageDraw.Draw(img).text((1880, 40), "S2  E-format toon", font=font("body", 18), fill=(150, 146, 136), anchor="rm")
    return img


def label(img, cx, y, s, size=20, col=(232, 224, 206), sub=None):
    d = ImageDraw.Draw(img)
    d.text((cx, y), s, font=font("body", size), fill=col, anchor="mt")
    if sub:
        d.text((cx, y + size + 4), sub, font=font("bodyr", size - 4), fill=(160, 156, 146), anchor="mt")


def tape(img, cx, cy, w, h, ang, seed):
    t = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    ink_shape(t, [(2, 2), (w - 3, 3), (w - 2, h - 3), (3, h - 2)], "#d8cc9e", seed=seed, ink=0, amt=0.25, grime=0.1)
    t = distress(t, seed, 0.08)
    a = t.getchannel("A").point(lambda v: int(v * 0.85))
    t.putalpha(a)
    t = t.rotate(ang, expand=True, resample=Image.BICUBIC)
    paste_c(img, t, cx, cy)
