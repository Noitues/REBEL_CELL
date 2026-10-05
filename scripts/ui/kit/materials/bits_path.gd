class_name BitsPath
extends RefCounted
## The binary bits' paths and times (ART-1 1B; ART_BIBLE v2 §6.3): pure math shared by the
## particle process shader's inputs (`shaders/kit/binary_bits.gdshader`), the CPU fallback
## and the views that schedule on arrival (HP ticks, segment flashes, lag drains). Every
## number comes from the source cell and KitNoise, never from the particles: arrival times
## are known before a bit flies (never read back). View only.

## Around a wheel the control point sits on the rim-side bisector at this many rim radii.
const RIM_CONTROL := 1.5
## Without a wheel the path bows by this share of its length (sucked along a curve).
const FREE_BOW := 0.25
## A bit's flight time varies by +- this share of the entry's flight.
const FLIGHT_SPREAD := 0.15
## Tumble speed range (rad/s).
const SPIN_MIN := 4.0
const SPIN_MAX := 11.0


## The quadratic Bezier control point from `start` to `target`. With a wheel (rim_radius >
## 0) it lies on the bisector of the start and target directions from the wheel's centre at
## RIM_CONTROL x the radius (so bits go round the rim, never across the face); a start
## opposite the target turns the bisector a quarter turn. Without a wheel the path bows to
## one side by FREE_BOW of its length.
static func control_point(start: Vector2, target: Vector2, rim_centre: Vector2 = Vector2.ZERO, rim_radius: float = 0.0) -> Vector2:
	if rim_radius > 0.0:
		var a := (start - rim_centre).normalized()
		var b := (target - rim_centre).normalized()
		var bis := a + b
		if bis.length() < 0.001:
			bis = Vector2(-a.y, a.x)
		return rim_centre + bis.normalized() * RIM_CONTROL * rim_radius
	var mid := (start + target) * 0.5
	var d := target - start
	return mid + Vector2(-d.y, d.x) * FREE_BOW


## The point at `t` (0..1) on the Bezier start -> ctrl -> target.
static func at(start: Vector2, ctrl: Vector2, target: Vector2, t: float) -> Vector2:
	var u := 1.0 - t
	return start * (u * u) + ctrl * (2.0 * u * t) + target * (t * t)


## The eased share of the path at time share `t` (slow, then sucked in): the shader's ease.
static func eased(t: float) -> float:
	t = clampf(t, 0.0, 1.0)
	return t * t * (3.0 - 2.0 * t) * 0.35 + t * t * 0.65


## The spawn delay of a bit whose source is `x_share` (0 left .. 1 right) across its source,
## with `spread` seconds from the first to the last (delay proportional to x).
static func spawn_delay(x_share: float, spread: float) -> float:
	return clampf(x_share, 0.0, 1.0) * spread


## Bit `i`'s flight time for burst seed `seed` around `flight` seconds.
static func flight_time(i: int, seed: int, flight: float) -> float:
	return flight * (1.0 + KitNoise.h11(seed, i, 31) * FLIGHT_SPREAD)


## Bit `i`'s flip phase (0..1) and tumble speed (rad/s, either way).
static func flip_phase(i: int, seed: int) -> float:
	return KitNoise.h01(seed, i, 32)


static func spin(i: int, seed: int) -> float:
	var s := lerpf(SPIN_MIN, SPIN_MAX, KitNoise.h01(seed, i, 33))
	return s if KitNoise.h01(seed, i, 34) > 0.5 else -s


## Every bit's plan: [{start, ctrl, delay, flight, arrive, phase, spin}] for `starts` flying
## to `target` (with the wheel's centre and radius when it goes round a rim).
static func plan(starts: PackedVector2Array, target: Vector2, flight: float, spread: float, seed: int,
		rim_centre: Vector2 = Vector2.ZERO, rim_radius: float = 0.0) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if starts.is_empty():
		return out
	var x0 := INF
	var x1 := -INF
	for p in starts:
		x0 = minf(x0, p.x)
		x1 = maxf(x1, p.x)
	for i in starts.size():
		var p := starts[i]
		var share := (p.x - x0) / (x1 - x0) if x1 > x0 else 0.0
		var delay := spawn_delay(share, spread)
		var fl := flight_time(i, seed, flight)
		out.append({"start": p, "ctrl": control_point(p, target, rim_centre, rim_radius), "delay": delay,
			"flight": fl, "arrive": delay + fl, "phase": flip_phase(i, seed), "spin": spin(i, seed)})
	return out


## The arrival times of a plan, sorted (the view schedules on these).
static func arrivals(p: Array[Dictionary]) -> PackedFloat32Array:
	var out := PackedFloat32Array()
	for b in p:
		out.append(float(b["arrive"]))
	out.sort()
	return out


## `count` source points spread over `rect` in a grid, row by row (a sticker's or a card's
## opaque cells; deterministic).
static func points_in_rect(rect: Rect2, count: int) -> PackedVector2Array:
	var out := PackedVector2Array()
	if count <= 0 or rect.size.x <= 0.0 or rect.size.y <= 0.0:
		return out
	var cols := maxi(1, int(round(sqrt(float(count) * rect.size.x / rect.size.y))))
	var rows := maxi(1, ceili(float(count) / float(cols)))
	for i in count:
		var c := i % cols
		var r := i / cols
		out.append(rect.position + Vector2((float(c) + 0.5) / float(cols) * rect.size.x, (float(r) + 0.5) / float(rows) * rect.size.y))
	return out
