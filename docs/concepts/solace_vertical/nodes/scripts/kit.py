"""Page-mock drawing kit (PIL): CRT windows, vinyl sticker lettering, choice stickers, price tags, small icons."""
import math
import random
import sys
sys.path.insert(0, "D:/rc_scratch/solace_v1/nodes/scripts")
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont
from common import *

NAVY = (8, 14, 34)
YELLOW = (255, 226, 0)
INKC = (17, 17, 17)
KRAFT = (200, 164, 112)
GLYPHS = "D:/rc_art/art-pass/docs/concepts/round17_slice_system/glyphs/"

KCOL = {"rest": (191, 115, 255), "workshop": (255, 209, 77), "cache": (77, 242, 230)}


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def S3(box, pad, fn, scale=3):
    """draw with fn(draw, ox, oy, scale) on a supersampled transparent crop covering box grown by pad; return (img, (x, y))."""
    x0, y0, x1, y1 = [int(v) for v in box]
    pad = int(math.ceil(pad))
    x0 -= pad
    y0 -= pad
    x1 += pad
    y1 += pad
    w, h = x1 - x0, y1 - y0
    im = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fn(d, x0, y0, scale)
    return im.resize((w, h), Image.LANCZOS), (x0, y0)


def rr(img, box, r, fill=None, outline=None, ow=0, pad=None):
    pad = (ow + 3) if pad is None else pad

    def fn(d, ox, oy, s):
        b = [(box[0] - ox) * s, (box[1] - oy) * s, (box[2] - ox) * s, (box[3] - oy) * s]
        d.rounded_rectangle(b, radius=r * s, fill=fill, outline=outline, width=int(ow * s))
    im, (x, y) = S3(box, pad, fn)
    img.alpha_composite(im, (x, y))


def poly_aa(img, pts, fill=None, outline=None, ow=0):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    box = (min(xs), min(ys), max(xs), max(ys))

    def fn(d, ox, oy, s):
        P = [((x - ox) * s, (y - oy) * s) for x, y in pts]
        if fill:
            d.polygon(P, fill=fill)
        if outline and ow:
            d.line(P + [P[0]], fill=outline, width=int(ow * s), joint="curve")
    im, (x, y) = S3(box, ow + 3, fn)
    img.alpha_composite(im, (x, y))


def glow(img, mask_fn, col, radius, alpha):
    """add a soft glow: mask_fn(draw) draws white shapes on an L image of the page size."""
    m = Image.new("L", img.size, 0)
    mask_fn(ImageDraw.Draw(m))
    m = m.filter(ImageFilter.GaussianBlur(radius))
    layer = Image.new("RGBA", img.size, col + (255,))
    layer.putalpha(m.point(lambda v: int(v * alpha)))
    img.alpha_composite(layer)


def text(img, xy, s, f, fill, anchor="la", stroke=0, stroke_fill=None):
    ImageDraw.Draw(img).text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=stroke_fill)


def tw(s, f):
    return ImageDraw.Draw(Image.new("L", (4, 4))).textlength(s, font=f)


# ---------------------------------------------------------------------------------------------------------------------
# backdrops
# ---------------------------------------------------------------------------------------------------------------------
def city_backdrop(tint, dark=0.62, blur=16, crop=(300, 0, 1900, 900), seed_flip=False):
    bg = Image.open(PLATE).convert("RGBA").crop(crop).resize((1920, 1080), Image.LANCZOS)
    if seed_flip:
        bg = bg.transpose(Image.FLIP_LEFT_RIGHT)
    bg = bg.filter(ImageFilter.GaussianBlur(blur))
    bg = Image.blend(bg, Image.new("RGBA", bg.size, (6, 8, 22, 255)), dark)
    bg = Image.blend(bg, Image.new("RGBA", bg.size, mix((6, 8, 22), tint, 0.35) + (255,)), 0.16)
    return bg


