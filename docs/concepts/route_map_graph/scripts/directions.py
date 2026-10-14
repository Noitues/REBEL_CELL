"""Route map graph: the three directions, four views each (1920x1080).

python directions.py [A|B|C ...] [start|mid|legend_hover|node_hover ...]
  A  Cable graph on the city   - the run graph laid on the 3D city: nodes on lot pads, 45/90 cable runs.
  B  Lifted schematic          - the city dims, the graph lifts into a layered terminal plate (bottom -> top);
                                 the current node is tied to its real lot by a leader line.
  C  Branch lanes              - a left -> right metro plate; each numbered option owns a coloured line, and every
                                 node / link it can still reach carries that line (shared links run in parallel).
Views: start (current = start, 3 options), mid (walked fight > event > shop, 2 options), legend_hover (whole graph at
full opacity, every tag), node_hover (option 1 hovered + picked: its tag, its file, CONFIRM live).
Needs ../scratch/plate_city.png (plate.py). All randomness is seeded.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import frame as FR  # noqa: E402
import rgraph as G  # noqa: E402
import kit44 as KT  # noqa: E402
import ui31 as K  # noqa: E402
import r32ui as U32  # noqa: E402

W, H = FR.W, FR.H
LANE = [(92, 225, 255), (255, 61, 168), (255, 210, 77)]     # C: option 1 / 2 / 3 lines (NET_CYAN, CELL_PINK, RESIST_GOLD)
LIFT = 26                                                     # A: sticker floats this far above its lot pad


# ================================================================ layouts
def layout_A():
    """Layer -> screen y (bottom -> top), k -> x inside the layer, a lean along the street diagonal, seeded jitter.
    In the build: pick, per node, the free lot nearest this target point (layout rule in NOTES)."""
    rng = random.Random(4417)
    y0, y7 = 966, 226
    S = 300
    pos = {}
    for i in G.NODES:
        l, k = G.LAYER[i], G.K[i]
        n = G.WIDTH[l]
        x = 905 + (k - (n - 1) / 2) * S + l * 26
        y = y0 - (y0 - y7) * l / 7
        if 0 < l < 7:
            x += rng.uniform(-34, 34)
            y += rng.uniform(-12, 12)
        pos[i] = (round(x), round(y))
    return pos


PLATE_B = (590, 138, 1452, 1004)


def layout_B():
    x0, y0, x1, y1 = PLATE_B
    cx = (x0 + x1) / 2
    S = 250
    pos = {}
    for i in G.NODES:
        l, k = G.LAYER[i], G.K[i]
        n = G.WIDTH[l]
        pos[i] = (round(cx + (k - (n - 1) / 2) * S), round(y1 - 58 - (y1 - y0 - 150) * l / 7))
    return pos


PLATE_C = (296, 300, 1612, 868)


def layout_C():
    x0, y0, x1, y1 = PLATE_C
    cy = (y0 + y1) / 2 + 10
    S = 158
    pos = {}
    for i in G.NODES:
        l, k = G.LAYER[i], G.K[i]
        n = G.WIDTH[l]
        pos[i] = (round(x0 + 92 + (x1 - x0 - 210) * l / 7), round(cy + (k - (n - 1) / 2) * S))
    return pos


# ================================================================ routing (screen space)
def route_up(a, b, diag=True, r=16):
    """Bottom -> top, 45/90 only. A small jog (|dx| < gap - 2r) is one 45 degree diagonal in the middle of the gap;
    a wide one runs up, turns (45 degree chamfer r) along the MIDDLE of the gap between layers, turns, and runs up,
    so a horizontal never passes at a node's own level. diag=False (B) uses the chamfered turn for every jog."""
    (xa, ya), (xb, yb) = a, b
    dx, gap = xb - xa, ya - yb
    if abs(dx) < 2:
        return [a, b]
    sg = 1 if dx > 0 else -1
    if diag and abs(dx) <= gap - 2 * r:
        s1 = (gap - abs(dx)) * 0.5
        return [a, (xa, ya - s1), (xb, ya - s1 - abs(dx)), b]
    ym = ya - gap * 0.5 + (9 if sg > 0 else -9)     # rightward runs low, leftward runs high: no false bus joins
    r = min(r, abs(dx) / 2)
    return [a, (xa, ym + r), (xa + sg * r, ym), (xb - sg * r, ym), (xb, ym - r), b]


