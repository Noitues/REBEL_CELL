class_name WheelView
extends Control
## Wireframe glowing wheel (STYLE_GUIDE 4): player wheel in cell_pink, enemy wheels in
## the corporation colour, a glyph on every slice, dashed outline for the Miss slice,
## resistance in resist_gold, statuses as glyph + tag, docked satellites and drones, the
## inner ring, per-pointer intent labels, a dashed cell_acid ghost preview, an orbit
## trail, and telegraphed migrations as flickering dashed pointers (GDD 9.2).
## Everything is readable without colour. View only: never changes game state.

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


func _init() -> void:
	custom_minimum_size = Vector2(330, 330)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


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
	var r := _radius() + 34
	return Rect2(global_position + center - Vector2(r, r), Vector2(r * 2, r * 2))


## Slot index under a global point on the outer ring band, or -1 outside the wheel.
func slot_at_global(point: Vector2) -> int:
	if combatant == null or combatant.wheel == null:
		return -1
	var local := point - global_position - _center()
	var dist := local.length()
	var radius := _radius()
	if dist < radius - 34 or dist > radius + 40:
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
	return Vector2(size.x / 2.0, size.y / 2.0 + 6) + shake


func _radius() -> float:
	return minf(size.x, size.y) * 0.31


func _tick_angle(tick: float, rotation_ticks: int) -> float:
	return deg_to_rad((tick - rotation_ticks) * (360.0 / RC.TICKS) - 90.0)


func _col(c: Color) -> Color:
	return c.inverted() if inverted else c


