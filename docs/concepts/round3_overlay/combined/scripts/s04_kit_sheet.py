"""04_kit_sheet.png: the overlay kit on a neutral ground, one example per element type, by material and job."""
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


def system_button(img_f, box, label):
    c = f2pil(img_f).convert("RGBA")
    lay = Image.new("RGBA", c.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(24, 30, 50, 255), outline=(60, 120, 140, 255), width=2)
    d.polygon([(x0, y0), (x0 + 16, y0), (x0, y0 + 16)], fill=(70, 150, 170, 255))
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), label, font=MK.bahn(40, "SemiBold"), fill=(104, 146, 160, 255), anchor="mm")
    return pil2f(Image.alpha_composite(c, lay))


def build():
    img = ground()
    # ---------------- light spill swatches (D) : before / after on the MODEM sign
    shop_raw = Image.open(BASE_SHOP).convert("RGB")
    raw = pil2f(OB_SHOP.system_buttons(shop_raw))
    lit = s03_shop.shop_base()
    crop = (0, 0, 300, 720)
    for k, src in enumerate((raw, lit)):
        tile = f2pil(src).crop(crop).resize((196, 470), Image.LANCZOS)
        x = 1478 + k * 214
        img[190:190 + 470, x:x + 196] = pil2f(tile)
    # ---------------- grease pencil (A) on a dark screen swatch so the glass reads
    gx0, gy0, gx1, gy1 = 990, 150, 1414, 700
    img[gy0:gy1, gx0:gx1] = np.array([0.085, 0.085, 0.10], np.float32)
    rng = np.random.default_rng(77)
    L = T.Layer(rng)
    T.print_reticle(L, 1310, 270, 60, (247, 33, 31, 210))
    T.print_dashed_circle(L, 1310, 270, 86, (247, 33, 31, 150), width=1.4, dash=6, gap=10)
    L.flush_print()
    L.wax_stroke(T.hand_circle(1310, 270, 44, 40, rng, turns=1.15), 7.5, PAL_F["red"])
    L.strokes(T.letter_strokes("THEM", 1130, 262, 40, 10, PAL_F["red"], rng, angle=0.04))
    L.strokes(T.arrow_strokes(T.bezier((1188, 286), (1230, 300), (1262, 286)), 6.5, PAL_F["red"], rng, head=16))
    path = T.chaikin(T.resample([(1030, 640), (1110, 600), (1200, 610), (1290, 560), (1350, 500)], 10), 3)
    L.strokes(T.arrow_strokes(path, 7, PAL_F["yellow"], rng, head=22, dashed=True, dash=28, gap=16))
    L.flush_print()
    T.print_waypoint(L, 1200, 610, "1", col=K_YELLOW + (255,))
    L.flush_print()
    L.strokes(T.letter_strokes("OURS", 1120, 470, 40, 10, PAL_F["yellow"], rng, angle=-0.05))
    L.light(glint=0.5, glint_gain=0.9)
    img = pencil_composite(img, L)
    sub = img[gy0:gy1, gx0:gx1]
    img[gy0:gy1, gx0:gx1] = glass(sub, np.random.default_rng(5),
                                  [(330, 420, 60, 46, 0.5, "print"), (190, 150, 190, 50, -0.3, "wipe")], band_pos=0.42)
    # ---------------- stickers (C)
    img = place_sticker(img, PC.crew_card(curl=dict(corner="br", amount=0.09)), 610, 310, angle=4, scale=0.72)
    img = place_sticker(img, PC.heat_poster(curl=dict(corner="bl", amount=0.10)), 838, 300, angle=-4, scale=0.66)
    img = place_sticker(img, note_card("BACKDOOR FIRST\nTHEN BRUTE IT", w=240, h=110, curl=dict(corner="tr", amount=0.12)),
                        640, 574, angle=-3, scale=0.86)
    img = place_sticker(img, PC.price_dot(60, seed=63, d=64), 860, 580, angle=9)
    # ---------------- spray (B) over a washed system button
    img = system_button(img, (70, 300, 430, 420), "EXECUTE")
    img = spray_verbs(img, [
        (verb("SEND\nIT", 92, angle=-7, drips=6, drip_len=70, seed=1104, line_gap=-0.06, align="center"), 252, 352),
        (verb("OR DIE", 64, angle=-4, drips=3, drip_len=40, seed=12), 250, 626),
    ])
    # ---------------- labels
    c = f2pil(img).convert("RGBA")
    d = ImageDraw.Draw(c)
    d.text((28, 22), "REBEL_CELL OVERLAY KIT", font=MK.bahn(34, "Bold"), fill=TXT)
    d.text((470, 30), "four materials, one job each   //   order bottom to top: base > light spill > grease pencil > stickers > spray",
           font=MK.bahn(19, "SemiLight"), fill=SUB)
    heads = [("B  STENCIL & SPRAY", "VERBS + HEADLINES", "pink face, white key, black shadow, glossy drips.\n"
              "Full stencil cuts only on big verbs. The washed\nsystem word stays readable underneath."),
             ("C  VINYL STICKERS", "OBJECTS", "crew ID (holo), Heat poster, price dot, kraft note\n"
              "card. White or kraft die-cut, gloss, soft shadow,\ncorner curl. Holo only on the key items."),
             ("A  GREASE PENCIL ON GLASS", "PLANS + MARKS", "yellow = plan and route, red = threat and target.\n"
              "Waxy lit strokes, 4 px cast shadow, printed reticle,\nrange ring, waypoint. Glass: sheen band + smudge."),
             ("D  LIGHT SPILL", "BASE LAYER", "glowing base elements (neon, MODEM sign, spinner\n"
              "rims) light the facets around them. Not an overlay:\nit lives in the base, under every mark.")]
    for (x0, x1), (h1, h2, body) in zip(COLS, heads):
        d.line((x0, 92, x1, 92), fill=(110, 110, 116), width=1)
        d.text((x0, 104), h1, font=MK.bahn(24, "Bold"), fill=TXT)
        d.text((x0, 136), h2, font=MK.bahn(16, "SemiBold"), fill=tuple(K_PINK))
        d.multiline_text((x0, 740), body, font=MK.bahn(17, "SemiLight"), fill=SUB, spacing=6)
    for (x, y, t) in [(250, 506, "verb over system word"), (250, 700, "headline"), (610, 470, "crew ID / holo"),
                      (838, 470, "Heat poster"), (640, 650, "note card / kraft + pencil"), (860, 640, "price dot"),
                      (1576, 690, "before"), (1790, 690, "after spill")]:
        d.text((x, y), t, font=MK.bahn(15, "SemiBold"), fill=SUB, anchor="ma")
    # palette
    d.line((28, 852, 1892, 852), fill=(110, 110, 116), width=1)
    d.text((28, 866), "PALETTE", font=MK.bahn(20, "Bold"), fill=TXT)
    chips = [(K_PINK, "PINK", "verbs"), (K_WHITE, "WHITE", "key, vinyl"), (K_BLACK, "BLACK", "shadow, ink"),
             (K_YELLOW, "YELLOW", "plan, route"), (K_RED, "RED", "threat, target"),
             (K_KRAFT, "KRAFT", "note cards"), (None, "HOLO", "key stickers")]
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
    # rules
    d.text((1380, 866), "RULES", font=MK.bahn(20, "Bold"), fill=TXT)
    d.multiline_text((1380, 900), "4-6 marks a screen, at least one of spray, sticker, pencil.\n"
                     "Never over spinner values, node icons, prices or HP.\n"
                     "Old base marks are covered by their kit version.\n"
                     "No system word under a verb? Draw a washed button first.",
                     font=MK.bahn(16, "SemiLight"), fill=SUB, spacing=7)
    c.convert("RGB").save(os.path.join(OUT, "04_kit_sheet.png"))
    print("saved 04_kit_sheet.png")


if __name__ == "__main__":
    build()
