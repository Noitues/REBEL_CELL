"""HQ Orbital: the launch complex, one CIRCUIT of the retarget cycle, and the run graph (pure python).
Revised 2026-10-15 after the designer's review (v1 with the door crossing archived in D:/rc_scratch/hq_orbital/v1).

THE RING RULE (round 43 Orbital + the review; numbers in hq_preset "compound"):
  A round launch podium with the rocket silo at its centre (two door leaves), a ring of stations round it (openings
  facing out): the PAD (start), SE dish, NE dish, the ANTENNA TOWER (a truss tower with decks; two enclosed ELITE rooms,
  the dangerous part of every circuit), NW dish, SW dish; then the ROCKET (the circuit's sabotage at the silo rim).
  LAUNCH CONTROL is the deck on the service gantry by the silo (the TARGET).
THE RETARGET CYCLE (the review's sabotage story on round 43's missile loop; a PROPOSAL, not in the GDD):
  a circuit = PAD > SE > NE > ANT 1 > ANT 2 > NW > SW > ROCKET. The bay doors stay SHUT during the circuit; at its end
  they OPEN, the rocket rises, and the Cell RETARGETS it (RETARGET n/3): it launches and strikes an Orbital facility in
  the city or in orbit (the launch cutscene, H_launch_board). After 3 retargets the antenna's top room unlocks the
  LAUNCH OVERRIDE: a shortcut to LAUNCH CONTROL that fires the rocket one round early into the SHUT doors: the HQ is
  destroyed and the run is won (the planned HQ-explosion cutscene).
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
RR = CP["ring_r"]
AN = CP["antenna"]
YF = 0.7
DOOR_Z = 1.6
CYCLE = 1
SHORTCUT_TYPES = ("override",)
GROUND_Z = 0.4
PH = CP["podium_h"]
SR = CP["silo_r"]


def az_vec(a):
    r = math.radians(a)
    return (math.sin(r), math.cos(r))


STATION, NAME = {}, {}
for (nid, a, nm) in CP["stations"]:
    STATION[nid], NAME[nid] = a, nm
NODES = ["start", "se", "ne", "ant1", "ant2", "nw", "sw", "rocket", "srv"]
NAME.update(ant1="ANTENNA DECK 1", ant2="ANTENNA DECK 2", rocket="THE ROCKET", srv="LAUNCH CONTROL")
ROOM = {}
for nid, a in STATION.items():
    n = az_vec(a)
    ROOM[nid] = dict(o=(n[0] * (RR + RD), n[1] * (RR + RD), GROUND_Z), n=n, w=RW, h=RH, d=RD)
_av = az_vec(AN["az"])
for (nid, z) in AN["rooms"]:
    ROOM[nid] = dict(o=(_av[0] * (AN["r"] + AN["half"]), _av[1] * (AN["r"] + AN["half"]), z + 0.6), n=_av, w=RW,
                     h=RH, d=RD)
_vr = az_vec(205.0)
ROOM["rocket"] = dict(o=(_vr[0] * (SR + 7.0), _vr[1] * (SR + 7.0), PH + 0.4), n=None, w=12.0, h=12.0, d=12.0)
ROOM["srv"] = dict(o=(0.0, CP["control"]["y"], PH + 18.0), n=None, w=16.0, h=8.0, d=10.0)
KIND = {"start": "start", "srv": "target"}
KIND.update(CP["kinds"])
LAYER = {n: k for k, n in enumerate(NODES)}
LAYER["srv"] = LAYER["nw"]
WORD = {"start": "THE PAD", "router": "FIGHT", "elite": "ELITE", "terminal": "EVENT", "modem": "SHOP",
        "rack": "SABOTAGE", "target": "LAUNCH CONTROL"}
FILE = {
    "router": ("T4", "Fight: a launch crew", ["20-30 Cycles, a card", "maybe a Firmware chip"]),
    "elite": ("T4", "Elite: the antenna's guard", ["40-50 Cycles, a rare card", "a Firmware chip"]),
    "terminal": ("T4", "Event: the uplink terminal", ["a choice: card, Cycles", "or HP"]),
    "modem": ("T4", "Shop: spend Cycles", ["cards, Firmware, a heal"]),
    "rack": ("T4", "Sabotage: retarget the rocket", ["it strikes Orbital, not the city", "RETARGET +1"]),
    "target": ("T4", "LAUNCH OVERRIDE: fire it early", ["into the shut doors:", "the HQ is destroyed"]),
}
HP_ARRIVE = "41 / 60"
RING = ["start", "se", "ne", "ant1", "ant2", "nw", "sw", "rocket"]
PATH = list(zip(RING, RING[1:]))

WALK_DEC = ["start", "se", "ne", "ant1", "ant2"]     # circuit 4, on the antenna's top room: the override is open
HOVER_DEC = "srv"
WALK_MID = WALK_DEC
WALK_ROCKET = ["start", "se", "ne", "ant1", "ant2", "nw", "sw"]
CIRCUIT = {"c": MECH["circuit"]}
SHOT = {}                                           # the shot's extra (door_k, rocket_k, bands overrides)                    # the circuit a shot shows (jobs set it per frame via extra)


def circuit_of(walked):
    return CIRCUIT["c"]


def override_open(walked):
    return circuit_of(walked) > MECH["retargets"]


def base_edges(walked, mt):
    out = list(PATH)
    if override_open(walked):
        out.append(("ant2", "srv"))
    return out


def edge_type(a, b):
    if b == "srv":
        return "override"
    if b == "rocket":
        return "sabotage"
    if b == "ant1":
        return "up_tower"
    if a == "ant1":
        return "tower"
    if a == "ant2":
        return "down_tower"
    return "causeway"


RL = RR + RD + YF


def door(i, side, mt=None):
    r = ROOM[i]
    n = r["n"] or (0.0, 1.0)
    t = (n[1], -n[0])
    x, y, z0 = r["o"]
    return (x + n[0] * YF + t[0] * side * r["w"] / 2, y + n[1] * YF + t[1] * side * r["w"] / 2, z0 + DOOR_Z)


def _arc(a0, a1, rad, z, step=5.0):
    n = max(2, int(abs(a1 - a0) / step))
    return [(az_vec(a0 + (a1 - a0) * k / n)[0] * rad, az_vec(a0 + (a1 - a0) * k / n)[1] * rad, z) for k in range(n + 1)]


def _ang(p):
    return math.degrees(math.atan2(p[0], p[1]))


ZP = PH + 0.4 + DOOR_Z
AX, AY = _av[0] * AN["r"], _av[1] * AN["r"]


def edge_path(a, b, mt=None):
    t = edge_type(a, b)
    if t == "causeway":
        da, db = door(a, -1), door(b, 1)
        a0, a1 = _ang(da), _ang(db)
        while a1 > a0:
            a1 -= 360
        return [da] + _arc(a0, a1, RL, da[2])[1:-1] + [db]
    if t == "up_tower":                               # round the ring to the tower foot, up the outer stair
        da, db = door(a, -1), door(b, 1)
        a0 = _ang(da)
        a1 = AN["az"] + 9.0
        while a1 > a0:
            a1 -= 360
        foot = _arc(a0, a1, RL, da[2])
        x, y = db[0], db[1]
        return [da] + foot[1:] + [(x + 3.0, y, da[2]), (x + 3.0, y, db[2]), db]
    if t == "tower":
        da, db = door(a, -1), door(b, 1)
        return [da, (da[0] - 2.5, da[1], da[2]), (db[0] + 2.5, db[1], db[2]), db]
    if t == "down_tower":                             # down the west stair to the ground, round the ring to NW
        da, db = door(a, -1), door(b, 1)
        a1 = _ang(db)
        a0 = AN["az"] - 9.0
        while a1 > a0:
            a1 -= 360
        return ([da, (da[0] - 3.0, da[1], da[2]), (da[0] - 3.0, da[1], GROUND_Z + DOOR_Z)]
                + _arc(a0, a1, RL, GROUND_Z + DOOR_Z)[1:-1] + [db])
    if t == "sabotage":
        da = door(a, -1)
        v = az_vec(215.0)
        pr = CP["podium_r"]
        o = ROOM["rocket"]["o"]
        return [da, (v[0] * (RR - 4), v[1] * (RR - 4), da[2]), (v[0] * (pr + 2), v[1] * (pr + 2), ZP), (o[0], o[1], ZP)]
    # the override: from the antenna's top room down the uplink to LAUNCH CONTROL (the TARGET path)
    da = door(a, 1)
    s = ROOM["srv"]["o"]
    return [da, (da[0] * 0.55, da[1] * 0.55, da[2] - 6.0), (s[0], s[1] + 10.0, s[2] + DOOR_Z + 4.0), (s[0], s[1], s[2] + DOOR_Z)]


def seg_normal(p):
    r = math.hypot(p[0], p[1])
    if r < CP["podium_r"] + 4 or p[2] > 20.0:
        return None
    return (p[0] / r, p[1] / r)


def mech(walked, mt=None):
    c = circuit_of(walked)
    at_rocket = walked[-1] in ("sw", "rocket")
    done = min(c - 1, MECH["retargets"])
    e = SHOT
    bands = e.get("bands", done + (1 if at_rocket else 0))
    return dict(circuit=c, retarget=done, retargets=MECH["retargets"], doors="open" if at_rocket else "shut", bands=bands,
                override=override_open(walked), affected=["srv"] if override_open(walked) else [], walked=list(walked))


hqk_graph.bind(globals())

OV_POINTS = [(az_vec(a)[0] * (RR + RD + 8), az_vec(a)[1] * (RR + RD + 8), z) for a in range(0, 360, 30) for z in (0.0, 20.0)]
OV_POINTS += [(AX, AY, AN["h"] + 4.0)]


def rocket_state(walked, extra=None):
    """(door_k, rocket_k, hacked bands): the doors and the rocket by the circuit's position (extra overrides)."""
    e = extra or {}
    open_ = walked[-1] in ("sw", "rocket")
    dk = e.get("door_k", 1.0 if open_ else 0.0)
    rk = e.get("rocket_k", 1.0 if open_ else 0.0)
    m = mech(walked)
    bands = e.get("bands", m["retarget"] + (1 if open_ else 0))
    return dk, rk, bands


