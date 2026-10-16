"""HQ Meridian v3: the r3 look preset plus the Meridian v3 variant: THE GATEHOUSE GANTRY (DESIGN.md).

The kit (hqk_*.py, hq_scene / hq_cam / hq_overlay / hq_post / hq_compose / hq_jobs) reads PRESET["hq"] and
PRESET["hq_fog"]; the street look itself stays look_preset.PRESET (r3, unchanged). Units: HQ kit BU (1 storey = 8 BU;
the pipeline rescales by k_units 0.2375). North = +y. The map lot is |x|, |y| <= 120.
    import hq_preset as HP; P = HP.PRESET; H = P["hq"]
"""
import copy

import look_preset as _LP
import meridian_rail as _MR

PRESET = copy.deepcopy(_LP.PRESET)
PALETTES = dict(_LP.PALETTES)

# the GATEHOUSE GANTRY's numbers (hq_graph / meridian_landmark read PRESET['hq']['compound'])
_CP = {
    "room_w": 14.0, "room_h": 8.0, "room_d": 10.0, "course": 9.0,
    "lot": 120.0,                                              # the map lot's half size: the HQ fills it
    "wall": {"t": 14.0, "courses": 4, "merlon_h": 4.6},       # container curtain walls (outer face on the lot)
    # v3 t2 (coordinator Q6): EVERYTHING inside the lot: towers, gatehouses and the rail-gate turrets stand inside
    # the outer faces (no bastions beyond |x|, |y| = 120)
    "ew_y": (-120.0, 86.0),                                    # the E / W walls (the gantry runways) run S -> N
    "corner": {"half": 14.0, "h": 56.0},                       # the S corner towers (inside the lot corners)
    # the RAIL GATES: the runway wall bridges both tracks (y0 .. the lot edge) on one big stepped arch; drum turrets
    # on its inner side
    "railgate": {"y0": 86.0, "arch": (89.0, 114.0), "arch_h": 26.0, "drum_r": 4.5, "drum_h": 58.0},
    "gate": {"half": 9.0, "h": 52.0, "arch_h": 15.0, "tower": (7.0, 12.0), "s_x": 0.0, "ew_y": -30.0},
    # the freight line (meridian_rail.py): two tracks along the N edge, then the city polyline to the port
    "rail": {"y": (96.0, 107.0), "x_east": 1250.0, "ease_len": 110.0, "train_x": (-96.0, 196.0),
             "json": r"D:\rc_scratch\city_all_corps\meridian_rail.json", "k_units": 0.2375,
             "deck_w": 20.0, "pier_step": 24.0},
    "quay": (70.0, 89.5),
    "lane": {"s_y": -97.0, "ew_x": 96.0, "n_end": 66.0},       # the inner truck lanes
    "yard": (-78.0, 76.0, -80.0, 62.0),                        # the bailey's container stacks x0 x1 y0 y1
    # the keep is PARKED for every shot (coordinator Q3: riding the crane is flavour)
    # round 2 (designer): parked mid-north, so the span stands just S of the train (the train reads in the bay beside
    # it); the TARGET is the keep: a body to keep_top, then the open LANTERN (the server inside), a cap, turret spires
    "gantry": {"y": 70.0, "leg": (7.0, 20.0), "leg_top": 142.0, "span_z": (104.0, 122.0), "span_half": 9.0,
               "keep_x": -50.0, "keep": (16.0, 13.0), "keep_top": 148.0, "lantern": (10.0, 8.5, 15.0), "hook_z": 45.0},
    # round 2 (designer): the truck RING ROAD round the lot (multi-lane, queues, lit cabs) and three highway on-ramps
    # (one per truck gate) for the city's highways to hub on: r = the ring's inner / outer kerb (|x| or |y|)
    "ring": {"r": (122.0, 158.0), "lanes": 6, "exits": [("S", "S", 0.0), ("W", "W", -30.0), ("E", "E", -30.0)],
             "ramp": 170.0, "deck_z": 40.0, "deck_w": 26.0, "reach": 1150.0, "pier_step": 30.0},
    "start": (-62.0, -121.0),                                  # the Cell's hack box: on the kerb by the queue
    "target_w": 16.0, "target_h": 8.0,
    "max_shortcuts": 0,
    # the illustrative run (rooms are SLOTS; the topology belongs to the game graph): id -> slot
    "walk_ov": ["start", "gs", "s2", "te", "o1"],
    "walk_dec": ["start", "gs", "s2", "te", "o1", "o2"],
}

