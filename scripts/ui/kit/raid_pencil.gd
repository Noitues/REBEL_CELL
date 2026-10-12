class_name RaidPencil
extends RefCounted
## ART-6 3A: the raid's grease-pencil geometry (ART_BIBLE v2 §1.2 "Grease pencil", §4.8
## "Pencil rules"; ported from art-concepts-r43 round 19-23 `ui19.pen_*`, `ui20.Pencil`,
## `ui21.Pencil`: jitter, arrow heads, scribble). Pure helpers on polylines: no state, no RNG
## (the wobble is a hash of the stroke's seed). B1b (integration review D3, one wax material):
## the vector drawing helpers this class had (a polyline body, shadow and sheen) are gone; every
## raid mark is drawn by the kit's wax (GreasePencilMark / GreasePencilWord through
## RaidPencilPool).

## Arrow head length (x the stroke width).
const HEAD_LEN := 3.0
## M14 12Q-RAID (ART_BIBLE v2 §5.1 "never colour alone"): with the colour-blind setting on, a
## threat's route carries hazard ticks (short bars across it, a barbed line) and its entry marks a
## reticle's four ticks, so hostile reads from the Cell's lime network by shape, not red alone
## (deutan: both read yellow). The ticks' spacing along the route and their half length (x the
## stroke width), the first tick's distance from the start, and the reticle ticks' reach outside a
## ring (x its radius) at the four diagonals.
const TICK_STEP := 7.0
const TICK_HALF := 1.6
const TICK_LEAD := 0.5
const RETICLE_FROM := 1.12
const RETICLE_TO := 1.5


## M14 12Q-RAID: true when the raid's hostile marks carry their shape cues (the colour-blind
## setting is on: Settings.colorblind_mode, which also adds its daltonize pass).
static func hostile_cues() -> bool:
	return Settings.colorblind_mode != &"off"


## M14 12Q-RAID: hazard ticks across route `pts`: a bar `half` px each side of it every `step` px,
## the first `step` x TICK_LEAD from the start, none in the last `step` (the arrow head's room).
static func hazard_ticks(pts: PackedVector2Array, step: float, half: float) -> Array[PackedVector2Array]:
	var out: Array[PackedVector2Array] = []
	var total := length_of(pts)
	if pts.size() < 2 or step <= 0.0:
		return out
	var d := step * TICK_LEAD
	while d <= total - step:
		var p := _at(pts, d)
		var n := _dir_at(pts, d).orthogonal()
		out.append(PackedVector2Array([p - n * half, p + n * half]))
		d += step
	return out


## M14 12Q-RAID: a reticle's four ticks round an ellipse at `centre` with `radii` (the
## diagonals, from RETICLE_FROM to RETICLE_TO of the radius).
static func reticle_ticks(centre: Vector2, radii: Vector2) -> Array[PackedVector2Array]:
	var out: Array[PackedVector2Array] = []
	for k in 4:
		var a := PI * 0.25 + PI * 0.5 * k
		var u := Vector2(cos(a) * radii.x, sin(a) * radii.y)
		out.append(PackedVector2Array([centre + u * RETICLE_FROM, centre + u * RETICLE_TO]))
	return out


## A repeatable pseudo-random value in [-1, 1] for stroke `seed` at `i` (a hash: no RNG).
static func noise(seed: int, i: float) -> float:
	var v := sin(float(seed) * 12.9898 + i * 78.233) * 43758.5453
	return (v - floorf(v)) * 2.0 - 1.0


## A smooth wobble in [-1, 1] along a stroke (`t` in samples).
static func wobble(seed: int, t: float) -> float:
	var a := floorf(t / 3.0)
	var f := t / 3.0 - a
	f = f * f * (3.0 - 2.0 * f)
	return lerpf(noise(seed, a), noise(seed, a + 1.0), f)


## The total length of polyline `pts`.
static func length_of(pts: PackedVector2Array) -> float:
	var total := 0.0
	for i in pts.size() - 1:
		total += pts[i].distance_to(pts[i + 1])
	return total


## The part of `pts` from `from_u` to `to_u` of its length (0..1 each).
static func trimmed(pts: PackedVector2Array, from_u: float, to_u: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	if pts.size() < 2 or to_u <= from_u:
		return out
	var total := length_of(pts)
	if total <= 0.0 or not is_finite(total):
		return out
	var a := clampf(from_u, 0.0, 1.0) * total
	var b := clampf(to_u, 0.0, 1.0) * total
	var run := 0.0
	for i in pts.size() - 1:
		var seg := pts[i].distance_to(pts[i + 1])
		var s0 := run
		var s1 := run + seg
		run = s1
		if s1 < a or s0 > b or seg <= 0.0:
			continue
		var p0 := pts[i].lerp(pts[i + 1], clampf((a - s0) / seg, 0.0, 1.0))
		var p1 := pts[i].lerp(pts[i + 1], clampf((b - s0) / seg, 0.0, 1.0))
		if out.is_empty():
			out.append(p0)
		out.append(p1)
	return out


## `pts` resampled every `step` px and wobbled sideways by up to `amp` px (deterministic).
static func roughen(pts: PackedVector2Array, seed: int, amp: float, step: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	if pts.size() < 2 or step <= 0.0:
		return pts
	var total := length_of(pts)
	if total <= 0.0 or not is_finite(total):
		return pts
	var n := clampi(ceili(total / step), 1, 2048)
	for k in n + 1:
		var u := float(k) / n
		var p := _at(pts, u * total)
		var dir := _dir_at(pts, u * total)
		out.append(p + dir.orthogonal() * wobble(seed, k) * amp)
	return out


static func _at(pts: PackedVector2Array, d: float) -> Vector2:
	for i in pts.size() - 1:
		var seg := pts[i].distance_to(pts[i + 1])
		if d <= seg:
			return pts[i].lerp(pts[i + 1], d / maxf(seg, 0.0001))
		d -= seg
	return pts[pts.size() - 1]


static func _dir_at(pts: PackedVector2Array, d: float) -> Vector2:
	for i in pts.size() - 1:
		var seg := pts[i].distance_to(pts[i + 1])
		if d <= seg and seg > 0.0:
			return (pts[i + 1] - pts[i]) / seg
		d -= seg
	var n := pts.size()
	return (pts[n - 1] - pts[n - 2]).normalized() if n >= 2 else Vector2.RIGHT


## A tight zigzag scribbled through `pts` (the part of a route a what-if would remove).
static func scribble_points(pts: PackedVector2Array, amp: float, pitch: float, seed: int = 1) -> PackedVector2Array:
	var out := PackedVector2Array()
	var total := length_of(pts)
	if total <= 0.0 or pitch <= 0.0:
		return out
	var n := clampi(ceili(total / pitch), 2, 512)
	for i in n + 1:
		var d := total * i / n
		var p := _at(pts, d)
		var dir := _dir_at(pts, d)
		var side := 1.0 if i % 2 == 0 else -1.0
		out.append(p + dir.orthogonal() * amp * side * (0.85 + 0.15 * noise(seed, i)))
	return out
