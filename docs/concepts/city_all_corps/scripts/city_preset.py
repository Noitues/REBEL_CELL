"""City-all-corps key art: every tunable in one place (pure Python; Blender and the post both import it).

Units: lots (the game's city grid) and BU (Blender units; 1 lot = U = 6 BU, the one-city kit's convention;
one floor = 1.9 BU, the mainline window pitch). Colours are linear-ish RGB 0..1 (the kit's convention).
Seeds are fixed here; nothing calls an unseeded RNG.
"""
import os

WT = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass"
CONCEPTS = os.path.join(WT, "docs", "concepts")
OUT = os.path.join(CONCEPTS, "city_all_corps")
KIT_LAYOUT = os.path.join(CONCEPTS, "route_map_graph", "storyboard", "scripts", "scratch", "layout")
LAYOUT = os.path.join(KIT_LAYOUT, "unified_v3.json")      # the one-city layout after the approved mainline rules
NET36 = os.path.join(KIT_LAYOUT, "net36.json")             # carries the round 34 fist outline (lots)
SCR = r"D:\rc_scratch\city_all_corps"
ZONED = os.path.join(SCR, "zoned.json")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

U = 6.0                         # BU per lot (layout36.U)
KH = U / 41.64 * 1.15           # game height units -> BU (onecity_scene.KH)
FLOOR = 1.9                     # BU per storey (mainline window pitch)
COLW = 1.6                      # BU per window column

SEEDS = dict(zoning=7701, build=7702, ring=7703, streaks=7704, beams=7705, sea=7706, landmark=7707, post=7708)

# ---------------------------------------------------------------- the seven corps + the unclaimed sprawl
# hue = the corp hue (ART_BIBLE / identity boards); sec = the district's second light; mat = facade albedo family;
# win = window colours (weights by repetition); lang = the building-language generator in city_build.py
DISTRICTS = {
    "meridian": dict(name="MERIDIAN", hue=(1.0, 0.549, 0.102), sec=(1.0, 0.25, 0.12), lang="freight",
                     mat=[(0.30, 0.20, 0.14), (0.26, 0.22, 0.20), (0.34, 0.24, 0.16)],
                     win=[(1.0, 0.62, 0.22), (1.0, 0.62, 0.22), (1.0, 0.78, 0.45), (1.0, 0.45, 0.15)], lit=0.34),
    "solace": dict(name="SOLACE", hue=(0.239, 1.0, 0.545), sec=(0.85, 1.0, 0.9), lang="capsule",
                   mat=[(0.40, 0.46, 0.43), (0.34, 0.40, 0.38), (0.46, 0.50, 0.47)],
                   win=[(0.75, 1.0, 0.82), (0.45, 1.0, 0.62), (0.95, 1.0, 0.95)], lit=0.40),
    "halcyon": dict(name="HALCYON", hue=(0.549, 0.482, 1.0), sec=(1.0, 0.70, 0.32), lang="civic",
                    mat=[(0.36, 0.34, 0.46), (0.32, 0.30, 0.42), (0.40, 0.38, 0.50)],
                    win=[(1.0, 0.74, 0.38), (0.72, 0.66, 1.0), (1.0, 0.82, 0.55)], lit=0.36),
    "orbital": dict(name="ORBITAL", hue=(0.498, 0.659, 1.0), sec=(0.92, 0.96, 1.0), lang="spire",
                    mat=[(0.30, 0.34, 0.42), (0.26, 0.30, 0.38), (0.36, 0.40, 0.48)],
                    win=[(0.70, 0.84, 1.0), (0.92, 0.95, 1.0), (0.55, 0.75, 1.0)], lit=0.38),
    "rebel_cell": dict(name="REBEL_CELL", hue=(0.91, 0.078, 0.118), sec=(1.0, 0.55, 0.3), lang="tenement",
                       mat=[(0.30, 0.22, 0.22), (0.26, 0.21, 0.22), (0.33, 0.26, 0.24)],
                       win=[(1.0, 0.66, 0.32), (1.0, 0.8, 0.5), (0.5, 0.85, 1.0), (1.0, 0.42, 0.7)], lit=0.40),
    "aurelian": dict(name="AURELIAN CONCORD", hue=(0.161, 0.859, 0.651), sec=(0.788, 0.639, 0.353), lang="roman",
                     mat=[(0.86, 0.78, 0.62), (0.80, 0.72, 0.56), (0.91, 0.84, 0.67)],       # travertine
                     win=[(1.0, 0.78, 0.45), (1.0, 0.70, 0.36), (1.0, 0.86, 0.6)], lit=0.36),
    "tethys": dict(name="TETHYS DEEP", hue=(0.184, 0.42, 1.0), sec=(0.486, 0.949, 0.894), lang="hull",
                   mat=[(0.16, 0.20, 0.26), (0.14, 0.18, 0.24), (0.20, 0.24, 0.30)],          # wet hull
                   win=[(1.0, 0.91, 0.72), (0.486, 0.949, 0.894), (1.0, 0.91, 0.72)], lit=0.34),
    "": dict(name="THE SPRAWL", hue=(0.75, 0.72, 0.82), sec=(1.0, 0.3, 0.65), lang="sprawl",
             mat=[(0.32, 0.30, 0.36), (0.28, 0.27, 0.32), (0.36, 0.33, 0.38)],
             win=[(1.0, 0.68, 0.28), (0.45, 0.9, 1.0), (1.0, 0.42, 0.72), (0.9, 0.9, 1.0)], lit=0.30),
}
CORPS = ["meridian", "solace", "halcyon", "orbital", "rebel_cell", "aurelian", "tethys"]

