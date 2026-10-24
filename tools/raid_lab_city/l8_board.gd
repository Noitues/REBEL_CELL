class_name L8Board
extends Node3D
## The city view of raid lab L8 (SPEC section 8, with the L9, L10, L11 and L12 presentation changes). It shows a dark
## slab city block in iso with a long lens. Our amber HQ sits on the left and the cobalt corp HQ on the right. Three
## lit routes and four gray cross streets run between them. Large NORTH / MID / SOUTH labels sit at the corp end of the
## routes, and street numbers 0-3 sit at the north edge. Districts are small building clusters with rings, value pips
## and exploit keys. The board also draws:
## - sentries, the ghost and the sealed candidates;
## - typed vehicles that travel the lines;
## - the hunter: a cobalt hound silhouette with glowing eyes and a small type badge. It stands at the head of its street
##   in PLAN and FORECAST (the outcome overlay) and runs the street in the playout;
## - planned paths (L12): known beams as solid lanes at full strength, the selected candidate dashed at full strength
##   with a pulse, other candidates at 15% alpha with no arrowheads. While paths are shown, cross streets that no line
##   uses are hidden;
## - the playout's trails;
## - a forecast outcome overlay (crack, shield, skull and hunter path glyphs);
## - route verdicts (L12): per sealed route, the tier glyph where the route meets HOME (heart, broken heart or skull);
## - district marks (L12): a cobalt "1" countdown ring next to the wrench of every DOWN district (TAKEN next raid), and
##   a crack decal on a district hit this raid that is OK again (until the next raid);
## - a response preview: an arc arrow in the sentry's type color from the source (a sentry, or the reserve tray at our
##   HQ) to the target cell for REDEPLOY / DEPLOY, and a red cross over the hound for JAM;
## - decay beats, where a cell left DOWN flips to cobalt TAKEN with a pulse;
## - the decided fall beat: our HQ tower turns red and collapses, with a red skull over the rubble;
## - highlights by meaning: an amber plus (capture), a red wrench outline (repair) and a white check ring (picked);
## - the lethal mark: at HOME 1/3 the last HOME pip pulses red and a red skull pulses on our HQ tower.
## Everything is built in code, and it runs inside a SubViewport that the main scene creates. It holds no rule. The lab
## hands it the leg (`setup`), the state (`show_state`), planned lines (`show_paths`), an outcome (`show_outcome`),
## route verdicts (`show_route_verdicts`), a response preview (`show_response_preview`) and a playout's cues (`play`,
## `decay`, `show_fall`); the board only draws them. `set_scramble` swaps the board labels for seeded noise. The camera
## is fitted to the board's real geometry (slab, HQ towers, labels) so it fills the free area left of the side panel,
## with no dark sky margin; the starfield is dimmed. Glow is capped while impacts flash, so hits read as shapes.
## Cosmetic motion is seeded or time-based, never global random.

signal cues_finished

# ======================= tuning (palette, energies, camera, geometry, timings) =======================
const COBALT := Color8(61, 107, 255)
const COBALT_HOT := Color8(159, 192, 255)
const GOLD := Color8(255, 210, 77)
const AMBER := Color8(255, 176, 32)
## Streets are neutral gray, so they never read as the ENFORCER orange.
const STREET_COL := Color8(112, 120, 140)
const ACID := Color8(212, 255, 0)
const RED := Color8(255, 61, 77)
const NET := Color8(92, 225, 255)
const SKY_WIRE := Color8(58, 143, 208)
const GREY := Color8(138, 146, 166)
const LABEL_GREY := Color8(190, 198, 214)
const WHITE := Color8(240, 244, 255)
const DEAD := Color8(35, 37, 44)
const BG := Color8(3, 5, 15)
const FLOOR_COL := Color8(6, 10, 24)
const SLAB_COL := Color8(12, 18, 36)
const ASPHALT := Color8(9, 12, 22)
const STEEL := Color8(26, 30, 46)
const WARM_METAL := Color8(64, 46, 30)
const NEUTRAL_BODY := Color8(30, 32, 38)
const TAKEN_BODY := Color8(18, 28, 72)
const HQ_BODY_HOME := Color8(72, 50, 30)
const HQ_BODY_CORP := Color8(18, 28, 72)
const HOT_WIN := Color8(255, 226, 168)
const AMBIENT := Color8(40, 52, 96)
const KEY_LIGHT := Color(0.55, 0.62, 1.0)
const WARM_LIGHT := Color(1.0, 0.7, 0.4)
const SHADOW_INK := Color(0.0, 0.0, 0.0, 0.8)
## Sentry and threat colors by type: drone = cyan, netrunner = magenta, enforcer = orange.
const TYPE_COLOR := {"D": Color8(92, 225, 255), "N": Color8(255, 64, 214), "E": Color8(255, 140, 26)}
## The hunter has its own look whatever its type: a cobalt hound silhouette with glowing eyes and a cobalt trail. Only
## its badge shows the type.
const HUNTER_BODY := COBALT
const HUNTER_EYE := Color8(235, 248, 255)
const HUNTER_TRAIL := COBALT
## The collapsed HQ's body color in the fall beat.
const FALL_BODY := Color8(70, 14, 20)
## L12 route verdicts: the heart of a held route (HOLDS / EVADED).
const HOLD_COL := Color8(70, 235, 160)

const ALBEDO_K := 0.25
const ROUGH := 0.45
const METAL := 0.5
const E_ROUTE := 1.4
const E_ROUTE_CORE := 2.6
const E_STREET := 0.7
const E_GRID := 0.35
const E_RIM := 1.5
const E_RING := 2.2
const E_RING_DOWN := 1.1
const E_RING_DIM := 0.35
const E_DECAL := 0.8
const DECAL_A_OK := 0.16
const DECAL_A_DOWN := 0.08
const DECAL_A_TAKEN := 0.24
const E_WIN := 2.0
const E_WIN_DIM := 0.25
const E_WIN_DOWN := 1.2
const E_PIP := 2.2
const E_PIP_DIM := 0.45
const E_KEY := 2.6
const E_KEY_DIM := 0.8
const E_SENTRY := 2.6
const E_GHOST := 2.2
const E_VEH := 3.0
const E_HUNTER := 1.6
const E_EYE := 6.0
const E_CAND_LIT := 4.0
## Impact flashes (shield, strike, rings) are kept low so they read as a shape, not a white blob.
const E_FX := 2.4
const E_HQ_WIN := 2.0
const E_HQ_EDGE := 2.4
const E_BEACON := 2.6
const E_HL := 1.4
const E_HL_GLYPH := 2.2
const E_PICK := 1.8
## L12: the skyline and the starfield motes are dimmed (below the glow threshold) so they sit behind the board.
const E_SKY := 0.35
const E_MOTE := 0.55
const E_WRENCH := 1.8
const E_PATH := 2.4
const E_TRAIL := 2.8
const E_OUT := 2.4
const E_LABEL := 1.0
const E_LETHAL := 2.6
const E_LETHAL_PIP := 3.2
const E_RESP := 2.6
const E_FALL := 2.6
const E_COUNT := 2.4
const E_CRACK := 1.8
const E_VERDICT := 2.4
const DECAL_ALPHA := 0.18
const HALO_ALPHA := 0.35
const HALO_E_K := 0.6

const AMBIENT_E := 0.55
const GLOW_INTENSITY := 0.45
const GLOW_STRENGTH := 0.9
const GLOW_BLOOM := 0.0
const GLOW_THRESHOLD := 1.0
## While an impact effect is alive, glow drops to this fraction of GLOW_INTENSITY.
const GLOW_IMPACT_K := 0.5
const IMPACT_FX := ["strike", "shield", "ring", "pulse"]
const KEY_E := 0.9
const KEY_ROT := Vector3(-52.0, -25.0, 0.0)
const HQ_LIGHT_E := 1.4
const HQ_LIGHT_RANGE := 9.0
const HQ_LIGHT_Y := 3.0
const HEAT_REF := 100.0

## The camera angles; distance and offsets are computed by the fit (see _fit_camera).
const CAM_PITCH_DEG := -48.0
const CAM_YAW_DEG := -20.0
const CAM_FOV := 16.0
const CAM_NEAR := 1.0
const CAM_FAR := 400.0
## The reference viewport and the free board area in it: left of the 420 px panel, between the HUD and the legend.
const FIT_VIEW := Vector2(1280.0, 720.0)
const FIT_FREE := Rect2(0.0, 64.0, 860.0, 606.0)
const FIT_MARGIN := 8.0
## World units above the HQ pips kept inside the fit (tower tops). The skyline is never fitted.
const FIT_HEADROOM := 0.15
## L12: the fit uses the board's real points, not a box. District glyphs (capture plus, outcome glyphs) rise to this
## height over the district grid; the route labels are this tall.
const FIT_GLYPH_TOP := 2.2
const FIT_LABEL_H := 0.7
const FIT_ITERS := 24
const FIT_FAR_PAD := 120.0
## How far flat glyphs (shapes, keys, wrenches) tilt toward the camera (fraction of its pitch).
const GLYPH_TILT := 0.6

const DEFAULT_W := 4
const DEFAULT_H := 3
const CELL_DX := 2.9
const CELL_DZ := 2.6
const SLAB_PAD := Vector2(1.6, 1.5)
const SLAB_T := 0.3
const FLOOR_DROP := 0.2
const FLOOR_SIZE := 300.0
const RIM_W := 0.08
const GRID_STEP := 1.0
const GRID_W := 0.02
const ROAD_Y := 0.015
const ROAD_T := 0.02
const ROUTE_W := 0.56
const ROUTE_CORE_W := 0.07
const ROUTE_EDGE_W := 0.04
const STREET_W := 0.26
const STREET_EXT := 0.9
const STREET_LIFT := 0.006
## Layer heights above the roads: cell decals, crack decals, planned paths, outcome paths, playout trails, highlights.
const DECAL_Y := 0.045
const DECAL_T := 0.006
const CRACK_DECAL_Y := 0.055
const PATH_Y := 0.06
const OUT_PATH_Y := 0.07
const TRAIL_Y := 0.08
const LANE_T := 0.012
const HL_Y := 0.1

## Coordinates on the board: route names at the corp end (right of the corp platform), street numbers at the north edge.
const ROUTE_NAMES := ["NORTH", "MID", "SOUTH"]
const ROUTE_LABEL_FONT := 72
const ROUTE_LABEL_DX := 0.25
const ROUTE_LABEL_Y := 0.25
## World units a route label spans right of its anchor, kept inside the fit so the labels stay in the free area.
const ROUTE_LABEL_W := 2.5
const STREET_LABEL_FONT := 64
const STREET_LABEL_DX := -0.6
const STREET_LABEL_IN := 0.3
const STREET_LABEL_Y := 0.2
## Scramble noise: seeded per label slot, same length, letters and digits become letters, other characters stay.
const SCRAMBLE_SEED := 4049
const SCRAMBLE_STREET_K := 100
const SCRAMBLE_FX := 900
const LETTERS := 26
const CODE_A := 65
const CODE_Z := 90
const CODE_LA := 97
const CODE_LZ := 122
const CODE_0 := 48
const CODE_9 := 57

const BLD_SEED := 811
const SEED_MX := 31
const SEED_MY := 7
const QUADS := [Vector2(-1, -1), Vector2(1, -1), Vector2(-1, 1), Vector2(1, 1)]
const BLD_OFF := 0.62
const BLD_W_MIN := 0.42
const BLD_W_MAX := 0.62
const BLD_H_MIN := 0.35
const BLD_H_MAX := 1.5
## Height caps so the roads through a district stay visible: front quads (toward the camera) and back-left quads.
const BLD_FRONT_H := 0.45
const BLD_SIDE_H := 0.95
const VALUE_MIN := 4
const VALUE_MAX := 12
const FLOOR_H := 0.26
const WIN_H := 0.05
const WIN_FRAC := 0.7
const WIN_EPS := 0.01
const RING_Y := 0.05
const RING_R_IN := 1.0
const RING_R_OUT := 1.12
const RING_FLAT := 0.25
const DECAL_R := 0.95
const HEX := 6
const TRI_SEGS := 3
const CIRCLE_SEGS := 24
const TORUS_TUBE := 6
const SPHERE_SEGS := 12
const SPHERE_RINGS := 6
const SHAPE_DEPTH := 0.04
const SQUARE_K := 1.5
const PIP_POS := Vector3(-1.08, 0.0, -1.08)
const PIP_SIZE := Vector3(0.26, 0.07, 0.26)
const PIP_STEP := 0.12
const KEY_POS := Vector3(1.08, 0.9, -1.08)
const KEY_BOW := Vector2(0.04, 0.09)
const KEY_PARTS := [[Vector3(0.18, 0.0, 0.0), Vector3(0.26, 0.05, 0.04)], [Vector3(0.27, -0.05, 0.0), Vector3(0.04, 0.08, 0.04)], [Vector3(0.2, -0.05, 0.0), Vector3(0.04, 0.06, 0.04)]]
const WRENCH_POS := Vector3(0.0, 1.9, 0.0)
const WRENCH_DISC := Vector2(0.3, 0.02)
const WRENCH_PARTS := [[Vector3(0.0, 0.0, 0.03), Vector3(0.07, 0.42, 0.05), -0.785], [Vector3(0.12, 0.2, 0.03), Vector3(0.06, 0.14, 0.05), -0.785], [Vector3(0.2, 0.12, 0.03), Vector3(0.06, 0.14, 0.05), -0.785]]
const FLICKER_HZ := 9.0
const FLICKER_LOW := 0.15
const FLICKER_ON := 0.45
const HASH_A := 12.9898
const HASH_B := 78.233
const HASH_C := 37.719
const HASH_D := 43758.5453

## L12 countdown mark on a DOWN district: a cobalt "1" in a ring, right of the wrench in the wrench's facing plane.
## The digit is built from boxes (stem, top flag, base), so the scramble never touches it.
const COUNT_POS := Vector2(0.58, 0.04)
const COUNT_BACK_R := 0.23
const COUNT_RING := Vector2(0.17, 0.22)
const COUNT_STEM := Vector3(0.055, 0.22, 0.04)
const COUNT_STEM_X := 0.01
const COUNT_FLAG := Vector3(0.045, 0.1, 0.04)
const COUNT_FLAG_POS := Vector2(-0.025, 0.08)
const COUNT_FLAG_ROT := -0.86
const COUNT_BASE := Vector3(0.13, 0.04, 0.04)
const COUNT_BASE_Y := -0.1
const COUNT_Z := 0.02
## L12 crack decal on a district hit this raid that is OK again: the crack polyline laid flat across the cell.
const CRACK_DECAL_S := 2.2
const CRACK_DECAL_YAW := 0.7

const SENTRY_POLE := Vector2(0.05, 0.95)
const SENTRY_BASE := Vector2(0.18, 0.08)
const SENTRY_GLYPH_Y := 1.22
const SENTRY_GLYPH_S := 0.27
const SENTRY_DECAL := Vector2(0.48, 0.58)
const GHOST_R := 1.34
const GHOST_HOME_R := 2.0
const GHOST_DASHES := 16
const GHOST_DASH := Vector3(0.3, 0.04, 0.07)
const GHOST_SPIN := 0.5

const HQ_PLAT := Vector2(2.2, 0.22)
const HQ_TIERS := 4
const HQ_BASE := 1.5
const HQ_STEP := 0.18
const HQ_TIER_H := 0.85
const HQ_WIN_ROWS := 3
const HQ_EDGE_W := 0.05
const HQ_BEACON_R := 0.22
const HOME_HP_MAX := 3
const HOME_PIP := Vector3(0.34, 0.24, 0.06)
const HOME_PIP_GAP := 0.44
const HOME_PIP_Y := 0.7

## The lethal mark on our HQ tower: a red skull near the tower top, pushed toward the camera, pulsing with the last pip.
const LETHAL_SKULL_Y := 3.25
const LETHAL_FWD := 0.7
const LETHAL_SKULL_S := 0.7
const LETHAL_HZ := 1.4
const LETHAL_LOW := 0.3
const LETHAL_GROW := 0.08

## The decided fall beat: the tower squashes to rubble, spreads and tilts, the pips drop with it, and a red skull
## stands over the rubble at the end.
const FALL_SCALE_Y := 0.14
const FALL_SPREAD := 0.18
const FALL_TILT := 0.22
const FALL_FLASH := 1.5
const FALL_PIP_Y := 1.2
const FALL_SKULL_Y := 1.7
const FALL_SKULL_S := 1.1
const FALL_SHAKE_U := 0.8
const FALL_RING_K := 1.4
const FALL_PULSE_K := 2.2

