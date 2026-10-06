class_name PencilShapes
extends RefCounted
## Grease pencil geometry (ART-1 1B; ported from round 3 `tg_lib.py`: resample, chaikin,
## hand_circle, bezier, arrow_strokes, and §6.3's "snapping to real edge polylines so marks
## stay true"). Pure functions on polylines; the jitter comes from KitNoise (never game RNG).

## A hand circle's points per full turn.
const CIRCLE_POINTS := 120
## B1b (integration review D3): a hand loop is one ellipse whose tail overlaps its start by
## this many degrees (not a perfect circle, not a second pass).
const OVERLAP_DEG := 20.0
const LOOP_TURNS := 1.0 + OVERLAP_DEG / 360.0
## The loop's irregularity (shares of its radius): the seeded radius jitter (D3: about
## +-3 %), its knot spacing (deg), how far inside the pen lands (over the first LAND_TURNS of
## a turn) and how far out the 20 degree tail runs, so start and end never meet cleanly.
const JITTER := 0.03
const KNOT_DEG := 55.0
const START_IN := 0.05
const LAND_TURNS := 0.12
const TAIL_OUT := 0.09
## Chaikin passes when smoothing a hand path.
const SMOOTH_PASSES := 2
## Arrow head flicks: angle off the shaft (deg) and the share of the head they bend in at.
const HEAD_ANGLE_DEG := 152.0
const HEAD_BEND := 0.4


