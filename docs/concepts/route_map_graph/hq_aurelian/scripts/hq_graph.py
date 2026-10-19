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


CONCEPT = "R"                                    # DESIGN.md 14.2: the route runs from the outer arcade in to the vault
SLOTS = AL.slots(LAYERS, CONCEPT)
GATES = {g_["a"]: g_ for g_ in AL.gates(CONCEPT)}   # the gate that leaves each level
for s_ in SLOTS:
    s_["id"] = nid(s_["layer"], s_["node"])
SLOT = {s_["id"]: s_ for s_ in SLOTS}


def _rec(s):
    w, h, d = s["size"]
    x, y, z = s["pos"]
    n = None if s["normal"] is None else (s["normal"][0], s["normal"][1])
    return dict(o=(x * KS, y * KS, z * KS), n=n, w=w * KS, h=h * KS, d=d * KS)


_en, _nn = AL.ENTRY["entry"], AL.ENTRY["entry_nrm"]      # the Cell's box on the boulevard, in front of the entry arch
ROOM = {"start": dict(o=((_en[0] + _nn[0] * 6.0) * KS, (_en[1] + _nn[1] * 6.0) * KS, 0.4), n=tuple(_nn), w=8.0, h=4.6, d=6.0)}
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
    if SLOT[a]["level"] == SLOT[b]["level"]:
        return "gallery"
    return "gate"


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


def _level_r(sl):
    """The city radius of the ellipse a slot sits on, and the side its door faces."""
    return math.hypot(sl["pos"][0], sl["pos"][1] / AL.BK)


def _run(sl, t0, t1, z, n=14):
    """A walk along the slot's level between two parameters (radians, the short way), at door height z (kit)."""
    inward = sl["kind"] in ("cavea", "podium")
    return _arc(t0, _short(t0, t1), _level_r(sl), z, YF * 3 / KS, inward, n)


def edge_path(a, b, mt=None):
    """World polylines (kit units). Galleries follow the level's ellipse (the ground arcade, a seating ring, the podium).
    A GATE edge (DESIGN.md 14.2) runs to the end of the level, through the gate's arch (the outer vomitorium, or a stair cut
    through the riser) and along the next level. The start's ramp runs in through the entry arch. The arena stair
    runs straight across the sand to the tholos."""
    da, db = door(a), door(b)
    if b == "srv":
        o = ROOM["srv"]["o"]
        v = (da[0] - o[0], da[1] - o[1])
        L = math.hypot(*v) or 1.0
        end = (o[0] + v[0] / L * 5.6 * KS, o[1] + v[1] / L * 5.6 * KS, o[2] + DOOR_Z)
        return [da, (da[0], da[1], end[2]), end]
    sb = SLOT[b]
    tb = math.radians(sb["t"])
    if a == "start":
        te = math.radians(AL.ENTRY_T)
        en = AL.ENTRY["entry"]
        zf = db[2]
        return [da, (en[0] * KS, en[1] * KS, zf)] + _run(sb, te, tb, zf, 16) + [db]
    sa = SLOT[a]
    ta = math.radians(sa["t"])
    if sa["level"] == sb["level"]:
        return [da] + _run(sa, ta, tb, da[2], 14) + [db]
    g = GATES[sa["level"]]
    tg = math.radians(g["t"])
    pts = [da] + _run(sa, ta, tg, da[2], 10)
    pts += [(x * KS, y * KS, z * KS + DOOR_Z) for (x, y, z) in g["p"]]
    pts += _run(sb, tg, tb, db[2], 10) + [db]
    return pts


def seg_normal(p):
    return None


BAND_BAYS = 1          # DESIGN.md 14.7: one grid bay (6 deg) either side of the current room and its options


