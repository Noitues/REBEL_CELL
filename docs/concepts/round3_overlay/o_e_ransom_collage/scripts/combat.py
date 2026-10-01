"""01_combat.png: SEND IT over EXECUTE, target ring, tactical note, crew photo."""
import math
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collage_lib import *  # noqa


def ring_segments(cx, cy, r0, r1, spans, rng, col=PINK):
    """Broken ring of cut paper strips, faceted arcs with slanted ends."""
    out = []
    for a0, a1 in spans:
        n = max(3, int((a1 - a0) / 14))
        outer, inner = [], []
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            ro = r1 + rng.uniform(-3, 3)
            ri = r0 + rng.uniform(-3, 3)
            outer.append((cx + math.cos(a) * ro, cy + math.sin(a) * ro))
            inner.append((cx + math.cos(a) * ri, cy + math.sin(a) * ri))
        # slanted scissor ends
        a = math.radians(a1 + 3)
        outer[-1] = (cx + math.cos(a) * r1, cy + math.sin(a) * r1)
        a = math.radians(a0 - 3)
        inner[0] = (cx + math.cos(a) * r0, cy + math.sin(a) * r0)
        pts = [S(*p) for p in outer + inner[::-1]]
        img, px, py = shape_piece(pts, col, rng)
        out.append(Piece(img, px, py, 0, shadow=S(5, 6)))
    return out


def send_it_parts(rng):
    """Returns (backing pieces, letter pieces, ornament pieces) for the main verb."""
    back = []
    slab = [S(1546, 806), S(1640, 772), S(1790, 786), S(1912, 770), S(1902, 902),
            S(1772, 924), S(1650, 908), S(1556, 918)]
    img, x, y = shape_piece(slab, BLACK, rng, halftone=((52, 46, 56), S(7), 30, 0.32))
    back.append(Piece(img, x, y, 0, shadow=S(11, 12), sh_col=PINK, sh_alpha=255))
    letters = ransom_word("SEND", S(1714), S(848), S(84), rng, rot_range=6, base_rot=4, size_var=(0.9, 1.15),
                          kern=-0.02, shadow=S(6, 8), diecut_p=0.2)
    # struck-through EXECUTE: pink cut slash
    slash = [S(1572, 970), S(1782, 950), S(1784, 958), S(1574, 979)]
    img, x, y = shape_piece(slash, PINK, rng)
    orn = [Piece(img, x, y, 0, shadow=S(4, 5))]
    star = star_poly(S(1846), S(1000), S(74), S(48), 11, rng, jitter=0.16, rot=0.2)
    img, x, y = shape_piece(star, YEL, rng, halftone=(PINK, S(8), 45, 0.18))
    orn.append(Piece(img, x, y, -6, shadow=S(8, 10)))
    letters += ransom_word("IT!", S(1846), S(998), S(58), rng, rot_range=10, base_rot=-8,
                           kern=-0.05, shadow=S(5, 7), diecut_p=0.3,
                           schemes=[("W", "K"), ("K", "W"), ("P", "K"), ("K", "P")])
    return back, letters, orn


def execute_plate(base):
    """The washed-out digital EXECUTE control under the human verb (machine layer)."""
    from PIL import ImageDraw as D
    # wash out the GO button itself
    m = Image.new("L", base.size, 0)
    D.Draw(m).ellipse([1610, 760, 1912, 1030], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(10))
    grey = ImageEnhance.Brightness(ImageEnhance.Color(base.convert("RGB")).enhance(0.0)).enhance(0.55).convert("RGBA")
    base = Image.composite(grey, base, m)
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = D.Draw(lay)
    d.polygon([(1584, 918), (1786, 918), (1772, 998), (1570, 998)], fill=(22, 26, 30, 225),
              outline=(120, 138, 146, 200))
    d.text((1676, 962), "EXECUTE", font=font(UI_FONT, 36), fill=(176, 188, 192, 235), anchor="mm")
    base.alpha_composite(lay)
    return base


