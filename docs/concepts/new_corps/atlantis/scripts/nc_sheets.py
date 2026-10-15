"""New corps: the 2D sheets (identity board, crest + icons, boss wheel). Identical copy in both scripts/ folders.

python nc_sheets.py <aurelian|tethys> [identity|crest|wheel|all] [backdrop=<png>]
"""
import math
import os
import random
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from PIL import Image, ImageChops, ImageDraw, ImageFilter  # noqa: E402

import nc_kit as K  # noqa: E402
from nc_kit import SL, U  # noqa: E402
from nc_text import TEXT  # noqa: E402

W, H = 2560, 1440
CREAM = (246, 240, 222)
RED_D = (232, 20, 30)


# ------------------------------------------------------------------ colour maths (clash check)
def _lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lab(rgb):
    r, g, b = _lin(np.array(rgb, np.float64))
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b)
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def de(a, b):
    la, lb = lab(a), lab(b)
    return math.sqrt(sum((p - q) ** 2 for p, q in zip(la, lb)))


def hue(c):
    import colorsys
    h, s, v = colorsys.rgb_to_hsv(*(x / 255 for x in c))
    return h * 360


# ------------------------------------------------------------------ type accent samples
def type_accent(corp, w=900, h=150):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if corp == "aurelian":
        tv = K.col(corp, "secondary")
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, w, h], fill=tv + (255,))
        rng = random.Random(4)
        for _ in range(260):                                      # travertine pores
            x, y = rng.uniform(0, w), rng.uniform(0, h)
            d.ellipse([x, y, x + rng.uniform(2, 9), y + rng.uniform(1, 3)], fill=(196, 176, 136, 255))
        for yy in range(0, h, 9):
            d.line([(0, yy + rng.uniform(-2, 2)), (w, yy + rng.uniform(-2, 2))], fill=(222, 204, 166, 120), width=1)
        f = U.F(U.PLEX_M, 54)
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        U.text(lay, (w / 2, h / 2), "AVRELIAN " + K.DOT + " CONCORD", f, (255, 255, 255), "mm", 13)
        m = lay.split()[3]
        im = SL.over(im, (255, 248, 230), SL.shift(m, 2, 3))     # carved: light lower lip
        im = SL.over(im, (92, 70, 44), SL.shift(m, -2, -2))      # dark upper edge
        im = SL.over(im, (120, 96, 62), m)
        # one neon tube line under it
        line = Image.new("L", im.size, 0)
        ImageDraw.Draw(line).line([(60, h - 22), (w - 60, h - 22)], fill=255, width=4)
        im = U.add_glow(im, line, K.col(corp, "primary"), 8, 1.0)
        im = SL.over(im, (220, 255, 240), line)
    else:
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, w, h], fill=(6, 17, 42, 255))
        f = U.F(U.PLEX_M, 84)
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        U.text(lay, (w / 2, h / 2 - 6), "tethys / deep", f, (255, 255, 255), "mm", 8)
        m = lay.split()[3]
        cut = Image.new("L", im.size, 255)
        ImageDraw.Draw(cut).rectangle([0, h / 2 + 4, w, h / 2 + 8], fill=0)   # the waterline cut
        m = ImageChops.multiply(m, cut)
        bc = K.col(corp, "primary")
        im = U.add_glow(im, m, bc, 12, 1.1)
        im = SL.over(im, (190, 214, 255), m)
        rng = random.Random(9)
        for _ in range(16):
            x, y, r = rng.uniform(40, w - 40), rng.uniform(10, h - 10), rng.uniform(2, 6)
            ImageDraw.Draw(im).ellipse([x - r, y - r, x + r, y + r], outline=(150, 190, 255, 160), width=1)
        U.text(im, (w - 20, h - 18), "-412 m", U.F(U.MONO, 20), (124, 242, 228), "rm", 2)
    return im


# ------------------------------------------------------------------ corp paper memo
def memo(corp, w=760, h=600, seed=3):
    t = TEXT[corp]
    p = U.paper_tex(w, h, seed=seed)
    pc = K.col(corp, "primary")
    dk = K.col(corp, "dark")
    d = ImageDraw.Draw(p)
    d.rectangle([0, 0, w, 96], fill=dk + (255,))
    g = K.mask(K.GLYPHS[corp]["crest"], 76)
    p.alpha_composite(K.tint(g, pc), (22, 10))
    U.text(p, (116, 34), K.CORPS[corp]["letterhead"], U.F(U.PLEX_M, 30), (240, 236, 226), "lm", 4 if corp == "aurelian" else 1)
    U.text(p, (116, 68), ("OFFICIVM CLIENTIVM  //  FORM XII-C" if corp == "aurelian" else "service desk  //  ward ops  //  form 7"),
           U.F(U.COUR, 17), (200, 196, 186), "lm", 0.5)
    d.line([(0, 96), (w, 96)], fill=pc + (255,), width=4)
    U.text(p, (36, 136), t["memo_title"], U.F(U.COUR_B, 30), (24, 22, 28), "lm", 0.5)
    y = 186
    for ln in t["memo"]:
        U.text(p, (36, y), ln, U.F(U.COUR, 24), (34, 32, 38), "lm", 0.2)
        y += 32
    # a redaction bar + the stamp
    d.rectangle([380, 196 + 32 * 3, 560, 196 + 32 * 3 + 22], fill=(18, 16, 20, 255))
    st = U.rubber_stamp(t["stamp"], 54, (176, 30, 40), angle=-11, seed=seed + 2)
    p.alpha_composite(st, (w - st.width - 20, 120))
    return p


def dispatch_panel(img, box, lines):
    img = U.term_panel(img, box, title="DISPATCH", accent=(232, 40, 50), tag="VOICE ONLY // NO FEED", seed=6)
    x0, y0, x1, y1 = box
    y = y0 + 58
    for ln in lines:
        U.text(img, (x0 + 22, y), ln, U.F(U.MONO, 22), (255, 214, 214), "la", 0.6)
        y += 32
    d = ImageDraw.Draw(img)
    d.rectangle([x0 + 22 + U.tw(lines[-1], U.F(U.MONO, 22), 0.6) + 6, y - 32, x0 + 34 + U.tw(lines[-1], U.F(U.MONO, 22), 0.6) + 6, y - 8],
                fill=(255, 214, 214, 255))
    return img


