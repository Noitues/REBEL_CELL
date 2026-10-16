"""HQ Solace: the double-helix towers and the LADDER run graph (pure python). Redesign 2026-10-15 (designer:
"solid towers, a bridge on every floor, the route climbs a ladder"); the v1 ribbon helix is archived in D:/rc_scratch.

THE TWIN-TOWER RULE (numbers in hq_preset "compound"):
  Two swept tubes wind round one axis: at floor f (height f * floor_h) the centre of strand A sits `radius` out at
  azimuth theta(f) = theta0 + twist * f, strand B opposite. v3 (designer review of round 1): 27 floors x 13.33 deg =
  ONE FULL TURN per strand, at the full-city landmark's twist rate (helix angle ~37 deg).
THE WINDOWS (v3): ONLY 2 a floor per strand: one facing INWARD (toward the other strand: the walkway) and one OUTWARD.
  Each is a landscape oval spanning `win.span` degrees of its tube half (half axes: span/2 of arc, `win.half_h` up).
  On the route floors the INWARD window IS the route node: a lit, kind-dressed interior behind it, the bow-tie bridge
  enters it, and the 2D node outline is the oval (the part of it the camera sees).
  Angles round a tube (phi) are measured from the floor's FRONT normal n = az(theta + 90): phi 0 = the front band (the
  UP stair runs up it), A's inward window at phi +90, B's at -90; outward windows opposite.
THE LADDER (the route, starts at the bottom, winds up):
  route floors (preset) on both strands: A1..A8, B1..B8. From a room: (a) UP the same strand to the next route floor
  (the front-band stair), or (b) ACROSS the floor's skybridge to the other strand's inward window. Rooms are never
  revisited, so a crossing is one-way per floor. Start: the clinic gate on the plaza; the end: THE GENOME CORE in the
  crown that joins the two strands at the top (GDD 11.7; the TARGET).
THE SEQUENCE (round 43 decision: the strands are semi-random node sets: each tower's rooms draw from a seeded deck) +
  the READ rule (proposal): you read `read_ahead` route floors above the current one on both towers; higher floors are
  UNREAD (kind hidden: a frosted window in 3D, '?' in 2D).
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
WIN = CP["win"]
R = CP["radius"]
FH = CP["floor_h"]
RT = CP["tube_r"]
TW, TD = CP["tower_w"], CP["tower_d"]
DOOR_Z = 1.6
CYCLE = 1
SHORTCUT_TYPES = ()
RF = CP["route_floors"]
PODIUM_H = CP["podium"][2]
WA = math.radians(WIN["span"] / 2.0)          # the oval's half span round the tube (radians)
WB = WIN["half_h"]                            # the oval's half height
CHORD = 2.0 * RT * math.sin(WA)
WAX = CHORD / 2.0                             # the flat oval's level half width (140 deg of its tube half)


def az_vec(a):
    r = math.radians(a)
    return (math.sin(r), math.cos(r))


def theta(f):
    return CP["theta0"] + CP["twist"] * f


def floor_z(f):
    return PODIUM_H + f * FH


def tower_frame(t, f):
    """(centre (x, y), radial unit (out from the axis), front normal) of tower t ('A' / 'B') at (fractional) floor f."""
    rv = az_vec(theta(f))
    if t == "B":
        rv = (-rv[0], -rv[1])
    c = (rv[0] * R, rv[1] * R)
    n = az_vec(theta(f) + 90.0)
    return c, rv, n


def tube_pt(t, z, phi, r=None):
    """A point on (or r from the centre line of) strand t at height z, phi from the front normal (CCW from above)."""
    c, rv, n = tower_frame(t, (z - PODIUM_H) / FH)
    rr = RT if r is None else r
    tx = (n[1], -n[0])
    return (c[0] + (n[0] * math.cos(phi) + tx[0] * math.sin(phi)) * rr,
            c[1] + (n[1] * math.cos(phi) + tx[1] * math.sin(phi)) * rr, z)


def phi_in(t):
    """phi of strand t's inward window normal: toward the other strand, turned `win.face_front` toward the floor front
    (planar windows facing straight at each other could never both face one camera)."""
    a = math.pi / 2 - math.radians(WIN["face_front"])
    return a if t == "A" else -a


def stair_phi(t):
    """The solid band between the two windows on the front side: the UP stair / link runs up it."""
    return -math.radians(WIN["stair_phi"]) if t == "A" else math.radians(WIN["stair_phi"])


def win_z(f):
    return floor_z(f) + WIN["zc"]


def win_centre_phi(t, side):
    return phi_in(t) + (0.0 if side == "in" else math.pi)


_WF = {}


def win_frame(t, f, side="in"):
    """v3 planar window (designer, after t3: no helix bending): a LEVEL / PLUMB oval in a vertical plane.
    C = the strand's centre line at the window's middle height, nw = the plane's normal (horizontal), tw = its level
    major axis. The skin is cut by the oval prism along nw (head on: a true oval); the flat glass / back wall sits in
    the plane at depth dp from C, as deep as the slanted tube needs so no point of the flat oval pokes out of it."""
    key = (t, f, side)
    if key in _WF:
        return _WF[key]
    zc = win_z(f)
    c = tube_pt(t, zc, 0.0, 0.0)
    p = tube_pt(t, zc, win_centre_phi(t, side), 1.0)
    nw = (p[0] - c[0], p[1] - c[1])
    tw = (nw[1], -nw[0])
    fr = dict(t=t, f=f, side=side, C=c, nw=nw, tw=tw, zc=zc)
    lam = [skin_depth(fr, WAX * math.cos(2 * math.pi * k / 96), WB * math.sin(2 * math.pi * k / 96)) for k in range(96)]
    fr["dp"] = min(lam) - 0.3
    _WF[key] = fr
    return fr


def skin_depth(fr, u, dz):
    """Depth (along nw, from C) of the strand's skin in front of the plane point (u, dz) (the tube slides with z)."""
    c = tube_pt(fr["t"], fr["zc"] + dz, 0.0, 0.0)
    rx, ry = c[0] - fr["C"][0], c[1] - fr["C"][1]
    su = rx * fr["tw"][0] + ry * fr["tw"][1]
    sn = rx * fr["nw"][0] + ry * fr["nw"][1]
    return sn + math.sqrt(max(0.0, RT * RT - (u - su) ** 2))