def crew_photo(rng):
    pcs = []
    cx, cy, rot = S(190), S(268), -4
    frame = jag_rect(S(252), S(310), rng, cut=0.05)
    frame = [(x - S(126), y - S(155)) for x, y in frame]
    img, _, _ = shape_piece(frame, BLACK, rng)
    pcs.append(Piece(img, cx, cy, rot, shadow=S(10, 12), sh_col=PINK, sh_alpha=255))
    ph = halftone_photo(S(210), S(260), rng)
    m = Image.new("L", ph.size, 0)
    ImageDraw.Draw(m).polygon(jag_rect(ph.width, ph.height, rng, cut=0.02, extra=False), fill=255)
    ph.putalpha(m)
    pcs.append(Piece(ph, cx - S(2), cy - S(8), rot, shadow=None))
    # yellow corner shard + pink cut stripe
    shard = [S(268, 98), S(318, 92), S(300, 160)]
    img, x, y = shape_piece(shard, YEL, rng)
    pcs.append(Piece(img, x, y, 0, shadow=S(5, 6)))
    stripe = [S(64, 360), S(150, 352), S(148, 362), S(62, 371)]
    img, x, y = shape_piece(stripe, PINK, rng)
    pcs.append(Piece(img, x, y, 0, shadow=S(3, 4)))
    pcs += ransom_word("KESTREL", S(196), S(430), S(34), rng, rot_range=9, base_rot=3,
                       kern=-0.06, shadow=S(4, 5), diecut_p=0.15, halftone_p=0.2)
    pcs.append(type_strip("OPERATIVE // CELL-9", S(206), S(466), S(14), rng, fg="W", bg="K", rot=2,
                          shadow=S(3, 4)))
    return pcs


def tactical_note(rng):
    pcs = [
        type_strip("BACKDOOR FIRST.", S(176), S(518), S(21), rng, rot=-2.5),
        type_strip("DRAG THEIR 9 BACK", S(198), S(556), S(21), rng, rot=1.5),
        type_strip("THEN >> SEND IT", S(186), S(596), S(21), rng, fg="K", bg="P", rot=-1),
    ]
    star = star_poly(S(316), S(508), S(22), S(11), 7, rng, jitter=0.2)
    img, x, y = shape_piece(star, YEL, rng)
    pcs.append(Piece(img, x, y, 12, shadow=S(3, 4)))
    return pcs


def target_mark(rng):
    pcs = ring_segments(1360, 412, 252, 270, [(-58, -14), (-2, 50), (128, 184), (196, 238)], rng)
    star = star_poly(S(1690), S(560), S(92), S(58), 9, rng, jitter=0.2, rot=0.4)
    img, x, y = shape_piece(star, WHITE, rng, halftone=(PINK, S(7), 45,
                            lambda xx, yy, s=S(7): s * 0.42 * max(0.0, yy / S(170) - 0.25)))
    pcs.append(Piece(img, x, y, 8, shadow=S(8, 10)))
    pcs += ransom_word("HIT", S(1688), S(540), S(50), rng, rot_range=8, base_rot=6, kern=-0.05,
                       shadow=S(4, 5), schemes=[("W", "K"), ("K", "Y"), ("W", "P"), ("Y", "K")])
    pcs += ransom_word("IT", S(1700), S(594), S(50), rng, rot_range=8, base_rot=-4, kern=-0.05,
                       shadow=S(4, 5), schemes=[("K", "P"), ("W", "K"), ("K", "Y")])
    return pcs


def build(seed=7, verb_state=None):
    """verb_state: callable(back, letters, orn) -> list of pieces for the verb (lifecycle)."""
    rng = random.Random(seed)
    base = load_base(BASE_COMBAT, dim=0.88, desat=0.85)
    canvas = new_canvas()
    crew = crew_photo(rng)
    note = tactical_note(rng)
    target = target_mark(rng)
    back, letters, orn = send_it_parts(rng)
    verb = verb_state(back, letters, orn) if verb_state else back + orn[:1] + letters[:4] + orn[1:] + letters[4:]
    for grp in (crew, note, target, verb):
        draw_pieces(canvas, grp)
    base = darken_under(base, canvas, 0.5, 30)
    base = execute_plate(base)
    return finish(base, canvas)


if __name__ == "__main__":
    build().save(OUT + "01_combat.png")
    print("ok")