# ---------------------------------------------------------------------------------------------------------------------
# CRT window
# ---------------------------------------------------------------------------------------------------------------------
def crt_window(img, box, accent, title, tag="", alpha=232, head=True, seed=1, glass_tint=0.10):
    x0, y0, x1, y1 = box
    glass = mix(NAVY, accent, glass_tint)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle(box, fill=glass + (alpha,))
    # edge glow inside: a blurred frame
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rectangle(box, outline=255, width=6)
    m = m.filter(ImageFilter.GaussianBlur(10))
    g = Image.new("RGBA", img.size, accent + (255,))
    g.putalpha(m.point(lambda v: int(v * 0.30)))
    layer.alpha_composite(g)
    d = ImageDraw.Draw(layer)
    # faint hex dump
    rnd = random.Random(seed)
    f = mono(12)
    for row in range(int((y1 - y0) / 17)):
        if rnd.random() < 0.55:
            s = " ".join("%02X" % rnd.randrange(256) for _ in range(rnd.randrange(8, 26)))
            if row >= 3:
                d.text((x0 + 14 + rnd.randrange(0, 60), y0 + 8 + row * 17), s, font=f, fill=accent + (9,))
    # scanlines every 3 px
    sl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sl)
    for y in range(int(y0), int(y1), 3):
        sd.line((x0, y, x1, y), fill=(0, 0, 0, 38))
    layer.alpha_composite(sl)
    d = ImageDraw.Draw(layer)
    d.rectangle(box, outline=accent + (200,), width=2)
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x1, y1, -1, -1), (x0, y1, 1, -1)):
        d.line((cx, cy, cx + 14 * sx, cy), fill=accent + (255,), width=3)
        d.line((cx, cy, cx, cy + 14 * sy), fill=accent + (255,), width=3)
    img.alpha_composite(layer)
    if head and title:
        hf = mono(23)
        col = mix(accent, PAPER, 0.35)
        text(img, (x0 + 18, y0 + 14), "> " + title.upper(), hf, col)
        if tag:
            text(img, (x1 - 18, y0 + 14), tag.upper(), mono(18), CELL_ACID, "ra")
            # the tag's square cursor
        d = ImageDraw.Draw(img)
        d.rectangle((x0 + 12, y0 + 46, x1 - 12, y0 + 47), fill=accent + (205,))


