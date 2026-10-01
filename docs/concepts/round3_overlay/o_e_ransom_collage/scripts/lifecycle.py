"""04_lifecycle.png: the SEND IT verb: snap in, idle jitter, scatter out."""
import math
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collage_lib import *  # noqa
import combat

CROP = (1450, 650, 1920, 1080)  # 1x region around the verb


def st_snap(back, letters, orn):
    out = list(back)
    landed = letters[:2]
    out += landed
    n = letters[2]
    # onion-skin trail of the incoming letter, then the letter itself mid-flight
    for k, (sc, dy, rot, a) in enumerate([(1.9, -150, 38, 0.10), (1.65, -100, 26, 0.22)]):
        out.append(n.copy(sx=sc, sy=sc, y=n.y + S(dy), x=n.x + S(dy * -0.25), rot=n.rot + rot,
                          alpha=a, shadow=None))
    out.append(n.copy(sx=1.38, sy=1.38, y=n.y - S(52), x=n.x + S(14), rot=n.rot + 14,
                      shadow=S(16, 20), sh_alpha=150))
    # impact burst where the E just landed
    e = letters[1]
    rng = random.Random(5)
    for i in range(6):
        a = -math.pi / 2 + (i - 2.5) * 0.42
        x0, y0 = e.x / SS + math.cos(a) * 52, e.y / SS + math.sin(a) * 52
        x1, y1 = e.x / SS + math.cos(a) * 74, e.y / SS + math.sin(a) * 74
        img, x, y = shape_piece([S(*p) for p in arrow_poly(x0, y0, x1, y1, 2, 5, 8, 8, 0.0)], YEL, rng)
        out.append(Piece(img, x, y, 0, shadow=S(2, 3)))
    return out


def st_idle(back, letters, orn):
    out = list(back) + orn[:1]
    rng = random.Random(11)
    ghosts = []
    for p in letters[:4]:
        for _ in range(2):
            ghosts.append(p.copy(x=p.x + S(rng.uniform(-4, 4)), y=p.y + S(rng.uniform(-5, 5)),
                                 rot=p.rot + rng.uniform(-4, 4), alpha=0.22, shadow=None))
    out += ghosts + letters[:4] + orn[1:]
    for p in letters[4:]:
        out.append(p.copy(x=p.x + S(rng.uniform(-4, 4)), y=p.y + S(rng.uniform(-5, 5)),
                          rot=p.rot + rng.uniform(-4, 4), alpha=0.22, shadow=None))
    out += letters[4:]
    return out


def st_exit(back, letters, orn):
    rng = random.Random(17)
    cx, cy = S(1730), S(900)
    out = []
    allp = back + orn + letters
    for i, p in enumerate(allp):
        dx, dy = p.x - cx, p.y - cy
        L = math.hypot(dx, dy) or 1
        big = p in back
        dist = S(rng.uniform(20, 40) if big else rng.uniform(45, 110))
        ux, uy = dx / L, dy / L - 0.35
        nx, ny = p.x + ux * dist, p.y + uy * dist + (S(46) if big else 0)
        rot = p.rot + (rng.uniform(8, 13) if big else rng.choice([-1, 1]) * rng.uniform(30, 100))
        flip = 1.0 if big else rng.choice([1.0, 0.35, -0.6, -1.0])
        a = 0.9 if big else rng.uniform(0.8, 1.0)
        # trail ghost halfway
        out.append(p.copy(x=(p.x + nx) / 2, y=(p.y + ny) / 2, rot=(p.rot + rot) / 2, alpha=0.16, shadow=None))
        out.append(p.copy(x=nx, y=ny, rot=rot, sx=flip, alpha=a,
                          shadow=S(12, 16) if not big else S(8, 10)))
    return out


def panel(state):
    im = combat.build(verb_state=state)
    return im.crop(CROP)


