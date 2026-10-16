"""Tethys Deep / ATLANTIS STATION HQ pass (round 2): every tunable in one place. Pure Python (Blender and the post
both import it). Units: BU (1 lot = 6 BU, one floor = 1.9 BU), the city_all_corps conventions. Seeds are fixed here.

The city itself is the city_all_corps build (read-only, imported from its folder); this pass adds:
  PIER     the floating pier city (tethys_landmark.py) that replaces the old ring-and-domes station
  DAM      the inner dam between the dry city and the drowned quarter, its sluice gates, catwalks, warning lights and
           the DOCK LOCK (tethys_quarter.py), replacing the thin stepped levee
  CLUTTER  the drowned streets: kerbs, markings, cars, lamps, signs, debris, kelp cables, drowned shop fronts
  WATER    the clearer-water and caustic overrides on city_preset.WATER
"""
import os

WT = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass"
CONCEPTS = os.path.join(WT, "docs", "concepts")
OUT = os.path.join(CONCEPTS, "route_map_graph", "hq_tethys")
# the city build: a frozen copy of city_all_corps/scripts at commit a032bf6c (revision 2b, the approved close-up's
# code), so the full-city agent's live edits never change this pass; matches the zoning snapshot below
CITY_SCRIPTS = os.path.join(OUT, "scripts", "city_base")
SCR = r"D:\rc_scratch\tethys"
ZONED_BASE = os.path.join(SCR, "zoned_base.json")     # a snapshot of city_all_corps' zoned.json (2026-10-15 23:10)
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
FONTS = os.path.join(WT, "assets", "fonts")

SEEDS = dict(pier=7201, clutter=7202, dam=7203, kelp=7204, cars=7205, signs=7206, fish=7207, whales=7208)

# ---------------------------------------------------------------- palette (identity.md)
ABYSS = (0.184, 0.42, 1.0)          # #2F6BFF the corp hue
RED = (0.78, 0.15, 0.30)            # #C8264E lightless red (material / tier II, never a UI signal)
PHOTO = (0.486, 0.949, 0.894)       # #7CF2E4 photophore (world light only)
DIVE = (1.0, 0.91, 0.72)            # #FFE9B8 dive-light (warm interiors)
SODIUM = (1.0, 0.62, 0.28)          # the dam's work light (the dry city's colour, not the corp's)
HAZARD = (1.0, 0.70, 0.08)

# ---------------------------------------------------------------- the clearer water (designer note 5)
# applied on top of city_preset.WATER: lower extinction (red still dies first), deeper fade, brighter and sharper
# caustics, more shafts, a lighter seabed (so the ripples have something to land on)
WATER = dict(
    sigma=(0.052, 0.017, 0.0072),            # was (0.090, 0.034, 0.016): about half, so streets read 20+ BU down
    inscatter=(0.002, 0.016, 0.050),
    win_boost=2.6,                            # was 1.6: drowned windows read through the water
    caustic=dict(k=3.0, scale=0.095, depth=46.0, col=(0.42, 0.95, 1.0), width=0.11, distort=0.8, floor=0.0, patch=0.30),
    shafts=dict(n=16, power=1.7e7, cone=3.2, density=0.0040, tilt=(0.10, 0.22)),
    surface=dict(rough=0.02, wave=0.05, tint=(0.02, 0.06, 0.12)),     # AD review 2: chop -50 % (was 0.10; r1 0.22)
    under_sky=dict(tile=60.0, power=34000.0, z=-1.2, col=(0.62, 0.88, 1.0)),
)
SEABED_K = 1.7          # the seabed albedo x this (sand under clear water)
# THE DEPTH RULE (round 2): the drowned quarter is a SHALLOW drowned street grid (so the streets and their clutter read
# through the clear water) and the trench is only round the station. Depth = shallow(b) (shallow[0] at the dam ..
# shallow[1] at the seawall), blended to the city_all_corps trench depth inside trench_r (+ blend) of the HQ.
# Drowned towers keep their height; a tower that would now break the surface is cut below it (top_gap BU under),
# except a seeded share `emerge` (the drowned towers that stand out of the water)
DEPTH = dict(shallow=(5.0, 24.0), trench_r=42.0, blend=24.0, emerge=0.10, top_gap=(1.2, 5.0), clear_r=70.0)
WET_LIT = 0.62          # the drowned towers' lit window share (was 0.45)