# ---------------------------------------------------------------- zoning rules (zoning.py)
ZONING = dict(
    k_neutral=3,              # the unclaimed buildings fall into k seeded clusters (farthest-point init, k-means)
    coast_band=40.0,          # a cluster whose mean depth b lies within this of the coast is coastal -> TETHYS
    fp_margin=0.25,           # lots of street-side gap kept between a landmark footprint and the refilled blocks
    landmark_r=5.6,           # landmark clearance radius in lots (layout36's HQ plaza rule, the same for all seven)
    pole_step=1.0,            # pole-of-inaccessibility search grid (lots) for a new HQ lot
    lagoon_frac=0.68,         # the seaward share of Tethys (by depth b) that is the drowned quarter
    crest_d=1.9,              # round 34: a building within this of a fist stroke shows red windows
    arterial_tr=0.55,         # a street line is an arterial when its mean lane traffic >= this ...
    arterial_len=36,          # ... over at least this many street tiles
    aqueduct_ext=8.0,         # the aqueduct runs the district's longest street line through the HQ, +- this past it
)

# ---------------------------------------------------------------- Tethys: the sea, the wall, the drowned quarter
WATER = dict(
    z=2.5,                    # sea level and the lapsed ward's water (BU above the dry street: the seawall holds it)
    wall_h=8.0,               # the seawall crest (BU above the street)
    levee_h=4.2,              # the drowned quarter's inner levee
    subside=(2.5, 30.0),      # drowned ground depth below the street: at the levee .. at the seawall
    trench=(95.0, 13.0),      # the Atlantis trench under the station: extra depth, radius (lots)
    sea_bed=(34.0, 120.0),    # the open sea floor: depth at the wall .. far out
    sea_out=24000.0,           # BU of open sea modelled past the coast
    # the clear-water recipe (city_build water_fade): per-BU extinction along the light path (view leg + down leg);
    # red dies first; in-scatter colour = the deep blue the far water fades to
    sigma=(0.090, 0.034, 0.016),
    inscatter=(0.003, 0.018, 0.055),   # darker deep blue (art review 6: more deep darks)
    win_boost=1.6,                    # wet facades: window emission x (1 + this) before the water fade
    path_cap=600.0,
    caustic=dict(k=1.1, scale=0.05, depth=30.0, col=(0.22, 0.72, 0.78), width=0.22, distort=0.9, floor=0.12, patch=0.05),   # soft ripples: emission, scale /BU, e-fold depth, ridge width, distortion, lit floor
    shafts=dict(n=9, power=1.0e7, cone=4.0, density=0.0035, tilt=(0.10, 0.22)),
    surface=dict(rough=0.035, wave=0.22, tint=(0.02, 0.06, 0.12)),
    sea_mist=dict(**{"from": 30.0}, top=55.0, density=0.0011),   # lots past the base coast, BU top, per-BU density
    under_sky=dict(tile=60.0, power=20000.0, z=-1.2,   # below the dry street level: it can only light drowned things
                   col=(0.62, 0.86, 1.0)),   # the lit surface seen from below (area lights)
)

# ---------------------------------------------------------------- AAA-2 look (the r3 preset, scaled to the aerial)
AAA = dict(
    neon=3.2, win=1.6, lane=6.0, streak=9.0, glow_area=1.6e4, moon=0.25,
    fog_peak=0.09, fog_base=0.06, fog_floor=(0.0, 3.0), fog_h=22.0, fog_top=70.0, haze=0.00015, haze_hi=0.0007,
    bank_scale=(0.0045, 0.0045, 0.05), clump_scale=(0.006, 0.006, 0.02),
    glow_mix=0.25, rebel_glow_k=1.8, roofwash=0.15,
    sheet=dict(z=58.0, thick=5.0, scale=(0.003, 0.003, 0.02), remap=(0.48, 0.66), peak=0.02),   # the thin upper fog sheet
    shore_bank=dict(width=14.0, h=7.0, peak=0.035),     # lots of depth b landward of the levee, BU e-fold, density
    bay_clear=0.96,                                       # share of the fog cleared over the bay water (clear air, art review 6)
    beams_city=6, beam_spacing=150.0, beam_power=2.2e8, beam_hero_power=2.6e8,
    step_rate=3.0, max_steps=256,
    exposure=1.0,
    black_point=0.85,        # post: share of the frame's 5th-percentile (per channel) taken off as the fog veil
    targets=dict(median=0.14, under_010=(0.25, 0.40), over_085_max=0.025),
)