def win_pt(fr, u, dz, depth):
    C, nw, tw = fr["C"], fr["nw"], fr["tw"]
    return (C[0] + tw[0] * u + nw[0] * depth, C[1] + tw[1] * u + nw[1] * depth, fr["zc"] + dz)


def win_local(fr, p):
    """(u, dz, depth) of world point p in the window's frame."""
    dx, dy = p[0] - fr["C"][0], p[1] - fr["C"][1]
    return (dx * fr["tw"][0] + dy * fr["tw"][1], p[2] - fr["zc"], dx * fr["nw"][0] + dy * fr["nw"][1])


def win_uv(k, n):
    a = 2 * math.pi * k / n
    return WAX * math.cos(a), WB * math.sin(a)


def win_plane_outline(fr, n=72, lift=0.0):
    """The flat oval in the window plane (the glass / frame / node outline)."""
    return [win_pt(fr, *win_uv(k, n), fr["dp"] + lift) for k in range(n)]


def win_skin_outline(fr, n=72):
    """Where the oval prism leaves the skin (the hole's edge; head on it is the same oval)."""
    out = []
    for k in range(n):
        u, dz = win_uv(k, n)
        out.append(win_pt(fr, u, dz, skin_depth(fr, u, dz)))
    return out


NODES = ["start"]
TOWER, FLOOR, LEVEL = {}, {}, {}
for k, f in enumerate(RF):
    for t in ("A", "B"):
        nid = "%s%d" % (t, k + 1)
        NODES.append(nid)
        TOWER[nid], FLOOR[nid], LEVEL[nid] = t, f, k + 1
NODES.append("srv")


def _node_rec(i):
    """The node's room record = its inward window's flat plane (kit: o = sill centre, n = the plane's normal)."""
    fr = win_frame(TOWER[i], FLOOR[i], "in")
    o = win_pt(fr, 0.0, -WB, fr["dp"])
    return dict(o=o, n=fr["nw"], w=2 * WAX, h=2 * WB, d=2.0)


