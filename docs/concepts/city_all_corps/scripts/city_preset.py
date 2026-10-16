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
    # revision 2 (art director): one beam per landmark, the storyboard r3 shaft (m44/onecity_cycles.py): emissive
    # cone (camera only) len BU, half-angle half deg, core / soft gaussians, gone by fade of its length; plus a wide
    # soft haze spot (fog only)
    beam=dict(len=420.0, half=1.1, core_s=0.13, soft_s=0.42, core_w=1.0, soft_w=0.3, efold=0.22, fade=0.6, hot=0.5,
              noise=0.012, emit=1.1, lean=0.35, haze_power=1.2e7, haze_cone=30.0),
    step_rate=3.0, max_steps=256,
    exposure=1.0,
    black_point=0.85,        # post: share of the frame's 5th-percentile (per channel) taken off as the fog veil
    targets=dict(median=0.155, under_010=(0.25, 0.40), over_085_max=0.025),   # designer r3b: lift to 0.15-0.16 (band 0.14 +- 0.03)
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
    "hero": dict(res=(3840, 2160), lens=28.0, pitch=47.0, yaw=135.0, dist=1180.0, target_ab=(0.0, 9.0), sy=0.0),
    "dbg_top": dict(res=(1280, 720), lens=35.0, pitch=70.0, yaw=135.0, dist=260.0, target_ab=(-6.0, 72.0), sy=0.0),
    "dbg_orb": dict(res=(1280, 720), lens=35.0, pitch=35.0, yaw=135.0, dist=170.0, target_ab=(-45.9, -24.4), sy=0.0),
    "dbg_aur": dict(res=(1280, 720), lens=35.0, pitch=38.0, yaw=135.0, dist=190.0, target_ab=(-1.8, -53.0), sy=0.0),
    "dbg_hw": dict(res=(1280, 720), lens=30.0, pitch=40.0, yaw=135.0, dist=420.0, target_ab=(5.0, -10.0), sy=0.0),
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
OUTLINE = dict(trim_off_k=0.25, lamp_p=0.35, lane_off_k=0.25, ring_trim_p=0.025, ring_major_k=0.09, ring_minor_k=0.024,
               out_k=0.3, ring_lamp_p=0.3, ring_wl=0.14)   # revision 2: outside the seven districts (sprawl + ring) trims and
               # lanes at out_k; ring roof lamps at ring_lamp_p and ring window lit share ring_wl carry the outer city
# the Meridian freight rail (designer, HQ revision): gate offset from the HQ centre (world BU), viaduct numbers
# (art director ruling, pipeline spec) the line leaves through the NORTH rail-yard gate (gate_u: world x offset of the
# gate along the north wall; wall_s: the wall line from the HQ centre; gate_out: the first track point outside it);
# the viaduct deck stands at deck_z so it clears the tallest frontage; buildings within side_d lots of the line are
# capped at side_cap BU (roof top); the deck ramps up over ramp BU from the gate and down over end_ramp BU to the
# terminal on the seawall. The polyline (world BU) is exported to rail_json for the HQ kit.
RAIL = dict(gate_u=5.0, wall_s=28.0, gate_out=6.0, coast_reach=3.0, deck_z=17.5, pier_step=7.0, ramp=60.0, end_ramp=45.0,
            signal_step=36.0, side_cap=15.5, side_d=1.2, glow_w=0.45, glow_k=0.9, trains=((0.22, 34.0, True), (0.50, 28.0, False), (0.78, 30.0, True)), rail_json=os.path.join(SCR, "meridian_rail_r3.json"))   # round 3: its own file (the HQ kit keeps reading the round-2 meridian_rail.json until the HQ moves)

