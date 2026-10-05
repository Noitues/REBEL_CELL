class_name RaidVehicle
extends RefCounted
## ART-6 3A: a raid threat's map icon, vehicle icons v4 (ART_BIBLE v2 §4.8, round 22
## `vehicle_icons_v4`, ported from art-concepts-r43 `round22_raid_world/scripts/icons22.py`):
## SHAPE = type (FAST a chevron badge with `>>`, HEAVY a thick block with its weight, SPECIAL a
## hexagon with the corp's verb glyph); FILL = the corp colour = health, drained from the top
## with a white drain line; RING = a dashed corp circle about 1.8x the icon carrying status
## pips clockwise from the top right (slowed, frozen) and, on hover only, the yellow heading
## arrow. The type comes from what the threat does in the rules (ThreatData), never from its
## name: FAST moves two links a step, SPECIAL freezes or alters links, the rest are HEAVY.
## FLYING has no rule yet (its art stays in docs/art_reference/). Static drawing; view only.

const FAST := "fast"
const HEAVY := "heavy"
const SPECIAL := "special"
## Statuses a threat can carry in the current rules (ICE Lock / a stationed Ghost's hold).
const STATUS_FROZEN := "frozen"
const STATUS_SLOWED := "slowed"

## Ring radius (x the icon radius), its dash count and gap share, widths (x radius).
const RING := 1.78
const RING_DASHES := 22
const RING_GAP := 0.42
const RING_W := 0.11
const RING_INK_W := 0.19
## The white rim round the shape and the ink inside it (x radius).
const RIM := 0.16
const INK_RIM := 0.06
## The drained part's share of the corp colour.
const EMPTY_SHARE := 0.22
## The glyph's size (x radius); FAST's `>>` sits raised (x radius).
const GLYPH := 0.52
const FAST_LIFT := 0.14
## Status pips: radius (x radius) and their spacing round the ring (radians).
const PIP := 0.42
const PIP_STEP := 0.62
## The heading arrow (hover): its reach past the ring and half width (x radius).
const HEADING_OUT := 0.5
const HEADING_SPREAD := 0.3


## The icon type of threat `t` from its rules.
static func type_of(t: ThreatData) -> String:
	if t == null:
		return HEAVY
	if t.freezes_edges or t.alters_edges:
		return SPECIAL
	if t.edges_per_step >= 2:
		return FAST
	return HEAVY


## The corp's ring colour (REBEL_CELL's red dashes paled toward white so they read, §2.4).
static func ring_color(corporation_id: StringName) -> Color:
	if corporation_id == &"rebel_cell":
		return RaidSkin.token(&"CORP_REBEL_CELL_2", Palette.STICKER_PINK)
	return Palette.corp_color(corporation_id)


## The icon's outline for type `type` round `c` at radius `r`.
static func shape(type: String, c: Vector2, r: float) -> PackedVector2Array:
	match type:
		FAST:
			return PackedVector2Array([c + Vector2(0, -1.08) * r, c + Vector2(0.92, -0.18) * r, c + Vector2(0.92, 0.86) * r,
				c + Vector2(0, 0.4) * r, c + Vector2(-0.92, 0.86) * r, c + Vector2(-0.92, -0.18) * r])
		SPECIAL:
			var out := PackedVector2Array()
			for i in 6:
				var a := PI / 6.0 + i * PI / 3.0
				out.append(c + Vector2(cos(a), sin(a)) * r)
			return out
	var k := r * 0.9
	var q := r * 0.16
	return PackedVector2Array([c + Vector2(-k + q, -k), c + Vector2(k - q, -k), c + Vector2(k, -k + q), c + Vector2(k, k - q),
		c + Vector2(k - q, k), c + Vector2(-k + q, k), c + Vector2(-k, k - q), c + Vector2(-k, -k + q)])


## The box the icon covers with its ring (local px).
static func rect(c: Vector2, r: float) -> Rect2:
	var R := r * (RING + PIP)
	return Rect2(c - Vector2(R, R), Vector2(R, R) * 2.0)


