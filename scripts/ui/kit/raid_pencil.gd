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
