class_name AttachStyle
extends RefCounted
## The one place the wheel attachments (satellites and drones, firmware sockets, the card-play
## preview, the Daemon rack) pick their tokens, glyphs and faces (ART-2 2B). Group 1 lands palette
## v2 (1A), the material kit (1B) and the glyph atlas (1C) in parallel: switching to them is an
## edit here, not in every piece. View only.

## Master units of the round 41 stack (ART_BIBLE v2 §3.21) per rim radius: the slices end at 360.
const MASTER_RIM := 360.0
## The frame's outer edge (master 414) and the needle band's tip (master 510).
const MASTER_FRAME := 414.0


## Rarity colour (§2.7): common cool white, uncommon cyan, rare gold; a boss part in Cell pink.
static func rarity_color(rarity: int) -> Color:
	match rarity:
		RC.Rarity.UNCOMMON:
			return Palette.NET_CYAN
		RC.Rarity.RARE:
			return Palette.RESIST_GOLD
		RC.Rarity.BOSS:
			return Palette.CELL_PINK
	return Palette.TEXT_HI


## Rarity pips (§2.7): 1, 2, 3 (a boss part shows 3).
static func rarity_pips(rarity: int) -> int:
	return clampi(rarity + 1, 1, 3)


## A wheel's frame colour (§3.11 ownership tint): the Cell's pink, else the enemy's corporation.
static func owner_color(c: CombatantState, lookup: ContentLookup) -> Color:
	if c == null or c.is_player:
		return Palette.CELL_PINK
	var data := lookup.get_content(c.source_id) as EnemyData if lookup != null else null
	return Palette.corp_color(data.corporation_id) if data != null and data.corporation_id != &"" else Palette.RESIST_GOLD


## The dark glass every plate and disc sits on.
static func glass(alpha: float = 0.92) -> Color:
	return Color(Palette.NIGHT_SKY, alpha)


## The cream of blades and ghost blades (§3.2).
static func cream() -> Color:
	return Palette.PAPER


## A slice program's colour (§2.3).
static func slice_color(type: int) -> Color:
	return Palette.slice_color(type)


## A slice glyph (white glyph on the screens, §3.4): SliceIcon until 1C's atlas lands.
static func draw_slice_glyph(ci: CanvasItem, at: Vector2, r: float, type: int) -> void:
	SliceIcon.draw_icon(ci, at, r, type, Palette.TEXT_HI)


## The value face (big numbers) and the terminal face (labels, tabs).
static func value_font() -> Font:
	return Palette.display()


static func label_font() -> Font:
	return Palette.mono()


## A centred string: `size` px, its middle on `at`.
static func draw_centred(ci: CanvasItem, font: Font, at: Vector2, text: String, size: int, col: Color, outline: int = 0) -> void:
	var w := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	var base := at + Vector2(-w * 0.5, size * 0.36)
	if outline > 0:
		ci.draw_string_outline(font, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, outline, Color(Palette.INK, col.a))
	ci.draw_string(font, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)


## A dashed polyline (ghosts, waiting rings): `dash` px on, `gap` px off.
static func draw_dashed(ci: CanvasItem, pts: PackedVector2Array, col: Color, width: float, dash: float, gap: float) -> void:
	var on := true
	var left := dash
	for i in range(pts.size() - 1):
		var a := pts[i]
		var b := pts[i + 1]
		var seg := a.distance_to(b)
		var t := 0.0
		while t < seg - 0.001:
			var step := minf(left, seg - t)
			if on:
				ci.draw_line(a.lerp(b, t / seg), a.lerp(b, (t + step) / seg), col, width, true)
			t += step
			left -= step
			if left <= 0.001:
				on = not on
				left = dash if on else gap


## Points of an arc (centre, radius, from, to, steps).
static func arc_points(c: Vector2, r: float, a0: float, a1: float, steps: int) -> PackedVector2Array:
	var out := PackedVector2Array()
	for k in steps + 1:
		var a := lerpf(a0, a1, float(k) / steps)
		out.append(c + Vector2(cos(a), sin(a)) * r)
	return out


## An annular sector polygon (the slice wedge, a band).
static func sector(c: Vector2, r0: float, r1: float, a0: float, a1: float, steps: int = 12) -> PackedVector2Array:
	var out := arc_points(c, r1, a0, a1, steps)
	var inner := arc_points(c, r0, a1, a0, steps)
	out.append_array(inner)
	return out


