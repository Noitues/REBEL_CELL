"""04_kit_sheet.png: the v2 overlay kit on a neutral ground, by material and job.

Columns: sticker words (verbs + headlines), sticker objects, grease pencil (plans), light spill (base)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from kit import *  # noqa
import s03_shop
import shop as OB_SHOP

GROUND = (52, 52, 56)
TXT = (232, 230, 224)
SUB = (160, 160, 166)
COLS = [(28, 470), (494, 950), (974, 1430), (1454, 1892)]


def ground():
    rng = np.random.default_rng(4)
    g = np.ones((H, W, 3), np.float32) * (np.array(GROUND, np.float32) / 255)
    n = (SP.fbm(H, W, rng, scales=(240, 60, 12), weights=(0.5, 0.3, 0.2)) - 0.5) * 0.05
    return np.clip(g + n[..., None], 0, 1)


def system_button(img_f, box, label, size=38):
    c = f2pil(img_f).convert("RGBA")
    lay = Image.new("RGBA", c.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(24, 30, 50, 255), outline=(60, 120, 140, 255), width=2)
    d.polygon([(x0, y0), (x0 + 16, y0), (x0, y0 + 16)], fill=(70, 150, 170, 255))
    d.text(((x0 + x1) / 2, y0 + 30), label, font=MK.bahn(size, "SemiBold"), fill=(104, 146, 160, 255), anchor="mm")
    return pil2f(Image.alpha_composite(c, lay))


def build():
    img = ground()
    # ---------------- light spill swatches (D): before / after on the MODEM sign
    shop_raw = Image.open(BASE_SHOP).convert("RGB")
    raw = pil2f(s03_shop.sign_buttons(Image.open(BASE_SHOP_SIGN).convert("RGB")) if s03_shop.USING_SIGN
               else OB_SHOP.system_buttons(shop_raw))
    lit = s03_shop.shop_base()
    crop = (0, 0, 300, 720)
    for k, src in enumerate((raw, lit)):
        tile = f2pil(src).crop(crop).resize((196, 470), Image.LANCZOS)
        x = 1478 + k * 214
        img[190:190 + 470, x:x + 196] = pil2f(tile)
    # ---------------- grease pencil (A) on a dark screen swatch so the glass reads
    gx0, gy0, gx1, gy1 = 990, 190, 1414, 660
    img[gy0:gy1, gx0:gx1] = np.array([0.085, 0.085, 0.10], np.float32)
    rng = np.random.default_rng(77)
    L = T.Layer(rng)
    T.print_reticle(L, 1310, 300, 60, (247, 33, 31, 210))
    T.print_dashed_circle(L, 1310, 300, 86, (247, 33, 31, 150), width=1.4, dash=6, gap=10)
    L.flush_print()
    L.wax_stroke(T.hand_circle(1310, 300, 44, 40, rng, turns=1.15), 7.5, PAL_F["red"])
    L.strokes(T.letter_strokes("HIT IT", 1120, 292, 40, 10, PAL_F["red"], rng, angle=0.04))
    L.strokes(T.arrow_strokes(T.bezier((1190, 316), (1230, 330), (1262, 316)), 6.5, PAL_F["red"], rng, head=16))
    path = T.chaikin(T.resample([(1030, 610), (1110, 570), (1200, 580), (1290, 530), (1350, 470)], 10), 3)
    L.strokes(T.arrow_strokes(path, 7, PAL_F["yellow"], rng, head=22, dashed=True, dash=28, gap=16))
    L.flush_print()
    T.print_waypoint(L, 1200, 580, "1", col=K_YELLOW + (255,))
    L.flush_print()
    L.wax_stroke(T.hand_circle(1090, 450, 40, 46, rng, turns=1.1), 7, PAL_F["yellow"])
    L.light(glint=0.5, glint_gain=0.9)
    img = pencil_composite(img, L)
    sub = img[gy0:gy1, gx0:gx1]
    img[gy0:gy1, gx0:gx1] = glass(sub, np.random.default_rng(5),
                                  [(330, 380, 60, 46, 0.5, "print"), (190, 150, 190, 50, -0.3, "wipe")], band_pos=0.42)
    # ---------------- sticker objects (C)
    img = place_sticker(img, PC.crew_card(curl=dict(corner="br", amount=0.09)), 610, 320, angle=4, scale=0.72)
    img = place_sticker(img, PC.heat_poster(curl=dict(corner="bl", amount=0.10)), 838, 310, angle=-4, scale=0.66)
    img = place_sticker(img, note_card("BACKDOOR FIRST\nTHEN BRUTE IT", w=240, h=110, curl=dict(corner="tr", amount=0.12)),
                        640, 584, angle=-3, scale=0.86)
    img = place_sticker(img, PC.price_dot(60, seed=63, d=64), 862, 590, angle=9)
    # ---------------- sticker words (C): verb over a washed system button + headline stickers
    img = system_button(img, (70, 190, 430, 300), "EXECUTE", 40)
    img = place_sticker(img, verb_sticker("SEND IT", 70, holo=True, seed=7, curl=dict(corner="tr", amount=0.09)),
                        250, 300, angle=5)
    img = place_sticker(img, verb_sticker("LEAVE", 50, holo=False, seed=23), 150, 450, angle=-4)
    img = place_sticker(img, word_sticker("HIT THIS", 44, [FILL_RED], seed=33, border=18), 340, 470, angle=5)
    img = place_sticker(img, word_sticker("OURS", 44, [FILL_YELLOW], seed=31, border=17), 128, 588, angle=4)
    img = place_sticker(img, PC.them_warning(), 338, 604, angle=-5, scale=0.86)
    # ---------------- labels
    c = f2pil(img).convert("RGBA")
    d = ImageDraw.Draw(c)
    d.text((28, 22), "REBEL_CELL OVERLAY KIT  v2", font=MK.bahn(34, "Bold"), fill=TXT)
    d.text((520, 30), "stickers for every word and object  //  grease pencil for plans  //  light spill in the base  //  no spray",
           font=MK.bahn(19, "SemiLight"), fill=SUB)
    heads = [("C  STICKER WORDS", "VERBS + HEADLINES", "bold die-cut lettering: black keyline, chunky\n"
              "extrude, thick crisp white border, gloss. Holo foil\non the primary verb. Slapped at an angle over the\n"
              "washed system word, which stays readable."),
             ("C  STICKER OBJECTS", "THINGS", "crew ID (holo), Heat poster, price dot, kraft note\n"
              "card. White or kraft die-cut, gloss, soft shadow,\ncorner curl. Holo only on the key items."),
             ("A  GREASE PENCIL ON GLASS", "PLANS", "yellow = plan and route, red = threat and target.\n"
              "Circles, arrows, waypoints. At most 1-2 short\nscrawled words a screen. Waxy lit strokes,\n"
              "4 px cast shadow, printed reticle and range ring."),
             ("D  LIGHT SPILL", "BASE LAYER", "glowing base elements (neon, MODEM sign, spinner\n"
              "rims) light the facets around them. Tuned per\nscreen: combat 1.15, city 0.38, shop 1.2.")]
    for (x0, x1), (h1, h2, body) in zip(COLS, heads):
        d.line((x0, 92, x1, 92), fill=(110, 110, 116), width=1)
        d.text((x0, 104), h1, font=MK.bahn(24, "Bold"), fill=TXT)
        d.text((x0, 136), h2, font=MK.bahn(16, "SemiBold"), fill=tuple(K_PINK))
        d.multiline_text((x0, 712), body, font=MK.bahn(17, "SemiLight"), fill=SUB, spacing=6)
    for (x, y, t) in [(250, 368, "primary verb (holo) over system word"), (250, 664, "verb  /  headline words"),
                      (610, 484, "crew ID / holo"), (838, 484, "Heat poster"), (640, 664, "note card / kraft + pencil"),
                      (862, 640, "price dot"), (1576, 670, "before"), (1790, 670, "after spill")]:
        d.text((x, y), t, font=MK.bahn(15, "SemiBold"), fill=SUB, anchor="ma")
    # palette
    d.line((28, 852, 1892, 852), fill=(110, 110, 116), width=1)
    d.text((28, 866), "PALETTE", font=MK.bahn(20, "Bold"), fill=TXT)
    chips = [(K_PINK, "PINK", "verb stickers"), (K_WHITE, "WHITE", "die-cut border"), (K_BLACK, "BLACK", "keyline, ink"),
             (K_YELLOW, "YELLOW", "plan, route"), (K_RED, "RED", "threat, target"),
             (K_KRAFT, "KRAFT", "note cards"), (None, "HOLO", "primary verb, ID")]
    holo = SL.holo_tex(120, 120, seed=3).resize((64, 64))
    for i, (col, name, role) in enumerate(chips):
        x = 28 + i * 190
        if col is None:
            c.paste(holo, (x, 904))
        else:
            d.rectangle((x, 904, x + 64, 968), fill=tuple(col))
        d.rectangle((x, 904, x + 64, 968), outline=(120, 120, 126), width=1)
        d.text((x + 76, 912), name, font=MK.bahn(18, "Bold"), fill=TXT)
        d.text((x + 76, 940), role, font=MK.bahn(15, "SemiLight"), fill=SUB)
    d.text((1380, 866), "RULES", font=MK.bahn(20, "Bold"), fill=TXT)
    d.multiline_text((1380, 900), "Order: base > spill > pencil > object stickers > word stickers.\n"
                     "4-6 marks a screen. Every word is a sticker; pencil plans.\n"
                     "Never over spinner values, node icons, prices or HP.\n"
                     "No system word under a verb? Draw a washed button first.",
                     font=MK.bahn(16, "SemiLight"), fill=SUB, spacing=7)
    c.convert("RGB").save(os.path.join(OUT, "04_kit_sheet.png"))
    print("saved 04_kit_sheet.png")


if __name__ == "__main__":
    build()
