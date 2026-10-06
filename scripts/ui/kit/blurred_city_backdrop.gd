class_name BlurredCityBackdrop
extends Control
## Parity fix TITLE-01 (designer 2026-10-05; concept round 33 `title_screen.png` / `.gif`): the
## one 3D city (its own CityView3D, the unified city of the Grid, raid and netrun, with 5c's
## motion layers) seen from a fixed camera with a corp's HQ landmark at a screen anchor, at
## night, tilt-shifted and darkened (`shaders/city/city_tilt_shift.gdshader`) so a menu reads
## over a dark, soft field. Framing, blur and darkening come from a CityBackdropLook (the
## title's: `content/config/title_city_backdrop.tres`); another screen takes it with its own
## look. Hosts build it only where the look's city quality tier takes the 3D city
## (CyberdeckBackground.use_blurred_city); the 2D NeonCity stays the fallback below it and
## headless.
## The city fades in over the night sky once its model is in (`city_bake_fade`, the bake's own
## arrival; MotionSkip completes it). Reduce effects / reduce motion: a still frame (the city
## renders once, then holds). A view: it never changes game state.

const SHADER := preload("res://shaders/city/city_tilt_shift.gdshader")
## The city's arrival over the sky (the 2D city's bake fade, reused).
const ARRIVE_MOTION := &"city_bake_fade"

var look: CityBackdropLook
## The corp whose HQ stands in the frame (frame_corp).
var corp: StringName
## The 3D city (null headless).
var city: CityView3D = null
var city_motion: CityViewMotion = null
var _picture: Control
var _blur: ColorRect
var _mat: ShaderMaterial
var _city_in: bool = false
var _arrive: Tween = null


func _init(p_look: CityBackdropLook = null, p_corp: StringName = &"") -> void:
	name = "BlurredCity"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	look = p_look if p_look != null else CityBackdropLook.new()
	corp = frame_corp(look, p_corp)
	_picture = Control.new()
	_picture.name = "Picture"
	_picture.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_picture.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_picture.modulate.a = 0.0
	_picture.draw.connect(_draw_picture)
	add_child(_picture)
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	_blur = ColorRect.new()
	_blur.name = "TiltShift"
	_blur.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_blur.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_blur.material = _mat
	add_child(_blur)
	_apply_look()
	resized.connect(_on_resized)


func _ready() -> void:
	MotionSkip.register_passive(self)
	Settings.changed.connect(_sync_still)
	get_viewport().size_changed.connect(_on_resized)
	if CityView3D.can_render():
		city = CityView3D.new()
		city.name = "BackdropCity"
		city.band_lock = CityLod.Band.GRID  # solid buildings and the city's full life
		city.set_iso(camera(CityView3D.CONFIG, look, corp, _view_px()))
		city.model_ready.connect(_on_city_ready)
		add_child(city)
		city_motion = CityViewMotion.make(city)
		city.add_child(city_motion)
	_on_resized()


## The corp whose HQ frames the view: `wanted` when it has an HQ on the city (a campaign's
## target), else the look's default.
static func frame_corp(p_look: CityBackdropLook, wanted: StringName) -> StringName:
	if wanted != &"" and wanted != CityView3D.CELL:
		for t: Dictionary in NeonCity.TERRITORIES:
			if t["id"] == wanted:
				return wanted
	return p_look.default_corp


## The corp of the campaign in save slot `slot` ("" = the newest, RunManager.latest_slot), or
## &"" when there is none (the title's last-played campaign).
static func corp_of_slot(slot: String) -> StringName:
	var s := slot if slot != "" else RunManager.latest_slot()
	if s == "":
		return &""
	return StringName(String(RunManager.slot_summary(s).get("corporation", "")))


## The fixed camera of `p_look` on `p_corp`'s HQ for a view of `view` px: the HQ's point
## (`lift` BU up its lot's centre) lands on the look's anchor. Pure.
static func camera(cfg: CityConfig, p_look: CityBackdropLook, p_corp: StringName, view: Vector2) -> CityIsoCamera:
	var hq := NeonCity.hq_of(p_corp) + Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS) * 0.5
	var cam := CityIsoCamera.make(cfg, CityIsoCamera.lot_to_world(cfg, hq, p_look.lift), p_look.ortho, view.max(Vector2.ONE))
	cam.pan_px(cam.viewport * (Vector2(0.5, 0.5) - p_look.anchor))
	return cam


## True once the 3D city's model is in and showing.
func city_in() -> bool:
	return _city_in


## True for a still frame (reduce effects / reduce motion).
static func still() -> bool:
	return Settings.reduce_effects or Settings.reduce_motion


## The arrival fade runs (MotionSkip).
func motion_running() -> bool:
	return _arrive != null and _arrive.is_valid() and _arrive.is_running()


## Lands the arrival at once (MotionSkip).
func complete_motion() -> void:
	if motion_running():
		_arrive.kill()
		Motion.settle(_picture, ^"modulate:a")
		_picture.modulate.a = 1.0


func _apply_look() -> void:
	for p: StringName in [&"focus_centre", &"focus_half", &"focus_power", &"side_dark", &"side_reach", &"side_power", &"foot_dark",
			&"foot_from", &"vignette", &"vignette_centre", &"vignette_scale", &"gain"]:
		_mat.set_shader_parameter(p, look.get(p))


## The view's size in screen pixels (the window's stretch included).
func _view_px() -> Vector2:
	var stretch := get_viewport().get_final_transform().get_scale().x if is_inside_tree() else 1.0
	return (size * stretch).round().max(Vector2(2, 2))


func _on_resized() -> void:
	if not is_inside_tree():
		return
	var px := _view_px()
	_mat.set_shader_parameter(&"sigma_px", look.blur_px * px.y / maxf(look.ref_height, 1.0))
	if city != null:
		city.set_view_size(Vector2i(px))
		city.set_iso(camera(city.cfg, look, corp, px))
		if _city_in and still():
			city.render_target_update_mode = SubViewport.UPDATE_ONCE
	_picture.queue_redraw()


func _on_city_ready() -> void:
	if _city_in:
		return
	_city_in = true
	_picture.queue_redraw()
	if still():
		_picture.modulate.a = 1.0
	else:
		_arrive = Motion.fade(_picture, 1.0, ARRIVE_MOTION)
	_sync_still()


func _sync_still() -> void:
	if city == null or not _city_in:
		return
	city.render_target_update_mode = SubViewport.UPDATE_ONCE if still() else SubViewport.UPDATE_ALWAYS


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Color(CityView3D.CONFIG.sky, 1.0))


func _draw_picture() -> void:
	if city != null and _city_in:
		_picture.draw_texture_rect(city.get_texture(), Rect2(Vector2.ZERO, size), false)
