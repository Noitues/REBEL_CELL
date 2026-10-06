class_name PencilSet
extends Node2D
## B1b (integration review D3, "one wax material everywhere"): a keyed set of grease-pencil
## marks and words, all on the kit's one wax material (GreasePencilMark / GreasePencilWord),
## that a view lays out in a pass (`begin`, then `stroke` / `circle` / `word` for every mark it
## shows, then `end`), in its parent's local px. A view that draws its map or its card in
## `_draw` lays its pencil here instead of drawing vector lines, so every pencil stroke and
## pencil word in the game is the wax (9 px at 1080p, the under-shadow, the write-on).
##
## A mark laid with `progress` AUTO writes itself on when it first shows (D25) and, once a pass
## no longer lays it, wipes off with the cloth (`pencil_wipe`) and is freed. A mark laid with a
## progress its owner drives (the raid's timed marks, RaidPencilPool) is set to it each pass and
## freed at once when no longer laid (its owner wipes it by its own clock). A mark's points are
## rebuilt only when they change (the camera moved).

## `progress` / `shown_to` for a mark that writes itself on (and wipes itself off).
const AUTO := -1.0
## The host meta key `show_on` keeps its set under.
const META := &"pencil_set"
## `show_on`'s set draws this many z steps over its host's siblings.
const LIFT_Z := 1

var _marks: Dictionary = {}  # key -> GreasePencilMark
var _words: Dictionary = {}  # key -> GreasePencilWord
var _keys: Dictionary = {}  # key -> points hash
var _used: Dictionary = {}


## A set under `host` (its local px).
static func under(host: Node) -> PencilSet:
	var s := PencilSet.new()
	s.name = "Pencil"
	host.add_child(s)
	return s


## For a view that draws in `_draw` (a print, a chip, a feed): `host`'s set (a child "Pencil",
## made on first use) shows one mark `strokes` in `ink` (none when empty); `lift` draws it over the
## host's later siblings (z, which PencilLint reads). Laid after the draw
## (the tree is not changed while drawing); the mark writes on when it first shows.
static func show_on(host: CanvasItem, strokes: Array, ink: GreasePencilMark.Ink, seed: int = 1, lift: bool = false) -> void:
	var s: PencilSet = host.get_meta(META, null) if host.has_meta(META) else null
	if s == null or not is_instance_valid(s):
		if strokes.is_empty():
			return
		s = PencilSet.new()
		s.name = "Pencil"
		# `lift`: over the host's later siblings (a verdict sticker slapped on a print): no UI covers pencil.
		s.z_index = LIFT_Z if lift else 0
		host.set_meta(META, s)
		host.add_child.call_deferred(s)
	var typed: Array[PackedVector2Array] = []
	for st: PackedVector2Array in strokes:
		typed.append(st)
	s._one = {"strokes": typed, "ink": ink, "seed": seed}
	s._lay_one.call_deferred()


## The strokes of a cross over `rect` inset `inset` px (two strokes, the second after the first).
static func cross_strokes(rect: Rect2, inset: float = 0.0) -> Array[PackedVector2Array]:
	var r := rect.grow(-inset)
	return [PackedVector2Array([r.position, r.end]),
		PackedVector2Array([Vector2(r.end.x, r.position.y), Vector2(r.position.x, r.end.y)])] as Array[PackedVector2Array]


var _one: Dictionary = {}


func _lay_one() -> void:
	if not is_inside_tree():
		return
	begin()
	var strokes: Array[PackedVector2Array] = _one.get("strokes", [] as Array[PackedVector2Array])
	if not strokes.is_empty():
		stroke("one", strokes, _one["ink"], AUTO, 0.0, false, int(_one["seed"]))
	end()


## Starts a pass.
func begin() -> void:
	_used.clear()


## A mark `key` of `strokes` (local px, in writing order) in `ink`, dashed for a what-if. With
## `progress` AUTO it writes itself on; else it is written to `progress` and wiped from
## `wiped` (shares of its length) as its owner drives them.
func stroke(key: String, strokes: Array[PackedVector2Array], ink: GreasePencilMark.Ink, progress: float = AUTO,
		wiped: float = 0.0, dashed: bool = false, seed: int = 1) -> GreasePencilMark:
	_used[key] = true
	var m: GreasePencilMark = _marks.get(key)
	var driven := progress >= 0.0
	if m == null:
		m = GreasePencilMark.new()
		m.name = "Mark_%d" % _marks.size()
		m.auto_write = not driven
		add_child(m)
		_marks[key] = m
	m.ink = ink
	m.dashed = dashed
	m.seed = seed
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
	if driven:
		m.progress = progress
		m.wiped_share = wiped
		m.visible = progress > wiped
	return m


