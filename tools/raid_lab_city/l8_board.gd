class_name L8Board
extends Node3D
## The city view of raid lab L8 (SPEC section 8, with the L9-L12 presentation changes, the L13 UI, the L14 UI, the
## L15 UI, the L16 UI and the L17 UI). It shows a dark slab city block in iso with a long lens. Our amber HQ sits on the
## left and the cobalt corp HQ on the right. Three lit routes and four gray cross streets run between them. Large
## NORTH / MID / SOUTH labels sit at the corp end of the routes, and street numbers 0-3 sit at the north edge.
## Districts are small building clusters with rings, value pips and exploit keys. The board also draws:
## - sentries, the ghost and the sealed candidates. L13: the three candidates share one "?" glyph, tethered to each,
##   that collapses into the real one at the reveal;
## - typed vehicles that travel the lines;
## - the hunter: a cobalt hound silhouette with glowing eyes and a small type badge. L13: its two sealed streets are
##   dashed hound lanes with a pawprint and a "?" badge, the hound standing between them (show_hunter_cands). At the
##   HUNTER REVEAL (hunter_reveal) one lane ignites, the other dissolves and the hound steps to its head, then runs it;
## - planned paths (L12): known beams as solid lanes at full strength, the selected candidate dashed at full strength
##   with a pulse, other candidates at 15% alpha with no arrowheads. While paths are shown, cross streets that no line
##   uses are hidden;
## - the playout's trails;
## - a forecast outcome overlay (crack, shield, skull and hunter path glyphs);
## - route verdicts (L12, moved by L13): per sealed route, the tier glyph at the lane's corp-side entry. They stay
##   through the launch until hide_route_verdicts();
## - district marks (L12): a cobalt "1" countdown ring next to the wrench of every DOWN district (TAKEN next raid), and
##   a crack decal on a district hit this raid that is OK again (until the next raid);
## - a response preview: an arc arrow in the sentry's type color from the source (a sentry, or the reserve tray at our
##   HQ) to the target cell for REDEPLOY / DEPLOY, a red cross over the hound for JAM, and (L13) for SACRIFICE the cell
##   crumbling under a cobalt veil with a shield dome over our HQ;
## - L13 Heat ghosts: one ghost beam on the corp tower per extra beam the current Heat brings, plus a faint one for the
##   next threshold (set_heat_ghosts). L15: each ghost carries two small icons, a beam "+1" and a card "+1";
## - decay beats, where a cell left DOWN flips to cobalt TAKEN with a pulse;
## - the decided fall beat: our HQ tower turns red and collapses, with a red skull over the rubble;
## - highlights by meaning: an amber plus (capture), a red wrench outline (repair), a white check ring (picked) and
##   (L14) a gold double edge (gold, the SCAN's pick or a Heat-dealt card);
## - the lethal mark: at HOME 1/3 the last HOME pip pulses red and a red skull pulses on our HQ tower.
## L14 additions (all additive):
## - card sentries: show_state accepts {cell: card_id} sentries plus a card lookup (the state's deck, or `cards`); each
##   sentry keeps its card's verb glyph (GUARD shield, SHIFT curved arrow, JAM zigzag) on a small disc beside its type
##   shape, and the cards listed in place.gold get a gold edge;
## - wound_fly: a cracked gray card flies from a district to a screen point (the lab's deck strip);
## - the second sealed beam: show_b_cands / reveal_b, and a sealed_b beam spawns from the lit B convoy;
## - set_fit_free: the free screen area the camera fills (room for the hand row and the deck strip).
## L15 additions (all additive):
## - playout clarity: only the current beam's trail is at full strength; DONE beams dim to 25% alpha with thin lines
##   (automatically when another beam starts moving, or with set_beam_done). Block markers and hit glyph stacks are
##   drawn only for the current beam; every hit cell keeps a small red X for the rest of the raid;
## - the hunter candidate streets fade once the hunter is revealed and runs (the dissolved street is no longer kept);
## - home glyphs: per route, the worst tier glyph at the route's lane end at our HQ (show_home_glyphs).
## L16 additions (all additive):
## - glyph-first response previews: preview_response(kind, a, b) draws a row's effect (SACRIFICE: a shield dome on HOME
##   and a cobalt crumble on the cell; REDEPLOY: a ghost arrow from the source to the target; DEPLOY: a ghost sentry
##   dropping in; JAM: a struck-out hound on the hunter lanes);
## - five distinct tier shapes, shared everywhere: HOLDS = full shield, BATTERED = cracked shield, DAMAGED = broken
##   heart, BREACHED = skull, EVADED = open eye. The 3D board glyphs and the 2D icon (static tier_icon, tier_color,
##   tier_ladder ordered best to worst) draw the same shapes;
## - set_view_rect: the camera fits a wider (or narrower) screen rect, for the playout's collapsed side panel;
## - set_fan: stacked sentries, wrenches and outcome glyphs on one district fan out around the cell center.
## L17 additions (all additive):
## - the forecast on the board: show_outcome_ghost(beams, fallen, home_lost, tier) draws one outcome as a ghost overlay
##   (the beams it fires as thin ghost lines, the districts going DOWN or TAKEN as a ghost crumble tint, the HOME pips
##   lost as ghost pips, and a large tier glyph over our HQ); clear_outcome_ghost() removes it;
## - card verbs on the board: a placed SHIFT or JAM sentry shows its verb glyph larger than a GUARD sentry does.
## Everything is built in code, and it runs inside a SubViewport that the main scene creates. It holds no rule. The lab
## hands it the leg (`setup`), the state (`show_state`), planned lines (`show_paths`), an outcome (`show_outcome`,
## `show_outcome_ghost`), route verdicts (`show_route_verdicts`), home glyphs (`show_home_glyphs`), the hunter streets
## (`show_hunter_cands`), the B routes (`show_b_cands`), a response preview (`show_response_preview`,
## `preview_response`), the Heat ghosts (`set_heat_ghosts`) and a playout's cues (`play`, `hunter_reveal`, `reveal_b`,
## `decay`, `show_fall`, `wound_fly`); the board only draws them. `set_scramble` swaps the board labels for seeded
## noise. The camera is fitted to the board's real geometry (slab, HQ towers, labels) so it fills the free area left
## of the side panel, with no dark sky margin; the starfield is dimmed. Glow is capped while impacts flash, so hits
## read as shapes. Cosmetic motion is seeded or time-based, never global random.

signal cues_finished

## L14: the handle behind wound_fly's signal; `done` fires once that card has landed (or was cleared).
class WoundFlight extends RefCounted:
	signal done

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
## L12 route verdicts: the color of a held route (HOLDS). L13: also the SACRIFICE shield over our HQ.
const HOLD_COL := Color8(70, 235, 160)
## L16 tier colors besides HOLD_COL (HOLDS), AMBER (BATTERED) and RED (BREACHED).
const EVADE_COL := Color8(170, 255, 120)
const DAMAGE_COL := Color8(255, 118, 60)
## L14 wound cards: a cracked gray card body and its lighter edge.
const WOUND_COL := Color8(82, 86, 98)
const WOUND_EDGE_COL := Color8(160, 166, 182)

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
## L14: verb glyphs, gold edges and wound cards (the card body stays below the glow threshold).
const E_VERB := 2.0
const E_GOLD := 2.4
const E_WOUND := 0.9
const E_WOUND_EDGE := 1.2
## L15: the small persistent X on a hit cell.
const E_HIT_X := 2.0
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
## The reference viewport and the default free board area in it: left of the 420 px panel, between the HUD and the
## legend. L14: set_fit_free replaces the free area (for example to leave room for the hand row). L16: set_view_rect
## overrides both while set (the playout's wide view).
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
## Layer heights above the roads: cell decals, crack decals, planned paths, hunter lanes, outcome paths, B candidate
## lanes, playout trails, highlights.
const DECAL_Y := 0.045
const DECAL_T := 0.006
const CRACK_DECAL_Y := 0.055
const PATH_Y := 0.06
const HUNT_Y := 0.065
const OUT_PATH_Y := 0.07
const B_LANE_Y := 0.075
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
const SCRAMBLE_TAG := 950
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

## L16 fan (set_fan): offsets around the cell center for the stacked markers of one district. The sentry moves
## front-left, the wrench and its countdown back-left, the forecast outcome glyphs right (several on one cell spread
## on a small ring around FAN_OUT_SOLO).
const FAN_SENTRY := Vector3(-0.4, 0.0, 0.42)
const FAN_WRENCH := Vector3(-0.5, 0.0, -0.45)
const FAN_OUT_SOLO := Vector3(0.45, 0.0, -0.1)
const FAN_OUT_R := 0.5
const FAN_OUT_A0 := -PI * 0.5

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
## L14: a gold edge ring outside the sentry decal (a card in place.gold).
const SENTRY_GOLD := Vector2(0.64, 0.72)
## L14 verb glyphs: a small dark disc right of the sentry's type shape (in its facing plane), holding the verb glyph
## drawn in local units scaled by VERB_S. GUARD = shield, SHIFT = curved arrow (an arc over the top ending in a
## downward head), JAM = zigzag.
const VERB_POS := Vector2(0.42, -0.04)
const VERB_Z := 0.02
const VERB_BACK_R := 0.17
const VERB_GOLD_R := Vector2(0.17, 0.2)
const VERB_S := 0.42
## L17: the verb badge's scale by verb, so a held tool (SHIFT, JAM) reads larger than a plain GUARD. The badge moves
## out by its growth so it stays clear of the type shape.
const VERB_SIZE := {"GUARD": 1.0, "SHIFT": 1.7, "JAM": 1.7}
const VERB_LINE_W := 0.11
const VERB_SHIELD_DY := 0.07
const SHIFT_SEGS := 8
const SHIFT_C := Vector2(0.0, -0.06)
const SHIFT_R := 0.26
const SHIFT_A := Vector2(PI * 1.05, -PI * 0.05)
const SHIFT_TIP := 0.04
const SHIFT_HEAD_L := 0.16
const SHIFT_HEAD_ANG := 0.65
const JAM_PTS := [Vector2(-0.3, -0.12), Vector2(-0.15, 0.14), Vector2(0.0, -0.12), Vector2(0.15, 0.14), Vector2(0.3, -0.12)]
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
## L13: the sealed candidates wait on the corp platform's edge (fraction of a cell past the last district), so the
## route verdicts fit between them and the districts.
const CAND_DX := 0.64
const CAND_ALPHA := 0.32
const CAND_SHRINK := 0.2
## L13: the shared "?" over the three sealed candidates (raised, pushed toward the camera), tethered to each one.
const CQ_Y := 1.75
const CQ_FWD := 0.3
const CQ_S := 1.2
const CQ_TETHER_W := 0.03
const CQ_TETHER_A := 0.5
const CQ_TETHER_TOP := 0.3
const CQ_TETHER_BOT := 0.22
## A "?" glyph: a billboard "?" on a dark disc (the scramble never touches "?").
const Q_BACK_R := 0.26
const Q_FONT := 56
const Q_Z := 0.05
const Q_MIN_S := 0.001

## L14 B candidates: the two remaining routes as pulsing dashed lanes in their type color, a ghosted convoy waiting at
## the corp end and a "?" above it. At REVEAL B the real one ignites (lane and convoy lit), the other dissolves and
## both "?" collapse.
const B_LANE_A := 0.5
const B_IGNITE_E := 1.8
const B_PULSE := 0.45
const B_PULSE_HZ := 1.4
const B_Q_DY := 1.15
const B_Q_FWD := 0.25
const B_Q_S := 0.9
const B_RING_K := 0.9

## L13 hunter street candidates: dashed cobalt hound lanes, a pawprint at each lane's head and a "?" badge above it.
## The hound stands between the two heads. At the reveal the real lane ignites (alpha to full, emission up) and the
## other dissolves; both "?" badges collapse and the hound steps to the real head.
const HC_ALPHA := 0.55
const HC_IGNITE_E := 1.9
const HC_PAW_Y := 0.55
const HC_PAW_S := 1.0
const HC_Q_Y := 1.25
const HC_Q_S := 1.0
const HC_RING_K := 0.9
## L15: once the revealed hunter starts its run, its candidate lane fades to this fraction (alpha and emission).
const HC_DONE_K := 0.25
const PAW_BACK_R := 0.27
const PAW_PAD_R := 0.1
const PAW_PAD := Vector2(0.0, -0.06)
const PAW_PAD_SCALE := Vector3(1.25, 1.0, 0.95)
const PAW_TOE_R := 0.045
const PAW_TOES := [Vector2(-0.13, 0.07), Vector2(-0.05, 0.15), Vector2(0.05, 0.15), Vector2(0.13, 0.07)]

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
## Playout trails: solid lanes that fade to a resting glow, plus hit, block, home, turn and jam marks.
const TRAIL_W := 0.14
const TRAIL_DOT_R := 0.12
const TRAIL_MIN := 0.05
const TRAIL_ALPHA := 0.95
const TRAIL_REST := 0.6
const TRAIL_REST_E := 0.55
const TRAIL_FADE_T := 1.6
## L15 DONE beams: their trail drops to this fraction of its alpha (25%) and emission, and its lines thin to DONE_W_K.
const DONE_ALPHA_K := 0.25
const DONE_E_K := 0.35
const DONE_W_K := 0.45
const HIT_MARK_R := Vector2(1.16, 1.25)
const HIT_GLYPH_POS := Vector3(0.95, 0.35, 0.95)
const HIT_GLYPH_STEP := Vector3(-0.34, 0.0, 0.0)
const HIT_GLYPH_S := 0.15
## L15: the small persistent X on every cell hit this raid (front-left of the cell, on a dark disc).
const HIT_X_POS := Vector3(-0.95, 0.35, 0.95)
const HIT_X_BAR := Vector3(0.26, 0.055, 0.04)
const HIT_X_BACK_R := 0.17
const HIT_X_Z := 0.02
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

## Route verdicts (L13: at each lane's corp-side entry, between the last district and the waiting candidate), raised
## and pushed toward the camera, with a ring on the road below. L16: the five tier shapes (see _tier_glyph). The heart
## is a diamond with two lobes; the break is a dark zigzag in front of it.
const VERDICT_DX := 0.36
const VERDICT_Y := 0.95
const VERDICT_FWD := 0.45
const VERDICT_S := 1.15
const VERDICT_SKULL_S := 0.62
const VERDICT_RING_R := Vector2(0.32, 0.4)
const HEART_SQ := 0.26
const HEART_SQ_Y := -0.06
const HEART_LOBE := Vector2(0.092, 0.032)
const HEART_LOBE_R := 0.13
const HEART_BACK_R := 0.3
const HEART_BREAK_W := 0.045
const HEART_BREAK_Z := 0.03
const HEART_BREAK := [Vector2(0.0, 0.17), Vector2(0.05, 0.05), Vector2(-0.04, -0.05), Vector2(0.03, -0.15), Vector2(0.0, -0.26)]
## L16 tier shapes on the board: the shield glyph (scaled to the heart's size), its dark crack (BATTERED), and the open
## eye (EVADED): an almond lens, a dark iris ring and a lit pupil.
const TIER_SHIELD_K := 0.85
const TIER_CRACK := [Vector2(-0.02, 0.24), Vector2(0.07, 0.1), Vector2(-0.06, -0.02), Vector2(0.05, -0.15), Vector2(-0.01, -0.34)]
const EYE_LENS_R := 0.36
const EYE_LENS_FLAT := 0.5
const EYE_IRIS := Vector2(0.1, 0.145)
const EYE_PUPIL_R := 0.075
const EYE_Z := 0.03
## The best-to-worst tier ladder (the legend order).
const TIER_LADDER := ["EVADED", "HOLDS", "BATTERED", "DAMAGED", "BREACHED"]
## L15 home glyphs: each route's worst tier glyph on the road between our HQ platform and the first district (world
## units right of our HQ's center), smaller than the corp-side verdicts.
const HOME_GLYPH_DX := 1.45
const HOME_GLYPH_FWD := 0.35
const HOME_GLYPH_S := 0.95
const HOME_GLYPH_SKULL_S := 0.52

