"""HQ Halcyon: the r3 look preset plus a Halcyon variant (corporate white / teal light, the eye, the compound).

Everything the r3 look tunes still comes from look_preset.PRESET (a copy of r3's, unchanged). This module only ADDS
keys under PRESET["halcyon"] and two palettes, so the street and the compound share one look:
    import halcyon_preset as HP; P = HP.PRESET; H = P["halcyon"]
Units as in r3: BU (1 storey = 8 BU), W (Blender light power), densities per BU.
"""
import copy

import look_preset as _LP

PRESET = copy.deepcopy(_LP.PRESET)
PALETTES = dict(_LP.PALETTES)

# The Cell's city round the compound keeps the r3 district pair (grimy neon): magenta / cyan / amber / violet.
# The compound gets its own light set (the "civic" palette); the corp hues stay the bible's (violet crest, amber eye).
PALETTES["halcyon_civic"] = {}          # the district pair round the compound = neon_bay (the r3 default)

PRESET["halcyon"] = {
    # ------------------------------------------------------------ palette (linear RGB)
    "palette": {
        "civic_white": (0.80, 0.93, 1.00),     # cold fluorescent white: uplights, cornice coves
        "civic_teal": (0.30, 1.00, 0.86),      # the thin teal reveal lines (ART: "white and teal corporate light")
        "scan": (0.78, 1.00, 0.97),            # the eye's light: white with a teal fringe (not amber: see NOTES, Q1)
        "scan_fringe": (0.25, 0.95, 0.90),
        "lockdown": (1.00, 0.05, 0.08),        # scanned room: red holo lockdown (bible: red ring = danger / locked)
        "corp_violet": (0.43, 0.16, 1.00),     # Halcyon violet #B06EFF (linear): crest, signage
        "corp_amber": (1.00, 0.40, 0.03),      # Halcyon amber #FFAA28 (linear): the eye's rim, as the landmark
        "panel": (0.40, 0.43, 0.46),           # the white stone / composite panels (albedo, wet)
        "panel_dark": (0.20, 0.22, 0.25),      # cut concrete of the room frames
        "glass": (0.015, 0.03, 0.035),
        "gold": (1.00, 0.62, 0.12),            # shortcut lifts (bible: shortcuts in gold)
    },
    # ------------------------------------------------------------ the compound layout (hq_graph.py reads these)
    "compound": {
        "rows": [6, 5, 4, 3, 2, 1],            # switchback rows, bottom to top (round 43: 21 nodes)
        "room_w": 14.0, "room_h": 8.0, "room_d": 10.0,
        "gap": 9.0,                            # between rooms in a row: the gallery (the long way)
        "tier_h": 13.0,                        # one tier = room + slab + cornice / terrace
        "setback": 3.0,                        # each tier sits this much further back (y)
        "podium_h": 6.0, "podium_x": 96.0,       # the podium is a square plinth (half-size), the plaza round it
        "stair_run": 20.0,                     # a corner stair's run along the next face (rise = one tier)
        "tier_margin": 4.0,                    # tier half-width = rows * pitch / 2 + margin
        "centre_w": 14.0,                      # the centre column the eye always watches (one room wide)
        "target_w": 22.0, "target_h": 10.0,    # THE PANOPTICON vault (the TARGET)
        "crown_h": 7.0,
        "eye": {"z_above": 20.0, "w": 42.0, "h": 24.0, "tube": 1.3, "iris_r": 7.0, "drum_r": 12.5, "drum_d": 10.0},
        "start": {"x": -88.0, "y": -112.0},    # the gatehouse (start) on the plaza, south-west of the podium
        "kinds": ["router", "terminal", "router", "elite", "modem", "router", "terminal"],   # round 43: n -> [n % 7]
        "max_shortcuts": 2,                    # round 43: at most 2 used
    },
    # ------------------------------------------------------------ the eye rule (round 43 + the proposal)
    "eye": {
        "phase": 0,                            # lighthouse: sector centre az = 45 (phase + step), 90 deg wide
        "consequence": "spotted",              # "spotted" (round 43, bible 4.7, LOCKED good-for-now) | "blocked" (r35/r42)
        "wash_w": 2.2e6, "wash_vol": 0.07, "wash_cone": 150.0, "wash_soft": 0.05, "wash_pitch": 38.0,
        "beam_w": 6.0e7, "beam_cone": (2.2, 6.0), "beam_pitch": 9.0,   # the lighthouse beam out over the city
        "blade_w": 9.0e6, "blade_halfwidth": 0.008, "blade_cone": 120.0,
        "glow_w": 6.0e3,                       # the iris point glow on the eye housing
        "iris_k": 60.0, "rim_k": 9.0,
    },
    # ------------------------------------------------------------ corporate searchlights ("civic order")
    "civic_beams": {"tiers": [0, 3], "podium": True, "cone": 1.1, "power": 3.0e7, "lean": (0.10, 0.34),
                    "lean_y": 0.12, "twin": 0.25},
    # ------------------------------------------------------------ the compound's own lighting
    "light": {"uplight_w": 320.0, "uplight_cone": 70.0, "cove_k": 2.2, "teal_k": 2.6, "room_k": 1.0, "room_w": 3200.0,
              "lockdown_k": 2.2, "plinth_wash": 400.0, "slit_k": 0.2, "sign_k": 0.12,
              "cityglow_k": 0.15, "city_beam_k": 0.8, "bank_glow": 4000.0, "shop_w": 900.0},
    # ------------------------------------------------------------ the Cell's city: a procedural 360 degree ring
    # square rings round the plaza (a city grid), so every orbit angle has a near / mid / far layer. Each ring: inner
    # and outer half-size, tower height range, block width range, neon share, window share, far factor (emission)
    "city": {"seed": 4311,
             "rings": [dict(name="near", r=(300.0, 372.0), h=(22.0, 64.0), w=(12.0, 24.0), neon_p=0.65, win_p=0.36,
                            far=1.0, signs=True),
                       dict(name="mid", r=(400.0, 540.0), h=(40.0, 120.0), w=(16.0, 34.0), neon_p=0.45, win_p=0.32,
                            far=0.7, signs=True),
                       dict(name="far", r=(620.0, 980.0), h=(80.0, 250.0), w=(22.0, 48.0), neon_p=0.35, win_p=0.30,
                            far=0.45, signs=False)],
             "beam_sectors": 8, "beam_ring": "mid", "billboards": 8,
             "sky_lanes": [(700.0, 150.0), (780.0, 182.0), (860.0, 226.0)],
             # the PERIMETER: a cleared, lit security belt between the ring road and the city (the eye sees everything);
             # every orbit camera (decision radius <= ~290 BU) stands in it, so no tower ever sits in front of a room
             "perimeter": dict(r=(160.0, 292.0), pylon_step=36.0, pylon_h=7.0, wall_r=292.0, wall_h=5.0),
             "win_p": 0.30, "win_k": 0.30},
    "road": {"plaza": 128.0, "road": (128.0, 154.0), "walk": (154.0, 160.0)},     # square ring road round the plaza
    # value targets are the r3 ones (PRESET["targets"]); the compound is white, so the grade watches its p95
}

