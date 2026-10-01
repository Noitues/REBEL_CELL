"""Builds 01_combat, 02_city, 03_shop, 04_lifecycle and the contact sheet.
Run: python make_scenes.py   (Pillow only, all randomness seeded)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from pieces import *  # noqa

OUT = ROOT + r"\docs\concepts\round3_overlay\o_c_vinyl_sticker"
B_COMBAT = ROOT + r"\docs\concepts\round2\r2c_geo_vector_gritty\stills\04_combat.png"
B_CITY = ROOT + r"\docs\concepts\round2\r2c_geo_vector_gritty\stills\02_city_night.png"
B_SHOP = ROOT + r"\docs\concepts\round2\r2c_v2_modem\modem_shop.png"

SYS_FILL = (17, 19, 28)
SYS_LINE = (96, 206, 226)
SYS_TEXT = (128, 140, 150)


def wash(canvas, box, k_dark=0.55, k_sat=0.25, feather=24):
    """Lightly darken/desaturate the base under an overlay (allowed by the brief)."""
    reg = canvas.crop(box).convert("RGB")
    reg = ImageEnhance.Color(reg).enhance(k_sat)
    reg = ImageEnhance.Brightness(reg).enhance(k_dark)
    w, h = reg.size
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse([feather, feather, w - feather, h - feather], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(feather / 2))
    canvas = canvas.copy()
    canvas.paste(reg.convert("RGBA"), box[:2], m)
    return canvas


def system_button(canvas, box, label, size=38, sub=None, alpha=236, top=False):
    """The machine's own washed-out button (digital, Cv2-like): chamfered slab, thin cyan line."""
    x0, y0, x1, y1 = box
    c = 14
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    poly = [(x0 + c, y0), (x1, y0), (x1, y1 - c), (x1 - c, y1), (x0, y1), (x0, y0 + c)]
    d.polygon(poly, fill=SYS_FILL + (alpha,))
    d.line(poly + [poly[0]], fill=SYS_LINE + (110,), width=2)
    f = ImageFont.truetype(PLEX, size)
    cy = (y0 + size * 0.75) if top else ((y0 + y1) / 2 - (9 if sub else 0))
    # tracked-out system type
    tw = sum(f.getlength(ch) for ch in label) + 6 * (len(label) - 1)
    x = (x0 + x1) / 2 - tw / 2
    for ch in label:
        d.text((x, cy), ch, font=f, fill=SYS_TEXT + (255,), anchor="lm")
        x += f.getlength(ch) + 6
    if sub:
        fs = ImageFont.truetype(PLEX, 15)
        d.text(((x0 + x1) / 2, cy + size * 0.62), sub, font=fs, fill=(96, 106, 116, 255), anchor="mm")
    return Image.alpha_composite(canvas, lay)


def dashed_panel(canvas, box, fill=(15, 18, 30), line=(100, 214, 234)):
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=fill + (250,))
    dash, gap = 14, 8
    for x in range(x0, x1, dash + gap):
        d.line([(x, y0), (min(x + dash, x1), y0)], fill=line + (255,), width=3)
        d.line([(x, y1), (min(x + dash, x1), y1)], fill=line + (255,), width=3)
    for y in range(y0, y1, dash + gap):
        d.line([(x0, y), (x0, min(y + dash, y1))], fill=line + (255,), width=3)
        d.line([(x1, y), (x1, min(y + dash, y1))], fill=line + (255,), width=3)
    return Image.alpha_composite(canvas, lay)


# ============================================================ combat
def combat_base():
    c = Image.open(B_COMBAT).convert("RGBA")
    c = wash(c, (1600, 750, 1920, 1050), k_dark=0.5, k_sat=0.2)
    c = system_button(c, (1612, 792, 1900, 900), "EXECUTE", 40, sub="SPIN BOTH WHEELS")
    return c


SEND_POS = (1730, 926, -6.0)   # cx, cy, angle (PIL: positive = counter-clockwise)


