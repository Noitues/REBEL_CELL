"""Round 13 -> ../tiers.png : 3 upgrade tiers (I / II / III) for every slice program.
Tiers are a placeholder (not in game): SliceData has no upgrade field yet.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
CACHE = os.path.join(OUT, "scratch", "tiers")

from PIL import Image, ImageDraw, ImageOps
import slicekit as K
from slicelib import f_num, f_ui, f_mono, bloom, PROGRAMS, ORDER

VALUES = {"EXPLOIT": (6, 8, 10), "ZERO-DAY": (12, 15, 18), "FIREWALL": (5, 7, 9), "SANDBOX": (8, 10, 12),
          "PROXY": (4, 5, 6), "PATCH": (3, 4, 6), "VIRUS": (3, 4, 5), "TROJAN": (1, 2, 3), "NULL": (None, None, None)}
WHEEL = ["EXPLOIT", "FIREWALL", "PROXY", "VIRUS", "ZERO-DAY", "PATCH"]


def grey(im):
    a = im.split()[3]
    g = ImageOps.grayscale(im.convert("RGB")).convert("RGBA")
    g.putalpha(a)
    return g


def render():
    os.makedirs(CACHE, exist_ok=True)
    for k in (1, 2, 3):
        K.tile("EXPLOIT", VALUES["EXPLOIT"][k - 1], t=0.45, tier=k, scale=0.95).save(os.path.join(CACHE, "hero_%d.png" % k))
        for p in ORDER:
            K.tile(p, VALUES[p][k - 1], t=0.45, tier=k, scale=0.46, seed=ORDER.index(p) + 2).save(os.path.join(CACHE, "%s_%d.png" % (p, k)))
        K.wheel([(p, VALUES[p][k - 1], k, None) for p in WHEEL], t=0.45, r_px=60).save(os.path.join(CACHE, "wheel_%d.png" % k))
    mixed = [(p, VALUES[p][k - 1], k, None) for p, k in zip(WHEEL, (3, 1, 2, 1, 3, 2))]
    K.wheel(mixed, t=0.45, r_px=60).save(os.path.join(CACHE, "wheel_mixed.png"))
    K.wheel(mixed, t=0.45, r_px=150).save(os.path.join(CACHE, "wheel_mixed150.png"))
    print("rendered", flush=True)


def compose():
    W, H = 2000, 1150
    im = Image.new("RGBA", (W, H), (11, 10, 16, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        d.line([(0, y), (W, y)], fill=(14, 13, 20))
    d.text((40, 18), "ROUND 13  SLICE TIERS  I / II / III", font=f_num(54), fill=(255, 255, 255))
    d.text((44, 80), "placeholder (not in game): SliceData has no upgrade tier yet.  The glyph + value block is identical at every tier; "
           "only the bezel, the tier tab and the screen's activity change.", font=f_mono(15, False), fill=(255, 170, 110))
    L = lambda x, y, s, c=(200, 200, 212), f=None: d.text((x, y), s, font=f or f_mono(14, False), fill=c)
    # hero row
    x = 40
    rules = [("I  PLAIN", (190, 190, 200), ["matte dark bezel, hairline dimmed", "screen at 70 % gain, 30 % desaturated", "tab: 1 grey pip"]),
             ("II  TRIMMED", (200, 230, 255), ["brushed steel bezel", "type-colour trim line + corner brackets", "screen at full gain   tab: 2 pips"]),
             ("III  GILDED", (255, 214, 120), ["gold bezel, etched circuit trace + vias", "holo rim (hue walks round the wheel)", "screen 122 %, holo sweep, data sparks  tab: 3"])]
    for k in (1, 2, 3):
        h = Image.open(os.path.join(CACHE, "hero_%d.png" % k))
        im.alpha_composite(h, (x, 112))
        t, c, lines = rules[k - 1]
        d.text((x + 10, 112 + h.height + 2), t, font=f_num(30), fill=c)
        for i, s in enumerate(lines):
            L(x + 12, 112 + h.height + 40 + i * 19, s)
        x += h.width + 20
    # mixed r=150 wheel + greyscale heroes
    w150 = Image.open(os.path.join(CACHE, "wheel_mixed150.png"))
    im.alpha_composite(w150, (x + 10, 100))
    L(x + 30, 100 + w150.height - 4, "r = 150  mixed tiers (III, I, II, I, III, II)", (170, 170, 182), f_mono(13, False))
    gx = x + w150.width + 30
    d.text((gx, 112), "GREYSCALE", font=f_ui(18, b"Bold SemiCondensed"), fill=(220, 220, 230))
    for k in (1, 2, 3):
        h = grey(Image.open(os.path.join(CACHE, "hero_%d.png" % k)))
        h = h.resize((int(h.width * 0.42), int(h.height * 0.42)), Image.LANCZOS)
        im.alpha_composite(h, (gx, 140 + (k - 1) * (h.height + 8)))
    # full roster grid: rows = tiers, cols = programs
    y0 = 520
    d.text((40, y0 - 8), "EVERY PROGRAM", font=f_num(32), fill=(255, 214, 64))
    t0 = Image.open(os.path.join(CACHE, "EXPLOIT_1.png"))
    cw = t0.width + 14
    for j, p in enumerate(ORDER):
        d.text((150 + j * cw + 10, y0 + 30), p, font=f_ui(16, b"Bold SemiCondensed"), fill=PROGRAMS[p]["col"])
    for k in (1, 2, 3):
        yy = y0 + 54 + (k - 1) * (t0.height + 10)
        d.text((44, yy + t0.height // 2 - 20), ["I", "II", "III"][k - 1], font=f_num(40), fill=rules[k - 1][1])
        for j, p in enumerate(ORDER):
            t = Image.open(os.path.join(CACHE, "%s_%d.png" % (p, k)))
            im.alpha_composite(t, (150 + j * cw, yy))
    # small wheels
    yw = y0 + 54 + 3 * (t0.height + 10) + 10
    d.text((40, yw), "r = 60", font=f_num(32), fill=(255, 214, 64))
    xw = 150
    for name, lab in (("wheel_1", "all I"), ("wheel_2", "all II"), ("wheel_3", "all III"), ("wheel_mixed", "mixed")):
        w = Image.open(os.path.join(CACHE, name + ".png"))
        im.alpha_composite(w, (xw, yw))
        g = grey(w)
        im.alpha_composite(g, (xw + w.width + 6, yw))
        L(xw + 10, yw + w.height, lab + "   (colour | grey)", (170, 170, 182), f_mono(13, False))
        xw += 2 * w.width + 50
    nx = xw + 10
    notes = ["At r = 60 the tab and pips drop below 2 px:", "the bezel MATERIAL carries the tier there", "(dark / silver / gold), and it survives grey.",
             "Value + glyph: same size, same plate, same", "position at every tier; III's sweep is", "thinned under the read plate."]
    for i, s in enumerate(notes):
        L(nx, yw + 8 + i * 20, s)
    im = bloom(im.convert("RGB"), 1, 0.30, 0.65)
    im.save(os.path.join(OUT, "tiers.png"))
    print("saved tiers.png", flush=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("render", "all"):
        render()
    if what in ("compose", "all"):
        compose()
