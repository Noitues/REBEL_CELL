"""HQ Meridian v2 (designer review 2026-10-15): the container fortress, the route RINGS the whole compound (360 deg),
the SHUTTLE CONTAINERS (pure python). v1 (the one-wall rampart + train / hook rides) is in git history.

THE RING RULE (proposal; numbers in hq_preset.PRESET["hq"]["compound"]):
  The fortress is a rectangle of container walls (outer faces |x| = 80, |y| = 60, 3 courses of 9 BU), square corner
  towers of 5 crossed courses; the LOOP TRACK runs round the whole fortress outside the walls (the freight train
  stands on it, a ring of flatcars); the FREIGHT PLATFORMS sit outside the track; the moat beyond them; MANIFEST
  CONTROL and the slewing KEEP CRANE stand in the yard.
  The run walks the outer faces of all four walls CLOCKWISE (from above: west wall north, north wall east, east wall
  south, south wall west), up the four corner towers, then over the skyway into MANIFEST CONTROL (THE MASTER
  MANIFEST on its roof). Every wall has one BREACH: a top-course slot the crane empties and refills.
THE SHUTTLES (the designer's container rule; a PROPOSAL; preset "mech"):
  Each breach X has a SHUTTLE container sX. It sits IN THE WALL (the breach is closed) for 2 turns, then the keep crane
  lifts it ONTO THE TRAIN (the flatcar opposite the breach) for 2 turns, and back: a 2-turn rhythm; the crane moves
  every turn (the N / S pair on even turns, the E / W pair on odd turns, each pair a swap: one out, one in).
  Per breach, with P the room before it, N the room after it, Q the freight platform outside it, T the next tower:
    P  -> sX   live only while sX is IN THE WALL (step into the container)
    sX -> N    live only while sX is IN THE WALL (step out on the far side of the breach)
    sX -> Q    the RIDE: live when sX is lifted to the train this turn (you ride it) or already sits on the train
    Q  -> T    always (the platform's stair up the next tower)
    P  -> Xb   the SALLY PORT under the breach, always (the slow way: a fight)  Xb -> N always
  So Q (the platform: a shop or a rack) is INACCESSIBLE unless a container carries you there, and the breach is open
  (dashed) whenever its shuttle is away. Links that a container position switches off are drawn dashed + a padlock;
  they turn solid when the container lands (the bible 4.7 de-power / re-make grammar).
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
TRK = CP["track_off"]                # the loop track's centre line, BU outside the wall faces
PLAT = CP["platform_off"]            # the freight platforms' room opening, BU outside the wall faces
HOLD = MECH["hold"]                  # turns a shuttle stays in one place (2)
CYCLE = 2 * HOLD
SHORTCUT_TYPES = ()
WALLS = ("W", "N", "E", "S")
NRM = {"W": (-1.0, 0.0), "N": (0.0, 1.0), "E": (1.0, 0.0), "S": (0.0, -1.0)}


def wall_pt(wall, u, dn=0.0):
    """A point on a wall's outer face: u along the wall in the run direction (clockwise from above), dn outward."""
    n = NRM[wall]
    if wall == "W":
        return (-WX - dn, u)
    if wall == "N":
        return (u, WY + dn)
    if wall == "E":
        return (WX + dn, -u)
    return (-u, -WY - dn)


FACES = {w: NRM[w] for w in WALLS}
TOWER = {"t1": ("N", (-TC[0], TC[1])), "t2": ("E", (TC[0], TC[1])), "t3": ("S", (TC[0], -TC[1])),
         "t4": ("W", (-TC[0], -TC[1]))}

NODES = ["start"]
ROOM, WALL_OF, BREACH = {}, {}, {}
for (nid, wall, u, c) in CP["rooms"]:
    x, y = wall_pt(wall, u)
    ROOM[nid] = dict(o=(x, y, c * CRS + SLAB), n=NRM[wall], w=RW, h=RH, d=RD)
    WALL_OF[nid] = wall
for w in WALLS:
    b = CP["breach"][w]
    BREACH[w] = b
