"""V3 dynamic: the run graph (unchanged from the parent) and a 3D street layout with varied buildings, room depths and
ten connection types (pure data, no Blender, no PIL).

Graph: imported from the parent's sgraph.py copy (same 19 nodes, same edges, same mid-run state), so it compares 1:1.

LAYOUT RULE (3D):
  graph layer L  -> route building column L along the street (x), its own width COLW[L] and front depth DY[L] (y)
  slot k in L    -> a floor of that building (FLOOR, k sorted by height so a planar graph stays planar)
  edge a -> b    -> a connection of type CONN[(a, b)] across the alley between L and L+1. The type follows the step:
                    same floor = skybridge tube / plank / data-pipe; rising = cargo lift / fire escape / duct / tram
                    rail / conduit; falling = zip-line / duct / service tunnel / rooftop jump. It is a hint only:
                    the node type always reads from the room and the sticker.
World units (BU): x along the street, y away from the street (the camera is at -y), z up. Ties by (layer, k).
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from sgraph import KIND, EDGES, NODES, LAYER, K, WORD, FILE, HP_ARRIVE, WALK_START, WALK_MID, HOVER_MID  # noqa: E402,F401
from sgraph import succ, reach, states, edge_states, branch  # noqa: E402,F401

# later states of the same run (used for the video and D_end)
WALK_END = ["L0_0", "L1_0", "L2_0", "L3_0", "L4_1", "L5_1", "L6_1"]     # last room before the TARGET: option 1 = TARGET
VIDEO_WALK = ["L0_0", "L1_0", "L2_0", "L3_0"]                          # the video's 3 steps: ladder, plank, duct

FLOOR_H = 8.0
SLAB = 0.9
DEPTH = 12.0
DOOR_Z = 1.6
LAST = 7
COLW = [12.0, 15.0, 13.0, 15.0, 14.0, 14.0, 12.0, 18.0]      # building widths vary
ALLEYW = [12.0, 10.0, 10.0, 11.0, 10.0, 10.0, 11.0]           # alleys host the connections
DY = [1.0, -3.0, 2.5, -1.0, 3.0, -2.5, 1.5, 0.0]               # front face depth per column: rooms sit at different depths
X0 = 0.0

# floors (presentation only): COMPACT. Siblings sit on consecutive floors and a step moves at most 4 floors, so the
# decision set (current + options) spans 3-4 storeys and can fill the frame. Topology and types are the parent's.
FLOOR = {
    "L0_0": 0,
    "L1_0": 1, "L1_1": 2, "L1_2": 3,
    "L2_0": 1, "L2_1": 3, "L2_2": 4,
    "L3_0": 2, "L3_1": 3, "L3_2": 5,
    "L4_0": 0, "L4_1": 3, "L4_2": 4,
    "L5_0": 1, "L5_1": 3, "L5_2": 5,
    "L6_0": 2, "L6_1": 4,
    "L7_0": 6,
}
STOREYS = {0: 2, 1: 5, 2: 6, 3: 6, 4: 5, 5: 7, 6: 6, 7: 9}
# building silhouette above the route floors (archetype per column)
ARCH = {0: "relay", 1: "setback", 2: "slab", 3: "tower", 4: "setback", 5: "billboard", 6: "tower", 7: "target"}

# connection type per edge (concept: hand-set by the rule in the docstring; the generator picks within the class)
CONN = {
    ("L0_0", "L1_0"): "ladder", ("L0_0", "L1_1"): "lift", ("L0_0", "L1_2"): "conduit",
    ("L1_0", "L2_0"): "plank", ("L1_1", "L2_0"): "zip", ("L1_1", "L2_1"): "ladder", ("L1_2", "L2_2"): "tube",
    ("L2_0", "L3_0"): "duct", ("L2_1", "L3_1"): "tube", ("L2_2", "L3_1"): "zip", ("L2_2", "L3_2"): "ladder",
    ("L3_0", "L4_0"): "tunnel", ("L3_0", "L4_1"): "lift", ("L3_1", "L4_1"): "pipe", ("L3_2", "L4_2"): "roofjump",
    ("L4_0", "L5_0"): "ladder", ("L4_1", "L5_0"): "zip", ("L4_1", "L5_1"): "plank", ("L4_2", "L5_2"): "ladder",
    ("L5_0", "L6_0"): "tram", ("L5_1", "L6_0"): "duct", ("L5_1", "L6_1"): "lift", ("L5_2", "L6_1"): "zip",
    ("L6_0", "L7_0"): "lift", ("L6_1", "L7_0"): "tram",
}
# lane (fraction across the alley) for the types that use one: rising, the one that ends higher further left;
# falling, the one that ends lower further left; a lane is never shared inside one alley
LANE_F = {
    ("L0_0", "L1_0"): 0.78, ("L0_0", "L1_1"): 0.5, ("L0_0", "L1_2"): 0.2,
    ("L1_1", "L2_1"): 0.5, ("L2_2", "L3_2"): 0.5,
    ("L3_0", "L4_0"): 0.3, ("L3_0", "L4_1"): 0.62,
    ("L4_0", "L5_0"): 0.5, ("L4_2", "L5_2"): 0.5,
    ("L5_1", "L6_1"): 0.25, ("L6_0", "L7_0"): 0.8,
}
CONN_NAME = {"tube": "skybridge tube", "zip": "zip-line", "lift": "cargo lift", "duct": "ventilation duct crawl",
             "ladder": "fire escape", "roofjump": "rooftop jump", "tram": "maintenance tram rail",
             "plank": "window-to-window plank", "pipe": "data-pipe (packets)", "tunnel": "service tunnel",
             "conduit": "conduit catwalk"}
CONN_HINT = {"tube": "level / gentle climb", "zip": "down", "lift": "up (or down)", "duct": "one floor, either way",
             "ladder": "up, floor by floor", "roofjump": "roof to roof, down", "tram": "steep climb",
             "plank": "level", "pipe": "level", "tunnel": "down, under the street", "conduit": "climb (legacy)"}


def col_x(l):
    x = X0
    for j in range(l):
        x += COLW[j] + ALLEYW[j]
    return (x, x + COLW[l])


def alley(l):
    return (col_x(l)[1], col_x(l + 1)[0])


def room_box(i):
    """(x0, z0, x1, z1) of node i's room opening; its front face is at y = DY[layer]."""
    x0, x1 = col_x(LAYER[i])
    f = FLOOR[i]
    return (x0 + 0.7, f * FLOOR_H + SLAB / 2, x1 - 0.7, (f + 1) * FLOOR_H - SLAB / 2)


