extends Control
## LOOK backdrop stills bake (windowed only; headless has no renderer). Drives CombatBackdrop's city path, like
## hq_run_lab's hq_ / site_ states, and saves for each state the GRADED frame (what the player sees of the close-up:
## the backdrop shader's city grade, exposure, tint and focus included) and the won mask, so the combat stills
## (assets/backdrops/combat/<corp>_<hq|site>_<night|day>.jpg + _won.png) are the live close-up frozen:
##   python tools/run_windowed.py --log <f> -- --resolution 1280x720 res://tools/art_pipeline/backdrop/bake_backdrop_stills.tscn
##     -- --out=<dir> --states=hq_solace_night,hq_solace_day [--masks=1] [--reduce-effects=1] [--settle=40]
## State = <hq|site>_<corp>_<night|day>. The live city close-up is always the night look (CombatBackdrop has no day);
## a `day` state bakes that same night frame (designer 2026-10-22: day stills = night stills until a live day look
## exists, so a day run's still hands over to the city it shows).
## Writes <out>/<state>.png (window size) and, with --masks=1, <out>/<state>_won.png (640x360: R = the
## target's silhouette, the HQ / Site landmark's solid meshes, G = its lit pixels), found by differencing the frame with
## those meshes hidden (rain, shader time and effects frozen with --reduce-effects=1).
## --old-dir=<dir holding the previous <state>.jpg stills>: the frame must differ clearly from the old still (mean channel
## difference over the frame >= OLD_DIFF_MIN), else the bake fails. Prints "BAKE <state> ready=<bool>" per state.

const MAX_WAIT := 900
const MASK_SIZE := Vector2i(640, 360)
## The mask's silhouette: the frame difference (max channel, 0..1) that counts as the target.
const SIL_DIFF := 0.10
## The mask's lights: the lit pixel's luma (graded frame) that counts as the target's own light.
const LIGHT_LUMA := 0.62
## --old-dir: the least mean difference (0..1) the new frame must have from the old still.
const OLD_DIFF_MIN := 0.03

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
var _fail: bool = false


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	_states = PackedStringArray(String(_args.get("states", "hq_solace_night")).split(","))
	Settings.city_quality = int(_args.get("tier", "1"))  # the close-up needs a city tier that takes it (CityConfig.backdrop_city_tiers)
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


func _process(_delta: float) -> void:
	_frame += 1
	if _ready_at < 0 and _backdrop.holding():
		_backdrop._hold_s = 0.0  # a cold city build outlasts backdrop_city_wait_s: the bake waits for it (it is not a fight)
	var city := _backdrop.city
	var ready := city == null or (city.model != null and not city.is_processing())
	ready = ready and (_backdrop.on_city() or city == null)
	if ready and _ready_at < 0:
		_ready_at = _frame
	if _ready_at < 0 and _frame < MAX_WAIT:
		return
	var since := _frame - maxi(_ready_at, 0)
	var settle := int(_args.get("settle", "40"))
	var state := _states[_step]
	var out := String(_args.get("out", "user://bake_backdrop"))
	if _phase == 0:
		if since < settle:
			return
		# The bake saves the LIVE close-up only: CombatBackdrop gives up on a slow city after backdrop_city_wait_s and shows
		# the baked still, which must never be baked into a still (the hold is kept in _process, in this tool alone).
		if city == null or not _backdrop.on_city() or city.chunks_built() <= 0:
			push_error("BAKE FAILED %s: the live close-up is not showing (on_city=%s)" % [state, _backdrop.on_city()])
			_fail = true
			get_tree().quit(1)
			return
		DirAccess.make_dir_recursive_absolute(out)
		_frame_img = get_viewport().get_texture().get_image()
		_check_not_old(state)
		_frame_img.save_png("%s/%s.png" % [out, state])
		if _args.get("masks", "0") != "1" or city == null:
			_next(state)
			return
		_hide_target(city, state)
		_hidden_at = _frame
		_phase = 1
		return
	if _frame - _hidden_at < 20:
		return
	var b := get_viewport().get_texture().get_image()
	b.save_png("%s/%s_hidden.png" % [out, state])
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
	if head[0] == "hq":
		node = city.landmarks.get(corp) as Node3D
	else:
		node = city.landmarks.get(CityView3D.SITE_KEY) as Node3D
	if node == null:
		push_error("BAKE: no target landmark for %s" % state)
		return
	for n in node.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		var hit := not String(mi.name).contains("id_ground")  # the whole landmark but its ground tile
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
	return _keep_target(out)