const VEH_Y := 0.38
const VEH_GLYPH_Y := 0.95
const VEH_GLYPH_S := 0.2
const DRONE_N := 5
const DRONE_S := 0.12
const DRONE_SPREAD := 0.28
const WORM_N := 6
const WORM_R := 0.13
const WORM_STEP := 0.17
const WORM_TAPER := 0.12
const CONVOY_N := 3
const CONVOY_BOX := Vector3(0.36, 0.26, 0.28)
const CONVOY_STEP := 0.42
const HALO := Vector2(0.3, 0.42)
const BOB_HZ := 2.5
const BOB_AMP := 0.06
const WIGGLE_AMP := 0.07
const SPAWN_DROP := 4.0
const TURN_FAST := 4.0
const EPS := 0.0001
## A new vehicle enters this far back along its line (fraction of a cell): routes from the corp platform, streets from the street end.
const ENTRY_ROUTE_K := 0.62
const ENTRY_STREET_K := 0.35
## Headings (rotation.y with +x as forward): toward HOME (-x), down a street (+z, y = 0 -> 2).
const HEADING_HOME := PI
const HEADING_DOWN := -PI * 0.5
## The hound, forward +x, standing on the floor, built inside a holder scaled by HOUND_S.
## Body parts: [position, size] or [position, size, rotation.z] (torso, chest, haunch, neck, head, snout, ears, tail).
const HOUND_S := 1.2
const HOUND_PARTS := [[Vector3(-0.02, 0.44, 0.0), Vector3(0.56, 0.19, 0.22)], [Vector3(0.18, 0.47, 0.0), Vector3(0.2, 0.26, 0.24)], [Vector3(-0.22, 0.45, 0.0), Vector3(0.16, 0.22, 0.22)], [Vector3(0.3, 0.6, 0.0), Vector3(0.12, 0.16, 0.14), -0.5], [Vector3(0.38, 0.66, 0.0), Vector3(0.2, 0.16, 0.17)], [Vector3(0.52, 0.62, 0.0), Vector3(0.14, 0.08, 0.1)], [Vector3(0.33, 0.78, 0.05), Vector3(0.05, 0.13, 0.04), 0.25], [Vector3(0.33, 0.78, -0.05), Vector3(0.05, 0.13, 0.04), 0.25], [Vector3(-0.38, 0.55, 0.0), Vector3(0.2, 0.045, 0.045), -0.6]]
## Legs: [position, size, gait phase sign] (diagonal pairs swing together).
const HOUND_LEGS := [[Vector3(0.18, 0.17, 0.08), Vector3(0.06, 0.32, 0.06), 1.0], [Vector3(0.18, 0.17, -0.08), Vector3(0.06, 0.32, 0.06), -1.0], [Vector3(-0.22, 0.17, 0.08), Vector3(0.06, 0.32, 0.06), -1.0], [Vector3(-0.22, 0.17, -0.08), Vector3(0.06, 0.32, 0.06), 1.0]]
## The glowing eyes on the front of the head, above the snout.
const HOUND_EYES := [[Vector3(0.485, 0.69, 0.048), Vector3(0.035, 0.06, 0.06)], [Vector3(0.485, 0.69, -0.048), Vector3(0.035, 0.06, 0.06)]]
const GAIT_HZ := 3.2
const GAIT_AMP := 0.05
const EYE_HZ := 0.8
const EYE_LOW := 0.55
## The hunter's type badge: a small type shape on a dark disc above the hound.
const HUNTER_BADGE_Y := 1.15
const HUNTER_BADGE_S := 0.13
const BADGE_BACK_K := 1.6
const CAND_DX := 0.55
const CAND_ALPHA := 0.32
const CAND_SHRINK := 0.2

## Planned paths: dashed lanes (sealed candidates, faded extras) or solid lanes (known beams), a chevron at the exit,
## the type glyph at the entry.
const LANE_GAP := 0.2
const PATH_W := 0.11
const DASH_L := 0.34
const DASH_G := 0.2
const PATH_ALPHA := 0.9
const PATH_DIM_K := 0.45
## L12: candidate routes other than the selected one are drawn at this alpha, with emission scaled by CAND_OFF_E and
## no arrowhead. The selected candidate and known beams are drawn at full alpha; the selected one pulses.
const CAND_OFF_ALPHA := 0.15
const CAND_OFF_E := 0.5
const PATH_FULL_ALPHA := 1.0
const PATH_PULSE := 0.4
const PATH_PULSE_HZ := 1.2
const PATH_GLYPH_Y := 0.55
const PATH_GLYPH_S := 0.16
const ARROW_L := 0.42
const ARROW_W := 0.09
const ARROW_ANG := 0.62
## Playout trails: solid lanes that fade to a resting glow, plus persistent hit, block, home, turn and jam marks.
const TRAIL_W := 0.14
const TRAIL_DOT_R := 0.12
const TRAIL_MIN := 0.05
const TRAIL_ALPHA := 0.95
const TRAIL_REST := 0.6
const TRAIL_REST_E := 0.55
const TRAIL_FADE_T := 1.6
const HIT_MARK_R := Vector2(1.16, 1.25)
const HIT_GLYPH_POS := Vector3(0.95, 0.35, 0.95)
const HIT_GLYPH_STEP := Vector3(-0.34, 0.0, 0.0)
const HIT_GLYPH_S := 0.15
const BLOCK_DOME_R := 0.62
const BLOCK_DOME_FLAT := 0.7
const BLOCK_BAR := Vector3(0.1, 0.14, 0.9)
const BLOCK_BAR_BACK := 0.45
const BLOCK_ALPHA := 0.4
const TURN_MARK_R := Vector2(0.72, 0.82)
const HOME_MARK_R := Vector2(1.5, 1.62)
const JAM_MARK := Vector3(0.6, 0.08, 0.05)
const JAM_MARK_Y := 0.5

## Forecast outcome glyphs: they float above the district on a dark backing disc so they read against the glow.
const OUT_GLYPH_Y := 1.75
const OUT_BACK_R := 0.42
const OUT_BACK_Z := 0.03
const CRACK_W := 0.07
const CRACK_PTS := [Vector2(-0.04, 0.34), Vector2(0.09, 0.14), Vector2(-0.08, -0.02), Vector2(0.08, -0.18), Vector2(-0.02, -0.34)]
const CRACK_BRANCH := [Vector2(-0.08, -0.02), Vector2(-0.26, -0.1)]
const CRACK_BRANCH_2 := [Vector2(0.09, 0.14), Vector2(0.25, 0.22)]
const OUT_RING_Y := 0.07
const SHIELD_TOP := Vector3(0.44, 0.2, 0.04)
const SHIELD_TOP_Y := 0.12
const SHIELD_TIP_R := 0.254
const SHIELD_TIP_Y := -0.107
const SHIELD_RING_R := Vector2(0.9, 1.0)
const SKULL_Y := 1.9
const SKULL_FWD := 1.3
const SKULL_S := 1.3
const SKULL_BACK_R := 0.52
const SKULL_HEAD_R := 0.32
const SKULL_HEAD_Y := 0.08
const SKULL_HEAD_FLAT := 0.5
const SKULL_EYE := Vector3(0.12, 0.12, 0.04)
const SKULL_EYE_POS := Vector3(0.12, 0.08, 0.17)
const SKULL_NOSE := Vector3(0.05, 0.07, 0.04)
const SKULL_NOSE_POS := Vector3(0.0, -0.06, 0.17)
const SKULL_JAW := Vector3(0.34, 0.14, 0.14)
const SKULL_JAW_Y := -0.25
const SKULL_TOOTH := Vector3(0.03, 0.15, 0.04)
const SKULL_TOOTH_X := [-0.07, 0.07]
const OUT_HOUND_S := 1.15
const OUT_HOUND_GLYPH_Y := 1.35
const OUT_HOUND_GLYPH_K := 1.4

## L12 route verdicts: a glyph just past where each route meets HOME (right of our HQ platform), raised and pushed
## toward the camera, with a ring on the road below it. Heart = HOLDS / EVADED, broken heart = BATTERED / DAMAGED,
## skull = BREACHED. The heart is a diamond with two lobes; the break is a dark zigzag in front of it.
const VERDICT_DX := 0.45
const VERDICT_Y := 0.95
const VERDICT_FWD := 0.35
const VERDICT_S := 1.5
const VERDICT_SKULL_S := 0.8
const VERDICT_RING_R := Vector2(0.32, 0.4)
const HEART_SQ := 0.26
const HEART_SQ_Y := -0.06
const HEART_LOBE := Vector2(0.092, 0.032)
const HEART_LOBE_R := 0.13
const HEART_BACK_R := 0.3
const HEART_BREAK_W := 0.045
const HEART_BREAK_Z := 0.03
const HEART_BREAK := [Vector2(0.0, 0.17), Vector2(0.05, 0.05), Vector2(-0.04, -0.05), Vector2(0.03, -0.15), Vector2(0.0, -0.26)]

## Response preview: an arc arrow from the source to the target (ends cut back so it lands on the rings), a cone head,
## a spinning dashed ring at a sentry source, the reserve tray at our HQ for DEPLOY, a ghost sentry at the target, and
## for JAM a red cross over the hound (which dims).
const RESP_END_Y := 0.3
const RESP_ARC_H := 0.9
const RESP_ARC_K := 0.12
const RESP_ARC_SEGS := 16
const RESP_ARC_W := 0.09
const RESP_HEAD_L := 0.4
const RESP_HEAD_R := 0.17
const RESP_HEAD_SEGS := 8
const RESP_HEAD_CUT := 0.6
const RESP_SRC_CUT := 0.55
const RESP_DST_CUT := 0.6
const RESP_TRAY_CUT := 0.35
const RESP_SRC_R := 0.8
const RESP_TRAY_DX := 1.45
const RESP_TRAY := Vector3(0.56, 0.06, 0.4)
const RESP_TRAY_R := 0.36
const RESP_BADGE_Y := 0.55
const RESP_BADGE_S := 0.16
const RESP_GHOST_A := 0.5
const RESP_JAM_R := 0.7
const RESP_JAM_Y := 0.6
const RESP_JAM_FWD := 0.5
const RESP_JAM_BAR := Vector3(1.0, 0.13, 0.05)
const RESP_JAM_DIM := 0.35
const RESP_PULSE := 0.35

## Highlights by meaning. Capture: an amber plus over the district and a pulsing amber ring. Repair: a red outline
## around the district's wrench and a red hex ring. Picked: a steady white ring with a check on its camera-side edge.
const HL_GLYPH_Y := 1.75
const HL_BACK_R := 0.42
const HL_RING_W := 0.1
const HL_HOME_R := 2.0
const PLUS_L := 0.56
const PLUS_W := 0.16
const REPAIR_RING_W := 0.07
const REPAIR_PAD := 0.035
const REPAIR_Z := 0.015
const PICK_R := 1.2
const PICK_HOME_PAD := 0.2
const PICK_RING_W := 0.07
const PICK_CHECK_Y := 0.4
const PICK_BACK_R := 0.26
const CHECK_W := 0.07
const CHECK_PTS := [Vector2(-0.15, 0.01), Vector2(-0.04, -0.1), Vector2(0.16, 0.13)]

const SHIELD_R := Vector2(0.25, 0.7)
const STRIKE := Vector3(0.1, 3.2, 0.1)
const FLASH_R := Vector2(0.5, 1.2)
const PULSE_R := Vector2(0.5, 1.3)
const FX_RING_T := 0.1
const SLASH := Vector3(0.9, 0.09, 0.06)
const SLASH_ROT := 0.6
const SLASH_Y := 0.55
const LABEL_PX := 0.01
const LABEL_FONT := 64
const LABEL_BIG := 120
const LABEL_OUTLINE := 12
const LABEL_RISE := 0.8
const LABEL_Y := 2.4
const HOME_LABEL_Y := 4.6
const SHAKE_AMP := 0.12
const SHAKE_HZ := 28.0
const SCREEN_Y := 0.9
const HL_ALPHA := 0.28
const HL_R := 1.25
const HL_HZ := 1.6
const HL_PULSE := 0.4

const SKY_SEED := 77
const SKY_N := 46
const SKY_X := Vector2(-28.0, 28.0)
const SKY_Z := Vector2(-30.0, -9.0)
const SKY_W := Vector2(1.5, 4.5)
const SKY_H := Vector2(3.0, 10.0)
const SKY_EDGE := 0.06
const MOTE_SEED := 2026
const MOTE_N := 90
const MOTE_BOX := Vector3(14.0, 3.5, 9.0)
const MOTE_S := 0.07

## Seconds at 1x, per cue kind and per effect.
const T_STEP := 0.32
const T_BLOCK := 0.55
const T_HIT := 0.5
const T_HOME := 0.7
const T_TURN := 0.9
const T_JAM := 0.7
const T_REVEAL := 1.4
const T_EVADED := 1.2
const T_DECAY := 0.8
const T_FALL := 1.8
const FX_SHIELD_T := 0.6
const FX_STRIKE_T := 0.55
const FX_RING_TIME := 0.6
const FX_FADE_T := 0.5
const FX_LABEL_T := 1.2
const SHAKE_T := 0.45
## An effect's progress shown frozen in instant mode (its settled look).
const SETTLE_U := 0.35
const SPEED_MIN := 0.1

const NO_CELL := Vector2i(-99, -99)
const NO_LINE := -999
const MOVE_KINDS := ["beam_step", "hit", "block", "home"]

# ======================= state =======================
var cam: Camera3D
var _env: Environment
var _yaw: float = deg_to_rad(CAM_YAW_DEG)
var _tilt: float = deg_to_rad(CAM_PITCH_DEG) * GLYPH_TILT
var _mats: Dictionary = {}
var _unit_box: BoxMesh
var _board: Node3D
var _path_root: Node3D
var _outcome_root: Node3D
var _verdict_root: Node3D
var _resp_root: Node3D
var _trail_root: Node3D
var _fx_root: Node3D
var _hl_root: Node3D
var _w: int = DEFAULT_W
var _h: int = DEFAULT_H
var _values: Dictionary = {}
var _exploits: Array = []
var _route_names: Array = ROUTE_NAMES.duplicate()
var _street_names: Array = []
var _route_labels: Array = []
var _street_labels: Array = []
var _street_nodes: Array = []
var _path_streets: Dictionary = {}
var _out_streets: Dictionary = {}
var _paths_on: bool = false
var _path_pulse: Array = []
var _scramble: bool = false
var _status: Dictionary = {}
var _sentries: Dictionary = {}
var _cracked: Dictionary = {}
var _ghost_cell: Vector2i = NO_CELL
var _ghost_home: bool = false
var _home_hp: int = HOME_HP_MAX
var _heat: int = 0
var _cell_root: Dictionary = {}
var _cell_key: Dictionary = {}
var _win_mats: Dictionary = {}
var _spin: Array = []
var _home_root: Node3D
var _home_tower: Node3D
var _home_light: OmniLight3D
var _home_pip_holder: Node3D
var _home_pips: Array = []
var _home_ghost: Node3D
var _beacon_mat: StandardMaterial3D
var _lethal: bool = false
var _lethal_root: Node3D
var _lethal_pip: StandardMaterial3D
var _lethal_mats: Array = []
var _fallen: bool = false
var _fall_mats: Array = []
var _fall_skull: Node3D = null
var _out_hound: Node3D = null
var _out_hound_mats: Array = []
var _eyes: Array = []
var _resp_mats: Array = []
var _resp_last: Dictionary = {}
var _resp_dimmed: bool = false
var _vehicles: Dictionary = {}
var _cands: Array = []
var _cand_real: int = -1
var _fx: Array = []
var _shakes: Dictionary = {}
var _hl: Array = []
var _path_use: Dictionary = {}
var _trail_fade: Array = []
var _trail_arrow: Dictionary = {}
var _lane: Dictionary = {}
var _road_use: Dictionary = {}
var _hit_count: Dictionary = {}
var _queue: Array = []
var _qi: int = -1
var _cur_cue: Dictionary = {}
var _cur_line: int = NO_LINE
var _cue_t: float = 0.0
var _cue_dur: float = 0.0
var _playing: bool = false
var _speed: float = 1.0
var _instant: bool = false
var _time: float = 0.0


func _init() -> void:
	_unit_box = BoxMesh.new()
	_unit_box.size = Vector3.ONE
	_build_env()
	_board = Node3D.new()
	add_child(_board)
	_path_root = Node3D.new()
	add_child(_path_root)
	_outcome_root = Node3D.new()
	add_child(_outcome_root)
	_verdict_root = Node3D.new()
	add_child(_verdict_root)
	_resp_root = Node3D.new()
	add_child(_resp_root)
	_trail_root = Node3D.new()
	add_child(_trail_root)
	_fx_root = Node3D.new()
	add_child(_fx_root)
	_hl_root = Node3D.new()
	add_child(_hl_root)
	_fit_camera()


func _ready() -> void:
	cam.make_current()
	_fit_camera()
	var vp := get_viewport()
	if vp != null and not vp.size_changed.is_connected(_fit_camera):
		vp.size_changed.connect(_fit_camera)


# ======================= public API =======================
## Build the board for a leg: {w, h, values: {Vector2i: int}, exploits: Array[Vector2i]}. The optional keys
## route_names (3 Strings) and street_names (w Strings) replace the board's coordinate labels. set_scramble() still
## applies on top of them. A fallen HQ (show_fall) is rebuilt standing. Route verdicts and crack decals are cleared.
func setup(leg: Dictionary) -> void:
	_w = int(leg.get("w", DEFAULT_W))
	_h = int(leg.get("h", DEFAULT_H))
	_values = (leg.get("values", {}) as Dictionary).duplicate()
	_exploits = (leg.get("exploits", []) as Array).duplicate()
	_route_names = (leg.get("route_names", ROUTE_NAMES) as Array).duplicate()
	_street_names.clear()
	var sn: Array = leg.get("street_names", [])
	for x in range(_w):
		_street_names.append(str(sn[x]) if x < sn.size() else str(x))
	reset_playout()
	clear_highlight()
	clear_outcome()
	clear_response_preview()
	hide_route_verdicts()
	_cracked.clear()
	_board.queue_free()
	_board = Node3D.new()
	add_child(_board)
	move_child(_board, 0)
	_cell_root.clear()
	_cell_key.clear()
	_win_mats.clear()
	_status.clear()
	_spin.clear()
	_street_nodes.clear()
	_home_ghost = null
	_lethal_root = null
	_fallen = false
	_fall_mats.clear()
	_fall_skull = null
	_build_floor()
	_build_roads()
	_build_coord_labels()
	_build_skyline()
	_build_motes()
	_home_root = _build_hq(-1, AMBER, HQ_BODY_HOME)
	_home_tower = _home_root.get_meta("tower") as Node3D
	_home_light = _home_root.get_meta("light") as OmniLight3D
	var corp := _build_hq(_w, COBALT, HQ_BODY_CORP)
	_beacon_mat = _mat_live(COBALT_HOT, E_BEACON)
	_sphere(corp, Vector3(0.0, HQ_PLAT.y + HQ_TIERS * HQ_TIER_H + HQ_BEACON_R, 0.0), HQ_BEACON_R, _beacon_mat)
	_build_home_pips()
	_refresh_lethal()
	for c: Vector2i in _cells():
		var root := Node3D.new()
		root.position = _grid_world(c)
		_board.add_child(root)
		_cell_root[c] = root
		_status[c] = "NEUTRAL"
		_refresh_cell(c)
	_apply_street_vis()
	_fit_camera()


