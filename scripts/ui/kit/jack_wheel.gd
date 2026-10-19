class_name JackWheel
extends Control
## NA-25b r3 (ART_BIBLE 4.6, art-pass A-019): the operative's real class wheel for the jack's chain, small and then enlarged: the combat's
## own `WheelView` (D4 bezel with its glass crescent, the slices with their read blocks, the cream blade, the class hub core, 3.2 and
## 3.3) drawn into a sub-viewport, never redrawn here. `JackSequence` slaps it onto the link, spins it up, swells it until its hub core
## covers the screen (the switch runs under it), holds the hub as a CRT terminal when the load is slow (1.2: navy glass, 3 px
## scanlines, a faint scrolling hex dump, the edge glow, a type-on line with its caret: `CrtTerminalPanel`), then burns a hole through
## the hub core (`jack_lens_hole.gdshader`) that grows past the screen. View only: no game state.

const HOLE_SHADER := preload("res://shaders/kit/jack_lens_hole.gdshader")
## The wheel view's own size (px); its drawn radius comes from it (`WheelView._radius`), scaled by `place`.
const VIEW_SIZE := Vector2(480.0, 480.0)
## The hole's rim (px, canvas units) at the screen's size.
const RIM_PX := 6.0
## Hole radius at the end of the opening, as a share past the screen's half diagonal.
const HOLE_OVERSCAN := 1.05

var wheel: WheelView = null
## The hub's CRT hold: the navy glass with its type-on line (hidden until `show_hold`).
var hold: CrtTerminalPanel = null
var _vp: SubViewport = null
var _tex: TextureRect = null
var _mat: ShaderMaterial = null
var _hold_root: Control = null
var _breathe: ColorRect = null
var _canvas := Vector2(1280.0, 720.0)


func _init() -> void:
	name = "JackWheel"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_vp = SubViewport.new()
	_vp.name = "WheelViewport"
	_vp.transparent_bg = true
	_vp.disable_3d = true
	_vp.render_target_update_mode = SubViewport.UPDATE_DISABLED
	add_child(_vp)
	_tex = TextureRect.new()
	_tex.name = "WheelTexture"
	_tex.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_tex.stretch_mode = TextureRect.STRETCH_SCALE
	_tex.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_tex.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_mat = ShaderMaterial.new()
	_mat.shader = HOLE_SHADER
	_tex.material = _mat
	_tex.texture = _vp.get_texture()
	add_child(_tex)
	visible = false


## The operative's display combatant for `link` (`link["operative"]`, else the default class's start wheel): what the combat shows.
static func combatant_for(link: Dictionary, lookup: ContentLookup) -> CombatantState:
	var op := link.get("operative") as OperativeState
	if op != null:
		return LoadoutView.display_combatant(op, lookup)
	var p := CombatantState.new()
	p.id = &"player"
	p.is_player = true
	var cls := lookup.get_content(RunManager.DEFAULT_CLASS) as ClassData
	if cls == null or cls.starting_wheel == null:
		return p
	p.source_id = cls.id
	p.display_name = cls.display_name
	p.max_hp = 1
	p.hp = 1
	p.wheel = WheelState.from_wheel_data(cls.starting_wheel, cls.starting_wheel.inner_ring)
	return p


## Builds the view for `link` at the screen size `screen` (canvas units). Call before the first `place`.
func setup(link: Dictionary, screen: Vector2) -> void:
	_canvas = screen
	var win := get_window().size if is_inside_tree() else Vector2i(screen)
	_vp.size = Vector2i(maxi(win.x, 1), maxi(win.y, 1))
	_vp.size_2d_override = Vector2i(screen)
	_vp.size_2d_override_stretch = true
	_mat.set_shader_parameter(&"canvas_size", screen)
	_mat.set_shader_parameter(&"rim_px", RIM_PX)
	if wheel != null and is_instance_valid(wheel):
		wheel.queue_free()
	var lookup := RunManager.lookup()
	wheel = WheelView.new()
	wheel.name = "ClassWheel"
	wheel.show_arrows = false
	wheel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	wheel.size = VIEW_SIZE
	_vp.add_child(wheel)
	wheel.size = VIEW_SIZE
	var c := combatant_for(link, lookup)
	wheel.show_combatant(c, [] as Array[CombatantState], [] as Array[Dictionary], lookup)
	_build_hold()
	set_hole(Vector2.ZERO, 0.0)


