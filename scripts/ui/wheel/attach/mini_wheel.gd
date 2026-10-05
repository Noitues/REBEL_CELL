class_name MiniWheel
extends RefCounted
## A satellite or drone as a docked mini-wheel (ART_BIBLE v2 §3.11, round 40 `satellites_v3`,
## round 41 `drones_v2`): the D4 frame scaled down in its owner's colour (the collar), the owner's
## slices with their glyph and value upright (glyph before the centre, value after), its own blade
## pointing away from the host with the value it reads, and its HP in the hub as a number and pips.
## Drawing only.

## Radii as shares of the mini-wheel's radius: hub, slices' inner and outer edge, glyph and value ring.
const HUB := 0.4
const SLICE_IN := 0.42
const SLICE_OUT := 0.86
const READ_AT := 0.64
## The collar's width (share of the radius), never under MIN_LINE px.
const COLLAR := 0.09
const MIN_LINE := 1.5
## The blade: root (outside the collar) and tip (biting the slices), half width; its value tab.
const BLADE_ROOT := 1.3
const BLADE_TIP := 0.8
const BLADE_HALF := 0.13
const TAB_AT := 1.48
const TAB_R := 0.2
## Text: value and HP sizes as shares of the radius, never under MIN_TEXT px.
const VALUE_SIZE := 0.3
const HP_SIZE := 0.34
const MIN_TEXT := 12
## Glyph radius (share of the radius) and the gap glyph-value (share).
const GLYPH_R := 0.17
const GLYPH_GAP := 0.13
## HP pips round the hub: at most this many (more share one pip each), their angular share.
const MAX_PIPS := 12
const PIP_SHARE := 0.62
## Slice fill and outline alpha.
const FILL_ALPHA := 0.34
const OUTLINE_ALPHA := 0.9


## Draws `sat`'s mini-wheel centred on `c`, radius `rm`; `up` is the screen angle that reads as its
## top (away from the host); `col` the owner's frame colour; `alpha` its opacity (the bloom);
## `hp` the HP shown (it rolls in a replay); its glyphs go on `glyphs` (1C's atlas).
static func draw(ci: CanvasItem, glyphs: GlyphBatch, c: Vector2, rm: float, up: float, sat: CombatantState, lookup: ContentLookup, col: Color, alpha: float, hp: float) -> void:
	if sat == null or sat.wheel == null or alpha <= 0.0:
		return
	var w := sat.wheel
	var n := maxi(1, w.slice_count)
	var tps := w.ticks_per_slice()
	var turn := up + PI * 0.5  # WheelView._ang(0) is straight up: turn it to `up`
	ci.draw_circle(c, rm, AttachStyle.glass(0.94 * alpha))
	var vs := maxi(MIN_TEXT, roundi(rm * VALUE_SIZE))
	for j in n:
		var slice := lookup.get_content(w.slot_slice_ids[j]) as SliceData if lookup != null else null
		var sc := AttachStyle.slice_color(slice.slice_type) if slice != null else Palette.DISABLED
		var a0 := WheelView._ang(j * tps - tps * 0.5 - w.rotation) + turn
		var a1 := WheelView._ang(j * tps + tps * 0.5 - w.rotation) + turn
		var wedge := AttachStyle.sector(c, rm * SLICE_IN, rm * SLICE_OUT, minf(a0, a1) + 0.04, maxf(a0, a1) - 0.04, 8)
		ci.draw_colored_polygon(wedge, Color(sc, FILL_ALPHA * alpha))
		var closed := wedge.duplicate()
		closed.append(wedge[0])
		ci.draw_polyline(closed, Color(sc.lightened(0.3), OUTLINE_ALPHA * alpha), MIN_LINE, true)
		if slice == null:
			continue
		var mid := WheelView._ang(j * tps - w.rotation) + turn
		var at := c + Vector2(cos(mid), sin(mid)) * rm * READ_AT
		var text := str(slice.base_output) if slice.base_output > 0 else ""
		var gx := -rm * GLYPH_GAP if text != "" else 0.0
		AttachStyle.draw_slice_glyph(glyphs, at + Vector2(gx, 0), rm * GLYPH_R * 2.0, slice, alpha)
		if text != "":
			AttachStyle.draw_centred(ci, AttachStyle.value_font(), at + Vector2(rm * GLYPH_GAP * 1.1, 0), text, vs, Color(Palette.TEXT_HI, alpha), 2)
	# Collar in the owner's colour, with a hairline at the slices' edge.
	ci.draw_arc(c, rm, 0, TAU, 40, Color(col, alpha), maxf(MIN_LINE, rm * COLLAR), true)
	ci.draw_arc(c, rm * SLICE_OUT, 0, TAU, 40, Color(col, 0.5 * alpha), MIN_LINE, true)
	# Hub: HP number and pips.
	ci.draw_circle(c, rm * HUB, AttachStyle.glass(alpha))
	var pips := mini(MAX_PIPS, maxi(1, sat.max_hp))
	var lit := ceili(clampf(hp / maxf(1.0, sat.max_hp), 0.0, 1.0) * pips)
	for k in pips:
		var p0 := -PI * 0.5 + TAU * k / pips
		var p1 := p0 + TAU / pips * PIP_SHARE
		ci.draw_arc(c, rm * HUB * 0.86, p0, p1, 4, Color(Palette.GAIN if k < lit else Palette.DISABLED, alpha), maxf(MIN_LINE, rm * 0.06), true)
	AttachStyle.draw_centred(ci, AttachStyle.value_font(), c, str(roundi(hp)), maxi(MIN_TEXT, roundi(rm * HP_SIZE)), Color(Palette.GAIN, alpha), 2)
	# Its own blade, pointing away from the host, with the value it reads.
	if not w.pointer_ticks.is_empty():
		var pa := WheelView._ang(w.pointer_ticks[0]) + turn
		var dir := Vector2(cos(pa), sin(pa))
		var side := dir.orthogonal() * rm * BLADE_HALF
		var root := c + dir * rm * BLADE_ROOT
		var tip := c + dir * rm * BLADE_TIP
		ci.draw_colored_polygon(PackedVector2Array([tip, root + side, root - side]), Color(AttachStyle.cream(), alpha))
		ci.draw_polyline(PackedVector2Array([tip, root + side, root - side, tip]), Color(Palette.INK, 0.7 * alpha), 1.0, true)
		var land := landing(sat, lookup)
		if land != null and land.base_output > 0:
			var tab := c + dir * rm * TAB_AT
			ci.draw_circle(tab, rm * TAB_R, AttachStyle.glass(alpha))
			ci.draw_arc(tab, rm * TAB_R, 0, TAU, 16, Color(AttachStyle.cream(), alpha), MIN_LINE, true)
			AttachStyle.draw_centred(ci, AttachStyle.label_font(), tab, str(land.base_output), MIN_TEXT, Color(AttachStyle.cream(), alpha))


## The slice `sat`'s own needle reads now (its current effect), or null.
static func landing(sat: CombatantState, lookup: ContentLookup) -> SliceData:
	if sat == null or sat.wheel == null or sat.wheel.pointer_ticks.is_empty() or lookup == null:
		return null
	var slot := WheelMath.slice_at(WheelMath.tick_at(sat.wheel.rotation, sat.wheel.pointer_ticks[0]), sat.wheel.slice_count)
	if slot < 0 or slot >= sat.wheel.slot_slice_ids.size():
		return null
	return lookup.get_content(sat.wheel.slot_slice_ids[slot]) as SliceData