# ---------------------------------------------------------------- the dam (designer note 3)
# The line: the drowned quarter's land boundary (wet cell edges facing a dry cell, landward of the seawall), the
# minimum b in a +-win window per a step, smoothed; it runs a0..a1 (lots across) and meets the seawall at both ends.
# The profile (BU across the line; + is the wet side; z up): a vertical wet face, a crest road between parapets, a
# stepped dry face with a berm catwalk, counterfort ribs, sluice gate bays, pump houses, floodlight masts.
DAM = dict(
    a_range=(-88.0, 88.0), a_step=1.0, win=2.5, smooth=6,
    wet=6.0, crest_dry=1.2, crest_z=12.0, berm=(-3.0, -4.6, 6.8), toe=-9.5, base_z=-42.0,
    parapet=1.0, conc=(0.40, 0.40, 0.42), conc_dark=(0.26, 0.26, 0.28), steel=(0.20, 0.21, 0.23),
    rib_step=7.0, rib_w=0.9, rib_out=1.1,
    gate_step=44.0, gate_w=9.0, pier_w=3.4, pier_z=18.0, gate_top=9.5, gate_open_every=3,
    pump_every=2,                    # every other gate bay carries a pump house + penstocks down the dry face
    lamp_step=4.0, catwalk_z=5.2, catwalk_w=1.7,
    mast_step=26.0, mast_h=7.0, flood_power=9.0e3, flood_cone=78.0, flood_window=(-75.0, 60.0),
    # uplights: sodium floods on the apron road washing the dry face (the dam reads as a lit wall between dark city
    # and dark water); every up_step of arc where a is inside up_window
    up_step=11.0, up_power=3.5e4, up_cone=64.0, up_window=(-55.0, 45.0), chute_k=(0.10, 0.42),
    clear_dry=(-16.0, 9.0), clear_wet=14.0,       # buildings whose footprint meets this band (BU) are removed
    apron=(-9.5, -15.5), canal=(-9.7, -12.2),
)
# the DOCK LOCK through the dam on the HQ's axis: chamber, mitre gates, the control tower, the dock basin
LOCK = dict(w=8.0, wall=2.2, down=-30.0, basin=-46.0, basin_w=18.0, chamber_z=1.4, basin_z=0.25, tower_h=24.0,
            clear=12.0)
CAUSEWAY = dict(w=4.2, z=5.0, pile_step=7.0, lamp_step=6.0, tube_r=1.5)

