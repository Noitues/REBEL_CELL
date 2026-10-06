class_name PencilWords
extends Control
## ART-10 4C: a short grease-pencil phrase written on the screen (ART_BIBLE v2 §1.2; round 33
## `title_screen.jpg`). With `art` it shows the concept's own pencil (round 33 title.py
## `slogan()`: NEVER SLEEP + the crown, baked by tools/art/bake_menus_r33.py into
## `assets/ui/menus/pencil/motto.png`). Without art (words the concept never drew: the pause
## menu's designer-ruled notes) it writes the words as wax, tilted. Short words only, true to the
## game or ruled by the designer; never a live number. View only.
##
## B1b (integration review D3 / D25, one wax material): every part is the kit's pencil, never a
## vector draw: the words are a GreasePencilWord, the crown a GreasePencilMark, the baked art a
## GreasePencilArt; each writes itself on when it shows (again when shown after being hidden)
## and never fades. This control only lays them out (its size is the words').

const STEP := UiTheme.HEADING
const MOTTO_ART := "res://assets/ui/menus/pencil/motto.png"
## The crown doodle's size (px) and its gap after the words (drawn words only).
const CROWN := Vector2(34, 22)
const CROWN_GAP := 10.0

var words: String = "":
	set(v):
		words = v
		_rebuild()
var tilt: float = 0.0:
	set(v):
		tilt = v
		_rebuild()
## The grease ink (PENCIL_PLAN yellow, or PENCIL_THREAT red) and the type step (parity PAUSE: a note under a sticker).
var color: Color = Palette.PENCIL_PLAN:
	set(v):
		color = v
		_rebuild()
var step: int = STEP:
	set(v):
		step = v
		_rebuild()
var crown := false:
	set(v):
		crown = v
		_rebuild()
var _tex: Texture2D = null
var _holder: Node2D = null
var _word: GreasePencilWord = null
var _crown: GreasePencilMark = null
var _art: GreasePencilArt = null


## Where the motto sits on the title, relative to the sign's top left (the concept's own
## placement: title.py `slogan()` against `BOARD`, in game px).
static func motto_at() -> Vector2:
	var m: Array = PencilPlan.meta().get("motto_box", [0, 0, 0, 0])
	var sb: Array = NeonSign.meta().get("sign_box", [0, 0, 0, 0])
	return Vector2(float(m[0]) - float(sb[0]), float(m[1]) - float(sb[1])) * PencilPlan.BOARD_TO_GAME


func _init(p_words: String = "", p_tilt: float = 0.0, p_crown: bool = false, p_art: String = "") -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	if p_art != "" and ResourceLoader.exists(p_art):
		_tex = load(p_art) as Texture2D
	_holder = Node2D.new()
	_holder.name = "Wax"
	add_child(_holder)
	words = p_words
	tilt = p_tilt
	crown = p_crown
	resized.connect(_place)


## The ink of `color` (the kit's two inks).
func ink() -> GreasePencilMark.Ink:
	return GreasePencilMark.Ink.THREAT if color == Palette.PENCIL_THREAT else GreasePencilMark.Ink.PLAN


## The pencil nodes this note shows (tests: each is the kit's material).
func pencil_nodes() -> Array[Node2D]:
	var out: Array[Node2D] = []
	for n in [_art, _word, _crown]:
		if n != null:
			out.append(n)
	return out


func _get_minimum_size() -> Vector2:
	if _tex != null:
		return _tex.get_size() * PencilPlan.BOARD_TO_GAME
	var px := Chrome.px(step)
	var w := Chrome.pencil_font().get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	return Vector2(ceilf(w + (CROWN.x + CROWN_GAP if crown else 0.0)), ceilf(px * 1.5))


func _rebuild() -> void:
	if _holder == null:
		return
	if _tex != null:
		if _art == null:
			_art = GreasePencilArt.new(_tex, _tex.get_size() * PencilPlan.BOARD_TO_GAME)
			_art.name = "Art"
			_holder.add_child(_art)
	else:
		if _word == null:
			_word = GreasePencilWord.new()
			_word.name = "Words"
			_holder.add_child(_word)
		_word.text = words
		_word.ink = ink()
		_word.text_step = step
		if crown and _crown == null:
			_crown = GreasePencilMark.new()
			_crown.name = "Crown"
			_holder.add_child(_crown)
		elif not crown and _crown != null:
			_crown.queue_free()
			_crown = null
		if _crown != null:
			_crown.ink = ink()
	update_minimum_size()
	_place()


func _place() -> void:
	if _holder == null:
		return
	if _art != null:
		_holder.position = Vector2.ZERO
		_holder.rotation = 0.0
		return
	var px := Chrome.px(step)
	var m := get_minimum_size()
	_holder.position = m * 0.5
	_holder.rotation = deg_to_rad(tilt)
	_word.position = Vector2(-m.x * 0.5, px * 0.4)
	if _crown != null:
		var o := Vector2(m.x * 0.5 - CROWN.x, -CROWN.y * 0.5)
		_crown.clear()
		_crown.add_stroke(PackedVector2Array([o + Vector2(0, CROWN.y), o, o + Vector2(CROWN.x * 0.3, CROWN.y * 0.55),
			o + Vector2(CROWN.x * 0.5, 0), o + Vector2(CROWN.x * 0.7, CROWN.y * 0.55), o + Vector2(CROWN.x, 0), o + Vector2(CROWN.x, CROWN.y),
			o + Vector2(0, CROWN.y)]))