def room_corners(i):
    """8 world corners of the room (front 4 then back 4)."""
    x0, z0, x1, z1 = room_box(i)
    y0 = DY[LAYER[i]]
    y1 = y0 + DEPTH - 0.6
    return [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), (x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]


def room_center(i):
    x0, z0, x1, z1 = room_box(i)
    return ((x0 + x1) / 2, DY[LAYER[i]] + 2.0, (z0 + z1) / 2)


def roof_z(l):
    return STOREYS[l] * FLOOR_H


YF = -0.7     # links run just in front of the facade


def _yat(x, xa, xb, ya, yb):
    if abs(xb - xa) < 1e-6:
        return ya
    t = max(0.0, min(1.0, (x - xa) / (xb - xa)))
    return ya + (yb - ya) * t


def edge_path(a, b):
    """3D polyline (x, y, z) the operative takes from a to b (also the overlay cable)."""
    typ = CONN[(a, b)]
    la = LAYER[a]
    ax0, az0, ax1, az1 = room_box(a)
    bx0, bz0, bx1, bz1 = room_box(b)
    ya, yb = DY[la] + YF, DY[la + 1] + YF
    za, zb = az0 + DOOR_Z, bz0 + DOOR_Z
    A, B = (ax1, za), (bx0, zb)
    p0, p1 = alley(la)
    aw = p1 - p0
    lx = p0 + aw * LANE_F.get((a, b), 0.5)
    mid = (p0 + p1) / 2
    xz = None
    y_explicit = None
    if typ in ("tube", "plank"):
        xz = [A, B]
    elif typ == "pipe":
        xz = [(ax1, za + 2.6), (bx0, zb + 2.6)]
    elif typ == "conduit":
        c = 0.9 if zb > za else -0.9
        xz = [A, (lx - 0.9, za), (lx, za + c), (lx, zb - c), (lx + 0.9, zb), B]
    elif typ == "lift":
        xz = [A, (lx, za), (lx, zb), B]
    elif typ == "ladder":
        pts = [A, (lx - 1.6, za)]
        n = max(2, int(round(abs(zb - za) / (FLOOR_H / 2))))
        for k in range(1, n + 1):
            pts.append((lx + (1.6 if k % 2 else -1.6), za + (zb - za) * k / n))
        pts.append(B)
        xz = pts
    elif typ == "zip":
        xz = [A, (ax1 + 0.8, za + 3.4), (bx0 - 0.8, zb + 2.2), B]
    elif typ == "duct":
        h = abs(zb - za) / 2
        xz = [A, (mid - h, za), (mid + h, zb), B]
    elif typ == "tram":
        x_end = (p0 + aw * 0.8 - 1.5) if (la == 6) else (p1 - 1.0)
        xz = [A, (p0 + 1.0, za), (x_end, zb), B]
    elif typ == "roofjump":
        ra, rb = roof_z(la) + 1.2, roof_z(la + 1) + 1.2
        xa_, xb_ = col_x(la)[1] - 1.5, col_x(la + 1)[0] + 1.5
        pts = [A, (ax1 + 0.3, za), (ax1 + 0.3, ra - 1.0), (xa_, ra)]
        top = max(ra, rb) + 3.0
        for k in range(1, 8):
            t = k / 8
            x = xa_ + (xb_ - xa_) * t
            z = (1 - t) * ra + t * rb + 4 * (top - (ra + rb) / 2) * t * (1 - t)
            pts.append((x, z))
        pts += [(xb_, rb), (bx0 - 0.3, rb - 1.0), (bx0 - 0.3, zb), B]
        xz = pts
    elif typ == "tunnel":
        zt = -2.6
        yt = -4.8
        hx = bx0 + 3.5
        out = [(ax1, ya, za), (lx, ya, za), (lx, ya, zt), (lx + 2.0, yt, zt), (hx, yt, zt), (hx, yt, -0.2),
               (hx, DY[la + 1] + YF, bz0 + 0.4), (hx + 0.5, DY[la + 1] + 1.5, bz0 + DOOR_Z)]
        return out
    out = []
    for x, z in xz:
        out.append((x, _yat(x, ax1, bx0, ya, yb), z))
    return out


