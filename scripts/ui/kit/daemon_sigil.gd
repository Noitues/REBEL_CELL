class_name DaemonSigil
extends RefCounted
## A unique drawn sigil per Daemon (until painted icons land in DaemonData.icon): built
## deterministically from the Daemon's id: an outer frame (hex, circle, diamond, shield),
## an inner motif (eye, fangs, spokes, loop, bars, bolt) and a rarity-coloured rim, in the
## Daemon's own hue. Two different ids never share frame + motif + hue.

const FRAMES := 4
const MOTIFS := 6
const HUES: Array[Color] = [Color("#B04DFF"), Color("#FF3DA8"), Color("#5CE1FF"), Color("#3DFF8B"), Color("#FFB000"), Color("#FF5A5A")]


static func _code(id: StringName) -> int:
	var h := 0
	for c in String(id):
		h = (h * 31 + c.unicode_at(0)) & 0xFFFFFF
	return h


static func color_of(id: StringName) -> Color:
	return HUES[_code(id) % HUES.size()]


## Draws `id`'s sigil centred on `c`, `r` = radius.
static func draw_sigil(ci: CanvasItem, c: Vector2, r: float, id: StringName, rarity: int = RC.Rarity.UNCOMMON) -> void:
	var code := _code(id)
	var col := color_of(id)
	var frame := (code / 7) % FRAMES
	var motif := (code / 29) % MOTIFS
	var pts := PackedVector2Array()
	match frame:
		0:
			for k in 7:
				pts.append(c + Vector2(cos(TAU * k / 6.0 + PI / 6.0), sin(TAU * k / 6.0 + PI / 6.0)) * r)
		1:
			for k in 25:
				pts.append(c + Vector2(cos(TAU * k / 24.0), sin(TAU * k / 24.0)) * r)
		2:
			pts = PackedVector2Array([c + Vector2(0, -r), c + Vector2(r, 0), c + Vector2(0, r), c + Vector2(-r, 0), c + Vector2(0, -r)])
		_:
			pts = PackedVector2Array([c + Vector2(-r * 0.85, -r * 0.8), c + Vector2(r * 0.85, -r * 0.8), c + Vector2(r * 0.85, r * 0.1), c + Vector2(0, r), c + Vector2(-r * 0.85, r * 0.1), c + Vector2(-r * 0.85, -r * 0.8)])
	var fill := pts.duplicate()
	fill.remove_at(fill.size() - 1)
	ci.draw_colored_polygon(fill, Color(Palette.NIGHT_SKY, 0.95))
	ci.draw_colored_polygon(fill, Color(col, 0.15))
	var rim: Color = [Color("#C9CED8"), col, Palette.RESIST_GOLD, Palette.CELL_PINK][clampi(rarity, 0, 3)]
	ci.draw_polyline(pts, Color(rim, 0.3), 5.0, true)
	ci.draw_polyline(pts, rim, 1.8, true)
	var m := r * 0.55
	var w := maxf(1.5, r * 0.12)
	match motif:
		0:  # eye
			ci.draw_arc(c + Vector2(0, m * 0.5), m, PI * 1.15, PI * 1.85, 12, col, w)
			ci.draw_arc(c - Vector2(0, m * 0.5), m, PI * 0.15, PI * 0.85, 12, col, w)
			ci.draw_circle(c, m * 0.3, col)
		1:  # fangs
			ci.draw_line(c + Vector2(-m, -m * 0.4), c + Vector2(m, -m * 0.4), col, w)
			for sx in [-0.45, 0.45]:
				ci.draw_colored_polygon(PackedVector2Array([c + Vector2(m * sx - m * 0.22, -m * 0.4), c + Vector2(m * sx + m * 0.22, -m * 0.4), c + Vector2(m * sx, m * 0.7)]), col)
		2:  # spokes
			for k in 6:
				var a := TAU * k / 6.0
				ci.draw_line(c + Vector2(cos(a), sin(a)) * m * 0.3, c + Vector2(cos(a), sin(a)) * m, col, w)
			ci.draw_circle(c, m * 0.22, col)
		3:  # loop
			ci.draw_arc(c, m * 0.75, 0.4, TAU - 0.2, 20, col, w)
			ci.draw_colored_polygon(PackedVector2Array([c + Vector2(m * 0.75, -m * 0.1), c + Vector2(m * 1.05, m * 0.35), c + Vector2(m * 0.4, m * 0.35)]), col)
		4:  # bars
			for k in 3:
				var hgt := m * (0.6 + k * 0.4)
				ci.draw_rect(Rect2(c + Vector2(-m * 0.8 + k * m * 0.6, m * 0.7 - hgt), Vector2(m * 0.4, hgt)), col)
		_:  # bolt
			ci.draw_colored_polygon(PackedVector2Array([c + Vector2(m * 0.2, -m), c + Vector2(-m * 0.5, m * 0.1), c + Vector2(0, m * 0.1), c + Vector2(-m * 0.2, m), c + Vector2(m * 0.5, -m * 0.1), c + Vector2(0, -m * 0.1)]), col)
