class_name CombatBackdrop
extends Control
## The combat backdrop (ART_BIBLE v2 §3.1, §3.14; DECISIONS D17 on its plan default): a close-up
## still of the place being attacked fills the screen (the corporation's HQ for a boss, the target
## Site otherwise, night or the cool day; BackdropCatalog picks it), softened and darkened in a
## pool behind each wheel, with darker bands under the top bar and the hand. Once the fight is won
## the district dims and the target's own lights turn Cell colours, with a yellow pencilled
## "OURS NOW" over it (`play_won`).
## Layers, bottom to top: the still, `heat_layer` (Heat on combat, §3.15: ART-3 draws its beacons
## and searchlights there, behind the wheels' pools in spirit), the pencil.
## ART-8 8w (D17 on the city): where the city quality tier takes it (CityConfig.backdrop_city_tiers,
## BackdropCatalog.city_mode) the backdrop is a close-up of the one city (its own CityView3D:
## the corp's HQ for a boss, the DISPATCH canyon staged for the Cell, the run's Site lot for a
## regular fight) drawn through the same shader, so the pools and bands work on it as on a still;
## the still shows until the city's model is in, and stays the fallback below the tier. Won on the
## city: the Site's windows turn Cell colours (SiteWonLights, 5d) and the district dims outside an
## ellipse round the target (no mask).
## Parity fix S-ARENA: the close-up keeps the concept's lit city once it settles (its own lit
## night look and a canvas grade, CityConfig backdrop_*), frames the whole HQ landmark or the
## Site's building (BackdropCatalog.fit_box), and renders at most backdrop_render_height tall.
## View only: it reads the wheels it is given (`wheel_source`) and the campaign, never changes them.

const SHADER := preload("res://shaders/arena/combat_backdrop.gdshader")
## The fight-won lights (and the pencil coming in at their end).
const WON_MOTION := &"backdrop_won_lights"
## Pools at most (the shader's uniforms: the operative and up to three enemy wheels).
const POOL_UNIFORMS: Array[StringName] = [&"pool_a", &"pool_b", &"pool_c", &"pool_d"]
## A wheel's pool reaches this far past its disc (its needles' band), times its disc radius.
const POOL_REACH := 1.25
## The district outside the target dims to this once won (§3.14: about 62 %).
const DISTRICT_DIM := 0.62
## "OURS NOW": size at 720 px of height, tilt (rad), lowest share of the height it stands at (clear
## of the top bar), and its ink outline (px at 720).
const OURS_NOW_PX := 34
const OURS_NOW_TILT := -0.09
const OURS_NOW_MIN_Y := 0.16
const OURS_NOW_OUTLINE := 6
## The design height the pencil's size is given at.
const DESIGN_HEIGHT := 720.0
## D17 on the city: how far (lots) a Site's point looks for its building.
const SITE_SEARCH := 4

## Returns the WheelViews (or anything with `combatant`, `lookup`, `global_center()` and
## `disc_radius()`) whose pools this backdrop softens; the combat scene sets it.
var wheel_source: Callable = Callable()
## Heat on combat (ART-3, §3.15) draws here: above the still, under the pencil.
var heat_layer: Control
## The place shown ({corp, kind, day}: BackdropCatalog.place).
var place: Dictionary = {}
## 0..1: the fight-won look (the shader's `won`).
var won: float = 0.0:
	set(v):
		won = v
		_sync_won()

var _mat: ShaderMaterial
var _still: Control
var _won_still: Control
var _ink: Control
var _tex: Texture2D = null
var _won_tex: Texture2D = null
var _enemy_key: String = ""
var _pools_sig: String = ""
var _won_tween: Tween = null
## D17 on the city: the close-up's city (null on the stills) and its shot (BackdropCatalog.city_shot).
var city: CityView3D = null
var shot: Dictionary = {}
var _city_ready: bool = false
var _won_lights: SiteWonLights = null


