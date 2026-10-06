class_name CyberdeckBackground
extends Control
## The physical world (STYLE_GUIDE 1): the Cell's room at night, looking down through
## rain on the isometric neon city (NeonCity); a worn metal deck edge sits at the bottom. Rain animates unless reduce-effects.
## Searchlights sweep past the window as Heat rises (GDD 9.4).
## Parity fix TITLE-01 (designer 2026-10-05): a host may swap the 2D city for the blurred 3D one
## (`use_blurred_city`, BlurredCityBackdrop: the title); where the look's city quality tier
## does not take the 3D city, headless, or under the 2D city's design-review args, it keeps the
## 2D NeonCity. Every other user (the HQ, the warm-ups, the labs) is unchanged.

## The title's 2D-city design-review args (title_scene `--demo-*`): they keep the 2D city.
const CITY_2D_DEMOS: Array[String] = ["--demo-district=", "--demo-ink=", "--demo-jitter=", "--demo-texture=", "--demo-cultures",
	"--demo-bigoverview=", "--demo-nopan", "--demo-overview"]

var heat_band: int = 0:
	set(v):
		heat_band = v
		if _frame != null:
			_frame.queue_redraw()
var city: NeonCity
var _frame: Control
## The blurred 3D city in place of the 2D one (null: the 2D city shows).
var blurred: BlurredCityBackdrop = null
var _search_t: float = 0.0


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


## True when look `look` takes the 3D city at Settings.city_quality value `city_quality` where
## `can_render` (a renderer is there). Pure.
static func blurred_city_mode(look: CityBackdropLook, city_quality: int, can_render: bool) -> bool:
	return look.city_mode(CityView3D.CONFIG.tier_for(city_quality), can_render)


## Swaps the 2D city for the blurred 3D city of `look` framed on `corp`'s HQ (BlurredCityBackdrop)
## when the quality tier takes it, a renderer is there and no 2D design-review arg is in `args`.
## The 2D city stays (hidden, its process off) for the host's references. True when swapped.
func use_blurred_city(look: CityBackdropLook, corp: StringName, args: PackedStringArray = OS.get_cmdline_user_args()) -> bool:
	if blurred != null:
		return true
	if not blurred_city_mode(look, Settings.city_quality, CityView3D.can_render()) or city_2d_demo(args):
		return false
	blurred = BlurredCityBackdrop.new(look, corp)
	add_child(blurred)
	move_child(blurred, city.get_index() + 1)
	city.visible = false
	city.process_mode = Node.PROCESS_MODE_DISABLED
	return true


## True when `args` hold one of the 2D city's design-review args (CITY_2D_DEMOS). Pure.
static func city_2d_demo(args: PackedStringArray) -> bool:
	for a in args:
		for d in CITY_2D_DEMOS:
			if a.begins_with(d):
				return true
	return false


## True while the blurred 3D city stands in for the 2D one.
func on_blurred_city() -> bool:
	return blurred != null


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
	# Heat searchlights sweep across the glass.
	if heat_band > 0:
		var sx := fmod(_search_t * 120.0 * heat_band, s.x + 400.0) - 200.0
		_frame.draw_colored_polygon(PackedVector2Array([Vector2(sx, s.y), Vector2(sx + 90, s.y), Vector2(sx + 320, 0), Vector2(sx + 160, 0)]), Color(Palette.PAPER, 0.05 * heat_band))
	# The deck edge: worn metal lip with screws and a pink under-glow.
	var deck_y := s.y - 18.0
	_frame.draw_rect(Rect2(0, deck_y, s.x, 18), Palette.DESK_DARK)
	_frame.draw_rect(Rect2(0, deck_y, s.x, 3), Palette.DESK_METAL)
	_frame.draw_rect(Rect2(0, deck_y - 6, s.x, 6), Color(Palette.CELL_PINK, 0.12))
	for i in 10:
		_frame.draw_circle(Vector2(24 + i * (s.x - 48) / 9.0, deck_y + 10), 2.5, Palette.DESK_METAL)
