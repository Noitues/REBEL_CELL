class_name CityLife
extends Control
## The city's T0 life (art pass W7, ART_BIBLE §9.2, §8 T0): aircraft crossing with their
## navigation blinkers, occasional drone patrols (FLAGGED adds patrols with red/blue lights,
## §9.3) and billboards looping in their corporation's hue **and** pattern (CorpPattern). The
## existing traffic dashes and window lights stay NeonCity's (its live layer); the window
## lights' toggle period is floored at T0's 3 s there (city_lights.gdshader).
##
## Deterministic: `frame()` is a pure function of the time, the seed, the state and the
## view (hashes, never an RNG), so the same inputs give the same draw list. Density follows
## Heat (`life_density` per band). Under reduce effects nothing moves: aircraft and drones
## are not drawn and billboards hold their first frame (the static end state), and the
## layer never redraws per frame. Items inside a UI calm zone are left out (nothing moves
## behind text). All periods are T0's (>= 3 s, CityLookData.validate); blinkers are small
## and slow, never a flash.

## World px per grid lot (NeonCity's iso tile).
const TILE := Vector2(NeonCity.TILE_A, NeonCity.TILE_B)
## Hash salts (one per kind of item and property).
const SALT_AIR := 401
const SALT_DRONE := 433
const SALT_BOARD := 467
## An aircraft's lane leans at most this far from level (radians), and flies this far past
## the view's edges (share of the view's width).
const AIR_TILT := 0.35
const AIR_OVERSHOOT := 0.15
## The billboards' loop has this many frames.
const BOARD_FRAMES := 3

var city: NeonCity
var state: CityState
var cfg: CityLookData
## Billboard anchors: [{"at": Vector2 (world px, the panel's foot), "corp": StringName}], worked
## out by CityAtmosphere from the city's roofs when the camera changes.
var boards: Array[Dictionary] = []
## Where patrols circle (world px): the target corp's HQ and the claimed Sites.
var patrol_points: PackedVector2Array = PackedVector2Array()
## Calm zones in the city's local px (items inside are left out).
var calm_local: Array[Rect2] = []
## The clock the layer draws at (seconds; frozen under reduce effects).
var t: float = 0.0
## The last draw list (tests and the lab read it).
var last_items: Array[Dictionary] = []
## Billboards live on a layer of their own that redraws only when a board changes frame or the
## camera moves (their corp patterns cost too much to redraw every frame; §13).
var _boards: Control
var _boards_sig: Array = []
## Redraws of the billboard layer so far (tests).
var board_redraws: int = 0


func _init() -> void:
	name = "CityLife"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_boards = Control.new()
	_boards.name = "CityBillboards"
	_boards.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_boards.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_boards.show_behind_parent = true
	_boards.draw.connect(_draw_boards)
	add_child(_boards)


