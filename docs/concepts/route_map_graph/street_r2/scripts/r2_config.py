"""Street round 2: every rule's config block (PIPELINE_SPEC 13.1 names), with its defaults. One-city units (BU).

Nothing here is hand-placed: each block is the parameter set of a seeded generator pass in r2_rules.py. The art seed is
the only per-street input besides the city layout and the run (spec 3.5: art streams keyed by content ids).
"""

# the art seed per still: the default street (seed 1) and the second seed of the overview (seed 2)
SEEDS = {"s1": 1, "s2": 2}

RULES_R2 = {
    # rank 1: the street front is a rhythm of heights with crowns, not a flat band
    "frontage.silhouette": dict(
        frontage_min_floors=6,          # approved (3.2)
        floors_low=(6, 8), floors_mid=(9, 13), floors_tall=(14, 21),
        rhythm_p=dict(low=0.34, mid=0.33, tall=0.33),   # class draw; the class never repeats 3 times running
        height_step_min=2,              # floors between neighbours
        triple_span_min=6,              # any 3 neighbours span at least 6 floors (no flat stretch: R-SIL-2)
        max_equal_tops=2,               # adjacent tops within 1 floor (guaranteed 1 by height_step_min)
        crown_share=0.34,               # >= 1/3 of the frontage carries a crown
        crown_kinds=("setback", "spire", "roof_box", "sign_frame"),
        route_sign_floors=3,            # a route column rises at least 3 floors over its top room (hero sign zone)
        sightline_floors=7,             # frontage in front of the corp landmark stays at most this tall (if not taller already)
        sightline_pad=0.035,            # frame widths around the landmark's screen x
        both_sides=True,                # applied to both sides of every border-link leg (one city)
        # lit silhouette: every frontage roof carries a neon rim in its district palette; the street face gets lit
        # bands every band_every floors (a seeded 3..5) and, with p_corner, lit corner strips - the custom street's
        # stepped neon rims, by rule
        roof_rim=True, band_every=(3, 5), p_corner=0.45,
    ),
    # rank 9 on the street: the backdrop row breaks the horizon (towers taller than 2x the median roof)
    "horizon.break": dict(
        spikes_min=3, spikes_max=5,
        spike_k=2.0,                    # spike roof >= spike_k x the median backdrop roof
        spike_spacing=1.0 / 6.0,        # frame widths apart (OVERVIEW)
        spike_top=(0.04, 0.24),         # the spike's roof lands this far down from the frame top (OVERVIEW)
        backdrop_band=(24.0, 170.0),    # BU behind the street face
        spike_min_w=4.0,                # footprint
        coast_amp=None,                 # the city-view coast term (not in a street frame)
    ),
    # rank 11: facade kits
    "materials.mix": dict(
        kits=("concrete_band", "glass_curtain", "panel_grille", "lit_atrium"),
        material_kinds=4,
        kit_radius=260.0,               # BU from the street midpoint: buildings the netrun views can resolve
        district_weights={
            "meridian": (0.30, 0.15, 0.40, 0.15),
            "halcyon": (0.20, 0.40, 0.15, 0.25),
            "": (0.35, 0.25, 0.25, 0.15),
        },
        roof_clutter_kinds=("ac", "tank", "vent_stack", "antenna", "dish"),
        roof_clutter_min_kinds=3,
    ),
    # rank 12
    "repetition.guard": dict(max_same_module_adjacent=2),      # identical = same kit AND same window module
    # rank 2: signs by rule, with LOD tiers (designer Q3)
    "dressing.signs": dict(
        hero_kinds=("blade", "wall"),
        hero_lum_ratio=(1.5, 2.0),      # hero luma / its ring: MEASURED on the plate (r2_checks), not solved at build time
        hero_central_frac=2.0 / 3.0,    # at least one hero inside the central 2/3 of the frame width
        p_secondary=0.5,
        p_shop_sign=0.75,               # a small text sign over a shopfront
        megastructures=1,
        mega_kinds=("globe", "arch", "holo"),
        signs_on_screen_min=6,
        legible_px=12.0,                # text cap height at 1080p for a sign to count as legible
        backdrop_sign_p=0.6,            # a tall vertical sign high on a visible backdrop tower
        p_roof_board=0.16,              # a lit board on legs on backdrop roofs over 14 BU in the OVERVIEW (replaces the
                                        # mainline kit's blank holo panel inside the kit radius); sign_frame crowns carry one too
        mega_headroom=0.03,             # the megastructure's top must stay this far inside the OVERVIEW frame
        sign_off=0.12,                  # BU in front of the face (placement check: <= 0.35)
        hero_emit=4.0, sec_emit=2.6, shop_emit=1.5, mega_emit=3.0, backdrop_emit=2.4,
    ),
    # LOD tiers by camera distance in BU (spec 5.1 / 5.2: signage_on_at 466 -> 216 BU; Q3)
    "lod.signs": dict(
        t1_shape=466.0,                 # d <= 466: the neon SHAPE appears (flat emissive silhouette in the sign's hue)
        t2_full=216.0,                  # d <= 216: the full sign (text / art texture, frame, mount)
        t3_detail=70.0,                 # d <= 70: detail (brackets, tube rims, cable, lamp heads, sub-line legible)
        fade_margin=0.15,               # Godot visibility_range_end_margin as a share of the band edge
    ),
    # rank 4
    "streets.light": dict(
        lamp_step=6.0, lamp_post_h=4.6, lamp_arm=1.1, kerb_off=3.3,
        p_shopfront=0.55,               # street-level faces off the frontage (the kit's own rule, kept)
        shopfront_frontage=1.0,         # every frontage base
        lanes=4, lane_period=80.0,
        # section_spill: the section cuts the near-side frontage, but keeps its light: one soft area light per cut
        # face (its width x up to 12 BU, at its street face, facing across the street, in its trim colour)
        section_spill=14.0,             # W per BU^2 of the cut face
        facade_wash=2400.0,             # W: an uplight spot at every non-route frontage face, in its trim colour
                                        # (route columns keep the v3 wash, 1500 W)
    ),
    # rank 7
    "foreground.street": dict(
        fg_band=0.20,
        zcut_street=0.15,               # the section fill in front of the road is lowered to road level
        fill_albedo=0.045,              # the lowered fill takes the wet road's albedo (no checkerboard)
        fg_lanes=(-6.5, -9.5, -13.0, -17.5),         # extra streak lanes on the section floor (camera side, BU from the centre line)
        edge_silhouettes=0,             # near-black cut blocks at the frame's side edges: allowed by the spec, not used
    ),
    # rank 6
    "atmosphere.layers": dict(
        sky_max_share=0.25,
        beam_fog_min=0.6,               # share of each beam's on-screen length inside fog
        planes=3, plane_step=0.03,
        back_haze=0.0040,               # density per BU x unit_scale behind the street (backdrop plane)
        back_haze_band=(30.0, 120.0),   # BU behind the street face: ramps in over this band
        back_haze_top=2.4,              # x H_SKY: thins above
        sky_haze=0.0014,                # haze above the skyline (beams cross it)
        plumes=4, plume_h=(7.0, 15.0), plume_r=(1.4, 2.4), plume_k=0.09,
    ),
    # rank 5
    "palette.districts": dict(
        district_hue_min=0.04, hue_cluster_max=0.45,
        hues={"meridian": (1.0, 0.549, 0.102), "halcyon": (0.549, 0.482, 1.0), "solace": (0.239, 1.0, 0.545),
              "orbital": (0.498, 0.659, 1.0), "rebel_cell": (0.91, 0.078, 0.118), "": (0.16, 0.8, 1.0)},
        # the sign palette per district: its own hue first, then the AAA pair and accents
        sign_pal={
            "meridian": [(1.0, 0.55, 0.10), (1.0, 0.78, 0.25), (1.0, 0.22, 0.20), (0.16, 0.80, 1.0), (1.0, 0.16, 0.6)],
            "halcyon": [(0.62, 0.45, 1.0), (1.0, 0.16, 0.6), (0.16, 0.80, 1.0), (0.85, 0.85, 1.0), (0.25, 1.0, 0.75)],
            "": [(1.0, 0.16, 0.6), (0.16, 0.80, 1.0), (0.20, 1.0, 0.70), (1.0, 0.85, 0.20), (1.0, 0.40, 0.18)],
        },
        scatter=(0.88, 0.86, 0.90),     # fog scatter colour, less violet (the ambient fill cap)
    ),
}

# words for the sign library (dressing only: corps of the setting and invented shop words; no game content)
WORDS = {
    "meridian": ["MERIDIAN", "FREIGHT", "DOCK 9", "CARGO", "CRANE", "SODIUM", "RAMEN", "PAWN", "BAR", "REPAIR"],
    "halcyon": ["HALCYON", "CLINIC", "PHARMA", "CLEAN AIR", "HOTEL", "SLEEP", "KARAOKE", "TEA", "DATA", "ORBITAL"],
    "": ["NOODLE", "OPEN 24", "CAPSULES", "VOLTA", "SOLACE", "ARCADE", "SUSHI", "PAWN", "BAR", "DATA"],
}
SUBS = ["24 H", "OPEN", "NO CREDIT", "LIVE", "B1", "2F", "ALL NIGHT", "FAST", "DOSE+", "NEW"]
