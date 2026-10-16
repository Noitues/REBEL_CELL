"""Side view: the page frame and the overlay drawing, on the locked kits (kit44 / ui31 / r31lib / r32ui / r35ui).

Frame (kept, re-flowed for a full-width street): NETRUN sticker + top strip (Heat / HP / Cycles) + DISPATCH line on
top; a LEFT SIDEBAR stacks the corp-paper dossier, the ROUTE terminal (pick prompt, CONFIRM, GRID VIEW, Save & quit)
and the node file holo slot (TIER, TYPE, REWARDS, HP on arrival); the legend strip sits on the street's cut.
The street owns x 300..1920, so the TARGET tower at the far right is never under a panel.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import kit44 as KT  # noqa: E402
import ui31 as K  # noqa: E402
import r31lib as RL  # noqa: E402
import r32ui as U32  # noqa: E402
import r35ui as R  # noqa: E402
import hq_graph as G  # noqa: E402  (hq: the compound graph)

OUT = os.path.dirname(HERE)
SCR = os.path.join(OUT, "scratch")
W, H = 1920, 1080

LIME = (212, 255, 0)
ORANGE = (255, 140, 26)
WHITE = (242, 246, 255)
GREY = (122, 118, 134)
CASING = (8, 6, 14)
PEN_Y = KT.PEN_Y
PEN_R = KT.PEN_R
GREY_A = 0.26
MIX_A = 0.55
TYPE_COL = {"router": (92, 225, 255), "elite": (255, 96, 40), "terminal": (61, 255, 139), "modem": (90, 150, 255),
            "rack": (255, 196, 60), "target": (255, 44, 60), "start": LIME}
STATE_COL = {"option": ORANGE, "current": LIME, "walked": LIME, "reach": WHITE, "target": WHITE, "grey": GREY}
STK = {"router": "router", "elite": "elite", "terminal": "terminal", "modem": "modem", "rack": "rack", "target": "rack"}


# ---------------------------------------------------------------- cables (2x supersampled)
class Cables:
    S = 2

    def __init__(self):
        self.lay = Image.new("RGBA", (W * self.S, H * self.S), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.lay)
        self.glow = Image.new("L", (W, H), 0)
        self.gd = ImageDraw.Draw(self.glow)

    def _p(self, pts):
        return [(x * self.S, y * self.S) for x, y in pts]

    def _caps(self, p, r, fill):
        for q in (p[0], p[-1]):
            self.d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=fill)

    def solid(self, pts, col, width, casing=3, a=255, glow=0):
        p = self._p(pts)
        if casing:
            self.d.line(p, fill=CASING + (int(a * 0.9),), width=int((width + casing * 2) * self.S), joint="curve")
            self._caps(p, (width / 2 + casing) * self.S, CASING + (int(a * 0.9),))
        self.d.line(p, fill=tuple(col) + (a,), width=int(width * self.S), joint="curve")
        self._caps(p, width / 2 * self.S, tuple(col) + (a,))
        if glow:
            self.gd.line(pts, fill=glow, width=int(width), joint="curve")

    def dashed(self, pts, col, width, on=16, off=10, casing=3, a=255, phase=0.0, glow=0):
        p = self._p(pts)
        if casing:
            self.d.line(p, fill=CASING + (int(a * 0.85),), width=int((width + casing * 2) * self.S), joint="curve")
        on, off = on * self.S, off * self.S
        t = -phase * self.S
        for (x0, y0), (x1, y1) in zip(p, p[1:]):
            L = math.hypot(x1 - x0, y1 - y0)
            if L < 1e-3:
                continue
            ux, uy = (x1 - x0) / L, (y1 - y0) / L
            s = 0.0
            while s < L:
                cyc = (t + s) % (on + off)
                if cyc < on:
                    e = min(L, s + (on - cyc))
                    self.d.line([(x0 + ux * s, y0 + uy * s), (x0 + ux * e, y0 + uy * e)], fill=tuple(col) + (a,),
                                width=int(width * self.S))
                    s = e
                else:
                    s += (on + off) - cyc
            t += L
        if glow:
            self.gd.line(pts, fill=glow, width=int(width), joint="curve")

    def comp(self, img, glow_col=None):
        if glow_col is not None:
            img = K.add_glow(img, self.glow, glow_col, 8, 0.55)
        img.alpha_composite(self.lay.resize((W, H), Image.LANCZOS))
        return img


def poly_len(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def cut_poly(pts, t):
    """The first t (0..1) of a polyline by length, and the point there."""
    L = poly_len(pts) * max(0.0, min(1.0, t))
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        s = math.hypot(b[0] - a[0], b[1] - a[1])
        if L <= s:
            f = L / s if s else 0
            q = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
            out.append(q)
            return out, q
        out.append(b)
        L -= s
    return out, pts[-1]


# ---------------------------------------------------------------- nodes
def sticker(img, kind, x, y, px, grey=False, alpha=1.0, hover=0.0, angle=None):
    ang = angle if angle is not None else ((sum(map(ord, kind)) % 9) - 4) * 0.8
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if kind == "start":
        import markers42 as M42
        disc = M42.cell_disc("fist", px)
        if grey:
            disc = Image.merge("RGBA", (*[disc.convert("L")] * 3, disc.split()[3]))
        lay.alpha_composite(disc, (int(x - px / 2), int(y - px / 2)))
    else:
        sd = U32.node_sd(STK[kind], px, grey=grey)
        lay = RL.place_sticker(lay, sd, x, y, angle=ang, hover=hover, shadow=0.0 if grey else 1.0)
    if alpha < 1.0:
        lay.putalpha(lay.split()[3].point(lambda v: int(v * alpha)))
    img.alpha_composite(lay)
    return img


def ring(img, x, y, r, col, w, alpha=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.ellipse([x - r + 1, y - r + 2, x + r + 1, y + r + 2], outline=(6, 5, 10, int(230 * alpha)), width=w)
    d.ellipse([x - r, y - r, x + r, y + r], outline=tuple(col) + (int(255 * alpha),), width=w)
    img.alpha_composite(lay)
    return img


def frame_poly(img, poly, col, w, alpha=1.0, glow=False):
    """The room's cut edge drawn in its state colour (round 35 hq_climb frames)."""
    lay = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    p = [(x * 2, y * 2) for x, y in poly] + [(poly[0][0] * 2, poly[0][1] * 2)]
    d.line([(x + 2, y + 3) for x, y in p], fill=(6, 5, 10, int(220 * alpha)), width=w * 2, joint="curve")
    d.line(p, fill=tuple(col) + (int(255 * alpha),), width=w * 2, joint="curve")
    if glow:
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).line([(x / 2, y / 2) for x, y in p], fill=255, width=w)
        img = K.add_glow(img, m, col, 10, 0.8)
    img.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    return img