def route_right(a, b, r=18):
    """Left -> right metro: horizontal, one 45 degree diagonal, horizontal."""
    (xa, ya), (xb, yb) = a, b
    dy, gap = yb - ya, xb - xa
    if abs(dy) < 2:
        return [a, b]
    s1 = (gap - abs(dy)) * 0.5
    return [a, (xa + s1, ya), (xb - s1, yb), b]


# ================================================================ shared drawing
def edge_style(cab, pts, s, alpha=1.0, wide=1.0):
    a = int(255 * alpha)
    if s == "walked":
        cab.solid(pts, FR.LIME, 7 * wide, casing=4, a=a)
    elif s == "option":
        cab.dashed(pts, FR.ORANGE, 8 * wide, on=18, off=9, casing=4, a=a)
    elif s == "future":
        cab.dashed(pts, FR.WHITE, 5 * wide, on=12, off=9, casing=4, a=int(a * 0.92))
    else:
        cab.solid(pts, FR.GREY, 4 * wide, casing=3, a=a)


def glow_from(img, lay, col_sel, k=0.5, radius=7):
    m = lay.split()[3]
    return K.add_glow(img, m, col_sel, radius, k)


class View:
    def __init__(self, d, view):
        self.d, self.view = d, view
        self.walked = G.WALK_START if view == "start" else G.WALK_MID
        self.st, self.opts = G.states(self.walked)
        self.es = G.edge_states(self.walked, self.st)
        self.all = view == "legend_hover"
        self.hover = self.opts[0] if view == "node_hover" else None
        self.pos = {"A": layout_A, "B": layout_B, "C": layout_C}[d]()
        # node_hover: the hovered option's own future stays full; the rest of the live future drops to MIX_A
        self.focus = G.reach([self.hover]) if self.hover else None

    def node_alpha(self, i):
        s = self.st[i]
        if s == "grey":
            return 1.0 if self.all else FR.GREY_A
        if self.focus is not None and s in ("reach",) and i not in self.focus:
            return FR.MIX_A
        return 1.0

    def edge_alpha(self, e):
        s = self.es[e]
        if s == "grey":
            return 1.0 if self.all else FR.GREY_A
        if self.focus is not None and s == "future" and not (e[0] in self.focus and e[1] in self.focus):
            return FR.MIX_A
        if self.focus is not None and s == "option" and e[1] != self.hover:
            return 0.8
        return 1.0

    def anchor(self, i):
        """Sticker centre."""
        x, y = self.pos[i]
        return (x, y - LIFT) if self.d == "A" else (x, y)

    def route(self, a, b):
        pa, pb = self.pos[a], self.pos[b]
        if self.d == "A":
            return route_up(pa, pb, diag=True, r=22)
        if self.d == "B":
            return route_up(pa, pb, diag=False)
        return route_right(pa, pb)


def draw_edges(img, v, lanes=None):
    """Grey group first (one layer, one alpha), then live cables, lime/orange glow."""
    grey = FR.Cables()
    live = FR.Cables()
    for e in G.EDGES:
        s = v.es[e]
        pts = v.route(*e)
        if s == "grey":
            edge_style(grey, pts, s, 1.0)
        elif lanes is None or s == "walked":
            edge_style(live, pts, s, v.edge_alpha(e))
    gl = grey.get()
    if not v.all:
        gl.putalpha(gl.split()[3].point(lambda q: int(q * FR.GREY_A)))
    img.alpha_composite(gl)
    if lanes is not None:
        img = draw_lanes(img, v, lanes)
    ll = live.get()
    for col in (FR.LIME, FR.ORANGE):
        m = Image.new("L", (W, H), 0)
        sel = [e for e in G.EDGES if v.es[e] == ("walked" if col == FR.LIME else "option") and (lanes is None or col == FR.LIME)]
        dd = ImageDraw.Draw(m)
        for e in sel:
            dd.line(v.route(*e), fill=int(255 * v.edge_alpha(e)), width=8, joint="curve")
        img = K.add_glow(img, m, col, 8, 0.55)
    img.alpha_composite(ll)
    return img


