class_name CityMinimap
extends CrtTerminalPanel
## ART-5 5a: the City Grid's minimap terminal (bible §4.1 "City Grid ≈ ortho 440 with
## panning: edge chevrons, minimap terminal, DRAG / WASD"; ref round39 `city_grid`): a CRT
## terminal (`> MINIMAP`, `DRAG / WASD`) showing the whole city's territories as a small
## iso diamond, the map's Sites (lime = yours, red = the target, white = the rest), and the
## camera's view as a box. A press or drag on it asks the page to centre the camera there
## (`centre_requested`); views never change state, the camera is the page's.

signal centre_requested(grid: Vector2)

## Sampling step (lots) of the territory picture, and its alpha.
const TERRAIN_STEP := 3
const TERRAIN_ALPHA := 0.55
## Inner layout (px at text scale 1): the map's inset under the title and over the caption.
const MAP_TOP := 26.0
const MAP_BOTTOM := 20.0
const MAP_SIDE := 10.0
const DOT_R := 2.5
const BOX_W := 1.5
## The camera's view box (our plan colour: yellow pencil).
const BOX_COLOR := Palette.PENCIL_PLAN
const TARGET_COLOR := Palette.PENCIL_THREAT
## The terminal grows with the text size up to this (at 2.0 it would take the map).
const SCALE_MAX := 1.3

var cfg: CityConfig = CityView3D.CONFIG
## Sites: {"at": Vector2 (grid), "kind": "you" | "target" | "site"}.
var sites: Array[Dictionary] = []
## The camera's view on the ground (four grid points).
var view_quad: PackedVector2Array = PackedVector2Array()
var _map: Control
var _dragging: bool = false

## The territory picture per city seed (view memory: a pure function of the layout).
static var _terrain: Dictionary = {}


func _init() -> void:
	super._init()
	caret = false
	hex_dump = false
	text_step = UiTheme.CAPTION
	text = CityMapOverlay.tr_word("MINIMAP")
	mouse_filter = Control.MOUSE_FILTER_STOP
	custom_minimum_size = cfg.minimap_size * _k()
	_map = Control.new()
	_map.name = "Map"
	_map.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_map.draw.connect(_draw_map)
	content.add_child(_map)
	resized.connect(_place_map)


func _ready() -> void:
	super._ready()
	_place_map()


static func _k() -> float:
	return minf(Settings.text_scale, SCALE_MAX)


## The territory picture of the game's city (`city`: a NeonCity for its territories).
static func terrain_of(city: NeonCity, p_cfg: CityConfig) -> ImageTexture:
	if _terrain.has(city.city_seed):
		return _terrain[city.city_seed]
	var r := p_cfg.city_rect
	var w := ceili(r.size.x / float(TERRAIN_STEP))
	var h := ceili(r.size.y / float(TERRAIN_STEP))
	var img := Image.create(w, h, false, Image.FORMAT_RGBA8)
	for y in h:
		for x in w:
			var i := r.position.x + x * TERRAIN_STEP
			var j := r.position.y + y * TERRAIN_STEP
			var t := city.territory_at(i, j)
			var c := Palette.corp_color(t).darkened(0.45) if t != &"" else Palette.NIGHT_BLOCK
			img.set_pixel(x, y, Color(c, TERRAIN_ALPHA))
	var tex := ImageTexture.create_from_image(img)
	_terrain[city.city_seed] = tex
	return tex


var _terrain_tex: Texture2D = null


## Sets the territory picture from `city` and redraws.
func show_city(city: NeonCity) -> void:
	_terrain_tex = terrain_of(city, cfg)
	_map.queue_redraw()


## The Sites shown and the camera's view (grid points), redrawn.
func show_state(p_sites: Array[Dictionary], p_view: PackedVector2Array) -> void:
	sites = p_sites
	view_quad = p_view
	_map.queue_redraw()


