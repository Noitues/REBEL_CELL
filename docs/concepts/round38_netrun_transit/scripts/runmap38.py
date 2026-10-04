"""Round 38 netrun transit: the run's own map, MEANDERING THROUGH THE BLOCKS along one border link.

Link: m1_d (owned, Priority relay) -> m2_d Priority Lane Exchange (T2), 16.5 lots, in plain city blocks.
GDD 4.2: the start (layer 0, the Cell's node), layers 1-6 with 2-3 nodes, layer 7 = the Site's Server Rack (TARGET);
the optional Server Rack sits in layer 4. Branches cross and MERGE (several nodes take two incoming edges).

Node spots are free ground INSIDE blocks (courtyards, alleys between buildings), not street junctions. Every edge is an
A* path on a 0.25-lot grid of the real city: building footprints are walls, street cells cost x6 (a path CROSSES a
street, it does not ride it), the open ground between buildings is cheap, and a seeded noise field + a pushed waypoint
make it weave in and out between the buildings of the blocks either side of the raid link.

python runmap38.py -> ../scratch/layout/run38.json (+ net_scope.json["transit"] = the fitted close camera)
"""
import heapq
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("NET36", "net_scope.json")
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import layout36 as L  # noqa: E402

LINK = ("m1_d", "m2_d")
RES = 8                                     # grid cells per lot
LAYERS = [1, 2, 3, 3, 3, 3, 2, 1]           # 0 = start, 7 = target
KINDS = {  # (layer, k) -> kind   GDD guarantees: L1 all Routers, a Modem in L3-5, ~1 Elite per layer in L3-6, Rack at L4
    (1, 0): "router", (1, 1): "router",
    (2, 0): "router", (2, 1): "terminal", (2, 2): "router",
    (3, 0): "modem", (3, 1): "elite", (3, 2): "router",
    (4, 0): "router", (4, 1): "rack", (4, 2): "terminal",
    (5, 0): "elite", (5, 1): "router", (5, 2): "modem",
    (6, 0): "router", (6, 1): "elite",
}
EDGES = {  # layer -> list of (k_from, k_to): crossing branches and merges (in-degree 2 marked *)
    0: [(0, 0), (0, 1)],
    1: [(0, 0), (0, 1), (1, 1), (1, 2)],                 # L2_1 *
    2: [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)],         # L3_0 *, L3_1 *
    3: [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)],         # L4_1 * (two), the optional Rack
    4: [(0, 0), (1, 0), (1, 1), (2, 2), (2, 1)],         # L5_0 *, L5_1 *
    5: [(0, 0), (1, 0), (1, 1), (2, 1)],                 # L6_0 *, L6_1 *
    6: [(0, 0), (1, 0)],                                 # L7 * (all merge into the Site)
}
WALKED = ["L0_0", "L1_1", "L2_1", "L3_1"]


def grids(box):
    u = json.load(open(os.path.join(L.DST, "unified.json")))
    x0, y0, x1, y1 = box
    w, h = int((x1 - x0) * RES), int((y1 - y0) * RES)

    def g(p):
        return ((p[0] - x0) * RES, (p[1] - y0) * RES)
    bm = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(bm)
    for b in u["buildings"]:
        q = b["q"]
        if not any(x0 - 2 < p[0] < x1 + 2 and y0 - 2 < p[1] < y1 + 2 for p in q):
            continue
        if b["h"] < 0.5:
            continue
        d.polygon([g(p) for p in q], fill=255)
    bld = np.asarray(bm, np.float32) > 0
    sm = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(sm)
    import citydata as CD
    for s in CD.load()["streets"]:
        i, j = s["i"], s["j"]
        if x0 - 1 < i < x1 + 1 and y0 - 1 < j < y1 + 1:
            d.rectangle([g((i, j)), g((i + 1, j + 1))], fill=255)
    street = np.asarray(sm, np.float32) > 0
    return bld, street, g


