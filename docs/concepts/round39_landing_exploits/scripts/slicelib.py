"""Round 5 / SCREENS & DATA: every slice is a tiny CRT running its program.

Pure Pillow + numpy. Each slice:
  1. draws its program's screen texture (a flat rectangle, y=0 at the outer rim),
  2. maps it onto the wedge in polar UV (x = arc length from the midline, y = rim
     distance), so text rows and scanlines bend into arcs (the CRT-curvature hint),
  3. adds barrel bulge, phosphor glow, scanlines, edge vignette, glass glint,
  4. sits in a per-slice bezel (rounded inner screen corners, hairline, power LED),
  5. gets the upright glyph + value block (white, dark outline) rotated with the slice
     over a darkened "read plate".
This mirrors the Godot shader 1:1 (see NOTES.md).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONTS = "C:/Windows/Fonts/"

R_OUT = 360.0
R_IN = 130.0
TICK_DEG = 12.0


# ----------------------------------------------------------------- fonts
_font_cache = {}


def font(name, px, variation=None):
    key = (name, int(px), variation)
    if key not in _font_cache:
        f = ImageFont.truetype(FONTS + name, max(4, int(px)))
        if variation:
            f.set_variation_by_name(variation)
        _font_cache[key] = f
    return _font_cache[key]


def f_num(px):
    return font("bahnschrift.ttf", px, b"Bold Condensed")


def f_ui(px, var=b"SemiBold"):
    return font("bahnschrift.ttf", px, var)


def f_mono(px, bold=True):
    return font("consolab.ttf" if bold else "consola.ttf", px)


# ----------------------------------------------------------------- programs
PROGRAMS = {
    #   name        slice type   colour            value
    "EXPLOIT": dict(kind="ATTACK", col=(255, 61, 168), val=6),
    "ZERO-DAY": dict(kind="CRITICAL", col=(255, 120, 215), val=12),
    "FIREWALL": dict(kind="DEFEND", col=(92, 225, 255), val=5),
    "SANDBOX": dict(kind="SHIELD", col=(70, 226, 205), val=8),
    "PROXY": dict(kind="EVADE", col=(123, 224, 123), val=4),
    "PATCH": dict(kind="HEAL", col=(170, 240, 110), val=3),
    "VIRUS": dict(kind="AFFLICT", col=(200, 90, 255), val=3),
    "TROJAN": dict(kind="DEPLOY", col=(176, 140, 255), val=2),
    "NULL": dict(kind="MISS", col=(106, 106, 106), val=None),
    # round 11: screen-content study only (Guy Fawkes-style mask backdrop, program to be decided)
    "MASKBG": dict(kind="TBD", col=(196, 204, 226), val=None),
}
ORDER = ["EXPLOIT", "ZERO-DAY", "FIREWALL", "SANDBOX", "PROXY", "PATCH", "VIRUS", "TROJAN", "NULL"]

MERIDIAN = (255, 138, 31)

# Round 6 corporation skins (materials borrowed from family D, shown inside C's screen frame)
CORPS = {
    "meridian": dict(name="MERIDIAN FREIGHT", col=(255, 140, 26), bezel=(0.17, 0.115, 0.075)),
    "solace": dict(name="SOLACE BIOSYSTEMS", col=(61, 255, 139), bezel=(0.20, 0.22, 0.22)),
    "halcyon": dict(name="HALCYON CIVIC", col=(140, 123, 255), bezel=(0.12, 0.11, 0.20)),
    "orbital": dict(name="ORBITAL COMMONS", col=(127, 168, 255), bezel=(0.13, 0.14, 0.17)),
    "rebel_cell": dict(name="REBEL_CELL", col=(232, 20, 30), bezel=(0.11, 0.04, 0.05)),
}
MERIDIAN_DIM = (110, 58, 14)


def c01(c, k=1.0):
    return np.array(c, dtype=np.float32) / 255.0 * k


# ----------------------------------------------------------------- glyphs (512 box masks)
def _poly_rot(pts, ang, cx=256, cy=256):
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]


def glyph_mask(name):
    S = 512
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    if name == "EXPLOIT":  # dagger, tilted
        L = Image.new("L", (S, S), 0)
        dl = ImageDraw.Draw(L)
        dl.polygon([(256, 20), (296, 110), (296, 330), (216, 330), (216, 110)], fill=255)
        dl.rectangle([140, 330, 372, 374], fill=255)
        dl.rectangle([232, 374, 280, 462], fill=255)
        dl.ellipse([224, 450, 288, 506], fill=255)
        dl.line([(256, 70), (256, 300)], fill=0, width=10)  # fuller groove
        m = L.rotate(-32, resample=Image.BICUBIC, center=(256, 270))
    elif name == "ZERO-DAY":  # 12-point burst
        pts = []
        for i in range(24):
            r = 240 if i % 2 == 0 else 112
            if i % 4 == 2:
                r = 190
            a = math.radians(i * 15 - 90)
            pts.append((256 + r * math.cos(a), 256 + r * math.sin(a)))
        d.polygon(pts, fill=255)
        d.ellipse([206, 206, 306, 306], fill=0)
        d.ellipse([232, 232, 280, 280], fill=255)
    elif name == "FIREWALL":  # shield with brick cut-outs
        d.polygon([(70, 60), (442, 60), (442, 250), (400, 360), (256, 480), (112, 360), (70, 250)], fill=255)
        for y in (150, 240, 330):
            d.line([(60, y), (452, y)], fill=0, width=18)
        for y0, y1, xs in ((60, 150, (256,)), (150, 240, (163, 349)), (240, 330, (256,)), (330, 480, (190, 322))):
            for x in xs:
                d.line([(x, y0), (x, y1)], fill=0, width=18)
    elif name == "SANDBOX":  # window-in-window
        d.rounded_rectangle([40, 60, 472, 452], radius=40, fill=255)
        d.rounded_rectangle([82, 140, 430, 412], radius=20, fill=0)
        for i, x in enumerate((90, 140, 190)):
            d.ellipse([x - 18, 82, x + 18, 118], fill=0)
        d.rounded_rectangle([156, 206, 356, 350], radius=14, fill=255)
        d.rectangle([186, 260, 326, 322], fill=0)
    elif name == "PROXY":  # double chevron
        for ox in (-90, 70):
            d.polygon([(110 + ox, 70), (210 + ox, 70), (370 + ox, 256), (210 + ox, 442), (110 + ox, 442), (270 + ox, 256)], fill=255)
    elif name == "PATCH":  # bandage
        L = Image.new("L", (S, S), 0)
        dl = ImageDraw.Draw(L)
        dl.rounded_rectangle([20, 176, 492, 336], radius=80, fill=255)
        dl.rectangle([186, 176, 326, 336], fill=0)
        dl.rectangle([200, 190, 312, 322], fill=255)
        for x in (226, 286):
            for y in (222, 290):
                dl.ellipse([x - 13, y - 13, x + 13, y + 13], fill=0)
        m = L.rotate(40, resample=Image.BICUBIC)
    elif name == "VIRUS":  # spiked capsid
        for i in range(8):
            a = math.radians(i * 45 + 22.5)
            x1, y1 = 256 + 200 * math.cos(a), 256 + 200 * math.sin(a)
            d.line([(256, 256), (x1, y1)], fill=255, width=34)
            d.ellipse([x1 - 36, y1 - 36, x1 + 36, y1 + 36], fill=255)
        d.ellipse([126, 126, 386, 386], fill=255)
        for (x, y, r) in ((215, 220, 30), (300, 250, 22), (240, 305, 18)):
            d.ellipse([x - r, y - r, x + r, y + r], fill=0)
    elif name == "TROJAN":  # gift box with bow
        d.rectangle([72, 236, 440, 476], fill=255)
        d.rectangle([44, 160, 468, 226], fill=255)
        d.rectangle([228, 160, 284, 476], fill=0)
        d.rectangle([242, 160, 270, 476], fill=255)
        d.ellipse([120, 44, 260, 160], fill=255)
        d.ellipse([252, 44, 392, 160], fill=255)
        d.ellipse([168, 82, 236, 140], fill=0)
        d.ellipse([276, 82, 344, 140], fill=0)
    elif name == "NULL":  # slashed zero
        d.ellipse([70, 70, 442, 442], fill=255)
        d.ellipse([132, 132, 380, 380], fill=0)
        d.line([(400, 60), (112, 452)], fill=255, width=60)
    else:
        m2 = glyph_mask_extra(name)
        if m2 is None:
            import glyphs10
            m2 = glyphs10.mask(name)
        if m2 is not None:
            m = m2
    return m


def _ngon(cx, cy, r, n, rot=0):
    return [(cx + r * math.cos(math.radians(rot + 360 * i / n)), cy + r * math.sin(math.radians(rot + 360 * i / n)))
            for i in range(n)]


def glyph_mask_extra(name):
    """Round 6 glyphs: corp special slices, inner-ring segments, class/corp emblems, drone."""
    S = 512
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    if name == "TARIFF":  # receipt with zig-zag tear and a coin
        pts = [(110, 40), (402, 40), (402, 430)]
        for i in range(8):
            x = 402 - (i + 0.5) * 36.5
            pts.append((x, 470 if i % 2 == 0 else 430))
        pts += [(110, 430)]
        d.polygon(pts, fill=255)
        for y in (110, 170, 230):
            d.rectangle([160, y, 350, y + 24], fill=0)
        d.ellipse([200, 280, 312, 392], fill=0)
        d.ellipse([222, 302, 290, 370], fill=255)
        d.rectangle([248, 290, 264, 382], fill=0)
    elif name == "CITATION":  # parking ticket with punch holes + "!"
        d.rounded_rectangle([90, 50, 422, 462], radius=26, fill=255)
        for y in (110, 190, 270, 350):
            d.ellipse([70, y, 110, y + 40], fill=0)
            d.ellipse([402, y, 442, y + 40], fill=0)
        d.rounded_rectangle([226, 110, 286, 320], radius=20, fill=0)
        d.ellipse([224, 352, 288, 416], fill=0)
    elif name == "FLARE":  # sun disc with separated rays
        d.ellipse([156, 156, 356, 356], fill=255)
        for i in range(10):
            a = math.radians(i * 36)
            p0 = (256 + 140 * math.cos(a), 256 + 140 * math.sin(a))
            p1 = (256 + 236 * math.cos(a), 256 + 236 * math.sin(a))
            d.line([p0, p1], fill=255, width=40)
        d.ellipse([206, 206, 306, 306], fill=0)
        d.ellipse([232, 232, 280, 280], fill=255)
    elif name == "DOSE":  # capsule pill, tilted
        L = Image.new("L", (S, S), 0)
        dl = ImageDraw.Draw(L)
        dl.rounded_rectangle([60, 176, 452, 336], radius=80, fill=255)
        dl.rectangle([252, 176, 264, 336], fill=0)
        dl.rounded_rectangle([276, 196, 432, 316], radius=60, fill=0)
        dl.ellipse([310, 230, 350, 270], fill=255)
        dl.ellipse([365, 255, 395, 285], fill=255)
        m = L.rotate(35, resample=Image.BICUBIC)
    elif name == "SEG_X2":
        f = font("bahnschrift.ttf", 360, b"Bold Condensed")
        d.text((256, 270), "x2", font=f, fill=255, anchor="mm")
    elif name == "SEG_PIERCE":  # arrow through a wall
        d.rectangle([236, 40, 276, 472], fill=255)
        d.rectangle([30, 230, 360, 282], fill=255)
        d.polygon([(330, 160), (482, 256), (330, 352)], fill=255)
        d.rectangle([220, 200, 292, 312], fill=0)
        d.rectangle([236, 200, 276, 312], fill=0)
        d.rectangle([200, 230, 312, 282], fill=255)
    elif name == "SEG_ECHO":  # source dot + two echo arcs
        d.ellipse([60, 196, 180, 316], fill=255)
        for r, w in ((150, 40), (250, 40)):
            d.arc([120 - r, 256 - r, 120 + r, 256 + r], -50, 50, fill=255, width=w)
    elif name == "SEG_CORRUPT":  # broken square + glitch blocks
        d.rectangle([80, 80, 400, 400], fill=255)
        d.rectangle([140, 140, 340, 340], fill=0)
        d.rectangle([60, 220, 260, 270], fill=0)
        d.rectangle([300, 300, 470, 360], fill=255)
        d.rectangle([40, 420, 160, 470], fill=255)
        d.rectangle([380, 40, 470, 110], fill=255)
    elif name == "SEG_ACCEL":  # triple chevron
        for ox in (-140, -20, 100):
            d.polygon([(110 + ox, 90), (180 + ox, 90), (290 + ox, 256), (180 + ox, 422), (110 + ox, 422), (220 + ox, 256)], fill=255)
    elif name == "SEG_ANCHOR":
        d.ellipse([206, 30, 306, 130], fill=255)
        d.ellipse([230, 54, 282, 106], fill=0)
        d.rectangle([236, 120, 276, 440], fill=255)
        d.rectangle([160, 170, 352, 206], fill=255)
        d.arc([80, 200, 432, 470], 20, 160, fill=255, width=40)
        d.polygon([(60, 330), (130, 320), (100, 390)], fill=255)
        d.polygon([(452, 330), (382, 320), (412, 390)], fill=255)
    elif name == "SEG_BLANK":
        d.rounded_rectangle([110, 226, 402, 286], radius=26, fill=255)
    elif name == "DRONE":  # quad-rotor
        for (x, y) in ((130, 130), (382, 130), (130, 382), (382, 382)):
            d.line([(256, 256), (x, y)], fill=255, width=44)
            d.ellipse([x - 82, y - 82, x + 82, y + 82], fill=255)
            d.ellipse([x - 56, y - 56, x + 56, y + 56], fill=0)
            d.ellipse([x - 18, y - 18, x + 18, y + 18], fill=255)
        d.rounded_rectangle([196, 196, 316, 316], radius=24, fill=255)
        d.ellipse([236, 236, 276, 276], fill=0)
    # ---- class marks
    elif name == "EM_BREAKER":  # crowbar + antenna spark
        d.line([(120, 440), (360, 100)], fill=255, width=56)
        d.arc([300, 40, 470, 210], 180, 330, fill=255, width=50)
        d.polygon([(80, 470), (110, 400), (170, 440)], fill=255)
    elif name == "EM_WRECKER":  # sledgehammer
        d.line([(150, 460), (300, 170)], fill=255, width=50)
        L = Image.new("L", (S, S), 0)
        ImageDraw.Draw(L).rounded_rectangle([170, 60, 450, 190], radius=18, fill=255)
        m.paste(255, (0, 0), L.rotate(-27, center=(310, 125)))
        d.rectangle([60, 300, 120, 330], fill=255)
        d.rectangle([40, 360, 110, 384], fill=255)
    elif name == "EM_GHOST":  # hood with mesh eyes
        d.pieslice([90, 50, 422, 382], 180, 360, fill=255)
        d.rectangle([90, 216, 422, 470], fill=255)
        for i in range(5):
            x = 90 + i * 83
            d.polygon([(x, 470), (x + 41, 420), (x + 83, 470)], fill=0)
        d.ellipse([170, 190, 236, 256], fill=0)
        d.ellipse([276, 190, 342, 256], fill=0)
    elif name == "EM_PHANTOM":  # mask with offset afterimage
        for off, f in ((40, 120), (0, 255)):
            L = Image.new("L", (S, S), 0)
            dl = ImageDraw.Draw(L)
            dl.ellipse([110 + off, 60, 402 + off, 452], fill=255)
            dl.polygon([(160 + off, 210), (240 + off, 200), (230 + off, 250)], fill=0)
            dl.polygon([(352 + off, 210), (272 + off, 200), (282 + off, 250)], fill=0)
            dl.rectangle([216 + off, 340, 296 + off, 356], fill=0)
            m.paste(f, (0, 0), L)
    elif name == "EM_RIGGER":  # goggles + cable
        for x in (150, 362):
            d.ellipse([x - 100, 140, x + 100, 340], fill=255)
            d.ellipse([x - 60, 180, x + 60, 300], fill=0)
        d.rectangle([240, 220, 272, 260], fill=255)
        d.arc([60, 250, 452, 500], 20, 160, fill=255, width=26)
    elif name == "EM_OVERCLOCKER":  # heat-sink crown
        d.rounded_rectangle([90, 300, 422, 440], radius=20, fill=255)
        for i in range(6):
            x = 110 + i * 56
            h = 200 if i in (2, 3) else 140
            d.rectangle([x, 300 - h, x + 30, 310], fill=255)
        d.ellipse([226, 340, 286, 400], fill=0)
    elif name == "EM_BOTNET":  # drone halo: centre + ring of dots
        d.ellipse([196, 196, 316, 316], fill=255)
        for i in range(8):
            a = math.radians(i * 45)
            x, y = 256 + 180 * math.cos(a), 256 + 180 * math.sin(a)
            d.ellipse([x - 34, y - 34, x + 34, y + 34], fill=255)
    elif name == "EM_HIVEMIND":  # linked hex nodes
        cs = [(256, 256)] + [(256 + 170 * math.cos(math.radians(a)), 256 + 170 * math.sin(math.radians(a))) for a in range(30, 390, 60)]
        for c in cs[1:]:
            d.line([cs[0], c], fill=255, width=26)
        for i in range(1, 7):
            d.line([cs[i], cs[1 + i % 6]], fill=255, width=26)
        for (x, y) in cs:
            d.polygon(_ngon(x, y, 52, 6, 30), fill=255)
    # ---- corp marks
    elif name == "EM_MERIDIAN":  # gantry crane hook + container
        d.rectangle([90, 60, 130, 460], fill=255)
        d.rectangle([90, 60, 420, 100], fill=255)
        d.line([(130, 160), (220, 70)], fill=255, width=30)
        d.rectangle([330, 100, 346, 230], fill=255)
        d.rectangle([270, 230, 420, 330], fill=255)
    elif name == "EM_SOLACE":  # double helix
        for k in range(2):
            pts = [(256 + 120 * math.sin(y / 70.0 + k * math.pi), y) for y in range(40, 480, 6)]
            d.line(pts, fill=255, width=34)
        for y in range(70, 470, 56):
            d.line([(256 + 120 * math.sin(y / 70.0), y), (256 - 120 * math.sin(y / 70.0), y)], fill=255, width=14)
    elif name == "EM_HALCYON":  # triangle under halo
        d.polygon([(256, 170), (440, 470), (72, 470)], fill=255)
        d.ellipse([136, 40, 376, 130], outline=255, width=26)
    elif name == "EM_ORBITAL":  # ringed planet
        d.ellipse([146, 146, 366, 366], fill=255)
        L = Image.new("L", (S, S), 0)
        ImageDraw.Draw(L).ellipse([20, 200, 492, 312], outline=255, width=30)
        m.paste(255, (0, 0), L.rotate(-20))
        d2 = ImageDraw.Draw(m)
        d2.ellipse([186, 186, 326, 326], fill=255)
    elif name == "EM_REBEL_CELL":  # inverted hexagon with core
        d.polygon(_ngon(256, 256, 230, 6, 90), fill=255)
        d.polygon(_ngon(256, 256, 165, 6, 90), fill=0)
        d.polygon(_ngon(256, 256, 80, 6, 90), fill=255)
    else:
        return None
    return m


_glyph_cache = {}


GLYPH_OVERRIDE = {}  # round 10: e.g. {"VIRUS": "VIAL", "PROXY": "MASK"} picks a rework option


def glyph_rgba(name, px, outline_px, fill=(255, 255, 255), edge=(12, 10, 22)):
    """White glyph with a dark rounded outline, px = box size."""
    name = GLYPH_OVERRIDE.get(name, name)
    key = (name, int(px), int(outline_px), fill, edge)
    if key in _glyph_cache:
        return _glyph_cache[key]
    pad = int(outline_px * 2 + 4)
    m = glyph_mask(name).resize((int(px), int(px)), Image.LANCZOS)
    big = Image.new("L", (int(px) + 2 * pad, int(px) + 2 * pad), 0)
    big.paste(m, (pad, pad))
    o = big.filter(ImageFilter.GaussianBlur(outline_px * 0.55)).point(lambda v: min(255, v * 7))
    out = Image.new("RGBA", big.size, edge + (0,))
    out.putalpha(o)
    white = Image.new("RGBA", big.size, fill + (255,))
    out.paste(white, (0, 0), big)
    _glyph_cache[key] = out
    return out


def number_rgba(text, px, stroke, fill=(255, 255, 255), edge=(12, 10, 22)):
    f = f_num(px)
    bb = f.getbbox(text, stroke_width=int(stroke))
    w, h = bb[2] - bb[0] + 4, bb[3] - bb[1] + 4
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((-bb[0] + 2, -bb[1] + 2), text, font=f, fill=fill, stroke_width=int(stroke), stroke_fill=edge)
    return im


def badge_rgba(text, px, ss, col=(255, 210, 90)):
    """Small rule chip (e.g. +1 RES, -1 RAM) under the value."""
    f = f_ui(px * ss, b"Bold Condensed")
    bb = f.getbbox(text)
    w, h = bb[2] - bb[0] + int(10 * ss), bb[3] - bb[1] + int(7 * ss)
    im = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([1, 1, w + 2, h + 2], radius=int(4 * ss), fill=(12, 10, 22, 235),
                        outline=col + (255,), width=max(1, int(1.6 * ss)))
    d.text((2 + int(5 * ss) - bb[0], 2 + int(3.5 * ss) - bb[1]), text, font=f, fill=col + (255,))
    return im


def icon_block(prog, value, span, ss, glyph_scale=1.0, number_scale=1.0, glyph=None, badge=None):
    """Upright block (outward = up). Returns RGBA and its size in ss px."""
    im = _icon_block(prog, value, span, ss, glyph_scale, number_scale, glyph)
    if badge:
        b = badge_rgba(badge, 11 * glyph_scale, ss)
        W = max(im.width, b.width)
        out = Image.new("RGBA", (W, im.height + b.height), (0, 0, 0, 0))
        out.alpha_composite(im, ((W - im.width) // 2, 0))
        out.alpha_composite(b, ((W - b.width) // 2, im.height - int(2 * ss)))
        return out
    return im


def _icon_block(prog, value, span, ss, glyph_scale=1.0, number_scale=1.0, glyph=None):
    rho_c = R_IN + 0.6 * (R_OUT - R_IN)
    chord = 2 * rho_c * math.sin(math.radians(span / 2))
    gs = min(0.38 * chord, 72.0) * glyph_scale
    if value is None:
        gs *= 1.3
    g = glyph_rgba(glyph or prog, gs * ss, max(2.5, gs * 0.075) * ss)
    if value is None:
        return g
    n = number_rgba(str(value), gs * 1.22 * ss * number_scale, max(2.5, gs * 0.075) * ss)
    wide = span >= 54
    gap = int(gs * 0.06 * ss)
    if wide:
        W = g.width + n.width + gap
        H = max(g.height, n.height)
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        im.alpha_composite(g, (0, (H - g.height) // 2))
        im.alpha_composite(n, (g.width + gap, (H - n.height) // 2))
    else:
        W = max(g.width, n.width)
        H = g.height + n.height + gap - int(gs * 0.18 * ss)
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        im.alpha_composite(g, ((W - g.width) // 2, 0))
        im.alpha_composite(n, ((W - n.width) // 2, H - n.height))
    return im


def shadowed(im, ss, k=0.55):
    a = im.split()[3].filter(ImageFilter.GaussianBlur(3 * ss))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * k)))
    pad = int(6 * ss)
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    out.alpha_composite(sh, (pad + int(1.5 * ss), pad + int(3 * ss)))
    out.alpha_composite(im, (pad, pad))
    return out


# ----------------------------------------------------------------- numpy helpers
def bilinear(tex, x, y):
    H, W, _ = tex.shape
    x = np.clip(x, 0, W - 1.001)
    y = np.clip(y, 0, H - 1.001)
    x0 = np.floor(x).astype(np.int32)
    y0 = np.floor(y).astype(np.int32)
    fx = (x - x0)[..., None]
    fy = (y - y0)[..., None]
    a = tex[y0, x0]
    b = tex[y0, x0 + 1]
    c = tex[y0 + 1, x0]
    d = tex[y0 + 1, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def round_min(a, b, r):
    """Rounded intersection of two inside-distances (positive inside)."""
    m = np.minimum(a, b)
    both = (a < r) & (b < r)
    rr = r - np.sqrt(np.maximum(r - a, 0) ** 2 + np.maximum(r - b, 0) ** 2)
    return np.where(both, rr, m)


def to_img(arr):
    return Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8))


# ----------------------------------------------------------------- slice render
class Ctx:
    """What a program's screen texture function receives."""

    def __init__(self, W, H, t, ss, span, r_out_s, col, theme, prog, seed):
        self.W, self.H, self.t, self.ss, self.span = W, H, t, ss, span
        self.r_out_s = r_out_s
        self.col = col
        self.theme = theme
        self.prog = prog
        self.seed = seed

    def halfw(self, y):
        """Visible half-width (texture px) at texture row y (approx)."""
        return (self.r_out_s - y) * math.radians(self.span / 2)


