"""r3 look preset: every tunable of the AAA-2 r3 look in one place. A new city layout plus this preset gives the same look.

Units: BU (1 storey = 8 BU), W (Blender light power), densities per BU. The rules that consume these are in
rules_r3.py (placements), fog_r3.py (media, beams), loop_r3.py / post_loop.py (motion) and post_aaa.py (grade).
A job key of the same name (jobs_aaa.py key=value) overrides a top-level preset value for one render.
"""

PRESET = {
    "name": "AAA-2 r3 realistic night",
    # ---------------------------------------------------------------- palette (the district pair + accents)
    "palette": {
        "district_a": (1.0, 0.16, 0.6),      # magenta
        "district_b": (0.16, 0.8, 1.0),      # cyan
        "accent_warm": (1.0, 0.58, 0.18),    # amber
        "accent_cool": (0.62, 0.38, 1.0),    # violet
        "underlight": [(0.0, "district_a"), (0.3, "district_b"), (0.55, "district_a"), (0.8, "district_b"),
                       (1.0, "accent_cool")],
    },
    # ---------------------------------------------------------------- the city heightfield the rules read
    "heightfield": {"step": 3.0, "x": (-200.0, 380.0), "y": (14.0, 320.0), "z_top": 600.0},
    # ---------------------------------------------------------------- fog: one continuous field + modulations
    "fog": {
        "peak": 0.021,                       # density at the layer cores, low down
        "base": 0.08,                        # the soft body under the layers (share of the peak)
        "height_scale": 55.0,                # e-folding height above 30 BU (dense low, thinning with altitude)
        "floor": 22.0,                       # general fog floor (alleys and tower bases at mid-height)
        "floor_margin": 5.0,                 # above the decision rooms' projected top, inside their view angle
        "calm_margin": (0.0, 0.07),          # extra view-angle margin (tan) round the decision set: start, full
        "warp": 80.0, "wave": 18.0, "tilt": 0.07,
        "layer_scales": ((0.004, 0.012, 0.075), (0.009, 0.02, 0.33)),   # banks (8-15 BU) and wisps (1-3 BU)
        "layer_mix": 0.62, "layer_remap": (0.47, 0.64),
        "clump_scale": (0.0075, 0.014, 0.022), "clump_remap": (0.40, 0.62),
        "box_y": (16.0, 300.0), "box_top": 240.0,
        "aniso": 0.45, "colour": (0.85, 0.80, 1.0),
        "underlight_k": 0.12,                # self-emission per unit density (kept low: it made pillars in gaps)
        "wind": 4.0,                         # BU/s drift (the loop cross-fades over one period)
        # banks hugging building bases and alleys (heightfield rule), lit from below
        "bank_peak": 0.10, "bank_z": (24.0, 38.0), "bank_reach": 9.0,
        "bank_glow_n": 4, "bank_glow_w": 8.0e4,
        # thin wisps at a height relative to the skyline
        "wisp_peak": 0.2, "wisp_frac": 0.62, "wisp_thick": 2.6, "wisp_tilt": 0.03,
        "wisp_glow_n": 2, "wisp_glow_w": 6.0e4,
    },
    "mist": {"peak": 0.016, "height": 5.5, "glow_w": 900.0, "glow_step": 22.0},
    "plumes": {"n": 4, "peak": 0.09, "height": (55.0, 70.0), "lean": (0.35, 0.5), "min_spacing": 50.0,
               "roof_z": (30.0, 110.0)},
    "cityglow_k": 1.8,
    "back_haze": 0.0016,
    # ---------------------------------------------------------------- beams
    "beams": {
        "k": 6, "heroes": 2, "min_spacing": 45.0, "y_range": (20.0, 115.0), "roof_min": 30.0, "min_rise": 0.12,
        "side_colours": {"left": ["accent_warm", "district_a"], "right": ["district_b", "accent_cool"]},
        "power_k": 60.0,                     # scales every beam
        "hero_soft": (3.0, 0.8e6), "hero_core": (0.9, 2.2e6),
        "thin": (1.3, 1.6e6),
        "hero_b_soft": (4.5, 1.4e6), "hero_b_core": (0.9, 3.6e6),   # the district-b hero (cyan): kept as reviewed
        "haze_twin": 0.3, "haze_twin_b": 0.9,                        # the faint unlinked twin, as a share
        "lean": (0.12, 0.42), "lean_y": (0.18, 0.3),
        "sweep_deg": (4.5, 6.0),
        "colours": ["district_a", "district_b", "accent_warm", "district_b", "district_a", "accent_cool"],
    },
    # ---------------------------------------------------------------- traffic streaks
    "street_lanes": {"fractions_near": (0.24, 0.53), "fractions_far": (0.32, 0.53), "len": (12.0, 80.0),
                     "gap": (10.0, 55.0), "periods": (300.0, 330.0, 300.0, 270.0)},
    "sky_lanes": {"n": 3, "z_frac": (0.62, 0.68, 0.85), "y": (52.0, 57.0, 118.0), "len": (6.0, 16.0),
                  "gap": (60.0, 160.0), "slope": (0.05, 0.12), "periods": (360.0, 400.0, 440.0),
                  "calm_k": 0.35},
    # ---------------------------------------------------------------- loop motion
    "loop": {"T": 4.0, "fps": 24, "globe_spin_deg": 22.5, "drift_px": (13.0, 3.0), "strobe_period": 24,
             "cursor_period": 24, "gloss_frames": 29, "windows": 3, "strobe_phases": 3},
    # ---------------------------------------------------------------- LOD by zoom (storyboard; 0 = city aerial, 1 = street)
    # each band (a, b): the layer fades in over zoom a..b (smoothstep). zoom = log-distance from the HQ aerial to the
    # route OVERVIEW (sb_cams.zoom_at). Big layer (fog banks, beams, windows, street-light rivers) is always on.
    "lod_bands": {
        "fog_octaves_by_zoom": (0.25, 0.60),   # the fine octave + ragged edges: banks resolve into layered strata
        "wisps_on_at": (0.45, 0.70),           # the thin wisp layer
        "plumes_on_at": (0.50, 0.72),          # rooftop steam plumes
        "signage_on_at": (0.60, 0.82),         # text signs, holo ads, billboards
        "small_lights_on_at": (0.75, 0.92),    # rain catching light (post); stall lights / strobes: see NOTES
        "puddles_sharp_at": (0.85, 1.00),      # puddle reflections sharpen (post blur on the wet ground)
        # v2 (review: the mid-dive frame was milky): the fog's density and the city glow under it ramp up with zoom,
        # so the city view keeps a dark night with big banks and clear air between them
        "fog_density_by_zoom": (0.35, 0.30, 0.90),   # (level at zoom 0, a, b)
        "cityglow_by_zoom": (0.45, 0.30, 0.90),
        # v3 (designer): the city view is the MAINLINE look; the dive blends to AAA-2 over this zoom band (grade, fog,
        # wet reflections, cel -> AAA-2 shading; in the storyboard a cross of the two worlds behind a cloud veil)
        "look_blend_by_zoom": (0.20, 0.55),
        # v3 one continuous city: the SECTION through the blocks in front of the netrun street lowers with the zoom,
        # from above every roof at the HQ to a 1.2 BU plinth at the street (z_far, z_near, band a, band b)
        "section_by_zoom": (60.0, 1.2, 0.25, 0.85),
    },
    # ---------------------------------------------------------------- post / value targets
    "post": {"exposure": 2.4, "vol_k": 1.3, "vol_soft": 0.25, "vol_glow": 0.8, "vol_glow_thr": 0.02, "rain_vol": 1.6},
    "targets": {"median": 0.14, "under_010": (0.25, 0.40), "over_085_max": 0.025},
}


# alternative district palettes (the same names, other colours): a district swaps only these four
PALETTES = {
    "neon_bay": {},                                                       # the default above
    "sodium_teal": {"district_a": (1.0, 0.42, 0.08), "district_b": (0.1, 0.95, 0.75),
                    "accent_warm": (1.0, 0.2, 0.25), "accent_cool": (0.45, 0.55, 1.0)},
}


def use_palette(name):
    """Switch the district palette in place (called once per build, from the job's "palette" key)."""
    PRESET["palette"].update(PALETTES.get(name, {}))


def colour(name):
    """A palette entry by name (or a literal colour)."""
    return PRESET["palette"][name] if isinstance(name, str) else name
