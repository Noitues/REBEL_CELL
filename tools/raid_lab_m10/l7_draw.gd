class_name L7Draw
extends RefCounted
## Drawing helpers of the L7 look: glowing beam ribbons, perspective floor rings, target brackets, the falling wrench, the
## countdown ring. Pure drawing on a CanvasItem; the view decides what to draw and when (from the resolver's events).

const G = preload("res://tools/raid_lab_m10/l5_glyphs.gd")


## A light ribbon along `path`: a wide faint halo, the beam body in `col`, a hot white-blue core. `glow` scales the halo and the
## core (1 = a known beam, 0 = a dim pending line: a thin plain line). Optionally an arrow head at the tip.
static func beam(ci: CanvasItem, path: PackedVector2Array, col: Color, w: float, glow: float = 1.0, arrow: bool = true) -> void:
	if path.size() < 2:
		return
	if glow <= 0.01:
		ci.draw_polyline(path, col, maxf(2.0, w * 0.55), true)
		return
	# The floor wash under the beam, a halo, the saturated cobalt body, a hot core (the frames' blazing line).
	ci.draw_polyline(path, Color(col.r, col.g, col.b, 0.05 * glow), w * 8.0, true)
	ci.draw_polyline(path, Color(col.r, col.g, col.b, 0.12 * glow), w * 4.2, true)
	ci.draw_polyline(path, Color(col.r, col.g, col.b, 0.3 * glow), w * 2.3, true)
	ci.draw_polyline(path, col, w * 1.2, true)
	var hot := Color(G.THREAT_HOT.r, G.THREAT_HOT.g, G.THREAT_HOT.b, minf(1.0, 0.5 + 0.4 * glow))
	ci.draw_polyline(path, hot, maxf(1.5, w * 0.24), true)
	if arrow:
		arrow_head(ci, path, hot, w)


static func arrow_head(ci: CanvasItem, path: PackedVector2Array, col: Color, w: float = 6.0) -> void:
	var last: Vector2 = path[path.size() - 1]
	var prev: Vector2 = path[path.size() - 2]
	if last.distance_to(prev) > 0.5:
		var d := (last - prev).normalized()
		var n := Vector2(-d.y, d.x)
		var s := 6.0 + w * 0.7
		ci.draw_colored_polygon(PackedVector2Array([last + d * s * 1.1, last - d * s * 0.7 + n * s * 0.9, last - d * s * 0.7 - n * s * 0.9]), col)


## A soft round light at c (stacked discs, the falloff of a glow).
static func glow(ci: CanvasItem, c: Vector2, r: float, col: Color, alpha: float = 0.5) -> void:
	for i in range(5):
		var f := float(i) / 5.0
		ci.draw_circle(c, r * (1.0 - f * 0.8), Color(col.r, col.g, col.b, alpha * 0.16 * (0.6 + f)))


## A ring on the floor under a cell, in the board's perspective: `r` in board units, `sides` 6 for the hex, 36 for a circle.
static func floor_ring(ci: CanvasItem, c: Vector2i, r: float, col: Color, w: float = 3.0, sides: int = 36, z: float = 0.06) -> void:
	var pts := PackedVector2Array()
	var rot := PI / 6.0 if sides == 6 else 0.0
	for k in range(sides + 1):
		var a := rot + TAU * float(k % sides) / sides
		pts.append(L7Cam.project(Vector3(L7Cam.COLS[c.x] + cos(a) * r, L7Cam.ROWS[c.y] + sin(a) * r, z)))
	ci.draw_polyline(pts, col, w, true)


## Four corner brackets round a box centered on `c` (a target lock).
static func brackets(ci: CanvasItem, c: Vector2, half: Vector2, col: Color, w: float = 3.0, arm: float = 11.0) -> void:
	for sx in [-1.0, 1.0]:
		for sy in [-1.0, 1.0]:
			var corner := c + Vector2(half.x * sx, half.y * sy)
			ci.draw_polyline(PackedVector2Array([corner - Vector2(arm * sx, 0.0), corner, corner - Vector2(0.0, arm * sy)]), col, w, true)