# The fog round the compound: the r3 recipe, with a calm slab in front of the face (the route) and a bank on the plaza.
PRESET["halcyon_fog"] = {
    "peak": 0.0065, "base": 0.10, "height_scale": 60.0, "floor": 10.0,
    "box": (-1100.0, -1100.0, 0.0, 1100.0, 1100.0, 300.0),            # the whole ring (360 deg)
    "layer_scales": ((0.004, 0.012, 0.075), (0.009, 0.02, 0.33)), "layer_mix": 0.62, "layer_remap": (0.47, 0.64),
    "clump_scale": (0.0075, 0.014, 0.022), "clump_remap": (0.40, 0.62),
    "calm": {"r": 105.0, "soft": 45.0, "k": 0.35},               # round the pyramid (square radius): the route reads
    "bank": {"r": (100.0, 172.0), "z": (0.0, 9.0), "peak": 0.012},  # plaza / ring-road mist bank, lit from below
    "haze": 0.0002, "aniso": 0.45, "colour": (0.85, 0.82, 1.0), "underlight_k": 0.10,
}

PRESET["post"].update({"exposure": 2.4})
PRESET["halcyon"]["post"] = {"exposure": 3.4, "exposure_zoom_k": 0.61, "black": 0.03, "knee_top": 0.86}

# LOD by zoom: the storyboard's keys (storyboard/scripts/look_preset.py "lod_bands", same names and bands), so the
# street, the storyboard and the HQ share one rule. Here zoom 0 = the HQ OVERVIEW, 1 = the DECISION framing:
#   zoom = clamp(log(d_overview / d) / log(d_overview / d_decision), 0, 1)      (hq_cam.zoom_of)
# Each band (a, b) fades its layer in over zoom a..b (smoothstep). The big layer (fog banks, the beams incl. the eye's
# scan, building and window lights, the route) is always on.
PRESET.setdefault("lod_bands", {
    "fog_octaves_by_zoom": (0.25, 0.60),   # the fine octave + ragged edges
    "wisps_on_at": (0.45, 0.70),           # the thin wisp strata
    "plumes_on_at": (0.50, 0.72),          # rooftop steam plumes
    "signage_on_at": (0.60, 0.82),         # signs, holo ads, billboards, the plinth lettering
    "small_lights_on_at": (0.75, 0.92),    # bollards, beacons, room LEDs; rain catching light (post)
    "puddles_sharp_at": (0.85, 1.00),      # puddle reflections sharpen (post blur on the wet ground)
})


def pal(name):
    """A Halcyon palette entry, else the district palette (r3), else a literal colour."""
    if not isinstance(name, str):
        return name
    if name in PRESET["halcyon"]["palette"]:
        return PRESET["halcyon"]["palette"][name]
    return PRESET["palette"][name]