def mover_from(door_k, rocket_k):
    return {"door_e": (door_k * (SR + 1.0), 0.0, 0.0), "door_w": (-door_k * (SR + 1.0), 0.0, 0.0),
            "rocket": (0.0, 0.0, -CP["rocket"]["raise"] + CP["rocket"]["raise"] * rocket_k)}


def MOVER_POS(mt, walked=None):
    dk, rk, _ = rocket_state(walked or WALK_MID, SHOT)
    return mover_from(dk, rk)


def CAM_RULE(walked, mt, CR):
    """Front and centre on the ACTIVE room (designer review): the camera stands off the current room's normal (it
    orbits the complex as the circuit advances), the current room in the middle of the usable frame, the options in
    view (the framing solver pulls back until they fit)."""
    st, opts = states(walked, mt)
    cur = walked[-1]
    ids = [cur] + opts
    pts = []
    for i in ids:
        pts += room_corners(i, mt)
    n = ROOM[cur]["n"] or (0.0, -1.0)
    yaw = CR.yaw_of((-n[0], -n[1]))
    b = CR.beat(walked)
    c = room_center(cur, mt)
    p = CR.frame_points(pts, yaw, b["pitch"], b["lens"], CR.FILL_W, CR.FILL_H, centre=c, dmin=CR.DMIN)
    q = p.proj(c, shift=False)
    p.sx = (q[0] - CR.UCX) / CR.W
    p.sy = (CR.UCY - q[1]) / CR.W
    return p


