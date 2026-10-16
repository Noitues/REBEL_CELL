"""HQ Meridian: the container fortress layout and the run graph (pure python).

THE RAMPART RULE (proposal; numbers in hq_preset.PRESET["hq"]["compound"]):
  The fortress is a rectangle of container walls (outer faces |x| = 80, |y| = 60, 3 courses of 9 BU), square corner
  towers of 5 crossed courses, a moat on three sides and the rail yard on the fourth (north). The gatehouse and its
  drawbridge sit on the WEST wall; MANIFEST CONTROL (the server tower) stands in the yard.
  rooms           cutaway containers in the OUTER face of the wall: the route walks the rampart, west wall (north-
                  bound, climbing one course every room or two), round the NW tower, along the north wall (east-bound,
                  over the track), round the NE tower, over the SKYWAY into the yard and up MANIFEST CONTROL's face
  same wall       a steel facade catwalk at sill height, ladders where the course changes
  corner          an exterior stair round the corner tower
  the server      THE MASTER MANIFEST: the open vault on MANIFEST CONTROL's roof (round 35 / GDD 11.7)
THE YARD CYCLE (round 43's crane / train cycle, adapted to the rampart: a PROPOSAL; preset "mech"):
  a 6-step cycle, idx = (step + phase) mod 6. The movers carry ROOMS (round 43: "nodes ride the crane and the train"):
  CAR   a container room on the freight train's flatcar. arrive / WEST (beside n1) / EAST (shunted, beside the NE
        tower) / east / leave / gone. Board from n1 when the car is WEST; step off to t2 when it is EAST. Still aboard
        when it leaves: ejected at the gate, Heat +1 (round 43 open question; proposal).
  HOOK  a container room on the gantry crane's hook. yard / swing / WALL (beside n3, over the track) / wall / YARD
        (beside MANIFEST CONTROL, at m2's level) / yard. Board from n3 when it is at the WALL; step off to m2 when it
        is in the YARD.
  At most `max_shortcuts` rides per run (proposal: 1). A ride skips 3 rooms (the train: n2-n4; the hook: n4-m1).
  Every mover move re-makes the links it touches (bible 4.7 link grammar); the next move is telegraphed (the dial).
Graph API: hqk_graph (bind). Ties by path order.
"""
import math
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
WX, WY = CP["wall"]["x"], CP["wall"]["y"]
TC, THALF = CP["tower"]["c"], CP["tower"]["half"]
CTL = CP["control"]
CYCLE = MECH["cycle"]
SHORTCUT_TYPES = ("board_train", "board_crane")

FACES = {"W": ((-1.0, 0.0), lambda u: (-WX, u)), "N": ((0.0, 1.0), lambda u: (u, WY)),
         "tw": ((0.0, 1.0), lambda u: (-TC[0] + u, TC[1] + THALF)), "te": ((0.0, 1.0), lambda u: (TC[0] + u, TC[1] + THALF)),
         "ctl": ((0.0, 1.0), lambda u: (CTL["c"][0] + u, CTL["c"][1] + CTL["half"]))}

NODES = ["start"] + [r[0] for r in CP["rooms"]] + ["car", "hook", "srv"]
ROOM = {}
WALL_OF = {}
for (nid, wall, u, c) in CP["rooms"]:
    n, f = FACES[wall]
    x, y = f(u)
    z0 = c if wall == "ctl" else c * CRS + SLAB
    ROOM[nid] = dict(o=(x, y, z0), n=n, w=RW, h=RH, d=RD)
    WALL_OF[nid] = wall
SX, SY = CP["start"]
ROOM["start"] = dict(o=(SX, SY - 4.0, 0.4), n=(0.0, -1.0), w=8.0, h=4.6, d=6.0)
VZ0 = CTL["h"] - CP["target_h"]
ROOM["srv"] = dict(o=(CTL["c"][0], CTL["c"][1] + CTL["half"] - 4.0, VZ0), n=None, w=CP["target_w"], h=CP["target_h"],
                   d=CP["target_w"] - 6.0)
CAR_Y, CAR_Z = CP["track_y"][0] + RD / 2.0, 2.6
HOOK_WALL = (CP["crane"]["x"], WY + 5.0 + RD, 2 * CRS + SLAB)              # over the track, by n3
HOOK_YARD = (CP["crane"]["x"], CTL["c"][1] + CTL["half"] + 1.0 + RD, ROOM["m2"]["o"][2])   # beside MANIFEST CONTROL
HOOK_TOP = 52.0                                                             # the lift height over the wall

