"""Pillow helpers: glyphs, the glyph+number label, plates, bloom, backgrounds, placement."""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

import common as C

SS = 4  # supersampling for glyph masks
OUTLINE = (12, 8, 18)


def font(path, size):
    return ImageFont.truetype(path, int(size))


# ---------------------------------------------------------------- glyphs (unit box, y down)
def _poly(d, pts, s, fill=255):
    d.polygon([(x * s, y * s) for x, y in pts], fill=fill)


def _ell(d, cx, cy, r, s, fill=255, ry=None):
    ry = r if ry is None else ry
    d.ellipse([(cx - r) * s, (cy - ry) * s, (cx + r) * s, (cy + ry) * s], fill=fill)


def glyph_mask(kind, size):
    s = size * SS
    im = Image.new("L", (s, s), 0)
    d = ImageDraw.Draw(im)
    if kind == "dagger":  # EXPLOIT: blade, guard, grip
        _poly(d, [(0.5, 0.0), (0.64, 0.2), (0.62, 0.62), (0.38, 0.62), (0.36, 0.2)], s)
        _poly(d, [(0.16, 0.6), (0.84, 0.6), (0.84, 0.72), (0.16, 0.72)], s)
        _poly(d, [(0.42, 0.7), (0.58, 0.7), (0.58, 0.9), (0.42, 0.9)], s)
        _ell(d, 0.5, 0.92, 0.09, s)
        _poly(d, [(0.49, 0.12), (0.51, 0.12), (0.51, 0.56), (0.49, 0.56)], s, 0)  # fuller
    elif kind == "burst":  # ZERO-DAY: 8-point star
        pts = []
        for i in range(16):
            a = -math.pi / 2 + i * math.pi / 8
            r = 0.5 if i % 2 == 0 else 0.2
            pts.append((0.5 + r * math.cos(a), 0.5 + r * math.sin(a)))
        _poly(d, pts, s)
    elif kind == "shield":  # FIREWALL: shield with wall courses
        _poly(d, [(0.12, 0.06), (0.88, 0.06), (0.88, 0.5), (0.5, 0.96), (0.12, 0.5)], s)
        for y in (0.3, 0.52):
            _poly(d, [(0.1, y), (0.9, y), (0.9, y + 0.06), (0.1, y + 0.06)], s, 0)
        for x, y0, y1 in ((0.5, 0.06, 0.3), (0.32, 0.36, 0.52), (0.68, 0.36, 0.52), (0.5, 0.58, 0.8)):
            _poly(d, [(x - 0.03, y0), (x + 0.03, y0), (x + 0.03, y1), (x - 0.03, y1)], s, 0)
    elif kind == "cube":  # SANDBOX: isometric box
        c, r = (0.5, 0.52), 0.46
        hexp = [(c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))
                for a in (-90, -30, 30, 90, 150, 210)]
        _poly(d, hexp, s)
        w = 0.035
        for a in (-30, 90, 210):
            ex = c[0] + r * math.cos(math.radians(a))
            ey = c[1] + r * math.sin(math.radians(a))
            d.line([(c[0] * s, c[1] * s), (ex * s, ey * s)], fill=0, width=int(w * 2 * s))
    elif kind == "chevrons":  # PROXY: double chevron
        for x0 in (0.06, 0.44):
            _poly(d, [(x0, 0.1), (x0 + 0.2, 0.1), (x0 + 0.5, 0.5), (x0 + 0.2, 0.9), (x0, 0.9), (x0 + 0.3, 0.5)], s)
    elif kind == "cross":  # PATCH: plus
        _poly(d, [(0.36, 0.06), (0.64, 0.06), (0.64, 0.36), (0.94, 0.36), (0.94, 0.64), (0.64, 0.64),
                  (0.64, 0.94), (0.36, 0.94), (0.36, 0.64), (0.06, 0.64), (0.06, 0.36), (0.36, 0.36)], s)
    elif kind == "virus":  # VIRUS: particle with knobbed spikes
        _ell(d, 0.5, 0.5, 0.27, s)
        for i in range(8):
            a = i * math.pi / 4
            x1, y1 = 0.5 + 0.4 * math.cos(a), 0.5 + 0.4 * math.sin(a)
            d.line([(0.5 * s, 0.5 * s), (x1 * s, y1 * s)], fill=255, width=int(0.08 * s))
            _ell(d, x1, y1, 0.085, s)
        _ell(d, 0.42, 0.44, 0.06, s, 0)
        _ell(d, 0.58, 0.58, 0.05, s, 0)
    elif kind == "gift":  # TROJAN: gift box with bow
        _poly(d, [(0.12, 0.42), (0.88, 0.42), (0.88, 0.94), (0.12, 0.94)], s)
        _poly(d, [(0.06, 0.28), (0.94, 0.28), (0.94, 0.42), (0.06, 0.42)], s)
        _poly(d, [(0.44, 0.28), (0.56, 0.28), (0.56, 0.94), (0.44, 0.94)], s, 0)
        _poly(d, [(0.06, 0.42), (0.94, 0.42), (0.94, 0.47), (0.06, 0.47)], s, 0)
        d.ellipse([0.2 * s, 0.04 * s, 0.5 * s, 0.3 * s], outline=255, width=int(0.08 * s))
        d.ellipse([0.5 * s, 0.04 * s, 0.8 * s, 0.3 * s], outline=255, width=int(0.08 * s))
    elif kind == "null":  # NULL: slashed zero
        d.ellipse([0.14 * s, 0.14 * s, 0.86 * s, 0.86 * s], outline=255, width=int(0.13 * s))
        d.line([(0.14 * s, 0.86 * s), (0.86 * s, 0.14 * s)], fill=255, width=int(0.13 * s))
    return im.resize((size, size), Image.LANCZOS)