# order: the run (path order), with the breach nodes in place
SEQ = CP["seq"]
NODES += SEQ + ["srv"]
for w in WALLS:
    u = CP["breach"][w]["u"]
    x, y = wall_pt(w, u)
    ROOM["b" + w.lower()] = dict(o=(x, y, SLAB), n=NRM[w], w=RW, h=RH, d=RD)              # the sally port (course 0)
    WALL_OF["b" + w.lower()] = w
    qx, qy = wall_pt(w, u, PLAT)
    ROOM["q" + w.lower()] = dict(o=(qx, qy, 0.6), n=NRM[w], w=RW, h=RH, d=RD)             # the freight platform room
    WALL_OF["q" + w.lower()] = "plat_" + w
for t, (w, (cx, cy)) in TOWER.items():
    n = NRM[w]
    o = (cx + n[0] * THALF, cy + n[1] * THALF, 3 * CRS + SLAB)
    ROOM[t] = dict(o=o, n=n, w=RW, h=RH, d=RD)
    WALL_OF[t] = "tower_" + t
SX, SY = CP["start"]
ROOM["start"] = dict(o=(SX, SY, 0.4), n=(-1.0, 0.0), w=8.0, h=4.6, d=6.0)
cfx, cfy = CTL["c"]
ROOM["m1"] = dict(o=(cfx - 3.0, cfy - CTL["half"], CTL["m1_z"]), n=(0.0, -1.0), w=RW, h=RH, d=RD)
WALL_OF["m1"] = "ctl"
VZ0 = CTL["h"] - CP["target_h"]
ROOM["srv"] = dict(o=(cfx, cfy - CTL["half"] + 4.0, VZ0), n=None, w=CP["target_w"], h=CP["target_h"],
                   d=CP["target_w"] - 6.0)

KIND = {"start": "start", "srv": "target"}
KIND.update(CP["kinds"])
LAYER = {n: i for i, n in enumerate(NODES)}
WORD = {"start": "GATE", "router": "FIGHT", "elite": "ELITE", "terminal": "EVENT", "modem": "SHOP", "rack": "RACK",
        "target": "THE MASTER MANIFEST"}
FILE = {
    "router": ("T4", "Fight: a yard security post", ["20-30 Cycles, a card", "maybe a Firmware chip"]),
    "elite": ("T4", "Elite fight (a loader rig)", ["40-50 Cycles, a rare card", "a Firmware chip"]),
    "terminal": ("T4", "Event: a container's cargo", ["a choice: card, Cycles", "or HP"]),
    "modem": ("T4", "Shop: the freight platform", ["cards, Firmware, a heal", "only by container"]),
    "rack": ("T4", "Rack: the platform's strongroom", ["banks your Schematics", "+3 Heat; only by container"]),
    "target": ("T4", "Central Server: the boss", ["the campaign", ""]),
}
HP_ARRIVE = "41 / 60"