KIND = {"start": "start", "srv": "target"}
KIND.update(CP["kinds"])
LAYER = {n: i for i, n in enumerate(["start", "w1", "w2", "w3", "w4", "t1", "n1", "n2", "n3", "n4", "t2", "m1", "m2", "srv"])}
LAYER.update(car=LAYER["n2"], hook=LAYER["n4"])
WORD = {"start": "GATE", "router": "FIGHT", "elite": "ELITE", "terminal": "EVENT", "modem": "SHOP", "rack": "RACK",
        "target": "THE MASTER MANIFEST"}
FILE = {
    "router": ("T4", "Fight: a yard security post", ["20-30 Cycles, a card", "maybe a Firmware chip"]),
    "elite": ("T4", "Elite fight (a loader rig)", ["40-50 Cycles, a rare card", "a Firmware chip"]),
    "terminal": ("T4", "Event: a manifest terminal", ["a choice: card, Cycles", "or HP"]),
    "modem": ("T4", "Shop: spend Cycles", ["cards, Firmware, a heal"]),
    "rack": ("T4", "Rack: elite, then banks", ["banks your Schematics", "+3 Heat"]),
    "target": ("T4", "Central Server: the boss", ["the campaign", ""]),
}
HP_ARRIVE = "41 / 60"
PATH = [("start", "w1"), ("w1", "w2"), ("w2", "w3"), ("w3", "w4"), ("w4", "t1"), ("t1", "n1"), ("n1", "n2"),
        ("n2", "n3"), ("n3", "n4"), ("n4", "t2"), ("t2", "m1"), ("m1", "m2"), ("m2", "srv")]
RIDES = [("n1", "car", "train", "west"), ("car", "t2", "train", "east"), ("n3", "hook", "crane", "wall"),
         ("hook", "m2", "crane", "yard")]

# the run states shown
WALK_DEC = ["start", "w1", "w2", "w3", "w4", "t1", "n1"]       # step 6: the train is IN (west), the crane swings
HOVER_DEC = "car"
WALK_MID = WALK_DEC


# ------------------------------------------------------------------ the cycle
def idx(mt):
    return (int(math.floor(mt + 1e-6)) + MECH["phase"]) % CYCLE


def train_at(mt):
    return MECH["train"][idx(mt)]


def crane_at(mt):
    return MECH["crane"][idx(mt)]


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def car_x(mt):
    """The car's x (continuous: the train moves during the second half of a step into the next state)."""
    a = MECH["train_x"][train_at(mt)]
    b = MECH["train_x"][train_at(mt + 1)]
    f = mt - math.floor(mt + 1e-6)
    return a + (b - a) * _smooth((f - 0.35) / 0.65)


def hook_xyz(mt):
    """The hook container's opening centre: wall / yard, and a lift-trolley-lower path between them."""
    def pos(state):
        return {"wall": HOOK_WALL, "yard": HOOK_YARD, "swing": (HOOK_WALL[0], (HOOK_WALL[1] + HOOK_YARD[1]) / 2, HOOK_TOP)}[state]
    a, b = pos(crane_at(mt)), pos(crane_at(mt + 1))
    f = _smooth(((mt - math.floor(mt + 1e-6)) - 0.3) / 0.7)
    if a == b:
        return a
    # lift to HOOK_TOP, trolley, lower (three thirds)
    if f < 1 / 3:
        k = _smooth(f * 3)
        return (a[0], a[1], a[2] + (HOOK_TOP - a[2]) * k)
    if f < 2 / 3:
        k = _smooth(f * 3 - 1)
        return (a[0], a[1] + (b[1] - a[1]) * k, HOOK_TOP)
    k = _smooth(f * 3 - 2)
    return (b[0], b[1], HOOK_TOP + (b[2] - HOOK_TOP) * k)


def room_rec_corp(i, mt):
    if mt is None:
        mt = len(WALK_MID) - 1
    if i == "car":
        return dict(o=(car_x(mt), CAR_Y, CAR_Z), n=(0.0, 1.0), w=RW, h=RH, d=RD)
    if i == "hook":
        return dict(o=hook_xyz(mt), n=(0.0, 1.0), w=RW, h=RH, d=RD)
    return None


def rides_used(walked):
    return sum(1 for n in walked if n in ("car", "hook"))


def base_edges(walked, mt):
    out = list(PATH)
    for a, b, mover, state in RIDES:
        now = train_at(mt) if mover == "train" else crane_at(mt)
        if now != state:
            continue
        if a in ("car", "hook") or rides_used(walked) < CP["max_shortcuts"]:
            out.append((a, b))
        elif a not in ("car", "hook") and (a, b) in zip(walked[:-1], walked[1:]):
            out.append((a, b))
    return out


def edge_type(a, b):
    if a == "start":
        return "ramp"
    if b == "car":
        return "board_train"
    if b == "hook":
        return "board_crane"
    if a in ("car", "hook"):
        return "step_off"
    if b == "srv":
        return "lift"
    if (a, b) == ("t2", "m1"):
        return "skyway"
    if WALL_OF.get(a) == WALL_OF.get(b):
        return "catwalk"
    return "corner"