# ================================================================ round 3 (designer review of round 1, 2026-10-16)
# H1 (note 7 + 8) the HQ layout: REBEL_CELL is the city centre (no landmark, the centre of the sprawl); the six corp HQs
# sit on bearings round it (degrees in the screen-aligned (a, b) plane: a right, b away from the map camera; 90 = toward
# the coast) at radius r (lots). Tethys keeps its pole over the drowned quarter (zoning L1). The lot is rounded to the
# nearest whole lot. Min pairwise HQ distance goes from 30 (round 2) to 52 lots.
HQ_LAYOUT = dict(
    rebel_cell=dict(centre=True),
    meridian=dict(bearing=32.0, r=52.0),
    solace=dict(bearing=150.0, r=50.0),
    orbital=dict(bearing=208.0, r=52.0),
    aurelian=dict(bearing=268.0, r=53.0),
    halcyon=dict(bearing=326.0, r=52.0),
    tethys=dict(pole=True),
)
# H2 (note 5) district colour by influence: every building draws its district from the HQs, weight exp(-d / lam) per
# HQ (d in lots), against a constant sprawl weight exp(-d0 / lam); the draw is seeded per building key. So a corp's
# colour is near-solid at its HQ, thins with distance, and mixes with its neighbours and the sprawl at the borders.
# The urban core factor u (H3) scales every corp weight (outside the core the city is sprawl). Drowned buildings stay
# Tethys (the lapsed ward is Tethys' own). rebel_cell draws its LANGUAGE (the canyon) but its palette is the sprawl's
# in this key art (note 8: the red appears only later in the game; no red glow, no fist windows, no beam).
INFLUENCE = dict(lam=10.0, d0=23.0, own_k=8.0, lam_k=dict(rebel_cell=0.75, tethys=1.15), seed=7711)
REBEL_KEYART_PALETTE = ""      # the district whose mat / win / hue / glow REBEL_CELL wears here ("" = the sprawl)
# H3 (note 6) the organic city edge: the urban core is a superellipse (power p) round the centre, radius r0 lots,
# broken by seeded harmonics (amp, harmonics k=2..kmax) and a 2D value-noise term (amp_n, cell lots); u = 1 inside,
# fading over `fade` lots (slow, so the light dies gradually into the sprawl). Ring buildings inside the core become city
# buildings (heights, lit share, district colour); map buildings outside it go dim and low.
URBAN = dict(r0=68.0, p=3.2, amp=0.24, kmax=7, amp_n=15.0, cell=9.0, amp_f=8.0, cell_f=4.0, fade=26.0, seed=7712, ring_conv=2.5, ring_merge=0.45, ring_h_k=0.62,
             h_k=(0.45, 1.0), lit_k=(0.22, 1.0), ring_city_h=(7.5, 0.75), ring_city_lit=0.30, glow_floor=0.18)
# H4 (note 4) highways: elevated multi-lane decks over the longest arterial street lines (both lot axes), clear of the
# landmark clearances, continued straight out through the sprawl ring (its blocks are kept off the line) and ramped down
# before the drowned quarter / the coast. Light trails: 2 lanes each way, heads warm white, tails red; in the ring they
# thin out (density and brightness x exp(-ext / thin) lots past the map). Day: the same draws become cars.
HIGHWAY = dict(per_axis=(2, 1), min_sep=34.0, clear_hq=1.5, z=(24.0, 30.0), width=5.4, pier_step=12.0, ext=120.0,
               ramp=50.0, coast_stop=6.0, thin=55.0, lane_off=(0.7, 1.75), streak_len=(6.0, 30.0), gap=(1.0, 12.0),
               edge_col=(0.75, 0.85, 1.0), edge_k=0.55, lamp_step=14.0, lamp_col=(1.0, 0.7, 0.36), side_cap_d=0.0)
