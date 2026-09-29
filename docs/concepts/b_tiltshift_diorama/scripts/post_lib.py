"""Pillow post helpers: tilt-shift by depth, bloom, grade, glass UI with light spill, grain. Seeded only."""
import math
import os
import random
from PIL import Image, ImageFilter, ImageChops, ImageDraw, ImageFont, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
W, H = 1920, 1080


def font(name, size):
    f = {"mono": "ShareTechMono-Regular.ttf", "anton": "Anton-Regular.ttf",
         "plex": "IBMPlexSansCondensed-Medium.ttf", "plexr": "IBMPlexSansCondensed-Regular.ttf"}[name]
    return ImageFont.truetype(os.path.join(FONT_DIR, f), size)


def hx(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def load_rgb(path):
    im = Image.open(path).convert("RGB")
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
    return im


def load_depth(path):
    d = Image.open(path)
    if d.mode in ("I;16", "I;16B", "I"):
        d = d.convert("I").point(lambda v: v * (1 / 257.0)).convert("L")
    else:
        d = d.convert("L")
    if d.size != (W, H):
        d = d.resize((W, H), Image.BILINEAR)
    return d


def lut(fn):
    return [max(0, min(255, int(round(fn(v))))) for v in range(256)]


def vertical_ramp(y_focus, band, gain):
    """L image: 0 inside the focus band, rising above/below it (classic tilt-shift)."""
    col = Image.new("L", (1, H))
    px = col.load()
    for y in range(H):
        d = max(0.0, abs(y - y_focus) - band) / H
        px[0, y] = max(0, min(255, int(d * gain * 255)))
    return col.resize((W, H))


def tilt_shift(img, depth, focus, dgain, vramp=None, radii=(0, 1.2, 2.5, 4.5, 7.5, 12, 18), sharp_below=3,
               spread=6):
    """Depth-of-field by blending pre-blurred levels. depth: L (0 near .. 255 far); pixels with
    depth < sharp_below are forced sharp (map layer written as focus)."""
    b = depth.point(lut(lambda v: 0 if v < sharp_below else abs(v - focus) * dgain))
    if vramp is not None:
        b = ImageChops.add(b, vramp)
    # keep override-sharp pixels sharp even with the vertical ramp
    sharp = depth.point(lut(lambda v: 255 if v < sharp_below else 0))
    b = ImageChops.subtract(b, sharp)
    b = b.filter(ImageFilter.GaussianBlur(spread))
    n = len(radii)
    levels = [img if r == 0 else img.filter(ImageFilter.GaussianBlur(r)) for r in radii]
    out = levels[0]
    for k in range(1, n):
        lo = (k - 1) / (n - 1) * 255
        hi = k / (n - 1) * 255
        m = b.point(lut(lambda v: (v - lo) / (hi - lo) * 255))
        out = Image.composite(levels[k], out, m)
    return out, b


def bloom(img, thresh=150, radii=(3, 10, 28, 70), gains=(0.55, 0.5, 0.45, 0.35)):
    lum = img.convert("L")
    m = lum.point(lut(lambda v: 0 if v < thresh else (v - thresh) / (255 - thresh) * 255 * 1.4))
    bright = Image.composite(img, Image.new("RGB", img.size, 0), m)
    out = img
    glow_total = Image.new("RGB", img.size, 0)
    for r, g in zip(radii, gains):
        gl = bright.filter(ImageFilter.GaussianBlur(r))
        gl = ImageEnhance.Brightness(gl).enhance(g)
        glow_total = ImageChops.add(glow_total, gl)
    out = ImageChops.screen(out, glow_total)
    return out, bright


def spill_map(bright, radius=60, gain=1.6):
    """Wide ambient light from glowing elements; added onto glass UI near them (feedback 10)."""
    g = bright.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(radius / 4))
    g = g.resize((W, H), Image.BILINEAR)
    return ImageEnhance.Brightness(g).enhance(gain)


def grade(img, sat=1.0, bright=1.0, contrast=1.0, tint=None, tint_amt=0.0):
    out = ImageEnhance.Color(img).enhance(sat)
    out = ImageEnhance.Brightness(out).enhance(bright)
    out = ImageEnhance.Contrast(out).enhance(contrast)
    if tint:
        out = Image.blend(out, ImageChops.multiply(out, Image.new("RGB", img.size, hx(tint)[:3])), tint_amt)
    return out


def vignette(img, strength=0.45):
    v = Image.new("L", (256, 144), 0)
    px = v.load()
    for y in range(144):
        for x in range(256):
            dx, dy = (x - 128) / 128, (y - 72) / 72
            d = min(1.0, math.sqrt(dx * dx * 0.8 + dy * dy * 0.9))
            px[x, y] = int(255 * (1 - strength * d ** 2.2))
    v = v.resize(img.size, Image.BILINEAR)
    return ImageChops.multiply(img, Image.merge("RGB", (v, v, v)))


