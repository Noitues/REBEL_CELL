"""01_combat.png -- also exposes the pieces the lifecycle strip re-uses."""
import sys
import os
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inklib as K
import glyphs as Gl
import scenes as S
import random

GO = (1760, 895)


def machine_layer(base):
    """The washed-out system button the human writes over (replaces GO with a dead EXECUTE)."""
    d = ImageDraw.Draw(base)
    rng = random.Random(41)
    d.polygon([(x * K.SS, y * K.SS) for x, y in S.hexagon(*GO, 146, 0)], fill=(20, 20, 24, 255))
    S.facet_fill(d, S.hexagon(*GO, 120, 0), rng, (84, 78, 74), var=10)
    d.line([(x * K.SS, y * K.SS) for x, y in S.hexagon(*GO, 132, 0) + [S.hexagon(*GO, 132, 0)[0]]],
           fill=(58, 56, 56, 255), width=2 * K.SS)
    S.sys_text(d, (GO[0], GO[1] - 4), "EXECUTE", 42, (148, 140, 132, 255))
    S.sys_text(d, (GO[0], GO[1] + 40), "SPIN BOTH WHEELS", 16, (118, 112, 106, 255))
    return base


VERB_STROKES = None


def verb_strokes():
    send = Gl.layout("SEND", 1594, 800, 84, seed=101, track=0.04)
    it = Gl.layout("IT", 1712, 900, 120, seed=202, rot=3)
    return send, it


def verb_wash_mask():
    """Two tapered wet sweeps (one per line) with dry-brush tails flying off to the right."""
    m = K.stroke_mask([(1582, 874), (1700, 848), (1830, 826), (1918, 798)], 150, 83, dry=0.85, wet=0.62)
    m = K.ImageChops.lighter(m, K.stroke_mask([(1664, 994), (1790, 962), (1918, 934)], 172, 84, dry=0.85, wet=0.58))
    return m


def paint_verb(Lr, cut_frac=None, head=True):
    """Pink wash swash, then SEND / IT stroke by stroke, then the underline flick and the seal.
    cut_frac: 0..1 of the painting (None = complete)."""
    send, it = verb_strokes()
    under = [("c", [(1688, 1042), (1780, 1030), (1890, 1012)], "f", 909)]
    wash_m = verb_wash_mask()
    # measure
    tmp = K.Ink()
    lens = [Gl.paint(tmp, send, 24, cut=0), Gl.paint(tmp, it, 33, cut=0), Gl.paint(tmp, under, 9, cut=0)]
    total = sum(lens)
    wash_part = 0.12
    if cut_frac is None:
        K.wash(Lr.wash, wash_m, (1560, 760, 1915, 1060), 78, soft=3, rough=0.32, body=165, edge=0.4)
        Gl.paint(Lr.sumi, send, 24, dry=0.6, wet=0.6)
        Gl.paint(Lr.sumi, it, 33, dry=0.7, wet=0.55)
        Gl.paint(Lr.sumi, under, 9, dry=0.9, wet=0.25, splat=0.8)
        Lr.seals.append((Gl.seal_patch(["CE", "LL"], 50, 50, 5), K.Place(1612, 1016, -6)))
        return
    # animation: wash blooms in first (fast), then the brush writes
    wf = min(1.0, cut_frac / wash_part)
    if wf > 0:
        m = K.scale_l(wash_m, 1.0)
        if wf < 1:
            # reveal the swash along its length, left to right
            mask = Image.new("L", m.size, 0)
            x_cut = int((1585 + (1915 - 1585) * wf) * K.SS)
            ImageDraw.Draw(mask).rectangle((0, 0, x_cut, m.size[1]), fill=255)
            m = K.ImageChops.multiply(m, K.blur(mask, 18 * K.SS))
        K.wash(Lr.wash, m, (1560, 760, 1915, 1060), 78, soft=3, rough=0.32, body=int(165 + 40 * (1 - wf)), edge=0.4)
    ink_frac = max(0.0, (cut_frac - wash_part) / (1 - wash_part))
    rem = ink_frac * total
    for strokes, w, kw in ((send, 24, dict(dry=0.6, wet=0.6)), (it, 33, dict(dry=0.7, wet=0.55)),
                           (under, 9, dict(dry=0.9, wet=0.25, splat=0.8))):
        if rem <= 0:
            break
        Gl.paint(Lr.sumi, strokes, w, cut=rem, head=head, **kw)
        rem -= Gl.paint(tmp, strokes, w, cut=0)
    if cut_frac >= 0.999:
        Lr.seals.append((Gl.seal_patch(["CE", "LL"], 50, 50, 5), K.Place(1612, 1016, -6)))


def static_layers():
    Lr = S.Layers()
    # target annotation on the enemy wheel: pink ensō round the 9, NOW, leader
    S.enso(Lr.pink, 1238, 386, 68, 63, -70, 318, 8, 31, dry=0.8, wet=0.45)
    S.ink_word(Lr.pink, "NOW", 1002, 232, 46, 32, width=9, dry=0.6)
    K.brush_stroke(Lr.pink, [(1112, 290), (1146, 314), (1172, 344)], 5, 33, dry=0.5, wet=0.4, splat=0.6)
    for (a, b) in (((1158, 330), (1176, 348)), ((1188, 326), (1176, 348))):
        pass
    # tactical note on torn washi, taped, near the enemy
    pl = K.Place(1752, 262, 4)
    Lr.papers.append((K.paper_patch(272, 150, 61), pl))
    Lr.tapes.append((K.tape_patch(92, 26, 62), K.Place(*pl(-6, -76), 9)))
    S.note_text(Lr, ["ICE stalls on the 9.", "Backdoor first,", "then send it."], pl, 27, 63, x0=-122, y0=-56)
    K.brush_stroke(Lr.pink, pl.pts([(-6, -26), (36, -28), (78, -24)]), 5, 64, dry=0.7, wet=0.3, splat=0.2)
    # crew portrait on rice paper
    pp = K.Place(196, 296, -3)
    Lr.papers.append((K.paper_patch(206, 270, 71, tone=(238, 232, 218)), pp))
    S.portrait(Lr, pp, 700)
    K.font_ink(Lr.sumi, ["NEEDLE"], pp, 24, 72, x0=-88, y0=98)
    Lr.seals.append((Gl.seal_patch(["9"], 30, 30, 73, shape="round"), K.Place(*pp(70, 114), -8)))
    Lr.tapes.append((K.tape_patch(84, 26, 74, color=(255, 128, 182), alpha=170), K.Place(*pp(-4, -133), -10)))
    return Lr


def render(out_path):
    base = machine_layer(K.load_base(S.BASE_COMBAT))
    cv = static_layers().compose(base)
    Lv = S.Layers()
    paint_verb(Lv)
    cv = Lv.compose(cv)
    img = K.finish(cv)
    img.save(out_path)
    return img


if __name__ == "__main__":
    render(os.path.join(S.OUT, "01_combat.png"))