## L17 outcome ghost (show_outcome_ghost): thin translucent beam lines (with a stop bar where a block ends one), a
## crumble tint on the districts that fall (DOWN in damage orange, TAKEN in cobalt: a ground tint, a veil and seeded
## debris lying on the cell), red ghost pips over the HOME pips lost, and a large tier glyph in front of our HQ tower.
## The ghost pulses gently.
const OG_Y := 0.085
const OG_BEAM_W := 0.06
const OG_BEAM_A := 0.5
const E_OG_BEAM := 1.6
const OG_STOP := Vector3(0.06, 0.12, 0.62)
const OG_GLYPH_S := 0.12
const OG_TINT_Y := 0.09
const OG_TINT_A := 0.3
const OG_VEIL_H := 1.1
const OG_VEIL_A := 0.18
const E_OG := 1.4
const OG_DEBRIS_SEED := 1717
const OG_DEBRIS_N := 6
const OG_DEBRIS := 0.13
const OG_DEBRIS_SPREAD := 0.75
const OG_DEBRIS_A := 0.65
const OG_PIP_K := 1.15
const OG_PIP_A := 0.6
const OG_PIP_FWD := 0.08
const E_OG_PIP := 2.4
const OG_TIER_Y := 2.5
const OG_TIER_FWD := 1.7
const OG_TIER_S := 2.1
const OG_TIER_SKULL_S := 1.15
const OG_TIER_RING := Vector2(1.5, 1.62)
const OG_PULSE := 0.25
const OG_HZ := 1.0

## L16 tier icons (tier_icon): square textures rasterized with ICON_SS x ICON_SS supersampling, the shape filling
## ICON_FILL of the square. Shape points in [-1, 1], y up: the shield, its crack, the heart (two lobes and a tip) and
## its break, the skull (head, jaw, eyes, nose, teeth gaps), and the eye (two circles' lens and an iris gap ring).
const ICON_SIZE := 32
const ICON_MIN := 8
const ICON_MAX := 256
const ICON_SS := 3
const ICON_FILL := 0.94
const ICON_CUT_W := 0.075
const ICON_SHIELD := [Vector2(-0.7, 0.8), Vector2(0.7, 0.8), Vector2(0.7, 0.1), Vector2(0.48, -0.42), Vector2(0.0, -0.9), Vector2(-0.48, -0.42), Vector2(-0.7, 0.1)]
const ICON_CRACK := [Vector2(-0.05, 0.9), Vector2(0.14, 0.38), Vector2(-0.14, 0.0), Vector2(0.12, -0.36), Vector2(-0.02, -0.95)]
const ICON_LOBES := [Vector2(-0.36, 0.32), Vector2(0.36, 0.32)]
const ICON_LOBE_R := 0.4
const ICON_HEART_TIP := [Vector2(-0.74, 0.2), Vector2(0.74, 0.2), Vector2(0.0, -0.86)]
const ICON_BREAK := [Vector2(0.0, 0.8), Vector2(0.12, 0.38), Vector2(-0.12, 0.05), Vector2(0.09, -0.3), Vector2(0.0, -0.95)]
const ICON_SKULL_C := Vector2(0.0, 0.18)
const ICON_SKULL_R := 0.64
const ICON_JAW_X := 0.38
const ICON_JAW_Y := Vector2(-0.74, -0.2)
const ICON_EYES := [Vector2(-0.25, 0.12), Vector2(0.25, 0.12)]
const ICON_EYE_R := 0.17
const ICON_NOSE := [Vector2(-0.08, -0.24), Vector2(0.08, -0.24), Vector2(0.0, -0.06)]
const ICON_TEETH_Y := -0.44
const ICON_TEETH_X := [0.0, -0.17, 0.17]
const ICON_TEETH_W := 0.035
const ICON_LENS_C := 0.6
const ICON_LENS_R := 1.0
const ICON_IRIS := Vector2(0.24, 0.34)

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
## L16: the REDEPLOY / DEPLOY arrow is a ghost (this alpha). The DEPLOY ghost sentry drops in from RESP_DROP_H in a
## loop (falling in the first RESP_DROP_FALL of each cycle, then resting); instant shots show it landed. The JAM strike
## also crosses out each live hunter lane's pawprint (scaled by RESP_JAM_LANE_K).
const RESP_ARROW_A := 0.6
const RESP_DROP_H := 1.6
const RESP_DROP_HZ := 0.6
const RESP_DROP_FALL := 0.45
const RESP_JAM_LANE_K := 0.62
const RESP_JAM_LANE_FWD := 0.25
## L13 SACRIFICE preview: a cobalt veil column over the district with seeded cobalt debris falling through it (a
## loop), a cobalt hex ring, and a tall translucent shield dome over our HQ with a shield glyph and a ring.
const SAC_SEED := 1313
const SAC_N := 10
const SAC_CUBE := 0.14
const SAC_VEIL_H := 1.6
const SAC_VEIL_A := 0.22
const SAC_SPREAD := 0.85
const SAC_Y := Vector2(0.5, 1.7)
const SAC_FLOOR_Y := 0.07
const SAC_HZ := 0.7
const SAC_SPIN := 3.0
const SAC_DOME_R := 1.6
const SAC_DOME_STRETCH := 2.4
const SAC_DOME_A := 0.16
const SAC_SHIELD_Y := 2.2
const SAC_SHIELD_FWD := 1.2
const SAC_SHIELD_S := 1.5

## L13 Heat ghosts: floating ghost beams off the corp tower's HOME-facing side, one slot per extra beam, pointing at
## HOME. Active ones are bright and pulse; the faint one marks the next threshold.
const HG_SLOTS := 3
const HG_Y0 := 2.35
const HG_STEP := 0.5
const HG_GAP := 0.08
const HG_LEN := 1.0
const HG_BAR := Vector2(0.08, 0.14)
const HG_ORB_R := 0.09
const HG_A := 0.75
const HG_A_FAINT := 0.18
const E_HG := 2.2
const E_HG_FAINT := 0.6
const HG_PULSE := 0.35
const HG_HZ := 0.9
## L15 tick icons (replacing the L14 "+1 card" tag): above each ghost's tip, a beam icon "+1" and a gold-edged card
## icon "+1", side by side (toward the tower). The faint ghost's icons are faint too.
const HG_TAG_DX := 0.25
const HG_TAG_Y := 0.2
const HG_TAG_CARD := Vector3(0.13, 0.19, 0.02)
const HG_TAG_EDGE := 0.025
const HG_TAG_FONT := 30
const HG_TAG_LX := 0.14
const HG_TAG_TEXT := "+1"
const HG_TAG_A_FAINT := 0.35
const HG_ICON_X := [0.0, 0.5]
const HG_ICON_BACK_R := 0.12
const HG_ICON_LINE := 0.04
const HG_BEAM_PTS := [Vector2(0.1, 0.0), Vector2(-0.09, 0.0)]
const HG_BEAM_HEAD := [[Vector2(-0.1, 0.0), Vector2(-0.03, 0.06)], [Vector2(-0.1, 0.0), Vector2(-0.03, -0.06)]]

## Highlights by meaning. Capture: an amber plus over the district and a pulsing amber ring. Repair: a red outline
## around the district's wrench and a red hex ring. Picked: a steady white ring with a check on its camera-side edge.
## Gold (L14): a steady gold double ring.
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
const GOLD_R := 1.32
const GOLD_RING_W := 0.06
const GOLD_RING_GAP := 0.12

## L14 wound flight: a cracked gray card rises off the district and arcs to the target screen point, shrinking (its
## apparent size ends at WOUND_END_K), turning a little and fading at the end. Drawn over everything.
const WOUND_CARD := Vector3(0.42, 0.6, 0.03)
const WOUND_EDGE_W := 0.035
const WOUND_CRACK_S := 0.8
const WOUND_START_Y := 1.4
const WOUND_ARC := 1.6
const WOUND_DEPTH_K := 0.8
const WOUND_END_K := 0.45
const WOUND_SPIN := 0.6
const WOUND_FADE_U := 0.85
const WOUND_SETTLE_U := 0.65
const WOUND_PRIORITY := 10

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
const T_REVEAL_B := 1.3
const T_HUNT_REVEAL := 1.2
const T_EVADED := 1.2
const T_DECAY := 0.8
const T_FALL := 1.8
const T_WOUND := 1.0
const T_WOUND_CUE := 0.25
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

## L16: tier icon textures by "tier|size|color".
static var _icon_cache: Dictionary = {}

# ======================= state =======================
var cam: Camera3D
var _env: Environment
var _yaw: float = deg_to_rad(CAM_YAW_DEG)
var _tilt: float = deg_to_rad(CAM_PITCH_DEG) * GLYPH_TILT
var _fit_free: Rect2 = FIT_FREE
var _view_rect: Rect2 = Rect2()
var _fan: bool = false
var _mats: Dictionary = {}
var _unit_box: BoxMesh
var _board: Node3D
var _path_root: Node3D
var _outcome_root: Node3D
var _ghost_root: Node3D
var _verdict_root: Node3D
var _home_glyph_root: Node3D
var _hunter_root: Node3D
var _b_root: Node3D
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
var _out_last: Dictionary = {}
var _ghost_streets: Dictionary = {}
var _ghost_mats: Array = []
var _paths_on: bool = false
var _path_pulse: Array = []
var _scramble: bool = false
var _status: Dictionary = {}
var _sentries: Dictionary = {}
var _sentry_verb: Dictionary = {}
var _sentry_gold: Dictionary = {}
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
var _corp_root: Node3D = null
var _heat_root: Node3D = null
var _hg_active: int = 0
var _hg_faint: bool = false
var _hg_tags: bool = true
var _hg_mats: Array = []
var _hg_labels: Array = []
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
var _hc_lanes: Array = []
var _hc_streets: Dictionary = {}
var _hc_hound: Node3D = null
var _hc_hound_mats: Array = []
var _hc_from: Vector3 = Vector3.ZERO
var _hc_real: int = -1
var _hc_spawned: bool = false
var _resp_mats: Array = []
var _resp_last: Dictionary = {}
var _resp_dimmed: bool = false
var _resp_dim_mats: Array = []
var _resp_crumble: Array = []
var _resp_drop: Array = []
var _vehicles: Dictionary = {}
var _cands: Array = []
var _cand_real: int = -1
var _cand_q: Node3D = null
var _cand_q_holder: Node3D = null
var _cand_q_base: Vector3 = Vector3.ZERO
var _cand_q_mats: Array = []
var _bcands: Array = []
var _b_real: int = -1
var _b_pulse: Array = []
var _wounds: Array = []
var _fx: Array = []
var _shakes: Dictionary = {}
var _hl: Array = []
var _path_use: Dictionary = {}
var _trail_fade: Array = []
var _trail_arrow: Dictionary = {}
var _lane: Dictionary = {}
var _road_use: Dictionary = {}
var _hit_count: Dictionary = {}
## L15: per playout line, {beam, mats, thin: [[node, kind]], marks: Node3D or null, done}.
var _beam_rec: Dictionary = {}
var _active_line: int = NO_LINE
var _hit_x: Dictionary = {}
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
	_ghost_root = Node3D.new()
	add_child(_ghost_root)
	_verdict_root = Node3D.new()
	add_child(_verdict_root)
	_home_glyph_root = Node3D.new()
	add_child(_home_glyph_root)
	_hunter_root = Node3D.new()
	add_child(_hunter_root)
	_b_root = Node3D.new()
	add_child(_b_root)
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
## applies on top of them. A fallen HQ (show_fall) is rebuilt standing. Route verdicts, home glyphs, hunter street
## candidates, B candidates, the outcome ghost, wound cards in flight and crack decals are cleared; the Heat ghosts are
## rebuilt from the last set_heat_ghosts().
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
	clear_outcome_ghost()
	clear_response_preview()
	hide_route_verdicts()
	clear_home_glyphs()
	clear_hunter_cands()
	_clear_wounds()
	_cracked.clear()
	_sentries.clear()
	_sentry_verb.clear()
	_sentry_gold.clear()
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
	_corp_root = corp
	_beacon_mat = _mat_live(COBALT_HOT, E_BEACON)
	_sphere(corp, Vector3(0.0, HQ_PLAT.y + HQ_TIERS * HQ_TIER_H + HQ_BEACON_R, 0.0), HQ_BEACON_R, _beacon_mat)
	_refresh_heat_ghosts()
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


## Show a state {owned: {cell: OK/DOWN/TAKEN}, home_hp, heat} and a placement {sentries: {cell: D/N/E or card_id},
## ghost: cell|"HOME"|null}.
## L14: a sentry value may be a card id. It is looked up in `cards` ({id: [id, type, verb] or [type, verb] or
## {type, verb}}) and else in st.deck ([[id, type, verb]]); the sentry takes the card's type and shows its verb glyph
## (GUARD, SHIFT, JAM). A plain type shows no verb glyph (the L13 look); an unknown id or a wound shows no sentry. The
## optional place.gold (Array of card ids) gives those sentries a gold edge. L17: SHIFT and JAM verb glyphs are drawn
## larger than GUARD.
## Every DOWN district shows the "TAKEN next raid" countdown mark; an OK district hit this raid shows a crack decal.
## Trails of the last playout stay; reset_playout() clears them.
func show_state(st: Dictionary, place: Dictionary, cards: Dictionary = {}) -> void:
	var owned: Dictionary = st.get("owned", {})
	for c: Vector2i in _cells():
		_status[c] = str(owned.get(c, "NEUTRAL"))
	_home_hp = int(st.get("home_hp", HOME_HP_MAX))
	_heat = int(st.get("heat", 0))
	var lookup := _card_lookup(st, cards)
	var gold := {}
	var gl: Variant = place.get("gold", [])
	if gl is Array:
		for gv: Variant in gl:
			gold[str(gv)] = true
	_sentries.clear()
	_sentry_verb.clear()
	_sentry_gold.clear()
	var sd: Dictionary = place.get("sentries", {})
	for k: Variant in sd:
		var tv := _sentry_of(sd[k], lookup)
		if str(tv[0]) == "":
			continue
		_sentries[k] = str(tv[0])
		if str(tv[1]) != "":
			_sentry_verb[k] = str(tv[1])
		if gold.has(str(sd[k])):
			_sentry_gold[k] = true
	var g: Variant = place.get("ghost", null)
	_ghost_home = g is String and String(g) == "HOME"
	_ghost_cell = g if g is Vector2i else NO_CELL
	for c: Vector2i in _cells():
		_refresh_cell(c)
	_refresh_pips()
	_refresh_home_ghost()
	if _beacon_mat != null:
		_beacon_mat.emission_energy_multiplier = E_BEACON * (1.0 + float(_heat) / HEAT_REF)


## The sealed candidates [{route, type}]: real -1 = ghosted convoys at the corp end under one shared "?" glyph (a new
## raid: vehicles, effects, trails, B candidates and crack decals are reset, planned paths stay); real >= 0 = the
## settled reveal (two gone, the real one lit, the "?" collapsed).
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
		_build_cand_q()
	_cand_real = real
	_apply_reveal(1.0 if real >= 0 else 0.0)
	_face_all()


