"""Route map graph: the shared page frame and graph drawing, built on the locked kits (kit44 / ui31 / r32ui / r35ui).

Frame (kept from the build + round 44): NETRUN sticker, top strip (Heat / HP / Cycles), DISPATCH line, the corp-paper
dossier, the ROUTE terminal (pick prompt, CONFIRM, GRID VIEW, Save & quit), the node file holo (TIER, TYPE, REWARDS,
HP on arrival), the legend strip. Graph drawing: node stickers (the round 31/32 node-type stickers, never redrawn),
state rings, cables (2x supersampled), tags, the red-pencil TARGET. All randomness is seeded.
"""
import math
import os
import sys

os.environ.setdefault("NET36", "net_scope.json")
os.environ.setdefault("RUN_V3", "1")
os.environ.setdefault("SOLID40", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance  # noqa: E402

import kit44 as KT  # noqa: E402
import ui31 as K  # noqa: E402
import r31lib as RL  # noqa: E402
import r32ui as U32  # noqa: E402
import r35ui as R  # noqa: E402
import sticker_lib31 as SL  # noqa: E402
import rgraph as G  # noqa: E402

OUT = os.path.dirname(HERE)
SCR = os.path.join(OUT, "scratch")
W, H = 1920, 1080

# ---------------------------------------------------------------- tokens (bible 2.2; the run colours of 4.6)
LIME = (212, 255, 0)          # walked / owned
ORANGE = (255, 140, 26)       # RING_AVAILABLE, available next
WHITE = (242, 246, 255)       # RING_UNAVAILABLE, not yet available
GREY = (122, 118, 134)        # RING_CUT, past / cut off
CASING = (8, 6, 14)
GREY_A = 0.26                 # past / cut-off group opacity (nodes + links)
MIX_A = 0.55                  # node_hover: reachable but not from the hovered option
STICKER_PX = {"option": 68, "current": 62, "walked": 52, "reach": 60, "grey": 50, "target": 84, "start": 56}
STK = {"router": "router", "elite": "elite", "terminal": "terminal", "modem": "modem", "rack": "rack", "target": "rack"}


# ---------------------------------------------------------------- plate
def plate():
    return Image.open(os.path.join(SCR, "plate_city.png")).convert("RGBA")


def grade(img, k=1.0, sat=1.0, blur=0.0):
    rgb = img.convert("RGB")
    if blur:
        rgb = rgb.filter(ImageFilter.GaussianBlur(blur))
    if sat != 1.0:
        rgb = ImageEnhance.Color(rgb).enhance(sat)
    if k != 1.0:
        rgb = ImageEnhance.Brightness(rgb).enhance(k)
    return rgb.convert("RGBA")


def dim_mask(img, mask_l, k):
    """Darken the world under an L mask by factor k (1 = untouched)."""
    return K.over(img, (3, 2, 8), mask_l, 1 - k)


# ---------------------------------------------------------------- cables (2x supersampled layer)
class Cables:
    S = 2

    def __init__(self):
        self.lay = Image.new("RGBA", (W * self.S, H * self.S), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.lay)

    def _p(self, pts):
        return [(x * self.S, y * self.S) for x, y in pts]

    def solid(self, pts, col, width, casing=4, a=255):
        p = self._p(pts)
        if casing:
            self.d.line(p, fill=CASING + (min(255, int(a * 0.9)),), width=int((width + casing * 2) * self.S), joint="curve")
            for q in (p[0], p[-1]):
                r = (width / 2 + casing) * self.S
                self.d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=CASING + (min(255, int(a * 0.9)),))
        self.d.line(p, fill=tuple(col) + (a,), width=int(width * self.S), joint="curve")

    def dashed(self, pts, col, width, on=16, off=10, casing=4, a=255, phase=0.0, casing_solid=True):
        p = self._p(pts)
        if casing and casing_solid:
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

    def get(self):
        return self.lay.resize((W, H), Image.LANCZOS)


def offset_poly(pts, d):
    """Offset an open polyline sideways by d px (miter, clamped) for parallel lanes."""
    if abs(d) < 1e-6:
        return list(pts)
    out = []
    n = len(pts)
    for i in range(n):
        if i == 0:
            dx, dy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L, dx / L
            out.append((pts[0][0] + nx * d, pts[0][1] + ny * d))
        elif i == n - 1:
            dx, dy = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L, dx / L
            out.append((pts[-1][0] + nx * d, pts[-1][1] + ny * d))
        else:
            ax, ay = pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
            bx, by = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
            la, lb = math.hypot(ax, ay) or 1, math.hypot(bx, by) or 1
            n1 = (-ay / la, ax / la)
            n2 = (-by / lb, bx / lb)
            mx, my = n1[0] + n2[0], n1[1] + n2[1]
            ml = math.hypot(mx, my) or 1
            mx, my = mx / ml, my / ml
            cos = mx * n1[0] + my * n1[1]
            k = d / max(0.5, cos)
            out.append((pts[i][0] + mx * k, pts[i][1] + my * k))
    return out


