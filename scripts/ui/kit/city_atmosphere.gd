class_name CityAtmosphere
extends Node
## A lit, living city that reacts to the player (art pass W7, ART_BIBLE §9, §2 CITY, §8 T0,
## §12, §13). One per live NeonCity (`NeonCity.atmosphere()`; never on a bake painter). It
## holds the CityState the screens pass down and turns it into:
## - lighting and grade in the city's own composite (city_live.gdshader, `lit`): per-ink
##   glow, haze bands, wet streets, rim light, the context grade and campaign lean, Heat's
##   searchlights / rim flicker / HUNTED grade, territory light in the haze, map dim + blur
##   and the UI calm zones;
## - T0 life (CityLife: aircraft, drones, billboards) and the Cell's turf (CityTurf: hatch
##   and spray tags on claimed buildings);
## - the light layers' brightness (window lights, beacons) under the grade, and their calm
##   zones and T0 period floor (city_lights.gdshader).
## Signal up, call down: it reads what the screens set (and, for a city that follows the
## campaign, reads the campaign like NeonCity's influence does) and never writes game state.
## Numbers: content/config/city_look.tres (CityLookData).
##
## Public API (call on `city.atmosphere()`, or the same methods on CyberdeckBackground /
## WireframeBackground):
##   set_context(&"title" | &"hq" | &"net" | &"combat")
##   set_heat(heat)                       # band from Palette.heat_band (config levels)
##   set_campaign_progress(f, corp_id)    # 0..1, grade leans up to 20% to the corp's hue
##   set_territory(claims)                # PackedVector2Array of claimed Sites' grid lots
##   set_map_mode(on)                     # §9.5: dim 40% + blur; the map overlay stays sharp
##   set_calm_zones(rects)                # canvas (global) rects of text panels
##   set_calm_controls(controls)          # or the panels themselves (followed as they move)
##   follow_campaign(on)                  # heat / progress / territory from RunManager when not set

## Quality tier (ART_BIBLE §13: 0 low (no glow, no reflections), 1 medium, 2 high); -1 uses
## city_look.tres's default. A design tool or an options row may set it.
static var quality: int = -1
## Off switch: the pre-W7 look (the review's "before" captures); never off in the game.
static var enabled: bool = true
## How often (s) a followed campaign is read again.
const POLL := 0.5

var city: NeonCity
var state: CityState = CityState.new()
var cfg: CityLookData
var life: CityLife
var turf: CityTurf
## Grade from the last push (tests and the lab).
var grade: Dictionary = {}
## Which state fields a screen set explicitly (the rest follow the campaign when allowed).
var _set: Dictionary = {}
var _follow: bool = true
var _poll_t: float = 0.0
var _calm_rects: Array[Rect2] = []
var _calm_controls: Array[Control] = []
var _fx_mat: ShaderMaterial
var _grade_mat: ShaderMaterial
var _sig: String = ""
var _dirty: bool = true
## Only the camera, the screen or a calm control moved: the screen-space uniforms follow
## (`_push_screen`, cheaper than a whole push: the title's pan moves the city every frame).
var _moved: bool = false
var _board_key: String = ""


func _init(p_city: NeonCity = null) -> void:
	name = "CityAtmosphere"
	cfg = CityLookData.shipped()
	if p_city == null:
		return
	city = p_city
	turf = CityTurf.new()
	turf.city = city
	turf.cfg = cfg
	life = CityLife.new()
	life.city = city
	life.cfg = cfg
	life.state = state
	# Above the view's image, the live lights and the fx layer; the territory marks and map
	# overlays stay above the city (NeonCity's own later children and the screens').
	_fx_mat = ShaderMaterial.new()
	_fx_mat.shader = NeonCity.LIVE_SHADER
	_fx_mat.set_shader_parameter("mode", 1)
	city._fx.use_parent_material = false
	city._fx.material = _fx_mat
	_grade_mat = ShaderMaterial.new()
	_grade_mat.shader = NeonCity.LIVE_SHADER
	_grade_mat.set_shader_parameter("mode", 2)
	_grade_mat.set_shader_parameter("scan_strength", 0.0)
	city._sil.material = _grade_mat
	city._veil.material = _grade_mat
	state.context = default_context()
	# Last: added to a city in the tree, this node's _ready runs at once (and pushes).
	city._view.add_child(turf)
	city._view.add_child(life)
	city._view.add_child(self)