# H5 (note 4) the elevated metro: one loop line through a waypoint per corp at `way_k` of the way from the centre to its
# HQ (bearing order), routed over street centre lines by a Dijkstra with a turn cost (few corners), avoiding the
# highway / rail lines (cost x avoid_k) and the landmark clearances; deck at z; stations at the waypoints; lit trains.
METRO = dict(way_k=0.6, z=12.0, width=3.0, turn=6.0, avoid_k=12.0, pier_step=9.0, edge_col=(0.55, 0.95, 1.0), edge_k=1.2,
             trains=7, car_len=3.2, cars=5, train_col=(0.8, 0.95, 1.0), station=(12.0, 4.6))
# ---- round 3b (designer notes on the r3 tests): no 90-degree turns, a port, a Meridian transport hub
# T1 every highway / rail / metro path is a centripetal Catmull-Rom curve (sampled every `step` lots); the corridor
# (half width + margin) is cleared of buildings in the map and kept off by the ring
CURVES = dict(step=0.5, clear_margin=0.35)
# T2 the PORT (rail terminus): a raised terminal platform on the coast stretch a in [a0, a1] (lots, screen-across), far
# from the drowned quarter; `depth` lots of yard landward of the seawall line, a quay `quay` lots out over the water;
# gantry cranes along the quay, ships moored outside, container stacks, rail yard tracks
PORT = dict(a0=62.0, a1=104.0, depth=13.0, quay=4.0, z=3.6, cranes=6, ships=3, stack_rows=7, entry_a=70.0)
# T3 the Meridian HUB: a ground-level truck ring road round the HQ lot (a rounded square outside the landmark footprint:
# half size = footprint + gap, corner radius r, width w BU), and highway SPOKES that leave it tangentially, ramp up to
# the deck height and run out into the sprawl along smooth curves through these screen-plane waypoints (ab lots)
HUB = dict(gap=10.0, r=16.0, w=10.0, lanes=(1.2, 3.4))
SPOKES = None      # round 3c: replaced by THROUGH (the highways no longer end at the hub: they pass alongside it)
# round 3c (designer notes on the r3b): THROUGH highways run PAST the Meridian truck ring (tangent, a lot or two outside its
# kerb) and on; the freight rail runs past the fort's north side (RAIL_WEST: waypoints in lots from the gate) and on to the port. RING = the perimeter ring highway round the city core (replaces the
# metro circle): the urban edge (u = 0.5) dilated by dil deg, smoothed (sig deg), pushed out by margin lots, held off the
# coast / drowned quarter / port (hold lots), a Catmull-Rom through every `ctrl_deg` degrees; deck z, width.
THROUGH = dict(
    ew=dict(wp=[(-175.0, -8.0), (-60.0, 2.0), (0.0, 9.0), (28.0, 11.0), (46.0, 12.5), (66.0, 17.0), (100.0, 27.0), (140.0, 26.0), (190.0, 20.0)], z=24.0),
    ns=dict(wp=[(8.0, -170.0), (14.0, -120.0), (17.0, -72.0), (21.0, -30.0), (25.0, 0.0), (24.5, 20.0), (27.0, 40.0), (40.0, 56.0), (54.0, 62.0), (66.0, 66.0)], z=30.0, to_port=True),
)
RING = dict(margin=4.0, dil=14.0, sig1=8.0, sig2=4.0, ctrl_deg=4.0, z=12.0, width=6.0, hold=9.0, port_hold=8.0)
RAIL_WEST = dict(west=[(-60.0, 2.0), (-34.0, 0.9), (-14.0, 0.2)], east=[(6.0, -0.3), (11.0, -3.5), (13.5, -10.5)])   # lots from the north gate (x east, y south)
# R1 ramps and interchanges: hub exits (kit DESIGN 14.2: S (0, -158), W (-158, -30), E (158, -30) kit units, x 0.33 here, on the
# outer kerb), slip ramps where a highway crosses the perimeter ring, a cloverleaf where the ring crosses the south highway,
# and on / off ramps down to the arterials (the highways' crossings with arterials in the core, spaced `art_gap` lots)
RAMPS = dict(w=3.0, thick=0.8, step=0.5, hub_exit=dict(S=(0.0, -52.0), W=(-52.0, -10.0), E=(52.0, -10.0)), hub_d=14.0, slip_d=11.0,
             clover_d=7.0, stack_d=8.0, clover_at="ew", art_d=14.0, art_n=3, art_gap=28.0, art_u=0.3, lane_len=22.0, lane_w=1.5, lamp_step=9.0)
