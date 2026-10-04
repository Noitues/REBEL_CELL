"""Round 36: ONE city model for the City Grid, the raid view and the netrun transit.

Source of truth = the game's own city layout (round6_city_restyle/city_layout.json, read-only, via citydata.py):
its street tiles, its 14 000 building extrusions (footprint, base, height, taper, ink), plazas, lane colours, the
five HQ lots and the Cell's base. Everything here is pure Python (Blender imports it too).

World units: 1 lot = U BU; world x = (lot_x - CX) * U, world y = -(lot_y - CY) * U  (hq_scene.py convention).
Camera: ONE orthographic iso camera for every view: yaw 135 deg (looking from +lot_x +lot_y, like the game's map),
pitch PITCH; only the target and ortho_scale change between the three views (and through the zoom).

python layout36.py  -> ../scratch/layout/unified.json (city export) + ../scratch/layout/net36.json (the network)
"""
import json
import math
import os
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
DST = os.path.join(ROOT, "scratch", "layout")

U = 6.0
CX, CY = 6.0, 6.0            # model centre (lots): between the four HQs and the Cell
RADIUS = 122.0               # lots exported around it
PITCH = 40.0
YAW = 135.0
W_, H_ = 1920, 1080

# the three views (+ the zoom path between them): target in LOTS, ortho in BU
VIEWS = {
    "city": dict(t=(5.0, 9.0), ortho=820.0),
    "raid": dict(t=(33.5, 35.0), ortho=176.0),
    "transit": None,          # filled from the network (the chosen link)
}


def W(p):
    return ((p[0] - CX) * U, -(p[1] - CY) * U)


def lots(wx, wy):
    return (wx / U + CX, -wy / U + CY)


def cam(target_lots, ortho):
    tx, ty = W(target_lots)
    return dict(yaw=YAW, pitch=PITCH, target=(tx, ty, 0.0), ortho=ortho, dist=2600.0)


def basis(c):
    yw, pt = math.radians(c["yaw"]), math.radians(c["pitch"])
    fwd = (math.cos(yw) * math.cos(pt), math.sin(yw) * math.cos(pt), -math.sin(pt))
    right = (math.sin(yw), -math.cos(yw), 0.0)
    up = (right[1] * fwd[2] - right[2] * fwd[1], right[2] * fwd[0] - right[0] * fwd[2], right[0] * fwd[1] - right[1] * fwd[0])
    return right, up, fwd


def project(c, x, y, z=0.0, w=W_, h=H_):
    r, u, f = basis(c)
    t = c["target"]
    d = (x - t[0], y - t[1], z - t[2])
    xc = sum(d[i] * r[i] for i in range(3))
    yc = sum(d[i] * u[i] for i in range(3))
    s = c["ortho"]
    return ((xc / s + 0.5) * w, (0.5 - yc / (s * h / w)) * h)


# ------------------------------------------------------------------ the network on the real streets
def street_graph(d):
    cells = {(s["i"], s["j"]) for s in d["streets"]}
    return cells


def nbrs(c, cells):
    i, j = c
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = (i + di, j + dj)
        if n in cells:
            yield n


def bfs(a, b, cells):
    prev = {a: None}
    q = deque([a])
    while q:
        c = q.popleft()
        if c == b:
            break
        for n in nbrs(c, cells):
            if n not in prev:
                prev[n] = c
                q.append(n)
    if b not in prev:
        return None
    out = []
    c = b
    while c is not None:
        out.append(c)
        c = prev[c]
    return out[::-1]


def simplify(path):
    """cell path -> polyline of corner cell centres (lots)."""
    pts = [(c[0] + 0.5, c[1] + 0.5) for c in path]
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = out[-1], pts[i], pts[i + 1]
        if (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]) != 0:
            out.append(b)
    out.append(pts[-1])
    return out


