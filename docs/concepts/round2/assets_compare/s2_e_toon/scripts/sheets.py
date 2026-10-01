"""Compose the 8 S2 asset sheets (1920x1080, #2A2A2E) from the Blender tiles + painted Pillow pieces.

usage: python sheets.py <tile_dir> <out_dir>
Grid positions are written to <out_dir>/scripts/../layout.json? no: to layout.json beside the sheets,
so the other style can line up panel by panel.
"""
import json
import math
import os
import random
import sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paint2d import (BG, INK, CREAM, font, hx, shade, mix, painted, ink_shape, text_ink, distress, fit, paste_c,
                     drop_shadow, new_sheet, label, tape, rrect_pts, wobble_poly, noise)

TD, OD = sys.argv[1], sys.argv[2]
LAYOUT = {}


def tile(name):
    return Image.open(os.path.join(TD, name + ".png")).convert("RGBA")


def save(img, name):
    img.convert("RGB").save(os.path.join(OD, name), optimize=True)
    print("wrote", name)


# =============================================================== 01 operatives
def polaroid(bust, state, cls, seed):
    W_, H_ = 196, 222
    p = Image.new("RGBA", (W_ + 20, H_ + 20), (0, 0, 0, 0))
    ink_shape(p, rrect_pts(8, 8, W_ + 8, H_ + 8, 6), "#ece2c8", seed=seed, ink=4, amt=0.12, grime=0.18)
    bgc = {"neutral": ("#4a5a68", "#232a34"), "hurt": ("#6a3a3a", "#2a1c22"), "triumphant": ("#c89a4a", "#4a3020"),
           "flatlined": ("#4a4a4a", "#1e1e20")}[state]
    ph = Image.linear_gradient("L").resize((168, 152))
    photo = Image.composite(Image.new("RGB", (168, 152), hx(bgc[1])), Image.new("RGB", (168, 152), hx(bgc[0])), ph)
    photo = Image.blend(photo, painted((168, 152), bgc[0], seed, amt=0.2, grime=0.2), 0.35).convert("RGBA")
    b = fit(bust, 160, 150)
    if state == "flatlined":
        b = ImageOps.grayscale(b.convert("RGB")).convert("RGBA")
        b.putalpha(fit(bust, 160, 150).getchannel("A"))
        b = ImageEnhance.Brightness(b).enhance(0.8)
    photo.alpha_composite(b, ((168 - b.width) // 2, 152 - b.height))
    if state == "hurt":
        d = ImageDraw.Draw(photo)
        d.line([(120, 0), (104, 40), (126, 70), (110, 112)], fill=(240, 236, 220), width=2)      # cracked print
        edge = Image.new("RGBA", (168, 152), (200, 30, 40, 0))
        m = Image.new("L", (168, 152), 0)
        ImageDraw.Draw(m).rectangle([0, 0, 167, 151], outline=150, width=10)
        edge.putalpha(m.filter(ImageFilter.GaussianBlur(5)))
        photo.alpha_composite(edge)
    if state == "flatlined":
        photo = ImageEnhance.Color(photo.convert("RGB")).enhance(0.2).convert("RGBA")
    p.alpha_composite(photo, (22, 22))
    ImageDraw.Draw(p).rectangle([22, 22, 189, 173], outline=INK + (255,), width=2)
    cap = {"neutral": cls.upper(), "hurt": "%s  -  HP 9" % cls.upper(), "triumphant": "%s  !!" % cls.upper(),
           "flatlined": cls.upper()}[state]
    ImageDraw.Draw(p).text((106, 200), cap, font=font("ink", 20), fill=(40, 30, 30), anchor="mm")
    if state == "flatlined":
        st = stamp_text("FLATLINED", (200, 40, 40), 30, seed)
        st = st.rotate(14, expand=True, resample=Image.BICUBIC)
        paste_c(p, st, 106, 110)
    p = p.rotate(random.Random(seed).uniform(-3, 3), expand=True, resample=Image.BICUBIC)
    tape(p, p.width / 2, 16, 70, 20, random.Random(seed).uniform(-8, 8), seed)
    return p


def stamp_text(s, col, size, seed, fnt="stencil", box=True):
    f = font(fnt, size)
    w = int(f.getlength(s)) + 28
    h = size + 22
    t = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    if box:
        d.rounded_rectangle([4, 4, w + 3, h + 3], radius=6, outline=col + (255,), width=4)
    d.text((w / 2 + 4, h / 2 + 4), s, font=f, fill=col + (255,), anchor="mm")
    return distress(t, seed, 0.3, 3)


def sheet01():
    img = new_sheet("01", "OPERATIVES", "Polaroid busts  -  2 classes x 4 states (art_asset B1)")
    cols = {"breaker": 700, "ghost": 1340}
    rows = {"neutral": 225, "hurt": 460, "triumphant": 695, "flatlined": 930}
    LAYOUT["01_operatives"] = {"cells": {}}
    for cls, cx in cols.items():
        text_ink(img, (cx, 96), {"breaker": "BREAKER", "ghost": "GHOST"}[cls], font("title", 30), stroke=3)
        ImageDraw.Draw(img).text((cx + 110, 96), {"breaker": "heavy jacket / antenna-crowbar",
                                                  "ghost": "hood / crystal face mesh"}[cls],
                                 font=font("bodyr", 16), fill=(160, 156, 146), anchor="lm")
    for st, cy in rows.items():
        text_ink(img, (260, cy - 10), st.upper(), font("title", 26), stroke=3, anchor="mm",
                 fill={"neutral": CREAM, "hurt": (255, 120, 110), "triumphant": (255, 210, 110),
                       "flatlined": (170, 170, 170)}[st])
        for cls, cx in cols.items():
            p = polaroid(tile("op_%s_%s" % (cls, st)), st, cls, hash((cls, st)) % 997 if False else len(cls) * 31 + cy)
            pcx, pcy = cx, cy + 12
            sc_ = 0.9
            p = p.resize((int(p.width * sc_), int(p.height * sc_)), Image.LANCZOS)
            drop_shadow(img, p, pcx, pcy)
            paste_c(img, p, pcx, pcy)
            label(img, cx + 200, cy + 10, "%s  -  %s" % (cls.capitalize(), st), size=18)
            LAYOUT["01_operatives"]["cells"]["%s_%s" % (cls, st)] = [pcx, pcy]
    save(img, "01_operatives.png")


# =============================================================== 02 enemies
def sheet02():
    img = new_sheet("02", "ENEMIES", "Busts / holograms with their corporate wheel bezel (B2, B5)")
    items = [("en_manifest", "bz_meridian", "THE MANIFEST", "Meridian boss  -  routing core", "#e8782a"),
             ("en_adjuster", "bz_solace", "CLAIMS ADJUSTER", "Solace elite  -  reads two claims", "#5fd8b0"),
             ("en_drone", "bz_meridian", "COLLECTIONS DRONE", "Meridian regular machine", "#e8782a")]
    LAYOUT["02_enemies"] = {"cells": {}}
    for i, (en, bz, name, sub, col) in enumerate(items):
        cx = 360 + i * 600
        # corporate backdrop disc (painted, inked)
        r = 230
        ink_shape(img, [(cx + math.cos(a / 40 * math.tau) * r, 430 + math.sin(a / 40 * math.tau) * r) for a in range(40)],
                  mix(hx(col), BG, 0.72), seed=i, ink=5, amt=0.2, grime=0.3)
        t = fit(tile(en), 440, 440)
        drop_shadow(img, t, cx, 430)
        paste_c(img, t, cx, 430)
        text_ink(img, (cx, 700), name, font("title", 32), fill=hx(col), stroke=3)
        label(img, cx, 724, sub, size=18)
        b = fit(tile(bz), 380, 150)
        drop_shadow(img, b, cx, 870)
        paste_c(img, b, cx, 870)
        label(img, cx, 960, "bezel: " + ("orange, container stripes" if "meridian" in bz else "mint, helix dots"),
              size=18)
        LAYOUT["02_enemies"]["cells"][en] = [cx, 430]
        LAYOUT["02_enemies"]["cells"][en + "_bezel"] = [cx, 870]
    save(img, "02_enemies.png")


# =============================================================== 03 landmarks
def sheet03():
    img = new_sheet("03", "CORPORATION LANDMARKS", "HQ landmarks on plinths (A2)")
    items = [("lm_ziggurat", "FREIGHT ZIGGURAT", "Meridian Freight Systems", "#e8782a"),
             ("lm_pyramid", "CIVIC PYRAMID", "Halcyon Civic", "#3f7fd8"),
             ("lm_tether", "ORBITAL TETHER", "Orbital Commons", "#9a7ae8")]
    LAYOUT["03_landmarks"] = {"cells": {}}
    for i, (lm, name, corp, col) in enumerate(items):
        cx = 360 + i * 600
        t = fit(tile(lm), 540, 760)
        cy = 920 - t.height / 2
        drop_shadow(img, t, cx, cy)
        paste_c(img, t, cx, cy)
        text_ink(img, (cx, 960), name, font("title", 32), fill=hx(col), stroke=3)
        label(img, cx, 984, corp, size=18)
        LAYOUT["03_landmarks"]["cells"][lm] = [cx, 540]
    save(img, "03_landmarks.png")


# =============================================================== 04 threats
def sheet04():
    img = new_sheet("04", "RAID THREAT TOKENS", "Map-token size (64 px) and 3x (192 px)  (B4)")
    items = [("th_bailiff", "BAILIFF", "armoured  -  slow, heavy", "Solace"),
             ("th_courier", "COURIER", "fast  -  fragile", "Meridian"),
             ("th_customs", "CUSTOMS AGENT", "seals the link behind it", "Meridian")]
    LAYOUT["04_threats"] = {"cells": {}}
    d = ImageDraw.Draw(img)
    for i, (th, name, sub, corp) in enumerate(items):
        cx = 360 + i * 600
        # a strip of city grid map under the small token: link + node discs
        y = 300
        ink_shape(img, rrect_pts(cx - 230, y - 80, cx + 230, y + 80, 14), "#3a3e44", seed=i + 5, ink=4, amt=0.2, grime=0.3)
        d.line([(cx - 190, y + 30), (cx + 190, y + 30)], fill=(232, 176, 48), width=7)
        for nx in (cx - 190, cx + 190):
            d.ellipse([nx - 14, y + 16, nx + 14, y + 44], fill=(200, 208, 216), outline=INK, width=3)
        if th == "th_customs":   # sealed link behind it
            d.line([(cx - 150, y + 30), (cx - 50, y + 30)], fill=(90, 90, 96), width=9)
            for k in range(4):
                d.line([(cx - 140 + k * 25, y + 20), (cx - 128 + k * 25, y + 40)], fill=(232, 120, 42), width=4)
        small = fit(tile(th), 64, 64)
        paste_c(img, small, cx, y + 4)
        label(img, cx, y + 92, "64 px", size=16)
        big = fit(tile(th), 192, 192)
        ink_shape(img, rrect_pts(cx - 150, 470, cx + 150, 770, 20), "#34383e", seed=i + 9, ink=4, amt=0.15, grime=0.2)
        drop_shadow(img, big, cx, 620)
        paste_c(img, big, cx, 620)
        label(img, cx, 782, "192 px (3x)", size=16)
        text_ink(img, (cx, 850), name, font("title", 34), stroke=3)
        label(img, cx, 876, sub, size=18, sub=corp)
        LAYOUT["04_threats"]["cells"][th] = {"small": [cx, y + 4], "big": [cx, 620]}
    save(img, "04_threats.png")


# =============================================================== pictograms (card rows) + icons
def glyph(kind, size=256, col=CREAM):
    """Painted-ink glyphs on transparent ground (drawn at 256, inked)."""
    g = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    s = size / 256.0

    def P(pts):
        return [(x * s, y * s) for x, y in pts]

    def shape(pts, c=col, seed=1, ink=12):
        ink_shape(g, P(pts), c if isinstance(c, str) else c, seed=seed, ink=max(3, int(ink * s)), wob=1.2 * s, tex=True,
                  amt=0.1, grime=0.08)

    def circ(cx, cy, r, n=28):
        return [(cx + math.cos(a / n * math.tau) * r, cy + math.sin(a / n * math.tau) * r) for a in range(n)]

    if kind == "ATTACK":
        shape([(120, 30), (136, 30), (140, 170), (128, 186), (116, 170)])
        shape([(84, 170), (172, 170), (172, 186), (84, 186)], "#c8a030")
        shape([(120, 186), (136, 186), (136, 226), (120, 226)], "#7a4a2a")
    elif kind == "CRITICAL":
        star = []
        for k in range(16):
            r = 110 if k % 2 == 0 else 58
            a = k / 16 * math.tau - math.pi / 2
            star.append((128 + math.cos(a) * r, 128 + math.sin(a) * r))
        shape(star, "#ffd040", seed=2)
        shape([(120, 60), (136, 60), (138, 150), (128, 160), (118, 150)], seed=3)
        shape([(98, 150), (158, 150), (158, 162), (98, 162)], "#c8a030")
        shape([(122, 162), (134, 162), (134, 196), (122, 196)], "#7a4a2a")
    elif kind == "DEFEND":
        shape([(56, 50), (200, 50), (200, 128), (128, 220), (56, 128)])
        shape([(116, 70), (140, 70), (140, 180), (128, 194), (116, 180)], "#8a9aa8")
    elif kind == "SHIELD":
        shape(circ(128, 140, 100)[14:] + [(28, 140)], "#9ae8f0", seed=4)
        shape([(76, 110), (180, 110), (180, 160), (128, 226), (76, 160)])
    elif kind == "EVADE":
        shape([(40, 150), (150, 150), (150, 110), (226, 172), (150, 234), (150, 194), (40, 194)], seed=5)
        for k, y in enumerate((60, 92)):
            shape([(70 + k * 20, y), (200, y), (200, y + 16), (70 + k * 20, y + 16)], seed=6 + k)
    elif kind == "HEAL":
        shape([(100, 36), (156, 36), (156, 100), (220, 100), (220, 156), (156, 156), (156, 220), (100, 220), (100, 156),
               (36, 156), (36, 100), (100, 100)])
    elif kind == "AFFLICT":
        shape([(128, 28), (196, 140), (196, 176), (170, 214), (128, 228), (86, 214), (60, 176), (60, 140)], seed=7)
        shape([(98, 140), (112, 126), (158, 176), (144, 190)], "#3a2a40", seed=8, ink=0)
        shape([(144, 126), (158, 140), (112, 190), (98, 176)], "#3a2a40", seed=9, ink=0)
    elif kind == "DEPLOY":
        shape([(84, 110), (172, 110), (188, 150), (68, 150)], seed=10)
        for sx in (40, 216):
            shape(circ(sx, 92, 30, 14), seed=11)
        shape([(70, 100), (186, 100), (186, 108), (70, 108)], "#6a6e70", ink=6)
        shape(circ(128, 172, 18, 12), "#ff6a5a", seed=12)
    elif kind == "MISS":
        shape(circ(128, 128, 100), seed=13)
        shape(circ(128, 128, 64), BG if False else "#2e3036", seed=14)
        shape([(52, 186), (186, 52), (204, 70), (70, 204)], "#ff6a5a", seed=15)
    elif kind == "CORRUPTED":
        for k, (x, y, w, h) in enumerate(((52, 52, 90, 70), (120, 100, 90, 60), (60, 140, 70, 70), (140, 170, 60, 40))):
            shape([(x, y), (x + w, y + 8), (x + w - 6, y + h), (x + 4, y + h - 6)], seed=20 + k)
    elif kind == "OVERCLOCKED":
        shape([(140, 24), (80, 136), (124, 136), (100, 232), (180, 108), (136, 108), (172, 24)], "#ffd040", seed=21)
    elif kind == "ENCRYPTED":
        shape([(70, 120), (186, 120), (186, 220), (70, 220)], seed=22)
        arc = [(128 + math.cos(math.radians(a)) * 46, 120 + math.sin(math.radians(a)) * 56) for a in range(180, 361, 15)]
        arc2 = [(128 + math.cos(math.radians(a)) * 26, 120 + math.sin(math.radians(a)) * 34) for a in range(360, 179, -15)]
        shape(arc + arc2, "#8a9aa8", seed=23)
        shape(circ(128, 166, 14, 10), "#3a2a20", seed=24, ink=0)
    elif kind == "PARASITE":
        shape(circ(128, 140, 62, 16), seed=25)
        shape(circ(128, 72, 30, 12), seed=26)
        for k in range(3):
            for sx in (-1, 1):
                y = 110 + k * 34
                shape([(128 + sx * 56, y), (128 + sx * 104, y - 18 + k * 18), (128 + sx * 110, y - 6 + k * 18),
                       (128 + sx * 60, y + 12)], seed=27 + k)
    return g


SLICES = [("ATTACK", "#cc442e"), ("CRITICAL", "#e8782a"), ("DEFEND", "#2a7ea0"), ("SHIELD", "#2aa0a8"),
          ("EVADE", "#7a8a96"), ("HEAL", "#3aa860"), ("AFFLICT", "#8a50c8"), ("DEPLOY", "#c8a030"), ("MISS", "#5a5c62")]
STATUS = [("CORRUPTED", False, "#8a2a4a"), ("OVERCLOCKED", True, "#d9a032"), ("ENCRYPTED", True, "#2aa0a8"),
          ("PARASITE", False, "#6a7a2a")]


def badge(kind, col, shape_kind="coin", helps=None, seed=0):
    """256 px painted badge + glyph. Slices: round coin. Statuses: helps = smooth shield + up chevron,
    hurts = jagged burst + down chevron (readable without colour)."""
    g = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    if shape_kind == "coin":
        pts = [(128 + math.cos(a / 36 * math.tau) * 116, 128 + math.sin(a / 36 * math.tau) * 116) for a in range(36)]
        ink_shape(g, pts, col, seed=seed, ink=12, amt=0.22, grime=0.25)
    elif helps:
        ink_shape(g, [(24, 22), (232, 22), (232, 140), (128, 240), (24, 140)], col, seed=seed, ink=12, amt=0.22, grime=0.25)
    else:
        pts = []
        for k in range(24):
            r = 122 if k % 2 == 0 else 92
            a = k / 24 * math.tau
            pts.append((128 + math.cos(a) * r, 128 + math.sin(a) * r))
        ink_shape(g, pts, col, seed=seed, ink=12, amt=0.22, grime=0.25)
    gl = glyph(kind).resize((176, 176), Image.LANCZOS)
    g.alpha_composite(gl, (40, 34 if (shape_kind != "coin" and helps) else 40))
    if shape_kind != "coin":
        c = (60, 220, 120) if helps else (230, 60, 60)
        tri = [(200, 210), (240, 210), (220, 178)] if helps else [(200, 180), (240, 180), (220, 212)]
        d = ImageDraw.Draw(g)
        d.ellipse([186, 170, 254, 238], fill=INK)
        d.polygon(tri, fill=c)
    return g


def sheet06():
    img = new_sheet("06", "ICONS", "9 slice types + 4 statuses at 64 px (24 px below)  (E2, E3, I)")
    LAYOUT["06_icons"] = {"cells": {}}
    text_ink(img, (60, 170), "SLICE TYPES", font("title", 26), anchor="lm", stroke=3)
    for i, (k, c) in enumerate(SLICES):
        cx = 180 + i * 195
        b = badge(k, c, "coin", seed=i)
        b64 = b.resize((64, 64), Image.LANCZOS)
        b24 = b.resize((24, 24), Image.LANCZOS)
        ink_shape(img, rrect_pts(cx - 70, 220, cx + 70, 440, 14), "#34383e", seed=i + 40, ink=3, amt=0.12, grime=0.15)
        paste_c(img, b64, cx, 290)
        paste_c(img, b24, cx, 380)
        label(img, cx, 452, k, size=18)
        LAYOUT["06_icons"]["cells"][k] = [cx, 290]
    text_ink(img, (60, 590), "STATUSES", font("title", 26), anchor="lm", stroke=3)
    for i, (k, helps, c) in enumerate(STATUS):
        cx = 380 + i * 390
        b = badge(k, c, "status", helps, seed=i + 20)
        ink_shape(img, rrect_pts(cx - 150, 640, cx + 150, 900, 16), "#34383e", seed=i + 50, ink=3, amt=0.12, grime=0.15)
        paste_c(img, b.resize((64, 64), Image.LANCZOS), cx - 60, 740)
        paste_c(img, b.resize((24, 24), Image.LANCZOS), cx - 60, 830)
        paste_c(img, b.resize((128, 128), Image.LANCZOS), cx + 70, 770)
        label(img, cx, 912, k, size=20, sub=("HELPS you  -  smooth shield, up arrow" if helps else
                                              "HURTS you  -  spiky burst, down arrow"))
        LAYOUT["06_icons"]["cells"][k] = [cx - 60, 740]
    save(img, "06_icons.png")


# =============================================================== 05 cards
RAR = {"Common": ("#8a8e92", 1), "Uncommon": ("#2aa080", 2), "Rare": ("#d9a032", 3)}


def pictos(kind):
    """Pictogram row for a card (painted mini badges + numbers)."""
    row = Image.new("RGBA", (300, 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(row)

    def chip(x, gl, col, num=None):
        b = badge(gl, col, "coin", seed=x).resize((52, 52), Image.LANCZOS)
        row.alpha_composite(b, (x, 4))
        if num is not None:
            text_ink(row, (x + 72, 30), str(num), font("slab", 30), stroke=3)
    if kind == "backspin":
        # anticlockwise spin pictogram: painted arc arrow + 9
        ar = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
        pts = [(110 + math.cos(math.radians(a)) * 80, 110 - math.sin(math.radians(a)) * 80) for a in range(30, 330, 10)]
        ImageDraw.Draw(ar).line(pts, fill=INK, width=40, joint="curve")
        ImageDraw.Draw(ar).line(pts, fill=(63, 240, 255), width=24, joint="curve")
        a = math.radians(30)
        tip = (110 + math.cos(a) * 80, 110 - math.sin(a) * 80)
        ImageDraw.Draw(ar).polygon([(tip[0] - 40, tip[1] - 4), (tip[0] + 34, tip[1] - 20), (tip[0] + 6, tip[1] + 44)],
                                   fill=(63, 240, 255), outline=INK, width=8)
        row.alpha_composite(ar.resize((54, 54), Image.LANCZOS), (40, 3))
        text_ink(row, (120, 30), "9", font("slab", 32), stroke=3)
        text_ink(row, (190, 30), "CCW", font("title", 22), stroke=2)
    elif kind == "arcflash":
        chip(40, "ATTACK", "#cc442e", 3)
        text_ink(row, (190, 30), "ALL", font("title", 24), stroke=2)
    else:
        chip(70, "DEFEND", "#2a7ea0", 12)
    return row


def card(kind, title, rarity, cost, text, art, ctype, seed):
    W_, H_ = 360, 520
    c = Image.new("RGBA", (W_ + 20, H_ + 20), (0, 0, 0, 0))
    rc, pips = RAR[rarity]
    tcol = {"SPIN": "#3a5a8a", "ATTACK": "#8e3a2a", "DEFEND": "#2a6a6a"}[ctype]
    ink_shape(c, rrect_pts(10, 10, W_ + 10, H_ + 10, 22), rc, seed=seed, ink=7, amt=0.22, grime=0.3)          # rarity frame
    ink_shape(c, rrect_pts(26, 26, W_ - 6, H_ - 6, 14), "#e4d6b0", seed=seed + 1, ink=4, amt=0.16, grime=0.22)  # paper
    # art window
    ink_shape(c, rrect_pts(40, 92, W_ - 20, 300, 10), tcol, seed=seed + 2, ink=4, amt=0.25, grime=0.35)
    a = fit(art, W_ - 90, 190)
    paste_c(c, a, (W_ + 20) / 2, 196)
    # title ribbon
    ink_shape(c, [(30, 50), (W_ - 10, 46), (W_ - 4, 86), (24, 90)], "#6a4428", seed=seed + 3, ink=5, amt=0.2, grime=0.2)
    text_ink(c, ((W_ + 40) / 2, 68), title, font("title", 32), stroke=3)
    # RAM cost gem (Blender crystal) + number
    gm = fit(tile("gem_ram"), 82, 82)
    paste_c(c, gm, 44, 44)
    text_ink(c, (44, 46), str(cost), font("slab", 36), fill=(16, 32, 40), ink=(220, 250, 255), stroke=3, shadow=False)
    # type tag
    ink_shape(c, rrect_pts(W_ / 2 - 60, 288, W_ / 2 + 80, 318, 8), tcol, seed=seed + 4, ink=3, amt=0.2, grime=0.1)
    text_ink(c, (W_ / 2 + 10, 303), ctype, font("title", 20), stroke=2, shadow=False)
    # pictogram row
    pr = pictos(kind)
    paste_c(c, pr, (W_ + 20) / 2, 356)
    # text
    d = ImageDraw.Draw(c)
    y = 400
    for line in text:
        d.text(((W_ + 20) / 2, y), line, font=font("body", 21), fill=(52, 34, 24), anchor="mt")
        y += 28
    # rarity: frame colour + gem pips + word
    for k in range(pips):
        paste_c(c, fit(tile("gem_ram"), 26, 26).convert("RGBA"), (W_ + 20) / 2 - (pips - 1) * 16 + k * 32, H_ - 26)
    pg = Image.new("RGBA", (W_ + 20, H_ + 20), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(c)
    d2.text((40, H_ - 26), rarity.upper(), font=font("title", 18), fill=hx(rc) if rarity != "Common" else (90, 90, 90),
            anchor="lm")
    d2.text((W_ - 4, H_ - 26), "[1]", font=font("body", 16), fill=(110, 90, 70), anchor="rm")
    if rarity == "Uncommon":   # tint the gem pips green
        pass
    tape(c, W_ - 40, 30, 80, 22, -30, seed)
    return c


def card_back(seed):
    W_, H_ = 360, 520
    c = Image.new("RGBA", (W_ + 20, H_ + 20), (0, 0, 0, 0))
    ink_shape(c, rrect_pts(10, 10, W_ + 10, H_ + 10, 22), "#3a3c42", seed=seed, ink=7, amt=0.25, grime=0.35)
    ink_shape(c, rrect_pts(30, 30, W_ - 10, H_ - 10, 14), "#26282e", seed=seed + 1, ink=4, amt=0.2, grime=0.3)
    d = ImageDraw.Draw(c)
    for k in range(-12, 14):    # hazard diagonal pattern
        x = 30 + k * 32
        d.line([(x, 30), (x + 480, 510)], fill=(48, 50, 56), width=10)
    b = fit(tile("ca_back"), 230, 230)
    paste_c(c, b, (W_ + 20) / 2, 250)
    text_ink(c, ((W_ + 20) / 2, 440), "REBEL_CELL", font("stencil", 38), fill=(204, 68, 46), stroke=3)
    c = distress(c, seed, 0.02)
    return c


def sheet05():
    img = new_sheet("05", "CARDS", "Three cards + card back (E5)  -  rarity: frame colour, gem pips, word")
    data = [("backspin", "BACKSPIN", "Common", 1, ["Spin a wheel", "9 ticks counter-", "clockwise."], "ca_backspin", "SPIN"),
            ("arcflash", "ARC FLASH", "Uncommon", 2, ["Deal 3 damage", "to every enemy."], "ca_arcflash", "ATTACK"),
            ("bulwark", "BULWARK", "Uncommon", 1, ["Gain 12 block."], "ca_bulwark", "DEFEND")]
    LAYOUT["05_cards"] = {"cells": {}}
    for i, (k, t, r, cost, txt, art, ct) in enumerate(data):
        cx = 280 + i * 455
        c = card(k, t, r, cost, txt, tile(art), ct, seed=i * 7 + 3)
        c = c.rotate((i - 1) * 1.5, expand=True, resample=Image.BICUBIC)
        drop_shadow(img, c, cx, 540)
        paste_c(img, c, cx, 540)
        label(img, cx, 830, "%s  -  %s" % (t.title(), r), size=20)
        LAYOUT["05_cards"]["cells"][k] = [cx, 540]
    cx = 280 + 3 * 455
    c = card_back(41)
    drop_shadow(img, c, cx, 540)
    paste_c(img, c, cx, 540)
    label(img, cx, 830, "Card back", size=20)
    LAYOUT["05_cards"]["cells"]["back"] = [cx, 540]
    save(img, "05_cards.png")


# =============================================================== 07 items
def sheet07():
    img = new_sheet("07", "ITEMS + CURRENCIES", "Daemon, firmware chip, slice tile for sale, currency icons (F1, F2)")
    LAYOUT["07_items"] = {"cells": {}}
    items = [("it_daemon", "ADRENAL LOOP", "daemon  -  Uncommon", "Each Perfect heals 2."),
             ("it_chip", "BARBED WIRE", "firmware chip  -  Common", "DEF slice also deals 2."),
             ("it_slice", "ATK 6 SLICE", "spinner slice tile  -  for sale", "")]
    for i, (it, name, sub, txt) in enumerate(items):
        cx = 360 + i * 600
        t = fit(tile(it), 400, 340)
        drop_shadow(img, t, cx, 340)
        paste_c(img, t, cx, 340)
        if it == "it_slice":
            ink_shape(img, rrect_pts(cx - 70, 300, cx + 70, 360, 10), "#2a2c30", seed=7, ink=4, amt=0.1, grime=0.1)
            text_ink(img, (cx, 330), "ATK 6", font("title", 34), fill=(255, 140, 110), stroke=3)
            tg = Image.new("RGBA", (170, 80), (0, 0, 0, 0))
            ink_shape(tg, [(6, 8), (162, 4), (166, 72), (4, 76)], "#d8cc9e", seed=8, ink=4, amt=0.3, grime=0.1)
            ImageDraw.Draw(tg).text((85, 40), "45 cyc", font=font("marker", 30), fill=(20, 16, 14), anchor="mm")
            tg = tg.rotate(-8, expand=True, resample=Image.BICUBIC)
            paste_c(img, tg, cx + 150, 470)
        text_ink(img, (cx, 560), name, font("title", 32), stroke=3)
        label(img, cx, 584, sub, size=18, sub=txt or None)
        LAYOUT["07_items"]["cells"][it] = [cx, 340]
    for i, (cu, name) in enumerate((("cu_cycles", "CYCLES"), ("cu_schematics", "SCHEMATICS"), ("cu_ram", "RAM"),
                                    ("cu_heat", "HEAT"))):
        cx = 330 + i * 420
        ink_shape(img, rrect_pts(cx - 130, 690, cx + 130, 940, 18), "#34383e", seed=i + 60, ink=3, amt=0.12, grime=0.15)
        t = fit(tile(cu), 150, 150)
        paste_c(img, t, cx - 30, 800)
        paste_c(img, fit(tile(cu), 48, 48), cx + 85, 760)
        paste_c(img, fit(tile(cu), 24, 24), cx + 85, 830)
        label(img, cx, 954, name, size=20, sub={"CYCLES": "run currency", "SCHEMATICS": "campaign currency",
                                                "RAM": "combat energy", "HEAT": "how hunted"}[name])
        LAYOUT["07_items"]["cells"][cu] = [cx, 800]
    save(img, "07_items.png")


# =============================================================== 08 stamps
def plank(w, h, col, seed, ink=6):
    p = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    ink_shape(p, [(10, 14), (w + 8, 8), (w + 12, h + 6), (8, h + 12)], col, seed=seed, ink=ink, amt=0.25, grime=0.35)
    return p


def sheet08():
    img = new_sheet("08", "STAMPS + HEADLINE WORDS", "Graphic moments (J): painted signs, rubber stamps, marker, crystal")
    LAYOUT["08_stamps"] = {"cells": {}}
    pos = {"VICTORY": (360, 340), "DEFEATED": (960, 340), "SOLD": (1560, 340), "JACK IN": (360, 760),
           "LETHAL": (960, 760), "PHASE 2": (1560, 760)}
    rng = random.Random(8)
    # VICTORY: gold painted sign board with ink + crystal shards
    cx, cy = pos["VICTORY"]
    p = plank(470, 150, "#d9a032", 1)
    text_ink(p, (245, 92), "VICTORY", font("title", 96), fill=(255, 244, 214), stroke=6)
    p = p.rotate(-3, expand=True, resample=Image.BICUBIC)
    drop_shadow(img, p, cx, cy)
    paste_c(img, p, cx, cy)
    for k in range(5):
        paste_c(img, fit(tile("gem_ram"), 40, 40).rotate(rng.uniform(0, 90), expand=True), cx - 230 + k * 115,
                cy - 95 + (k % 2) * 12)
    # DEFEATED: red rubber stamp, distressed, rotated, on the enemy's spot
    cx, cy = pos["DEFEATED"]
    ink_shape(img, rrect_pts(cx - 230, cy - 120, cx + 230, cy + 120, 20), "#3a3c42", seed=3, ink=4, amt=0.2, grime=0.3)
    st = stamp_text("DEFEATED", (210, 44, 40), 92, 4)
    st = st.rotate(-9, expand=True, resample=Image.BICUBIC)
    paste_c(img, st, cx, cy)
    # SOLD: rubber stamp across a taped price tag
    cx, cy = pos["SOLD"]
    tg = Image.new("RGBA", (380, 200), (0, 0, 0, 0))
    ink_shape(tg, [(10, 16), (366, 8), (372, 184), (6, 190)], "#d8cc9e", seed=5, ink=5, amt=0.3, grime=0.15)
    ImageDraw.Draw(tg).text((190, 100), "45 cyc", font=font("marker", 56), fill=(30, 24, 20), anchor="mm")
    tg = tg.rotate(4, expand=True, resample=Image.BICUBIC)
    paste_c(img, tg, cx, cy)
    tape(img, cx - 150, cy - 90, 100, 28, -20, 6)
    st = stamp_text("SOLD", (200, 40, 40), 120, 7)
    paste_c(img, st.rotate(14, expand=True, resample=Image.BICUBIC), cx + 10, cy)
    # JACK IN: crystal (digital) plate in a painted iron bezel
    cx, cy = pos["JACK IN"]
    p = Image.new("RGBA", (520, 200), (0, 0, 0, 0))
    ink_shape(p, rrect_pts(10, 10, 510, 190, 90), "#4a4e56", seed=8, ink=6, amt=0.2, grime=0.3)
    gem = fit(tile("gem_ram"), 900, 900).resize((470, 150), Image.LANCZOS)
    p.alpha_composite(gem, (25, 25))
    text_ink(p, (260, 100), "JACK IN", font("title", 88), fill=(16, 32, 40), ink=(220, 250, 255), stroke=5, shadow=False)
    drop_shadow(img, p, cx, cy)
    paste_c(img, p, cx, cy)
    # LETHAL: marker letters on a hazard stripe with a painted skull
    cx, cy = pos["LETHAL"]
    p = Image.new("RGBA", (500, 190), (0, 0, 0, 0))
    hz = Image.new("RGBA", (500, 190), (0, 0, 0, 0))
    d = ImageDraw.Draw(hz)
    for k in range(-4, 14):
        d.polygon([(k * 48, 0), (k * 48 + 24, 0), (k * 48 - 66, 190), (k * 48 - 90, 190)], fill=(230, 190, 40))
    m = Image.new("L", (500, 190), 0)
    ImageDraw.Draw(m).polygon(wobble_poly([(14, 22), (486, 12), (490, 178), (10, 182)], 2, 9), fill=255)
    base = painted((500, 190), "#2a2a2e", 9, amt=0.2, grime=0.3).convert("RGBA")
    base.alpha_composite(hz)
    p.paste(base, (0, 0), m)
    ImageDraw.Draw(p).line(wobble_poly([(14, 22), (486, 12), (490, 178), (10, 182)], 2, 9) + [(14, 22)], fill=INK, width=6)
    ink_shape(p, [(22, 50), (130, 46), (132, 140), (24, 146)], "#2a2a2e", seed=10, ink=0, tex=False)
    sk = badge("AFFLICT", "#e8e0cc", "coin", seed=11).resize((90, 90), Image.LANCZOS)
    p.alpha_composite(sk, (32, 50))
    text_ink(p, (300, 96), "LETHAL", font("marker", 96), fill=(255, 70, 60), stroke=6)
    p = p.rotate(2, expand=True, resample=Image.BICUBIC)
    drop_shadow(img, p, cx, cy)
    paste_c(img, p, cx, cy)
    # PHASE 2: Meridian orange container-stripe banner with stencil letters
    cx, cy = pos["PHASE 2"]
    p = plank(480, 160, "#e8782a", 12)
    d = ImageDraw.Draw(p)
    for k in range(10):
        d.line([(30 + k * 48, 24), (30 + k * 48, 160)], fill=(176, 80, 24), width=6)
    text_ink(p, (250, 96), "PHASE 2", font("stencil", 100), fill=(42, 44, 48), ink=(255, 220, 170), stroke=4)
    p = distress(p, 12, 0.06)
    drop_shadow(img, p, cx, cy)
    paste_c(img, p, cx, cy)
    for w, (x, y) in pos.items():
        label(img, x, y + 150, w, size=22, sub={"VICTORY": "painted gold sign + crystal", "DEFEATED": "red rubber stamp",
                                               "SOLD": "stamp over taped price", "JACK IN": "crystal plate (digital)",
                                               "LETHAL": "marker on hazard tape", "PHASE 2": "corp stencil banner (Meridian)"}[w])
        LAYOUT["08_stamps"]["cells"][w] = [x, y]
    save(img, "08_stamps.png")


def contact():
    names = ["01_operatives", "02_enemies", "03_landmarks", "04_threats", "05_cards", "06_icons", "07_items", "08_stamps"]
    TW, TH, PAD = 760, 428, 20
    sh = Image.new("RGB", (2 * TW + 3 * PAD, 4 * (TH + 40) + 5 * PAD + 50), (24, 22, 24))
    d = ImageDraw.Draw(sh)
    d.text((PAD, 20), "S2  E-format toon  -  asset samples", font=font("title", 34), fill=(255, 226, 170))
    for i, n in enumerate(names):
        im = Image.open(os.path.join(OD, n + ".png")).convert("RGB").resize((TW, TH), Image.LANCZOS)
        x = PAD + (i % 2) * (TW + PAD)
        y = 70 + PAD + (i // 2) * (TH + 40 + PAD)
        sh.paste(im, (x, y))
        d.text((x + 4, y + TH + 8), n, font=font("body", 22), fill=(230, 222, 204))
    sh.save(os.path.join(OD, "contact_sheet.jpg"), quality=86)


if __name__ == "__main__":
    os.makedirs(OD, exist_ok=True)
    for f in (sheet01, sheet02, sheet03, sheet04, sheet05, sheet06, sheet07, sheet08):
        f()
    json.dump(LAYOUT, open(os.path.join(OD, "layout.json"), "w"), indent=1)
    contact()
    print("SHEETS DONE")