def _t(n):
    return (n[1], -n[0])


def door(i, side, mt=None):
    r = room_rec(i, mt)  # noqa: F821  (bound)
    n = r["n"] or (0.0, 1.0)
    t = _t(n)
    x, y, z0 = r["o"]
    return (x + n[0] * YF + t[0] * side * r["w"] / 2, y + n[1] * YF + t[1] * side * r["w"] / 2, z0 + DOOR_Z)


def fpt(i, du, z=None, mt=None, dn=YF):
    """A point on room i's facade frame: du along the tangent from the opening's centre, dn out, at height z."""
    r = room_rec(i, mt)  # noqa: F821
    n = r["n"] or (0.0, 1.0)
    t = _t(n)
    x, y, z0 = r["o"]
    return (x + n[0] * dn + t[0] * du, y + n[1] * dn + t[1] * du, z0 + DOOR_Z if z is None else z)


def edge_path(a, b, mt=None):
    t = edge_type(a, b)
    if t == "ramp":
        d = door(b, -1)
        gy = CP["gate_u"]
        return [(SX + 4.0, SY, 1.2), (-WX - CP["moat"]["w"] - 4.0, gy, 1.2), (-WX - YF, gy, d[2]), d]
    if t == "catwalk":
        da, db = door(a, 1), door(b, -1)
        ra, rb = ROOM[a], ROOM[b]
        if abs(da[2] - db[2]) < 0.5:
            return [da, db]
        m = tuple((da[k] + db[k]) / 2 for k in range(2))
        return [da, (m[0], m[1], da[2]), (m[0], m[1], db[2]), db]
    if (a, b) == ("w4", "t1"):
        da, db = door(a, 1), door(b, -1)
        tx0 = -TC[0] - THALF - YF
        ty0 = TC[1] - THALF - 3.0
        return [da, (da[0], ty0, da[2]), (tx0, ty0, da[2]), (tx0, TC[1] + THALF + YF, db[2]), db]
    if (a, b) == ("t1", "n1"):
        da, db = door(a, 1), door(b, -1)
        x = -TC[0] + THALF + 1.5
        return [da, (x, da[1], da[2]), (x, db[1], db[2]), db]
    if (a, b) == ("n4", "t2"):
        da, db = door(a, 1), door(b, -1)
        x = TC[0] - THALF - 1.5
        return [da, (x, da[1], da[2]), (x, db[1], db[2]), db]
    if t == "skyway":
        da, db = door(a, -1), door(b, 1)
        x = TC[0] - THALF - 4.0
        return [da, (x, da[1], da[2] + 1.0), (x, db[1] + 7.0, db[2]), (db[0] + 1.5, db[1] + 7.0, db[2]), db]
    if (a, b) == ("m1", "m2"):
        da, db = door(a, -1), door(b, 1)
        x = (da[0] + db[0]) / 2
        return [da, (x, da[1], da[2]), (x, db[1], db[2]), db]
    if t == "lift":
        da = door(a, -1)
        s = ROOM["srv"]["o"]
        x = da[0] - 1.5
        return [da, (x, da[1], da[2]), (x, da[1], s[2] + DOOR_Z), (s[0] - 6.0, da[1], s[2] + DOOR_Z)]
    if b == "car":
        da, db = door(a, -1), door(b, -1, mt)
        x = da[0] - 2.5
        return [da, (x, da[1], da[2]), (x, da[1] + 3.0, 1.4), (x, db[1], 1.4), db]
    if a == "car":
        da, db = door(a, 1, mt), door(b, 1)
        x = TC[0] + THALF - 1.0
        return [da, (da[0] + 2.0, da[1], 1.4), (x, da[1], 1.4), (x, db[1], 1.4), (x, db[1], db[2]), db]
    if b == "hook":
        da, db = door(a, 1), door(b, -1, mt)
        x = db[0] - 1.0
        return [da, (x, da[1], da[2]), (x, da[1], db[2]), (x, db[1], db[2]), db]
    if a == "hook":
        da, db = door(a, 1, mt), door(b, -1)
        return [da, (db[0] - 0.5, da[1], da[2]), db]
    da, db = door(a, 1), door(b, -1)
    return [da, db]


def seg_normal(p):
    """The facade side a link point sits on (hidden when that side faces away)."""
    if p[0] < -WX - 0.2 and p[1] < TC[1] + THALF - 1:
        return (-1.0, 0.0)
    return (0.0, 1.0)


