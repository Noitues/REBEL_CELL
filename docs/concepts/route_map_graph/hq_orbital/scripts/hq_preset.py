"""HQ Orbital: the r3 look preset plus the Orbital variant (the launch complex, the missile loop, the silo doors).

Orbital ice white #CDF0FF sits next to the UI's text white: the complex carries it in material (pale steel, ice-blue
glass, the ringed-planet crest) and in light; the overlay keeps the locked state colours.
"""
import copy

import look_preset as _LP

PRESET = copy.deepcopy(_LP.PRESET)
PALETTES = dict(_LP.PALETTES)

PRESET["hq"] = {
    "corp": "orbital", "corp_name": "ORBITAL COMMONS",
    "dossier": ("ORBITAL", "LAUNCH SECURITY", (205, 240, 255)),
    "target_name": "LAUNCH CONTROL", "target_place": "the service gantry",
    "out_big": r"D:\rc_scratch\hq_orbital",
    "palette": {
        "ice": (0.61, 0.87, 1.00),            # #CDF0FF linear: the corp light (work lights, dish rims, the crest)
        "steel": (0.30, 0.33, 0.37),          # pale steel (albedo)
        "caution": (1.0, 0.62, 0.0),          # the yellow-black caution ring on the silo rim
        "launch": (1.0, 0.30, 0.06),          # the shaft's launch glow (hot orange-red)
        "marker": (1.0, 0.04, 0.03),          # red marker lights (closed doors, masts)
        "panel": (0.40, 0.43, 0.46), "panel_dark": (0.18, 0.20, 0.22), "concrete": (0.24, 0.25, 0.26),
        "glass": (0.02, 0.04, 0.06), "lockdown": (1.0, 0.05, 0.08), "gold": (1.0, 0.62, 0.12),
        "scan": (0.8, 0.95, 1.0), "sodium": (1.0, 0.45, 0.10),
    },
    "compound": {
        "room_w": 14.0, "room_h": 8.0, "room_d": 10.0,
        "ring_r": 96.0,                        # the stations' ring (bunker openings face out)
        "podium_r": 64.0, "podium_h": 10.0,    # the launch podium; the silo is its centre
        "silo_r": 17.0,
        "stations": [("start", 180.0, "PAD"), ("se", 120.0, "SE DISH"), ("ne", 60.0, "NE DISH"),
                     ("nw", 300.0, "NW DISH"), ("sw", 240.0, "SW DISH")],
        # the ANTENNA (designer review 2026-10-15): a truss tower with real decks; two enclosed ELITE rooms on it
        "antenna": {"az": 0.0, "r": 104.0, "half": 9.0, "h": 104.0, "decks": [26.0, 52.0, 78.0],
                    "rooms": [("ant1", 26.0), ("ant2", 52.0)]},
        "rocket": {"r": 6.0, "h": 58.0, "raise": 62.0},          # body radius, body height, raised offset
        "control": {"y": -38.0},                                 # LAUNCH CONTROL deck on the gantry (the TARGET)
        "kinds": {"se": "router", "ne": "modem", "ant1": "elite", "ant2": "elite", "nw": "terminal", "sw": "router",
                  "rocket": "rack"},
        "max_shortcuts": 1,
    },
    # THE RETARGET CYCLE (designer review 2026-10-15 on round 43's missile loop; proposal): a CIRCUIT walks the ring
    # (the antenna's two elite rooms included); at its end the bay doors OPEN, the rocket rises and the Cell RETARGETS
    # it (it strikes an Orbital facility in the city / in orbit). After `retargets` circuits the antenna top unlocks the
    # LAUNCH OVERRIDE: a shortcut to LAUNCH CONTROL that fires the rocket one round early into the SHUT doors (the HQ is
    # destroyed: the run is won). `circuit` = the circuit shown by the stills (preset per shot).
    "mech": {"circuit": 4, "retargets": 3},
    "light": {"room_k": 1.0, "room_w": 3000.0, "lockdown_k": 2.0, "sign_k": 0.5, "trim_k": 2.4, "cityglow_k": 0.15,
              "city_beam_k": 0.8, "bank_glow": 3200.0, "shop_w": 900.0, "flood_w": 3.0e4, "dish_k": 3.0,
              "shaft_w": 8.0e4, "rim_w": 1.2e5, "key_w": 6.0e4, "halo_r": (180.0, 290.0), "halo_h": 110.0,
              "halo_peak": 0.010, "halo_fill_w": 4.5e4, "marker_k": 14.0,
              "svc_w": 2.5e4, "pad_flood_w": 2.5e4, "room_key_w": 9000.0, "underfog_w": 1.5e4,
              # the launch cutscene (H_launch_board): the Orbital facility struck in the city, the trail, the blast
              "strike": {"at": (430.0, 520.0), "apex": 260.0, "glow_w": 6.0e4, "trail_k": 6.0, "boom_w": 4.0e6}},
    "beams": {"power": 2.6e7, "cone": 1.1},
    "bank_glow_cols": ["ice", "sodium"],
    "city": {"seed": 7311,
             "rings": [dict(name="near", r=(300.0, 372.0), h=(22.0, 64.0), w=(12.0, 24.0), neon_p=0.5, win_p=0.36,
                            far=1.0, signs=True),
                       dict(name="mid", r=(400.0, 540.0), h=(40.0, 120.0), w=(16.0, 34.0), neon_p=0.4, win_p=0.32,
                            far=0.7, signs=True),
                       dict(name="far", r=(620.0, 980.0), h=(80.0, 250.0), w=(22.0, 48.0), neon_p=0.3, win_p=0.30,
                            far=0.45, signs=False)],
             "beam_sectors": 8, "beam_ring": "mid", "billboards": 8,
             "sky_lanes": [(700.0, 150.0), (780.0, 182.0), (860.0, 226.0)],
             "perimeter": dict(r=(170.0, 292.0), pylon_step=40.0, pylon_h=6.0, wall_r=292.0, wall_h=4.0),
             "win_p": 0.30, "win_k": 0.20},
    "road": {"plaza": 136.0, "road": (136.0, 162.0), "walk": (162.0, 170.0)},
    "cam": {"pitch_lo": 16.0, "pitch_hi": 26.0, "lens": 30.0, "dmin": 110.0, "fill": (0.56, 0.62),
            "pitch_o": 46.0, "lens_o": 36.0, "fill_o": (0.92, 0.90), "ov_yaw": 150.0, "ov_centre": (0.0, 0.0, 20.0)},
    "post": {"black": 0.04, "exposure_zoom_k": 0.40},
}

PRESET["hq_fog"] = {
    "peak": 0.0060, "base": 0.10, "height_scale": 60.0, "floor": 10.0,
    "box": (-1100.0, -1100.0, 0.0, 1100.0, 1100.0, 300.0),
    "layer_scales": ((0.004, 0.012, 0.075), (0.009, 0.02, 0.33)), "layer_mix": 0.62, "layer_remap": (0.47, 0.64),
    "clump_scale": (0.0075, 0.014, 0.022), "clump_remap": (0.40, 0.62),
    "calm": {"r": 125.0, "soft": 45.0, "k": 0.35},
    "bank": {"r": (125.0, 175.0), "z": (0.0, 9.0), "peak": 0.012},
    "haze": 0.0003, "aniso": 0.45, "colour": (0.85, 0.9, 1.0),
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
