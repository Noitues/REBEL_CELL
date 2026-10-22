extends Control
## LOOK backdrop stills bake (windowed only; headless has no renderer). Drives CombatBackdrop's city path, like
## hq_run_lab's hq_ / site_ states, and saves for each state the GRADED frame (what the player sees of the close-up:
## the backdrop shader's city grade, exposure, tint and focus included) and the won mask, so the combat stills
## (assets/backdrops/combat/<corp>_<hq|site>_<night|day>.jpg + _won.png) are the live close-up frozen:
##   python tools/run_windowed.py --log <f> -- --resolution 1280x720 res://tools/art_pipeline/backdrop/bake_backdrop_stills.tscn
##     -- --out=<dir> --states=hq_solace_night,hq_solace_day [--masks=1] [--reduce-effects=1] [--settle=40]
## State = <hq|site>_<corp>_<night|day>. The live city close-up is always the night look (CombatBackdrop has no day);
## the `day` states re-light the same framing with the cool day look (CityMotionConfig day_*, rain off, fog kept) once the
## city is up. Writes <out>/<state>.png (window size) and, with --masks=1, <out>/<state>_won.png (640x360: R = the
## target's silhouette, the HQ / Site landmark's solid meshes, G = its lit pixels), found by differencing the frame with
## those meshes hidden (rain, shader time and effects frozen with --reduce-effects=1).
## Prints "BAKE <state> ready=<bool>" per state.

const MAX_WAIT := 900
const MASK_SIZE := Vector2i(640, 360)
## The mask's silhouette: the frame difference (max channel, 0..1) that counts as the target.
const SIL_DIFF := 0.05
## The mask's lights: the lit pixel's luma (graded frame) that counts as the target's own light.
const LIGHT_LUMA := 0.62

var _args: Dictionary = {}
var _states: PackedStringArray = PackedStringArray()
var _step: int = 0
var _frame: int = 0
var _ready_at: int = -1
var _host: Control = null
var _backdrop: CombatBackdrop = null
var _reduce_was: int = -1
var _phase: int = 0
var _hidden_at: int = -1
var _frame_img: Image = null
var _hidden: Array[MeshInstance3D] = []
var _day: bool = false


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	_states = PackedStringArray(String(_args.get("states", "hq_solace_night")).split(","))
	if _args.has("reduce-effects"):
		_reduce_was = int(Settings.reduce_effects)
		Settings.reduce_effects = _args["reduce-effects"] == "1"
		RenderingServer.global_shader_parameter_set(Fx.REDUCE_GLOBAL, 1.0 if Settings.reduce_effects else 0.0)
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var bg := ColorRect.new()
	bg.color = Palette.NIGHT_SKY
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	_load(_states[0])


func _load(state: String) -> void:
	if _host != null:
		_host.queue_free()
	_host = Control.new()
	_host.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_host)
	_backdrop = null
	_ready_at = -1
	_frame = 0
	_phase = 0
	_hidden_at = -1
	_hidden.clear()
	var p := state.rsplit("_", true, 1)
	var head := p[0].split("_", true, 1)
	var kind := head[0]
	var corp := StringName(head[1])
	_day = p[1] == "day"
	# The same campaign every state (seed 11), so the city is the same whatever ran before (hq_run_lab's rule).
	RunManager.save_slot = "lab_bake_backdrop"
	var u := CampaignRules.unlock_for(RunManager.lookup(), RunManager.lookup().get_content(corp))
	var added := u != null and not RunManager.profile.unlocks.has(u.id)
	if added:
		RunManager.profile.unlocks.append(u.id)
	RunManager.new_campaign(11, corp)
	if added:
		RunManager.profile.unlocks.erase(u.id)
	_backdrop = CombatBackdrop.new()
	_host.add_child(_backdrop)
	var cd := RunManager.lookup().get_content(corp) as CorporationData
	var site: StringName = CityLandmarks.site_of(CityView3D.CONFIG, corp) if kind != "hq" else &""
	for sd in cd.city_grid.sites:
		if sd != null and sd.tier == 1 and site == &"":
			site = sd.id
	# The place's `day` is false whatever the state: the live city close-up has only the night look (see the header).
	_backdrop.show_place(BackdropCatalog.place(corp, kind == "hq", false, site))