# ---------------------------------------------------------------------------------------------------------------------
# vinyl sticker lettering
# ---------------------------------------------------------------------------------------------------------------------
def sticker_word(img, xy, s, px, fill, tilt=0.0, anchor="lt", shadow_col=None, border=10, ink=4):
    f = anton(px)
    w = int(tw(s, f)) + 2 * (border + ink + 8)
    h = int(px * 1.5) + 2 * (border + ink + 8)
    SC = 2
    lay = Image.new("RGBA", (w * SC, h * SC), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    F = anton(px * SC)
    c = (w * SC / 2, h * SC / 2)
    d.text(c, s, font=F, fill=(255, 255, 255, 255), anchor="mm", stroke_width=(border + ink) * SC, stroke_fill=(252, 251, 249, 255))
    d.text(c, s, font=F, fill=INKC + (255,), anchor="mm", stroke_width=ink * SC, stroke_fill=INKC + (255,))
    # extrude (ink) under the fill
    for k in range(1, int(px * 0.07) + 2):
        d.text((c[0], c[1] + k * SC), s, font=F, fill=shadow_col or mix(fill, (0, 0, 0), 0.55), anchor="mm")
    d.text(c, s, font=F, fill=fill + (255,), anchor="mm")
    # a gloss band on the upper half
    gm = Image.new("L", lay.size, 0)
    ImageDraw.Draw(gm).rectangle((0, 0, w * SC, int(h * SC * 0.46)), fill=34)
    gm = ImageChops.multiply(gm, lay.split()[3])
    gl = Image.new("RGBA", lay.size, (255, 255, 255, 255))
    gl.putalpha(gm)
    lay.alpha_composite(gl)
    lay = lay.resize((w, h), Image.LANCZOS)
    if tilt:
        lay = lay.rotate(tilt, resample=Image.BICUBIC, expand=True)
    # drop shadow
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    sh.putalpha(lay.split()[3].point(lambda v: int(v * 0.55)))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    x, y = xy
    ax = {"l": 0, "m": 0.5, "r": 1}[anchor[0]]
    ay = {"t": 0, "m": 0.5, "b": 1}[anchor[1]]
    px0, py0 = int(x - lay.width * ax), int(y - lay.height * ay)
    img.alpha_composite(sh, (px0 + 4, py0 + 8))
    img.alpha_composite(lay, (px0, py0))
    return (px0, py0, px0 + lay.width, py0 + lay.height)


def sticker_chip(img, box, s, px, fill, fg, tilt=0.0):
    """a die-cut rounded sticker with Anton lettering inside (verb buttons: PATCH, BUY, CONFIRM, UNDO, LEAVE)."""
    x0, y0, x1, y1 = box
    w, h = int(x1 - x0), int(y1 - y0)
    pad = 16
    lay = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    rr(lay, (pad, pad, pad + w, pad + h), h * 0.32, fill=(252, 251, 249, 255), outline=(109, 105, 110, 255), ow=1, pad=3)
    rr(lay, (pad + 6, pad + 6, pad + w - 6, pad + h - 6), h * 0.22, fill=INKC + (255,))
    rr(lay, (pad + 9, pad + 9, pad + w - 9, pad + h - 9), h * 0.18, fill=fill + (255,))
    f = anton(px)
    ImageDraw.Draw(lay).text((pad + w / 2, pad + h / 2 + 1), s, font=f, fill=fg + (255,), anchor="mm")
    gm = Image.new("L", lay.size, 0)
    ImageDraw.Draw(gm).rectangle((0, 0, lay.width, pad + h * 0.45), fill=30)
    gm = ImageChops.multiply(gm, lay.split()[3])
    gl = Image.new("RGBA", lay.size, (255, 255, 255, 255))
    gl.putalpha(gm)
    lay.alpha_composite(gl)
    if tilt:
        lay = lay.rotate(tilt, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    sh.putalpha(lay.split()[3].point(lambda v: int(v * 0.5)))
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    img.alpha_composite(sh, (int(x0 - pad + 3), int(y0 - pad + 7)))
    img.alpha_composite(lay, (int(x0 - pad - (lay.width - w - 2 * pad) / 2), int(y0 - pad - (lay.height - h - 2 * pad) / 2)))


def holo_chip(img, box, s, px):
    """the LEAVE sticker: rainbow-foil plate, white lettering with an ink keyline (a still of the holo sheen)."""
    x0, y0, x1, y1 = box
    w, h = int(x1 - x0), int(y1 - y0)
    pad = 16
    lay = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    rr(lay, (pad, pad, pad + w, pad + h), h * 0.32, fill=(252, 251, 249, 255), outline=(109, 105, 110, 255), ow=1, pad=3)
    foil = Image.new("RGBA", (w - 12, h - 12))
    fd = ImageDraw.Draw(foil)
    stops = [(255, 80, 168), (255, 226, 0), (92, 225, 255), (160, 120, 255), (255, 80, 168)]
    for xx in range(foil.width):
        t = (xx / foil.width) * (len(stops) - 1)
        i = min(int(t), len(stops) - 2)
        fd.line((xx, 0, xx, foil.height), fill=mix(stops[i], stops[i + 1], t - i) + (255,))
    mask = Image.new("L", foil.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, foil.width - 1, foil.height - 1), radius=int(h * 0.22), fill=255)
    foil.putalpha(mask)
    lay.alpha_composite(foil, (pad + 6, pad + 6))
    f = anton(px)
    ImageDraw.Draw(lay).text((pad + w / 2, pad + h / 2 + 1), s, font=f, fill=(255, 255, 255, 255), anchor="mm", stroke_width=4, stroke_fill=INKC + (255,))
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    sh.putalpha(lay.split()[3].point(lambda v: int(v * 0.5)))
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    img.alpha_composite(sh, (int(x0 - pad + 3), int(y0 - pad + 7)))
    img.alpha_composite(lay, (int(x0 - pad), int(y0 - pad)))


# ---------------------------------------------------------------------------------------------------------------------
# small icons
# ---------------------------------------------------------------------------------------------------------------------
def heart(img, c, r, col):
    pts = []
    for i in range(60):
        t = math.pi * 2 * i / 60
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((c[0] + x * r / 17, c[1] - y * r / 17))
    poly_aa(img, pts, fill=col + (255,))


def cycles_icon(img, c, r, col):
    d = Doc(40, 40)
    d.line(arc(20, 20, 13, -50, 250, 24), col, 4.6)
    d.poly([(20 + 13 * math.cos(math.radians(250)) - 7, 20 + 13 * math.sin(math.radians(250)) - 2), (20 + 13 * math.cos(math.radians(250)) + 6, 20 + 13 * math.sin(math.radians(250)) - 5),
            (20 + 13 * math.cos(math.radians(250)) + 1, 20 + 13 * math.sin(math.radians(250)) + 7)], col)
    im = d.render(2 * r / 40.0, ss=4)
    img.alpha_composite(im, (int(c[0] - im.width / 2), int(c[1] - im.height / 2)))


def glyph(img, name, c, size, col=(246, 243, 232)):
    g = Image.open(GLYPHS + name + ".png").convert("RGBA").resize((size, size), Image.LANCZOS)
    a = g.split()[3]
    # dark rounded outline (0.075 x size) then the white glyph
    ol = a.filter(ImageFilter.MaxFilter(max(3, int(size * 0.075 * 2) | 1)))
    dk = Image.new("RGBA", g.size, (12, 10, 22, 255))
    dk.putalpha(ol)
    img.alpha_composite(dk, (int(c[0] - size / 2), int(c[1] - size / 2)))
    tint = Image.new("RGBA", g.size, col + (255,))
    tint.putalpha(a)
    img.alpha_composite(tint, (int(c[0] - size / 2), int(c[1] - size / 2)))


SLICE_GLYPH = {"Shim 8": "slice_proxy", "Shield 8": "placeholder_shield", "Hotfix 6": "slice_patch", "Overflow 12": "slice_virus",
               "Sandbox 8": "slice_sandbox", "Trojan 1": "slice_trojan", "Shield 5": "placeholder_shield", "Block 12": "picto_block",
               "Overflow 14": "slice_virus"}


def chip_glyph(img, c, s, col):
    """a firmware chip (square, pins) as a tiny mark."""
    x, y = c
    rr(img, (x - s * 0.45, y - s * 0.45, x + s * 0.45, y + s * 0.45), s * 0.12, fill=col + (255,), outline=INKC + (255,), ow=1.4)
    d = ImageDraw.Draw(img)
    for k in (-0.25, 0.0, 0.25):
        d.line((x + k * s, y - s * 0.62, x + k * s, y - s * 0.45), fill=col + (255,), width=2)
        d.line((x + k * s, y + s * 0.45, x + k * s, y + s * 0.62), fill=col + (255,), width=2)


def price_tag(img, box, s, ink=INKC):
    """a kraft price tag (notched left, a punched hole), the Cycles mark and the price in Anton."""
    x0, y0, x1, y1 = box
    h = y1 - y0
    pts = [(x0 + h * 0.42, y0), (x1, y0), (x1, y1), (x0 + h * 0.42, y1), (x0, y0 + h / 2)]
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(x + 3, y + 5) for x, y in pts], fill=(0, 0, 0, 120))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    poly_aa(img, pts, fill=KRAFT + (255,), outline=(120, 92, 56, 255), ow=1.5)
    d = ImageDraw.Draw(img)
    d.ellipse((x0 + h * 0.42 - 4, y0 + h / 2 - 4, x0 + h * 0.42 + 4, y0 + h / 2 + 4), fill=(60, 44, 30, 255))
    cycles_icon(img, (x0 + h * 0.42 + 22, y0 + h / 2), 11, ink)
    text(img, (x1 - 10, y0 + h / 2 + 1), s, anton(h * 0.56), ink + (255,), "rm")


