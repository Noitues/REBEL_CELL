"""03_shop.png -- the MODEM shop, marked up in ink."""
import sys
import os
import random
from PIL import ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inklib as K
import glyphs as Gl
import scenes as S
from render_city import label


def dashed_rect(d, box, color, dash=10, gap=7, w=2):
    x0, y0, x1, y1 = [v * K.SS for v in box]
    dash, gap, w = dash * K.SS, gap * K.SS, w * K.SS
    for (a, b, horiz, fixed) in ((x0, x1, True, y0), (x0, x1, True, y1), (y0, y1, False, x0), (y0, y1, False, x1)):
        t = a
        while t < b:
            e = min(b, t + dash)
            d.line([(t, fixed), (e, fixed)] if horiz else [(fixed, t), (fixed, e)], fill=color, width=w)
            t = e + gap


def machine_layer(base):
    """Dead system buttons (PURCHASE / EXIT) replacing the old sticker stack."""
    d = ImageDraw.Draw(base)
    rng = random.Random(5)
    d.rectangle([v * K.SS for v in (22, 760, 290, 1052)], fill=(15, 17, 25, 255))
    for box, word in (((38, 776, 274, 894), "PURCHASE"), ((38, 928, 274, 1038), "EXIT")):
        d.rectangle([v * K.SS for v in box], fill=(26, 30, 40, 255))
        dashed_rect(d, box, (66, 100, 110, 255))
        S.sys_text(d, ((box[0] + box[2]) / 2, box[3] - 24), word, 26, (104, 128, 136, 255))
    return base


def price_tag(Lr, x, y, ang, text, seed):
    pl = K.Place(x, y, ang)
    Lr.papers.append((K.paper_patch(66, 44, seed, amp=2.2, fibre=0.7), pl))
    c = pl(22, -10)
    K.wash(Lr.wash, K.disc_fn(c[0], c[1], 7), (c[0] - 20, c[1] - 20, c[0] + 20, c[1] + 20), seed + 1, rough=0.6, body=150, bloom=0.3)
    ww = Gl.word_width(text, 26)
    S.ink_word(Lr.sumi, text, *pl(-ww / 2, -13), 26, seed + 2, width=5.5, dry=0.5)
    Lr.tapes.append((K.tape_patch(30, 14, seed + 3), K.Place(*pl(-30, -20), ang - 40)))


def build():
    Lr = S.Layers()
    # BUY over PURCHASE (primary verb: sumi on pink), LEAVE over EXIT (secondary: pink ink)
    label(Lr, "BUY", 76, 790, 62, 101, wash_w=140)
    S.ink_word(Lr.pink, "LEAVE", 60, 960, 48, 102, width=10, dry=0.55)
    # the pick: ensō round +1 DAMAGE, arrow from the note
    S.enso(Lr.pink, 1222, 606, 97, 87, -28, 326, 8, 111, dry=0.8, wet=0.5)
    K.brush_stroke(Lr.pink, [(1402, 560), (1372, 572), (1328, 584)], 7, 112, dry=0.4, wet=0.6, splat=0.3)
    K.brush_stroke(Lr.pink, [(1352, 560), (1340, 572), (1326, 585)], 7, 113, dry=0.3, splat=0.2, mode="l")
    K.brush_stroke(Lr.pink, [(1348, 608), (1338, 596), (1326, 586)], 7, 114, dry=0.3, splat=0.3, mode="l")
    # washi sheet replacing the old scrawl
    pl = K.Place(1632, 520, -2)
    Lr.papers.append((K.paper_patch(458, 382, 121), pl))
    Lr.tapes.append((K.tape_patch(96, 28, 122), K.Place(*pl(-200, -184), -32)))
    Lr.tapes.append((K.tape_patch(96, 28, 123, color=(255, 128, 182), alpha=170), K.Place(*pl(206, -180), 28)))
    for (wx, wy, cap) in ((-186, -150, 80), (-120, -52, 80)):
        pass
    sweep = K.stroke_mask(pl.pts([(-200, -60), (-40, -78), (140, -96), (216, -100)]), 190, 124, dry=0.8, wet=0.7, splat=0)
    a, b = pl(-230, -192), pl(230, 192)
    K.wash(Lr.wash, sweep, (a[0], a[1], b[0], b[1]), 125, soft=4.5, rough=0.6, body=165, edge=0.45)
    S.ink_word(Lr.sumi, "THIS", *pl(-186, -164), 80, 126, width=19, dry=0.6, wet=0.6)
    S.ink_word(Lr.sumi, "ONE!", *pl(-104, -64), 80, 127, width=19, dry=0.65, wet=0.6)
    K.font_ink(Lr.sumi, ["+1 DAMAGE. grab it before", "the cycle eats it."], pl, 25, 128, x0=-196, y0=58)
    Lr.seals.append((Gl.seal_patch(["OK"], 62, 62, 129, shape="round", negative=False, border=0.09), K.Place(*pl(166, 124), 10)))
    # price tags, beside (never over) the machine prices
    price_tag(Lr, 532, 396, -6, "25", 141)
    price_tag(Lr, 1300, 396, 5, "75", 145)
    price_tag(Lr, 1302, 758, -4, "60", 149)
    return Lr


def render(out_path):
    base = machine_layer(K.load_base(S.BASE_SHOP))
    cv = build().compose(base)
    img = K.finish(cv)
    img.save(out_path)
    return img


if __name__ == "__main__":
    render(os.path.join(S.OUT, "03_shop.png"))