## L14: the second sealed beam's candidates, the two routes other than the real A. routes holds route indices or
## {route, type} entries. Each route shows a pulsing dashed lane in its type color (cobalt when untyped), a ghosted
## convoy of that type waiting at the corp end (none when untyped) and a "?" above it. real >= 0 (a route index) shows
## the settled reveal at once. Replaces any shown before; they stay through play() until the B beam spawns (a cue
## with beam "sealed_b", or the first non-hunter vehicle entering at the corp end of the revealed route), the next
## show_candidates(-1) or setup().
func show_b_cands(routes: Array, real: int = -1) -> void:
	_clear_b_cands()
	_b_real = -1
	for rv: Variant in routes:
		var route := -1
		var type := ""
		if rv is Dictionary:
			route = int((rv as Dictionary).get("route", -1))
			type = str((rv as Dictionary).get("type", ""))
		else:
			route = int(rv)
		if route < 0 or route >= _h:
			continue
		var typed := TYPE_COLOR.has(type)
		var col: Color = _type_col(type) if typed else COBALT_HOT
		var root := Node3D.new()
		_b_root.add_child(root)
		var bc := {"route": route, "type": type, "root": root, "node": null, "mats": [], "parts": [], "faces": [],
			"hunter": false, "lane": [], "q": null}
		var cs: Array = []
		for x in range(_w - 1, -1, -1):
			cs.append(Vector2i(x, route))
		var span := _line_span({"kind": "ROUTE", "index": route, "cells": cs, "type": type, "home": true}, B_LANE_Y)
		if not span.is_empty():
			var lm := _mat_live(col, E_PATH, B_LANE_A)
			bc["lane"] = [lm]
			_b_pulse.append(lm)
			_dashes(root, span[0] as Vector3, span[1] as Vector3, Vector3.ZERO, lm)
		var pos := _grid_world(Vector2i(_w - 1, route)) + Vector3(CAND_DX * CELL_DX, VEH_Y, 0.0)
		if typed:
			var v := _make_vehicle(type, false, CAND_ALPHA)
			var n: Node3D = v["node"]
			n.position = pos
			n.rotation.y = HEADING_HOME
			bc["node"] = n
			bc["mats"] = v["mats"]
			bc["parts"] = v["parts"]
			bc["faces"] = v["faces"]
		bc["q"] = _qmark(root, pos + Vector3(0.0, B_Q_DY, 0.0) + _cam_back() * B_Q_FWD, B_Q_S, col)
		_bcands.append(bc)
	if real >= 0 and _b_has(real):
		_b_real = real
		_apply_b_reveal(1.0)
	else:
		_apply_b_reveal(0.0)
	_face_all()


## L14: the REVEAL B beat. The B candidate on route `real` (a route index) ignites, the other dissolves and both "?"
## collapse. It plays at the current speed (instant settles at once) and returns cues_finished; the sealed_b cues
## follow it.
func reveal_b(real: int) -> Signal:
	return play([{"kind": "reveal_b", "line": real}], _speed)


## L14: remove the B candidates.
func clear_b_cands() -> void:
	_clear_b_cands()
	_b_real = -1


## L14: a cracked gray card flies from district `cell` to the screen point `to` (viewport pixels of this board's
## viewport, the same space as cell_screen_pos), for a district turned TAKEN. It does not interrupt a playout and runs
## at the current speed. Returns a signal that fires when the card lands (in instant mode: the next frame, the card
## left frozen near its end until the next play() or reset).
func wound_fly(cell: Vector2i, to: Vector2) -> Signal:
	var f := WoundFlight.new()
	_start_wound(cell, to, f)
	return f.done


## L13: the hunter's two sealed streets (street indices, in hunter_cands order) for a hunter of the given type. Each
## street is a dashed cobalt hound lane with a pawprint at its head and a "?" badge above it; the hound (glowing eyes,
## type badge) stands between the two heads. Both streets count as used (they stay visible while paths are shown).
## real >= 0 shows the settled reveal at once. Replaces any shown before; they stay through play() until
## clear_hunter_cands() or setup(). The next hunter cue spawns its hound where this one stands. L15: after the reveal
## the dissolved street stops counting as used, and once the hunter starts its run the revealed lane fades.
func show_hunter_cands(streets: Array, type: String, real: int = -1) -> void:
	clear_hunter_cands()
	var heads: Array = []
	for sv: Variant in streets:
		var x := int(sv)
		var root := Node3D.new()
		_hunter_root.add_child(root)
		var lane := {"street": x, "root": root, "mats": [], "q": null, "head": Vector3.ZERO}
		_hc_lanes.append(lane)
		if x < 0 or x >= _w:
			continue
		var cs: Array = []
		for y in range(_h):
			cs.append(Vector2i(x, y))
		var span := _line_span({"kind": "STREET", "index": x, "cells": cs, "type": type, "home": false}, HUNT_Y)
		if span.is_empty():
			continue
		var a: Vector3 = span[0]
		var b: Vector3 = span[1]
		var horiz: bool = span[2]
		var m := _mat_live(HUNTER_TRAIL, E_PATH, HC_ALPHA)
		var gm := _mat_live(COBALT_HOT, E_HL_GLYPH)
		lane["mats"] = [m, gm]
		var lat := _lateral(horiz) * _lane_offset(_path_use.duplicate(), _road_key(a, horiz))
		_dashes(root, a, b, lat, m)
		_paw(root, a + lat + Vector3(0.0, HC_PAW_Y - a.y, 0.0), HC_PAW_S, gm)
		var q := _qmark(root, a + lat + Vector3(0.0, HC_Q_Y - a.y, 0.0), HC_Q_S, COBALT_HOT)
		lane["q"] = q
		var head := Vector3(a.x, 0.0, a.z) + lat
		lane["head"] = head
		heads.append(head)
		_hc_streets[x] = true
	if not heads.is_empty():
		var mid := Vector3.ZERO
		for hp: Vector3 in heads:
			mid += hp
		mid /= float(heads.size())
		_hc_hound = Node3D.new()
		_hc_hound.position = mid
		_hunter_root.add_child(_hc_hound)
		var inner := Node3D.new()
		inner.rotation.y = HEADING_DOWN
		inner.scale = Vector3.ONE * OUT_HOUND_S
		_hc_hound.add_child(inner)
		var body := _mat_live(HUNTER_BODY, E_HUNTER)
		var eye := _mat_live(HUNTER_EYE, E_EYE)
		var bm := _mat_live(_type_col(type), E_OUT)
		_hc_hound_mats = [body, bm]
		_build_hound(inner, body, eye)
		_eyes.append({"node": _hc_hound, "mat": eye})
		_badge(_hc_hound, Vector3(0.0, OUT_HOUND_GLYPH_Y, 0.0), type, HUNTER_BADGE_S * OUT_HOUND_GLYPH_K, bm)
		_hc_from = mid
	_hc_hound_vis()
	_apply_street_vis()
	if real >= 0 and real < _hc_lanes.size():
		_hc_real = real
		_apply_hunter_reveal(1.0)


## L13: the HUNTER REVEAL beat. The lane of hunter street candidate real (an index into show_hunter_cands' streets)
## ignites, the other dissolves, both "?" badges collapse and the hound steps to the real lane's head. It plays at the
## current speed (instant settles at once) and returns cues_finished; the hunter's run cues follow it.
func hunter_reveal(real: int) -> Signal:
	return play([{"kind": "hunter_reveal", "line": real}], _speed)


## L13: remove the hunter street candidates and their hound (every cross street shows again).
func clear_hunter_cands() -> void:
	if _hunter_root != null:
		for ch in _hunter_root.get_children():
			ch.queue_free()
	_hc_lanes.clear()
	_hc_streets.clear()
	_hc_hound = null
	_hc_hound_mats = []
	_hc_real = -1
	_hc_spawned = false
	_apply_street_vis()


## L13: the Heat ghosts on the corp tower: `active` bright ghost beams (one per extra beam the current Heat brings) and,
## when next_faint, one faint ghost for the next threshold. L15: with tags (the default) each ghost carries two small
## icons, a beam "+1" and a gold-edged card "+1" (what the band brings). Kept across setup().
func set_heat_ghosts(active: int, next_faint: bool, tags: bool = true) -> void:
	_hg_active = maxi(0, active)
	_hg_faint = next_faint
	_hg_tags = tags
	_refresh_heat_ghosts()


## L14: the free screen area (in the 1280 x 720 reference viewport) the camera fits the board into. An empty rect
## restores the default (left of the 420 px panel, between the HUD and the legend). A set_view_rect() rect, while
## set, takes precedence.
func set_fit_free(r: Rect2) -> void:
	_fit_free = r if r.size.x > 0.0 and r.size.y > 0.0 else FIT_FREE
	_fit_camera()


## L16: the screen rect (in the 1280 x 720 reference viewport, scaled to this board's viewport) the camera fits the
## board into, overriding set_fit_free while set. The playout passes a wide rect when the side panel collapses to a
## strip; an empty rect (Rect2()) drops the override and restores the set_fit_free area (BETWEEN, PLAN).
func set_view_rect(rect: Rect2) -> void:
	_view_rect = rect if rect.size.x > 0.0 and rect.size.y > 0.0 else Rect2()
	_fit_camera()


## L16: fan out the stacked markers of one district (the lab turns it on at Heat >= 75): the sentry (with its verb
## disc) moves front-left, the wrench and its countdown back-left, and the forecast outcome glyphs to the right, several
## on one cell spread on a small ring. The response preview's ghost sentry follows the sentry slot. Off restores the
## centered look. Cells, the shown outcome and the shown response preview are redrawn.
func set_fan(on: bool) -> void:
	if on == _fan:
		return
	_fan = on
	_cell_key.clear()
	_refresh_all_cells()
	if not _out_last.is_empty():
		show_outcome(_out_last.duplicate())
	elif not _resp_last.is_empty():
		show_response_preview(_resp_last.duplicate())


## L16: true while the district markers are fanned out.
func is_fanned() -> bool:
	return _fan


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
##   start, facing down the street (the hunter-candidates hound hides meanwhile). Its street counts as used.
## L16: while fanned (set_fan), the glyphs sit right of the cell center, several on one cell spread on a small ring.
## Replaces any outcome shown before; an active response preview is redrawn on top. play() clears it.
func show_outcome(o: Dictionary) -> void:
	clear_outcome()
	_out_last = o.duplicate()
	var hits: Array = o.get("hits", [])
	var blocks: Array = o.get("blocks", [])
	var types: Array = o.get("block_types", [])
	var counts := {}
	for hv: Variant in hits:
		if hv is Vector2i:
			counts[hv] = int(counts.get(hv, 0)) + 1
	for bv: Variant in blocks:
		if bv is Vector2i:
			counts[bv] = int(counts.get(bv, 0)) + 1
	var idx := {}
	for hv: Variant in hits:
		if hv is Vector2i:
			var hc: Vector2i = hv
			_out_hit(hc, _out_fan(hc, counts, idx))
	for i in range(blocks.size()):
		var bv: Variant = blocks[i]
		if bv is Vector2i:
			var bc: Vector2i = bv
			var t := str(types[i]) if i < types.size() else str(_sentries.get(bc, "D"))
			_out_block(bc, t, _out_fan(bc, counts, idx))
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
	_out_last = {}
	if _outcome_root == null:
		return
	for ch in _outcome_root.get_children():
		ch.queue_free()
	_hc_hound_vis()
	_apply_street_vis()


## L17: draw one forecast outcome (a forecast cell A x B x hunter, or a response row's outcome) on the city as a ghost
## overlay, replacing any ghost shown before:
## - beams: the lines the outcome fires, as the board draws them ({kind, index, cells, type, home}, optional beam (a
##   cue beam key; "hunter" draws in the hunter's cobalt), hunter: bool, and stop: the cell where a block ends the line,
##   Vector2i or [x, y]), drawn as thin translucent lines with a chevron (a stop bar when stopped) and a small type
##   glyph at the entry. Their streets count as used while paths are shown;
## - fallen: {cell: "DOWN" | "TAKEN"} (cells as Vector2i, [x, y] or "x,y"), the districts that fall, drawn as a ghost
##   crumble tint (damage orange for DOWN, cobalt for TAKEN);
## - home_lost: the HOME pips this outcome loses, drawn as red ghost pips over the last kept pips;
## - tier: a large tier glyph (the five L16 shapes) in front of our HQ tower, with a ring on its platform ("" skips).
## It stays until clear_outcome_ghost(), the next show_outcome_ghost(), play(), reset_playout() or setup().
func show_outcome_ghost(beams: Array, fallen: Dictionary, home_lost: int, tier: String) -> void:
	clear_outcome_ghost()
	if _ghost_root == null:
		return
	var use := {}
	for bv: Variant in beams:
		if bv is Dictionary:
			_og_beam(bv as Dictionary, use)
	for k: Variant in fallen:
		var c: Variant = _og_cell(k)
		if c is Vector2i and _cell_root.has(c):
			_og_crumble(c as Vector2i, str(fallen[k]))
	if home_lost > 0:
		_og_pips(home_lost)
	if tier != "":
		_og_tier(tier)
	_apply_street_vis()


## L17: remove the outcome ghost overlay.
func clear_outcome_ghost() -> void:
	_ghost_mats.clear()
	_ghost_streets.clear()
	if _ghost_root == null:
		return
	for ch in _ghost_root.get_children():
		ch.queue_free()
	_apply_street_vis()


## Stamp each sealed route's forecast tier at that lane's corp-side entry (L13). v = [{route: int, tier: String}], one
## entry per candidate route. L16: the five tier shapes (HOLDS full shield, BATTERED cracked shield, DAMAGED broken
## heart, BREACHED skull, EVADED open eye) in their tier_color, each with a ring on the road. Replaces any verdicts
## shown before; they stay through the launch (play() keeps them) until hide_route_verdicts() or setup().
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


## Remove the route verdicts.
func hide_route_verdicts() -> void:
	if _verdict_root == null:
		return
	for ch in _verdict_root.get_children():
		ch.queue_free()


## L15: per route, its worst tier glyph at the route's lane end at our HQ (between our HQ platform and the first
## district), with a ring on the road. per_route holds either tier Strings indexed by route (null or "" skips a route)
## or {route: int, tier: String} entries. Same glyphs as the route verdicts (L16: the five tier shapes). Replaces any
## shown before; they stay (play() keeps them) until clear_home_glyphs() or setup().
func show_home_glyphs(per_route: Array) -> void:
	clear_home_glyphs()
	if _home_root == null:
		return
	for i in range(per_route.size()):
		var ev: Variant = per_route[i]
		var route := i
		var t := ""
		if ev is Dictionary:
			route = int((ev as Dictionary).get("route", i))
			t = str((ev as Dictionary).get("tier", ""))
		elif typeof(ev) == TYPE_NIL:
			continue
		else:
			t = str(ev)
		if route < 0 or route >= _h or t == "":
			continue
		var ground := Vector3(_home_world().x + HOME_GLYPH_DX, 0.0, _grid_world(Vector2i(0, route)).z)
		_tier_glyph(_home_glyph_root, ground, t, HOME_GLYPH_S, HOME_GLYPH_SKULL_S, HOME_GLYPH_FWD)


## L15: remove the home glyphs.
func clear_home_glyphs() -> void:
	if _home_glyph_root == null:
		return
	for ch in _home_glyph_root.get_children():
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


## L16: preview one response row's effect on the board (hover or select), the glyph-first way:
## - "SACRIFICE", a = the cell: a shield dome on HOME and a cobalt crumble on the cell;
## - "REDEPLOY", a = the source cell, b = the target cell: a ghost arrow from the source to the target, in the source
##   sentry's type color, with a ghost sentry (and its card verb) at the target;
## - "DEPLOY", a = the type ("D" / "N" / "E"), b = the target cell (a cell then a type is accepted too): a ghost
##   sentry dropping in on the target, with a ghost arrow from the reserve tray at our HQ;
## - "JAM", a = the hunter's street (optional): a struck-out hound, crossing out the hound and every live hunter lane;
## - "HOLD" or anything else: clears the preview.
## Cells may be Vector2i or [x, y]. It replaces any preview shown before (see show_response_preview); play() clears it.
func preview_response(kind: String, a: Variant = null, b: Variant = null) -> void:
	var k := kind.to_upper()
	var ca: Variant = _as_cell(a)
	var cb: Variant = _as_cell(b)
	match k:
		"REDEPLOY":
			if not (cb is Vector2i):
				clear_response_preview()
				return
			var t := "D"
			var verb := ""
			if ca is Vector2i:
				t = str(_sentries.get(ca, "D"))
				verb = str(_sentry_verb.get(ca, ""))
			show_response_preview({"kind": "REDEPLOY", "from": ca if ca is Vector2i else null, "to": cb, "type": t,
				"verb": verb})
		"DEPLOY":
			var cell: Variant = cb
			var t := str(a)
			if ca is Vector2i:
				cell = ca
				t = str(b)
			if not (cell is Vector2i):
				clear_response_preview()
				return
			show_response_preview({"kind": "DEPLOY", "from": null, "to": cell, "type": t})
		"SACRIFICE":
			if not (ca is Vector2i):
				clear_response_preview()
				return
			show_response_preview({"kind": "SACRIFICE", "cell": ca})
		"JAM":
			var p := {"kind": "JAM"}
			if a is int:
				p["street"] = int(a)
			show_response_preview(p)
		_:
			clear_response_preview()