def hp_bar(img, box, frac, col, segs=20):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    w = (x1 - x0) / segs
    for i in range(segs):
        on = (i + 1) / segs <= frac + 1e-6
        d.rectangle((x0 + i * w + 1, y0, x0 + (i + 1) * w - 2, y1), fill=(col + (255,)) if on else (40, 48, 70, 255))


def choice_row(img, box, num, name, accent, state="normal", right=None, gl=None, plate=(30, 24, 52), label_px=34, style="sticker"):
    """a choice sticker row (the event page's: white die-cut, a yellow number tab, a dark plate, Anton lettering).
    state: normal | picked | second | off."""
    x0, y0, x1, y1 = box
    h = y1 - y0
    a = 255 if state != "off" else 120
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    border = (252, 251, 249, a)
    if state in ("picked", "second"):
        glow(lay, lambda dd: dd.rounded_rectangle((x0 - 2, y0 - 2, x1 + 2, y1 + 2), radius=14, fill=255), accent, 12, 0.7)
    rr(lay, (x0, y0, x1, y1), 14, fill=border, outline=(109, 105, 110, a), ow=1, pad=3)
    pl = plate if state != "picked" else mix(plate, accent, 0.30)
    rr(lay, (x0 + 5, y0 + 5, x1 - 5, y1 - 5), 10, fill=INKC + (a,))
    rr(lay, (x0 + 8, y0 + 8, x1 - 8, y1 - 8), 8, fill=pl + (a,))
    tab = (x0 + 8, y0 + 8, x0 + 8 + h * 0.78, y1 - 8)
    tabc = YELLOW if state in ("normal", "picked") else (accent if state == "second" else (150, 150, 150))
    rr(lay, tab, 8, fill=tabc + (a,))
    ImageDraw.Draw(lay).text(((tab[0] + tab[2]) / 2, (tab[1] + tab[3]) / 2 + 1), str(num), font=anton(h * 0.58), fill=INKC + (a,), anchor="mm")
    img.alpha_composite(lay)
    cx = tab[2] + 16
    if gl:
        glyph(img, gl, (cx + h * 0.30, (y0 + y1) / 2), int(h * 0.62))
        cx += h * 0.72
    text(img, (cx, (y0 + y1) / 2 + 2), name.upper(), anton(label_px * h / 80 * 1.35 if False else label_px), (246, 243, 232, a), "lm")
    if right:
        right(img, (x1 - 16, (y0 + y1) / 2), a)
