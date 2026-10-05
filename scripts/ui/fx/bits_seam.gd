class_name BitsSeam
extends RefCounted
## ART-2 2C: the one place the combat FX pick how a BitPath's bits are drawn (ART_BIBLE v2
## §6.3). Group 1's 1B material kit brings the pooled binary-bits emitter (GPUParticles2D
## with the Bezier process shader); until it is merged on main the bits are drawn here as
## glyphs (the bible's CPU fallback: Share Tech Mono 0/1/+ with a dark rim, a white-hot
## core for their first `hot` s and one faint trail copy). Switching to the kit's emitter
## is an edit to this file only. View only: it draws, it never reads a particle back.

## A bit's rim (the bible's dark rim at 95 %), its outline width as a share of its size
## (~1/22 thickens the thin face), and the trail copy: its alpha and how far behind (s).
const RIM_ALPHA := 0.95
const OUTLINE_SHARE := 1.0 / 22.0
const RIM_PX := 3
const TRAIL_ALPHA := 0.28
const TRAIL_LAG := 0.035
## A bit's smallest drawn lettering (px).
const MIN_PX := 6


## Draws `path` on `ci` at `t` s from its start in `color` (global points shifted by
## `origin`, the canvas item's global position), white-hot for its first `hot` s; `trail`
## draws the faint copy behind each moving bit; `dim` scales every alpha.
static func draw(ci: CanvasItem, path: BitPath, t: float, color: Color, origin: Vector2, hot: float = 0.1, trail: bool = true, dim: float = 1.0) -> void:
	if path == null:
		return
	var font := Palette.mono()
	for i in path.bits.size():
		var s := path.sample(i, t, hot)
		if not bool(s["shown"]):
			continue
		var b: Dictionary = path.bits[i]
		var px := maxi(MIN_PX, roundi(float(b["size"]) * float(s["scale"])))
		var glyph: String = BitPath.GLYPHS[int(b["glyph"])]
		var a := float(s["alpha"]) * dim
		var col := color.lerp(Palette.PAPER, float(s["hot"]))
		var at: Vector2 = (s["at"] as Vector2) - origin
		if trail and t > float(b["appear"]) + TRAIL_LAG:
			var back := path.sample(i, t - TRAIL_LAG, hot)
			if bool(back["shown"]):
				_glyph(ci, font, (back["at"] as Vector2) - origin, glyph, px, Color(color, a * TRAIL_ALPHA), false)
		_glyph(ci, font, at, glyph, px, Color(col, a), true)


static func _glyph(ci: CanvasItem, font: Font, at: Vector2, glyph: String, px: int, col: Color, rim: bool) -> void:
	var base := at + Vector2(-px * 0.3, px * 0.35)
	if rim:
		ci.draw_char_outline(font, base, glyph, px, maxi(RIM_PX, roundi(px * OUTLINE_SHARE) + RIM_PX - 1), Color(Palette.NIGHT_SKY, col.a * RIM_ALPHA))
	ci.draw_char(font, base, glyph, px, col)