def make_combat():
    c = combat_base()
    # crew photo (holo ID sticker, lifted corner)
    c = place(c, crew_card(curl=dict(corner="br", amount=0.09)), 182, 606, angle=5)
    # tactical note (matte kraft, paint-pen hand)
    c = place(c, kraft_note(["BACKDOOR FIRST", "DODGE THEIR 9", "THEN SEND IT"], w=262, h=132, pen_size=23,
                            curl=dict(corner="tr", amount=0.12)), 962, 578, angle=-3)
    # target annotation: paint pen on the enemy spinner
    pen = Pen(c.size, PEN_Y, seed=5)
    pen.circle(1360, 410, 262, 238, width=9, start=-2.5, over=0.5, tilt=0.05, grow=0.03)
    pen.text("HIT IT!", 1690, 158, 54, angle=7)
    pen.arrow([(1655, 196), (1630, 228), (1598, 252)], width=7, head=20)
    c = pen.ink(c)
    # the verb, slapped over EXECUTE
    c = place(c, verb("SEND IT", size=88, seed=7, curl=dict(corner="tr", amount=0.10)),
              SEND_POS[0], SEND_POS[1], angle=SEND_POS[2])
    return c


# ============================================================ city
def make_city():
    c = Image.open(B_CITY).convert("RGBA")
    pen = Pen(c.size, PEN_Y, seed=9)
    # planned path, home -> target, along the street
    pen.arrow([(752, 648), (860, 704), (1010, 722), (1150, 690), (1228, 628)], width=8, head=24)
    # target ring
    pen.circle(1292, 592, 50, 62, width=8, start=-2.0, over=0.5, tilt=0.1)
    # threat pointer
    pen.arrow([(1690, 612), (1660, 640), (1636, 652)], width=7, head=18)
    c = pen.ink(c)
    c = place(c, yellow_word(["HIT THIS"], size=46, seed=3, curl=dict(corner="tl", amount=0.12)), 1300, 468, angle=5)
    c = place(c, clear_word(["OURS"], size=50, seed=4), 572, 742, angle=-5)
    c = place(c, them_warning(curl=None), 1760, 568, angle=7)
    c = place(c, heat_poster(curl=dict(corner="tl", amount=0.11)), 1772, 892, angle=-4)
    return c


# ============================================================ shop
def slogan_badge(seed=55, curl=None):
    S = SS
    up = lettering(["UPGRADE"], 92, [("grad", (255, 238, 80), YELLOW_LO)], key_w=4, extrude=6, seed=seed, jitter=3, track=1, pad=10)
    die = lettering(["OR DIE!"], 112, [("grad", (255, 104, 116), CORAL_LO)], key_w=4, extrude=7, seed=seed + 1, jitter=4, track=1, pad=10)
    w, h = 420 * S, 352 * S
    P = 40 * S
    W, H = w + 2 * P, h + 2 * P
    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(art)
    d.rounded_rectangle([P, P, W - P, H - P], radius=22 * S, fill=INK + (255,))
    # thin hazard ribbon along the bottom
    hz = Image.new("RGBA", (W, H), YELLOW + (255,))
    hd = ImageDraw.Draw(hz)
    y0, y1 = H - P - 30 * S, H - P - 14 * S
    for x in range(-H, W + H, int(18 * S)):
        hd.polygon([(x, y0), (x + 9 * S, y0), (x + 9 * S - (y1 - y0), y1), (x - (y1 - y0), y1)], fill=INK + (255,))
    hz.putalpha(rrect_mask((W, H), [P + 16 * S, y0, W - P - 16 * S, y1], 3 * S))
    art = Image.alpha_composite(art, hz)
    art.alpha_composite(up, (int((W - up.size[0]) / 2), int(P + 2 * S)))
    art.alpha_composite(die, (int((W - die.size[0]) / 2), int(P + 128 * S)))
    d = ImageDraw.Draw(art)
    text_img(d, (P + 20 * S, P + 18 * S), "MODEM // HOUSE RULE", MONO, 13, (150, 144, 156, 255), anchor="lm")
    return build_sticker(art, border=13, material="gloss", close=6, curl=curl, seed=seed, gloss_pos=0.3)


