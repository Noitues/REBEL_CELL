"""Rebel Cell, OPTION A (picked by the designer 2026-10-15): three STACKED lanes in one side-view cross-section.

Derived from the real district grid (one continuous city, no separate street set): the section is cut along the
grid's street line `stack.cut` just south of DISPATCH's block at the fist's palm; the first row of real blocks north of
the cut is opened like a dollhouse. The three lanes run east along that street toward the palm:
  L  BREAKER on the ROOFTOPS of that row (rooftop rooms; the detour climbs over a taller roof behind)
  C  GHOST at STREET level (the row's ground floors: shopfronts)
  R  RIGGER in the SERVICE TUNNEL under the street (the detour drops to a deeper service level)
Each lane ends at its KILL SWITCH in a column at `x_switch`; the three must be thrown on the same step (a lone throw
re-arms); DISPATCH counters one room (STALL +1); then ONE operative takes the service shaft into DISPATCH (the palm
building's server floor: the TARGET), the other two PARK at their switches as support. Machinery: rc_lanes.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_preset as HP  # noqa: E402
import hqk_graph  # noqa: E402
import rc_lanes  # noqa: E402

VARIANT = "A"
CP = HP.PRESET["hq"]["compound"]
MECH = HP.PRESET["hq"]["mech"]
STK = CP["stack"]
RW, RH, RD = CP["room_w"], CP["room_h"], CP["room_d"]
YF = 0.7
DOOR_Z = 1.6
CYCLE = 1
SHORTCUT_TYPES = ()
LANES = ("L", "C", "R")
RUNNERS = CP["runners"]
PALM = CP["palm"]
S0 = (0.0, -1.0)
CUT = STK["cut"]

NODES = ["start", "L1", "C1", "R1", "L2", "L2a", "C2", "R2", "R2a", "L2b", "R2b", "L3", "C3", "R3", "LK", "CK", "RK",
         "srv"]
LANE = {n: n[0] for n in NODES if n[0] in LANES}
SWITCH = {"L": "LK", "C": "CK", "R": "RK"}
X0, DX = STK["x0"], STK["dx"]
XS = {"1": X0, "2": X0 + DX, "3": X0 + 2 * DX, "2a": X0 + DX - 10.0, "2b": X0 + DX + 14.0, "K": STK["x_switch"]}
ZL = STK["z"]
ROOF = STK["roofs"]                              # the rooftop rooms' roof heights (the real blocks' heights)
ROOM = {}
for s in LANES:
    for key in ("1", "2", "3", "K", "2a", "2b"):
        nid = s + key if key != "K" else s + "K"
        if nid not in NODES:
            continue
        if s == "L":
            z = ROOF.get(key, ROOF["1"])
        elif s == "R":
            z = ZL["R"] - (12.0 if key in ("2a", "2b") else 0.0)
        else:
            z = ZL["C"]
        ROOM[nid] = dict(o=(XS[key], CUT, z), n=S0, w=RW, h=RH, d=RD)
SX = X0 - 46.0
ROOM["start"] = dict(o=(SX, CUT, 0.4), n=S0, w=8.0, h=4.6, d=6.0)
ROOM["srv"] = dict(o=(STK["dispatch_x"], CUT, STK["dispatch_z"]), n=S0, w=18.0, h=10.0, d=12.0)
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
WALK_SWITCH = WALK_DEC + ["L2b", "C2", "R2b", "L3", "C3", "R3", "LK", "CK", "RK"]
WALK_SHOW = WALK_SWITCH + ["srv"]                                        # the GHOST (street) enters
HOVER_DEC = "L2b"
WALK_MID = WALK_DEC
SHAFT_X = STK["x_switch"] + 12.0


def base_edges(walked, mt):
    return list(PATH)


def edge_type(a, b):
    if a == "start":
        return "drop"
    if b == "srv":
        return "shaft"
    if KIND[b] == "switch":
        return "to_switch"
    return "lane"


def door(i, side, mt=None):
    r = ROOM[i]
    x, y, z0 = r["o"]
    return (x - side * r["w"] / 2, y - YF, z0 + DOOR_Z)       # S-facing: screen-right = +x = side -1 in the kit frame


def edge_path(a, b, mt=None):
    """Along the section plane (just in front of the cut): out of a's east door, across, up / down where the level
    changes (a ladder on the facade, a stair in the tunnel), into b's west door; the showdown: the service shaft."""
    pa, pb = ROOM[a]["o"], ROOM[b]["o"]
    if a == "start":
        db = door(b, 1)
        return [(SX + 4.0, CUT - YF, 1.2), (db[0] - 6.0, CUT - YF, 1.2), (db[0] - 6.0, CUT - YF, db[2]), db]
    da = door(a, -1)
    if b == "srv":
        s = ROOM["srv"]["o"]
        zs = s[2] + DOOR_Z
        return [da, (SHAFT_X, da[1], da[2]), (SHAFT_X, da[1], zs), (s[0] - RW / 2 - 1.0, da[1], zs)]
    db = door(b, 1)
    xm = (da[0] + db[0]) / 2
    if abs(da[2] - db[2]) < 0.5:
        return [da, db]
    return [da, (xm - 2.0, da[1], da[2]), (xm + 2.0, db[1], db[2]), db]


