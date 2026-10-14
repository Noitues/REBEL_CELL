"""Route map graph, direction A iterated: the route BLOOMS UP THE BUILDINGS (designer lead idea).

python avariants.py [A1 A2 A3 A4] [rest hover gif]
All at mid-run (walked fight > event > shop; options 1 = fight, 2 = Rack). Hover = option 2 (the Rack branch).
  A1 Bloom climb     a light pulse runs the hovered cable; every downstream node building lights floor by floor in its
                     node-type colour, a rooftop beacon beam carries the node sticker; buildings the path passes
                     light partly; other branches stay calm.
  A2 Rooftop beacons nodes are sticker beacons on masts on their own roofs; cables drop down the facades, run the
                     ground and climb the next facade; hover draws the branch's facade edges and rooflines in neon.
  A3 Street current  the links are glowing ground currents (data in the cable runs); hover floods the branch with
                     light trails and its buildings flicker on.
  A4 Power cut       hover cuts the city's power: every window goes dark except the branch, whose buildings stay lit
                     in their node colours and whose cables become live power lines. The future is the only light.
Nodes are snapped to real buildings of the round 38 transit camera (gbuf.py G-buffer). All randomness is seeded.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import frame as FR  # noqa: E402
import rgraph as G  # noqa: E402
import directions as D  # noqa: E402
import gbuf as GB  # noqa: E402
import kit44 as KT  # noqa: E402
import ui31 as K  # noqa: E402
import r32ui as U32  # noqa: E402

W, H = FR.W, FR.H
D.LIFT = 0                                        # A-variants: v.pos IS the sticker point (masts drop to the roofs)
HOVER = "L4_1"
TYPE_COL = {"router": (92, 225, 255), "elite": (255, 96, 40), "terminal": (61, 255, 139), "modem": (90, 150, 255),
            "rack": (255, 196, 60), "target": (255, 44, 60), "start": FR.LIME}
_GB = {}


def gbuf():
    if "g" not in _GB:
        _GB["g"] = GB.GBuf()
    return _GB["g"]


# ================================================================ nodes on real buildings
def snap():
    """The graph floats over the city in clean layer rows (layout_A sticker points). Each node takes one real
    building below its sticker: roof centre within 48 px sideways and 34-150 px below the sticker, preferring a tall
    facade (it carries the bloom), one building per node. The sticker moves sideways onto that roof's x; a mast drops
    from the sticker to the roof. Returns {node: (bid, roof_x, roof_y, sticker_x, sticker_y)}."""
    if "snap" in _GB:
        return _GB["snap"]
    gb = gbuf()
    base = D.layout_A()
    taken = set()
    out = {}
    rp = gb.roof
    ids, inv = np.unique(gb.idc[rp], return_inverse=True)
    ys, xs = np.nonzero(rp)
    cnt = np.bincount(inv)
    mx, my = np.bincount(inv, xs) / cnt, np.bincount(inv, ys) / cnt
    roofs = {int(b): (float(mx[j]), float(my[j]), int(cnt[j])) for j, b in enumerate(ids) if cnt[j] >= 30 and b > 0}
    for i in G.NODES:
        x, y = base[i]
        y -= 26
        best = None
        for b, (rx, ry, n) in sorted(roofs.items()):
            if b in taken or abs(rx - x) > 48 or not (34 <= ry - y <= 150):
                continue
            top = gb.top(b)
            if not (2.5 <= top <= 30):
                continue
            sc = abs(rx - x) * 1.5 + abs(ry - y - 80) * 0.4 - 2.0 * min(top, 16)
            if best is None or sc < best[0]:
                best = (sc, b, rx, ry)
        if best is None:
            out[i] = (None, x, y + 60, x, y)
        else:
            taken.add(best[1])
            gb.set_clip(best[1], (best[2] - 120, best[3] - 90, best[2] + 120, best[3] + 460))
            out[i] = (best[1], round(best[2]), round(best[3]), round(best[2]), y)
    _GB["snap"] = out
    return out


def view(hover):
    v = D.View("A", "mid")
    sn = snap()
    v.snap = sn
    v.pos = {i: (sn[i][3], sn[i][4]) for i in G.NODES}         # cables join the floating stickers
    v.roof = {i: (sn[i][1], sn[i][2]) for i in G.NODES}
    if hover:
        v.hover = HOVER
        v.focus = G.reach([HOVER])
    return v


# ================================================================ timing (the bloom, 1.2 s)
def climb_t(t, depth, dur=0.32, lead=0.16, step=0.17):
    """Climb 0..1 of a building `depth` layers past the hovered option at normalised time t (0..1 over 1.2 s)."""
    return float(np.clip((t - lead - step * depth) / dur, 0, 1))


def branch(v):
    """The hovered branch: nodes (with depth) and edges (current -> option, then everything inside its reach)."""
    fut = G.reach([HOVER])
    nodes = {i: G.LAYER[i] - G.LAYER[HOVER] for i in fut}
    edges = [(v.walked[-1], HOVER)] + [e for e in G.EDGES if e[0] in fut and e[1] in fut]
    return nodes, edges


def path_buildings(v, edges, node_bids, per_edge=3):
    gb = gbuf()
    out = []
    seen = set(node_bids)
    for e in edges:
        pts = v.route(*e)
        ids = gb.buildings_near_path(pts, rad=20, min_px=260, exclude=seen)
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        for b in ids:
            gb.set_clip(b, (min(xs) - 60, min(ys) - 60, max(xs) + 60, max(ys) + 260))
        ids = [b for b in ids if gb.top(b) > 2.0][:per_edge]
        for b in ids:
            seen.add(b)
            out.append((b, e))
    return out


# ================================================================ emission per variant
def emission(var, v, t):
    gb = gbuf()
    em = np.zeros((H, W, 3), np.float32)
    if t is None:
        return em
    nodes, edges = branch(v)
    nb = {i: v.snap[i][0] for i in nodes if v.snap[i][0] is not None}
    pb = path_buildings(v, edges, nb.values())
    if var == "A1":
        for i, b in sorted(nb.items()):
            em += gb.bloom(b, climb_t(t, nodes[i]), TYPE_COL[G.KIND[i]], k=1.5, seed=3, wash=0.45)
        for b, e in pb:
            d = max(0, G.LAYER[e[0]] - G.LAYER[HOVER]) + 0.5
            em += gb.bloom(b, 0.45 * climb_t(t, d), (255, 190, 130), k=0.28, seed=5, trace=False)
    elif var == "A2":
        for i, b in sorted(nb.items()):
            c = climb_t(t, nodes[i])
            em += trace_only(gb, b, c, TYPE_COL[G.KIND[i]], 1.1)
        for b, e in pb:
            d = max(0, G.LAYER[e[0]] - G.LAYER[HOVER]) + 0.5
            em += trace_only(gb, b, climb_t(t, d), FR.ORANGE, 0.75)
    elif var == "A3":
        rng = random.Random(77)
        for i, b in sorted(nb.items()):
            c = climb_t(t, nodes[i], dur=0.12)
            fl = 1.0 if c >= 1 else (0.35 + 0.65 * rng.random()) * c
            em += gb.bloom(b, 1.0 if c > 0 else 0, (255, 236, 200), k=0.75 * fl, seed=11, trace=False)
            em += gb.bloom(b, c, TYPE_COL[G.KIND[i]], k=0.5 * c, seed=11, trace=True) * 0.6
        for b, e in pb:
            d = max(0, G.LAYER[e[0]] - G.LAYER[HOVER]) + 0.3
            c = climb_t(t, d, dur=0.1)
            if c > 0:
                fl = 1.0 if c >= 1 else 0.3 + 0.7 * rng.random()
                em += gb.bloom(b, 1.0, (255, 226, 190), k=0.42 * fl, seed=13, trace=False)
    elif var == "A4":
        for i, b in sorted(nb.items()):
            c = max(0.25, climb_t(t, nodes[i], lead=0.05, step=0.12, dur=0.25))
            em += gb.bloom(b, c, TYPE_COL[G.KIND[i]], k=1.0, seed=3)
        for b, e in pb:
            em += gb.bloom(b, 1.0, (255, 220, 175), k=0.5 * min(1, t * 3), seed=5, trace=False)
    return em


def trace_only(gb, b, c, col, k):
    """A2: neon up the facade edges to the climb front, then the roofline (no windows)."""
    em = np.zeros((H, W, 3), np.float32)
    if b is None or c <= 0:
        return em
    m = gb.mask(b) & gb.bld
    top = gb.top(b)
    zc = c * (top + 0.4)
    cc = np.array(col, np.float32) / 255.0
    e = gb.edge & m & (gb.z < zc)
    em += e[..., None] * cc * 1.2 * k
    wash = m & gb.wall & (gb.z < zc) & (gb.z > zc - 2.5)
    em += (wash * np.clip(1 - (zc - gb.z) / 2.5, 0, 1) * 0.35)[..., None] * cc * k
    if c >= 0.98:
        rim = gb.edge & m & (gb.z > top - 0.4)
        em += rim[..., None] * cc * 1.6 * k
        em += (m & gb.roof)[..., None] * cc * 0.25 * k
    return em


# ================================================================ world grade per variant
def world(var, v, t):
    img = FR.grade(FR.plate(), 0.8, 0.92)
    if var == "A4" and t is not None:
        k = 0.82 - 0.5 * min(1.0, t * 2.5)          # the power cut: the city drops to ~32 %
        img = FR.grade(FR.plate(), k, 0.6)
    return img


# ================================================================ cables
def cable_path_pts(v, e):
    return v.route(*e)                 # (a facade-drop route was tried for A2 and tangled the graph: see NOTES)


def facade_route(v, e):
    """A2: down the source building's facade, the 45/90 ground run, up the target's facade."""
    gb = gbuf()
    a, b = e
    (xa, ya), (xb, yb) = v.roof[a], v.roof[b]
    ba, bb = v.snap[a][0], v.snap[b][0]

    def foot(i, x, y, bid):
        if bid is None:
            return (x, y)
        m = gb.mask(bid) & gb.bld
        ys, xs = np.nonzero(m)
        return (x, float(ys.max()) - 4)
    fa = foot(a, xa, ya, ba)
    fb = foot(b, xb, yb, bb)
    mid = D.route_up(fa, fb, diag=True, r=22) if fa[1] > fb[1] else [fa, fb]
    return [(xa, ya)] + mid + [(xb, yb)]


def draw_cables(img, v, var, t):
    nodes, bedges = branch(v) if t is not None else ({}, [])
    grey = FR.Cables()
    live = FR.Cables()
    for e in G.EDGES:
        s = v.es[e]
        pts = cable_path_pts(v, e)
        if s == "grey":
            D.edge_style(grey, pts, s, 1.0)
            continue
        a = v.edge_alpha(e)
        if var == "A3":
            continue                                     # A3 draws its links as ground current (below)
        if var == "A4" and t is not None and e not in bedges and s != "walked":
            a *= 0.45                                    # power cut: the dead branch's cables go slack
        D.edge_style(live, pts, s, a)
    gl = grey.get()
    gl.putalpha(gl.split()[3].point(lambda q: int(q * FR.GREY_A)))
    img.alpha_composite(gl)
    if var == "A3":
        img = street_current(img, v, t, bedges)
    ll = live.get()
    img = K.add_glow(img, ll.split()[3], (255, 170, 90), 6, 0.18)
    img.alpha_composite(ll)
    if t is not None and var in ("A1", "A4"):
        img = pulse(img, v, t, bedges, var)
    return img


def poly_len(p):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(p, p[1:]))


def point_at(p, s):
    for a, b in zip(p, p[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if s <= L:
            k = s / (L or 1)
            return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
        s -= L
    return p[-1]


def sub_poly(p, s0, s1):
    out = [point_at(p, s0)]
    acc = 0.0
    for a, b in zip(p, p[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if s0 < acc + L and acc + L < s1:
            out.append(b)
        acc += L
    out.append(point_at(p, s1))
    return out


def pulse(img, v, t, bedges, var):
    """A light pulse runs each branch cable in turn (by layer), leaving it lit behind it."""
    lay = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    heads = []
    for e in bedges:
        dpt = G.LAYER[e[0]] - G.LAYER[HOVER]            # -1 for current -> option
        u = float(np.clip((t - 0.17 * (dpt + 1)) / 0.2, 0, 1))
        if u <= 0:
            continue
        p = cable_path_pts(v, e)
        L = poly_len(p)
        seg = sub_poly(p, 0, L * u)
        d.line([(x * 2, y * 2) for x, y in seg], fill=FR.ORANGE + (150,), width=16, joint="curve")
        if u < 1:
            heads.append(point_at(p, L * u))
    lay = lay.resize((W, H), Image.LANCZOS)
    img = K.add_glow(img, lay.split()[3], (255, 200, 140), 10, 0.6)
    img.alpha_composite(lay)
    m = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(m)
    for x, y in heads:
        dm.ellipse([x - 9, y - 9, x + 9, y + 9], fill=255)
    img = K.add_glow(img, m, (255, 240, 210), 16, 1.6)
    img = K.over(img, (255, 255, 255), m)
    return img


def street_current(img, v, t, bedges):
    """A3: every live link is a soft ground current with packets; hovered branch floods with light trails."""
    rng = random.Random(9)
    em = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(em)
    soft = Image.new("L", (W, H), 0)
    ds = ImageDraw.Draw(soft)
    for e in G.EDGES:
        s = v.es[e]
        if s == "grey":
            continue
        p = v.route(*e)
        col = {"walked": FR.LIME, "option": FR.ORANGE, "future": FR.WHITE}[s]
        a = v.edge_alpha(e)
        d.line([(x * 2, y * 2) for x, y in p], fill=FR.CASING + (int(200 * a),), width=22, joint="curve")
        d.line([(x * 2, y * 2) for x, y in p], fill=col + (int(150 * a),), width=10, joint="curve")
        ds.line(p, fill=int(150 * a), width=14, joint="curve")
        L = poly_len(p)
        ph = (rng.random() * 40 + (t or 0) * 160) % 40
        s0 = ph
        while s0 < L:                                    # packets: short bright dashes (data in the cable run)
            q = sub_poly(p, s0, min(L, s0 + 10))
            d.line([(x * 2, y * 2) for x, y in q], fill=(255, 255, 255, int(235 * a)), width=8)
            s0 += 40
    if t is not None:
        for e in bedges:                                 # the flood: light trails along the branch
            p = v.route(*e)
            L = poly_len(p)
            dpt = G.LAYER[e[0]] - G.LAYER[HOVER]
            u = float(np.clip((t - 0.12 * (dpt + 1)) / 0.25, 0, 1))
            if u <= 0:
                continue
            for k in range(5):
                off = (k - 2) * 4.0
                q = FR.offset_poly(sub_poly(p, 0, L * u), off)
                col = [(255, 90, 60), (255, 236, 200), (255, 140, 26), (255, 255, 255), (255, 70, 120)][k]
                d.line([(x * 2, y * 2) for x, y in q], fill=col + (220,), width=4, joint="curve")
            ds.line(sub_poly(p, 0, L * u), fill=255, width=26, joint="curve")
    lay = em.resize((W, H), Image.LANCZOS)
    img = K.add_glow(img, soft, (255, 190, 120), 16, 0.5)
    img.alpha_composite(lay)
    return img


# ================================================================ nodes
def beacons(img, v, var, t):
    """Every node stands on its roof: a mast from the roof up to its floating sticker, in the state colour, with a
    roof socket ring. A1 hover: the mast of each bloomed node becomes a beacon beam in the node-type colour.
    A2: a heavier antenna mast with a dish ring (the beacon IS the node)."""
    nodes = branch(v)[0] if t is not None else {}
    lay = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    gl = Image.new("L", (W, H), 0)
    dg = ImageDraw.Draw(gl)
    for i in G.NODES:
        x, y = v.roof[i]
        top = v.pos[i][1] + 20
        s = v.st[i]
        a = 1.0 if s != "grey" else FR.GREY_A
        col = {"walked": FR.LIME, "current": FR.LIME, "option": FR.ORANGE, "grey": FR.GREY}.get(s, FR.WHITE)
        wm = 3 if var == "A2" else 2
        d.line([(x * 2, y * 2), (x * 2, top * 2)], fill=FR.CASING + (int(220 * a),), width=(wm + 4) * 2)
        d.line([(x * 2, y * 2), (x * 2, top * 2)], fill=col + (int(255 * a),), width=wm * 2)
        rx, ry = (16, 7) if var == "A2" else (11, 5)
        d.ellipse([(x - rx) * 2, (y - ry) * 2, (x + rx) * 2, (y + ry) * 2], outline=col + (int(255 * a),), width=4)
        if var == "A2":
            d.ellipse([(x - 22) * 2, (y - 10) * 2, (x + 22) * 2, (y + 10) * 2], outline=col + (int(120 * a),), width=2)
        if var == "A1" and i in nodes and climb_t(t, nodes[i]) >= 1:
            c2 = TYPE_COL[G.KIND[i]]
            dg.rectangle([x - 6, top, x + 6, y], fill=220)
            d.line([(x * 2, y * 2), (x * 2, top * 2)], fill=c2 + (255,), width=8)
    lay = lay.resize((W, H), Image.LANCZOS)
    img = K.add_glow(img, gl, (255, 230, 200), 9, 0.8)
    img.alpha_composite(lay)
    return img


def draw_all_nodes(img, v, var, t):
    if var == "A2":
        old = D.LIFT
        D.LIFT = 0
        img = D.draw_nodes(img, v)
        D.LIFT = old
        return img
    return D.draw_nodes(img, v)


# ================================================================ page
def build(var, t):
    v = view(t is not None)
    v.d_var = var
    if var == "A2":
        D_LIFT = 44
    img = world(var, v, t)
    em = emission(var, v, t)
    if em.any():
        img = GB.add_emission(img, em)
    img = draw_cables(img, v, var, t)
    img = beacons(img, v, var, t)
    old = D.LIFT
    pd = D.pad_stem
    D.pad_stem = lambda img, ground, stk, col, alpha: img     # nodes stand on roofs now: no ground pad / stem
    img = D.draw_nodes(img, v)
    img = D.draw_marks(img, v)
    pen = D.target_pen(v)
    if t is not None:
        img = D.draw_tags(img, v)
    D.pad_stem = pd
    hv = v.anchor(HOVER) if t is not None else None
    D.LIFT = old
    img = FR.dossier(img)
    img = FR.chrome_top(img, "Shop's behind you. Two ways left: the long way has a Rack.")
    img = FR.route_panel(img, len(v.opts), None)
    if t is not None:
        img = FR.node_file(img, HOVER, "52 / 60 on arrival")
    img, kbox = FR.legend(img, False)
    img = FR.finish_pencil(img, pen)
    if hv:
        img = FR.cursor(img, hv[0] + 8, hv[1] + 6)
    return img


def gif(var, n=15, ms=80):
    frames = []
    for f in range(n):
        t = f / (n - 1)
        im = FR.RL.bloom(build(var, t), 0.10, 0.84, 8).convert("RGB")
        frames.append(im.crop((300, 130, 1620, 1010)).resize((880, 587), Image.LANCZOS))
    frames += [frames[-1]] * 6
    path = os.path.join(FR.OUT, "%s_motion.gif" % var)
    FR.save_gif(frames, [ms] * n + [ms] * 5 + [900], path)


if __name__ == "__main__":
    args = sys.argv[1:]
    vs = [a for a in args if a.startswith("A")] or ["A1", "A2", "A3", "A4"]
    what = [a for a in args if a in ("rest", "hover", "gif", "snap")] or ["rest", "hover", "gif"]
    if "snap" in what:
        for i, s in snap().items():
            print(i, s)
    for var in vs:
        if "rest" in what:
            FR.save(build(var, None), "%s_rest.png" % var)
        if "hover" in what:
            FR.save(build(var, 1.0), "%s_hover.png" % var)
        if "gif" in what:
            gif(var)