func _init() -> void:
	name = "CombatBackdrop"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	_mat.set_shader_parameter(&"lime", Palette.CELL_ACID)
	_mat.set_shader_parameter(&"pink", Palette.CELL_PINK)
	_mat.set_shader_parameter(&"district_dim", DISTRICT_DIM)
	_mat.set_shader_parameter(&"pool_dark", CityView3D.CONFIG.backdrop_pool_dark)
	_mat.set_shader_parameter(&"pool_falloff", CityView3D.CONFIG.backdrop_pool_falloff)
	_still = _layer("Still", _draw_still)
	_still.material = _mat
	_won_still = _layer("WonStill", _draw_won_still)
	_won_still.material = _mat
	_won_still.visible = false
	heat_layer = _layer("HeatLayer", Callable())
	_ink = _layer("OursNow", _draw_ink)
	resized.connect(_on_resized)


func _ready() -> void:
	MotionSkip.register_passive(self)


func _layer(n: String, draw_fn: Callable) -> Control:
	var c := Control.new()
	c.name = n
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	if draw_fn.is_valid():
		c.draw.connect(draw_fn)
	add_child(c)
	return c


## Shows the still for `p` (BackdropCatalog.place); a new place (another fight) starts un-won.
func show_place(p: Dictionary) -> void:
	if p == place and _tex != null:
		return
	var fresh := place.is_empty()  # the first place keeps a won look already landed
	place = p.duplicate()
	var path := BackdropCatalog.still_path(place)
	_tex = load(path) as Texture2D if path != "" else null
	var won_path := BackdropCatalog.won_still_path(place)
	_won_tex = load(won_path) as Texture2D if won_path != "" else null
	var mask_path := BackdropCatalog.won_mask_path(place)
	_mat.set_shader_parameter(&"won_mask", load(mask_path) as Texture2D if mask_path != "" else null)
	_mat.set_shader_parameter(&"use_mask", true)
	# A won look that is another still crossfades to it; the district does not dim twice.
	_mat.set_shader_parameter(&"district_dim", 1.0 if _won_tex != null else DISTRICT_DIM)
	_use_city()
	if _tex != null:
		_mat.set_shader_parameter(&"aspect", float(_tex.get_width()) / float(_tex.get_height()))
	if not fresh:
		_stop_won()
		won = 0.0
	else:
		_sync_won()
	_pools_sig = ""
	_still.queue_redraw()


## The fight is won: the district dims and the target's lights turn Cell colours (D17), then the
## pencil writes OURS NOW. `instant` (a skip, no replay) shows it landed at once.
func play_won(instant: bool = false) -> void:
	if won >= 1.0:
		return
	_stop_won()
	if instant:
		won = 1.0
		return
	_won_tween = Motion.run(WON_MOTION, self, ^"won", 1.0)


## True while the won look is coming in (MotionSkip).
func motion_running() -> bool:
	return _won_tween != null and _won_tween.is_valid() and _won_tween.is_running()


## Lands the won look at once (MotionSkip).
func complete_motion() -> void:
	if motion_running():
		_stop_won()
		won = 1.0


func _stop_won() -> void:
	if _won_tween != null and _won_tween.is_valid():
		_won_tween.kill()
	_won_tween = null


func _sync_won() -> void:
	if _mat == null:
		return
	if _won_lights != null:
		_won_lights.visible = won > 0.0
	_mat.set_shader_parameter(&"won", won if _won_tex == null else 0.0)
	_won_still.visible = _won_tex != null and won > 0.0
	_won_still.modulate.a = won
	_won_still.queue_redraw()
	_ink.queue_redraw()


func _process(_delta: float) -> void:
	if not wheel_source.is_valid():
		return
	var views: Array = wheel_source.call()
	_follow_fight(views)
	_follow_pools(views)


