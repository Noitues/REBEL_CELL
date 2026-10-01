"""03_shop.png: BUY / LEAVE over washed PURCHASE / EXIT and the UPGRADE OR DIE headline (spray),
house-rule card + price dots (stickers), THIS ONE! ring (grease pencil)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from kit import *  # noqa
import shop as OB_SHOP   # B: washed PURCHASE / EXIT buttons (cover the old BUY/SELL/TRADE stickers)


def shop_base():
    base = Image.open(BASE_SHOP).convert("RGB")
    base = OB_SHOP.system_buttons(base)
    b = pil2f(base)
    # D: the MODEM / CYBER SHOP neon and the chip icons spill onto the facets around them
    return light_spill(b, [box_mask(30, 25, 255, 770), box_mask(360, 170, 1310, 325)], gain=2.0)


def pencil_layer(rng):
    L = T.Layer(rng)
    L.wax_stroke(T.hand_circle(1222, 604, 108, 96, rng, turns=1.12, angle=0.08), 8.5, PAL_F["yellow"])
    L.strokes(T.letter_strokes("THIS ONE!", 1190, 872, 42, 10.5, PAL_F["yellow"], rng, angle=-0.05))
    L.strokes(T.arrow_strokes(T.bezier((1330, 860), (1372, 820), (1330, 712)), 7, PAL_F["yellow"], rng, head=20))
    L.light(glint=0.16, glint_gain=0.8)
    return L


def house_card(seed=55):
    """Plain white vinyl card that covers the old marker scrawl; the headline is sprayed over it."""
    S = SL.SS
    w, h = 452, 360
    P = 40 * S
    Wc, Hc = w * S + 2 * P, h * S + 2 * P
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
    d = ImageDraw.Draw(art)
    SL.text_img(d, (P + 20 * S, P + 20 * S), "MODEM // HOUSE RULE 01", SL.MONO, 13, (150, 144, 156, 255), anchor="lm")
    SL.text_img(d, (Wc - P - 20 * S, Hc - P - 46 * S), "NO REFUNDS. NO NAMES.", SL.MONO, 12, (120, 116, 128, 255), anchor="rm")
    return SL.build_sticker(art, border=13, material="gloss", close=6, curl=dict(corner="br", amount=0.08), seed=seed,
                            gloss_pos=0.3)


SMUDGES = [(1290, 990, 64, 50, 0.5, "print"), (390, 430, 60, 46, -0.3, "print"), (870, 880, 300, 64, -0.1, "wipe")]


def build(save=True):
    rng = np.random.default_rng(303)
    img = shop_base()
    img = pencil_composite(img, pencil_layer(rng))
    img = glass(img, np.random.default_rng(13), SMUDGES, band_pos=0.40, corner="bl")
    img = place_sticker(img, house_card(), 1622, 520, angle=2)
    img = place_sticker(img, PC.price_dot(25, seed=60, d=58), 520, 398, angle=-8)
    img = place_sticker(img, PC.price_dot(60, seed=63, d=58), 1290, 758, angle=9)
    img = spray_verbs(img, [
        (verb("UPGRADE\nOR DIE", 74, angle=-4, drips=5, drip_len=50, seed=3319, line_gap=-0.02, align="center"), 1620, 488),
        (verb("BUY", 92, angle=-5, drips=4, drip_len=40, seed=3320), 158, 852),
        (verb("LEAVE", 66, angle=4, drips=3, drip_len=36, seed=3321), 158, 990),
    ])
    if save:
        f2pil(img).save(os.path.join(OUT, "03_shop.png"))
        print("saved 03_shop.png")
    return img


if __name__ == "__main__":
    build()