## The effect glyph of firmware `id` (§3.9, 18 glyphs, never a slice glyph), drawn upright in `r`.
## Drawn shapes until 1C's atlas carries them.
static func draw_firmware_glyph(ci: CanvasItem, id: StringName, at: Vector2, r: float, col: Color) -> void:
	var w := maxf(1.2, r * 0.18)
	match id:
		&"patch_plus":  # double plus
			for dx in [-0.42, 0.42]:
				var c := at + Vector2(r * dx, 0)
				ci.draw_line(c + Vector2(-r * 0.32, 0), c + Vector2(r * 0.32, 0), col, w)
				ci.draw_line(c + Vector2(0, -r * 0.32), c + Vector2(0, r * 0.32), col, w)
		&"hardened":  # armoured hex with ***
			ci.draw_polyline(_poly(at, r * 0.8, 6, PI / 6.0), col, w)
			for k in 3:
				ci.draw_circle(at + Vector2((k - 1) * r * 0.32, 0), w * 0.6, col)
		&"burner":  # gas ring
			ci.draw_arc(at, r * 0.62, 0, TAU, 16, col, w)
			for k in 6:
				var a := TAU * k / 6.0
				ci.draw_line(at + Vector2(cos(a), sin(a)) * r * 0.62, at + Vector2(cos(a), sin(a)) * r * 0.9, col, w * 0.8)
		&"leech":  # fanged drop
			ci.draw_colored_polygon(PackedVector2Array([at + Vector2(0, -r * 0.85), at + Vector2(r * 0.55, r * 0.2), at + Vector2(0, r * 0.75), at + Vector2(-r * 0.55, r * 0.2)]), col)
			ci.draw_colored_polygon(PackedVector2Array([at + Vector2(-r * 0.25, 0), at + Vector2(-r * 0.05, 0), at + Vector2(-r * 0.15, r * 0.4)]), Palette.NIGHT_SKY)
			ci.draw_colored_polygon(PackedVector2Array([at + Vector2(r * 0.05, 0), at + Vector2(r * 0.25, 0), at + Vector2(r * 0.15, r * 0.4)]), Palette.NIGHT_SKY)
		&"mirror":  # |>|<|
			ci.draw_colored_polygon(PackedVector2Array([at + Vector2(-r * 0.8, -r * 0.5), at + Vector2(-r * 0.12, 0), at + Vector2(-r * 0.8, r * 0.5)]), col)
			ci.draw_colored_polygon(PackedVector2Array([at + Vector2(r * 0.8, -r * 0.5), at + Vector2(r * 0.12, 0), at + Vector2(r * 0.8, r * 0.5)]), col)
			ci.draw_line(at + Vector2(0, -r * 0.7), at + Vector2(0, r * 0.7), col, w * 0.7)
		&"shunt":  # fork with two arrowheads
			ci.draw_line(at + Vector2(0, r * 0.8), at + Vector2(0, 0), col, w)
			for sx in [-1.0, 1.0]:
				var tip := at + Vector2(sx * r * 0.6, -r * 0.7)
				ci.draw_line(at, tip, col, w)
				ci.draw_colored_polygon(PackedVector2Array([tip + Vector2(0, -r * 0.18), tip + Vector2(sx * r * 0.2, r * 0.1), tip + Vector2(-sx * r * 0.14, r * 0.12)]), col)
		&"overvolt":  # bolt
			ci.draw_colored_polygon(PackedVector2Array([at + Vector2(r * 0.2, -r * 0.9), at + Vector2(-r * 0.45, r * 0.1), at + Vector2(-r * 0.02, r * 0.1), at + Vector2(-r * 0.2, r * 0.9), at + Vector2(r * 0.45, -r * 0.12), at + Vector2(r * 0.02, -r * 0.12)]), col)
		&"bulkhead":  # blast door
			ci.draw_rect(Rect2(at - Vector2(r * 0.7, r * 0.7), Vector2(r * 1.4, r * 1.4)), col, false, w)
			for k in 3:
				var y := (k - 1) * r * 0.36
				ci.draw_line(at + Vector2(-r * 0.6, y - r * 0.2), at + Vector2(r * 0.6, y + r * 0.2), col, w * 0.8)
		&"siphon":  # pipe
			ci.draw_polyline(PackedVector2Array([at + Vector2(-r * 0.8, -r * 0.5), at + Vector2(r * 0.3, -r * 0.5), at + Vector2(r * 0.3, r * 0.6), at + Vector2(r * 0.8, r * 0.6)]), col, w * 1.4)
		&"static_coat":  # zig-zag shield
			ci.draw_polyline(PackedVector2Array([at + Vector2(-r * 0.7, -r * 0.7), at + Vector2(r * 0.7, -r * 0.7), at + Vector2(r * 0.7, 0), at + Vector2(0, r * 0.85), at + Vector2(-r * 0.7, 0), at + Vector2(-r * 0.7, -r * 0.7)]), col, w)
			ci.draw_polyline(PackedVector2Array([at + Vector2(-r * 0.4, -r * 0.1), at + Vector2(-r * 0.15, -r * 0.35), at + Vector2(r * 0.1, -r * 0.05), at + Vector2(r * 0.4, -r * 0.3)]), col, w * 0.8)
		&"barbed_wire":
			ci.draw_line(at + Vector2(-r * 0.85, 0), at + Vector2(r * 0.85, 0), col, w)
			for k in 3:
				var c := at + Vector2((k - 1) * r * 0.55, 0)
				ci.draw_line(c + Vector2(-r * 0.18, -r * 0.3), c + Vector2(r * 0.18, r * 0.3), col, w * 0.8)
				ci.draw_line(c + Vector2(-r * 0.18, r * 0.3), c + Vector2(r * 0.18, -r * 0.3), col, w * 0.8)
		&"recycler":  # three-arrow triangle
			var tri := _poly(at, r * 0.75, 3, -PI / 2.0)
			ci.draw_polyline(tri, col, w)
			for k in 3:
				ci.draw_circle(tri[k], w, col)
		&"counterstrike":  # <=>
			ci.draw_line(at + Vector2(-r * 0.7, -r * 0.25), at + Vector2(r * 0.7, -r * 0.25), col, w)
			ci.draw_line(at + Vector2(-r * 0.7, r * 0.25), at + Vector2(r * 0.7, r * 0.25), col, w)
			ci.draw_colored_polygon(PackedVector2Array([at + Vector2(r * 0.9, -r * 0.25), at + Vector2(r * 0.55, -r * 0.5), at + Vector2(r * 0.55, 0)]), col)
			ci.draw_colored_polygon(PackedVector2Array([at + Vector2(-r * 0.9, r * 0.25), at + Vector2(-r * 0.55, 0), at + Vector2(-r * 0.55, r * 0.5)]), col)
		&"nanite_mesh":  # hex cluster
			for k in 3:
				var a := TAU * k / 3.0 - PI / 2.0
				ci.draw_polyline(_poly(at + Vector2(cos(a), sin(a)) * r * 0.38, r * 0.34, 6, PI / 6.0), col, w * 0.8)
		&"power_cell":  # battery
			ci.draw_rect(Rect2(at - Vector2(r * 0.42, r * 0.7), Vector2(r * 0.84, r * 1.4)), col, false, w)
			ci.draw_rect(Rect2(at - Vector2(r * 0.18, r * 0.88), Vector2(r * 0.36, r * 0.18)), col)
			ci.draw_rect(Rect2(at - Vector2(r * 0.26, -r * 0.05), Vector2(r * 0.52, r * 0.5)), col)
		&"tracer":  # round
			ci.draw_colored_polygon(PackedVector2Array([at + Vector2(-r * 0.3, r * 0.8), at + Vector2(-r * 0.3, -r * 0.3), at + Vector2(0, -r * 0.85), at + Vector2(r * 0.3, -r * 0.3), at + Vector2(r * 0.3, r * 0.8)]), col)
		&"skimmer":  # coin stack
			for k in 3:
				var c := at + Vector2(0, (1 - k) * r * 0.4)
				ci.draw_rect(Rect2(c - Vector2(r * 0.6, r * 0.14), Vector2(r * 1.2, r * 0.28)), col, false, w * 0.8)
		&"coolant_loop":  # radiator coil
			var pts := PackedVector2Array()
			for k in 7:
				pts.append(at + Vector2(-r * 0.75 + k * r * 0.25, (r * 0.55) * (1.0 if k % 2 == 0 else -1.0)))
			ci.draw_polyline(pts, col, w)
		_:
			ci.draw_rect(Rect2(at - Vector2(r * 0.4, r * 0.4), Vector2(r * 0.8, r * 0.8)), col, false, w)


static func _poly(c: Vector2, r: float, n: int, rot: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	for k in n + 1:
		var a := rot + TAU * k / n
		out.append(c + Vector2(cos(a), sin(a)) * r)
	return out