func _draw() -> void:
	if combatant == null or combatant.wheel == null:
		draw_string(Palette.mono(), Vector2(8, 20), "(no wheel)", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Palette.PAPER)
		return
	var wheel := combatant.wheel
	var center := _center()
	var radius := _radius()
	var line := _col(wheel_color if combatant.is_alive() else Color(wheel_color, 0.3))
	var tps := wheel.ticks_per_slice()
	if inverted:
		draw_circle(center, radius + 30, Color(Palette.PAPER, 0.9))
	if highlighted:
		draw_arc(center, radius + 30, 0, TAU, 64, _col(Color(Palette.CELL_ACID, 0.7)), 2.0)
		draw_string(Palette.marker(), center + Vector2(-30, -radius - 36), "TARGET", HORIZONTAL_ALIGNMENT_LEFT, -1, 13, _col(Palette.CELL_ACID))
	# Glow pass: wide translucent ring, then the crisp wireframe.
	draw_arc(center, radius, 0, TAU, 96, Color(line, 0.18), 22.0)
	draw_arc(center, radius + 11, 0, TAU, 96, line, 1.5)
	draw_arc(center, radius - 11, 0, TAU, 96, line, 1.5)
	for i in wheel.slice_count:
		var slice := lookup.get_content(wheel.slot_slice_ids[i]) as SliceData
		var start := _tick_angle(i * tps - tps / 2.0, wheel.rotation)
		var end := _tick_angle(i * tps + tps / 2.0, wheel.rotation)
		var mid := _tick_angle(i * tps, wheel.rotation)
		var fill := _col(Color(Palette.slice_color(slice.slice_type), 0.28))
		if slice.slice_type == RC.SliceType.MISS:
			_draw_dashed_arc(center, radius, start, end, line, 2.0)
		else:
			draw_arc(center, radius, start, end, 12, fill, 20.0)
		draw_line(center + Vector2(cos(start), sin(start)) * (radius - 11), center + Vector2(cos(start), sin(start)) * (radius + 11), line, 1.5)
		var glyph_pos := center + Vector2(cos(mid), sin(mid)) * radius
		var glyph: String = Palette.SLICE_GLYPHS.get(slice.slice_type, "?")
		draw_string(Palette.display(), glyph_pos + Vector2(-7, 7), glyph, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, _col(Palette.PAPER))
		var label := "%s %d" % [Palette.SLICE_NAMES.get(slice.slice_type, "?"), slice.base_output] if slice.base_output > 0 else String(Palette.SLICE_NAMES.get(slice.slice_type, "?"))
		var status: int = wheel.slice_statuses[i]
		if status != RC.Status.NONE:
			label += " %s%s" % [Palette.STATUS_GLYPHS.get(status, ""), Palette.STATUS_TAGS.get(status, "")]
		if wheel.slot_firmware_ids[i] != &"":
			label += " {%s}" % wheel.slot_firmware_ids[i]
		var lp := center + Vector2(cos(mid), sin(mid)) * (radius + 30)
		draw_string(Palette.mono(), lp + Vector2(-26, 4), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, _col(Palette.PAPER))
		for sat in satellites:
			if sat.dock_slot == i:
				var sp := center + Vector2(cos(mid), sin(mid)) * (radius + 50)
				var sat_col := _col(Palette.CELL_ACID if sat.is_player else Palette.RESIST_GOLD)
				draw_arc(sp, 9, 0, TAU, 16, sat_col, 1.5)
				draw_string(Palette.mono(), sp + Vector2(-18, 22), "%s %d" % [sat.display_name.to_lower(), sat.hp], HORIZONTAL_ALIGNMENT_LEFT, -1, 10, sat_col)
	for t in RC.TICKS:
		var a := _tick_angle(t, wheel.rotation)
		var inner_r := radius - 16 if t % tps == 0 else radius - 13
		draw_line(center + Vector2(cos(a), sin(a)) * inner_r, center + Vector2(cos(a), sin(a)) * (radius - 11), Color(line, 0.6), 1.0)
	if wheel.has_inner_ring():
		var ring_r := radius - 30
		draw_arc(center, ring_r, 0, TAU, 64, Color(line, 0.5), 1.0)
		for k in RC.RING_SEGMENTS:
			var seg := lookup.get_content(wheel.ring_segment_ids[k]) as RingSegmentData
			var s := _tick_angle(k * 10 - 5, wheel.inner_rotation)
			var e := _tick_angle(k * 10 + 5, wheel.inner_rotation)
			draw_arc(center, ring_r, s, e, 12, Color(line, 0.35 if k % 2 == 0 else 0.2), 10.0)
			var m := _tick_angle(k * 10, wheel.inner_rotation)
			draw_string(Palette.mono(), center + Vector2(cos(m), sin(m)) * ring_r + Vector2(-8, 4), seg.display_name if seg != null else "?", HORIZONTAL_ALIGNMENT_LEFT, -1, 10, _col(Palette.PAPER))
	# Pointers (white), orbit trail (faint future positions), ghost preview (dashed acid).
	var pcol := Color(_col(Palette.PAPER), pointer_alpha)
	for p in wheel.pointer_ticks:
		var a := deg_to_rad(p * (360.0 / RC.TICKS) - 90.0)
		var tip := center + Vector2(cos(a), sin(a)) * (radius - 18)
		var base := center + Vector2(cos(a), sin(a)) * (radius + 18)
		draw_line(base, tip, pcol, 3.0)
		draw_circle(tip, 4, pcol)
		if wheel.pointer_orbit != 0:
			for k in range(1, 4):
				var oa := deg_to_rad(posmod(p + wheel.pointer_orbit * k, RC.TICKS) * (360.0 / RC.TICKS) - 90.0)
				draw_circle(center + Vector2(cos(oa), sin(oa)) * (radius + 16), 3, Color(Palette.PAPER, 0.5 - k * 0.12))
	# Telegraphed migration (GDD 2.11, 9.2): next turn's pointers, dashed and flickering.
	for p in wheel.pending_pointer_ticks:
		var a := deg_to_rad(p * (360.0 / RC.TICKS) - 90.0)
		var tip := center + Vector2(cos(a), sin(a)) * (radius - 18)
		var base := center + Vector2(cos(a), sin(a)) * (radius + 18)
		var mcol := Color(_col(Palette.CELL_ACID), 1.2 - pointer_alpha)
		var n := 6
		for k in n:
			if k % 2 == 0:
				draw_line(base.lerp(tip, float(k) / n), base.lerp(tip, float(k + 1) / n), mcol, 3.0)
		draw_string(Palette.mono(), base + Vector2(6, -4), "next", HORIZONTAL_ALIGNMENT_LEFT, -1, 10, mcol)
	if ghost_rotation != null and not wheel.pointer_ticks.is_empty():
		var p0: int = wheel.pointer_ticks[0]
		var predicted := WheelMath.tick_at(int(ghost_rotation), p0)
		var delta := int(ghost_rotation) - wheel.rotation
		var a0 := deg_to_rad(p0 * (360.0 / RC.TICKS) - 90.0)
		var a1 := a0 - deg_to_rad(delta * (360.0 / RC.TICKS))
		_draw_dashed_arc(center, radius + 24, minf(a0, a1), maxf(a0, a1), _col(Palette.CELL_ACID), 2.0)
		var gp := center + Vector2(cos(a1), sin(a1)) * (radius + 24)
		draw_circle(gp, 5, _col(Palette.CELL_ACID))
		draw_string(Palette.marker(), gp + Vector2(8, 4), "-> tick %d" % predicted, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, _col(Palette.CELL_ACID))
	# Centre readout: vitals and per-pointer intent (GDD 9.2).
	var lines := [combatant.display_name, "HP %d/%d  BLK %d  SHD %d" % [combatant.hp, combatant.max_hp, combatant.block, combatant.shield]]
	if combatant.resistance > 0 or combatant.hub_resistance > 0 or wheel.passive_resistance > 0:
		lines.append("RESIST %d" % combatant.resistance)
	if wheel.frozen:
		lines.append("FROZEN")
	if wheel.hub_id != &"":
		lines.append(String(wheel.hub_id) + (" (BREACHED)" if combatant.is_hub_breached() else ""))
	for r in readouts:
		var slice: SliceData = r["slice"]
		var tier_text: String = Palette.TIER_NAMES.get(r["tier"], "?") if wheel.slice_count == RC.SLICES else "full"
		var text := "P%d %s %s %s" % [r["pointer_index"], Palette.SLICE_GLYPHS.get(slice.slice_type, "?"), Palette.SLICE_NAMES.get(slice.slice_type, "?"), tier_text]
		if r["segment"] != null:
			text += " ring:%s" % r["segment"].display_name
		if r["guard_id"] != &"":
			text += " [guarded]"
		lines.append(text)
	lines.append_array(extra_lines)
	for i in lines.size():
		var col := _col(Palette.RESIST_GOLD) if lines[i].begins_with("RESIST") else _col(Palette.PAPER)
		draw_string(Palette.mono(), Vector2(center.x - 62, center.y - 34 + i * 13), lines[i], HORIZONTAL_ALIGNMENT_LEFT, 132, 10, col)


func _draw_dashed_arc(center: Vector2, radius: float, start: float, end: float, color: Color, width: float) -> void:
	var span := end - start
	var dashes := maxi(3, int(absf(span) / 0.12))
	for i in dashes:
		if i % 2 == 1:
			continue
		var a := start + span * i / dashes
		var b := start + span * (i + 1) / dashes
		draw_arc(center, radius, a, b, 4, color, width)