def band_points(walked, mt=None, pose=None):
    """The landmark's FACE BAND at the current level (DESIGN.md 14.7): the arc of the level's face from the current room to the
    options' rooms, plus one bay either side, as kit points (the front plane, floor and room-top heights). The occlusion cone
    covers it, so a tower in front of the colonnade (or the ring) is cut even where no room sits behind it."""
    cur = walked[-1]
    st, opts = states(walked, mt)  # noqa: F821
    ids = [i for i in [cur] + list(opts) if i in SLOT]
    pts = []
    for lv in sorted(set(SLOT[i]["level"] for i in ids)):
        ts = [SLOT[i]["t"] for i in ids if SLOT[i]["level"] == lv]
        sl = next(SLOT[i] for i in ids if SLOT[i]["level"] == lv)
        pad = BAND_BAYS * 360.0 / 60.0
        t0, t1 = min(ts) - pad, max(ts) + pad
        r = _level_r(sl)
        z0, h = sl["pos"][2], sl["size"][1]
        if pose is not None:
            # the band runs on to the frame edge: every point of the level's face in frame (the AD's left-centre tower stood two bays
            # beyond the options' +1 bay and still hid the colonnade)
            a0, a1 = next(L_ for L_ in AL._levels(CONCEPT) if L_["name"] == lv)["arc"]
            t0, t1 = min(a0, a1) - 12.0, max(a0, a1) + 12.0
            n_ = int((t1 - t0) / 3.0)
        else:
            n_ = 8
        for k in range(n_ + 1):
            t = math.radians(t0 + (t1 - t0) * k / n_)
            x, y = AL.ell(t, r)
            for z in (z0, z0 + h):
                p_ = (x * KS, y * KS, z * KS)
                if pose is not None:
                    q = pose.proj(p_, w=2560)
                    if q is None or not (0 <= q[0] <= 2560 and 0 <= q[1] <= 1440):
                        continue
                pts.append(p_)
    return pts


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


WALK_DEC = walk_to(1)              # current in the outer arcade (layer 0), its options in the same arcade (layer 1)
WALK_CAV = walk_to(5)              # current on a seating ring (R2, layer 4), its options on the same ring (layer 5)
WALK_OV = WALK_DEC
WALK_MID = WALK_DEC
HOVER_DEC = None


def MOVER_POS(mt, walked=None):
    return {}


def _lerp(a, b, t):
    return a + (b - a) * t


def CAM_RULE(walked, mt, CR):
    """DESIGN.md 14.3: the camera orbits the colosseum to face the current room's bearing (the yaw is the mean look of the
    distinct room normals holding the current room and the options, or the options' when that mean is degenerate, as at a
    gate where the normals are opposite); the PITCH RISES as the route moves inward (CAMP pitch_band, outer arcade 30 to
    arena and vault 55). Outside the colonnade for the arcade rooms; inside the bowl for the seating rings and the podium,
    looking down across the arena; the vault from the OVERVIEW bearing, closer."""
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
    band = CAMP["pitch_band"]
    pitch = band["ARC"] if s is None else band[s["level"]]
    pts = []
    for i in ids:
        pts += room_corners(i, mt)  # noqa: F821
    c = room_center(cur, mt)  # noqa: F821
    if s is not None and s["kind"] == "vault":
        p = CR.frame_points(pts, CAMP["ov_yaw"], pitch, CR.LENS_D, CR.FILL_W, CR.FILL_H, centre=c,
                            dmin=0.6 * CR.overview(WALK_OV).dist)
        return CR.centre_on(p, c)
    if s is None or s["kind"] in ("loggia", "attic", "arcade"):
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
            "H_decision_inner": (CR.decision(WALK_CAV), dict(walked=WALK_CAV)),
            "H_hover": (CR.hover(WALK_DEC, hov), dict(walked=WALK_DEC, hover=hov, hover_k=1.0))}


def CLOSE_SHOTS(CR):
    """Close-up checks (python hq_run.py shots CLOSE_SHOTS <quality>): the arcade rooms, the entry, the outer gate, a riser gate."""
    out = {}
    P = CR.Pose

    def look(n):
        return CR.yaw_of((-n[0], -n[1]))
    r = ROOM["n0_1"]
    c = room_center("n0_1")  # noqa: F821
    out["C_arcade"] = (P(c, look(r["n"]), 30.0, 150.0, 42.0), dict(walked=WALK_DEC))
    en = AL.ENTRY["entry"]
    nn = AL.ENTRY["entry_nrm"]
    out["C_entry"] = (P((en[0] * KS, en[1] * KS, 6.0), look(nn), 30.0, 160.0, 42.0), dict(walked=WALK_DEC))
    g = AL.gates(CONCEPT)[0]
    out["C_gate_outer"] = (P((g["p"][0][0] * KS, g["p"][0][1] * KS, 6.0), look(g["n"]), 24.0, 100.0, 42.0), dict(walked=WALK_DEC))
    g = AL.gates(CONCEPT)[1]
    out["C_gate_riser"] = (P((g["p"][0][0] * KS, g["p"][0][1] * KS, 11.0 * KS), look(g["n"]), 32.0, 80.0, 36.0), dict(walked=WALK_CAV))
    return out


def SHEET_SHOTS(CR):
    return {}


def REVEAL(CR):
    return []


if __name__ == "__main__":
    st_, op_ = states(WALK_DEC)  # noqa: F821
    print("nodes", len(NODES), "edges", len(EDGES), "dec", WALK_DEC, "options", op_, "cav", WALK_CAV)
