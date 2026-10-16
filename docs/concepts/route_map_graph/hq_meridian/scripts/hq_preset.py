"""HQ Meridian: the r3 look preset plus the Meridian variant (the container fortress, the yard cycle).

The kit (hqk_*.py, hq_scene / hq_cam / hq_overlay / hq_post / hq_compose / hq_jobs) reads PRESET["hq"] and
PRESET["hq_fog"]; the street look itself stays look_preset.PRESET (r3, unchanged). Units as r3: BU (1 storey = 8 BU).
    import hq_preset as HP; P = HP.PRESET; H = P["hq"]
"""
import copy

import look_preset as _LP

PRESET = copy.deepcopy(_LP.PRESET)
PALETTES = dict(_LP.PALETTES)

PRESET["hq"] = {
    "corp": "meridian", "corp_name": "MERIDIAN FREIGHT",
    "dossier": ("MERIDIAN", "FREIGHT SECURITY", (255, 140, 26)),
    "target_name": "THE MASTER MANIFEST", "target_place": "MANIFEST CONTROL",
    "out_big": r"D:\rc_scratch\hq_meridian",
    # ------------------------------------------------------------ palette (linear RGB)
    # Meridian orange #FF8C1A is ALSO the route's "next" orange: the fortress keeps orange to small hazard marks and
    # the MERIDIAN FREIGHT sign; the steel is rust-dark, the light is cold yard sodium-white + red hazard (NOTES Q1).
    "palette": {
        "steel": (0.105, 0.052, 0.034),          # rust-dark corrugated container steel (albedo)
        "steel_alt": [(0.11, 0.045, 0.03), (0.05, 0.065, 0.08), (0.10, 0.07, 0.035), (0.075, 0.03, 0.03),
                      (0.035, 0.05, 0.045)],    # the container courses: rust, navy, ochre, oxblood, green-grey
        "corp_orange": (1.0, 0.26, 0.012),       # #FF8C1A linear: the sign, hazard marks
        "corp_red": (1.0, 0.027, 0.02),          # #FF2E28 linear: beacons, the gate lamps
        "yard_white": (1.0, 0.86, 0.66),         # warm-white yard floods (sodium-white)
        "yard_cool": (0.62, 0.84, 1.0),          # the cold mast floods
        "hazard": (1.0, 0.55, 0.02),             # mover beacons (amber, rotating)
        "panel": (0.30, 0.31, 0.33), "panel_dark": (0.16, 0.16, 0.17),
        "glass": (0.015, 0.03, 0.035), "concrete": (0.20, 0.20, 0.21),
        "lockdown": (1.0, 0.05, 0.08), "gold": (1.0, 0.62, 0.12),
        "scan": (1.0, 0.82, 0.55),
        "sodium": (1.0, 0.42, 0.09),             # sodium yard light
        "work": (1.0, 0.30, 0.04),               # Meridian orange work lights / lit seams
    },
    # ------------------------------------------------------------ the fortress (hq_graph.py reads these)
    "compound": {
        "room_w": 14.0, "room_h": 8.0, "room_d": 10.0, "course": 9.0,      # a container room; one wall course
        "wall": {"x": 80.0, "y": 60.0, "courses": 3, "d": 10.0},           # outer faces at |x| = 80, |y| = 60
        "tower": {"half": 11.0, "c": (78.0, 58.0), "courses": 5},          # four corner towers (crossed courses)
        "moat": {"w": 9.0, "gap": 3.0},
        "track_y": (78.0, 88.0),                                           # the through track + the siding (north)
        "crane": {"x": 4.0, "legs_x": 14.0, "legs_y": (36.0, 48.0), "z": 62.0, "boom_y": (12.0, 114.0), "apex": 96.0},
        "control": {"c": (27.0, 0.0), "half": 15.0, "h": 66.0},            # MANIFEST CONTROL (the server tower)
        "gate_u": -38.0,                                                   # the gatehouse on the west wall
        "start": (-106.0, -38.0),
        # the route (path order): name, wall (W / N / tw = NW tower north face / te / ctl), u (BU along the wall,
        # screen-right positive), course (or z for the control tower)
        "rooms": [("w1", "W", -20.0, 0), ("w2", "W", -2.0, 1), ("w3", "W", 16.0, 1), ("w4", "W", 34.0, 2),
                  ("t1", "tw", 0.0, 3), ("n1", "N", -54.0, 2), ("n2", "N", -32.0, 2), ("n3", "N", -12.0, 1),
                  ("n4", "N", 30.0, 2), ("t2", "te", 0.0, 3), ("m1", "ctl", 7.0, 30.0), ("m2", "ctl", -8.0, 44.0)],
        "kinds": {"w1": "router", "w2": "terminal", "w3": "router", "w4": "elite", "t1": "modem", "n1": "router",
                  "n2": "terminal", "n3": "router", "n4": "elite", "t2": "modem", "m1": "router", "m2": "elite",
                  "car": "elite", "hook": "router"},
        "target_w": 22.0, "target_h": 10.0,
        "max_shortcuts": 1,                       # rides (the train or the hook): at most 1 (proposal)
    },
    # ------------------------------------------------------------ THE YARD CYCLE (round 43, adapted: NOTES 3)
    "mech": {
        "phase": 1, "cycle": 6,
        # the train's car: where it stands at each step of the cycle (x of the car's centre; None = out of the yard)
        "train": ["arrive", "west", "east", "east", "leave", "gone"],
        "train_x": {"arrive": -300.0, "west": -54.0, "east": 78.0, "leave": 320.0, "gone": 700.0},
        "crane": ["yard", "swing", "wall", "wall", "yard", "yard"],
        "eject": "the train leaves with you: ejected at the gate, Heat +1",       # proposal (round 43 open question)
    },
    "light": {"flood_w": 2.6e4, "flood_cone": 62.0, "uplight_w": 260.0, "room_k": 1.0, "room_w": 3000.0,
              "lockdown_k": 2.0, "sign_k": 0.5, "slit_k": 0.25, "trim_k": 2.2, "cityglow_k": 0.15,
              "city_beam_k": 0.8, "bank_glow": 3500.0, "shop_w": 900.0, "beacon_w": 2.5e3, "mover_k": 1.6,
              # the landmark rig (designer audit): the compound reads 1.5-2x the local city background
              "seam_k": 2.8, "logo_k": 3.0, "work_w": 10000.0, "tower_flood_w": 1.6e5, "keep_w": 7.0e4,
              "sodium_w": 2500.0, "rail_k": 2.5, "rim_w": 1.5e5, "bank_h": 75.0, "bank_peak": 0.007,
              "bank_box": (-230.0, -270.0, 0.0, 230.0, -120.0, 110.0), "bank_fill_w": 2.5e4,
              "boom_k": 3.0, "hook_spot_w": 1.2e4, "train_run_k": 6.0, "head_w": 3.0e6},
    "beams": {"power": 2.4e7, "cone": 1.2},      # the yard's mast searchlights (cold)
    "city": {"seed": 5311,
             "rings": [dict(name="near", r=(300.0, 372.0), h=(22.0, 64.0), w=(12.0, 24.0), neon_p=0.65, win_p=0.36,
                            far=1.0, signs=True),
                       dict(name="mid", r=(400.0, 540.0), h=(40.0, 120.0), w=(16.0, 34.0), neon_p=0.45, win_p=0.32,
                            far=0.7, signs=True),
                       dict(name="far", r=(620.0, 980.0), h=(80.0, 250.0), w=(22.0, 48.0), neon_p=0.35, win_p=0.30,
                            far=0.45, signs=False)],
             "beam_sectors": 8, "beam_ring": "mid", "billboards": 8,
             "sky_lanes": [(700.0, 150.0), (780.0, 182.0), (860.0, 226.0)],
             "perimeter": dict(r=(170.0, 292.0), pylon_step=40.0, pylon_h=12.0, wall_r=292.0, wall_h=5.0),
             "win_p": 0.30, "win_k": 0.20},
    "road": {"plaza": 136.0, "road": (136.0, 162.0), "walk": (162.0, 170.0)},
    "cam": {"pitch_lo": 14.0, "pitch_hi": 24.0, "lens": 30.0, "dmin": 135.0, "fill": (0.56, 0.62),
            "pitch_o": 30.0, "lens_o": 40.0, "fill_o": (0.95, 0.90), "ov_yaw": 150.0, "ov_centre": (0.0, 8.0, 26.0)},
    "post": {"black": 0.04, "exposure_zoom_k": 0.40},
}

