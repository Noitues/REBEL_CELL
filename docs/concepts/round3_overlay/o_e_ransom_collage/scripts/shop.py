"""03_shop.png: BUY over PURCHASE, LEAVE over EXIT, THIS ONE!, price tags, UPGRADE OR DIE."""
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collage_lib import *  # noqa
from combat import ring_segments

CYAN = (96, 214, 238)


def verb_panel(base):
    """Machine layer: replace the old sticker buttons with washed digital PURCHASE / EXIT."""
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([22, 768, 300, 1052], fill=(17, 21, 33, 255))
    # dashed cyan frame like the shop panels
    for x in range(22, 300, 14):
        d.line([(x, 768), (x + 8, 768)], fill=CYAN + (150,), width=3)
        d.line([(x, 1052), (x + 8, 1052)], fill=CYAN + (150,), width=3)
    for y in range(768, 1052, 14):
        d.line([(22, y), (22, y + 8)], fill=CYAN + (150,), width=3)
        d.line([(300, y), (300, y + 8)], fill=CYAN + (150,), width=3)
    for (y0, y1, label) in ((786, 892, "PURCHASE"), (930, 1036, "EXIT")):
        d.rectangle([44, y0, 278, y1], fill=(28, 36, 50, 255), outline=(70, 96, 110, 255), width=2)
        d.text((161, y1 - 24), label, font=font(UI_FONT, 32), fill=(150, 170, 178, 235), anchor="mm")
    base = base.copy()
    base.alpha_composite(lay)
    return base


def price_tag(rng, cx, cy, text, col, rot):
    w, h = 96, 50
    pts = [(0, h * 0.5), (22, 0), (w, 2), (w - 3, h), (22, h - 1)]
    pts = [(S(cx - w / 2 + x), S(cy - h / 2 + y)) for x, y in pts]
    img, x, y = shape_piece(pts, col, rng, edge=True)
    # punch hole
    m = img.getchannel("A")
    hx, hy = S(16) + 6, img.height / 2
    ImageDraw.Draw(m).ellipse([hx - S(5), hy - S(5), hx + S(5), hy + S(5)], fill=0)
    img.putalpha(m)
    pcs = [Piece(img, x, y, rot, shadow=S(5, 6))]
    pcs += ransom_word(text, S(cx + 10), S(cy), S(34), rng, rot_range=8, base_rot=rot, kern=-0.08,
                       shadow=S(3, 4), diecut_p=0.0, size_var=(0.9, 1.12), fonts=NUM_FONTS,
                       schemes=[("W", "K"), ("K", "W"), ("K", "Y"), ("Y", "K")])
    return pcs


def build(seed=33):
    rng = random.Random(seed)
    base = load_base(BASE_SHOP, dim=0.9, desat=0.85)
    canvas = new_canvas()
    groups = []
    # --- UPGRADE OR DIE poster (covers and replaces the old marker scrawl)
    up = []
    slab = [S(1398, 352), S(1560, 338), S(1716, 348), S(1850, 336), S(1846, 560), S(1832, 712),
            S(1640, 700), S(1520, 716), S(1404, 690), S(1412, 520)]
    img, x, y = shape_piece(slab, BLACK, rng, halftone=((52, 46, 56), S(7), 30, 0.32))
    up.append(Piece(img, x, y, 0, shadow=S(12, 13), sh_col=PINK, sh_alpha=255))
    star = star_poly(S(1660), S(598), S(122), S(78), 14, rng, jitter=0.12, rot=0.15)
    img, x, y = shape_piece(star, YEL, rng, halftone=(PINK, S(9), 45,
                            lambda xx, yy, s=S(9): s * 0.45 * max(0.0, yy / S(300) - 0.45)))
    up.append(Piece(img, x, y, 0, shadow=S(8, 9)))
    up += ransom_word("UPGRADE", S(1624), S(408), S(66), rng, rot_range=8, base_rot=4, kern=-0.05,
                      shadow=S(5, 7))
    up += ransom_word("OR", S(1530), S(492), S(48), rng, rot_range=10, base_rot=-6, kern=-0.04,
                      shadow=S(4, 6), schemes=[("K", "W"), ("W", "P")])
    up += ransom_word("DIE!", S(1664), S(606), S(104), rng, rot_range=7, base_rot=-5, kern=-0.06,
                      shadow=S(7, 9), diecut_p=0.25,
                      schemes=[("W", "K"), ("K", "W"), ("P", "K"), ("K", "P"), ("W", "P")])
    groups.append(up)
    # --- THIS ONE! around +2 ARMOR
    pick = ring_segments(706, 610, 92, 106, [(-70, -6), (6, 40), (140, 196), (206, 252)], rng)
    star = star_poly(S(842), S(498), S(84), S(54), 10, rng, jitter=0.16, rot=0.2)
    img, x, y = shape_piece(star, WHITE, rng, halftone=(PINK, S(7), 45,
                            lambda xx, yy, s=S(7): s * 0.42 * max(0.0, yy / S(150) - 0.3)))
    pick.append(Piece(img, x, y, 10, shadow=S(7, 9)))
    pick += ransom_word("THIS", S(838), S(480), S(36), rng, rot_range=8, base_rot=6, kern=-0.05,
                        shadow=S(3, 5))
    pick += ransom_word("ONE!", S(846), S(520), S(36), rng, rot_range=8, base_rot=-3, kern=-0.05,
                        shadow=S(3, 5))
    groups.append(pick)
    # --- price tags (sit beside the digital price, never on it)
    groups.append(price_tag(rng, 806, 760, "50", PINK, -8))
    groups.append(price_tag(rng, 548, 398, "25", YEL, 6))
    # --- verbs
    buy = []
    star = star_poly(S(176), S(800), S(64), S(38), 12, rng, jitter=0.14, rot=0.05)
    img, x, y = shape_piece(star, PINK, rng, halftone=(BLACK, S(8), 45,
                            lambda xx, yy, s=S(8): s * 0.4 * max(0.0, yy / S(190) - 0.5)))
    buy.append(Piece(img, x, y, -8, shadow=S(8, 10)))
    buy += ransom_word("BUY", S(170), S(800), S(56), rng, rot_range=9, base_rot=-6, kern=-0.04,
                       shadow=S(6, 8), schemes=[("K", "Y"), ("W", "K"), ("K", "W"), ("Y", "K")])
    groups.append(buy)
    leave = []
    img, x, y = shape_piece([S(*p) for p in arrow_poly(290, 944, 46, 958, 12, 18, 34, 46, 0.3)], YEL, rng)
    leave.append(Piece(img, x, y, 0, shadow=S(6, 7)))
    leave += ransom_word("LEAVE", S(168), S(950), S(44), rng, rot_range=9, base_rot=4, kern=-0.05,
                         shadow=S(5, 7), schemes=[("K", "W"), ("W", "K"), ("K", "Y"), ("K", "P")])
    groups.append(leave)
    for yy in (866, 1010):  # strike the machine words
        img, x, y = shape_piece([S(70, yy + 4), S(252, yy - 4), S(253, yy), S(71, yy + 8)], PINK, rng)
        groups.append([Piece(img, x, y, 0, shadow=S(3, 4))])
    for g in groups:
        draw_pieces(canvas, g)
    base = darken_under(base, canvas, 0.45, 30)
    base = verb_panel(base)
    return finish(base, canvas)


if __name__ == "__main__":
    build().save(OUT + "03_shop.png")
    print("ok")