def noise(h, w, cell, seed):
    rng = np.random.default_rng(seed)
    n = rng.random((h // cell + 2, w // cell + 2)).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).resize(((w // cell + 2) * cell, (h // cell + 2) * cell), Image.BICUBIC)
    return np.asarray(im, np.float32)[:h, :w] / 255.0


def astar(cost, a, b):
    h, w = cost.shape
    INF = 1e18
    dist = {a: 0.0}
    prev = {a: None}
    pq = [(0.0, a)]
    nb = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
    while pq:
        f, c = heapq.heappop(pq)
        if c == b:
            break
        dc = dist[c]
        for dx, dy, s in nb:
            n = (c[0] + dx, c[1] + dy)
            if not (0 <= n[0] < w and 0 <= n[1] < h):
                continue
            cc = cost[n[1], n[0]]
            if cc >= 1e8:
                continue
            nd = dc + s * cc
            if nd < dist.get(n, INF):
                dist[n] = nd
                prev[n] = c
                heapq.heappush(pq, (nd + math.hypot(b[0] - n[0], b[1] - n[1]) * 0.9, n))
    out, c = [], b
    while c is not None:
        out.append(c)
        c = prev.get(c)
    return out[::-1]


def free_spot(free, tgt, used, g, rmax=70, ok=None):
    """The nearest free in-block ground cell to tgt, at least 1.6 lots from other nodes."""
    h, w = free.shape
    gx, gy = g(tgt)
    best = None
    for r in range(0, rmax):
        for yy in range(int(gy) - r, int(gy) + r + 1):
            for xx in (int(gx) - r, int(gx) + r) if abs(yy - int(gy)) != r else range(int(gx) - r, int(gx) + r + 1):
                if 0 <= xx < w and 0 <= yy < h and free[yy, xx] and (ok is None or ok(xx, yy)) and all(math.hypot(xx - u[0], yy - u[1]) >= 2.1 * RES for u in used):
                    best = (xx, yy)
                    break
            if best:
                break
        if best:
            break
    return best


def build():
    net = L.load_net()
    nb = {n["id"]: n for n in net["nodes"]}
    a, b = nb[LINK[0]]["lot"], nb[LINK[1]]["lot"]
    box = (min(a[0], b[0]) - 10, min(a[1], b[1]) - 3, max(a[0], b[0]) + 10, max(a[1], b[1]) + 3)
    bld, street, g = grids(box)
    h, w = bld.shape
    # open ground inside the blocks: not a building, not a street, at least 2 cells clear of walls
    clear = np.asarray(Image.fromarray((bld * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) == 0
    near_st = np.asarray(Image.fromarray((street * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * RES // 2 * 2 + 1)), np.float32) > 0
    free = clear & ~street
    deep = free & ~near_st                      # node spots: the block interior, half a lot off the street
    rng = random.Random(3838)
    L0 = lambda p: (p[0] / RES + box[0], p[1] / RES + box[1])     # noqa: E731
    used = [g(a), g(b)]
    nodes = []
    Ld = math.hypot(b[0] - a[0], b[1] - a[1])
    ux, uy = (b[0] - a[0]) / Ld, (b[1] - a[1]) / Ld
    px, py = -uy, ux
    for li, n in enumerate(LAYERS):
        if li == 0:
            nodes.append(dict(id="L0_0", layer=0, k=0, lot=list(a), kind="start", g=g(a)))
            continue
        if li == len(LAYERS) - 1:
            nodes.append(dict(id="L7_0", layer=li, k=0, lot=list(b), kind="rack", g=g(b)))
            continue
        t = li / (len(LAYERS) - 1)
        wig = rng.uniform(-1.5, 1.5)
        for k in range(n):
            off = wig + (k - (n - 1) / 2) * 4.2
            tgt = (a[0] + (b[0] - a[0]) * t + px * off, a[1] + (b[1] - a[1]) * t + py * off)
            along = lambda xx, yy, t=t: abs(((xx / RES + box[0] - a[0]) * ux + (yy / RES + box[1] - a[1]) * uy) / Ld - t) < 0.09  # noqa: E731
            c = None
            for sc in (1.0, 0.7, 0.45, 1.3):              # stay in the layer's band: pull in (or push out) before giving up
                tg2 = (a[0] + (b[0] - a[0]) * t + px * off * sc, a[1] + (b[1] - a[1]) * t + py * off * sc)
                c = free_spot(deep, tg2, used, g, 44, along) or free_spot(free, tg2, used, g, 44, along)
                if c:
                    break
            c = c or free_spot(free, tgt, used, g)
            used.append(c)
            nodes.append(dict(id="L%d_%d" % (li, k), layer=li, k=k, lot=list(L0((c[0] + 0.5, c[1] + 0.5))), kind=KINDS[(li, k)], g=c))
    byid = {n["id"]: n for n in nodes}
    # cost field: walls, streets (cross, don't ride), meander noise
    nz = noise(h, w, 6, 38) * 0.6 + noise(h, w, 3, 39) * 0.4
    base = 1.0 + 3.0 * nz
    cost = np.where(street, 6.0 + 2.0 * nz, base).astype(np.float64)
    cost = np.where(near_st & ~street, cost * 3.0, cost)        # do not hug the kerb: go into the block
    cost[bld] = 1e9
    edges = []
    for li, pairs in EDGES.items():
        for (ka, kb) in pairs:
            A, B = byid["L%d_%d" % (li, ka)], byid["L%d_%d" % (li + 1, kb)]
            ga = (int(A["g"][0]), int(A["g"][1]))
            gb = (int(B["g"][0]), int(B["g"][1]))
            # a waypoint pushed sideways between the two (seeded per edge) so it weaves, then two A* legs
            er = random.Random(hash((A["id"], B["id"])) & 0xFFFF if False else (li * 31 + ka * 7 + kb * 3))
            mx, my = (ga[0] + gb[0]) / 2, (ga[1] + gb[1]) / 2
            dx, dy = gb[0] - ga[0], gb[1] - ga[1]
            ln = math.hypot(dx, dy) or 1
            side = er.choice([-1, 1]) * er.uniform(1.0, 2.0) * RES
            wp_t = (mx - dy / ln * side, my + dx / ln * side)
            wp = free_spot(free, L0(wp_t), [], g) or (int(mx), int(my))
            for q in (ga, gb):
                cost[max(0, q[1] - 3):q[1] + 4, max(0, q[0] - 3):q[0] + 4] = np.minimum(cost[max(0, q[1] - 3):q[1] + 4, max(0, q[0] - 3):q[0] + 4], 2.0)
            p1 = astar(cost, ga, (int(wp[0]), int(wp[1])))
            p2 = astar(cost, (int(wp[0]), int(wp[1])), gb)
            path = p1 + p2[1:]
            # light smoothing (keep the weave): every 2nd cell, Chaikin once
            pts = [L0((c[0] + 0.5, c[1] + 0.5)) for c in path[::2]] + [L0((path[-1][0] + 0.5, path[-1][1] + 0.5))]
            sm = [pts[0]]
            for i in range(len(pts) - 1):
                p, q = pts[i], pts[i + 1]
                sm += [(p[0] * 0.75 + q[0] * 0.25, p[1] * 0.75 + q[1] * 0.25), (p[0] * 0.25 + q[0] * 0.75, p[1] * 0.25 + q[1] * 0.75)]
            sm.append(pts[-1])
            edges.append(dict(a=A["id"], b=B["id"], pts=[list(p) for p in sm]))
            for c in path[6:-6]:                       # later edges look for their own alley
                cost[max(0, c[1] - 2):c[1] + 3, max(0, c[0] - 2):c[0] + 3] += 2.5
    for n in nodes:
        n.pop("g", None)
    json.dump(dict(nodes=nodes, edges=edges, link=list(LINK), walked=WALKED), open(os.path.join(L.DST, "run38.json"), "w"), indent=1)
    # the close transit camera: fitted to every run node, clamped to 100-118 BU (round 39 was 190)
    import scope39
    tc = dict(t=[19.5, 8.0], ortho=130.0)    # framed so the run clears the HUD (grid search over the projected nodes)
    net["transit"] = dict(link=list(LINK), t=tc["t"], ortho=tc["ortho"])
    json.dump(net, open(os.path.join(L.DST, "net_scope.json"), "w"), indent=1)
    print("nodes", len(nodes), "edges", len(edges), "cam", tc)


def load():
    return json.load(open(os.path.join(L.DST, "run38.json")))


def states(run, walked, cur, show_all=False):
    """walked / current / option / target / white (shown only when show_all) / past / hidden."""
    g = {}
    for e in run["edges"]:
        g.setdefault(e["a"], []).append(e["b"])
    reach, todo = set(), [cur]
    while todo:
        for x in g.get(todo.pop(), []):
            if x not in reach:
                reach.add(x)
                todo.append(x)
    opts = g.get(cur, [])
    st = {}
    for n in run["nodes"]:
        i = n["id"]
        if i == cur:
            s = "current"
        elif i in walked:
            s = "walked"
        elif i in opts:
            s = "option"
        elif n["layer"] == 7:
            s = "target"
        elif i in reach:
            s = "white" if show_all else "hidden"
        else:
            s = "past" if show_all else "hidden"
        st[i] = s
    return st


if __name__ == "__main__":
    build()
