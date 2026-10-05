class_name BitPath
extends RefCounted
## ART-2 2C (ART_BIBLE v2 §3.18 dissolve A, §3.20, §6.3): a stream of 0/1 bits as pure
## numbers. Every bit is a function of time (it appears, tumbles free, then rides a
## quadratic Bezier into its target and is absorbed), so the view **precomputes arrival
## times** (`arrivals`) to schedule what the bits feed (an HP tick, a segment flash) and
## never reads particles back. Scatter comes from hashes of the stream's `seed`, never from
## an RNG, so a stream is the same every time it plays. No nodes, no state of the game.
##
## A bit: {from, burst (the free flight's displacement), ctrl, to (global px), appear,
## release, travel (s from the stream's start), glyph (GLYPHS index), size (px), fade
## (true: it fades out as it goes, with no target to be absorbed into), end_scale}.

## The glyphs a bit can be: 0, 1 and the heal's plus (§3.20).
const GLYPHS: Array[String] = ["0", "1", "+"]
const ZERO := 0
const ONE := 1
const PLUS := 2
## A Bezier's control point sits on the rim-side bisector at this many outer radii, so a
## shard goes round the wheel and never across its face (§6.3).
const RIM_CONTROL := 1.5
## Dissolve A spirals clockwise into the hub: the control point is the cell turned this far
## round the hub (rad, clockwise on screen) and pulled in to this share of its distance.
const SPIRAL_TURN := PI * 0.5
const SPIRAL_PULL := 0.9

var bits: Array[Dictionary] = []


## The point at `t` (0..1) along the quadratic Bezier a -> c -> b.
static func quad(a: Vector2, c: Vector2, b: Vector2, t: float) -> Vector2:
	var u := 1.0 - t
	return a * u * u + c * 2.0 * u * t + b * t * t


## Hash noise 0..1 (decoration only, never an RNG).
static func noise(a: int, b: int, c: int = 0) -> float:
	return float(hash(Vector3i(a, b, c)) & 0xFFFF) / 65535.0


## The seconds after the stream starts at which bit `i` is absorbed.
func arrival(i: int) -> float:
	var b := bits[i]
	return float(b["release"]) + float(b["travel"])


## Every bit's arrival (s from the stream's start), ascending: what the view schedules on.
func arrivals() -> PackedFloat32Array:
	var out := PackedFloat32Array()
	for i in bits.size():
		out.append(arrival(i))
	out.sort()
	return out


## The last bit's arrival (s): the stream's length.
func length() -> float:
	var last := 0.0
	for i in bits.size():
		last = maxf(last, arrival(i))
	return last


## Where bit `i` is at `t` s from the stream's start, its alpha and scale:
## {at, alpha, scale, shown, hot (0..1: how white-hot it still is)}.
func sample(i: int, t: float, hot_seconds: float = 0.1) -> Dictionary:
	var b := bits[i]
	var appear := float(b["appear"])
	var release := float(b["release"])
	var travel := maxf(0.001, float(b["travel"]))
	if t < appear or t >= release + travel:
		return {"shown": false}
	var from: Vector2 = b["from"]
	var free_end := from + (b["burst"] as Vector2)
	var hot := 1.0 - clampf((t - appear) / maxf(0.001, hot_seconds), 0.0, 1.0)
	if t < release:
		var q := clampf((t - appear) / maxf(0.001, release - appear), 0.0, 1.0)
		var eased := 1.0 - (1.0 - q) * (1.0 - q)
		return {"shown": true, "at": from.lerp(free_end, eased), "alpha": 1.0, "scale": 1.0, "hot": hot}
	var p := clampf((t - release) / travel, 0.0, 1.0)
	if bool(b.get("fade", false)):
		# No target: it drifts and fades out (a dissolving word's bits).
		var e := 1.0 - (1.0 - p) * (1.0 - p)
		return {"shown": true, "at": quad(free_end, b["ctrl"], b["to"], e), "alpha": 1.0 - p, "scale": 1.0, "hot": hot}
	# Ease-in cubic into the target, shrinking to its end scale (§6.3).
	var c := p * p * p
	return {"shown": true, "at": quad(free_end, b["ctrl"], b["to"], c), "alpha": 1.0, "scale": lerpf(1.0, float(b.get("end_scale", 1.0)), c), "hot": hot}


