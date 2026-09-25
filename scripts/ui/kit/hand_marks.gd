class_name HandMarks
extends RefCounted
## Hand-drawn selection marks (the Cell's marker): a scrawled X (remove) and a loose,
## dripping circle (upgrade). Drawn on any CanvasItem over the thing they mark.


## A marker X across `r`: two thick strokes, each gone over twice with a slight offset.
static func draw_x(ci: CanvasItem, r: Rect2, col: Color) -> void:
	var inset := r.size * 0.1
	var a := r.position + inset
	var b := r.end - inset
	var c := Vector2(r.end.x - inset.x, r.position.y + inset.y)
	var d := Vector2(r.position.x + inset.x, r.end.y - inset.y)
	for pass_i in 2:
		var o := Vector2(2.0, -1.5) * pass_i
		var w := 9.0 if pass_i == 0 else 4.0
		var cc := col if pass_i == 0 else Color(col.lightened(0.3), 0.8)
		_stroke(ci, a + o + Vector2(-4, 3), b + o + Vector2(5, -2), w, cc)
		_stroke(ci, c + o + Vector2(3, -4), d + o + Vector2(-3, 5), w, cc)


## A loose marker circle around `c` (radius `r`), not quite closed, with two drips.
static func draw_drip_circle(ci: CanvasItem, c: Vector2, r: Vector2, col: Color) -> void:
	for pass_i in 2:
		var pts := PackedVector2Array()
		var start := -0.4 + pass_i * 0.15
		for k in 41:
			var t := start + TAU * 1.04 * k / 40.0
			var wob := 1.0 + 0.04 * sin(t * 3.0 + pass_i)
			pts.append(c + Vector2(cos(t) * r.x, sin(t) * r.y) * wob + Vector2(pass_i * 2.0, -pass_i * 1.5))
		ci.draw_polyline(pts, col if pass_i == 0 else Color(col.lightened(0.3), 0.7), 8.0 if pass_i == 0 else 3.5, true)
	for k in 2:
		var t := PI * (0.35 + k * 0.28)
		var p := c + Vector2(cos(t) * r.x, sin(t) * r.y)
		DripButton._drip(ci, p, 26.0 - k * 10.0, 8.0, col)


static func _stroke(ci: CanvasItem, a: Vector2, b: Vector2, w: float, col: Color) -> void:
	var n := (b - a).orthogonal().normalized()
	var steps := 12
	var prev := a
	for k in range(1, steps + 1):
		var t := float(k) / steps
		var p := a.lerp(b, t) + n * sin(t * PI) * 4.0
		ci.draw_line(prev, p, col, w * (0.7 + 0.3 * sin(t * PI)), true)
		prev = p
	ci.draw_circle(a, w * 0.35, col)
	ci.draw_circle(b, w * 0.45, col)
