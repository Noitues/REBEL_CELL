class_name WheelBezel
extends RefCounted
## Wheel hardware (ART_BIBLE §6.1): who owns a wheel is told by its bezel, never by its
## position or its slice colours.
## - The operative's bezel is scratched metal with torn PAPER stickers and a CELL_PINK rim;
##   its Polaroid mini-portrait is inset at the top of the hub.
## - An enemy's bezel is machined in its corporation's hue, filled with the corporation's
##   pattern (CorpPattern, §3.6) and notched all round (a hostile, saw-toothed edge); its
##   portrait hangs above the bezel.
## Both read in greyscale: paper patches and a smooth rim against teeth and a pattern.
## A look is a Dictionary ({owner, ...}, see operative_look / enemy_look); every mark is
## built as geometry first (`marks`), so the tests compare looks without a renderer.
## View only: static painters, decoration from hashes, never game randomness.

enum Owner { OPERATIVE, ENEMY }

## The bezel's width outside the slice band (px at every text scale: it is hardware).
const BEZEL_W := 26.0
## The rim line (px) and the inner hairline.
const RIM_W := 3.0
const HAIRLINE_W := 1.0
## Operative stickers: how many torn paper patches, their span (rad), inset from the
## bezel's edges (px), the share of their ends that is torn, and scratches on each.
const STICKERS := 5
const STICKER_SPAN := 0.42
const STICKER_INSET := 3.0
const STICKER_TEAR := 0.16
const STICKER_SCRATCHES := 3
## A sticker's paper alpha (the metal shows through a little) and its scratches' ink alpha.
const STICKER_ALPHA := 0.9
const SCRATCH_ALPHA := 0.4
## Metal base alpha, the enemy's hue wash over it and its pattern's strength.
const BASE_ALPHA := 0.95
const HUE_WASH := 0.22
const PATTERN_ALPHA := 0.55
## Enemy notches: teeth round the outer edge, their depth (px).
const NOTCHES := 36
const NOTCH_DEPTH := 6.0
## Arc smoothness for rings drawn as polylines.
const RING_SEGMENTS := 96
## The Polaroid inset (operative): its size and centre as shares of the hub radius, its
## frame (share of its side), its tilt (rad) and its tape strip (shares of its side).
const INSET_SIZE := 0.5
const INSET_Y := 0.52
const INSET_FRAME := 0.1
const INSET_TILT := -0.07
const INSET_TAPE := Vector2(0.5, 0.14)
## The enemy's portrait badge above the bezel: its side (px at 1.0), the gap to the needle
## reach below it and to the tag above.
const BADGE_SIDE := 30.0
const BADGE_GAP := 3.0
## Hub pattern alpha (a texture behind the hub's words, never over them).
const HUB_PATTERN_ALPHA := 0.16


## §7.1 class identity: each class's bezel ornament, hub pattern and hub glyph (no two
## classes share any of the three). An unknown class gets PLAIN (no ornament).
const PLAIN := &"plain"
const ORNAMENTS := {&"breaker": &"rivets", &"wrecker": &"welded", &"ghost": &"flicker", &"phantom": &"double_rim",
	&"rigger": &"cables", &"overclocker": &"fins", &"botnet": &"orbit_dots", &"hivemind": &"hex_lattice"}
const HUB_PATTERNS := {&"breaker": &"plates", &"wrecker": &"scorch", &"ghost": &"scanlines", &"phantom": &"echo_rings",
	&"rigger": &"grid", &"overclocker": &"rays", &"botnet": &"dot_grid", &"hivemind": &"hex_cells"}
const HUB_GLYPHS := {&"breaker": &"crowbar", &"wrecker": &"visor", &"ghost": &"hood", &"phantom": &"mask",
	&"rigger": &"goggles", &"overclocker": &"chip", &"botnet": &"drone", &"hivemind": &"nodes"}
## Ornaments that move (T0, `bezel_ambient`): the Ghost's flicker, the Botnet's orbit.
const AMBIENT_ORNAMENTS: Array[StringName] = [&"flicker", &"orbit_dots"]