# ------------------------------------------------------------------ A. identity board
def identity(corp):
    C = K.CORPS[corp]
    T = TEXT[corp]
    pc, sc, dk = K.col(corp, "primary"), K.col(corp, "secondary"), K.col(corp, "dark")
    img = K.board(W, H, top=tuple(int(v * 0.35) + 6 for v in dk), bot=(4, 4, 8), seed=11)
    # header: crest sticker + name lettering
    cs = K.icon_sticker(K.GLYPHS[corp]["crest"], pc, dk, px=230, seed=3, border=12, gloss_k=0.3)
    img = SL.place(img, cs, 190, 190, angle=-4)
    nm = K.word_sticker([C["name"]], 104, K.grad(pc), seed=5)
    img = SL.place(img, nm, 340 + nm["img"].width // 4, 150, angle=-1.5)
    U.text(img, (350, 262), C["tagline"], U.F(U.PLEX_M, 40), (240, 238, 232), "la", 1.0)
    U.text(img, (352, 316), "EXPLORATORY CONCEPT // NOT CONTENT // a proposal for a 6th / 7th corporation",
           U.F(U.MONO, 19), (150, 160, 178), "la", 1.0)
    # left column: what they sell, house rule, boss, slots
    x0 = 60
    img = K.section(img, (x0, 380), "WHAT THEY SELL", "Night-city terms", pc)
    y = K.para(img, (x0 + 18, 456), K.wrap(T["sells"], 70), 21)
    y = K.para(img, (x0 + 18, y + 6), ["**Controls: "] + K.wrap(T["controls"], 70), 19, col=(190, 200, 214))
    img = U.term_panel(img, (x0, y + 22, x0 + 820, y + 300), title="HOUSE RULE (PROPOSAL)", accent=pc, tag=T["house_title"].split(" ")[0], seed=4)
    yy = K.para(img, (x0 + 22, y + 74), K.wrap(T["house"], 74), 19, col=(214, 232, 236))
    yy = K.para(img, (x0 + 22, yy + 6), K.wrap("BOSS: " + T["boss_rule"], 74), 19, col=pc)
    y = y + 320
    img = K.section(img, (x0, y), "THE SLOTS IT FILLS", "same as the four corps", pc)
    rows = [("Central Server", C["server"] + "  (hub: " + C["hub"] + ")"), ("Enemies", T["enemies"]), ("Exploits", T["exploits"]),
            ("Raids", T["raid"]), ("Event speakers", T["speakers"]), ("Story paths", T["paths"]),
            ("Campaign lost", "verb stamp: " + T["lost"])]
    y += 70
    for k, v in rows:
        U.text(img, (x0 + 18, y), k.upper(), U.F(U.MONO, 17), pc, "la", 1.0)
        ls = K.wrap(v, 62)
        for ln in ls:
            U.text(img, (x0 + 210, y), ln, U.F(U.PLEX, 18), (214, 220, 232), "la", 0)
            y += 25
        y += 6
    # top right: material + landmark (the other two of hue + material + crest + landmark)
    mat = {"aurelian": ["MATERIAL  travertine + white marble, bronze gone verdigris, gilt", "          lettering; neon only as thin trim lines",
                        "LANDMARK  THE CIRCUS AURELIUS: a colosseum tower whose",
                        "          seating rings turn (the HQ, see hq_overview.png)",
                        "DISTRICT  colonnades, arcades, aqueduct data conduits,", "          rooftop statues as billboards, triumph-arch gates"],
           "tethys": ["MATERIAL  pressure glass + riveted titanium, wet black hull,", "          photophore strips; red lights (invisible at depth)",
                      "LANDMARK  ATLANTIS STATION: a pressure spire down the trench",
                      "          wall to the vent (the HQ, see hq_overview.png)",
                      "DISTRICT  the drowned ward: domes, tube walks, kelp streets,", "          sub lanes instead of cars, marine snow for fog"]}[corp]
    for i, ln in enumerate(mat):
        U.text(img, (1340, 92 + i * 34), ln, U.F(U.MONO, 21), (226, 230, 238) if not ln.startswith(" ") else (180, 190, 206), "la", 0.4)
    T_heat = T["heat"]

    # middle column: palette + clash check
    x1 = 960
    img = K.section(img, (x1, 380), "PALETTE", "hue + material + crest + landmark (bible 2.4)", pc)
    sw = [C["primary"], C["secondary"], C["dark"]] + C["extra"]
    for i, (n, h_) in enumerate(sw):
        img = K.swatch(img, x1 + 18 + i * 162, 460, K.hx(h_), n, h_, w=150, h=110)
    roles = ["corp hue: crest, pins, wheel kit, beacons", "tier II / material", "pads, paper bands, backs",
             "world signage" if corp == "aurelian" else "world lights only", "world material" if corp == "aurelian" else "world lights only"]
    for i, r_ in enumerate(roles):
        for j, ln in enumerate(K.wrap(r_, 18)):
            U.text(img, (x1 + 18 + i * 162, 580 + j * 20), ln, U.F(U.PLEX, 15), (170, 180, 196), "la", 0)
    # clash check table
    y = 650
    U.text(img, (x1 + 18, y), "CLASH CHECK (CIE76 dE vs " + C["primary"][0] + ")  -  > 40 clear, 25-40 needs a second cue, < 25 clash",
           U.F(U.MONO, 16), (200, 206, 220), "la", 0.4)
    y += 30
    groups = [("CORPS", K.EXISTING_CORPS), ("ROUTE STATES", K.ROUTE_STATES), ("UI ROLES", K.UI_ROLES)]
    other = "tethys" if corp == "aurelian" else "aurelian"
    groups[0] = ("CORPS", K.EXISTING_CORPS + [(K.CORPS[other]["short"] + " (new)", K.CORPS[other]["primary"][1])])
    for gname, items in groups:
        U.text(img, (x1 + 18, y + 18), gname, U.F(U.MONO, 15), (150, 160, 178), "lm", 1)
        for i, (n, h_) in enumerate(items):
            c = K.hx(h_)
            xx = x1 + 150 + i * 132
            dd = ImageDraw.Draw(img)
            dd.rectangle([xx, y, xx + 54, y + 36], fill=pc + (255,))
            dd.rectangle([xx + 54, y, xx + 108, y + 36], fill=c + (255,))
            e = de(pc, c)
            cc = (123, 224, 123) if e > 40 else ((255, 176, 0) if e > 25 else (255, 68, 51))
            U.text(img, (xx + 54, y + 50), "%s %.0f" % ("ok" if e > 40 else ("cue" if e > 25 else "CLASH"), e), U.F(U.MONO, 14), cc, "mm", 0.4)
            nm_ = n.split(" (")[0][:14]
            U.text(img, (xx + 54, y + 68), nm_, U.F(U.PLEX, 13), (150, 160, 178), "mm", 0)
        y += 92
    # squint strip: all seven corp hues blurred, and in greyscale
    U.text(img, (x1 + 18, y + 4), "SQUINT TEST (blur 14 px) and GREYSCALE", U.F(U.MONO, 16), (200, 206, 220), "la", 0.4)
    y += 30
    hues = [K.hx(h_) for _, h_ in K.EXISTING_CORPS] + [K.col("aurelian", "primary"), K.col("tethys", "primary")]
    names = ["MER", "SOL", "HAL", "ORB", "CELL", "AUR", "TET"]
    strip = Image.new("RGBA", (7 * 112, 90), (12, 11, 18, 255))
    ds = ImageDraw.Draw(strip)
    for i, c in enumerate(hues):
        ds.ellipse([i * 112 + 16, 8, i * 112 + 96, 82], fill=c + (255,))
    bl = strip.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(bl, (x1 + 18, y))
    gr = strip.convert("L").convert("RGBA")
    img.alpha_composite(gr, (x1 + 18, y + 100))
    for i, n in enumerate(names):
        U.text(img, (x1 + 18 + i * 112 + 56, y + 204), n, U.F(U.MONO, 15), (200, 206, 220), "mm", 1)
    y += 232
    ta = type_accent(corp, w=820, h=136)
    img.alpha_composite(ta, (x1 + 18, y))
    U.text(img, (x1 + 18, y + 146), "TYPE ACCENT", U.F(U.MONO, 16), pc, "la", 1)
    yy = y + 172
    for ln in K.wrap(T["type_accent"], 92):
        U.text(img, (x1 + 18, yy), ln, U.F(U.PLEX, 16), (190, 200, 214), "la", 0)
        yy += 22

    # right column: voice
    x2 = 1880
    img = K.section(img, (x2, 380), "TONE OF VOICE", None, pc)
    yy = 430
    for ln in K.wrap(T["tone"], 56):
        U.text(img, (x2 + 18, yy), ln, U.F(U.PLEX, 19), (214, 220, 232), "la", 0)
        yy += 26
    p = memo(corp, w=600, h=560)
    img = U.paste_paper(img, p, (x2 + 20, yy + 20), angle=1.6, sh=0.75)
    U.text(img, (x2 + 18, yy + 600), "corp paper = intercepted documents (Courier Prime)", U.F(U.MONO, 15), (150, 160, 178), "la", 0.4)
    img = dispatch_panel(img, (x2, yy + 640, 2520, yy + 790), K.wrap(" ".join(TEXT[corp]["dispatch"]), 50))
    y = yy + 812
    U.text(img, (x2 + 18, y), "HEAT ON THEIR STREETS (bible 3.15 bands)", U.F(U.MONO, 17), pc, "la", 1.0)
    for ln in T_heat:
        y += 26
        U.text(img, (x2 + 18, y), ln, U.F(U.PLEX, 18), (214, 220, 232), "la", 0)
    return img


# ------------------------------------------------------------------ B. crest + icons
def crest_icons(corp, mapbg=None):
    C = K.CORPS[corp]
    pc, sc, dk = K.col(corp, "primary"), K.col(corp, "secondary"), K.col(corp, "dark")
    img = K.board(W, H, top=tuple(int(v * 0.3) + 6 for v in dk), bot=(4, 4, 8), seed=13)
    tt = K.word_sticker(["CREST + ICONS"], 64, U.FILL_YELLOW, seed=9)
    img = SL.place(img, tt, 250, 80, angle=-2)
    U.text(img, (460, 80), C["name"] + "  //  crest: " + C["crest"] + "  //  vinyl = things that never change",
           U.F(U.MONO, 22), (200, 206, 220), "lm", 1)
    # 1. the crest: big vinyl, flat mask, sizes
    img = K.section(img, (60, 160), "THE CREST", "flat silhouette (the 16 px rule) + vinyl + sizes", pc)
    cs = K.icon_sticker(K.GLYPHS[corp]["crest"], pc, dk, px=300, seed=3, border=12, gloss_k=0.3)
    img = SL.place(img, cs, 260, 440, angle=-3)
    g = K.mask(K.GLYPHS[corp]["crest"], 240)
    plate = Image.new("RGBA", (260, 260), (240, 238, 232, 255))
    plate.alpha_composite(K.tint(g, (17, 17, 17)), (10, 10))
    img.alpha_composite(plate, (470, 300))
    xx = 470
    for px in (64, 32, 16):
        gg = K.mask(K.GLYPHS[corp]["crest"], px)
        img.alpha_composite(K.tint(gg, pc), (xx, 600 - px // 2))
        U.text(img, (xx + px // 2, 640), "%d px" % px, U.F(U.MONO, 14), (150, 160, 178), "mm", 0)
        xx += px + 40
    # 2. site marker variants on a map strip
    img = K.section(img, (800, 160), "SITE MARKER (bible 4.5 grammar)", "pad + icon disc + state ring + tier pips", pc)
    box = (800, 230, 1620, 660)
    strip = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), (14, 14, 22, 255))
    if mapbg and os.path.exists(mapbg):
        bg = Image.open(mapbg).convert("RGBA")
        strip = U.fit_cover(bg, strip.width, strip.height)
        strip = U.grade(strip, dim=0.45, blur=2.0, sat=0.9)
    img.alpha_composite(strip, box[:2])
    states = [("notyet", 1, "not yet", False), ("next", 1, "selectable", False), ("next", 3, "T3", False),
              ("yours", 2, "cleared", True)]
    for i, (av, tier, lab, clr) in enumerate(states):
        x = box[0] + 110 + i * 200
        img = K.site_marker(img, x, box[1] + 230, corp, tier=tier, avail=av, k=1.5, cleared=clr)
        U.text(img, (x, box[1] + 330), lab, U.F(U.MONO, 17), (220, 222, 232), "mm", 1)
    U.text(img, (box[0] + 16, box[3] - 22), "crest in the corp hue on the corp-dark disc; rings stay route orange / white / lime",
           U.F(U.MONO, 15), (170, 180, 196), "la", 0.4)
    # boss marker: crest + TARGET
    # 3. site-type icons (vinyl stickers)
    img = K.section(img, (60, 700), "SITE TYPES (vinyl stickers)", "what each ordinary Site is; the Site file + node backdrop use them", pc)
    sites = K.GLYPHS[corp]["sites"]
    step = 1560 // len(sites)
    for i, (nm, desc, fn) in enumerate(sites):
        x = 140 + i * step
        st = K.icon_sticker(fn, (250, 248, 242), dk, px=150, seed=20 + i, ring_col=pc)
        img = SL.place(img, st, x, 880, angle=[-4, 3, -2, 5, -3, 2, -1][i])
        ws = K.word_sticker([nm], 30, K.grad(pc), seed=30 + i, border=8, jitter=1.5)
        img = SL.place(img, ws, x, 1002, angle=[2, -2, 1, -1, 2, -2, 1][i], scale=0.9)
        U.text(img, (x, 1052), desc, U.F(U.PLEX, 16), (190, 200, 214), "mm", 0)
    # 3b. the 32 px read + the twin check (soft IoU of the 32 px silhouettes, every new icon against every other)
    img = K.section(img, (60, 1092), "32 PX + TWIN CHECK", "every icon at 32 and 16 px; highest soft IoU pairs (bible 3.5: keep < 0.68)", pc)
    allg = icon_pool()
    mine = [(n, f) for n, f in allg if n.startswith(K.CORPS[corp]["short"])]
    for i, (n, f) in enumerate(mine):
        x = 80 + i * 96
        img.alpha_composite(K.tint(K.mask(f, 32), (240, 240, 244)), (x, 1170))
        img.alpha_composite(K.tint(K.mask(f, 16), (240, 240, 244)), (x + 40, 1186))
    pairs = twin_pairs(allg)
    y = 1240
    for (iou, a, b) in pairs[:4]:
        okc = (123, 224, 123) if iou < 0.68 else (255, 68, 51)
        U.text(img, (80, y), "%.2f  %s  <>  %s" % (iou, a, b), U.F(U.MONO, 18), okc, "la", 0.4)
        y += 28
    U.text(img, (80, y + 6), "max %.2f across %d new icons + crests + emblems: %s" % (pairs[0][0], len(allg), "no twins" if pairs[0][0] < 0.68 else "CHECK"),
           U.F(U.MONO, 18), (210, 214, 226), "la", 0.4)
    # 4. boss emblem
    img = K.section(img, (1700, 160), "BOSS EMBLEM (reference)", "boss wheel + emblem moved to boss_wheel_v2", pc)
    if corp == "aurelian":                     # review 2: emoji style (flat colour, thick outline), the thumb is the pick
        px = 270
        cart = K.emblem_thumb_cartoon(512)
        art = cart.resize((px * SL.SS, px * SL.SS), Image.LANCZOS)
        pad = Image.new("RGBA", (art.width + 80 * SL.SS, art.height + 80 * SL.SS), (0, 0, 0, 0))
        pad.alpha_composite(art, (40 * SL.SS, 40 * SL.SS))
        sd = SL.build_sticker(pad, border=10, gloss_k=0.25, seed=60)
        img = SL.place(img, sd, 1850, 430, angle=-3)
        for j, mpx in enumerate((64, 32)):
            img.alpha_composite(cart.resize((mpx, mpx), Image.LANCZOS), (2300 + j * 90, 300 - mpx // 2))
            U.text(img, (2300 + j * 90 + mpx // 2, 350), "%d px" % mpx, U.F(U.MONO, 14), (150, 160, 178), "mm", 0)
        U.text(img, (2010, 520 - 30), "emoji-style thumbs-down: gilt laurel cuff, purple sleeve", U.F(U.MONO, 14), (180, 190, 206), "la", 0)
    else:
        be = K.icon_sticker(K.GLYPHS[corp]["boss"], pc, (10, 8, 14), px=260, seed=41, ring_col=sc, gloss_k=0.3)
        img = SL.place(img, be, 1860, 440, angle=4)
    if corp != "aurelian":
        bm = K.mask(K.GLYPHS[corp]["boss"], 64)
        img.alpha_composite(K.tint(bm, pc), (2040, 408))
        U.text(img, (2072, 488), "64 px", U.F(U.MONO, 14), (150, 160, 178), "mm", 0)
        bm = K.mask(K.GLYPHS[corp]["boss"], 24)
        img.alpha_composite(K.tint(bm, pc), (2140, 428))
        U.text(img, (2152, 488), "24", U.F(U.MONO, 14), (150, 160, 178), "mm", 0)
    for i, ln in enumerate(K.wrap(TEXT[corp]["boss_rule"], 40)):
        U.text(img, (2010, 540 + i * 24), ln, U.F(U.PLEX, 17), (190, 200, 214), "la", 0)
    # 5. letterhead mock
    img = K.section(img, (1700, 720), "CORP PAPER LETTERHEAD", "intercepted document; Courier Prime fields", pc)
    p = letterhead(corp)
    img = U.paste_paper(img, p, (1730, 790), angle=-1.2, sh=0.8)
    U.text(img, (60, 1400), "Proposal sheet. Glyphs are procedural (nc_kit.py), white silhouettes with ink keylines; no real brands.",
           U.F(U.MONO, 16), (130, 140, 160), "la", 0.4)
    return img


def icon_pool():
    out = []
    for c in ("aurelian", "tethys"):
        g = K.GLYPHS[c]
        sh = K.CORPS[c]["short"]
        out.append((sh + " crest", g["crest"]))
        out.append((sh + " boss", g["boss"]))
        if g.get("sub_mark"):
            out.append((sh + " sub-mark", g["sub_mark"]))
        out += [(sh + " " + n, f) for n, _, f in g["sites"]]
    return out


def twin_pairs(pool):
    arrs = []
    for n, f in pool:
        a = np.asarray(K.mask(f, 32).filter(ImageFilter.GaussianBlur(1.0)), np.float32) / 255
        arrs.append(a)
    res = []
    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            iou = np.minimum(arrs[i], arrs[j]).sum() / max(1e-6, np.maximum(arrs[i], arrs[j]).sum())
            res.append((float(iou), pool[i][0], pool[j][0]))
    return sorted(res, reverse=True)


def crest_options(corp="tethys"):
    pc, dk = K.col(corp, "primary"), K.col(corp, "dark")
    img = K.board(W, H, top=tuple(int(v * 0.35) + 6 for v in dk), bot=(4, 4, 8), seed=19)
    tt = K.word_sticker(["CREST OPTIONS"], 60, U.FILL_YELLOW, seed=9)
    img = SL.place(img, tt, 240, 80, angle=-2)
    U.text(img, (470, 80), "TETHYS DEEP  //  a crest built from waves, round, with a moon feel  //  one pick",
           U.F(U.MONO, 22), (210, 214, 226), "lm", 1)
    notes = {"A  TIDE WHIRL": "DESIGNER PICK (review 2): three crests turning round a calm centre, the TIDE cycle as a mark; reads as waves AND as curling arms (the octopus boss).",
             "B  MOONWAVE": "A full moon cut by three rolling swells. Strong moon, but busy: the cuts fill in below 32 px.",
             "C  CRESCENT SURF": "A crescent whose inner edge IS a breaking wave, spray at the lip. Was the first pick; kept as an alternative.",
             "D  DEEP SWELL": "A seal of stacked swells, the top one breaking. Calm and corporate, but stripes at small size."}
    for i, (name, fn) in enumerate(K.CREST_OPTIONS):
        x = 60 + i * 620
        pick = name.startswith("A")
        st = K.icon_sticker(fn, pc, dk, px=330, seed=50 + i, gloss_k=0.3, ring_col=(255, 255, 255) if pick else None)
        img = SL.place(img, st, x + 270, 420, angle=[-3, 2, -2, 3][i])
        plate = Image.new("RGBA", (200, 200), (240, 238, 232, 255))
        plate.alpha_composite(K.tint(K.mask(fn, 180), (17, 17, 17)), (10, 10))
        img.alpha_composite(plate, (x + 20, 700))
        xx = x + 250
        for px in (64, 32, 16):
            img.alpha_composite(K.tint(K.mask(fn, px), pc), (xx, 800 - px // 2))
            U.text(img, (xx + px // 2, 850), "%d" % px, U.F(U.MONO, 14), (150, 160, 178), "mm", 0)
            xx += px + 30
        U.text(img, (x + 20, 930), name + ("   << PICK" if pick else ""), U.F(U.ANTON, 44), pc if pick else (230, 230, 236), "la", 1)
        for j, ln in enumerate(K.wrap(notes[name], 46)):
            U.text(img, (x + 20, 994 + j * 26), ln, U.F(U.PLEX, 20), (200, 208, 222), "la", 0)
    img = U.term_panel(img, (60, 1150, 1700, 1400), title="ORIGINALITY + WHERE THE NAUTILUS WENT", accent=pc, seed=5)
    lines = ["Mood reference only (flowing waves, one bold round shape). Not derived from any existing emblem: no circle-with-",
             "crescent-above-three-wave-lines layout, no feather or moon-over-water arrangement; in C the wave IS the crescent.",
             "The old NAUTILUS crest is kept as the ATLANTIS STATION sub-brand mark (the HQ arcology's own signage, the dossier",
             "footer, the HQ netrun's gate sticker). It also retires the 'shell' read from the Site icons, so no twin."]
    for j, ln in enumerate(lines):
        U.text(img, (82, 1206 + j * 40), ln, U.F(U.PLEX, 20), (214, 224, 236), "la", 0)
    sm = K.icon_sticker(K.g_nautilus, pc, dk, px=180, seed=61, gloss_k=0.3)
    img = SL.place(img, sm, 1960, 1260, angle=-4)
    U.text(img, (2120, 1260), "ATLANTIS STATION", U.F(U.ANTON, 34), (230, 230, 236), "la", 1)
    U.text(img, (2120, 1304), "sub-brand mark (was the crest)", U.F(U.MONO, 16), (160, 170, 186), "la", 0.4)
    return img


def letterhead(corp, w=780, h=600):
    C = K.CORPS[corp]
    T = TEXT[corp]
    pc, dk = K.col(corp, "primary"), K.col(corp, "dark")
    p = U.paper_tex(w, h, seed=21, fold=False)
    d = ImageDraw.Draw(p)
    g = K.mask(K.GLYPHS[corp]["crest"], 110)
    if corp == "aurelian":
        p.alpha_composite(K.tint(g, dk), (w // 2 - 55, 24))
        U.text(p, (w / 2, 160), "AVRELIAN " + K.DOT + " CONCORD", U.F(U.PLEX_M, 30), dk, "mm", 10)
        U.text(p, (w / 2, 194), "HOUSE OF CLIENTS  " + K.DOT + "  OFFICE OF THE DOLE  " + K.DOT + "  LVDI ET CIRCENSES", U.F(U.PLEX_M, 14), (120, 100, 80), "mm", 3)
        d.line([(60, 214), (w - 60, 214)], fill=pc + (255,), width=3)
        d.line([(60, 220), (w - 60, 220)], fill=dk + (255,), width=1)
        fields = [("CLIENT", "CELL-9 (UNREGISTERED)"), ("LOT", "XXIV / SEAT CXII"), ("PATRON", "House Aurelian, Ward VII"),
                  ("SUBJECT", "Arrears of attendance")]
    else:
        d.rectangle([0, 0, w, 150], fill=dk + (255,))
        p.alpha_composite(K.tint(K.mask(K.GLYPHS[corp]["crest"], 104), pc), (40, 22))
        U.text(p, (170, 62), "tethys / deep", U.F(U.PLEX_M, 46), (200, 220, 255), "lm", 2)
        U.text(p, (172, 108), "atlantis station  .  -412 m  .  pressure-rated correspondence", U.F(U.PLEX, 17), (124, 160, 220), "lm", 1)
        d.rectangle([0, 150, w, 156], fill=pc + (255,))
        fields = [("resident", "cell-9 (no plan on file)"), ("ward", "9 (below the line)"), ("pumps", "PAUSE at 00:30"),
                  ("subject", "breathe plan lapsed")]
    y = 262
    for k, v in fields:
        U.text(p, (70, y), k.upper() + ":", U.F(U.COUR_B, 21), (40, 36, 42), "lm", 0.2)
        U.text(p, (250, y), v, U.F(U.COUR, 21), (40, 36, 42), "lm", 0.2)
        y += 38
    d.line([(70, y + 6), (w - 70, y + 6)], fill=(150, 140, 120, 255), width=1)
    y += 30
    for ln in T["memo"][2:6]:
        U.text(p, (70, y), ln, U.F(U.COUR, 20), (50, 46, 52), "lm", 0.2)
        y += 28
    d.rectangle([70, y + 4, 330, y + 24], fill=(18, 16, 20, 255))
    st = U.rubber_stamp("INTERCEPTED", 46, (176, 30, 40), angle=8, seed=8)
    p.alpha_composite(st, (w - st.width - 20, h - st.height - 10))
    return p


# ------------------------------------------------------------------ E. boss wheel (D4 "lens & rail")
def g_tide():
    m, d = K.new()
    for k, yb in enumerate((150, 256, 362)):
        pts = [(40 + i * 10.8, yb + 34 * math.sin(i / 40 * math.pi * 2.5 + k)) for i in range(41)]
        d.line(pts, fill=255, width=46)
    return m


SLICE_COL = {"SHIM": (255, 61, 168), "OVERFLOW": (255, 61, 168), "DEFRAG": (92, 225, 255), "SANDBOX": (92, 225, 255),
             "NULL": (106, 106, 106), "INFECT": (200, 90, 255), "HOTFIX": (123, 224, 123)}


def boss_wheel(corp, backdrop=None):
    C = K.CORPS[corp]
    pc, sc, dk = K.col(corp, "primary"), K.col(corp, "secondary"), K.col(corp, "dark")
    SS = 2
    img = K.board(W, H, top=tuple(int(v * 0.4) + 6 for v in dk), bot=(4, 4, 8), seed=17)
    if backdrop and os.path.exists(backdrop):
        bg = U.fit_cover(Image.open(backdrop).convert("RGBA"), W, H)
        img = U.grade(bg, dim=0.62, blur=1.5, sat=0.95)
    img = U.vignette(img, 0.5)
    cx, cy, R = 1280, 744, 440
    # darkened pool behind the wheel (bible 3.1)
    pool = Image.new("L", (W, H), 0)
    ImageDraw.Draw(pool).ellipse([cx - R - 160, cy - R - 160, cx + R + 160, cy + R + 160], fill=150)
    img = SL.over(img, (3, 3, 8), pool.filter(ImageFilter.GaussianBlur(80)))
    # work layer at SS
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    X, Y = cx * SS, cy * SS

    def circ(r, **kw):
        d.ellipse([X - r * SS, Y - r * SS, X + r * SS, Y + r * SS], **kw)

    if corp == "aurelian":
        slices = [("VERDICT", 3, "special"), ("SHIM", 14, "slice_exploit"), ("DEFRAG", 12, "slice_firewall"),
                  ("NULL", None, "slice_null"), ("OVERFLOW", 24, "slice_zero_day"), ("SANDBOX", 8, "slice_sandbox")]
        special_fn = K.GLYPHS[corp]["boss"]
    else:
        slices = [("TIDE", 6, "special"), ("SHIM", 12, "slice_exploit"), ("SANDBOX", 10, "slice_sandbox"),
                  ("OVERFLOW", 22, "slice_zero_day"), ("NULL", None, "slice_null"), ("DEFRAG", 14, "slice_firewall")]
        special_fn = g_tide
    # threat ring (counter-rotating, corp colour chevrons) r 500..540
    circ(548, fill=(8, 8, 12, 255))
    for k in range(60):
        a0 = math.radians(-90 + k * 6 + 1)
        a1 = a0 + math.radians(3.4)
        pts = []
        for rr, aa in ((506, a0), (540, a0 + 0.01), (540, a1), (506, a1 - 0.01)):
            pts.append((X + rr * SS * math.cos(aa), Y + rr * SS * math.sin(aa)))
        c = pc if k % 5 else sc
        d.polygon(pts, fill=c + (230 if k % 2 else 140,))
    # bezel r 470..505: corp material
    circ(505, fill=sc + (255,) if corp == "aurelian" else (44, 52, 64, 255))
    circ(470, fill=(12, 10, 16, 255))
    if corp == "aurelian":
        # travertine pores + a verdigris meander (greek key) band
        rng = random.Random(5)
        for _ in range(500):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(474, 503)
            d.ellipse([X + rr * SS * math.cos(a) - 3, Y + rr * SS * math.sin(a) - 1.5, X + rr * SS * math.cos(a) + 4, Y + rr * SS * math.sin(a) + 1.5],
                      fill=(196, 176, 136, 255))
        n = 48
        for k in range(n):
            a = math.radians(k * 360 / n)
            da = math.radians(360 / n)
            pts = []
            for (rr, f) in ((480, 0.0), (496, 0.0), (496, 0.75), (486, 0.75), (486, 0.35), (480, 0.35)):
                aa = a + da * f
                pts.append((X + rr * SS * math.cos(aa), Y + rr * SS * math.sin(aa)))
            d.line(pts, fill=pc + (255,), width=3 * SS)
    else:
        # porthole bezel: brass-steel ring, rivets, a blue glass channel
        circ(500, outline=(120, 104, 76, 255), width=4 * SS)
        for k in range(36):
            a = math.radians(k * 10)
            rr = 488
            x_, y_ = X + rr * SS * math.cos(a), Y + rr * SS * math.sin(a)
            d.ellipse([x_ - 5 * SS, y_ - 5 * SS, x_ + 5 * SS, y_ + 5 * SS], fill=(150, 132, 98, 255), outline=(40, 34, 26, 255), width=SS)
        circ(477, outline=pc + (200,), width=4 * SS)
    # telemetry ring r 440..470
    circ(470, fill=(10, 10, 16, 255))
    circ(441, fill=(0, 0, 0, 0))
    # slices r 172..438
    for i, (nm, val, gl) in enumerate(slices):
        a_c = -90 + i * 60
        a0, a1 = a_c - 29.2, a_c + 29.2
        sc_ = SLICE_COL.get(nm, pc)
        if nm in ("VERDICT", "TIDE"):
            sc_ = pc
        lift = 12 if i == 0 else 0
        ox, oy = lift * math.cos(math.radians(a_c)) * SS, lift * math.sin(math.radians(a_c)) * SS
        base = tuple(int(c * 0.30) for c in sc_)
        d.pieslice([X - 438 * SS + ox, Y - 438 * SS + oy, X + 438 * SS + ox, Y + 438 * SS + oy], a0, a1, fill=base + (255,))
    # screens: scanlines + corp pattern inside each slice
    tex = Image.new("RGBA", L.size, (0, 0, 0, 0))
    td = ImageDraw.Draw(tex)
    for yy in range(0, H * SS, 6):
        td.line([(0, yy), (W * SS, yy)], fill=(0, 0, 0, 60), width=2)
    rng = random.Random(3)
    if corp == "aurelian":
        for k in range(26):                                     # arcade arches as a faint screen motif
            a = math.radians(rng.uniform(0, 360))
            rr = rng.uniform(220, 410)
            x_, y_ = X + rr * SS * math.cos(a), Y + rr * SS * math.sin(a)
            s_ = rng.uniform(14, 26) * SS
            td.arc([x_ - s_, y_ - s_, x_ + s_, y_ + s_], 180, 360, fill=pc + (60,), width=2 * SS)
            td.line([(x_ - s_, y_), (x_ - s_, y_ + s_ * 1.4)], fill=pc + (60,), width=2 * SS)
            td.line([(x_ + s_, y_), (x_ + s_, y_ + s_ * 1.4)], fill=pc + (60,), width=2 * SS)
    else:
        for k in range(140):                                    # caustic net + rising bubbles
            a = math.radians(rng.uniform(0, 360))
            rr = rng.uniform(190, 430)
            x_, y_ = X + rr * SS * math.cos(a), Y + rr * SS * math.sin(a)
            s_ = rng.uniform(2, 7) * SS
            td.ellipse([x_ - s_, y_ - s_, x_ + s_, y_ + s_], outline=(150, 200, 255, 70), width=SS)
    wm = Image.new("L", L.size, 0)
    ImageDraw.Draw(wm).ellipse([X - 438 * SS, Y - 438 * SS, X + 438 * SS, Y + 438 * SS], fill=255)
    ImageDraw.Draw(wm).ellipse([X - 172 * SS, Y - 172 * SS, X + 172 * SS, Y + 172 * SS], fill=0)
    tex.putalpha(ImageChops.multiply(tex.split()[3], wm))
    L.alpha_composite(tex)
    d = ImageDraw.Draw(L)
    # slice gaps
    for i in range(6):
        a = math.radians(-90 + i * 60 + 30)
        d.line([(X + 172 * SS * math.cos(a), Y + 172 * SS * math.sin(a)), (X + 440 * SS * math.cos(a), Y + 440 * SS * math.sin(a))],
               fill=(6, 6, 10, 255), width=7 * SS)
    # dim the inactive slices (68 %), cream outline on the active one
    dimm = Image.new("L", L.size, 0)
    dd = ImageDraw.Draw(dimm)
    dd.pieslice([X - 440 * SS, Y - 440 * SS, X + 440 * SS, Y + 440 * SS], -90 + 30, -90 + 330, fill=82)
    dd.ellipse([X - 172 * SS, Y - 172 * SS, X + 172 * SS, Y + 172 * SS], fill=0)
    L = SL.over(L, (0, 0, 0), ImageChops.multiply(dimm, L.split()[3]))
    d = ImageDraw.Draw(L)
    d.arc([X - 450 * SS, Y - 450 * SS, X + 450 * SS, Y + 450 * SS], -90 - 29, -90 + 29, fill=CREAM + (255,), width=4 * SS)
    for a in (-90 - 29, -90 + 29):
        ar = math.radians(a)
        d.line([(X + 184 * SS * math.cos(ar), Y + 184 * SS * math.sin(ar)), (X + 450 * SS * math.cos(ar), Y + 450 * SS * math.sin(ar))],
               fill=CREAM + (255,), width=4 * SS)
    # telemetry text + readout rail over the pointer
    tel = ("%s // %s // PHASE 1 // " % (C["server"], C["house"])) * 4
    f = U.F(U.MONO, 15 * SS)
    n = len(tel)
    for i, ch in enumerate(tel):
        a = -90 + 52 + i * (256 / n)
        ar = math.radians(a)
        rr = 455 * SS
        g = Image.new("RGBA", (30 * SS, 30 * SS), (0, 0, 0, 0))
        ImageDraw.Draw(g).text((15 * SS, 15 * SS), ch, font=f, fill=pc + (170,), anchor="mm")
        g = g.rotate(-a - 90, Image.BICUBIC)
        L.alpha_composite(g, (int(X + rr * math.cos(ar) - 15 * SS), int(Y + rr * math.sin(ar) - 15 * SS)))
    d = ImageDraw.Draw(L)
    for a0, a1 in ((-140, -98), (-82, -40)):
        d.arc([X - 468 * SS, Y - 468 * SS, X + 468 * SS, Y + 468 * SS], a0, a1, fill=pc + (255,), width=24 * SS)
    rail = "%s 24 // CRIT // " % ("OVERFLOW")
    for side, (a0, a1) in ((0, (-140, -98)), (1, (-82, -40))):
        s_ = "VERDICT // MARK" if (side == 1 and corp == "aurelian") else ("TIDE // HIGH" if side == 1 else "SHIM 14 // GOOD")
        if corp == "tethys" and side == 0:
            s_ = "SHIM 12 // GOOD"
        nn = len(s_)
        for i, ch in enumerate(s_):
            a = a0 + 3 + i * ((a1 - a0 - 6) / max(1, nn - 1))
            ar = math.radians(a)
            rr = 468 * SS
            g = Image.new("RGBA", (30 * SS, 30 * SS), (0, 0, 0, 0))
            ImageDraw.Draw(g).text((15 * SS, 15 * SS), ch, font=U.F(U.MONO, 16 * SS), fill=(10, 10, 14, 255), anchor="mm")
            g = g.rotate(-a - 90, Image.BICUBIC)
            L.alpha_composite(g, (int(X + rr * math.cos(ar) - 15 * SS), int(Y + rr * math.sin(ar) - 15 * SS)))
    # hub
    d = ImageDraw.Draw(L)
    circ(172, fill=(8, 8, 12, 255))
    circ(164, fill=tuple(int(c * 0.6) for c in dk) + (255,), outline=pc + (255,), width=3 * SS)
    for k in range(10):                                         # corp chevron sweep
        a = math.radians(-60 + k * 12)
        rr = 150 * SS
        x_, y_ = X + rr * math.cos(a), Y + rr * math.sin(a)
        d.line([(x_, y_), (X + (rr - 20 * SS) * math.cos(a + 0.12), Y + (rr - 20 * SS) * math.sin(a + 0.12))], fill=pc + (40 + k * 18,), width=5 * SS)
    em = K.mask(K.GLYPHS[corp]["boss"], 150 * SS)
    L.alpha_composite(K.tint(SL.dilate(em, 6 * SS), (6, 6, 10)), (int(X - 75 * SS), int(Y - 120 * SS)))
    L.alpha_composite(K.tint(em, pc), (int(X - 75 * SS), int(Y - 120 * SS)))
    U.text(L, (X, Y + 62 * SS), C["server"], U.F(U.ANTON, 30 * SS), (240, 238, 232), "mm", 1 * SS)
    U.text(L, (X, Y + 98 * SS), C["hub"].title(), U.F(U.PLEX, 18 * SS), (200, 206, 220), "mm", 0)
    img_l = L.resize((W, H), Image.LANCZOS)
    img.alpha_composite(img_l)
    # read blocks (upright): dark ellipse plate, glyph + value
    for i, (nm, val, gl) in enumerate(slices):
        a = math.radians(-90 + i * 60)
        rr = 320
        x_, y_ = cx + rr * math.cos(a), cy + rr * math.sin(a)
        if i == 0:
            x_, y_ = x_ + 10 * math.cos(a), y_ + 10 * math.sin(a)
        pl = Image.new("L", (W, H), 0)
        ImageDraw.Draw(pl).ellipse([x_ - 96, y_ - 46, x_ + 96, y_ + 46], fill=170 if i == 0 else 120)
        img = SL.over(img, (4, 4, 8), pl.filter(ImageFilter.GaussianBlur(8)))
        k_ = 1.0 if i == 0 else 0.7
        wc = tuple(int(255 * k_) for _ in range(3))
        if gl == "special":
            gm = K.mask(special_fn, 64)
            img.alpha_composite(K.tint(SL.dilate(gm, 4), (6, 6, 10)), (int(x_ - 80), int(y_ - 32)))
            img.alpha_composite(K.tint(gm, wc), (int(x_ - 80), int(y_ - 32)))
        else:
            gimg = U.glyph(gl, 60, wc)
            img.alpha_composite(gimg, (int(x_ - 80), int(y_ - 30)))
        s_ = "" if nm == "NULL" else str(val)
        U.text(img, (x_ + 6, y_ + 2), s_, U.F(U.ANTON, 64), wc, "lm", 1)
        U.text(img, (x_, y_ + 58), nm, U.F(U.MONO, 17), tuple(int(c * k_) for c in (200, 206, 220)), "mm", 1)
    # pointer blade + nameplate banner with a crowned blade
    blade = Image.new("L", (W, H), 0)
    bd = ImageDraw.Draw(blade)
    tip = cy - 448
    bd.polygon([(cx - 46, cy - 548), (cx + 46, cy - 548), (cx + 30, cy - 488), (cx, tip), (cx - 30, cy - 488)], fill=255)
    img = U.shadow(img, blade, (4, 6), 6, 0.7)
    img = SL.over(img, CREAM, blade)
    d = ImageDraw.Draw(img)
    d.rectangle([cx - 30, cy - 540, cx + 30, cy - 500], fill=(12, 12, 16, 255))
    U.text(img, (cx, cy - 520), "24" if corp == "aurelian" else "22", U.F(U.ANTON, 32), pc, "mm", 1)
    d.polygon([(cx - 22, cy - 560), (cx - 14, cy - 580), (cx - 6, cy - 562), (cx, cy - 586), (cx + 6, cy - 562), (cx + 14, cy - 580), (cx + 22, cy - 560)],
              fill=pc + (255,))
    ban = (cx - 230, cy - 700, cx + 230, cy - 590)
    m = U.rect_mask((W, H), ban, chamfer=18)
    img = U.shadow(img, m, (5, 8), 8, 0.6)
    img = SL.over(img, tuple(int(c * 0.55) for c in dk), m)
    e = ImageChops.subtract(m, SL.erode(m, 3))
    img = U.add_glow(img, e, pc, 10, 0.8)
    img = SL.over(img, pc, e)
    U.text(img, (cx, cy - 660), C["server"], U.F(U.ANTON, 56), (246, 244, 236), "mm", 2)
    U.text(img, (cx, cy - 612), "%s  |  BOSS  |  PHASE 1" % C["name"], U.F(U.MONO, 17), pc, "mm", 1.5)
    # crest lugs on the threat ring
    for a in (180, 0, 135, 45):
        ar = math.radians(a)
        x_, y_ = cx + 524 * math.cos(ar), cy + 524 * math.sin(ar)
        lug = K.icon_sticker(K.GLYPHS[corp]["crest"], pc, dk, px=70, seed=int(a) + 3, border=5)
        img = SL.place(img, lug, x_, y_, angle=0, shadow=0.6)
    # HP arc under the wheel with phase pips
    hp = Image.new("L", (W, H), 0)
    hd = ImageDraw.Draw(hp)
    for k in range(40):
        a0 = 140 - k * 2.5 + 0.4
        if True:
            hd.arc([cx - 580, cy - 580, cx + 580, cy + 580], 40 + k * 2.5 + 0.4, 40 + (k + 1) * 2.5 - 0.4, fill=255, width=22)
    img = SL.over(img, (60, 210, 90), hp)
    for pct in (0.66, 0.33):
        a = math.radians(40 + 100 * (1 - pct))
        x_, y_ = cx + 580 * math.cos(a) - 11, cy + 580 * math.sin(a) - 11
        ImageDraw.Draw(img).regular_polygon((x_ + 11, y_ + 11, 15), 4, rotation=45, fill=(250, 250, 250, 255), outline=(10, 10, 14, 255))
    U.live_number(img, (cx, cy + 640), "400/400", 64, (123, 224, 123), anchor="mm")
    # callouts (board)
    tt = K.word_sticker(["BOSS WHEEL"], 60, U.FILL_YELLOW, seed=12)
    img = SL.place(img, tt, 210, 80, angle=-2)
    U.text(img, (64, 150), "D4 'lens & rail' frame, tier III corp kit  //  " + C["name"], U.F(U.MONO, 20), (210, 214, 226), "lm", 1)
    notes = {
        "aurelian": ["RIM: travertine bezel with a verdigris meander", "inlay; the threat ring in verdigris + travertine",
                     "LUGS: the laurel-arch crest x4", "SPECIAL: VERDICT (thumb) marks your slice;",
                     "Perfect = OVERCLOCKED, Weak = CORRUPTED", "HUB: The Grand Stand calls a VERDICT each turn",
                     "SCREENS: faint arcade arches (the corp motif)", "P2 idea: gilt plates bolt on, the crowd roars"],
        "tethys": ["RIM: riveted porthole bezel, abyss-blue glass", "channel; threat ring in abyss blue + red",
                   "LUGS: the nautilus crest x4", "SPECIAL: TIDE (three swells): the tide step",
                   "on the rail (LOW / RISING / HIGH / FALLING)", "HUB: The Vent Cap OVERCLOCKS a slice each turn",
                   "SCREENS: caustic net + rising bubbles", "P2 idea: the hub floods (reuses LOCKDOWN water)"],
    }[corp]
    img = U.term_panel(img, (1880, 260, 2500, 640), title="WHAT IS CORP-SPECIFIC", accent=pc, seed=8)
    for i, ln in enumerate(notes):
        U.text(img, (1902, 316 + i * 38), ln, U.F(U.PLEX, 20), (214, 224, 236), "la", 0)
    U.text(img, (60, 1400), "Slice colours stay slice-type colours (bible 2.3); only the frame, lugs, hub and the special carry the corp.",
           U.F(U.MONO, 16), (150, 160, 178), "la", 0.4)
    return img


def main():
    corp = sys.argv[1]
    what = sys.argv[2] if len(sys.argv) > 2 else "all"
    kw = dict(a.split("=", 1) for a in sys.argv[3:] if "=" in a)
    outdir = os.path.join(K.NC, K.CORPS[corp]["folder"])
    if what in ("identity", "all"):
        K.save(identity(corp), os.path.join(outdir, "identity_board.png"))
    if what in ("crest", "all"):
        K.save(crest_icons(corp, kw.get("mapbg")), os.path.join(outdir, "crest_icons.png"))
    if what == "crestopt":
        K.save(crest_options(corp), os.path.join(outdir, "crest_options.png"))
    if what == "wheel_old":
        K.save(boss_wheel(corp, kw.get("backdrop")), os.path.join(outdir, "boss_wheel.png"))


if __name__ == "__main__":
    main()
