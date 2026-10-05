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


def screen_x(p):
    return (p[0] + p[1]) / math.sqrt(2.0)


def _rows_sorted(rows):
    return [sorted(r, key=screen_x) for r in rows]


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


def _rebel_cell():
    # heroes25 rebel_base (STATE dispatch): six blocks round a courtyard, the relay mast (DISPATCH CORE) in the middle.
    rows = [
        [(-10.0, -18.0, 14.6), (10.0, -20.0, 9.6), (20.0, -15.0, 9.6), (20.0, -2.0, 10.6)],     # front roofs
        [(-20.0, -19.0, 14.6), (-19.0, -8.0, 18.6), (4.0, -10.0, 4.2), (18.0, 9.0, 10.6)],      # roofs, courtyard shack
        [(-19.0, 1.0, 18.6), (-6.0, -6.0, 4.2), (8.0, -2.0, 0.6), (20.0, 19.0, 16.6)],         # the deck, shack, courtyard
        [(-19.0, 9.0, 18.6), (-6.0, 4.0, 4.2), (-3.0, 19.0, 12.6), (11.0, 19.0, 16.6)],        # back roofs
        [(-20.0, 18.0, 12.6), (-11.0, 19.0, 12.6), (14.0, 4.0, 10.6), (5.0, 21.0, 16.6)],      # back roofs
        [(-4.0, -2.0, 0.6), (4.0, -5.0, 0.6), (-2.0, 5.0, 0.6), (5.0, 4.0, 0.6)],              # round the mast
    ]
    return dict(rows=rows, server=(0.0, 0.0, 35.6), entry=(24.0, -24.0, 0.5),
                camera=((0.0, 0.0, 8.0), 125.0), server_name="DISPATCH CORE")


_BUILD = {"meridian": _meridian, "solace": _solace, "halcyon": _halcyon, "orbital": _orbital, "rebel_cell": _rebel_cell}


def layout(corp):
    """The compound layout of `corp`: rows (LAYERS x SLOTS, sorted left to right), server, entry, camera, name."""
    d = _BUILD[corp]()
    d["rows"] = _rows_sorted(d["rows"])
    assert len(d["rows"]) == LAYERS and all(len(r) == SLOTS for r in d["rows"]), corp
    return d


def screen_px(p_godot, ortho):
    """A Godot-frame point on screen (px, y up) at the reference camera (REF_WIDTH_PX wide, PITCH_DEG, the city azimuth)."""
    x, y, z = p_godot[0], -p_godot[2], p_godot[1]
    ppu = REF_WIDTH_PX / ortho
    el = math.radians(PITCH_DEG)
    return ((x + y) / math.sqrt(2.0) * ppu, ((y - x) / math.sqrt(2.0) * math.sin(el) + z * math.cos(el)) * ppu)


def to_godot(p):
    """Blender (x, y, z) -> Godot / glTF (x, z, -y)."""
    return (p[0], p[2], -p[1])
