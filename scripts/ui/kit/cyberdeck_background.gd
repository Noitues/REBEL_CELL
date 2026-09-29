class_name CyberdeckBackground
extends Control
## The physical world (STYLE_GUIDE 1): the Cell's room at night, looking down through
## rain on the isometric neon city (NeonCity); a worn metal deck edge sits at the bottom. Rain animates unless reduce-effects.
## Heat (GDD 9.4) reaches the city itself (art pass W7, ART_BIBLE §9.3): searchlights over the
## corp's district from NOTICED, patrols and rim flicker from FLAGGED, a HUNTED grade.

## The Heat band (0 COOL .. 3 HUNTED), passed down to the city (CityAtmosphere).
var heat_band: int = 0:
	set(v):
		heat_band = v
		if city != null:
			city.atmosphere().set_heat_band(v)
var city: NeonCity
var _frame: Control


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	city = NeonCity.new()
	city.rain = true
	city.follow_campaign = true  # territory influence (H20)
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


# --- Art pass W7: the city's state, passed down (see CityAtmosphere) --------------------------

## The screen's context: &"title", &"hq", &"net" or &"combat" (the city's grade).
func set_context(context: StringName) -> void:
	city.atmosphere().set_context(context)


## Heat (its band from Palette.heat_band).
func set_heat(heat: int) -> void:
	city.atmosphere().set_heat(heat)


## Campaign progress 0..1 toward the target corporation (the grade leans to its hue).
## Art pass W9F: forgets the campaign lean (CityAtmosphere.clear_campaign_progress).
func clear_campaign_progress() -> void:
	city.atmosphere().clear_campaign_progress()


func set_campaign_progress(progress: float, corp_id: StringName) -> void:
	city.atmosphere().set_campaign_progress(progress, corp_id)


## The Cell's claimed Sites (grid lots).
func set_territory(claims: PackedVector2Array) -> void:
	city.atmosphere().set_territory(claims)


## Maps over the city (§9.5): dim 40% and a slight blur.
func set_map_mode(on: bool) -> void:
	city.atmosphere().set_map_mode(on)


## UI calm zones: the text panels over the city (followed as they move).
func set_calm_controls(controls: Array[Control]) -> void:
	city.atmosphere().set_calm_controls(controls)


func _draw_frame() -> void:
	var s := size
	# The deck edge: worn metal lip with screws and a pink under-glow.
	var deck_y := s.y - 18.0
	_frame.draw_rect(Rect2(0, deck_y, s.x, 18), Palette.DESK_DARK)
	_frame.draw_rect(Rect2(0, deck_y, s.x, 3), Palette.DESK_METAL)
	_frame.draw_rect(Rect2(0, deck_y - 6, s.x, 6), Color(Palette.CELL_PINK, 0.12))
	for i in 10:
		_frame.draw_circle(Vector2(24 + i * (s.x - 48) / 9.0, deck_y + 10), 2.5, Palette.DESK_METAL)