## Show a state {owned: {cell: OK/DOWN/TAKEN}, home_hp, heat} and a placement {sentries: {cell: D/N/E}, ghost: cell|"HOME"|null}.
## Every DOWN district shows the "TAKEN next raid" countdown mark; an OK district hit this raid shows a crack decal.
## Trails of the last playout stay; reset_playout() clears them.
func show_state(st: Dictionary, place: Dictionary) -> void:
	var owned: Dictionary = st.get("owned", {})
	for c: Vector2i in _cells():
		_status[c] = str(owned.get(c, "NEUTRAL"))
	_home_hp = int(st.get("home_hp", HOME_HP_MAX))
	_heat = int(st.get("heat", 0))
	_sentries = (place.get("sentries", {}) as Dictionary).duplicate()
	var g: Variant = place.get("ghost", null)
	_ghost_home = g is String and String(g) == "HOME"
	_ghost_cell = g if g is Vector2i else NO_CELL
	for c: Vector2i in _cells():
		_refresh_cell(c)
	_refresh_pips()
	_refresh_home_ghost()
	if _beacon_mat != null:
		_beacon_mat.emission_energy_multiplier = E_BEACON * (1.0 + float(_heat) / HEAT_REF)


## The sealed candidates [{route, type}]: real -1 = ghosted convoys at the corp end (a new raid: vehicles, effects,
## trails and crack decals are reset, planned paths stay); real >= 0 = the settled reveal (two gone, the real one lit).
func show_candidates(cands: Array, real: int = -1) -> void:
	if real < 0 or _cands.is_empty():
		if real < 0:
			_reset_motion()
			clear_cracks()
		_clear_candidates()
		for cd: Dictionary in cands:
			var route := int(cd.get("route", 0))
			var v := _make_vehicle(str(cd.get("type", "D")), false, CAND_ALPHA)
			var n: Node3D = v["node"]
			n.position = _grid_world(Vector2i(_w - 1, route)) + Vector3(CAND_DX * CELL_DX, VEH_Y, 0.0)
			n.rotation.y = HEADING_HOME
			v["route"] = route
			_cands.append(v)
	_cand_real = real
	_apply_reveal(1.0 if real >= 0 else 0.0)
	_face_all()


## Draw planned lines along their roads, each with its type glyph at the entry. A line is {kind, index, cells, type,
## home}, with the optional keys:
## - dim: bool, drawn faded and dashed with no arrowhead (for example an extra that will not fire);
## - cand: int, the sealed candidate index (or sealed: true, which uses the line's index).
## Known beams (not candidates, not dim) are solid lanes at full strength with a chevron at the exit. Candidates are
## dashed; with selected >= 0, the selected candidate is drawn at full strength with a pulse and a chevron, and the
## other candidates at 15% alpha with no arrowhead. Paths always run their whole line: there are no block ticks on
## planned paths (blocks are shown only by show_outcome for the selected route). While paths are shown, cross streets
## that no shown line uses are hidden. Replaces any paths shown before.
func show_paths(lines: Array, selected: int = -1) -> void:
	clear_paths()
	_paths_on = true
	var later: Array = []
	for lv: Variant in lines:
		if not (lv is Dictionary):
			continue
		var ln: Dictionary = lv
		if str(ln.get("kind", "")) == "STREET":
			_path_streets[int(ln.get("index", -1))] = true
		if _path_off(ln, selected):
			later.append(ln)
		else:
			_draw_path(ln, selected)
	for ln: Dictionary in later:
		_draw_path(ln, selected)
	_apply_street_vis()


## Remove every planned path (every cross street shows again).
func clear_paths() -> void:
	for ch in _path_root.get_children():
		ch.queue_free()
	_path_use.clear()
	_path_pulse.clear()
	_path_streets.clear()
	_paths_on = false
	_apply_street_vis()


## Show one sealed route's forecast outcome on the board:
## o = {hits: Array[Vector2i], blocks: Array[Vector2i], block_types: Array[String], home: bool, hunter: line or null}.
## - Hit cells get a red crack glyph.
## - Blocks get a shield glyph in the sentry's type color.
## - A HOME hit puts a red skull over our HQ.
## - The hunter's street gets a dashed cobalt line, with the cobalt hound (glowing eyes, type badge) standing at its
##   start, facing down the street. Its street counts as used (it stays visible while paths are shown).
## Replaces any outcome shown before; an active response preview is redrawn on top. play() clears it.
func show_outcome(o: Dictionary) -> void:
	clear_outcome()
	var hits: Array = o.get("hits", [])
	for hv: Variant in hits:
		if hv is Vector2i:
			_out_hit(hv as Vector2i)
	var blocks: Array = o.get("blocks", [])
	var types: Array = o.get("block_types", [])
	for i in range(blocks.size()):
		var bv: Variant = blocks[i]
		if bv is Vector2i:
			var bc: Vector2i = bv
			var t := str(types[i]) if i < types.size() else str(_sentries.get(bc, "D"))
			_out_block(bc, t)
	if bool(o.get("home", false)):
		_out_home()
	var hl: Variant = o.get("hunter", null)
	if hl is Dictionary:
		_out_hunter(hl as Dictionary)
	_apply_street_vis()
	if not _resp_last.is_empty():
		show_response_preview(_resp_last.duplicate())


## Remove the outcome overlay.
func clear_outcome() -> void:
	_out_hound = null
	_out_hound_mats = []
	_out_streets.clear()
	if _outcome_root == null:
		return
	for ch in _outcome_root.get_children():
		ch.queue_free()
	_apply_street_vis()


## L12: stamp each sealed route's forecast tier where that route meets HOME. v = [{route: int, tier: String}], one
## entry per candidate route. HOLDS / EVADED: a green heart; BATTERED / DAMAGED: an amber broken heart; BREACHED: a red
## skull. Each glyph floats just right of our HQ platform on its route, with a ring on the road. Replaces any verdicts
## shown before; play() hides them (launch).
func show_route_verdicts(v: Array) -> void:
	hide_route_verdicts()
	for ev: Variant in v:
		if not (ev is Dictionary):
			continue
		var e: Dictionary = ev
		var route := int(e.get("route", -1))
		if route < 0 or route >= _h:
			continue
		_verdict(route, str(e.get("tier", "")))


## L12: remove the route verdicts.
func hide_route_verdicts() -> void:
	if _verdict_root == null:
		return
	for ch in _verdict_root.get_children():
		ch.queue_free()


## L12: the districts marked as hit this raid (Vector2i). Those still or again OK show a crack decal until the next
## raid (show_candidates with real -1) or clear_cracks(). The playout adds every hit cell on its own.
func set_cracked(cells: Array) -> void:
	_cracked.clear()
	for c: Variant in cells:
		if c is Vector2i:
			_cracked[c] = true
	_refresh_all_cells()


## L12: drop every crack decal.
func clear_cracks() -> void:
	if _cracked.is_empty():
		return
	_cracked.clear()
	_refresh_all_cells()


## Draw a response row's effect on the board: p = {kind: "REDEPLOY"|"DEPLOY"|"JAM"|"HOLD", from: Vector2i or null,
## to: Vector2i or null, type: String}, with the optional key street: int (the hunter's street for JAM when no outcome
## hound is shown).
## - REDEPLOY / DEPLOY: an arc arrow in the sentry type's color from the source to the target cell, with a ghost
##   sentry at the target. The source is a spinning dashed ring on the sentry's cell, or (from = null) the reserve tray
##   just right of our HQ on the target's route.
## - JAM: a red cross over the hound (the outcome hound, else the head of p.street); the hound and its path dim.
## - HOLD: nothing.
## Replaces any preview shown before. play() clears it.
func show_response_preview(p: Dictionary) -> void:
	clear_response_preview()
	_resp_last = p.duplicate()
	var kind := str(p.get("kind", "HOLD"))
	var type := str(p.get("type", "D"))
	match kind:
		"REDEPLOY", "DEPLOY":
			var tv: Variant = p.get("to", null)
			if not (tv is Vector2i):
				return
			var to: Vector2i = tv
			var m := _mat_live(_type_col(type), E_RESP)
			_resp_mats.append(m)
			var fv: Variant = p.get("from", null)
			var a := Vector3.ZERO
			var cut := RESP_SRC_CUT
			if fv is Vector2i:
				a = _grid_world(fv as Vector2i)
				_resp_source(a, m)
			else:
				a = _tray_pos(to)
				cut = RESP_TRAY_CUT
				_resp_tray(a, type, m)
			_resp_arrow(a, _grid_world(to), cut, RESP_DST_CUT, m)
			_resp_target(to, type, m)
		"JAM":
			_resp_jam(p)


## Remove the response preview (and undim the hound).
func clear_response_preview() -> void:
	if _resp_root != null:
		for ch in _resp_root.get_children():
			ch.queue_free()
	_resp_mats.clear()
	_resp_last = {}
	if _resp_dimmed:
		_tint(_out_hound_mats, 1.0, 1.0)
	_resp_dimmed = false


## Play cues in order (beam_step, block, hit, home, hunter_turn, jam, reveal, evaded, decay, fall) and emit
## cues_finished at the end. Planned paths, the outcome overlay, the route verdicts and the response preview are
## cleared; every beam leaves a trail with its hits and stops until reset_playout(). Hit cells get the crack mark.
func play(cues: Array, speed: float = 1.0) -> Signal:
	clear_paths()
	clear_outcome()
	clear_response_preview()
	hide_route_verdicts()
	_queue = cues.duplicate()
	_qi = -1
	_speed = maxf(speed, SPEED_MIN)
	_playing = true
	if _instant:
		_clear_fx()
		_finish_instant()
	else:
		_next_cue()
	return cues_finished


## The decay beat at the start of raid 2 and raid 3. Each cell (Vector2i) left DOWN flips to cobalt TAKEN with a short
## pulse and loses its sentry glyph, one after the other. It plays at the current speed and returns cues_finished.
func decay(cells: Array) -> Signal:
	var cues: Array = []
	for c: Variant in cells:
		if c is Vector2i:
			cues.append({"kind": "decay", "cell": c})
	return play(cues, _speed)


## The decided fall beat: our HQ tower turns red, shakes and collapses to rubble, every HOME pip goes red, and a red
## skull stands over the rubble. It plays at the current speed (instant settles at once) and returns cues_finished.
## The HQ stays fallen until the next setup().
func show_fall() -> Signal:
	return play([{"kind": "fall"}], _speed)


## Instant on: every cue settles in one frame, effects show frozen at their settled look and trails at rest. Turning it
## on mid-playout finishes the playout at once.
func set_instant(on: bool) -> void:
	_instant = on
	if on:
		_snap_trails()
		if _playing:
			_settle_cue(_cur_cue)
			_finish_instant()


## Change the playout speed (1, 2, 4) while it runs.
func set_speed(speed: float) -> void:
	_speed = maxf(speed, SPEED_MIN)


## Scramble on: the board labels (route names, street numbers, the EVADED stamp) show seeded noise of the same length.
## Off: the real names come back.
func set_scramble(on: bool) -> void:
	_scramble = on
	_apply_label_text()


## Lethal on (HOME 1/3): the last remaining HOME pip pulses red and a red skull pulses on our HQ tower. Off removes both.
func set_lethal(on: bool) -> void:
	if on == _lethal and (not on or is_instance_valid(_lethal_root)):
		return
	_lethal = on
	_refresh_lethal()


## Viewport pixels of a cell (x = -1 is HOME, x = w the corp HQ), for the 2D UI.
func cell_screen_pos(cell: Vector2i) -> Vector2:
	if cam == null or not cam.is_inside_tree():
		return Vector2.ZERO
	return cam.unproject_position(_grid_world(cell) + Vector3(0.0, SCREEN_Y, 0.0))


## Glow the given cells (Vector2i, or the String "HOME") in a pulsing color.
func highlight(cells: Array, color: Color) -> void:
	clear_highlight()
	for c: Variant in cells:
		var pos := _home_world() if c is String else _grid_world(c as Vector2i)
		_hl_disc(pos, color)


## Mark the given cells (Vector2i, or the String "HOME") by meaning:
## - "capture": an amber plus over the district and a pulsing amber ring;
## - "repair": a red outline around the district's wrench and a pulsing red hex ring;
## - "picked": a steady white ring with a check mark (a picked or committed choice).
## Any other kind falls back to a gray glow. add = false clears the highlights shown before; add = true keeps them, so
## kinds can be combined.
func highlight_kind(cells: Array, kind: String, add: bool = false) -> void:
	if not add:
		clear_highlight()
	for c: Variant in cells:
		var home := c is String
		var pos := _home_world() if home else _grid_world(c as Vector2i)
		match kind:
			"capture":
				_hl_capture(pos, home)
			"repair":
				_hl_repair(pos, home)
			"picked":
				_hl_picked(pos, home)
			_:
				_hl_disc(pos, GREY)


## Remove every highlight.
func clear_highlight() -> void:
	for ch in _hl_root.get_children():
		ch.queue_free()
	_hl.clear()


## Drop every vehicle, effect, shake, candidate, trail, planned path, route verdict and response preview (a fresh raid).
## Crack decals stay until the next raid's show_candidates(-1).
func reset_playout() -> void:
	_reset_motion()
	clear_paths()
	clear_response_preview()
	hide_route_verdicts()


# ======================= camera fit =======================
func _view_size() -> Vector2:
	if is_inside_tree():
		var s := get_viewport().get_visible_rect().size
		if s.x > 0.0 and s.y > 0.0:
			return s
	return FIT_VIEW


func _slab_half() -> Vector2:
	return Vector2((_w + 1) * 0.5 * CELL_DX + SLAB_PAD.x, (_h - 1) * 0.5 * CELL_DZ + SLAB_PAD.y)


## L12: the world points the camera keeps in frame: the slab's ground corners, the route labels at the corp end, the
## district glyph tops over the grid's corner cells, and the two HQ tower tops (with the HOME pips). No bounding box,
## so no empty sky above the back of the slab is fitted; the skyline is never fitted.
func _fit_points() -> Array[Vector3]:
	var pts: Array[Vector3] = []
	var half := _slab_half()
	for sx: float in [-1.0, 1.0]:
		for sz: float in [-1.0, 1.0]:
			pts.append(Vector3(half.x * sx, 0.0, half.y * sz))
	var z0 := _grid_world(Vector2i(0, 0)).z
	var z1 := _grid_world(Vector2i(0, _h - 1)).z
	var lx := _grid_world(Vector2i(_w, 0)).x + HQ_PLAT.x * 0.5 + ROUTE_LABEL_DX + ROUTE_LABEL_W
	for z: float in [z0, z1]:
		for y: float in [0.0, FIT_LABEL_H]:
			pts.append(Vector3(lx, y, z))
	var gx0 := _grid_world(Vector2i(0, 0)).x
	var gx1 := _grid_world(Vector2i(_w - 1, 0)).x
	for x: float in [gx0, gx1]:
		for z: float in [z0, z1]:
			pts.append(Vector3(x, FIT_GLYPH_TOP, z))
	var top := _pip_top() + FIT_HEADROOM
	var r := HQ_BASE * 0.5
	for xcol: int in [-1, _w]:
		var hx := _grid_world(Vector2i(xcol, 0)).x
		for sx: float in [-1.0, 1.0]:
			for sz: float in [-1.0, 1.0]:
				pts.append(Vector3(hx + r * sx, top, r * sz))
	return pts


## Fit the camera. It aims at the board's fit points (see _fit_points) and picks the distance so their projections
## fill the free area, then shifts the image there with h_offset / v_offset (camera-plane units). This is the same math
## as Godot's perspective projection (KEEP_HEIGHT), so cell_screen_pos matches what is drawn.
func _fit_camera() -> void:
	if cam == null:
		return
	var cb := Basis.from_euler(Vector3(deg_to_rad(CAM_PITCH_DEG), deg_to_rad(CAM_YAW_DEG), 0.0))
	var pts := _fit_points()
	var bounds := AABB(pts[0], Vector3.ZERO)
	for p: Vector3 in pts:
		bounds = bounds.expand(p)
	var center := bounds.get_center()
	var inv := cb.transposed()
	var rel: Array[Vector3] = []
	for p: Vector3 in pts:
		rel.append(inv * (p - center))
	var vp := _view_size()
	var k := Vector2(vp.x / FIT_VIEW.x, vp.y / FIT_VIEW.y)
	var ref := FIT_FREE.grow(-FIT_MARGIN)
	var area := Rect2(ref.position * k, ref.size * k)
	var n0 := Vector2(area.position.x / vp.x * 2.0 - 1.0, 1.0 - area.end.y / vp.y * 2.0)
	var n1 := Vector2(area.end.x / vp.x * 2.0 - 1.0, 1.0 - area.position.y / vp.y * 2.0)
	var t_size := n1 - n0
	var t_mid := (n0 + n1) * 0.5
	var ty := tan(deg_to_rad(CAM_FOV) * 0.5)
	var tx := ty * vp.x / vp.y
	var d := bounds.size.length() / ty
	var off := Vector2.ZERO
	for it in range(FIT_ITERS):
		var r := _ndc_rect(rel, d, off, tx, ty)
		var s := maxf(r.size.x / t_size.x, r.size.y / t_size.y)
		d *= s
		off *= s
		r = _ndc_rect(rel, d, off, tx, ty)
		var shift := t_mid - r.get_center()
		off -= Vector2(shift.x * d * tx, shift.y * d * ty)
	cam.keep_aspect = Camera3D.KEEP_HEIGHT
	cam.fov = CAM_FOV
	cam.near = CAM_NEAR
	cam.far = maxf(CAM_FAR, d + FIT_FAR_PAD)
	cam.transform = Transform3D(cb, center + cb * Vector3(0.0, 0.0, d))
	cam.h_offset = off.x
	cam.v_offset = off.y