func _ready() -> void:
	Settings.changed.connect(_mark)
	_push()


## The context a city starts in until a screen names one: the net for a net city, the title
## while the menu pans, else the HQ window.
func default_context() -> StringName:
	if city == null:
		return &"title"
	if city.net_mode:
		return &"net"
	return &"title" if city.pan else &"hq"


# --- The public API (call down from the screens) ----------------------------------------------

## The screen's context: &"title", &"hq", &"net" or &"combat" (the grade, §9.1).
func set_context(context: StringName) -> void:
	_set["context"] = true
	if CityLookData.CONTEXTS.has(context) and context != state.context:
		state.context = context
		_mark()


## Heat (the band follows Palette.heat_band, from the config's MAJOR levels).
func set_heat(heat: int) -> void:
	_set["heat"] = true
	if heat != state.heat:
		state.set_heat(heat)
		_mark()


## The Heat band alone (CityState.Band), for a screen that knows only the band.
func set_heat_band(band: int) -> void:
	_set["heat"] = true
	band = clampi(band, CityState.Band.COOL, CityState.Band.HUNTED)
	if band != state.band:
		state.band = band
		_mark()


## Campaign progress 0..1 and the target corporation: the grade leans up to
## `progress_max_shift` toward its hue (§9.3).
func set_campaign_progress(progress: float, corp_id: StringName) -> void:
	_set["progress"] = true
	progress = clampf(progress, 0.0, 1.0)
	if not is_equal_approx(progress, state.progress) or corp_id != state.corp_id:
		state.progress = progress
		state.corp_id = corp_id
		_mark()


## The Cell's claimed Sites (grid lots): hatch, spray tags and light in the haze (§9.3).
func set_territory(claims: PackedVector2Array) -> void:
	_set["territory"] = true
	if claims != state.claims:
		state.claims = claims
		_mark()


## Maps over the city (§9.5): the city dims by `map_dim` (40%) and blurs slightly. Nodes,
## links and labels belong to the map overlay above it and are never dimmed.
func set_map_mode(on: bool) -> void:
	if on != state.map_mode:
		state.map_mode = on
		_mark()


## UI calm zones (§2 CITY): canvas (global) rects of text panels. Behind them the city is
## darker and less saturated, and nothing moves (live lights hidden, life left out).
func set_calm_zones(rects: Array[Rect2]) -> void:
	_calm_rects = rects.duplicate()
	_mark()


## Calm zones that follow these controls' global rects while they are visible.
func set_calm_controls(controls: Array[Control]) -> void:
	_calm_controls = controls.duplicate()
	_mark()


## Whether heat, progress and territory follow the city's campaign when a screen hasn't set
## them (on by default for a city that follows one).
func follow_campaign(on: bool) -> void:
	_follow = on
	_mark()


## The calm zones now in the city's local px (the canvas rects and the followed controls).
func calm_local() -> Array[Rect2]:
	var out: Array[Rect2] = []
	if city == null or not city.is_inside_tree():
		return out
	var inv := city.get_global_transform_with_canvas().affine_inverse()
	for r in _canvas_calm():
		out.append(inv * r)
	return out


# --- Internals ----------------------------------------------------------------------------------

func _mark() -> void:
	_dirty = true


func _canvas_calm() -> Array[Rect2]:
	var out: Array[Rect2] = _calm_rects.duplicate()
	for c in _calm_controls:
		if is_instance_valid(c) and c.is_visible_in_tree():
			var xf := c.get_global_transform_with_canvas()
			out.append(xf * Rect2(Vector2.ZERO, c.size))
	return out