def shop_base():
    c = Image.open(B_SHOP).convert("RGBA")
    # replace the old taped BUY/SELL/TRADE stickers with the system's own buttons
    c = dashed_panel(c, (26, 764, 286, 1052))
    c = system_button(c, (44, 786, 268, 900), "PURCHASE", 30, alpha=255, top=True)
    c = system_button(c, (44, 924, 268, 1036), "EXIT", 30, alpha=255, top=True)
    return c


def make_shop():
    c = shop_base()
    # price tags: merch price dots restating each chip price (bigger, never hidden)
    for i, (x, v) in enumerate([(434, 25), (696, 35), (946, 50), (1206, 75)]):
        c = place(c, price_dot(v, seed=60 + i, d=64), x, 404, angle=[-8, 6, -4, 9][i])
    # the house slogan, re-made as a hero sticker over the old marker scrawl
    c = place(c, slogan_badge(curl=dict(corner="br", amount=0.09)), 1626, 520, angle=3)
    # paint pen: THIS ONE!
    pen = Pen(c.size, PEN_Y, seed=13)
    pen.circle(708, 660, 122, 132, width=9, start=-2.3, over=0.5, tilt=0.06)
    pen.arrow([(948, 852), (880, 840), (812, 796)], width=8, head=22)
    pen.text("THIS ONE!", 1070, 866, 52, angle=-4)
    c = pen.ink(c)
    # verbs
    c = place(c, verb("BUY", size=66, seed=21, curl=dict(corner="tr", amount=0.12)), 160, 868, angle=-6)
    c = place(c, verb("LEAVE", size=56, seed=23), 158, 1004, angle=5)
    return c