def number_chip(img, x, y, n, col=ORANGE):
    box = (x - 15, y - 16, x + 15, y + 16)
    img = KT.panel_shadow(img, box, 0, blur=6, k=0.55, off=(0, 3))
    d = K.BD(img)
    d.rectangle(box, fill=col + (255,), outline=(10, 8, 14, 255), width=2)
    K.text(img, (x, y + 1), str(n), K.F(K.ANTON, 24), (14, 10, 6), "mm", 0)
    return img


def tag(img, x, y, i, state, anchor="lm"):
    col = {"option": ORANGE, "current": LIME, "walked": LIME, "reach": WHITE, "target": (255, 90, 90),
           "grey": (170, 166, 184)}[state]
    word = G.WORD[G.KIND[i]]
    s = word if G.KIND[i] in ("start", "target") else "%s  L%d" % (word, G.LAYER[i])
    img, box = KT.chip(img, (x, y), s, col, 14, anchor=anchor, pad=7)
    return img


def token(img, x, y, px=46, angle=-14):
    return RL.place_sticker(img, U32.token_sd(px), x, y, angle=angle, hover=0.6)


def target_pencil(cx, cy, rx, ry, word_xy):
    pr = KT.pencil(PEN_R, 381)
    pr.circle(cx, cy, rx, ry, width=9)
    pr.text("TARGET", word_xy[0], word_xy[1], 34, angle=-6)
    return pr


def finish_pencil(img, pr, col=PEN_R):
    img = KT.spill(img, pr.mask.resize((W, H)), col, 0.14, 30)
    return KT.ink(img, pr)


# ---------------------------------------------------------------- page chrome
def chrome_top(img, dispatch):
    img = KT.place_sticker(img, KT.sticker("NETRUN", 46, "yellow", seed=63), 122, 50, angle=-3)
    items = [dict(kind="heat", value=52, w=300), dict(kind="hp", label="HP", value="52", max="/60"),
             dict(kind="cycles", label="CYCLES", value="18")]
    img, box = KT.topbar(img, 250, 14, items, h=66)
    b = (250, 92, 1620, 122)
    img = KT.term(img, b, None, accent=(232, 20, 30), header=False, seed=41, chamfer=8)
    K.text(img, (b[0] + 14, (b[1] + b[3]) / 2), "DISPATCH:", K.F(K.MONO, 15), (255, 70, 70), "lm", 1.2)
    K.text(img, (b[0] + 120, (b[1] + b[3]) / 2), dispatch, K.F(K.MONO, 15), (226, 230, 240), "lm", 0.4)
    return img


SIDE_X1 = 290