## Draw a response row's effect on the board: p = {kind: "REDEPLOY"|"DEPLOY"|"SACRIFICE"|"JAM"|"HOLD", from: Vector2i
## or null, to: Vector2i or null, type: String}, with the optional keys street: int (the hunter's street for JAM when
## no hound is shown), cell: Vector2i (the SACRIFICE cell; to is accepted too), verb: String (L14: the card verb shown
## on the ghost sentry) and gold: bool (L14: a gold double edge on the target).
## - REDEPLOY / DEPLOY: a ghost arc arrow (L16) in the sentry type's color from the source to the target cell, with a
##   ghost sentry at the target. The source is a spinning dashed ring on the sentry's cell, or (from = null) the
##   reserve tray just right of our HQ on the target's route; then (L16) the ghost sentry drops in on a loop.
## - SACRIFICE (L13): the cell crumbles under a cobalt veil (falling cobalt debris, a cobalt hex ring), and a shield
##   dome with a shield glyph stands over our HQ.
## - JAM: a red cross over the hound (the outcome hound, else the hunter-candidates hound, else the head of p.street);
##   the hound and its path dim. L16: every live hunter lane's pawprint is crossed out too.
## - HOLD: nothing (a gold edge goes on our HQ).
## Replaces any preview shown before. play() clears it.
func show_response_preview(p: Dictionary) -> void:
	clear_response_preview()
	_resp_last = p.duplicate()
	var kind := str(p.get("kind", "HOLD"))
	var type := str(p.get("type", "D"))
	var gold := bool(p.get("gold", false))
	match kind:
		"REDEPLOY", "DEPLOY":
			var tv: Variant = p.get("to", null)
			if not (tv is Vector2i):
				return
			var to: Vector2i = tv
			var m := _mat_live(_type_col(type), E_RESP, RESP_ARROW_A)
			_resp_mats.append(m)
			var fv: Variant = p.get("from", null)
			var a := Vector3.ZERO
			var cut := RESP_SRC_CUT
			var drop := false
			if fv is Vector2i:
				a = _grid_world(fv as Vector2i)
				_resp_source(a, m)
			else:
				a = _tray_pos(to)
				cut = RESP_TRAY_CUT
				drop = true
				_resp_tray(a, type, m)
			_resp_arrow(a, _grid_world(to), cut, RESP_DST_CUT, m)
			_resp_target(to, type, m, str(p.get("verb", "")), drop)
			if gold:
				_gold_rings(_resp_root, _grid_world(to), GOLD_R)
		"SACRIFICE":
			var cv: Variant = p.get("cell", p.get("to", null))
			if cv is Vector2i:
				_resp_sacrifice(cv as Vector2i)
				if gold:
					_gold_rings(_resp_root, _grid_world(cv as Vector2i), GOLD_R)
		"JAM":
			_resp_jam(p, gold)
		_:
			if gold and _home_root != null:
				_gold_rings(_resp_root, _home_world() + Vector3(0.0, HQ_PLAT.y, 0.0), GHOST_HOME_R + PICK_HOME_PAD)


## Remove the response preview (and undim the hound).
func clear_response_preview() -> void:
	if _resp_root != null:
		for ch in _resp_root.get_children():
			ch.queue_free()
	_resp_mats.clear()
	_resp_crumble.clear()
	_resp_drop.clear()
	_resp_last = {}
	if _resp_dimmed:
		_tint(_resp_dim_mats, 1.0, 1.0)
	_resp_dim_mats = []
	_resp_dimmed = false


## Play cues in order (beam_step, block, hit, home, hunter_turn, jam, reveal, reveal_b, hunter_reveal, evaded, decay,
## fall, wound) and emit cues_finished at the end. Planned paths, the outcome overlay, the outcome ghost (L17) and the
## response preview are cleared; the route verdicts, home glyphs, the hunter street candidates and the B candidates
## stay. Every beam leaves a trail with its hits and stops until reset_playout(). Hit cells get the crack mark.
## L14 cue keys: beam ("beam1", "extra1", "extra2", "sealed", "sealed_b", "hunter"), optional; a "sealed" beam enters
## from the lit A convoy and a "sealed_b" beam from the lit B convoy. A "wound" cue {cell, to: Vector2} starts a wound
## card flight (see wound_fly) and moves on after a short beat.
## L15: the line whose cue moves is the current beam (full strength, with its block markers and hit glyphs). When a
## different line starts moving, every other line becomes DONE: its trail dims to 25% alpha with thin lines and its
## block markers and hit glyphs go. Every hit cell keeps a small red X until the next raid.
func play(cues: Array, speed: float = 1.0) -> Signal:
	clear_paths()
	clear_outcome()
	clear_outcome_ghost()
	clear_response_preview()
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


## L15: mark a beam's trail DONE (dimmed to 25% alpha, thin lines, no block markers or hit glyphs). beam is a cue's
## beam key ("beam1", "extra1", "extra2", "sealed", "sealed_b", "hunter"); "" or "*" marks every line drawn so far.
## The playout does this on its own when another line starts moving; this is for the lab's beats between plays.
func set_beam_done(beam: String) -> void:
	for k: Variant in _beam_rec.keys():
		var rec: Dictionary = _beam_rec[k]
		if beam == "" or beam == "*" or str(rec["beam"]) == beam:
			_set_line_done(int(k))


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


## Instant on: every cue settles in one frame, effects show frozen at their settled look and trails at rest; wound
## cards in flight land at once. Turning it on mid-playout finishes the playout at once.
func set_instant(on: bool) -> void:
	_instant = on
	if on:
		_snap_trails()
		_clear_wounds()
		if _playing:
			_settle_cue(_cur_cue)
			_finish_instant()


## Change the playout speed (1, 2, 4) while it runs.
func set_speed(speed: float) -> void:
	_speed = maxf(speed, SPEED_MIN)


## Scramble on: the board labels (route names, street numbers, the EVADED stamp, the Heat tick "+1" labels) show seeded
## noise of the same length. Off: the real names come back. "?" glyphs are never scrambled.
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
## - "picked": a steady white ring with a check mark (a picked or committed choice);
## - "gold" (L14): a steady gold double edge.
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
			"gold":
				_hl_gold(pos, home)
			_:
				_hl_disc(pos, GREY)


## Remove every highlight.
func clear_highlight() -> void:
	for ch in _hl_root.get_children():
		ch.queue_free()
	_hl.clear()


## Drop every vehicle, effect, shake, candidate (A and B), trail (with the hit X marks), planned path, outcome ghost
## and response preview (a fresh raid). Route verdicts stay until hide_route_verdicts(), home glyphs until
## clear_home_glyphs(), hunter street candidates until clear_hunter_cands(), crack decals until the next raid's
## show_candidates(-1); wound cards keep flying.
func reset_playout() -> void:
	_reset_motion()
	clear_paths()
	clear_outcome_ghost()
	clear_response_preview()


# ======================= tier glyphs (L16, static) =======================
## L16: the tier ladder, best to worst: EVADED, HOLDS, BATTERED, DAMAGED, BREACHED (the legend order).
static func tier_ladder() -> Array:
	return TIER_LADDER.duplicate()


## L16: a tier's color (HOLDS green, EVADED lime, BATTERED amber, DAMAGED orange-red, BREACHED red; gray otherwise).
static func tier_color(tier: String) -> Color:
	match tier:
		"HOLDS":
			return HOLD_COL
		"EVADED":
			return EVADE_COL
		"BATTERED":
			return AMBER
		"DAMAGED":
			return DAMAGE_COL
		"BREACHED":
			return RED
	return GREY


## L16: a tier's glyph as a square texture with a transparent background, the same shape as on the board: HOLDS a full
## shield, BATTERED a cracked shield, DAMAGED a broken heart, BREACHED a skull, EVADED an open eye. size is in pixels
## (8..256); col with alpha 0 (the default) uses tier_color. Textures are cached. Returns null for an unknown tier.
static func tier_icon(tier: String, size: int = ICON_SIZE, col: Color = Color(0.0, 0.0, 0.0, 0.0)) -> Texture2D:
	if not TIER_LADDER.has(tier):
		return null
	var c := col if col.a > 0.0 else tier_color(tier)
	var px := clampi(size, ICON_MIN, ICON_MAX)
	var key := "%s|%d|%s" % [tier, px, c.to_html()]
	if _icon_cache.has(key):
		return _icon_cache[key]
	var img := Image.create_empty(px, px, false, Image.FORMAT_RGBA8)
	var ss := float(ICON_SS)
	var n := float(ICON_SS * ICON_SS)
	var fp := float(px)
	for y in range(px):
		for x in range(px):
			var hit := 0
			for sy in range(ICON_SS):
				for sx in range(ICON_SS):
					var p := Vector2((float(x) + (float(sx) + 0.5) / ss) / fp * 2.0 - 1.0, 1.0 - (float(y) + (float(sy) + 0.5) / ss) / fp * 2.0)
					if _icon_in(tier, p / ICON_FILL):
						hit += 1
			img.set_pixel(x, y, Color(c.r, c.g, c.b, c.a * float(hit) / n))
	var tex := ImageTexture.create_from_image(img)
	_icon_cache[key] = tex
	return tex


## True when p (in [-1, 1], y up) lies inside the tier's icon shape.
static func _icon_in(tier: String, p: Vector2) -> bool:
	match tier:
		"HOLDS":
			return _in_poly(p, ICON_SHIELD)
		"BATTERED":
			return _in_poly(p, ICON_SHIELD) and _poly_dist(p, ICON_CRACK) > ICON_CUT_W
		"DAMAGED":
			var heart := _in_poly(p, ICON_HEART_TIP)
			for lc: Vector2 in ICON_LOBES:
				if p.distance_to(lc) < ICON_LOBE_R:
					heart = true
			return heart and _poly_dist(p, ICON_BREAK) > ICON_CUT_W
		"BREACHED":
			var skull := p.distance_to(ICON_SKULL_C) < ICON_SKULL_R or (absf(p.x) < ICON_JAW_X and p.y > ICON_JAW_Y.x and p.y < ICON_JAW_Y.y)
			if not skull:
				return false
			for ec: Vector2 in ICON_EYES:
				if p.distance_to(ec) < ICON_EYE_R:
					return false
			if _in_poly(p, ICON_NOSE):
				return false
			if p.y < ICON_TEETH_Y:
				for tx: float in ICON_TEETH_X:
					if absf(p.x - tx) < ICON_TEETH_W:
						return false
			return true
		"EVADED":
			var lens := p.distance_to(Vector2(0.0, -ICON_LENS_C)) < ICON_LENS_R and p.distance_to(Vector2(0.0, ICON_LENS_C)) < ICON_LENS_R
			var r := p.length()
			return lens and not (r > ICON_IRIS.x and r < ICON_IRIS.y)
	return false


## Point in polygon (even-odd).
static func _in_poly(p: Vector2, pts: Array) -> bool:
	var inside := false
	var j := pts.size() - 1
	for i in range(pts.size()):
		var a: Vector2 = pts[i]
		var b: Vector2 = pts[j]
		if (a.y > p.y) != (b.y > p.y) and p.x < (b.x - a.x) * (p.y - a.y) / (b.y - a.y) + a.x:
			inside = not inside
		j = i
	return inside


## The distance from p to a polyline.
static func _poly_dist(p: Vector2, pts: Array) -> float:
	var best := INF
	for i in range(pts.size() - 1):
		var a: Vector2 = pts[i]
		var b: Vector2 = pts[i + 1]
		best = minf(best, Geometry2D.get_closest_point_to_segment(p, a, b).distance_to(p))
	return best


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
## fill the free area (the set_view_rect rect while set, else _fit_free), then shifts the image there with h_offset /
## v_offset (camera-plane units). This is the same math as Godot's perspective projection (KEEP_HEIGHT), so
## cell_screen_pos matches what is drawn.
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
	var free := _view_rect if _view_rect.size.x > 0.0 and _view_rect.size.y > 0.0 else _fit_free
	var ref := free.grow(-FIT_MARGIN)
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


## L16: a fan offset while fanned, else zero.
func _fan_vec(v: Vector3) -> Vector3:
	return v if _fan else Vector3.ZERO


## L16: a Vector2i from a Vector2i or an [x, y] array; anything else is returned as is.
func _as_cell(v: Variant) -> Variant:
	if v is Vector2i:
		return v
	if v is Array and (v as Array).size() == 2:
		return Vector2i(int(v[0]), int(v[1]))
	return v


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


## L14: a material of its own drawn over everything (wound cards in flight).
func _mat_top(col: Color, energy: float, alpha: float = 1.0) -> StandardMaterial3D:
	var m := _mat_live(col, energy, alpha)
	m.no_depth_test = true
	m.render_priority = WOUND_PRIORITY
	return m


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


## L13: a "?" glyph (a billboard "?" over a dark disc) in a facing holder scaled by s.
func _qmark(parent: Node3D, pos: Vector3, s: float, col: Color) -> Node3D:
	var holder := _facing(parent, pos)
	holder.scale = Vector3.ONE * s
	_backing(holder, Q_BACK_R)
	_label(holder, "?", Vector3(0.0, 0.0, Q_Z), col, Q_FONT)
	return holder


## L13: a pawprint glyph (an oval pad and four toes) on a dark disc, facing the camera, scaled by s.
func _paw(parent: Node3D, pos: Vector3, s: float, m: Material) -> Node3D:
	var holder := _facing(parent, pos)
	holder.scale = Vector3.ONE * s
	_backing(holder, PAW_BACK_R)
	var pad := _cyl(holder, Vector3(PAW_PAD.x, PAW_PAD.y, 0.0), PAW_PAD_R, SHAPE_DEPTH, CIRCLE_SEGS, m)
	pad.rotation.x = -PI * 0.5
	pad.scale = PAW_PAD_SCALE
	for t: Vector2 in PAW_TOES:
		_cyl(holder, Vector3(t.x, t.y, 0.0), PAW_TOE_R, SHAPE_DEPTH, CIRCLE_SEGS, m).rotation.x = -PI * 0.5
	return holder


## A shield shape (a bar and a downward point) built flat in an existing facing holder's plane.
func _shield_into(holder: Node3D, m: Material) -> void:
	_box(holder, Vector3(0.0, SHIELD_TOP_Y, 0.0), SHIELD_TOP, m)
	_cyl(holder, Vector3(0.0, SHIELD_TIP_Y, 0.0), SHIELD_TIP_R, SHAPE_DEPTH, TRI_SEGS, m).rotation.x = PI * 0.5


## L14: a card verb glyph built flat in a facing holder's plane (local units, about +-0.3): GUARD a shield, SHIFT a
## curved arrow, JAM a zigzag. Other verbs draw nothing.
func _verb_into(g: Node3D, verb: String, m: Material) -> void:
	match verb:
		"GUARD":
			var s := Node3D.new()
			s.position = Vector3(0.0, VERB_SHIELD_DY, 0.0)
			g.add_child(s)
			_shield_into(s, m)
		"SHIFT":
			var pts: Array = []
			for i in range(SHIFT_SEGS + 1):
				var a := lerpf(SHIFT_A.x, SHIFT_A.y, float(i) / float(SHIFT_SEGS))
				pts.append(SHIFT_C + Vector2(cos(a), sin(a)) * SHIFT_R)
			_polyline(g, pts, VERB_LINE_W, m)
			var dir := Vector2(sin(SHIFT_A.y), -cos(SHIFT_A.y))
			var tip: Vector2 = (pts[pts.size() - 1] as Vector2) + dir * SHIFT_TIP
			for sd: float in [1.0, -1.0]:
				_polyline(g, [tip, tip - dir.rotated(sd * SHIFT_HEAD_ANG) * SHIFT_HEAD_L], VERB_LINE_W, m)
		"JAM":
			_polyline(g, JAM_PTS, VERB_LINE_W, m)