# H6 arterial trails continue into the sprawl along their own lines (ring blocks kept off them) and thin out
TRAILS = dict(ext=110.0, thin=40.0)
# H7 (note 2) ORBITAL: no floodlit disc. Spotlights on short masts at the platform edge, aimed at the rocket body.
SOLACE_LIFT = 1.8         # designer r3b: the Solace helix a little brighter (its key + fill spots)
ORBITAL_PAD = dict(n=5, mast_h=6.5, r_in=2.2, aim_z=(10.0, 26.0), cone=11.0, blend=0.35, power=3.5e6, rim_lamp_k=0.45)
# H8 (note 3) AURELIAN: a colonnade of round columns as the outer wall (per tier), the wall recessed behind it, and the
# cavea as stair-stepped terraces (steps per seating ring)
AURELIAN_LM = dict(cols=60, col_r=0.62, recess=1.7, steps=4)
# H9 landmark modules (hook): a corp may be built by an external module instead of the built-in landmarks.py function.
# Value = path to a .py exposing build(ctx) -> dict(label=xyz, crown=xyz or None, hue=rgb); ctx documented in NOTES.md.
# Meridian (hq_meridian_v3) and Tethys (hq_tethys/scripts/tethys_landmark.py) are being redesigned: set the path here.
LANDMARK_MODULES = dict(meridian=None, tethys=None)

# AD r3 review (day test 2): material families by day (weight, albedo; "glass" = a dark glass curtain), roof finishes,
# parks (ring blocks and map plazas), tree clumps
DAY_MATS = dict(
    city=[(0.36, (0.52, 0.50, 0.47)), (0.20, "glass"), (0.16, (0.46, 0.26, 0.19)), (0.12, (0.40, 0.25, 0.15)),
          (0.16, (0.62, 0.60, 0.56))],                               # concrete, glass, brick, rust, pale stone
    sprawl=[(0.22, (0.42, 0.40, 0.37)), (0.32, (0.44, 0.24, 0.17)), (0.30, (0.42, 0.26, 0.14)), (0.16, (0.30, 0.28, 0.27))],
    glass=(0.14, 0.20, 0.24), k=0.6)                                 # k: how far the family pulls the district albedo
DAY_ROOFS = [(0.34, (0.09, 0.09, 0.10)), (0.30, (0.46, 0.44, 0.40)), (0.16, (0.20, 0.32, 0.13)), (0.12, (0.07, 0.09, 0.17)),
             (0.08, (0.55, 0.30, 0.18))]                             # tar, gravel, green roof, solar, terracotta
RING_PARK = dict(p=0.06)
PARKS = dict(plaza_p=0.6, lawn=(0.16, 0.25, 0.10), path=(0.33, 0.31, 0.28), paved=(0.34, 0.33, 0.31), clumps=(2, 5),
             trees=(3, 7), r=(0.55, 1.15), tree_cols=[(0.12, 0.22, 0.07), (0.16, 0.26, 0.09), (0.10, 0.18, 0.08), (0.20, 0.27, 0.10)])
BILLBOARD = dict(day_k=0.35)       # the larger billboards (blade signs, rooftop holo panels) by day, x the night neon

