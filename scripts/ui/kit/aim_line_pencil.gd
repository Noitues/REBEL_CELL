class_name AimLinePencil
extends Node
## S-COMBAT-HUD (parity CMB-10, designer ruling 2026-10-05: card aiming is drawn in grease
## pencil): the aim from the card to its target is a yellow grease-pencil arrow on the kit's
## wax (GreasePencilMark through RaidPencilPool, the pencil layer above every UI: no UI ever
## covers grease pencil), the concept's look (art pass round 19 `card_play_v2_storyboard`
## 04 PEEL + AIM / 05 SLAP, `card_play.py` draw_aim): a bowed stroke from the card's top edge
## that ends short of the target with two head flicks, and once the aim is on a valid target
## a hand loop round that wheel (or drone). Solid: it is what this play will do (§1.2).
##
## Motion (kept entries, restyled): the arrow writes on over `aim_line_draw` each time the aim
## moves (the scene drives `arrow_t`); the loop writes on over `pencil_write_on` when the aim
## snaps onto a target (B1b, D25: ~0.4 s; `target_snap` stays the reticle's snap); a mark the
## aim leaves wipes off with the kit's cloth wipe
## (`pencil_wipe`, never an alpha fade). Reduce effects / headless: whole at once, gone at
## once. MotionSkip passive: one press completes every write and wipe.
##
## The scene says what to draw each frame through `spec` (a Callable returning the aim:
## {} for none, else {from, to, arrow_t, hub (bool: the arrow stops at the hub's edge),
## stop (px it stops short), loop: {} or {key, center, radius}, marks: [{key, center, radius,
## ink}] (slices circled), lines: [{key, from, to}] (B2: the HP result chips underlined)}).
## Each underline writes on over `pencil_write_on` the first frame it is laid (its own clock, so
## a wheel whose chips start to change mid-aim writes its line too) and wipes off when it goes.
## View only.

## The arrow's bow (share of its length, the concept's quarter bow halved for the shorter
## combat reach), the loop's size (shares of the target's radius: the concept's 1.12 x 0.97
## ellipse) and the share of the hub the arrow stops at (concept: 0.28 of the wheel). The wax's
## width is the kit's one width (GreasePencilMark.stroke_width, B1b).
const BOW := 0.12
const LOOP_R := Vector2(1.12, 1.087)
const HUB_STOP := 0.28
## Points per arrow shaft; the arrow's and the loop's wax seeds (the concept's 11 and 5).
const SHAFT_POINTS := 24
const ARROW_SEED := 11
const LOOP_SEED := 5

## B2 underline: points along it, its hand wobble (share of the wax's width) and its pen overrun
## past each end (share of its length: the concept's underline runs a little past the chips).
const LINE_POINTS := 16
const LINE_WOBBLE := 0.22
const LINE_OVERRUN := 0.04

const LOOP_MOTION := GreasePencilMark.WRITE
const WIPE_MOTION := GreasePencilMark.WIPE

## () -> Dictionary: the aim to draw now (see the class doc).
var spec: Callable = Callable()

var _pool: RaidPencilPool = null
var _loop_key: String = ""
var _loop_t: float = 1.0
## The last arrow / loop drawn: {strokes, ink, width, seed}.
var _last_arrow: Dictionary = {}
var _last_loop: Dictionary = {}
var _last_marks: Dictionary = {}
## Marks wiping off: [{key, strokes, ink, width, seed, t}].
var _wipes: Array[Dictionary] = []
var _wipe_count: int = 0
## B2: each underline's write-on progress (key -> 0..1).
var _line_t: Dictionary = {}


func _init() -> void:
	name = "AimLinePencil"


func _ready() -> void:
	MotionSkip.register_passive(self)


func _exit_tree() -> void:
	if _pool != null and is_instance_valid(_pool):
		_pool.release()
	_pool = null


## MotionSkip: a loop is writing on or a mark is wiping off.
func motion_running() -> bool:
	if _loop_t < 1.0 or not _wipes.is_empty():
		return true
	for k in _line_t:
		if float(_line_t[k]) < 1.0:
			return true
	return false


## MotionSkip: everything written whole, every wipe done.
func complete_motion() -> void:
	_loop_t = 1.0
	for k in _line_t:
		_line_t[k] = 1.0
	_wipes.clear()
	_lay(_current())


## The marks showing now (tests): the pool's marks.
func shown() -> Array[Node2D]:
	return _pool.shown() if _pool != null and is_instance_valid(_pool) else ([] as Array[Node2D])


## The arrow and loop points for `aim` (global px): {arrow: [strokes], loop: [strokes]}.
static func shapes(aim: Dictionary) -> Dictionary:
	var out := {"arrow": [] as Array[PackedVector2Array], "loop": [] as Array[PackedVector2Array]}
	if aim.is_empty():
		return out
	var from: Vector2 = aim["from"]
	var to: Vector2 = aim["to"]
	var stop := float(aim.get("stop", 0.0))
	if from.distance_to(to) > stop + 1.0:
		var end := to + (from - to).normalized() * stop
		var mid := (from + end) * 0.5 + (end - from).orthogonal() * BOW
		var shaft := PencilShapes.bezier(from, mid, end, SHAFT_POINTS)
		out["arrow"] = PencilShapes.arrow(shaft, GreasePencilMark.stroke_width() * RaidPencil.HEAD_LEN, ARROW_SEED)
	var loop: Dictionary = aim.get("loop", {})
	if not loop.is_empty():
		var r := float(loop["radius"])
		var pts := PencilShapes.hand_circle(loop["center"], Vector2(r * LOOP_R.x, r * LOOP_R.y), LOOP_SEED)
		(out["loop"] as Array[PackedVector2Array]).append(pts)
	return out


