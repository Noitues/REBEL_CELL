class_name WheelView
extends Control
## The spinner (STYLE_GUIDE 4, combat pass): neon gauge bars, one wedge per slice with its
## drawn icon inside and its value outside (no labels: the full slice text is the hover
## tooltip), a small white "perfect" arrow inside each slice at its outer edge, white
## gauge-needle pointers, a segmented HP arc underneath with the numbers in its gap, the
## name in the hub, and the intent as a taped paper tag above (what resolves next).
## Also: statuses, firmware, docked satellites, the inner ring, the dashed acid ghost
## preview, orbit trails, telegraphed migrations. Readable without colour.
## View only: never changes game state.

var combatant: CombatantState = null
var satellites: Array[CombatantState] = []
var readouts: Array[Dictionary] = []
var lookup: ContentLookup = null
var highlighted: bool = false
var wheel_color: Color = Palette.CELL_PINK
## Ghost preview (GDD 9.2): predicted outer/inner rotation after a hovered card, or null.
var ghost_rotation: Variant = null
var ghost_inner_rotation: Variant = null
## Perfect feedback: wheel-local inversion for a couple of frames.
var inverted: bool = false
var shake: Vector2 = Vector2.ZERO
## Migration flicker: pointer alpha animated by the scene while a MIGRATE is pending.
var pointer_alpha: float = 1.0
## Extra readout lines (revealed boss phases, ICE notes).
var extra_lines: Array[String] = []
## What resolves next for this combatant (the scene's preview): {"type": slice type or -1,
## "text": String}; empty = no tag.
var intent: Dictionary = {}
## Horizontal position of the wheel centre as a fraction of the view's width.
var center_x: float = 0.5


func _init() -> void:
	custom_minimum_size = Vector2(330, 330)
	# PASS: hover tooltips on slices; clicks still reach the scene.
	mouse_filter = Control.MOUSE_FILTER_PASS
	tooltip_text = " "


## Hover: the full text of the slice under the mouse (type, output, status, firmware).
func _get_tooltip(at_position: Vector2) -> String:
	var slot := slot_at_global(global_position + at_position)
	if slot < 0 or combatant == null:
		return ""
	return _slice_label(slot)


func _slice_label(i: int) -> String:
	var wheel := combatant.wheel
	var slice := lookup.get_content(wheel.slot_slice_ids[i]) as SliceData
	var label := "%s %d" % [Palette.SLICE_NAMES.get(slice.slice_type, "?"), slice.base_output] if slice.base_output > 0 else String(Palette.SLICE_NAMES.get(slice.slice_type, "?"))
	var status: int = wheel.slice_statuses[i]
	if status != RC.Status.NONE:
		label += " %s%s" % [Palette.STATUS_GLYPHS.get(status, ""), Palette.STATUS_TAGS.get(status, "")]
	if wheel.slot_firmware_ids[i] != &"":
		label += " {%s}" % wheel.slot_firmware_ids[i]
	return label


## Updates what the view shows. `p_satellites` are the drones docked on this wheel.
func show_combatant(c: CombatantState, p_satellites: Array[CombatantState], p_readouts: Array[Dictionary], p_lookup: ContentLookup) -> void:
	combatant = c
	satellites = p_satellites
	readouts = p_readouts
	lookup = p_lookup
	wheel_color = Palette.CELL_PINK if c.is_player else Palette.corp_color(_corporation_of(c))
	queue_redraw()


func set_ghost(outer: Variant, inner: Variant = null) -> void:
	ghost_rotation = outer
	ghost_inner_rotation = inner
	queue_redraw()


## The wheel's on-screen disc (for layout checks: zine elements never cover it).
func wheel_rect() -> Rect2:
	var center := _center()
	var r := _radius() + 22
	return Rect2(global_position + center - Vector2(r, r), Vector2(r * 2, r * 2))


## Slot index under a global point on the outer ring band, or -1 outside the wheel.
func slot_at_global(point: Vector2) -> int:
	if combatant == null or combatant.wheel == null:
		return -1
	var local := point - global_position - _center()
	var dist := local.length()
	var radius := _radius()
	if dist < radius - _band() - 4 or dist > radius + 30:
		return -1
	var angle := rad_to_deg(atan2(local.y, local.x)) + 90.0
	var tick := posmod(roundi(angle / (360.0 / RC.TICKS)) + combatant.wheel.rotation, RC.TICKS)
	return WheelMath.slice_at(tick, combatant.wheel.slice_count)