def render_slice(canvas, cx, cy, prog, a0, span, value, t, theme="player", ss=2,
                 opts=None, seed=0, glyph=None, badge=None, special=None):
    """Draw one program tile into canvas (H,W,4 float, premultiplied rgb + a)."""
    import programs  # local import keeps the module graph simple

    o = dict(glyph_scale=1.0, tex_gain=1.0, plate=0.62, number_scale=1.0, icons=True)
    if opts:
        o.update(opts)
    col = PROGRAMS[prog]["col"]
    Ro, Ri = R_OUT * ss, R_IN * ss
    gap = 1.6 * ss
    bw = 8.5 * ss
    mid = a0 + span / 2
    half = span / 2

    # bounding box of the wedge
    angs = np.radians(np.linspace(a0, a0 + span, 32))
    pts = [(cx + r * np.sin(a), cy - r * np.cos(a)) for r in (Ri, Ro) for a in angs]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1 = int(max(0, min(xs) - 2)), int(min(canvas.shape[1], max(xs) + 3))
    y0, y1 = int(max(0, min(ys) - 2)), int(min(canvas.shape[0], max(ys) + 3))
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
    rho = np.hypot(dx, dy)
    th = np.degrees(np.arctan2(dx, -dy)) % 360
    d = ((th - mid + 180) % 360) - 180

    e_side = rho * np.sin(np.radians(np.clip(half - np.abs(d), -90, 90))) - gap
    e_out = Ro - gap - rho
    e_in = rho - Ri - gap
    e_tile = round_min(round_min(e_side, e_out, 4 * ss), e_in, 4 * ss)
    a_tile = np.clip(e_tile, 0, 1)
    if a_tile.max() <= 0:
        return
    s_side = e_side - bw
    s_out = e_out - bw
    s_in = e_in - bw * 0.85
    e_scr = round_min(round_min(s_side, s_out, 11 * ss), s_in, 9 * ss)
    a_scr = np.clip(e_scr + 0.5, 0, 1)

    # ---- screen texture
    r_out_s = Ro - gap - bw
    r_in_s = Ri + gap + bw * 0.85
    W = int(r_out_s * math.radians(span) + 8 * ss)
    H = int(r_out_s - r_in_s + 4 * ss)
    ctx = Ctx(W, H, t, ss, span, r_out_s, col, theme, prog, seed)
    ctx.opts = o
    ctx.special = special
    tex_img = programs.texture(ctx)
    tex = np.asarray(tex_img, dtype=np.float32) / 255.0
    glow = np.asarray(tex_img.filter(ImageFilter.GaussianBlur(5 * ss)), dtype=np.float32) / 255.0
    glow2 = np.asarray(tex_img.filter(ImageFilter.GaussianBlur(14 * ss)), dtype=np.float32) / 255.0
    tex = tex * o["tex_gain"] + glow * 0.55 + glow2 * 0.35

    tx = W / 2 + rho * np.radians(d)
    ty = r_out_s - rho
    # barrel bulge around the screen centre
    nx = (tx - W / 2) / (W / 2)
    ny = (ty - H / 2) / (H / 2)
    f = 1 - 0.055 * (nx * nx + ny * ny)
    sx = W / 2 + (tx - W / 2) * f
    sy = H / 2 + (ty - H / 2) * f
    scr = bilinear(tex, sx, sy)
    # scanlines (rows of constant radius = arcs)
    sl = 0.70 + 0.30 * (0.5 + 0.5 * np.cos(2 * np.pi * ty / (3.0 * ss)))
    scr *= sl[..., None]
    # edge vignette inside the bezel
    vig = 0.35 + 0.65 * smooth(0, 26 * ss, e_scr)
    scr *= vig[..., None]
    # read plate under the glyph + value
    blk = None
    rc_f = o.get("rc", 0.6)
    if o["icons"] and o.get("upright"):
        # round 10: the glyph + value block stays upright (counter-rotates as the wheel spins),
        # so a 6 never reads as a 9; the read plate becomes a screen-space ellipse under it.
        blk = shadowed(icon_block(prog, value, span, ss, o["glyph_scale"], o["number_scale"], glyph, badge), ss)
        rc = (R_IN + rc_f * (R_OUT - R_IN)) * ss
        bcx = cx + rc * math.sin(math.radians(mid))
        bcy = cy - rc * math.cos(math.radians(mid))
        ax, ay = blk.width * 0.5 + 14 * ss, blk.height * 0.5 + 12 * ss
        q = ((xx + 0.5 - bcx) / ax) ** 2 + ((yy + 0.5 - bcy) / ay) ** 2
        plate = 1 - o["plate"] * np.exp(-q * 1.4)
        scr *= plate[..., None]
    elif o["icons"]:
        rho_c = (R_IN + 0.6 * (R_OUT - R_IN)) * ss
        lat = rho * np.radians(d)
        chord = 2 * rho_c * math.sin(math.radians(half))
        ax = max(min(chord * 0.42, 95 * ss), 30 * ss)
        ay = 78 * ss if span < 54 else 58 * ss
        q = (lat / ax) ** 2 + ((rho - rho_c) / ay) ** 2
        plate = 1 - o["plate"] * np.exp(-q * 1.6)
        scr *= plate[..., None]
    # glass glint (top-left of each screen)
    gl = np.exp(-((ny + 0.75) * 2.6) ** 2) * np.clip(0.6 - nx * 0.5, 0, 1) * 0.07
    scr += gl[..., None]

    # ---- bezel
    if theme == "player":
        base = np.array([0.085, 0.08, 0.11], np.float32)
        hair = c01(col)
    elif theme in CORPS:
        base = np.array(CORPS[theme]["bezel"], np.float32)
        hair = c01(col)  # type accent rim on the corp material
    else:
        base = np.array([0.15, 0.16, 0.18], np.float32)
        hair = c01(MERIDIAN)
    light = 0.85 + 0.3 * np.cos(np.radians(th - 315))  # key light top-left
    bez = base[None, None, :] * light[..., None]
    lip = np.exp(-(e_tile / (1.2 * ss)) ** 2) * 0.22  # outer lip catch-light
    bez = bez + lip[..., None]
    shadow = smooth(-5 * ss, 0, e_scr)  # inner bevel shadow toward the screen
    bez *= (1 - 0.6 * shadow)[..., None]
    hl = np.exp(-((e_scr + 1.3 * ss) / (0.9 * ss)) ** 2)  # hairline around the screen
    bez = bez + hl[..., None] * hair[None, None, :] * 1.1
    # power LED on the outer bezel
    led_r = Ro - gap - bw * 0.5
    led_lat = (half - min(4.0, half * 0.35)) * math.pi / 180 * led_r * 0.86
    ldx = rho * np.radians(d) - led_lat
    ldy = rho - led_r
    ld = np.hypot(ldx, ldy)
    led = np.clip(1.6 * ss - ld, 0, 1) + np.exp(-(ld / (3.5 * ss)) ** 2) * 0.5
    led_col = c01(col) if theme == "player" else c01(CORPS[theme]["col"] if theme in CORPS else MERIDIAN)
    bez = bez + led[..., None] * led_col[None, None, :] * 1.3

    rgb = scr * a_scr[..., None] + bez * (1 - a_scr[..., None])
    a = a_tile[..., None]
    region = canvas[y0:y1, x0:x1]
    region[..., :3] = region[..., :3] * (1 - a) + rgb * a
    region[..., 3:] = region[..., 3:] * (1 - a) + a

    # ---- glyph + value, rotated with the slice
    if o["icons"]:
        if blk is None:
            blk = shadowed(icon_block(prog, value, span, ss, o["glyph_scale"], o["number_scale"], glyph, badge), ss)
            blk = blk.rotate(-mid, resample=Image.BICUBIC, expand=True)
        rc = (R_IN + rc_f * (R_OUT - R_IN)) * ss
        px = cx + rc * math.sin(math.radians(mid)) - blk.width / 2
        py = cy - rc * math.cos(math.radians(mid)) - blk.height / 2
        if o.get("defer_icons"):  # round 13: caller pastes the block later (needle passes under it)
            return blk, px, py
        paste_rgba(canvas, blk, px, py)


