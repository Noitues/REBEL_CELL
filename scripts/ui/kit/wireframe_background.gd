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


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	city = NeonCity.new()
	city.net_mode = true
	city.dim = 0.35
	city.city_seed = skyline_seed
	add_child(city)
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