## The wrench token that drops onto a node going DOWN: a dark disc with a pale ring and a wrench; `u` 0..1 is the drop
## (it lands at u = 1 and fades after), `alpha` the overall fade.
static func wrench_token(ci: CanvasItem, c: Vector2, u: float, alpha: float = 1.0, r: float = 15.0) -> void:
	var y := -86.0 * (1.0 - L7Config.drop(u))
	var p := c + Vector2(0.0, y)
	ci.draw_circle(p, r + 2.0, Color(0.02, 0.03, 0.08, 0.92 * alpha))
	ci.draw_arc(p, r, 0.0, TAU, 28, Color(G.INK.r, G.INK.g, G.INK.b, alpha), 2.5, true)
	G.wrench(ci, p + Vector2(1.0, 1.0), r * 0.6, Color(G.INK.r, G.INK.g, G.INK.b, alpha))


## A countdown ring: a track, an arc of `frac` (1 = full) in `col` starting at the top, and a centered number.
static func countdown_ring(ci: CanvasItem, c: Vector2, r: float, frac: float, col: Color, number: String) -> void:
	ci.draw_circle(c, r, Color(0.02, 0.04, 0.1, 0.9))
	ci.draw_arc(c, r, 0.0, TAU, 40, Color(col.r, col.g, col.b, 0.22), 4.0, true)
	if frac > 0.001:
		ci.draw_arc(c, r, -PI * 0.5, -PI * 0.5 + TAU * clampf(frac, 0.0, 1.0), 40, col, 4.0, true)
	G.text_c(ci, c, number, int(r * 1.1), G.INK, "head")


## A thin bar that drains (the decide bar): a dim track and the remaining part in `col`.
static func drain_bar(ci: CanvasItem, r: Rect2, frac: float, col: Color) -> void:
	ci.draw_rect(r, Color(col.r, col.g, col.b, 0.18))
	ci.draw_rect(Rect2(r.position, Vector2(r.size.x * clampf(frac, 0.0, 1.0), r.size.y)), col)


## A curve from a to b bulging by `bulge` px to the side (the decoy's pull, the skip's bypass), drawn up to `u` 0..1.
static func arc(ci: CanvasItem, a: Vector2, b: Vector2, bulge: float, col: Color, w: float, u: float = 1.0) -> void:
	var n := Vector2(-(b - a).y, (b - a).x).normalized() * bulge
	var m := (a + b) * 0.5 + n
	var pts := PackedVector2Array()
	var steps := 16
	var upto := clampf(u, 0.0, 1.0)
	for i in range(int(ceil(steps * upto)) + 1):
		var t := minf(float(i) / steps, upto)
		pts.append(a * (1.0 - t) * (1.0 - t) + m * 2.0 * t * (1.0 - t) + b * t * t)
	if pts.size() >= 2:
		ci.draw_polyline(pts, col, w, true)


## Dashed polyline with a scrolling phase (the shimmer of a sealed line): dashes of `on` px every `on + off`, shifted by `phase` px.
static func dashed(ci: CanvasItem, path: PackedVector2Array, col: Color, on: float, off: float, w: float, phase: float = 0.0) -> void:
	var period := on + off
	var carry := fposmod(phase, period)
	for i in range(path.size() - 1):
		var a := path[i]
		var b := path[i + 1]
		var length := a.distance_to(b)
		if length < 0.5:
			continue
		var d := (b - a) / length
		var s := -carry
		while s < length:
			var s0 := maxf(0.0, s)
			var s1 := minf(length, s + on)
			if s1 > s0:
				ci.draw_line(a + d * s0, a + d * s1, col, w, true)
			s += period
		carry = fposmod(carry + length, period)