## Draws threat icon `type` of `corporation_id` at `c` (radius `r`): `hp` 0..1, `statuses`,
## `heading` (radians, NAN for none: hover only), `ring_phase` (0..1, the dashes' turn),
## `alpha`.
static func draw(ci: CanvasItem, c: Vector2, r: float, type: String, corporation_id: StringName, hp: float = 1.0,
		statuses: Array = [], heading: float = NAN, ring_phase: float = 0.0, alpha: float = 1.0) -> void:
	var col := Color(Palette.corp_color(corporation_id), alpha)
	var ink := Color(Palette.NIGHT_SKY, alpha)
	var rim := Color(Palette.PAPER, alpha)
	var R := r * RING
	_dashed_circle(ci, c, R, ink, r * RING_INK_W, ring_phase)
	_dashed_circle(ci, c, R, Color(ring_color(corporation_id), alpha), r * RING_W, ring_phase)
	ci.draw_colored_polygon(shape(type, c, r * (1.0 + RIM)), rim)
	var body := shape(type, c, r * (1.0 + INK_RIM))
	ci.draw_colored_polygon(body, ink)
	var inner := shape(type, c, r)
	# The health fill: the corp colour from the bottom up to hp, the drained top dark.
	ci.draw_colored_polygon(inner, Color(col.darkened(1.0 - EMPTY_SHARE), alpha))
	var top := INF
	var bottom := -INF
	for p in inner:
		top = minf(top, p.y)
		bottom = maxf(bottom, p.y)
	var level := lerpf(bottom, top, clampf(hp, 0.0, 1.0))
	var cut := PackedVector2Array([Vector2(c.x - r * 3.0, level), Vector2(c.x + r * 3.0, level), Vector2(c.x + r * 3.0, bottom + r), Vector2(c.x - r * 3.0, bottom + r)])
	for piece in Geometry2D.intersect_polygons(inner, cut):
		if piece.size() >= 3:
			ci.draw_colored_polygon(piece, col)
	if hp > 0.0 and hp < 1.0:
		for seg in Geometry2D.intersect_polyline_with_polygon(PackedVector2Array([Vector2(c.x - r * 2.0, level), Vector2(c.x + r * 2.0, level)]), inner):
			if seg.size() >= 2:
				ci.draw_polyline(seg, rim, maxf(1.0, r * 0.1))
	_glyph(ci, type, corporation_id, c + Vector2(0, -r * FAST_LIFT if type == FAST else 0.0), r * GLYPH, ink)
	for i in statuses.size():
		var a := -PI * 0.25 + i * PIP_STEP
		_pip(ci, c + Vector2(cos(a), sin(a)) * R, r * PIP, String(statuses[i]), alpha)
	if not is_nan(heading):
		var tip := c + Vector2.from_angle(heading) * (R + r * HEADING_OUT)
		var l := c + Vector2.from_angle(heading + HEADING_SPREAD) * (R - r * 0.1)
		var rr := c + Vector2.from_angle(heading - HEADING_SPREAD) * (R - r * 0.1)
		var tri := PackedVector2Array([tip, l, rr])
		ci.draw_colored_polygon(tri, Color(RaidSkin.pencil_plan(), alpha))
		tri.append(tip)
		ci.draw_polyline(tri, ink, maxf(1.0, r * 0.08))


static func _dashed_circle(ci: CanvasItem, c: Vector2, R: float, col: Color, width: float, phase: float) -> void:
	for i in RING_DASHES:
		var a0 := TAU * (i + phase) / RING_DASHES
		ci.draw_arc(c, R, a0, a0 + TAU / RING_DASHES * (1.0 - RING_GAP), 6, col, width)


