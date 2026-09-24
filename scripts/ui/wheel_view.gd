class_name WheelView
extends Control
## Placeholder wheel drawing (M1: ugly is fine). Shows slices with type glyph and
## output, pointers, inner ring segments, statuses, docked satellites and vitals.
## View only: it never changes game state.

const SLICE_COLORS := {
	RC.SliceType.ATTACK: Color(0.85, 0.3, 0.3),
	RC.SliceType.CRIT: Color(1.0, 0.45, 0.2),
	RC.SliceType.DEFEND: Color(0.3, 0.55, 0.9),
	RC.SliceType.SHIELD: Color(0.4, 0.8, 0.9),
	RC.SliceType.EVADE: Color(0.5, 0.8, 0.5),
	RC.SliceType.DEPLOY: Color(0.7, 0.5, 0.9),
	RC.SliceType.HEAL: Color(0.4, 0.9, 0.5),
	RC.SliceType.AFFLICT: Color(0.8, 0.2, 0.7),
	RC.SliceType.MISS: Color(0.35, 0.35, 0.35),
}
const GLYPHS := {
	RC.SliceType.ATTACK: "ATK", RC.SliceType.CRIT: "CRIT", RC.SliceType.DEFEND: "DEF",
	RC.SliceType.SHIELD: "SHD", RC.SliceType.EVADE: "EVD", RC.SliceType.DEPLOY: "DEP",
	RC.SliceType.HEAL: "HEAL", RC.SliceType.AFFLICT: "AFL", RC.SliceType.MISS: "MISS",
}
const STATUS_TAGS := {RC.Status.CORRUPTED: "CRPT", RC.Status.OVERCLOCKED: "OVCL", RC.Status.ENCRYPTED: "ENC"}

var combatant: CombatantState = null
var satellites: Array[CombatantState] = []
var readouts: Array[Dictionary] = []
var lookup: ContentLookup = null
var highlighted: bool = false


func _init() -> void:
	custom_minimum_size = Vector2(360, 330)


## Updates what the view shows. `p_satellites` are the drones docked on this wheel.
func show_combatant(c: CombatantState, p_satellites: Array[CombatantState], p_readouts: Array[Dictionary], p_lookup: ContentLookup) -> void:
	combatant = c
	satellites = p_satellites
	readouts = p_readouts
	lookup = p_lookup
	queue_redraw()


func _tick_angle(tick: float, rotation_ticks: int) -> float:
	# Tick `rotation` sits under the top pointer (GDD 2.3).
	var shown := rotation_ticks
	return deg_to_rad((tick - shown) * (360.0 / RC.TICKS) - 90.0)