## The draw list at time `p_t` (pure): aircraft, drones and billboards in world px.
## `view` is the world rect shown; `reduce` is reduce effects (the static end state).
static func frame(p_t: float, p_seed: int, p_state: CityState, view: Rect2, p_cfg: CityLookData, reduce: bool,
		p_boards: Array[Dictionary], p_patrols: PackedVector2Array) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var density: float = p_cfg.life_density[clampi(p_state.band, 0, p_cfg.life_density.size() - 1)]
	# Billboards (fixtures: they stay, at their first frame, under reduce effects).
	var nb := mini(p_boards.size(), roundi(p_cfg.billboards_max * density))
	for i in nb:
		var b: Dictionary = p_boards[i]
		var at: Vector2 = b["at"]
		var ph := hash01(p_seed, SALT_BOARD, i)
		var f := 0 if reduce else int(fposmod(p_t / p_cfg.billboard_period + ph, 1.0) * BOARD_FRAMES) % BOARD_FRAMES
		out.append({"kind": &"billboard", "pos": at, "corp": b["corp"], "frame": f, "i": i})
	if reduce:
		return out
	# Aircraft crossing the view on straight lanes, blinking.
	var na := roundi(p_cfg.aircraft_max * density)
	for i in na:
		var tilt := (hash01(p_seed, SALT_AIR, i * 4) - 0.5) * 2.0 * AIR_TILT
		var dir := Vector2(cos(tilt), sin(tilt)) * (1.0 if hash01(p_seed, SALT_AIR, i * 4 + 1) < 0.5 else -1.0)
		var y := view.position.y + view.size.y * lerpf(0.08, 0.92, hash01(p_seed, SALT_AIR, i * 4 + 2))
		var span := view.size.x * (1.0 + AIR_OVERSHOOT * 2.0)
		var cross := p_cfg.aircraft_cross_seconds * lerpf(0.8, 1.25, hash01(p_seed, SALT_AIR, i * 4 + 3))
		var k := fposmod(p_t / cross + hash01(p_seed, SALT_AIR, i * 7 + 5), 1.0)
		var mid := Vector2(view.get_center().x, y)
		var pos := mid + dir * (k - 0.5) * span
		var blink := fposmod(p_t / p_cfg.aircraft_blink_period + hash01(p_seed, SALT_AIR, i * 7 + 6), 1.0) < p_cfg.aircraft_blink_on
		out.append({"kind": &"aircraft", "pos": pos, "dir": dir, "blink": blink, "i": i})
	# Drone patrols round the patrol points: occasional at COOL, always out and lit red/blue
	# from FLAGGED (their light alternates at most `flagged_flicker_hz`, §9.3).
	if not p_patrols.is_empty():
		var nd := roundi(p_cfg.drones_max * density)
		var police := p_state.patrols()
		if police:
			nd += p_cfg.flagged_drones
		for i in nd:
			var centre: Vector2 = p_patrols[i % p_patrols.size()]
			var ph := hash01(p_seed, SALT_DRONE, i)
			var loop := fposmod(p_t / p_cfg.drone_period + ph, 1.0)
			var patrol := police and i >= nd - p_cfg.flagged_drones
			if not patrol and loop > p_cfg.drone_out_share:
				continue
			var a := TAU * loop * (1.0 if hash01(p_seed, SALT_DRONE, i + 50) < 0.5 else -1.0) + ph * TAU
			var r := p_cfg.drone_radius_lots * lerpf(0.6, 1.2, hash01(p_seed, SALT_DRONE, i + 90))
			var pos := centre + Vector2(cos(a) * TILE.x, sin(a) * TILE.y) * r
			var red := fposmod(p_t * p_cfg.flagged_flicker_hz + ph, 1.0) < 0.5
			out.append({"kind": &"drone", "pos": pos, "patrol": patrol, "red": red, "i": i})
	return out


## Deterministic 0..1 hash of (seed, salt, n) (view decoration only).
static func hash01(p_seed: int, salt: int, n: int) -> float:
	var h := (n * 73856093) ^ (salt * 19349663) ^ (p_seed * 83492791)
	h = (h ^ (h >> 13)) * 1274126177
	h = h ^ (h >> 16)
	return float(h & 0xFFFF) / 65535.0


## Works out the draw list at the current clock and redraws.
func refresh_items() -> void:
	if city == null or state == null or cfg == null:
		return
	var off := Vector2(city._ox, city._oy)
	var view := Rect2(-off, city.size)
	var items := frame(t, city.city_seed, state, view, cfg, not Fx.effects_enabled(), boards, patrol_points)
	last_items = []
	for it in items:
		var local: Vector2 = (it["pos"] as Vector2) + off
		var hidden := false
		for r in calm_local:
			if r.has_point(local):
				hidden = true
				break
		if not hidden:
			last_items.append(it)
	var sig: Array = [off]
	for it in last_items:
		if it["kind"] == &"billboard":
			sig.append([it["i"], it["frame"]])
	if sig != _boards_sig:
		_boards_sig = sig
		_boards.queue_redraw()
	queue_redraw()


func _draw_boards() -> void:
	if city == null:
		return
	board_redraws += 1
	var off := Vector2(city._ox, city._oy)
	for it in last_items:
		if it["kind"] == &"billboard":
			_draw_board((it["pos"] as Vector2) + off, it["corp"], int(it["frame"]), int(it["i"]))