ROOM = {}
for i in NODES[1:-1]:
    ROOM[i] = _node_rec(i)
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

WALK_DEC = ["start", "A1", "A2", "B2", "B3"]        # crossed on route floor 2, climbing tower B: up to B4 or across to A3
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


BAND_R = RT + 1.0                                     # the stair / link band radius


def _tip(i):
    """Where the UP stair meets node i: the inward window's tip on the stair side, at the window's middle."""
    fr = win_frame(TOWER[i], FLOOR[i], "in")
    sp = tube_pt(TOWER[i], fr["zc"], stair_phi(TOWER[i]), 1.0)
    side = 1.0 if ((sp[0] - fr["C"][0]) * fr["tw"][0] + (sp[1] - fr["C"][1]) * fr["tw"][1]) > 0 else -1.0
    u = side * WAX * 0.97
    return win_pt(fr, u, 0.0, skin_depth(fr, u, 0.0) + 0.6)


def _band(t, z0, z1, step=2.5):
    n = max(1, int(abs(z1 - z0) / step))
    return [tube_pt(t, z0 + (z1 - z0) * k / n, stair_phi(t), BAND_R) for k in range(n + 1)]


def deck_z(f):
    """The bridge deck = the node window's recess floor."""
    return win_z(f) - 0.75 * WB


def _in_recess(i, z):
    """A point inside node i's recess at height z, on the radial line to the other strand (the bridge's end)."""
    t = TOWER[i]
    c, rv, n = tower_frame(t, (z - PODIUM_H) / FH)
    return (c[0] - rv[0] * RT * 0.72, c[1] - rv[1] * RT * 0.72, z)


def edge_path(a, b, mt=None):
    t = edge_type(a, b)
    if t == "ramp":
        tb = TOWER[b]
        base = tube_pt(tb, PODIUM_H + 0.6, stair_phi(tb), BAND_R)
        return [(SX, SY + 4.0, 1.2), ((base[0] + SX) * 0.5, -CP["podium"][1] - 6.0, 1.2),
                (base[0], -CP["podium"][1] + 2.0, PODIUM_H + 0.4)] + _band(tb, PODIUM_H + 0.6, win_z(FLOOR[b])) + [_tip(b)]
    if t == "bridge":
        f = FLOOR[a]
        zf = deck_z(f) + DOOR_Z
        da, db = _in_recess(a, zf), _in_recess(b, zf)
        n = tower_frame("A", (zf - PODIUM_H) / FH)[2]
        off = CP["bridge_w"][1] / 2 + 0.8                 # along the bridge's front edge (the waist)
        mid = (n[0] * off, n[1] * off, zf)
        return [da, ((da[0] + mid[0]) / 2 + n[0] * 2.0, (da[1] + mid[1]) / 2 + n[1] * 2.0, zf), mid,
                ((db[0] + mid[0]) / 2 + n[0] * 2.0, (db[1] + mid[1]) / 2 + n[1] * 2.0, zf), db]
    if t == "stair":
        return [_tip(a)] + _band(TOWER[a], win_z(FLOOR[a]), win_z(FLOOR[b])) + [_tip(b)]
    s = ROOM["srv"]["o"]
    pts = [_tip(a)] + _band(TOWER[a], win_z(FLOOR[a]), floor_z(TOPF) + DOOR_Z)
    return pts + [(s[0] + pts[-1][0] * 0.3, s[1] + pts[-1][1] * 0.3, s[2] + DOOR_Z)]


def seg_normal(p):
    """A link segment hides when its side faces away: on a strand's skin the skin normal, on a bridge the front."""
    f = (p[2] - PODIUM_H) / FH
    for t in ("A", "B"):
        c = tower_frame(t, f)[0]
        d = math.hypot(p[0] - c[0], p[1] - c[1])
        if d < RT + 3.0 and p[2] > PODIUM_H + 0.3:
            return ((p[0] - c[0]) / d, (p[1] - c[1]) / d)
    fi = max(0, min(TOPF, int(round(f))))
    return az_vec(theta(fi) + 90.0)


# ------------------------------------------------------------------ the oval node outline (2D overlay)
FACING_MIN = 0.12        # a node's flat window counts as seen when cos(camera, its normal) is above this


