class_name PencilShapes
extends RefCounted
## Grease pencil geometry (ART-1 1B; ported from round 3 `tg_lib.py`: resample, chaikin,
## hand_circle, bezier, arrow_strokes, and §6.3's "snapping to real edge polylines so marks
## stay true"). Pure functions on polylines; the jitter comes from KitNoise (never game RNG).

## A hand circle's points per full turn.
const CIRCLE_POINTS := 120
## LOOK-TOOLBOX 12 (AUDIT: "rings are perfect ellipses"): a hand loop is one egg-shaped pass
## whose tail overlaps its start (RcPencilLook.loop_overlap_deg) and runs out past it
## (loop_tail_out), its radius jittered (loop_jitter), its axis tilted by the seed (loop_tilt).
## The knot spacing (deg) and how far inside the pen lands (over the first LAND_TURNS of a turn).
const KNOT_DEG := 55.0
const START_IN := 0.05
const LAND_TURNS := 0.12
const LOOK: RcPencilLook = preload("res://addons/rc_look/config/pencil_look.tres")
## Chaikin passes when smoothing a hand path.
const SMOOTH_PASSES := 2
## Arrow head flicks: angle off the shaft (deg; LOOK-TOOLBOX 12: 140, was 152, whose barbs merged
## into the shaft at the 10-16 px widths) and the share of the head they bend in at.
const HEAD_ANGLE_DEG := 140.0
const HEAD_BEND := 0.4
## The shaft's heading at the tip is read over this share of the head's length.
const HEAD_BACK := 0.6


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


## The loop's turns (one, plus the look's overlap).
static func loop_turns() -> float:
	return 1.0 + LOOK.loop_overlap_deg / 360.0


## The loop's radius jitter share (RcPencilLook.loop_jitter).
static func jitter_share() -> float:
	return LOOK.loop_jitter


## The loop's radius share at turn share `u` (0 at the start, 1 a full turn): 1 + its jitter
## (jitter_share at most, seeded KitNoise knots every KNOT_DEG, never game RNG).
static func jitter(seed: int, u: float) -> float:
	var x := u * 360.0 / KNOT_DEG
	var n := KitNoise.smooth(seed + 11, x) * 0.65 + KitNoise.smooth(seed + 29, x * 2.3) * 0.35
	return jitter_share() * (n * 2.0 - 1.0)


## A hand-drawn loop round `centre` (radii `radii`), tilted `angle` plus the seed's tilt (B1b,
## review D3 lock; LOOK-TOOLBOX 12): one pass that goes `turns` times round (< 0: loop_turns(),
## it overruns its start), egg-shaped (loop_egg) and jittered (jitter_share) from `seed`
## (deterministic KitNoise), the pen landing START_IN inside the line and the tail running out
## loop_tail_out past it, so the start and the end never meet cleanly.
static func hand_circle(centre: Vector2, radii: Vector2, seed: int, turns: float = -1.0, angle: float = 0.0) -> PackedVector2Array:
	var out := PackedVector2Array()
	if turns < 0.0:
		turns = loop_turns()
	angle += KitNoise.h11(seed, 61) * LOOK.loop_tilt
	var egg_phase := KitNoise.h01(seed, 62) * TAU
	var n := int(CIRCLE_POINTS * turns)
	var start := deg_to_rad(lerpf(-150.0, -100.0, KitNoise.h01(seed, 1)))
	var over := maxf(turns - 1.0, 0.0001)
	for i in n:
		var t := float(i) / float(n - 1)
		var u := turns * t
		var a := start + TAU * u
		var rr := 1.0 + jitter(seed, u) + LOOK.loop_egg * cos(2.0 * a + egg_phase)
		# the pen lands a little inside the line it will draw, and its tail runs out past it
		rr -= START_IN * (1.0 - smoothstep(0.0, LAND_TURNS, u))
		rr += LOOK.loop_tail_out * clampf((u - 1.0) / over, 0.0, 1.0)
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
## short stroke out of the tip). `head` px long; KitNoise from `seed` varies them.
static func arrow(shaft: PackedVector2Array, head: float, seed: int) -> Array[PackedVector2Array]:
	var out: Array[PackedVector2Array] = [shaft]
	if shaft.size() < 2:
		return out
	var tip := shaft[shaft.size() - 1]
	# the heading over the head's own length (LOOK-TOOLBOX 12: never a count of samples, which a
	# densely sampled hand path bends inside its last corner)
	var back := tip
	var walked := 0.0
	for i in range(shaft.size() - 2, -1, -1):
		walked += shaft[i].distance_to(shaft[i + 1])
		back = shaft[i]
		if walked >= head * HEAD_BACK:
			break
	var dv := (tip - back).normalized()
	for k in 2:
		var sgn := 1.0 if k == 0 else -1.0
		var ang := deg_to_rad(HEAD_ANGLE_DEG * sgn + KitNoise.h11(seed, 40 + k) * 5.0)
		var v := dv.rotated(ang)
		var hl := head * lerpf(0.9, 1.1, KitNoise.h01(seed, 50 + k))
		# LOOK-TOOLBOX 12: from the tip out (the pen presses at the point and flicks off), so the
		# pressure keeps the point solid and thins the barbs, never a broom of thin strands at the tip
		out.append(PackedVector2Array([tip, tip + v * hl * HEAD_BEND, tip + v * hl]))
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