func _ndc_rect(rel: Array[Vector3], d: float, off: Vector2, tx: float, ty: float) -> Rect2:
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	for r: Vector3 in rel:
		var depth := maxf(d - r.z, EPS)
		var p := Vector2((r.x - off.x) / (depth * tx), (r.y - off.y) / (depth * ty))
		lo = lo.min(p)
		hi = hi.max(p)
	return Rect2(lo, hi - lo)


# ======================= helpers: positions, materials, meshes =======================
func _cells() -> Array:
	var out: Array = []
	for y in range(_h):
		for x in range(_w):
			out.append(Vector2i(x, y))
	return out


func _grid_world(c: Vector2i) -> Vector3:
	return Vector3((c.x - (_w - 1) * 0.5) * CELL_DX, 0.0, (c.y - (_h - 1) * 0.5) * CELL_DZ)


func _home_world() -> Vector3:
	return Vector3(_grid_world(Vector2i(-1, 0)).x, 0.0, 0.0)


func _world(c: Vector2i, hunter: bool) -> Vector3:
	return _grid_world(c) + Vector3(0.0, 0.0 if hunter else VEH_Y, 0.0)


func _home_entry(row: int) -> Vector3:
	return Vector3(_home_world().x + HQ_PLAT.x * 0.5, VEH_Y, _grid_world(Vector2i(0, row)).z)


## The head of a street: just above row 0, where the hound starts its run.
func _street_head(x: int) -> Vector3:
	return _grid_world(Vector2i(x, 0)) - Vector3(0.0, 0.0, CELL_DZ * ENTRY_STREET_K)


## The height of the HOME pips above our HQ's base (the tower top plus the pip lift).
func _pip_top() -> float:
	return HQ_PLAT.y + HQ_TIERS * HQ_TIER_H + HOME_PIP_Y


## The camera's backward axis (toward the viewer) at the board's pitch and yaw.
func _cam_back() -> Vector3:
	return Basis.from_euler(Vector3(deg_to_rad(CAM_PITCH_DEG), _yaw, 0.0)).z


## The camera's backward axis flattened onto the ground (the side of a cell that faces the viewer).
func _cam_ground() -> Vector3:
	var b := _cam_back()
	var g := Vector3(b.x, 0.0, b.z)
	return g.normalized() if g.length() > EPS else Vector3(0.0, 0.0, 1.0)


func _type_col(type: String) -> Color:
	return TYPE_COLOR.get(type, GREY)


func _mat(col: Color, energy: float, alpha: float = 1.0) -> StandardMaterial3D:
	var k := "%s|%s|%s" % [col.to_html(), energy, alpha]
	if not _mats.has(k):
		_mats[k] = _make_mat(col, energy, alpha, alpha < 1.0)
	return _mats[k]


## A material of its own (for fades, flicker and pulses); its base alpha and energy are kept as metadata.
func _mat_live(col: Color, energy: float, alpha: float = 1.0) -> StandardMaterial3D:
	return _make_mat(col, energy, alpha, true)


func _make_mat(col: Color, energy: float, alpha: float, transparent: bool) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(col.r * ALBEDO_K, col.g * ALBEDO_K, col.b * ALBEDO_K, alpha)
	m.roughness = ROUGH
	if energy > 0.0:
		m.emission_enabled = true
		m.emission = col
		m.emission_energy_multiplier = energy
	if transparent:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.set_meta("a", alpha)
	m.set_meta("e", energy)
	return m


func _solid(col: Color) -> StandardMaterial3D:
	var k := "s%s" % col.to_html()
	if not _mats.has(k):
		var m := StandardMaterial3D.new()
		m.albedo_color = col
		m.roughness = ROUGH
		m.metallic = METAL
		_mats[k] = m
	return _mats[k]


func _tint(mats: Array, alpha_mul: float, energy_mul: float) -> void:
	for m: StandardMaterial3D in mats:
		var a := m.albedo_color
		a.a = clampf(float(m.get_meta("a", 1.0)) * alpha_mul, 0.0, 1.0)
		m.albedo_color = a
		m.emission_energy_multiplier = float(m.get_meta("e", 0.0)) * energy_mul


func _mi(parent: Node3D, mesh: Mesh, mat: Material, pos: Vector3) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = mat
	mi.position = pos
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(mi)
	return mi


func _box(parent: Node3D, pos: Vector3, size: Vector3, mat: Material) -> MeshInstance3D:
	var mi := _mi(parent, _unit_box, mat, pos)
	mi.scale = size
	return mi


func _cyl(parent: Node3D, pos: Vector3, r: float, h: float, segs: int, mat: Material) -> MeshInstance3D:
	var cm := CylinderMesh.new()
	cm.top_radius = r
	cm.bottom_radius = r
	cm.height = h
	cm.radial_segments = segs
	cm.rings = 1
	return _mi(parent, cm, mat, pos)


func _sphere(parent: Node3D, pos: Vector3, r: float, mat: Material) -> MeshInstance3D:
	var sm := SphereMesh.new()
	sm.radius = r
	sm.height = r * 2.0
	sm.radial_segments = SPHERE_SEGS
	sm.rings = SPHERE_RINGS
	return _mi(parent, sm, mat, pos)


func _torus(parent: Node3D, pos: Vector3, r_in: float, r_out: float, segs: int, mat: Material) -> MeshInstance3D:
	var tm := TorusMesh.new()
	tm.inner_radius = r_in
	tm.outer_radius = r_out
	tm.rings = segs
	tm.ring_segments = TORUS_TUBE
	var mi := _mi(parent, tm, mat, pos)
	mi.scale = Vector3(1.0, RING_FLAT, 1.0)
	return mi


## A thin box from p0 to p1 in 3D (any direction except straight up), w thick.
func _seg3(parent: Node3D, p0: Vector3, p1: Vector3, w: float, mat: Material) -> void:
	var d := p1 - p0
	var length := d.length()
	if length < EPS:
		return
	var xv := d / length
	var zv := xv.cross(Vector3.UP)
	if zv.length() < EPS:
		zv = Vector3.FORWARD
	zv = zv.normalized()
	var yv := zv.cross(xv)
	var mi := _mi(parent, _unit_box, mat, (p0 + p1) * 0.5)
	mi.basis = Basis(xv * (length + w * 0.5), yv * w, zv * w)


## A cone with its apex at `tip`, pointing along `dir`.
func _cone(parent: Node3D, tip: Vector3, dir: Vector3, r: float, h: float, mat: Material) -> void:
	if dir.length() < EPS:
		return
	var cm := CylinderMesh.new()
	cm.top_radius = 0.0
	cm.bottom_radius = r
	cm.height = h
	cm.radial_segments = RESP_HEAD_SEGS
	cm.rings = 1
	var yv := dir.normalized()
	var ref := Vector3.RIGHT if absf(yv.dot(Vector3.RIGHT)) < 0.9 else Vector3.FORWARD
	var xv := yv.cross(ref).normalized()
	var zv := xv.cross(yv)
	var mi := _mi(parent, cm, mat, tip - yv * h * 0.5)
	mi.basis = Basis(xv, yv, zv)


## A billboard text label, drawn over everything, with a dark outline.
func _label(parent: Node3D, text: String, pos: Vector3, col: Color, size: int, align: HorizontalAlignment = HORIZONTAL_ALIGNMENT_CENTER) -> Label3D:
	var l := Label3D.new()
	l.text = text
	l.font_size = size
	l.pixel_size = LABEL_PX
	l.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	l.no_depth_test = true
	l.modulate = col
	l.outline_size = LABEL_OUTLINE
	l.outline_modulate = SHADOW_INK
	l.horizontal_alignment = align
	l.position = pos
	parent.add_child(l)
	return l


## A holder turned toward the camera, for flat glyphs.
func _facing(parent: Node3D, pos: Vector3) -> Node3D:
	var holder := Node3D.new()
	holder.position = pos
	holder.rotation = Vector3(_tilt, _yaw, 0.0)
	parent.add_child(holder)
	return holder


## The type's shape (D triangle, N square, E circle) as a flat glyph facing the camera.
func _shape(parent: Node3D, pos: Vector3, type: String, s: float, mat: Material) -> Node3D:
	var holder := _facing(parent, pos)
	_shape_into(holder, type, s, mat)
	return holder


## The type's shape built flat in an existing facing holder's plane.
func _shape_into(holder: Node3D, type: String, s: float, mat: Material) -> void:
	match type:
		"D":
			_cyl(holder, Vector3.ZERO, s, SHAPE_DEPTH, TRI_SEGS, mat).rotation.x = -PI * 0.5
		"N":
			_box(holder, Vector3.ZERO, Vector3(s * SQUARE_K, s * SQUARE_K, SHAPE_DEPTH), mat)
		_:
			_cyl(holder, Vector3.ZERO, s, SHAPE_DEPTH, CIRCLE_SEGS, mat).rotation.x = -PI * 0.5


## A type badge: the type's shape on a dark disc, facing the camera.
func _badge(parent: Node3D, pos: Vector3, type: String, s: float, mat: Material) -> Node3D:
	var holder := _facing(parent, pos)
	_backing(holder, s * BADGE_BACK_K)
	_shape_into(holder, type, s, mat)
	return holder


## The hound silhouette (forward +x, on the floor) in a holder scaled by HOUND_S: body parts in `body`, glowing eyes in
## `eye`. Returns the leg nodes, each with a "gait" meta (+1 or -1) for the run cycle.
func _build_hound(parent: Node3D, body: Material, eye: Material) -> Array:
	var holder := Node3D.new()
	holder.scale = Vector3.ONE * HOUND_S
	parent.add_child(holder)
	for p: Array in HOUND_PARTS:
		var pos: Vector3 = p[0]
		var size: Vector3 = p[1]
		var b := _box(holder, pos, size, body)
		if p.size() > 2:
			b.rotation.z = float(p[2])
	var legs: Array = []
	for p: Array in HOUND_LEGS:
		var pos: Vector3 = p[0]
		var size: Vector3 = p[1]
		var leg := _box(holder, pos, size, body)
		leg.set_meta("gait", float(p[2]))
		legs.append(leg)
	for p: Array in HOUND_EYES:
		var pos: Vector3 = p[0]
		var size: Vector3 = p[1]
		_box(holder, pos, size, eye)
	return legs


## A flat chevron lying on the road, its tip at `tip`, pointing along `dir`.
func _chevron(parent: Node3D, tip: Vector3, dir: Vector3, mat: Material) -> Node3D:
	var holder := Node3D.new()
	holder.position = tip
	holder.rotation.y = _heading(dir, 0.0)
	parent.add_child(holder)
	for s: float in [1.0, -1.0]:
		var arm := Vector3(-cos(ARROW_ANG), 0.0, s * sin(ARROW_ANG))
		_box(holder, arm * ARROW_L * 0.5, Vector3(ARROW_L, LANE_T * 2.0, ARROW_W), mat).rotation.y = s * ARROW_ANG
	return holder


func _dashed_ring(parent: Node3D, r: float, mat: Material) -> Node3D:
	var holder := Node3D.new()
	holder.position = Vector3(0.0, RING_Y * 2.0, 0.0)
	parent.add_child(holder)
	for k in range(GHOST_DASHES):
		var a := TAU * float(k) / float(GHOST_DASHES)
		_box(holder, Vector3(cos(a) * r, 0.0, sin(a) * r), GHOST_DASH, mat).rotation.y = -a - PI * 0.5
	_spin.append(holder)
	return holder


## Thin boxes along a 2D polyline in a facing holder's plane.
func _polyline(holder: Node3D, pts: Array, w: float, mat: Material) -> void:
	for i in range(pts.size() - 1):
		var p0: Vector2 = pts[i]
		var p1: Vector2 = pts[i + 1]
		var d := p1 - p0
		var seg := _box(holder, Vector3((p0.x + p1.x) * 0.5, (p0.y + p1.y) * 0.5, 0.0), Vector3(d.length() + w, w, SHAPE_DEPTH), mat)
		seg.rotation.z = atan2(d.y, d.x)


## A dark disc behind a facing glyph, so the glyph reads against glow and buildings.
func _backing(holder: Node3D, r: float) -> void:
	_cyl(holder, Vector3(0.0, 0.0, -OUT_BACK_Z), r, SHAPE_DEPTH, CIRCLE_SEGS, _solid(BG)).rotation.x = -PI * 0.5


## A skull glyph facing the camera (head, dark eyes and nose, jaw with teeth) on a dark disc, scaled by s.
func _skull(parent: Node3D, pos: Vector3, s: float, m: Material) -> Node3D:
	var dark := _solid(BG)
	var holder := _facing(parent, pos)
	holder.scale = Vector3.ONE * s
	_backing(holder, SKULL_BACK_R)
	var head := _sphere(holder, Vector3(0.0, SKULL_HEAD_Y, 0.0), SKULL_HEAD_R, m)
	head.scale = Vector3(1.0, 1.0, SKULL_HEAD_FLAT)
	for sd: float in [-1.0, 1.0]:
		_box(holder, Vector3(SKULL_EYE_POS.x * sd, SKULL_EYE_POS.y, SKULL_EYE_POS.z), SKULL_EYE, dark)
	_box(holder, SKULL_NOSE_POS, SKULL_NOSE, dark)
	_box(holder, Vector3(0.0, SKULL_JAW_Y, 0.0), SKULL_JAW, m)
	for tx: float in SKULL_TOOTH_X:
		_box(holder, Vector3(tx, SKULL_JAW_Y, SKULL_JAW.z * 0.5), SKULL_TOOTH, dark)
	return holder


## A heart glyph facing the camera (a diamond with two round lobes) on a dark disc, scaled by s. broken adds a dark
## zigzag break in front of it.
func _heart(parent: Node3D, pos: Vector3, s: float, m: Material, broken: bool) -> Node3D:
	var holder := _facing(parent, pos)
	holder.scale = Vector3.ONE * s
	_backing(holder, HEART_BACK_R)
	_box(holder, Vector3(0.0, HEART_SQ_Y, 0.0), Vector3(HEART_SQ, HEART_SQ, SHAPE_DEPTH), m).rotation.z = PI * 0.25
	for sd: float in [-1.0, 1.0]:
		_cyl(holder, Vector3(HEART_LOBE.x * sd, HEART_LOBE.y, 0.0), HEART_LOBE_R, SHAPE_DEPTH, CIRCLE_SEGS, m).rotation.x = -PI * 0.5
	if broken:
		var crack := Node3D.new()
		crack.position = Vector3(0.0, 0.0, HEART_BREAK_Z)
		holder.add_child(crack)
		_polyline(crack, HEART_BREAK, HEART_BREAK_W, _solid(BG))
	return holder


func _ease_out(u: float) -> float:
	var x := 1.0 - clampf(u, 0.0, 1.0)
	return 1.0 - x * x * x


## A road key ("R" + z for routes, "S" + x for streets) so lines sharing a road get side-by-side lanes.
func _road_key(p: Vector3, horiz: bool) -> String:
	return ("R%d" % roundi(p.z * 10.0)) if horiz else ("S%d" % roundi(p.x * 10.0))


func _lateral(horiz: bool) -> Vector3:
	return Vector3(0.0, 0.0, 1.0) if horiz else Vector3(1.0, 0.0, 0.0)


## The next lane offset on a road: 0, +gap, -gap, +2 gap...
func _lane_offset(use: Dictionary, road: String) -> float:
	var n := int(use.get(road, 0))
	use[road] = n + 1
	if n == 0:
		return 0.0
	return LANE_GAP * float(ceili(float(n) * 0.5)) * (1.0 if n % 2 == 1 else -1.0)


# ======================= board labels and scramble =======================
## The text a board label shows: the real text, or seeded noise of the same length while scrambled.
func _board_text(text: String, slot: int) -> String:
	if not _scramble:
		return text
	return _noise(text, SCRAMBLE_SEED * SEED_MX + slot)


## Seeded noise of the same length: letters and digits become uppercase letters (lowercase stays lowercase), anything
## else is kept.
func _noise(text: String, noise_seed: int) -> String:
	var rng := RandomNumberGenerator.new()
	rng.seed = noise_seed
	var out := ""
	for i in range(text.length()):
		var code := text.unicode_at(i)
		if (code >= CODE_A and code <= CODE_Z) or (code >= CODE_0 and code <= CODE_9):
			out += char(CODE_A + rng.randi_range(0, LETTERS - 1))
		elif code >= CODE_LA and code <= CODE_LZ:
			out += char(CODE_LA + rng.randi_range(0, LETTERS - 1))
		else:
			out += text.substr(i, 1)
	return out