## Reads the followed campaign for what no screen set (read only).
func _poll_campaign() -> void:
	if not _follow or city == null:
		return
	var camp := city._followed_campaign()
	if camp == null:
		return
	if not _set.has("heat") and camp.heat != state.heat:
		state.set_heat(camp.heat)
		_dirty = true
	var inf := city.influence
	if inf.is_empty():
		return
	if not _set.has("territory"):
		var claims := PackedVector2Array()
		for s: Dictionary in inf.get("sources", []):
			if float(s["w"]) >= CityInfluence.WEIGHT_CLAIMED + CityInfluence.WEIGHT_DISABLED * 0.5:
				claims.append(s["at"])
		if claims != state.claims:
			state.claims = claims
			_dirty = true
	if not _set.has("progress"):
		var sites := (inf.get("sites", PackedVector2Array()) as PackedVector2Array).size()
		var won := 0.0
		for s: Dictionary in inf.get("sources", []):
			won += clampf(float(s["w"]), 0.0, 1.0)
		var progress := clampf(won / maxf(1.0, sites), 0.0, 1.0)
		var corp: StringName = inf.get("corp", &"")
		if not is_equal_approx(progress, state.progress) or corp != state.corp_id:
			state.progress = progress
			state.corp_id = corp
			_dirty = true


func _process(delta: float) -> void:
	if city == null:
		return
	_poll_t += delta
	if _poll_t >= POLL:
		_poll_t = 0.0
		_poll_campaign()
	# Until a screen names the context, it follows the city (the title turns its pan on
	# after the city is made).
	if not _set.has("context") and state.context != default_context():
		state.context = default_context()
		_dirty = true
	# The camera, the screen or a calm control moved: the screen-space uniforms follow.
	var sig := "%s|%s|%s|%s" % [city.get_global_transform_with_canvas(), Vector2(city._ox, city._oy), city.size, _canvas_calm()]
	if sig != _sig:
		_sig = sig
		_moved = true
	if _dirty:
		_push()
	elif _moved:
		_push_screen()
	if not city.is_visible_in_tree() or not enabled:
		return
	if Fx.effects_enabled():
		life.t += delta
		life.refresh_items()


## The screen fraction (0..1 of the render target) of city-local point `p`.
func _frac(p: Vector2) -> Vector2:
	var vp := city.get_viewport()
	var px := vp.get_final_transform() * (city.get_global_transform_with_canvas() * p)
	return px / _target_size()


func _target_size() -> Vector2:
	var vp := city.get_viewport()
	var tex := vp.get_texture()
	var s := Vector2(tex.get_size()) if tex != null else Vector2.ZERO
	if s.x < 1.0 or s.y < 1.0:
		s = vp.get_visible_rect().size
	return Vector2(maxf(1.0, s.x), maxf(1.0, s.y))


## Canvas px -> screen fraction (a calm rect).
func _frac_canvas(r: Rect2) -> Vector4:
	var vp := city.get_viewport()
	var xf := vp.get_final_transform()
	var a := xf * r.position / _target_size()
	var b := xf * r.end / _target_size()
	return Vector4(a.x, a.y, b.x, b.y)


## The quality tier in use.
func tier() -> int:
	return clampi(cfg.quality_default if quality < 0 else quality, 0, 2)