def draw_lanes(img, v, lanes):
    """C: each option's reachable links carry its line; shared links run as parallel lines (metro bundle)."""
    cab = FR.Cables()
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gw = 6
    for e in G.EDGES:
        s = v.es[e]
        if s not in ("option", "future"):
            continue
        on = [j for j, (ns, es) in enumerate(lanes) if e in es or (s == "option" and e[1] == v.opts[j])]
        if not on:
            continue
        pts = v.route(*e)
        a = v.edge_alpha(e)
        n = len(on)
        cab.solid(pts, FR.CASING, gw * n + 2 * (n - 1) + 8, casing=0, a=int(235 * a))
        for q, j in enumerate(on):
            off = (q - (n - 1) / 2) * (gw + 2)
            p = FR.offset_poly(pts, off)
            if s == "option":
                cab.solid(p, LANE[j], gw, casing=0, a=int(255 * a))
            else:
                cab.dashed(p, LANE[j], gw, on=22, off=6, casing=0, a=int(255 * a))
    lay = cab.get()
    img = K.add_glow(img, lay.split()[3], (200, 200, 230), 6, 0.25)
    img.alpha_composite(lay)
    return img


def draw_nodes(img, v, lanes=None):
    order = sorted(G.NODES, key=lambda i: (v.anchor(i)[1], i))
    # grey nodes on their own layer at GREY_A (never glow)
    for i in order:
        if v.st[i] != "grey":
            continue
        x, y = v.anchor(i)
        if v.d == "A":
            img = pad_stem(img, v.pos[i], (x, y), FR.GREY, v.node_alpha(i))
        img = FR.draw_node(img, i, x, y, "grey", alpha=v.node_alpha(i), glow=False)
    for i in order:
        s = v.st[i]
        if s == "grey":
            continue
        x, y = v.anchor(i)
        col = {"walked": FR.LIME, "current": FR.LIME, "option": FR.ORANGE}.get(s, FR.WHITE)
        if v.d == "A":
            img = pad_stem(img, v.pos[i], (x, y), col, v.node_alpha(i))
        if lanes is not None and s in ("reach", "target", "option"):
            img = lane_ring(img, v, i, x, y, lanes)
        img = FR.draw_node(img, i, x, y, s, hover=(i == v.hover), alpha=v.node_alpha(i))
    return img


