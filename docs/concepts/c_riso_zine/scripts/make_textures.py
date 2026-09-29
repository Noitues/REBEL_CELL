"""RISO PUNK ZINE: print every texture the Blender scenes use (seeded, deterministic).

Usage: python make_textures.py <out_dir>
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from riso_print import (INK, die_cut, dilate, font, gradient, grain, halftone, ink,
                        jitter_poly, paper, radial, shift, text_center, torn_rect_mask)

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "_tex")
os.makedirs(OUT, exist_ok=True)


def save(img, name):
    img.save(os.path.join(OUT, name + ".png"))


def lighten(c, k):
    return tuple(max(0, min(255, int(v + k))) for v in c)


# ----------------------------------------------------------------------------- city
def skyline(name, seed, depth, w=2400, h=820, tall=(0.35, 0.95), sign_p=0.25, win_p=0.33):
    """A cut-paper skyline card. depth 0 = far (pale, blue), 3 = near (dark)."""
    rng = random.Random(seed)
    stock = [(58, 70, 132), (38, 48, 102), (24, 30, 70), (14, 16, 40)][depth]
    sil = Image.new("L", (w, h), 0)
    sd = ImageDraw.Draw(sil)
    col = Image.new("RGB", (w, h), stock)
    em = Image.new("RGB", (w, h), (0, 0, 0))
    ed = ImageDraw.Draw(em)
    blds = []
    x = -30
    while x < w:
        bw = rng.randint(90, 250)
        bh = int(h * rng.uniform(*tall))
        top = h - bh
        pts = [(x, h), (x, top), (x + bw, top), (x + bw, h)]
        kind = rng.random()
        if kind < 0.35:
            inset = bw * rng.uniform(0.15, 0.3)
            up = rng.randint(40, 120)
            pts = [(x, h), (x, top), (x + inset, top), (x + inset, top - up),
                   (x + bw - inset, top - up), (x + bw - inset, top), (x + bw, top), (x + bw, h)]
            top -= up
        elif kind < 0.5:
            pts = [(x, h), (x, top + 30), (x + bw * 0.5, top - 20), (x + bw, top + 30), (x + bw, h)]
        sd.polygon(jitter_poly(pts, 1.1, rng, 7), fill=255)
        if rng.random() < 0.3:
            ax = x + bw * rng.uniform(0.3, 0.7)
            sd.line((ax, top, ax, top - rng.randint(30, 110)), fill=255, width=4)
            ed.ellipse((ax - 4, top - 118, ax + 4, top - 110), fill=INK["harm"])
        blds.append((x, top, bw, bh))
        x += bw + rng.randint(-24, 10)
    # printed shading: black halftone rising from the street
    shade = gradient((w, h), 20, 210)
    col = ink(col, ImageChops.multiply(halftone(shade, 7, 45), sil), INK["black"], opacity=0.8)
    # rim light printed in cyan / pink on building edges (screen ink)
    rim = Image.new("L", (w, h), 0)
    rimp = Image.new("L", (w, h), 0)
    rd, rpd = ImageDraw.Draw(rim), ImageDraw.Draw(rimp)
    for (bx, top, bw, bh) in blds:
        rd.rectangle((bx + bw - 16, top, bx + bw, h), fill=150)
        if rng.random() < 0.35:
            rpd.rectangle((bx, top, bx + 12, h), fill=140)
    col = ink(col, ImageChops.multiply(halftone(rim, 6, 15), sil), INK["cyan"], (3, 2), 0.55, "screen")
    col = ink(col, ImageChops.multiply(halftone(rimp, 6, 75), sil), INK["pink"], (-2, 1), 0.5, "screen")
    # windows
    cd = ImageDraw.Draw(col)
    palette = [INK["glow_cyan"], INK["pink"], (255, 214, 140), INK["acid"], (255, 214, 140)]
    ws = [(5, 7, 12, 16), (6, 9, 14, 19), (7, 10, 16, 21), (8, 12, 18, 24)][depth]
    for (bx, top, bw, bh) in blds:
        wc = rng.choice(palette)
        for yy in range(int(top) + 24, h - 30, ws[3]):
            for xx in range(int(bx) + 14, int(bx + bw) - 18, ws[2]):
                if rng.random() < win_p:
                    c = wc if rng.random() < 0.8 else rng.choice(palette)
                    cd.rectangle((xx, yy, xx + ws[0], yy + ws[1]), fill=lighten(c, -40))
                    ed.rectangle((xx + 2, yy + 1, xx + 2 + ws[0], yy + 1 + ws[1]), fill=c)
                else:
                    cd.rectangle((xx, yy, xx + ws[0], yy + ws[1]), fill=lighten(stock, -10))
        if rng.random() < sign_p and bw > 110:
            sc = rng.choice([INK["pink"], INK["glow_cyan"], INK["violet"], INK["amber"]])
            sx = bx + rng.uniform(10, bw - 50)
            sy = top + rng.uniform(40, 140)
            sh_ = rng.randint(140, 300)
            cd.rectangle((sx, sy, sx + 34, sy + sh_), fill=(10, 10, 16))
            ed.rectangle((sx, sy, sx + 34, sy + sh_), outline=sc, width=3)
            for k in range(int(sy) + 12, int(sy + sh_) - 14, 26):
                ed.rectangle((sx + 9, k, sx + 25, k + rng.randint(8, 18)), fill=sc)
    # scissor-cut rim: a thin lighter edge of card core
    cut = dilate(sil, 3)
    edge = ImageChops.subtract(cut, sil)
    col = Image.composite(Image.new("RGB", (w, h), lighten(stock, 55)), col, edge)
    col = grain(col, 26, seed)
    col.putalpha(cut)
    em = ImageChops.multiply(em, Image.merge("RGB", (cut, cut, cut)))
    save(col, name)
    save(em, name + "_em")


def hq_tower():
    w, h = 700, 1900
    rng = random.Random(77)
    sil = Image.new("L", (w, h), 0)
    sd = ImageDraw.Draw(sil)
    pts = [(20, h), (20, 1400), (80, 1400), (80, 900), (140, 900), (140, 560), (200, 560),
           (200, 360), (300, 300), (340, 60), (360, 60), (400, 300), (500, 360), (500, 560),
           (560, 560), (560, 900), (620, 900), (620, 1400), (680, 1400), (680, h)]
    sd.polygon(jitter_poly(pts, 1.0, rng, 7), fill=255)
    stock = (20, 22, 48)
    col = Image.new("RGB", (w, h), stock)
    col = ink(col, ImageChops.multiply(halftone(gradient((w, h), 0, 220), 7, 45), sil), INK["black"], opacity=0.8)
    rim = Image.new("L", (w, h), 0)
    rd = ImageDraw.Draw(rim)
    for (a, b, c) in [(620, 900, 1400), (560, 560, 900), (500, 360, 560), (680, 1400, h)]:
        rd.rectangle((a - 22, b, a, c), fill=170)
    col = ink(col, ImageChops.multiply(halftone(rim, 6, 15), sil), INK["pink"], (3, 1), 0.7, "screen")
    em = Image.new("RGB", (w, h), 0)
    ed, cd = ImageDraw.Draw(em), ImageDraw.Draw(col)
    for (x0, x1, y0, y1) in [(40, 660, 1420, h - 40), (100, 600, 920, 1380), (160, 540, 580, 880), (220, 480, 380, 540)]:
        for yy in range(y0, y1, 22):
            for xx in range(x0, x1, 18):
                if rng.random() < 0.3:
                    c = INK["acid"] if rng.random() < 0.7 else INK["pink"]
                    cd.rectangle((xx, yy, xx + 8, yy + 11), fill=lighten(c, -60))
                    ed.rectangle((xx + 2, yy + 1, xx + 10, yy + 12), fill=c)
    # the Cell mark: an inverted hexagon, sprayed + neon outlined
    cx, cy, r = 350, 700, 120
    hexp = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(30, 390, 60)]
    cd.polygon(hexp, fill=(8, 8, 14))
    ed.line(hexp + [hexp[0]], fill=INK["pink"], width=10)
    tri = [(cx - 60, cy - 40), (cx + 60, cy - 40), (cx, cy + 62)]
    ed.line(tri + [tri[0]], fill=INK["pink"], width=8)
    ed.ellipse((cx - 12, cy - 22, cx + 12, cy + 2), fill=INK["acid"])
    ed.ellipse((344, 52, 356, 64), fill=INK["harm"])
    cut = dilate(sil, 3)
    col = Image.composite(Image.new("RGB", (w, h), lighten(stock, 60)), col, ImageChops.subtract(cut, sil))
    col = grain(col, 26, 77)
    col.putalpha(cut)
    save(col, "hq")
    save(ImageChops.multiply(em, Image.merge("RGB", (cut, cut, cut))), "hq_em")


def sky():
    w, h = 3200, 1500
    col = Image.new("RGB", (w, h), INK["night"])
    glow = gradient((w, h), 0, 230)
    col = ink(col, halftone(glow.point(lambda v: int(v * 0.8)), 10, 15), INK["pink"], (0, 0), 0.55, "screen")
    col = ink(col, halftone(gradient((w, h), 170, 0), 12, 75), INK["cyan"], (4, 3), 0.25, "screen")
    rng = random.Random(5)
    d = ImageDraw.Draw(col)
    for _ in range(900):  # xerox specks
        x, y = rng.uniform(0, w), rng.uniform(0, h * 0.7)
        s = rng.choice([1, 1, 2, 3])
        d.ellipse((x, y, x + s, y + s), fill=(200, 200, 230))
    save(grain(col, 30, 5), "sky")


def highway(name, seed, w=3000, h=90):
    rng = random.Random(seed)
    col = Image.new("RGB", (w, h), (34, 36, 58))
    d = ImageDraw.Draw(col)
    d.rectangle((0, 0, w, 10), fill=(90, 96, 140))
    for x in range(0, w, 40):
        d.rectangle((x, 12, x + 4, 26), fill=(70, 76, 120))
    d.rectangle((0, h - 12, w, h), fill=(18, 18, 30))
    col = ink(col, halftone(Image.new("L", (w, h), 90), 6, 45), INK["cyan"], (2, 1), 0.35, "screen")
    em = Image.new("RGB", (w, h), 0)
    ed = ImageDraw.Draw(em)
    for lane, c in [(40, (255, 245, 230)), (58, INK["harm"]), (72, INK["pink"])]:
        x = rng.uniform(0, 60)
        while x < w:
            L = rng.uniform(30, 140)
            ed.line((x, lane, x + L, lane), fill=c, width=4)
            ed.ellipse((x + L - 4, lane - 4, x + L + 4, lane + 4), fill=c)
            x += L + rng.uniform(40, 220)
    col = grain(col, 20, seed)
    save(col, name)
    save(em, name + "_em")


def vehicle(name, kind, seed):
    rng = random.Random(seed)
    if kind == "car":
        w, h = 180, 70
        poly = [(6, 60), (6, 38), (40, 34), (62, 12), (120, 12), (146, 34), (174, 38), (174, 60)]
    elif kind == "flyer":
        w, h = 260, 110
        poly = [(10, 60), (40, 40), (90, 20), (170, 20), (220, 44), (250, 60), (230, 78), (30, 78)]
    elif kind == "heli":
        w, h = 520, 240
        poly = [(60, 120), (100, 80), (220, 70), (300, 80), (330, 120), (480, 112), (500, 90), (512, 96),
                (505, 140), (330, 146), (280, 170), (120, 170), (70, 150)]
    else:  # drone
        w, h = 200, 110
        poly = [(20, 40), (60, 40), (70, 55), (130, 55), (140, 40), (180, 40), (180, 50), (140, 50),
                (132, 75), (68, 75), (60, 50), (20, 50)]
    sil = Image.new("L", (w, h), 0)
    sd = ImageDraw.Draw(sil)
    sd.polygon(jitter_poly(poly, 0.8, rng, 6), fill=255)
    if kind == "heli":
        sd.rectangle((40, 50, 470, 58), fill=255)
        sd.rectangle((196, 56, 206, 74), fill=255)
        sd.rectangle((130, 170, 136, 196), fill=255)
        sd.rectangle((250, 170, 256, 196), fill=255)
        sd.rectangle((100, 194, 290, 200), fill=255)
    if kind == "drone":
        sd.rectangle((10, 30, 70, 36), fill=255)
        sd.rectangle((130, 30, 190, 36), fill=255)
    col = Image.new("RGB", (w, h), (18, 18, 28))
    col = ink(col, ImageChops.multiply(halftone(gradient((w, h), 0, 200), 5, 45), sil), INK["cyan"], (2, 1), 0.4, "screen")
    em = Image.new("RGB", (w, h), 0)
    ed = ImageDraw.Draw(em)
    if kind == "car":
        ed.rectangle((166, 42, 176, 50), fill=(255, 250, 235))
        ed.rectangle((4, 42, 14, 50), fill=INK["harm"])
    elif kind == "flyer":
        ed.rectangle((40, 76, 220, 82), fill=INK["glow_cyan"])
        ed.rectangle((236, 56, 250, 64), fill=(255, 250, 235))
        ed.rectangle((96, 26, 160, 38), fill=INK["pink"])
    elif kind == "heli":
        ed.ellipse((80, 140, 104, 164), fill=(255, 255, 240))
        ed.ellipse((496, 92, 508, 104), fill=INK["harm"])
        ed.ellipse((310, 124, 322, 136), fill=(80, 120, 255))
        ed.rectangle((120, 90, 200, 110), fill=(255, 200, 120))
    else:
        ed.ellipse((90, 58, 110, 72), fill=INK["harm"])
        ed.ellipse((20, 44, 28, 52), fill=(80, 120, 255))
        ed.ellipse((172, 44, 180, 52), fill=INK["harm"])
    cut = dilate(sil, 2)
    col = Image.composite(Image.new("RGB", (w, h), (80, 84, 120)), col, ImageChops.subtract(cut, sil))
    col.putalpha(cut)
    save(col, name)
    save(em, name + "_em")


def holo(name, color, seed, w=640, h=360):
    rng = random.Random(seed)
    img = Image.new("RGBA", (w, h), color + (70,))
    d = ImageDraw.Draw(img)
    em = Image.new("RGB", (w, h), tuple(int(v * 0.25) for v in color))
    ed = ImageDraw.Draw(em)
    # a big logo blob
    cx, cy = rng.uniform(110, 200), h / 2
    r = rng.uniform(70, 110)
    shape = rng.choice(["circle", "tri", "hex"])
    if shape == "circle":
        ed.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=14)
        ed.ellipse((cx - r * 0.4, cy - r * 0.4, cx + r * 0.4, cy + r * 0.4), fill=color)
    elif shape == "tri":
        ed.polygon([(cx, cy - r), (cx + r, cy + r * 0.8), (cx - r, cy + r * 0.8)], outline=color, width=14)
    else:
        pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]
        ed.polygon(pts, outline=color, width=14)
    # illegible glyph text
    x0 = 260
    for row in range(5):
        y = 70 + row * 46 + (row == 0) * -10
        x = x0
        gh = 30 if row == 0 else 18
        while x < w - 40:
            gw = rng.randint(8, 26) if row else rng.randint(20, 40)
            if rng.random() < 0.85:
                ed.rectangle((x, y, x + gw, y + gh), fill=color)
                if rng.random() < 0.5:
                    ed.rectangle((x + 3, y + 4, x + gw - 3, y + gh - 4), fill=(0, 0, 0))
            x += gw + rng.randint(4, 14) + (rng.random() < 0.15) * 20
    ed.rectangle((4, 4, w - 5, h - 5), outline=color, width=4)
    for y in range(0, h, 4):  # scanlines
        ed.line((0, y, w, y), fill=(0, 0, 0))
    lum = em.convert("L").point(lambda v: min(255, 70 + v))
    img.putalpha(lum)
    rgb = Image.composite(em, Image.new("RGB", (w, h), color), em.convert("L").point(lambda v: 255 if v > 60 else 0))
    rgb.putalpha(lum)
    save(rgb, name)
    save(em, name + "_em")


def fog(name, seed, blur, dotted, w=900, h=420, tint=(200, 205, 255)):
    rng = random.Random(seed)
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    for _ in range(14):
        cx, cy = rng.uniform(w * 0.2, w * 0.8), rng.uniform(h * 0.35, h * 0.65)
        rx, ry = rng.uniform(80, 220), rng.uniform(40, 110)
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(blur))
    if dotted:
        m = ImageChops.multiply(halftone(m, 9, 30), m.point(lambda v: 255 if v > 20 else 0))
        m = m.filter(ImageFilter.GaussianBlur(max(0.6, blur * 0.12)))
    img = Image.new("RGBA", (w, h), tint + (0,))
    img.putalpha(m.point(lambda v: int(v * 0.6)))
    save(img, name)


def ground_map():
    w, h = 2600, 1500
    col = Image.new("RGB", (w, h), (16, 20, 48))
    rng = random.Random(9)
    streets = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(streets)
    for x in range(-40, w, 190):
        d.line((x + rng.uniform(-6, 6), 0, x + rng.uniform(-6, 6), h), fill=160, width=rng.choice([10, 14, 26]))
    for y in range(-20, h, 170):
        d.line((0, y + rng.uniform(-6, 6), w, y + rng.uniform(-6, 6)), fill=160, width=rng.choice([10, 14, 26]))
    col = ink(col, halftone(streets, 6, 15), INK["cyan"], (3, 2), 0.35, "screen")
    blocks = ImageChops.invert(streets.point(lambda v: 255 if v > 10 else 0))
    col = ink(col, halftone(blocks.point(lambda v: int(v * 0.5)), 8, 45), INK["black"], (0, 0), 0.6)
    # claimed turf: acid hatch;  Meridian: orange 45deg container stripes
    hat = Image.new("L", (w, h), 0)
    hd = ImageDraw.Draw(hat)
    for k in range(-h, w, 26):
        hd.line((k, h, k + h, 0), fill=255, width=6)
    region = Image.new("L", (w, h), 0)
    ImageDraw.Draw(region).polygon(jitter_poly([(120, 700), (1000, 640), (1080, 1400), (160, 1440)], 8, rng, 20), fill=150)
    col = ink(col, ImageChops.multiply(hat, region), INK["acid"], (2, 0), 0.35, "screen")
    region2 = Image.new("L", (w, h), 0)
    ImageDraw.Draw(region2).polygon(jitter_poly([(1700, 600), (2500, 560), (2540, 1300), (1760, 1380)], 8, rng, 20), fill=140)
    col = ink(col, ImageChops.multiply(ImageChops.invert(hat).point(lambda v: 0 if v < 128 else 255), region2), INK["orange"], (-2, 1), 0.25, "screen")
    save(grain(col, 28, 9), "groundmap")


# ----------------------------------------------------------------------------- combat
GLYPH = {}


def glyph(d, kind, cx, cy, s, fill):
    if kind in ("atk",):
        d.polygon([(cx, cy - s), (cx + s * 0.35, cy + s * 0.5), (cx, cy + s * 0.3), (cx - s * 0.35, cy + s * 0.5)], fill=fill)
    elif kind == "def":
        d.polygon([(cx - s * 0.6, cy - s * 0.7), (cx + s * 0.6, cy - s * 0.7), (cx + s * 0.6, cy), (cx, cy + s * 0.8), (cx - s * 0.6, cy)], fill=fill)
    elif kind == "crit":
        pts = []
        for k in range(16):
            r = s if k % 2 == 0 else s * 0.42
            a = math.pi * 2 * k / 16
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d.polygon(pts, fill=fill)
    elif kind == "evd":
        for o in (-0.35, 0.25):
            d.line([(cx - s * 0.4 + o * s, cy - s * 0.6), (cx + s * 0.2 + o * s, cy), (cx - s * 0.4 + o * s, cy + s * 0.6)], fill=fill, width=int(s * 0.22))
    elif kind == "aff":
        d.ellipse((cx - s * 0.5, cy - s * 0.1, cx + s * 0.5, cy + s * 0.8), fill=fill)
        d.polygon([(cx, cy - s * 0.9), (cx + s * 0.45, cy + s * 0.2), (cx - s * 0.45, cy + s * 0.2)], fill=fill)
    elif kind == "miss":
        d.line((cx - s * 0.5, cy - s * 0.5, cx + s * 0.5, cy + s * 0.5), fill=fill, width=int(s * 0.2))
        d.line((cx - s * 0.5, cy + s * 0.5, cx + s * 0.5, cy - s * 0.5), fill=fill, width=int(s * 0.2))


SLICE_COL = {"atk": INK["pink"], "crit": INK["pink"], "def": INK["cyan"], "evd": (123, 224, 123),
             "aff": (200, 90, 255), "miss": (110, 110, 110)}


def spinner_slices(name, slices, seed, size=1024, r0=0.60, r1=0.96):
    rng = random.Random(seed)
    S = size
    c = S / 2
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    tick = 360.0 / 30
    t = 0
    for (n, kind, val) in slices:
        a0, a1 = -90 + t * tick, -90 + (t + n) * tick
        t += n
        m = Image.new("L", (S, S), 0)
        md = ImageDraw.Draw(m)
        md.pieslice((c - c * r1, c - c * r1, c + c * r1, c + c * r1), a0 + 0.9, a1 - 0.9, fill=255)
        md.ellipse((c - c * r0, c - c * r0, c + c * r0, c + c * r0), fill=0)
        base = SLICE_COL[kind]
        piece = Image.new("RGB", (S, S), lighten(base, 10))
        # riso shading: black halftone toward the inner edge, self-misregistered
        piece = ink(piece, halftone(radial((S, S), 255, 0).point(lambda v: max(0, v - 120) * 2), 9, 45), INK["black"], (0, 0), 0.35)
        if kind == "miss":
            piece = ink(piece, halftone(Image.new("L", (S, S), 110), 8, 15), INK["black"], (0, 0), 0.6)
        pd = ImageDraw.Draw(piece)
        am = math.radians((a0 + a1) / 2)
        rg = c * (r0 + r1) / 2
        gx, gy = c + math.cos(am) * rg * 1.04, c + math.sin(am) * rg * 1.04
        glyph(pd, kind, gx + 3, gy + 2, 34, INK["black"])  # misregistered key
        glyph(pd, kind, gx, gy, 34, (255, 255, 255) if kind != "miss" else (200, 200, 200))
        if val:
            fx = c + math.cos(am) * c * (r0 + 0.06)
            fy = c + math.sin(am) * c * (r0 + 0.06)
            text_center(pd, (fx - 40, fy - 30, fx + 40, fy + 30), str(val), font("anton", 44), INK["black"])
        piece = grain(piece, 22, seed + t)
        pr = piece.convert("RGBA")
        pr.putalpha(m)
        img = Image.alpha_composite(img, pr)
    save(img, name)
    return img


def spinner_bezel(name, style, seed, size=1024, r0=0.80, r1=1.0):
    rng = random.Random(seed)
    S, c = size, size / 2
    m = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(m)
    md.ellipse((1, 1, S - 2, S - 2), fill=255)
    md.ellipse((c - c * r0, c - c * r0, c + c * r0, c + c * r0), fill=0)
    base = Image.new("RGB", (S, S), (30, 30, 38))
    d = ImageDraw.Draw(base)
    if style == "meridian":
        st = Image.new("L", (S, S), 0)
        sd = ImageDraw.Draw(st)
        for k in range(-S, S * 2, 44):
            sd.line((k, 0, k - S, S), fill=255, width=18)
        base = ink(base, st, INK["orange"], (0, 0), 0.9, "normal")
        base = ink(base, halftone(Image.new("L", (S, S), 90), 7, 45), INK["black"], (2, 2), 0.7)
    else:
        base = ink(base, halftone(radial((S, S), 40, 200), 7, 15), INK["pink"], (3, 1), 0.35, "screen")
        for k in range(12):  # riveted plates
            a = math.radians(k * 30 + 15)
            rx, ry = c + math.cos(a) * c * 0.9, c + math.sin(a) * c * 0.9
            d.ellipse((rx - 9, ry - 9, rx + 9, ry + 9), fill=(170, 170, 185))
            d.ellipse((rx - 5, ry - 7, rx + 3, ry - 1), fill=(240, 240, 250))
            a2 = math.radians(k * 30)
            d.line((c + math.cos(a2) * c * r0, c + math.sin(a2) * c * r0, c + math.cos(a2) * c, c + math.sin(a2) * c), fill=(8, 8, 12), width=5)
    d = ImageDraw.Draw(base)
    for k in range(30):
        a = math.radians(-90 + k * 12)
        L = 0.05 if k % 5 else 0.09
        d.line((c + math.cos(a) * c * (r0 + 0.01), c + math.sin(a) * c * (r0 + 0.01),
                c + math.cos(a) * c * (r0 + 0.01 + L), c + math.sin(a) * c * (r0 + 0.01 + L)), fill=(245, 242, 232), width=6 if k % 5 == 0 else 3)
    base = grain(base, 26, seed)
    base.putalpha(m)
    save(base, name)


def spinner_inner(name, seed, size=1024, r0=0.34, r1=0.62, tone=INK["paper"]):
    S, c = size, size / 2
    m = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(m)
    md.ellipse((c - c * r1, c - c * r1, c + c * r1, c + c * r1), fill=255)
    md.ellipse((c - c * r0, c - c * r0, c + c * r0, c + c * r0), fill=0)
    base = paper((S, S), tone, seed, amount=18)
    base = ink(base, halftone(radial((S, S), 0, 255).point(lambda v: max(0, v - 60)), 8, 45), INK["cyan"], (3, 2), 0.5)
    d = ImageDraw.Draw(base)
    f = font("mono", 30)
    for k in range(30):
        a = math.radians(-90 + k * 12)
        d.line((c + math.cos(a) * c * (r1 - 0.06), c + math.sin(a) * c * (r1 - 0.06), c + math.cos(a) * c * (r1 - 0.01), c + math.sin(a) * c * (r1 - 0.01)), fill=INK["black"], width=3)
        if k % 5 == 0:
            tx, ty = c + math.cos(a) * c * (r1 - 0.12), c + math.sin(a) * c * (r1 - 0.12)
            text_center(d, (tx - 30, ty - 20, tx + 30, ty + 20), str(k), f, INK["black"])
    base.putalpha(m)
    save(base, name)


def spinner_hub(name, who, seed, size=640):
    rng = random.Random(seed)
    S, c = size, size / 2
    art = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse((8, 8, S - 8, S - 8), fill=255)
    if who == "op":
        base = Image.new("RGB", (S, S), INK["paper"])
        fig = Image.new("L", (S, S), 0)
        fd = ImageDraw.Draw(fig)
        fd.ellipse((c - 110, 120, c + 110, 360), fill=230)            # head
        fd.polygon([(c - 250, S), (c - 200, 420), (c + 200, 420), (c + 250, S)], fill=200)  # jacket
        fd.rectangle((c - 60, 330, c + 60, 440), fill=180)
        base = ink(base, halftone(fig, 9, 45), INK["pink"], (0, 0), 1.0)
        vis = Image.new("L", (S, S), 0)
        ImageDraw.Draw(vis).polygon([(c - 120, 210), (c + 120, 200), (c + 110, 260), (c - 115, 268)], fill=255)
        base = ink(base, vis, INK["black"], (4, 2))
        ant = Image.new("L", (S, S), 0)
        ImageDraw.Draw(ant).line((c + 60, 130, c + 150, 20), fill=255, width=12)
        base = ink(base, ant, INK["black"], (0, 0))
        base = ink(base, halftone(fig.point(lambda v: v // 2), 11, 15), INK["black"], (5, 3), 0.8)
    else:
        base = Image.new("RGB", (S, S), (30, 26, 22))
        st = Image.new("L", (S, S), 0)
        sd = ImageDraw.Draw(st)
        for k in range(-S, S * 2, 60):
            sd.line((k, 0, k - S, S), fill=255, width=22)
        base = ink(base, st, INK["orange"], (0, 0), 0.5, "normal")
        crane = Image.new("L", (S, S), 0)
        cd = ImageDraw.Draw(crane)  # container crane glyph (Meridian landmark)
        cd.rectangle((c - 140, 140, c - 110, 470), fill=255)
        cd.rectangle((c - 180, 150, c + 190, 180), fill=255)
        cd.line((c - 125, 145, c + 150, 170), fill=255, width=8)
        cd.rectangle((c + 70, 180, c + 80, 300), fill=255)
        cd.rectangle((c + 20, 300, c + 130, 370), fill=255)
        cd.rectangle((c - 200, 470, c + 200, 490), fill=255)
        base = ink(base, crane, (15, 12, 10), (4, 3))
        base = ink(base, crane, INK["orange"], (0, 0), 1.0, "normal")
    base = grain(base, 26, seed)
    art = base.convert("RGBA")
    art.putalpha(m)
    save(die_cut(art, 12, True, seed), name)


def sticker_word(name, txt, fg, bg, seed, fnt="anton", size=90, rot=0, pad=26, shape="rect"):
    f = font(fnt, size)
    tmp = ImageDraw.Draw(Image.new("L", (10, 10)))
    bb = tmp.textbbox((0, 0), txt, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    w, h = tw + pad * 2, th + pad * 2
    art = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(art)
    if shape == "rect":
        d.rounded_rectangle((0, 0, w - 1, h - 1), 18, fill=bg + (255,))
    elif shape == "burst":
        pts = []
        for k in range(22):
            r = (0.5 if k % 2 == 0 else 0.36)
            a = math.pi * 2 * k / 22
            pts.append((w / 2 + math.cos(a) * w * r * 1.05, h / 2 + math.sin(a) * h * r * 1.25))
        art = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(art)
        d.polygon(pts, fill=bg + (255,))
    else:
        d.ellipse((0, 0, w - 1, h - 1), fill=bg + (255,))
    rgb = art.convert("RGB")
    rgb = ink(rgb, halftone(gradient((w, h), 0, 120), 6, 45), INK["black"], (0, 0), 0.4)
    d = ImageDraw.Draw(rgb)
    d.text((pad - bb[0] + 4, pad - bb[1] + 3), txt, font=f, fill=INK["black"] if fg != INK["black"] else INK["pink"])
    d.text((pad - bb[0], pad - bb[1]), txt, font=f, fill=fg)
    rgb = rgb.convert("RGBA")
    rgb.putalpha(art.getchannel("A"))
    if rot:
        rgb = rgb.rotate(rot, expand=True, resample=Image.BICUBIC)
    save(die_cut(rgb, 12, True, seed), name)


def sticker_icon(name, kind, seed, size=220):
    art = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(art)
    c = size / 2
    if kind == "eye":
        d.ellipse((10, 50, size - 10, size - 50), fill=INK["amber"] + (255,))
        d.ellipse((c - 44, c - 44, c + 44, c + 44), fill=INK["black"] + (255,))
        d.ellipse((c - 16, c - 30, c + 4, c - 10), fill=(255, 255, 255, 255))
    elif kind == "barcode":
        art = Image.new("RGBA", (size, int(size * 0.6)), (255, 255, 255, 255))
        d = ImageDraw.Draw(art)
        rng = random.Random(seed)
        x = 12
        while x < size - 16:
            wd = rng.choice([2, 3, 5, 7])
            d.rectangle((x, 10, x + wd, size * 0.6 - 34), fill=INK["black"])
            x += wd + rng.choice([2, 3, 4])
        d.text((14, size * 0.6 - 30), "MRD-0x55A1", font=font("mono", 22), fill=INK["black"])
    elif kind == "fist":  # the Cell hexagon
        pts = [(c + 95 * math.cos(math.radians(a)), c + 95 * math.sin(math.radians(a))) for a in range(30, 390, 60)]
        d.polygon(pts, fill=INK["pink"] + (255,))
        d.polygon([(c - 48, c - 32), (c + 48, c - 32), (c, c + 50)], fill=INK["black"] + (255,))
    elif kind == "skull":
        d.ellipse((30, 20, size - 30, size - 60), fill=(245, 242, 232, 255))
        d.rectangle((70, size - 80, size - 70, size - 30), fill=(245, 242, 232, 255))
        d.ellipse((62, 70, 102, 116), fill=INK["black"])
        d.ellipse((size - 102, 70, size - 62, 116), fill=INK["black"])
        d.polygon([(c, 120), (c - 12, 140), (c + 12, 140)], fill=INK["black"])
    save(die_cut(art, 12, True, seed), name)


def card(name, title, cost, kind, lines, seed, w=300, h=420):
    rng = random.Random(seed)
    tc = SLICE_COL.get(kind, INK["pink"])
    body = paper((w, h), INK["paper"] if kind != "black" else (30, 30, 34), seed, amount=16)
    if kind == "pinkcard":
        body = paper((w, h), (246, 180, 206), seed, amount=16)
        tc = INK["pink"]
    d = ImageDraw.Draw(body)
    ft = font("anton", 40)
    d.text((18, 12), title, font=ft, fill=INK["black"])
    # illustration window: two-colour riso (ink + type colour), misregistered
    ix0, iy0, ix1, iy1 = 16, 72, w - 16, 250
    win = Image.new("L", (w, h), 0)
    ImageDraw.Draw(win).rectangle((ix0, iy0, ix1, iy1), fill=255)
    art = Image.new("L", (w, h), 0)
    ad = ImageDraw.Draw(art)
    cx, cy = (ix0 + ix1) / 2, (iy0 + iy1) / 2
    ad.ellipse((cx - 70, cy - 70, cx + 70, cy + 70), fill=170)
    for k in range(6):
        a = math.radians(k * 60 + rng.uniform(0, 30))
        ad.line((cx, cy, cx + math.cos(a) * 70, cy + math.sin(a) * 70), fill=40, width=6)
    ad.arc((cx - 92, cy - 92, cx + 92, cy + 92), 200, 330, fill=255, width=14)
    ad.polygon([(cx + 80, cy - 70), (cx + 108, cy - 40), (cx + 70, cy - 36)], fill=255)
    body = ink(body, ImageChops.multiply(halftone(gradient((w, h), 60, 200), 7, 15), win), tc, (0, 0), 0.9)
    body = ink(body, ImageChops.multiply(halftone(art, 6, 45), win), INK["black"], (4, 3), 0.95)
    d = ImageDraw.Draw(body)
    d.rectangle((ix0, iy0, ix1, iy1), outline=INK["black"], width=3)
    fm = font("mono", 21)
    for i, ln in enumerate(lines):
        d.text((20, 266 + i * 26), ln, font=fm, fill=INK["black"] if kind != "black" else (230, 230, 230))
    # cost bubble
    d.ellipse((w - 70, 10, w - 16, 64), fill=INK["acid"], outline=INK["black"], width=3)
    text_center(d, (w - 70, 10, w - 16, 62), str(cost), font("anton", 34), INK["black"])
    d.rectangle((0, 0, w - 1, h - 1), outline=INK["black"], width=4)
    art_rgba = body.convert("RGBA")
    save(die_cut(art_rgba, 14, True, seed), name)


def glass_panel(name, w, h, rows, title=None, seed=0, edge=INK["glow_cyan"], alpha=225):
    img = Image.new("RGBA", (w, h), (5, 13, 28, alpha))
    d = ImageDraw.Draw(img)
    for y in range(0, h, 3):
        d.line((0, y, w, y), fill=(12, 26, 48, alpha))
    d.rectangle((0, 0, w - 1, h - 1), outline=edge + (190,), width=2)
    y = 12
    if title:
        d.text((16, y), title, font=font("mono", 28), fill=(207, 246, 255, 255))
        y += 38
        d.line((16, y, w - 16, y), fill=INK["pink"] + (255,), width=3)
        y += 12
    for (txt, col, size) in rows:
        d.text((16, y), txt, font=font("mono", size), fill=col + (255,))
        y += int(size * 1.35)
    save(img, name)


def washed_word(name, txt, w, h, size, sub=None, seed=0, frame=True):
    """The digital system layer under the marker: low contrast, scanlined, washed."""
    img = Image.new("RGBA", (w, h), (5, 13, 28, 200))
    d = ImageDraw.Draw(img)
    if frame:
        d.rectangle((0, 0, w - 1, h - 1), outline=(92, 225, 255, 90), width=2)
        d.rectangle((8, 8, w - 9, h - 9), outline=(92, 225, 255, 40), width=1)
    f = font("mono", size)
    bb = d.textbbox((0, 0), txt, font=f)
    tx = (w - (bb[2] - bb[0])) / 2 - bb[0]
    ty = (h - (bb[3] - bb[1])) / 2 - bb[1] - (10 if sub else 0)
    ghost = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(ghost)
    gd.text((tx + 4, ty), txt, font=f, fill=(255, 72, 176, 40))
    gd.text((tx, ty), txt, font=f, fill=(150, 205, 225, 105))
    img = Image.alpha_composite(img, ghost)
    d = ImageDraw.Draw(img)
    if sub:
        d.text((16, h - 34), sub, font=font("mono", 20), fill=(150, 190, 210, 90))
    for y in range(0, h, 4):
        d.line((0, y, w, y), fill=(0, 0, 0, 60))
    save(img, name)


def paper_tag(name, label, value, color, seed, w=220, h=96):
    rng = random.Random(seed)
    base = paper((w, h), color, seed, amount=18)
    outer, inner = torn_rect_mask(w, h, 3, 2.5, rng, 3)
    d = ImageDraw.Draw(base)
    d.text((14, 8), label, font=font("mono", 18), fill=INK["black"])
    d.text((14, 28), value, font=font("marker", 40), fill=INK["black"])
    rim = ImageChops.subtract(outer, inner)
    base = Image.composite(Image.new("RGB", (w, h), (252, 250, 244)), base, rim)
    base.putalpha(outer)
    save(base, name)


def tape(name, seed, w=180, h=56):
    rng = random.Random(seed)
    img = Image.new("RGBA", (w, h), (236, 226, 190, 150))
    m = Image.new("L", (w, h), 0)
    pts = [(0, 0)] + [(w, 0)]
    right = [(w - rng.uniform(0, 8), y) for y in range(0, h + 1, 6)]
    left = [(rng.uniform(0, 8), y) for y in range(h, -1, -6)]
    ImageDraw.Draw(m).polygon([(6, 0), (w - 6, 0)] + right + [(w - 6, h), (6, h)] + left, fill=150)
    img.putalpha(m)
    d = ImageDraw.Draw(img)
    for x in range(0, w, 5):
        d.line((x, 0, x, h), fill=(255, 250, 230, int(m.getpixel((min(w - 1, x), h // 2)) * 0.2)))
    save(img, name)


def shard(name, ch, color, seed):
    w, h = 90, 120
    art = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(art)
    f = font("mono", 120)
    text_center(d, (0, 0, w, h), ch, f, color + (255,))
    art = art.filter(ImageFilter.MaxFilter(5))
    st = die_cut(art, 6, False, seed, backing=(255, 255, 255))
    save(st, name)
    em = Image.new("RGB", st.size, 0)
    em.paste(Image.new("RGB", st.size, color), (0, 0), st.getchannel("A").point(lambda v: 255 if v > 128 else 0))
    save(em, name + "_em")


def poster_heat(name, seed, value="34", band="NOTICED", stock=None, inkc=None):
    w, h = 260, 360
    rng = random.Random(seed)
    base = paper((w, h), stock or INK["yellow"], seed, amount=20)
    base = ink(base, halftone(gradient((w, h), 30, 190), 8, 45), inkc or INK["amber"], (0, 0), 0.9)
    d = ImageDraw.Draw(base)
    d.text((18, 12), "HEAT", font=font("anton", 90), fill=INK["black"])
    d.ellipse((60, 150, 200, 230), fill=INK["black"])
    d.ellipse((105, 165, 155, 215), fill=INK["yellow"])
    d.ellipse((118, 178, 142, 202), fill=INK["black"])
    d.text((22, 250), value, font=font("marker", 64), fill=INK["black"])
    d.text((120, 272), band, font=font("mono", 24), fill=INK["black"])
    outer, inner = torn_rect_mask(w, h, 4, 4, rng, 4)
    base = Image.composite(Image.new("RGB", (w, h), (255, 252, 240)), base, ImageChops.subtract(outer, inner))
    base.putalpha(outer)
    save(base, name)


def vellum(name, w=1920, h=1080):
    """Frosted tracing paper that pushes the combat city back (feedback 3)."""
    rng = random.Random(3)
    img = Image.new("RGBA", (w, h), (18, 20, 40, 150))
    m = Image.new("L", (w, h), 150)
    fib = Image.new("L", (w // 4, h // 4), 0)
    fib = Image.frombytes("L", fib.size, rng.randbytes(fib.size[0] * fib.size[1])).resize((w, h), Image.BILINEAR)
    m = ImageChops.add(m, fib.point(lambda v: (v - 128) // 6 if v > 128 else 0))
    img.putalpha(m)
    save(img, name)


def strip_page():
    w, h = 1920, 1080
    base = paper((w, h), INK["paper"], 500, amount=18)
    base = ink(base, halftone(radial((w, h), 0, 230).point(lambda v: max(0, v - 60)), 11, 15), INK["pink"], (0, 0), 0.5)
    base = ink(base, halftone(gradient((w, h), 0, 120, True), 9, 75), INK["cyan"], (4, 3), 0.35)
    d = ImageDraw.Draw(base)
    d.text((64, 26), "THE MARKER'S LIFE", font=font("anton", 64), fill=INK["black"])
    d.text((66, 104), "pink marker = someone writing on your screen. system words stay underneath.", font=font("mono", 24), fill=INK["black"])
    save(base, "strip_page")


def strip_screen():
    w, h = 560, 820
    img = Image.new("RGBA", (w, h), (5, 13, 28, 250))
    d = ImageDraw.Draw(img)
    for y in range(0, h, 3):
        d.line((0, y, w, y), fill=(12, 26, 48, 250))
    d.rectangle((0, 0, w - 1, h - 1), outline=(92, 225, 255, 200), width=3)
    d.text((18, 16), "TURN 3 . RAM 7/12", font=font("mono", 24), fill=(122, 136, 156, 255))
    d.line((18, 50, w - 18, 50), fill=INK["pink"] + (255,), width=3)
    f = font("mono", 22)
    for i, (t, c) in enumerate([("forecast  ATK 6 -> CRIT 12", (207, 246, 255)), ("agent     BLOCK 3", (175, 192, 214)),
                                ("you       +0 heat", (175, 192, 214)), ("risk      CORRUPTED", (255, 68, 51))]):
        d.text((18, 66 + i * 30), t, font=f, fill=c + (255,))
    # a small wheel glyph (outline only, glass UI)
    cx, cy, r = w / 2, 330, 90
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(92, 225, 255, 200), width=4)
    d.ellipse((cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55), outline=(92, 225, 255, 140), width=3)
    for k in range(6):
        a = math.radians(k * 60)
        d.line((cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55, cx + math.cos(a) * r, cy + math.sin(a) * r), fill=(92, 225, 255, 160), width=3)
    save(img, "strip_screen")


def caption(name, txt, seed):
    rng = random.Random(seed)
    w, h = 520, 70
    base = paper((w, h), INK["yellow"], seed, amount=16)
    d = ImageDraw.Draw(base)
    d.text((16, 16), txt, font=font("mono", 30), fill=INK["black"])
    outer, inner = torn_rect_mask(w, h, 3, 2.5, rng, 3)
    base = Image.composite(Image.new("RGB", (w, h), (252, 250, 244)), base, ImageChops.subtract(outer, inner))
    base.putalpha(outer)
    save(base, name)


def main():
    strip_page()
    strip_screen()
    caption("cap_1", "1  WRITE-ON, stroke by stroke", 601)
    caption("cap_2", "2  DRIPS FORM ... AND WAIT", 602)
    caption("cap_3", "3  PRESS: PAGE LEAVES, INK RUNS", 603)
    sky()
    for i in range(4):
        skyline(f"city_{i}", 100 + i, i, tall=[(0.45, 0.98), (0.35, 0.85), (0.25, 0.7), (0.15, 0.5)][i],
                win_p=[0.13, 0.17, 0.22, 0.28][i])
    skyline("city_4", 150, 3, tall=(0.2, 0.55), win_p=0.4)
    skyline("city_5", 160, 2, tall=(0.3, 0.8), win_p=0.3)
    hq_tower()
    for i in range(3):
        highway(f"hwy_{i}", 200 + i)
    vehicle("car", "car", 1)
    vehicle("flyer", "flyer", 2)
    vehicle("heli", "heli", 3)
    vehicle("drone", "drone", 4)
    holo("holo_0", INK["glow_cyan"], 11)
    holo("holo_1", INK["pink"], 12)
    holo("holo_2", INK["violet"], 13)
    holo("holo_3", (212, 255, 0), 14)
    holo("holo_4", INK["amber"], 15)
    for i, (b, dot) in enumerate([(3, False), (10, True), (24, False), (6, True), (40, False), (16, True)]):
        fog(f"fog_{i}", 300 + i, b, dot)
    ground_map()
    # combat
    op = [(6, "atk", 6), (4, "def", 5), (3, "crit", 12), (5, "atk", 6), (3, "evd", 2), (5, "def", 6), (4, "atk", 8)]
    en = [(5, "atk", 8), (4, "aff", 3), (6, "def", 6), (6, "atk", 6), (3, "crit", 14), (3, "miss", 0), (3, "def", 4)]
    spinner_slices("sp_slices_op", op, 21)
    spinner_slices("sp_slices_en", en, 22)
    spinner_bezel("sp_bezel_op", "breaker", 23)
    spinner_bezel("sp_bezel_en", "meridian", 24)
    spinner_inner("sp_inner_op", 25)
    spinner_inner("sp_inner_en", 26, tone=(233, 222, 200))
    spinner_hub("sp_hub_op", "op", 27)
    spinner_hub("sp_hub_en", "en", 28)
    sticker_word("stk_comply", "COMPLY", INK["black"], INK["orange"], 31, size=70)
    sticker_word("stk_payup", "PAY UP", INK["orange"], INK["black"], 32, size=64)
    sticker_word("stk_debt", "DEBT", (255, 255, 255), INK["harm"], 33, size=60, shape="round", pad=34)
    sticker_word("stk_dmg", "-12", INK["black"], INK["harm"], 34, size=120, shape="burst", pad=70)
    sticker_word("stk_nope", "NOPE", INK["pink"], INK["black"], 35, "marker", 60)
    sticker_word("stk_hot", "HOT", INK["black"], INK["amber"], 36, "marker", 64, shape="round", pad=40)
    sticker_word("stk_cell", "REBEL CELL", INK["black"], INK["pink"], 37, "anton", 64)
    sticker_word("stk_price1", "@ 69", INK["black"], INK["yellow"], 38, "anton", 54)
    sticker_word("stk_price2", "@ 61", INK["black"], INK["acid"], 39, "anton", 54)
    sticker_word("stk_price3", "@ 75", INK["black"], (246, 180, 206), 40, "anton", 54)
    sticker_word("stk_hq", "HOME", INK["black"], INK["acid"], 41, "marker", 60)
    sticker_word("stk_node", "X", INK["black"], INK["acid"], 42, "anton", 60, shape="round", pad=32)
    sticker_word("stk_node_p", "!", (255, 255, 255), INK["pink"], 43, "anton", 60, shape="round", pad=40)
    sticker_word("stk_node_o", "$", INK["black"], INK["orange"], 44, "anton", 56, shape="round", pad=36)
    sticker_word("stk_node_c", "+", INK["black"], INK["glow_cyan"], 45, "anton", 60, shape="round", pad=38)
    sticker_word("stk_wanted", "WANTED", INK["black"], INK["harm"], 46, "anton", 80)
    sticker_word("stk_nofuture", "NO FUTURE?", INK["pink"], INK["black"], 47, "marker", 54)
    sticker_icon("stk_eye", "eye", 51)
    sticker_icon("stk_barcode", "barcode", 52)
    sticker_icon("stk_fist", "fist", 53)
    sticker_icon("stk_skull", "skull", 54)
    card("card_0", "JOLT", 1, "atk", ["Spin a wheel", "3 ticks."], 61)
    card("card_1", "FINE TUNE", 1, "pinkcard", ["Two +-1 nudges", "on one ring."], 62)
    card("card_2", "BRUTE SPIN", 2, "def", ["Spin a wheel", "6 ticks."], 63)
    card("card_3", "TAP TAP", 2, "evd", ["Three +-1", "nudges."], 64)
    card("card_4", "ENCRYPT", 1, "aff", ["Chosen slice", "eats a status."], 65)
    card("card_5", "MIRROR FLIP", 3, "crit", ["Flip a wheel.", "Blocked by", "resistance."], 66)
    glass_panel("gl_fc_op", 760, 150, [("<> DEFEND . HALF POWER", (207, 246, 255), 28),
                                        ("+3 BLOCK   CRIT 20%  ATK 60%", (175, 192, 214), 22),
                                        ("YOU GET CORRUPTED", (255, 68, 51), 22)], seed=1)
    glass_panel("gl_fc_en", 760, 150, [("<> AFFLICT . GOOD AIM", (207, 246, 255), 28),
                                        ("PUTS CORRUPTED ON YOU", (255, 68, 51), 22),
                                        ("collections drone +3 BLOCK", (175, 192, 214), 22)], seed=2, edge=INK["orange"])
    glass_panel("gl_turn", 1300, 44, [("TURN 1 . FREE NUDGE 1 . Q/E NUDGE YOUR WHEEL . W NUDGE THE TARGET", (122, 136, 156), 22)], seed=3, alpha=160)
    glass_panel("gl_log", 420, 260, [("> tick 14  ATK 6 -> agent", (175, 192, 214), 20), ("> BLOCK absorbed 3", (175, 192, 214), 20),
                                      ("> CRIT 12 landed", (255, 68, 51), 20), ("> heat +2", (255, 176, 0), 20),
                                      ("> ram 5/12", (122, 136, 156), 20)], "SYSTEM LOG", seed=4)
    washed_word("wash_execute", "EXECUTE", 620, 190, 118, "[SPACE] COMMIT TURN", 1)
    washed_word("wash_purchase", "PURCHASE", 560, 150, 96, "[ENTER] CONFIRM ORDER", 2)
    washed_word("wash_disconnect", "DISCONNECT", 640, 140, 88, "[ESC] CLOSE SESSION", 3)
    washed_word("wash_target", "TARGET_ACQUIRED", 700, 110, 64, None, 4)
    washed_word("wash_evade", "EVASIVE ROUTE", 640, 120, 70, "ALERT LEVEL 3", 5)
    washed_word("wash_home", "HQ_NODE", 360, 90, 54, None, 6, frame=False)
    for i, (lab, val, c) in enumerate([("HEAT", "34/100", INK["yellow"]), ("SCHEMATICS", "20", (246, 180, 206)),
                                       ("HP", "60/60", INK["yellow"]), ("CYCLES", "120", INK["paper"]),
                                       ("CARDS", "10", INK["paper_alt"]), ("RANK", "2", (246, 180, 206))]):
        paper_tag(f"tag_{i}", lab, val, c, 70 + i)
    for i in range(4):
        tape(f"tape_{i}", 80 + i)
    shard("shard_0", "0", INK["glow_cyan"], 90)
    shard("shard_1", "1", INK["pink"], 91)
    shard("shard_2", "1", INK["glow_cyan"], 92)
    shard("shard_3", "0", INK["pink"], 93)
    poster_heat("poster_heat", 95)
    poster_heat("poster_hunted", 96, "82", "HUNTED", (250, 190, 180), INK["harm"])
    holo("holo_5", INK["harm"], 16)
    vellum("vellum")
    # modem shop
    glass_panel("gl_chips", 700, 330, [("[#] BARBED WIRE      @141", (207, 246, 255), 24), ("    DEF slice also deals 2", (175, 192, 214), 20),
                                        ("[#] SHUNT             @129", (207, 246, 255), 24), ("    resolves the neighbour", (175, 192, 214), 20),
                                        ("[#] SCRUBBER          @218", (207, 246, 255), 24), ("    server rack eats 1 heat", (175, 192, 214), 20)],
                "MICROCHIPS", seed=5)
    glass_panel("gl_slices", 700, 260, [("SHD 5   ATK 10   EVD 2", (207, 246, 255), 26), ("@100 each . socket into slot 1", (175, 192, 214), 20),
                                         ("", (0, 0, 0), 12), ("DAEMONS: none in stock", (122, 136, 156), 20)], "SLICES", seed=6, edge=INK["amber"])
    glass_panel("gl_cards", 820, 420, [("", (0, 0, 0), 20)], "CARDS", seed=7)
    glass_panel("gl_remove", 700, 250, [("SHRED A CARD      @50", (207, 246, 255), 26), ("cycles 120", (175, 192, 214), 20)], "REMOVE A CARD", seed=8, edge=INK["acid"])
    glass_panel("gl_head", 900, 70, [("05  MODEM CYBER SHOP   //  node 4-C  //  uplink 98%", (175, 192, 214), 24)], seed=9, alpha=150)
    # zine panel for the strip
    glass_panel("gl_strip_hud", 540, 110, [("TURN 3 . RAM 7/12", (122, 136, 156), 22), ("forecast: ATK 6 -> CRIT 12", (175, 192, 214), 22)], seed=10, alpha=200)
    print("textures ->", OUT)


if __name__ == "__main__":
    main()