## The operative's look: a PAPER-stickered bezel, CELL_PINK rim, and the class's own
## ornament, hub pattern and glyph in its accent (§7.1).
static func operative_look(class_id: StringName) -> Dictionary:
	return {"owner": Owner.OPERATIVE, "class_id": class_id, "rim": Palette.CELL_PINK, "accent": Palette.class_accent(class_id),
		"pattern": CorpPattern.Kind.NONE, "ornament": ORNAMENTS.get(class_id, PLAIN), "hub_pattern": HUB_PATTERNS.get(class_id, PLAIN),
		"hub_glyph": HUB_GLYPHS.get(class_id, PLAIN)}


## True when `look`'s ornament moves (it needs the ambient clock).
static func is_ambient(look: Dictionary) -> bool:
	return AMBIENT_ORNAMENTS.has(StringName(look.get("ornament", PLAIN)))


## An enemy's look: a machined bezel in `corporation_id`'s hue with its pattern, notched.
static func enemy_look(corporation_id: StringName, is_boss: bool = false) -> Dictionary:
	return {"owner": Owner.ENEMY, "corp": corporation_id, "rim": Palette.corp_color(corporation_id), "accent": Palette.corp_color(corporation_id),
		"pattern": Palette.corp_pattern_id(corporation_id), "boss": is_boss}


## The owner of `look` (Owner).
static func owner_of(look: Dictionary) -> int:
	return int(look.get("owner", Owner.ENEMY))


## Draws the bezel ring of `look` between `r0` and `r1` round `c` on `ci`. `hc` (high
## contrast) makes the metal opaque and the rim thicker.
static func draw_bezel(ci: CanvasItem, c: Vector2, r0: float, r1: float, look: Dictionary, hc: bool = false) -> void:
	var mid := (r0 + r1) * 0.5
	var w := r1 - r0
	ci.draw_arc(c, mid, 0.0, TAU, RING_SEGMENTS, Color(Palette.NIGHT_BLOCK, 1.0 if hc else BASE_ALPHA), w, true)
	var rim: Color = look.get("rim", Palette.TEXT_MID)
	var rim_w := RIM_W * (2.0 if hc else 1.0)
	if owner_of(look) == Owner.OPERATIVE:
		for s in sticker_polys(c, r0, r1):
			ci.draw_colored_polygon(s, Color(Palette.PAPER, 1.0 if hc else STICKER_ALPHA))
		for line in scratch_lines(c, r0, r1):
			ci.draw_polyline(line, Color(Palette.INK, SCRATCH_ALPHA), 1.0, true)
		ci.draw_arc(c, r1 - rim_w * 0.5, 0.0, TAU, RING_SEGMENTS, rim, rim_w, true)
	else:
		ci.draw_arc(c, mid, 0.0, TAU, RING_SEGMENTS, Color(rim, HUE_WASH), w, true)
		CorpPattern.fill_ring(ci, c, r0 + HAIRLINE_W, r1 - NOTCH_DEPTH, int(look.get("pattern", CorpPattern.Kind.NONE)), Color(rim, PATTERN_ALPHA))
		# The hostile edge: dark notches cut into the rim, the toothed outline in the hue.
		for tri in notch_cuts(c, r1):
			ci.draw_colored_polygon(tri, Palette.NIGHT_SKY)
		ci.draw_polyline(notch_outline(c, r1), rim, rim_w * 0.8, true)
	ci.draw_arc(c, r0 + HAIRLINE_W * 0.5, 0.0, TAU, RING_SEGMENTS, Color(rim, 0.6), HAIRLINE_W, true)