# ------------------------------------------------------------------ the shuttle clock
def shuttle_at(w, t):
    """'wall' | 'train' for breach w's shuttle at integer turn t (HOLD turns each, phase per breach)."""
    return "wall" if ((int(t) + MECH["phase"][w]) // HOLD) % 2 == 0 else "train"


def moving(w, t):
    """True if breach w's shuttle moves at the change from turn t to t + 1 (the crane takes it)."""
    return shuttle_at(w, t) != shuttle_at(w, t + 1)


def mover_order(t):
    """The crane's lifts at the change t -> t+1, in order (one at a time, half a step each)."""
    return [w for w in MECH["crane_order"] if moving(w, t)]


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


LIFT_Z = CP["crane"]["lift_z"]


def shuttle_pos(w, mt):
    """The shuttle room's opening centre (x, y, z0) at mechanic time mt (continuous: the clips move it).
    The change t -> t+1 runs over the step's fraction 0.30-1.0: the pair's first lift in the first half of that,
    the second in the second; a lift = up out of the slot, swing out over the track, down onto the flatcar."""
    t = math.floor(mt + 1e-6)
    f = mt - t
    u = CP["breach"][w]["u"]
    wall = wall_pt(w, u) + (2 * CRS + SLAB,)
    car = wall_pt(w, u, TRK + RD / 2.0) + (CP["car_deck"],)
    a = wall if shuttle_at(w, t) == "wall" else car
    if not moving(w, t):
        return a
    b = car if a is wall else wall
    order = mover_order(t)
    k = order.index(w)
    n = len(order)
    f0 = 0.30 + 0.70 * k / n
    f1 = 0.30 + 0.70 * (k + 1) / n
    g = (f - f0) / (f1 - f0)
    if g <= 0:
        return a
    if g >= 1:
        return b
    if g < 1 / 3:
        e = _smooth(g * 3)
        return (a[0], a[1], a[2] + (LIFT_Z - a[2]) * e)
    if g < 2 / 3:
        e = _smooth(g * 3 - 1)
        return (a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e, LIFT_Z)
    e = _smooth(g * 3 - 2)
    return (b[0], b[1], LIFT_Z + (b[2] - LIFT_Z) * e)


def crane_target(mt):
    """Where the keep crane's hook is (x, y, z) and which shuttle it carries (or None), for the slewing jib."""
    t = math.floor(mt + 1e-6)
    f = mt - t
    order = mover_order(t)
    n = len(order)
    for k, w in enumerate(order):
        f0 = 0.30 + 0.70 * k / n
        f1 = 0.30 + 0.70 * (k + 1) / n
        if f0 <= f < f1:
            p = shuttle_pos(w, mt)
            return (p[0], p[1], p[2] + RH + 2.0), w
    # idle: parked over the next lift's shuttle (or the first of this turn's pair)
    nxt = mover_order(t + (1 if f >= 0.3 else 0)) or order or [MECH["crane_order"][0]]
    p = shuttle_pos(nxt[0], t + (1 if f >= 0.3 else 0))
    return (p[0], p[1], LIFT_Z + RH + 6.0), None


def room_rec_corp(i, mt):
    if mt is None:
        mt = len(WALK_MID) - 1
    if len(i) == 2 and i[0] == "s" and i[1].upper() in WALLS:
        w = i[1].upper()
        return dict(o=shuttle_pos(w, mt), n=NRM[w], w=RW, h=RH, d=RD)
    return None


# ------------------------------------------------------------------ the links
def _always():
    out = [("start", SEQ[0])]
    for a, b in CP["walk_links"]:
        out.append((a, b))
    return out


GATED = set()
for w in WALLS:
    b = CP["breach"][w]
    s_, P_, N_, Q_, T_ = "s" + w.lower(), b["prev"], b["next"], "q" + w.lower(), b["tower"]
    GATED |= {(P_, s_), (s_, N_), (s_, Q_)}


def base_edges(walked, mt):
    t = int(math.floor(mt + 1e-6))
    out = _always()
    for w in WALLS:
        b = CP["breach"][w]
        s_, P_, N_, Q_, T_ = "s" + w.lower(), b["prev"], b["next"], "q" + w.lower(), b["tower"]
        out += [(P_, "b" + w.lower()), ("b" + w.lower(), N_), (Q_, T_)]
        if shuttle_at(w, t) == "wall":
            out += [(P_, s_), (s_, N_)]
        if shuttle_at(w, t) == "train" or moving(w, t):
            out.append((s_, Q_))
    out.append(("m1", "srv"))
    return out


def edge_type(a, b):
    if a == "start":
        return "ramp"
    if b == "srv":
        return "lift"
    if a == "t4" and b == "m1":
        return "skyway"
    if (a, b) in GATED:
        if a[0] == "s" and b[0] == "q":
            return "ride"
        return "shuttle"
    if b[0] == "b" and len(b) == 2 or a[0] == "b" and len(a) == 2:
        return "sally"
    if a[0] == "q":
        return "platform_stair"
    if WALL_OF.get(a) == WALL_OF.get(b):
        return "catwalk"
    return "corner"


def _t(n):
    return (n[1], -n[0])


def door(i, side, mt=None):
    r = room_rec(i, mt)  # noqa: F821  (bound)
    n = r["n"] or (0.0, -1.0)
    t = _t(n)
    x, y, z0 = r["o"]
    return (x + n[0] * YF + t[0] * side * r["w"] / 2, y + n[1] * YF + t[1] * side * r["w"] / 2, z0 + DOOR_Z)


def _out(p, n, d):
    return (p[0] + n[0] * d, p[1] + n[1] * d, p[2])


def edge_path(a, b, mt=None):
    """World polylines. The run goes clockwise, which on every outer face is screen-RIGHT -> LEFT ... so a room's exit
    door is its side +1 in the kit frame and the entry door side -1 (the facade frame's tangent)."""
    t = edge_type(a, b)
    ra, rb = room_rec(a, mt), room_rec(b, mt)  # noqa: F821
    if t == "ramp":
        db = door(b, -1, mt)
        gy = CP["gate_u"]
        return [(SX + 4.0, SY, 1.2), (-WX - TRK - 14.0, gy, 1.2), (-WX - YF, gy, 1.2), (db[0], db[1], 1.2), db]
    if t == "lift":
        da = door(a, 1, mt)
        s = ROOM["srv"]["o"]
        return [da, (da[0] + 1.5, da[1] - 1.5, da[2]), (da[0] + 1.5, da[1] - 1.5, s[2] + DOOR_Z),
                (s[0], s[1] - 6.0, s[2] + DOOR_Z)]
    if t == "skyway":
        # up the SW tower's outer face to its roof, over the roof to the inner corner, the glazed skyway across the
        # yard to MANIFEST CONTROL's south face
        da, db = door(a, 1, mt), door(b, -1, mt)
        tz = CP["tower"]["courses"] * CRS + 1.5
        cx, cy = -TC[0], -TC[1]
        p1 = (da[0], da[1], tz)
        p2 = (cx + THALF - 2.0, cy + THALF - 2.0, tz)
        p3 = (db[0], db[1] - 8.0, db[2])
        return [da, p1, p2, p3, db]
    if t == "ride":
        # out of the container's door, onto the flatcar's deck and across the track to the platform
        da, db = door(a, 1, mt), door(b, -1, mt)
        n = ra["n"]
        return [da, _out(da, n, 2.0), (db[0], db[1], db[2])]
    if t == "shuttle":
        da, db = door(a, 1, mt), door(b, -1, mt)
        if abs(da[2] - db[2]) < 0.5:
            return [da, db]
        n = ra["n"] if ra["n"] else rb["n"]
        m = ((da[0] + db[0]) / 2, (da[1] + db[1]) / 2)
        return [da, (m[0], m[1], da[2]), (m[0], m[1], db[2]), db]
    if t == "sally":
        da, db = door(a, 1, mt), door(b, -1, mt)
        n = ra["n"]
        m = ((da[0] + db[0]) / 2, (da[1] + db[1]) / 2)
        return [da, (m[0], m[1], da[2]), (m[0], m[1], db[2]), db]
    if t == "platform_stair":
        # along the platform past the track's corner, up the tower's outer stair
        da, db = door(a, 1, mt), door(b, -1, mt)
        n = ra["n"]
        nb = rb["n"]
        p0 = _out(da, n, 0.0)
        c = (db[0] + nb[0] * (PLAT - 1.0), db[1] + nb[1] * (PLAT - 1.0))
        # the corner of the platform ring
        corner = (p0[0] + (c[0] - p0[0]) * (abs(nb[0])), p0[1] + (c[1] - p0[1]) * (abs(nb[1])))
        corner = (c[0] if abs(n[1]) > 0.5 else p0[0], c[1] if abs(n[0]) > 0.5 else p0[1])
        return [da, (corner[0], corner[1], da[2]), (c[0], c[1], 1.2), (c[0], c[1], db[2]), db]
    da, db = door(a, 1, mt), door(b, -1, mt)
    na, nb = ra["n"], rb["n"]
    if na == nb:
        # same facing (a catwalk; or a wall room <-> its tower's face a few BU further out): along da's plane to the
        # midpoint, a ladder / stair to db's plane and height, along to db
        if abs(da[2] - db[2]) < 0.5 and abs((db[0] - da[0]) * na[0] + (db[1] - da[1]) * na[1]) < 0.3:
            return [da, db]
        tg = _t(na)
        m = ((da[0] + db[0]) / 2, (da[1] + db[1]) / 2)
        ka = (m[0] - da[0]) * tg[0] + (m[1] - da[1]) * tg[1]
        kb = (m[0] - db[0]) * tg[0] + (m[1] - db[1]) * tg[1]
        p1 = (da[0] + tg[0] * ka, da[1] + tg[1] * ka, da[2])
        p2 = (db[0] + tg[0] * kb, db[1] + tg[1] * kb, db[2])
        return [da, p1, p2, db]
    # corner: round the corner tower on the outside (a stair round its outer corner)
    mx, my = (da[0] + db[0]) / 2, (da[1] + db[1]) / 2
    tcx = TC[0] if mx > 0 else -TC[0]
    tcy = TC[1] if my > 0 else -TC[1]
    cx = tcx + (THALF + 2.0) * (1 if tcx > 0 else -1)
    cy = tcy + (THALF + 2.0) * (1 if tcy > 0 else -1)
    p1 = (cx, da[1]) if abs(na[0]) > 0.5 else (da[0], cy)
    p3 = (cx, db[1]) if abs(nb[0]) > 0.5 else (db[0], cy)
    zm = (da[2] + db[2]) / 2
    return [da, (p1[0], p1[1], da[2]), (cx, cy, zm), (p3[0], p3[1], db[2]), db]


def seg_normal(p):
    """The facade side a link point sits on (hidden when that side faces away): the nearest wall's outward normal."""
    x, y = p[0], p[1]
    if abs(x) <= WX - 2 and abs(y) <= WY - 2:
        return None                                           # inside the yard (the skyway, the lift)
    ex, ey = abs(x) / WX, abs(y) / WY
    if ex > ey:
        return (1.0 if x > 0 else -1.0, 0.0)
    return (0.0, 1.0 if y > 0 else -1.0)


def mech(walked, mt=None):
    mt = len(walked) - 1 if mt is None else mt
    t = int(math.floor(mt + 1e-6))
    st, _ = states(walked, mt)  # noqa: F821
    sh = {w: shuttle_at(w, t) for w in WALLS}
    nxt = {w: shuttle_at(w, t + 1) for w in WALLS}
    lands_in = {}
    for w in WALLS:
        for k in range(1, CYCLE + 1):
            if shuttle_at(w, t + k) != sh[w]:
                lands_in[w] = k
                break
    affected = ["s" + w.lower() for w in WALLS if st.get("s" + w.lower()) in ("option", "reach", "current")]
    return dict(turn=t, shuttles=sh, shuttles_next=nxt, lands_in=lands_in, crane_next=mover_order(t), affected=affected)


hqk_graph.bind(globals())
_edges_all = edges  # noqa: F821  (bound)


def locked_edges(walked, mt=None):
    """Gated links NOT live now (a container is away): drawn dashed + a padlock; live ones stay in the wax."""
    t = int(math.floor((len(walked) - 1 if mt is None else mt) + 1e-6))
    live = set(base_edges(walked, t))
    seen = set(zip(walked[:-1], walked[1:]))
    st, _ = states(walked, t)  # noqa: F821
    ahead = {i for i, s in st.items() if s in ("current", "option", "reach")}
    return sorted([e for e in GATED if e not in live and e not in seen and e[1] not in walked and e[0] in ahead],
                  key=lambda e: (ORDER[e[0]], ORDER[e[1]]))  # noqa: F821


def edges(walked, mt=None):  # noqa: F811
    lk = set(locked_edges(walked, mt))
    return [e for e in _edges_all(walked, mt) if e not in lk]


# ------------------------------------------------------------------ the run states shown
WALK_OV = CP["walk_ov"]
WALK_DEC = CP["walk_dec"]
HOVER_DEC = CP["hover_dec"]
WALK_MID = WALK_DEC

_tz = CP["tower"]["courses"] * CRS
OV_POINTS = [(sx * (WX + TRK + 6), sy * (WY + TRK + 6), 0.0) for sx in (-1, 1) for sy in (-1, 1)]
OV_POINTS += [(sx * (TC[0] + THALF), sy * (TC[1] + THALF), _tz) for sx in (-1, 1) for sy in (-1, 1)]
OV_POINTS += [(cfx, cfy, CTL["h"] + 12.0), (CP["crane"]["x"], CP["crane"]["y"], CP["crane"]["z"] + 10.0)]


def MOVER_POS(mt, walked=None):
    out = {"s" + w.lower(): shuttle_pos(w, mt) for w in WALLS}
    hp, _ = crane_target(mt)
    out["hook"] = hp
    return out


def STILLS(CR):
    o = CR.overview(WALK_OV)
    return {
        "H_overview": (o, dict(walked=WALK_OV, mt=MECH["ov_mt"], extra=dict(lifting=MECH["ov_lifting"]))),
        "H_decision": (CR.decision(WALK_DEC), dict(walked=WALK_DEC)),
        "H_hover": (CR.hover(WALK_DEC, HOVER_DEC), dict(walked=WALK_DEC, hover=HOVER_DEC, hover_k=1.0)),
    }


def SHEET_SHOTS(CR):
    a = CP["sheet"]["live"]
    b = CP["sheet"]["transit"]
    c = CP["sheet"]["dead"]
    return {
        "S_link_live": (CR.decision(a["walk"]), dict(walked=a["walk"])),
        "S_in_transit": (CR.decision(b["walk"]), dict(walked=b["walk"], mt=b["mt"], extra=dict(lifting="N"))),
        "S_link_dead": (CR.decision(c["walk"]), dict(walked=c["walk"])),
    }


ORBIT_T = 5.0


def ORBIT(CR):
    """H_orbit_v2: two steps round the NE corner (n2 -> t2 -> e1) while the E / W shuttle pair moves; the camera orbits
    on the kit's rule (the decision yaw follows the faces holding the current room + its options), eased between the
    decision poses; mt runs continuously so the crane's lift plays out during the steps."""
    ws = CP["orbit"]["walks"]
    poses = [CR.decision(w) for w in ws]
    n = int(ORBIT_T * CR.FPS)
    out = []
    seg = (n - 1) / (len(ws) - 1)
    for k in range(n):
        x = k / seg
        i = min(len(ws) - 2, int(x))
        f = x - i
        e = CR.ease((f - 0.25) / 0.6)                  # hold a beat on each decision, then move
        p = poses[i].mix(poses[i + 1], e)
        t0 = len(ws[i]) - 1
        mt = t0 + min(0.999, f)
        walked = ws[i] if e < 0.5 else ws[i + 1]
        out.append((k / CR.FPS, p, walked, mt, dict(ui=1.0, route=1.0)))
    return out


REVEAL_T = 6.5


def REVEAL(CR):
    """Kept for the kit (v1 reveal); v2 delivers the orbit clip instead."""
    return ORBIT(CR)


if __name__ == "__main__":
    for t in range(9):
        print("turn", t, {w: shuttle_at(w, t)[0] for w in WALLS}, "crane", mover_order(t))
    for nm, w in (("OV", WALK_OV), ("DEC", WALK_DEC)):
        st, opts = states(w)
        print(nm, "at", w[-1], "turn", len(w) - 1, "options", opts, "locked", locked_edges(w))
    # the planner: play greedy lines to the server (every option tried at each breach)
    import itertools  # noqa: F401

    def play(w):
        while w[-1] != "srv":
            o = succ(w[-1], w)
            if not o:
                return w, "STUCK at %s turn %d" % (w[-1], len(w) - 1)
            w = w + [o[0]]
        return w, "server at turn %d" % (len(w) - 1)
    print(play(["start"]))
    print(play(list(WALK_DEC) + ["qn"]))
