class_name CyberdeckBackground
extends Control
## The physical world (STYLE_GUIDE 1): the Cell's room at night. A big rain-streaked
## window looks down on the isometric neon city (NeonCity); dark mullions frame it and a
## worn metal deck edge sits at the bottom. Rain animates unless reduce-effects.
## Searchlights sweep past the window as Heat rises (GDD 9.4).

var heat_band: int = 0:
	set(v):
		heat_band = v
		if _frame != null:
			_frame.queue_redraw()
var city: NeonCity
var _frame: Control
var _search_t: float = 0.0


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	city = NeonCity.new()
	city.rain = true
	city.dim = 0.2
	add_child(city)
	_frame = Control.new()
	_frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_frame.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_frame.draw.connect(_draw_frame)
	add_child(_frame)


func _ready() -> void:
	if RunManager.campaign != null:
		set_district(RunManager.campaign.corporation_id)


## The window looks out on the district of the corporation being fought.
func set_district(corporation_id: StringName) -> void:
	city.district = corporation_id


func _process(delta: float) -> void:
	if Settings.reduce_effects or heat_band <= 0:
		return
	_search_t += delta
	_frame.queue_redraw()


func _draw_frame() -> void:
	var s := size
	var bar := Color("#05060C")
	var edge := Color(Palette.NET_CYAN, 0.12)
	# Heat searchlights sweep across the glass.
	if heat_band > 0:
		var sx := fmod(_search_t * 120.0 * heat_band, s.x + 400.0) - 200.0
		_frame.draw_colored_polygon(PackedVector2Array([Vector2(sx, s.y), Vector2(sx + 90, s.y), Vector2(sx + 320, 0), Vector2(sx + 160, 0)]), Color(Palette.PAPER, 0.05 * heat_band))
	# Window mullions: two verticals and a transom, each with a faint neon catch-light.
	for fx in [s.x * 0.34, s.x * 0.67]:
		_frame.draw_rect(Rect2(fx - 7, 0, 14, s.y), bar)
		_frame.draw_line(Vector2(fx + 7, 0), Vector2(fx + 7, s.y), edge, 1.0)
	_frame.draw_rect(Rect2(0, s.y * 0.07 - 5, s.x, 10), bar)
	_frame.draw_line(Vector2(0, s.y * 0.07 + 5), Vector2(s.x, s.y * 0.07 + 5), edge, 1.0)
	# The deck edge: worn metal lip with screws and a pink under-glow.
	var deck_y := s.y - 18.0
	_frame.draw_rect(Rect2(0, deck_y, s.x, 18), Palette.DESK_DARK)
	_frame.draw_rect(Rect2(0, deck_y, s.x, 3), Palette.DESK_METAL)
	_frame.draw_rect(Rect2(0, deck_y - 6, s.x, 6), Color(Palette.CELL_PINK, 0.12))
	for i in 10:
		_frame.draw_circle(Vector2(24 + i * (s.x - 48) / 9.0, deck_y + 10), 2.5, Palette.DESK_METAL)