## The operative's torn paper stickers on the bezel (polygons).
static func sticker_polys(c: Vector2, r0: float, r1: float) -> Array[PackedVector2Array]:
	var out: Array[PackedVector2Array] = []
	var a_in := r0 + STICKER_INSET
	var a_out := r1 - STICKER_INSET - RIM_W
	for k in STICKERS:
		var a0 := TAU * (k + _h(k, 1) * 0.5) / STICKERS
		var span := STICKER_SPAN * (0.7 + 0.6 * _h(k, 2))
		var pts := PackedVector2Array()
		var steps := 8
		for i in steps + 1:
			var a := a0 + span * i / steps
			pts.append(c + Vector2.from_angle(a) * a_out)
		# The torn end: a jagged edge back to the inner side.
		for i in 3:
			var tear := span * STICKER_TEAR * _h(k, 10 + i)
			var rr := lerpf(a_out, a_in, (i + 1) / 4.0)
			pts.append(c + Vector2.from_angle(a0 + span - tear) * rr)
		for i in range(steps, -1, -1):
			var a := a0 + span * i / steps
			pts.append(c + Vector2.from_angle(a) * a_in)
		for i in 3:
			var tear := span * STICKER_TEAR * _h(k, 20 + i)
			var rr := lerpf(a_in, a_out, (i + 1) / 4.0)
			pts.append(c + Vector2.from_angle(a0 + tear) * rr)
		out.append(pts)
	return out


## Scratch lines across the stickers (short chords, ink).
static func scratch_lines(c: Vector2, r0: float, r1: float) -> Array[PackedVector2Array]:
	var out: Array[PackedVector2Array] = []
	for k in STICKERS:
		var a0 := TAU * (k + _h(k, 1) * 0.5) / STICKERS
		var span := STICKER_SPAN * (0.7 + 0.6 * _h(k, 2))
		for s in STICKER_SCRATCHES:
			var a := a0 + span * (0.2 + 0.6 * _h(k, 30 + s))
			var d := span * 0.12
			out.append(PackedVector2Array([c + Vector2.from_angle(a - d) * lerpf(r0, r1, 0.35 + 0.2 * _h(k, 40 + s)),
				c + Vector2.from_angle(a + d) * lerpf(r0, r1, 0.55 + 0.2 * _h(k, 50 + s))]))
	return out