## `pts` resampled every `step` px along its length (end points kept).
static func resample(pts: PackedVector2Array, step: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	if pts.size() < 2 or step <= 0.0:
		return pts.duplicate()
	out.append(pts[0])
	var carry := 0.0
	for i in range(1, pts.size()):
		var a := pts[i - 1]
		var b := pts[i]
		var seg := a.distance_to(b)
		var d := step - carry
		while d <= seg:
			out.append(a.lerp(b, d / seg))
			d += step
		carry = seg - (d - step)
	if out[out.size() - 1] != pts[pts.size() - 1]:
		out.append(pts[pts.size() - 1])
	return out


## Chaikin corner cutting, `passes` times (ends kept).
static func chaikin(pts: PackedVector2Array, passes: int = SMOOTH_PASSES) -> PackedVector2Array:
	var p := pts
	for _k in passes:
		if p.size() < 3:
			return p
		var q := PackedVector2Array([p[0]])
		for i in p.size() - 1:
			q.append(p[i].lerp(p[i + 1], 0.25))
			q.append(p[i].lerp(p[i + 1], 0.75))
		q.append(p[p.size() - 1])
		p = q
	return p


## The polyline's length (px).
static func length_of(pts: PackedVector2Array) -> float:
	var l := 0.0
	for i in range(1, pts.size()):
		l += pts[i - 1].distance_to(pts[i])
	return l


## The part of `pts` between lengths `from_len` and `to_len` (px), end points interpolated:
## write-on and the wipe trim points, never alpha.
static func trim(pts: PackedVector2Array, from_len: float, to_len: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	if pts.size() < 2 or to_len <= from_len:
		return out
	var acc := 0.0
	for i in range(1, pts.size()):
		var a := pts[i - 1]
		var b := pts[i]
		var seg := a.distance_to(b)
		var s0 := acc
		var s1 := acc + seg
		if s1 >= from_len and s0 <= to_len and seg > 0.0:
			var t0 := clampf((from_len - s0) / seg, 0.0, 1.0)
			var t1 := clampf((to_len - s0) / seg, 0.0, 1.0)
			var p0 := a.lerp(b, t0)
			if out.is_empty() or out[out.size() - 1] != p0:
				out.append(p0)
			out.append(a.lerp(b, t1))
		acc = s1
	return out


## The loop's radius share at turn share `u` (0 at the start, 1 a full turn): 1 + its jitter
## (JITTER at most, seeded KitNoise knots every KNOT_DEG, never game RNG).
static func jitter(seed: int, u: float) -> float:
	var x := u * 360.0 / KNOT_DEG
	var n := KitNoise.smooth(seed + 11, x) * 0.65 + KitNoise.smooth(seed + 29, x * 2.3) * 0.35
	return JITTER * (n * 2.0 - 1.0)


## A hand-drawn ellipse round `centre` (radii `radii`), tilted `angle` (B1b, review D3 lock):
## one pass that goes `turns` times round (LOOP_TURNS: it overruns its start by a 20 degree
## tail), its radius jittered by up to JITTER from `seed` (deterministic KitNoise), the pen
## landing START_IN inside the line and the tail running out TAIL_OUT past it, so the start
## and the end never meet cleanly.
static func hand_circle(centre: Vector2, radii: Vector2, seed: int, turns: float = LOOP_TURNS, angle: float = 0.0) -> PackedVector2Array:
	var out := PackedVector2Array()
	var n := int(CIRCLE_POINTS * turns)
	var start := deg_to_rad(lerpf(-150.0, -100.0, KitNoise.h01(seed, 1)))
	var over := maxf(turns - 1.0, 0.0001)
	for i in n:
		var t := float(i) / float(n - 1)
		var u := turns * t
		var a := start + TAU * u
		var rr := 1.0 + jitter(seed, u)
		# the pen lands a little inside the line it will draw, and its tail runs out past it
		rr -= START_IN * (1.0 - smoothstep(0.0, LAND_TURNS, u))
		rr += TAIL_OUT * clampf((u - 1.0) / over, 0.0, 1.0)
		var p := Vector2(radii.x * rr * cos(a), radii.y * rr * sin(a)).rotated(angle)
		out.append(centre + p)
	return out


## A quadratic Bezier p0 -> p1 -> p2 as `n` points.
static func bezier(p0: Vector2, p1: Vector2, p2: Vector2, n: int = 60) -> PackedVector2Array:
	var out := PackedVector2Array()
	for i in n:
		var t := float(i) / float(n - 1)
		var u := 1.0 - t
		out.append(p0 * (u * u) + p1 * (2.0 * u * t) + p2 * (t * t))
	return out


## A hand arrow's strokes in writing order: the shaft, then the two head flicks (each a
## short bent stroke into the tip). `head` px long; KitNoise from `seed` varies them.
static func arrow(shaft: PackedVector2Array, head: float, seed: int) -> Array[PackedVector2Array]:
	var out: Array[PackedVector2Array] = [shaft]
	if shaft.size() < 2:
		return out
	var tip := shaft[shaft.size() - 1]
	var back := shaft[maxi(0, shaft.size() - 8)]
	var dv := (tip - back).normalized()
	for k in 2:
		var sgn := 1.0 if k == 0 else -1.0
		var ang := deg_to_rad(HEAD_ANGLE_DEG * sgn + KitNoise.h11(seed, 40 + k) * 5.0)
		var v := dv.rotated(ang)
		var hl := head * lerpf(0.9, 1.1, KitNoise.h01(seed, 50 + k))
		out.append(PackedVector2Array([tip + v * hl, tip + v * hl * HEAD_BEND, tip]))
	return out


## Every point of `pts` moved onto the nearest point of the polyline `edge` (a route, a
## wall, a slice's rim), so a mark drawn near it says exactly what the rules will do.
static func snap_to(pts: PackedVector2Array, edge: PackedVector2Array) -> PackedVector2Array:
	var out := PackedVector2Array()
	if edge.size() < 2:
		return pts.duplicate()
	for p in pts:
		var best := edge[0]
		var best_d := INF
		for i in range(1, edge.size()):
			var q := Geometry2D.get_closest_point_to_segment(p, edge[i - 1], edge[i])
			var d := p.distance_squared_to(q)
			if d < best_d:
				best_d = d
				best = q
		out.append(best)
	return out


## The bounding rect of `pts` grown by `margin`.
static func bounds(pts: PackedVector2Array, margin: float = 0.0) -> Rect2:
	if pts.is_empty():
		return Rect2()
	var r := Rect2(pts[0], Vector2.ZERO)
	for p in pts:
		r = r.expand(p)
	return r.grow(margin)