## L14: the verb badge on a sentry glyph holder: a small dark disc right of the type shape (gold-ringed when gold)
## holding the verb glyph. L17: scaled by VERB_SIZE (SHIFT and JAM larger than GUARD), moved out by its growth.
func _verb_badge(holder: Node3D, verb: String, m: Material, gold: bool) -> void:
	var k := float(VERB_SIZE.get(verb, 1.0))
	var b := Node3D.new()
	b.position = Vector3(VERB_POS.x + VERB_BACK_R * (k - 1.0), VERB_POS.y, VERB_Z)
	b.scale = Vector3.ONE * k
	holder.add_child(b)
	_backing(b, VERB_BACK_R)
	if gold:
		var ring := _torus(b, Vector3.ZERO, VERB_GOLD_R.x, VERB_GOLD_R.y, CIRCLE_SEGS, _mat(GOLD, E_GOLD))
		ring.scale = Vector3.ONE
		ring.rotation.x = -PI * 0.5
	var g := Node3D.new()
	g.scale = Vector3.ONE * VERB_S
	b.add_child(g)
	_verb_into(g, verb, m)


## L14: the four edges of a flat card (size x by y) in a facing holder's plane, just in front of its face.
func _card_edges(holder: Node3D, size: Vector3, w: float, m: Material) -> void:
	var z := size.z * 0.5 + SHAPE_DEPTH * 0.25
	for s: float in [1.0, -1.0]:
		_box(holder, Vector3(0.0, s * size.y * 0.5, z), Vector3(size.x + w, w, SHAPE_DEPTH), m)
		_box(holder, Vector3(s * size.x * 0.5, 0.0, z), Vector3(w, size.y + w, SHAPE_DEPTH), m)


## L14: a steady gold double ring on the ground at pos (outer radius r).
func _gold_rings(parent: Node3D, pos: Vector3, r: float) -> void:
	var m := _mat(GOLD, E_GOLD)
	var p := pos + Vector3(0.0, HL_Y, 0.0)
	_torus(parent, p, r, r + GOLD_RING_W, CIRCLE_SEGS, m)
	_torus(parent, p, r - GOLD_RING_GAP - GOLD_RING_W, r - GOLD_RING_GAP, CIRCLE_SEGS, m)


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


## L16: a shield glyph facing the camera on a dark disc, scaled by s; cracked adds a dark zigzag crack in front of it.
func _shield_glyph(parent: Node3D, pos: Vector3, s: float, m: Material, cracked: bool) -> Node3D:
	var holder := _facing(parent, pos)
	holder.scale = Vector3.ONE * s
	_backing(holder, HEART_BACK_R)
	var sh := Node3D.new()
	sh.scale = Vector3.ONE * TIER_SHIELD_K
	sh.position = Vector3(0.0, VERB_SHIELD_DY * TIER_SHIELD_K, 0.0)
	holder.add_child(sh)
	_shield_into(sh, m)
	if cracked:
		var crack := Node3D.new()
		crack.position = Vector3(0.0, 0.0, HEART_BREAK_Z)
		holder.add_child(crack)
		_polyline(crack, TIER_CRACK, HEART_BREAK_W, _solid(BG))
	return holder


## L16: an open eye glyph facing the camera on a dark disc, scaled by s: an almond lens, a dark iris ring and a lit
## pupil.
func _eye_glyph(parent: Node3D, pos: Vector3, s: float, m: Material) -> Node3D:
	var holder := _facing(parent, pos)
	holder.scale = Vector3.ONE * s
	_backing(holder, HEART_BACK_R + 0.06)
	var lens := _cyl(holder, Vector3.ZERO, EYE_LENS_R, SHAPE_DEPTH, CIRCLE_SEGS, m)
	lens.rotation.x = -PI * 0.5
	lens.scale = Vector3(1.0, 1.0, EYE_LENS_FLAT)
	var iris := _torus(holder, Vector3(0.0, 0.0, EYE_Z), EYE_IRIS.x, EYE_IRIS.y, CIRCLE_SEGS, _solid(BG))
	iris.scale = Vector3.ONE
	iris.rotation.x = -PI * 0.5
	_cyl(holder, Vector3(0.0, 0.0, EYE_Z), EYE_PUPIL_R, SHAPE_DEPTH, CIRCLE_SEGS, m).rotation.x = -PI * 0.5
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


# ======================= cards (L14) =======================
## The card lookup {id: [type, verb]}: st.deck ([[id, type, verb]]) first, then `cards` on top ({id: [id, type, verb]
## or [type, verb] or {type, verb} or a type String}).
func _card_lookup(st: Dictionary, cards: Dictionary) -> Dictionary:
	var out := {}
	var deck: Variant = st.get("deck", [])
	if deck is Array:
		for cd: Variant in deck:
			if cd is Array and (cd as Array).size() >= 3:
				out[str(cd[0])] = [str(cd[1]), str(cd[2])]
	for k: Variant in cards:
		var v: Variant = cards[k]
		if v is Array:
			var a: Array = v
			if a.size() >= 3:
				out[str(k)] = [str(a[1]), str(a[2])]
			elif a.size() == 2:
				out[str(k)] = [str(a[0]), str(a[1])]
		elif v is Dictionary:
			out[str(k)] = [str((v as Dictionary).get("type", "")), str((v as Dictionary).get("verb", ""))]
		elif v is String:
			out[str(k)] = [String(v), ""]
	return out


## A sentry value (a type or a card id) as [type, verb]; ["", ""] for an unknown id or a wound.
func _sentry_of(v: Variant, lookup: Dictionary) -> Array:
	var s := str(v)
	if TYPE_COLOR.has(s):
		return [s, ""]
	if lookup.has(s):
		var tv: Array = lookup[s]
		var t := str(tv[0])
		if TYPE_COLOR.has(t) and str(tv[1]) != "WOUND":
			return [t, str(tv[1])]
	return ["", ""]


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
	for e: Array in _hg_labels:
		var l: Variant = e[0]
		if is_instance_valid(l):
			(l as Label3D).text = _board_text(HG_TAG_TEXT, SCRAMBLE_TAG + int(e[1]))


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


## While planned paths are shown, a cross street shows only when a shown line (a planned STREET line, the outcome
## hunter's street, an outcome ghost street or a hunter street candidate) uses it; otherwise every street shows.
func _apply_street_vis() -> void:
	for x in range(_street_nodes.size()):
		var n: Variant = _street_nodes[x]
		if is_instance_valid(n):
			(n as Node3D).visible = not _paths_on or _path_streets.has(x) or _out_streets.has(x) or _hc_streets.has(x) or _ghost_streets.has(x)


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


## L13: rebuild the Heat ghosts on the corp tower from _hg_active / _hg_faint (L15: with their beam and card icons).
func _refresh_heat_ghosts() -> void:
	if is_instance_valid(_heat_root):
		_heat_root.queue_free()
	_heat_root = null
	_hg_mats.clear()
	_hg_labels.clear()
	if not is_instance_valid(_corp_root):
		return
	_heat_root = Node3D.new()
	_corp_root.add_child(_heat_root)
	var n := mini(_hg_active, HG_SLOTS)
	for k in range(n):
		_heat_ghost(k, false)
	if _hg_faint and n < HG_SLOTS:
		_heat_ghost(n, true)


## One Heat ghost in slot k: a floating bar off the corp tower's HOME side with an orb at its root and a chevron
## pointing at HOME. Active ghosts pulse; the faint one is dim and still. L15: above the ghost's tip, two icons side by
## side: a beam arrow "+1" (cobalt) and a gold-edged card "+1".
func _heat_ghost(k: int, faint: bool) -> void:
	var y := HG_Y0 + HG_STEP * float(k)
	var x0 := -HQ_BASE * 0.5 - HG_GAP
	var x1 := x0 - HG_LEN
	var m := _mat_live(COBALT_HOT, E_HG_FAINT if faint else E_HG, HG_A_FAINT if faint else HG_A)
	var bar_end := x1 + ARROW_L * 0.3
	_box(_heat_root, Vector3((x0 + bar_end) * 0.5, y, 0.0), Vector3(x0 - bar_end, HG_BAR.x, HG_BAR.y), m)
	_chevron(_heat_root, Vector3(x1, y, 0.0), Vector3(-1.0, 0.0, 0.0), m)
	_sphere(_heat_root, Vector3(x0, y, 0.0), HG_ORB_R, m)
	if not faint:
		_hg_mats.append(m)
	if not _hg_tags:
		return
	var ia := HG_A_FAINT if faint else 1.0
	var ie := E_HG_FAINT if faint else E_HG
	var tm := _mat_live(GOLD, ie, ia)
	var bm := _mat_live(COBALT_HOT, ie, ia)
	var holder := _facing(_heat_root, Vector3(x1 + HG_TAG_DX, y + HG_TAG_Y, 0.0))
	var a := HG_TAG_A_FAINT if faint else 1.0
	# The beam icon: an arrow pointing at HOME.
	var bi := Node3D.new()
	bi.position = Vector3(float(HG_ICON_X[0]), 0.0, 0.0)
	holder.add_child(bi)
	_backing(bi, HG_ICON_BACK_R)
	_polyline(bi, HG_BEAM_PTS, HG_ICON_LINE, bm)
	for hd: Array in HG_BEAM_HEAD:
		_polyline(bi, hd, HG_ICON_LINE, bm)
	_hg_tag_label(holder, float(HG_ICON_X[0]) + HG_TAG_LX, a, COBALT_HOT, k * 2)
	# The card icon: a dark card with gold edges.
	var ci := Node3D.new()
	ci.position = Vector3(float(HG_ICON_X[1]), 0.0, 0.0)
	holder.add_child(ci)
	_box(ci, Vector3.ZERO, HG_TAG_CARD, _solid(BG))
	_card_edges(ci, HG_TAG_CARD, HG_TAG_EDGE, tm)
	_hg_tag_label(holder, float(HG_ICON_X[1]) + HG_TAG_LX, a, GOLD, k * 2 + 1)
	if not faint:
		_hg_mats.append(tm)
		_hg_mats.append(bm)


## L15: one "+1" label beside a Heat tick icon (scramble slot SCRAMBLE_TAG + slot).
func _hg_tag_label(holder: Node3D, x: float, a: float, col: Color, slot: int) -> void:
	var l := _label(holder, _board_text(HG_TAG_TEXT, SCRAMBLE_TAG + slot), Vector3(x, 0.0, 0.0), Color(col, a), HG_TAG_FONT, HORIZONTAL_ALIGNMENT_LEFT)
	l.outline_modulate = Color(SHADOW_INK, SHADOW_INK.a * a)
	_hg_labels.append([l, slot])


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
	var key := "%s|%s|%s|%s|%s|%s|%s" % [st, sen, str(_sentry_verb.get(c, "")), _sentry_gold.has(c), c == _ghost_cell, _cracked.has(c), _fan]
	if str(_cell_key.get(c, "")) == key:
		return
	_cell_key[c] = key
	_rebuild_cell(c, st, sen)


## NEUTRAL: dim gray. OK: warm amber ring, decal and lit pips (plus a crack decal when hit this raid). DOWN: dim amber,
## a wrench with the cobalt "1" countdown mark (TAKEN next raid) and flicker. TAKEN: cobalt. L16: while fanned, the
## sentry and the wrench move off the cell center (FAN_SENTRY, FAN_WRENCH).
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
		var wp := WRENCH_POS + _fan_vec(FAN_WRENCH)
		_build_wrench(root, wp)
		_build_countdown(root, wp)
	if st == "OK" and _cracked.has(c):
		_build_crack(root)
	if sen != "":
		var sroot := root
		if _fan:
			sroot = Node3D.new()
			sroot.position = FAN_SENTRY
			root.add_child(sroot)
		_build_sentry(sroot, sen, str(_sentry_verb.get(c, "")), _sentry_gold.has(c))
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


func _build_wrench(root: Node3D, pos: Vector3 = WRENCH_POS) -> void:
	var holder := _facing(root, pos)
	_cyl(holder, Vector3.ZERO, WRENCH_DISC.x, WRENCH_DISC.y, CIRCLE_SEGS, _solid(DEAD)).rotation.x = -PI * 0.5
	var m := _mat(GREY, E_WRENCH)
	for p: Array in WRENCH_PARTS:
		var pp: Vector3 = p[0]
		var size: Vector3 = p[1]
		_box(holder, pp, size, m).rotation.z = float(p[2])


## L12: the "TAKEN next raid" countdown next to the wrench: a cobalt ring on a dark disc with a cobalt "1" (boxes).
func _build_countdown(root: Node3D, pos: Vector3 = WRENCH_POS) -> void:
	var holder := _facing(root, pos)
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


## A sentry: a type-colored decal, a pylon and its type shape. L14: the card's verb glyph on a small disc beside the
## shape, and a gold edge ring (and gold-ringed verb disc) for a gold card. L17: the verb disc's size follows the verb.
func _build_sentry(root: Node3D, type: String, verb: String = "", gold: bool = false) -> void:
	var col := _type_col(type)
	var m := _mat(col, E_SENTRY)
	_torus(root, Vector3(0.0, DECAL_Y + RING_Y * 0.5, 0.0), SENTRY_DECAL.x, SENTRY_DECAL.y, CIRCLE_SEGS, m)
	_cyl(root, Vector3(0.0, DECAL_Y + DECAL_T, 0.0), SENTRY_DECAL.x, DECAL_T, CIRCLE_SEGS, _mat(col, E_SENTRY * HALO_E_K, DECAL_ALPHA))
	_cyl(root, Vector3(0.0, SENTRY_BASE.y * 0.5, 0.0), SENTRY_BASE.x, SENTRY_BASE.y, HEX, _solid(STEEL))
	_cyl(root, Vector3(0.0, SENTRY_POLE.y * 0.5, 0.0), SENTRY_POLE.x, SENTRY_POLE.y, HEX, _mat(col, E_SENTRY * HALO_E_K))
	var holder := _shape(root, Vector3(0.0, SENTRY_GLYPH_Y, 0.0), type, SENTRY_GLYPH_S, m)
	if verb != "":
		_verb_badge(holder, verb, _mat(WHITE, E_VERB), gold)
	if gold:
		_torus(root, Vector3(0.0, DECAL_Y + RING_Y * 0.5, 0.0), SENTRY_GOLD.x, SENTRY_GOLD.y, CIRCLE_SEGS, _mat(GOLD, E_GOLD))


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
## the gray wrench) and a pulsing red hex ring on its ground. L16: it follows the fanned wrench.
func _hl_repair(pos: Vector3, home: bool) -> void:
	var m := _mat_live(RED, E_HL_GLYPH)
	_hl.append(m)
	var r := HL_HOME_R if home else HL_R
	var lift := HQ_PLAT.y if home else 0.0
	_torus(_hl_root, pos + Vector3(0.0, HL_Y + lift, 0.0), r, r + HL_RING_W, HEX, m)
	var wp := WRENCH_POS + (Vector3.ZERO if home else _fan_vec(FAN_WRENCH))
	var holder := _facing(_hl_root, pos + wp + Vector3(0.0, lift, 0.0))
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


## L14 gold edge: a steady gold double ring around the district (or our HQ platform).
func _hl_gold(pos: Vector3, home: bool) -> void:
	var r := (GHOST_HOME_R + PICK_HOME_PAD) if home else GOLD_R
	var lift := HQ_PLAT.y if home else 0.0
	_gold_rings(_hl_root, pos + Vector3(0.0, lift, 0.0), r)


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
## L16: the fan offset of the next outcome glyph on cell c (zero while not fanned). counts holds the glyphs per cell,
## idx the ones drawn so far.
func _out_fan(c: Vector2i, counts: Dictionary, idx: Dictionary) -> Vector3:
	var i := int(idx.get(c, 0))
	idx[c] = i + 1
	if not _fan:
		return Vector3.ZERO
	var n := int(counts.get(c, 1))
	if n <= 1:
		return FAN_OUT_SOLO
	var a := FAN_OUT_A0 + TAU * float(i) / float(n)
	return FAN_OUT_SOLO + Vector3(cos(a), 0.0, sin(a)) * FAN_OUT_R


