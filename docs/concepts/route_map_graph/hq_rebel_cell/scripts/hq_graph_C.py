"""Rebel Cell, OPTION C: the converging map (designer brief 2026-10-15). The Cell's district (bible 4.4, round 34): a
normal street grid, the fist drawn in red windows; NO landmark tower: DISPATCH is a plain building at the fist's palm.
Three operatives start at three edges of the district (west roofs, the south street, east roofs) and converge on the
DISPATCH node at the palm; each lane ends at its KILL SWITCH; the three switches must be thrown on the same step; then
ONE operative enters the showdown, the other two park at their switches (support). Machinery: rc_lanes.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_preset as HP  # noqa: E402
import hqk_graph  # noqa: E402
import rc_lanes  # noqa: E402

VARIANT = "C"
CP = HP.PRESET["hq"]["compound"]
MECH = HP.PRESET["hq"]["mech"]
RW, RH, RD = CP["room_w"], CP["room_h"], CP["room_d"]
YF = 0.7
DOOR_Z = 1.6
CYCLE = 1
SHORTCUT_TYPES = ()
LANES = ("L", "C", "R")
RUNNERS = CP["runners"]
PALM = CP["palm"]
S0 = (0.0, -1.0)                                  # every room opens south (the camera's side)

NODES = ["start", "L1", "C1", "R1", "L2", "L2a", "C2", "R2", "R2a", "L2b", "R2b", "L3", "C3", "R3", "LK", "CK", "RK",
         "srv"]
LANE = {n: n[0] for n in NODES if n[0] in LANES}
SWITCH = {"L": "LK", "C": "CK", "R": "RK"}
CC = CP["conv"]
ROOM = {}
for nid, (x, y, z) in CC["rooms"].items():
    ROOM[nid] = dict(o=(x, y, z), n=S0, w=RW, h=RH, d=RD)
SX, SY = CP["start"]
ROOM["start"] = dict(o=(SX, SY, 0.4), n=S0, w=8.0, h=4.6, d=6.0)
ROOM["srv"] = dict(o=(PALM[0], PALM[1], CP["dispatch_z"]), n=None, w=18.0, h=10.0, d=14.0)
KIND = {"start": "start", "srv": "target"}
KIND.update(CP["kinds"])
DEPTH = {"start": 0, "L1": 1, "C1": 1, "R1": 1, "L2": 2, "L2a": 2, "C2": 2, "R2": 2, "R2a": 2, "L2b": 3, "R2b": 3,
         "L3": 3, "C3": 3, "R3": 3, "LK": 4, "CK": 4, "RK": 4, "srv": 5}
LAYER = dict(DEPTH)
WORD = {"start": "THE DROP", "router": "FIGHT", "elite": "MIRROR", "terminal": "EVENT", "modem": "SHOP",
        "switch": "KILL SWITCH", "target": "DISPATCH"}
FILE = {
    "router": ("T5", "Fight: DISPATCH's crew", ["20-30 Cycles, a card", "maybe a Firmware chip"]),
    "elite": ("T5", "MIRROR: your own slices", ["your wheel x1.5, one pointer", "your Daemons (GDD M11)"]),
    "terminal": ("T5", "Event: the old safehouse", ["a choice: card, Cycles", "or HP"]),
    "modem": ("T5", "Shop: the street kitchen", ["cards, Firmware, a heal"]),
    "switch": ("T5", "KILL SWITCH: throw it together", ["all 3 on one step", "a lone throw re-arms"]),
    "target": ("T5", "DISPATCH: the final showdown", ["one operative enters", "two hold the switches"]),
}
HP_ARRIVE = "41 / 60"
PATH = [("start", "L1"), ("start", "C1"), ("start", "R1"),
        ("L1", "L2"), ("L1", "L2a"), ("L2a", "L2b"), ("L2b", "L3"), ("L2", "L3"), ("L3", "LK"), ("LK", "srv"),
        ("C1", "C2"), ("C2", "C3"), ("C3", "CK"), ("CK", "srv"),
        ("R1", "R2"), ("R1", "R2a"), ("R2a", "R2b"), ("R2b", "R3"), ("R2", "R3"), ("R3", "RK"), ("RK", "srv")]

WALK_DEC = ["start", "L1", "C1", "R1", "L2a", "C2", "R2a"]               # mid-run (step 2)
WALK_SWITCH = WALK_DEC + ["L2b", "C2", "R2b", "L3", "C3", "R3", "LK", "CK", "RK"]   # all three switches thrown
WALK_SHOW = WALK_SWITCH + ["srv"]                                        # the GHOST (alley) enters
HOVER_DEC = "L2b"
WALK_MID = WALK_DEC


def base_edges(walked, mt):
    return list(PATH)


def edge_type(a, b):
    if a == "start":
        return "drop"
    if b == "srv":
        return "showdown"
    if KIND[b] == "switch":
        return "to_switch"
    return "lane"


def door(i, side, mt=None):
    r = ROOM[i]
    n = r["n"] or S0
    t = (n[1], -n[0])
    x, y, z0 = r["o"]
    return (x + n[0] * YF + t[0] * side * r["w"] / 2, y + n[1] * YF + t[1] * side * r["w"] / 2, z0 + DOOR_Z)


def edge_path(a, b, mt=None):
    pa, pb = ROOM[a]["o"], ROOM[b]["o"]
    if a == "start":
        db = (pb[0], pb[1] - YF, pb[2] + DOOR_Z)
        return [(SX, SY - YF, 1.2), (db[0], SY - YF, 1.2), (db[0], db[1] - 8.0, 1.2), (db[0], db[1] - 8.0, db[2]), db]
    da = (pa[0], pa[1] - YF, pa[2] + DOOR_Z)
    if b == "srv":
        s = ROOM["srv"]["o"]
        return [da, (da[0], da[1] - 5.0, da[2]), (s[0] + (da[0] - s[0]) * 0.3, s[1] - 12.0, s[2] + DOOR_Z), (s[0], s[1] - 6.0, s[2] + DOOR_Z)]
    db = (pb[0], pb[1] - YF, pb[2] + DOOR_Z)
    zc = max(da[2], db[2]) if LANE.get(a) != "C" else da[2]
    return [da, (da[0], da[1] - 5.0, da[2]), (db[0], db[1] - 7.0, zc), (db[0], db[1] - 7.0, db[2]), db]


def seg_normal(p):
    return None


rc_lanes.bind(globals())
hqk_graph.bind(globals())

FX, FY = CP["fist"]["x"], CP["fist"]["y"]
OV_POINTS = [(x, y, 0.0) for x in FX for y in FY] + [(SX, SY - 10.0, 0.0)]


def CAM_RULE(walked, mt, CR):
    """Pan between operatives: the camera looks up the district (north) at the active operative (front and centre),
    with the other two lanes in view."""
    st, opts = states(walked)
    ids = [c for c in lane_currents(walked).values() if c != "start"] + opts
    pts = []
    for i in ids:
        pts += room_corners(i)  # noqa: F821
    b = CR.beat(walked)
    return CR.frame_points(pts, 0.0, b["pitch"], b["lens"], CR.FILL_W, CR.FILL_H, dmin=CR.DMIN)


def MOVER_POS(mt, walked=None):
    return {}


def STILLS(CR):
    w = WALK_DEC
    return {
        "H_overview": (CR.overview(w), dict(walked=w)),
        "H_decision": (CR.decision(w), dict(walked=w)),
        "H_hover": (CR.hover(w, HOVER_DEC), dict(walked=w, hover=HOVER_DEC, hover_k=1.0)),
    }


def OPTION_SHOTS(CR):
    """Option C's concept frames: mid-run, the kill-switch moment, the convergence."""
    o = CR.overview(WALK_DEC)
    near = CR.Pose((PALM[0], PALM[1] - 40.0, 20.0), 0.0, 40.0, 420.0, 30.0, -0.06, 0.02)
    sw = WALK_DEC + ["L2b", "C2", "R2b", "L3", "C3", "R3", "LK", "CK", "RK"]
    return {
        "OC_1_midrun": (o, dict(walked=WALK_DEC, extra=dict(red=1.0))),
        "OC_2_switch": (near, dict(walked=sw, extra=dict(red=1.0, pulse=1.0, switch_moment=1))),
        "OC_3_showdown": (near, dict(walked=WALK_SHOW, extra=dict(red=1.0, pulse=0.3, showdown=1))),
    }