## Hands the state to the shaders and layers.
func _push() -> void:
	_dirty = false
	_moved = false
	if city == null or not city.is_inside_tree():
		return
	var on := enabled and not city._painter
	var reduce := not Fx.effects_enabled()
	grade = CityGrade.params(state, cfg, city.dim, Settings.high_contrast)
	var vm := city._view.material as ShaderMaterial
	var size := _target_size()
	var aspect := size.x / size.y
	var calm := _calm_array()
	var feather := cfg.calm_feather_px / maxf(1.0, city.get_viewport().get_visible_rect().size.y)
	for m: ShaderMaterial in [vm, _fx_mat, _grade_mat]:
		m.set_shader_parameter("lit", on)
		m.set_shader_parameter("aspect", aspect)
		m.set_shader_parameter("g_contrast", grade["contrast"])
		m.set_shader_parameter("g_saturation", grade["saturation"])
		m.set_shader_parameter("g_warmth", grade["warmth"])
		m.set_shader_parameter("g_lift", grade["lift"])
		m.set_shader_parameter("g_dim", grade["dim"])
		m.set_shader_parameter("g_map_dim", grade["map_dim"])
		m.set_shader_parameter("g_tint", grade["tint"])
		m.set_shader_parameter("g_tint_amount", grade["tint_amount"])
		m.set_shader_parameter("calm", calm)
		m.set_shader_parameter("calm_count", calm.size())
		m.set_shader_parameter("calm_dim", grade["calm_dim"])
		m.set_shader_parameter("calm_desat", grade["calm_desaturate"])
		m.set_shader_parameter("calm_feather", feather)
	_fx_mat.set_shader_parameter("scan_strength", vm.get_shader_parameter("scan_strength"))
	_fx_mat.set_shader_parameter("flicker", vm.get_shader_parameter("flicker"))
	_push_lighting(vm, reduce, on)
	# The territory spread's lasting wash is a CELL_TURF hatch (influence_reveal), not khaki.
	var fm := city._front_layer.material as ShaderMaterial
	fm.set_shader_parameter("hatch_px", cfg.hatch_spacing_px if on else 0.0)
	fm.set_shader_parameter("hatch_width", cfg.hatch_width_px)
	fm.set_shader_parameter("wash_gain", cfg.wash_gain if on else 1.0)
	# The light layers: dimmed with the grade, hidden in calm zones, toggling no faster than T0.
	var k := CityGrade.brightness(grade) if on else 1.0
	for layer: Control in [city._lights_layer, city._beacons_layer]:
		layer.self_modulate = Color(k, k, k, 1.0)
		var lm := layer.material as ShaderMaterial
		lm.set_shader_parameter("min_period", cfg.window_period_min if on else 0.0)
		lm.set_shader_parameter("calm", calm)
		lm.set_shader_parameter("calm_count", calm.size() if on else 0)
		lm.set_shader_parameter("calm_feather", feather)
		lm.set_shader_parameter("aspect", aspect)
	turf.visible = on
	life.visible = on
	turf.modulate = Color(k, k, k, 1.0)
	life.modulate = Color(k, k, k, 1.0)
	turf.set_claims(state.claims if on else PackedVector2Array())
	_place_life()
	life.calm_local = calm_local()
	life.refresh_items()


## The calm zones as screen fractions (at most 8).
func _calm_array() -> PackedVector4Array:
	var calm := PackedVector4Array()
	for r in _canvas_calm():
		if calm.size() < 8:
			calm.append(_frac_canvas(r))
	return calm


## The camera, the screen or a calm control moved: only the screen-space uniforms (calm
## zones, rim lights, searchlights, leaks) and the life's calm rects follow.
func _push_screen() -> void:
	_moved = false
	if city == null or not city.is_inside_tree():
		return
	var on := enabled and not city._painter
	var calm := _calm_array()
	for m: ShaderMaterial in [city._view.material, _fx_mat, _grade_mat]:
		m.set_shader_parameter("calm", calm)
		m.set_shader_parameter("calm_count", calm.size())
	for layer: Control in [city._lights_layer, city._beacons_layer]:
		var lm := layer.material as ShaderMaterial
		lm.set_shader_parameter("calm", calm)
		lm.set_shader_parameter("calm_count", calm.size() if on else 0)
	_push_lighting(city._view.material as ShaderMaterial, not Fx.effects_enabled(), on)
	life.calm_local = calm_local()


