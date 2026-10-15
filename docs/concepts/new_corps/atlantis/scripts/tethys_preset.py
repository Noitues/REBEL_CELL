"""Tethys Deep (atlantis): the look preset. Every number the scene uses lives here (variant keys in NOTES.md)."""
import copy

PRESET = {
    "palette": {"abyss": "#2F6BFF", "red": "#C8264E", "trench": "#06112A", "photo": "#7CF2E4", "dive": "#FFE9B8",
                "hull": "#141A24", "titan": "#5E6B7C", "rock": "#1C2430", "sand": "#2A3440"},
    "light": {"neon": 9.0, "photo": 5.0, "window": 3.0, "room": 7.0, "sub_head": 4.0e3, "sub_trail": 10.0,
              "shaft": 6.0e6, "sun": 0.12, "surface": 0.35, "caustic": 0.07, "dome": 2.5, "red": 8.0, "vent": 30.0,
              "uplight": 1.6e4},
    "water": {"density": 0.008, "hq_density": 0.0035, "scatter": (0.06, 0.26, 0.86, 1), "absorb": (0.02, 0.38, 0.80, 1), "aniso": 0.65,
              "noise": (0.012, 0.25, 0.85)},
    "seeds": {"district": 7101, "kit": 7102, "hq": 7103, "street": 7104, "jitter": 7105, "shafts": 7106, "snow": 7107,
              "kelp": 7108, "bubbles": 7109},
    "signs": {"ads": ["breathe easy", "air plan 9", "tethys / deep", "dry rooms now"]},
    "district": {
        "len": 360.0, "surface_z": 150.0, "block_w": (20.0, 34.0), "tower_h": (30.0, 110.0), "domes": 7,
        "cam": (0.0, -40.0, 34.0), "target": (0.0, 170.0, 52.0), "lens": 24.0, "sub_lanes": [(-6.0, 14.0), (6.0, 22.0), (-2.0, 60.0), (10.0, 90.0)],
        "shafts": 14,
    },
    "kit_sheet": {"pitch": 96.0, "cam": (0.0, -390.0, 300.0), "target": (0.0, 80.0, 300.0), "lens": 30.0, "shift": (0.0, -0.47)},
    "hq": {
        "surface_z": 380.0, "trench_w": 370.0,
        "decks": [(320.0, 5), (258.0, 4), (196.0, 4), (134.0, 3), (72.0, 2)],    # (z, rooms)
        "deck_len": 280.0, "deck_r": 16.0, "room": (24.0, 12.0, 6.0),
        "drops": [[(-64.0, "open"), (64.0, "flooded")], [(-48.0, "airlock"), (56.0, "open")],
                  [(-72.0, "flooded"), (32.0, "open")], [(0.0, "flooded")]],
        "tide_z": 180.0, "tide_next_z": 236.0, "current": [1, 1],
        "cam": (0.0, -520.0, 196.0), "target": (0.0, 0.0, 190.0), "lens": 24.0,
    },
    "street": {
        "x0": 0.0, "x1": 430.0, "block_w": (28.0, 42.0),
        "rooms": {"S": (0, 0), "L1_0": (1, 1), "L2_0": (2, 3), "L2_1": (2, 7), "L3_0": (3, 4), "L3_1": (4, 9),
                  "L4_0": (5, 2), "L4_1": (5, 7), "L5_0": (6, 5), "L5_1": (7, 2), "L6_0": (8, 4), "L6_1": (8, 9),
                  "L7": (9, 7)},
        "current": "L3_0", "surface_z": 170.0,
        "cam": (208.0, -255.0, 46.0), "target": (208.0, 40.0, 54.0), "lens": 26.5,
    },
}

VARIANTS = {"tethys_deep": {}, "tethys_shallow": {"water": {"density": 0.006}, "light": {"shaft": 9.0e6}}}


def variant(name):
    p = copy.deepcopy(PRESET)
    for k, v in VARIANTS.get(name, {}).items():
        p[k].update(v)
    return p