def ROCKET_POSE(CR):
    """The hero view of the rocket at a circuit's sabotage: low from the south-west, the rocket risen out of the open
    doors, the gantry and LAUNCH CONTROL beside it."""
    return CR.Pose((0.0, 0.0, PH + 30.0), 32.0, 4.0, 150.0, 26.0, -0.02, 0.02)


def STILLS(CR):
    w = WALK_DEC
    wr = WALK_ROCKET
    return {
        "H_overview": (CR.overview(wr), dict(walked=wr, extra=dict(circuit=2))),   # v2: the rocket up, doors OPEN
        "H_decision": (CR.decision(w), dict(walked=w, extra=dict(circuit=4))),
        "H_hover": (CR.hover(w, HOVER_DEC), dict(walked=w, hover=HOVER_DEC, hover_k=1.0, extra=dict(circuit=4))),
        "H_rocket": (ROCKET_POSE(CR), dict(walked=wr, extra=dict(circuit=2, rocket_view=1))),
    }


def SHEET_SHOTS(CR):
    a = ["start", "se"]
    b = ["start", "se", "ne", "ant1"]
    c = WALK_ROCKET
    return {"S_ring": (CR.decision(a), dict(walked=a, extra=dict(circuit=2))),
            "S_antenna": (CR.decision(b), dict(walked=b, extra=dict(circuit=2))),
            "S_sabotage": (CR.decision(c), dict(walked=c, extra=dict(circuit=2)))}


REVEAL_T = 6.5


