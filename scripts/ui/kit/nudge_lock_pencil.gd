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
## The ring runs this many degrees past its start; its radius wobbles by WOBBLE (share) every
## WOBBLE_KNOT_PTS points; it is tilted up to TILT_DEG; the slash reaches SLASH_REACH of the
## ring's radius (past it), is off the diagonal up to SLASH_TILT_DEG and bows by SLASH_BOW.
const OVERSHOOT_DEG := 40.0
const WOBBLE := 0.06
const WOBBLE_KNOT_PTS := 14.0
const TILT_DEG := 12.0
const SLASH_REACH := 1.25
const SLASH_TILT_DEG := 6.0
const SLASH_BOW := 0.08
## A wide chip (RESPIN): the ring is an oval hugging the chip's outline, this share of its half
## sizes past it (r4), tilted at most FIT_TILT_DEG so the ends stay by the chip; the slash runs
## the chip's own corner to corner, FIT_SLASH_REACH of the ring's reach along it. The wax is
## lowered to FIT_ALPHA so `RESPIN` and the RAM cost read through it. The whole mark is kept
## FIT_SAFE_MARGIN px inside the screen.
const FIT_MARGIN := 0.1
const FIT_TILT_DEG := 3.0
const FIT_SLASH_REACH := 1.25
const FIT_ALPHA := 0.55
const FIT_SAFE_MARGIN := 12.0
## The ring's foot keeps this far above a label under the button (px: wax half width and shadow).
const FOOT_CLEAR := 7.0
## The wax pressure share (width varies along each stroke) of the lock marks.
const PRESSURE := 0.35
## Wax grain (r3): the share of both edges that drops out, and the core's streaky break.
const EDGE_GRAIN := 0.14
const CORE_BREAK := 0.7
## The re-scribble's zig-zags and how far each swings off the slash (share of the ring radius).
const SCRIBBLE_PASSES := 3
const SCRIBBLE_WIDTH := 0.55
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


## The circle-slash for a button at `center` with `radii` (global px): ONE hand-drawn ring stroke
## that overshoots its start, then the slash across it (writing order), top-left to bottom-right,
## past the ring at both ends. `keep_above` (a global y; INF = none) is the top of what sits under
## the button (its key label): the ring's foot, its stroke and shadow stay above it. Pure (tests
## read it).
static func shapes(center: Vector2, radii: Vector2, seed: int, keep_above: float = INF, fit: bool = false) -> Array[PackedVector2Array]:
	var rr := radii * ((1.0 + FIT_MARGIN) if fit else CIRCLE_SHARE)
	if keep_above < INF:
		rr.y = minf(rr.y, maxf(radii.y, keep_above - center.y - FOOT_CLEAR))
	var tilt := KitNoise.h11(seed, 3) * (FIT_TILT_DEG if fit else TILT_DEG)
	var ring := PencilShapes.hand_circle(center, rr, seed, 1.0 + OVERSHOOT_DEG / 360.0, deg_to_rad(tilt))
	for i in ring.size():
		var w := 1.0 + WOBBLE * (KitNoise.smooth(seed + 5, float(i) / WOBBLE_KNOT_PTS) * 2.0 - 1.0)
		ring[i] = center + (ring[i] - center) * w
	ring = PencilShapes.chaikin(ring)
	var reach := rr.length() * SLASH_REACH
	var d := Vector2.from_angle(deg_to_rad(SLASH_DEG + 180.0 + KitNoise.h11(seed, 4) * SLASH_TILT_DEG))
	if fit:
		d = -radii.normalized()
		reach = _fit_reach(rr, d)
	var a := center + d * reach
	var b := center - d * reach * (1.0 + 0.08 * KitNoise.h11(seed, 6))
	var bow := (b - a).orthogonal().normalized() * (reach * SLASH_BOW * KitNoise.h11(seed, 8))
	var slash := PencilShapes.resample(PencilShapes.chaikin(PackedVector2Array([a, a.lerp(b, 0.35) + bow, a.lerp(b, 0.7) + bow * 0.5, b])), SLASH_STEP)
	return [ring, slash] as Array[PackedVector2Array]