## The lighting uniforms: glow per ink, haze, wet streets, rim lights, searchlights, leaks.
func _push_lighting(vm: ShaderMaterial, reduce: bool, on: bool) -> void:
	var taps: int = cfg.quality_glow_taps[tier()]
	var inks := PackedVector4Array()
	for c in CityPalette.INKS:
		var n := Vector3(c.r, c.g, c.b).normalized()
		inks.append(Vector4(n.x, n.y, n.z, 1.0))
	vm.set_shader_parameter("inks", inks)
	vm.set_shader_parameter("ink_gain", cfg.ink_glow)
	vm.set_shader_parameter("glow_threshold", cfg.glow_threshold)
	vm.set_shader_parameter("glow_radius", cfg.glow_radius_px)
	vm.set_shader_parameter("glow_strength", cfg.glow_strength)
	vm.set_shader_parameter("glow_taps", taps)
	var bands := PackedVector3Array()
	for i in cfg.haze_band_y.size():
		bands.append(Vector3(cfg.haze_band_y[i], cfg.haze_band_width[i], cfg.haze_band_alpha[i]))
	vm.set_shader_parameter("haze_bands", bands)
	vm.set_shader_parameter("haze_count", bands.size())
	vm.set_shader_parameter("haze_color", CityPalette.HAZE)
	vm.set_shader_parameter("haze_gain", grade["haze_gain"])
	vm.set_shader_parameter("haze_drift", cfg.haze_drift)
	vm.set_shader_parameter("haze_period", cfg.haze_drift_period)
	vm.set_shader_parameter("refl_strength", cfg.reflection_strength if tier() > 0 else 0.0)
	vm.set_shader_parameter("refl_reach", cfg.reflection_reach_px)
	vm.set_shader_parameter("refl_period", cfg.reflection_ripple_period)
	vm.set_shader_parameter("refl_ripple", cfg.reflection_ripple_px)
	vm.set_shader_parameter("blur_px", grade["blur_px"])
	# Rim light from the brightest signs in view, then FLAGGED's red/blue on corp buildings.
	var rim_pos := PackedVector4Array()
	var rim_col := PackedVector4Array()
	var view := Rect2(Vector2.ZERO, city.size)
	var signs: Array[Dictionary] = []
	for sg: Dictionary in city._signs:
		var at: Vector2 = (sg["pos"] as Vector2) + city._shift
		if view.grow(city.size.y * cfg.rim_radius).has_point(at):
			signs.append({"at": at, "color": sg["color"], "d": at.distance_squared_to(view.get_center())})
	signs.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a["d"] < b["d"])
	var rim_max := mini(cfg.rim_lights_max, 8)
	for sg in signs.slice(0, rim_max):
		var f := _frac(sg["at"])
		var c: Color = sg["color"]
		rim_pos.append(Vector4(f.x, f.y, cfg.rim_radius, cfg.rim_strength))
		rim_col.append(Vector4(c.r, c.g, c.b, 1.0))
	var flicker_from := rim_pos.size()
	if state.patrols() and not reduce and state.corp_id != &"":
		for p in _corp_points():
			if rim_pos.size() >= 8:
				break
			var f := _frac(p)
			rim_pos.append(Vector4(f.x, f.y, cfg.rim_radius * 1.3, cfg.flagged_rim_strength))
			rim_col.append(Vector4(1, 1, 1, 1))
	vm.set_shader_parameter("rim_pos", rim_pos)
	vm.set_shader_parameter("rim_col", rim_col)
	vm.set_shader_parameter("rim_count", rim_pos.size())
	vm.set_shader_parameter("flicker_from", flicker_from)
	vm.set_shader_parameter("flicker_hz", cfg.flagged_flicker_hz)
	vm.set_shader_parameter("police_red", CityPalette.POLICE_RED)
	vm.set_shader_parameter("police_blue", CityPalette.POLICE_BLUE)
	# NOTICED: searchlights sweep from the target corp's district (kept on screen).
	var search := PackedVector4Array()
	if state.searchlights() and on:
		var hq := _corp_hq_local()
		for i in cfg.searchlight_count:
			var f := _frac(hq + Vector2((i - (cfg.searchlight_count - 1) * 0.5) * NeonCity.TILE_A * 6.0, 0))
			f = Vector2(clampf(f.x, 0.08, 0.92), clampf(f.y, 0.35, 1.0))
			search.append(Vector4(f.x, f.y, i * 2.4, cfg.searchlight_length))
	vm.set_shader_parameter("search", search)
	vm.set_shader_parameter("search_count", search.size())
	vm.set_shader_parameter("search_period", cfg.searchlight_period)
	vm.set_shader_parameter("search_arc", deg_to_rad(cfg.searchlight_arc_deg))
	vm.set_shader_parameter("search_width", tan(deg_to_rad(cfg.searchlight_width_deg)))
	vm.set_shader_parameter("search_alpha", cfg.searchlight_alpha)
	vm.set_shader_parameter("search_color", CityPalette.SEARCHLIGHT)
	# Claimed territory: CELL_TURF light leaking into the haze.
	var leaks := PackedVector4Array()
	var lot_px := (_frac(city.grid_to_local(0, 0) + Vector2(NeonCity.TILE_A, 0)) - _frac(city.grid_to_local(0, 0))).x * (_target_size().x / _target_size().y)
	for c in state.claims:
		if leaks.size() >= 8:
			break
		var f := _frac(city.grid_to_local(c.x + 0.5, c.y + 0.5))
		leaks.append(Vector4(f.x, f.y, absf(lot_px) * cfg.leak_radius_lots, cfg.leak_strength))
	vm.set_shader_parameter("leaks", leaks)
	vm.set_shader_parameter("leak_count", leaks.size())
	vm.set_shader_parameter("leak_color", Palette.CELL_TURF)


