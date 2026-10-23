class_name L8Board
extends Node3D
## The city view of raid lab L8 (SPEC section 8). It shows a dark slab city block in iso with a long lens, with our amber HQ
## on the left and the cobalt corp HQ on the right. Three lit routes and four cross streets run between them. Districts are
## small building clusters with rings, value pips and exploit keys. The board also draws sentries, the ghost, typed
## vehicles that travel the lines, the hunter hound, the sealed candidates, planned paths and the playout's trails.
## Everything is built in code, and it runs inside a SubViewport that the main scene creates. It holds no rule: the lab
## hands it the leg (`setup`), the state (`show_state`), planned lines (`show_paths`) and a playout's cues (`play`), and
## the board only draws them. The camera is fitted so the whole board sits in the free area left of the side panel.
## Cosmetic motion is seeded or time-based, never global random.

signal cues_finished

# ======================= tuning (palette, energies, camera, geometry, timings) =======================
const COBALT := Color8(61, 107, 255)
const COBALT_HOT := Color8(159, 192, 255)
const GOLD := Color8(255, 210, 77)
const AMBER := Color8(255, 176, 32)
const COPPER := Color8(201, 116, 26)
const ACID := Color8(212, 255, 0)
const RED := Color8(255, 61, 77)
const NET := Color8(92, 225, 255)
const SKY_WIRE := Color8(58, 143, 208)
const GREY := Color8(138, 146, 166)
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

const ALBEDO_K := 0.25
const ROUGH := 0.45
const METAL := 0.5
const E_ROUTE := 1.4
const E_ROUTE_CORE := 3.0
const E_STREET := 1.0
const E_GRID := 0.35
const E_RIM := 1.7
const E_RING := 2.6
const E_RING_DOWN := 1.1
const E_RING_DIM := 0.35
const E_DECAL := 0.8
const DECAL_A_OK := 0.16
const DECAL_A_DOWN := 0.08
const DECAL_A_TAKEN := 0.24
const E_WIN := 2.2
const E_WIN_DIM := 0.25
const E_WIN_DOWN := 1.2
const E_PIP := 2.6
const E_PIP_DIM := 0.45
const E_KEY := 3.0
const E_KEY_DIM := 0.8
const E_SENTRY := 3.4
const E_GHOST := 2.6
const E_VEH := 3.5
const E_CAND_LIT := 6.0
const E_FX := 5.0
const E_HQ_WIN := 2.0
const E_HQ_EDGE := 2.6
const E_BEACON := 3.0
const E_HL := 2.5
const E_SKY := 0.6
const E_MOTE := 2.0
const E_WRENCH := 1.8
const E_PATH := 2.6
const E_TRAIL := 4.0
const DECAL_ALPHA := 0.18
const HALO_ALPHA := 0.35
const HALO_E_K := 0.6

const AMBIENT_E := 0.55
const GLOW_INTENSITY := 0.8
const GLOW_STRENGTH := 1.1
const GLOW_BLOOM := 0.08
const GLOW_THRESHOLD := 0.95
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
const FIT_MARGIN := 40.0
## World units above the HQ pips kept inside the fitted box (tower tops, labels).
const FIT_HEADROOM := 0.6
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
## Layer heights above the roads: cell decals, planned paths, playout trails, highlights.
const DECAL_Y := 0.045
const DECAL_T := 0.006
const PATH_Y := 0.06
const TRAIL_Y := 0.08
const LANE_T := 0.012
const HL_Y := 0.1

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
## The cobalt hound: [position, size] boxes, forward +x, standing on the floor.
const HOUND_PARTS := [[Vector3(0.0, 0.42, 0.0), Vector3(0.52, 0.2, 0.22)], [Vector3(0.33, 0.56, 0.0), Vector3(0.2, 0.18, 0.18)], [Vector3(0.47, 0.53, 0.0), Vector3(0.12, 0.08, 0.1)], [Vector3(0.3, 0.7, 0.05), Vector3(0.05, 0.12, 0.04)], [Vector3(0.3, 0.7, -0.05), Vector3(0.05, 0.12, 0.04)], [Vector3(0.18, 0.2, 0.08), Vector3(0.05, 0.26, 0.05)], [Vector3(0.18, 0.2, -0.08), Vector3(0.05, 0.26, 0.05)], [Vector3(-0.18, 0.2, 0.08), Vector3(0.05, 0.26, 0.05)], [Vector3(-0.18, 0.2, -0.08), Vector3(0.05, 0.26, 0.05)], [Vector3(-0.32, 0.52, 0.0), Vector3(0.16, 0.04, 0.04)]]
const CAND_DX := 0.55
const CAND_ALPHA := 0.32
const CAND_SHRINK := 0.2

