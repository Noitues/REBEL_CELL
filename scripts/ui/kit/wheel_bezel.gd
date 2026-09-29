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


## The operative's look: a PAPER-stickered bezel, CELL_PINK rim, the class's accent
## (§7.1; ornaments come per class, `ornament`).
static func operative_look(class_id: StringName) -> Dictionary:
	return {"owner": Owner.OPERATIVE, "class_id": class_id, "rim": Palette.CELL_PINK, "accent": Palette.class_accent(class_id),
		"pattern": CorpPattern.Kind.NONE}


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


## Hash noise 0..1 (decoration only).
static func _h(a: int, b: int, c: int = 0) -> float:
	return float(hash(Vector3i(a, b, c)) & 0xFFFF) / 65535.0
