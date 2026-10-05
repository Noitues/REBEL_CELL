"""ART-5 5b: the shared settings of the landmark pipeline (v1). Pure Python: imported by the Blender driver
(landmark_build_v1.py), the preview finish (landmark_post_v1.py) and the orchestrator (build_landmarks_v1.py).

Every landmark is one glTF 2.0 binary per job. Coordinates: the concept's Blender world (x = lot x, y = -lot y,
z up; 1 unit = 1 BU, 1 lot = LOT_BU BU), which the glTF exporter's +Y-up conversion turns into the game's 3D
frame exactly (CityIsoCamera.lot_to_world: x = lot x * LOT_BU, y up, z = lot y * LOT_BU). The origin of each job
is the centre of its lot rectangle on the ground.
"""

VERSION = "v1"
LOT_BU = 6.0
HQ_LOTS = 10          # NeonCity.HQ_LOTS: an HQ owns a 10 x 10 lot rectangle
SITE_LOTS = 6         # a regular Site stands on a 6 x 6 lot block (concept hq_scene: "scaled onto their 6 x 6 lot block")
SITE_SCALE = 0.80     # concept hq_scene: new Sites are built at 0.80 ...
SITE_ROT = 0.0        # the locked Site renders (rounds 26-27) have the front facing -y (lot -y, screen lower-left):
                      # their build_at meant to turn them 45 deg but only turned the sign objects (it moved the
                      # geometry without rotating it), so the references show them unturned; we match the references

# the game's one iso camera (bible 4.1, CityIsoCamera): yaw 135, pitch 40; screen right / up in the concept frame
YAW, PITCH = 135.0, 40.0

# the reference camera of each job: (camera location, target, lens mm) in the concept frame, from the concept's
# hq_scene.CAMS (round 26) and the round 31 Meridian override; "iso" = the game's ortho camera at `ortho` BU wide.
DIAG = (0.7071067811865476, -0.7071067811865476)


def _diag(D, Hc, Zt):
    return ((DIAG[0] * D, DIAG[1] * D, Hc), (0.0, 0.0, Zt), 34.0)


JOBS = {
    "meridian_hq": dict(corp="meridian", kind="hq", concept_job="meridian_hq", states=[""],
                        cam=((0.0, 150.0, 60.0), (0.0, 22.0, 15.0), 34.0),
                        refs=["city/round31_meridian_combat/combat_meridian.jpg"],
                        what="Container castle: texture A (raw corrugated steel), lower walls, faceted moat, gantry crane keep, rail yard and the 20-frame crane + train loop"),
    "solace_hq": dict(corp="solace", kind="hq", concept_job="solace_hq", states=[""], cam=_diag(240, 84, 60),
                      refs=["city/round26_hq_targets/hq_solace_close_night.jpg", "city/round26_hq_targets/hq_solace_close_day.jpg"],
                      what="Lit DNA double helix: down-lights, light cones, the spotlight up the axis and the 12-frame LED chaser"),
    "solace_site": dict(corp="solace", kind="site", concept_job="solace_site", states=[""], cam=_diag(80, 54, 9),
                        refs=["city/round26_hq_targets/site_solace_night.jpg"],
                        what="SOLACE GENERAL hospital: clinic block, wings, lime cross, ambulance bay, helipad"),
    "halcyon_hq": dict(corp="halcyon", kind="hq", concept_job="halcyon_hq", states=[""], cam=_diag(205, 86, 50),
                       refs=["city/round26_hq_targets/hq_halcyon_close_night.jpg", "city/round26_hq_targets/hq_halcyon_close_day.jpg"],
                       what="Seven-tier Civic Core with stair ramps and the scanning eye (its own pivot, +/-55 deg sweep, searchlight)"),
    "halcyon_site": dict(corp="halcyon", kind="site", concept_job="halcyon_site", states=["court"], cam=_diag(80, 54, 9),
                         refs=["city/round27_hq_targets/site_halcyon_court_night.jpg"],
                         what="Halcyon Court: temple front, pediment eye, the Justice statue with the eye for a blindfold and lit scales"),
    "orbital_hq": dict(corp="orbital", kind="hq", concept_job="orbital_hq", states=["", "open"], cam=_diag(120, 70, 22),
                       refs=["city/round26_hq_targets/hq_orbital_close_night.jpg", "city/round26_hq_targets/hq_orbital_close_night_open.jpg",
                             "city/round26_hq_targets/hq_orbital_close_day.jpg"],
                       what="Silo crescent: launch podium, in-ground silo with the doors 1.6 below the rim (closed / open with the rocket), mast and dishes"),
    "orbital_site": dict(corp="orbital", kind="site", concept_job="orbital_site", states=[""], cam=_diag(80, 54, 9),
                         refs=["city/round26_hq_targets/site_orbital_night.jpg"],
                         what="OC-TV station: studio, roof dishes, lattice mast with red lights, the big screen, uplink truck"),
    "rebel_cell_district": dict(corp="rebel_cell", kind="district", concept_job="rebel_cell_hq", states=["home", "dispatch"],
                                cam="iso", iso_ortho=300.0,
                                refs=["city/round34_rebel_cell/map_A_home.jpg", "city/round34_rebel_cell/map_fist_reveal.frames.jpg"],
                                what="The Cell's district: a normal street grid whose window lights draw the tucked-thumb fist in red, with the blackout ring and the reveal"),
}

# folder per corp under assets/city/landmarks/
CORPS = ["meridian", "solace", "halcyon", "orbital", "rebel_cell"]

# animation timing (concept GIFs): seconds per frame
FRAME_S = {"meridian_hq": 0.150, "solace_hq": 0.090, "halcyon_hq": 0.110, "rebel_cell_district": 0.200}

# REBEL_CELL crest (round 34 map34, variant A, toned down): sizes in BU on the iso screen plane
CREST_H_BU = 110.0          # map34 CREST_H 880 city px / 8.0 px per BU
CREST_LIFT_BU = 37.5        # map34 CREST_LIFT 300 px: the crest centre stands this far above the palm's ground point
CREST_UNITS_H = 14.8        # the crest's own unit grid (map34.Crest: k = H / 14.8)
RING_RX, RING_RY = 0.62, 0.55   # blackout ring radii, in crest heights
WIN_DENSITY = {"home": 0.70, "dispatch": 0.90}   # bible 4.4: red-window density in the fist
REVEAL_Q = [0.0, 0.0, 0.0, 0.1, 0.22, 0.36, 0.5, 0.64, 0.78, 0.9, 1.0, 1.0, 1.0, 1.0]  # map_all34.Q, 200 ms a frame
RED = {"home": (200, 58, 56), "dispatch": (240, 24, 36)}   # map34.RED (sRGB 0-255)
DISTRICT_LOTS = 32          # the standalone district patch: 32 x 32 lots around the palm

# glTF NORMAL: the landmark shader shades with the flat facet normal from screen derivatives
EXPORT_NORMALS = False   # art_export/1 (8p): no normals; tested: the Solace strands shade the same with or without
TONE = (0.86, 1.12)      # target_corps.mat_toon tone jitter range, baked into COLOR_0
PART_ALPHA = (0.55, 1.0) # COLOR_0.a range of the toon roles (the part value written to ROUGHNESS)

# sign text curve resolution (Blender default 12): 2 keeps the letters' corners and a tenth of the triangles
TEXT_RESOLUTION = 2
