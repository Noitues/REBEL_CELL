"""HQ Rebel Cell: the r3 look preset plus the DISPATCH finale variant (the Cell's own district: the red-window fist,
the canyon, the DISPATCH core; SYNC STRIKE).

Rebel Cell red #E8141E is the TARGET / threat red of the UI: the district keeps it in the windows and the core's
vents; the route keeps the locked state colours.
"""
import copy

import look_preset as _LP

PRESET = copy.deepcopy(_LP.PRESET)
PALETTES = dict(_LP.PALETTES)

PRESET["hq"] = {
    "corp": "rebel_cell", "corp_name": "REBEL_CELL",
    "dossier": ("DISPATCH", "ORDER LOG // NO FEED", (255, 40, 50)),
    "target_name": "DISPATCH CORE", "target_place": "the knuckles",
    "out_big": r"D:\rc_scratch\hq_rev\rebel_cell",     # v2 revision; v1 passes stay in D:\rc_scratch\hq_rebel_cell
    "suffix": "_v2",
    "no_plaza": True,
    "palette": {
        "cell_red": (0.80, 0.007, 0.013),      # #E8141E linear: the fist's windows, the core's vents
        "red_hot": (1.0, 0.05, 0.07),          # DISPATCH red (scripts): the core, the locks
        "pale_pink": (1.0, 0.45, 0.48),        # #FFAAAC-ish: lit edges
        "sodium": (1.0, 0.45, 0.10), "neon_a": (1.0, 0.16, 0.6), "neon_b": (0.16, 0.8, 1.0),
        "panel": (0.30, 0.31, 0.33), "panel_dark": (0.14, 0.14, 0.15), "concrete": (0.16, 0.16, 0.17),
        "glass": (0.02, 0.02, 0.03), "lockdown": (1.0, 0.05, 0.08), "gold": (1.0, 0.62, 0.12), "scan": (1.0, 0.3, 0.3),
    },
    "compound": {
        "room_w": 14.0, "room_h": 8.0, "room_d": 10.0,
        # the Cell's district (bible 4.4 / round 34): a normal street grid over the fist's box; NO landmark tower
        "fist": {"x": (-175.0, 175.0), "y": (-70.0, 290.0), "cell": 12.0, "street": 3.0, "seed": 8320,
                 "ring": (205.0, 235.0)},          # the blackout ring (round 34): blocks this far from the fist centre
        "palm": (0.0, 150.0), "dispatch_z": 30.0,  # DISPATCH: a plain building at the fist's palm (its roof shack)
        "runners": {"L": "BREAKER", "C": "GHOST", "R": "RIGGER"},
        "tint": {"L": (255, 70, 170), "C": (90, 230, 255), "R": (120, 255, 150)},   # per-operative accent (token,
                                                                                    # wax edge), never a state colour
        "kinds": {"L1": "router", "L2": "elite", "L2a": "terminal", "L2b": "router", "L3": "router",
                  "C1": "terminal", "C2": "router", "C3": "elite",
                  "R1": "modem", "R2": "router", "R2a": "router", "R2b": "modem", "R3": "elite",
                  "LK": "switch", "CK": "switch", "RK": "switch"},
        # option C (converging): rooms (x, y, z) on the west roofs, the south street, the east roofs; all open south
        "conv": {"rooms": {"L1": (-150.0, 150.0, 30.0), "L2": (-110.0, 162.0, 38.0), "L2a": (-122.0, 118.0, 26.0),
                           "L2b": (-92.0, 122.0, 32.0), "L3": (-72.0, 150.0, 40.0), "LK": (-40.0, 150.0, 44.0),
                           "C1": (0.0, 10.0, 0.4), "C2": (0.0, 50.0, 0.4), "C3": (0.0, 88.0, 0.4), "CK": (0.0, 118.0, 0.4),
                           "R1": (150.0, 150.0, 28.0), "R2": (110.0, 162.0, 36.0), "R2a": (122.0, 118.0, 26.0),
                           "R2b": (92.0, 122.0, 30.0), "R3": (72.0, 150.0, 38.0), "RK": (40.0, 150.0, 42.0)}},
        # option A (stacked lanes, side view): the section cut at y = cut; lanes at three heights, switches at x_switch
        # (the cut is a street line of the real block grid: blocks start at fist.x0 - 90 every `cell`)
        "stack": {"cut": 104.0, "x0": -170.0, "dx": 44.0, "z": {"L": 34.0, "C": 0.4, "R": -24.0},
                  "roofs": {"1": 30.0, "2": 36.0, "3": 32.0, "2a": 46.0, "2b": 48.0, "K": 38.0},
                  "x_switch": -36.0, "dispatch_x": 4.0, "dispatch_z": 14.0, "earth": -120.0,
                  "alley_w": 18.0},     # v2: the alley's width; its kerb is the section face (the tunnel sits in it)
        "start": (0.0, -60.0),
        "max_shortcuts": 0,
    },
    "mech": {"countered": ["C2"], "stall": 1},
    "light": {"room_k": 1.0, "room_w": 2800.0, "lockdown_k": 2.0, "sign_k": 0.5, "trim_k": 2.4, "cityglow_k": 0.12,
              "city_beam_k": 0.7, "bank_glow": 2500.0, "shop_w": 900.0, "flood_w": 2.4e4,
              # the windows (the review: the red is SUBTLE until the blackout, then spreads through the fist)
              "win_k": 0.85, "win_p": 0.36, "red_before_p": 0.08, "red_before_k": 0.5, "red_k": 0.8, "red_full_p": 0.85,
              "wash_k": 3.0, "spread_r": 230.0, "pulse_k": 2.5, "rim_w": 8.0e4, "key_w": 3.0e4, "sod_w": 2500.0,
              # v2: the alley canyon's own lights + the district's street strips (the red-sequence fix: light)
              "mf_spill_w": 6000.0, "alley_lamp_w": 2600.0, "fist_spill_w": 9000.0, "holo_spill_w": 1200.0,
              "stall_w": 700.0, "room_warm_w": 900.0, "fist_glow_w": 2.0e4, "uc_wash_w": 6000.0,
              "strip_w": 9.0e3, "strip_every": 1, "strip_seg": 90.0, "section_key_k": 0.8},
    "beams": {"power": 2.4e7, "cone": 1.1},
    "bank_glow_cols": ["cell_red", "sodium"],
    "city": {"seed": 8311,
             "rings": [dict(name="near", r=(320.0, 392.0), h=(30.0, 80.0), w=(12.0, 24.0), neon_p=0.5, win_p=0.3,
                            far=0.8, signs=True),
                       dict(name="mid", r=(420.0, 560.0), h=(50.0, 140.0), w=(16.0, 34.0), neon_p=0.4, win_p=0.28,
                            far=0.6, signs=True),
                       dict(name="far", r=(640.0, 980.0), h=(80.0, 250.0), w=(22.0, 48.0), neon_p=0.3, win_p=0.26,
                            far=0.4, signs=False)],
             "beam_sectors": 8, "beam_ring": "mid", "billboards": 8,
             "sky_lanes": [(700.0, 150.0), (780.0, 182.0), (860.0, 226.0)],
             "perimeter": None, "win_p": 0.26, "win_k": 0.26},
    "road": {"plaza": 300.0, "road": (300.0, 318.0), "walk": (318.0, 320.0)},
    # option A: the side view (the V3 dollhouse, nearly level) at the section
    # v2 r2: the camera looks down onto the undercroft's floor (pitch was 11 / 12-14)
    "cam": {"pitch_lo": 17.0, "pitch_hi": 19.0, "lens": 30.0, "dmin": 120.0, "fill": (0.74, 0.74),
            "pitch_o": 17.0, "lens_o": 30.0, "fill_o": (0.95, 0.92), "ov_yaw": 0.0, "ov_centre": (-80.0, 104.0, 14.0)},
    "post": {"black": 0.04, "exposure_zoom_k": 0.40},
}

