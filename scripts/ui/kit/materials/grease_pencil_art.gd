class_name GreasePencilArt
extends Node2D
## B1b (integration review D3 / D25): a piece of the concepts' own baked grease-pencil art (the
## title's plan numbers and its motto, round 33 `title.py`, baked by tools/art/bake_menus_r33.py)
## drawn through the one wax material, `marker_stroke.gdshader` mode 3: the art is already wax
## from the concepts' generator, so the material only writes it on, left to right over
## `pencil_write_on`'s duration (a ragged wax front), and wipes it the same way over
## `pencil_wipe`'s; never alpha, never whole at once. Auto writes on when it first shows (and
## again when shown after being hidden). Reduce effects / headless: whole at once. In
## GreasePencilMark.GROUP (PencilLint). A view only.

signal written

const WRITE := GreasePencilMark.WRITE
const WIPE := GreasePencilMark.WIPE

var texture: Texture2D = null:
	set(v):
		texture = v
		queue_redraw()
## The art's drawn size (local px).
var draw_size: Vector2 = Vector2.ZERO:
	set(v):
		draw_size = v
		queue_redraw()
## Written share 0..1, left to right.
var progress: float = 1.0:
	set(v):
		progress = clampf(v, 0.0, 1.0)
		if _mat != null:
			_mat.set_shader_parameter(&"reveal", progress)

var _mat: ShaderMaterial = null
var _tween: Tween = null
var _tween_kind: StringName = &""
var _pending: bool = true


func _init(p_texture: Texture2D = null, p_size: Vector2 = Vector2.ZERO) -> void:
	add_to_group(GreasePencilMark.GROUP)
	_mat = ShaderMaterial.new()
	_mat.shader = GreasePencilMark.SHADER
	_mat.set_shader_parameter(&"mode", 3)
	_mat.set_shader_parameter(&"reveal", 1.0)
	material = _mat
	texture = p_texture
	draw_size = p_size if p_size != Vector2.ZERO else (p_texture.get_size() if p_texture != null else Vector2.ZERO)


func _ready() -> void:
	MotionSkip.register_passive(self)
	_arm()


func _notification(what: int) -> void:
	if what == NOTIFICATION_VISIBILITY_CHANGED and not is_visible_in_tree():
		_arm()


func _draw() -> void:
	if texture != null:
		draw_texture_rect(texture, Rect2(Vector2.ZERO, draw_size), false)


## The art's rect (global): no UI may cover it.
func global_rect() -> Rect2:
	return get_global_transform() * Rect2(Vector2.ZERO, draw_size)


func _arm() -> void:
	_pending = true
	if Motion.live(WRITE) and not motion_running():
		progress = 0.0
	set_process(true)


func _process(_delta: float) -> void:
	if not _pending:
		set_process(false)
		return
	if texture != null and is_visible_in_tree():
		_pending = false
		set_process(false)
		write_on()


func motion_running() -> bool:
	return _tween != null and _tween.is_valid() and _tween.is_running()


func complete_motion() -> void:
	if _pending and texture != null:
		_pending = false
		set_process(false)
		progress = 1.0
	if not motion_running():
		return
	_tween.kill()
	_tween = null
	_end(_tween_kind)


func _end(kind: StringName) -> void:
	_tween_kind = &""
	progress = 1.0 if kind == WRITE else 0.0
	if kind == WRITE:
		written.emit()


## Writes the art on, left to right. Returns its seconds (0: whole at once).
func write_on() -> float:
	if motion_running():
		complete_motion()
	_pending = false
	if not Motion.live(WRITE):
		_end(WRITE)
		return 0.0
	var e := Motion.entry(WRITE)
	var d := Motion.seconds(WRITE)
	progress = 0.0
	_tween_kind = WRITE
	_tween = create_tween()
	_tween.tween_property(self, "progress", 1.0, d).set_ease(e.ease).set_trans(e.trans)
	_tween.tween_callback(func() -> void:
		_tween = null
		_end(WRITE))
	return d


## Wipes the art off (the written front runs back). Returns its seconds (0: gone at once).
func wipe() -> float:
	if motion_running():
		complete_motion()
	_pending = false
	set_process(false)
	if not Motion.live(WIPE):
		_end(WIPE)
		return 0.0
	var e := Motion.entry(WIPE)
	var d := Motion.seconds(WIPE)
	_tween_kind = WIPE
	_tween = create_tween()
	_tween.tween_property(self, "progress", 0.0, d).set_ease(e.ease).set_trans(e.trans)
	_tween.tween_callback(func() -> void:
		_tween = null
		_end(WIPE))
	return d
