"""Overlay compositions for the three base screens (sumi-ink & watercolour medium)."""
import math
import random
from PIL import Image, ImageDraw, ImageFont
import inklib as K
import glyphs as Gl

ROOT = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\docs\concepts"
BASE_COMBAT = ROOT + r"\round2\r2c_geo_vector_gritty\stills\04_combat.png"
BASE_CITY = ROOT + r"\round2\r2c_geo_vector_gritty\stills\02_city_night.png"
BASE_SHOP = ROOT + r"\round2\r2c_v2_modem\modem_shop.png"
OUT = ROOT + r"\round3_overlay\o_f_ink_brush"

SYS_FONT = K.FONTS + "bahnschrift.ttf"


class Layers:
    """Everything one screen's overlay paints into, composited in a fixed order."""

    def __init__(self):
        self.sumi = K.Ink()
        self.pink = K.Ink()
        self.wash = K.Pigment()
        self.acid = K.Pigment()
        self.usumi = K.Pigment()
        self.papers = []   # (patch, place)
        self.tapes = []    # (patch, place)
        self.seals = []    # (patch, place)
        self.dim = Image.new("L", (K.CW, K.CH), 0)  # extra base knock-back under marks

    def compose(self, base, sheen=0.22, bleed=0.12, pink_sheen=0.0, matte=0.0, dim_on=True):
        cv = base.copy()
        # 1. knock back the base a touch under the human layer so it reads
        _, pa, _ = K.ink_layers(self.pink, K.PINK_INK_THIN, K.PINK_INK_DENSE)
        dim = K.ImageChops.lighter(self.dim, pa)
        dim = K.ImageChops.lighter(dim, K.scale_l(self.wash.m, 0.8))
        if dim_on:
            K.darken_under(cv, dim, amount=0.42, radius=16)
        # 2. paper (with soft contact shadow)
        for patch, pl in self.papers:
            K.paste_patch(cv, patch, pl)
        # 3. watercolour
        for pig, lt, dp in ((self.usumi, K.USUMI_LIGHT, K.USUMI_DEEP),
                            (self.acid, K.ACID_WASH_LIGHT, K.ACID_WASH_DEEP),
                            (self.wash, K.PINK_WASH_LIGHT, K.PINK_WASH_DEEP)):
            c, a = K.pigment_layers(pig, lt, dp)
            K.comp(cv, c, a)
        # 4. seals sit in the paper / wash, under the brush
        for patch, pl in self.seals:
            K.paste_patch(cv, patch, pl, shadow=0)
        # 5. ink
        c, a, sh = K.ink_layers(self.pink, K.PINK_INK_THIN, K.PINK_INK_DENSE, sheen=pink_sheen, bleed=bleed * 0.6)
        K.comp(cv, c, a)
        if sh is not None:
            K.comp(cv, K.solid((255, 236, 246), (K.CW, K.CH)), sh)
        c, a, sh = K.ink_layers(self.sumi, K.SUMI_THIN, K.SUMI_DENSE, sheen=sheen, bleed=bleed, matte=matte)
        K.comp(cv, c, a)
        if sh is not None:
            K.comp(cv, K.solid((236, 232, 246), (K.CW, K.CH)), sh)
        # 6. tape over everything it holds
        for patch, pl in self.tapes:
            K.paste_patch(cv, patch, pl, shadow=0.25, sh_off=(1, 2), sh_blur=2)
        return cv


# machine-layer stand-ins (the washed-out system buttons the human writes over) ------------
def facet_fill(draw, poly, rng, base, var=14, sat_keep=1.0):
    S = K.SS
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    B = []
    for a, b in zip(poly, poly[1:] + poly[:1]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 45))
        for i in range(n):
            t = i / n
            B.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    I = [(cx + (x - cx) * rng.uniform(0.45, 0.6), cy + (y - cy) * rng.uniform(0.45, 0.6)) for x, y in B]
    c = (cx + rng.uniform(-8, 8), cy + rng.uniform(-8, 8))

    def col():
        d = rng.randint(-var, var)
        return tuple(int(K.clamp(v + d, 0, 255)) for v in base)
    n = len(B)
    for i in range(n):
        j = (i + 1) % n
        for tri in ((B[i], B[j], I[i]), (I[i], B[j], I[j]), (c, I[i], I[j])):
            draw.polygon([(x * S, y * S) for x, y in tri], fill=col())


def sys_text(draw, xy, text, size, fill, anchor="mm", spacing=0):
    f = ImageFont.truetype(SYS_FONT, int(size * K.SS))
    try:
        f.set_variation_by_name("Bold")
    except Exception:
        pass
    draw.text((xy[0] * K.SS, xy[1] * K.SS), text, font=f, fill=fill, anchor=anchor)


def hexagon(cx, cy, r, rot=0.0):
    return [(cx + r * math.cos(math.radians(60 * i + rot)), cy + r * math.sin(math.radians(60 * i + rot))) for i in range(6)]


