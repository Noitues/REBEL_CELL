"""Aurelian HQ (THE CIRCUS AURELIUS, concept B LOGGIA AND CAVEA): the corp preset for the HQ-kit engine.

The engine (hq_scene / hq_jobs / hq_cam / hq_overlay / hq_post / hq_compose / hqk_graph, look_preset) is Meridian v3's,
imported in place from ../../hq_meridian_v3/scripts (no copies; see hq_run.py). The kit is hq_meridian/scripts/hq_kit.
Units: HQ kit BU (1 storey = 8 BU); the canonical model is authored in city units and scaled by 1 / k_units (4.21).
    import hq_preset as HP; P = HP.PRESET; H = P["hq"]
"""
import copy
import os
import sys

_V3 = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "hq_meridian_v3", "scripts"))
if _V3 not in sys.path:
    sys.path.append(_V3)
import look_preset as _LP  # noqa: E402

KS = 1.0 / 0.2375
PRESET = copy.deepcopy(_LP.PRESET)
PALETTES = dict(_LP.PALETTES)

# the compound numbers the engine reads (hq_scene: room_w / room_h / room_d); the landmark's own are in
# aurelian_landmark (canonical, city units)
_CP = {"room_w": 3.3 * KS, "room_h": 1.9 * KS, "room_d": 2.4 * KS,
       "lot": (36.0 * KS, 30.0 * KS),                      # the LANDMARK_FP ellipse semi-axes (kit BU)
       "max_shortcuts": 0}

