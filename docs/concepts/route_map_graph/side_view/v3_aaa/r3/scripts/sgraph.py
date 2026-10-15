"""Side view: the run graph and the street layout rule (pure data, no Blender, no PIL).

The graph is the same realistic run as the parent round (route_map_graph/scripts/rgraph.py) so the two rounds compare
1:1: 19 nodes, 7 steps + the start, fight / elite / event / shop / rack, the TARGET Rack at the end.

LAYOUT RULE (the whole idea of the side view):
  graph layer L  -> building column L along the street (left = start, right = the TARGET tower)
  slot k in L    -> a floor of that building; k sorted by height (k = 0 lowest), so a planar graph stays planar
  edge a -> b    -> a physical link across the alley between column L and L+1:
                    same floor = a straight skybridge; otherwise a catwalk out of a's door, a lift riser in the alley
                    (its own lane), and a catwalk into b's door. Lanes are ordered so that no two links cross:
                    rising links: the one that ends higher takes the lane further left; falling links: the one that
                    ends lower takes the lane further left (disjoint height ranges never meet).
World units (BU): x along the street, z up, the street front face at y = 0. Side ortho: 10 px per BU at 1080p,
screen x = 10 x, screen y = GROUND_Y - 10 z. Ties broken by (layer, k), never by dict order.
"""
import json
import os

KIND = {
    "L0_0": "start",
    "L1_0": "router", "L1_1": "router", "L1_2": "router",
    "L2_0": "terminal", "L2_1": "router", "L2_2": "router",
    "L3_0": "modem", "L3_1": "elite", "L3_2": "terminal",
    "L4_0": "router", "L4_1": "rack", "L4_2": "router",
    "L5_0": "elite", "L5_1": "router", "L5_2": "modem",
    "L6_0": "router", "L6_1": "elite",
    "L7_0": "target",
}
_E = {
    0: [(0, 0), (0, 1), (0, 2)],
    1: [(0, 0), (1, 0), (1, 1), (2, 2)],
    2: [(0, 0), (1, 1), (2, 1), (2, 2)],
    3: [(0, 0), (0, 1), (1, 1), (2, 2)],
    4: [(0, 0), (1, 0), (1, 1), (2, 2)],
    5: [(0, 0), (1, 0), (1, 1), (2, 1)],
    6: [(0, 0), (1, 0)],
}
EDGES = [("L%d_%d" % (l, a), "L%d_%d" % (l + 1, b)) for l in sorted(_E) for a, b in _E[l]]
NODES = sorted(KIND, key=lambda i: (int(i[1]), int(i[3])))
LAYER = {i: int(i[1]) for i in NODES}
K = {i: int(i[3]) for i in NODES}

WORD = {"start": "START", "router": "FIGHT", "elite": "ELITE", "terminal": "EVENT", "modem": "SHOP", "rack": "RACK",
        "target": "TARGET"}
FILE = {
    "router": ("T1", "Fight: a security room", ["15-25 Cycles, a card", "maybe a Firmware chip"]),
    "elite": ("T1", "Elite fight (armoured)", ["30-40 Cycles, a rare card", "a Firmware chip"]),
    "terminal": ("T1", "Event: a Terminal voice", ["a choice: card, Cycles", "or HP"]),
    "modem": ("T1", "Shop: spend Cycles", ["cards, Firmware, a heal"]),
    "rack": ("T2", "Rack: elite, then banks", ["banks your Schematics", "+3 Heat"]),
    "target": ("T2", "The Site's Server Rack", ["the Site, +12 Schematics", "an Exploit"]),
}
HP_ARRIVE = "52 / 60"          # concept value: no node damages on arrival in this run

WALK_START = ["L0_0"]
WALK_MID = ["L0_0", "L1_0", "L2_0", "L3_0"]          # fight, event, now at the shop
HOVER_MID = "L4_1"                                    # option 2 = the Rack

# ------------------------------------------------------------------ the street (world units)
PX = 10.0                     # px per BU at 1080p (side ortho)
GROUND_Y = 930.0              # screen y of the street surface (z = 0)
FLOOR_H = 8.0                 # one storey
SLAB = 0.9                    # floor slab thickness (the cut slab in section)
COL_W = 13.0                  # building width (a column)
ALLEY = 7.5                   # alley between columns (the links' lanes live here)
X0 = 31.5                     # left edge of column L0 (the sidebar is left of it)
TGT_W = 16.0                  # the TARGET tower is wider
DEPTH = 12.0                  # building depth (y)

# floor of each node (k sorted low to high): rising and falling comes from these
FLOOR = {
    "L0_0": 0,
    "L1_0": 1, "L1_1": 3, "L1_2": 5,
    "L2_0": 1, "L2_1": 4, "L2_2": 6,
    "L3_0": 2, "L3_1": 4, "L3_2": 7,
    "L4_0": 1, "L4_1": 4, "L4_2": 6,
    "L5_0": 2, "L5_1": 5, "L5_2": 7,
    "L6_0": 3, "L6_1": 6,
    "L7_0": 8,
}
# building heights in storeys (route floors + solid floors above; the TARGET tower tallest)
STOREYS = {0: 3, 1: 7, 2: 8, 3: 9, 4: 7, 5: 9, 6: 8, 7: 10}


def col_x(l):
    """(x0, x1) of column l."""
    x0 = X0 + l * (COL_W + ALLEY)
    return (x0, x0 + (TGT_W if l == 7 else COL_W))