func _place_map() -> void:
	if _map == null:
		return
	var k := _k()
	_map.position = Vector2(MAP_SIDE, MAP_TOP * k)
	_map.size = Vector2(maxf(1.0, size.x - MAP_SIDE * 2.0), maxf(1.0, size.y - (MAP_TOP + MAP_BOTTOM) * k))
	_map.queue_redraw()


## The minimap's own iso: grid point -> map px (the city rect's diamond fitted in the map).
func to_map(g: Vector2) -> Vector2:
	var r := Rect2(cfg.city_rect)
	var tb := sin(deg_to_rad(cfg.pitch_deg))
	var c := r.get_center()
	var span_x := r.size.x + r.size.y
	var span_y := (r.size.x + r.size.y) * tb
	var s := minf(_map.size.x / span_x, _map.size.y / span_y)
	var d := g - c
	return _map.size * 0.5 + Vector2((d.x - d.y), (d.x + d.y) * tb) * s


## Map px -> grid point (inverse of `to_map`).
func from_map(p: Vector2) -> Vector2:
	var r := Rect2(cfg.city_rect)
	var tb := sin(deg_to_rad(cfg.pitch_deg))
	var span_x := r.size.x + r.size.y
	var span_y := (r.size.x + r.size.y) * tb
	var s := minf(_map.size.x / span_x, _map.size.y / span_y)
	var q := (p - _map.size * 0.5) / s
	var dd := q.x
	var ss := q.y / tb
	return r.get_center() + Vector2((ss + dd) * 0.5, (ss - dd) * 0.5)


func _draw_map() -> void:
	var r := Rect2(cfg.city_rect)
	var corners := PackedVector2Array([to_map(r.position), to_map(Vector2(r.end.x, r.position.y)), to_map(r.end),
		to_map(Vector2(r.position.x, r.end.y))])
	if _terrain_tex != null:
		_map.draw_colored_polygon(corners, Color.WHITE, PackedVector2Array([Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1)]), _terrain_tex)
	else:
		_map.draw_colored_polygon(corners, Color(Palette.NIGHT_BLOCK, TERRAIN_ALPHA))
	var edge := corners.duplicate()
	edge.append(corners[0])
	_map.draw_polyline(edge, Color(Palette.NET_CYAN, 0.5), 1.0)
	for s in sites:
		var col := Palette.PAPER
		match String(s.get("kind", "")):
			"you":
				col = Palette.CELL_TURF
			"target":
				col = TARGET_COLOR
		_map.draw_circle(to_map(s["at"]), DOT_R, col)
	if view_quad.size() == 4:
		var box := PackedVector2Array()
		for g in view_quad:
			box.append(to_map(g))
		box.append(box[0])
		_map.draw_polyline(box, BOX_COLOR, BOX_W)
	var f := Palette.mono()
	var px := UiTheme.font_px(UiTheme.CAPTION)
	# The pad pans with the right stick (UiTip.for_input picks the device's words).
	var hint := UiTip.for_input(CityMapOverlay.tr_word("DRAG / WASD"), CityMapOverlay.tr_word("RIGHT STICK"))
	var hw := f.get_string_size(hint, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	# The hint sits on the title line, right-aligned (drawn from the map's layer).
	_map.draw_string(f, Vector2(_map.size.x - hw, -_map.position.y + f.get_ascent(px) + PAD.y * 0.5), hint, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color(Palette.TERMINAL_TEXT, 0.7))
	var key := CityMapOverlay.tr_word("lime=you red=target box=view")
	_map.draw_string(f, Vector2(0, _map.size.y + f.get_ascent(px) + 2.0), key, HORIZONTAL_ALIGNMENT_LEFT, _map.size.x, px, Color(Palette.TERMINAL_TEXT, 0.6))


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		_dragging = event.pressed
		if event.pressed:
			centre_requested.emit(from_map(event.position - _map.position))
		accept_event()
	elif event is InputEventMouseMotion and _dragging:
		centre_requested.emit(from_map(event.position - _map.position))
		accept_event()