# ---------------------------------------------------------------- MAINLINE look (sb_mhq / post40 / target_corps values)
MAINLINE = dict(
    ramp=[(0.09, 0.08, 0.21), (0.20, 0.17, 0.36), (0.36, 0.30, 0.54)],      # target_corps MODES["night"]
    ink=(0.05, 0.04, 0.09), haze=(0.08, 0.06, 0.16), haze_k=0.34, bloom=0.75, spill=0.5, grime=0.15,
    fog=(0.20, 0.17, 0.33), fog_k=0.22, grade=(0.94, 0.92, 1.04),
    match_sat=0.64, match_gain=(0.76, 0.76, 0.84),                           # sb_mhq.MATCH (capture calibration)
    rain=(0.75, 0.82, 1.0), rain_a=0.11,
)

# ---------------------------------------------------------------- cameras (perspective; BU world, x east, y north)
# yaw 135 / the game's map direction: the camera stands on the lot +x +y side looking toward lot -x -y (the coast).
CAMS = {
    "hero": dict(res=(3840, 2160), lens=28.0, pitch=47.0, yaw=135.0, dist=1100.0, target_ab=(0.0, 18.0), sy=0.0),
    "dbg_top": dict(res=(1280, 720), lens=35.0, pitch=70.0, yaw=135.0, dist=260.0, target_ab=(-6.0, 72.0), sy=0.0),
    "dbg_orb": dict(res=(1280, 720), lens=35.0, pitch=35.0, yaw=135.0, dist=170.0, target_ab=(-28.4, -18.4), sy=0.0),
    "dbg_rc": dict(res=(1280, 720), lens=30.0, pitch=32.0, yaw=135.0, dist=170.0, target_ab=(-0.1, -43.3), sy=0.0),
    "dbg_rail": dict(res=(1280, 720), lens=28.0, pitch=42.0, yaw=135.0, dist=330.0, target_ab=(30.0, 52.0), sy=0.0),
    "close": dict(res=(2560, 1440), lens=24.0, pitch=42.0, yaw=135.0, dist=175.0, target_ab=(-8.0, 74.0), sy=0.0),
}

# ---------------------------------------------------------------- landmark footprints (BU from the HQ lot, world axes)
# zoning L2 builds city blocks right up to these (designer: no open belt or plinth round any HQ)
LANDMARK_FP = {
    "halcyon": ("sq", 30.0),           # the pyramid's bottom tier (no podium)
    "meridian": ("sq", 32.0),          # the container walls + corner towers
    "solace": ("circ", 12.5),          # the two tubes and their base drum
    "orbital": ("circ", 24.0),         # the launch podium (silo, rocket, gantry, antenna on it)
    "aurelian": ("ell", 36.0, 30.0),   # the circus + its four campanili
    "tethys": ("circ", 34.0),          # the station in the lagoon (no refill: water)
    "rebel_cell": None,                # no landmark building: the whole base lot is city
}
LANDMARK_NO_REFILL = ("tethys",)

# the coast as a BAY (zoning Z6): the seawall bows out to sea round the drowned quarter; headlands past it
BAY = dict(depth=16.0, width=60.0, head_start=120.0, head_k=0.004, min_water=2.0)
REBEL_H = 0.7              # REBEL_CELL building heights x this (the low street canyon, art review)
# outlines (art review: the roof-trim / lane grid read as the rejected wireframe look)
OUTLINE = dict(trim_off_k=0.25, lamp_p=0.35, lane_off_k=0.25, ring_trim_p=0.025, ring_major_k=0.3, ring_minor_k=0.08)
# the Meridian freight rail (designer, HQ revision): gate offset from the HQ centre (world BU), viaduct numbers
# (art director ruling, pipeline spec) the line leaves through the NORTH rail-yard gate (gate_u: world x offset of the
# gate along the north wall; wall_s: the wall line from the HQ centre; gate_out: the first track point outside it);
# the viaduct deck stands at deck_z so it clears the tallest frontage; buildings within side_d lots of the line are
# capped at side_cap BU (roof top); the deck ramps up over ramp BU from the gate and down over end_ramp BU to the
# terminal on the seawall. The polyline (world BU) is exported to rail_json for the HQ kit.
RAIL = dict(gate_u=5.0, wall_s=28.0, gate_out=6.0, coast_reach=3.0, deck_z=17.5, pier_step=7.0, ramp=60.0, end_ramp=45.0,
            signal_step=36.0, side_cap=15.5, side_d=1.2, rail_json=os.path.join(SCR, "meridian_rail.json"))