## The enemy's toothed outer edge (a closed polyline): NOTCHES teeth NOTCH_DEPTH deep.
static func notch_outline(c: Vector2, r1: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for k in NOTCHES:
		var a := TAU * k / NOTCHES
		var half := TAU / NOTCHES * 0.5
		pts.append(c + Vector2.from_angle(a) * r1)
		pts.append(c + Vector2.from_angle(a + half * 0.5) * r1)
		pts.append(c + Vector2.from_angle(a + half) * (r1 - NOTCH_DEPTH))
		pts.append(c + Vector2.from_angle(a + half * 1.5) * r1)
	pts.append(pts[0])
	return pts


## The notches cut out of the enemy's rim (triangles, drawn dark).
static func notch_cuts(c: Vector2, r1: float) -> Array[PackedVector2Array]:
	var out: Array[PackedVector2Array] = []
	for k in NOTCHES:
		var a := TAU * k / NOTCHES
		var half := TAU / NOTCHES * 0.5
		out.append(PackedVector2Array([c + Vector2.from_angle(a + half * 0.5) * (r1 + 0.5), c + Vector2.from_angle(a + half) * (r1 - NOTCH_DEPTH),
			c + Vector2.from_angle(a + half * 1.5) * (r1 + 0.5)]))
	return out


## The enemy's hub: its corporation's pattern, faint, behind the hub's words.
static func draw_hub_pattern(ci: CanvasItem, c: Vector2, r: float, look: Dictionary) -> void:
	if owner_of(look) != Owner.ENEMY:
		return
	var kind := int(look.get("pattern", CorpPattern.Kind.NONE))
	CorpPattern.fill_ring(ci, c, 0.0, r, kind, Color(look.get("rim", Palette.TEXT_MID), HUB_PATTERN_ALPHA))


## Where the operative's Polaroid inset sits in a hub of radius `hub_r` centred on `c`
## (unrotated rect).
static func inset_rect(c: Vector2, hub_r: float) -> Rect2:
	var side := hub_r * INSET_SIZE
	var at := c + Vector2(0.0, -hub_r * INSET_Y)
	return Rect2(at - Vector2(side, side) * 0.5, Vector2(side, side))


## Draws a Polaroid mini-portrait in `rect` (a paper frame, the portrait, a strip of tape),
## tilted by INSET_TILT: `texture` when given (final art, W5), else PortraitArt of `subject`.
static func draw_inset(ci: CanvasItem, rect: Rect2, subject: Dictionary, texture: Texture2D = null, alpha: float = 1.0) -> void:
	var c := rect.get_center()
	ci.draw_set_transform(c, INSET_TILT, Vector2.ONE)
	var r := Rect2(rect.position - c, rect.size)
	ci.draw_rect(Rect2(r.position + Vector2(2, 2), r.size), Color(Palette.SHADOW, Palette.SHADOW.a * alpha))
	ci.draw_rect(r, Color(Palette.PAPER, alpha))
	var pad := r.size.x * INSET_FRAME
	var image := Rect2(r.position + Vector2(pad, pad), r.size - Vector2(pad, pad) * 2.0)
	if texture != null:
		ci.draw_texture_rect(texture, image, false, Color(Color.WHITE, alpha))
	elif not subject.is_empty() and alpha >= 1.0:
		PortraitArt.draw(ci, image, subject)
	else:
		ci.draw_rect(image, Color(Palette.NIGHT_BLOCK, alpha))
	ci.draw_rect(r, Color(Palette.INK, 0.6 * alpha), false, 1.0)
	var tape := Vector2(r.size.x * INSET_TAPE.x, r.size.y * INSET_TAPE.y)
	ci.draw_rect(Rect2(Vector2(-tape.x * 0.5, r.position.y - tape.y * 0.5), tape), Color(Palette.NOTE_TAPE, Palette.NOTE_TAPE.a * alpha))
	ci.draw_set_transform(Vector2.ZERO)


## Draws an enemy's portrait badge (a machined square frame in its hue) in `rect`.
static func draw_badge(ci: CanvasItem, rect: Rect2, subject: Dictionary, look: Dictionary, texture: Texture2D = null) -> void:
	var rim: Color = look.get("rim", Palette.TEXT_MID)
	ci.draw_rect(rect.grow(2.0), Palette.NIGHT_SKY)
	if texture != null:
		ci.draw_texture_rect(texture, rect, false)
	else:
		PortraitArt.draw(ci, rect, subject)
	ci.draw_rect(rect.grow(1.0), rim, false, 2.0)
	# Two notches on its lower edge: the same hostile cut as the bezel.
	for sx: float in [-0.25, 0.25]:
		var x: float = rect.get_center().x + rect.size.x * sx
		ci.draw_colored_polygon(PackedVector2Array([Vector2(x - 3.0, rect.end.y + 2.0), Vector2(x, rect.end.y - 2.0), Vector2(x + 3.0, rect.end.y + 2.0)]), Palette.NIGHT_SKY)


# --- §7.1 class identity: ornaments, hub patterns, hub glyphs ---------------------------------
# Every mark is built as geometry ({lines, dots, polys, width, alpha}) and drawn by
# draw_marks, so a test can tell the eight classes apart without a renderer.

## Ornament geometry (px at every text scale; hardware): rivet plates, weld bead and dents,
## flicker dashes, afterimage offsets, cable wraps, heat-sink fins, orbit dots, hex cells.
const RIVET_PLATES := 8
const RIVET_R := 2.2
const WELD_ZIGS := 72
const WELD_AMP := 2.5
const DENTS := 5
const DENT_DEPTH := 4.0
const DENT_SPAN := 0.26
const FLICKER_DASHES := 24
const FLICKER_OUT := 3.0
const AFTERIMAGE_STEP := Vector2(3.0, -2.0)
const AFTERIMAGES := 2
const CABLE_WRAPS := 9
const CABLE_AMP := 4.0
const FINS := 16
const FIN_LEN := 7.0
const FIN_W := 3.0
const ORBIT_DOTS := 12
const ORBIT_OUT := 6.0
const ORBIT_DOT_R := 2.5
const HEX_RING := 36
const HEX_R := 4.6
const ORNAMENT_W := 2.0
## Hub pattern spacing (px) and marks.
const HUB_STEP := 9.0
const HUB_CRACKS := 7
const HUB_RAYS := 16
const HUB_DOT_R := 1.3
## The glyph badge on the inset's corner: its radius as a share of the inset's side.
const GLYPH_BADGE := 0.24
const MARK_SEGMENTS := 48


## The class ornament of `look` round the bezel `r0`..`r1` at `c` (empty for an enemy or a
## plain class). `phase` (0..1) is the ambient clock (0 = rest: reduce effects, headless).
static func ornament_marks(look: Dictionary, c: Vector2, r0: float, r1: float, phase: float = 0.0) -> Dictionary:
	var m := _marks()
	if owner_of(look) != Owner.OPERATIVE:
		return m
	match StringName(look.get("ornament", PLAIN)):
		&"rivets":
			for k in RIVET_PLATES:
				var a := TAU * k / RIVET_PLATES
				m.lines.append(PackedVector2Array([c + Vector2.from_angle(a) * r0, c + Vector2.from_angle(a) * (r1 - RIM_W)]))
				for side: float in [-1.0, 1.0]:
					var da := side * 0.06
					m.dots.append(Vector3(c.x + cos(a + da) * (r0 + 5.0), c.y + sin(a + da) * (r0 + 5.0), RIVET_R))
					m.dots.append(Vector3(c.x + cos(a + da) * (r1 - 7.0), c.y + sin(a + da) * (r1 - 7.0), RIVET_R))
		&"welded":
			var bead := PackedVector2Array()
			for k in WELD_ZIGS + 1:
				var a := TAU * k / WELD_ZIGS
				bead.append(c + Vector2.from_angle(a) * (r1 - RIM_W - 3.0 + (WELD_AMP if k % 2 == 0 else -WELD_AMP)))
			m.lines.append(bead)
			for k in DENTS:
				var a0 := TAU * (k + _h(k, 60)) / DENTS
				var dent := PackedVector2Array()
				for i in 9:
					var t := i / 8.0
					dent.append(c + Vector2.from_angle(a0 + DENT_SPAN * t) * (r1 + 1.0 - DENT_DEPTH * sin(PI * t)))
				m.lines.append(dent)
		&"flicker":
			m.alpha = 1.0 - clampf(_flicker(phase, float(look.get("flicker_depth", FLICKER_DEPTH))), 0.0, 1.0)
			for k in FLICKER_DASHES:
				var a := TAU * k / FLICKER_DASHES
				m.lines.append(_arc_pts(c, r1 + FLICKER_OUT, a, a + TAU / FLICKER_DASHES * 0.55, 6))
		&"double_rim":
			for k in range(1, AFTERIMAGES + 1):
				m.lines.append(_arc_pts(c + AFTERIMAGE_STEP * k, r1 + k * 2.0, 0.0, TAU, MARK_SEGMENTS))
		&"cables":
			for strand in 2:
				var pts := PackedVector2Array()
				for k in MARK_SEGMENTS * 2 + 1:
					var a := TAU * k / (MARK_SEGMENTS * 2)
					var w := sin(a * CABLE_WRAPS + strand * PI)
					pts.append(c + Vector2.from_angle(a) * (r1 - RIM_W - CABLE_AMP + CABLE_AMP * w))
				m.lines.append(pts)
		&"fins":
			for k in FINS:
				var a := TAU * (k + 0.5) / FINS
				var d := Vector2.from_angle(a)
				var n := d.orthogonal() * FIN_W * 0.5
				m.polys.append(PackedVector2Array([c + d * r1 + n, c + d * (r1 + FIN_LEN) + n, c + d * (r1 + FIN_LEN) - n, c + d * r1 - n]))
		&"orbit_dots":
			for k in ORBIT_DOTS:
				var a := TAU * (k + phase) / ORBIT_DOTS
				m.dots.append(Vector3(c.x + cos(a) * (r1 + ORBIT_OUT), c.y + sin(a) * (r1 + ORBIT_OUT), ORBIT_DOT_R * (1.0 if k % 3 == 0 else 0.6)))
		&"hex_lattice":
			for ring in 2:
				var rr := lerpf(r0 + HEX_R + 1.0, r1 - RIM_W - HEX_R, float(ring))
				for k in HEX_RING:
					var a := TAU * (k + ring * 0.5) / HEX_RING
					m.lines.append(_hex(c + Vector2.from_angle(a) * rr, HEX_R))
	return m


## The operative's hub pattern (§7.1) in a hub of radius `r` at `c`, clipped to it.
static func hub_marks(look: Dictionary, c: Vector2, r: float) -> Dictionary:
	var m := _marks()
	if owner_of(look) != Owner.OPERATIVE:
		return m
	var raw: Array[PackedVector2Array] = []
	match StringName(look.get("hub_pattern", PLAIN)):
		&"plates":
			var n := ceili(r * 2.0 / HUB_STEP) + 1
			for i in range(-n, n + 1):
				var o := c + Vector2(i * HUB_STEP, 0.0)
				raw.append(PackedVector2Array([o + Vector2(-r, -r), o + Vector2(r, r)]))
		&"scorch":
			for k in HUB_CRACKS:
				var a := TAU * (k + _h(k, 70)) / HUB_CRACKS
				var pts := PackedVector2Array([c + Vector2.from_angle(a) * r * 0.2])
				for i in range(1, 5):
					pts.append(c + Vector2.from_angle(a + (_h(k, 80 + i) - 0.5) * 0.4) * r * (0.2 + 0.8 * i / 4.0))
				raw.append(pts)
		&"scanlines":
			var y := -r
			while y <= r:
				raw.append(PackedVector2Array([c + Vector2(-r, y), c + Vector2(r, y)]))
				y += HUB_STEP * 0.6
		&"echo_rings":
			var rr := HUB_STEP
			while rr < r:
				m.lines.append(_arc_pts(c, rr, 0.0, TAU, MARK_SEGMENTS))
				rr += HUB_STEP
		&"grid":
			var t := -r
			while t <= r:
				raw.append(PackedVector2Array([c + Vector2(t, -r), c + Vector2(t, r)]))
				raw.append(PackedVector2Array([c + Vector2(-r, t), c + Vector2(r, t)]))
				t += HUB_STEP * 1.4
		&"rays":
			for k in HUB_RAYS:
				var a := TAU * k / HUB_RAYS
				m.lines.append(PackedVector2Array([c + Vector2.from_angle(a) * r * 0.25, c + Vector2.from_angle(a) * r * 0.95]))
		&"dot_grid":
			var t := -r
			while t <= r:
				var u := -r
				while u <= r:
					if Vector2(t, u).length() < r - HUB_DOT_R:
						m.dots.append(Vector3(c.x + t, c.y + u, HUB_DOT_R))
					u += HUB_STEP
				t += HUB_STEP
		&"hex_cells":
			var hs := HUB_STEP
			var row := 0
			var y := -r
			while y <= r:
				var x := -r + (hs * 0.87 if row % 2 == 1 else 0.0)
				while x <= r:
					if Vector2(x, y).length() < r - hs:
						m.lines.append(_hex(c + Vector2(x, y), hs * 0.95))
					x += hs * 1.74
				y += hs * 1.5
				row += 1
	var circle := _arc_pts(c, r, 0.0, TAU, MARK_SEGMENTS)
	for line in raw:
		for piece in Geometry2D.intersect_polyline_with_polygon(line, circle):
			m.lines.append(piece)
	return m


## The class glyph (§7.1) centred at `c`, `s` px in radius.
static func glyph_marks(glyph: StringName, c: Vector2, s: float) -> Dictionary:
	var m := _marks()
	match glyph:
		&"crowbar":
			m.lines.append(PackedVector2Array([c + Vector2(-0.2, 0.9) * s, c + Vector2(-0.2, -0.5) * s, c + Vector2(0.1, -0.85) * s, c + Vector2(0.5, -0.7) * s]))
			m.lines.append(PackedVector2Array([c + Vector2(-0.2, 0.9) * s, c + Vector2(-0.5, 0.75) * s]))
		&"visor":
			m.lines.append(PackedVector2Array([c + Vector2(-0.8, -0.5) * s, c + Vector2(0.8, -0.5) * s, c + Vector2(0.8, 0.5) * s, c + Vector2(-0.8, 0.5) * s, c + Vector2(-0.8, -0.5) * s]))
			m.polys.append(PackedVector2Array([c + Vector2(-0.55, -0.12) * s, c + Vector2(0.55, -0.12) * s, c + Vector2(0.55, 0.12) * s, c + Vector2(-0.55, 0.12) * s]))
		&"hood":
			m.lines.append(_arc_pts(c + Vector2(0, 0.2) * s, s * 0.8, PI, TAU, 16))
			for i in 3:
				m.lines.append(PackedVector2Array([c + Vector2(-0.5 + i * 0.5, -0.1) * s, c + Vector2(-0.5 + i * 0.5, 0.6) * s]))
		&"mask":
			m.lines.append(PackedVector2Array([c + Vector2(-0.85, -0.3) * s, c + Vector2(0, -0.6) * s, c + Vector2(0.85, -0.3) * s, c + Vector2(0.5, 0.7) * s, c + Vector2(-0.5, 0.7) * s, c + Vector2(-0.85, -0.3) * s]))
			for sx: float in [-1.0, 1.0]:
				m.polys.append(PackedVector2Array([c + Vector2(sx * 0.2, -0.1) * s, c + Vector2(sx * 0.55, -0.2) * s, c + Vector2(sx * 0.45, 0.05) * s]))
		&"goggles":
			for sx: float in [-1.0, 1.0]:
				m.lines.append(_arc_pts(c + Vector2(sx * 0.45, 0) * s, s * 0.35, 0.0, TAU, 16))
			m.lines.append(PackedVector2Array([c + Vector2(-0.1, 0) * s, c + Vector2(0.1, 0) * s]))
		&"chip":
			m.lines.append(PackedVector2Array([c + Vector2(-0.5, -0.5) * s, c + Vector2(0.5, -0.5) * s, c + Vector2(0.5, 0.5) * s, c + Vector2(-0.5, 0.5) * s, c + Vector2(-0.5, -0.5) * s]))
			for i in 3:
				var t := -0.3 + i * 0.3
				m.lines.append(PackedVector2Array([c + Vector2(t, -0.5) * s, c + Vector2(t, -0.85) * s]))
				m.lines.append(PackedVector2Array([c + Vector2(t, 0.5) * s, c + Vector2(t, 0.85) * s]))
		&"drone":
			m.lines.append(_arc_pts(c, s * 0.3, 0.0, TAU, 12))
			for k in 3:
				var a := TAU * k / 3.0 - PI * 0.5
				m.lines.append(PackedVector2Array([c + Vector2.from_angle(a) * s * 0.3, c + Vector2.from_angle(a) * s * 0.7]))
				m.dots.append(Vector3(c.x + cos(a) * s * 0.8, c.y + sin(a) * s * 0.8, s * 0.16))
		&"nodes":
			var pts: Array[Vector2] = [c + Vector2(0, -0.7) * s, c + Vector2(-0.7, 0.5) * s, c + Vector2(0.7, 0.5) * s]
			m.lines.append(PackedVector2Array([pts[0], pts[1], pts[2], pts[0]]))
			for p in pts:
				m.dots.append(Vector3(p.x, p.y, s * 0.2))
	return m


## Draws `marks` on `ci` in `col` (its alpha times the marks' own).
static func draw_marks(ci: CanvasItem, m: Dictionary, col: Color) -> void:
	var c := Color(col, col.a * float(m.get("alpha", 1.0)))
	if c.a <= 0.0:
		return
	var w := float(m.get("width", ORNAMENT_W))
	for line: PackedVector2Array in m.lines:
		if line.size() >= 2:
			ci.draw_polyline(line, c, w, true)
	for d: Vector3 in m.dots:
		ci.draw_circle(Vector2(d.x, d.y), d.z, c, true, -1.0, true)
	for poly: PackedVector2Array in m.polys:
		ci.draw_colored_polygon(poly, c)


## Draws the class ornament of `look` (see ornament_marks).
static func draw_ornament(ci: CanvasItem, c: Vector2, r0: float, r1: float, look: Dictionary, phase: float = 0.0) -> void:
	draw_marks(ci, ornament_marks(look, c, r0, r1, phase), look.get("accent", Palette.TEXT_MID))


## Draws the operative's hub pattern (see hub_marks), faint behind the hub's words.
static func draw_class_hub(ci: CanvasItem, c: Vector2, r: float, look: Dictionary) -> void:
	var m := hub_marks(look, c, r)
	m.width = 1.0
	draw_marks(ci, m, Color(look.get("accent", Palette.TEXT_MID), HUB_PATTERN_ALPHA * 1.6))


## The class glyph's badge on the inset's lower right corner (its centre and radius).
static func glyph_badge(inset: Rect2) -> Dictionary:
	return {"at": inset.end - Vector2(inset.size.x, inset.size.y) * 0.08, "r": inset.size.x * GLYPH_BADGE}


## Draws the class glyph of `look` in a dark disc on the Polaroid inset's corner.
static func draw_glyph_badge(ci: CanvasItem, inset: Rect2, look: Dictionary, alpha: float = 1.0) -> void:
	var g := StringName(look.get("hub_glyph", PLAIN))
	if g == PLAIN or not inset.has_area():
		return
	var b := glyph_badge(inset)
	var at: Vector2 = b["at"]
	var r: float = b["r"]
	var accent: Color = look.get("accent", Palette.TEXT_MID)
	ci.draw_circle(at, r, Color(Palette.NIGHT_SKY, alpha))
	ci.draw_arc(at, r, 0.0, TAU, 20, Color(accent, alpha), 1.5, true)
	var m := glyph_marks(g, at, r * 0.62)
	m.width = maxf(1.2, r * 0.14)
	draw_marks(ci, m, Color(accent, alpha))


## A mark set's fingerprint (tests: two classes never share a bezel): its counts and its
## geometry, rounded.
static func marks_key(m: Dictionary) -> String:
	var sum := Vector2.ZERO
	var n := 0
	for line: PackedVector2Array in m.lines:
		for p in line:
			sum += p
			n += 1
	for d: Vector3 in m.dots:
		sum += Vector2(d.x, d.y) * d.z
	for poly: PackedVector2Array in m.polys:
		for p in poly:
			sum += p * 2.0
	return "%d/%d/%d/%d:%d,%d" % [m.lines.size(), n, m.dots.size(), m.polys.size(), roundi(sum.x), roundi(sum.y)]


## The Ghost's flicker at `phase` (0 at rest): a few quick dips per period, from hashes.
static func _flicker(phase: float, depth: float = FLICKER_DEPTH) -> float:
	var step := floori(phase * FLICKER_STEPS)
	return (1.0 if _h(step, 90) > FLICKER_ON else 0.25 * _h(step, 91)) * depth if phase > 0.0 else 0.0


## The flicker's steps per ambient period, the share of steps that dip hard, and its depth.
const FLICKER_STEPS := 24
const FLICKER_ON := 0.8
const FLICKER_DEPTH := 0.7


static func _marks() -> Dictionary:
	var lines: Array[PackedVector2Array] = []
	var dots: Array[Vector3] = []
	var polys: Array[PackedVector2Array] = []
	return {"lines": lines, "dots": dots, "polys": polys, "width": ORNAMENT_W, "alpha": 1.0}


static func _arc_pts(c: Vector2, r: float, a0: float, a1: float, n: int) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for i in n + 1:
		pts.append(c + Vector2.from_angle(lerpf(a0, a1, float(i) / n)) * r)
	return pts


static func _hex(c: Vector2, r: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for k in 7:
		pts.append(c + Vector2.from_angle(PI / 6.0 + k * PI / 3.0) * r)
	return pts


## Hash noise 0..1 (decoration only).
static func _h(a: int, b: int, c: int = 0) -> float:
	return float(hash(Vector3i(a, b, c)) & 0xFFFF) / 65535.0