func _route_name(y: int) -> String:
	return str(_route_names[y]) if y < _route_names.size() else str(y)


func _street_name(x: int) -> String:
	return str(_street_names[x]) if x < _street_names.size() else str(x)


func _apply_label_text() -> void:
	for y in range(_route_labels.size()):
		var l: Variant = _route_labels[y]
		if is_instance_valid(l):
			(l as Label3D).text = _board_text(_route_name(y), y)
	for x in range(_street_labels.size()):
		var l: Variant = _street_labels[x]
		if is_instance_valid(l):
			(l as Label3D).text = _board_text(_street_name(x), SCRAMBLE_STREET_K + x)


# ======================= the static set =======================
func _build_env() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = BG
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = AMBIENT
	env.ambient_light_energy = AMBIENT_E
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.glow_enabled = true
	env.glow_intensity = GLOW_INTENSITY
	env.glow_strength = GLOW_STRENGTH
	env.glow_bloom = GLOW_BLOOM
	env.glow_hdr_threshold = GLOW_THRESHOLD
	env.glow_blend_mode = Environment.GLOW_BLEND_MODE_SCREEN
	_env = env
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	cam = Camera3D.new()
	cam.projection = Camera3D.PROJECTION_PERSPECTIVE
	cam.keep_aspect = Camera3D.KEEP_HEIGHT
	cam.fov = CAM_FOV
	cam.near = CAM_NEAR
	cam.far = CAM_FAR
	add_child(cam)
	var key := DirectionalLight3D.new()
	key.light_color = KEY_LIGHT
	key.light_energy = KEY_E
	key.rotation_degrees = KEY_ROT
	add_child(key)


func _build_floor() -> void:
	_box(_board, Vector3(0.0, -SLAB_T - FLOOR_DROP, 0.0), Vector3(FLOOR_SIZE, SLAB_T, FLOOR_SIZE), _solid(FLOOR_COL))
	var half := _slab_half()
	_box(_board, Vector3(0.0, -SLAB_T * 0.5, 0.0), Vector3(half.x * 2.0, SLAB_T, half.y * 2.0), _solid(SLAB_COL))
	var rim := _mat(AMBER, E_RIM)
	for s: float in [-1.0, 1.0]:
		_box(_board, Vector3(0.0, ROAD_Y, half.y * s), Vector3(half.x * 2.0, ROAD_T, RIM_W), rim)
		_box(_board, Vector3(half.x * s, ROAD_Y, 0.0), Vector3(RIM_W, ROAD_T, half.y * 2.0), rim)
	var grid := _mat(NET, E_GRID, HALO_ALPHA)
	var gx := -half.x + GRID_STEP
	while gx < half.x:
		_box(_board, Vector3(gx, ROAD_Y * 0.5, 0.0), Vector3(GRID_W, ROAD_T * 0.5, half.y * 2.0), grid)
		gx += GRID_STEP
	var gz := -half.y + GRID_STEP
	while gz < half.y:
		_box(_board, Vector3(0.0, ROAD_Y * 0.5, gz), Vector3(half.x * 2.0, ROAD_T * 0.5, GRID_W), grid)
		gz += GRID_STEP


## The three lit routes and the four gray cross streets. The street strips are kept (one per column) so the planned
## paths can hide the ones no line uses.
func _build_roads() -> void:
	var x0 := _grid_world(Vector2i(-1, 0)).x
	var x1 := _grid_world(Vector2i(_w, 0)).x
	var mid := (x0 + x1) * 0.5
	var length := x1 - x0
	for y in range(_h):
		var z := _grid_world(Vector2i(0, y)).z
		_box(_board, Vector3(mid, ROAD_Y, z), Vector3(length, ROAD_T, ROUTE_W), _solid(ASPHALT))
		_box(_board, Vector3(mid, ROAD_Y + STREET_LIFT, z), Vector3(length, ROAD_T, ROUTE_CORE_W), _mat(GOLD, E_ROUTE_CORE))
		for s: float in [-1.0, 1.0]:
			_box(_board, Vector3(mid, ROAD_Y + STREET_LIFT, z + s * ROUTE_W * 0.5), Vector3(length, ROAD_T, ROUTE_EDGE_W), _mat(AMBER, E_ROUTE))
	var z0 := _grid_world(Vector2i(0, 0)).z - STREET_EXT
	var z1 := _grid_world(Vector2i(0, _h - 1)).z + STREET_EXT
	_street_nodes.clear()
	for x in range(_w):
		var px := _grid_world(Vector2i(x, 0)).x
		_street_nodes.append(_box(_board, Vector3(px, ROAD_Y + STREET_LIFT * 2.0, (z0 + z1) * 0.5), Vector3(STREET_W, ROAD_T, z1 - z0), _mat(STREET_COL, E_STREET)))


## While planned paths are shown, a cross street shows only when a shown line (a planned STREET line or the outcome
## hunter's street) uses it; otherwise every street shows.
func _apply_street_vis() -> void:
	for x in range(_street_nodes.size()):
		var n: Variant = _street_nodes[x]
		if is_instance_valid(n):
			(n as Node3D).visible = not _paths_on or _path_streets.has(x) or _out_streets.has(x)


## Route names right of the corp platform on each road (the corp end), and street numbers at the north edge. Both
## follow the scramble.
func _build_coord_labels() -> void:
	_route_labels.clear()
	_street_labels.clear()
	var corp_x := _grid_world(Vector2i(_w, 0)).x + HQ_PLAT.x * 0.5 + ROUTE_LABEL_DX
	for y in range(_h):
		var z := _grid_world(Vector2i(0, y)).z
		_route_labels.append(_label(_board, _board_text(_route_name(y), y), Vector3(corp_x, ROUTE_LABEL_Y, z), GOLD, ROUTE_LABEL_FONT, HORIZONTAL_ALIGNMENT_LEFT))
	var half := _slab_half()
	for x in range(_w):
		var px := _grid_world(Vector2i(x, 0)).x + STREET_LABEL_DX
		_street_labels.append(_label(_board, _board_text(_street_name(x), SCRAMBLE_STREET_K + x), Vector3(px, STREET_LABEL_Y, -half.y + STREET_LABEL_IN), LABEL_GREY, STREET_LABEL_FONT))


func _build_skyline() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = SKY_SEED
	var body := _solid(BG)
	var edge := _mat(SKY_WIRE, E_SKY)
	for i in range(SKY_N):
		var p := Vector3(rng.randf_range(SKY_X.x, SKY_X.y), 0.0, rng.randf_range(SKY_Z.x, SKY_Z.y))
		var w := rng.randf_range(SKY_W.x, SKY_W.y)
		var h := rng.randf_range(SKY_H.x, SKY_H.y)
		_box(_board, p + Vector3(0.0, h * 0.5, 0.0), Vector3(w, h, w), body)
		_box(_board, p + Vector3(0.0, h, w * 0.5), Vector3(w, SKY_EDGE, SKY_EDGE), edge)
		_box(_board, p + Vector3(-w * 0.5, h * 0.5, w * 0.5), Vector3(SKY_EDGE, h, SKY_EDGE), edge)


func _build_motes() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = MOTE_SEED
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	var bm := BoxMesh.new()
	bm.size = Vector3.ONE * MOTE_S
	mm.mesh = bm
	mm.instance_count = MOTE_N
	for i in range(MOTE_N):
		var p := Vector3(rng.randf_range(-MOTE_BOX.x, MOTE_BOX.x), rng.randf_range(VEH_Y, MOTE_BOX.y), rng.randf_range(-MOTE_BOX.z, MOTE_BOX.z))
		mm.set_instance_transform(i, Transform3D(Basis.IDENTITY, p))
		mm.set_instance_color(i, AMBER if i % TRI_SEGS != 0 else NET)
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = mm
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.vertex_color_use_as_albedo = true
	m.albedo_color = Color(E_MOTE, E_MOTE, E_MOTE)
	mmi.material_override = m
	_board.add_child(mmi)


## An HQ campus at column x (-1 = ours, w = the corp's): a platform across the routes, a stepped tower with glowing
## corner edges and crowns in the HQ's color, window bands, a light. The tower sits in its own node (meta "tower") and
## the light is kept as meta "light", so the fall beat can collapse and redden them.
func _build_hq(xcol: int, col: Color, body_col: Color) -> Node3D:
	var root := Node3D.new()
	root.position = Vector3(_grid_world(Vector2i(xcol, 0)).x, 0.0, 0.0)
	_board.add_child(root)
	var depth := (_h - 1) * CELL_DZ + ROUTE_W * 2.0
	_box(root, Vector3(0.0, HQ_PLAT.y * 0.5, 0.0), Vector3(HQ_PLAT.x, HQ_PLAT.y, depth), _solid(STEEL))
	var edge := _mat(col, E_RING)
	for s: float in [-1.0, 1.0]:
		_box(root, Vector3(HQ_PLAT.x * 0.5 * s, HQ_PLAT.y, 0.0), Vector3(RIM_W, ROAD_T, depth), edge)
	var tower := Node3D.new()
	root.add_child(tower)
	root.set_meta("tower", tower)
	var body := _solid(body_col)
	var accent := _mat(col, E_HQ_EDGE)
	var win := _mat(HOT_WIN if col == AMBER else COBALT_HOT, E_HQ_WIN)
	for i in range(HQ_TIERS):
		var s := HQ_BASE - i * HQ_STEP
		var y := HQ_PLAT.y + (i + 0.5) * HQ_TIER_H
		var th := HQ_TIER_H * 0.92
		_box(tower, Vector3(0.0, y, 0.0), Vector3(s, th, s), body)
		for cx: float in [-1.0, 1.0]:
			for cz: float in [-1.0, 1.0]:
				_box(tower, Vector3(cx * s * 0.5, y, cz * s * 0.5), Vector3(HQ_EDGE_W, th, HQ_EDGE_W), accent)
		var ty := y + th * 0.5
		for sd: float in [-1.0, 1.0]:
			_box(tower, Vector3(0.0, ty, sd * s * 0.5), Vector3(s, HQ_EDGE_W, HQ_EDGE_W), accent)
			_box(tower, Vector3(sd * s * 0.5, ty, 0.0), Vector3(HQ_EDGE_W, HQ_EDGE_W, s), accent)
		for k in range(HQ_WIN_ROWS):
			var wy := y + (k - (HQ_WIN_ROWS - 1) * 0.5) * HQ_TIER_H / float(HQ_WIN_ROWS + 1)
			_box(tower, Vector3(0.0, wy, s * 0.5 + WIN_EPS), Vector3(s * WIN_FRAC, WIN_H, WIN_EPS), win)
			_box(tower, Vector3(-s * 0.5 - WIN_EPS, wy, 0.0), Vector3(WIN_EPS, WIN_H, s * WIN_FRAC), win)
	var lt := OmniLight3D.new()
	lt.light_color = WARM_LIGHT if col == AMBER else COBALT
	lt.light_energy = HQ_LIGHT_E
	lt.omni_range = HQ_LIGHT_RANGE
	lt.position = Vector3(0.0, HQ_LIGHT_Y, 0.0)
	root.add_child(lt)
	root.set_meta("light", lt)
	return root


func _build_home_pips() -> void:
	_home_pips.clear()
	_home_pip_holder = _facing(_home_root, Vector3(0.0, _pip_top(), 0.0))
	for i in range(HOME_HP_MAX):
		_home_pips.append(_box(_home_pip_holder, Vector3((i - (HOME_HP_MAX - 1) * 0.5) * HOME_PIP_GAP, 0.0, 0.0), HOME_PIP, _mat(GOLD, E_PIP)))
	_refresh_pips()


## Gold for kept pips, red for lost ones; while lethal, the last kept pip uses the pulsing red material.
func _refresh_pips() -> void:
	for i in range(_home_pips.size()):
		var m: Material = _mat(GOLD, E_PIP) if i < _home_hp else _mat(RED, E_PIP)
		if _lethal and _lethal_pip != null and i == _home_hp - 1:
			m = _lethal_pip
		(_home_pips[i] as MeshInstance3D).material_override = m


## Build or remove the lethal mark (the pulsing skull on our tower and the pulsing last pip). A fallen HQ has none.
func _refresh_lethal() -> void:
	if is_instance_valid(_lethal_root):
		_lethal_root.queue_free()
	_lethal_root = null
	_lethal_pip = null
	_lethal_mats.clear()
	if _lethal and _home_root != null and not _fallen:
		var m := _mat_live(RED, E_LETHAL)
		_lethal_pip = _mat_live(RED, E_LETHAL_PIP)
		_lethal_mats = [m, _lethal_pip]
		var pos := Vector3(0.0, LETHAL_SKULL_Y, 0.0) + _cam_back() * LETHAL_FWD
		_lethal_root = _skull(_home_root, pos, LETHAL_SKULL_S, m)
	_refresh_pips()


func _refresh_home_ghost() -> void:
	if _home_ghost != null:
		_home_ghost.queue_free()
		_home_ghost = null
	if _ghost_home and _home_root != null:
		_home_ghost = _dashed_ring(_home_root, GHOST_HOME_R, _mat(GOLD, E_GHOST))


# ======================= districts =======================
func _refresh_all_cells() -> void:
	for c: Vector2i in _cell_root:
		_refresh_cell(c)


func _refresh_cell(c: Vector2i) -> void:
	if not _cell_root.has(c):
		return
	var st: String = _status.get(c, "NEUTRAL")
	var sen := str(_sentries.get(c, ""))
	var key := "%s|%s|%s|%s" % [st, sen, c == _ghost_cell, _cracked.has(c)]
	if str(_cell_key.get(c, "")) == key:
		return
	_cell_key[c] = key
	_rebuild_cell(c, st, sen)


## NEUTRAL: dim gray. OK: warm amber ring, decal and lit pips (plus a crack decal when hit this raid). DOWN: dim amber,
## a wrench with the cobalt "1" countdown mark (TAKEN next raid) and flicker. TAKEN: cobalt.
func _rebuild_cell(c: Vector2i, st: String, sen: String) -> void:
	var root: Node3D = _cell_root[c]
	for ch in root.get_children():
		root.remove_child(ch)
		ch.queue_free()
	var v := int(_values.get(c, VALUE_MIN))
	var body_col := NEUTRAL_BODY
	var win_col := GREY
	var win_e := E_WIN_DIM
	var ring_col := GREY
	var ring_e := E_RING_DIM
	var pip_col := GREY
	var pip_e := E_PIP_DIM
	var decal_col := AMBER
	var decal_a := 0.0
	match st:
		"OK":
			body_col = WARM_METAL
			win_col = HOT_WIN
			win_e = E_WIN
			ring_col = AMBER
			ring_e = E_RING
			pip_col = AMBER
			pip_e = E_PIP
			decal_a = DECAL_A_OK
		"DOWN":
			body_col = DEAD
			win_col = AMBER
			win_e = E_WIN_DOWN
			ring_col = AMBER
			ring_e = E_RING_DOWN
			pip_col = AMBER
			pip_e = E_PIP_DIM
			decal_a = DECAL_A_DOWN
		"TAKEN":
			body_col = TAKEN_BODY
			win_col = COBALT_HOT
			win_e = E_WIN
			ring_col = COBALT
			ring_e = E_RING
			pip_col = COBALT
			pip_e = E_PIP
			decal_col = COBALT
			decal_a = DECAL_A_TAKEN
	var win := _mat_live(win_col, win_e)
	_win_mats[c] = win
	var body := _solid(body_col)
	var rng := RandomNumberGenerator.new()
	rng.seed = BLD_SEED + c.x * SEED_MX + c.y * SEED_MY
	var hmax := lerpf(BLD_H_MIN, BLD_H_MAX, clampf(float(v - VALUE_MIN) / float(VALUE_MAX - VALUE_MIN), 0.0, 1.0))
	for q: Vector2 in QUADS:
		var off := Vector3(q.x * BLD_OFF, 0.0, q.y * BLD_OFF)
		var cap := BLD_FRONT_H if q.y > 0.0 else (BLD_SIDE_H if q.x < 0.0 else BLD_H_MAX)
		var h := minf(rng.randf_range(BLD_H_MIN, maxf(BLD_H_MIN, hmax)), cap)
		var w := rng.randf_range(BLD_W_MIN, BLD_W_MAX)
		_box(root, off + Vector3(0.0, h * 0.5, 0.0), Vector3(w, h, w), body)
		var floors := maxi(1, int(h / FLOOR_H))
		for f in range(floors):
			var y := (f + 0.5) * h / float(floors)
			_box(root, off + Vector3(0.0, y, w * 0.5 + WIN_EPS), Vector3(w * WIN_FRAC, WIN_H, WIN_EPS), win)
			_box(root, off + Vector3(-w * 0.5 - WIN_EPS, y, 0.0), Vector3(WIN_EPS, WIN_H, w * WIN_FRAC), win)
	if decal_a > 0.0:
		_cyl(root, Vector3(0.0, DECAL_Y, 0.0), DECAL_R, DECAL_T, CIRCLE_SEGS, _mat(decal_col, E_DECAL, decal_a))
	_torus(root, Vector3(0.0, RING_Y, 0.0), RING_R_IN, RING_R_OUT, HEX, _mat(ring_col, ring_e))
	var pip := _mat(pip_col, pip_e)
	for i in range(v / 2):
		_box(root, PIP_POS + Vector3(0.0, PIP_SIZE.y * 0.5 + i * PIP_STEP, 0.0), PIP_SIZE, pip)
	if _exploits.has(c):
		_build_key(root, _mat(ACID, E_KEY if st == "OK" or st == "DOWN" else E_KEY_DIM))
	if st == "DOWN":
		_build_wrench(root)
		_build_countdown(root)
	if st == "OK" and _cracked.has(c):
		_build_crack(root)
	if sen != "":
		_build_sentry(root, sen)
	if c == _ghost_cell:
		_dashed_ring(root, GHOST_R, _mat(GOLD, E_GHOST))