## Whether a global point is inside the wheel disc (hub included).
func contains_global(point: Vector2) -> bool:
	return wheel_rect().has_point(point)


func _corporation_of(c: CombatantState) -> StringName:
	var data := lookup.get_content(c.source_id) if lookup != null else null
	return data.corporation_id if data != null and "corporation_id" in data else &""


func _center() -> Vector2:
	return Vector2(size.x * center_x, size.y * 0.56) + shake


func _radius() -> float:
	return minf(size.x, size.y) * 0.26


## Width of the slice bar band.
func _band() -> float:
	return _radius() * 0.34


func _tick_angle(tick: float, rotation_ticks: int) -> float:
	return deg_to_rad((tick - rotation_ticks) * (360.0 / RC.TICKS) - 90.0)


func _col(c: Color) -> Color:
	return c.inverted() if inverted else c


func _wedge(center: Vector2, r0: float, r1: float, a0: float, a1: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for k in 11:
		var a := lerpf(a0, a1, k / 10.0)
		pts.append(center + Vector2(cos(a), sin(a)) * r1)
	for k in 11:
		var a := lerpf(a1, a0, k / 10.0)
		pts.append(center + Vector2(cos(a), sin(a)) * r0)
	return pts


func _draw() -> void:
	if combatant == null or combatant.wheel == null:
		draw_string(Palette.mono(), Vector2(8, 20), "(no wheel)", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Palette.PAPER)
		return
	var wheel := combatant.wheel
	var center := _center()
	var radius := _radius()
	var band := _band()
	var inner := radius - band
	var line := _col(wheel_color if combatant.is_alive() else Color(wheel_color, 0.3))
	var tps := wheel.ticks_per_slice()
	# Platform so the wheel reads over the city.
	draw_circle(center, radius + 40, Color(Palette.NIGHT_SKY, 0.55))
	if inverted:
		draw_circle(center, radius + 24, Color(Palette.PAPER, 0.9))
	draw_circle(center, inner - 3, Color("#07080F"))
	# Slices: neon bars, icon inside, value outside, the perfect arrow at the outer edge.
	for i in wheel.slice_count:
		var slice := lookup.get_content(wheel.slot_slice_ids[i]) as SliceData
		var start := _tick_angle(i * tps - tps / 2.0, wheel.rotation)
		var end := _tick_angle(i * tps + tps / 2.0, wheel.rotation)
		var mid := _tick_angle(i * tps, wheel.rotation)
		var sc := Palette.slice_color(slice.slice_type)
		var wedge := _wedge(center, inner, radius, start + 0.03, end - 0.03)
		if slice.slice_type == RC.SliceType.MISS:
			draw_colored_polygon(wedge, _col(Color(sc, 0.18)))
			_draw_dashed_arc(center, radius - 1, start + 0.03, end - 0.03, line, 1.5)
			_draw_dashed_arc(center, inner + 1, start + 0.03, end - 0.03, line, 1.5)
		else:
			draw_colored_polygon(wedge, _col(Color(sc, 0.85)))
			var closed := wedge.duplicate()
			closed.append(wedge[0])
			draw_polyline(closed, _col(Color(sc.lightened(0.3), 0.9)), 1.2)
		var dir := Vector2(cos(mid), sin(mid))
		SliceIcon.draw_icon(self, center + dir * (inner + band * 0.5), band * 0.3, slice.slice_type, _col(Palette.PAPER))
		if slice.base_output > 0:
			draw_string(Palette.display(), center + dir * (radius + 16) + Vector2(-20, 8), str(slice.base_output), HORIZONTAL_ALIGNMENT_CENTER, 40, 20, _col(sc.lightened(0.35)))
		var tip := center + dir * (radius - 3)
		var base := center + dir * (radius - 10)
		var side := dir.orthogonal() * 4.0
		draw_colored_polygon(PackedVector2Array([tip, base + side, base - side]), _col(Palette.PAPER))
		var status: int = wheel.slice_statuses[i]
		if status != RC.Status.NONE:
			var sp := center + dir * (inner + band * 0.5) + dir.orthogonal() * band * 0.42
			draw_circle(sp, 7, Palette.NIGHT_SKY)
			draw_string(Palette.mono(), sp + Vector2(-7, 5), Palette.STATUS_GLYPHS.get(status, ""), HORIZONTAL_ALIGNMENT_CENTER, 14, 11, _col(Palette.CELL_ACID))
		if wheel.slot_firmware_ids[i] != &"":
			var fp := center + dir * (inner + 5) - dir.orthogonal() * band * 0.3
			draw_rect(Rect2(fp - Vector2(3, 3), Vector2(6, 6)), _col(Palette.NET_CYAN))
		for sat in satellites:
			if sat.dock_slot == i:
				var satp := center + dir * (radius + 34)
				var sat_col := _col(Palette.CELL_ACID if sat.is_player else Palette.RESIST_GOLD)
				draw_arc(satp, 9, 0, TAU, 16, sat_col, 1.5)
				draw_string(Palette.mono(), satp + Vector2(-18, 22), "%s %d" % [sat.display_name.to_lower(), sat.hp], HORIZONTAL_ALIGNMENT_LEFT, -1, 10, sat_col)
	draw_arc(center, radius, 0, TAU, 96, Color(line, 0.9), 1.5)
	draw_arc(center, inner, 0, TAU, 96, Color(line, 0.6), 1.0)
	if wheel.has_inner_ring():
		var ring_r := inner - 12
		for k in RC.RING_SEGMENTS:
			var seg := lookup.get_content(wheel.ring_segment_ids[k]) as RingSegmentData
			var s0 := _tick_angle(k * 10 - 5, wheel.inner_rotation)
			var e0 := _tick_angle(k * 10 + 5, wheel.inner_rotation)
			draw_arc(center, ring_r, s0, e0, 12, Color(line, 0.35 if k % 2 == 0 else 0.2), 9.0)
			var m := _tick_angle(k * 10, wheel.inner_rotation)
			draw_string(Palette.mono(), center + Vector2(cos(m), sin(m)) * (ring_r - 14) + Vector2(-8, 4), seg.display_name if seg != null else "?", HORIZONTAL_ALIGNMENT_LEFT, -1, 9, _col(Palette.PAPER))
	# Pointers: short white gauge needles, hub just outside the rim, tip just past its edge.
	var pcol := Color(_col(Palette.PAPER), pointer_alpha)
	for p in wheel.pointer_ticks:
		var a := deg_to_rad(p * (360.0 / RC.TICKS) - 90.0)
		var dir := Vector2(cos(a), sin(a))
		var hub := center + dir * (radius + band * 0.55)
		var ntip := center + dir * (radius - band * 0.2)
		draw_colored_polygon(PackedVector2Array([ntip, hub + dir.orthogonal() * 4.0, hub - dir.orthogonal() * 4.0]), pcol)
		draw_circle(hub, 9, Palette.NIGHT_SKY)
		draw_arc(hub, 9, 0, TAU, 20, pcol, 2.5)
		draw_circle(hub, 3, pcol)
		if wheel.pointer_orbit != 0:
			for k in range(1, 4):
				var oa := deg_to_rad(posmod(p + wheel.pointer_orbit * k, RC.TICKS) * (360.0 / RC.TICKS) - 90.0)
				draw_circle(center + Vector2(cos(oa), sin(oa)) * (radius + band * 0.55), 3, Color(Palette.PAPER, 0.5 - k * 0.12))
	# Telegraphed migration (GDD 2.11, 9.2): next turn's needles, dashed and flickering.
	for p in wheel.pending_pointer_ticks:
		var a := deg_to_rad(p * (360.0 / RC.TICKS) - 90.0)
		var ntip := center + Vector2(cos(a), sin(a)) * (radius - band * 0.2)
		var hub := center + Vector2(cos(a), sin(a)) * (radius + band * 0.55)
		var mcol := Color(_col(Palette.CELL_ACID), 1.2 - pointer_alpha)
		var n := 6
		for k in n:
			if k % 2 == 0:
				draw_line(hub.lerp(ntip, float(k) / n), hub.lerp(ntip, float(k + 1) / n), mcol, 3.0)
		draw_string(Palette.mono(), hub + Vector2(10, -4), "next", HORIZONTAL_ALIGNMENT_LEFT, -1, 10, mcol)
	if ghost_rotation != null and not wheel.pointer_ticks.is_empty():
		var p0: int = wheel.pointer_ticks[0]
		var predicted := WheelMath.tick_at(int(ghost_rotation), p0)
		var delta := int(ghost_rotation) - wheel.rotation
		var a0 := deg_to_rad(p0 * (360.0 / RC.TICKS) - 90.0)
		var a1 := a0 - deg_to_rad(delta * (360.0 / RC.TICKS))
		_draw_dashed_arc(center, radius + 30, minf(a0, a1), maxf(a0, a1), _col(Palette.CELL_ACID), 2.0)
		var gp := center + Vector2(cos(a1), sin(a1)) * (radius + 30)
		draw_circle(gp, 5, _col(Palette.CELL_ACID))
		draw_string(Palette.marker(), gp + Vector2(8, 4), "-> tick %d" % predicted, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, _col(Palette.CELL_ACID))
	# HP: a segmented arc under the wheel, the numbers in its gap (tonearm style).
	var hp_col := _col(Color("#3DFF8B"))
	var segs := 20
	var frac := float(combatant.hp) / maxf(1.0, combatant.max_hp)
	for k in segs:
		var a0 := PI * 0.1 + PI * 0.8 * k / segs
		var a1 := a0 + PI * 0.8 / segs * 0.8
		if absf((a0 + a1) * 0.5 - PI * 0.5) < 0.34:
			continue
		var lit := float(k) / segs < frac
		draw_colored_polygon(_wedge(center, radius + 32, radius + 40, a0, a1), hp_col if lit else Color(1, 1, 1, 0.1))
	draw_string(Palette.display(), center + Vector2(-50, radius + 44), "%d/%d" % [combatant.hp, combatant.max_hp], HORIZONTAL_ALIGNMENT_CENTER, 100, 22, hp_col)
	# Hub: name, then block / shield / resist / states and revealed boss lines.
	var hub_lines: Array[String] = []
	if combatant.block > 0:
		hub_lines.append("BLK %d" % combatant.block)
	if combatant.shield > 0:
		hub_lines.append("SHD %d" % combatant.shield)
	if combatant.resistance > 0 or combatant.hub_resistance > 0 or wheel.passive_resistance > 0:
		hub_lines.append("RESIST %d" % combatant.resistance)
	if wheel.frozen:
		hub_lines.append("FROZEN")
	if wheel.hub_id != &"":
		hub_lines.append(String(wheel.hub_id) + (" (BREACHED)" if combatant.is_hub_breached() else ""))
	hub_lines.append_array(extra_lines)
	var hw := (inner - 10) * 2.0
	draw_string(Palette.marker(), center + Vector2(-hw * 0.5, -6 - hub_lines.size() * 6), combatant.display_name.to_upper(), HORIZONTAL_ALIGNMENT_CENTER, hw, 13, _col(line.lightened(0.2)))
	for i in hub_lines.size():
		var col := _col(Palette.RESIST_GOLD) if hub_lines[i].begins_with("RESIST") else _col(Palette.PAPER)
		draw_string(Palette.mono(), center + Vector2(-hw * 0.5, 10 - hub_lines.size() * 6 + i * 12), hub_lines[i], HORIZONTAL_ALIGNMENT_CENTER, hw, 10, col)
	# Intent: a flat taped paper tag above the needle (what resolves next).
	if not intent.is_empty() and String(intent.get("text", "")) != "":
		_intent_tag(Vector2(center.x, center.y - radius - band - 30), int(intent.get("type", -1)), String(intent["text"]))


func _intent_tag(anchor: Vector2, type: int, text: String) -> void:
	var f := Palette.marker()
	var w := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 15).x + (38 if type >= 0 else 16)
	var r := Rect2(anchor + Vector2(-w * 0.5, -30), Vector2(w, 30))
	draw_rect(Rect2(r.position + Vector2(3, 4), r.size), Palette.SHADOW)
	draw_rect(r, Palette.NOTE_PAPER)
	draw_rect(r, Color(Palette.INK, 0.5), false, 1.0)
	draw_rect(Rect2(r.position + Vector2(w * 0.5 - 14, -5), Vector2(28, 9)), Palette.NOTE_TAPE)
	var tx := r.position.x + 8
	if type >= 0:
		SliceIcon.draw_icon(self, r.position + Vector2(17, 15), 9, type, Palette.slice_color(type))
		tx += 22
	draw_string(f, Vector2(tx, r.position.y + 21), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Palette.INK)


func _draw_dashed_arc(center: Vector2, radius: float, start: float, end: float, color: Color, width: float) -> void:
	var span := end - start
	var dashes := maxi(3, int(absf(span) / 0.12))
	for i in dashes:
		if i % 2 == 1:
			continue
		var a := start + span * i / dashes
		var b := start + span * (i + 1) / dashes
		draw_arc(center, radius, a, b, 4, color, width)