# ============================================================ lifecycle
def make_lifecycle():
    base = combat_base()
    cx, cy, ang = SEND_POS
    crop = (1320, 600, 1920, 1080)
    pad = Image.new("RGBA", (2400, 1080), (12, 11, 15, 255))
    pad.paste(base, (0, 0))
    K = 1.0
    frames = []
    # 1 APPEAR: ghost in the air, then the squash on contact, shine sweep across
    f = pad.copy()
    f = place(f, verb("SEND IT", size=88, seed=7, gloss_pos=0.0), cx - 40, cy - 70, angle=ang - 14,
              scale=1.22, hover=1.0, opacity=0.28, shadow=0.6)
    f = place(f, verb("SEND IT", size=88, seed=7, gloss_pos=0.55), cx, cy + 6, angle=ang - 2,
              squash=(1.13, 0.84), shadow=1.2)
    frames.append(f)
    # 2 IDLE: corner flutter (two ghosted corner states) + foil phase shift
    f = pad.copy()
    f = place(f, verb("SEND IT", size=88, seed=7, phase=0.22, gloss_pos=0.30, curl=dict(corner="tr", amount=0.19)),
              cx, cy, angle=ang, opacity=0.35, shadow=0.0)
    f = place(f, verb("SEND IT", size=88, seed=7, phase=0.38, gloss_pos=0.40, curl=dict(corner="tr", amount=0.08)),
              cx, cy, angle=ang)
    frames.append(f)
    # 3 LEAVE: peeled from the corner, curling away, EXECUTE revealed underneath
    f = pad.copy()
    f = place(f, verb("SEND IT", size=88, seed=7, phase=0.5, gloss_pos=0.62,
                      curl=dict(corner="tr", amount=0.62, bend=0.25, flap_shadow=0.6)),
              cx - 34, cy + 52, angle=ang - 12, scale=0.96, hover=0.7, shadow=1.0)
    frames.append(f)

    out = Image.new("RGBA", (1920, 1080), (13, 12, 16, 255))
    d = ImageDraw.Draw(out)
    ft = ImageFont.truetype(ANTON, 44)
    fm = ImageFont.truetype(MONO, 18)
    fp = ImageFont.truetype(PLEX, 22)
    d.text((70, 62), "SEND IT  //  VINYL STICKER LIFECYCLE", font=ft, fill=(240, 236, 228), anchor="lm")
    d.text((1850, 62), "o_c_vinyl_sticker  //  verb over EXECUTE", font=fm, fill=(130, 126, 140), anchor="rm")
    titles = [("01  APPEAR  -  SLAP", ["drops in from 1.25x, 12 deg over-rotated", "contact: squash 1.13 / 0.84, 90 ms",
                                       "settle with one overshoot, 160 ms", "shine sweep across the gloss, 220 ms"]),
              ("02  IDLE  -  FLUTTER + FOIL", ["top-right corner lifts 0.08 <-> 0.19, 2.4 s loop",
                                              "holo hue drifts with tilt / time", "specular band breathes +/- 0.05",
                                              "shadow under the lifted corner widens"]),
              ("03  LEAVE  -  PEEL OFF", ["peel from the lifted corner, fold travels 0 -> 0.6",
                                          "sticker lifts: shadow blurs and drifts", "curls away down-left, 280 ms, ease-in",
                                          "EXECUTE is left behind, still the machine's"])]
    pw, ph = 560, 448
    for i, fr in enumerate(frames):
        x0 = 70 + i * (pw + 45)
        y0 = 130
        tile = fr.crop((int(crop[0]), int(crop[1]), int(crop[2]), int(crop[3]))).resize((pw, ph), Image.LANCZOS)
        # frame
        d.rectangle([x0 - 3, y0 - 3, x0 + pw + 2, y0 + ph + 2], fill=(40, 38, 46))
        out.paste(tile, (x0, y0))
        d = ImageDraw.Draw(out)
        d.text((x0, y0 + ph + 42), titles[i][0], font=ImageFont.truetype(ANTON, 34), fill=YELLOW, anchor="lm")
        for j, line in enumerate(titles[i][1]):
            d.text((x0, y0 + ph + 92 + j * 34), "-  " + line, font=fp, fill=(196, 192, 204), anchor="lm")
    # timeline strip
    ty = 1000
    d.line([(70, ty), (1850, ty)], fill=(70, 66, 78), width=2)
    for i, lab in enumerate(["0 ms", "450 ms", "idle loop", "on page exit", "+280 ms"]):
        x = 70 + i * (1780 / 4)
        d.ellipse([x - 6, ty - 6, x + 6, ty + 6], fill=PEN_Y)
        d.text((x, ty + 28), lab, font=fm, fill=(150, 146, 160), anchor="mm")
    pen = Pen(out.size, PEN_Y, seed=77)
    pen.arrow([(615, 362), (640, 352), (668, 360)], width=6, head=14)
    pen.arrow([(1220, 362), (1245, 352), (1273, 360)], width=6, head=14)
    out = pen.ink(out)
    return out


def contact(imgs):
    sheet = Image.new("RGB", (1920, 1080), (12, 11, 15))
    for i, im in enumerate(imgs):
        t = im.convert("RGB").resize((952, 535), Image.LANCZOS)
        sheet.paste(t, (4 + (i % 2) * 960, 4 + (i // 2) * 540))
    return sheet


if __name__ == "__main__":
    which = sys.argv[1:] or ["combat", "city", "shop", "life", "sheet"]
    makers = {"combat": ("01_combat.png", make_combat), "city": ("02_city.png", make_city),
              "shop": ("03_shop.png", make_shop), "life": ("04_lifecycle.png", make_lifecycle)}
    for k in which:
        if k in makers:
            name, fn = makers[k]
            fn().convert("RGB").save(os.path.join(OUT, name), optimize=True)
            print("wrote", name)
    if "sheet" in which:
        ims = [Image.open(os.path.join(OUT, n)) for n in ["01_combat.png", "02_city.png", "03_shop.png", "04_lifecycle.png"]]
        contact(ims).save(os.path.join(OUT, "contact_sheet.jpg"), quality=88)
        print("wrote contact_sheet.jpg")