def nearest_cell(p, cells, pred=None):
    best = None
    for c in cells:
        if pred and not pred(c):
            continue
        dd = math.hypot(c[0] + 0.5 - p[0], c[1] + 0.5 - p[1])
        if best is None or dd < best[0]:
            best = (dd, c)
    return best[1]


def junction(c, cells):
    n = list(nbrs(c, cells))
    ax = any(x[0] != c[0] for x in n)
    ay = any(x[1] != c[1] for x in n)
    return ax and ay


# node: id, lot cell, state (owned / available / white / grey / core / hq), kind, tier
OWNED_PLAN = [("relay", 1), ("firewall", 1), ("vault", 2), ("safehouse", 1), ("proxy", 2), ("relay", 2)]
KIND_GLYPH = {"core": None, "relay": "picto_all_targets", "firewall": "slice_firewall", "vault": "placeholder_vault",
              "proxy": "placeholder_spoof", "safehouse": "placeholder_key", "site": "picto_target", "key": "placeholder_key"}


def build_network(d, L, cell_base=None):
    import citydata as CD
    cells = street_graph(d)
    hq = CD.hq_centres(d)
    cell_base = cell_base or CD.rc_base_centre(d, L)
    J = [c for c in cells if junction(c, cells)]
    nodes = []

    def add(nid, c, state, kind, tier, corp=""):
        nodes.append(dict(id=nid, cell=list(c), lot=[c[0] + 0.5, c[1] + 0.5], state=state, kind=kind, tier=tier, corp=corp))

    core = nearest_cell((cell_base[0] - 3.5, cell_base[1] - 3.5), J)
    add("core", core, "core", "core", 0, "rebel_cell")
    used = [core]

    def far(c, m):
        return all(math.hypot(c[0] - u[0], c[1] - u[1]) >= m for u in used)

    def ring(centre, r0, r1, n, spacing, state, kinds, corp="", bias=None):
        cand = [c for c in J if r0 <= math.hypot(c[0] + 0.5 - centre[0], c[1] + 0.5 - centre[1]) <= r1]
        if bias:
            cand.sort(key=bias)
        else:
            cand.sort(key=lambda c: (round(math.atan2(c[1] - centre[1], c[0] - centre[0]), 2), c))
        out = []
        for c in cand:
            if len(out) >= n:
                break
            if far(c, spacing):
                used.append(c)
                out.append(c)
        for k, c in enumerate(out):
            kind, tier = kinds[k % len(kinds)]
            add("%s%d" % (state[0], len(nodes)), c, state, kind, tier, corp)
        return out

    cb = (core[0] + 0.5, core[1] + 0.5)
    ring(cb, 3.5, 13, 6, 4.5, "owned", OWNED_PLAN, "rebel_cell", bias=lambda c: (math.hypot(c[0] - cb[0] - 1, c[1] - cb[1] - 1), c))
    # available Sites: one step beyond the owned ring, toward the corps
    ring(cb, 12, 19, 5, 6.0, "available", [("site", 1), ("site", 2), ("site", 1), ("site", 2), ("site", 1)],
         bias=lambda c: (math.hypot(c[0] - cb[0], c[1] - cb[1]) - 0.08 * ((cb[0] - c[0]) + (cb[1] - c[1])), c))
    # grey (used up) Sites inside / near the territory
    ring(cb, 6, 18, 2, 5.0, "grey", [("site", 1), ("site", 1)], bias=lambda c: (-(c[0] - cb[0]) + (c[1] - cb[1]), c))
    # white (not yet available) Sites near every HQ, with a tier-3 key in each corp district
    for corp, c0 in sorted(hq.items()):
        ring(c0, 9, 18, 4, 7.0, "white", [("site", 2), ("site", 3), ("key", 3), ("site", 2)], corp=corp,
             bias=lambda c, c0=c0: (abs(math.hypot(c[0] - c0[0], c[1] - c0[1]) - 12), c))
    # sprawl between the HQs: white T1/T2
    ring((10, 10), 18, 34, 7, 9.0, "white", [("site", 1), ("site", 2)])
    byid = {n["id"]: n for n in nodes}
    owned = [n for n in nodes if n["state"] in ("owned", "core")]

    def path(a, b):
        p = bfs(tuple(a["cell"]), tuple(b["cell"]), cells)
        return simplify(p) if p else None
    links = []

    def link(a, b, state):
        p = path(a, b)
        if p and len(p) >= 2:
            links.append(dict(a=a["id"], b=b["id"], state=state, pts=p))

    # owned: a tree from CORE (each owned node to its nearest already-connected owned node)
    conn = [byid["core"]]
    for n in sorted([n for n in owned if n["id"] != "core"], key=lambda n: math.hypot(n["lot"][0] - cb[0], n["lot"][1] - cb[1])):
        m = min(conn, key=lambda o: math.hypot(o["lot"][0] - n["lot"][0], o["lot"][1] - n["lot"][1]))
        link(m, n, "owned")
        conn.append(n)
    # border links: each available Site to its nearest owned node (orange), grey ones too (grey)
    for n in nodes:
        if n["state"] in ("available", "grey"):
            m = min(conn, key=lambda o: math.hypot(o["lot"][0] - n["lot"][0], o["lot"][1] - n["lot"][1]))
            link(m, n, "border" if n["state"] == "available" else "grey")
    # the wider grid: white Sites chain toward their nearest neighbour (dim white links)
    whites = [n for n in nodes if n["state"] == "white"]
    for n in whites:
        others = [o for o in nodes if o is not n and o["state"] in ("white", "available")]
        m = min(others, key=lambda o: math.hypot(o["lot"][0] - n["lot"][0], o["lot"][1] - n["lot"][1]))
        if not any({l["a"], l["b"]} == {n["id"], m["id"]} for l in links):
            link(m, n, "white")
    return dict(nodes=nodes, links=links, hq={k: list(v) for k, v in hq.items()}, cell_base=list(cell_base))