def paste_rgba(canvas, im, px, py):
    px, py = int(round(px)), int(round(py))
    arr = np.asarray(im, dtype=np.float32) / 255.0
    h, w = arr.shape[:2]
    x0, y0 = max(0, px), max(0, py)
    x1, y1 = min(canvas.shape[1], px + w), min(canvas.shape[0], py + h)
    if x1 <= x0 or y1 <= y0:
        return
    src = arr[y0 - py:y1 - py, x0 - px:x1 - px]
    a = src[..., 3:]
    dst = canvas[y0:y1, x0:x1]
    dst[..., :3] = dst[..., :3] * (1 - a) + src[..., :3] * a
    dst[..., 3:] = dst[..., 3:] * (1 - a) + a


def bloom(img, ss=1, strength=0.55, thresh=0.55):
    """img: PIL RGB. Adds a soft additive glow of the bright parts."""
    arr = np.asarray(img, dtype=np.float32) / 255.0
    lum = arr.max(axis=2, keepdims=True)
    hi = arr * np.clip((lum - thresh) / (1 - thresh), 0, 1)
    hi_img = to_img(hi)
    b1 = np.asarray(hi_img.filter(ImageFilter.GaussianBlur(6 * ss)), np.float32) / 255
    b2 = np.asarray(hi_img.filter(ImageFilter.GaussianBlur(22 * ss)), np.float32) / 255
    out = arr + (b1 * 0.7 + b2 * 0.6) * strength
    return to_img(out)


def render_tile_image(prog, span, value, t, theme="player", ss=2, opts=None, scale=1.0, seed=0):
    """A single tile pointing up, cropped, as RGBA at master*scale."""
    pad = 8
    Ro = R_OUT * ss
    half = math.radians(span / 2)
    w = int(2 * Ro * math.sin(min(half, math.pi / 2)) + 2 * pad * ss)
    h = int(Ro - R_IN * ss * math.cos(half) + 2 * pad * ss)
    cx = w / 2
    cy = Ro + pad * ss
    canvas = np.zeros((h, w, 4), np.float32)
    render_slice(canvas, cx, cy, prog, -span / 2, span, value, t, theme, ss, opts, seed)
    rgb = canvas[..., :3]
    a = canvas[..., 3:]
    im = Image.fromarray((np.clip(np.concatenate([rgb, a], 2), 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")
    W2, H2 = int(w / ss * scale), int(h / ss * scale)
    return im.resize((W2, H2), Image.LANCZOS)