func _draw() -> void:
	if combatant == null or combatant.wheel == null:
		draw_string(get_theme_default_font(), Vector2(8, 20), "(no wheel)")
		return
	var wheel := combatant.wheel
	var center := Vector2(size.x / 2.0, size.y / 2.0 + 10)
	var radius := minf(size.x, size.y) * 0.32
	var font := get_theme_default_font()
	if highlighted:
		draw_arc(center, radius + 34, 0, TAU, 64, Color(1, 0.85, 0.2, 0.6), 3)
	var tps := wheel.ticks_per_slice()
	for i in wheel.slice_count:
		var slice := lookup.get_content(wheel.slot_slice_ids[i]) as SliceData
		var start := _tick_angle(i * tps - tps / 2.0, wheel.rotation)
		var end := _tick_angle(i * tps + tps / 2.0, wheel.rotation)
		var color: Color = SLICE_COLORS.get(slice.slice_type, Color.GRAY)
		if not combatant.is_alive():
			color = color.darkened(0.6)
		draw_arc(center, radius, start, end, 12, color, 26)
		var mid := _tick_angle(i * tps, wheel.rotation)
		var pos := center + Vector2(cos(mid), sin(mid)) * (radius + 26)
		var label := "%s %d" % [GLYPHS.get(slice.slice_type, "?"), slice.base_output]
		if slice.base_output == 0:
			label = GLYPHS.get(slice.slice_type, "?")
		var status: int = wheel.slice_statuses[i]
		if status != RC.Status.NONE:
			label += " [%s]" % STATUS_TAGS.get(status, "?")
		if wheel.slot_firmware_ids[i] != &"":
			label += " {%s}" % wheel.slot_firmware_ids[i]
		draw_string(font, pos - Vector2(22, -4), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 11)
		for sat in satellites:
			if sat.dock_slot == i:
				var sat_pos := center + Vector2(cos(mid), sin(mid)) * (radius + 44)
				draw_circle(sat_pos, 8, Color(0.9, 0.7, 0.2))
				draw_string(font, sat_pos + Vector2(-16, 20), "drone %d HP" % sat.hp, HORIZONTAL_ALIGNMENT_LEFT, -1, 10)
	# Tick marks so nudges are visible.
	for t in RC.TICKS:
		var a := _tick_angle(t, wheel.rotation)
		var inner_r := radius - 15 if t % tps == 0 else radius - 13
		draw_line(center + Vector2(cos(a), sin(a)) * inner_r, center + Vector2(cos(a), sin(a)) * (radius - 10), Color(0, 0, 0, 0.6), 1)
	if wheel.has_inner_ring():
		var ring_r := radius - 32
		for k in RC.RING_SEGMENTS:
			var seg := lookup.get_content(wheel.ring_segment_ids[k]) as RingSegmentData
			var start := _tick_angle(k * 10 - 5, wheel.inner_rotation)
			var end := _tick_angle(k * 10 + 5, wheel.inner_rotation)
			draw_arc(center, ring_r, start, end, 12, Color(0.6, 0.6, 0.9) if k % 2 == 0 else Color(0.45, 0.45, 0.75), 14)
			var mid := _tick_angle(k * 10, wheel.inner_rotation)
			var pos := center + Vector2(cos(mid), sin(mid)) * (ring_r)
			draw_string(font, pos - Vector2(8, -4), seg.display_name if seg != null else "?", HORIZONTAL_ALIGNMENT_LEFT, -1, 10)
	for p in wheel.pointer_ticks:
		var a := deg_to_rad(p * (360.0 / RC.TICKS) - 90.0)
		var tip := center + Vector2(cos(a), sin(a)) * (radius - 18)
		var base := center + Vector2(cos(a), sin(a)) * (radius + 16)
		draw_line(base, tip, Color.WHITE, 3)
		draw_circle(tip, 4, Color.WHITE)
	var hub := "" if wheel.hub_id == &"" else String(wheel.hub_id)
	if combatant.is_hub_breached():
		hub += " (BREACHED)"
	var lines := [
		combatant.display_name,
		"HP %d/%d  BLK %d  SHD %d" % [combatant.hp, combatant.max_hp, combatant.block, combatant.shield],
	]
	if combatant.resistance > 0 or combatant.hub_resistance > 0 or wheel.passive_resistance > 0:
		lines.append("resist %d" % combatant.resistance)
	if wheel.frozen:
		lines.append("FROZEN")
	if hub != "":
		lines.append(hub)
	for r in readouts:
		var slice: SliceData = r["slice"]
		var tier_text: String = RC.PrecisionTier.keys()[r["tier"]] if wheel.slice_count == RC.SLICES else "full"
		var text := "P%d: %s %s" % [r["pointer_index"], GLYPHS.get(slice.slice_type, "?"), tier_text]
		if r["segment"] != null:
			text += " ring:%s" % r["segment"].display_name
		if r["guard_id"] != &"":
			text += " guarded"
		lines.append(text)
	for i in lines.size():
		draw_string(font, Vector2(center.x - 60, center.y - 30 + i * 13), lines[i], HORIZONTAL_ALIGNMENT_LEFT, 130, 10)
