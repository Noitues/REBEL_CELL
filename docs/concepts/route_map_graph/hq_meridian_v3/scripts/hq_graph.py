"""HQ Meridian v3: THE GATEHOUSE GANTRY (DESIGN.md), pure python: the room SLOTS on the landmark and an ILLUSTRATIVE
run graph for the overview test. No mechanic: v3 is a design pass (the rules belong to the game sessions).

Layout (numbers in hq_preset.PRESET["hq"]["compound"]; north = +y; the lot is |x|, |y| <= 120):
  curtain walls of containers on the W, S and E edges (outer faces on the lot edge, 14 thick, 4 courses); truck
  gatehouses in the middle of each; the high-speed line on the N edge (two tracks at y 100 / 112) passing under the
  two N corner towers (the rail gates); the GANTRY: two crenellated tower-legs riding runways on the E / W wall tops,
  a battlemented span between them, the trolley KEEP riding the span (THE MASTER MANIFEST in its crown).
The run climbs the castle like a siege: a gate, the walls, the corner towers, a branch (outer W wall / the train vs the
E truck lane / the inner E wall), up a leg, across the span, into the keep. Rooms are cut-open slots in containers
(wall courses, a truck's box, a train car's box) or windows in the legs / span; topology here is illustration only.
Graph API: hqk_graph (bind). Ties by path order.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_preset as HP  # noqa: E402
import hqk_graph  # noqa: E402

CP = HP.PRESET["hq"]["compound"]
MECH = HP.PRESET["hq"]["mech"]
RW, RH, RD = CP["room_w"], CP["room_h"], CP["room_d"]
CRS = CP["course"]
SLAB = 1.0
DOOR_Z = 1.6
YF = 0.7
L = CP["lot"]
WT = CP["wall"]["t"]
GY = CP["gantry"]["y"]
LEGX = L - WT / 2                          # the legs ride the wall centre lines
LHX, LHY = CP["gantry"]["leg"]
SZ0, SZ1 = CP["gantry"]["span_z"]
SH = CP["gantry"]["span_half"]
KX = CP["gantry"]["keep_x"]
KTOP = CP["gantry"]["keep_top"]
CH = CP["corner"]["half"]
CYCLE = 1
SHORTCUT_TYPES = ()
S_, N_, W_, E_ = (0.0, -1.0), (0.0, 1.0), (-1.0, 0.0), (1.0, 0.0)


def R(o, n, w=RW, h=RH, d=RD):
    return dict(o=o, n=n, w=w, h=h, d=d)


def course_z(c):
    return c * CRS + SLAB


# v3 t2: the overview looks from the SE, so the wall branch runs up the E outer face (seen) and the bay branch up the
# W bay lane / the W wall's inner face (seen over the wall); everything inside the lot
ROOM = {
    "start": R((CP["start"][0], CP["start"][1], 0.4), S_, 8.0, 4.6, 6.0),
    "gs": R((0.0, -L + 1.6, 20.0), S_, 14.0, 8.0, 10.0),                     # the S gatehouse chamber over the arch
    "s1": R((-56.0, -L, course_z(1)), S_),                                   # S wall, outer face
    "s2": R((56.0, -L, course_z(1)), S_),
    "tw": R((-L + CH, -L, course_z(4)), S_),                                 # the SW corner tower's south face
    "te": R((L - CH, -L, course_z(4)), S_),
    "o1": R((L, -80.0, course_z(1)), E_),                                    # E wall, outer face
    "o2": R((L, 12.0, course_z(2)), E_),
    "tb": R((-CP["lane"]["ew_x"] + 3.0, -62.0, 1.8), E_, 14.0, 7.0, 6.0),    # a truck's box in the W bay lane
    "wi": R((-L + WT, 0.0, course_z(2)), E_),                                # W wall, INNER face (the yard side)
    "r1": R((48.0, CP["rail"]["y"][0] - 3.6, 2.6), S_, 14.0, 6.2, 6.0),      # a cut-open carriage on the inner track
    "le1": R((LEGX, GY - LHY, 46.0), S_, 12.0, 8.0, 10.0),                   # the E leg, lower floor
    "le2": R((LEGX, GY - LHY, 66.0), S_, 12.0, 8.0, 10.0),
    "lw1": R((-LEGX, GY - LHY, 46.0), S_, 12.0, 8.0, 10.0),
    "lw2": R((-LEGX, GY - LHY, 66.0), S_, 12.0, 8.0, 10.0),
    "spe": R((60.0, GY - SH, SZ0 + 3.0), S_, 14.0, 8.0, 10.0),               # the span's gallery, south face
    "spw": R((-90.0, GY - SH, SZ0 + 3.0), S_, 14.0, 8.0, 10.0),
    "srv": R((KX, GY - 1.0, KTOP), None, CP["target_w"], CP["target_h"], CP["target_w"] - 6.0),   # the keep's crown
}
NODES = ["start", "gs", "s1", "s2", "tw", "te", "o1", "tb", "o2", "wi", "r1", "le1", "lw1", "le2", "lw2", "spe",
         "spw", "srv"]
EDGES = [("start", "gs"), ("gs", "s1"), ("gs", "s2"), ("s1", "tw"), ("s2", "te"), ("te", "o1"), ("tw", "tb"),
         ("o1", "o2"), ("tb", "wi"), ("o2", "le1"), ("o2", "r1"), ("wi", "lw1"), ("r1", "le2"), ("le1", "le2"),
         ("lw1", "lw2"), ("le2", "spe"), ("lw2", "spw"), ("spe", "srv"), ("spw", "srv")]
KIND = {"start": "start", "srv": "target", "gs": "router", "s1": "router", "s2": "terminal", "tw": "modem",
        "te": "elite", "o1": "router", "tb": "terminal", "o2": "terminal", "wi": "router", "r1": "rack",
        "le1": "router", "lw1": "router", "le2": "elite", "lw2": "modem", "spe": "router", "spw": "elite"}
SLOT = {"gs": "gatehouse", "s1": "wall_outer", "s2": "wall_outer", "tw": "corner_tower", "te": "corner_tower",
        "o1": "wall_outer", "o2": "wall_outer", "tb": "truck_box", "wi": "wall_inner", "r1": "train_box",
        "le1": "leg", "lw1": "leg", "le2": "leg", "lw2": "leg", "spe": "span", "spw": "span", "srv": "keep_crown"}
LAYER = {}
for n_ in NODES:
    LAYER[n_] = 0 if n_ == "start" else 1 + max(LAYER[a] for a, b in EDGES if b == n_)
WORD = {"start": "GATE", "router": "FIGHT", "elite": "ELITE", "terminal": "EVENT", "modem": "SHOP", "rack": "RACK",
        "target": "THE MASTER MANIFEST"}
FILE = {
    "router": ("T4", "Fight: a yard security post", ["20-30 Cycles, a card", ""]),
    "elite": ("T4", "Elite fight", ["40-50 Cycles, a rare card", ""]),
    "terminal": ("T4", "Event: a container's cargo", ["a choice", ""]),
    "modem": ("T4", "Shop", ["cards, Firmware, a heal", ""]),
    "rack": ("T4", "Rack", ["banks your Schematics", ""]),
    "target": ("T4", "Central Server: the boss", ["the campaign", ""]),
}
HP_ARRIVE = "41 / 60"


def base_edges(walked, mt):
    return list(EDGES)


def edge_type(a, b):
    if a == "start":
        return "ramp"
    if b == "srv":
        return "keep_stair"
    return SLOT.get(a, "") + ">" + SLOT.get(b, "")


def _t(n):
    return (n[1], -n[0])


def door(i, side, mt=None):
    r = ROOM[i]
    n = r["n"] or (0.0, -1.0)
    t = _t(n)
    x, y, z0 = r["o"]
    return (x + n[0] * YF + t[0] * side * r["w"] / 2, y + n[1] * YF + t[1] * side * r["w"] / 2, z0 + DOOR_Z)


def edge_path(a, b, mt=None):
    """Illustrative world polylines: out of a's door, across at a's height, up / down at b, into b's door."""
    ra, rb = ROOM[a], ROOM[b]
    if b == "srv":
        da = door(a, 1)
        s = rb["o"]
        return [da, (da[0], da[1] - 2.0, da[2]), (s[0] + 10.0, da[1] - 2.0, da[2]), (s[0] + 10.0, s[1] - 9.0, s[2] + 2.0),
                (s[0], s[1] - 6.0, s[2] + 2.0)]
    da, db = door(a, 1), door(b, -1)
    na, nb = ra["n"], rb["n"] or (0.0, -1.0)
    pa = (da[0] + na[0] * 3.0, da[1] + na[1] * 3.0, da[2])
    pb = (db[0] + nb[0] * 3.0, db[1] + nb[1] * 3.0, db[2])
    return [da, pa, (pb[0], pb[1], pa[2]), pb, db]