# ---------------------------------------------------------------- the pier city (designer note 4: Kamino / Tipoca)
# One dominant central station and its own small copies on stilts, out along six piers, filling the map lot
# (city_preset.LANDMARK_FP tethys = circle r 34 BU). Every pod is the same generator at a smaller scale.
PIER = dict(
    lot_r=34.0,
    hull=(0.50, 0.53, 0.58),          # pressure-hull grey-white (Kamino), lit by the key (AD review 2: was 0.70..0.80)
    hull_dark=(0.30, 0.34, 0.40),
    titan=(0.46, 0.50, 0.56),
    arms=6, arm0=30.0,                 # six piers, the first at this bearing (deg, world)
    # every pod is the station at scale s (plan) and hs (height); the main station itself is drawn at main_s / main_hs
    # so the piers between the pods are long enough to read (Kamino: pods spaced out along walkways)
    main_s=0.80, main_hs=1.05,
    inner=dict(r=20.0, s=0.32, hs=0.42),     # one pod on each pier at r (BU) ...
    outer=dict(r=30.5, s=0.24, hs=0.32),     # one at each pier end ...
    mid=dict(r=26.5, s=0.19, hs=0.27),       # ... and one between each pair of piers, on the ring walkway
    full_hs=0.4,                             # pods at or above this height scale keep the second tier
    deck_z=4.6,                        # walkway decks above the water (ZW 2.5)
    main=dict(stilt_r=9.0, stilts=10, skirt=(9.6, 13.4), z_skirt=(3.6, 6.0), drum=(13.0, 6.0, 12.5),
              cap=(13.0, 0.36), tier=(6.6, 17.5, 23.5), tier_cap=(6.6, 0.55), mast=(1.3, 27.0, 47.0),
              halo=(4.2, 37.0)),
    # AD review 2: the HQ at ~2-2.5x its local background (was 4.5-5x): a softer key on a less white hull, quieter
    # hue rings, warm window detail instead of white glare
    key=dict(power=0.9e6, cone=26.0, col=(0.92, 0.95, 1.0)),
    fill=dict(power=0.45e6, cone=40.0),
    emit_k=0.75,                       # AD review 3: the station's brightest emitters (halo, portholes) x this (-25 %)
    ring_k=0.41,                       # the abyss / photophore rim rings on the station and pods (x the corp hue)
    win_col=(1.0, 0.80, 0.52),         # warm ribbon windows (DIVE pushed warmer) ...
    win_k=0.94,                        # ... and their strength (window colour x this)
    pod_detail=dict(antennas=(2, 3), ant_h=(1.6, 3.4), dish_p=0.6, port_wl=0.75, tip=(1.0, 0.25, 0.25)),
    # THE BREAKWATER (AD review 2): the hex ring walkway is a solid breakwater; inside it the water is glass-calm (no
    # surface chop, low reflection), the see-through window down to the moon pool and the server
    breakwater=dict(w=1.8, z0=-4.0, z1=1.3, calm_r=25.5, calm_soft=3.0, refl_in=0.20, refl_out=0.5, chop_out=1.0,
                    caustic_in=0.03, caustic_surf_out=0.30, caustic_seabed_out=0.30),
    # THE DEEP STAIR + MOON POOL (AD review 2: the server INSIDE the lot): five pressure decks step down from the
    # station along a spine to the server, which sits at the foot of a lit MOON POOL inside the breakwater, screen-left
    # of the station (map frame at yaw 135: seaward = +b, lateral = screen-right). Rule: a thing at depth d projects
    # d / tan(pitch) toward the map camera, so a shallow server beside the station shows through the calm water
    # between the station and the left pods, never behind the station or the dam.
    decks=(-5.0, -8.5, -12.0, -15.5, -19.0),    # deck tops (z rel. ZW)
    deck_r=(5.6, 5.2, 4.8, 4.4, 4.0),
    stair=dict(seaward=-12.0, lateral=-9.0, server_z=-23.0),     # the server's offset (BU, r 16: inside the lot) and depth
    moonpool=dict(r=4.6, step=3.0, k=3.0, collar_k=5.0, cyan=(0.12, 0.95, 1.0), column_k=0.22, light=2.0e5),
    shaft_r=2.6,
    server=dict(ring_r=4.4, ring_w=1.1, rim_col=(1.0, 0.55, 0.20), rim_k=6.0, rim_light=2.0e5, core_k=10.0, abyss_k=3.0, vent_k=5.0, light=2.5e5, chimney_r=1.6, riser_r=0.35,
                riser_k=1.2),
    deep_k=1.8,                        # the deep stair's neon rings and drop lights
    stilt=(0.13, 0.15, 0.19),          # dark stilts: a forest that does not curtain the deep stair
)

