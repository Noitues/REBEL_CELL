class_name GreasePencilWord
extends Node2D
## One or two short scrawled words in grease pencil (ART-1 1B; round 3 kit "HIT IT": "at most
## 1-2 short scrawled words a screen"; ART_BIBLE v2 §1.2: never body text, never a claim that
## misstates the game state). LOOK-TOOLBOX 12 (AUDIT: "the TARGET word looks like neon marker"):
## the letters are RC Wax (RcWaxFont, the pencil's own face) drawn as real wax strokes on the
## one wax engine, a GreasePencilMark with the word's own width (`RcPencilLook.word_width_em` of
## the font px) and a blunt word pressure, over the engine's crisp under-shadow: chunky wax with
## a cast shadow, no gradient, no glow. Each word gets a seeded hand (its text's hash): letters
## turn, drop and size a little. It is the one word path: PencilSet.word, PencilWords, PencilNote
## and every view's TARGET make one of these. A character the face lacks is drawn in the
## TrueType twin (Palette.pencil(), same advances) with the wax grain (mode 2).
## Writes on letter by letter over `pencil_write_on`'s duration (stroke by stroke in writing
## order) and wipes off letter by letter from the first over `pencil_wipe`'s: trimming, never
## alpha. B1b (D25): with `auto_write` (the default) it writes itself on the first time it shows,
## and again each time it shows after being hidden; an owner that drives `shown_to` turns it
## off. In GreasePencilMark.GROUP, so PencilLint keeps UI off it. A view only.

signal written
signal wiped

const SHADER := preload("res://shaders/kit/marker_stroke.gdshader")
const WRITE := &"pencil_write_on"
const WIPE := &"pencil_wipe"

## M14 perf slice: the setters below do nothing when the value (and, for the step, its font
## px at the current text size) is unchanged: a pool owner lays every word again each frame.
@export var text: String = "HIT IT":
	set(v):
		if v == text:
			return
		text = v
		_rebuild()
@export var ink: GreasePencilMark.Ink = GreasePencilMark.Ink.THREAT:
	set(v):
		if v == ink:
			return
		ink = v
		_sync()
@export var text_step: int = UiTheme.HEADING:
	set(v):
		if v == text_step and _drawn_px == UiTheme.font_px(v):
			return
		text_step = v
		_rebuild()
## Writes itself on when it first shows (and each time it shows again after being hidden).
@export var auto_write: bool = true:
	set(v):
		auto_write = v
		_arm()

## Letters shown from (wiped) and up to (written).
var shown_from: float = 0.0:
	set(v):
		if v == shown_from:
			return
		shown_from = v
		_show()
var shown_to: float = 1.0e6:
	set(v):
		if v == shown_to:
			return
		shown_to = v
		_show()
## The font px the word was last laid at (text_step's guard).
var _drawn_px: int = -1

var _mark: GreasePencilMark = null
## Characters RC Wax lacks, in the TrueType twin: the wax grain over its shadow copy.
var _fallback: Node2D = null
var _fallback_shadow: Node2D = null
var _mat: ShaderMaterial = null
## The layout: each letter's share of the stroke length [start, end) and the missing letters.
var _letter_from := PackedFloat32Array()
var _letter_to := PackedFloat32Array()
var _missing: Array[Dictionary] = []
var _tween: Tween = null
var _tween_kind: StringName = &""
var _pending: bool = true


func _init() -> void:
	add_to_group(GreasePencilMark.GROUP)
	_mark = GreasePencilMark.new()
	_mark.name = "Wax"
	_mark.auto_write = false
	_mark.highlight = true
	_mark.dropout_gap = GreasePencilMark.WORD_DROPOUT_GAP
	# the word's own mark is part of the word: PencilLint reads the word
	_mark.remove_from_group(GreasePencilMark.GROUP)
	add_child(_mark)
	_fallback_shadow = Node2D.new()
	_fallback_shadow.position = GreasePencilMark.SHADOW_OFFSET
	_fallback_shadow.draw.connect(_draw_fallback.bind(true))
	add_child(_fallback_shadow)
	_fallback = Node2D.new()
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	_mat.set_shader_parameter(&"mode", 2)
	_mat.set_shader_parameter(&"alpha_max", GreasePencilMark.WAX_ALPHA)
	GreasePencilMark.set_dropouts(_mat, GreasePencilMark.WORD_DROPOUT_GAP)
	_fallback.material = _mat
	_fallback.draw.connect(_draw_fallback.bind(false))
	add_child(_fallback)
	_rebuild()


func _ready() -> void:
	MotionSkip.register_passive(self)  # ANIM-R6 D7: a word writing on ends with any press that ends a motion
	_arm()


func _notification(what: int) -> void:
	if what == NOTIFICATION_VISIBILITY_CHANGED and not is_visible_in_tree():
		_arm()  # D25: shown again, it writes on again


## The word's hand seed (its text: the same word always has the same hand).
func hand_seed() -> int:
	return absi(text.hash())