def seg_normal(p):
    return None


rc_lanes.bind(globals())
hqk_graph.bind(globals())

OV_POINTS = [(X0 - 60.0, CUT, -50.0), (STK["dispatch_x"] + 30.0, CUT, -50.0), (X0 - 60.0, CUT, 90.0),
             (STK["dispatch_x"] + 30.0, CUT, 90.0)]


def CAM_RULE(walked, mt, CR):
    """The side view (V3 dollhouse): straight at the section (yaw 0), nearly level, framing the three operatives and
    their options; each step it slides along the street with them."""
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
    o = CR.overview(WALK_DEC)
    sw = CR.decision(WALK_SWITCH)
    return {
        "OA_1_midrun": (o, dict(walked=WALK_DEC)),
        "OA_2_switch": (sw, dict(walked=WALK_SWITCH, extra=dict(pulse=1.0, switch_moment=1))),
        "OA_3_showdown": (sw, dict(walked=WALK_SHOW, extra=dict(pulse=0.3, showdown=1))),
    }


def RED_SHOTS(CR):
    """The red sequence (round 34 blackout + the review), over the whole district (HQ_DISTRICT_ONLY build)."""
    top = CR.Pose((0.0, 110.0, 0.0), 0.0, 74.0, 700.0, 30.0, -0.04, 0.0)
    w = ["start"]
    return {
        "RS_1_before": (top, dict(walked=w, extra=dict(seq=0.0, ui_off=1))),
        "RS_2_blackout": (top, dict(walked=w, extra=dict(seq=1.0, ui_off=1))),
        "RS_3_spreading": (top, dict(walked=w, extra=dict(seq=1.45, ui_off=1))),
        "RS_4_full": (top, dict(walked=w, extra=dict(seq=3.0, ui_off=1))),
    }


def RED_SEQ_FRAMES(CR, n=36):
    top = CR.Pose((0.0, 110.0, 0.0), 0.0, 74.0, 700.0, 30.0, -0.04, 0.0)
    return {"q%03d" % k: (top, dict(walked=["start"], extra=dict(seq=3.0 * k / (n - 1), ui_off=1))) for k in range(n)}


def SHEET_SHOTS(CR):
    return {}


REVEAL_T = 6.5


def REVEAL(CR):
    """The HQ beat = the red sequence in motion (render with HQ_DISTRICT_ONLY=1: the whole district): from above, an
    ordinary district (the fist barely hinted, 0-1 s); it washes out, then the ring and the hand's lines go dark (the
    BLACKOUT, 1-2.4 s); the red spreads from the palm through the fist (2.4-5 s); the full fist, the camera settling
    lower toward the south edge (5-6.5 s). No route / UI (the section's netrun follows)."""
    w = ["start"]
    top = CR.Pose((0.0, 110.0, 0.0), 0.0, 74.0, 700.0, 30.0, -0.04, 0.0)
    end = CR.Pose((0.0, 110.0, 0.0), 0.0, 58.0, 640.0, 30.0, -0.04, 0.02)
    n = int(REVEAL_T * CR.FPS)
    out = []
    for k in range(n):
        t = k / CR.FPS
        if t < 1.0:
            seq = 0.0
        elif t < 2.4:
            seq = (t - 1.0) / 1.4
        elif t < 5.0:
            seq = 1.0 + 2.0 * CR.ease((t - 2.4) / 2.6)
        else:
            seq = 3.0
        p = top.mix(end, CR.ease((t - 3.0) / 3.5))
        out.append((t, p, w, 0, dict(ui=0.0, route=0.0, seq=seq, ui_off=1)))
    return out