func _build_key(root: Node3D, mat: Material) -> void:
	var holder := _facing(root, KEY_POS)
	var bow := _torus(holder, Vector3.ZERO, KEY_BOW.x, KEY_BOW.y, CIRCLE_SEGS, mat)
	bow.scale = Vector3.ONE
	bow.rotation.x = -PI * 0.5
	for p: Array in KEY_PARTS:
		var pos: Vector3 = p[0]
		var size: Vector3 = p[1]
		_box(holder, pos, size, mat)


func _build_wrench(root: Node3D) -> void:
	var holder := _facing(root, WRENCH_POS)
	_cyl(holder, Vector3.ZERO, WRENCH_DISC.x, WRENCH_DISC.y, CIRCLE_SEGS, _solid(DEAD)).rotation.x = -PI * 0.5
	var m := _mat(GREY, E_WRENCH)
	for p: Array in WRENCH_PARTS:
		var pos: Vector3 = p[0]
		var size: Vector3 = p[1]
		_box(holder, pos, size, m).rotation.z = float(p[2])


## L12: the "TAKEN next raid" countdown next to the wrench: a cobalt ring on a dark disc with a cobalt "1" (boxes).
func _build_countdown(root: Node3D) -> void:
	var holder := _facing(root, WRENCH_POS)
	var mark := Node3D.new()
	mark.position = Vector3(COUNT_POS.x, COUNT_POS.y, 0.0)
	holder.add_child(mark)
	var m := _mat(COBALT, E_COUNT)
	_backing(mark, COUNT_BACK_R)
	var ring := _torus(mark, Vector3.ZERO, COUNT_RING.x, COUNT_RING.y, CIRCLE_SEGS, m)
	ring.scale = Vector3.ONE
	ring.rotation.x = -PI * 0.5
	var digit := Node3D.new()
	digit.position = Vector3(0.0, 0.0, COUNT_Z)
	mark.add_child(digit)
	_box(digit, Vector3(COUNT_STEM_X, 0.0, 0.0), COUNT_STEM, m)
	_box(digit, Vector3(COUNT_FLAG_POS.x, COUNT_FLAG_POS.y, 0.0), COUNT_FLAG, m).rotation.z = COUNT_FLAG_ROT
	_box(digit, Vector3(COUNT_STEM_X, COUNT_BASE_Y, 0.0), COUNT_BASE, m)


## L12: a crack decal laid flat across a district hit this raid that is OK again.
func _build_crack(root: Node3D) -> void:
	var holder := Node3D.new()
	holder.position = Vector3(0.0, CRACK_DECAL_Y, 0.0)
	holder.rotation = Vector3(-PI * 0.5, CRACK_DECAL_YAW, 0.0)
	holder.scale = Vector3.ONE * CRACK_DECAL_S
	root.add_child(holder)
	var m := _mat(RED, E_CRACK)
	_polyline(holder, CRACK_PTS, CRACK_W, m)
	_polyline(holder, CRACK_BRANCH, CRACK_W * 0.8, m)
	_polyline(holder, CRACK_BRANCH_2, CRACK_W * 0.8, m)


func _build_sentry(root: Node3D, type: String) -> void:
	var col := _type_col(type)
	var m := _mat(col, E_SENTRY)
	_torus(root, Vector3(0.0, DECAL_Y + RING_Y * 0.5, 0.0), SENTRY_DECAL.x, SENTRY_DECAL.y, CIRCLE_SEGS, m)
	_cyl(root, Vector3(0.0, DECAL_Y + DECAL_T, 0.0), SENTRY_DECAL.x, DECAL_T, CIRCLE_SEGS, _mat(col, E_SENTRY * HALO_E_K, DECAL_ALPHA))
	_cyl(root, Vector3(0.0, SENTRY_BASE.y * 0.5, 0.0), SENTRY_BASE.x, SENTRY_BASE.y, HEX, _solid(STEEL))
	_cyl(root, Vector3(0.0, SENTRY_POLE.y * 0.5, 0.0), SENTRY_POLE.x, SENTRY_POLE.y, HEX, _mat(col, E_SENTRY * HALO_E_K))
	_shape(root, Vector3(0.0, SENTRY_GLYPH_Y, 0.0), type, SENTRY_GLYPH_S, m)


# ======================= highlights =======================
## The plain pulsing glow (highlight()): a filled disc and a ring in the given color.
func _hl_disc(pos: Vector3, color: Color) -> void:
	var m := _mat_live(color, E_HL, HL_ALPHA)
	var root := Node3D.new()
	root.position = pos + Vector3(0.0, HL_Y, 0.0)
	_hl_root.add_child(root)
	_cyl(root, Vector3.ZERO, HL_R, ROAD_T, CIRCLE_SEGS, m)
	_torus(root, Vector3.ZERO, HL_R, HL_R + RIM_W, CIRCLE_SEGS, m)
	_hl.append(m)


## Capture target: an amber plus on a dark disc over the district and a pulsing amber ring on its ground.
func _hl_capture(pos: Vector3, home: bool) -> void:
	var m := _mat_live(AMBER, E_HL_GLYPH)
	_hl.append(m)
	var r := HL_HOME_R if home else HL_R
	var lift := HQ_PLAT.y if home else 0.0
	_torus(_hl_root, pos + Vector3(0.0, HL_Y + lift, 0.0), r, r + HL_RING_W, CIRCLE_SEGS, m)
	var holder := _facing(_hl_root, pos + Vector3(0.0, HL_GLYPH_Y + lift, 0.0))
	_backing(holder, HL_BACK_R)
	_box(holder, Vector3.ZERO, Vector3(PLUS_L, PLUS_W, SHAPE_DEPTH), m)
	_box(holder, Vector3.ZERO, Vector3(PLUS_W, PLUS_L, SHAPE_DEPTH), m)


## Repair target: a red outline around the district's wrench glyph (a ring round its disc and padded red parts behind
## the gray wrench) and a pulsing red hex ring on its ground.
func _hl_repair(pos: Vector3, home: bool) -> void:
	var m := _mat_live(RED, E_HL_GLYPH)
	_hl.append(m)
	var r := HL_HOME_R if home else HL_R
	var lift := HQ_PLAT.y if home else 0.0
	_torus(_hl_root, pos + Vector3(0.0, HL_Y + lift, 0.0), r, r + HL_RING_W, HEX, m)
	var holder := _facing(_hl_root, pos + WRENCH_POS + Vector3(0.0, lift, 0.0))
	var ring := _torus(holder, Vector3.ZERO, WRENCH_DISC.x, WRENCH_DISC.x + REPAIR_RING_W, CIRCLE_SEGS, m)
	ring.scale = Vector3.ONE
	ring.rotation.x = -PI * 0.5
	for p: Array in WRENCH_PARTS:
		var pp: Vector3 = p[0]
		var size: Vector3 = p[1]
		var padded := size + Vector3(REPAIR_PAD, REPAIR_PAD, 0.0) * 2.0
		_box(holder, Vector3(pp.x, pp.y, REPAIR_Z), padded, m).rotation.z = float(p[2])


## Picked or committed: a steady white ring and a white check on its camera-side edge (clear of the outcome glyphs).
func _hl_picked(pos: Vector3, home: bool) -> void:
	var m := _mat(WHITE, E_PICK)
	var r := (GHOST_HOME_R + PICK_HOME_PAD) if home else PICK_R
	var lift := HQ_PLAT.y if home else 0.0
	_torus(_hl_root, pos + Vector3(0.0, HL_Y + lift, 0.0), r, r + PICK_RING_W, CIRCLE_SEGS, m)
	var holder := _facing(_hl_root, pos + _cam_ground() * r + Vector3(0.0, PICK_CHECK_Y + lift, 0.0))
	_backing(holder, PICK_BACK_R)
	_polyline(holder, CHECK_PTS, CHECK_W, m)


# ======================= planned paths =======================
## The ends of a line on the ground at height y: [entry, exit, horizontal]. Routes end at the HOME platform. Returns []
## for an empty or zero-length line.
func _line_span(ln: Dictionary, y: float) -> Array:
	var cells: Array = ln.get("cells", [])
	if cells.is_empty():
		return []
	var route := str(ln.get("kind", "ROUTE")) == "ROUTE"
	var first: Vector2i = cells[0]
	var last: Vector2i = cells[cells.size() - 1]
	var step := Vector2i(-1, 0) if route else Vector2i(0, 1)
	if cells.size() > 1:
		var second: Vector2i = cells[1]
		step = Vector2i(signi(second.x - first.x), signi(second.y - first.y))
	var sv := Vector3(float(step.x), 0.0, float(step.y))
	var horiz := step.x != 0
	var a := Vector3.ZERO
	var b := Vector3.ZERO
	if horiz:
		a = _grid_world(first) - sv * CELL_DX * ENTRY_ROUTE_K
		b = _home_entry(last.y) if bool(ln.get("home", route)) else _grid_world(last) + sv * CELL_DX * ENTRY_ROUTE_K
	else:
		a = _grid_world(first) - sv * STREET_EXT
		b = _grid_world(last) + sv * STREET_EXT
	a.y = y
	b.y = y
	if (b - a).length() < EPS:
		return []
	return [a, b, horiz]


## A dashed lane from a to b (shifted by lat), ending in a chevron when arrow is true.
func _dashes(parent: Node3D, a: Vector3, b: Vector3, lat: Vector3, m: Material, arrow: bool = true) -> void:
	var d := b - a
	var length := d.length()
	if length < EPS:
		return
	var dir := d / length
	var rot := _heading(dir, 0.0)
	var stop := length - ARROW_L * 0.3 if arrow else length
	var u := 0.0
	while u < stop:
		var e := minf(u + DASH_L, stop)
		_box(parent, a + dir * ((u + e) * 0.5) + lat, Vector3(e - u, LANE_T, PATH_W), m).rotation.y = rot
		u += DASH_L + DASH_G
	if arrow:
		_chevron(parent, b + lat, dir, m)


## L12: a solid lane from a to b (shifted by lat), ending in a chevron (known beams).
func _lane_solid(parent: Node3D, a: Vector3, b: Vector3, lat: Vector3, m: Material) -> void:
	var d := b - a
	var length := d.length()
	if length < EPS:
		return
	var dir := d / length
	var stop := length - ARROW_L * 0.3
	_box(parent, a + dir * (stop * 0.5) + lat, Vector3(stop, LANE_T, PATH_W), m).rotation.y = _heading(dir, 0.0)
	_chevron(parent, b + lat, dir, m)


## The sealed candidate index of a line: its "cand" key, or its index when it is marked "sealed"; -1 for known beams.
func _cand_of(ln: Dictionary) -> int:
	if ln.has("cand"):
		return int(ln["cand"])
	if bool(ln.get("sealed", false)):
		return int(ln.get("index", -1))
	return -1


## True for a candidate line that is not the selected one (drawn at 15% alpha, after the full-strength lines).
func _path_off(ln: Dictionary, selected: int) -> bool:
	var c := _cand_of(ln)
	return c >= 0 and selected >= 0 and c != selected


## One planned line with its type glyph at the entry. The whole line is drawn; blocks never cut or tick it.
## - Unselected candidate: dashed, 15% alpha, no arrowhead.
## - Selected candidate: dashed, full strength, chevron, pulsing.
## - Candidate with no selection: dashed, chevron.
## - Dim (an extra that will not fire): dashed and faded, no arrowhead.
## - Known beam: a solid lane at full strength, chevron.
func _draw_path(ln: Dictionary, selected: int = -1) -> void:
	var span := _line_span(ln, PATH_Y)
	if span.is_empty():
		return
	var a: Vector3 = span[0]
	var b: Vector3 = span[1]
	var horiz: bool = span[2]
	var type := str(ln.get("type", "D"))
	var col := _type_col(type)
	var lat := _lateral(horiz) * _lane_offset(_path_use, _road_key(a, horiz))
	var cand := _cand_of(ln)
	var m: StandardMaterial3D
	if cand >= 0 and selected >= 0 and cand != selected:
		m = _mat(col, E_PATH * CAND_OFF_E, CAND_OFF_ALPHA)
		_dashes(_path_root, a, b, lat, m, false)
	elif cand >= 0 and selected >= 0:
		m = _mat_live(col, E_PATH, PATH_FULL_ALPHA)
		_path_pulse.append(m)
		_dashes(_path_root, a, b, lat, m, true)
	elif cand >= 0:
		m = _mat(col, E_PATH, PATH_ALPHA)
		_dashes(_path_root, a, b, lat, m, true)
	elif bool(ln.get("dim", false)):
		m = _mat(col, E_PATH * PATH_DIM_K, PATH_ALPHA * PATH_DIM_K)
		_dashes(_path_root, a, b, lat, m, false)
	else:
		m = _mat(col, E_PATH, PATH_FULL_ALPHA)
		_lane_solid(_path_root, a, b, lat, m)
	_shape(_path_root, a + lat + Vector3(0.0, PATH_GLYPH_Y, 0.0), type, PATH_GLYPH_S, m)


# ======================= forecast outcome overlay =======================
## A hit: a red crack glyph over the district and a red hex ring on its ground.
func _out_hit(c: Vector2i) -> void:
	var m := _mat(RED, E_OUT)
	_torus(_outcome_root, _grid_world(c) + Vector3(0.0, OUT_RING_Y, 0.0), HIT_MARK_R.x, HIT_MARK_R.y, HEX, m)
	var holder := _facing(_outcome_root, _grid_world(c) + Vector3(0.0, OUT_GLYPH_Y, 0.0))
	_backing(holder, OUT_BACK_R)
	_polyline(holder, CRACK_PTS, CRACK_W, m)
	_polyline(holder, CRACK_BRANCH, CRACK_W * 0.8, m)
	_polyline(holder, CRACK_BRANCH_2, CRACK_W * 0.8, m)


## A block: a shield glyph in the sentry's type color over the district and a ring of that color on its ground.
func _out_block(c: Vector2i, type: String) -> void:
	var m := _mat(_type_col(type), E_OUT)
	_torus(_outcome_root, _grid_world(c) + Vector3(0.0, OUT_RING_Y, 0.0), SHIELD_RING_R.x, SHIELD_RING_R.y, CIRCLE_SEGS, m)
	var holder := _facing(_outcome_root, _grid_world(c) + Vector3(0.0, OUT_GLYPH_Y, 0.0))
	_backing(holder, OUT_BACK_R)
	_box(holder, Vector3(0.0, SHIELD_TOP_Y, 0.0), SHIELD_TOP, m)
	_cyl(holder, Vector3(0.0, SHIELD_TIP_Y, 0.0), SHIELD_TIP_R, SHAPE_DEPTH, TRI_SEGS, m).rotation.x = PI * 0.5


## HOME hit: a red skull in front of our HQ tower and a red ring on its platform.
func _out_home() -> void:
	var m := _mat(RED, E_OUT)
	_torus(_outcome_root, _home_world() + Vector3(0.0, HQ_PLAT.y + RING_Y, 0.0), HOME_MARK_R.x, HOME_MARK_R.y, CIRCLE_SEGS, m)
	_skull(_outcome_root, _home_world() + Vector3(0.0, SKULL_Y, 0.0) + _cam_back() * SKULL_FWD, SKULL_S, m)


## The hunter's run: a dashed cobalt lane down its street, with the cobalt hound (glowing eyes, type badge) standing
## at its start, facing down the street. Its materials are kept so a JAM preview can dim it; its street counts as used.
func _out_hunter(ln: Dictionary) -> void:
	if str(ln.get("kind", "")) == "STREET":
		_out_streets[int(ln.get("index", -1))] = true
	var span := _line_span(ln, OUT_PATH_Y)
	if span.is_empty():
		return
	var a: Vector3 = span[0]
	var b: Vector3 = span[1]
	var horiz: bool = span[2]
	var type := str(ln.get("type", "D"))
	var m := _mat_live(HUNTER_TRAIL, E_PATH)
	var body := _mat_live(HUNTER_BODY, E_HUNTER)
	var eye := _mat_live(HUNTER_EYE, E_EYE)
	var bm := _mat_live(_type_col(type), E_OUT)
	_out_hound_mats = [m, body, bm]
	var lat := _lateral(horiz) * _lane_offset(_path_use.duplicate(), _road_key(a, horiz))
	_dashes(_outcome_root, a, b, lat, m)
	var dir := (b - a).normalized()
	var hound := Node3D.new()
	hound.position = Vector3(a.x, 0.0, a.z) + lat
	hound.rotation.y = _heading(dir, HEADING_DOWN)
	hound.scale = Vector3.ONE * OUT_HOUND_S
	_outcome_root.add_child(hound)
	_build_hound(hound, body, eye)
	_eyes.append({"node": hound, "mat": eye})
	_out_hound = hound
	_badge(_outcome_root, hound.position + Vector3(0.0, OUT_HOUND_GLYPH_Y, 0.0), type, HUNTER_BADGE_S * OUT_HOUND_GLYPH_K, bm)