func _sync() -> void:
	if _mark == null:
		return
	_mark.ink = ink
	_mark.seed = int(GreasePencilMark.shader_seed(hand_seed()))
	_mat.set_shader_parameter(&"ink", GreasePencilMark.ink_color(ink))
	_mat.set_shader_parameter(&"seed", GreasePencilMark.shader_seed(hand_seed()))
	_mat.set_shader_parameter(&"word_cap_px", Palette.pencil().get_ascent(font_px()) * GreasePencilMark.WORD_CAP_SHARE)
	var k := absf(get_global_transform().get_scale().x) if is_inside_tree() else 1.0
	_mat.set_shader_parameter(&"dropout_scale", GreasePencilMark.dropout_scale(maxf(k, 0.0001)))


## Lays the letters again (the text or its size changed).
func _rebuild() -> void:
	if _mark == null:
		return
	var px := font_px()
	_drawn_px = px
	var look := GreasePencilMark.LOOK
	var lay := RcWaxFont.layout(text, float(px), hand_seed(), look)
	_mark.clear()
	_mark.local_width = float(px) * look.word_width_em
	var strokes: Array[PackedVector2Array] = lay["strokes"]
	var letter: PackedInt32Array = lay["letter"]
	var lens := PackedFloat32Array()
	lens.resize(text.length())
	lens.fill(0.0)
	for i in strokes.size():
		_mark.add_stroke(strokes[i])
		lens[letter[i]] += PencilShapes.length_of(PencilShapes.resample(strokes[i], GreasePencilMark.STEP_PX))
	var total := 0.0
	for l in lens:
		total += l
	_letter_from.resize(text.length())
	_letter_to.resize(text.length())
	var acc := 0.0
	for i in text.length():
		_letter_from[i] = acc / total if total > 0.0 else 0.0
		acc += lens[i]
		_letter_to[i] = acc / total if total > 0.0 else 0.0
	_missing = lay["missing"]
	_sync()
	_show()


## The share of the word's stroke length written at letter position `t` (letters, fractional).
func _share_at(t: float) -> float:
	var n := text.length()
	if n == 0:
		return 0.0
	if t <= 0.0:
		return 0.0
	if t >= float(n):
		return 1.0
	var i := floori(t)
	return lerpf(_letter_from[i], _letter_to[i], t - float(i))


func _show() -> void:
	if _mark == null:
		return
	_mark.progress = _share_at(shown_to)
	_mark.wiped_share = _share_at(shown_from)
	if _fallback != null:
		_fallback.queue_redraw()
		_fallback_shadow.queue_redraw()


## The word's font px.
func font_px() -> int:
	return UiTheme.font_px(text_step)


## The word's rect in global coordinates (with its shadow): no UI may cover it. The face's
## line box over the word's advance, merged with its strokes' own rect (a letter's hand can
## lean past the box).
func global_rect() -> Rect2:
	var font := Palette.pencil()
	var px := font_px()
	var sz := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, px)
	var r := Rect2(Vector2(0, -font.get_ascent(px)), sz).grow(2.0)
	r.end += GreasePencilMark.SHADOW_OFFSET
	var out := get_global_transform() * r
	if _mark != null and _mark.total_length() > 0.0:
		out = out.merge(_mark.global_rect())
	return out


## The wax mark that draws the letters (tests: the one wax engine).
func wax_mark() -> GreasePencilMark:
	return _mark


## The fallback characters' shadow copy and wax node (tests: offset and ink).
func shadow_node() -> Node2D:
	return _fallback_shadow


func wax_node() -> Node2D:
	return _fallback


func _draw_fallback(shadow: bool) -> void:
	if _missing.is_empty():
		return
	var node := _fallback_shadow if shadow else _fallback
	var font := Palette.pencil()
	var px := font_px()
	var col := Palette.PENCIL_SHADOW if shadow else Palette.NO_TINT
	for m: Dictionary in _missing:
		var i := int(m["index"])
		if float(i) >= shown_from and float(i) < shown_to:
			HighContrast.draw_text(node, font, Vector2(float(m["x"]), 0), text[i], HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)


## D25: an auto word waits to show, then writes itself on.
func _arm() -> void:
	if not auto_write:
		_pending = false
		set_process(false)
		return
	_pending = true
	if Motion.live(WRITE) and not motion_running():
		shown_to = 0.0
	set_process(true)


func _process(_delta: float) -> void:
	if not _pending or not auto_write:
		set_process(false)
		return
	if text != "" and is_visible_in_tree():
		_pending = false
		set_process(false)
		write_on()


func motion_running() -> bool:
	return _tween != null and _tween.is_valid() and _tween.is_running()


func complete_motion() -> void:
	if _pending and auto_write and text != "":
		_pending = false
		set_process(false)
		shown_to = float(text.length())
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
		wiped.emit()


## Writes the word on letter by letter over `pencil_write_on`'s duration. Returns its seconds
## (0: whole at once).
func write_on() -> float:
	if motion_running():
		complete_motion()
	_pending = false
	shown_from = 0.0
	if not Motion.live(WRITE):
		_end(WRITE)
		return 0.0
	var e := Motion.entry(WRITE)
	var n := float(text.length())
	var d := Motion.seconds(WRITE)
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
	_pending = false
	set_process(false)
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