def street_len():
    return col_x(LAST)[1]


def dump(path, extra=None):
    d = dict(nodes={i: dict(kind=KIND[i], layer=LAYER[i], k=K[i], floor=FLOOR[i], room=room_box(i), dy=DY[LAYER[i]])
                    for i in NODES},
             edges=[dict(a=a, b=b, type=CONN[(a, b)], path=edge_path(a, b)) for a, b in EDGES],
             cols={l: col_x(l) for l in range(8)}, dy=DY, storeys=STOREYS, arch=ARCH,
             const=dict(FLOOR_H=FLOOR_H, SLAB=SLAB, DEPTH=DEPTH, YF=YF))
    if extra:
        d.update(extra)
    with open(path, "w") as f:
        json.dump(d, f, indent=1)


def crossings():
    """Self-check: no two links of one alley cross in the street elevation (x, z), shared ends excluded."""
    def segs(p):
        q = [(x, z) for x, _, z in p]
        return list(zip(q, q[1:]))

    def cross(s, t):
        (x1, y1), (x2, y2) = s
        (x3, y3), (x4, y4) = t
        d = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
        if abs(d) < 1e-9:
            return False
        u = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / d
        v = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / d
        return 1e-6 < u < 1 - 1e-6 and 1e-6 < v < 1 - 1e-6
    bad = []
    for i, e in enumerate(EDGES):
        for f in EDGES[i + 1:]:
            if LAYER[e[0]] != LAYER[f[0]] or e[0] == f[0] or e[1] == f[1]:
                continue
            if any(cross(s, t) for s in segs(edge_path(*e)) for t in segs(edge_path(*f))):
                bad.append((e, f))
    return bad


if __name__ == "__main__":
    for e in EDGES:
        print(e, CONN[e], FLOOR[e[0]], "->", FLOOR[e[1]])
    print("types used:", sorted(set(CONN.values())))
    print("crossings:", crossings())
    print("street length", street_len())