def text_mask(txt, height):
    """Anton digits sized so the cap height is `height` px."""
    f = font(C.FONT_NUM, height * 1.36 * SS)
    l, t, r, b = f.getbbox(txt)
    im = Image.new("L", (r - l + 4 * SS, b - t + 4 * SS), 0)
    ImageDraw.Draw(im).text((2 * SS - l, 2 * SS - t), txt, font=f, fill=255)
    w, h = im.size
    return im.resize((max(1, w // SS), max(1, h // SS)), Image.LANCZOS)


def label(kind, value, chord_px, wide=False, scale=1.0):
    """Upright glyph + number (white, dark outline). Up = outward along the slice axis."""
    g = int(max(10, min(chord_px * 0.34, 62 * scale)))
    if kind == "null":
        g = int(g * 1.35)
    gm = glyph_mask(kind, g)
    tm = text_mask(str(value), g * 1.05) if kind != "null" else None
    gap = max(2, int(g * 0.1))
    if tm is None:
        W, H = g, g
        parts = [(gm, 0, 0)]
    elif wide:
        W = g + gap + tm.width
        H = max(g, tm.height)
        parts = [(gm, 0, (H - g) // 2), (tm, g + gap, (H - tm.height) // 2)]
    else:
        W = max(g, tm.width)
        H = g + gap + tm.height
        parts = [(gm, (W - g) // 2, 0), (tm, (W - tm.width) // 2, g + gap)]
    o = max(2, int(round(g * 0.09)))
    pad = o * 3
    mask = Image.new("L", (W + 2 * pad, H + 2 * pad), 0)
    for m, x, y in parts:
        mask.paste(m, (x + pad, y + pad), m)
    out_m = mask.filter(ImageFilter.MaxFilter(2 * o + 1))
    shadow = out_m.filter(ImageFilter.GaussianBlur(o * 1.2))
    img = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", mask.size, (0, 0, 0, 255))
    sh.putalpha(shadow.point(lambda v: int(v * 0.75)))
    img.alpha_composite(sh)
    ol = Image.new("RGBA", mask.size, OUTLINE + (255,))
    ol.putalpha(out_m)
    img.alpha_composite(ol)
    wh = Image.new("RGBA", mask.size, (255, 255, 255, 255))
    wh.putalpha(mask)
    img.alpha_composite(wh)
    return img


def place(canvas, img, cx, cy, angle_deg):
    """Rotate `img` CCW by angle_deg and alpha-composite it centred at (cx, cy)."""
    r = img.rotate(angle_deg, resample=Image.BICUBIC, expand=True)
    x, y = int(round(cx - r.width / 2)), int(round(cy - r.height / 2))
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(r, (x, y), r)
    canvas.alpha_composite(layer)


def plate(canvas_size, cx, cy, w, h, angle_deg, strength=0.55):
    """Soft dark elliptical plate (the 'calm' term) to sit under a label."""
    pw, ph = int(w * 2), int(h * 2)
    m = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(m).ellipse([pw * 0.18, ph * 0.18, pw * 0.82, ph * 0.82], fill=int(255 * strength))
    m = m.filter(ImageFilter.GaussianBlur(min(pw, ph) * 0.1))
    m = m.rotate(angle_deg, resample=Image.BICUBIC, expand=True)
    layer = Image.new("L", canvas_size, 0)
    layer.paste(m, (int(cx - m.width / 2), int(cy - m.height / 2)))
    return layer


def apply_plates(base_rgba, plate_l):
    """Darken base under plate mask, only where the base has alpha (stays inside tiles)."""
    a = np.array(base_rgba).astype(np.float32)
    p = np.array(plate_l).astype(np.float32) / 255.0 * (a[..., 3] / 255.0)
    a[..., :3] *= (1.0 - p[..., None])
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")


def bloom(img, thresh=200, radius=14, gain=0.8):
    rgb = img.convert("RGB")
    a = np.array(rgb).astype(np.float32)
    lum = a.max(axis=2)
    m = ((lum - thresh) / (255 - thresh)).clip(0, 1)
    hi = Image.fromarray((a * m[..., None]).clip(0, 255).astype(np.uint8))
    b1 = np.array(hi.filter(ImageFilter.GaussianBlur(radius))).astype(np.float32)
    b2 = np.array(hi.filter(ImageFilter.GaussianBlur(radius * 3))).astype(np.float32)
    glow = (b1 * 0.7 + b2 * 0.6) * gain
    out = Image.fromarray(glow.clip(0, 255).astype(np.uint8)).convert("RGBA")
    out.putalpha(Image.fromarray(glow.max(axis=2).clip(0, 255).astype(np.uint8)))
    return out


def add_glow(canvas, glow):
    """Additive blend of an RGB(A) glow layer onto canvas."""
    base = canvas.convert("RGB")
    g = glow.convert("RGB")
    res = ImageChops.add(base, g)
    out = res.convert("RGBA")
    return out


def drop_shadow(rgba, offset=(10, 14), blur=16, alpha=0.75):
    a = rgba.getchannel("A").filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha))
    sh = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
    sh.putalpha(a)
    out = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    out.paste(sh, offset, sh)
    return out


def background(w, h, tint=(255, 61, 168), seed=3):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    top = np.array([16, 12, 26], np.float32)
    bot = np.array([7, 6, 12], np.float32)
    t = (yy / h)[..., None]
    img = top * (1 - t) + bot * t
    cx, cy = w / 2, h * 0.45
    d = np.sqrt(((xx - cx) / w) ** 2 + ((yy - cy) / h) ** 2)
    glow = np.exp(-(d / 0.32) ** 2)[..., None] * np.array(tint, np.float32) * 0.07
    img = img + glow
    # faint machined grid
    grid = ((xx % 48) < 1) | ((yy % 48) < 1)
    img = img + grid[..., None] * 5.0
    rng = np.random.default_rng(seed)
    img = img + rng.normal(0, 1.6, (h, w, 1))
    vig = 1.0 - 0.55 * (d ** 1.6)
    img = img * vig[..., None]
    out = Image.fromarray(img.clip(0, 255).astype(np.uint8)).convert("RGBA")
    return out


def text(canvas, xy, s, size, fill=(235, 230, 245, 255), path=None, anchor="la"):
    d = ImageDraw.Draw(canvas)
    d.text(xy, s, font=font(path or C.FONT_UI, size), fill=fill, anchor=anchor)


def chord_px(ticks, ppu):
    return 2 * C.R_ANCHOR * math.sin(C.half_angle(ticks)) * ppu
