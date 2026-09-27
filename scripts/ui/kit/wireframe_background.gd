class_name WireframeBackground
extends Control
## The net (STYLE_GUIDE 1): the same isometric city as the physical world, re-rendered as
## cyberspace. Streets become cyan circuit traces, windows glow net colours and a faint
## wireframe grid floats over it all. `corp_creep` (0-1) lets corporate neon creep over
## the city as Heat rises (GDD 9.4). The grid scrolls slowly unless reduce-effects.

var corp_color: Color = Palette.CORP_SOLACE:
	set(v):
		if v != corp_color:
			corp_color = v
			_sync_city()
var corp_creep: float = 0.0:
	set(v):
		if not is_equal_approx(v, corp_creep):
			corp_creep = v
			_sync_city()
var floor_offset: float = 0.0
var skyline_seed: int = 7
var city: NeonCity
var _grid: Control
## ANIM-5 camera ease (4.14): the city hangs from this rig. The camera itself (the city's
## focus, anchor and zoom) always changes at once, so every fit and layout reads the
## real frame; the rig only moves the picture, from the old frame to the new one.
var rig: Control
## The old frame being held (screen points of two grid points) while the new one is
## worked out; empty when none.
var _held: Array = []
var _ease_tween: Tween = null
## Grid points whose screen positions pin down a frame (zoom and offset).
const CAMERA_PROBE_A := Vector2(0, 0)
const CAMERA_PROBE_B := Vector2(10, 0)
const CAMERA_MOTION := &"map_camera_ease"


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	city = NeonCity.new()
	city.net_mode = true
	city.follow_campaign = true  # territory influence (H20)
	city.dim = 0.35
	city.city_seed = skyline_seed
	rig = Control.new()
	rig.name = "CameraRig"
	rig.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rig.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(rig)
	rig.add_child(city)
	city.rebuilt.connect(_on_city_rebuilt)
	_grid = Control.new()
	_grid.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_grid.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_grid.draw.connect(_draw_grid)
	add_child(_grid)


func _ready() -> void:
	if RunManager.campaign != null:
		set_district(RunManager.campaign.corporation_id)


## Shows the district of the corporation being fought (its streets and its HQ).
func set_district(corporation_id: StringName) -> void:
	city.district = corporation_id


func _sync_city() -> void:
	if city == null:
		return
	city.corp_color = corp_color
	city.corp_creep = corp_creep
	city.refresh()


func _process(delta: float) -> void:
	if Settings.reduce_effects:
		return
	floor_offset = fmod(floor_offset + delta * 0.15, 1.0)
	_grid.queue_redraw()


func _draw_grid() -> void:
	# An isometric wireframe lattice over the city, drifting along one axis.
	var a := NeonCity.TILE_A * NeonCity.STREET_EVERY
	var b := NeonCity.TILE_B * NeonCity.STREET_EVERY
	var col := Color(Palette.NET_CYAN, 0.07)
	var shift := floor_offset * 2.0 * a
	var n := int((size.x + size.y * 2.0) / a) + 4
	for k in range(-n, n):
		var x0 := k * a * 2.0 + shift
		_grid.draw_line(Vector2(x0, 0), Vector2(x0 + size.y * a / b, size.y), col, 1.0)
		_grid.draw_line(Vector2(x0, 0), Vector2(x0 - size.y * a / b, size.y), col, 1.0)


# --- Camera ease (Animation pass ANIM-5, 4.14) -----------------------------------------------

## Screen positions (viewport px, the rig left out) of the two probe grid points under the
## city's current camera: they pin down the frame.
func camera_points() -> Array:
	var xf := get_global_transform_with_canvas() * city.get_transform()
	return [xf * city.grid_to_local(CAMERA_PROBE_A.x, CAMERA_PROBE_A.y), xf * city.grid_to_local(CAMERA_PROBE_B.x, CAMERA_PROBE_B.y)]


## Keeps the picture on the current frame while the camera changes (a page rebuilds and
## refits its map), until `ease_camera`. Nothing happens when motion doesn't play.
func hold_camera() -> void:
	if not Motion.live(CAMERA_MOTION) or not city.camera_settled():
		return
	if _ease_tween != null and _ease_tween.is_valid():
		_ease_tween.kill()
	_held = camera_points()


## True while an old frame is held or the picture eases to the new one.
func camera_easing() -> bool:
	return not _held.is_empty() or (_ease_tween != null and _ease_tween.is_valid())


## Eases the picture from the held frame to the camera's current one (map_camera_ease);
## at once when nothing is held or motion doesn't play.
func ease_camera() -> void:
	if _held.is_empty():
		return
	_apply_hold()
	_held = []
	if not Motion.live(CAMERA_MOTION):
		_rig_rest()
		return
	var e := Motion.entry(CAMERA_MOTION)
	_ease_tween = create_tween().set_parallel(true).set_ease(e.ease).set_trans(e.trans)
	_ease_tween.tween_property(rig, "position", Vector2.ZERO, Motion.seconds(CAMERA_MOTION))
	_ease_tween.tween_property(rig, "scale", Vector2.ONE, Motion.seconds(CAMERA_MOTION))
	_ease_tween.finished.connect(_rig_rest)


## Drops any hold or ease: the picture shows the camera's frame at once.
func settle_camera() -> void:
	_held = []
	if _ease_tween != null and _ease_tween.is_valid():
		_ease_tween.kill()
	_rig_rest()


## Runs `measure` with the rig at rest (fits and placements read the true frame).
func unrigged(measure: Callable) -> Variant:
	var pos := rig.position
	var scl := rig.scale
	rig.position = Vector2.ZERO
	rig.scale = Vector2.ONE
	var out: Variant = measure.call()
	rig.position = pos
	rig.scale = scl
	return out


func _on_city_rebuilt() -> void:
	if not _held.is_empty():
		_apply_hold()


## Rig transform that shows the held frame with the camera's current one.
func _apply_hold() -> void:
	var now := camera_points()
	var span := (now[1] as Vector2) - (now[0] as Vector2)
	var held_span := (_held[1] as Vector2) - (_held[0] as Vector2)
	if span.length() < 0.001:
		return
	var k := held_span.length() / span.length()
	var origin := get_global_transform_with_canvas().affine_inverse()
	# Screen x -> k x + t maps the new frame onto the held one; in the rig's parent space.
	var a: Vector2 = origin * (now[0] as Vector2)
	var b: Vector2 = origin * (_held[0] as Vector2)
	rig.scale = Vector2(k, k)
	rig.position = b - a * k


func _rig_rest() -> void:
	rig.position = Vector2.ZERO
	rig.scale = Vector2.ONE
	if city != null:
		city.refresh()