def lane_ring(img, v, i, x, y, lanes):
    """C: a node any option can reach wears an outer ring split into those options' line colours."""
    on = [j for j, (ns, es) in enumerate(lanes) if i in ns]
    if not on:
        return img
    kind = G.KIND[i]
    px = FR.STICKER_PX["target" if kind == "target" else v.st[i]]
    r = px / 2 + (16 if kind != "target" else 12)
    a = v.node_alpha(i)
    S = 2
    lay = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    box = [(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S]
    d.ellipse([b + (-5 * S if q < 2 else 5 * S) for q, b in enumerate(box)], outline=FR.CASING + (int(220 * a),), width=12 * S)
    n = len(on)
    for q, j in enumerate(on):
        a0 = -90 + 360 * q / n + (4 if n > 1 else 0)
        a1 = -90 + 360 * (q + 1) / n - (4 if n > 1 else 0)
        d.arc(box, a0, a1 if n > 1 else a0 + 360, fill=LANE[j] + (int(255 * a),), width=6 * S)
    img.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    return img


def pad_stem(img, ground, stk, col, alpha):
    """A: the node stands on its lot. Iso pad on the ground + a thin stem up to the sticker."""
    gx, gy = ground
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rx, ry = 30, 15
    q = [(gx, gy - ry), (gx + rx, gy), (gx, gy + ry), (gx - rx, gy)]
    d.polygon(q, fill=(6, 5, 12, 200), outline=tuple(col) + (230,))
    q2 = [(gx, gy - ry * 0.55), (gx + rx * 0.55, gy), (gx, gy + ry * 0.55), (gx - rx * 0.55, gy)]
    d.polygon(q2, outline=tuple(col) + (150,))
    d.line([(gx, gy), (stk[0], stk[1] + 18)], fill=tuple(col) + (200,), width=2)
    if alpha < 1:
        lay.putalpha(lay.split()[3].point(lambda t: int(t * alpha)))
    img.alpha_composite(lay)
    return img


def draw_marks(img, v, lanes=None):
    """Numbers on the options, the operative token on the current node."""
    for n, o in enumerate(v.opts):
        x, y = v.anchor(o)
        px = FR.STICKER_PX["option"]
        cx, cy = x - px / 2 - 8, y - px / 2 - 6
        if lanes is not None:
            img = FR.number_chip(img, cx, cy, n + 1, fill=LANE[n])
        else:
            img = FR.number_chip(img, cx, cy, n + 1)
    x, y = v.anchor(v.walked[-1])
    img = FR.token(img, x, y, (34, -40) if v.d == "C" else (40, 28))
    return img


def draw_tags(img, v):
    if v.all:
        for i in G.NODES:
            x, y = v.anchor(i)
            px = FR.STICKER_PX["target" if G.KIND[i] == "target" else v.st[i]]
            if G.KIND[i] == "target":
                continue                              # the pencil TARGET is its tag
            img = FR.tag(img, x + px / 2 + 12, y + 2, i, v.st[i])
    elif v.hover:
        x, y = v.anchor(v.hover)
        img = FR.tag(img, x + FR.STICKER_PX["option"] / 2 + 14, y + 4, v.hover, "option")
    return img


def target_pen(v):
    t = "L7_0"
    x, y = v.anchor(t)
    return FR.target_pencil(x, y, 54)


# ================================================================ direction specific worlds
def world_A(v):
    img = FR.grade(FR.plate(), 0.82, 0.92)
    # a soft dark bed under the run so 5 px cables read on a busy city (the graph hull, blurred)
    xs = [p[0] for p in v.pos.values()]
    ys = [p[1] for p in v.pos.values()]
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle([min(xs) - 70, min(ys) - 120, max(xs) + 70, max(ys) + 40], 80, fill=255)
    img = FR.dim_mask(img, m.filter(ImageFilter.GaussianBlur(60)), 0.62)
    return img


def lot_pad(img, sx, sy):
    """The current node's real lot on the city: the locked circuit-inlay socket (r32ui.pad), lime, with a ping ring."""
    q = [(sx, sy - 18), (sx + 36, sy), (sx, sy + 18), (sx - 36, sy)]
    img = U32.pad(img, q, FR.LIME, glow=0.9, lit=1.0, k=1.0)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([sx - 60, sy - 30, sx + 60, sy + 30], outline=150, width=2)
    return K.over(img, FR.LIME, m)


def leader(img, pts):
    cab = FR.Cables()
    cab.dashed(pts, FR.LIME, 3, on=8, off=6, casing=2)
    lay = cab.get()
    img = K.add_glow(img, lay.split()[3], FR.LIME, 6, 0.5)
    img.alpha_composite(lay)
    return img


def ruler_tab(img, x, y, s, horizontal):
    """The current layer's ruler label turns lime and carries the leader out of the plate."""
    img, box = KT.chip(img, (x, y), s, FR.LIME, 15, anchor="mm", bright=True, pad=6)
    return img


def world_B(v):
    img = FR.grade(FR.plate(), 0.42, 0.55, blur=1.2)
    x0, y0, x1, y1 = PLATE_B
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rectangle([x0 - 30, y0 - 20, x1 + 30, y1 + 20], fill=70)
    img = K.add_glow(img, m, (40, 120, 160), 60, 0.25)
    # the leader first (it runs on the city, out of the plate's left edge at the current layer)
    cur = v.walked[-1]
    nx, ny = v.anchor(cur)
    up = -1 if ny > 800 else 1
    sx, sy = x0 - 170, ny + up * 80
    img = leader(img, [(x0 + 4, ny), (x0 - 90, ny), (sx, sy)])
    img = lot_pad(img, sx, sy)
    img = KT.panel_shadow(img, PLATE_B, 18, blur=24, k=0.6, off=(0, 14))
    img = K.term_panel(img, PLATE_B, "RUN MAP  //  PRIORITY LANE EXCHANGE", accent=K.CYAN, alpha=206, seed=29, chamfer=18,
                       hexbg=False, scan=0.08)
    d = K.BD(img)
    for gx in range(x0 + 20, x1 - 10, 30):
        d.line([(gx, y0 + 34), (gx, y1 - 10)], fill=K.CYAN + (13,), width=1)
    for gy in range(y0 + 44, y1 - 6, 30):
        d.line([(x0 + 6, gy), (x1 - 6, gy)], fill=K.CYAN + (13,), width=1)
    pos = layout_B()
    for l in range(8):
        yy = pos["L%d_0" % l][1]
        d.line([(x0 + 48, yy), (x0 + 70, yy)], fill=K.CYAN + (120,), width=2)
        d.line([(x1 - 70, yy), (x1 - 48, yy)], fill=K.CYAN + (120,), width=2)
        if l == G.LAYER[cur]:
            img = ruler_tab(img, x0 + 26, yy, "L%d" % l, False)
            d = K.BD(img)
            d.line([(x0 + 48, yy), (x0 + 70, yy)], fill=FR.LIME + (230,), width=3)
        else:
            K.text(img, (x0 + 16, yy), "L%d" % l, K.F(K.MONO, 15), K.CYAN, "lm", 0.8)
    return img


def world_C(v):
    img = FR.grade(FR.plate(), 0.55, 0.7, blur=0.8)
    x0, y0, x1, y1 = PLATE_C
    cur = v.walked[-1]
    nx, ny = v.anchor(cur)
    sx, sy = nx - 84, y1 + 96
    img = leader(img, [(nx, y1 - 4), (nx, y1 + 12), (sx, sy)])
    img = lot_pad(img, sx, sy)
    img = KT.panel_shadow(img, PLATE_C, 16, blur=22, k=0.6, off=(0, 12))
    img = K.term_panel(img, PLATE_C, "RUN MAP  //  PRIORITY LANE EXCHANGE", accent=K.CYAN, alpha=214, seed=31, chamfer=16,
                       hexbg=False, scan=0.08)
    d = K.BD(img)
    pos = layout_C()
    for l in range(8):
        xx = pos["L%d_0" % l][0]
        d.line([(xx, y0 + 40), (xx, y0 + 56)], fill=K.CYAN + (120,), width=2)
        if l == G.LAYER[cur]:
            img = ruler_tab(img, xx, y1 - 20, "L%d" % l, True)
            d = K.BD(img)
        else:
            K.text(img, (xx, y1 - 18), "L%d" % l, K.F(K.MONO, 15), K.CYAN, "mm", 0.8)
    return img


# ================================================================ page
def build(d, view):
    v = View(d, view)
    lanes = G.lanes(v.opts) if d == "C" else None
    img = {"A": world_A, "B": world_B, "C": world_C}[d](v)
    img = draw_edges(img, v, lanes)
    img = draw_nodes(img, v, lanes)
    img = draw_marks(img, v, lanes)
    pen = target_pen(v)
    img = draw_tags(img, v)
    mid = view != "start"
    img = FR.dossier(img)
    disp = ("Jacking you in. Three ways up; all of them end at the Rack." if view == "start"
            else "Shop's behind you. Two ways left: the long way has a Rack.")
    img = FR.chrome_top(img, disp)
    picked = "Fight" if view == "node_hover" else None
    img = FR.route_panel(img, len(v.opts), picked)
    if v.hover:
        img = FR.node_file(img, v.hover, "52 / 60 on arrival")
    img, kbox = FR.legend(img, v.all, extra=None)
    img = FR.finish_pencil(img, pen)
    if v.all:
        img = FR.cursor(img, kbox[2] - 120, kbox[1] + 14)
    elif v.hover:
        x, y = v.anchor(v.hover)
        img = FR.cursor(img, x + 6, y + 4)
    return img


if __name__ == "__main__":
    args = sys.argv[1:]
    ds = [a for a in args if a in ("A", "B", "C")] or ["A", "B", "C"]
    vs = [a for a in args if a in ("start", "mid", "legend_hover", "node_hover")] or ["start", "mid", "legend_hover", "node_hover"]
    for d in ds:
        for vw in vs:
            FR.save(build(d, vw), "%s_%s.png" % (d, vw))
