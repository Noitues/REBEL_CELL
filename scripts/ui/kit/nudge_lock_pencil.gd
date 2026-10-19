class_name NudgeLockPencil
extends Node
## N7 (designer ruling 2026-10-19, art-pass 18.1): a locked nudge button (and a locked RESPIN chip)
## wears a red #FF1C2C wax circle-slash, the kit's one grease-pencil material (GreasePencilMark
## through RaidPencilPool, on the pencil layer above every UI: no UI ever covers it). It replaces
## the NUDGE LOCKED / RESPIN LOCKED word chips and the refusal toast (3.1: on the button, never as
## a word).
##
## Motion: it writes on (`pencil_write_on`) when the lock applies and cloth-wipes off
## (`pencil_wipe`) when it ends, never an alpha fade; a refused click re-scribbles it once
## (`nudge_lock_scribble`, T1, 0.25 s). Reduce effects / headless: written whole at once, gone at
## once (the end state is the same). MotionSkip passive: one press completes every write and wipe.
##
## The scene says what to mark through `spec` (a Callable returning an Array of {key, group,
## center (global px), radii (Vector2, px)}); `group` names what a refusal re-scribbles (a wheel's
## combatant id, or "respin"). View only.

## The circle's reach past the button (shares of its radii) and the wax seed's fold.
const CIRCLE_SHARE := 1.3
## The slash runs from the circle's upper left to its lower right, this far round it (degrees off
## the circle's top-left diagonal either way: 0 is the true diagonal).
const SLASH_DEG := 45.0
## The slash's points are resampled this far apart (px) so its write-on trims smoothly.
const SLASH_STEP := 3.0
const WRITE_MOTION := GreasePencilMark.WRITE
const WIPE_MOTION := GreasePencilMark.WIPE
const SCRIBBLE_MOTION := &"nudge_lock_scribble"

## () -> Array[Dictionary]: the marks to show now (see the class doc).
var spec: Callable = Callable()

var _pool: RaidPencilPool = null
## key -> {group, strokes, seed, t (written share), dur (seconds of its write)}.
var _live: Dictionary = {}
## Marks wiping off: [{key, strokes, seed, t}].
var _wipes: Array[Dictionary] = []
var _wipe_count: int = 0


func _init() -> void:
	name = "NudgeLockPencil"


func _ready() -> void:
	MotionSkip.register_passive(self)


func _exit_tree() -> void:
	if _pool != null and is_instance_valid(_pool):
		_pool.release()
	_pool = null


## The circle-slash for a button at `center` with `radii` (global px): the hand circle, then the
## slash across it (writing order). Pure (tests read it).
static func shapes(center: Vector2, radii: Vector2, seed: int) -> Array[PackedVector2Array]:
	var rr := radii * CIRCLE_SHARE
	var circle := PencilShapes.hand_circle(center, rr, seed)
	var d := Vector2.from_angle(deg_to_rad(SLASH_DEG + 180.0))
	var a := center + d * rr
	var b := center - d * rr
	var slash := PencilShapes.resample(PackedVector2Array([a, b]), SLASH_STEP)
	return [circle, slash] as Array[PackedVector2Array]


## The keys of the marks showing now (written or writing; not the ones wiping off).
func shown_keys() -> Array[String]:
	var out: Array[String] = []
	for k: String in _live:
		out.append(k)
	out.sort()
	return out


## True while a write-on, re-scribble or wipe plays.
func motion_running() -> bool:
	if not _wipes.is_empty():
		return true
	for k: String in _live:
		if float(_live[k]["t"]) < 1.0:
			return true
	return false


## MotionSkip: everything written whole, every wipe done.
func complete_motion() -> void:
	for k: String in _live:
		_live[k]["t"] = 1.0
	_wipes.clear()
	_lay()


## A refused click on `group` (a wheel's combatant id, or "respin"): its slash is written once
## more over `nudge_lock_scribble` (at once without motion).
func rescribble(group: String) -> void:
	for k: String in _live:
		if String(_live[k]["group"]) == group:
			_live[k]["t"] = 0.0 if Motion.live(SCRIBBLE_MOTION) else 1.0
			_live[k]["dur"] = Motion.seconds(SCRIBBLE_MOTION)


func _marks() -> Array:
	if not spec.is_valid():
		return []
	var v: Variant = spec.call()
	return v if v is Array else []


func _process(delta: float) -> void:
	var want: Dictionary = {}
	for m: Dictionary in _marks():
		want[String(m["key"])] = m
	for key: String in _live.keys():
		if not want.has(key):
			_start_wipe(key)
			_live.erase(key)
	for key: String in want:
		var m: Dictionary = want[key]
		var seed := key.hash()
		var strokes := shapes(m["center"], m["radii"], seed)
		if not _live.has(key):
			_live[key] = {"group": String(m["group"]), "t": 0.0 if Motion.live(WRITE_MOTION) else 1.0, "dur": Motion.seconds(WRITE_MOTION)}
		var st: Dictionary = _live[key]
		st["strokes"] = strokes
		st["seed"] = seed
		if float(st["t"]) < 1.0:
			st["t"] = minf(1.0, float(st["t"]) + delta / maxf(float(st["dur"]), 0.001))
	for w in _wipes:
		w["t"] = minf(1.0, float(w["t"]) + delta / maxf(Motion.seconds(WIPE_MOTION), 0.001))
	_wipes = _wipes.filter(func(w: Dictionary) -> bool: return float(w["t"]) < 1.0)
	_lay()


func _start_wipe(key: String) -> void:
	if not Motion.live(WIPE_MOTION):
		return
	var st: Dictionary = _live[key]
	_wipe_count += 1
	_wipes.append({"key": "wipe_%d" % _wipe_count, "strokes": st["strokes"], "seed": st["seed"], "t": 0.0})


func _lay() -> void:
	if _pool == null or not is_instance_valid(_pool):
		if _live.is_empty() and _wipes.is_empty():
			return
		_pool = RaidPencilPool.make(self)
	_pool.begin()
	for key: String in _live:
		var st: Dictionary = _live[key]
		_pool.stroke(key, st["strokes"], GreasePencilMark.Ink.THREAT, float(st["t"]), 0.0, false, int(st["seed"]))
	for w in _wipes:
		_pool.stroke(String(w["key"]), w["strokes"], GreasePencilMark.Ink.THREAT, 1.0, float(w["t"]), false, int(w["seed"]))
	_pool.end()
