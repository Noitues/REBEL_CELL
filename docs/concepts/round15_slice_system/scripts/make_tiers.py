"""Round 15 -> ../tiers.png : three tier-flair options, ALL INSIDE the slice border (nothing past the rim).
Each option: I / II / III heroes, every program row, colour / grey / deutan / protan, r = 60 wheels.
Tiers are a placeholder (not in game): SliceData has no upgrade field yet.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
CACHE = os.path.join(OUT, "scratch", "tiers")

import numpy as np
from PIL import Image, ImageDraw, ImageOps
import slicekit as K
from slicelib import f_num, f_ui, f_mono, bloom, PROGRAMS, ORDER

VALUES = {"EXPLOIT": (6, 8, 10), "ZERO-DAY": (12, 15, 18), "FIREWALL": (5, 7, 9), "SANDBOX": (8, 10, 12),
          "PROXY": (4, 5, 6), "PATCH": (3, 4, 6), "VIRUS": (3, 4, 5), "TROJAN": (1, 2, 3), "NULL": (None, None, None)}
WHEEL = ["EXPLOIT", "FIREWALL", "PROXY", "VIRUS", "ZERO-DAY", "PATCH"]
STYLES = {
    "a": ("OPTION a  inset line -> filled gap", ["II: a thin line inset from the border,", "    a gap between them", "III: gold border; the gap fills with", "    gold cross-hatch"]),
    "b": ("OPTION b  outer arc + ticks", ["II: wider steel border + trim (round 14)", "III: gold border, chevrons along the", "    inner side of the OUTER arc only;", "    tick marks + PERFECT mark lit gold"]),
    "c": ("OPTION c  pattern all round", ["II: wider steel border + trim (round 14)", "III: gold border + a twisted-rope", "    stripe all the way round the inner", "    border"]),
}
RECOMMEND = "a"
MACHADO = {
    "protan": np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]], np.float32),
    "deutan": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]], np.float32),
}


def cvd(im, kind):
    a = np.asarray(im.convert("RGBA"), np.float32) / 255
    rgb = a[..., :3]
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    sim = np.clip(lin @ MACHADO[kind].T, 0, 1)
    srgb = np.where(sim <= 0.0031308, sim * 12.92, 1.055 * sim ** (1 / 2.4) - 0.055)
    return Image.fromarray((np.concatenate([srgb, a[..., 3:]], -1) * 255 + 0.5).astype(np.uint8), "RGBA")


def grey(im):
    a = im.split()[3]
    g = ImageOps.grayscale(im.convert("RGB")).convert("RGBA")
    g.putalpha(a)
    return g


VIEWS = [("colour", lambda i: i), ("grey", grey), ("deutan", lambda i: cvd(i, "deutan")), ("protan", lambda i: cvd(i, "protan"))]


def P(*a):
    return os.path.join(CACHE, "_".join(str(x) for x in a) + ".png")


def render():
    os.makedirs(CACHE, exist_ok=True)
    for st in STYLES:
        K.TIER_STYLE = st
        for k in (1, 2, 3):
            K.tile("EXPLOIT", VALUES["EXPLOIT"][k - 1], t=0.45, tier=k, scale=0.42).save(P(st, "hero", k))
            K.tile("VIRUS", VALUES["VIRUS"][k - 1], t=0.45, tier=k, scale=0.25, seed=8).save(P(st, "small", k))
            K.wheel([(p, VALUES[p][k - 1], k, None) for p in WHEEL], t=0.45, r_px=60).save(P(st, "wheel", k))
            for p in ORDER:
                K.tile(p, VALUES[p][k - 1], t=0.45, tier=k, scale=0.21, seed=ORDER.index(p) + 2).save(P(st, p, k))
        print(st, flush=True)
    K.TIER_STYLE = RECOMMEND
    mixed = [(p, VALUES[p][k - 1], k, None) for p, k in zip(WHEEL, (3, 1, 2, 1, 3, 2))]
    K.wheel(mixed, t=0.45, r_px=150).save(P("mixed150"))


def compose():
    W, BH = 1960, 400
    H = 120 + 3 * BH + 50
    im = Image.new("RGBA", (W, H), (11, 10, 16, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        d.line([(0, y), (W, y)], fill=(14, 13, 20))
    d.text((40, 18), "ROUND 15  SLICE TIERS  (flair inside the border)", font=f_num(54), fill=(255, 255, 255))
    d.text((44, 80), "placeholder (not in game).  Nothing stands past the rim any more.  Glyph + value block identical at every tier; the tier tab pips (1/2/3) "
           "stay in every option.", font=f_mono(14, False), fill=(255, 170, 110))
    L = lambda x, y, s, c=(200, 200, 212), f=None: d.text((x, y), s, font=f or f_mono(12, False), fill=c)
    for bi, (st, (title, lines)) in enumerate(STYLES.items()):
        y0 = 118 + bi * BH
        rec = st == RECOMMEND
        d.rounded_rectangle([20, y0 - 4, W - 20, y0 + BH - 14], radius=10, outline=(255, 200, 70) if rec else (50, 48, 66), width=2 if rec else 1)
        d.text((34, y0 + 2), title, font=f_num(28), fill=(255, 214, 64))
        if rec:
            d.text((34, y0 + 36), "RECOMMENDED", font=f_ui(16, b"Bold SemiCondensed"), fill=(255, 200, 70))
        for i, s in enumerate(lines):
            L(36, y0 + 64 + i * 17, s)
        # heroes
        hx = 34
        hy = y0 + 140
        for k in (1, 2, 3):
            h = Image.open(P(st, "hero", k))
            im.alpha_composite(h, (hx, hy))
            d.text((hx + h.width // 2 - 8, hy + h.height - 4), ["I", "II", "III"][k - 1], font=f_num(24), fill=(220, 220, 230))
            hx += h.width + 4
        # every program
        gx0 = 600
        t0 = Image.open(P(st, "EXPLOIT", 1))
        cw = t0.width + 2
        for j, p in enumerate(ORDER):
            d.text((gx0 + j * cw + 8, y0 + 6), p, font=f_ui(12, b"Bold SemiCondensed"), fill=PROGRAMS[p]["col"])
        for k in (1, 2, 3):
            for j, p in enumerate(ORDER):
                t = Image.open(P(st, p, k))
                im.alpha_composite(t, (gx0 + j * cw, y0 + 24 + (k - 1) * (t0.height + 2)))
        gy = y0 + 292
        # vision row: I, II, III in colour / grey / deutan / protan
        sm = Image.open(P(st, "small", 1))
        for r, (vn, fn) in enumerate(VIEWS):
            bx = 34 + r * (3 * (sm.width + 2) + 22)
            L(bx + 4, gy - 4, vn + "  I / II / III", (175, 175, 190))
            for k in (1, 2, 3):
                t = fn(Image.open(P(st, "small", k)))
                im.alpha_composite(t, (bx + (k - 1) * (sm.width + 2), gy + 12))
        # r = 60 wheels: I, II, III colour, then III grey / deutan / protan
        wx0 = gx0 + 9 * cw + 20
        L(wx0, y0 + 6, "r = 60:  I  /  II  /  III", (175, 175, 190))
        w1 = Image.open(P(st, "wheel", 1))
        for k in (1, 2, 3):
            im.alpha_composite(Image.open(P(st, "wheel", k)), (wx0 + (k - 1) * (w1.width - 4), y0 + 20))
        L(wx0, y0 + 20 + w1.height + 2, "III in grey / deutan / protan", (175, 175, 190))
        for j, (vn, fn) in enumerate(VIEWS[1:]):
            im.alpha_composite(fn(Image.open(P(st, "wheel", 3))), (wx0 + j * (w1.width - 4), y0 + 36 + w1.height))
    notes = ("Why a: II and III are told apart by STRUCTURE (one line -> a line plus a filled, hatched band) that hugs the whole screen edge, so it reads at r = 60, "
             "in grey and in both CVD sims. b puts all its III signal on the outer arc (thin at r = 60); c's II and III share the steel/gold split only by colour + a fine stripe.")
    import textwrap
    for i, ln in enumerate(textwrap.wrap(notes, 190)):
        d.text((34, 118 + 3 * BH - 8 + i * 16), ln, font=f_mono(12, False), fill=(200, 200, 212))
    out = bloom(im.convert("RGB"), 1, 0.25, 0.66)
    out.save(os.path.join(OUT, "tiers.png"))
    print("saved tiers.png", out.size, flush=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("render", "all"):
        render()
    if what in ("compose", "all"):
        compose()
