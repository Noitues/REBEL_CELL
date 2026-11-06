"""Round 10 glyphs (512 box, white = filled) for the VIRUS / PROXY rework.

Same flat, bold language as C's glyphs: one solid white silhouette with a few dark cut-outs,
so slicelib.glyph_rgba can give it the dark rounded outline.
VIRUS: VIAL (poison flask), SKULLDROP (drop with a skull face), BIOHAZ (trefoil).
PROXY: MASK (Guy Fawkes-style smiling mask), DODGE (solid arrow + hollow afterimage).
"""
import math
from PIL import Image, ImageDraw

S = 512


def _new():
    m = Image.new("L", (S, S), 0)
    return m, ImageDraw.Draw(m)


def vial():
    m, d = _new()
    # round-bottom flask: lip, neck, bulb
    d.rounded_rectangle([168, 34, 344, 92], radius=18, fill=255)
    d.rectangle([204, 84, 308, 210], fill=255)
    d.ellipse([86, 168, 426, 496], fill=255)
    # glass highlight gap between neck and lip
    d.rectangle([186, 92, 326, 104], fill=0)
    # liquid surface: a wavy cut across the bulb
    pts = []
    for i in range(41):
        x = 96 + i * 8
        pts.append((x, 268 + 16 * math.sin(i * 0.31)))
    d.line(pts, fill=0, width=22, joint="curve")
    # bubbles rising in the poison
    for (x, y, r) in ((196, 352, 34), (300, 318, 22), (262, 420, 26), (338, 398, 14)):
        d.ellipse([x - r, y - r, x + r, y + r], fill=0)

    return m


def skulldrop():
    m, d = _new()
    # teardrop: circle + tapered tip
    d.ellipse([86, 168, 426, 500], fill=255)
    d.polygon([(256, 14), (104, 268), (408, 268)], fill=255)
    # skull face cut-outs
    for ex in (192, 320):
        d.ellipse([ex - 50, 270, ex + 50, 362], fill=0)
    d.polygon([(256, 372), (230, 414), (282, 414)], fill=0)
    for tx in (204, 238, 274, 308):
        d.rectangle([tx - 11, 432, tx + 11, 486], fill=0)
    d.rectangle([190, 428, 322, 440], fill=0)
    return m


def biohaz():
    m, d = _new()
    c = (256, 270)
    for k in range(3):
        a = math.radians(-90 + k * 120)
        ox, oy = c[0] + 112 * math.cos(a), c[1] + 112 * math.sin(a)
        d.ellipse([ox - 124, oy - 124, ox + 124, oy + 124], fill=255)
    for k in range(3):
        a = math.radians(-90 + k * 120)
        ix, iy = c[0] + 160 * math.cos(a), c[1] + 160 * math.sin(a)
        d.ellipse([ix - 76, iy - 76, ix + 76, iy + 76], fill=0)
    d.ellipse([c[0] - 40, c[1] - 40, c[0] + 40, c[1] + 40], fill=0)
    for k in range(3):  # gaps through the centre ring
        a = math.radians(-90 + k * 120 + 60)
        d.line([c, (c[0] + 200 * math.cos(a), c[1] + 200 * math.sin(a))], fill=0, width=18)
    d.ellipse([c[0] - 92, c[1] - 92, c[0] + 92, c[1] + 92], outline=255, width=30)
    for k in range(3):
        a = math.radians(-90 + k * 120 + 60)
        d.line([(c[0] + 50 * math.cos(a), c[1] + 50 * math.sin(a)), (c[0] + 130 * math.cos(a), c[1] + 130 * math.sin(a))], fill=0, width=16)
    return m


def mask_guy():
    """Guy Fawkes-style mask: wide brow, pointed chin, upturned moustache, thin smile, goatee."""
    m, d = _new()
    d.ellipse([92, 18, 420, 372], fill=255)
    d.polygon([(100, 230), (412, 230), (392, 330), (322, 432), (256, 500), (190, 432), (120, 330)], fill=255)
    # eyebrows: high arches rising to the temples
    d.arc([118, 112, 246, 220], 195, 335, fill=0, width=20)
    d.arc([266, 112, 394, 220], 205, 345, fill=0, width=20)
    # eyes: narrow smiling slits
    d.polygon([(132, 214), (180, 192), (236, 208), (232, 230), (180, 226), (138, 234)], fill=0)
    d.polygon([(380, 214), (332, 192), (276, 208), (280, 230), (332, 226), (374, 234)], fill=0)
    # nose ridge
    d.line([(256, 208), (248, 288), (262, 296)], fill=0, width=12)
    # moustache: two sweeping horns curling up to the cheeks
    for s in (-1, 1):
        up = [(256, 306), (256 + s * 40, 302), (256 + s * 80, 296), (256 + s * 112, 278), (256 + s * 128, 250), (256 + s * 124, 226)]
        lo = [(256 + s * 106, 252), (256 + s * 100, 296), (256 + s * 72, 324), (256 + s * 36, 334), (256, 334)]
        d.polygon(up + lo, fill=0)
    # thin smile under the moustache
    d.arc([206, 318, 306, 378], 25, 155, fill=0, width=12)
    # goatee: a narrow spike down the chin
    d.polygon([(238, 384), (274, 384), (256, 466)], fill=0)
    return m


def dodge():
    """Solid arrow swerving up-right, with a hollow afterimage left behind on the old line."""
    m, d = _new()
    L = Image.new("L", (S, S), 0)
    dl = ImageDraw.Draw(L)
    arrow = [(70, 222), (300, 222), (300, 150), (470, 256), (300, 362), (300, 290), (70, 290)]
    dl.polygon(arrow, fill=255)
    solid = L.rotate(28, resample=Image.BICUBIC, center=(256, 256), translate=(18, -64))
    G = Image.new("L", (S, S), 0)
    dg = ImageDraw.Draw(G)
    dg.line(arrow + [arrow[0]], fill=255, width=34, joint="curve")
    ghost = G.rotate(0, translate=(-28, 90))
    m.paste(255, (0, 0), ghost)
    # gap ring around the solid arrow so the two never merge
    from PIL import ImageFilter
    halo = solid.filter(ImageFilter.MaxFilter(25))
    m.paste(0, (0, 0), halo)
    m.paste(255, (0, 0), solid)
    return m


MASKS = {"VIAL": vial, "SKULLDROP": skulldrop, "BIOHAZ": biohaz, "MASK": mask_guy, "DODGE": dodge}


def mask(name):
    f = MASKS.get(name)
    return f() if f else None

