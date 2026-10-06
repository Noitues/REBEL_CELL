class_name RaidPencilPool
extends Node2D
## ART-6 3A: the raid's grease pencil on 1B's material (GreasePencilMark / GreasePencilWord,
## ART-1 1B): a pool of marks and words its owner asks for each frame by key (`begin`, then
## `stroke` / `word` for every mark it shows, then `end`), so the raid keeps its own timing
## (reading holds in real time, a skip at the end state) while the wax, its shader, its
## under-shadow and PencilLint's group are the kit's. A mark's points are rebuilt only when
## they change (the camera moved). The pool lives on the scene's raid pencil CanvasLayer
## (LAYER: above every UI layer the raid shows, under Fx's jack cover), so no UI ever covers
## the pencil (§1.2); its owner frees it when it leaves (`release`). Points are global (screen)
## px: every raid layer maps its map anchors through one seam (RaidMapAnchor) first.

## The raid pencil's CanvasLayer order: over Dialogue's subtitles (90), under Fx (100).
const LAYER := 95
const LAYER_NAME := "RaidPencilLayer"

var _marks: Dictionary = {}  # key -> GreasePencilMark
var _words: Dictionary = {}  # key -> GreasePencilWord
var _keys: Dictionary = {}  # key -> points hash
var _used: Dictionary = {}


## A pool on the raid pencil layer of `host`'s scene (made once per scene).
static func make(host: Node) -> RaidPencilPool:
	var pool := RaidPencilPool.new()
	var scene := host
	while scene.get_parent() != null and scene.get_parent() != host.get_tree().root:
		scene = scene.get_parent()
	var layer := scene.get_node_or_null(LAYER_NAME) as CanvasLayer
	if layer == null:
		layer = CanvasLayer.new()
		layer.name = LAYER_NAME
		layer.layer = LAYER
		scene.add_child(layer)
	layer.add_child(pool)
	return pool


## Frees the pool (its owner left).
func release() -> void:
	queue_free()


## Starts a frame's requests.
func begin() -> void:
	_used.clear()


## A mark `key` of `strokes` (global px, in writing order), written to `progress` and wiped
## from `wiped` (shares of its length), in `ink`, `width` px, dashed for a what-if.
func stroke(key: String, strokes: Array[PackedVector2Array], ink: GreasePencilMark.Ink, width: float, progress: float = 1.0,
		wiped: float = 0.0, dashed: bool = false, seed: int = 1) -> GreasePencilMark:
	_used[key] = true
	var m: GreasePencilMark = _marks.get(key)
	if m == null:
		m = GreasePencilMark.new()
		m.name = "Mark_%d" % _marks.size()
		add_child(m)
		_marks[key] = m
	m.ink = ink
	m.dashed = dashed
	m.seed = seed
	if not is_equal_approx(m.width, width):
		m.width = width
	var h := 0
	for s in strokes:
		if s.size() > 0:
			h = hash([h, s.size(), Vector2i(s[0]), Vector2i(s[s.size() - 1]), Vector2i(s[s.size() / 2])])
	if int(_keys.get(key, -1)) != h:
		_keys[key] = h
		m.clear()
		for s in strokes:
			if s.size() >= 2:
				m.add_stroke(s)
	m.progress = progress
	m.wiped_share = wiped
	m.visible = progress > wiped
	return m


## A pencil word `key`: `text` centred on `centre` (global px), scaled `k` (the map's zoom),
## turned `tilt` radians, letters shown from `shown_from` to `shown_to` (shares of the word).
func word(key: String, text: String, centre: Vector2, step: int, ink: GreasePencilMark.Ink, k: float = 1.0, shown_to: float = 1.0,
		shown_from: float = 0.0, tilt: float = -0.04) -> GreasePencilWord:
	_used[key] = true
	var w: GreasePencilWord = _words.get(key)
	if w == null:
		w = GreasePencilWord.new()
		w.name = "Word_%d" % _words.size()
		add_child(w)
		_words[key] = w
	if w.text != text:
		w.text = text
	w.ink = ink
	w.text_step = step
	var n := float(text.length())
	w.shown_to = shown_to * n
	w.shown_from = shown_from * n
	w.scale = Vector2.ONE * k
	w.rotation = tilt
	var size := word_size(text, step) * k
	var font := Palette.pencil()
	var px := UiTheme.font_px(step)
	w.position = centre + Vector2(-size.x * 0.5, font.get_ascent(px) * k - size.y * 0.5).rotated(tilt)
	w.visible = shown_to > shown_from
	return w


## The size of word `text` at type step `step` (unscaled).
static func word_size(text: String, step: int) -> Vector2:
	var font := Palette.pencil()
	var px := UiTheme.font_px(step)
	return Vector2(font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x, font.get_height(px))


## Ends a frame: marks and words not asked for are freed.
func end() -> void:
	for key in _marks.keys():
		if not _used.has(key):
			(_marks[key] as Node).queue_free()
			_marks.erase(key)
			_keys.erase(key)
	for key in _words.keys():
		if not _used.has(key):
			(_words[key] as Node).queue_free()
			_words.erase(key)


## Every mark and word showing (tests).
func shown() -> Array[Node2D]:
	var out: Array[Node2D] = []
	for m in _marks.values():
		if (m as Node2D).visible:
			out.append(m)
	for w in _words.values():
		if (w as Node2D).visible:
			out.append(w)
	return out
