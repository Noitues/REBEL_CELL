class_name GreasePencilWord
extends Node2D
## One or two short scrawled words in grease pencil (ART-1 1B; round 3 kit "HIT IT": "at most
## 1-2 short scrawled words a screen"; ART_BIBLE v2 §1.2: never body text, never a claim that
## misstates the game state). The marker face with `marker_stroke.gdshader`'s wax grain
## (mode 2) over a dark under-shadow. Writes on letter by letter (`pencil_write_on`) and wipes
## off letter by letter from the first (`pencil_wipe`): trimming, never alpha. In
## GreasePencilMark.GROUP, so PencilLint keeps UI off it. A view only.

signal written

const SHADER := preload("res://shaders/kit/marker_stroke.gdshader")
const WRITE := &"pencil_write_on"
const WIPE := &"pencil_wipe"
## Letters per second of writing are the write-on speed (px/s) over this many px a letter.
const LETTER_PX := 28.0
## The under-shadow's alpha (round 3 kit composite: 0.42).
const SHADOW_ALPHA := 0.42

@export var text: String = "HIT IT":
	set(v):
		text = v
		_redraw()
@export var ink: GreasePencilMark.Ink = GreasePencilMark.Ink.THREAT:
	set(v):
		ink = v
		_sync()
@export var text_step: int = UiTheme.HEADING:
	set(v):
		text_step = v
		_redraw()

## Letters shown from (wiped) and up to (written).
var shown_from: float = 0.0:
	set(v):
		shown_from = v
		_redraw()
var shown_to: float = 1.0e6:
	set(v):
		shown_to = v
		_redraw()

var _wax: Node2D = null
var _shadow: Node2D = null
var _mat: ShaderMaterial = null
var _tween: Tween = null
var _tween_kind: StringName = &""


func _init() -> void:
	add_to_group(GreasePencilMark.GROUP)
	_shadow = Node2D.new()
	_shadow.position = GreasePencilMark.SHADOW_OFFSET
	_shadow.draw.connect(_draw_text.bind(true))
	add_child(_shadow)
	_wax = Node2D.new()
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	_mat.set_shader_parameter(&"mode", 2)
	_wax.material = _mat
	_wax.draw.connect(_draw_text.bind(false))
	add_child(_wax)
	_sync()


func _ready() -> void:
	MotionSkip.register_passive(self)  # ANIM-R6 D7: a word writing on ends with any press that ends a motion


func _sync() -> void:
	if _mat != null:
		_mat.set_shader_parameter(&"ink", GreasePencilMark.ink_color(ink))


func _redraw() -> void:
	if _wax != null:
		_wax.queue_redraw()
		_shadow.queue_redraw()


## The word's rect in global coordinates (with its shadow): no UI may cover it.
func global_rect() -> Rect2:
	var font := Palette.pencil()
	var px := UiTheme.font_px(text_step)
	var sz := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, px)
	var r := Rect2(Vector2(0, -font.get_ascent(px)), sz).grow(2.0)
	r.end += GreasePencilMark.SHADOW_OFFSET
	return get_global_transform() * r


func _draw_text(shadow: bool) -> void:
	var node := _shadow if shadow else _wax
	var font := Palette.pencil()
	var px := UiTheme.font_px(text_step)
	var col := Palette.PENCIL_SHADOW if shadow else Palette.NO_TINT
	if shadow:
		col.a = SHADOW_ALPHA
	var x := 0.0
	for i in text.length():
		var ch := text[i]
		var adv := font.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
		if float(i) >= shown_from and float(i) < shown_to:
			node.draw_string(font, Vector2(x, 0), ch, HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)
		x += adv


func motion_running() -> bool:
	return _tween != null and _tween.is_valid() and _tween.is_running()


func complete_motion() -> void:
	if not motion_running():
		return
	_tween.kill()
	_tween = null
	_end(_tween_kind)


func _end(kind: StringName) -> void:
	_tween_kind = &""
	if kind == WRITE:
		shown_to = float(text.length())
		written.emit()
	elif kind == WIPE:
		shown_from = float(text.length())


## Writes the word on letter by letter. Returns its seconds (0: whole at once).
func write_on() -> float:
	if motion_running():
		complete_motion()
	shown_from = 0.0
	if not Motion.live(WRITE):
		_end(WRITE)
		return 0.0
	var e := Motion.entry(WRITE)
	var n := float(text.length())
	var d := minf(n * LETTER_PX / maxf(e.amplitude, 1.0), e.duration) / maxf(Motion.speed, Motion.SPEED_MIN)
	shown_to = 0.0
	_tween_kind = WRITE
	_tween = create_tween()
	_tween.tween_property(self, "shown_to", n, d).set_ease(e.ease).set_trans(e.trans)
	_tween.tween_callback(func() -> void:
		_tween = null
		_end(WRITE))
	return d


## Wipes the word off from its first letter. Returns its seconds (0: gone at once).
func wipe() -> float:
	if motion_running():
		complete_motion()
	if not Motion.live(WIPE):
		_end(WIPE)
		return 0.0
	var e := Motion.entry(WIPE)
	var d := Motion.seconds(WIPE)
	_tween_kind = WIPE
	_tween = create_tween()
	_tween.tween_property(self, "shown_from", float(text.length()), d).set_ease(e.ease).set_trans(e.trans)
	_tween.tween_callback(func() -> void:
		_tween = null
		_end(WIPE))
	return d
