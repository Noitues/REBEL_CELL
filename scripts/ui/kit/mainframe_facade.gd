class_name MainframeFacade
extends Control
## ART-9 4A (ART_BIBLE v2 §4.10, §1.2 "World"): the MAINFRAME shop's exterior, the F1b Tenement
## facade (one-point street view, alley stair, two wall-to-wall cables, front building with roll
## shutters), baked from round 12 / 33's Blender scene per state (day, night, rain;
## tools/art_bake/mainframe_facade_bake.py) with the MAINFRAME sign v4 on its plate. The sign's
## light spills onto the walls, the street and the puddles: the blue and red spill layers are added
## over the dark facade at the sign's levels (round 33's composite), so a takeover darkens the
## street with the sign. Night and rain get rain streaks that move. Decoration: changes no state.

## Facade states (the baked files' names).
const STATES: Array[StringName] = [&"night", &"rain", &"day"]
const DIR := "res://assets/backdrops/shop/"
## The bake's size and where its sign plate sits on it (round 12 layout at 1920x1080, x 2/3).
const BAKE_SIZE := Vector2(1280, 720)
const PLATE := Rect2(Vector2(52, 26) * (2.0 / 3.0), Vector2(160, 662) * (2.0 / 3.0))
## Rain: streaks on screen, their length and slant (px), alpha, and how fast they fall (px/s).
const RAIN_STREAKS := {&"rain": 220, &"night": 110, &"day": 0}
const RAIN_LEN := Vector2(10.0, 26.0)
const RAIN_SLANT := 0.16
const RAIN_ALPHA := Vector2(0.10, 0.28)
const RAIN_SPEED := 900.0

var state: StringName = &"night"
## The sign's top keeps below this y (the top bar covers the screen's top): the picture moves
## down by what it lacks (its street's foot goes under the screen's edge; the top strip repeats
## the sky).
var top_clear: float = 0.0:
	set(v):
		top_clear = v
		_place_sign()
		queue_redraw()
var sign: MainframeSign
var _base: Texture2D
var _spill_blue: Texture2D
var _spill_red: Texture2D
var _spill_layer: Control
var _rain: Control
var _rain_t: float = 0.0


func _init(p_state: StringName = &"night") -> void:
	name = "MainframeFacade"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	state = p_state if STATES.has(p_state) else &"night"
	_base = load(DIR + "facade_%s.webp" % state) as Texture2D
	_spill_blue = load(DIR + "facade_%s_spill_blue.webp" % state) as Texture2D
	_spill_red = load(DIR + "facade_%s_spill_red.webp" % state) as Texture2D
	_spill_layer = Control.new()
	_spill_layer.name = "Spill"
	_spill_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var add := CanvasItemMaterial.new()
	add.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_spill_layer.material = add
	_spill_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	_spill_layer.draw.connect(_draw_spill)
	add_child(_spill_layer)
	sign = MainframeSign.new()
	sign.name = "MainframeSign"
	sign.light_changed.connect(_spill_layer.queue_redraw)
	add_child(sign)
	_rain = Control.new()
	_rain.name = "Rain"
	_rain.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_rain.set_anchors_preset(Control.PRESET_FULL_RECT)
	_rain.draw.connect(_draw_rain)
	add_child(_rain)
	resized.connect(_place_sign)
	set_process(int(RAIN_STREAKS.get(state, 0)) > 0)


## The facade state for a visit (night most often; rain and day by the visit's hash).
static func state_for(key: String) -> StringName:
	var h := absi(key.hash()) % 4
	return [&"night", &"rain", &"night", &"day"][h]


## Where the facade's picture is drawn in this control (cover: it fills the control, cut evenly).
func picture_rect() -> Rect2:
	var k := maxf(size.x / BAKE_SIZE.x, size.y / BAKE_SIZE.y)
	var s := BAKE_SIZE * k
	var r := Rect2((size - s) * Vector2(0.5, 1.0), s)
	r.position.y += maxf(0.0, top_clear - (r.position.y + PLATE.position.y * k))
	return r


## The sign plate's rect in this control.
func plate_rect() -> Rect2:
	var p := picture_rect()
	var k := p.size.x / BAKE_SIZE.x
	return Rect2(p.position + PLATE.position * k, PLATE.size * k)


func _place_sign() -> void:
	sign.fit_plate(plate_rect())
	_spill_layer.queue_redraw()


func _draw() -> void:
	var r := picture_rect()
	if r.position.y > 0.0:
		draw_texture_rect_region(_base, Rect2(r.position.x, 0.0, r.size.x, r.position.y), Rect2(Vector2.ZERO, Vector2(BAKE_SIZE.x, 1.0)))
	draw_texture_rect(_base, r, false)


func _draw_spill() -> void:
	var s := sign.spill()
	var r := picture_rect()
	if s.x > 0.0:
		_spill_layer.draw_texture_rect(_spill_blue, r, false, Color(Palette.NO_TINT, clampf(s.x, 0.0, 1.0)))
	if s.y > 0.0:
		_spill_layer.draw_texture_rect(_spill_red, r, false, Color(Palette.NO_TINT, clampf(s.y, 0.0, 1.0)))


func _process(delta: float) -> void:
	if not Motion.live(&"mainframe_rain"):
		return
	_rain_t += delta * Motion.amplitude(&"mainframe_rain")
	_rain.queue_redraw()


## Rain streaks falling (positions by hash, so a frame is the same for the same time).
func _draw_rain() -> void:
	var n := int(RAIN_STREAKS.get(state, 0))
	if n <= 0:
		return
	var r := Rect2(Vector2.ZERO, size)
	for i in n:
		var hx := float(absi(hash([i, 7])) % 10000) / 10000.0
		var hy := float(absi(hash([i, 11])) % 10000) / 10000.0
		var hl := float(absi(hash([i, 13])) % 1000) / 1000.0
		var len := lerpf(RAIN_LEN.x, RAIN_LEN.y, hl)
		var y := fposmod(hy * r.size.y + _rain_t * RAIN_SPEED * (0.7 + 0.6 * hl), r.size.y + len) - len
		var x := hx * (r.size.x + r.size.y * RAIN_SLANT) - y * RAIN_SLANT
		var a := lerpf(RAIN_ALPHA.x, RAIN_ALPHA.y, hl)
		_rain.draw_line(Vector2(x, y), Vector2(x - len * RAIN_SLANT, y + len), Color(Palette.TEXT_HI, a), 1.0)