def seg_normal(p):
    return None


def mech(walked, mt=None):
    return dict(affected=[])


hqk_graph.bind(globals())

# v3: the occlusion rule's target volume is the VISIBLE route nodes: ground-level rooms the landmark itself hides from
# the overview (inside the curtain walls) are left out, so they do not drag the cone down to the street and ghost the
# whole foreground (the walls would hide them anyway)
OCC_HIDDEN = ("tb", "r1")
WALK_OV = CP["walk_ov"]
WALK_MID = CP["walk_dec"]
OV_POINTS = [(sx * L, sy * L, 0.0) for sx in (-1, 1) for sy in (-1, 1)]
OV_POINTS += [(sx * LEGX, GY, CP["gantry"]["leg_top"] + 6.0) for sx in (-1, 1)]
OV_POINTS += [(KX, GY, KTOP + CP["gantry"]["lantern"][2] + 18.0)]


def MOVER_POS(mt, walked=None):
    return {}


WALK_DEC = CP["walk_dec"]
HOVER_DEC = "le1"                          # the option from o2 that climbs the E leg


def STILLS(CR):
    return {"H_overview": (CR.overview(WALK_OV), dict(walked=WALK_OV)),
            "H_decision": (CR.decision(WALK_DEC), dict(walked=WALK_DEC)),
            "H_hover": (CR.hover(WALK_DEC, HOVER_DEC), dict(walked=WALK_DEC, hover=HOVER_DEC, hover_k=1.0))}


def SHEET_SHOTS(CR):
    return {}


def REVEAL(CR):
    return []


if __name__ == "__main__":
    st, opts = states(WALK_OV)  # noqa: F821
    print("layers", LAYER)
    print("at", WALK_OV[-1], "options", opts)
