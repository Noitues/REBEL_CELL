"""HQ Solace: the r3 look preset plus the Solace variant (the DNA helix tower, the strand sequence).

The kit reads PRESET["hq"] / PRESET["hq_fog"]; r3's look_preset stays unchanged.
Solace lime #96FF46 sits next to the Cell's lime #D4FF00: Solace light stays in the 3D (strand LEDs, pod glass) and
NEVER on a link or a ring (bible 2.4); the overlay keeps the locked state colours.
"""
import copy

import look_preset as _LP

PRESET = copy.deepcopy(_LP.PRESET)
PALETTES = dict(_LP.PALETTES)

PRESET["hq"] = {
    "corp": "solace", "corp_name": "SOLACE BIOSYSTEMS",
    "dossier": ("SOLACE", "WARD SECURITY", (150, 255, 70)),
    "glass_atlas": r"D:\rc_scratch\hq_rev\solace\v3\glass_atlas.png",   # v3 final: hq_glass_atlas.py (seed 6360)
    "target_name": "THE GENOME CORE", "target_place": "the helix cap",
    "out_big": r"D:\rc_scratch\hq_rev\solace\v3",        # v3 (designer review of round 1); v2 passes in ..\solace
    "suffix": "_v3",
    "palette": {
        "porcelain": (0.13, 0.15, 0.15),       # the strands: wet dark porcelain (v2 r2: was pale grey 0.36)
        "leaf": (0.30, 1.00, 0.06),            # #96FF46 linear: strand LEDs, pod glass glow
        "leaf_dim": (0.10, 0.45, 0.04),
        "pink": (1.00, 0.06, 0.28),            # #FF4696 linear: secondary accents (the cap ring, warning marks)
        "clinic": (0.85, 0.97, 1.00),          # sterile clinic white light
        "glass": (0.02, 0.06, 0.03),
        "panel": (0.40, 0.43, 0.44), "panel_dark": (0.18, 0.20, 0.21), "concrete": (0.22, 0.23, 0.23),
        "lockdown": (1.0, 0.05, 0.08), "gold": (1.0, 0.62, 0.12), "scan": (0.7, 1.0, 0.6),
        "frost": (0.55, 0.75, 0.62),           # an unread pod's frosted pane
    },
    "compound": {
        "room_w": 14.0, "room_h": 7.0, "room_d": 10.0,
        # TWO TWISTING TOWERS (designer redesign 2026-10-15): tower A centred `radius` out at azimuth theta(floor),
        # tower B opposite; every floor rotates `twist` degrees from the one below; a bow-tie skybridge on every floor
        # v3 (designer review of round 1): each strand makes a FULL 360 degree turn, at the city landmark's twist
        # rate (helix angle atan(2 pi R / pitch): city 2 pi 7.5 / 62 -> 37.2 deg; here 2 pi 40 / 337.5 -> 36.7 deg):
        # 27 floors of 12.5 BU, 360 / 27 = 13.33 degrees a floor (v2: 19 floors x 11 deg = 209 deg)
        "radius": 40.0, "floor_h": 12.5, "floors": 27, "tube_r": 10.0, "tower_w": 20.0, "tower_d": 20.0,
        "theta0": 90.0, "twist": 360.0 / 27.0,
        "route_floors": [3, 6, 9, 12, 15, 18, 21, 24],  # every third floor (8 route levels, as v2), up the whole turn
        "bridge_w": (7.0, 4.0),                  # the bow-tie: width where it enters the node recess (v3 final 9 -> 7), at the waist
        # v3 windows: ONLY 2 a floor per strand, one facing INWARD (the walkway) and one OUTWARD; a landscape oval
        # spanning `span` degrees of its tube half; `half_h` its half height, `zc` its centre above the floor slab.
        # The inward window of a route floor IS the route node (lit interior, kind-dressed; the bridge enters it)
        # v3 final (designer after t3): every window is a FLAT level / plumb oval in a vertical plane set into the tube;
        # its normal turns `face_front` deg from radial toward the floor front (the two inward windows face each other
        # across the walkway AND the camera); `stair_phi` = the solid band between the windows on the front side
        "win": {"span": 140.0, "half_h": 4.2, "zc": 5.4, "frame_r": 0.25, "face_front": 35.0, "stair_phi": 35.0},
        "podium": (64.0, 50.0, 5.0),             # the plaza podium: half x, half y, height
        "crown_h": 14.0, "target_w": 22.0, "target_h": 10.0,
        "seed": 6301,                            # the semi-random tower sets (round 43 decision)
        "deck": ["router", "router", "elite", "terminal", "modem", "router", "elite", "terminal"],
        "start": (0.0, -86.0),
        "max_shortcuts": 0,
    },
    "mech": {"read_ahead": 2},                 # route floors read ahead of the current one (proposal)
    "light": {"room_k": 1.0, "room_w": 2600.0, "lockdown_k": 2.0, "sign_k": 0.5, "trim_k": 2.4, "cityglow_k": 0.22,
              "city_beam_k": 0.6, "bank_glow": 2500.0, "shop_w": 700.0, "flood_w": 2.2e4,
              # the twin towers' light (designer redesign): office bands, the atrium shaft, slab downlights,
              # the ground spots, the bridges; rim from the city behind; the halo fog ring
              "band_k": 0.22, "atrium_k": 1.6, "down_k": 1.4, "down_w": 600.0, "ground_spot_w": 3.5e4,
              "bridge_k": 1.1, "bridge_wall_k": 0.10, "bridge_route_k": 2.4, "rim_w": 1.0e5, "halo_r": (170.0, 290.0), "halo_h": 120.0,
              "halo_peak": 0.004, "halo_fill_w": 4.0e3,
              "plaza_wash_w": 2.5e3,                     # v2 r2: the plinth dark (was 9e3)
              # v2 r2 (art director): the helix lit 1.5-2x its background: a leaf-green fresnel RIM on the strands,
              # the oval portholes lit from inside (visible), the plinth's lit entry
              # v2 full: rim 0.9 -> 0.5, portholes 2.6 -> 1.6. v3: the 2 big ovals a floor have ~4x the v2 glass and
              # half the decision frame's landmark is window: porthole 1.6 -> 0.45 (lit from the middle, dim at the
              # rim), rim 0.5 -> 0.32 (decision ratio 3.4 -> 2.9, overview 2.8 -> 2.6)
              "rim_k": 0.32, "rim_pow": 5.0, "porthole_k": 0.45, "glass_k": 2.4, "entry_w": 0.0},   # v3 final: the entry area light off (its pool at the stair foot read as haze); the lobby glows by its own trim
    "beams": {"power": 2.0e7, "cone": 1.1},
    "bank_glow_cols": ["clinic", "leaf_dim"],
    "city": {"seed": 6311,
             "rings": [dict(name="near", r=(300.0, 372.0), h=(22.0, 64.0), w=(12.0, 24.0), neon_p=0.4, win_p=0.30,
                            far=1.0, signs=True),
                       dict(name="mid", r=(400.0, 540.0), h=(40.0, 120.0), w=(16.0, 34.0), neon_p=0.3, win_p=0.28,
                            far=0.7, signs=True),
                       dict(name="far", r=(620.0, 980.0), h=(80.0, 250.0), w=(22.0, 48.0), neon_p=0.35, win_p=0.30,
                            far=0.45, signs=False)],
             "beam_sectors": 8, "beam_ring": "mid", "billboards": 8,
             "sky_lanes": [(700.0, 150.0), (780.0, 182.0), (860.0, 226.0)],
             "perimeter": dict(r=(170.0, 292.0), pylon_step=40.0, pylon_h=6.0, wall_r=292.0, wall_h=4.0),
             "win_p": 0.34, "win_k": 0.52},      # v3: 0.42 -> 0.52 (decision local background); t2b: was 0.30 / 0.30 (median 0.10)            # v2: 0.26 / 0.16 -> the city lit (light, not exposure)
    # v2: the dense downtown right up to the plaza podium (hq_kit.downtown)
    "downtown": {"seed": 6340, "keep": ("rect", 72.0, 92.0), "street0": 8.0, "cell": 30.0, "street": 7.0,
                 "r_out": 296.0, "h_near": (14.0, 36.0), "h_far": (26.0, 72.0), "tall_p": 0.05, "sign_p": 0.55,
                 "holo_p": 0.07, "trim_p": 0.4, "lamp_step": 15.0, "lamp_lights": 70, "lamp_w": 1800.0, "zref_k": 0.5},
    "road": {"plaza": 136.0, "road": (136.0, 162.0), "walk": (162.0, 170.0)},
    "cam": {"pitch_lo": 12.0, "pitch_hi": 26.0, "lens": 30.0, "dmin": 120.0, "fill": (0.56, 0.62),
            "pitch_o": 27.0, "lens_o": 34.0, "fill_o": (0.95, 1.0),      # v3: the taller strands fill 75 % of the frame height (was 29.5 / 0.92)
            "ov_yaw": 110.0, "ov_centre": (0.0, 0.0, 175.0)},   # v3: yaw 110 shows 15 of 16 nodes (all the walked + the options)
    "post": {"black": 0.04, "exposure_zoom_k": 0.32},   # v3: 0.40 -> 0.32 (the decision city lifted)
    # v2 r2 (art director: no flat solid sky band): a graded night sky (by view elevation), haze toward the horizon
    "sky_ramp": [(0.0, (0.035, 0.03, 0.05)), (0.05, (0.028, 0.022, 0.045)), (0.16, (0.012, 0.012, 0.03)),
                 (0.45, (0.003, 0.004, 0.012))],
}

PRESET["hq_fog"] = {
    "peak": 0.0065, "base": 0.10, "height_scale": 70.0, "floor": 10.0,
    "box": (-1100.0, -1100.0, 0.0, 1100.0, 1100.0, 320.0),
    "layer_scales": ((0.004, 0.012, 0.075), (0.009, 0.02, 0.33)), "layer_mix": 0.62, "layer_remap": (0.47, 0.64),
    "clump_scale": (0.0075, 0.014, 0.022), "clump_remap": (0.40, 0.62),
    "calm": {"r": 100.0, "soft": 40.0, "k": 0.10},     # v3: the plinth crisp (designer: thin haze only; was 70/45/0.30)
    "bank": {"r": (150.0, 210.0), "z": (0.0, 9.0), "peak": 0.008},   # v3: the ground bank off the plinth (was 80-170)
    "haze": 0.0006, "aniso": 0.45, "colour": (0.86, 0.95, 0.9),        # final: 0.0006 + cityglow 0.22 (mid-distance city haze, median 0.096 -> ~0.12)
}

PRESET["post"].update({"exposure": 2.6})     # v3 final: 2.4 -> 2.6 (designer: the landmark a little brighter; overview median ~0.14-0.15)
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
# SOL_R2
# T2B_VALUES