PRESET["hq_fog"] = {
    "peak": 0.0065, "base": 0.10, "height_scale": 60.0, "floor": 10.0,
    "box": (-1100.0, -1100.0, 0.0, 1100.0, 1100.0, 300.0),
    "layer_scales": ((0.004, 0.012, 0.075), (0.009, 0.02, 0.33)), "layer_mix": 0.62, "layer_remap": (0.47, 0.64),
    "clump_scale": (0.0075, 0.014, 0.022), "clump_remap": (0.40, 0.62),
    "calm": {"r": 112.0, "soft": 45.0, "k": 0.35},
    "bank": {"r": (100.0, 180.0), "z": (0.0, 9.0), "peak": 0.012},
    "haze": 0.0003, "aniso": 0.45, "colour": (0.88, 0.84, 1.0),
}

PRESET["post"].update({"exposure": 2.4})
PRESET.setdefault("lod_bands", {
    "fog_octaves_by_zoom": (0.25, 0.60), "wisps_on_at": (0.45, 0.70), "plumes_on_at": (0.50, 0.72),
    "signage_on_at": (0.60, 0.82), "small_lights_on_at": (0.75, 0.92), "puddles_sharp_at": (0.85, 1.00),
})


def pal(name):
    if not isinstance(name, str):
        return name
    if name in PRESET["hq"]["palette"]:
        return PRESET["hq"]["palette"][name]
    return PRESET["palette"][name]