## Planned paths: dashed lanes, a chevron at the exit, the type glyph at the entry.
const LANE_GAP := 0.2
const PATH_W := 0.11
const DASH_L := 0.34
const DASH_G := 0.2
const PATH_ALPHA := 0.9
const PATH_DIM_K := 0.45
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

const SHIELD_R := Vector2(0.3, 0.9)
const STRIKE := Vector3(0.16, 5.0, 0.16)
const FLASH_R := Vector2(0.6, 1.6)
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
const HL_ALPHA := 0.35
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
var _yaw: float = deg_to_rad(CAM_YAW_DEG)
var _tilt: float = deg_to_rad(CAM_PITCH_DEG) * GLYPH_TILT
var _mats: Dictionary = {}
var _unit_box: BoxMesh
var _board: Node3D
var _path_root: Node3D
var _trail_root: Node3D
var _fx_root: Node3D
var _hl_root: Node3D
var _w: int = DEFAULT_W
var _h: int = DEFAULT_H
var _values: Dictionary = {}
var _exploits: Array = []
var _status: Dictionary = {}
var _sentries: Dictionary = {}
var _ghost_cell: Vector2i = NO_CELL
var _ghost_home: bool = false
var _home_hp: int = HOME_HP_MAX
var _heat: int = 0
var _cell_root: Dictionary = {}
var _cell_key: Dictionary = {}
var _win_mats: Dictionary = {}
var _spin: Array = []
var _home_root: Node3D
var _home_pips: Array = []
var _home_ghost: Node3D
var _beacon_mat: StandardMaterial3D
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
## Build the board for a leg: {w, h, values: {Vector2i: int}, exploits: Array[Vector2i]}.
func setup(leg: Dictionary) -> void:
	_w = int(leg.get("w", DEFAULT_W))
	_h = int(leg.get("h", DEFAULT_H))
	_values = (leg.get("values", {}) as Dictionary).duplicate()
	_exploits = (leg.get("exploits", []) as Array).duplicate()
	reset_playout()
	clear_highlight()
	_board.queue_free()
	_board = Node3D.new()
	add_child(_board)
	move_child(_board, 0)
	_cell_root.clear()
	_cell_key.clear()
	_win_mats.clear()
	_status.clear()
	_spin.clear()
	_home_ghost = null
	_build_floor()
	_build_roads()
	_build_skyline()
	_build_motes()
	_home_root = _build_hq(-1, AMBER, HQ_BODY_HOME)
	var corp := _build_hq(_w, COBALT, HQ_BODY_CORP)
	_beacon_mat = _mat_live(COBALT_HOT, E_BEACON)
	_sphere(corp, Vector3(0.0, HQ_PLAT.y + HQ_TIERS * HQ_TIER_H + HQ_BEACON_R, 0.0), HQ_BEACON_R, _beacon_mat)
	_build_home_pips()
	for c: Vector2i in _cells():
		var root := Node3D.new()
		root.position = _grid_world(c)
		_board.add_child(root)
		_cell_root[c] = root
		_status[c] = "NEUTRAL"
		_refresh_cell(c)
	_fit_camera()


## Show a state {owned: {cell: OK/DOWN/TAKEN}, home_hp, heat} and a placement {sentries: {cell: D/N/E}, ghost: cell|"HOME"|null}.
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


## The sealed candidates [{route, type}]: real -1 = ghosted convoys at the corp end (a new raid: vehicles, effects and
## trails are reset, planned paths stay); real >= 0 = the settled reveal (two gone, the real one lit).
func show_candidates(cands: Array, real: int = -1) -> void:
	if real < 0 or _cands.is_empty():
		if real < 0:
			_reset_motion()
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


## Draw planned lines (line dictionaries {kind, index, cells, type, home}, optional dim: bool) as type-colored dashed
## lanes along their roads, each with its type glyph at the entry and a chevron at the exit (routes end into HOME).
## Replaces any paths shown before.
func show_paths(lines: Array) -> void:
	clear_paths()
	for lv: Variant in lines:
		if lv is Dictionary:
			_draw_path(lv as Dictionary)


## Remove every planned path.
func clear_paths() -> void:
	for ch in _path_root.get_children():
		ch.queue_free()
	_path_use.clear()


