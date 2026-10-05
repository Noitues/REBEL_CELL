class_name CityGridControls
extends Node
## ART-5 5a: the City Grid's player camera on the unified city (bible §4.1: panning with
## DRAG / WASD, the minimap terminal; the continuous log-linear zoom of §6.1): the mouse
## wheel (and + / -) zooms about the cursor, a drag on the map, WASD and the pad's right
## stick pan, the minimap centres. The maths is CityMapCamera's; the page applies each frame
## through `apply` (its `_frame_city`), so every fit, label and lean reads the real camera.
## A view: the camera is view state, never game state. Headless nothing polls (no input).

## The wheel / key zoom step and the pan speed are the config's (zoom_step, pan_screens_s).
## Stick dead zone.
const STICK_DEAD := 0.25

var cfg: CityConfig = CityView3D.CONFIG
var city: NeonCity
## The page's screen rect the city frame is laid out in (its parent control's px).
var screen: Control
## Applies a frame: func(scale: float, focus: Vector2, anchor: Vector2).
var apply: Callable
var minimap: CityMinimap = null
## The map's Sites for the minimap: func() -> Array[Dictionary] ({"at", "kind"}).
var sites_of: Callable = Callable()


func _init(p_city: NeonCity, p_screen: Control, p_apply: Callable) -> void:
	name = "CityGridControls"
	city = p_city
	screen = p_screen
	apply = p_apply


## Hooks overlay `overlay` (wheel and drag on the map) and minimap `m`.
func attach(overlay: CityMapOverlay, m: CityMinimap) -> void:
	# The overlay speaks in viewport (canvas) px; the frame is the page's px.
	overlay.zoom_requested.connect(func(at: Vector2, notches: float) -> void:
		zoom_at(screen.get_global_transform_with_canvas().affine_inverse() * at, notches))
	overlay.pan_requested.connect(func(d: Vector2) -> void:
		pan_by(d / screen.get_global_transform_with_canvas().get_scale().x))
	minimap = m
	if m != null:
		m.centre_requested.connect(centre_on)
		m.show_city(city)
	sync_minimap()


func _frame() -> Array:
	return [screen.size, city.focus_grid if city.focus_grid != Vector2.INF else Vector2.ZERO, city.focus_anchor,
		city.scale.x, city.tile_b()]


func _apply(f: Dictionary) -> void:
	apply.call(float(f["scale"]), f["focus"], f["anchor"])
	sync_minimap()


## Zooms by `notches` wheel steps (> 0 out) about screen point `p` (the page's px).
func zoom_at(p: Vector2, notches: float) -> void:
	var fr := _frame()
	_apply(CityMapCamera.zoom_about(cfg, p, pow(cfg.zoom_step, notches), fr[0], fr[1], fr[2], fr[3], fr[4]))


## Pans by `delta` screen px (the city follows).
func pan_by(delta: Vector2) -> void:
	if delta == Vector2.ZERO:
		return
	var fr := _frame()
	_apply(CityMapCamera.pan(cfg, delta, fr[0], fr[1], fr[2], fr[3], fr[4]))


## Centres the camera on grid point `g` (the minimap).
func centre_on(g: Vector2) -> void:
	_apply(CityMapCamera.centre_on(cfg, g, city.scale.x))


## The minimap's Sites and view box, from the camera now.
func sync_minimap() -> void:
	if minimap == null or not is_instance_valid(minimap):
		return
	var fr := _frame()
	var s: Array[Dictionary] = []
	if sites_of.is_valid():
		s = sites_of.call()
	minimap.show_state(s, CityMapCamera.view_quad(fr[0], fr[1], fr[2], fr[3], fr[4]))


func _process(delta: float) -> void:
	if DisplayServer.get_name() == "headless" or not screen.is_visible_in_tree():
		return
	var focus := screen.get_viewport().gui_get_focus_owner()
	if focus is LineEdit or focus is TextEdit:
		return
	var v := Vector2.ZERO
	if Input.is_physical_key_pressed(KEY_A):
		v.x -= 1.0
	if Input.is_physical_key_pressed(KEY_D):
		v.x += 1.0
	if Input.is_physical_key_pressed(KEY_W):
		v.y -= 1.0
	if Input.is_physical_key_pressed(KEY_S):
		v.y += 1.0
	var stick := Vector2(Input.get_joy_axis(0, JOY_AXIS_RIGHT_X), Input.get_joy_axis(0, JOY_AXIS_RIGHT_Y))
	if stick.length() > STICK_DEAD:
		v += stick
	if v != Vector2.ZERO:
		# Keys move the view: the city slides the other way.
		pan_by(-v.limit_length(1.0) * screen.size.x * cfg.pan_screens_s * delta)


func _unhandled_key_input(event: InputEvent) -> void:
	if not screen.is_visible_in_tree() or not (event is InputEventKey) or not event.pressed:
		return
	var k := (event as InputEventKey).physical_keycode
	if k == KEY_EQUAL or k == KEY_KP_ADD:
		zoom_at(screen.size * 0.5, -1.0)
		get_viewport().set_input_as_handled()
	elif k == KEY_MINUS or k == KEY_KP_SUBTRACT:
		zoom_at(screen.size * 0.5, 1.0)
		get_viewport().set_input_as_handled()