# ---------------------------------------------------------------- the drowned streets (designer note 2)
CLUTTER = dict(
    kerb_h=0.25, kerb_w=0.35, half=2.65,
    car_p=0.70, car_n=3, car_flip=0.12, car_lit=0.22,
    car_cols=[(0.42, 0.10, 0.08), (0.14, 0.20, 0.30), (0.40, 0.38, 0.34), (0.10, 0.10, 0.12), (0.46, 0.36, 0.10),
              (0.20, 0.30, 0.26)],
    lamp_p=0.60, lamp_lit=0.60, lamp_lean=0.18, lamp_h=4.6,
    sign_p=0.22, board_p=0.10, board_lit=0.65,
    debris_n=(1, 5), container_p=0.07, bus_p=0.035,
    kelp_n=(1, 4), kelp_tip=0.9, kelp_k=2.2, cable_p=0.35,
    shop_p=0.50, shop_lit=0.62, blade_p=0.38, blade_lit=0.55,
    neon=[(1.0, 0.25, 0.55), (0.25, 0.85, 1.0), (1.0, 0.62, 0.22), (0.75, 0.35, 1.0), (0.486, 0.949, 0.894)],
    reach=480.0,                      # BU from the HQ: clutter only where a camera can see it (the whole quarter)
)

# ---------------------------------------------------------------- cameras (city_preset.CAMS format; added at run time)
CAMS = {
    # the close-up, as tethys_flooded_closeup.png (yaw 135, high aerial over the dam) pulled back a little so the dam
    # crosses the lower third
    "t_close": dict(res=(2560, 1440), lens=24.0, pitch=40.0, yaw=135.0, dist=190.0, target_ab=(-6.0, 72.5), sy=0.0),
    # the HQ netrun OVERVIEW: high 3/4 orbit (pitch 56), the lot + the causeway + the dam + the dry city
    "t_over": dict(res=(1280, 720), lens=30.0, pitch=50.0, yaw=135.0, dist=210.0, target_ab=(-6.3, 71.2), sy=0.0),
}
OCC_CAMS = ("t_over",)       # cameras that apply the occlusion rule (the netrun view; the close-up is key art)


# ---------------------------------------------------------------- the wildlife (designer note, 2026-10-16)
# Fish SHOALS (a small boids run per shoal: separation, alignment, cohesion and a swirl field) swirl round the drowned
# streets, the stilts of the pier city and the piers; some are silver and catch the caustics on their backs, a few carry
# a photophore glint. A migrating POD of WHALES (adults and a calf) passes through the open water beyond the breakwater,
# on an arc round the station, deep enough to clear the drowned towers and lit by one soft cool light under the surface.
# Fish are drawn larger than life (about 1 BU = 1.8 m long) so a shoal reads at the map camera.
WILDLIFE = dict(
    fish=dict(
        length=(2.0, 3.2), n=(40, 80), radius=(2.6, 5.6), steps=9,
        street_max=9, street_big=(40, 70), street_big_R=(5.0, 8.0), street_reach=(40.0, 170.0), open_n=6, open_r=(38.0, 50.0), open_z=(5.0, 11.0), street_z=(2.0, 9.0), street_top=2.4,   # above the bed, below the surface
        kinds=(("drift", 0.5), ("stream", 0.5)),
        cols=[((0.84, 0.90, 0.94), (0.30, 0.42, 0.56)), ((0.74, 0.86, 0.96), (0.22, 0.36, 0.58)),
              ((0.88, 0.70, 0.40), (0.34, 0.26, 0.16)), ((0.78, 0.82, 0.78), (0.22, 0.34, 0.34)),
              ((0.92, 0.46, 0.30), (0.40, 0.18, 0.14))],
        col_w=(4, 4, 2, 3, 1), glint_p=0.30, glint_k=2.0, belly_glow=0.3,
    ),
    whales=dict(
        adults=4, calf=True, L=(19.0, 25.0), calf_k=0.40, arc_r=45.0, phi_deg=22.0, along=(-46.0, -15.0, 16.0, 44.0),
        dr=(0.0, -3.0, 2.0, -1.5), z=(-10.0, -14.5, -9.5, -12.5), clear=3.2, section_n=12, stations=26,
        top=(0.24, 0.31, 0.41), belly=(0.74, 0.80, 0.86), flipper=(0.60, 0.68, 0.76),
        light=dict(power=4.5e5, cone=75.0, col=(0.70, 0.88, 1.0), up=14.0),
    ),
)
