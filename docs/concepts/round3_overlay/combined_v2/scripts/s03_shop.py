"""03_shop.png: BUY (holo) / LEAVE (pink) verb stickers over washed PURCHASE / EXIT, the UPGRADE OR DIE
headline sticker, THIS ONE! word sticker, price dots (stickers); card ring + arrow (grease pencil).

Base: docs/concepts/round4_modem_sign/shop_with_sign.png if it exists, else the round-2 MODEM shop
with its old paper BUY/SELL/TRADE stickers covered by B's washed system buttons."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from kit import *  # noqa
import shop as OB_SHOP   # B: washed PURCHASE / EXIT buttons (cover the old BUY/SELL/TRADE stickers)

USING_SIGN = os.path.exists(BASE_SHOP_SIGN)


CYAN = (98, 214, 236)

# Layout per base. With the round-4 sign the left column is the sign itself (it already replaced the
# old BUY/SELL/TRADE stickers), so the washed system buttons move to a bar under the card builder.
if USING_SIGN:
    BTN = [((700, 876, 958, 1040), "PURCHASE"), ((984, 876, 1190, 1040), "EXIT")]
    BUY_POS, LEAVE_POS = (834, 996, -5), (1090, 998, 4)
    THIS_POS = (1318, 884, -5)
    ARROW = ((1236, 846), (1112, 806), (1112, 680))
    DOTS = [(25, 520, 398, -8), (50, 796, 760, 7)]
    SPILL = [box_mask(22, 22, 250, 1034), box_mask(360, 170, 1310, 325)]
else:
    BTN = None
    BUY_POS, LEAVE_POS = (162, 862, -6), (158, 1004, 4)
    THIS_POS = (1150, 878, -5)
    ARROW = ((1092, 834), (1070, 760), (1110, 676))
    DOTS = [(25, 520, 398, -8), (60, 1290, 758, 9)]
    SPILL = [box_mask(30, 25, 255, 740), box_mask(360, 170, 1310, 325)]


def sign_buttons(base):
    """Washed PURCHASE / EXIT buttons in the base UI language (B's style), on a dashed bar."""
    img = base.convert("RGBA")
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = 684, 862, 1206, 1056
    d.rectangle((x0, y0, x1, y1), fill=(14, 16, 30, 246))
    for x in range(x0, x1, 14):
        d.line((x, y0, x + 7, y0), fill=CYAN + (200,), width=3)
        d.line((x, y1, x + 7, y1), fill=CYAN + (200,), width=3)
    for y in range(y0, y1, 14):
        d.line((x0, y, x0, y + 7), fill=CYAN + (200,), width=3)
        d.line((x1, y, x1, y + 7), fill=CYAN + (200,), width=3)
    f = MK.bahn(34, "SemiBold")
    for (bx0, by0, bx1, by1), label in BTN:
        d.rectangle((bx0, by0, bx1, by1), fill=(24, 30, 50, 255), outline=(60, 120, 140, 255), width=2)
        d.polygon([(bx0, by0), (bx0 + 16, by0), (bx0, by0 + 16)], fill=(70, 150, 170, 255))
        d.text(((bx0 + bx1) / 2, by0 + 28), label, font=f, fill=(104, 146, 160, 255), anchor="mm")
    return Image.alpha_composite(img, lay).convert("RGB")


def shop_base():
    if USING_SIGN:
        base = sign_buttons(Image.open(BASE_SHOP_SIGN).convert("RGB"))
        gain = 1.2
    else:
        base = OB_SHOP.system_buttons(Image.open(BASE_SHOP).convert("RGB"))
        gain = 1.5
    # D: the MODEM / CYBER SHOP neon and the chip icons spill onto the facets (tuned per base)
    return light_spill(pil2f(base), SPILL, gain=gain)


def pencil_layer(rng):
    L = T.Layer(rng)
    L.wax_stroke(T.hand_circle(1222, 604, 108, 96, rng, turns=1.12, angle=0.08), 8.5, PAL_F["yellow"])
    L.strokes(T.arrow_strokes(T.bezier(*ARROW), 7, PAL_F["yellow"], rng, head=20))
    L.light(glint=0.16, glint_gain=0.8)
    return L


def headline(seed=55):
    """UPGRADE / OR DIE! as die-cut lettering on a black vinyl badge (covers the old marker scrawl)."""
    S = SL.SS
    up = SL.lettering(["UPGRADE"], 90, [FILL_YELLOW], key_w=4, extrude=6, seed=seed, jitter=3, track=1, pad=10)
    die = SL.lettering(["OR DIE!"], 110, [FILL_PINK], key_w=4, extrude=7, seed=seed + 1, jitter=4, track=1, pad=10)
    w, h = 430 * S, 352 * S
    P = 30 * S
    Wc, Hc = w + 2 * P, h + 2 * P
    art = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    d = ImageDraw.Draw(art)
    d.rounded_rectangle([P, P, Wc - P, Hc - P], radius=22 * S, fill=SL.INK + (255,))
    hz = Image.new("RGBA", (Wc, Hc), K_YELLOW + (255,))
    hd = ImageDraw.Draw(hz)
    y0, y1 = Hc - P - 30 * S, Hc - P - 14 * S
    for x in range(-Hc, Wc + Hc, int(18 * S)):
        hd.polygon([(x, y0), (x + 9 * S, y0), (x + 9 * S - (y1 - y0), y1), (x - (y1 - y0), y1)], fill=SL.INK + (255,))
    hz.putalpha(SL.rrect_mask((Wc, Hc), [P + 16 * S, y0, Wc - P - 16 * S, y1], 3 * S))
    art = Image.alpha_composite(art, hz)
    art.alpha_composite(up, (int((Wc - up.size[0]) / 2), int(P + 2 * S)))
    art.alpha_composite(die, (int((Wc - die.size[0]) / 2), int(P + 128 * S)))
    d = ImageDraw.Draw(art)
    SL.text_img(d, (P + 20 * S, P + 18 * S), "MODEM // HOUSE RULE 01", SL.MONO, 13, (150, 144, 156, 255), anchor="lm")
    return SL.build_sticker(art, border=18, material="gloss", close=6, curl=dict(corner="br", amount=0.08),
                            seed=seed, gloss_pos=0.3)


SMUDGES = [(1290, 990, 64, 50, 0.5, "print"), (390, 430, 60, 46, -0.3, "print"), (870, 880, 300, 64, -0.1, "wipe")]


def build(save=True):
    rng = np.random.default_rng(303)
    img = shop_base()
    img = pencil_composite(img, pencil_layer(rng))
    img = glass(img, np.random.default_rng(13), SMUDGES, band_pos=0.40, corner="bl")
    img = place_sticker(img, headline(), 1624, 522, angle=2)
    for i, (v, x, y, a) in enumerate(DOTS):
        img = place_sticker(img, PC.price_dot(v, seed=60 + i, d=58), x, y, angle=a)
    img = place_sticker(img, word_sticker("THIS ONE!", 50, [FILL_YELLOW], seed=35, border=18,
                                          curl=dict(corner="bl", amount=0.12)), THIS_POS[0], THIS_POS[1], angle=THIS_POS[2])
    img = place_sticker(img, verb_sticker("BUY", 60, holo=True, seed=21, curl=dict(corner="tr", amount=0.11),
                                          holo_phase=0.3), BUY_POS[0], BUY_POS[1], angle=BUY_POS[2])
    img = place_sticker(img, verb_sticker("LEAVE", 50, holo=False, seed=23), LEAVE_POS[0], LEAVE_POS[1], angle=LEAVE_POS[2])
    if save:
        f2pil(img).save(os.path.join(OUT, "03_shop.png"))
        print("saved 03_shop.png", "(base: shop_with_sign)" if USING_SIGN else "(base: round-2 modem_shop, old stickers covered)")
    return img


if __name__ == "__main__":
    build()