## Keeps only the silhouette's biggest connected piece and the pieces standing in its column span (the target and its
## detached parts): hiding the target also uncovers buildings the view cut hid for it, which are not the target.
static func _keep_target(m: Image) -> Image:
	var w := m.get_width()
	var h := m.get_height()
	var label := PackedInt32Array()
	label.resize(w * h)
	var comps: Array = []  # each {"n": px count, "x0", "x1", "px": PackedInt32Array}
	for y0 in h:
		for x0 in w:
			if label[y0 * w + x0] != 0 or m.get_pixel(x0, y0).r < 0.5:
				continue
			var id := comps.size() + 1
			var stack: Array[Vector2i] = [Vector2i(x0, y0)]
			label[y0 * w + x0] = id
			var px := PackedInt32Array()
			var lo := x0
			var hi := x0
			while not stack.is_empty():
				var p: Vector2i = stack.pop_back()
				px.append(p.y * w + p.x)
				lo = mini(lo, p.x)
				hi = maxi(hi, p.x)
				for d: Vector2i in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1), Vector2i(1, 1), Vector2i(-1, -1), Vector2i(1, -1), Vector2i(-1, 1)]:
					var q := p + d
					if q.x < 0 or q.y < 0 or q.x >= w or q.y >= h or label[q.y * w + q.x] != 0 or m.get_pixel(q.x, q.y).r < 0.5:
						continue
					label[q.y * w + q.x] = id
					stack.append(q)
			comps.append({"n": px.size(), "x0": lo, "x1": hi, "px": px})
	var out := Image.create(w, h, false, Image.FORMAT_RGB8)
	if comps.is_empty():
		return out
	var big: Dictionary = comps[0]
	for c: Dictionary in comps:
		if int(c["n"]) > int(big["n"]):
			big = c
	for c: Dictionary in comps:
		if int(c["x1"]) < int(big["x0"]) or int(c["x0"]) > int(big["x1"]):
			continue
		for i: int in c["px"]:
			out.set_pixel(i % w, i / w, m.get_pixel(i % w, i / w))
	return out


## --old-dir given: fails the bake when the frame is too like the previous still (a still baked from a still).
func _check_not_old(state: String) -> void:
	if not _args.has("old-dir"):
		return
	var p := "%s/%s.jpg" % [String(_args["old-dir"]), state.replace("_solace_", "_solace_")]
	var old := Image.load_from_file(p)
	if old == null or old.is_empty():
		push_error("BAKE: no old still %s" % p)
		return
	var a := _frame_img.duplicate() as Image
	a.convert(Image.FORMAT_RGB8)
	old.convert(Image.FORMAT_RGB8)
	old.resize(a.get_width(), a.get_height())
	var sum := 0.0
	for y in range(0, a.get_height(), 4):
		for x in range(0, a.get_width(), 4):
			var ca := a.get_pixel(x, y)
			var co := old.get_pixel(x, y)
			sum += (absf(ca.r - co.r) + absf(ca.g - co.g) + absf(ca.b - co.b)) / 3.0
	var d := sum / float((a.get_height() / 4) * (a.get_width() / 4))
	print("BAKE %s diff_from_old=%.3f" % [state, d])
	if d < OLD_DIFF_MIN:
		push_error("BAKE FAILED %s: the frame is the old still (diff %.3f < %.3f)" % [state, d, OLD_DIFF_MIN])
		get_tree().quit(1)
