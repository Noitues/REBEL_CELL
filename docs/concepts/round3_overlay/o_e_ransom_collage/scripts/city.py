"""02_city.png: HIT THIS, OURS, planned path, THEM, Heat poster."""
import math
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collage_lib import *  # noqa
from combat import ring_segments


def bez(p0, p1, p2, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])


def path_chevrons(rng, p0, p1, p2, step=66, size=18):
    pcs = []
    # arc length sampling
    pts = [bez(p0, p1, p2, i / 400) for i in range(401)]
    acc, out, last = 0.0, [], pts[0]
    for i, p in enumerate(pts[1:], 1):
        acc += math.hypot(p[0] - last[0], p[1] - last[1])
        last = p
        if acc >= step:
            acc = 0
            out.append(i)
    for k, i in enumerate(out[:-1]):
        x, y = pts[i]
        x2, y2 = pts[min(400, i + 4)]
        a = math.atan2(y2 - y, x2 - x)
        s = size * (1 + 0.06 * rng.uniform(-1, 1))
        ux, uy = math.cos(a), math.sin(a)
        nx, ny = -uy, ux
        # chevron: arrow wedge with notch
        ch = [(x + ux * s, y + uy * s), (x - ux * s * 0.6 + nx * s, y - uy * s * 0.6 + ny * s),
              (x - ux * s * 0.15, y - uy * s * 0.15),
              (x - ux * s * 0.6 - nx * s, y - uy * s * 0.6 - ny * s)]
        col = YEL if k % 3 else PINK
        img, px, py = shape_piece([S(*p) for p in ch], col, rng)
        pcs.append(Piece(img, px, py, rng.uniform(-6, 6), shadow=S(4, 5)))
    # final head
    x, y = pts[out[-1]]
    xe, ye = pts[-1]
    img, px, py = shape_piece([S(*p) for p in arrow_poly(x - (xe - x) * 0.6, y - (ye - y) * 0.6, xe, ye,
                                                        10, 14, 34, 46, 0.3)], YEL, rng)
    pcs.append(Piece(img, px, py, 0, shadow=S(5, 6)))
    return pcs


def heat_poster(rng, cx=1772, cy=902, rot=5):
    pcs = []
    W, H = 276, 318
    slab = [(x + cx - W / 2 - 10, y + cy - H / 2 + 10) for x, y in jag_rect(W + 16, H, rng, cut=0.04)]
    img, x, y = shape_piece([S(*p) for p in slab], BLACK, rng)
    pcs.append(Piece(img, x, y, rot - 3, shadow=S(10, 12), sh_col=PINK, sh_alpha=255))
    sheet = [(x + cx - W / 2, y + cy - H / 2) for x, y in jag_rect(W, H, rng, cut=0.03)]
    img, x, y = shape_piece([S(*p) for p in sheet], WHITE, rng,
                            halftone=(PINK, S(9), 45,
                                      lambda xx, yy, s=S(9): s * 0.5 * max(0.0, yy / S(330) - 0.35) ** 0.7))
    pcs.append(Piece(img, x, y, rot, shadow=S(6, 8)))
    star = star_poly(S(cx + 8), S(cy - 2), S(136), S(84), 13, rng, jitter=0.14, rot=0.1)
    img, x, y = shape_piece(star, PINK, rng)
    pcs.append(Piece(img, x, y, rot, shadow=S(5, 6)))
    pcs += ransom_word("HEAT", S(cx - 4), S(cy - 118), S(54), rng, rot_range=7, base_rot=rot + 2,
                       kern=-0.03, shadow=S(5, 6), diecut_p=0.1)
    pcs += ransom_word("62", S(cx + 6), S(cy + 2), S(150), rng, rot_range=6, base_rot=rot - 4,
                       kern=-0.08, shadow=S(8, 10), diecut_p=0.0, halftone_p=0.5, fonts=NUM_FONTS,
                       schemes=[("K", "Y"), ("Y", "K")], size_var=(0.95, 1.08))
    band = [(cx - 158, cy + 104), (cx + 160, cy + 86), (cx + 166, cy + 138), (cx - 150, cy + 154)]
    img, x, y = shape_piece([S(*p) for p in band], BLACK, rng)
    pcs.append(Piece(img, x, y, 0, shadow=S(5, 6), sh_col=YEL, sh_alpha=255))
    pcs += ransom_word("FLAGGED", S(cx + 4), S(cy + 120), S(38), rng, rot_range=8, base_rot=rot - 2,
                       kern=-0.06, shadow=S(3, 4), diecut_p=0.2, size_var=(0.85, 1.15),
                       schemes=[("W", "K"), ("K", "W"), ("K", "Y"), ("W", "P"), ("P", "W")])
    return pcs


