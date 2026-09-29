"""RISO PUNK ZINE: Pillow print-shop helpers (halftone, spot inks, misregistration,
torn edges, die-cut stickers, grain). Pure Pillow, seeded, no numpy.

Imported by make_textures.py and post.py. Not run directly.
"""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
FONT_DIR = os.path.join(REPO, "assets", "fonts")

# Spot inks and stocks (sRGB). Roles are documented in DIRECTION.md.
INK = {
    "pink": (255, 72, 176),      # riso fluoro pink: the Cell, marker, attack
    "cyan": (0, 169, 224),       # riso aqua as printed on paper
    "glow_cyan": (92, 225, 255), # NET_CYAN as light
    "black": (26, 24, 28),       # riso black
    "acid": (212, 255, 0),       # CELL_ACID: focus stickers only
    "yellow": (242, 220, 122),   # NOTE_YELLOW
    "amber": (255, 176, 0),      # CRT_AMBER / NOTICED heat
    "harm": (255, 68, 51),       # HARM
    "gain": (123, 224, 123),     # GAIN
    "violet": (176, 77, 255),
    "orange": (255, 140, 26),    # Meridian corp
    "paper": (242, 238, 228),
    "paper_alt": (233, 228, 214),
    "kraft": (196, 170, 128),
    "night": (13, 16, 38),
    "glass": (5, 13, 28),
}


def font(name, size):
    files = {
        "marker": "PermanentMarker-Regular.ttf",
        "anton": "Anton-Regular.ttf",
        "mono": "ShareTechMono-Regular.ttf",
        "plex": "IBMPlexSansCondensed-Medium.ttf",
    }
    return ImageFont.truetype(os.path.join(FONT_DIR, files[name]), size)


def solid(size, color, alpha=255):
    return Image.new("RGBA", size, tuple(color) + (alpha,))