def sidebar(img, n_opts, hover=None, picked=None, file_top=724):
    """The left column: dossier (corp paper), ROUTE terminal, node file slot."""
    R.TYPEF, R.TYPEB = K.COUR, K.COUR_B
    op = dict(R.OPERATIVE)
    op["hp"] = "52 / 60"
    dz = R.dossier(op=op, heat_stamp=None)
    dz = dz.resize((int(dz.width * 0.62), int(dz.height * 0.62)), Image.LANCZOS)
    img = RL.drop_shadow(img, dz, 16, 136, blur=14, off=(6, 12), op=0.55)
    box = (14, 476, SIDE_X1, 712)
    img = KT.term(img, box, "ROUTE", seed=23)
    f = K.F(K.MONO, 14)
    K.text(img, (30, 520), "PICK A FLOOR: click a", f, (205, 218, 230), "lm", 0.3)
    K.text(img, (30, 538), "numbered room, then CONFIRM.", f, (205, 218, 230), "lm", 0.3)
    K.text(img, (30, 556), ("Keys 1-%d go now." % n_opts) if n_opts > 1 else "Key 1 goes now.", f, (205, 218, 230), "lm", 0.3)
    if picked:
        img = K.term_button(img, (30, 572, 274, 612), "CONFIRM: %s" % picked, None, state="focus", accent=ORANGE)
    else:
        img = K.term_button(img, (30, 572, 274, 612), "CONFIRM", None, state="disabled")
        K.text(img, (268, 606), "pick first", K.F(K.MONO, 11), (130, 138, 156), "rm", 0.6)
    img = K.term_button(img, (30, 618, 274, 656), "GRID VIEW", None)
    K.text(img, (268, 650), "[G]", K.F(K.MONO, 11), K.CYAN, "rm", 0.6)
    img = K.term_button(img, (30, 662, 274, 700), "Save & quit", None)
    if hover:
        img = node_file(img, hover, (14, file_top, SIDE_X1 + 6, file_top + 262))
    return img


def node_file(img, i, box):
    kind = G.KIND[i]
    tier, typ, rew = G.FILE[kind]
    title = "%s  //  L%d" % (G.WORD[kind], G.LAYER[i])
    rows = [("TIER", tier), ("TYPE", typ), ("REWARDS", rew[0])]
    rows += [("", r) for r in rew[1:]]
    rows += [("sep", ""), ("HP", G.HP_ARRIVE + " on arrival", (140, 255, 170))]
    return KT.holo_file(img, box, title, rows, corp='meridian', seed=12, key_w=78, scale=0.8)   # v2: the HQ's own seal


def legend(img, hot=False, cx=1105):
    def ringf(col):
        def f(px):
            im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
            ImageDraw.Draw(im).ellipse([3, 3, px - 4, px - 4], outline=col + (255,), width=3)
            return im
        return f
    items = [(lambda px, k=k: U32.icon(k, px), lab) for k, lab in (("router", "FIGHT"), ("elite", "ELITE"),
                                                                   ("terminal", "EVENT"), ("modem", "SHOP"), ("rack", "RACK"))]
    items += [(ringf(LIME), "walked"), (ringf(ORANGE), "next"), (ringf(WHITE), "ahead"), (ringf(GREY), "past")]
    hint = "SHOWING ALL" if hot else "HOVER: SHOW ALL"
    f = K.F(K.MONO, 15)
    w = sum(int(30 + f.getlength(lab) + 18) for _, lab in items) + f.getlength("|  " + hint) + 40
    img, box = KT.key_strip(img, int(cx - w / 2), 1030, items, hint=hint, hot=hot)
    return img


def cursor(img, x, y):
    return KT.cursor(img, x, y)


def save(img, path, bloom=True):
    if bloom:
        img = RL.bloom(img, 0.10, 0.84, 8)
    img.convert("RGB").save(path)
    print("saved", os.path.basename(path), flush=True)
    return img


KEY_SWATCH = [LIME, ORANGE, WHITE, GREY, (255, 28, 44), (92, 225, 255), (255, 61, 168), (61, 255, 139), (90, 150, 255),
              (255, 196, 60), (255, 96, 40), (8, 6, 14), (255, 255, 255), (255, 226, 0)]


def save_gif(frames, durs, path, colors=255):
    w, h = frames[0].size
    picks = frames[:: max(1, len(frames) // 6)]
    sw = 120
    mont = Image.new("RGB", (w, h * len(picks) + sw), (0, 0, 0))
    for k, f in enumerate(picks):
        mont.paste(f.convert("RGB"), (0, k * h))
    d = ImageDraw.Draw(mont)
    step = w // len(KEY_SWATCH)
    for k, c in enumerate(KEY_SWATCH):
        d.rectangle([k * step, h * len(picks), (k + 1) * step, h * len(picks) + sw], fill=c)
    pal = mont.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=False, disposal=1)
    print("saved", os.path.basename(path), flush=True)
