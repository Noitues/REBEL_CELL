class_name RouteStopPlacer
extends Node
## Parity ROUTE-04 (round 37 `city_default`: the route is picked on the map, no list): the
## route's choices are focus stops ON their map stickers. Each stop is the choice's own button
## (pressed = the choice, as before), drawn as nothing (the sticker, its number chip and its
## label are the map's), set top-level so the ROUTE window's column gives it no room, and kept
## each frame over its sticker by this placer. Its focus and hover light the sticker on the map
## (CityMapOverlay.hover_id: the paper ring with ticks). The stops stay in the ROUTE window's
## tree where the list was, so the page's focus links (UiFocus.link_layout) walk them in the
## map's numbered order, then GRID VIEW. View only; no game state.

## A stop's reach beyond its sticker's (screen px, each side).
const STOP_PAD := 6.0
## The theme colours a stop clears (its words stay for tooltips, tests and readers; the map's
## label shows them).
const FONT_COLORS: Array[StringName] = [&"font_color", &"font_hover_color", &"font_pressed_color", &"font_focus_color",
	&"font_hover_pressed_color", &"font_disabled_color", &"font_outline_color", &"icon_normal_color", &"icon_focus_color",
	&"icon_hover_color", &"icon_pressed_color", &"icon_disabled_color"]
const STYLES: Array[StringName] = [&"normal", &"hover", &"pressed", &"focus", &"disabled", &"hover_pressed"]

## The scene whose `city_overlay` the stickers are on (read each frame: the map is mounted
## after the choices are made, and a move swaps nothing but positions).
var scene: Node = null
## Stop button -> its node id, in the map's numbered order.
var stops: Array[Button] = []


func _init(p_scene: Node = null) -> void:
	name = "RouteStopPlacer"
	scene = p_scene


## Makes `b` (the choice for node `id`) a stop on the map: drawn as nothing, top-level, lit
## on the map while focused or pointed at; `on_focus` is called with `id` when it takes the
## focus or the pointer (the scene shows the node's panel).
func add_stop(b: Button, id: StringName, on_focus: Callable) -> void:
	b.set_meta(&"route_stop", id)
	b.top_level = true
	b.flat = true
	b.clip_text = true
	b.custom_minimum_size = Vector2.ZERO
	for st in STYLES:
		b.add_theme_stylebox_override(st, StyleBoxEmpty.new())
	for c in FONT_COLORS:
		b.add_theme_color_override(c, Color(Palette.NO_TINT, 0.0))
	b.focus_entered.connect(_light.bind(id, on_focus))
	b.mouse_entered.connect(_light.bind(id, on_focus))
	b.focus_exited.connect(_unlight.bind(b))
	b.mouse_exited.connect(_unlight.bind(b))
	stops.append(b)
	_place(b)


## The overlay the stickers are on (null off the route).
func overlay() -> CityMapOverlay:
	if scene == null or not is_instance_valid(scene):
		return null
	var ov: Variant = scene.get("city_overlay")
	return ov as CityMapOverlay if ov is CityMapOverlay and is_instance_valid(ov) else null


func _process(_delta: float) -> void:
	for b in stops:
		if is_instance_valid(b):
			_place(b)


## Puts stop `b` over its sticker (screen px): the sticker's reach plus STOP_PAD.
func _place(b: Button) -> void:
	var ov := overlay()
	if ov == null or not ov.is_inside_tree():
		return
	var n := ov._node_dict(b.get_meta(&"route_stop"))
	if n.is_empty():
		return
	var at := ov.icon_pos(n)
	if at.x == INF:
		return
	var xf := ov.get_global_transform_with_canvas()
	var r := ov.icon_radius(n) * xf.get_scale().x + STOP_PAD
	var side := Vector2(r, r) * 2.0
	if b.size != side:
		b.size = side
	b.global_position = xf * at - b.size * 0.5


func _light(id: StringName, on_focus: Callable) -> void:
	var ov := overlay()
	if ov != null:
		ov.hover_id = id
	if on_focus.is_valid():
		on_focus.call(id)


func _unlight(b: Button) -> void:
	var ov := overlay()
	if ov == null or not is_instance_valid(b):
		return
	if b.has_focus() or b.is_hovered():
		return
	if ov.hover_id == b.get_meta(&"route_stop"):
		ov.hover_id = &""


## The stop at the screen point `p` (screen px), or null (tests and the pointer).
func stop_at(p: Vector2) -> Button:
	for b in stops:
		if is_instance_valid(b) and b.get_global_rect().has_point(p):
			return b
	return null
