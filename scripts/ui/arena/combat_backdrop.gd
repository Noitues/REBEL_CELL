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


func _init() -> void:
	name = "CombatBackdrop"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	_mat.set_shader_parameter(&"lime", Palette.CELL_ACID)
	_mat.set_shader_parameter(&"pink", Palette.CELL_PINK)
	_mat.set_shader_parameter(&"district_dim", DISTRICT_DIM)
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
	# A won look that is another still crossfades to it; the district does not dim twice.
	_mat.set_shader_parameter(&"district_dim", 1.0 if _won_tex != null else DISTRICT_DIM)
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
		show_place(BackdropCatalog.place_for(RunManager.campaign, enemies))
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
