class_name SliceIcon
extends RefCounted
## Drawn icons for wheel slices (STYLE_GUIDE 4: a glyph on every slice, readable without
## colour): attack blade, crit starburst, defend shield, shield hex, evade dodge arrows,
## heal cross, afflict drip, deploy drone, miss dashed X. Shared by the combat wheels, the
## spinner view and the Modem's slice tiles. Draw on any CanvasItem.


## Draws the icon for `type` centred on `c`, `r` = half size, ink `col`.
static func draw_icon(ci: CanvasItem, c: Vector2, r: float, type: int, col: Color, outline: Color = Color(0, 0, 0, 0.85)) -> void:
	var w := maxf(1.5, r * 0.18)
	match type:
		RC.SliceType.ATTACK:
			var blade := PackedVector2Array([c + Vector2(-r * 0.15, r * 0.55), c + Vector2(-r * 0.15, -r * 0.35), c + Vector2(0, -r * 0.85), c + Vector2(r * 0.15, -r * 0.35), c + Vector2(r * 0.15, r * 0.55)])
			_filled(ci, blade, col, outline)
			ci.draw_line(c + Vector2(-r * 0.5, r * 0.55), c + Vector2(r * 0.5, r * 0.55), outline, w + 2.0)
			ci.draw_line(c + Vector2(-r * 0.5, r * 0.55), c + Vector2(r * 0.5, r * 0.55), col, w)
			ci.draw_line(c + Vector2(0, r * 0.55), c + Vector2(0, r * 0.9), col, w)
		RC.SliceType.CRIT:
			var star := PackedVector2Array()
			for k in 16:
				var rr := r * (0.95 if k % 2 == 0 else 0.4)
				var a := TAU * k / 16.0 - PI * 0.5
				star.append(c + Vector2(cos(a), sin(a)) * rr)
			_filled(ci, star, col, outline)
		RC.SliceType.DEFEND:
			var shield := PackedVector2Array([c + Vector2(-r * 0.7, -r * 0.7), c + Vector2(r * 0.7, -r * 0.7), c + Vector2(r * 0.7, 0), c + Vector2(0, r * 0.85), c + Vector2(-r * 0.7, 0)])
			_filled(ci, shield, col, outline)
			ci.draw_line(c + Vector2(0, -r * 0.55), c + Vector2(0, r * 0.55), Color(outline, 0.5), w * 0.7)
		RC.SliceType.SHIELD:
			var hexa := PackedVector2Array()
			for k in 6:
				var a := TAU * k / 6.0 - PI * 0.5
				hexa.append(c + Vector2(cos(a), sin(a)) * r * 0.85)
			_filled(ci, hexa, col, outline)
			var inner := PackedVector2Array()
			for k in 7:
				var a := TAU * k / 6.0 - PI * 0.5
				inner.append(c + Vector2(cos(a), sin(a)) * r * 0.45)
			ci.draw_polyline(inner, Color(outline, 0.6), w * 0.7)
		RC.SliceType.EVADE:
			for dx in [-0.35, 0.25]:
				var o := c + Vector2(r * dx, 0)
				var chev := PackedVector2Array([o + Vector2(-r * 0.3, -r * 0.6), o + Vector2(r * 0.25, 0), o + Vector2(-r * 0.3, r * 0.6)])
				ci.draw_polyline(chev, outline, w + 3.0)
				ci.draw_polyline(chev, col, w + 0.5)
		RC.SliceType.HEAL:
			var t := r * 0.28
			var cross := PackedVector2Array([c + Vector2(-t, -r * 0.8), c + Vector2(t, -r * 0.8), c + Vector2(t, -t), c + Vector2(r * 0.8, -t), c + Vector2(r * 0.8, t), c + Vector2(t, t),
				c + Vector2(t, r * 0.8), c + Vector2(-t, r * 0.8), c + Vector2(-t, t), c + Vector2(-r * 0.8, t), c + Vector2(-r * 0.8, -t), c + Vector2(-t, -t)])
			_filled(ci, cross, col, outline)
		RC.SliceType.AFFLICT:
			# A toxic drip: a round drop with a pointed top and two dark eyes.
			var drop := PackedVector2Array([c + Vector2(0, -r * 0.95)])
			for k in 13:
				var a := -PI * 0.15 + PI * 1.3 * k / 12.0
				drop.append(c + Vector2(0, r * 0.25) + Vector2(cos(a), sin(a)) * r * 0.6)
			_filled(ci, drop, col, outline)
			ci.draw_circle(c + Vector2(-r * 0.2, r * 0.25), r * 0.1, outline)
			ci.draw_circle(c + Vector2(r * 0.2, r * 0.25), r * 0.1, outline)
		RC.SliceType.DEPLOY:
			ci.draw_rect(Rect2(c - Vector2(r * 0.3, r * 0.2), Vector2(r * 0.6, r * 0.4)), col)
			for sx in [-1.0, 1.0]:
				ci.draw_line(c + Vector2(r * 0.3 * sx, 0), c + Vector2(r * 0.65 * sx, -r * 0.35), col, w)
				ci.draw_line(c + Vector2(r * 0.4 * sx, -r * 0.5), c + Vector2(r * 0.9 * sx, -r * 0.5), col, w)
			ci.draw_line(c + Vector2(-r * 0.2, r * 0.2), c + Vector2(-r * 0.35, r * 0.6), col, w * 0.8)
			ci.draw_line(c + Vector2(r * 0.2, r * 0.2), c + Vector2(r * 0.35, r * 0.6), col, w * 0.8)
		RC.SliceType.MISS:
			for k in 4:
				var t0 := -0.7 + k * 0.4
				ci.draw_line(c + Vector2(t0, t0) * r, c + Vector2(t0 + 0.25, t0 + 0.25) * r, col, w)
				ci.draw_line(c + Vector2(t0, -t0) * r, c + Vector2(t0 + 0.25, -t0 - 0.25) * r, col, w)
		_:
			ci.draw_circle(c, r * 0.4, col)


static func _filled(ci: CanvasItem, pts: PackedVector2Array, col: Color, outline: Color) -> void:
	var closed := pts.duplicate()
	closed.append(pts[0])
	ci.draw_colored_polygon(pts, col)
	ci.draw_polyline(closed, outline, 2.0)