def RED_SHOTS(CR):
    """The red sequence (round 34 blackout reveal + the review): before, blackout, red spreading, the full fist."""
    top = CR.Pose((0.0, 110.0, 0.0), 0.0, 62.0, 760.0, 30.0, -0.04, 0.0)
    w = ["start"]
    return {
        "RS_1_before": (top, dict(walked=w, extra=dict(seq=0.0, ui_off=1))),
        "RS_2_blackout": (top, dict(walked=w, extra=dict(seq=1.0, ui_off=1))),
        "RS_3_spreading": (top, dict(walked=w, extra=dict(seq=2.0, ui_off=1))),
        "RS_4_full": (top, dict(walked=w, extra=dict(seq=3.0, ui_off=1))),
    }


def SHEET_SHOTS(CR):
    return {}


REVEAL_T = 6.5


def REVEAL(CR):
    """The HQ beat = the red sequence in motion: straight down over the district, ordinary windows with a few red ones
    (the fist barely hinted); the BLACKOUT (the ring and the hand's lines go dark); the red SPREADS from the palm until
    the whole fist glows; then the tilt down to the OVERVIEW; route and UI last."""
    w = ["start"]
    o = CR.overview(WALK_DEC)
    top = CR.Pose((0.0, 110.0, 0.0), 0.0, 62.0, 760.0, 30.0, -0.04, 0.0)
    n = int(REVEAL_T * CR.FPS)
    out = []
    for k in range(n):
        t = k / CR.FPS
        seq = 3.0 * CR.ease(t / 4.0) if t < 4.0 else 3.0
        e = CR.ease((t - 4.0) / 2.0)
        p = top.mix(o, e)
        ui = CR.ease((t - 5.6) / 0.8)
        out.append((t, p, w, 0, dict(ui=ui, route=ui, seq=seq)))
    return out