# --- LOOK-TOOLBOX 12: the hand (AUDIT "geometry is machine-perfect") ---------------------------

## `pts` with a hand's sideways wobble: a smooth seeded offset (KitNoise, never game RNG) of up
## to RcPencilLook.path_wobble of the width `w`, in waves path_wave widths long, easing in from
## the start (the pen lands where it means to) and out to the end (a tip that must hit).
static func hand_path(pts: PackedVector2Array, seed: int, w: float) -> PackedVector2Array:
	var p := resample(pts, maxf(w * 0.5, 1.0))
	var total := length_of(p)
	if p.size() < 3 or total <= 0.0:
		return p
	var out := PackedVector2Array()
	var d := 0.0
	var amp := w * LOOK.path_wobble
	var wave := maxf(w * LOOK.path_wave, 1.0)
	for j in p.size():
		if j > 0:
			d += p[j].distance_to(p[j - 1])
		var t := d / total
		var nrm := (p[mini(j + 1, p.size() - 1)] - p[maxi(j - 1, 0)]).normalized().orthogonal()
		var ease := smoothstep(0.0, 0.25, t) * (1.0 - smoothstep(0.85, 1.0, t))
		out.append(p[j] + nrm * (KitNoise.smooth(seed + 3, d / wave) * 2.0 - 1.0) * amp * ease)
	return out


## A hand underline from `from` to `to` (width `w`): one stroke that bows a little (line_bow
## of the width), overshoots each end (line_overshoot of its length, at least
## line_overshoot_min widths) and ends in a hooked downstroke (hook_len widths turning
## hook_turn_deg clockwise on screen), as the concept's underline does.
static func hand_line(from: Vector2, to: Vector2, seed: int, w: float) -> PackedVector2Array:
	var dvec := to - from
	var len := maxf(dvec.length(), 1.0)
	var dir := dvec / len
	var nrm := dir.orthogonal()
	var over := maxf(len * LOOK.line_overshoot, w * LOOK.line_overshoot_min)
	var a := from - dir * over * (0.5 + 0.5 * KitNoise.h01(seed, 71))
	var b := to + dir * over
	var bow := w * LOOK.line_bow * KitNoise.h11(seed, 72)
	var pts := PackedVector2Array()
	var n := maxi(int((len + 2.0 * over) / maxf(w, 1.0)), 4)
	for i in n + 1:
		var t := float(i) / float(n)
		pts.append(a.lerp(b, t) + nrm * sin(PI * t) * bow)
	# the hook: the pen turns down and back as it lifts
	var hook := w * LOOK.hook_len
	var turn := deg_to_rad(LOOK.hook_turn_deg)
	var steps := 6
	var at := b
	for k in steps:
		at += dir.rotated(turn * float(k + 1) / float(steps)) * hook / float(steps)
		pts.append(at)
	return hand_path(pts, seed, w)


## A hand route through `pts` (width `w`): its corners rounded to corner_radius widths with a
## little overshoot past each (corner_overshoot widths: the pen runs on before it turns), then
## the hand's wobble.
static func hand_route(pts: PackedVector2Array, seed: int, w: float) -> PackedVector2Array:
	if pts.size() < 3:
		return hand_path(pts, seed, w)
	var out := PackedVector2Array([pts[0]])
	var r := w * LOOK.corner_radius
	var ov := w * LOOK.corner_overshoot
	for i in range(1, pts.size() - 1):
		var p := pts[i]
		var din := (p - pts[i - 1]).normalized()
		var dout := (pts[i + 1] - p).normalized()
		var rin := minf(r, p.distance_to(pts[i - 1]) * 0.45)
		var rout := minf(r, p.distance_to(pts[i + 1]) * 0.45)
		var c1 := p + din * minf(ov, rin) + dout * minf(ov, rout) * 0.35
		out.append_array(bezier(p - din * rin, c1, p + dout * rout, 8))
	out.append(pts[pts.size() - 1])
	return hand_path(out, seed, w)


## The bounding rect of `pts` grown by `margin`.
static func bounds(pts: PackedVector2Array, margin: float = 0.0) -> Rect2:
	if pts.is_empty():
		return Rect2()
	var r := Rect2(pts[0], Vector2.ZERO)
	for p in pts:
		r = r.expand(p)
	return r.grow(margin)