# ======================= route verdicts =======================
## One route's verdict: a ring on the road just right of our HQ platform and the tier glyph above it, pushed toward the
## camera. Unknown tiers draw nothing.
func _verdict(route: int, tier_name: String) -> void:
	var entry := _home_entry(route)
	var ground := Vector3(entry.x + VERDICT_DX, 0.0, entry.z)
	var pos := ground + Vector3(0.0, VERDICT_Y, 0.0) + _cam_back() * VERDICT_FWD
	var col := HOLD_COL
	match tier_name:
		"HOLDS", "EVADED":
			col = HOLD_COL
		"BATTERED", "DAMAGED":
			col = AMBER
		"BREACHED":
			col = RED
		_:
			return
	var m := _mat(col, E_VERDICT)
	_torus(_verdict_root, ground + Vector3(0.0, OUT_RING_Y, 0.0), VERDICT_RING_R.x, VERDICT_RING_R.y, CIRCLE_SEGS, m)
	match tier_name:
		"HOLDS", "EVADED":
			_heart(_verdict_root, pos, VERDICT_S, m, false)
		"BATTERED", "DAMAGED":
			_heart(_verdict_root, pos, VERDICT_S, m, true)
		_:
			_skull(_verdict_root, pos, VERDICT_SKULL_S, m)


# ======================= response preview =======================
## Where the reserve tray sits for a DEPLOY: just right of our HQ platform, on the target's route row.
func _tray_pos(to: Vector2i) -> Vector3:
	var z := _grid_world(Vector2i(0, clampi(to.y, 0, _h - 1))).z
	return Vector3(_home_world().x + RESP_TRAY_DX, 0.0, z)


## The reserve tray: a small steel tray with a hex ring and the type badge above it.
func _resp_tray(pos: Vector3, type: String, m: Material) -> void:
	_box(_resp_root, pos + Vector3(0.0, RESP_TRAY.y * 0.5, 0.0), RESP_TRAY, _solid(STEEL))
	_torus(_resp_root, pos + Vector3(0.0, RESP_TRAY.y, 0.0), RESP_TRAY_R, RESP_TRAY_R + HL_RING_W, HEX, m)
	_badge(_resp_root, pos + Vector3(0.0, RESP_BADGE_Y, 0.0), type, RESP_BADGE_S, m)


## A sentry source: a spinning dashed ring in the type color around the sentry's cell.
func _resp_source(pos: Vector3, m: Material) -> void:
	var holder := Node3D.new()
	holder.position = pos
	_resp_root.add_child(holder)
	_dashed_ring(holder, RESP_SRC_R, m)


## The target: a ghost sentry of the type (half alpha) and a ring in the type color.
func _resp_target(c: Vector2i, type: String, m: Material) -> void:
	var pos := _grid_world(c)
	var gm := _mat_live(_type_col(type), E_SENTRY, RESP_GHOST_A)
	_resp_mats.append(gm)
	_torus(_resp_root, pos + Vector3(0.0, DECAL_Y + RING_Y * 0.5, 0.0), SENTRY_DECAL.x, SENTRY_DECAL.y, CIRCLE_SEGS, gm)
	_cyl(_resp_root, pos + Vector3(0.0, SENTRY_POLE.y * 0.5, 0.0), SENTRY_POLE.x, SENTRY_POLE.y, HEX, gm)
	_shape(_resp_root, pos + Vector3(0.0, SENTRY_GLYPH_Y, 0.0), type, SENTRY_GLYPH_S, gm)
	_torus(_resp_root, pos + Vector3(0.0, HL_Y, 0.0), HL_R, HL_R + HL_RING_W, CIRCLE_SEGS, m)


## An arc arrow from a to b (ground points), its ends cut back by a_cut / b_cut, peaking higher for longer moves, with
## a cone head landing on the target.
func _resp_arrow(a: Vector3, b: Vector3, a_cut: float, b_cut: float, m: Material) -> void:
	var flat := Vector3(b.x - a.x, 0.0, b.z - a.z)
	var dist := flat.length()
	if dist < EPS:
		return
	var dir := flat / dist
	if dist <= a_cut + b_cut + EPS:
		a_cut = 0.0
		b_cut = 0.0
	var p0 := a + dir * a_cut
	var p1 := b - dir * b_cut
	p0.y = RESP_END_Y
	p1.y = RESP_END_Y
	var hgt := RESP_ARC_H + RESP_ARC_K * dist
	var pts: Array[Vector3] = []
	for i in range(RESP_ARC_SEGS + 1):
		var u := float(i) / float(RESP_ARC_SEGS)
		var p := p0.lerp(p1, u)
		p.y += hgt * 4.0 * u * (1.0 - u)
		pts.append(p)
	var last := pts.size() - 1
	var t := (pts[last] - pts[last - 1]).normalized()
	for i in range(RESP_ARC_SEGS):
		var q1 := pts[i + 1]
		if i == RESP_ARC_SEGS - 1:
			q1 -= t * RESP_HEAD_L * RESP_HEAD_CUT
		_seg3(_resp_root, pts[i], q1, RESP_ARC_W, m)
	_cone(_resp_root, pts[last], t, RESP_HEAD_R, RESP_HEAD_L, m)


## JAM: a red cross (pushed toward the camera) and a red ring over the hound, and the hound and its path dim. Uses the
## outcome hound, else the head of p.street; draws nothing without either.
func _resp_jam(p: Dictionary) -> void:
	var pos := Vector3.ZERO
	var have := false
	if is_instance_valid(_out_hound):
		pos = _out_hound.position
		have = true
	else:
		var sv: Variant = p.get("street", null)
		if sv is int:
			pos = _street_head(int(sv))
			have = true
	if not have:
		return
	var m := _mat_live(RED, E_RESP)
	_resp_mats.append(m)
	_torus(_resp_root, Vector3(pos.x, HL_Y, pos.z), RESP_JAM_R, RESP_JAM_R + HL_RING_W, CIRCLE_SEGS, m)
	var holder := _facing(_resp_root, Vector3(pos.x, RESP_JAM_Y, pos.z) + _cam_back() * RESP_JAM_FWD)
	for s: float in [1.0, -1.0]:
		_box(holder, Vector3.ZERO, RESP_JAM_BAR, m).rotation.z = s * PI * 0.25
	if not _out_hound_mats.is_empty():
		_tint(_out_hound_mats, RESP_JAM_DIM, RESP_JAM_DIM)
		_resp_dimmed = true


# ======================= playout trails and marks =======================
func _trail_add(mats: Array) -> void:
	if _instant:
		_tint(mats, TRAIL_REST, TRAIL_REST_E)
	else:
		_tint(mats, 1.0, 1.0)
		_trail_fade.append({"mats": mats, "t": 0.0})


func _snap_trails() -> void:
	for f: Dictionary in _trail_fade:
		_tint(f["mats"], TRAIL_REST, TRAIL_REST_E)
	_trail_fade.clear()


func _step_trails(dt: float) -> void:
	if _trail_fade.is_empty():
		return
	var keep: Array = []
	for f: Dictionary in _trail_fade:
		f["t"] = float(f["t"]) + dt
		var u := clampf(float(f["t"]) / TRAIL_FADE_T, 0.0, 1.0)
		var e := _ease_out(u)
		_tint(f["mats"], lerpf(1.0, TRAIL_REST, e), lerpf(1.0, TRAIL_REST_E, e))
		if u < 1.0:
			keep.append(f)
	_trail_fade = keep


## A trail segment of one line from a to b on the ground (its own lane per road), with a dot and the line's moving chevron.
func _trail_seg(line: int, a: Vector3, b: Vector3, col: Color) -> void:
	var a0 := Vector3(a.x, TRAIL_Y, a.z)
	var b0 := Vector3(b.x, TRAIL_Y, b.z)
	var d := b0 - a0
	var flat := Vector2(d.x, d.z).length()
	if flat < TRAIL_MIN:
		return
	var horiz := absf(d.x) >= absf(d.z)
	var road := _road_key(a0, horiz)
	var key := "%d|%s" % [line, road]
	if not _lane.has(key):
		_lane[key] = _lane_offset(_road_use, road)
	var lat := _lateral(horiz) * float(_lane[key])
	var m := _mat_live(col, E_TRAIL, TRAIL_ALPHA)
	_box(_trail_root, (a0 + b0) * 0.5 + lat, Vector3(flat, LANE_T, TRAIL_W), m).rotation.y = _heading(d, 0.0)
	_cyl(_trail_root, b0 + lat, TRAIL_DOT_R, LANE_T * 1.5, HEX, m)
	if _trail_arrow.has(line):
		var old: Node3D = _trail_arrow[line]
		if is_instance_valid(old):
			old.queue_free()
	var am := _mat_live(col, E_TRAIL, TRAIL_ALPHA)
	_trail_arrow[line] = _chevron(_trail_root, b0 + lat + d.normalized() * ARROW_L * 0.6, d.normalized(), am)
	_trail_add([m, am])


func _mark_hit(cell: Vector2i, type: String) -> void:
	var m := _mat_live(_type_col(type), E_TRAIL, TRAIL_ALPHA)
	_torus(_trail_root, _grid_world(cell) + Vector3(0.0, RING_Y, 0.0), HIT_MARK_R.x, HIT_MARK_R.y, HEX, m)
	var n := int(_hit_count.get(cell, 0))
	_hit_count[cell] = n + 1
	_shape(_trail_root, _grid_world(cell) + HIT_GLYPH_POS + HIT_GLYPH_STEP * float(n), type, HIT_GLYPH_S, m)
	_trail_add([m])


## A block: a type-colored shield dome over the sentry and a bar across the lane where the line stopped.
func _mark_block(cell: Vector2i, type: String, dir: Vector3) -> void:
	var col := _type_col(type)
	var dm := _mat_live(col, E_FX, BLOCK_ALPHA)
	var dome := _sphere(_trail_root, _grid_world(cell), BLOCK_DOME_R, dm)
	dome.scale = Vector3(1.0, BLOCK_DOME_FLAT, 1.0)
	var bm := _mat_live(col, E_TRAIL, TRAIL_ALPHA)
	var flat := Vector3(dir.x, 0.0, dir.z)
	if flat.length() > EPS:
		var d := flat.normalized()
		var holder := Node3D.new()
		holder.position = _grid_world(cell) - d * BLOCK_BAR_BACK + Vector3(0.0, TRAIL_Y + BLOCK_BAR.y * 0.5, 0.0)
		holder.rotation.y = _heading(d, 0.0)
		_trail_root.add_child(holder)
		_box(holder, Vector3.ZERO, BLOCK_BAR, bm)
	_trail_add([dm, bm])


func _mark_home() -> void:
	var m := _mat_live(RED, E_TRAIL, TRAIL_ALPHA)
	_torus(_trail_root, _home_world() + Vector3(0.0, HQ_PLAT.y + RING_Y, 0.0), HOME_MARK_R.x, HOME_MARK_R.y, CIRCLE_SEGS, m)
	_trail_add([m])


func _mark_turn(cell: Vector2i) -> void:
	var m := _mat_live(COBALT_HOT, E_TRAIL, TRAIL_ALPHA)
	_torus(_trail_root, _grid_world(cell) + Vector3(0.0, RING_Y, 0.0), TURN_MARK_R.x, TURN_MARK_R.y, CIRCLE_SEGS, m)
	_trail_add([m])


func _mark_jam(pos: Vector3) -> void:
	var m := _mat_live(RED, E_TRAIL, TRAIL_ALPHA)
	var holder := _facing(_trail_root, pos + Vector3(0.0, JAM_MARK_Y, 0.0))
	for s: float in [1.0, -1.0]:
		_box(holder, Vector3.ZERO, JAM_MARK, m).rotation.z = s * PI * 0.25
	_trail_add([m])


func _clear_trails() -> void:
	for ch in _trail_root.get_children():
		ch.queue_free()
	_trail_fade.clear()
	_trail_arrow.clear()
	_lane.clear()
	_road_use.clear()
	_hit_count.clear()


## Vehicles, effects, shakes, candidates and trails go; planned paths and crack decals stay.
func _reset_motion() -> void:
	for v: Dictionary in _vehicles.values():
		(v["node"] as Node3D).queue_free()
	_vehicles.clear()
	_clear_fx()
	_clear_candidates()
	_clear_trails()
	_cand_real = -1
	_shakes.clear()
	_playing = false
	for c: Vector2i in _cell_root:
		(_cell_root[c] as Node3D).position = _grid_world(c)
	if _home_root != null:
		_home_root.position = _home_world()


# ======================= vehicles, the hound, the candidates =======================
## A beam vehicle in its type color and shape, or the hunter: the cobalt hound (glowing eyes, running legs) with a
## cobalt halo and a small type badge.
func _make_vehicle(type: String, hunter: bool, alpha: float) -> Dictionary:
	var root := Node3D.new()
	_fx_root.add_child(root)
	var col: Color = HUNTER_BODY if hunter else _type_col(type)
	var m := _mat_live(col, E_HUNTER if hunter else E_VEH, alpha)
	var mats: Array = [m]
	var parts: Array = []
	var faces: Array = []
	var base_y := 0.0 if hunter else VEH_Y
	if hunter:
		var eye := _mat_live(HUNTER_EYE, E_EYE, alpha)
		mats.append(eye)
		parts = _build_hound(root, m, eye)
		var bm := _mat_live(_type_col(type), E_VEH, alpha)
		mats.append(bm)
		faces.append(_badge(root, Vector3(0.0, HUNTER_BADGE_Y, 0.0), type, HUNTER_BADGE_S, bm))
	else:
		match type:
			"D":
				for i in range(DRONE_N):
					var a := TAU * float(i) / float(DRONE_N)
					var hd := _shape(root, Vector3(cos(a) * DRONE_SPREAD, 0.0, sin(a) * DRONE_SPREAD), "D", DRONE_S, m)
					parts.append(hd)
					faces.append(hd)
			"N":
				for i in range(WORM_N):
					parts.append(_sphere(root, Vector3(-WORM_STEP * i, 0.0, 0.0), WORM_R * (1.0 - WORM_TAPER * i), m))
			_:
				for i in range(CONVOY_N):
					parts.append(_box(root, Vector3(-CONVOY_STEP * i, 0.0, 0.0), CONVOY_BOX, m))
		faces.append(_shape(root, Vector3(0.0, VEH_GLYPH_Y - VEH_Y, 0.0), type, VEH_GLYPH_S, m))
	for p: Node3D in parts:
		p.set_meta("base", p.position)
	var halo_col: Color = HUNTER_TRAIL if hunter else col
	var halo := _mat_live(halo_col, E_VEH * HALO_E_K, alpha * HALO_ALPHA)
	mats.append(halo)
	_torus(root, Vector3(0.0, RING_Y - base_y, 0.0), HALO.x, HALO.y, CIRCLE_SEGS, halo)
	return {"node": root, "mats": mats, "parts": parts, "faces": faces, "hunter": hunter, "type": type,
		"from": Vector3.ZERO, "to": Vector3.ZERO, "rot_from": 0.0, "rot_to": 0.0, "turn_k": TURN_FAST}


func _heading(d: Vector3, fallback: float) -> float:
	if Vector2(d.x, d.z).length() < EPS:
		return fallback
	return atan2(-d.z, d.x)


## Where a new beam vehicle enters: a little back along its line (the cue's optional "from" cell, else read ahead in the
## queue), else it drops from the sky.
func _entry_point(line: int, cell: Vector2i) -> Vector3:
	var step := Vector2i.ZERO
	if _qi >= 0 and _qi < _queue.size():
		var cur: Dictionary = _queue[_qi]
		var fv: Variant = cur.get("from", null)
		if fv is Vector2i:
			var fc: Vector2i = fv
			step = Vector2i(signi(cell.x - fc.x), signi(cell.y - fc.y))
	if step == Vector2i.ZERO:
		for j in range(_qi + 1, _queue.size()):
			var q: Dictionary = _queue[j]
			var kind := str(q.get("kind", ""))
			if int(q.get("line", NO_LINE)) != line or not MOVE_KINDS.has(kind):
				continue
			var nc: Vector2i = q.get("cell", cell)
			if kind == "home":
				nc = Vector2i(-1, cell.y)
			if nc != cell:
				step = Vector2i(signi(nc.x - cell.x), signi(nc.y - cell.y))
				break
	if step == Vector2i.ZERO:
		return _world(cell, false) + Vector3(0.0, SPAWN_DROP, 0.0)
	return _world(cell, false) - Vector3(step.x * CELL_DX * ENTRY_ROUTE_K, 0.0, step.y * CELL_DZ * ENTRY_STREET_K)


func _vehicle_for(line: int, type: String, hunter: bool, cell: Vector2i, drop_at: Vector3) -> Dictionary:
	if _vehicles.has(line):
		var old: Dictionary = _vehicles[line]
		if bool(old["hunter"]) or not hunter:
			return old
		_kill_vehicle(line)
	var entry: Vector3 = (drop_at + Vector3(0.0, SPAWN_DROP, 0.0)) if hunter else _entry_point(line, cell)
	if not hunter and _cand_real >= 0:
		for cv: Dictionary in _cands:
			if int(cv["route"]) == _cand_real and cell == Vector2i(_w - 1, _cand_real):
				entry = (cv["node"] as Node3D).position
		_clear_candidates()
		_cand_real = -1
	var v := _make_vehicle(type, hunter, 1.0)
	var n: Node3D = v["node"]
	n.position = entry
	var target: Vector3 = drop_at if hunter else _world(cell, false)
	n.rotation.y = _heading(target - entry, HEADING_HOME)
	_vehicles[line] = v
	return v


func _aim(v: Dictionary, target: Vector3) -> void:
	var n: Node3D = v["node"]
	v["from"] = n.position
	v["to"] = target
	v["rot_from"] = n.rotation.y
	v["rot_to"] = _heading(target - n.position, n.rotation.y)
	v["turn_k"] = TURN_FAST