## Play cues in order (beam_step, block, hit, home, hunter_turn, jam, reveal, evaded) and emit cues_finished at the end.
## Planned paths are cleared; every beam leaves a trail with its hits and stops until reset_playout().
func play(cues: Array, speed: float = 1.0) -> Signal:
	clear_paths()
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
		var m := _mat_live(color, E_HL, HL_ALPHA)
		var root := Node3D.new()
		root.position = pos + Vector3(0.0, HL_Y, 0.0)
		_hl_root.add_child(root)
		_cyl(root, Vector3.ZERO, HL_R, ROAD_T, CIRCLE_SEGS, m)
		_torus(root, Vector3.ZERO, HL_R, HL_R + RIM_W, CIRCLE_SEGS, m)
		_hl.append(m)


## Remove every highlight.
func clear_highlight() -> void:
	for ch in _hl_root.get_children():
		ch.queue_free()
	_hl.clear()


## Drop every vehicle, effect, shake, candidate, trail and planned path (a fresh raid).
func reset_playout() -> void:
	_reset_motion()
	clear_paths()


# ======================= camera fit =======================
func _view_size() -> Vector2:
	if is_inside_tree():
		var s := get_viewport().get_visible_rect().size
		if s.x > 0.0 and s.y > 0.0:
			return s
	return FIT_VIEW


func _slab_half() -> Vector2:
	return Vector2((_w + 1) * 0.5 * CELL_DX + SLAB_PAD.x, (_h - 1) * 0.5 * CELL_DZ + SLAB_PAD.y)


## Fit the camera: aim at the board box (slab, both HQs, tower headroom), pick the distance so its 8 projected corners
## fill the free area, and shift the image there with h_offset / v_offset (camera-plane units). Same math as Godot's
## perspective projection (KEEP_HEIGHT), so cell_screen_pos matches what is drawn.
func _fit_camera() -> void:
	if cam == null:
		return
	var cb := Basis.from_euler(Vector3(deg_to_rad(CAM_PITCH_DEG), deg_to_rad(CAM_YAW_DEG), 0.0))
	var half := _slab_half()
	var top := HQ_PLAT.y + HQ_TIERS * HQ_TIER_H + HOME_PIP_Y + FIT_HEADROOM
	var box := AABB(Vector3(-half.x, 0.0, -half.y), Vector3(half.x * 2.0, top, half.y * 2.0))
	var center := box.get_center()
	var inv := cb.transposed()
	var rel: Array[Vector3] = []
	for i in range(8):
		rel.append(inv * (box.get_endpoint(i) - center))
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
	var d := box.size.length() / ty
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
	match type:
		"D":
			_cyl(holder, Vector3.ZERO, s, SHAPE_DEPTH, TRI_SEGS, mat).rotation.x = -PI * 0.5
		"N":
			_box(holder, Vector3.ZERO, Vector3(s * SQUARE_K, s * SQUARE_K, SHAPE_DEPTH), mat)
		_:
			_cyl(holder, Vector3.ZERO, s, SHAPE_DEPTH, CIRCLE_SEGS, mat).rotation.x = -PI * 0.5
	return holder


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
	for x in range(_w):
		var px := _grid_world(Vector2i(x, 0)).x
		_box(_board, Vector3(px, ROAD_Y + STREET_LIFT * 2.0, (z0 + z1) * 0.5), Vector3(STREET_W, ROAD_T, z1 - z0), _mat(COPPER, E_STREET))


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
## corner edges and crowns in the HQ's color, window bands, a light.
func _build_hq(xcol: int, col: Color, body_col: Color) -> Node3D:
	var root := Node3D.new()
	root.position = Vector3(_grid_world(Vector2i(xcol, 0)).x, 0.0, 0.0)
	_board.add_child(root)
	var depth := (_h - 1) * CELL_DZ + ROUTE_W * 2.0
	_box(root, Vector3(0.0, HQ_PLAT.y * 0.5, 0.0), Vector3(HQ_PLAT.x, HQ_PLAT.y, depth), _solid(STEEL))
	var edge := _mat(col, E_RING)
	for s: float in [-1.0, 1.0]:
		_box(root, Vector3(HQ_PLAT.x * 0.5 * s, HQ_PLAT.y, 0.0), Vector3(RIM_W, ROAD_T, depth), edge)
	var body := _solid(body_col)
	var accent := _mat(col, E_HQ_EDGE)
	var win := _mat(HOT_WIN if col == AMBER else COBALT_HOT, E_HQ_WIN)
	for i in range(HQ_TIERS):
		var s := HQ_BASE - i * HQ_STEP
		var y := HQ_PLAT.y + (i + 0.5) * HQ_TIER_H
		var th := HQ_TIER_H * 0.92
		_box(root, Vector3(0.0, y, 0.0), Vector3(s, th, s), body)
		for cx: float in [-1.0, 1.0]:
			for cz: float in [-1.0, 1.0]:
				_box(root, Vector3(cx * s * 0.5, y, cz * s * 0.5), Vector3(HQ_EDGE_W, th, HQ_EDGE_W), accent)
		var ty := y + th * 0.5
		for sd: float in [-1.0, 1.0]:
			_box(root, Vector3(0.0, ty, sd * s * 0.5), Vector3(s, HQ_EDGE_W, HQ_EDGE_W), accent)
			_box(root, Vector3(sd * s * 0.5, ty, 0.0), Vector3(HQ_EDGE_W, HQ_EDGE_W, s), accent)
		for k in range(HQ_WIN_ROWS):
			var wy := y + (k - (HQ_WIN_ROWS - 1) * 0.5) * HQ_TIER_H / float(HQ_WIN_ROWS + 1)
			_box(root, Vector3(0.0, wy, s * 0.5 + WIN_EPS), Vector3(s * WIN_FRAC, WIN_H, WIN_EPS), win)
			_box(root, Vector3(-s * 0.5 - WIN_EPS, wy, 0.0), Vector3(WIN_EPS, WIN_H, s * WIN_FRAC), win)
	var lt := OmniLight3D.new()
	lt.light_color = WARM_LIGHT if col == AMBER else COBALT
	lt.light_energy = HQ_LIGHT_E
	lt.omni_range = HQ_LIGHT_RANGE
	lt.position = Vector3(0.0, HQ_LIGHT_Y, 0.0)
	root.add_child(lt)
	return root