def transit_view(net):
    """The netrun transit view follows the longest border link (owned -> available)."""
    bl = [l for l in net["links"] if l["state"] == "border"]
    l = max(bl, key=lambda l: sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(l["pts"], l["pts"][1:])))
    pts = l["pts"]
    mid = pts[len(pts) // 2]
    return l, dict(t=(mid[0], mid[1]), ortho=88.0)


def load_net():
    return json.load(open(os.path.join(DST, "net36.json")))


if __name__ == "__main__":
    import citydata as CD
    import grid27
    d = CD.load()
    L = CD.Lots(d)
    hq = CD.hq_centres(d)
    cb = CD.rc_base_centre(d, L)
    fist = CD.fist_lots(d, L)          # the crest outline (round 34: red windows), kept before the patch drops it
    grid27.patch(d)                    # round 34 (locked): the Cell's district gets the normal street grid back
    rem = [(v, 5.6) for v in hq.values()] + [(cb, 4.6)]
    net = build_network(d, L, cb)
    net['fist'] = [[list(p), list(q)] for p, q in fist]
    # buildings standing ON a node's street cell are not possible (streets); nothing else is removed
    o = CD.export(d, L, (CX, CY), RADIUS, rem, os.path.join(DST, "unified.json"), extra=dict(hqs={k: list(v) for k, v in hq.items()},
                                                                                         cell_base=list(cb)))
    lk, tv = transit_view(net)
    net["transit"] = dict(link=[lk["a"], lk["b"]], t=list(tv["t"]), ortho=tv["ortho"])
    json.dump(net, open(os.path.join(DST, "net36.json"), "w"), indent=1)
    from collections import Counter
    print("buildings", len(o["buildings"]), "tiles", len(o["tiles"]), "nodes", Counter(n["state"] for n in net["nodes"]),
          "links", Counter(l["state"] for l in net["links"]), "transit", net["transit"], "cell", cb)
