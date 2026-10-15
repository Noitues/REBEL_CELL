"""Aurelian Concord (roman): the look preset. Every number the scene uses lives here (variant keys in NOTES.md)."""
import copy

DOT = chr(0xB7)

PRESET = {
    "palette": {"verdigris": "#29DBA6", "travertine": "#E9D5AA", "marble": "#F3EFE6", "porphyry": "#3A1426",
                "bronze": "#3F8F76", "gilt": "#C9A35A"},
    "light": {"neon": 9.0, "shop": 4.0, "window": 3.0, "streak": 14.0, "room": 7.0, "lamp": 260.0, "beam": 3.0e7,
              "win_warm": (1.0, 0.62, 0.32, 1), "win_cool": (0.45, 0.7, 1.0, 1), "hq_wash": 2.0e5, "uplight": 2.4e4,
              "server": 4.0e4},
    "fog": {"density": 0.005},
    "kit": {"storey": 4.2, "ground_h": 6.4, "col_pitch": 3.6, "lit_p": 0.42, "campanile_level": 7.0, "campanile_cols": 14},
    "seeds": {"district": 6101, "kit": 6102, "hq": 6103, "street": 6104, "jitter": 6105, "beams": 6106, "packets": 6107},
    "signs": {"arch": "CONCORDIA " + DOT + " AVRELIA", "ads": ["PANEM", "LVDI LIVE", "BE A CLIENT", "BREAD TONIGHT"]},
    "district": {
        "street_len": 360.0, "near_until": 170.0, "block_w": (22.0, 38.0), "floors": (3, 6), "tower_h": (60.0, 140.0),
        "aqueduct_y": 124.0, "aqueduct_z": 34.0, "arch_y": 252.0, "campanile_p": 0.25,
        "billboards": [(-46.0, 96.0, 52.0, 14.0, "e_holo_p"), (30.0, 196.0, 64.0, 16.0, "e_holo"), (-60.0, 300.0, 80.0, 18.0, "e_holo")],
        "beams": [(-70.0, 200.0, 100.0, "#29DBA6"), (80.0, 260.0, 130.0, "#FFFFFF"), (-130.0, 400.0, 160.0, "#FF4FB0"),
                  (150.0, 380.0, 150.0, "#29DBA6")],
        "cam": (0.0, -34.0, 36.0), "cam_target": (0.0, 200.0, 24.0), "lens": 26.0,
    },
    "kit_sheet": {
        "items": [("insula", 6, "pediment"), ("insula", 9, "statue"), ("insula", 7, "crown"), ("campanile", 8),
                  ("basilica",), ("aqueduct",), ("arch",), ("piazza",)],
        "pitch": 96.0, "cam": (0.0, -390.0, 300.0), "target": (0.0, 80.0, 300.0), "lens": 30.0, "shift": (0.0, -0.47),
    },
    "hq": {
        "outer_r": 150.0, "outer_h": 46.0, "outer_bays": 40,
        "rings": [(142.0, 116.0, 34.0), (116.0, 92.0, 25.0), (92.0, 70.0, 16.0), (70.0, 50.0, 8.0)],
        "rooms": [[155, 131, 107, 83, 59, 35], [150, 124, 98, 72, 46], [140, 111, 82, 53], [125, 95, 65]],
        "room": (14.0, 8.0, 7.0),
        "gate_w": 9.0,
        "gates_now": [[100, 280], [60, 240], [118, 298], [80, 260]],
        "gate_step": [24, -26, 29, -31],
        "current": [0, 2],
        "cam": (0.0, -250.0, 330.0), "target": (0.0, 58.0, 12.0), "lens": 33.0,
    },
    "street": {
        "x0": 0.0, "x1": 430.0, "block_w": (28.0, 42.0), "floors": (7, 12),
        "rooms": {"S": (0, 0), "L1_0": (1, 1), "L2_0": (2, 3), "L2_1": (2, 7), "L3_0": (3, 4), "L3_1": (4, 9),
                  "L4_0": (5, 2), "L4_1": (5, 7), "L5_0": (6, 5), "L5_1": (7, 2), "L6_0": (8, 4), "L6_1": (8, 9),
                  "L7": (9, 7)},
        "current": "L3_0",
        "billboards": [(52.0, 52.0, 14.0, "e_holo_p"), (300.0, 66.0, 16.0, "e_holo")],
        "beams": [(40.0, 120.0, 120.0, "#29DBA6"), (250.0, 200.0, 150.0, "#FFFFFF"), (380.0, 140.0, 120.0, "#FF4FB0")],
        "cam": (208.0, -250.0, 44.0), "target": (208.0, 40.0, 46.0), "lens": 26.5,
    },
}

VARIANTS = {
    "aurelian_night": {},
    "aurelian_games": {"light": {"neon": 12.0}, "fog": {"density": 0.006}},
}


def variant(name):
    p = copy.deepcopy(PRESET)
    for k, v in VARIANTS.get(name, {}).items():
        p[k].update(v)
    return p