def room_box(i):
    """(x0, z0, x1, z1) of node i's room opening (inside the cut walls and slabs)."""
    x0, x1 = col_x(LAYER[i])
    f = FLOOR[i]
    return (x0 + 0.7, f * FLOOR_H + SLAB / 2, x1 - 0.7, (f + 1) * FLOOR_H - SLAB / 2)


DOOR_Z = 1.6                  # links meet a room 1.6 BU above its floor (catwalk deck height)


def door(i, side):
    x0, z0, x1, z1 = room_box(i)
    return ((x0 if side == "L" else x1), z0 + DOOR_Z)


def lanes():
    """edge -> lane x (BU) for every non-straight edge, per alley. No two links cross."""
    out = {}
    for l in range(7):
        es = [(a, b) for a, b in EDGES if LAYER[a] == l]
        rise = [(a, b) for a, b in es if FLOOR[b] > FLOOR[a]]
        fall = [(a, b) for a, b in es if FLOOR[b] < FLOOR[a]]
        rise.sort(key=lambda e: (-FLOOR[e[1]], -FLOOR[e[0]], e))
        fall.sort(key=lambda e: (FLOOR[e[1]], FLOOR[e[0]], e))
        # disjoint height ranges never cross, so the two groups can share lane positions; keep them apart anyway
        order = []
        for e in fall + rise:
            order.append(e)
        ax0 = col_x(l)[1]
        ax1 = col_x(l + 1)[0]
        n = len(order)
        for j, e in enumerate(order):
            out[e] = ax0 + (ax1 - ax0) * (j + 1) / (n + 1)
    return out


LANE = lanes()
CHAMFER = 0.9                 # 45 deg corner chamfer (BU)


def edge_path(a, b):
    """World polyline (x, z) of the link a -> b: catwalk, riser, catwalk (45/90 only, chamfered)."""
    ax, az = door(a, "R")
    bx, bz = door(b, "L")
    if FLOOR[a] == FLOOR[b]:
        return [(ax, az), (bx, bz)]
    lx = LANE[(a, b)]
    c = CHAMFER if bz > az else -CHAMFER
    return [(ax, az), (lx - CHAMFER, az), (lx, az + c), (lx, bz - c), (lx + CHAMFER, bz), (bx, bz)]


def to_px(x, z):
    return (x * PX, GROUND_Y - z * PX)


# ------------------------------------------------------------------ states
def succ(i):
    return sorted([b for a, b in EDGES if a == i], key=lambda n: (LAYER[n], K[n]))


def reach(froms):
    seen, stack = set(), list(froms)
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        stack.extend(succ(n))
    return seen


def states(walked):
    """node -> walked | current | option | reach | target | grey (past or cut off)."""
    cur = walked[-1]
    opts = succ(cur)
    fut = reach(opts)
    st = {}
    for i in NODES:
        if i == cur:
            st[i] = "current"
        elif i in walked:
            st[i] = "walked"
        elif i in opts:
            st[i] = "option"
        elif KIND[i] == "target":
            st[i] = "target"
        elif i in fut:
            st[i] = "reach"
        else:
            st[i] = "grey"
    return st, opts


def edge_states(walked, st):
    out = {}
    for a, b in EDGES:
        if a in walked and b in walked and walked.index(b) == walked.index(a) + 1:
            out[(a, b)] = "walked"
        elif st[a] == "current" and st[b] == "option":
            out[(a, b)] = "option"
        elif st[a] in ("option", "reach") and st[b] in ("reach", "target"):
            out[(a, b)] = "future"
        else:
            out[(a, b)] = "grey"
    return out


def branch(o):
    """The hovered option's downstream: nodes it can reach (itself included) and the edges inside."""
    ns = reach([o])
    return ns, {(a, b) for a, b in EDGES if a in ns and b in ns}


def dump(path):
    """Layout JSON for the Blender scene."""
    d = dict(nodes={i: dict(kind=KIND[i], layer=LAYER[i], k=K[i], floor=FLOOR[i], room=room_box(i)) for i in NODES},
             edges=[dict(a=a, b=b, path=edge_path(a, b)) for a, b in EDGES],
             cols={l: col_x(l) for l in range(8)}, storeys=STOREYS,
             const=dict(FLOOR_H=FLOOR_H, SLAB=SLAB, DEPTH=DEPTH, ALLEY=ALLEY))
    with open(path, "w") as f:
        json.dump(d, f, indent=1)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch", "layout.json")
    dump(out)
    for e in EDGES:
        print(e, FLOOR[e[0]], "->", FLOOR[e[1]], "lane", round(LANE.get(e, 0), 2))
    # self-check: no two links of one alley cross (segment intersection, endpoints excluded)
    def segs(p):
        return list(zip(p, p[1:]))

    def cross(s, t):
        (x1, y1), (x2, y2) = s
        (x3, y3), (x4, y4) = t
        d = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
        if abs(d) < 1e-9:
            return False
        u = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / d
        v = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / d
        return 1e-6 < u < 1 - 1e-6 and 1e-6 < v < 1 - 1e-6
    bad = 0
    for i, e in enumerate(EDGES):
        for f in EDGES[i + 1:]:
            if LAYER[e[0]] != LAYER[f[0]] or e[0] == f[0] or e[1] == f[1]:
                continue
            if any(cross(s, t) for s in segs(edge_path(*e)) for t in segs(edge_path(*f))):
                print("CROSS", e, f)
                bad += 1
    print("crossings:", bad)