## Picks the place from the fight the wheels show (a boss among the enemies: its HQ) and the
## campaign (its corporation, day or night); a fight with a living enemy is not won.
func _follow_fight(views: Array) -> void:
	var enemies: Array[EnemyData] = []
	var keys := PackedStringArray()
	var alive := false
	for v in views:
		var c: CombatantState = v.combatant
		if c == null or c.is_player or c.is_satellite or v.lookup == null:
			continue
		enemies.append(v.lookup.get_content(c.source_id) as EnemyData)
		keys.append(String(c.source_id))
		alive = alive or c.is_alive()
	if enemies.is_empty():
		return
	var key := ",".join(keys)
	if key != _enemy_key:
		_enemy_key = key
		var site: StringName = RunManager.netrun.run.site_id if RunManager.netrun != null else &""
		show_place(BackdropCatalog.place_for(RunManager.campaign, enemies, site))
	if alive and won > 0.0 and not motion_running():
		won = 0.0  # a fight going on (a new one with the same foes) is not won


func _follow_pools(views: Array) -> void:
	var cover := _cover_rect()
	if cover.size.x <= 0.0:
		return
	var pools: Array[Vector3] = []
	for v in views:
		if pools.size() >= POOL_UNIFORMS.size():
			break
		var c: CombatantState = v.combatant
		if c == null or not (v as CanvasItem).is_visible_in_tree():
			continue
		var at: Vector2 = (v.global_center() - global_position - cover.position) / cover.size
		pools.append(Vector3(at.x, at.y, float(v.disc_radius()) * POOL_REACH / cover.size.x))
	var sig := str(pools)
	if sig == _pools_sig:
		return
	_pools_sig = sig
	for k in POOL_UNIFORMS.size():
		_mat.set_shader_parameter(POOL_UNIFORMS[k], pools[k] if k < pools.size() else Vector3.ZERO)


## The still's rect (local): it covers the view, centred, keeping its aspect.
func _cover_rect() -> Rect2:
	if _tex == null or size.x <= 0.0 or size.y <= 0.0:
		return Rect2(Vector2.ZERO, size)
	var ts := Vector2(_tex.get_width(), _tex.get_height())
	var s := maxf(size.x / ts.x, size.y / ts.y)
	var d := ts * s
	return Rect2((size - d) * 0.5, d)


func _on_resized() -> void:
	_pools_sig = ""
	if city != null and size.x >= 2.0 and size.y >= 2.0:
		city.set_view_size(render_px(size))
		_frame_city()
	_still.queue_redraw()
	_won_still.queue_redraw()
	_ink.queue_redraw()


func _draw_still() -> void:
	if _tex == null:
		_still.draw_rect(Rect2(Vector2.ZERO, size), Palette.NIGHT_SKY)
		return
	_still.draw_texture_rect(_tex, _cover_rect(), false)


func _draw_won_still() -> void:
	if _won_tex != null:
		_won_still.draw_texture_rect(_won_tex, _cover_rect(), false)


## Where OURS NOW stands (local), on the target's top, clear of the top bar.
func ours_now_spot() -> Vector2:
	if _city_ready and city != null and city.iso != null:
		var top := city.project(_target_top()) * (size / Vector2(city.size).max(Vector2.ONE))
		return Vector2(top.x, maxf(top.y, size.y * OURS_NOW_MIN_Y))
	var cover := _cover_rect()
	var a := BackdropCatalog.anchor(place) if not place.is_empty() else BackdropCatalog.ANCHOR_FALLBACK
	var p := cover.position + cover.size * a
	p.y = maxf(p.y, size.y * OURS_NOW_MIN_Y)
	return p


func _draw_ink() -> void:
	# The pencil writes once the lights have turned (the last part of the won motion).
	var show := clampf(won * 2.0 - 1.0, 0.0, 1.0)
	if show <= 0.0 or place.is_empty():
		return
	var k := size.y / DESIGN_HEIGHT
	var fs := maxi(1, roundi(OURS_NOW_PX * k))
	var word := tr("OURS NOW")
	var font := Palette.marker()
	var w := font.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var at := ours_now_spot()
	_ink.draw_set_transform(at, OURS_NOW_TILT, Vector2.ONE)
	var origin := Vector2(-w * 0.5, fs * 0.35)
	var ink := Color(Palette.INK, show)
	_ink.draw_string_outline(font, origin, word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, maxi(1, roundi(OURS_NOW_OUTLINE * k)), ink)
	_ink.draw_string(font, origin, word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(Palette.RESIST_GOLD, show))
	_ink.draw_set_transform(Vector2.ZERO)