func _draw() -> void:
	if city == null:
		return
	var off := Vector2(city._ox, city._oy)
	for it in last_items:
		var p: Vector2 = (it["pos"] as Vector2) + off
		match it["kind"]:
			&"aircraft":
				_draw_aircraft(p, it["dir"], bool(it["blink"]))
			&"drone":
				_draw_drone(p, bool(it["patrol"]), bool(it["red"]))


## A billboard on a roof: a dark panel filled with its corp's pattern in its hue, looping
## through three frames (pattern, hue panel with the pattern cut dark, pattern with scan bars).
func _draw_board(foot: Vector2, corp: StringName, f: int, i: int) -> void:
	var ci := _boards
	var s := cfg.billboard_size_px
	var along := Vector2(TILE.x, TILE.y).normalized() * s.x * (1.0 if i % 2 == 0 else -1.0)
	along.y = absf(along.y) * (1.0 if i % 2 == 0 else -1.0)
	var up := Vector2(0, -s.y)
	var lift := Vector2(0, -s.y * 0.4)
	var pts := PackedVector2Array([foot + lift, foot + lift + along, foot + lift + along + up, foot + lift + up])
	var hue := Palette.corp_color(corp)
	var kind := Palette.corp_pattern_id(corp)
	var a := cfg.billboard_alpha
	# Its glow on the haze, then the panel.
	var glow := PackedVector2Array([pts[0] + Vector2(-3, 3), pts[1] + Vector2(3, 3), pts[2] + Vector2(3, -3), pts[3] + Vector2(-3, -3)])
	ci.draw_colored_polygon(glow, Color(hue, 0.12 * a))
	ci.draw_colored_polygon(pts, Color(CityPalette.SHADE, 0.85))
	match f:
		0:
			CorpPattern.fill_polygon(ci, pts, kind, Color(hue, a), 0.5)
		1:
			ci.draw_colored_polygon(pts, Color(hue, 0.55 * a))
			CorpPattern.fill_polygon(ci, pts, kind, Color(CityPalette.SHADE, 0.7), 0.5)
		_:
			CorpPattern.fill_polygon(ci, pts, kind, Color(hue, 0.6 * a), 0.5)
			for k in 3:
				var v := (k + 0.5) / 3.0
				ci.draw_line(pts[0].lerp(pts[3], v), pts[1].lerp(pts[2], v), Color(hue, a), 1.5)
	ci.draw_polyline(pts + PackedVector2Array([pts[0]]), Color(hue, a), 1.2)
	# The mast under it.
	ci.draw_line(foot, foot + lift, Color(hue, 0.5 * a), 1.0)


## An aircraft: a short body with its red nav light and a white strobe while it blinks.
func _draw_aircraft(p: Vector2, dir: Vector2, blink: bool) -> void:
	draw_line(p - dir * 4.0, p + dir * 4.0, Color(CityPalette.NAV_WHITE, 0.35), 1.5)
	draw_circle(p - dir * 4.0, 1.4, Color(CityPalette.NAV_RED, 0.9))
	if blink:
		draw_circle(p + dir * 4.0, 5.0, Color(CityPalette.NAV_WHITE, 0.18))
		draw_circle(p + dir * 4.0, 1.8, CityPalette.NAV_WHITE)


## A drone: a small body with its light; a patrol's light alternates red and blue and casts
## a faint cone on the street below.
func _draw_drone(p: Vector2, patrol: bool, red: bool) -> void:
	var col := CityPalette.NAV_WHITE
	if patrol:
		col = CityPalette.POLICE_RED if red else CityPalette.POLICE_BLUE
		draw_colored_polygon(PackedVector2Array([p, p + Vector2(-9, 26), p + Vector2(9, 26)]), Color(col, 0.08))
	draw_circle(p, 9.0, Color(col, 0.2))
	draw_line(p + Vector2(-4, 0), p + Vector2(4, 0), Color(CityPalette.NAV_WHITE, 0.5), 1.2)
	draw_circle(p, 1.7, col)