def main():
    rng = random.Random(99)
    W, H = 1920, 1080
    bg = paper_fill(W * SS, H * SS, BLACK, rng, grain=4, gloss=0.02).convert("RGBA")
    ht = halftone_dots(W * SS, H * SS, (34, 30, 36), S(12),
                       lambda x, y: S(12) * 0.38 * max(0.0, 1 - y / (H * SS) * 1.3), 30)
    bg.alpha_composite(ht)
    pcs = []
    pcs += ransom_word("SEND IT", S(300), S(92), S(62), rng, rot_range=8, base_rot=-3, kern=-0.04, shadow=S(6, 8))
    pcs.append(type_strip("VERB LIFECYCLE  //  CUT-PAPER LAYER  //  1 OF 1", S(1040), S(96), S(22), rng,
                          fg="W", bg="K", rot=-1))
    labels = [("01", "SNAP IN"), ("02", "IDLE"), ("03", "SCATTER")]
    notes = [
        ["LETTERS LAND ONE BY ONE, 60 MS APART", "EACH: SCALE 1.4 > 1.0, SPIN 14 > 0 DEG", "HARD SHADOW CATCHES UP 1 FRAME LATE"],
        ["EVERY CUT-OUT BOBS +/-2 PX, TICKS +/-2 DEG", "STEPPED AT 8 FPS: PAPER, NOT JELLY", "STARBURST BREATHES 0.97 > 1.03"],
        ["PIECES SCATTER OUTWARD, 30 MS STAGGER", "SOME FLIP: THE WHITE PAPER BACK SHOWS", "SLAB DROPS LAST, 220 MS TOTAL"],
    ]
    pw = 592
    ph = int(pw * (CROP[3] - CROP[1]) / (CROP[2] - CROP[0]))
    canvas = new_canvas()
    shots = []
    for i, st in enumerate((st_snap, st_idle, st_exit)):
        x0 = 45 + i * (pw + 30)
        y0 = 222
        img = panel(st).resize((pw * SS, ph * SS), Image.LANCZOS).convert("RGBA")
        shots.append((img, x0, y0))
        # cut-paper panel number + label
        pcs += ransom_word(labels[i][0], S(x0 + 46), S(y0 - 6), S(50), rng, rot_range=6, base_rot=4,
                           kern=-0.06, shadow=S(5, 6), schemes=[("K", "Y"), ("Y", "K")], fonts=NUM_FONTS)
        pcs += ransom_word(labels[i][1], S(x0 + 120 + len(labels[i][1]) * 14), S(y0 - 4), S(36), rng,
                           rot_range=7, base_rot=-2, kern=-0.05, shadow=S(4, 5))
        for j, line in enumerate(notes[i]):
            pcs.append(type_strip(line, S(x0 + pw / 2 + rng.uniform(-14, 14)), S(y0 + ph + 50 + j * 40), S(17), rng,
                                  fg="K", bg="P" if j == 0 else "W", rot=rng.uniform(-1.5, 1.5)))
    # panels: framed screenshots with hard pink offset
    for img, x0, y0 in shots:
        sh = Image.new("RGBA", img.size, PINK + (255,))
        bg.alpha_composite(sh, (S(x0 + 10), S(y0 + 12)))
        fr = Image.new("RGBA", (img.width + S(12), img.height + S(12)), WHITE + (255,))
        bg.alpha_composite(fr, (S(x0 - 6), S(y0 - 6)))
        bg.alpha_composite(img, (S(x0), S(y0)))
    # arrows between panels
    for i in range(2):
        x = 45 + (i + 1) * (pw + 30) - 15
        img, px, py = shape_piece([S(*p) for p in arrow_poly(x - 26, 500, x + 26, 500, 10, 14, 22, 30)], YEL, rng)
        pcs.append(Piece(img, px, py, 0, shadow=S(4, 5)))
    # palette chips: the whole layer is these four papers
    for k, (name, col) in enumerate((("CELL PINK", PINK), ("INK BLACK", BLACK), ("PAPER WHITE", WHITE),
                                     ("TOXIC", YEL))):
        x = 520 + k * 240
        pts = [S(*p) for p in jag_rect(150, 52, rng, cut=0.06)]
        pts = [(px + S(x - 75), py + S(985)) for px, py in pts]
        img, px, py = shape_piece(pts, col, rng)
        pcs.append(Piece(img, px, py, rng.uniform(-4, 4), shadow=S(5, 6),
                         sh_col=PINK if col == BLACK else BLACK, sh_alpha=255))
        pcs.append(type_strip(name, S(x), S(1048), S(15), rng, fg="W", bg="K", rot=rng.uniform(-2, 2)))
    draw_pieces(canvas, pcs)
    bg.alpha_composite(canvas)
    bg.resize((W, H), Image.LANCZOS).convert("RGB").save(OUT + "04_lifecycle.png")
    print("ok")


if __name__ == "__main__":
    main()