func _build_hold() -> void:
	if _hold_root != null and is_instance_valid(_hold_root):
		_hold_root.queue_free()
	if _breathe != null and is_instance_valid(_breathe):
		_breathe.queue_free()
	_breathe = ColorRect.new()
	_breathe.name = "Breathe"
	_breathe.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_breathe.size = _canvas
	_breathe.color = Color(PaletteSkins.chrome(Palette.NET_CYAN), 0.0)
	_vp.add_child(_breathe)
	_hold_root = Control.new()
	_hold_root.name = "HubHold"
	_hold_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_hold_root.size = _canvas
	_hold_root.visible = false
	_vp.add_child(_hold_root)
	var back := ColorRect.new()
	back.name = "Back"
	back.color = Palette.NIGHT_SKY
	back.mouse_filter = Control.MOUSE_FILTER_IGNORE
	back.size = _canvas
	_hold_root.add_child(back)
	hold = CrtTerminalPanel.new()
	hold.name = "HubTerminal"
	hold.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hold.size = _canvas
	hold.text_step = UiTheme.TITLE  # a boot-log line over a whole screen of glass
	_hold_root.add_child(hold)


## The wheel's drawn radius (px at scale 1) and its hub core's share of it.
func base_radius() -> float:
	return wheel._radius() if wheel != null else 1.0


func hub_share() -> float:
	return wheel.hub_px(wheel.art_scale()) / maxf(base_radius(), 1.0) if wheel != null else 1.0


## Puts the wheel's centre on `at` with a drawn radius of `r` px (canvas units), `scale_xy` squashing it (the slap), turned `turn` radians.
func place(at: Vector2, r: float, turn: float = 0.0, scale_xy: Vector2 = Vector2.ONE) -> void:
	if wheel == null:
		return
	var s := Vector2.ONE * (r / maxf(base_radius(), 1.0)) * scale_xy
	wheel.scale = s
	wheel.position = at - wheel._center() * s
	wheel.anim_rotation = turn / TAU * float(RC.TICKS)
	wheel.queue_redraw()
	_vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	visible = true


## Cuts the hub open at `center` with a hole of radius `r` (canvas units); 0 closes it.
func set_hole(center: Vector2, r: float) -> void:
	_mat.set_shader_parameter(&"hole_center", center)
	_mat.set_shader_parameter(&"hole_r", r)


## The hole's radius when the hub opens `t` (0 closed .. 1 open) over a hub of radius `hub_r` on a screen of `screen`: it grows with
## the ease-out cubic past the screen's half diagonal (the pure rule the lens and its test share).
static func hole_radius(t: float, hub_r: float, screen: Vector2) -> float:
	var e := 1.0 - pow(1.0 - clampf(t, 0.0, 1.0), 3.0)
	return minf(hub_r, screen.length() * 0.5 * HOLE_OVERSCAN) * e


## True when a hub of radius `hub_r` centred on `at` with a hole of `hole_r` covers every pixel of a screen of `screen` (the hole
## itself uncovers its disc; the hub covers the rest when its radius reaches the farthest corner).
static func covers(at: Vector2, hub_r: float, hole_r: float, screen: Vector2) -> bool:
	if hole_r > 0.0:
		return false
	var far := 0.0
	for corner in [Vector2.ZERO, Vector2(screen.x, 0.0), Vector2(0.0, screen.y), screen]:
		far = maxf(far, at.distance_to(corner))
	return hub_r >= far


## The plain breathe of a short hold: a cyan lift of `alpha` over the covering hub core (0 off).
func set_breathe(alpha: float) -> void:
	if _breathe != null:
		_breathe.color = Color(PaletteSkins.chrome(Palette.NET_CYAN), alpha)


## Shows the hub's CRT hold with `line` typing on (the sequence calls it once the hold passes `jack_hub_crt`); `on` false hides it.
func show_hold(on: bool, line: String = "") -> void:
	if _hold_root == null:
		return
	if on and not _hold_root.visible:
		_hold_root.visible = true
		hold.type_on(line)
	elif not on:
		_hold_root.visible = false


## True while the CRT hold shows.
func holding() -> bool:
	return _hold_root != null and _hold_root.visible


## Stops drawing (the sequence ended).
func clear() -> void:
	visible = false
	if _vp != null:
		_vp.render_target_update_mode = SubViewport.UPDATE_DISABLED
	if _hold_root != null:
		_hold_root.visible = false
	set_breathe(0.0)