def visible_outline(i, cam, n=72):
    """Node i's flat oval (in its window plane) when the camera sees its face, else None (it faces away, or the other
    strand stands in the way)."""
    fr = win_frame(TOWER[i], FLOOR[i], "in")
    m = win_pt(fr, 0.0, 0.0, fr["dp"])
    v = (cam[0] - m[0], cam[1] - m[1], cam[2] - m[2])
    L = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    if (v[0] * fr["nw"][0] + v[1] * fr["nw"][1]) / max(L, 1e-6) < FACING_MIN:
        return None
    o = "B" if TOWER[i] == "A" else "A"
    for k in range(1, 60):
        s = k / 60.0
        q = (m[0] + (cam[0] - m[0]) * (1 - s), m[1] + (cam[1] - m[1]) * (1 - s), m[2] + (cam[2] - m[2]) * (1 - s))
        if abs(q[2] - m[2]) > 60.0 or q[2] < PODIUM_H:
            continue
        co = tower_frame(o, (q[2] - PODIUM_H) / FH)[0]
        if math.hypot(q[0] - co[0], q[1] - co[1]) < RT * 0.92:
            return None
    return win_plane_outline(fr, n, 0.05)


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
    """The orbit-and-rise (v3): the camera faces the FRONT band of the decision's floors (the floor of the current
    room and its options, so the azimuth follows the twist: 13.3 deg a floor); the two inward windows (the current
    room and the room ACROSS) sit at the strands' inner edges, the UP stair on the front band between."""
    st, opts = states(walked, mt)
    ids = ([walked[-1]] if walked[-1] != "start" else []) + opts
    pts = []
    for i in ids:
        pts += room_corners(i, mt)
    fl = [FLOOR[i] for i in ids if i in FLOOR]
    fm = sum(fl) / len(fl) if fl else RF[0]
    nf = az_vec(theta(fm + WIN["zc"] / FH) + 90.0)
    cur = walked[-1]
    if cur in TOWER:
        # turn CAM_BIAS toward the current window's facing, so the active oval opens toward the camera
        nc = ROOM[cur]["n"]
        b_ = math.radians(CAM_BIAS)
        nf = (nf[0] * math.cos(b_) + nc[0] * math.sin(b_), nf[1] * math.cos(b_) + nc[1] * math.sin(b_))
    yaw = CR.yaw_of((-nf[0], -nf[1]))
    b = CR.beat(walked)
    if cur == "start":
        return CR.frame_points(pts, yaw, b["pitch"], b["lens"], CR.FILL_W, CR.FILL_H, dmin=CR.DMIN)
    c = room_center(cur, mt)
    p = CR.frame_points(pts, yaw, b["pitch"], b["lens"], CR.FILL_W, CR.FILL_H, dmin=CR.DMIN)
    sx, sy = p.sx, p.sy
    q = CR.centre_on(p, c)                         # front and centre on the active room (designer review) ...
    q.sx, q.sy = sx + (q.sx - sx) * CAM_CENTRE_K, sy + (q.sy - sy) * CAM_CENTRE_K   # ... part way: the options stay in
    return q


CAM_BIAS = 0.0           # v3 decision: degrees the camera turns from the floor front toward the current window (planar windows: 0, both inward windows face 55 deg off the camera)
CAM_CENTRE_K = 0.4       # v3 decision: how far toward the active room the frame centres (1 = exactly on it)


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


def DEBUG_SHOTS(CR):
    """Close looks for checking the windows / rooms (not deliverables)."""
    w = WALK_DEC
    c = tube_pt("B", win_z(10), 0.0, 0.0)
    n = tower_frame("B", 10.4)[2]
    return {"D_win": (CR.Pose((c[0], c[1], win_z(10)), CR.yaw_of((-n[0], -n[1])) - 30.0, 8.0, 45.0, 35.0), dict(walked=w)),
            "D_node": (CR.Pose(room_center("B3"), CR.yaw_of((-ROOM["B3"]["n"][0], -ROOM["B3"]["n"][1])) + 25.0, 10.0,
                               45.0, 35.0), dict(walked=w))}


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
        z = PODIUM_H + 22.0 + 160.0 * a
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