func _build_home_pips() -> void:
	_home_pips.clear()
	var holder := _facing(_home_root, Vector3(0.0, HQ_PLAT.y + HQ_TIERS * HQ_TIER_H + HOME_PIP_Y, 0.0))
	for i in range(HOME_HP_MAX):
		_home_pips.append(_box(holder, Vector3((i - (HOME_HP_MAX - 1) * 0.5) * HOME_PIP_GAP, 0.0, 0.0), HOME_PIP, _mat(GOLD, E_PIP)))
	_refresh_pips()


func _refresh_pips() -> void:
	for i in range(_home_pips.size()):
		(_home_pips[i] as MeshInstance3D).material_override = _mat(GOLD, E_PIP) if i < _home_hp else _mat(RED, E_PIP)


func _refresh_home_ghost() -> void:
	if _home_ghost != null:
		_home_ghost.queue_free()
		_home_ghost = null
	if _ghost_home and _home_root != null:
		_home_ghost = _dashed_ring(_home_root, GHOST_HOME_R, _mat(GOLD, E_GHOST))


# ======================= districts =======================
func _refresh_cell(c: Vector2i) -> void:
	var st: String = _status.get(c, "NEUTRAL")
	var sen := str(_sentries.get(c, ""))
	var key := "%s|%s|%s" % [st, sen, c == _ghost_cell]
	if str(_cell_key.get(c, "")) == key:
		return
	_cell_key[c] = key
	_rebuild_cell(c, st, sen)


## NEUTRAL: dim gray. OK: warm amber ring, decal and lit pips. DOWN: dim amber, a wrench and flicker. TAKEN: cobalt.
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


func _build_sentry(root: Node3D, type: String) -> void:
	var col := _type_col(type)
	var m := _mat(col, E_SENTRY)
	_torus(root, Vector3(0.0, DECAL_Y + RING_Y * 0.5, 0.0), SENTRY_DECAL.x, SENTRY_DECAL.y, CIRCLE_SEGS, m)
	_cyl(root, Vector3(0.0, DECAL_Y + DECAL_T, 0.0), SENTRY_DECAL.x, DECAL_T, CIRCLE_SEGS, _mat(col, E_SENTRY * HALO_E_K, DECAL_ALPHA))
	_cyl(root, Vector3(0.0, SENTRY_BASE.y * 0.5, 0.0), SENTRY_BASE.x, SENTRY_BASE.y, HEX, _solid(STEEL))
	_cyl(root, Vector3(0.0, SENTRY_POLE.y * 0.5, 0.0), SENTRY_POLE.x, SENTRY_POLE.y, HEX, _mat(col, E_SENTRY * HALO_E_K))
	_shape(root, Vector3(0.0, SENTRY_GLYPH_Y, 0.0), type, SENTRY_GLYPH_S, m)