func _bit(from: Vector2, burst: Vector2, ctrl: Vector2, to: Vector2, appear: float, release: float, travel: float, glyph: int, size: float,
		fade: bool = false, end_scale: float = 1.0) -> void:
	bits.append({"from": from, "burst": burst, "ctrl": ctrl, "to": to, "appear": appear, "release": release, "travel": travel,
		"glyph": glyph, "size": size, "fade": fade, "end_scale": end_scale})


## The control point that takes a bit from `a` to `b` round a wheel at `center` of outer
## radius `r_out`: on the bisector of their angles (the short way round), RIM_CONTROL radii out.
static func rim_control(a: Vector2, b: Vector2, center: Vector2, r_out: float) -> Vector2:
	var da := (a - center)
	var db := (b - center)
	if da.length() < 0.001 or db.length() < 0.001:
		return (a + b) * 0.5
	var mid := (da.normalized() + db.normalized())
	if mid.length() < 0.001:
		mid = da.normalized().orthogonal()
	return center + mid.normalized() * r_out * RIM_CONTROL


## Hit shards (§3.20 Hit): `n` bits burst from `at` along `normal` (spread `spread` rad,
## out `reach` px), tumble for `free` s, then curve round the wheel (`center`, `r_out`) into
## `targets` (spread over them by index), their suck starts staggered over `stagger` s, each
## travelling `travel` s. Glyph sizes from `size_min` to `size_max`; `through` (0..1) of
## them only go to the targets when `bounce` (a blocked hit): the rest fall away and fade.
static func shards(seed: int, at: Vector2, normal: Vector2, n: int, spread: float, reach: float, free: float, stagger: float, travel: float,
		targets: Array[Vector2], center: Vector2, r_out: float, size_min: float, size_max: float, end_scale: float,
		bounce: bool = false, through: float = 1.0, fall: float = 0.0) -> BitPath:
	var bp := BitPath.new()
	var base := normal.angle() if normal.length() > 0.001 else -PI * 0.5
	var passing := n if not bounce else maxi(0, roundi(n * through))
	for i in n:
		var a := base + (noise(seed, i, 1) - 0.5) * spread
		var d := reach * (0.45 + 0.55 * noise(seed, i, 2))
		var burst := Vector2(cos(a), sin(a)) * d
		var size := lerpf(size_min, size_max, noise(seed, i, 3))
		var glyph := ONE if noise(seed, i, 4) > 0.5 else ZERO
		var release := free + stagger * (float(i) / maxf(1.0, float(n - 1)))
		if bounce and i >= passing:
			# Dim shards bounce off the wall and fall away under gravity, fading.
			var off := at + burst
			var drop := off + Vector2(-burst.x * 0.4, fall)
			bp._bit(at, burst, (off + drop) * 0.5 + Vector2(0, -fall * 0.25), drop, 0.0, release, travel, glyph, size * 0.8, true)
			continue
		var to: Vector2 = targets[i % targets.size()] if not targets.is_empty() else center
		var start := at + burst
		bp._bit(at, burst, rim_control(start, to, center, r_out), to, 0.0, release, travel, glyph, size, false, end_scale)
	return bp


