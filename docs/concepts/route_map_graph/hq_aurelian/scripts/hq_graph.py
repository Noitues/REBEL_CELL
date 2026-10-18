"""Aurelian HQ (concept B, LOGGIA AND CAVEA): pure python. The room SLOTS come from aurelian_landmark.slots() for the
graph below; the graph itself is a MOCK fixture (spec 8.4: the topology belongs to the game; D10: 10 layers here).

Kit units (x 1 / k_units of the canonical city units). North = +y. The run: the Cell's box on the boulevard south of
the circus, up the outer colonnade (T1-T3, the attic AT), round the rim walk, down the four seating rings (R1-R4),
across the arena to THE CONCORDAT VAULT in the Rostrum's tholos. No mechanic (art makes no rule).
Graph API: hqk_graph (bind; Meridian v3's engine). Ties by path order.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import aurelian_landmark as AL  # noqa: E402
import hq_preset as HP  # noqa: E402
import hqk_graph  # noqa: E402  (Meridian v3's engine dir, on the path via hq_preset)

KS = 1.0 / AL.K_UNITS
CP = HP.PRESET["hq"]["compound"]
MECH = HP.PRESET["hq"]["mech"]
CAMP = HP.PRESET["hq"]["cam"]
LAYERS = [2, 3, 3, 4, 3, 3, 4, 3, 2, 1]          # MOCK fixture (the last layer = the vault)
YF = 0.7
DOOR_Z = 1.6
CYCLE = 1
SHORTCUT_TYPES = ()
KIND_CYCLE = ["router", "terminal", "router", "elite", "modem", "router", "rack", "router", "terminal", "elite"]


def nid(layer, node):
    return "srv" if layer == len(LAYERS) - 1 else "n%d_%d" % (layer, node)


SLOTS = AL.slots(LAYERS, "B")
for s_ in SLOTS:
    s_["id"] = nid(s_["layer"], s_["node"])
SLOT = {s_["id"]: s_ for s_ in SLOTS}


def _rec(s):
    w, h, d = s["size"]
    x, y, z = s["pos"]
    n = None if s["normal"] is None else (s["normal"][0], s["normal"][1])
    return dict(o=(x * KS, y * KS, z * KS), n=n, w=w * KS, h=h * KS, d=d * KS)


_st = AL.ell(math.radians(218.0), AL.A + 6.0)
ROOM = {"start": dict(o=(_st[0] * KS, _st[1] * KS, 0.4), n=(0.0, -1.0), w=8.0, h=4.6, d=6.0)}
for s_ in SLOTS:
    ROOM[s_["id"]] = _rec(s_)
NODES = ["start"] + [s_["id"] for s_ in SLOTS if s_["id"] != "srv"] + ["srv"]
EDGES = [("start", nid(0, j)) for j in range(LAYERS[0])]
EDGES += [(nid(*a), nid(*b)) for a, b in AL.fixture_edges(LAYERS)]
KIND = {"start": "start", "srv": "target"}
for k_, i_ in enumerate(n for n in NODES if n not in KIND):
    KIND[i_] = KIND_CYCLE[(SLOT[i_]["layer"] * 3 + SLOT[i_]["node"]) % len(KIND_CYCLE)]
LAYER = {"start": 0}
for i_ in NODES[1:]:
    LAYER[i_] = SLOT[i_]["layer"] + 1
WORD = {"start": "BOULEVARD", "router": "FIGHT", "elite": "ELITE", "terminal": "EVENT", "modem": "SHOP",
        "rack": "RACK", "target": "THE CONCORDAT VAULT"}
FILE = {
    "router": ("T4", "Fight", ["", ""]),
    "elite": ("T4", "Elite fight", ["", ""]),
    "terminal": ("T4", "Event", ["", ""]),
    "modem": ("T4", "Shop", ["", ""]),
    "rack": ("T4", "Rack", ["", ""]),
    "target": ("T4", "Central Server: the boss", ["", ""]),
}
HP_ARRIVE = "41 / 60"


def base_edges(walked, mt):
    return list(EDGES)


def edge_type(a, b):
    if a == "start":
        return "ramp"
    if b == "srv":
        return "arena_stair"
    ka, kb = SLOT[a]["kind"], SLOT[b]["kind"]
    if ka == "attic" and kb == "cavea":
        return "rim_walk"
    if SLOT[a]["level"] == SLOT[b]["level"]:
        return "gallery"
    return "stair_up" if SLOT[b]["pos"][2] > SLOT[a]["pos"][2] else "vomitorium"


def door(i):
    r = ROOM[i]
    n = r["n"] or (0.0, -1.0)
    x, y, z0 = r["o"]
    return (x + n[0] * YF * 3, y + n[1] * YF * 3, z0 + DOOR_Z)


def _arc(t0, t1, r_city, z, outward_off, inward, n=16):
    pts = []
    for k in range(n + 1):
        t = t0 + (t1 - t0) * k / n
        x, y = AL.ell(t, r_city)
        nr = AL.ell_normal(t, r_city, inward)
        pts.append(((x + nr[0] * outward_off) * KS, (y + nr[1] * outward_off) * KS, z))
    return pts


def _short(t0, t1):
    return t0 + ((t1 - t0 + math.pi) % (2 * math.pi)) - math.pi


def edge_path(a, b, mt=None):
    """World polylines (kit units): galleries follow the ellipse, stairs rise / fall at the end of a level, the rim walk
    crosses round the end of the bowl on the attic cap, the arena stair runs straight to the tholos."""
    da, db = door(a), door(b)
    if a == "start":
        return [da, (db[0], db[1] + 0.0, da[2]), db]
    if b == "srv":
        o = ROOM["srv"]["o"]
        v = (da[0] - o[0], da[1] - o[1])
        L = math.hypot(*v) or 1.0
        end = (o[0] + v[0] / L * 5.6 * KS, o[1] + v[1] / L * 5.6 * KS, o[2] + DOOR_Z)
        return [da, (da[0], da[1], end[2]), end]
    sa, sb = SLOT[a], SLOT[b]
    ta, tb = math.radians(sa["t"]), math.radians(sb["t"])
    if sa["kind"] == "attic" and sb["kind"] == "cavea":
        zr = (AL.RING_Z[0] + 0.7) * KS
        tb2 = _short(ta, tb)
        return [da, (da[0], da[1], zr)] + _arc(ta, tb2, AL.RING_R[0] + 0.2, zr, 0.0, True, 24) + [(db[0], db[1], zr), db]
    inward = sa["kind"] == "cavea"
    ra = math.hypot(sa["pos"][0], sa["pos"][1] / AL.BK)
    pts = [da] + _arc(ta, tb, ra, da[2], YF * 3 / KS, inward, 14)
    if abs(db[2] - da[2]) > 0.5 or SLOT[a]["level"] != SLOT[b]["level"]:
        pts.append((pts[-1][0], pts[-1][1], db[2]))
    pts.append(db)
    return pts


def seg_normal(p):
    return None


def mech(walked, mt=None):
    return dict(affected=[])


hqk_graph.bind(globals())

OCC_HIDDEN = ()
# the OVERVIEW frames the bowl: the colonnade's base and the rim all round, the campanili tops and the laurel crown
OV_POINTS = []
for k_ in range(24):
    t_ = 2 * math.pi * k_ / 24
    x_, y_ = AL.ell(t_, AL.A + 0.7)
    OV_POINTS += [(x_ * KS, y_ * KS, 0.0), (x_ * KS, y_ * KS, 18.4 * KS)]
OV_POINTS += [(0.0, 0.0, 26.0 * KS)]


def walk_to(n):
    """A walk of n steps from the start along the first edge each time (the mock run state)."""
    w = ["start"]
    while len(w) < n + 1:
        nx_ = sorted((b for a, b in EDGES if a == w[-1]), key=lambda q: ORDER[q])  # noqa: F821
        if not nx_:
            break
        w.append(nx_[0])
    return w


WALK_DEC = walk_to(2)              # current on T1 (layer 1), options up on T2
WALK_CAV = walk_to(7)              # current on R2 (layer 6), options down on R3
WALK_OV = WALK_DEC
WALK_MID = WALK_DEC
HOVER_DEC = None


def MOVER_POS(mt, walked=None):
    return {}


def _lerp(a, b, t):
    return a + (b - a) * t


def CAM_RULE(walked, mt, CR):
    """DESIGN.md section 7: loggia / attic rooms from outside (pitch 14-22 by tier), cavea rooms from inside the bowl
    (pitch 26-36 by ring); the yaw is the mean look of the distinct room normals, or the options' when that mean is
    degenerate (the rim-walk crossing, where the normals are opposite)."""
    ids = CR.decision_ids(walked, mt)
    cur = walked[-1]
    _, opts = states(walked, mt)  # noqa: F821

    def mean(ii):
        seen = []
        for i in ii:
            n = ROOM[i]["n"]
            if n is not None and (round(n[0], 2), round(n[1], 2)) not in seen:
                seen.append((round(n[0], 2), round(n[1], 2)))
        return (sum(-n[0] for n in seen), sum(-n[1] for n in seen)), len(seen)
    (sx, sy), cnt = mean(ids)
    if cnt and math.hypot(sx, sy) / cnt < 0.3:
        (sx, sy), cnt = mean(opts)
    yaw = CR.yaw_of((sx, sy)) if cnt else CAMP["ov_yaw"]
    s = SLOT.get(cur)
    if s is None or s["kind"] in ("loggia", "attic"):
        lvl = 0 if s is None else s["li"]
        pitch = _lerp(CAMP["pitch_lo"], CAMP["pitch_hi"], min(1.0, lvl / 3.0))
    else:
        ring = s["li"] - 4
        pitch = _lerp(CAMP["pitch_lo_cav"], CAMP["pitch_hi_cav"], max(0.0, min(1.0, ring / 3.0)))
    pts = []
    for i in ids:
        pts += room_corners(i, mt)  # noqa: F821
    c = room_center(cur, mt)  # noqa: F821
    if s is not None and s["kind"] in ("loggia", "attic"):
        # outside the colonnade the camera rides above the roofs across the boulevard (the blocks are tall: the city
        # looks down into the circus), at least dmin_loggia out; the occlusion rule flattens the blocks in the cone
        p = CR.frame_points(pts, yaw, pitch, CAMP["lens_loggia"], CR.FILL_W, CR.FILL_H, centre=c, dmin=CAMP["dmin_loggia"])
        return CR.centre_on(p, c)
    p = CR.frame_points(pts, yaw, pitch, CR.LENS_D, CR.FILL_W, CR.FILL_H, centre=c, dmin=CR.DMIN)
    return CR.centre_on(p, c)




def STILLS(CR):
    _, opts = states(WALK_DEC)  # noqa: F821
    hov = opts[-1]
    return {"H_overview": (CR.overview(WALK_OV), dict(walked=WALK_OV)),
            "H_decision": (CR.decision(WALK_DEC), dict(walked=WALK_DEC)),
            "H_decision_cavea": (CR.decision(WALK_CAV), dict(walked=WALK_CAV)),
            "H_hover": (CR.hover(WALK_DEC, hov), dict(walked=WALK_DEC, hover=hov, hover_k=1.0))}


def SHEET_SHOTS(CR):
    return {}


def REVEAL(CR):
    return []


if __name__ == "__main__":
    st_, op_ = states(WALK_DEC)  # noqa: F821
    print("nodes", len(NODES), "edges", len(EDGES), "dec", WALK_DEC, "options", op_, "cav", WALK_CAV)