PRESET["hq"] = {
    "corp": "aurelian", "corp_name": "AURELIAN CONCORD",
    "dossier": ("AURELIAN", "CONCORD CIVIC SECURITY", (41, 219, 166)),
    "target_name": "THE CONCORDAT VAULT", "target_place": "THE ROSTRUM",
    "out_big": r"D:\rc_scratch\aurelian\big",
    "suffix": "_test", "reveal_name": "H_reveal",
    # ------------------------------------------------------------ palette (linear RGB)
    "palette": {
        "travertine": (0.86, 0.78, 0.62),       # DISTRICTS.aurelian.mat[0] (canonical)
        "gilt": (0.788, 0.639, 0.353),          # DISTRICTS.aurelian.sec (canonical neon)
        "loggia": (1.0, 0.76, 0.42),            # the canonical lit-arch colour (wc)
        "uplight": (1.0, 0.86, 0.66),           # the canonical warm flood colour
        "cavea_fill": (1.0, 0.90, 0.76),
        "server": (1.0, 0.78, 0.40),
        "rim_a": (0.161, 0.859, 0.651),         # verdigris: light only, never paint (identity colours unchanged)
        "rim_b": (1.0, 0.80, 0.55),
        "district_a": (0.161, 0.859, 0.651),    # the Aurelian district's neon around the lot
        "district_b": (0.788, 0.639, 0.353),
        "accent_warm": (1.0, 0.58, 0.18), "accent_cool": (0.45, 0.62, 1.0),
        "lockdown": (1.0, 0.05, 0.08), "gold": (1.0, 0.62, 0.12), "scan": (1.0, 0.82, 0.55),
        "sodium": (1.0, 0.42, 0.09), "work": (1.0, 0.62, 0.30),
        "glass": (0.015, 0.03, 0.035), "concrete": (0.20, 0.20, 0.21),
        "panel": (0.30, 0.31, 0.33), "panel_dark": (0.16, 0.16, 0.17),
    },
    "compound": _CP,
    "mech": {},
    # ------------------------------------------------------------ the landmark rig (DESIGN.md section 6)
    "light": {"room_k": 1.0, "room_w": 2600.0, "shop_w": 900.0, "bank_glow": 1.0e4, "cityglow_k": 0.25,
              "city_beam_k": 0.8,
              "gilt_k": 0.6, "loggia_k": 0.35, "cove_k": 0.35, "server_k": 4.0, "flood_k": 0.006,
              "up_n": 24, "up_w": 450.0, "cavea_w": 2.5e3, "vault_key_w": 4.0e3, "rim_w": 9.0e3,
              # round 2 test fixes: the city lift (block uplights, light-linked to city + ground), per-frame multipliers
              "transparent_bounces": 128, "fill_n": 40, "fill_w": 25000.0, "camfill_w": 28000.0, "fill_cone": 95.0,
              "up_frame": {"H_decision": 1.0}, "fill_frame": {"H_overview": 0.6, "H_decision_cavea": 0.5},
              "camfill_frame": {"H_overview": 0.6, "H_decision_cavea": 0.5},
              "ov_loggia": 0.70, "ov_laurel": 0.60},
    "beams": {"power": 2.4e7, "cone": 1.2},
    "bank_glow_cols": ["work", "sodium"],
    "city": {"seed": 7311,
             "rings": [dict(name="near", r=(560.0, 660.0), h=(90.0, 200.0), w=(18.0, 34.0), neon_p=0.65, win_p=0.36,
                            far=1.0, signs=True),
                       dict(name="mid", r=(700.0, 900.0), h=(120.0, 260.0), w=(22.0, 40.0), neon_p=0.45, win_p=0.32,
                            far=0.7, signs=True),
                       dict(name="far", r=(960.0, 1300.0), h=(160.0, 320.0), w=(26.0, 52.0), neon_p=0.35, win_p=0.30,
                            far=0.45, signs=False)],
             "beam_sectors": 8, "beam_ring": "mid", "billboards": 8,
             "sky_lanes": [(900.0, 260.0), (1000.0, 300.0), (1100.0, 340.0)],
             "perimeter": None, "corridor": [], "corridor_low": (34.0, 12.0),
             "win_p": 0.36, "win_k": 0.55},
    # the dense downtown to the lot edge (hq_kit.downtown; spec 8.2): the city near the circus is tall (city median
    # about 34 BU = 143 kit), so the bowl is a low landmark the city looks down into; the occlusion rule clears views
    "downtown": {"seed": 7340, "keep": ("rect", 36.0 * KS, 30.0 * KS), "street0": 40.0, "cell": 30.0, "street": 7.0,
                 "r_out": 540.0, "h_near": (30.0, 90.0), "h_far": (90.0, 200.0), "tall_p": 0.10, "sign_p": 0.6,
                 "holo_p": 0.07, "trim_p": 0.4, "lamp_step": 15.0, "lamp_lights": 120, "lamp_w": 1800.0,
                 "corridor": [], "corridor_low": (34.0, 12.0), "occ": {"margin": 0.10}, "mast_pad": 8.0},
    "road": {"plaza": 36.0 * KS, "road": (36.0 * KS + 1.0, 36.0 * KS + 4.0), "walk": (36.0 * KS + 4.0, 36.0 * KS + 6.0)},
    "no_plaza": True,
    "cam": {"pitch_lo": 30.0, "pitch_hi": 34.0, "lens": 30.0, "dmin": 135.0, "fill": (0.56, 0.62), "dmin_loggia": 260.0, "lens_loggia": 42.0,
            "pitch_lo_cav": 26.0, "pitch_hi_cav": 36.0,
            "pitch_o": 36.0, "lens_o": 36.0, "fill_o": (0.97, 0.94), "ov_yaw": 20.0, "ov_centre": (0.0, 6.0, 30.0)},
    "post": {"black": 0.04, "exposure": 1.6, "exposure_zoom_k": 0.0},
    "frame_stops": {"H_overview": -0.08, "H_decision": -0.45, "H_decision_cavea": -0.30},       # per-frame exposure trim in stops (the cavea frame is the brightest)
}

PRESET["hq_fog"] = {
    "peak": 0.0055, "base": 0.10, "height_scale": 60.0, "floor": 10.0,
    "box": (-1400.0, -1400.0, 0.0, 1400.0, 1400.0, 360.0),
    "layer_scales": ((0.004, 0.012, 0.075), (0.009, 0.02, 0.33)), "layer_mix": 0.62, "layer_remap": (0.47, 0.64),
    "clump_scale": (0.0075, 0.014, 0.022), "clump_remap": (0.40, 0.62),
    "calm": {"r": 170.0, "soft": 40.0, "k": 0.45},                    # calm over the lot: the landmark stays crisp
    "bank": {"r": (190.0, 320.0), "z": (0.0, 24.0), "peak": 0.007},
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