def halftone(gray, cell=8, angle=15.0, gain=1.0):
    """gray: L image, 255 = full ink. Returns an L dot mask (255 = ink)."""
    w, h = gray.size
    rot = gray.rotate(angle, resample=Image.BILINEAR, expand=True, fillcolor=0)
    rw, rh = rot.size
    gw, gh = max(1, rw // cell), max(1, rh // cell)
    small = rot.resize((gw, gh), Image.BOX)
    dots = Image.new("L", (gw * cell, gh * cell), 0)
    d = ImageDraw.Draw(dots)
    px = small.load()
    rmax = cell * 0.71
    for j in range(gh):
        cy = j * cell + cell * 0.5
        for i in range(gw):
            v = px[i, j]
            if v < 6:
                continue
            r = rmax * math.sqrt(min(1.0, v / 255.0 * gain))
            cx = i * cell + cell * 0.5
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    dots = dots.resize((rw, rh)) if dots.size != (rw, rh) else dots
    back = dots.rotate(-angle, resample=Image.BILINEAR, expand=True)
    bw, bh = back.size
    left, top = (bw - w) // 2, (bh - h) // 2
    return back.crop((left, top, left + w, top + h)).point(lambda v: 255 if v > 110 else 0)


def shift(mask, dx, dy):
    out = Image.new(mask.mode, mask.size, 0)
    out.paste(mask, (dx, dy))
    return out


def ink(base, mask, color, offset=(0, 0), opacity=1.0, mode="multiply"):
    """Lay a spot ink through mask onto an RGB/RGBA base. offset = misregistration."""
    if offset != (0, 0):
        mask = shift(mask, *offset)
    if opacity < 1.0:
        mask = mask.point(lambda v: int(v * opacity))
    rgb = base.convert("RGB")
    col = Image.new("RGB", base.size, color)
    if mode == "multiply":
        layer = ImageChops.multiply(rgb, col)
    elif mode == "screen":
        layer = ImageChops.screen(rgb, col)
    else:
        layer = col
    out = Image.composite(layer, rgb, mask)
    if base.mode == "RGBA":
        out.putalpha(base.getchannel("A"))
    return out


def grain(img, amount=18, seed=0, size_div=1):
    """Xerox grain: monochrome noise blended in (seeded via the effect's size trick)."""
    rng = random.Random(seed)
    w, h = img.size
    sw, sh = max(1, w // size_div), max(1, h // size_div)
    n = Image.frombytes("L", (sw, sh), rng.randbytes(sw * sh))
    if (sw, sh) != (w, h):
        n = n.resize((w, h), Image.BILINEAR)
    n = n.point(lambda v: 128 + int((v - 128) * amount / 128.0))
    rgb = img.convert("RGB")
    nrgb = Image.merge("RGB", (n, n, n))
    out = ImageChops.overlay(rgb, nrgb) if hasattr(ImageChops, "overlay") else rgb
    if img.mode == "RGBA":
        out.putalpha(img.getchannel("A"))
    return out


def jitter_poly(points, amp, rng, step=6):
    """Resample a closed polygon every `step` px and jitter it: scissor/torn edges."""
    out = []
    n = len(points)
    for k in range(n):
        x0, y0 = points[k]
        x1, y1 = points[(k + 1) % n]
        L = math.hypot(x1 - x0, y1 - y0)
        segs = max(1, int(L / step))
        for s in range(segs):
            t = s / segs
            out.append((x0 + (x1 - x0) * t + rng.uniform(-amp, amp),
                        y0 + (y1 - y0) * t + rng.uniform(-amp, amp)))
    return out


def torn_rect_mask(w, h, margin, amp, rng, rim=4):
    """Returns (outer_mask, inner_mask): the rim between them is the torn white fibre."""
    pts = [(margin, margin), (w - margin, margin), (w - margin, h - margin), (margin, h - margin)]
    outer = Image.new("L", (w, h), 0)
    ImageDraw.Draw(outer).polygon(jitter_poly(pts, amp, rng, 5), fill=255)
    inner = Image.new("L", (w, h), 0)
    pts2 = [(margin + rim, margin + rim), (w - margin - rim, margin + rim),
            (w - margin - rim, h - margin - rim), (margin + rim, h - margin - rim)]
    ImageDraw.Draw(inner).polygon(jitter_poly(pts2, amp * 1.3, rng, 4), fill=255)
    return outer, ImageChops.multiply(inner, outer)


def dilate(mask, px):
    m = mask
    while px > 0:
        k = 5 if px >= 2 else 3
        m = m.filter(ImageFilter.MaxFilter(k))
        px -= k // 2
    return m


def die_cut(art, border=14, gloss=True, seed=0, backing=(250, 250, 247)):
    """Vinyl sticker: white die-cut border around the art's alpha + glossy highlight."""
    rng = random.Random(seed)
    pad = border + 6
    w, h = art.size
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    a = Image.new("L", canvas.size, 0)
    a.paste(art.getchannel("A"), (pad, pad))
    cut = dilate(a, border).filter(ImageFilter.GaussianBlur(3)).point(lambda v: 255 if v > 90 else 0)
    base = Image.new("RGBA", canvas.size, backing + (0,))
    base.putalpha(cut)
    # faint grey keyline so white-on-paper still reads
    edge = ImageChops.subtract(cut, cut.filter(ImageFilter.MinFilter(3)))
    keyl = Image.new("RGBA", canvas.size, (120, 120, 130, 0))
    keyl.putalpha(edge.point(lambda v: int(v * 0.5)))
    base = Image.alpha_composite(base, keyl)
    base.alpha_composite(art, (pad, pad))
    if gloss:
        gl = Image.new("L", canvas.size, 0)
        gd = ImageDraw.Draw(gl)
        cw, ch = canvas.size
        x0 = rng.uniform(0.05, 0.35) * cw
        gd.polygon([(x0, 0), (x0 + cw * 0.18, 0), (x0 - ch * 0.35 + cw * 0.18, ch), (x0 - ch * 0.35, ch)], fill=70)
        gd.polygon([(x0 + cw * 0.24, 0), (x0 + cw * 0.28, 0), (x0 - ch * 0.35 + cw * 0.28, ch), (x0 - ch * 0.35 + cw * 0.24, ch)], fill=50)
        gl = ImageChops.multiply(gl.filter(ImageFilter.GaussianBlur(4)), cut)
        white = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
        white.putalpha(gl)
        base = Image.alpha_composite(base, white)
    return base


def paper(size, color=None, seed=0, fibres=True, amount=14):
    rng = random.Random(seed)
    color = color or INK["paper"]
    img = Image.new("RGB", size, color)
    if fibres:
        d = ImageDraw.Draw(img)
        w, h = size
        for _ in range(int(w * h / 900)):
            x, y = rng.uniform(0, w), rng.uniform(0, h)
            a = rng.uniform(0, math.pi)
            L = rng.uniform(3, 14)
            c = tuple(max(0, min(255, v + rng.randint(-14, 8))) for v in color)
            d.line((x, y, x + math.cos(a) * L, y + math.sin(a) * L), fill=c, width=1)
    return grain(img, amount, seed)


def text_center(draw, box, txt, fnt, fill):
    x0, y0, x1, y1 = box
    bb = draw.textbbox((0, 0), txt, font=fnt)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.text((x0 + (x1 - x0 - tw) / 2 - bb[0], y0 + (y1 - y0 - th) / 2 - bb[1]), txt, font=fnt, fill=fill)


def gradient(size, top, bottom, horizontal=False):
    w, h = size
    g = Image.new("L", (1, 256) if not horizontal else (256, 1))
    for i in range(256):
        v = int(top + (bottom - top) * i / 255)
        g.putpixel((0, i) if not horizontal else (i, 0), v)
    return g.resize(size, Image.BILINEAR)


def radial(size, inner=255, outer=0):
    w, h = size
    g = Image.new("L", (256, 256), 0)
    px = g.load()
    for j in range(256):
        for i in range(256):
            r = min(1.0, math.hypot(i - 127.5, j - 127.5) / 127.5)
            px[i, j] = int(inner + (outer - inner) * r)
    return g.resize(size, Image.BILINEAR)