# ======================= planned paths =======================
## One planned line: a dashed lane from its entry to its exit (HOME platform for routes), glyph at entry, chevron at exit.
func _draw_path(ln: Dictionary) -> void:
	var cells: Array = ln.get("cells", [])
	if cells.is_empty():
		return
	var type := str(ln.get("type", "D"))
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
	a.y = PATH_Y
	b.y = PATH_Y
	var d := b - a
	var length := d.length()
	if length < EPS:
		return
	var dir := d / length
	var lat := _lateral(horiz) * _lane_offset(_path_use, _road_key(a, horiz))
	var k := PATH_DIM_K if bool(ln.get("dim", false)) else 1.0
	var m := _mat(_type_col(type), E_PATH * k, PATH_ALPHA * k)
	var rot := _heading(dir, 0.0)
	var stop := length - ARROW_L * 0.3
	var u := 0.0
	while u < stop:
		var e := minf(u + DASH_L, stop)
		_box(_path_root, a + dir * ((u + e) * 0.5) + lat, Vector3(e - u, LANE_T, PATH_W), m).rotation.y = rot
		u += DASH_L + DASH_G
	_chevron(_path_root, b + lat, dir, m)
	_shape(_path_root, a + lat + Vector3(0.0, PATH_GLYPH_Y, 0.0), type, PATH_GLYPH_S, m)


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


## Vehicles, effects, shakes, candidates and trails go; planned paths stay.
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
func _make_vehicle(type: String, hunter: bool, alpha: float) -> Dictionary:
	var root := Node3D.new()
	_fx_root.add_child(root)
	var col: Color = COBALT_HOT if hunter else _type_col(type)
	var m := _mat_live(col, E_VEH, alpha)
	var parts: Array = []
	var faces: Array = []
	var base_y := 0.0 if hunter else VEH_Y
	if hunter:
		for p: Array in HOUND_PARTS:
			var pos: Vector3 = p[0]
			var size: Vector3 = p[1]
			_box(root, pos, size, m)
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
	var halo := _mat_live(col, E_VEH * HALO_E_K, alpha * HALO_ALPHA)
	_torus(root, Vector3(0.0, RING_Y - base_y, 0.0), HALO.x, HALO.y, CIRCLE_SEGS, halo)
	return {"node": root, "mats": [m, halo], "parts": parts, "faces": faces, "hunter": hunter, "type": type,
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
			_trail_seg(line, a, b, COBALT_HOT if hunter else _type_col(type))
			if kind == "hit":
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
			_fx_label("EVADED", Vector3(0.0, LABEL_Y, 0.0), ACID, LABEL_BIG)
	if _instant:
		_update_cue(1.0)


func _update_cue(u: float) -> void:
	if _cur_line != NO_LINE and _vehicles.has(_cur_line):
		var v: Dictionary = _vehicles[_cur_line]
		var n: Node3D = v["node"]
		n.position = (v["from"] as Vector3).lerp(v["to"], _ease_out(u))
		n.rotation.y = lerp_angle(float(v["rot_from"]), float(v["rot_to"]), minf(1.0, u * float(v["turn_k"])))
	if str(_cur_cue.get("kind", "")) == "reveal":
		_apply_reveal(u)


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
	var l := Label3D.new()
	l.text = text
	l.font_size = size
	l.pixel_size = LABEL_PX
	l.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	l.no_depth_test = true
	l.modulate = col
	l.outline_size = LABEL_OUTLINE
	l.outline_modulate = SHADOW_INK
	l.position = pos
	_fx_root.add_child(l)
	_fx_add(l, "label", FX_LABEL_T, [])


func _clear_fx() -> void:
	for f: Dictionary in _fx:
		var n: Node3D = f["node"]
		if is_instance_valid(n):
			n.queue_free()
	_fx.clear()


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
	for v: Dictionary in all:
		var parts: Array = v["parts"]
		for i in range(parts.size()):
			var p: Node3D = parts[i]
			var base: Vector3 = p.get_meta("base", p.position)
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
	for c: Vector2i in _win_mats:
		if str(_status.get(c, "")) != "DOWN":
			continue
		var n := sin(float(floori(_time * FLICKER_HZ)) * HASH_A + c.x * HASH_B + c.y * HASH_C) * HASH_D
		var on := n - floorf(n) > FLICKER_ON
		(_win_mats[c] as StandardMaterial3D).emission_energy_multiplier = E_WIN_DOWN * (1.0 if on else FLICKER_LOW)
	var pulse := 1.0 - HL_PULSE + HL_PULSE * sin(_time * HL_HZ * TAU)
	_tint(_hl, pulse, pulse)
