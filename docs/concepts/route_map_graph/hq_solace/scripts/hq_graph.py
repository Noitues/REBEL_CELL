"""HQ Solace: the double-helix towers and the LADDER run graph (pure python). Redesign 2026-10-15 (designer:
"solid towers, a bridge on every floor, the route climbs a ladder"); the v1 ribbon helix is archived in D:/rc_scratch.

THE TWIN-TOWER RULE (numbers in hq_preset "compound"):
  Two solid towers wind round one axis: floor f (height f * floor_h) of tower A is a box centred `radius` out at
  azimuth theta(f) = theta0 + twist * f, tower B is the same floor turned 180 degrees. Each floor turns `twist` from the
  one below, so the two stacks form a double helix. Every floor carries a glazed BOW-TIE skybridge between the two
  towers (the base pairs). Rooms are cutaways in the FRONT face of a floor (the face whose normal is theta + 90): both
  towers' rooms of a floor face the same way, so one camera sees a floor's two rooms and the bridge between them.
THE LADDER (the route, starts at the bottom, winds up):
  route floors (preset) on both towers: A1..A8, B1..B8. From a room: (a) UP the same tower to the next route floor
  (a facade stair), or (b) ACROSS the floor's skybridge to the other tower's room. Rooms are never revisited, so a
  crossing is one-way per floor. Start: the clinic gate on the plaza; the end: THE GENOME CORE in the crown that joins
  the two towers at the top (GDD 11.7; the TARGET).
THE SEQUENCE (round 43 decision: the strands are semi-random node sets: each tower's rooms draw from a seeded deck) +
  the READ rule (proposal): you read `read_ahead` route floors above the current one on both towers; higher floors are
  UNREAD (kind hidden: a frosted room in 3D, '?' in 2D).
Graph API: hqk_graph (bind). Ties by path order.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_preset as HP  # noqa: E402
import hqk_graph  # noqa: E402

CP = HP.PRESET["hq"]["compound"]
MECH = HP.PRESET["hq"]["mech"]
RW, RH, RD = CP["room_w"], CP["room_h"], CP["room_d"]
R = CP["radius"]
FH = CP["floor_h"]
TW, TD = CP["tower_w"], CP["tower_d"]
YF = 0.7
DOOR_Z = 1.6
CYCLE = 1
SHORTCUT_TYPES = ()
RF = CP["route_floors"]
PODIUM_H = CP["podium"][2]


def az_vec(a):
    r = math.radians(a)
    return (math.sin(r), math.cos(r))


def theta(f):
    return CP["theta0"] + CP["twist"] * f


def floor_z(f):
    return PODIUM_H + f * FH


def tower_frame(t, f):
    """(centre (x, y), radial unit (out from the axis), front normal) of tower t ('A' / 'B') at floor f."""
    rv = az_vec(theta(f))
    if t == "B":
        rv = (-rv[0], -rv[1])
    c = (rv[0] * R, rv[1] * R)
    n = az_vec(theta(f) + 90.0)
    return c, rv, n


NODES = ["start"]
TOWER, FLOOR, LEVEL = {}, {}, {}
for k, f in enumerate(RF):
    for t in ("A", "B"):
        nid = "%s%d" % (t, k + 1)
        NODES.append(nid)
        TOWER[nid], FLOOR[nid], LEVEL[nid] = t, f, k + 1
NODES.append("srv")
ROOM = {}
for i in NODES[1:-1]:
    c, rv, n = tower_frame(TOWER[i], FLOOR[i])
    ROOM[i] = dict(o=(c[0] + n[0] * TW / 2, c[1] + n[1] * TW / 2, floor_z(FLOOR[i]) + 1.0), n=n, w=RW, h=RH, d=RD)
SX, SY = CP["start"]
ROOM["start"] = dict(o=(SX, SY - 4.0, 0.4), n=(0.0, -1.0), w=8.0, h=4.6, d=6.0)
TOPF = CP["floors"]
ROOM["srv"] = dict(o=(0.0, 0.0, floor_z(TOPF) + 1.5), n=None, w=CP["target_w"], h=CP["target_h"], d=CP["target_w"])
LEVEL["start"], LEVEL["srv"] = 0, len(RF) + 1

_rr = random.Random(CP["seed"])
KIND = {"start": "start", "srv": "target"}
for i in NODES:
    if i not in KIND:
        KIND[i] = CP["deck"][_rr.randrange(len(CP["deck"]))]
LAYER = dict(LEVEL)
WORD = {"start": "CLINIC GATE", "router": "FIGHT", "elite": "ELITE", "terminal": "EVENT", "modem": "SHOP",
        "rack": "RACK", "target": "THE GENOME CORE"}
FILE = {
    "router": ("T4", "Fight: a ward security unit", ["20-30 Cycles, a card", "maybe a Firmware chip"]),
    "elite": ("T4", "Elite fight (a compliance lock)", ["40-50 Cycles, a rare card", "a Firmware chip"]),
    "terminal": ("T4", "Event: a patient terminal", ["a choice: card, Cycles", "or HP"]),
    "modem": ("T4", "Shop: spend Cycles", ["cards, Firmware, a heal"]),
    "rack": ("T4", "Rack: elite, then banks", ["banks your Schematics", "+3 Heat"]),
    "target": ("T4", "Central Server: the boss", ["the campaign", ""]),
}
HP_ARRIVE = "41 / 60"
NL = len(RF)
PATH = [("start", "A1"), ("start", "B1")]
for k in range(1, NL + 1):
    PATH += [("A%d" % k, "B%d" % k), ("B%d" % k, "A%d" % k)]
    if k < NL:
        PATH += [("A%d" % k, "A%d" % (k + 1)), ("B%d" % k, "B%d" % (k + 1))]
PATH += [("A%d" % NL, "srv"), ("B%d" % NL, "srv")]

WALK_DEC = ["start", "A1", "A2", "B2", "B3"]        # crossed on floor 2, climbing tower B: up to B4 or across to A3
HOVER_DEC = "A3"
WALK_MID = WALK_DEC


def base_edges(walked, mt):
    return list(PATH)


def edge_type(a, b):
    if a == "start":
        return "ramp"
    if b == "srv":
        return "to_crown"
    if TOWER.get(a) != TOWER.get(b):
        return "bridge"
    return "stair"


def door(i, side, mt=None):
    r = ROOM[i]
    n = r["n"] or (0.0, 1.0)
    t = (n[1], -n[0])
    x, y, z0 = r["o"]
    return (x + n[0] * YF + t[0] * side * r["w"] / 2, y + n[1] * YF + t[1] * side * r["w"] / 2, z0 + DOOR_Z)


def inner_side(i):
    """The door side (+1 / -1) of room i that faces the axis (the bridge)."""
    c, rv, n = tower_frame(TOWER[i], FLOOR[i])
    t = (n[1], -n[0])
    return 1 if (t[0] * -rv[0] + t[1] * -rv[1]) > 0 else -1


def edge_path(a, b, mt=None):
    t = edge_type(a, b)
    if t == "ramp":
        db = door(b, -inner_side(b))
        return [(SX, SY + 4.0, 1.2), ((db[0] + SX) * 0.5, -CP["podium"][1] - 6.0, 1.2),
                (db[0], -CP["podium"][1] + 2.0, PODIUM_H + 0.4), (db[0], db[1], PODIUM_H + 0.4), db]
    if t == "bridge":
        da, db = door(a, inner_side(a)), door(b, inner_side(b))
        n = ROOM[a]["n"]
        zf = floor_z(FLOOR[a]) + DOOR_Z + 1.0
        off = CP["bridge_w"][1] / 2 + 0.8                 # along the bridge's front edge (the waist)
        mid = (n[0] * off, n[1] * off, zf)
        return [da, ((da[0] + mid[0]) / 2 + n[0] * 2.0, (da[1] + mid[1]) / 2 + n[1] * 2.0, zf), mid,
                ((db[0] + mid[0]) / 2 + n[0] * 2.0, (db[1] + mid[1]) / 2 + n[1] * 2.0, zf), db]
    if t == "stair":
        da, db = door(a, -inner_side(a)), door(b, -inner_side(b))
        f0, f1 = FLOOR[a], FLOOR[b]
        pts = [da]
        for f in range(f0 + 1, f1 + 1):
            c, rv, n = tower_frame(TOWER[a], f)
            corner = (c[0] + rv[0] * (TD / 2 + 1.2) + n[0] * (TW / 2 + YF), c[1] + rv[1] * (TD / 2 + 1.2) + n[1] * (TW / 2 + YF))
            pts.append((corner[0], corner[1], floor_z(f) + DOOR_Z + 1.0))
        return pts + [db]
    da = door(a, inner_side(a))
    s = ROOM["srv"]["o"]
    pts = [da]
    for f in range(FLOOR[a] + 1, TOPF + 1):
        c, rv, n = tower_frame(TOWER[a], f)
        p = (c[0] - rv[0] * (TD / 2 - 2.0) + n[0] * (TW / 2 + YF), c[1] - rv[1] * (TD / 2 - 2.0) + n[1] * (TW / 2 + YF))
        pts.append((p[0], p[1], floor_z(f) + DOOR_Z + 1.0))
    return pts + [(s[0] + pts[-1][0] * 0.3, s[1] + pts[-1][1] * 0.3, s[2] + DOOR_Z)]


def seg_normal(p):
    """Links run on the front faces: hidden when the front of the floor at that height faces away."""
    f = max(0, min(TOPF, int(round((p[2] - PODIUM_H) / FH))))
    return az_vec(theta(f) + 90.0)


def mech(walked, mt=None):
    cur = walked[-1]
    lv = LEVEL.get(cur, 0)
    horizon = lv + MECH["read_ahead"]
    unread = [i for i in NODES if i not in ("start", "srv") and LEVEL[i] > horizon and i not in walked]
    return dict(horizon=horizon, unread=unread, affected=unread, level=lv, walked=list(walked),
                height=(floor_z(FLOOR[cur]) if cur in FLOOR else 0.0) / floor_z(TOPF))


hqk_graph.bind(globals())

_top = floor_z(TOPF) + CP["crown_h"] + 6.0
OV_POINTS = [(az_vec(a)[0] * (R + TW * 0.7), az_vec(a)[1] * (R + TW * 0.7), z) for a in range(0, 360, 45)
             for z in (0.0, _top)] + [(SX, SY - 6, 0.0)]


def CAM_RULE(walked, mt, CR):
    """The orbit-and-rise: the camera faces the front of the options' floor (the azimuth follows the twist), framing
    the current room, the room up and the room across; pitch rises with the climb."""
    st, opts = states(walked, mt)
    ids = ([walked[-1]] if walked[-1] != "start" else []) + opts
    pts = []
    for i in ids:
        pts += room_corners(i, mt)
    b = CR.beat(walked)
    if walked[-1] == "start":
        return CR.frame_points(pts, CR.look_yaw(opts or ids, mt), b["pitch"], b["lens"], CR.FILL_W, CR.FILL_H, dmin=CR.DMIN)
    c = room_center(walked[-1], mt)
    p = CR.frame_points(pts, CR.look_yaw(opts or ids, mt), b["pitch"], b["lens"], CR.FILL_W, CR.FILL_H, centre=c,
                        dmin=CR.DMIN)
    return CR.centre_on(p, c)                     # front and centre on the active room (designer review)


def MOVER_POS(mt, walked=None):
    return {}


def STILLS(CR):
    w = WALK_DEC
    return {
        "H_overview": (CR.overview(w), dict(walked=w)),
        "H_decision": (CR.decision(w), dict(walked=w)),
        "H_hover": (CR.hover(w, HOVER_DEC), dict(walked=w, hover=HOVER_DEC, hover_k=1.0)),
    }


def SHEET_SHOTS(CR):
    a = ["start", "A1"]
    b = ["start", "A1", "A2", "B2", "B3", "B4", "B5", "A5"]
    c = ["start", "A1", "A2", "B2", "B3", "B4", "B5", "A5", "A6", "A7", "B7", "B8"]
    return {"S_ground_floor": (CR.decision(a), dict(walked=a)),
            "S_mid_climb": (CR.decision(b), dict(walked=b)),
            "S_top": (CR.decision(c), dict(walked=c))}


REVEAL_T = 6.5


def REVEAL(CR):
    """The HQ beat: from the plaza looking straight up between the two towers (the bridges stack overhead like DNA
    rungs), the camera rises up the gap, orbiting with the twist, then pulls out to the OVERVIEW."""
    w = ["start"]
    o = CR.overview(WALK_DEC)
    n = int(REVEAL_T * CR.FPS)
    out = []
    for k in range(n):
        t = k / CR.FPS
        a = CR.ease(t / 3.4)
        z = PODIUM_H + 22.0 + 110.0 * a
        f = (z - PODIUM_H) / FH
        up = CR.Pose((0.0, 0.0, z + 30.0), theta(f) + 90.0 + 180.0, -62.0 + 30.0 * a, 46.0, 20.0, 0.0, 0.0)
        e = CR.ease((t - 2.8) / 3.0)
        p = up.mix(o, e)
        ui = CR.ease((t - 5.5) / 0.9)
        out.append((t, p, w, 0, dict(ui=ui, route=ui)))
    return out


if __name__ == "__main__":
    for i in NODES:
        print(i, KIND[i], "floor", FLOOR.get(i), "level", LEVEL[i])
    st, opts = states(WALK_DEC)
    print("DECISION at", WALK_DEC[-1], "options", opts, mech(WALK_DEC))