## How far along unit direction `d` the slash of an oval ring with radii `rr` reaches: the ring's
## own radius that way, times FIT_SLASH_REACH. Pure.
static func _fit_reach(rr: Vector2, d: Vector2) -> float:
	var k := sqrt(pow(d.x / rr.x, 2.0) + pow(d.y / rr.y, 2.0))
	return FIT_SLASH_REACH / maxf(k, 0.0001)


## The bounds of `strokes`, grown by the wax's half width and shadow. Pure.
static func mark_bounds(strokes: Array[PackedVector2Array]) -> Rect2:
	var box := Rect2()
	var first := true
	for st in strokes:
		for p in st:
			if first:
				box = Rect2(p, Vector2.ZERO)
				first = false
			else:
				box = box.expand(p)
	return box.grow(GreasePencilMark.WIDTH * 0.5 + GreasePencilMark.SHADOW_GROW)


## `strokes` brought inside `frame` shrunk by FIT_SAFE_MARGIN: on each axis the overflow is taken
## half by moving the mark in and half by squashing it toward its far side, so a chip flush with
## the screen edge keeps a ring that still hugs it. A mark larger than the frame is centred on it
## and squashed to fit. Pure.
static func clamp_into(strokes: Array[PackedVector2Array], frame: Rect2) -> Array[PackedVector2Array]:
	if strokes.is_empty():
		return strokes
	var pad := GreasePencilMark.WIDTH * 0.5 + GreasePencilMark.SHADOW_GROW
	var box := mark_bounds(strokes).grow(-pad)  # the points' own bounds: the wax's width is not squashed
	var safe := frame.grow(-(FIT_SAFE_MARGIN + pad))
	var scale := Vector2.ONE
	var origin := Vector2.ZERO
	var off := Vector2.ZERO
	for axis in 2:
		var lo: float = box.position[axis]
		var hi: float = box.end[axis]
		var s: float = box.size[axis]
		if s >= safe.size[axis]:
			scale[axis] = safe.size[axis] / s
			origin[axis] = lo
			off[axis] = safe.position[axis] - lo
		elif lo < safe.position[axis]:
			var o: float = safe.position[axis] - lo
			scale[axis] = (s - o * 0.5) / s
			origin[axis] = hi
			off[axis] = o * 0.5
		elif hi > safe.end[axis]:
			var o: float = hi - safe.end[axis]
			scale[axis] = (s - o * 0.5) / s
			origin[axis] = lo
			off[axis] = -o * 0.5
	if scale == Vector2.ONE and off == Vector2.ZERO:
		return strokes
	var out: Array[PackedVector2Array] = []
	for st in strokes:
		var q := PackedVector2Array()
		for p in st:
			q.append(origin + (p - origin) * scale + off)
		out.append(q)
	return out


## The re-scribble of a refused click: one back-and-forth stroke of SCRIBBLE_PASSES zig-zags down
## the slash's line, over the held mark (which stays whole). Pure.
static func scribble(center: Vector2, radii: Vector2, seed: int, fit: bool = false) -> PackedVector2Array:
	var rr := radii * ((1.0 + FIT_MARGIN) if fit else CIRCLE_SHARE)
	var d := Vector2.from_angle(deg_to_rad(SLASH_DEG + 180.0))
	var reach := rr.length() * SLASH_REACH
	var swing := rr.length() * SCRIBBLE_WIDTH
	if fit:
		d = -radii.normalized()
		reach = _fit_reach(rr, d)
		swing = minf(rr.y, swing)
	var n := d.orthogonal()
	var pts := PackedVector2Array()
	var count := SCRIBBLE_PASSES * 2 + 1
	for i in count:
		var u := float(i) / float(count - 1)
		var side := (1.0 if i % 2 == 0 else -1.0) * swing
		side *= 1.0 + 0.2 * KitNoise.h11(seed, i, 9)
		pts.append(center + d * reach * (1.0 - 2.0 * u) + n * side)
	return PencilShapes.resample(pts, SLASH_STEP)


## The keys of the marks showing now (written or writing; not the ones wiping off).
func shown_keys() -> Array[String]:
	var out: Array[String] = []
	for k: String in _live:
		out.append(k)
	IdSort.sort_ids(out)
	return out


## True while a write-on, re-scribble or wipe plays.
func motion_running() -> bool:
	if not _wipes.is_empty():
		return true
	for k: String in _live:
		if float(_live[k]["t"]) < 1.0 or float(_live[k].get("scr", 1.0)) < 1.0:
			return true
	return false