# ---------------------------------------------------------------- node stickers
_cache = {}


def node_sd(kind, px, grey=False):
    return U32.node_sd(STK[kind], px, grey=grey)


def start_disc(px):
    """The start = the Cell's owned node: the locked v4 'yours' fist disc (markers42)."""
    import markers42 as M42
    return M42.cell_disc("fist", px)


def ring_layer(lay, x, y, r, col, w):
    d = ImageDraw.Draw(lay)
    d.ellipse([x - r + 1, y - r + 2, x + r + 1, y + r + 2], outline=(6, 5, 10, 230), width=w)
    d.ellipse([x - r, y - r, x + r, y + r], outline=tuple(col) + (255,), width=w)


def draw_node(img, i, x, y, state, hover=False, alpha=1.0, glow=True):
    """Draw node i at (x, y) (sticker centre). state: option/current/walked/reach/target/grey. Returns img."""
    kind = G.KIND[i]
    px = STICKER_PX["target" if kind == "target" else ("start" if kind == "start" else state)]
    if kind == "target" and state == "grey":
        px = 70
    ang = ((sum(map(ord, i)) % 9) - 4) * 0.8
    grey = state == "grey"
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if kind == "start":
        disc = start_disc(px)
        if grey:
            disc = Image.merge("RGBA", (*[disc.convert("L")] * 3, disc.split()[3]))
        lay.alpha_composite(disc, (int(x - px / 2), int(y - px / 2)))
    else:
        sd = node_sd(kind, px, grey=grey)
        lay = RL.place_sticker(lay, sd, x, y, angle=ang, hover=0.55 if hover else (0.25 if state == "option" else 0.0),
                               shadow=0.0 if grey else 1.0)
    ring = {"option": (ORANGE, 5), "current": (LIME, 5), "walked": (LIME, 3), "reach": (WHITE, 3), "grey": (GREY, 3),
            "target": (WHITE, 3)}[state]
    if kind != "target" or state == "grey":
        ring_layer(lay, x, y - (5 if hover else 0), px / 2 + 7, ring[0], ring[1])
    if alpha < 1.0:
        a = lay.split()[3].point(lambda v: int(v * alpha))
        lay.putalpha(a)
    if glow and not grey and alpha >= 0.99 and state in ("option", "current"):
        m = Image.new("L", (W, H), 0)
        r = px / 2 + 7
        ImageDraw.Draw(m).ellipse([x - r, y - r, x + r, y + r], outline=255, width=5)
        img = K.add_glow(img, m, ring[0], 9, 0.9)
    img.alpha_composite(lay)
    return img


def token(img, x, y, off=(38, 30)):
    """The operative token = YOU ARE HERE (no words). Sits on the side of the current node away from its options."""
    return RL.place_sticker(img, U32.token_sd(50), x + off[0], y + off[1], angle=-14, hover=0.6)


def number_chip(img, x, y, n, col=ORANGE, fill=None):
    """The locked option number chip (key hint, no words)."""
    f = K.F(K.MONO, 19)
    box = (x - 15, y - 16, x + 15, y + 16)
    img = KT.panel_shadow(img, box, 0, blur=6, k=0.55, off=(0, 3))
    d = K.BD(img)
    d.rectangle(box, fill=(fill or col) + (255,), outline=(10, 8, 14, 255), width=2)
    K.text(img, (x, y + 1), str(n), K.F(K.ANTON, 24), (14, 10, 6), "mm", 0)
    return img


def tag(img, x, y, i, state, anchor="lm"):
    """Hover-only name tag: the type word (+ layer). Terminal chip in the node's state colour."""
    col = {"option": ORANGE, "current": LIME, "walked": LIME, "reach": WHITE, "target": (255, 90, 90),
           "grey": (170, 166, 184)}[state]
    word = G.WORD[G.KIND[i]]
    s = word if G.KIND[i] in ("start", "target") else "%s  L%d" % (word, G.LAYER[i])
    img, box = KT.chip(img, (x, y), s, col, 14, anchor=anchor, pad=7)
    return img


def target_pencil(x, y, r=62):
    pr = KT.pencil(KT.PEN_R, 381)
    pr.circle(x, y, r + 8, r - 2, width=9)
    pr.text("TARGET", x + r + 52, y - r + 8, 32, angle=-6)
    return pr


def finish_pencil(img, pr):
    img = KT.spill(img, pr.mask.resize((W, H)), KT.PEN_R, 0.14, 30)
    return KT.ink(img, pr)


