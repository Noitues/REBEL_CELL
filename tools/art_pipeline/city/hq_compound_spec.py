"""ART-8 8p: the HQ compound layout per corporation (plain Python, no bpy).

One source for three consumers:
  - build_hq_compound.py (Blender) builds the static compound and writes the anchors into the manifest;
  - make_hq_compounds.py writes content/city/hq_compounds/<corp>.tres (HqCompoundLayoutData) from it;
  - validate_hq_compounds.py checks the exports and the .tres against it.

Frame: the concept's Blender frame (x, y, z), z up, 1 BU = 1 glTF metre; the compound's ground centre is the
origin. Godot / glTF is (x, z, -y) (CityIsoCamera's note). Slot rows follow the CURRENT HQ-run rules: the netrun map
(GDD 4.2: map_layers layers, map_nodes_min..map_nodes_max nodes, the last layer the single final node) sits on the
compound as rows of map_nodes_max slots for layers 1..map_layers-1, and the final node (and the single breach node
of today's boss run) is the Central Server. Every slot sits on a static part of the model (a wall top, a terrace,
the podium, a roof), never on a part that moves under G12 (train, trolley, silo doors, rocket).

Within a row the slots are sorted left to right on screen at the city azimuth (camera at +x -y looking at -x +y:
screen right = +x +y), so the generator's non-crossing edge order (index order) stays non-crossing on screen.
"""
import math

CORPS = ["meridian", "solace", "halcyon", "orbital", "rebel_cell"]
LAYERS = 6           # campaign_config map_layers - 1 (the last layer is the Central Server)
SLOTS = 4            # campaign_config map_nodes_max
PITCH_DEG = 55.0     # bible 4.7: overhead compound at the city azimuth, 55 deg
YAW_DEG = 135.0      # CityIsoCamera yaw (camera on the +x -y diagonal)
# target_corps.TINT: the corp tint on the toon ramp (round 24), carried to the toon shader through the manifest.
RAMP_TINT = {"meridian": (1.0, 1.0, 1.0), "solace": (0.92, 1.07, 0.96), "halcyon": (1.0, 0.94, 1.08),
             "orbital": (0.76, 1.02, 1.12), "rebel_cell": (1.16, 0.88, 0.92)}
TONE = (0.86, 1.12)  # target_corps.mat_toon per-triangle tone range, baked into the vertex colours
ANCHOR_LIFT = 0.3    # build_hq_compound.LIFT: an anchor stands this far above its surface
MIN_SLOT_PX = 50.0   # slots (and the server) at least this far apart on screen at the reference framing
REF_WIDTH_PX = 1920.0
SNAP_BELOW = 4.5    # a slot's surface must lie within nominal z + 3 .. nominal z - SNAP_BELOW

# heroes26 / mer43_nodes heights
HC = 5.2
WALL = 2 * HC + 0.6
TOWER = 4 * HC + 0.6
GATE = 3 * HC + 0.6
YARD = 0.8
PORTAL = 31.6        # crane_dyn portal deck (zp 30 + beam)
KEEP = 37.2          # crane_dyn machinery house roof


def screen_x(p, yaw_deg=YAW_DEG):
    """How far right on screen a Blender-frame point is at camera yaw `yaw_deg` (CityIsoCamera.right() is Godot
    (sin yaw, 0, cos yaw) = Blender (sin yaw, -cos yaw)); the city azimuth (135 deg) gives (x + y) / sqrt 2."""
    a = math.radians(yaw_deg)
    return p[0] * math.sin(a) - p[1] * math.cos(a)


def _rows_sorted(rows, yaw_deg=YAW_DEG):
    return [sorted(r, key=lambda p: screen_x(p, yaw_deg)) for r in rows]


def _meridian():
    rows = [
        # south lane (wall top) on the left, north / back lane on the right, the keep between; all close on the server tower
        [(18.0, -18.0, TOWER), (18.0, -6.6, GATE), (18.0, 6.6, GATE), (18.0, 18.0, TOWER)],           # front towers + gatehouse
        [(9.0, -18.0, WALL), (12.0, -11.0, YARD), (7.0, 11.0, YARD), (9.0, 18.0, WALL)],             # walls, front yard
        [(3.0, -18.0, WALL), (9.0, -7.0, PORTAL), (9.0, 7.0, PORTAL), (3.0, 18.0, WALL)],             # walls, keep portal
        [(-3.0, -18.0, WALL), (-18.0, 11.0, WALL), (0.0, -4.0, KEEP), (-8.0, 18.0, WALL)],             # walls, keep house
        [(-9.0, -18.0, WALL), (-18.0, -5.0, WALL), (-18.0, 4.0, WALL), (-18.0, 18.0, TOWER)],         # walls, back wall, t3
        [(-18.0, -11.0, WALL), (-14.0, -6.0, YARD), (-14.0, 3.0, YARD), (-14.0, 11.0, YARD)],         # the back yard by the server
    ]
    return dict(rows=rows, server=(-18.0, -18.0, TOWER), entry=(40.0, 0.0, 0.5),
                camera=((4.0, 12.0, 6.0), 150.0), server_name="THE MASTER MANIFEST")