import os as _os
if _os.environ.get("HQ_VARIANT", "A") == "A" and not _os.environ.get("HQ_DISTRICT_ONLY"):
    _S = PRESET["hq"]["compound"]["stack"]
    PRESET["hq"]["ground_cut_y"] = _S["cut"] + 0.6 - _S["alley_w"]          # the section: no ground in front of the kerb
if _os.environ.get("HQ_DISTRICT_ONLY"):                                        # the red sequence: the whole district
    PRESET["hq"]["cam"].update({"pitch_o": 62.0, "ov_centre": (0.0, 110.0, 20.0)})

PRESET["hq_fog"] = {
    "peak": 0.0065, "base": 0.10, "height_scale": 60.0, "floor": 10.0,
    "box": (-1100.0, -1100.0, 0.0, 1100.0, 1100.0, 300.0),
    "layer_scales": ((0.004, 0.012, 0.075), (0.009, 0.02, 0.33)), "layer_mix": 0.62, "layer_remap": (0.47, 0.64),
    "clump_scale": (0.0075, 0.014, 0.022), "clump_remap": (0.40, 0.62),
    "calm": {"r": 140.0, "soft": 45.0, "k": 0.40},
    "bank": {"r": (190.0, 300.0), "z": (0.0, 12.0), "peak": 0.012},
    "haze": 0.0003, "aniso": 0.45, "colour": (0.95, 0.85, 0.9),
}

# v2 (art director): no lit fog plane in front of the section: the fog starts at the kerb (thin, dark low strata
# behind it); the red-sequence build gets low strata + a soft haze so the red glow bleeds into the air
if _os.environ.get("HQ_VARIANT", "A") == "A" and not _os.environ.get("HQ_DISTRICT_ONLY"):
    _S = PRESET["hq"]["compound"]["stack"]
    PRESET["hq_fog"]["box"] = (-1100.0, _S["cut"] + 0.6 - _S["alley_w"] - 1.0, 0.0, 1100.0, 1100.0, 300.0)
if _os.environ.get("HQ_DISTRICT_ONLY"):
    PRESET["hq_fog"].update({"peak": 0.011, "height_scale": 28.0, "floor": 3.0, "haze": 0.0009})
    PRESET["hq"]["post"] = dict(PRESET["hq"]["post"], bloom=(0.20, 0.17, 0.13), bloom_thr=0.9)   # v2 r2: slight bloom on the red fist
    PRESET["hq"]["light"]["fist_glow_w"] = 4.5e4      # full render (art director): the red glow visibly tints the air
    PRESET["hq_fog"].update({"peak": 0.013, "haze": 0.0011})
# v2: room interiors in the alley look (the kit's room shell reads these)
PRESET["hq"]["room_inner"] = (0.17, 0.14, 0.15)
PRESET["hq"]["room_strip"] = (1.0, 0.72, 0.45)
PRESET["hq"]["compound"]["fist"]["mask"] = "fist_mask_v2.json"      # the crest fist outline (rc_fist_v2.py)

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
# RC_R2B