# ---------------------------------------------------------------- page chrome
def chrome_top(img, dispatch="Jacked in. The route was computed before you asked."):
    img = KT.place_sticker(img, KT.sticker("NETRUN", 46, "yellow", seed=63), 122, 50, angle=-3)
    items = [dict(kind="heat", value=52, w=300), dict(kind="hp", label="HP", value="52", max="/60"),
             dict(kind="cycles", label="CYCLES", value="18")]
    img, box = KT.topbar(img, 250, 14, items, h=66)
    # DISPATCH line (the build's comms line): one terminal band, red DISPATCH speaker word
    b = (250, 92, 1620, 122)
    img = KT.term(img, b, None, accent=(232, 20, 30), header=False, seed=41, chamfer=8)
    K.text(img, (b[0] + 14, (b[1] + b[3]) / 2), "DISPATCH:", K.F(K.MONO, 15), (255, 70, 70), "lm", 1.2)
    K.text(img, (b[0] + 120, (b[1] + b[3]) / 2), dispatch, K.F(K.MONO, 15), (226, 230, 240), "lm", 0.4)
    return img


def dossier(img, hp="52 / 60"):
    R.TYPEF, R.TYPEB = K.COUR, K.COUR_B
    op = dict(R.OPERATIVE)
    op["hp"] = hp
    dz = R.dossier(op=op, heat_stamp=None)
    dz = dz.resize((int(dz.width * 0.6), int(dz.height * 0.6)), Image.LANCZOS)
    return RL.drop_shadow(img, dz, 14, 138, blur=14, off=(6, 12), op=0.55)


def route_panel(img, n_opts, picked=None):
    box = (1636, 138, 1904, 404)
    img = KT.term(img, box, "ROUTE", seed=23)
    f = K.F(K.MONO, 15)
    K.text(img, (1652, 186), "PICK A NODE: click a", f, (205, 218, 230), "lm", 0.3)
    K.text(img, (1652, 206), "numbered sticker, then", f, (205, 218, 230), "lm", 0.3)
    K.text(img, (1652, 226), "CONFIRM. Keys 1-%d go now." % n_opts, f, (205, 218, 230), "lm", 0.3)
    if picked:
        img = K.term_button(img, (1652, 248, 1888, 294), "CONFIRM: %s" % picked, None, state="focus", accent=ORANGE)
        K.text(img, (1880, 286), "[Enter]", K.F(K.MONO, 12), ORANGE, "rm", 0.6)
    else:
        img = K.term_button(img, (1652, 248, 1888, 294), "CONFIRM", None, state="disabled")
        K.text(img, (1880, 286), "pick first", K.F(K.MONO, 12), (130, 138, 156), "rm", 0.6)
    img = K.term_button(img, (1652, 302, 1888, 348), "GRID VIEW", None)
    K.text(img, (1880, 340), "[G]", K.F(K.MONO, 12), K.CYAN, "rm", 0.6)
    img = K.term_button(img, (1652, 354, 1888, 394), "Save & quit", None)
    return img


def node_file(img, i, hp_arrive="52 / 60 on arrival", box=(1600, 420, 1904, 712)):
    kind = G.KIND[i]
    tier, typ, rew = G.FILE[kind]
    title = "%s  //  L%d" % (G.WORD[kind], G.LAYER[i])
    rows = [("TIER", tier), ("TYPE", typ), ("REWARDS", rew[0])]
    rows += [("", r) for r in rew[1:]]
    rows += [("sep", ""), ("HP", hp_arrive, (140, 255, 170))]
    # the file wraps long TYPE lines at this width: shorten with the panel font
    return KT.holo_file(img, box, title, rows, seed=12, key_w=86, scale=0.86)


def legend(img, hot, extra=None):
    def ring(col, dash=False):
        def f(px):
            im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
            ImageDraw.Draw(im).ellipse([3, 3, px - 4, px - 4], outline=col + (255,), width=3)
            return im
        return f
    items = [(lambda px, k=k: U32.icon(k, px), lab) for k, lab in (("router", "FIGHT"), ("elite", "ELITE"),
                                                                   ("terminal", "EVENT"), ("modem", "SHOP"), ("rack", "RACK"))]
    items += [(ring(LIME), "walked"), (ring(ORANGE), "next"), (ring(WHITE), "ahead"), (ring(GREY), "past")]
    if extra:
        items += extra
    hint = "SHOWING ALL" if hot else "HOVER: SHOW ALL"
    f = K.F(K.MONO, 15)
    w = sum(int(30 + f.getlength(lab) + 18) for _, lab in items) + f.getlength("|  " + hint) + 40
    x = int((1620 + 290) / 2 - w / 2)
    return KT.key_strip(img, x, 1026, items, hint=hint, hot=hot)


def cursor(img, x, y):
    return KT.cursor(img, x, y)


def save(img, name):
    img = RL.bloom(img, 0.10, 0.84, 8)
    return KT.save(img, name)


# ---------------------------------------------------------------- GIFs: one shared palette that keeps the run colours
KEY_SWATCH = [LIME, ORANGE, WHITE, GREY, (255, 28, 44), (92, 225, 255), (255, 61, 168), (61, 255, 139), (90, 150, 255),
              (255, 196, 60), (255, 96, 40), (8, 6, 14), (255, 255, 255), (255, 210, 77)]


def save_gif(frames, durs, path, colors=255):
    """Quantize every frame to ONE palette built from the frames plus big swatches of the state / type colours
    (a per-frame median cut drops small lime areas and maps them to orange)."""
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