PRESET["hq"] = {
    "corp": "meridian", "corp_name": "MERIDIAN FREIGHT",
    "dossier": ("MERIDIAN", "FREIGHT SECURITY", (255, 140, 26)),
    "target_name": "THE MASTER MANIFEST", "target_place": "THE KEEP",
    "out_big": r"D:\rc_scratch\meridian_v3",
    "suffix": "_v3", "reveal_name": "H_reveal",
    # ------------------------------------------------------------ palette (linear RGB)
    "palette": {
        "steel": (0.075, 0.037, 0.024),
        "steel_alt": [(0.078, 0.032, 0.021), (0.035, 0.046, 0.056), (0.07, 0.049, 0.025), (0.052, 0.021, 0.021),
                      (0.025, 0.035, 0.032)],    # the container courses: rust, navy, ochre, oxblood, green-grey
        "gantry": (0.30, 0.075, 0.022),          # v3 t2 (coordinator Q5): RUST-ORANGE paint (albedo), not the route orange
        "edge": (1.0, 0.80, 0.52),               # v3 t2: the lit edges / stencil: sodium-white
        "stone": (0.085, 0.075, 0.07),           # the gatehouses' and towers' dark cast concrete (the masonry)
        "keep": (0.20, 0.19, 0.18),              # the trolley keep's cladding
        "corp_orange": (1.0, 0.26, 0.012),       # #FF8C1A linear: the sign, seams, the span's lit edge
        "corp_red": (1.0, 0.027, 0.02),          # beacons, the gate lamps
        "yard_white": (1.0, 0.86, 0.66),
        "yard_cool": (0.62, 0.84, 1.0),
        "hazard": (1.0, 0.55, 0.02),
        "panel": (0.30, 0.31, 0.33), "panel_dark": (0.16, 0.16, 0.17),
        "glass": (0.015, 0.03, 0.035), "concrete": (0.20, 0.20, 0.21),
        "lockdown": (1.0, 0.05, 0.08), "gold": (1.0, 0.62, 0.12),
        "scan": (1.0, 0.82, 0.55),
        "sodium": (1.0, 0.42, 0.09),
        "work": (1.0, 0.30, 0.04),
        "train": (0.15, 0.16, 0.19),             # round 2: graphite livery, so the lit window band reads
        "train_light": (0.55, 0.85, 1.0),        # its cold running light
    },
    # ------------------------------------------------------------ THE GATEHOUSE GANTRY (hq_graph / hq_build read these)
    "compound": _CP,
    "mech": {},
    "light": {"flood_w": 2.6e4, "flood_cone": 62.0, "uplight_w": 260.0, "room_k": 1.0, "room_w": 3000.0,
              "lockdown_k": 2.0, "sign_k": 0.5, "slit_k": 0.25, "trim_k": 2.2, "cityglow_k": 0.25,
              "city_beam_k": 0.8, "bank_glow": 1.0e4, "shop_w": 900.0, "beacon_w": 2.5e3,
              # the landmark rig (designer: the landmark ~2x its local background)
              "seam_k": 3.0, "logo_k": 3.5, "leg_up_w": 9.0e4, "span_down_w": 2.8e4, "keep_wash_w": 6.0e4,
              "gate_w": 2.0e4, "sodium_w": 3000.0, "rail_k": 2.5, "rim_w": 2.0e5, "train_k": 8.0, "head_w": 2.0e6,
              "truck_w": 1500.0, "wash_w": 9000.0,
              "lane_w": 9000.0, "train_area_w": 8.0e3, "cab_k": 3.0,
              "ring_w": 6.0e3, "lantern_w": 5000.0, "keep_key_w": 5.0e4, "streak_k": 3.0},
    "beams": {"power": 2.4e7, "cone": 1.2},
    "bank_glow_cols": ["work", "sodium"],
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
             # the high-speed line E-W along the north edge, through the whole city
             "corridor": _MR.segments(_CP, 16.0) + _MR.highway_segments(_CP, 18.0), "corridor_low": (34.0, 12.0),
             "win_p": 0.36, "win_k": 0.34},
    # the dense downtown right up to the lot (hq_kit.downtown): the first block face 8 BU beyond the lot edge
    "downtown": {"seed": 5340, "keep": ("rect", 158.0, 158.0), "street0": 3.0, "cell": 30.0, "street": 7.0,
                 "r_out": 296.0, "h_near": (16.0, 44.0), "h_far": (34.0, 96.0), "tall_p": 0.08, "sign_p": 0.6,
                 "holo_p": 0.07, "trim_p": 0.4, "lamp_step": 15.0, "lamp_lights": 120, "lamp_w": 1800.0,
                 "corridor": _MR.segments(_CP, 13.0) + _MR.highway_segments(_CP, 16.0), "corridor_low": (34.0, 12.0),
                 # the occlusion rule, tuned for a lot-filling HQ whose route rooms sit on its outer faces: a tighter
                 # vertical margin, so 1-storey stubs across the street are cut, not ghosted
                 "occ": {"margin": 0.03, "vsoft": 0.012}},
    "road": {"plaza": 121.0, "road": (122.0, 158.0), "walk": (158.0, 161.0)},
    "cam": {"pitch_lo": 21.0, "pitch_hi": 27.0, "lens": 30.0, "dmin": 135.0, "fill": (0.50, 0.54),
            "pitch_o": 38.0, "lens_o": 36.0, "fill_o": (0.90, 0.85), "ov_yaw": 35.0, "ov_centre": (0.0, 0.0, 34.0)},   # round 2c: from the SW, high 3/4
    "post": {"black": 0.04, "exposure_zoom_k": 0.55},
}

PRESET["hq_fog"] = {
    "peak": 0.0065, "base": 0.10, "height_scale": 60.0, "floor": 10.0,
    "box": (-1100.0, -1100.0, 0.0, 1100.0, 1100.0, 300.0),
    "layer_scales": ((0.004, 0.012, 0.075), (0.009, 0.02, 0.33)), "layer_mix": 0.62, "layer_remap": (0.47, 0.64),
    "clump_scale": (0.0075, 0.014, 0.022), "clump_remap": (0.40, 0.62),
    "calm": {"r": 130.0, "soft": 30.0, "k": 0.45},                    # calm over the lot: the landmark stays crisp
    "bank": {"r": (150.0, 260.0), "z": (0.0, 24.0), "peak": 0.008},
    "haze": 0.0005, "aniso": 0.45, "colour": (0.94, 0.90, 0.88),
}

PRESET["post"].update({"exposure": 2.85})
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