func _kill_vehicle(line: int) -> void:
	if not _vehicles.has(line):
		return
	var v: Dictionary = _vehicles[line]
	_vehicles.erase(line)
	_fx_add(v["node"], "fade", FX_FADE_T, v["mats"])


func _clear_candidates() -> void:
	for cv: Dictionary in _cands:
		(cv["node"] as Node3D).queue_free()
	_cands.clear()


## 0 = all three sealed and ghosted; 1 = two dissolved, the real one lit.
func _apply_reveal(u: float) -> void:
	for cv: Dictionary in _cands:
		var n: Node3D = cv["node"]
		if _cand_real < 0:
			_tint(cv["mats"], 1.0, 1.0)
			n.scale = Vector3.ONE
			n.visible = true
		elif int(cv["route"]) == _cand_real:
			_tint(cv["mats"], lerpf(1.0, 1.0 / CAND_ALPHA, u), lerpf(1.0, E_CAND_LIT / E_VEH, u))
		else:
			_tint(cv["mats"], 1.0 - u, 1.0 - u)
			n.scale = Vector3.ONE * lerpf(1.0, CAND_SHRINK, u)
			n.visible = u < 1.0


func _face_all() -> void:
	var all: Array = _vehicles.values() + _cands
	for v: Dictionary in all:
		for f: Node3D in v["faces"]:
			if f.is_inside_tree():
				f.global_rotation = Vector3(_tilt, _yaw, 0.0)


# ======================= the fall beat =======================
## Start the fall: the tower's materials swap to dark red bodies and hot red edges, the light turns red, every HOME
## pip goes red, the lethal mark goes, and a red ring and dome burst from the platform.
func _start_fall() -> void:
	if _home_root == null or not is_instance_valid(_home_tower):
		return
	_fallen = true
	_lethal = false
	if _fall_mats.is_empty():
		var hot := _mat_live(RED, E_FALL)
		_fall_mats = [hot]
		var body := _solid(FALL_BODY)
		for n: Node in _home_tower.find_children("*", "MeshInstance3D", true, false):
			var mi := n as MeshInstance3D
			var old := mi.material_override as StandardMaterial3D
			mi.material_override = hot if old != null and old.emission_enabled else body
	if is_instance_valid(_home_light):
		_home_light.light_color = RED
	_home_hp = 0
	_refresh_lethal()
	_fx_ring(_home_world(), RED, GHOST_HOME_R * FALL_RING_K)
	var m := _mat_live(RED, E_FX, HALO_ALPHA)
	_fx_add(_sphere(_fx_root, _home_world() + Vector3(0.0, HQ_PLAT.y, 0.0), 1.0, m), "pulse", T_FALL, [m], {"r": FALL_PULSE_K})


## The collapse at progress u: the tower squashes, spreads and tilts, the pips drop with it, the red edges flash then
## settle, the HQ shakes (not in instant), and at the end a red skull stands over the rubble.
func _apply_fall(u: float) -> void:
	if not _fallen or not is_instance_valid(_home_tower):
		return
	var k := clampf(u, 0.0, 1.0)
	var e := k * k
	var spread := 1.0 + FALL_SPREAD * e
	_home_tower.scale = Vector3(spread, lerpf(1.0, FALL_SCALE_Y, e), spread)
	_home_tower.rotation.z = FALL_TILT * e
	if is_instance_valid(_home_pip_holder):
		_home_pip_holder.position.y = lerpf(_pip_top(), FALL_PIP_Y, e)
	_tint(_fall_mats, 1.0, 1.0 + FALL_FLASH * (1.0 - k))
	if not _instant and k < FALL_SHAKE_U:
		_shakes["HOME"] = SHAKE_T * (1.0 - k / FALL_SHAKE_U)
	if k >= 1.0 and not is_instance_valid(_fall_skull):
		_fall_skull = _skull(_home_root, Vector3(0.0, FALL_SKULL_Y, 0.0) + _cam_back() * SKULL_FWD, FALL_SKULL_S, _mat(RED, E_LETHAL))


# ======================= cue playback =======================
func _cue_dur_of(kind: String) -> float:
	match kind:
		"block":
			return T_BLOCK
		"hit":
			return T_HIT
		"home":
			return T_HOME
		"hunter_turn":
			return T_TURN
		"jam":
			return T_JAM
		"reveal":
			return T_REVEAL
		"evaded":
			return T_EVADED
		"decay":
			return T_DECAY
		"fall":
			return T_FALL
	return T_STEP


func _next_cue() -> void:
	_qi += 1
	if _qi >= _queue.size():
		_playing = false
		_cur_cue = {}
		call_deferred("_emit_finished")
		return
	_cur_cue = _queue[_qi]
	_cue_t = 0.0
	_cue_dur = _cue_dur_of(str(_cur_cue.get("kind", "")))
	_start_cue(_cur_cue)


func _finish_instant() -> void:
	for i in range(_qi + 1, _queue.size()):
		_qi = i
		_cur_cue = _queue[i]
		_start_cue(_cur_cue)
		_settle_cue(_cur_cue)
	_qi = _queue.size()
	_cur_cue = {}
	_playing = false
	_face_all()
	call_deferred("_emit_finished")


func _emit_finished() -> void:
	cues_finished.emit()


func _start_cue(cue: Dictionary) -> void:
	var kind := str(cue.get("kind", ""))
	var cell: Vector2i = cue.get("cell", NO_CELL)
	var type := str(cue.get("type", "D"))
	var line := int(cue.get("line", 0))
	_cur_line = NO_LINE
	match kind:
		"beam_step", "hit", "block":
			var v := _vehicle_for(line, type, false, cell, Vector3.ZERO)
			var hunter := bool(v["hunter"])
			_aim(v, _world(cell, hunter))
			_cur_line = line
			var a: Vector3 = v["from"]
			var b: Vector3 = v["to"]
			_trail_seg(line, a, b, HUNTER_TRAIL if hunter else _type_col(type))
			if kind == "hit":
				_cracked[cell] = true
				_fx_strike(cell, type)
				_shakes[cell] = SHAKE_T
				_mark_hit(cell, type)
			elif kind == "block":
				_fx_shield(cell, type)
				_mark_block(cell, type, b - a)
		"home":
			var row := cell.y
			var v := _vehicle_for(line, type, false, Vector2i(-1, row), Vector3.ZERO)
			_aim(v, _home_entry(row))
			_cur_line = line
			_trail_seg(line, v["from"] as Vector3, v["to"] as Vector3, _type_col(type))
			_mark_home()
		"hunter_turn", "jam":
			var head := _street_head(cell.x)
			var v := _vehicle_for(line, type, true, cell, head)
			_aim(v, head)
			_cur_line = line
			_mark_turn(cell)
			if kind == "hunter_turn":
				v["rot_to"] = HEADING_DOWN
				v["turn_k"] = 1.0
			else:
				_fx_slash(head)
				_mark_jam(head)
		"reveal":
			if line >= 0:
				_cand_real = line
		"evaded":
			_fx_label(_board_text("EVADED", SCRAMBLE_FX), Vector3(0.0, LABEL_Y, 0.0), ACID, LABEL_BIG)
		"decay":
			if _cell_root.has(cell):
				_status[cell] = "TAKEN"
				_sentries.erase(cell)
				_refresh_cell(cell)
				_fx_pulse(cell)
		"fall":
			_start_fall()
	if _instant:
		_update_cue(1.0)


func _update_cue(u: float) -> void:
	if _cur_line != NO_LINE and _vehicles.has(_cur_line):
		var v: Dictionary = _vehicles[_cur_line]
		var n: Node3D = v["node"]
		n.position = (v["from"] as Vector3).lerp(v["to"], _ease_out(u))
		n.rotation.y = lerp_angle(float(v["rot_from"]), float(v["rot_to"]), minf(1.0, u * float(v["turn_k"])))
	var kind := str(_cur_cue.get("kind", ""))
	if kind == "reveal":
		_apply_reveal(u)
	elif kind == "fall":
		_apply_fall(u)


func _settle_cue(cue: Dictionary) -> void:
	if cue.is_empty():
		return
	_update_cue(1.0)
	var kind := str(cue.get("kind", ""))
	var cell: Vector2i = cue.get("cell", NO_CELL)
	var line := int(cue.get("line", 0))
	match kind:
		"hit":
			_advance_status(cell)
		"block", "jam":
			_kill_vehicle(line)
		"home":
			_home_impact()
			_kill_vehicle(line)


func _advance_status(c: Vector2i) -> void:
	match str(_status.get(c, "NEUTRAL")):
		"OK":
			_status[c] = "DOWN"
		"DOWN":
			_status[c] = "TAKEN"
			_sentries.erase(c)
	_refresh_cell(c)


func _home_impact() -> void:
	_home_hp = maxi(0, _home_hp - 1)
	_refresh_pips()
	_shakes["HOME"] = SHAKE_T
	_fx_label("-1", _home_world() + Vector3(0.0, HOME_LABEL_Y, 0.0), RED, LABEL_BIG)
	_fx_ring(_home_world(), RED, GHOST_HOME_R)


# ======================= effects =======================
func _fx_add(node: Node3D, kind: String, dur: float, mats: Array, extra: Dictionary = {}) -> void:
	var f := {"node": node, "kind": kind, "t": 0.0, "dur": dur, "mats": mats, "base": node.position}
	f.merge(extra)
	_fx.append(f)
	_fx_apply(f, SETTLE_U if _instant else 0.0)


func _fx_apply(f: Dictionary, u: float) -> void:
	var n: Node3D = f["node"]
	var k := 1.0 - u
	var e := _ease_out(u)
	match str(f["kind"]):
		"shield":
			n.scale = Vector3.ONE * lerpf(SHIELD_R.x, SHIELD_R.y, e)
		"ring":
			var s := lerpf(FLASH_R.x, FLASH_R.y, e) * float(f.get("r", 1.0))
			n.scale = Vector3(s, RING_FLAT, s)
		"pulse":
			var s := lerpf(PULSE_R.x, PULSE_R.y, e) * float(f.get("r", 1.0))
			n.scale = Vector3(s, s * BLOCK_DOME_FLAT, s)
		"strike":
			n.scale = Vector3(STRIKE.x * k, STRIKE.y, STRIKE.z * k)
		"label":
			var l := n as Label3D
			l.modulate.a = k
			l.position = (f["base"] as Vector3) + Vector3(0.0, LABEL_RISE * e, 0.0)
	_tint(f["mats"], k, 1.0)


func _fx_shield(cell: Vector2i, type: String) -> void:
	var col := _type_col(type)
	var m := _mat_live(col, E_FX, HALO_ALPHA)
	_fx_add(_sphere(_fx_root, _world(cell, false), 1.0, m), "shield", FX_SHIELD_T, [m])
	_fx_ring(_grid_world(cell), col, 1.0)


func _fx_strike(cell: Vector2i, type: String) -> void:
	var col := _type_col(type)
	var m := _mat_live(col, E_FX)
	_fx_add(_box(_fx_root, _grid_world(cell) + Vector3(0.0, STRIKE.y * 0.5, 0.0), STRIKE, m), "strike", FX_STRIKE_T, [m])
	_fx_ring(_grid_world(cell), col, 1.0)


## Decay: a cobalt dome swells over the district with a cobalt ring and a small shake.
func _fx_pulse(cell: Vector2i) -> void:
	var m := _mat_live(COBALT, E_FX, HALO_ALPHA)
	_fx_add(_sphere(_fx_root, _grid_world(cell) + Vector3(0.0, RING_Y, 0.0), 1.0, m), "pulse", T_DECAY, [m])
	_fx_ring(_grid_world(cell), COBALT_HOT, 1.0)
	_shakes[cell] = SHAKE_T


func _fx_ring(pos: Vector3, col: Color, r: float) -> void:
	var m := _mat_live(col, E_FX)
	var t := _torus(_fx_root, pos + Vector3(0.0, RING_Y * 2.0, 0.0), 1.0 - FX_RING_T, 1.0, HEX, m)
	_fx_add(t, "ring", FX_RING_TIME, [m], {"r": r})


func _fx_slash(pos: Vector3) -> void:
	var m := _mat_live(RED, E_FX)
	var holder := _facing(_fx_root, pos + Vector3(0.0, SLASH_Y, 0.0))
	_box(holder, Vector3.ZERO, SLASH, m).rotation.z = SLASH_ROT
	_fx_add(holder, "slash", T_JAM + FX_FADE_T, [m])


func _fx_label(text: String, pos: Vector3, col: Color, size: int) -> void:
	var l := _label(_fx_root, text, pos, col, size)
	_fx_add(l, "label", FX_LABEL_T, [])


func _clear_fx() -> void:
	for f: Dictionary in _fx:
		var n: Node3D = f["node"]
		if is_instance_valid(n):
			n.queue_free()
	_fx.clear()


## Cap the glow while an impact effect (strike, shield, ring, pulse) is alive, so the impact reads as a shape.
func _cap_glow() -> void:
	if _env == null:
		return
	var impact := false
	for f: Dictionary in _fx:
		if IMPACT_FX.has(str(f["kind"])) and is_instance_valid(f["node"]):
			impact = true
			break
	_env.glow_intensity = GLOW_INTENSITY * (GLOW_IMPACT_K if impact else 1.0)


# ======================= the frame =======================
func _process(delta: float) -> void:
	if not _instant:
		_time += delta
		var dt := delta * _speed
		if _playing:
			_cue_t += dt
			_update_cue(clampf(_cue_t / maxf(_cue_dur, EPS), 0.0, 1.0))
			if _cue_t >= _cue_dur:
				_settle_cue(_cur_cue)
				_next_cue()
		_step_fx(dt)
		_step_trails(dt)
		_step_shakes(dt)
		_animate(delta)
	_face_all()
	_cap_glow()


func _step_fx(dt: float) -> void:
	var keep: Array = []
	for f: Dictionary in _fx:
		var n: Node3D = f["node"]
		if not is_instance_valid(n):
			continue
		f["t"] = float(f["t"]) + dt
		var u := float(f["t"]) / float(f["dur"])
		if u >= 1.0:
			n.queue_free()
			continue
		_fx_apply(f, u)
		keep.append(f)
	_fx = keep


func _step_shakes(dt: float) -> void:
	for k: Variant in _shakes.keys():
		var left := float(_shakes[k]) - dt
		var base := _home_world() if k is String else _grid_world(k as Vector2i)
		var root: Node3D = _home_root if k is String else _cell_root.get(k, null)
		if left <= 0.0:
			_shakes.erase(k)
			if root != null:
				root.position = base
			continue
		_shakes[k] = left
		if root != null:
			var amp := SHAKE_AMP * left / SHAKE_T
			root.position = base + Vector3(sin(_time * SHAKE_HZ) * amp, 0.0, cos(_time * SHAKE_HZ * GLYPH_TILT) * amp)


func _animate(delta: float) -> void:
	var all: Array = _vehicles.values() + _cands
	var gait := sin(_time * GAIT_HZ * TAU) * GAIT_AMP
	for v: Dictionary in all:
		var parts: Array = v["parts"]
		var hunter := bool(v["hunter"])
		for i in range(parts.size()):
			var p: Node3D = parts[i]
			var base: Vector3 = p.get_meta("base", p.position)
			if hunter:
				p.position = base + Vector3(gait * float(p.get_meta("gait", 0.0)), 0.0, 0.0)
				continue
			var ph := _time * BOB_HZ * TAU + i
			match str(v["type"]):
				"N":
					p.position = base + Vector3(0.0, 0.0, sin(ph) * WIGGLE_AMP)
				_:
					p.position = base + Vector3(0.0, sin(ph) * BOB_AMP, 0.0)
	var live: Array = []
	for s: Variant in _spin:
		if is_instance_valid(s):
			(s as Node3D).rotation.y += GHOST_SPIN * delta
			live.append(s)
	_spin = live
	var ep := lerpf(EYE_LOW, 1.0, 0.5 + 0.5 * sin(_time * EYE_HZ * TAU)) * (RESP_JAM_DIM if _resp_dimmed else 1.0)
	var live_eyes: Array = []
	for e: Dictionary in _eyes:
		if is_instance_valid(e["node"]):
			(e["mat"] as StandardMaterial3D).emission_energy_multiplier = E_EYE * ep
			live_eyes.append(e)
	_eyes = live_eyes
	for c: Vector2i in _win_mats:
		if str(_status.get(c, "")) != "DOWN":
			continue
		var n := sin(float(floori(_time * FLICKER_HZ)) * HASH_A + c.x * HASH_B + c.y * HASH_C) * HASH_D
		var on := n - floorf(n) > FLICKER_ON
		(_win_mats[c] as StandardMaterial3D).emission_energy_multiplier = E_WIN_DOWN * (1.0 if on else FLICKER_LOW)
	var pulse := 1.0 - HL_PULSE + HL_PULSE * sin(_time * HL_HZ * TAU)
	_tint(_hl, pulse, pulse)
	if not _path_pulse.is_empty():
		_tint(_path_pulse, 1.0, 1.0 + PATH_PULSE * sin(_time * PATH_PULSE_HZ * TAU))
	if not _resp_mats.is_empty():
		_tint(_resp_mats, 1.0, 1.0 - RESP_PULSE + RESP_PULSE * sin(_time * HL_HZ * TAU))
	if _lethal and not _lethal_mats.is_empty():
		var lp := 0.5 + 0.5 * sin(_time * LETHAL_HZ * TAU)
		_tint(_lethal_mats, 1.0, lerpf(LETHAL_LOW, 1.0, lp))
		if is_instance_valid(_lethal_root):
			_lethal_root.scale = Vector3.ONE * LETHAL_SKULL_S * (1.0 + LETHAL_GROW * lp)