## A hit: a red crack glyph over the district (shifted by off) and a red hex ring on its ground.
func _out_hit(c: Vector2i, off: Vector3 = Vector3.ZERO) -> void:
	var m := _mat(RED, E_OUT)
	_torus(_outcome_root, _grid_world(c) + Vector3(0.0, OUT_RING_Y, 0.0), HIT_MARK_R.x, HIT_MARK_R.y, HEX, m)
	var holder := _facing(_outcome_root, _grid_world(c) + off + Vector3(0.0, OUT_GLYPH_Y, 0.0))
	_backing(holder, OUT_BACK_R)
	_polyline(holder, CRACK_PTS, CRACK_W, m)
	_polyline(holder, CRACK_BRANCH, CRACK_W * 0.8, m)
	_polyline(holder, CRACK_BRANCH_2, CRACK_W * 0.8, m)


## A block: a shield glyph in the sentry's type color over the district (shifted by off) and a ring of that color on
## its ground.
func _out_block(c: Vector2i, type: String, off: Vector3 = Vector3.ZERO) -> void:
	var m := _mat(_type_col(type), E_OUT)
	_torus(_outcome_root, _grid_world(c) + Vector3(0.0, OUT_RING_Y, 0.0), SHIELD_RING_R.x, SHIELD_RING_R.y, CIRCLE_SEGS, m)
	var holder := _facing(_outcome_root, _grid_world(c) + off + Vector3(0.0, OUT_GLYPH_Y, 0.0))
	_backing(holder, OUT_BACK_R)
	_shield_into(holder, m)


## HOME hit: a red skull in front of our HQ tower and a red ring on its platform.
func _out_home() -> void:
	var m := _mat(RED, E_OUT)
	_torus(_outcome_root, _home_world() + Vector3(0.0, HQ_PLAT.y + RING_Y, 0.0), HOME_MARK_R.x, HOME_MARK_R.y, CIRCLE_SEGS, m)
	_skull(_outcome_root, _home_world() + Vector3(0.0, SKULL_Y, 0.0) + _cam_back() * SKULL_FWD, SKULL_S, m)


## The hunter's run: a dashed cobalt lane down its street, with the cobalt hound (glowing eyes, type badge) standing
## at its start, facing down the street. Its materials are kept so a JAM preview can dim it; its street counts as used.
## The hunter-candidates hound hides while this one stands.
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
	_hc_hound_vis()


# ======================= outcome ghost (L17) =======================
## A fallen-map key as a cell: a Vector2i, an [x, y] array or an "x,y" / "(x, y)" string.
func _og_cell(v: Variant) -> Variant:
	var c: Variant = _as_cell(v)
	if c is String or c is StringName:
		var p := String(c).replace("(", "").replace(")", "").replace("[", "").replace("]", "").split(",")
		if p.size() == 2:
			return Vector2i(p[0].strip_edges().to_int(), p[1].strip_edges().to_int())
	return c


## One ghost beam: a thin translucent lane along its road (its own lane per road via use), a small type glyph at the
## entry, and a chevron at the exit, or a stop bar at the block cell when the line has a stop.
func _og_beam(ln: Dictionary, use: Dictionary) -> void:
	var cells: Array = ln.get("cells", [])
	if cells.is_empty():
		return
	var line := ln.duplicate()
	var cs: Array = []
	for cv: Variant in cells:
		var c: Variant = _as_cell(cv)
		if c is Vector2i:
			cs.append(c)
	if cs.is_empty():
		return
	line["cells"] = cs
	var stop: Variant = _as_cell(ln.get("stop", null))
	var cut := false
	if stop is Vector2i and cs.has(stop):
		line["cells"] = cs.slice(0, cs.find(stop) + 1)
		line["home"] = false
		cut = true
	if str(line.get("kind", "")) == "STREET":
		_ghost_streets[int(line.get("index", -1))] = true
	var span := _line_span(line, OG_Y)
	if span.is_empty():
		return
	var a: Vector3 = span[0]
	var b: Vector3 = span[1]
	var horiz: bool = span[2]
	if cut:
		b = _grid_world(stop as Vector2i)
		b.y = OG_Y
	var d := b - a
	var length := d.length()
	if length < EPS:
		return
	var dir := d / length
	var type := str(line.get("type", "D"))
	var hunter := str(line.get("beam", "")) == "hunter" or bool(line.get("hunter", false))
	var col: Color = HUNTER_TRAIL if hunter else _type_col(type)
	var m := _mat_live(col, E_OG_BEAM, OG_BEAM_A)
	_ghost_mats.append(m)
	var lat := _lateral(horiz) * _lane_offset(use, _road_key(a, horiz))
	var rot := _heading(dir, 0.0)
	var stop_l := length if cut else length - ARROW_L * 0.3
	_box(_ghost_root, a + dir * (stop_l * 0.5) + lat, Vector3(stop_l, LANE_T, OG_BEAM_W), m).rotation.y = rot
	if cut:
		var holder := Node3D.new()
		holder.position = b + lat + Vector3(0.0, OG_STOP.y * 0.5, 0.0)
		holder.rotation.y = rot
		_ghost_root.add_child(holder)
		_box(holder, Vector3.ZERO, OG_STOP, m)
	else:
		_chevron(_ghost_root, b + lat, dir, m)
	_shape(_ghost_root, a + lat + Vector3(0.0, PATH_GLYPH_Y, 0.0), type, OG_GLYPH_S, m)


## A district that falls in this outcome: a ground tint, a low veil column, a hex ring and seeded debris lying on the
## cell, in damage orange (DOWN) or cobalt (TAKEN).
func _og_crumble(c: Vector2i, st: String) -> void:
	var col: Color = COBALT if st == "TAKEN" else DAMAGE_COL
	var pos := _grid_world(c)
	var tint := _mat_live(col, E_OG, OG_TINT_A)
	var veil := _mat_live(col, E_OG * 0.5, OG_VEIL_A)
	var ring := _mat_live(col, E_OG_BEAM, OG_BEAM_A)
	var deb := _mat_live(COBALT_HOT if st == "TAKEN" else col, E_OG, OG_DEBRIS_A)
	_ghost_mats.append_array([tint, veil, ring, deb])
	_cyl(_ghost_root, pos + Vector3(0.0, OG_TINT_Y, 0.0), DECAL_R, DECAL_T, CIRCLE_SEGS, tint)
	_cyl(_ghost_root, pos + Vector3(0.0, OG_VEIL_H * 0.5, 0.0), DECAL_R, OG_VEIL_H, HEX, veil)
	_torus(_ghost_root, pos + Vector3(0.0, OUT_RING_Y, 0.0), HIT_MARK_R.x, HIT_MARK_R.y, HEX, ring)
	var rng := RandomNumberGenerator.new()
	rng.seed = OG_DEBRIS_SEED + c.x * SEED_MX + c.y * SEED_MY
	for i in range(OG_DEBRIS_N):
		var p := pos + Vector3(rng.randf_range(-OG_DEBRIS_SPREAD, OG_DEBRIS_SPREAD), OG_DEBRIS * 0.5, rng.randf_range(-OG_DEBRIS_SPREAD, OG_DEBRIS_SPREAD))
		var cube := _box(_ghost_root, p, Vector3.ONE * OG_DEBRIS, deb)
		cube.rotation = Vector3(rng.randf_range(-0.5, 0.5), rng.randf_range(0.0, TAU), rng.randf_range(-0.5, 0.5))


## The HOME pips this outcome loses: red ghost pips just in front of the last n kept pips.
func _og_pips(n: int) -> void:
	if _home_root == null:
		return
	var hp := clampi(_home_hp, 0, HOME_HP_MAX)
	var from := maxi(0, hp - n)
	if from >= hp:
		return
	var m := _mat_live(RED, E_OG_PIP, OG_PIP_A)
	_ghost_mats.append(m)
	var holder := _facing(_ghost_root, _home_world() + Vector3(0.0, _pip_top(), 0.0) + _cam_back() * OG_PIP_FWD)
	for i in range(from, hp):
		_box(holder, Vector3((i - (HOME_HP_MAX - 1) * 0.5) * HOME_PIP_GAP, 0.0, 0.0), HOME_PIP * OG_PIP_K, m)


## The outcome's tier: a large tier glyph in front of our HQ tower and a ring on its platform.
func _og_tier(tier_name: String) -> void:
	if not TIER_LADDER.has(tier_name) or _home_root == null:
		return
	var m := _mat_live(tier_color(tier_name), E_VERDICT)
	_ghost_mats.append(m)
	var plat := _home_world() + Vector3(0.0, HQ_PLAT.y + RING_Y, 0.0)
	_torus(_ghost_root, plat, OG_TIER_RING.x, OG_TIER_RING.y, CIRCLE_SEGS, m)
	var pos := _home_world() + Vector3(0.0, OG_TIER_Y, 0.0) + _cam_back() * OG_TIER_FWD
	_tier_shape(_ghost_root, pos, tier_name, OG_TIER_S, OG_TIER_SKULL_S, m)


# ======================= hunter street candidates (L13) =======================
## The hunter-candidates hound shows until its hunter spawns, and hides while an outcome hound stands.
func _hc_hound_vis() -> void:
	if is_instance_valid(_hc_hound):
		_hc_hound.visible = not _hc_spawned and not is_instance_valid(_out_hound)


## The hunter reveal at progress u: both "?" badges collapse, the real lane ignites, the other dissolves, and the
## hound steps from where it stood to the real lane's head. With no real lane set, everything shows sealed. L15: at
## the end the dissolved street stops counting as used.
func _apply_hunter_reveal(u: float) -> void:
	var e := _ease_out(u)
	for i in range(_hc_lanes.size()):
		var ln: Dictionary = _hc_lanes[i]
		var rv: Variant = ln["root"]
		if not is_instance_valid(rv):
			continue
		var root: Node3D = rv
		var qv: Variant = ln["q"]
		var q: Node3D = qv as Node3D if is_instance_valid(qv) else null
		if _hc_real < 0:
			_tint(ln["mats"], 1.0, 1.0)
			root.visible = true
			if q != null:
				q.scale = Vector3.ONE * HC_Q_S
				q.visible = true
			continue
		if q != null:
			q.scale = Vector3.ONE * HC_Q_S * maxf(1.0 - e, Q_MIN_S)
			q.visible = u < 1.0
		if i == _hc_real:
			_tint(ln["mats"], lerpf(1.0, 1.0 / HC_ALPHA, u), lerpf(1.0, HC_IGNITE_E, u))
		else:
			_tint(ln["mats"], 1.0 - u, 1.0 - u)
			root.visible = u < 1.0
	if _hc_real >= 0 and _hc_real < _hc_lanes.size() and is_instance_valid(_hc_hound) and not _hc_spawned:
		var head: Vector3 = (_hc_lanes[_hc_real] as Dictionary)["head"]
		_hc_hound.position = _hc_from.lerp(head, e)
	if _hc_real >= 0 and _hc_real < _hc_lanes.size() and u >= 1.0:
		var real_x := int((_hc_lanes[_hc_real] as Dictionary)["street"])
		for i in range(_hc_lanes.size()):
			var x := int((_hc_lanes[i] as Dictionary)["street"])
			if i != _hc_real and x != real_x:
				_hc_streets.erase(x)
		_apply_street_vis()


## L15: the hunter has started its run: the "?" badges go, the revealed lane (every lane when none was revealed)
## fades to HC_DONE_K and the dissolved ones hide.
func _hc_fade() -> void:
	for i in range(_hc_lanes.size()):
		var ln: Dictionary = _hc_lanes[i]
		var qv: Variant = ln["q"]
		if is_instance_valid(qv):
			(qv as Node3D).visible = false
		var rv: Variant = ln["root"]
		if _hc_real < 0 or i == _hc_real:
			_tint(ln["mats"], HC_DONE_K, HC_DONE_K)
		elif is_instance_valid(rv):
			(rv as Node3D).visible = false


# ======================= B candidates (L14) =======================
func _b_has(route: int) -> bool:
	for bc: Dictionary in _bcands:
		if int(bc["route"]) == route:
			return true
	return false


func _clear_b_cands() -> void:
	for bc: Dictionary in _bcands:
		var nv: Variant = bc["node"]
		if is_instance_valid(nv):
			(nv as Node3D).queue_free()
	if _b_root != null:
		for ch in _b_root.get_children():
			ch.queue_free()
	_bcands.clear()
	_b_pulse.clear()


## REVEAL B at progress u: both "?" collapse, the real route's lane and convoy ignite, the other dissolves. With no
## real route set, everything shows sealed.
func _apply_b_reveal(u: float) -> void:
	var e := _ease_out(u)
	for bc: Dictionary in _bcands:
		var root: Node3D = bc["root"]
		var nv: Variant = bc["node"]
		var n: Node3D = nv as Node3D if is_instance_valid(nv) else null
		var qv: Variant = bc["q"]
		var q: Node3D = qv as Node3D if is_instance_valid(qv) else null
		var lane: Array = bc["lane"]
		if _b_real < 0:
			_tint(bc["mats"], 1.0, 1.0)
			_tint(lane, 1.0, 1.0)
			if n != null:
				n.scale = Vector3.ONE
				n.visible = true
			if is_instance_valid(root):
				root.visible = true
			if q != null:
				q.scale = Vector3.ONE * B_Q_S
				q.visible = true
			continue
		if q != null:
			q.scale = Vector3.ONE * B_Q_S * maxf(1.0 - e, Q_MIN_S)
			q.visible = u < 1.0
		if int(bc["route"]) == _b_real:
			_tint(bc["mats"], lerpf(1.0, 1.0 / CAND_ALPHA, u), lerpf(1.0, E_CAND_LIT / E_VEH, u))
			_tint(lane, lerpf(1.0, 1.0 / B_LANE_A, u), lerpf(1.0, B_IGNITE_E, u))
		else:
			_tint(bc["mats"], 1.0 - u, 1.0 - u)
			_tint(lane, 1.0 - u, 1.0 - u)
			if n != null:
				n.scale = Vector3.ONE * lerpf(1.0, CAND_SHRINK, u)
				n.visible = u < 1.0
			if is_instance_valid(root):
				root.visible = u < 1.0


# ======================= wound cards (L14) =======================
## Start one wound card flight from `cell` to the screen point `to` (see wound_fly); f fires when it lands.
func _start_wound(cell: Vector2i, to: Vector2, f: WoundFlight) -> void:
	if f == null:
		f = WoundFlight.new()
	if cam == null or not cam.is_inside_tree():
		_emit_flight.call_deferred(f)
		return
	var p0 := _grid_world(cell) + Vector3(0.0, WOUND_START_Y, 0.0)
	var fwd := -cam.global_transform.basis.z
	var d0 := maxf((p0 - cam.global_position).dot(fwd), CAM_NEAR * 2.0)
	var p1 := cam.project_position(to, d0 * WOUND_DEPTH_K)
	var ctrl := (p0 + p1) * 0.5 + Vector3(0.0, WOUND_ARC, 0.0)
	var holder := Node3D.new()
	holder.rotation = Vector3(deg_to_rad(CAM_PITCH_DEG), _yaw, 0.0)
	_fx_root.add_child(holder)
	var inner := Node3D.new()
	holder.add_child(inner)
	var body := _mat_top(WOUND_COL, E_WOUND)
	var edge := _mat_top(WOUND_EDGE_COL, E_WOUND_EDGE)
	var crack := _mat_top(RED, E_CRACK)
	var mats: Array = [body, edge, crack]
	_box(inner, Vector3.ZERO, WOUND_CARD, body)
	_card_edges(inner, WOUND_CARD, WOUND_EDGE_W, edge)
	var cn := Node3D.new()
	cn.position = Vector3(0.0, 0.0, WOUND_CARD.z * 0.5 + SHAPE_DEPTH)
	cn.scale = Vector3.ONE * WOUND_CRACK_S
	inner.add_child(cn)
	_polyline(cn, CRACK_PTS, CRACK_W, crack)
	_polyline(cn, CRACK_BRANCH, CRACK_W * 0.8, crack)
	_polyline(cn, CRACK_BRANCH_2, CRACK_W * 0.8, crack)
	_fx_ring(_grid_world(cell), RED, 1.0)
	var w := {"node": holder, "inner": inner, "mats": mats, "p0": p0, "p1": p1, "ctrl": ctrl, "s0": 1.0,
		"s1": WOUND_DEPTH_K * WOUND_END_K, "t": 0.0, "dur": T_WOUND, "flight": f}
	if _instant:
		_apply_wound(w, WOUND_SETTLE_U)
		_fx_add(holder, "wound_rest", T_WOUND, mats)
		_emit_flight.call_deferred(f)
		return
	_apply_wound(w, 0.0)
	_wounds.append(w)


