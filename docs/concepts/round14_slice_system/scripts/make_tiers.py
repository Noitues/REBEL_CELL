"""Round 14 -> ../tiers.png : tiers I / II / III with three SHAPE options for tier III, checked in
greyscale, deuteranopia and protanopia (Machado 2009, severity 1.0) and at r = 60.
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
VARIANTS = [("I", 1, None), ("II", 2, None), ("III-A crown", 3, "A"), ("III-B double rim", 3, "B"), ("III-C crest", 3, "C")]
RECOMMEND = "C"

MACHADO = {
    "protan": np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]], np.float32),
    "deutan": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]], np.float32),
}


def cvd(im, kind):
    """Colour-vision-deficiency simulation in linear RGB."""
    a = np.asarray(im.convert("RGBA"), np.float32) / 255
    rgb = a[..., :3]
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    sim = np.clip(lin @ MACHADO[kind].T, 0, 1)
    srgb = np.where(sim <= 0.0031308, sim * 12.92, 1.055 * sim ** (1 / 2.4) - 0.055)
    out = np.concatenate([srgb, a[..., 3:]], -1)
    return Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA")


def grey(im):
    a = im.split()[3]
    g = ImageOps.grayscale(im.convert("RGB")).convert("RGBA")
    g.putalpha(a)
    return g


VIEWS = [("colour", lambda i: i), ("grey", grey), ("deutan", lambda i: cvd(i, "deutan")), ("protan", lambda i: cvd(i, "protan"))]


def vid(v):
    return v[0].split()[0]


def render():
    os.makedirs(CACHE, exist_ok=True)
    for name, tier, style in VARIANTS:
        if style:
            K.TIER3 = style
        k = tier - 1
        K.tile("EXPLOIT", VALUES["EXPLOIT"][k], t=0.45, tier=tier, scale=0.62).save(os.path.join(CACHE, "hero_%s.png" % vid((name,))))
        K.tile("VIRUS", VALUES["VIRUS"][k], t=0.45, tier=tier, scale=0.34, seed=8).save(os.path.join(CACHE, "small_%s.png" % vid((name,))))
        K.wheel([(p, VALUES[p][k], tier, None) for p in WHEEL], t=0.45, r_px=60).save(os.path.join(CACHE, "wheel_%s.png" % vid((name,))))
    K.TIER3 = RECOMMEND
    for p in ORDER:
        K.tile(p, VALUES[p][2], t=0.45, tier=3, scale=0.36, seed=ORDER.index(p) + 2).save(os.path.join(CACHE, "%s_3.png" % p))
        for k in (1, 2):
            K.tile(p, VALUES[p][k - 1], t=0.45, tier=k, scale=0.36, seed=ORDER.index(p) + 2).save(os.path.join(CACHE, "%s_%d.png" % (p, k)))
    mixed = [(p, VALUES[p][k - 1], k, None) for p, k in zip(WHEEL, (3, 1, 2, 1, 3, 2))]
    K.wheel(mixed, t=0.45, r_px=150).save(os.path.join(CACHE, "wheel_mixed150.png"))
    print("rendered", flush=True)


def compose():
    W, H = 2200, 1530
    im = Image.new("RGBA", (W, H), (11, 10, 16, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        d.line([(0, y), (W, y)], fill=(14, 13, 20))
    d.text((40, 18), "ROUND 14  SLICE TIERS  I / II / III", font=f_num(54), fill=(255, 255, 255))
    d.text((44, 80), "placeholder (not in game).  I -> II: wider, brighter steel border + trim.  II -> III: a SHAPE change past the rim (3 options), so the tier reads "
           "without colour.  Glyph + value block identical at every tier.", font=f_mono(14, False), fill=(255, 170, 110))
    L = lambda x, y, s, c=(200, 200, 212), f=None: d.text((x, y), s, font=f or f_mono(13, False), fill=c)
    # heroes
    x = 30
    descr = {"I": ["matte dark bezel, 1 grey pip", "screen 70 %, desaturated"], "II": ["brushed steel + trim + corner", "brackets, 2 pips, screen 100 %"],
             "III-A": ["gold + 3 crown spikes", "standing on the rim"], "III-B": ["gold + a second notched", "rim (double bezel)"],
             "III-C": ["gold + a pointed crest tab", "with a gem (RECOMMENDED)"]}
    for v in VARIANTS:
        h = Image.open(os.path.join(CACHE, "hero_%s.png" % vid(v)))
        im.alpha_composite(h, (x, 112))
        colr = (255, 214, 120) if v[1] == 3 else ((200, 230, 255) if v[1] == 2 else (190, 190, 200))
        if v[2] == RECOMMEND:
            d.rounded_rectangle([x - 4, 108, x + h.width + 2, 112 + h.height + 64], radius=10, outline=(255, 200, 70), width=2)
        d.text((x + 10, 112 + h.height + 2), v[0], font=f_num(26), fill=colr)
        for i, s in enumerate(descr[vid(v)]):
            L(x + 12, 112 + h.height + 32 + i * 16, s)
        x += h.width + 12
    w150 = Image.open(os.path.join(CACHE, "wheel_mixed150.png"))
    im.alpha_composite(w150, (x + 10, 96))
    L(x + 30, 96 + w150.height - 6, "r = 150, mixed (III-C, I, II, I, III-C, II)", (170, 170, 182), f_mono(12, False))
    # vision check: hero-small tiles
    y0 = 112 + 260 + 62
    d.text((30, y0), "VISION CHECK", font=f_num(32), fill=(255, 214, 64))
    L(250, y0 + 12, "rows: colour / greyscale / deuteranopia / protanopia (Machado 2009, full severity)", (175, 175, 190))
    sm = Image.open(os.path.join(CACHE, "small_I.png"))
    cw, ch = sm.width + 18, sm.height + 10
    tx0, ty0 = 140, y0 + 60
    for j, v in enumerate(VARIANTS):
        d.text((tx0 + j * cw + 10, ty0 - 22), v[0], font=f_ui(15, b"Bold SemiCondensed"), fill=(220, 220, 230))
    for r, (vn, fn) in enumerate(VIEWS):
        d.text((30, ty0 + r * ch + ch // 2 - 12), vn, font=f_ui(17, b"Bold SemiCondensed"), fill=(200, 200, 215))
        for j, v in enumerate(VARIANTS):
            t = fn(Image.open(os.path.join(CACHE, "small_%s.png" % vid(v))))
            im.alpha_composite(t, (tx0 + j * cw, ty0 + r * ch))
    # r = 60 wheels, same 4 views
    wx0 = tx0 + 5 * cw + 40
    d.text((wx0, y0), "r = 60", font=f_num(32), fill=(255, 214, 64))
    w0 = Image.open(os.path.join(CACHE, "wheel_I.png"))
    ww = w0.width + 6
    for j, v in enumerate(VARIANTS):
        d.text((wx0 + j * ww + 20, ty0 - 22), v[0].split()[0], font=f_ui(15, b"Bold SemiCondensed"), fill=(220, 220, 230))
        for r, (vn, fn) in enumerate(VIEWS):
            t = fn(Image.open(os.path.join(CACHE, "wheel_%s.png" % vid(v))))
            t = t.resize((int(t.width * ch / t.height * 0.98), int(ch * 0.98)), Image.LANCZOS) if t.height > ch else t
            im.alpha_composite(t, (wx0 + j * ww, ty0 + r * ch))
    # roster with the recommended III
    ry = ty0 + 4 * ch + 20
    d.text((30, ry), "EVERY PROGRAM  (III = option C)", font=f_num(30), fill=(255, 214, 64))
    t0 = Image.open(os.path.join(CACHE, "EXPLOIT_3.png"))
    rcw = t0.width + 8
    for j, p in enumerate(ORDER):
        d.text((110 + j * rcw + 10, ry + 40), p, font=f_ui(14, b"Bold SemiCondensed"), fill=PROGRAMS[p]["col"])
    yy = ry + 58
    for k in (1, 2, 3):
        tt = Image.open(os.path.join(CACHE, "EXPLOIT_%d.png" % k))
        d.text((40, yy + tt.height // 2 - 18), ["I", "II", "III"][k - 1], font=f_num(34), fill=(200, 200, 215))
        for j, p in enumerate(ORDER):
            t = Image.open(os.path.join(CACHE, "%s_%d.png" % (p, k)))
            im.alpha_composite(t, (110 + j * rcw, yy + tt.height - t.height))
        gx = 110 + 9 * rcw + 20
        g = grey(Image.open(os.path.join(CACHE, "EXPLOIT_%d.png" % k)))
        im.alpha_composite(g, (gx, yy + tt.height - g.height))
        yy += tt.height + 6
    L(110 + 9 * rcw + 24, ry + 40, "greyscale", (170, 170, 182))
    nx = 110 + 9 * rcw + 20 + t0.width + 30
    notes = ["Why C: the crest is one big mark on the", "slice's outer centre; it survives r = 60,", "grey and both CVD sims (a bright pointed",
             "bump vs a flat rim). A's spikes read at", "hero size but merge into a jagged rim at", "r = 60; B reads as a thick rim there, but", "its notches vanish below r = 100.",
             "All three stand past the rim: the wheel", "frame (other agent) must leave ~34 px", "(master) of room, or the crest overlaps it."]
    for i, s in enumerate(notes):
        L(nx, ry + 50 + i * 19, s)
    out = bloom(im.convert("RGB"), 1, 0.28, 0.66)
    out = out.crop((0, 0, W, yy + 20))
    out.save(os.path.join(OUT, "tiers.png"))
    print("saved tiers.png", out.size, flush=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("render", "all"):
        render()
    if what in ("compose", "all"):
        compose()