# --- D17 on the city (ART-8 8w) -----------------------------------------------------------------

## True when this backdrop shows the city's close-up (else the stills).
func on_city() -> bool:
	return _city_ready


## Builds (or re-aims) the city close-up for `place` when the quality tier takes it.
func _use_city() -> void:
	var cfg := CityView3D.CONFIG
	if not BackdropCatalog.city_mode(cfg, cfg.tier_for(Settings.city_quality), CityView3D.can_render()):
		_drop_city()
		return
	var corp: StringName = place.get("corp", BackdropCatalog.DEFAULT_CORP)
	var corp_data := RunManager.lookup().get_content(corp) as CorporationData
	var lots := CityLayout.site_points(corp_data) if corp_data != null and corp_data.city_grid != null else {}
	var sz := size if size.x >= 2.0 and size.y >= 2.0 else Vector2(1280, 720)
	shot = BackdropCatalog.city_shot(cfg, place, lots, sz)
	if city != null and (shot["stage"] != &"") != city.compounds.has(CityView3D.CELL):
		_drop_city()
	if city == null:
		city = CityView3D.new()
		city.name = "BackdropCity"
		city.set_iso(shot["camera"])
		if shot["stage"] != &"":
			city.stage_compound(shot["stage"])
		city.model_ready.connect(_on_city_ready)
		add_child(city)
		city.set_view_size(render_px(sz))
	_light_city()
	city.set_site_landmark(StringName(shot.get("landmark", &"")), shot["lot"])
	_frame_city()
	if city.model != null and city.chunks_built() > 0:
		_on_city_ready()


func _frame_city() -> void:
	if city == null or shot.is_empty():
		return
	var cam: CityIsoCamera = (shot["camera"] as CityIsoCamera).copy()
	cam.viewport = Vector2(city.size)
	city.set_iso(cam)
	var t := city.project(shot.get("centre", cam.target))
	_mat.set_shader_parameter(&"keep_at", Vector2(t.x / maxf(1.0, float(city.size.x)), t.y / maxf(1.0, float(city.size.y))))
	_mat.set_shader_parameter(&"keep_radius", CityView3D.CONFIG.backdrop_keep_radius)


func _on_city_ready() -> void:
	if city == null:
		return
	if String(shot.get("focus", "")) == "site" and city.model != null:
		# The Site's own building: the nearest lot with a roof (the layout's point may be a street).
		var lot := _building_lot(city.model, shot["lot"])
		shot["lot"] = lot
		var cfg := CityView3D.CONFIG
		(shot["camera"] as CityIsoCamera).target = city.lot_world(lot, cfg.backdrop_site_lift)
		_frame_city()
	_city_ready = true
	_light_city()
	_tex = city.get_texture()
	_won_tex = null
	_mat.set_shader_parameter(&"use_mask", false)
	_mat.set_shader_parameter(&"won_mask", null)
	_mat.set_shader_parameter(&"district_dim", DISTRICT_DIM)
	_mat.set_shader_parameter(&"aspect", float(city.size.x) / maxf(1.0, float(city.size.y)))
	_build_won_lights()
	_sync_won()
	_pools_sig = ""
	_still.queue_redraw()


## S-ARENA: the close-up's render size for a backdrop of `sz` px: at most
## CityConfig.backdrop_render_height px tall (the backdrop sits softened behind the wheels, so a
## 1080p view renders it at that height and draws it scaled: the wider lit close-up keeps the 8 ms
## city budget), never more than the view.
static func render_px(sz: Vector2) -> Vector2i:
	var cap := float(CityView3D.CONFIG.backdrop_render_height)
	var k := minf(1.0, cap / maxf(1.0, sz.y)) if cap > 0.0 else 1.0
	return Vector2i(maxi(2, roundi(sz.x * k)), maxi(2, roundi(sz.y * k)))