def mech(walked, mt=None):
    mt = len(walked) - 1 if mt is None else mt
    i = idx(mt)
    nxt = idx(mt + 1)
    leave_in = None
    for k in range(1, CYCLE + 1):
        if MECH["train"][(i + k) % CYCLE] == "leave":
            leave_in = k
            break
    st, _ = states(walked, mt)  # noqa: F821
    affected = [n for n in ("car", "hook") if st.get(n) in ("option", "reach", "current")]
    return dict(idx=i, idx_next=nxt, train=MECH["train"][i], train_next=MECH["train"][nxt], crane=MECH["crane"][i],
                crane_next=MECH["crane"][nxt], leave_in=leave_in, affected=affected, rides=rides_used(walked))


hqk_graph.bind(globals())


if __name__ == "__main__":
    for s in range(14):
        print("step", s, "idx", idx(s), "train", train_at(s), "x %.0f" % car_x(s), "crane", crane_at(s),
              "hook", tuple(round(v, 1) for v in hook_xyz(s)))
    st, opts = states(WALK_DEC)
    print("DECISION at", WALK_DEC[-1], "options", opts, mech(WALK_DEC))
    print("states", st)
    print("branch car", sorted(branch("car", WALK_DEC)[0]), "branch n2", sorted(branch("n2", WALK_DEC)[0]))
    # play both lines out to the server
    for first in ("car", "n2"):
        w = list(WALK_DEC) + [first]
        while w[-1] != "srv":
            o = succ(w[-1], w)
            if not o:
                print("  stuck at", w[-1], "step", len(w) - 1)
                break
            pick = "hook" if "hook" in o else o[0]
            w.append(pick)
        print("line", first, "->", w[len(WALK_DEC):], "server at step", len(w) - 1)


# ------------------------------------------------------------------ framing data for the rig
_tz = CP["tower"]["courses"] * CRS
OV_POINTS = [(sx * (TC[0] + THALF), sy * (TC[1] + THALF), z) for sx in (-1, 1) for sy in (-1, 1) for z in (0.0, _tz)]
OV_POINTS += [(CTL["c"][0], CTL["c"][1], CTL["h"] + 12.0), (CP["crane"]["x"], CP["crane"]["legs_y"][1], CP["crane"]["z"]),
              (SX - 6, SY, 0.0), (-60.0, CP["track_y"][1] + 6.0, 0.0), (90.0, CP["track_y"][1] + 6.0, 0.0)]


def STILLS(CR):
    w = WALK_DEC
    return {
        "H_overview": (CR.overview(w), dict(walked=w)),
        "H_decision": (CR.decision(w), dict(walked=w)),
        "H_hover": (CR.hover(w, HOVER_DEC), dict(walked=w, hover=HOVER_DEC, hover_k=1.0)),
    }


def MOVER_POS(mt, walked=None):
    h = hook_xyz(mt)
    c = room_rec("car", mt)["o"]
    return {"train": c, "hook": h, "trolley": (CP["crane"]["x"], h[1] - RD / 2, CP["crane"]["z"])}


def SHEET_SHOTS(CR):
    a = WALK_DEC + ["car"]
    b = WALK_DEC + ["n2", "n3"]
    c = WALK_DEC + ["n2", "n3", "hook"]
    return {
        "S_on_the_train": (CR.decision(a), dict(walked=a)),
        "S_hook_at_wall": (CR.decision(b), dict(walked=b)),
        "S_hook_in_yard": (CR.decision(c), dict(walked=c)),
    }


REVEAL_T = 6.5


def REVEAL(CR):
    """The HQ beat: a rail dolly beside the arriving freight train (low, west of the fortress, tracking the car), then
    a crane-up past the gantry while the hook lifts out of the yard, into the OVERVIEW; route and UI draw in last."""
    w = ["start"]
    o = CR.overview(WALK_DEC)
    n = int(REVEAL_T * CR.FPS)
    out = []
    for k in range(n):
        t = k / CR.FPS
        a = CR.ease_out(min(1.0, t / 3.0))
        mt = 5.35 + 0.65 * a                       # the train runs in and stops at n1; the hook lifts from the yard
        cx = car_x(mt)
        track = CR.Pose((max(cx + 22.0, -190.0), CP["track_y"][0] - 6.0, 7.0), 128.0, 6.0, 62.0, 24.0, 0.0, 0.02)   # the camera stays inside the perimeter belt
        e = CR.ease((t - 2.2) / 3.6)
        p = track.mix(o, e)
        p.F = tuple(CR.lerp(a_, b_, CR.ease((t - 2.0) / 3.6)) for a_, b_ in zip(track.F, o.F))
        # the crane-up: an extra rise mid-way so the camera passes the gantry's girders
        p.pitch = CR.lerp(track.pitch, o.pitch, e) + 10.0 * (4 * e * (1 - e)) * 0.0
        ui = CR.ease((t - 5.4) / 0.9)
        out.append((t, p, w, mt, dict(ui=ui, route=ui)))
    return out