## B2: a hand underline from `from` to `to` (global px): one wax pass that overruns each end by
## LINE_OVERRUN of its length, wobbling by up to LINE_WOBBLE of the wax's width (seeded KitNoise
## through PencilShapes.jitter: deterministic, never game RNG), its far end lifting a little as
## a hand's does.
static func underline(from: Vector2, to: Vector2, seed: int) -> PackedVector2Array:
	var out := PackedVector2Array()
	var d := to - from
	var len := maxf(d.length(), 1.0)
	var dir := d / len
	var nrm := dir.orthogonal()
	var amp := GreasePencilMark.stroke_width() * LINE_WOBBLE / PencilShapes.JITTER
	var a := from - dir * len * LINE_OVERRUN
	var b := to + dir * len * LINE_OVERRUN
	for i in LINE_POINTS:
		var t := float(i) / float(LINE_POINTS - 1)
		var lift := t * t * GreasePencilMark.stroke_width() * LINE_WOBBLE
		out.append(a.lerp(b, t) + nrm * (PencilShapes.jitter(seed, t) * amp + lift))
	return out


func _current() -> Dictionary:
	if not spec.is_valid():
		return {}
	var v: Variant = spec.call()
	return v if v is Dictionary else {}


func _process(delta: float) -> void:
	var aim := _current()
	var loop: Dictionary = aim.get("loop", {})
	var key := String(loop.get("key", ""))
	if key != _loop_key:
		if not _last_loop.is_empty():
			_start_wipe(_last_loop)
		_last_loop = {}
		_loop_key = key
		_loop_t = 0.0 if key != "" and Motion.live(LOOP_MOTION) else 1.0
	if _loop_t < 1.0:
		_loop_t = minf(1.0, _loop_t + delta / maxf(Motion.seconds(LOOP_MOTION), 0.001))
	if aim.is_empty() and not _last_arrow.is_empty():
		_start_wipe(_last_arrow)
		_last_arrow = {}
	for w in _wipes:
		w["t"] = minf(1.0, float(w["t"]) + delta / maxf(Motion.seconds(WIPE_MOTION), 0.001))
	_wipes = _wipes.filter(func(w: Dictionary) -> bool: return float(w["t"]) < 1.0)
	for k in _line_t:
		_line_t[k] = minf(1.0, float(_line_t[k]) + delta / maxf(Motion.seconds(LOOP_MOTION), 0.001))
	_lay(aim)


func _start_wipe(mark: Dictionary) -> void:
	if not Motion.live(WIPE_MOTION):
		return
	var w := mark.duplicate()
	_wipe_count += 1
	w["key"] = "wipe_%d" % _wipe_count
	w["t"] = 0.0
	_wipes.append(w)


## Asks the pool for this frame's marks.
func _lay(aim: Dictionary) -> void:
	if _pool == null or not is_instance_valid(_pool):
		if aim.is_empty() and _wipes.is_empty():
			return
		_pool = RaidPencilPool.make(self)
	_pool.begin()
	var sh := shapes(aim)
	var arrow: Array[PackedVector2Array] = sh["arrow"]
	if not arrow.is_empty():
		var t := clampf(float(aim.get("arrow_t", 1.0)), 0.0, 1.0)
		_pool.stroke("arrow", arrow, GreasePencilMark.Ink.PLAN, t, 0.0, false, ARROW_SEED)
		_last_arrow = {"strokes": arrow, "ink": GreasePencilMark.Ink.PLAN, "seed": ARROW_SEED}
	var loop: Array[PackedVector2Array] = sh["loop"]
	if not loop.is_empty():
		_pool.stroke("loop", loop, GreasePencilMark.Ink.PLAN, _loop_t, 0.0, false, LOOP_SEED)
		_last_loop = {"strokes": loop, "ink": GreasePencilMark.Ink.PLAN, "seed": LOOP_SEED}
	# The slices the play changes: a small hand circle each, written with the loop.
	var marks: Dictionary = {}
	for m: Dictionary in aim.get("marks", []):
		var key := "mark|%s" % String(m["key"])
		var seed := String(m["key"]).hash()
		var r := float(m["radius"])
		var strokes: Array[PackedVector2Array] = [PencilShapes.hand_circle(m["center"], Vector2(r, r), seed)]
		_pool.stroke(key, strokes, m["ink"], _loop_t, 0.0, false, seed)
		marks[key] = {"strokes": strokes, "ink": m["ink"], "seed": seed}
	# B2: the HP result chips of each wheel the play changes, underlined (each its own write-on).
	var lines_now: Dictionary = {}
	for ln: Dictionary in aim.get("lines", []):
		var key := "line|%s" % String(ln["key"])
		var seed := String(ln["key"]).hash()
		if not _line_t.has(key):
			_line_t[key] = 0.0 if Motion.live(LOOP_MOTION) else 1.0
		var strokes: Array[PackedVector2Array] = [underline(ln["from"], ln["to"], seed)]
		_pool.stroke(key, strokes, GreasePencilMark.Ink.PLAN, float(_line_t[key]), 0.0, false, seed)
		marks[key] = {"strokes": strokes, "ink": GreasePencilMark.Ink.PLAN, "seed": seed}
		lines_now[key] = true
	for key in _line_t.keys():
		if not lines_now.has(key):
			_line_t.erase(key)
	for key in _last_marks:
		if not marks.has(key):
			_start_wipe(_last_marks[key])
	_last_marks = marks
	for w in _wipes:
		_pool.stroke(String(w["key"]), w["strokes"], w["ink"], 1.0, float(w["t"]), false, int(w["seed"]))
	_pool.end()