## Dissolve A (§3.18 step 6): `rect` (global) cut into `cell` px cells; a scan front runs
## top to bottom over `scan` s; each cell decodes to a 0/1 glyph as the front passes it,
## holds `hold` s (plus up to `jitter` s), then spirals clockwise into `hub` over `travel`
## s (plus up to `travel_spread`). Glyphs `size_min`..`size_max` px.
static func dissolve(seed: int, rect: Rect2, cell: float, scan: float, hold: float, jitter: float, travel: float, travel_spread: float,
		hub: Vector2, size_min: float, size_max: float, end_scale: float) -> BitPath:
	var bp := BitPath.new()
	var cols := maxi(1, int(rect.size.x / cell))
	var rows := maxi(1, int(rect.size.y / cell))
	var step := Vector2(rect.size.x / cols, rect.size.y / rows)
	for r in rows:
		for c in cols:
			var i := r * cols + c
			var at := rect.position + Vector2((c + 0.5) * step.x, (r + 0.5) * step.y)
			var appear := scan * (float(r) / maxf(1.0, float(rows)))
			var release := appear + hold + jitter * noise(seed, i, 5)
			var tr := travel + travel_spread * noise(seed, i, 6)
			var ctrl := hub + (at - hub).rotated(SPIRAL_TURN) * SPIRAL_PULL
			var glyph := ONE if noise(seed, i, 7) > 0.5 else ZERO
			bp._bit(at, Vector2.ZERO, ctrl, hub, appear, release, tr, glyph, lerpf(size_min, size_max, noise(seed, i, 8)), false, end_scale)
	return bp


## Bits that flow in (heal from outside, a drone packing at its dock, a wall's stream, RAM
## gain into the meter): `n` bits from `sources` (cycled) to `targets` (cycled), appearing
## over `stagger` s, each travelling `travel` s along a Bezier bowed by `bow` px to the side.
## `plus_share` of them are `+` glyphs (the heal).
static func inflow(seed: int, sources: Array[Vector2], targets: Array[Vector2], n: int, stagger: float, travel: float, bow: float,
		size_min: float, size_max: float, end_scale: float, plus_share: float = 0.0) -> BitPath:
	var bp := BitPath.new()
	if sources.is_empty() or targets.is_empty():
		return bp
	for i in n:
		var from: Vector2 = sources[i % sources.size()]
		var to: Vector2 = targets[i % targets.size()]
		var appear := stagger * (float(i) / maxf(1.0, float(n - 1)))
		var side := (noise(seed, i, 9) - 0.5) * 2.0
		var ctrl := (from + to) * 0.5 + (to - from).orthogonal().normalized() * bow * side
		var glyph := PLUS if noise(seed, i, 10) < plus_share else (ONE if noise(seed, i, 11) > 0.5 else ZERO)
		bp._bit(from, Vector2.ZERO, ctrl, to, appear, appear, travel, glyph, lerpf(size_min, size_max, noise(seed, i, 12)), false, end_scale)
	return bp


## A word's dissolve (§3.20 temporary labels): bits at `points` (left to right), each
## released `sweep` s * its x share after the start, drifting up `rise` px as they fade
## over `travel` s.
static func drift(seed: int, points: Array[Vector2], sweep: float, travel: float, rise: float, size_min: float, size_max: float) -> BitPath:
	var bp := BitPath.new()
	if points.is_empty():
		return bp
	var x0 := points[0].x
	var x1 := points[0].x
	for p in points:
		x0 = minf(x0, p.x)
		x1 = maxf(x1, p.x)
	for i in points.size():
		var p: Vector2 = points[i]
		var share := (p.x - x0) / maxf(1.0, x1 - x0)
		var appear := sweep * share
		var to := p + Vector2((noise(seed, i, 13) - 0.5) * rise * 0.6, -rise * (0.6 + 0.4 * noise(seed, i, 14)))
		var glyph := ONE if noise(seed, i, 15) > 0.5 else ZERO
		bp._bit(p, Vector2.ZERO, (p + to) * 0.5, to, appear, appear, travel, glyph, lerpf(size_min, size_max, noise(seed, i, 16)), true)
	return bp


## Points on a ring at `center` of radius `r`, from angle `a0` to `a1` (rad), `n` of them
## (an HP arc's drained segments, a wall's course, a dock).
static func arc_points(center: Vector2, r: float, a0: float, a1: float, n: int) -> Array[Vector2]:
	var out: Array[Vector2] = []
	for i in maxi(1, n):
		var a := lerpf(a0, a1, (float(i) + 0.5) / maxf(1.0, float(n)))
		out.append(center + Vector2(cos(a), sin(a)) * r)
	return out