# ---------------------------------------------------------------- DAY look (note 1): late afternoon sun through haze
DAY = dict(
    sun=dict(strength=10.0, col=(1.0, 0.80, 0.56), elev=14.0, azim=80.0, angle=0.5),   # azim: degrees from world +x (CCW)
    sky=dict(zenith=(0.15, 0.29, 0.66), horizon=(0.68, 0.76, 0.88), ground=(0.26, 0.26, 0.27), strength=0.6),
    haze=dict(density=0.0012, h=70.0, col=(0.80, 0.79, 0.76), aniso=0.6, bank=0.008, bank_h=12.0, sea_k=0.7),   # designer r3b: a hazy smog day
    glass=(0.10, 0.12, 0.15), glass_rough=0.07, facade_rough=0.72,
    neon_k=0.22, win_k=0.18, streak_k=0.0, lamp_k=0.0, beams=False, landmark_spot_k=0.0, underwater_k=0.0,
    tint=0.28, tint_near=0.32, tint_r=14.0, water=dict(rough=0.09, wave=0.06, scale=0.08), sea_mist_k=0.0, depth_haze=dict(start=1300.0, efold=2400.0, max=0.9), ground_k=1.7, target_median=0.15, target_spread=0.39, white=6.0, contrast=1.12, contrast_max=3.5, sat=1.0, black_point=0.8, lift=0.05,   # designer r3b: refs (combat_day_boss, mainline_match) median 0.14-0.15, spread 0.39
    car_cols=[(0.75, 0.74, 0.72), (0.12, 0.12, 0.13), (0.55, 0.08, 0.06), (0.85, 0.85, 0.86), (0.2, 0.3, 0.45), (0.9, 0.62, 0.1)],
)


# ================================================================ round 4: LAYOUT A2 "Horseshoe Bay" (designer-approved city plan)
# The 3D city is rebuilt from docs/concepts/city_planner/city_A2.json (metres, origin at the centre, +X east, +Y north,
# +-10 km). SCALE: 1 lot (100 m) = U = 6 BU, so 1 BU = 16.67 m; the plan's 20 km square is 200 lots (1200 BU): the same
# lot count as today's map plus ring (about one building per lot), so building density and the hero camera distance stay
# comparable. Lot coords: x = X / 100 + CX, y = CY - Y / 100 (the lot y axis points south, as before): world BU =
# (X, Y) x 0.06. The screen-aligned (a, b) plane of the legacy layout becomes (a, b) = (X, Y) / 100 (b = north).
LAYOUT_MODE = os.environ.get("CITY_LAYOUT", "a2")          # "a2" (this layout) or "legacy" (the diamond map, rounds 1-3)
A2_JSON = os.path.join(CONCEPTS, "city_planner", "city_A2.json")
A2_FIELDS = os.path.join(SCR, "a2_fields.npz")
A2 = dict(
    m_per_lot=100.0, grid=(-98, -98, 206),                  # raster cell (i, j) = lot cell; grid origin i0, j0 and size n
    core_period=5, sub_period=3,                             # street period (cells) in the districts / the suburbs
    sub_u=0.32, sub_edge=(-4.0, 6.0), edge_noise=5.0,        # suburb urban factor; organic edge: soft width, noise amplitude (cells)
    bld_med={"rebel_cell": 37.5, "aurelian": 34.0, "halcyon": 33.0, "solace": 32.0, "meridian": 19.6, "orbital": 58.0, "tethys": 28.6},
    bld_sigma=0.62, bld_max=430.0, centre_gain=1.4, centre_r=14.0,
    clear=dict(ring=1.0, motorway=1.0, truck=0.9, arterial=0.7, rail=0.8, rail_light=0.3, ramp=0.7),    # corridor half widths (lots)
    z=dict(ring=12.0, ring2=10.0, motorway=(22.0, 26.0), truck=16.0, freight=5.0, commuter=9.0, metro=14.0),
    width=dict(ring=6.4, ring2=5.6, motorway=5.4, truck=4.6),   # deck widths in BU (the real 28-40 m would be 2-2.4 BU: exaggerated to read)
    hold_wall=2.0,
)
if LAYOUT_MODE == "a2":
    ZONED = os.path.join(SCR, "zoned_a2.json")
    WATER["sea_bed"] = (70.0, 170.0)      # A2: a deeper open sea (the shallows would glow with caustics)
    WATER["z"] = 0.0                     # A2: the sea is at 0 and the land stands TERRAIN base above it (a beach into the water); the drowned quarter sits behind dams
    WATER["under_sky"] = dict(WATER["under_sky"], z=-3.0)
    HQ_LAYOUT = {}
    LANDMARK_MODULES = dict(
        meridian=os.path.join(CONCEPTS, "route_map_graph", "hq_meridian_v3", "scripts", "meridian_landmark.py"),
        tethys=os.path.join(CONCEPTS, "route_map_graph", "hq_tethys", "scripts", "tethys_landmark.py"))