## A hand loop `key` round `centre` (radii `radii`): one ellipse with its 20 degree tail.
func circle(key: String, centre: Vector2, radii: Vector2, ink: GreasePencilMark.Ink, seed: int = 1,
		progress: float = AUTO) -> GreasePencilMark:
	return stroke(key, [PencilShapes.hand_circle(centre, radii, seed)], ink, progress, 0.0, false, seed)


## A cross `key` over `rect` (two strokes, the second after the first), inset `inset` px.
func cross(key: String, rect: Rect2, ink: GreasePencilMark.Ink, inset: float = 0.0, seed: int = 1,
		progress: float = AUTO) -> GreasePencilMark:
	return stroke(key, cross_strokes(rect, inset), ink, progress, 0.0, false, seed)


## A pencil word `key`: `text` centred on `centre` (local px), scaled `k` (a map's zoom), turned
## `tilt` radians. With `shown_to` AUTO it writes itself on; else its letters show from
## `shown_from` to `shown_to` (shares of the word) as its owner drives them.
func word(key: String, text: String, centre: Vector2, step: int, ink: GreasePencilMark.Ink, k: float = 1.0,
		shown_to: float = AUTO, shown_from: float = 0.0, tilt: float = -0.04) -> GreasePencilWord:
	_used[key] = true
	var w: GreasePencilWord = _words.get(key)
	var driven := shown_to >= 0.0
	if w == null:
		w = GreasePencilWord.new()
		w.name = "Word_%d" % _words.size()
		w.auto_write = not driven
		add_child(w)
		_words[key] = w
	if w.text != text:
		w.text = text
	w.ink = ink
	w.text_step = step
	w.scale = Vector2.ONE * k
	w.rotation = tilt
	var size := word_size(text, step) * k
	var font := Palette.pencil()
	var px := UiTheme.font_px(step)
	w.position = centre + Vector2(-size.x * 0.5, font.get_ascent(px) * k - size.y * 0.5).rotated(tilt)
	if driven:
		var n := float(text.length())
		w.shown_to = shown_to * n
		w.shown_from = shown_from * n
		w.visible = shown_to > shown_from
	return w


## The size of word `text` at type step `step` (unscaled).
static func word_size(text: String, step: int) -> Vector2:
	var font := Palette.pencil()
	var px := UiTheme.font_px(step)
	return Vector2(font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x, font.get_height(px))


## The centre of a word whose baseline starts at `baseline_left` (turned `tilt`), for `word`.
static func centre_of(baseline_left: Vector2, text: String, step: int, k: float = 1.0, tilt: float = 0.0) -> Vector2:
	var size := word_size(text, step) * k
	var px := UiTheme.font_px(step)
	var ascent := Palette.pencil().get_ascent(px) * k
	return baseline_left + Vector2(size.x * 0.5, size.y * 0.5 - ascent).rotated(tilt)


## Ends a pass: a mark or word not laid in it wipes off (AUTO) or is freed (driven).
func end() -> void:
	for key in _marks.keys():
		if not _used.has(key):
			_retire(_marks[key])
			_marks.erase(key)
			_keys.erase(key)
	for key in _words.keys():
		if not _used.has(key):
			_retire(_words[key])
			_words.erase(key)


## Wipes every mark and word off (the view closed its pencil).
func wipe_all() -> void:
	begin()
	end()


func _retire(n: Node) -> void:
	var auto := bool(n.get(&"auto_write"))
	if not auto or not (n as CanvasItem).is_visible_in_tree():
		n.queue_free()
		return
	n.wiped.connect(n.queue_free, CONNECT_ONE_SHOT | CONNECT_DEFERRED)
	if float(n.call(&"wipe")) <= 0.0 and is_instance_valid(n) and not n.is_queued_for_deletion():
		n.queue_free()


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


## The mark `key` (null when not laid).
func mark(key: String) -> GreasePencilMark:
	return _marks.get(key)


## The word `key` (null when not laid).
func word_of(key: String) -> GreasePencilWord:
	return _words.get(key)
