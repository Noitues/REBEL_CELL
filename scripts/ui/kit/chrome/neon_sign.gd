class_name NeonSign
extends Control
## ART-10 4C: the REBEL_CELL neon tube sign on its circuit board (ART_BIBLE v2 §4.13 title
## option A; round 33 `title_screen.jpg` / `.gif`). The art is the concept's own: round 33
## `title.py` `board()` + `neon()` baked by `tools/art/bake_menus_r33.py` into one image per
## distinct lit state of its 48-frame loop (`assets/ui/menus/sign/sign_<n>.png`) and that
## state's glow on black (`glow_<n>.png`, an additive layer behind the board so the pink light
## falls on the city). Idle (`title_sign_flicker`: one loop): the underscore blinks as a
## cursor, one E stutters, the sign drops to "CELL" for two frames, as `lit_state()` draws it.
## Under reduce effects, headless or with the entry off it holds state 0 (fully lit). The
## sign is diegetic signage (the brand mark): never translated. View only.

const MOTION := &"title_sign_flicker"
const DIR := "res://assets/ui/menus/sign/"
## The concept board space (1920 wide) to the game's 1280: two thirds.
const BOARD_TO_GAME := 2.0 / 3.0

static var _meta: Dictionary = {}

var _clock: float = 0.0
var _frame: int = -1
var _signs: Array[Texture2D] = []
var _glows: Array[Texture2D] = []
var _glow: Control = null


## The baked sign's metadata (frame -> state, the crop boxes), read once.
static func meta() -> Dictionary:
	if _meta.is_empty():
		var f := FileAccess.open(DIR + "meta.json", FileAccess.READ)
		if f != null:
			_meta = JSON.parse_string(f.get_as_text())
	return _meta


## The sign's size in the game (px at 1280x720; a world object: it never scales with the text).
static func board_size() -> Vector2:
	var b: Array = meta().get("sign_box", [0, 0, 990, 328])
	return Vector2(float(b[2]) - float(b[0]), float(b[3]) - float(b[1])) * BOARD_TO_GAME


func _init() -> void:
	name = "NeonSign"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	custom_minimum_size = board_size()
	var n: int = (meta().get("states", []) as Array).size()
	for i in n:
		_signs.append(load(DIR + "sign_%d.png" % i) as Texture2D)
		_glows.append(load(DIR + "glow_%d.png" % i) as Texture2D)
	# The glow layer: additive, behind the board (it spills past the board's edges).
	_glow = Control.new()
	_glow.name = "Glow"
	_glow.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_glow.show_behind_parent = true
	var add := CanvasItemMaterial.new()
	add.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_glow.material = add
	_glow.draw.connect(_draw_glow)
	add_child(_glow)


func _process(delta: float) -> void:
	if not Motion.live(MOTION):
		if _frame != -1:
			_frame = -1
			_redraw()
		return
	var loop := maxf(0.1, Motion.seconds(MOTION))
	var frames: Array = meta().get("frames", [0])
	_clock = fmod(_clock + delta, loop)
	var f := int(_clock / loop * frames.size())
	if f != _frame:
		_frame = f
		_redraw()


func _redraw() -> void:
	queue_redraw()
	_glow.queue_redraw()


## The loop frame shown now (-1: held fully lit).
func frame() -> int:
	return _frame


## The lit state drawn at loop frame `f` (-1 = state 0, fully lit).
static func state_at(f: int) -> int:
	var frames: Array = meta().get("frames", [0])
	return 0 if f < 0 or frames.is_empty() else int(frames[f % frames.size()])


func _draw() -> void:
	var s := state_at(_frame)
	if s < _signs.size() and _signs[s] != null:
		draw_texture_rect(_signs[s], Rect2(Vector2.ZERO, board_size()), false)


func _draw_glow() -> void:
	var s := state_at(_frame)
	if s >= _glows.size() or _glows[s] == null:
		return
	var sb: Array = meta().get("sign_box", [0, 0, 0, 0])
	var gb: Array = meta().get("glow_box", [0, 0, 0, 0])
	var at := Vector2(float(gb[0]) - float(sb[0]), float(gb[1]) - float(sb[1])) * BOARD_TO_GAME
	var sz := Vector2(float(gb[2]) - float(gb[0]), float(gb[3]) - float(gb[1])) * BOARD_TO_GAME
	_glow.draw_texture_rect(_glows[s], Rect2(at, sz), false)
