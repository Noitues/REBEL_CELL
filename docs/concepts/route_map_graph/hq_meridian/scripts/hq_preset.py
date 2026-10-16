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
    "out_big": r"D:\rc_scratch\hq_rev\meridian",       # v2 revision (2026-10-15 review); v1 passes stay in hq_meridian
    "suffix": "_v2", "reveal_name": "H_orbit",            # v2: the HQ clip is the orbit round the NE corner
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
        # v2 (review 2026-10-15): the route RINGS the fortress; the loop track, the freight platforms and the moat
        # run round all four sides (offsets: BU outside the wall faces)
        "track_off": 20.0, "platform_off": 38.0, "platform_deck": (28.0, 41.0), "moat_off": (45.0, 54.0),
        "car_deck": 2.6,
        # v2 (designer: "a train track leading away"): the loop's FREIGHT LINE out: a junction on the loop's north side,
        # the line north through a portal on the platform, a truss bridge over the moat, a ramp up onto an elevated
        # VIADUCT on piers threading a cleared corridor (over a street of the downtown grid) out of frame toward the port
        # full render: the climb is a 3 % freight grade from the rail yard (y 150) out; deck_z (73.7) is reached off frame
        "viaduct": {"x": 66.0, "y0": 80.0, "ramp": (150.0, 2607.0), "deck_z": 73.7, "grade": 0.03, "end_y": 1180.0, "w": 9.0,
                    "pier_step": 24.0, "mast_step": 36.0},
        # the slewing KEEP CRANE in the yard (the bible's crane keep, now able to reach all four walls)
        "crane": {"x": 14.0, "y": 6.0, "z": 86.0, "jib": 128.0, "counter": 36.0, "mast": 7.0, "lift_z": 42.0},
        "control": {"c": (-30.0, -10.0), "half": 15.0, "h": 66.0, "m1_z": 30.0},   # MANIFEST CONTROL (the server)
        "gate_u": -36.0,                                                   # the gatehouse on the west wall (course 0)
        "start": (-150.0, -36.0),
        # the ring route: name, wall, u (BU along the wall in the run direction: clockwise from above), course
        "rooms": [("w1", "W", -14.0, 1), ("w2", "W", 36.0, 1), ("n1", "N", -42.0, 1), ("n2", "N", 24.0, 1),
                  ("e1", "E", -30.0, 1), ("e2", "E", 30.0, 1), ("s1", "S", -44.0, 1), ("s2", "S", 28.0, 1)],
        # one BREACH per wall (a top-course slot; its shuttle container) between prev and next; the platform room's
        # stair climbs the next corner tower
        "breach": {"W": dict(u=12.0, prev="w1", next="w2", tower="t1"),
                   "N": dict(u=-10.0, prev="n1", next="n2", tower="t2"),
                   "E": dict(u=0.0, prev="e1", next="e2", tower="t3"),
                   "S": dict(u=-10.0, prev="s1", next="s2", tower="t4")},
        "seq": ["w1", "sw", "bw", "qw", "w2", "t1", "n1", "sn", "bn", "qn", "n2", "t2", "e1", "se", "be", "qe", "e2",
                "t3", "s1", "ss", "bs", "qs", "s2", "t4", "m1"],
        "walk_links": [("w2", "t1"), ("t1", "n1"), ("n2", "t2"), ("t2", "e1"), ("e2", "t3"), ("t3", "s1"),
                       ("s2", "t4"), ("t4", "m1")],
        "kinds": {"w1": "router", "sw": "terminal", "bw": "router", "qw": "modem", "w2": "terminal", "t1": "elite",
                  "n1": "router", "sn": "terminal", "bn": "router", "qn": "rack", "n2": "router", "t2": "elite",
                  "e1": "terminal", "se": "terminal", "be": "router", "qe": "modem", "e2": "router", "t3": "elite",
                  "s1": "router", "ss": "terminal", "bs": "router", "qs": "rack", "s2": "terminal", "t4": "elite",
                  "m1": "router"},
        # the run states the stills show (turns: len(walk) - 1)
        "walk_ov": ["start", "w1", "bw", "w2", "t1", "n1"],
        "walk_dec": ["start", "w1", "bw", "w2", "t1", "n1", "sn"],
        "hover_dec": "qn",
        "sheet": {"live": {"walk": ["start", "w1", "bw", "w2", "t1", "n1"]},
                  "transit": {"walk": ["start", "w1", "bw", "w2", "t1", "n1", "sn"], "mt": 6.5},
                  "dead": {"walk": ["start", "w1", "bw", "w2", "t1", "n1", "sn", "qn", "t2", "e1", "se", "qe", "t3",
                                    "s1"]}},
        "orbit": {"walks": [["start", "w1", "bw", "w2", "t1", "n1", "sn", "n2"],
                            ["start", "w1", "bw", "w2", "t1", "n1", "sn", "n2", "t2"],
                            ["start", "w1", "bw", "w2", "t1", "n1", "sn", "n2", "t2", "e1"]]},
        "target_w": 22.0, "target_h": 10.0,
        "max_shortcuts": 0,
    },
    # ------------------------------------------------------------ THE SHUTTLES (v2 proposal: NOTES "v2 revision")
    "mech": {
        "hold": 2,                                           # a shuttle stays 2 turns in the wall, 2 on the train
        "phase": {"N": 3, "S": 1, "E": 0, "W": 2},           # N / S swap on one turn, E / W on the next
        "crane_order": ["N", "E", "S", "W"],                 # the order of the crane's lifts inside one change
        "ov_mt": 5.52, "ov_lifting": "E",                    # the overview: mid-lift (E going to the train)
    },
    "light": {"flood_w": 2.6e4, "flood_cone": 62.0, "uplight_w": 260.0, "room_k": 1.0, "room_w": 3000.0,
              "lockdown_k": 2.0, "sign_k": 0.5, "slit_k": 0.25, "trim_k": 2.2, "cityglow_k": 0.25,
              "city_beam_k": 0.8, "bank_glow": 1.0e4, "shop_w": 900.0, "beacon_w": 2.5e3, "mover_k": 1.6,
              # the landmark rig (designer audit): the compound reads 1.5-2x the local city background
              "seam_k": 2.8, "logo_k": 3.0, "work_w": 10000.0, "tower_flood_w": 1.6e5, "keep_w": 7.0e4,
              "sodium_w": 2500.0, "rail_k": 2.5, "rim_w": 1.5e5, "bank_h": 75.0, "bank_peak": 0.007,
              "bank_box": (-230.0, -270.0, 0.0, 230.0, -120.0, 110.0), "bank_fill_w": 2.5e4,
              "boom_k": 3.0, "hook_spot_w": 1.2e4, "train_run_k": 6.0, "head_w": 3.0e6},
    "beams": {"power": 2.4e7, "cone": 1.2},      # the yard's mast searchlights (cold)
    "bank_glow_cols": ["work", "sodium"],        # v2: the haze bank round the fort lit orange (art director)
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
             "corridor": [(66.0, 100.0, 66.0, 1250.0, 9.0)], "corridor_low": (46.0, 57.7, 50.0, 0.03, 73.7, 16.0, 8.0),   # low rail-side sheds
             "win_p": 0.36, "win_k": 0.34},      # v2: the city mass reads (was 0.30 / 0.20)
    # v2: the dense downtown right up to the compound (hq_kit.downtown); the ring city starts at 300 beyond it
    "downtown": {"seed": 5340, "keep": ("rect", 136.0, 116.0), "street0": 8.0, "cell": 30.0, "street": 7.0,
                 "r_out": 296.0, "h_near": (16.0, 44.0), "h_far": (34.0, 96.0), "tall_p": 0.08, "sign_p": 0.6,
                 "holo_p": 0.07, "trim_p": 0.4, "lamp_step": 15.0, "lamp_lights": 120, "lamp_w": 1800.0,
                 "corridor": [(66.0, 100.0, 66.0, 1250.0, 6.5)], "corridor_low": (40.0, 57.7, 50.0, 0.03, 73.7, 16.0, 8.0)},     # spec: the frontage stays 2 storeys under the deck      # the viaduct's corridor (no building under it)
    "road": {"plaza": 136.0, "road": (136.0, 162.0), "walk": (162.0, 170.0)},
    "cam": {"pitch_lo": 21.0, "pitch_hi": 27.0, "lens": 30.0, "dmin": 135.0, "fill": (0.50, 0.54),
            "pitch_o": 40.0, "lens_o": 36.0, "fill_o": (0.95, 0.92), "ov_yaw": 140.0, "ov_centre": (0.0, 0.0, 20.0)},
    "post": {"black": 0.04, "exposure_zoom_k": 0.40},
}

PRESET["hq_fog"] = {
    "peak": 0.0065, "base": 0.10, "height_scale": 60.0, "floor": 10.0,
    "box": (-1100.0, -1100.0, 0.0, 1100.0, 1100.0, 300.0),
    "layer_scales": ((0.004, 0.012, 0.075), (0.009, 0.02, 0.33)), "layer_mix": 0.62, "layer_remap": (0.47, 0.64),
    "clump_scale": (0.0075, 0.014, 0.022), "clump_remap": (0.40, 0.62),
    "calm": {"r": 96.0, "soft": 30.0, "k": 0.55},
    # v2 (art director: too dark, the blocks read as confetti): an ORANGE-weighted haze bank round the fort (lit from
    # below by the bank glows in work orange / sodium), a neutral haze further out
    "bank": {"r": (128.0, 230.0), "z": (0.0, 24.0), "peak": 0.010},     # t2b: was z 34 / peak 0.018 (median 0.35)
    "haze": 0.0005, "aniso": 0.45, "colour": (0.94, 0.90, 0.88),        # t2b: was 0.0009
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
# MER_SPEC
# T2B_VALUES
# MER_GRADE