if LAYOUT_MODE == "a2":
    # A2 cameras: from the south over the bay looking north (yaw 90): the Old City in the middle, Halcyon / Solace / Orbital /
    # Aurelian round it, Tethys and Meridian on the two shores of the bay; (a, b) = (east, north) in lots
    CAMS = {
        "hero": dict(res=(3840, 2160), lens=28.0, pitch=33.0, yaw=90.0, dist=1130.0, target_ab=(2.0, -2.0), sy=0.0),
        "dbg_top": dict(res=(1280, 720), lens=35.0, pitch=70.0, yaw=90.0, dist=900.0, target_ab=(0.0, 0.0), sy=0.0),
        "dbg_old": dict(res=(1280, 720), lens=35.0, pitch=38.0, yaw=90.0, dist=300.0, target_ab=(7.0, 0.0), sy=0.0),
        "dbg_mer": dict(res=(1280, 720), lens=35.0, pitch=36.0, yaw=90.0, dist=330.0, target_ab=(60.0, -44.0), sy=0.0),
        "dbg_teth": dict(res=(1280, 720), lens=35.0, pitch=36.0, yaw=90.0, dist=300.0, target_ab=(-32.0, -56.0), sy=0.0),
        "dbg_orb": dict(res=(1280, 720), lens=35.0, pitch=36.0, yaw=90.0, dist=260.0, target_ab=(86.0, 4.0), sy=0.0),
        "dbg_port": dict(res=(1280, 720), lens=35.0, pitch=40.0, yaw=90.0, dist=260.0, target_ab=(44.0, -44.0), sy=0.0),
        "dbg_hal": dict(res=(1280, 720), lens=35.0, pitch=36.0, yaw=90.0, dist=260.0, target_ab=(10.0, 56.0), sy=0.0),
        "dbg_sol": dict(res=(1280, 720), lens=35.0, pitch=36.0, yaw=90.0, dist=260.0, target_ab=(-42.0, 48.0), sy=0.0),
        "dbg_aur": dict(res=(1280, 720), lens=35.0, pitch=36.0, yaw=90.0, dist=260.0, target_ab=(-52.0, -14.0), sy=0.0),
        "dbg_isl": dict(res=(1280, 720), lens=35.0, pitch=25.0, yaw=90.0, dist=110.0, target_ab=(-7.0, -59.0), sy=0.0),
    }
    DAY = dict(DAY, sun=dict(DAY["sun"], azim=DAY["sun"]["azim"] - 45.0),      # the sun keeps its angle to the (new) view direction
               target_median=0.25, target_spread=0.36, contrast_max=2.0, lift=0.10)      # round 5: a brighter day, shadows not crushed
if LAYOUT_MODE == "a2":
    # round 5: the terrain (terrain_a2.py): margin cells of ground round the plan grid, hill exaggeration, foothills / mountains
    TERRAIN = dict(base=1.2, margin=170, seed=5101, hill_exag=1.5, foot=(3.0, 30.0), mtn=(24.0, 78.0), foot_h=20.0, mtn_h=125.0, edge_k=0.45, edge=(95.0, 150.0),
                   cliff_h=16.0, outer=(5.0, 34.0), flat_hq=(1.6, 3.2), max_build_slope=0.30, max_build_h=42.0)
