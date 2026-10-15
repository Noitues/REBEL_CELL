"""HQ Halcyon: the run graph = hq_kit.layout.Compound configured by halcyon_preset (+ the Halcyon words and states).

The generic rules (the spiral, galleries, corner stairs, climbs, the vault, the scan rule) live in hq_kit/layout.py.
This module is Halcyon's config + the module-level names the overlay kit reads (r3 sgraph API: NODES, KIND, LAYER,
WORD, FILE, HP_ARRIVE, states, edge_states, branch ...).

Halcyon config: rows 6-5-4-3-2-1 (round 43), path "spiral" from the south face, shortcuts "climb" (3>19, 4>20, 9>21),
max 2; the scan rule is the LIGHTHOUSE (a 90 degree sector turning 45 degrees a step, clockwise: watch type
"lighthouse", phase 0). Consequence word: preset halcyon.eye.consequence ("spotted" | "blocked").
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import halcyon_preset as HP  # noqa: E402
from hq_kit import layout as L  # noqa: E402

CP = HP.PRESET["halcyon"]["compound"]
EYEP = HP.PRESET["halcyon"]["eye"]
C = L.Compound(dict(CP, path="spiral", face0=0, shortcuts="climb"),
               watch=dict(type="lighthouse", phase=EYEP["phase"], sector=90.0, step=45.0))

FACES, N, T = L.FACES, L.N, L.T
ROWS, R = C.ROWS, C.R
RW, RH, RD, PITCH, TH, PODIUM = C.RW, C.RH, C.RD, C.PITCH, C.TH, C.PODIUM
SLAB, DOOR_Z, YF = L.SLAB, L.DOOR_Z, L.YF
NODES, ROW, K, U, FACE, KIND, LAYER, ORDER = C.NODES, C.ROW, C.K, C.U, C.FACE, C.KIND, C.LAYER, C.ORDER
N_ROOMS, PATH, SHORTCUTS = C.N_ROOMS, C.PATH, C.SHORTCUTS

WORD = {"start": "GATE", "router": "FIGHT", "elite": "ELITE", "terminal": "EVENT", "modem": "SHOP", "rack": "RACK",
        "target": "THE PANOPTICON"}
FILE = {
    "router": ("T4", "Fight: a civic security post", ["20-30 Cycles, a card", "maybe a Firmware chip"]),
    "elite": ("T4", "Elite fight (riot unit)", ["40-50 Cycles, a rare card", "a Firmware chip"]),
    "terminal": ("T4", "Event: a Terminal voice", ["a choice: card, Cycles", "or HP"]),
    "modem": ("T4", "Shop: spend Cycles", ["cards, Firmware, a heal"]),
    "rack": ("T4", "Rack: elite, then banks", ["banks your Schematics", "+3 Heat"]),
    "target": ("T4", "Central Server: the boss", ["the campaign", ""]),
}
HP_ARRIVE = "41 / 60"

# the run states shown (two orbit angles): EARLY on the south face, LATER on the east face
WALK_EARLY = ["start", "n1", "n2", "n3"]                            # options: 4 (long way), 19 (climb, south face)
HOVER_EARLY = "n19"
WALK_LATE = ["start"] + ["n%d" % i for i in range(1, 10)]           # the long way to 9 (east face)
HOVER_LATE = "n21"                                                   # options 10 (long way), 21 (climb, east face)
WALK_MID = WALK_LATE

tier_floor, half_size, tiers, fp = C.tier_floor, C.half_size, C.tiers, C.fp
room_z, room_front, room_corners, room_center = C.room_z, C.room_front, C.room_corners, C.room_center
start_pos, eye_pos, crown_top = C.start_pos, C.eye_pos, C.crown_top
edges, succ, reach, states, edge_states = C.edges, C.succ, C.reach, C.states, C.edge_states
shortcuts_used, edge_type, door, edge_path = C.shortcuts_used, C.edge_type, C.door, C.edge_path
room_az, scanned = C.room_az, C.scanned


def branch(o, walked=None):
    return C.branch(o, walked if walked is not None else WALK_MID)


def eye_az(step):
    return C.watch_az(step)


def in_sector(az, c):
    d = (az - c + 180.0) % 360.0 - 180.0
    return -45.0 <= d < 45.0


def hidden_mid(a, b):
    return None                       # every link is on the outside (designer correction): nothing is x-rayed by type


def dump(path, walked=None, extra=None):
    return C.dump(path, walked or WALK_MID, extra)


if __name__ == "__main__":
    print("rooms", N_ROOMS, "shortcuts", ["%s>%s" % (a[1:], b[1:]) for a, b in SHORTCUTS])
    for r in range(R):
        print("segment", r + 1, "face", FACES[C.SEG_FACE[r]], "tier hs %.1f" % half_size(r),
              [(n, KIND[n], U[n]) for n in NODES if ROW[n] == r])
    for name, w in (("EARLY", WALK_EARLY), ("LATE", WALK_LATE)):
        st, opts = states(w)
        sc, f = scanned(w)
        print(name, "current", w[-1], "options", opts, "eye az", f, "scanned", sc, "shortcuts used",
              shortcuts_used(w), "grey", [n for n in NODES if st[n] == "grey"])
    print("eye", eye_pos(), "start", start_pos())