def _solace():
    # heroes42 sol_strand(0): radius 13.5, z 6.5..108, 2.6 turns, 160 steps, strand A at -45 deg, B opposite.
    R, Z0, Z1, TURNS, N = 13.5, 6.5, 108.0, 2.6, 160

    def strand(i, b):
        t = i / N
        a = t * TURNS * 2 * math.pi + math.radians(-45.0) + (math.pi if b else 0.0)
        z = Z0 + t * (Z1 - Z0)
        return (round(R * 1.12 * math.cos(a), 3), round(R * 1.12 * math.sin(a), 3), round(z + 3.2, 3))
    rows = []
    for k in range(LAYERS):
        i = 15 + 20 * k  # spacing searched for the widest gap between slots at the reference framing
        rows.append([strand(i, False), strand(i + 9, False), strand(i, True), strand(i + 9, True)])  # both strands
    top = strand(N, False)
    return dict(rows=rows, server=(top[0] / 1.12, top[1] / 1.12, 111.4), entry=(16.0, -16.0, 3.7),
                camera=((0.0, 0.0, 58.0), 190.0), server_name="THE GENOME CORE")


def _halcyon():
    # heroes43 H_TIERS: the switchback terraces on the -Y face (half size, terrace height).
    tiers = [(27, 9), (23.5, 18), (20, 27), (16.5, 36), (13.5, 45), (10.5, 54)]
    rows = []
    for hs, z in tiers:
        rows.append([(round((-0.78 + 1.56 * (i + 0.5) / SLOTS) * hs, 3), -hs + 2.0, z + 0.6) for i in range(SLOTS)])
    return dict(rows=rows, server=(0.0, -5.0, 62.6), entry=(0.0, -40.0, 0.5),
                camera=((2.0, -12.0, 36.0), 112.0), server_name="THE PANOPTICON")


def _orbital():
    # The podium (annulus r 12.5..28 at PZ 6); rows close in from the steps (-45 deg) round both sides to Launch
    # Control at the mast foot (135 deg). Small dishes at 60 / 210 deg, big dishes at 90 / 180 deg.
    PZ = 6.0

    def at(deg, r, z):
        a = math.radians(deg)
        return (round(r * math.cos(a), 3), round(r * math.sin(a), 3), z)
    rows = []
    for phi in (18.0, 45.0, 75.0):
        rows.append([at(-45.0 - phi, 24.5, PZ + 0.1), at(-45.0 - phi, 16.0, PZ + 0.1),
                     at(-45.0 + phi, 16.0, PZ + 0.1), at(-45.0 + phi, 24.5, PZ + 0.1)])
    rows.append([at(210.0, 23.5, PZ + 7.0), at(200.0, 15.5, PZ + 0.1), at(70.0, 15.5, PZ + 0.1), at(60.0, 23.5, PZ + 7.0)])
    rows.append([at(180.0, 20.5, PZ + 18.0), at(165.0, 15.5, PZ + 0.1), at(105.0, 15.5, PZ + 0.1), at(90.0, 20.5, PZ + 18.0)])
    rows.append([at(150.0, 24.5, PZ + 0.1), at(143.0, 15.0, PZ + 0.1), at(127.0, 15.0, PZ + 0.1), at(120.0, 24.5, PZ + 0.1)])
    return dict(rows=rows, server=at(135.0, 20.0, PZ + 6.0), entry=(19.0, -19.0, PZ + 0.5),
                camera=((0.0, 0.0, 14.0), 125.0), server_name="LAUNCH CONTROL")