## A wound card at flight progress u: along a raised arc, shrinking, turning a little, fading at the end.
func _apply_wound(w: Dictionary, u: float) -> void:
	var holder: Node3D = w["node"]
	if not is_instance_valid(holder):
		return
	var k := clampf(u, 0.0, 1.0)
	var e := k * k * (3.0 - 2.0 * k)
	var p0: Vector3 = w["p0"]
	var p1: Vector3 = w["p1"]
	var c: Vector3 = w["ctrl"]
	holder.position = p0.lerp(c, e).lerp(c.lerp(p1, e), e)
	holder.scale = Vector3.ONE * lerpf(float(w["s0"]), float(w["s1"]), e)
	(w["inner"] as Node3D).rotation.z = WOUND_SPIN * e
	var fade := 1.0 if k < WOUND_FADE_U else 1.0 - (k - WOUND_FADE_U) / (1.0 - WOUND_FADE_U)
	_tint(w["mats"], fade, 1.0)


func _step_wounds(dt: float) -> void:
	if _wounds.is_empty():
		return
	var keep: Array = []
	for w: Dictionary in _wounds:
		w["t"] = float(w["t"]) + dt
		var u := float(w["t"]) / float(w["dur"])
		if u >= 1.0:
			var n: Variant = w["node"]
			if is_instance_valid(n):
				(n as Node3D).queue_free()
			_emit_flight.call_deferred(w["flight"])
			continue
		_apply_wound(w, u)
		keep.append(w)
	_wounds = keep


## Every wound card in flight lands at once (its signal fires next frame).
func _clear_wounds() -> void:
	for w: Dictionary in _wounds:
		var n: Variant = w["node"]
		if is_instance_valid(n):
			(n as Node3D).queue_free()
		_emit_flight.call_deferred(w["flight"])
	_wounds.clear()


func _emit_flight(f: WoundFlight) -> void:
	if f != null:
		f.done.emit()


# ======================= route verdicts and home glyphs =======================
## One route's verdict at the lane's corp-side entry: a ring on the road between the last district and the waiting
## candidate, and the tier glyph above it, pushed toward the camera. Unknown tiers draw nothing.
func _verdict(route: int, tier_name: String) -> void:
	var ground := Vector3(_grid_world(Vector2i(_w - 1, route)).x + VERDICT_DX * CELL_DX, 0.0, _grid_world(Vector2i(0, route)).z)
	_tier_glyph(_verdict_root, ground, tier_name, VERDICT_S, VERDICT_SKULL_S, VERDICT_FWD)


## L16: a tier glyph over a ground point: a ring on the road in the tier's color and, raised and pushed toward the
## camera by fwd, the tier's shape (see _tier_shape). Unknown tiers draw nothing.
func _tier_glyph(parent: Node3D, ground: Vector3, tier_name: String, s: float, skull_s: float, fwd: float) -> void:
	if not TIER_LADDER.has(tier_name):
		return
	var pos := ground + Vector3(0.0, VERDICT_Y, 0.0) + _cam_back() * fwd
	var m := _mat(tier_color(tier_name), E_VERDICT)
	_torus(parent, ground + Vector3(0.0, OUT_RING_Y, 0.0), VERDICT_RING_R.x, VERDICT_RING_R.y, CIRCLE_SEGS, m)
	_tier_shape(parent, pos, tier_name, s, skull_s, m)


## L16/L17: a tier's shape facing the camera at pos: HOLDS a full shield, BATTERED a cracked shield, DAMAGED a broken
## heart, BREACHED a skull (scaled by skull_s), EVADED an open eye.
func _tier_shape(parent: Node3D, pos: Vector3, tier_name: String, s: float, skull_s: float, m: Material) -> void:
	match tier_name:
		"HOLDS":
			_shield_glyph(parent, pos, s, m, false)
		"BATTERED":
			_shield_glyph(parent, pos, s, m, true)
		"DAMAGED":
			_heart(parent, pos, s, m, true)
		"EVADED":
			_eye_glyph(parent, pos, s, m)
		_:
			_skull(parent, pos, skull_s, m)


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


## The target: a ghost sentry of the type (half alpha) and a ring in the type color. L14: with the card's verb glyph
## when verb is set. L16: at the fanned sentry slot while fanned; with drop, the pylon and shape drop in from above on
## a loop (DEPLOY).
func _resp_target(c: Vector2i, type: String, m: Material, verb: String = "", drop: bool = false) -> void:
	var pos := _grid_world(c) + _fan_vec(FAN_SENTRY)
	var gm := _mat_live(_type_col(type), E_SENTRY, RESP_GHOST_A)
	_resp_mats.append(gm)
	_torus(_resp_root, pos + Vector3(0.0, DECAL_Y + RING_Y * 0.5, 0.0), SENTRY_DECAL.x, SENTRY_DECAL.y, CIRCLE_SEGS, gm)
	var body: Node3D = _resp_root
	var bpos := pos
	if drop:
		var dh := Node3D.new()
		dh.position = pos
		dh.set_meta("base", pos)
		_resp_root.add_child(dh)
		_resp_drop.append(dh)
		body = dh
		bpos = Vector3.ZERO
	_cyl(body, bpos + Vector3(0.0, SENTRY_POLE.y * 0.5, 0.0), SENTRY_POLE.x, SENTRY_POLE.y, HEX, gm)
	var holder := _shape(body, bpos + Vector3(0.0, SENTRY_GLYPH_Y, 0.0), type, SENTRY_GLYPH_S, gm)
	if verb != "":
		var vm := _mat_live(WHITE, E_VERB, RESP_GHOST_A)
		_resp_mats.append(vm)
		_verb_badge(holder, verb, vm, false)
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


## L13 SACRIFICE: the cell crumbles to cobalt (a cobalt veil column, a cobalt hex ring, seeded debris falling through
## the veil in a loop) and a translucent shield dome with a shield glyph and a ring stands over our HQ.
func _resp_sacrifice(c: Vector2i) -> void:
	var pos := _grid_world(c)
	var m := _mat_live(COBALT, E_RESP)
	var veil := _mat_live(COBALT, E_FX * 0.5, SAC_VEIL_A)
	var hot := _mat_live(COBALT_HOT, E_RESP)
	_resp_mats.append_array([m, veil, hot])
	_torus(_resp_root, pos + Vector3(0.0, OUT_RING_Y, 0.0), HIT_MARK_R.x, HIT_MARK_R.y, HEX, m)
	_cyl(_resp_root, pos + Vector3(0.0, SAC_VEIL_H * 0.5, 0.0), DECAL_R, SAC_VEIL_H, HEX, veil)
	var rng := RandomNumberGenerator.new()
	rng.seed = SAC_SEED + c.x * SEED_MX + c.y * SEED_MY
	for i in range(SAC_N):
		var base := pos + Vector3(rng.randf_range(-SAC_SPREAD, SAC_SPREAD), rng.randf_range(SAC_Y.x, SAC_Y.y), rng.randf_range(-SAC_SPREAD, SAC_SPREAD))
		var cube := _box(_resp_root, base, Vector3.ONE * SAC_CUBE, hot)
		_resp_crumble.append({"node": cube, "base": base, "ph": rng.randf()})
	var hm := _mat_live(HOLD_COL, E_RESP)
	var dome := _mat_live(HOLD_COL, E_FX * 0.5, SAC_DOME_A)
	_resp_mats.append_array([hm, dome])
	var hp := _home_world() + Vector3(0.0, HQ_PLAT.y, 0.0)
	_sphere(_resp_root, hp, SAC_DOME_R, dome).scale = Vector3(1.0, SAC_DOME_STRETCH, 1.0)
	_torus(_resp_root, hp + Vector3(0.0, RING_Y, 0.0), HOME_MARK_R.x, HOME_MARK_R.y, CIRCLE_SEGS, hm)
	var holder := _facing(_resp_root, _home_world() + Vector3(0.0, SAC_SHIELD_Y, 0.0) + _cam_back() * SAC_SHIELD_FWD)
	holder.scale = Vector3.ONE * SAC_SHIELD_S
	_backing(holder, OUT_BACK_R)
	_shield_into(holder, hm)


## JAM: a red cross (pushed toward the camera) and a red ring over the hound, and the hound and its path dim. Uses the
## outcome hound, else the hunter-candidates hound (its lanes dim too), else the head of p.street. L14: gold adds a
## gold double edge under the hound. L16: every live hunter lane (both while sealed, the revealed one after the
## reveal) gets its pawprint crossed out too, so the hound reads struck out on its lanes.
func _resp_jam(p: Dictionary, gold: bool = false) -> void:
	var pos := Vector3.ZERO
	var have := false
	var dim: Array = []
	if is_instance_valid(_out_hound):
		pos = _out_hound.position
		have = true
		dim = _out_hound_mats.duplicate()
	elif is_instance_valid(_hc_hound) and not _hc_spawned:
		pos = _hc_hound.position
		have = true
		dim = _hc_hound_mats.duplicate()
		for ln: Dictionary in _hc_lanes:
			dim.append_array(ln["mats"])
	else:
		var sv: Variant = p.get("street", null)
		if sv is int:
			pos = _street_head(int(sv))
			have = true
	var m := _mat_live(RED, E_RESP)
	if have:
		_resp_mats.append(m)
		_torus(_resp_root, Vector3(pos.x, HL_Y, pos.z), RESP_JAM_R, RESP_JAM_R + HL_RING_W, CIRCLE_SEGS, m)
		var holder := _facing(_resp_root, Vector3(pos.x, RESP_JAM_Y, pos.z) + _cam_back() * RESP_JAM_FWD)
		for s: float in [1.0, -1.0]:
			_box(holder, Vector3.ZERO, RESP_JAM_BAR, m).rotation.z = s * PI * 0.25
		if gold:
			_gold_rings(_resp_root, Vector3(pos.x, 0.0, pos.z), RESP_JAM_R + GOLD_RING_GAP * 2.0)
	if not _hc_spawned:
		for i in range(_hc_lanes.size()):
			var ln: Dictionary = _hc_lanes[i]
			var rv: Variant = ln["root"]
			if not is_instance_valid(rv) or not (rv as Node3D).visible:
				continue
			if _hc_real >= 0 and i != _hc_real:
				continue
			if (ln["mats"] as Array).is_empty():
				continue
			if not _resp_mats.has(m):
				_resp_mats.append(m)
			var head: Vector3 = ln["head"]
			var lh := _facing(_resp_root, head + Vector3(0.0, HC_PAW_Y, 0.0) + _cam_back() * RESP_JAM_LANE_FWD)
			lh.scale = Vector3.ONE * RESP_JAM_LANE_K
			for s: float in [1.0, -1.0]:
				_box(lh, Vector3.ZERO, RESP_JAM_BAR, m).rotation.z = s * PI * 0.25
	if not dim.is_empty():
		_tint(dim, RESP_JAM_DIM, RESP_JAM_DIM)
		_resp_dim_mats = dim
		_resp_dimmed = true


# ======================= playout trails and marks =======================
## L15: the record of a playout line (made on first use): its beam key, every trail material, the nodes to thin when
## DONE, and the node holding its current-beam-only markers (blocks, hit glyphs, turn rings).
func _line_rec(line: int) -> Dictionary:
	if not _beam_rec.has(line):
		var marks := Node3D.new()
		_trail_root.add_child(marks)
		_beam_rec[line] = {"beam": "", "mats": [], "thin": [], "marks": marks, "done": false}
	return _beam_rec[line]


## L15: the node a line's current-beam-only markers go under, or null once the line is DONE (they are not drawn).
func _marks_of(line: int) -> Node3D:
	var rec := _line_rec(line)
	var mv: Variant = rec["marks"]
	if bool(rec["done"]) or not is_instance_valid(mv):
		return null
	return mv as Node3D


## L15: the line of the cue that moves is the current beam; every other line becomes DONE.
func _activate_line(line: int) -> void:
	var rec := _line_rec(line)
	var b := _cue_beam()
	if b != "":
		rec["beam"] = b
	if line == _active_line:
		return
	for k: Variant in _beam_rec.keys():
		if int(k) != line:
			_set_line_done(int(k))
	_active_line = line


## L15: a line's trail goes DONE: 25% alpha, low emission, thin lines; its block markers and hit glyphs go.
func _set_line_done(line: int) -> void:
	if not _beam_rec.has(line):
		return
	var rec: Dictionary = _beam_rec[line]
	if bool(rec["done"]):
		return
	rec["done"] = true
	var keep: Array = []
	for f: Dictionary in _trail_fade:
		if int(f.get("line", NO_LINE)) != line:
			keep.append(f)
	_trail_fade = keep
	_tint(rec["mats"], DONE_ALPHA_K, DONE_E_K)
	for e: Array in rec["thin"]:
		_thin(e[0], str(e[1]))
	if _trail_arrow.has(line):
		_thin(_trail_arrow[line], "arrow")
	var mv: Variant = rec["marks"]
	if is_instance_valid(mv):
		(mv as Node3D).queue_free()
	rec["marks"] = null
	if line == _active_line:
		_active_line = NO_LINE


## L15: thin a DONE trail node: a segment loses width, a dot shrinks flat, a chevron shrinks.
func _thin(nv: Variant, kind: String) -> void:
	if not is_instance_valid(nv):
		return
	var n: Node3D = nv
	match kind:
		"seg":
			n.scale = Vector3(n.scale.x, n.scale.y, n.scale.z * DONE_W_K)
		"dot":
			n.scale = Vector3(n.scale.x * DONE_W_K, n.scale.y, n.scale.z * DONE_W_K)
		_:
			n.scale = n.scale * DONE_W_K


func _trail_add(mats: Array, line: int = NO_LINE) -> void:
	if line != NO_LINE:
		var rec := _line_rec(line)
		(rec["mats"] as Array).append_array(mats)
		if bool(rec["done"]):
			_tint(mats, DONE_ALPHA_K, DONE_E_K)
			return
	if _instant:
		_tint(mats, TRAIL_REST, TRAIL_REST_E)
	else:
		_tint(mats, 1.0, 1.0)
		_trail_fade.append({"mats": mats, "t": 0.0, "line": line})


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
	var rec := _line_rec(line)
	var horiz := absf(d.x) >= absf(d.z)
	var road := _road_key(a0, horiz)
	var key := "%d|%s" % [line, road]
	if not _lane.has(key):
		_lane[key] = _lane_offset(_road_use, road)
	var lat := _lateral(horiz) * float(_lane[key])
	var m := _mat_live(col, E_TRAIL, TRAIL_ALPHA)
	var seg := _box(_trail_root, (a0 + b0) * 0.5 + lat, Vector3(flat, LANE_T, TRAIL_W), m)
	seg.rotation.y = _heading(d, 0.0)
	var dot := _cyl(_trail_root, b0 + lat, TRAIL_DOT_R, LANE_T * 1.5, HEX, m)
	(rec["thin"] as Array).append([seg, "seg"])
	(rec["thin"] as Array).append([dot, "dot"])
	if _trail_arrow.has(line):
		var old: Variant = _trail_arrow[line]
		if is_instance_valid(old):
			(old as Node3D).queue_free()
	var am := _mat_live(col, E_TRAIL, TRAIL_ALPHA)
	var arrow := _chevron(_trail_root, b0 + lat + d.normalized() * ARROW_L * 0.6, d.normalized(), am)
	_trail_arrow[line] = arrow
	if bool(rec["done"]):
		_thin(seg, "seg")
		_thin(dot, "dot")
		_thin(arrow, "arrow")
	_trail_add([m, am], line)


