"""GLITCH VECTOR CRT - Pillow post: CRT/tilt-shift/fog, the Heat glitch, glass UI, paper stickers.

Pure Pillow (no numpy). Every random choice takes a seeded random.Random.
The layer order is the style's rule:
  DIGITAL (city, wheels, glass UI)  ->  light spill  ->  CRT + HEAT GLITCH  ->  ANALOG (stickers, marker)
so the glitch corrupts the screen but never the stickers and the marker sitting on the glass.
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont, ImageEnhance, ImageOps

W, H = 1920, 1080
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
FONTS = os.path.join(ROOT, "assets", "fonts")

PAL = {
    "void": (2, 4, 8), "phosphor": (57, 255, 156), "cyan": (92, 225, 255), "magenta": (255, 43, 214),
    "pink": (255, 61, 168), "acid": (212, 255, 0), "harm": (255, 68, 51), "amber": (255, 176, 0),
    "gain": (123, 224, 123), "orange": (255, 140, 26), "violet": (176, 77, 255),
    "glass": (5, 13, 28), "glass_edge": (92, 225, 255), "text_hi": (242, 246, 255), "text_mid": (175, 192, 214),
    "text_lo": (122, 136, 156), "paper": (242, 238, 228), "paper_alt": (233, 228, 214), "note_yellow": (242, 220, 122),
    "sticker_pink": (245, 175, 203), "ink": (17, 17, 17), "harm_ink": (171, 46, 34), "flagged": (255, 122, 26),
}


def font(name, size):
    files = {"mono": "ShareTechMono-Regular.ttf", "anton": "Anton-Regular.ttf", "plex": "IBMPlexSansCondensed-Medium.ttf",
             "plexr": "IBMPlexSansCondensed-Regular.ttf", "marker": "PermanentMarker-Regular.ttf"}
    return ImageFont.truetype(os.path.join(FONTS, files[name]), size)


# ------------------------------------------------------------------ basic ops
def add(base, layer, k=1.0):
    if k != 1.0:
        layer = ImageEnhance.Brightness(layer).enhance(k)
    return ImageChops.add(base.convert("RGB"), layer.convert("RGB"))


def screen(base, layer):
    return ImageChops.screen(base.convert("RGB"), layer.convert("RGB"))


def recede(img, desat=0.35, dim=0.42, blur=2.2, tint=(10, 30, 40)):
    """Push the city back behind combat: desaturate, darken, soften, cool (feedback 3)."""
    im = ImageEnhance.Color(img).enhance(desat)
    im = ImageEnhance.Brightness(im).enhance(dim)
    im = im.filter(ImageFilter.GaussianBlur(blur))
    t = Image.new("RGB", im.size, tint)
    return Image.blend(im, t, 0.12)


def vgrad_mask(size, stops):
    """stops: list of (y_frac, value 0..255); linear between."""
    w, h = size
    col = Image.new("L", (1, h))
    px = col.load()
    for y in range(h):
        f = y / (h - 1)
        for (a, va), (b, vb) in zip(stops, stops[1:]):
            if a <= f <= b:
                t = (f - a) / max(b - a, 1e-6)
                px[0, y] = int(va + (vb - va) * t)
                break
    return col.resize((w, h))


def tilt_shift(img, focus=(0.42, 0.78), max_blur=7.0, keep=None):
    """Ortho tilt-shift: sharp band, blur growing with distance (top = far) (feedback 7.3)."""
    f0, f1 = focus
    out = img
    for k, r in enumerate((max_blur * 0.35, max_blur * 0.7, max_blur)):
        bl = img.filter(ImageFilter.GaussianBlur(r))
        lvl = (k + 1) / 3
        # far (top) side gets progressively more; near (bottom) side gets a little
        top_edge = max(0.0, f0 - 0.14 * (k + 1))
        m = vgrad_mask(img.size, [(0, 255), (top_edge, 255), (min(f0, top_edge + 0.14), 0), (f1, 0),
                                  (min(1.0, f1 + 0.25 * (k + 1)), int(150 * lvl)), (1, int(150 * lvl))])
        if keep is not None:  # depth-aware exception: near, tall things (the HQ tower) stay sharp
            m = ImageChops.subtract(m, keep)
        out = Image.composite(bl, out, m)
    return out


def fog_patches(img, rng, n=14, tint=(40, 90, 110), strength=0.5, region=(0, 0, W, H), soften=True, scale=1.0):
    """Patchy fog: separate banks, each with its own blur radius and density (feedback 7.2)."""
    dens = Image.new("L", img.size, 0)
    for i in range(n):
        layer = Image.new("L", img.size, 0)
        d = ImageDraw.Draw(layer)
        cx = rng.uniform(region[0], region[2]); cy = rng.uniform(region[1], region[3])
        w = rng.uniform(220, 700) * scale; h = w * rng.uniform(0.16, 0.36)
        for k in range(rng.randint(3, 7)):
            ox, oy = rng.uniform(-w * 0.5, w * 0.5), rng.uniform(-h * 0.4, h * 0.4)
            s_ = rng.uniform(0.35, 0.8)
            d.ellipse((cx + ox - w * s_ / 2, cy + oy - h * s_ / 2, cx + ox + w * s_ / 2, cy + oy + h * s_ / 2),
                      fill=int(rng.uniform(110, 230)))
        blur = rng.choice((5, 12, 24, 45, 80))   # some banks crisp-edged, some very soft
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
        dens = ImageChops.lighter(dens, layer)
    alpha = dens.point(lambda v: int(v * strength))
    fogged = Image.composite(Image.new("RGB", img.size, tint), img, alpha)
    if not soften:
        return fogged
    # fog is lit from inside by the city: soften what is behind it
    soft = img.filter(ImageFilter.GaussianBlur(6))
    fogged2 = Image.composite(Image.composite(Image.new("RGB", img.size, tint), soft, alpha), fogged, dens.point(lambda v: min(255, v)))
    return fogged2


def scanlines(img, period=3, dark=0.86):
    m = Image.new("L", (1, period), 255)
    m.putpixel((0, period - 1), int(255 * dark))
    m = m.resize((1, period)).resize((img.width, period))
    tile = Image.new("L", img.size)
    for y in range(0, img.height, period):
        tile.paste(m, (0, y))
    return ImageChops.multiply(img.convert("RGB"), Image.merge("RGB", (tile, tile, tile)))


def vignette(img, k=0.55):
    w, h = img.size
    m = Image.new("L", (w // 8, h // 8), 0)
    d = ImageDraw.Draw(m)
    d.ellipse((-w // 16, -h // 16, w // 8 + w // 16, h // 8 + h // 16), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(w // 50)).resize((w, h))
    dark = ImageEnhance.Brightness(img).enhance(1 - k)
    return Image.composite(img, dark, m)


def grain(img, rng, amount=10):
    n = Image.effect_noise((img.width // 2, img.height // 2), amount).resize(img.size).convert("L")
    return ImageChops.add(img.convert("RGB"), Image.merge("RGB", (n, n, n)), 1.0, -128)


def crt(img, rng, vig=0.45):
    img = scanlines(img, 3, 0.84)
    img = rgb_split(img, 1)
    img = vignette(img, vig)
    return grain(img, rng, 8)


# ------------------------------------------------------------------ HEAT GLITCH (feedback 11)
def rgb_split(img, dx, dy=0):
    r, g, b = img.convert("RGB").split()
    r = ImageChops.offset(r, -dx, -dy)
    b = ImageChops.offset(b, dx, dy)
    return Image.merge("RGB", (r, g, b))


def binary_rain(size, rng, density, col=(57, 255, 156), fnt=None):
    lay = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(lay)
    fnt = fnt or font("mono", 18)
    cw = 16
    cols = size[0] // cw
    for c in range(cols):
        if rng.random() > density:
            continue
        x = c * cw
        head = rng.uniform(-100, size[1] + 200)
        length = rng.randint(6, 30)
        for k in range(length):
            y = head - k * 20
            if 0 <= y < size[1]:
                a = (1 - k / length) ** 1.6
                cc = tuple(int(v * a) for v in (col if k else (220, 255, 235)))
                d.text((x, y), rng.choice("01"), font=fnt, fill=cc)
    return lay


def glitch(img, level, rng, rain_col=(57, 255, 156)):
    """level 0..1 : COOL ~0.05, NOTICED ~0.3, FLAGGED ~0.6, HUNTED 1.0.
    Minor flicker at low Heat, screen-wide corruption at HUNTED. Switchable in Options."""
    im = img.convert("RGB")
    w, h = im.size
    if level <= 0:
        return im
    # 1. global RGB channel split grows with heat
    im = rgb_split(im, int(1 + 3 * level ** 1.3))
    # 2. scanline tearing: horizontal bands displaced sideways
    for _ in range(int(2 + 20 * level ** 1.5)):
        y = rng.randrange(0, h - 4)
        bh = rng.randint(2, int(6 + 34 * level))
        dx = int(rng.gauss(0, 8 + 55 * level))
        band = im.crop((0, y, w, min(h, y + bh)))
        band = ImageChops.offset(band, dx, 0)
        if rng.random() < 0.4 * level:
            band = rgb_split(band, int(4 + 24 * level))
        im.paste(band, (0, y))
    # 3. datamosh blocks: macroblocks copied from elsewhere, smeared, quantized
    for _ in range(int(24 * level ** 2)):
        bs = rng.choice((16, 16, 32, 32, 48))
        bw, bh = bs * rng.randint(1, 5), bs * rng.randint(1, 2)
        sx, sy = rng.randrange(0, w - bw), rng.randrange(0, h - bh)
        tx = max(0, min(w - bw, sx + rng.randint(-3, 3) * bs))
        ty = max(0, min(h - bh, sy + rng.randint(-2, 2) * bs))
        blk = im.crop((sx, sy, sx + bw, sy + bh))
        r = rng.random()
        if r < 0.35:
            blk = blk.resize((max(1, bw // bs), max(1, bh // bs))).resize((bw, bh), Image.NEAREST)
        elif r < 0.6:
            blk = blk.crop((0, 0, bw, 2)).resize((bw, bh))  # vertical smear (motion-vector drag)
        elif r < 0.75:
            blk = ImageOps.posterize(blk, 2)
        im.paste(blk, (tx, ty))
    # 4. flicker: a few dim/bright rolling bands
    for _ in range(int(1 + 5 * level)):
        y = rng.randrange(0, h)
        bh = rng.randint(20, int(40 + 100 * level))
        band = im.crop((0, y, w, min(h, y + bh)))
        band = ImageEnhance.Brightness(band).enhance(rng.choice((0.55, 0.7, 1.25, 1.4)))
        im.paste(band, (0, y))
    # 5. scrolling binary rain (from FLAGGED up)
    if level > 0.35:
        im = ImageChops.add(im, ImageEnhance.Brightness(binary_rain(im.size, rng, 0.42 * (level - 0.3), rain_col)).enhance(0.3 + 0.4 * level))
    return im


# ------------------------------------------------------------------ GLASS UI
def glass_panel(img, box, title=None, edge=PAL["glass_edge"], alpha=0.86, rule=PAL["pink"]):
    x0, y0, x1, y1 = box
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle(box, fill=PAL["glass"] + (int(255 * alpha),))
    # faint scanlines inside glass
    for y in range(y0 + 2, y1, 4):
        d.line((x0 + 1, y, x1 - 1, y), fill=(92, 225, 255, 10))
    d.rectangle(box, outline=edge + (190,), width=1)
    # corner brackets
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line((cx, cy, cx + 14 * sx, cy), fill=edge + (255,), width=2)
        d.line((cx, cy, cx, cy + 14 * sy), fill=edge + (255,), width=2)
    if title:
        f = font("mono", 20)
        d.text((x0 + 14, y0 + 9), title, font=f, fill=PAL["text_hi"] + (255,))
        d.line((x0 + 14, y0 + 36, x1 - 14, y0 + 36), fill=rule + (230,), width=2)
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"))
    return img


def text(img, xy, s, fnt, fill, anchor="la"):
    ImageDraw.Draw(img).text(xy, s, font=fnt, fill=fill, anchor=anchor)


def light_spill(img, emissive, panels, k=0.55, blur=60):
    """Glows cast ambient light onto nearby GLASS panels (feedback 10). Stickers/marker excluded:
    they are composited later, so they never receive it."""
    spill = emissive.filter(ImageFilter.GaussianBlur(blur))
    spill = ImageEnhance.Brightness(spill).enhance(k * 2.2)
    mask = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(mask)
    for b in panels:
        d.rectangle(b, fill=255)
    lit = ImageChops.screen(img, spill)
    # rim: panel edges catch more light
    rim = Image.new("L", img.size, 0)
    dr = ImageDraw.Draw(rim)
    for b in panels:
        dr.rectangle(b, outline=255, width=3)
    rim_lit = ImageChops.screen(img, ImageEnhance.Brightness(spill).enhance(2.0))
    out = Image.composite(lit, img, mask)
    return Image.composite(rim_lit, out, rim)


# ------------------------------------------------------------------ PAPER / STICKERS (analog)
def paper_texture(size, rng, base=PAL["paper"], fibres=True):
    w, h = size
    im = Image.new("RGB", size, base)
    n = Image.effect_noise((max(1, w // 2), max(1, h // 2)), 18).resize(size).convert("L")
    im = ImageChops.multiply(im, Image.merge("RGB", [n.point(lambda v: 205 + v // 5)] * 3))
    if fibres:
        d = ImageDraw.Draw(im)
        for _ in range(int(w * h / 900)):
            x, y = rng.uniform(0, w), rng.uniform(0, h)
            a = rng.uniform(0, math.pi)
            L = rng.uniform(3, 9)
            c = tuple(max(0, v - rng.randint(10, 25)) for v in base)
            d.line((x, y, x + L * math.cos(a), y + L * math.sin(a)), fill=c, width=1)
    return im


def halftone(size, rng, ink, spacing=7, angle=0.3, fn=None):
    w, h = size
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for gy in range(-h, 2 * h, spacing):
        for gx in range(-w, 2 * w, spacing):
            x = gx * math.cos(angle) - gy * math.sin(angle)
            y = gx * math.sin(angle) + gy * math.cos(angle)
            if 0 <= x < w and 0 <= y < h:
                v = fn(x / w, y / h) if fn else 0.5
                r = spacing * 0.55 * v
                if r > 0.4:
                    d.ellipse((x - r, y - r, x + r, y + r), fill=ink + (255,))
    return im


def die_cut(img_rgba, border=7, col=(250, 250, 246)):
    """Sticker: white die-cut border following the alpha, slightly rounded."""
    a = img_rgba.split()[3]
    grown = a.filter(ImageFilter.MaxFilter(border * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 100 else 0)
    base = Image.new("RGBA", img_rgba.size, col + (0,))
    base.putalpha(grown)
    return Image.alpha_composite(base, img_rgba)


def pad(im, p):
    out = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    out.paste(im, (p, p))
    return out


def place_sticker(img, st, center, rot, shadow=(8, 10), lift=0.0, slap_blur=0):
    """Paste a sticker with a hard offset shadow. lift>0 = mid-slap: bigger, softer, farther shadow."""
    st = pad(st, 40)
    if lift > 0:
        st = st.resize((int(st.width * (1 + 0.18 * lift)), int(st.height * (1 + 0.18 * lift))), Image.BICUBIC)
    st = st.rotate(rot, resample=Image.BICUBIC, expand=True)
    if slap_blur:
        st = st.filter(ImageFilter.GaussianBlur(slap_blur))
    a = st.split()[3]
    sh = Image.new("RGBA", st.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * (0.55 - 0.25 * lift))))
    if lift > 0:
        sh = sh.filter(ImageFilter.GaussianBlur(10 * lift))
    base = img.convert("RGBA")
    sx, sy = int(center[0] - st.width / 2), int(center[1] - st.height / 2)
    ox, oy = int(shadow[0] * (1 + 3 * lift)), int(shadow[1] * (1 + 3 * lift))
    base.paste(sh, (sx + ox, sy + oy), sh)
    base.paste(st, (sx, sy), st)
    img.paste(base.convert("RGB"))
    return img


def tape(size, rng, col=(236, 226, 190)):
    w, h = size
    im = Image.new("RGBA", size, col + (170,))
    d = ImageDraw.Draw(im)
    for x in range(0, w, 3):  # torn ends
        d.line((x, 0, x, rng.randint(0, 3)), fill=(0, 0, 0, 0))
        d.line((x, h - 1, x, h - 1 - rng.randint(0, 3)), fill=(0, 0, 0, 0))
    return im


def card_sticker(rng, title, cost, rules, kind="paper", rarity="common", glyph="spin", w=172, h=240):
    """A card as a die-cut sticker. kind: paper | black | pink (card type). rarity by stock."""
    bgc = {"paper": PAL["paper"], "black": (22, 22, 24), "pink": PAL["sticker_pink"]}[kind]
    ink = PAL["ink"] if kind != "black" else PAL["paper"]
    face = paper_texture((w, h), rng, bgc, fibres=(kind != "black")).convert("RGBA")
    d = ImageDraw.Draw(face)
    # illustration window (riso: ink + one card-type colour, misregistered)
    ix0, iy0, ix1, iy1 = 10, 44, w - 10, 44 + int(h * 0.48)
    win = Image.new("RGBA", (ix1 - ix0, iy1 - iy0), (0, 0, 0, 0))
    spot = {"paper": PAL["pink"], "black": PAL["cyan"], "pink": (180, 30, 110)}[kind]
    ht = halftone(win.size, rng, spot, 6, 0.35, fn=lambda u, v: 0.25 + 0.75 * max(0.0, 1 - math.hypot(u - 0.5, v - 0.55) * 1.7))
    win.alpha_composite(ht, (3, 2))
    dw = ImageDraw.Draw(win)
    cxw, cyw = win.width / 2, win.height / 2 + 4
    R = min(win.width, win.height) * 0.36
    if glyph == "spin":
        dw.arc((cxw - R, cyw - R, cxw + R, cyw + R), 20, 320, fill=ink + (255,), width=5)
        dw.polygon([(cxw + R * 0.95, cyw - R * 0.55), (cxw + R * 1.25, cyw - R * 0.05), (cxw + R * 0.62, cyw - R * 0.02)], fill=ink + (255,))
        for k in range(8):
            a = k / 8 * 6.283
            dw.line((cxw + R * 0.55 * math.cos(a), cyw + R * 0.55 * math.sin(a), cxw + R * 0.75 * math.cos(a), cyw + R * 0.75 * math.sin(a)), fill=ink + (255,), width=3)
    elif glyph == "bolt":
        dw.polygon([(cxw - 8, cyw - R), (cxw + R * 0.5, cyw - R), (cxw + 4, cyw - 4), (cxw + R * 0.55, cyw - 4),
                    (cxw - R * 0.4, cyw + R * 1.1), (cxw - 4, cyw + 6), (cxw - R * 0.5, cyw + 6)], fill=ink + (255,))
    elif glyph == "shield":
        dw.polygon([(cxw - R * 0.8, cyw - R * 0.8), (cxw + R * 0.8, cyw - R * 0.8), (cxw + R * 0.7, cyw + R * 0.1), (cxw, cyw + R),
                    (cxw - R * 0.7, cyw + R * 0.1)], outline=ink + (255,), width=5)
    elif glyph == "nudge":
        for s in (-1, 1):
            dw.polygon([(cxw + s * R * 0.2, cyw - R * 0.6), (cxw + s * R * 1.0, cyw), (cxw + s * R * 0.2, cyw + R * 0.6)], fill=ink + (255,))
    face.alpha_composite(win, (ix0, iy0))
    d.rectangle((ix0, iy0, ix1, iy1), outline=ink + (255,), width=2)
    # title + cost gem (marker numeral in a circle)
    fs = 26
    while fs > 14 and d.textlength(title, font=font("anton", fs)) > w - 64:
        fs -= 1
    d.text((14, 10 + (26 - fs) // 2), title, font=font("anton", fs), fill=ink + (255,))
    d.ellipse((w - 44, 6, w - 8, 42), fill=PAL["acid"] + (255,), outline=(17, 17, 17, 255), width=2)
    d.text((w - 26, 25), str(cost), font=font("marker", 24), fill=(17, 17, 17, 255), anchor="mm")
    # effect band + rules
    by = iy1 + 8
    y = by
    for line in rules:
        d.text((12, y), line, font=font("plex", 15), fill=ink + (255,))
        y += 18
    if rarity == "rare":  # holographic foil sheen across the stock
        foil = Image.new("RGBA", (w, h))
        fd = ImageDraw.Draw(foil)
        for k in range(-h, w + h, 3):
            hue = (k / 40.0) % 1.0
            c = tuple(int(150 + 105 * math.sin(6.283 * (hue + o))) for o in (0, 0.33, 0.66))
            fd.line((k, 0, k - h, h), fill=c + (34,), width=3)
        face.alpha_composite(foil)
    elif rarity == "uncommon":  # glossy sticker highlight
        gl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gd = ImageDraw.Draw(gl)
        gd.polygon([(0, 0), (w * 0.55, 0), (0, h * 0.35)], fill=(255, 255, 255, 46))
        face.alpha_composite(gl)
    # rounded corners
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 10, fill=255)
    face.putalpha(m)
    return die_cut(face, 6)


def peel_corner(st, frac=0.2):
    """Lifted corner of a sticker mid-slap: fold the bottom-right corner back (shows the paper backing)."""
    w, h = st.size
    s = int(min(w, h) * frac)
    out = st.copy()
    d = ImageDraw.Draw(out)
    d.polygon([(w - s, h), (w, h - s), (w, h)], fill=(0, 0, 0, 0))
    d.polygon([(w - s, h), (w, h - s), (w - s - 6, h - s - 6)], fill=(214, 210, 200, 255), outline=(160, 156, 146, 255))
    return out