def build(seed=21):
    rng = random.Random(seed)
    base = load_base(BASE_CITY, dim=0.9, desat=0.85)
    canvas = new_canvas()
    groups = []
    # --- planned path: home -> target
    groups.append(path_chevrons(rng, (742, 628), (1010, 615), (1268, 592)))
    # --- target: yellow broken ring + HIT THIS burst + arrow
    tgt = ring_segments(1293, 588, 44, 54, [(-80, -10), (8, 92), (112, 160), (182, 250)], rng, col=YEL)
    star = star_poly(S(1448), S(462), S(96), S(60), 11, rng, jitter=0.16, rot=0.3)
    img, x, y = shape_piece(star, WHITE, rng, halftone=(PINK, S(7), 45,
                            lambda xx, yy, s=S(7): s * 0.42 * max(0.0, yy / S(190) - 0.3)))
    tgt.append(Piece(img, x, y, -6, shadow=S(8, 10)))
    img, x, y = shape_piece([S(*p) for p in arrow_poly(1392, 524, 1336, 566, 8, 12, 24, 32)], BLACK, rng)
    tgt.append(Piece(img, x, y, 0, shadow=S(4, 5), sh_col=PINK, sh_alpha=255))
    tgt += ransom_word("HIT", S(1444), S(438), S(50), rng, rot_range=8, base_rot=-4, kern=-0.04, shadow=S(4, 5))
    tgt += ransom_word("THIS", S(1452), S(492), S(42), rng, rot_range=9, base_rot=3, kern=-0.05, shadow=S(4, 5))
    groups.append(tgt)
    # --- home: OURS with a little pointer
    home = []
    slab = [S(520, 652), S(650, 640), S(662, 700), S(530, 712)]
    img, x, y = shape_piece(slab, BLACK, rng, halftone=((52, 46, 56), S(6), 30, 0.3))
    home.append(Piece(img, x, y, 0, shadow=S(7, 8), sh_col=PINK, sh_alpha=255))
    img, x, y = shape_piece([S(*p) for p in arrow_poly(640, 650, 684, 618, 7, 10, 20, 26)], PINK, rng)
    home.append(Piece(img, x, y, 0, shadow=S(4, 5)))
    home += ransom_word("OURS", S(590), S(676), S(44), rng, rot_range=8, base_rot=-3, kern=-0.04,
                        shadow=S(4, 5), schemes=[("K", "W"), ("W", "P"), ("K", "Y"), ("P", "W"), ("W", "K")])
    groups.append(home)
    # --- threat: THEM at the boss
    them = []
    slash = [S(1652, 586), S(1880, 548), S(1900, 616), S(1664, 650)]
    img, x, y = shape_piece(slash, BLACK, rng)
    them.append(Piece(img, x, y, 0, shadow=S(9, 10), sh_col=YEL, sh_alpha=255))
    img, x, y = shape_piece([S(*p) for p in arrow_poly(1672, 632, 1636, 650, 6, 9, 18, 24)], YEL, rng)
    them.append(Piece(img, x, y, 0, shadow=S(4, 5)))
    them += ransom_word("THEM", S(1776), S(598), S(50), rng, rot_range=9, base_rot=8, kern=-0.04,
                        shadow=S(4, 5), schemes=[("P", "K"), ("K", "P"), ("W", "K"), ("K", "W"), ("K", "Y")])
    groups.append(them)
    groups.append(heat_poster(rng))
    for g in groups:
        draw_pieces(canvas, g)
    base = darken_under(base, canvas, 0.45, 30)
    return finish(base, canvas)


if __name__ == "__main__":
    build().save(OUT + "02_city.png")
    print("ok")