## The target corp's HQ (city-local px): its landmark's centre, or the view's centre.
func _corp_hq_local() -> Vector2:
	if state.corp_id == &"":
		return city.size * 0.5
	var g := NeonCity.hq_of(state.corp_id) + Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS) * 0.5
	return city.grid_to_local(g.x, g.y)


## Corp buildings for FLAGGED's rim flicker (city-local px): the HQ's corners.
func _corp_points() -> Array[Vector2]:
	var out: Array[Vector2] = []
	var g := NeonCity.hq_of(state.corp_id)
	for q: Vector2 in [Vector2(0, 0), Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS), Vector2(NeonCity.HQ_LOTS, 0), Vector2(0, NeonCity.HQ_LOTS)]:
		out.append(city.grid_to_local(g.x + q.x, g.y + q.y))
	return out


## Billboards on roofs in view and the patrols' centres (world px), when the camera or the
## look changes.
func _place_life() -> void:
	life.state = state
	var off := Vector2(city._ox, city._oy)
	var patrols := PackedVector2Array()
	if state.corp_id != &"":
		patrols.append(_corp_hq_local() - off)
	for c in state.claims:
		patrols.append(city.grid_to_local(c.x + 0.5, c.y + 0.5) - off)
	if patrols.is_empty():
		patrols.append(city.size * 0.5 - off)
	life.patrol_points = patrols
	var key := "%s|%s|%s|%s|%s" % [city.city_seed, city.district, state.corp_id, off.snapped(Vector2.ONE * NeonCity.REGION_SNAP), city.size.snapped(Vector2.ONE * NeonCity.REGION_SNAP)]
	if key == _board_key:
		return
	_board_key = key
	var boards: Array[Dictionary] = []
	var taken := {}
	var mid := city._grid_of(city.size * 0.5)
	var span := maxf(city.size.x / NeonCity.TILE_A, city.size.y / NeonCity.TILE_B) * 0.35
	for i in cfg.billboards_max:
		var gx := mid.x + (CityLife.hash01(city.city_seed, 701, i) - 0.5) * 2.0 * span
		var gy := mid.y + (CityLife.hash01(city.city_seed, 703, i) - 0.5) * 2.0 * span
		var l := city.nearest_building(gx, gy, 3, taken)
		taken[l] = true
		var rec := city.roof_of(l.x, l.y)
		if rec.is_empty():
			continue
		var roof: PackedVector2Array = rec["roof"]
		var top := roof[0]
		for p in roof:
			if p.y < top.y:
				top = p
		var corp := city.territory_at(l.x, l.y)
		if corp == &"":
			corp = state.corp_id if state.corp_id != &"" else city.district
		if corp == &"":
			continue
		boards.append({"at": top - off, "corp": corp})
	life.boards = boards