# ART-8 8w: DISPATCH's HQ run plays in the round 43 Tokyo canyon (DECISIONS, resolved open question), built by
# build_dispatch_canyon.py from round 34's street34 / cfg28. The canyon frame: local x across the street (+x = the
# right side, FIST_SIDE), local y along it from the camera end (0 .. CANYON_LEN); the export's origin is its midpoint
# on the centre line, so Blender (x, y) = (CANYON_HALF - local y, local x).
CANYON_LEN = 114.0        # cfg28.Cfg.canyon_len(): (46 - 27) lots x 6 BU
CANYON_HALF = CANYON_LEN / 2.0
CANYON_LOT_CENTRE = (46.0 - CANYON_HALF / 6.0, 36.5)  # cfg28 canyon_origin() moved half the street along it (lots)
CANYON_FLOOR_PAD = 9.0    # the alley floor runs this far past both ends (BU): the camera end and the head crossing
CANYON_ROWS_Y = (10.0, 28.0, 46.0, 64.0, 80.0, 100.0)  # layer rows along the street (local y); row 5 sits at 80 so its roof
# slots stay on the low shophouses in front of the tall one at 86 (82 put them 18 px / 1 px from row 6 on screen)
CANYON_ALLEY_X = 0.9      # alley slots: either side of the centre line, inside the shop awnings (street34: to 1.2)
CANYON_ALLEY_STAGGER = 8.0  # the right alley slot stands this far up the street from the left one (apart on screen)
CANYON_ROOF_X = 5.4       # rooftop slots: the front of the shophouse roofs (SW + 2.2)
CANYON_ROOF_Z = 40.0      # rooftop slots snap down from above the tallest shophouse (street34: <= ~30 BU)
CANYON_ROOF_SEEK = (0.0, -2.0, -4.0, -6.0, -8.0)  # a rooftop slot over a gap moves toward the camera end to a roof
# (never up the street, where it would climb onto the next row's roof and close the gap on screen)
CANYON_YAW_DEG = 180.0    # the HQ-run camera looks down the canyon (toward lot -x, as round 34's camera)
CANYON_PITCH_DEG = 40.0   # the city's own pitch (the canyon's sides stay readable as rooftops)


def _canyon_b(lx, ly, z):
    return (round(CANYON_HALF - ly, 3), round(lx, 3), z)


def _rebel_cell():
    # The canyon: per layer, the left rooftop, both pavement edges and the right rooftop (round 43 Sync Strike's three
    # lanes: left rooftops, the alley, right rooftops); DISPATCH CORE on the REBEL_CELL billboard over the head crossing.
    rows = [[_canyon_b(-CANYON_ROOF_X, y, CANYON_ROOF_Z), _canyon_b(-CANYON_ALLEY_X, y, 0.5),
             _canyon_b(CANYON_ALLEY_X, y + CANYON_ALLEY_STAGGER, 0.5), _canyon_b(CANYON_ROOF_X, y, CANYON_ROOF_Z)] for y in CANYON_ROWS_Y]
    # DISPATCH CORE stands in the head crossing under the REBEL_CELL billboard (its screen has no top to stand on).
    return dict(rows=rows, server=_canyon_b(0.0, CANYON_LEN + 1.0, 0.5), entry=_canyon_b(0.0, -8.0, 0.5),
                camera=((0.0, 0.0, 6.0), 170.0), server_name="DISPATCH CORE", yaw=CANYON_YAW_DEG, pitch=CANYON_PITCH_DEG,
                snap_below=CANYON_ROOF_Z, seek=CANYON_ROOF_SEEK, lot_centre=CANYON_LOT_CENTRE, builder="build_dispatch_canyon.py",
                origin="the canyon's midpoint on its centre line at (0, 0, 0); place it on lot point place_lot (round 34's "
                       "own canyon lots: the grid street j 36, i 27..46, beside the Cell's palm)")


_BUILD = {"meridian": _meridian, "solace": _solace, "halcyon": _halcyon, "orbital": _orbital, "rebel_cell": _rebel_cell}


def layout(corp):
    """The compound layout of `corp`: rows (LAYERS x SLOTS, sorted left to right), server, entry, camera, name."""
    d = _BUILD[corp]()
    d.setdefault("yaw", YAW_DEG)
    d.setdefault("pitch", PITCH_DEG)
    d.setdefault("snap_below", SNAP_BELOW)
    d.setdefault("builder", "build_hq_compound.py")
    d["rows"] = _rows_sorted(d["rows"], d["yaw"])
    assert len(d["rows"]) == LAYERS and all(len(r) == SLOTS for r in d["rows"]), corp
    return d


def screen_px(p_godot, ortho, yaw_deg=YAW_DEG, pitch_deg=PITCH_DEG):
    """A Godot-frame point on screen (px, y up) at the reference camera (REF_WIDTH_PX wide; the city azimuth at
    PITCH_DEG unless the layout has its own camera)."""
    x, y, z = p_godot[0], -p_godot[2], p_godot[1]
    ppu = REF_WIDTH_PX / ortho
    el = math.radians(pitch_deg)
    a = math.radians(yaw_deg)
    right = x * math.sin(a) - y * math.cos(a)
    away = x * math.cos(a) + y * math.sin(a)  # along the view on the ground (Blender frame of CityIsoCamera.forward())
    return (right * ppu, (away * math.sin(el) + z * math.cos(el)) * ppu)


def to_blender(p):
    """Godot / glTF (x, y, z) -> Blender (x, -z, y)."""
    return (p[0], -p[2], p[1])


def to_godot(p):
    """Blender (x, y, z) -> Godot / glTF (x, z, -y)."""
    return (p[0], p[2], -p[1])
