"""02_city.png -- the City Grid at night, marked up in ink."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inklib as K
import glyphs as Gl
import scenes as S


def label(Lr, text, x, y, cap, seed, tilt=-0.06, wash_w=None, ink_w=None, sumi=True):
    """Black brush word over a pink wash sweep sized to the word."""
    ww = Gl.word_width(text, cap)
    wash_w = wash_w or cap * 2.9
    cy = y + cap * 0.55
    x0, x1 = x - cap * 0.5, x + ww + cap * 1.9
    path = [(x0, cy - tilt * (x0 - x)), ((x0 + x1) / 2, cy - tilt * ((x0 + x1) / 2 - x) + cap * 0.06),
            (x1, cy - tilt * (x1 - x))]
    m = K.stroke_mask(path, wash_w, seed + 1, dry=0.8, wet=0.74, splat=0.0)
    K.wash(Lr.wash, m, (x0 - 30, cy - wash_w, x1 + 60, cy + wash_w), seed + 2,
           soft=4.5, rough=0.6, body=170, edge=0.4)
    S.ink_word(Lr.sumi if sumi else Lr.pink, text, x, y, cap, seed, width=ink_w or cap * 0.24, dry=0.55, wet=0.62)


def build():
    Lr = S.Layers()
    pk = Lr.pink
    # target: HIT THIS
    S.enso(pk, 1291, 598, 54, 50, 120, 320, 7, 11, dry=0.8, wet=0.45)
    label(Lr, "HIT THIS", 1352, 456, 42, 12)
    K.brush_stroke(pk, [(1352, 512), (1336, 532), (1324, 552)], 4.5, 13, dry=0.5, splat=0.5)
    # home: OURS
    S.enso(pk, 705, 607, 50, 46, 200, 318, 7, 21, dry=0.8, wet=0.45)
    label(Lr, "OURS", 474, 648, 42, 22)
    # the planned route, one dry pass of the brush, home -> target
    K.brush_stroke(pk, [(752, 654), (850, 724), (960, 792), (1080, 788), (1190, 724), (1252, 662)], 8, 31,
                   dry=0.7, wet=0.55, splat=0.3)
    K.brush_stroke(pk, [(1206, 668), (1234, 662), (1260, 655)], 9, 32, dry=0.4, splat=0.2, mode="l")
    K.brush_stroke(pk, [(1250, 708), (1254, 682), (1260, 656)], 9, 33, dry=0.4, splat=0.4, mode="l")
    # threat: THEM!
    S.ink_word(pk, "THEM!", 1678, 586, 46, 41, width=9, dry=0.55)
    K.brush_stroke(pk, [(1682, 650), (1770, 646), (1866, 640)], 6, 42, dry=0.85, wet=0.3, splat=0.5)
    K.brush_stroke(pk, [(1674, 622), (1652, 640), (1634, 652)], 4.5, 43, dry=0.5, splat=0.4)
    # Heat poster: torn washi, two tapes, brushed 62, FLAGGED seal
    pl = K.Place(1772, 906, 2.5)
    Lr.papers.append((K.paper_patch(232, 300, 51), pl))
    Lr.tapes.append((K.tape_patch(70, 24, 52), K.Place(*pl(-104, -142), -38)))
    Lr.tapes.append((K.tape_patch(70, 24, 53, color=(255, 128, 182), alpha=170), K.Place(*pl(104, -142), 36)))
    c = pl(2, -4)
    K.wash(Lr.wash, K.disc_fn(c[0], c[1], 74), (c[0] - 90, c[1] - 90, c[0] + 90, c[1] + 90), 54, rough=0.7, body=150, bloom=0.5)
    S.ink_word(Lr.sumi, "HEAT", *pl(-96, -130), 30, 55, width=6.5, dry=0.5)
    K.font_ink(Lr.sumi, ["they see us."], pl, 18, 56, x0=10, y0=-122)
    S.ink_word(Lr.sumi, "62", *pl(-84, -62), 112, 57, width=25, dry=0.75, wet=0.5)
    Lr.seals.append((Gl.seal_patch(["FLAGGED"], 200, 50, 58), K.Place(*pl(4, 112), -4)))
    return Lr


def render(out_path):
    base = K.load_base(S.BASE_CITY)
    cv = build().compose(base)
    img = K.finish(cv)
    img.save(out_path)
    return img


if __name__ == "__main__":
    render(os.path.join(S.OUT, "02_city.png"))