## A hit on the current beam: a type-colored hex ring and the stacked hit glyphs (current beam only, under its marks).
func _mark_hit(cell: Vector2i, type: String, line: int) -> void:
	var root := _marks_of(line)
	if root == null:
		return
	var m := _mat_live(_type_col(type), E_TRAIL, TRAIL_ALPHA)
	_torus(root, _grid_world(cell) + Vector3(0.0, RING_Y, 0.0), HIT_MARK_R.x, HIT_MARK_R.y, HEX, m)
	var hk := "%d|%s" % [line, str(cell)]
	var n := int(_hit_count.get(hk, 0))
	_hit_count[hk] = n + 1
	_shape(root, _grid_world(cell) + HIT_GLYPH_POS + HIT_GLYPH_STEP * float(n), type, HIT_GLYPH_S, m)
	_trail_add([m], line)


## L15: the small persistent red X on a cell hit this raid (one per cell, until the next raid's trails reset).
func _mark_hit_x(cell: Vector2i) -> void:
	if _hit_x.has(cell):
		return
	_hit_x[cell] = true
	var m := _mat(RED, E_HIT_X)
	var holder := _facing(_trail_root, _grid_world(cell) + HIT_X_POS)
	_backing(holder, HIT_X_BACK_R)
	for s: float in [1.0, -1.0]:
		_box(holder, Vector3(0.0, 0.0, HIT_X_Z), HIT_X_BAR, m).rotation.z = s * PI * 0.25


## A block on the current beam: a type-colored shield dome over the sentry and a bar across the lane where the line
## stopped (current beam only).
func _mark_block(cell: Vector2i, type: String, dir: Vector3, line: int) -> void:
	var root := _marks_of(line)
	if root == null:
		return
	var col := _type_col(type)
	var dm := _mat_live(col, E_FX, BLOCK_ALPHA)
	var dome := _sphere(root, _grid_world(cell), BLOCK_DOME_R, dm)
	dome.scale = Vector3(1.0, BLOCK_DOME_FLAT, 1.0)
	var bm := _mat_live(col, E_TRAIL, TRAIL_ALPHA)
	var flat := Vector3(dir.x, 0.0, dir.z)
	if flat.length() > EPS:
		var d := flat.normalized()
		var holder := Node3D.new()
		holder.position = _grid_world(cell) - d * BLOCK_BAR_BACK + Vector3(0.0, TRAIL_Y + BLOCK_BAR.y * 0.5, 0.0)
		holder.rotation.y = _heading(d, 0.0)
		root.add_child(holder)
		_box(holder, Vector3.ZERO, BLOCK_BAR, bm)
	_trail_add([dm, bm], line)


func _mark_home(line: int) -> void:
	var m := _mat_live(RED, E_TRAIL, TRAIL_ALPHA)
	_torus(_trail_root, _home_world() + Vector3(0.0, HQ_PLAT.y + RING_Y, 0.0), HOME_MARK_R.x, HOME_MARK_R.y, CIRCLE_SEGS, m)
	_trail_add([m], line)


func _mark_turn(cell: Vector2i, line: int) -> void:
	var root := _marks_of(line)
	if root == null:
		return
	var m := _mat_live(COBALT_HOT, E_TRAIL, TRAIL_ALPHA)
	_torus(root, _grid_world(cell) + Vector3(0.0, RING_Y, 0.0), TURN_MARK_R.x, TURN_MARK_R.y, CIRCLE_SEGS, m)
	_trail_add([m], line)


func _mark_jam(pos: Vector3, line: int) -> void:
	var m := _mat_live(RED, E_TRAIL, TRAIL_ALPHA)
	var holder := _facing(_trail_root, pos + Vector3(0.0, JAM_MARK_Y, 0.0))
	for s: float in [1.0, -1.0]:
		_box(holder, Vector3.ZERO, JAM_MARK, m).rotation.z = s * PI * 0.25
	_trail_add([m], line)


func _clear_trails() -> void:
	for ch in _trail_root.get_children():
		ch.queue_free()
	_trail_fade.clear()
	_trail_arrow.clear()
	_lane.clear()
	_road_use.clear()
	_hit_count.clear()
	_beam_rec.clear()
	_active_line = NO_LINE
	_hit_x.clear()


## Vehicles, effects, shakes, candidates (A and B) and trails go; planned paths, route verdicts, home glyphs, hunter
## street candidates, wound cards in flight and crack decals stay.
func _reset_motion() -> void:
	for v: Dictionary in _vehicles.values():
		(v["node"] as Node3D).queue_free()
	_vehicles.clear()
	_clear_fx()
	_clear_candidates()
	_clear_b_cands()
	_clear_trails()
	_cand_real = -1
	_b_real = -1
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


## The current cue's optional beam key ("" when absent).
func _cue_beam() -> String:
	if _qi >= 0 and _qi < _queue.size():
		return str((_queue[_qi] as Dictionary).get("beam", ""))
	return ""


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


## The vehicle of a line, made on first use. A new hunter starts where the hunter-candidates hound stands (that hound
## then hides and, L15, the candidate lanes fade), else it drops from the sky over drop_at. After a reveal, the first
## non-hunter vehicle takes over the lit A convoy (beam "sealed", or entering at its corp end); after REVEAL B, the
## lit B convoy (beam "sealed_b", or entering at its corp end). The waiting convoys then go.
func _vehicle_for(line: int, type: String, hunter: bool, cell: Vector2i, drop_at: Vector3) -> Dictionary:
	if _vehicles.has(line):
		var old: Dictionary = _vehicles[line]
		if bool(old["hunter"]) or not hunter:
			return old
		_kill_vehicle(line)
	var entry: Vector3 = (drop_at + Vector3(0.0, SPAWN_DROP, 0.0)) if hunter else _entry_point(line, cell)
	if hunter and is_instance_valid(_hc_hound) and not _hc_spawned:
		entry = Vector3(_hc_hound.position.x, 0.0, _hc_hound.position.z)
		_hc_spawned = true
		_hc_hound_vis()
		_hc_fade()
	var beam := _cue_beam()
	if not hunter and _cand_real >= 0 and beam != "sealed_b":
		for cv: Dictionary in _cands:
			if int(cv["route"]) == _cand_real and (beam == "sealed" or cell == Vector2i(_w - 1, _cand_real)):
				entry = (cv["node"] as Node3D).position
		_clear_candidates()
		_cand_real = -1
	elif not hunter and _b_real >= 0 and beam != "sealed":
		for bc: Dictionary in _bcands:
			var bn: Variant = bc["node"]
			if int(bc["route"]) == _b_real and is_instance_valid(bn) and (beam == "sealed_b" or cell == Vector2i(_w - 1, _b_real)):
				entry = (bn as Node3D).position
		_clear_b_cands()
		_b_real = -1
	var v := _make_vehicle(type, hunter, 1.0)
	var n: Node3D = v["node"]
	n.position = entry
	var target: Vector3 = drop_at if hunter else _world(cell, false)
	n.rotation.y = _heading(target - entry, HEADING_DOWN if hunter else HEADING_HOME)
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
	if is_instance_valid(_cand_q):
		_cand_q.queue_free()
	_cand_q = null
	_cand_q_holder = null
	_cand_q_mats.clear()


## L13: the shared "?" over the sealed candidates: one glyph above their middle, pushed toward the camera, with a thin
## tether down to each candidate's glyph.
func _build_cand_q() -> void:
	if _cands.is_empty():
		return
	_cand_q = Node3D.new()
	_fx_root.add_child(_cand_q)
	var c := Vector3.ZERO
	for cv: Dictionary in _cands:
		c += (cv["node"] as Node3D).position
	c /= float(_cands.size())
	_cand_q_base = Vector3(c.x, CQ_Y, c.z) + _cam_back() * CQ_FWD
	_cand_q_mats.clear()
	for cv: Dictionary in _cands:
		var tm := _mat_live(WHITE, E_PATH * PATH_DIM_K, CQ_TETHER_A)
		_cand_q_mats.append(tm)
		var g := (cv["node"] as Node3D).position + Vector3(0.0, VEH_GLYPH_Y - VEH_Y + CQ_TETHER_BOT, 0.0)
		_seg3(_cand_q, _cand_q_base - Vector3(0.0, CQ_TETHER_TOP, 0.0), g, CQ_TETHER_W, tm)
	_cand_q_holder = _qmark(_cand_q, _cand_q_base, CQ_S, WHITE)


## 0 = all three sealed and ghosted under the "?"; 1 = two dissolved, the real one lit, the "?" collapsed into it.
func _apply_reveal(u: float) -> void:
	var dst := _cand_q_base
	for cv: Dictionary in _cands:
		var n: Node3D = cv["node"]
		if _cand_real < 0:
			_tint(cv["mats"], 1.0, 1.0)
			n.scale = Vector3.ONE
			n.visible = true
		elif int(cv["route"]) == _cand_real:
			_tint(cv["mats"], lerpf(1.0, 1.0 / CAND_ALPHA, u), lerpf(1.0, E_CAND_LIT / E_VEH, u))
			dst = n.position + Vector3(0.0, VEH_GLYPH_Y - VEH_Y, 0.0)
		else:
			_tint(cv["mats"], 1.0 - u, 1.0 - u)
			n.scale = Vector3.ONE * lerpf(1.0, CAND_SHRINK, u)
			n.visible = u < 1.0
	if not is_instance_valid(_cand_q):
		return
	if _cand_real < 0:
		_cand_q.visible = true
		_tint(_cand_q_mats, 1.0, 1.0)
		if is_instance_valid(_cand_q_holder):
			_cand_q_holder.position = _cand_q_base
			_cand_q_holder.scale = Vector3.ONE * CQ_S
		return
	var e := _ease_out(u)
	_tint(_cand_q_mats, 1.0 - u, 1.0 - u)
	if is_instance_valid(_cand_q_holder):
		_cand_q_holder.position = _cand_q_base.lerp(dst, e)
		_cand_q_holder.scale = Vector3.ONE * CQ_S * maxf(1.0 - e, Q_MIN_S)
	_cand_q.visible = u < 1.0


func _face_all() -> void:
	var all: Array = _vehicles.values() + _cands + _bcands
	for v: Dictionary in all:
		for f: Node3D in v["faces"]:
			if is_instance_valid(f) and f.is_inside_tree():
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
		"reveal_b":
			return T_REVEAL_B
		"hunter_reveal":
			return T_HUNT_REVEAL
		"evaded":
			return T_EVADED
		"decay":
			return T_DECAY
		"fall":
			return T_FALL
		"wound":
			return T_WOUND_CUE
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
			_activate_line(line)
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
				_mark_hit(cell, type, line)
				_mark_hit_x(cell)
			elif kind == "block":
				_fx_shield(cell, type)
				_mark_block(cell, type, b - a, line)
		"home":
			_activate_line(line)
			var row := cell.y
			var v := _vehicle_for(line, type, false, Vector2i(-1, row), Vector3.ZERO)
			_aim(v, _home_entry(row))
			_cur_line = line
			_trail_seg(line, v["from"] as Vector3, v["to"] as Vector3, _type_col(type))
			_mark_home(line)
		"hunter_turn", "jam":
			_activate_line(line)
			var head := _street_head(cell.x)
			var v := _vehicle_for(line, type, true, cell, head)
			_aim(v, head)
			_cur_line = line
			_mark_turn(cell, line)
			if kind == "hunter_turn":
				v["rot_to"] = HEADING_DOWN
				v["turn_k"] = 1.0
			else:
				_fx_slash(head)
				_mark_jam(head, line)
		"reveal":
			if line >= 0:
				_cand_real = line
		"reveal_b":
			var br := int(cue.get("line", -1))
			if _b_has(br):
				_b_real = br
				var ground := _grid_world(Vector2i(_w - 1, br)) + Vector3(CAND_DX * CELL_DX, 0.0, 0.0)
				_fx_ring(ground, COBALT_HOT, B_RING_K)
		"hunter_reveal":
			var hi := int(cue.get("line", -1))
			if hi >= 0 and hi < _hc_lanes.size():
				_hc_real = hi
				if is_instance_valid(_hc_hound):
					_hc_from = _hc_hound.position
				var lane: Dictionary = _hc_lanes[hi]
				_fx_ring(lane["head"] as Vector3, COBALT_HOT, HC_RING_K)
		"evaded":
			_fx_label(_board_text("EVADED", SCRAMBLE_FX), Vector3(0.0, LABEL_Y, 0.0), ACID, LABEL_BIG)
		"decay":
			if _cell_root.has(cell):
				_status[cell] = "TAKEN"
				_sentries.erase(cell)
				_sentry_verb.erase(cell)
				_sentry_gold.erase(cell)
				_refresh_cell(cell)
				_fx_pulse(cell)
		"fall":
			_start_fall()
		"wound":
			var tv: Variant = cue.get("to", null)
			if tv is Vector2 and cell != NO_CELL:
				_start_wound(cell, tv as Vector2, null)
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
	elif kind == "reveal_b":
		_apply_b_reveal(u)
	elif kind == "hunter_reveal":
		_apply_hunter_reveal(u)
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
			_sentry_verb.erase(c)
			_sentry_gold.erase(c)
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
		"wound_rest":
			return
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
		_step_wounds(dt)
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
	var all: Array = _vehicles.values() + _cands + _bcands
	var gait := sin(_time * GAIT_HZ * TAU) * GAIT_AMP
	for v: Dictionary in all:
		var parts: Array = v["parts"]
		var hunter := bool(v["hunter"])
		for i in range(parts.size()):
			var p: Node3D = parts[i]
			if not is_instance_valid(p):
				continue
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
	if _b_real < 0 and not _b_pulse.is_empty():
		var bp := 1.0 - B_PULSE + B_PULSE * sin(_time * B_PULSE_HZ * TAU)
		_tint(_b_pulse, bp, bp)
	if not _ghost_mats.is_empty():
		var gp := 1.0 - OG_PULSE + OG_PULSE * (0.5 + 0.5 * sin(_time * OG_HZ * TAU))
		_tint(_ghost_mats, gp, gp)
	if not _resp_mats.is_empty():
		_tint(_resp_mats, 1.0, 1.0 - RESP_PULSE + RESP_PULSE * sin(_time * HL_HZ * TAU))
	for cb: Dictionary in _resp_crumble:
		var cn: Variant = cb["node"]
		if not is_instance_valid(cn):
			continue
		var node: Node3D = cn
		var cu := fposmod(_time * SAC_HZ + float(cb["ph"]), 1.0)
		var cbase: Vector3 = cb["base"]
		node.position = Vector3(cbase.x, lerpf(cbase.y, SAC_FLOOR_Y, cu * cu), cbase.z)
		node.rotation = Vector3(cu * SAC_SPIN, cu * SAC_SPIN * GLYPH_TILT, 0.0)
	for dv: Variant in _resp_drop:
		if not is_instance_valid(dv):
			continue
		var dn: Node3D = dv
		var du := fposmod(_time * RESP_DROP_HZ, 1.0)
		var dk := clampf(du / RESP_DROP_FALL, 0.0, 1.0)
		var db: Vector3 = dn.get_meta("base", dn.position)
		dn.position = db + Vector3(0.0, RESP_DROP_H * (1.0 - dk * dk), 0.0)
	if not _hg_mats.is_empty():
		_tint(_hg_mats, 1.0, 1.0 - HG_PULSE + HG_PULSE * sin(_time * HG_HZ * TAU))
	if _lethal and not _lethal_mats.is_empty():
		var lp := 0.5 + 0.5 * sin(_time * LETHAL_HZ * TAU)
		_tint(_lethal_mats, 1.0, lerpf(LETHAL_LOW, 1.0, lp))
		if is_instance_valid(_lethal_root):
			_lethal_root.scale = Vector3.ONE * LETHAL_SKULL_S * (1.0 + LETHAL_GROW * lp)