def grain(img, seed, amount=10):
    rng = random.Random(seed)
    t = Image.new("L", (480, 270))
    t.putdata([128 + int(rng.gauss(0, amount)) for _ in range(480 * 270)])
    t = t.resize(img.size, Image.BILINEAR)
    g = Image.merge("RGB", (t, t, t))
    return Image.blend(img, ImageChops.overlay(img, g), 0.5)


def alpha_over(base, rgba, xy=(0, 0)):
    b = base.convert("RGBA")
    b.alpha_composite(rgba, xy)
    return b.convert("RGB")


def glass_panel(base, box, spill=None, spill_gain=0.9, title=None, radius=4, alpha=200, title_col="#ff3da8",
                edge="#5ce1ff", blur=10, scan=True):
    """Navy glass panel over the frame: frosted blur, tint, light spill from nearby glows, cyan edge."""
    x0, y0, x1, y1 = [int(v) for v in box]
    crop = base.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(blur))
    tint = Image.new("RGB", crop.size, (5, 13, 28))
    crop = Image.blend(crop, tint, alpha / 255)
    if spill is not None:
        sp = spill.crop((x0, y0, x1, y1))
        crop = ImageChops.add(crop, ImageEnhance.Brightness(sp).enhance(spill_gain))
    d = ImageDraw.Draw(crop, "RGBA")
    if scan:
        for yy in range(0, crop.size[1], 3):
            d.line([(0, yy), (crop.size[0], yy)], fill=(0, 0, 0, 34))
    mask = Image.new("L", crop.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, crop.size[0] - 1, crop.size[1] - 1), radius, fill=255)
    base.paste(crop, (x0, y0), mask)
    d = ImageDraw.Draw(base, "RGBA")
    # edge: cyan rule, brightened where spill is strong
    d.rounded_rectangle((x0, y0, x1 - 1, y1 - 1), radius, outline=hx(edge, 190), width=1)
    if spill is not None:
        e = Image.new("L", (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(e).rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1), radius, outline=255, width=2)
        sp = spill.crop((x0, y0, x1, y1))
        lit = ImageChops.add(base.crop((x0, y0, x1, y1)), ImageEnhance.Brightness(sp).enhance(2.5))
        base.paste(lit, (x0, y0), e)
    if title:
        d.text((x0 + 14, y0 + 10), title, font=font("mono", 17), fill=hx("#cff6ff"))
        d.line([(x0 + 14, y0 + 34), (x1 - 14, y0 + 34)], fill=hx(title_col, 230), width=2)
    return base


def text(base, xy, s, f, fill, anchor="la", spacing=4):
    d = ImageDraw.Draw(base, "RGBA")
    d.multiline_text(xy, s, font=f, fill=fill, anchor=anchor, spacing=spacing)


def paste_rotated(base, im, cx, cy, deg):
    r = im.rotate(deg, resample=Image.BICUBIC, expand=True)
    b = base.convert("RGBA")
    b.alpha_composite(r, (int(cx - r.size[0] / 2), int(cy - r.size[1] / 2)))
    return b.convert("RGB")


def card_face(card, w, h):
    """Card content (transparent background) drawn in card space; the sticker face is GP."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    dark = card.get("dark", False)
    ink = hx("#f2eee4") if dark else hx("#111111")
    fs = 26
    while fs > 14 and font("anton", fs).getlength(card["name"]) > w - 62:
        fs -= 1
    d.text((12, 12 + (26 - fs) * 0.6), card["name"], font=font("anton", fs), fill=ink)
    # cost pip
    d.ellipse((w - 44, 10, w - 12, 42), fill=hx("#d4ff00"), outline=hx("#111111"), width=2)
    d.text((w - 28, 26), str(card["cost"]), font=font("anton", 21), fill=hx("#111111"), anchor="mm")
    # art: a mini wheel with the move drawn in ink
    cx, cy, r = w // 2, int(h * 0.47), int(w * 0.25)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=ink, width=3)
    d.ellipse((cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45), outline=ink, width=2)
    for k in range(6):
        a = k * math.pi / 3
        d.line([(cx + math.cos(a) * r * 0.45, cy + math.sin(a) * r * 0.45), (cx + math.cos(a) * r, cy + math.sin(a) * r)],
               fill=ink, width=2)
    acc = hx("#ff3da8") if not dark else hx("#5ce1ff")
    d.arc((cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10), -150, -40 + card.get("sweep", 0), fill=acc, width=5)
    d.multiline_text((12, h - 64), card["text"], font=font("plex", 15), fill=ink, spacing=2)
    d.text((12, h - 24), card.get("foot", ""), font=font("mono", 14), fill=ink)
    return im