def REVEAL(CR):
    """The HQ beat: inside the open silo looking up the rocket, the camera rises out of the shaft past its nose while
    the rocket sinks and the doors close under it, then pulls back to the OVERVIEW; route and UI draw in last."""
    w = ["start"]
    o = CR.overview(WALK_DEC)
    n = int(REVEAL_T * CR.FPS)
    out = []
    for k in range(n):
        t = k / CR.FPS
        a = CR.ease(t / 2.2)
        up = CR.Pose((0.0, 0.0, PH + 40.0 + 50.0 * a), o.yaw + 140.0 - 40.0 * a, -84.0 + 70.0 * a, 30.0 + 40.0 * a, 22.0,
                     0.0, 0.0)
        e = CR.ease((t - 1.6) / 3.8)
        p = up.mix(o, e)
        p.yaw = CR.lerp(up.yaw, o.yaw, e)
        door_k = 1.0 - CR.ease((t - 1.6) / 2.4)
        rk = 1.0 - CR.ease((t - 1.0) / 2.6)
        ui = CR.ease((t - 5.5) / 0.9)
        out.append((t, p, w, 0, dict(ui=ui, route=ui, movers=mover_from(door_k, rk), shaft=max(door_k, 0.1), bands=1,
                                      circuit=1)))
    return out


if __name__ == "__main__":
    for w in (WALK_DEC, WALK_ROCKET):
        st, opts = states(w)
        print(w[-1], "options", opts, mech(w))


def set_shot(extra):
    """Per-shot state the kit sets before computing states (jobs, overlay): the circuit shown."""
    CIRCUIT["c"] = (extra or {}).get("circuit", MECH["circuit"])
    SHOT.clear()
    SHOT.update(extra or {})


def strike_arc(n=80):
    """The rocket's arc from the open silo to the struck Orbital facility in the city (a parabola, apex preset)."""
    sx, sy = HP.PRESET["hq"]["light"]["strike"]["at"]
    apex = HP.PRESET["hq"]["light"]["strike"]["apex"]
    z0, z1 = PH + CP["rocket"]["h"] + 20.0, 56.0
    out = []
    for k in range(n + 1):
        t = k / n
        z = z0 + (z1 - z0) * t + 4.0 * apex * t * (1 - t)
        out.append((sx * t, sy * t, z))
    return out


def strike_pos(t):
    """Position (and the heading) of the rocket in flight at arc parameter t."""
    a = strike_arc(200)
    k = max(0, min(199, int(t * 200)))
    p, q = a[k], a[k + 1]
    return p, (q[0] - p[0], q[1] - p[1], q[2] - p[2])


def LAUNCH_SHOTS(CR):
    """The launch cutscene as storyboard frames (H_launch_board): after a circuit's sabotage the camera pulls out to a
    CITY-WIDE view, the rocket launches, arcs across the city, lands on an Orbital facility and explodes; the camera
    zooms back into the HQ. Each: (name, pose, walked, extra)."""
    sx, sy = HP.PRESET["hq"]["light"]["strike"]["at"]
    w = WALK_ROCKET
    hq = ROCKET_POSE(CR)
    side = math.degrees(math.atan2(sx, sy)) + 90.0       # side-on to the arc, so it reads as an arc
    city = CR.Pose((sx * 0.5, sy * 0.5, 90.0), side, 34.0, 1150.0, 24.0, 0.0, 0.0)
    near = CR.Pose((sx * 0.55, sy * 0.55, 150.0), side, 26.0, 860.0, 24.0, 0.0, 0.0)
    site = CR.Pose((sx, sy, 50.0), 20.0, 14.0, 260.0, 30.0, 0.0, 0.02)

    def fl(t):
        p, h = strike_pos(t)
        return dict(flight=p, boom=(sx, sy, 56.0)), h
    out = []
    base = dict(circuit=2, launch=1, bands=2)
    out.append(("L1_sabotage", hq, w, dict(base, trail=0.0)))
    out.append(("L2_pullout", city, w, dict(base, trail=0.0, door_k=1.0)))
    m, h = fl(0.06)
    out.append(("L3_launch", city, w, dict(base, trail=0.06, in_flight=1, heading=h, movers=m, rocket_k=0.0)))
    m, h = fl(0.5)
    out.append(("L4_arc", near, w, dict(base, trail=0.5, in_flight=1, heading=h, movers=m, rocket_k=0.0)))
    m, h = fl(0.93)
    out.append(("L5_descent", site, w, dict(base, trail=0.93, in_flight=1, heading=h, movers=m, rocket_k=0.0)))
    m, h = fl(1.0)
    out.append(("L6_strike", near, w, dict(base, trail=1.0, boom=1.0, movers=m, rocket_k=0.0)))
    out.append(("L7_zoom_back", CR.overview(WALK_DEC), ["start"], dict(base, trail=1.0, boom=0.5, movers=m, rocket_k=0.0,
                                                                       door_k=0.3)))
    return out