## The type's glyph: FAST `>>`, HEAVY its weight, SPECIAL the corp's verb.
static func _glyph(ci: CanvasItem, type: String, corporation_id: StringName, c: Vector2, s: float, ink: Color) -> void:
	match type:
		FAST:
			for ox: float in [-0.42, 0.28]:
				var p := c + Vector2(ox * s, 0)
				ci.draw_colored_polygon(PackedVector2Array([p + Vector2(-0.25, -0.8) * s, p + Vector2(0.4, 0) * s, p + Vector2(-0.25, 0.8) * s,
					p + Vector2(0.05, 0.8) * s, p + Vector2(0.7, 0) * s, p + Vector2(0.05, -0.8) * s]), ink)
		HEAVY:
			# A weight: two wedges meeting in the middle (round 22 "special_weight").
			ci.draw_colored_polygon(PackedVector2Array([c + Vector2(-0.8, -0.7) * s, c + Vector2(0.8, -0.7) * s, c + Vector2(0.18, 0) * s, c + Vector2(-0.18, 0) * s]), ink)
			ci.draw_colored_polygon(PackedVector2Array([c + Vector2(-0.18, 0) * s, c + Vector2(0.18, 0) * s, c + Vector2(0.8, 0.7) * s, c + Vector2(-0.8, 0.7) * s]), ink)
			ci.draw_rect(Rect2(c + Vector2(-0.9, -0.85) * s, Vector2(1.8, 0.2) * s), ink)
			ci.draw_rect(Rect2(c + Vector2(-0.9, 0.65) * s, Vector2(1.8, 0.2) * s), ink)
		_:
			verb_glyph(ci, corporation_id, c, s, ink)


## The corp's SPECIAL verb (round 22 VERB): Meridian a padlock, Solace a dose, Halcyon a
## freeze, Orbital the lander DROP, REBEL_CELL a burn.
static func verb_glyph(ci: CanvasItem, corporation_id: StringName, c: Vector2, s: float, ink: Color) -> void:
	var w := maxf(1.2, s * 0.22)
	match corporation_id:
		&"meridian":
			ci.draw_rect(Rect2(c + Vector2(-0.6, -0.1) * s, Vector2(1.2, 0.9) * s), ink)
			ci.draw_arc(c + Vector2(0, -0.1) * s, s * 0.4, PI, TAU, 10, ink, w)
		&"solace":
			ci.draw_set_transform(c, -0.7, Vector2.ONE)
			ci.draw_rect(Rect2(Vector2(-0.85, -0.35) * s, Vector2(1.7, 0.7) * s), ink)
			ci.draw_set_transform(Vector2.ZERO)
		&"halcyon":
			for k in 3:
				var d := Vector2.from_angle(PI * k / 3.0) * s * 0.85
				ci.draw_line(c - d, c + d, ink, w)
		&"orbital":
			ci.draw_colored_polygon(PackedVector2Array([c + Vector2(-0.22, -0.85) * s, c + Vector2(0.22, -0.85) * s, c + Vector2(0.22, -0.1) * s,
				c + Vector2(0.6, -0.1) * s, c + Vector2(0, 0.5) * s, c + Vector2(-0.6, -0.1) * s, c + Vector2(-0.22, -0.1) * s]), ink)
			ci.draw_rect(Rect2(c + Vector2(-0.7, 0.65) * s, Vector2(1.4, 0.2) * s), ink)
		_:
			ci.draw_colored_polygon(PackedVector2Array([c + Vector2(-0.55, 0.75) * s, c + Vector2(-0.6, 0) * s, c + Vector2(-0.2, -0.4) * s,
				c + Vector2(0, -0.9) * s, c + Vector2(0.3, -0.35) * s, c + Vector2(0.6, 0.05) * s, c + Vector2(0.55, 0.75) * s]), ink)


## A status pip on the ring: frozen (ice, a snowflake) or slowed (blue, a slowed clock).
static func _pip(ci: CanvasItem, p: Vector2, pr: float, status: String, alpha: float) -> void:
	var ink := Color(Palette.NIGHT_SKY, alpha)
	var col := Palette.NET_CYAN.lerp(Palette.TEXT_HI, 0.55) if status == STATUS_FROZEN else Palette.NET_CYAN.lerp(Palette.NEON_VIOLET, 0.35)
	ci.draw_circle(p, pr * 1.12, ink)
	ci.draw_circle(p, pr, Color(col, alpha))
	var s := pr * 0.62
	var w := maxf(1.0, pr * 0.16)
	if status == STATUS_FROZEN:
		for k in 3:
			var d := Vector2.from_angle(PI * k / 3.0 + PI / 2.0) * s
			ci.draw_line(p - d, p + d, ink, w)
	else:
		ci.draw_arc(p, s, 0, TAU, 14, ink, w)
		ci.draw_line(p, p + Vector2(0, -s * 0.7), ink, w)
		ci.draw_line(p, p + Vector2(s * 0.55, s * 0.3), ink, w)