## S-ARENA (CMB-01, MOTION-07): the close-up keeps the concept's lit night (CityConfig
## backdrop_*) instead of the Grid's dark grade, so the still -> city hand-over no longer drops
## the scene to near black; the canvas grade (`city_grade`) applies once the city shows (the
## stills are the concept already).
func _light_city() -> void:
	var cfg := CityView3D.CONFIG
	city.set_night_share(0.0, BackdropCatalog.city_look(cfg, String(shot.get("focus", "hq"))))
	_mat.set_shader_parameter(&"city_exposure", cfg.backdrop_exposure)
	_mat.set_shader_parameter(&"city_tint", cfg.backdrop_tint)
	_mat.set_shader_parameter(&"city_saturation", cfg.backdrop_saturation)
	_mat.set_shader_parameter(&"city_grade", _city_ready)


## The shader's city grade (`graded`) on `c`, the value the shader samples, for the tests and the contrast
## checks: value V -> 1 - (1 - V)^exposure, hue kept, times the tint, then the saturation.
static func graded(cfg: CityConfig, c: Color) -> Color:
	var v := maxf(c.r, maxf(c.g, c.b))
	var k := (1.0 - pow(1.0 - clampf(v, 0.0, 1.0), cfg.backdrop_exposure)) / maxf(v, 0.0001)
	var t := cfg.backdrop_tint
	var g := Vector3(clampf(c.r * k * t.r, 0.0, 1.0), clampf(c.g * k * t.g, 0.0, 1.0), clampf(c.b * k * t.b, 0.0, 1.0))
	var grey := g.dot(Vector3(0.2126, 0.7152, 0.0722))
	var o := Vector3(grey, grey, grey).lerp(g, cfg.backdrop_saturation)
	return Color(o.x, o.y, o.z, c.a)


## 5d's fight-won lights on the run's Site (hidden until won).
func _build_won_lights() -> void:
	if _won_lights != null:
		_won_lights.queue_free()
		_won_lights = null
	var site: StringName = shot.get("won_site", &"")
	if site == &"" or city.model == null:
		return
	_won_lights = SiteWonLights.new()
	_won_lights.build(city.model, {site: shot["lot"]})
	city.add_to_layer(&"fx", _won_lights)
	_won_lights.visible = won > 0.0


func _drop_city() -> void:
	if city != null:
		city.queue_free()
	city = null
	shot = {}
	_won_lights = null
	_city_ready = false
	_mat.set_shader_parameter(&"city_grade", false)


## The target's top (world): a fitted landmark's own top, the Site building's roof, or the
## HQ / canyon target raised.
func _target_top() -> Vector3:
	var cam: CityIsoCamera = shot["camera"]
	if shot.has("top"):
		return shot["top"]
	if String(shot.get("focus", "")) == "site":
		var lot: Vector2 = shot["lot"]
		return city.lot_world(lot, city.top_at(Vector2i(lot.floor())))
	return cam.target + Vector3(0.0, CityView3D.CONFIG.backdrop_hq_lift, 0.0)


## The lot centre of the building nearest lot point `p` (within SITE_SEARCH lots; nearest first,
## ties by y then x), else `p` itself.
static func _building_lot(model: CityModel, p: Vector2) -> Vector2:
	var at := Vector2i(p.floor())
	var best := Vector2i(-99999, -99999)
	var best_d := INF
	for dy in range(-SITE_SEARCH, SITE_SEARCH + 1):
		for dx in range(-SITE_SEARCH, SITE_SEARCH + 1):
			var l := at + Vector2i(dx, dy)
			if model.top_at(l) <= 0.0:
				continue
			var d := float(dx * dx + dy * dy)
			if d < best_d:
				best_d = d
				best = l
	return Vector2(best) + Vector2(0.5, 0.5) if best_d < INF else p

