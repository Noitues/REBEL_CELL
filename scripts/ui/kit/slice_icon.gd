class_name SliceIcon
extends RefCounted
## Drawn icons for wheel slices (STYLE_GUIDE 4: a glyph on every slice, readable without
## colour): attack blade, crit starburst, defend shield, shield hex, evade dodge arrows,
## heal cross, afflict drip, deploy drone, miss dashed X. Shared by the combat wheels, the
## spinner view and the Modem's slice tiles. Draw on any CanvasItem.


## How icons sit on a slice (design review, `--demo-iconstyle=N`):
## 0 BLACK & WHITE: solid black glyph, white outline (baseline).
## 1 BADGE: the black-and-white glyph in a dark disc with a white rim.
## 2 INVERSE BADGE: a white glyph with a black outline in a dark disc.
## 3 GLOW: the black-and-white glyph over a soft halo of the slice colour.
## 4 BOLD: a larger black glyph with a heavy white outline.
static var style: int = 0
static var _outline_w: float = 2.0
static var _bold: bool = false
const STYLE_NAMES: Array[String] = ["BLACK & WHITE", "BADGE", "INVERSE BADGE", "GLOW", "BOLD"]


## A slice's icon on its wedge, in the current `style` (`slice_col` = the wedge colour).
static func draw_on_slice(ci: CanvasItem, c: Vector2, r: float, type: int, slice_col: Color) -> void:
	var black := Color(0.02, 0.02, 0.03)
	var white := Color(1, 1, 1)
	match style:
		1:
			ci.draw_circle(c, r * 1.25, Color(0.03, 0.03, 0.05, 0.9))
			ci.draw_arc(c, r * 1.25, 0, TAU, 32, white, maxf(1.5, r * 0.12), true)
			draw_icon(ci, c, r * 0.85, type, black, white)
		2:
			ci.draw_circle(c, r * 1.25, Color(0.03, 0.03, 0.05, 0.9))
			ci.draw_arc(c, r * 1.25, 0, TAU, 32, Color(slice_col, 0.9), maxf(1.5, r * 0.1), true)
			draw_icon(ci, c, r * 0.85, type, white, black)
		3:
			for k in 4:
				ci.draw_circle(c, r * (1.5 - k * 0.2), Color(slice_col.lightened(0.3), 0.14))
			draw_icon(ci, c, r, type, black, white)
		4:
			_bold = true
			draw_icon(ci, c, r * 1.15, type, black, white)
			_bold = false
		_:
			draw_icon(ci, c, r, type, black, white)


## Draws the icon for `type` centred on `c`, `r` = half size, ink `col`.
static func draw_icon(ci: CanvasItem, c: Vector2, r: float, type: int, col: Color, outline: Color = Color(0, 0, 0, 0.85)) -> void:
	var w := maxf(1.5, r * 0.18)
	_outline_w = r * (0.3 if _bold else 0.16)
	match type:
		RC.SliceType.ATTACK:
			var blade := PackedVector2Array([c + Vector2(-r * 0.24, r * 0.5), c + Vector2(-r * 0.24, -r * 0.35), c + Vector2(0, -r * 0.9), c + Vector2(r * 0.24, -r * 0.35), c + Vector2(r * 0.24, r * 0.5)])
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
			# Two passes: the outline colour wider underneath, then the ink.
			for pass_n in 2:
				var ink := outline if pass_n == 0 else col
				var grow := 3.0 if pass_n == 0 else 0.0
				ci.draw_rect(Rect2(c - Vector2(r * 0.3, r * 0.2) - Vector2.ONE * grow * 0.5, Vector2(r * 0.6, r * 0.4) + Vector2.ONE * grow), ink)
				for sx in [-1.0, 1.0]:
					ci.draw_line(c + Vector2(r * 0.3 * sx, 0), c + Vector2(r * 0.65 * sx, -r * 0.35), ink, w + grow)
					ci.draw_line(c + Vector2(r * 0.4 * sx, -r * 0.5), c + Vector2(r * 0.9 * sx, -r * 0.5), ink, w + grow)
				ci.draw_line(c + Vector2(-r * 0.2, r * 0.2), c + Vector2(-r * 0.35, r * 0.6), ink, w * 0.8 + grow)
				ci.draw_line(c + Vector2(r * 0.2, r * 0.2), c + Vector2(r * 0.35, r * 0.6), ink, w * 0.8 + grow)
		RC.SliceType.MISS:
			for pass_n in 2:
				var ink := outline if pass_n == 0 else col
				var grow := 3.0 if pass_n == 0 else 0.0
				for k in 4:
					var t0 := -0.7 + k * 0.4
					ci.draw_line(c + Vector2(t0, t0) * r, c + Vector2(t0 + 0.25, t0 + 0.25) * r, ink, w + grow)
					ci.draw_line(c + Vector2(t0, -t0) * r, c + Vector2(t0 + 0.25, -t0 - 0.25) * r, ink, w + grow)
		_:
			ci.draw_circle(c, r * 0.4, col)


static func _filled(ci: CanvasItem, pts: PackedVector2Array, col: Color, outline: Color) -> void:
	var closed := pts.duplicate()
	closed.append(pts[0])
	ci.draw_colored_polygon(pts, col)
	ci.draw_polyline(closed, outline, maxf(2.0, _outline_w), true)