## The cool day look of the close-up (CityMotionConfig day_*; rain off), keys as BackdropCatalog.city_look.
func _day_look(focus: String) -> Dictionary:
	var m := load("res://content/config/city_motion_config.tres") as CityMotionConfigData
	var look := BackdropCatalog.city_look(CityView3D.CONFIG, focus)
	look["ramp"] = m.day_ramp.duplicate()
	look["sky"] = m.day_sky
	look["window_gain"] = m.day_window_gain
	look["neon_gain"] = m.day_neon_gain
	look["haze"] = m.day_haze
	look["grade"] = m.day_grade
	look["bloom"] = m.day_bloom
	look["glow_threshold"] = m.day_glow_threshold
	look["night"] = false
	look["rain_alpha"] = 0.0
	return look


func _process(_delta: float) -> void:
	_frame += 1
	var city := _backdrop.city
	var ready := city == null or (city.model != null and not city.is_processing())
	ready = ready and (_backdrop.on_city() or city == null)
	if ready and _ready_at < 0:
		_ready_at = _frame
	if _ready_at < 0 and _frame < MAX_WAIT:
		return
	if _day and city != null:
		city.set_night_share(0.0, _day_look(String(_backdrop.shot.get("focus", "hq"))))
	var since := _frame - maxi(_ready_at, 0)
	var settle := int(_args.get("settle", "40"))
	var state := _states[_step]
	var out := String(_args.get("out", "user://bake_backdrop"))
	if _phase == 0:
		if since < settle:
			return
		DirAccess.make_dir_recursive_absolute(out)
		_frame_img = get_viewport().get_texture().get_image()
		_frame_img.save_png("%s/%s.png" % [out, state])
		if _args.get("masks", "0") != "1" or city == null:
			_next(state)
			return
		_hide_target(city, state)
		_hidden_at = _frame
		_phase = 1
		return
	if _frame - _hidden_at < 6:
		return
	var b := get_viewport().get_texture().get_image()
	_mask(_frame_img, b).save_png("%s/%s_won.png" % [out, state])
	for mi in _hidden:
		mi.visible = true
	_next(state)


func _next(state: String) -> void:
	print("BAKE %s ready=%s" % [state, _ready_at >= 0])
	_step += 1
	if _step >= _states.size():
		RunManager.delete_save()
		if _reduce_was >= 0:
			Settings.reduce_effects = _reduce_was == 1
		get_tree().quit()
		return
	_load(_states[_step])


## Hides the target landmark's solid meshes (the HQ's own, or the fought Site's landmark).
func _hide_target(city: CityView3D, state: String) -> void:
	var cfg := CityView3D.CONFIG
	var head := state.rsplit("_", true, 1)[0].split("_", true, 1)
	var corp := StringName(head[1])
	var node: Node3D
	var keep: PackedStringArray = cfg.backdrop_fit_keep
	if head[0] == "hq":
		node = city.landmarks.get(corp) as Node3D
		keep = cfg.backdrop_hq_fit_keep_by_corp.get(corp, cfg.backdrop_fit_keep)
	else:
		node = city.landmarks.get(CityView3D.SITE_KEY) as Node3D
	if node == null:
		push_error("BAKE: no target landmark for %s" % state)
		return
	for n in node.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		var hit := false
		for w in keep:
			hit = hit or String(mi.name).contains(w)
		if hit and mi.visible:
			mi.visible = false
			_hidden.append(mi)


## R = where hiding the target changed the frame (its silhouette), G = its lit pixels, at MASK_SIZE.
static func _mask(a: Image, b: Image) -> Image:
	var w := a.get_width()
	var h := a.get_height()
	var out := Image.create(w, h, false, Image.FORMAT_RGB8)
	for y in h:
		for x in w:
			var ca := a.get_pixel(x, y)
			var cb := b.get_pixel(x, y)
			var d := maxf(absf(ca.r - cb.r), maxf(absf(ca.g - cb.g), absf(ca.b - cb.b)))
			var sil := 1.0 if d > SIL_DIFF else 0.0
			var lum := 0.2126 * ca.r + 0.7152 * ca.g + 0.0722 * ca.b
			out.set_pixel(x, y, Color(sil, sil * (1.0 if lum > LIGHT_LUMA else 0.0), 0.0))
	out.resize(MASK_SIZE.x, MASK_SIZE.y, Image.INTERPOLATE_BILINEAR)
	return out