# ---------------------------------------------------------------------------------------------
def portrait(Lr, pl, seed):
    """Quick ink portrait sketch of the operative on a rice-paper card (local coords)."""
    rng = random.Random(seed)
    P = pl.pts
    # pink sun disc behind the head, upper right (hinomaru echo)
    c = pl(50, -76)
    K.wash(Lr.wash, K.disc_fn(c[0], c[1], 40), (c[0] - 60, c[1] - 60, c[0] + 60, c[1] + 60), seed + 1, rough=0.6, body=150, bloom=0.4)
    # hair mass: a dark sumi wash under the strokes
    hb = pl(0, 0)
    K.wash(Lr.usumi, K.swash_fn(P([(-60, 44), (-68, -30), (-40, -92), (10, -102), (52, -80), (64, -30), (60, 20)]), 15, taper=0.2, seed=seed + 30),
           (hb[0] - 100, hb[1] - 130, hb[0] + 100, hb[1] + 80), seed + 31, soft=3, rough=0.6, body=200)
    K.wash(Lr.usumi, K.stroke_mask(P([(-44, -20), (-46, 14), (-30, 44)]), 14, seed + 21, dry=0.6, wet=0.4),
           (pl(0, 0)[0] - 90, pl(0, 0)[1] - 90, pl(0, 0)[0] + 90, pl(0, 0)[1] + 90), seed + 22, soft=3, rough=0.5, body=80)
    s = Lr.sumi
    # hair: a heavy wet bob, laid in three fast sweeps
    K.brush_stroke(s, P([(-4, -104), (-46, -92), (-68, -48), (-68, 10), (-60, 50)]), 34, seed + 4, dry=0.45, wet=0.7, splat=0.4, entry=1.4)
    K.brush_stroke(s, P([(0, -106), (42, -94), (64, -56), (66, -8), (60, 26)]), 28, seed + 5, dry=0.6, wet=0.6, splat=0.3)
    K.brush_stroke(s, P([(-58, -72), (-20, -66), (20, -58), (52, -40)]), 24, seed + 6, dry=0.7, wet=0.5, splat=0.2)
    # face: found-and-lost contour
    K.brush_stroke(s, P([(54, -6), (48, 22), (30, 44), (4, 54)]), 4, seed + 8, dry=0.4, wet=0.6, splat=0, end="f")
    K.brush_stroke(s, P([(-46, 24), (-30, 44), (-10, 52)]), 3, seed + 9, dry=0.7, wet=0.3, splat=0)
    # eyes, nose, mouth
    K.brush_stroke(s, P([(-32, -12), (-12, -13)]), 4.5, seed + 12, dry=0.2, splat=0, mode="l", end="s")
    K.brush_stroke(s, P([(14, -13), (34, -11)]), 4.5, seed + 13, dry=0.2, splat=0, mode="l", end="s")
    K.brush_stroke(s, P([(4, -4), (-1, 16), (8, 19)]), 2.6, seed + 14, dry=0.2, splat=0, mode="l")
    K.brush_stroke(s, P([(-11, 33), (2, 35), (12, 31)]), 3.4, seed + 15, dry=0.3, splat=0)
    # neck + jacket collar, confident heavy sweeps
    K.brush_stroke(s, P([(-18, 54), (-20, 74)]), 3, seed + 16, dry=0.5, splat=0, mode="l")
    K.brush_stroke(s, P([(20, 52), (22, 72)]), 3, seed + 17, dry=0.5, splat=0, mode="l")
    K.brush_stroke(s, P([(-98, 88), (-64, 62), (-24, 70)]), 20, seed + 18, dry=0.8, wet=0.35, splat=0.3)
    K.brush_stroke(s, P([(96, 86), (58, 60), (18, 72)]), 20, seed + 19, dry=0.8, wet=0.35, splat=0.3)
    # pink visor slash across the eyes: the one cyber note
    K.brush_stroke(Lr.pink, P([(-60, -10), (0, -14), (64, -19)]), 9, seed + 20, dry=0.85, wet=0.25, splat=0.3)


def note_text(Lr, lines, pl, size, seed, x0, y0, lead=1.15):
    K.font_ink(Lr.sumi, lines, pl, size, seed, x0=x0, y0=y0, lead=lead)


def ink_word(ink, text, x, y, cap, seed, width=None, **kw):
    st = Gl.layout(text, x, y, cap, seed)
    Gl.paint(ink, st, width or cap * 0.19, **kw)
    return st


def enso(ink, cx, cy, rx, ry, start_deg, sweep_deg, width, seed, dry=0.75, wet=0.4, splat=0.5, wobble=0.04):
    rng = random.Random(seed)
    pts = []
    n = 24
    for i in range(n + 1):
        a = math.radians(start_deg + sweep_deg * i / n)
        k = 1 + rng.uniform(-wobble, wobble) + 0.05 * i / n
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return K.brush_stroke(ink, pts, width, seed, dry=dry, wet=wet, splat=splat)