## MotionSkip: everything written whole, every wipe done.
func complete_motion() -> void:
	for k: String in _live:
		_live[k]["t"] = 1.0
		_live[k]["scr"] = 1.0
	_wipes.clear()
	_lay()


## A refused click on `group` (a wheel's combatant id, or "respin"): its slash is written once
## more over `nudge_lock_scribble` (at once without motion).
func rescribble(group: String) -> void:
	for k: String in _live:
		if String(_live[k]["group"]) == group:
			_live[k]["scr"] = 0.0 if Motion.live(SCRIBBLE_MOTION) else 1.0
			_live[k]["scr_dur"] = Motion.seconds(SCRIBBLE_MOTION)


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
		var fit := bool(m.get("fit", false))
		var strokes := shapes(m["center"], m["radii"], seed, float(m.get("keep_above", INF)), fit)
		if fit:
			strokes = clamp_into(strokes, _frame())
		if not _live.has(key):
			_live[key] = {"group": String(m["group"]), "t": 0.0 if Motion.live(WRITE_MOTION) else 1.0, "dur": Motion.seconds(WRITE_MOTION)}
		var st: Dictionary = _live[key]
		st["strokes"] = strokes
		st["center"] = m["center"]
		st["radii"] = m["radii"]
		st["seed"] = seed
		st["fit"] = fit
		if float(st["t"]) < 1.0:
			st["t"] = minf(1.0, float(st["t"]) + delta / maxf(float(st["dur"]), 0.001))
		if float(st.get("scr", 1.0)) < 1.0:
			st["scr"] = minf(1.0, float(st["scr"]) + delta / maxf(float(st["scr_dur"]), 0.001))
	for w in _wipes:
		w["t"] = minf(1.0, float(w["t"]) + delta / maxf(Motion.seconds(WIPE_MOTION), 0.001))
	_wipes = _wipes.filter(func(w: Dictionary) -> bool: return float(w["t"]) < 1.0)
	_lay()


## The screen the marks must stay inside.
func _frame() -> Rect2:
	return get_viewport().get_visible_rect() if is_inside_tree() else Rect2(Vector2.ZERO, Vector2(1920.0, 1080.0))


func _start_wipe(key: String) -> void:
	if not Motion.live(WIPE_MOTION):
		return
	var st: Dictionary = _live[key]
	_wipe_count += 1
	_wipes.append({"key": "wipe_%d" % _wipe_count, "strokes": st["strokes"], "seed": st["seed"], "fit": st.get("fit", false), "t": 0.0})


func _lay() -> void:
	if _pool == null or not is_instance_valid(_pool):
		if _live.is_empty() and _wipes.is_empty():
			return
		_pool = RaidPencilPool.make(self)
	_pool.begin()
	for key: String in _live:
		var st: Dictionary = _live[key]
		var scr := float(st.get("scr", 1.0))
		if scr < 1.0:
			var fit := bool(st.get("fit", false))
			var sp: Array[PackedVector2Array] = [scribble(st["center"], st["radii"], int(st["seed"]), fit)]
			if fit:
				sp = clamp_into(sp, _frame())
			_flat(_pool.stroke(key + "|scr", sp, GreasePencilMark.Ink.THREAT, scr, 0.0, false, int(st["seed"]) + 1), fit)
		_flat(_pool.stroke(key, st["strokes"], GreasePencilMark.Ink.THREAT, float(st["t"]), 0.0, false, int(st["seed"])), bool(st.get("fit", false)))
	for w in _wipes:
		_flat(_pool.stroke(String(w["key"]), w["strokes"], GreasePencilMark.Ink.THREAT, 1.0, float(w["t"]), false, int(w["seed"])), bool(w.get("fit", false)))
	_pool.end()


## Hand pressure along the stroke, no lit side: a flat wax stroke.
func _flat(m: GreasePencilMark, fit: bool = false) -> void:
	m.wax_alpha = FIT_ALPHA if fit else GreasePencilMark.WAX_ALPHA
	m.wobble = PRESSURE
	m.highlight = false
	m.edge_grain = EDGE_GRAIN
	m.core_break = CORE_BREAK
