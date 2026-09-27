class_name WheelView
extends Control
## The spinner (STYLE_GUIDE 4, combat pass): neon gauge bars, one wedge per slice with its
## drawn icon inside and its value outside, a small white "perfect" arrow inside each
## slice at its outer edge, white gauge-needle pointers, a segmented HP arc underneath
## with the numbers in its gap, the name in the hub, and a taped tag above: what the
## needle lands on and every result the end of the turn brings (H20: chips for damage,
## block, statuses, RAM, Heat... instead of a text list).
## H20 also adds: curved nudge arrows (top left turns the wheel anticlockwise, top right
## clockwise: a nudge to the right turns the top of the wheel to the right), a target
## marker, predicted HP loss on the HP arc, and drop zones for dragged cards (the wheel,
## a nudge arrow, a slice, a docked satellite).
## Also: statuses, firmware, docked satellites, the inner ring, the dashed acid ghost
## preview, orbit trails, telegraphed migrations. Readable without colour.
## View only: never changes game state; it emits what the player points at.

## Mouse on a nudge arrow (ring, direction +1 clockwise / -1 anticlockwise).
signal arrow_pressed(ring: int, direction: int)
## The mouse moved onto a nudge arrow ({kind: "arrow", ring, direction}) or off it ({}).
signal arrow_hovered(zone: Dictionary)
## Left click anywhere else on the view: the zone under the mouse (see zone_at).
signal zone_clicked(zone: Dictionary)
## A card dragged over this view ({} when it leaves a zone) and dropped on it.
signal drag_hovered(zone: Dictionary, data: Dictionary)
signal drag_dropped(zone: Dictionary, data: Dictionary)

var combatant: CombatantState = null
var satellites: Array[CombatantState] = []
var readouts: Array[Dictionary] = []
var lookup: ContentLookup = null
## This wheel is the current target (drawn as a crosshair ring).
var highlighted: bool = false
## A docked satellite that is the current target ("" = none).
var targeted_satellite: StringName = &""
## What each docked satellite's needle lands on: id -> {type, tier, text} (from the scene).
var satellite_landings: Dictionary = {}
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
## What resolves next for this combatant: {"type": slice type or -1, "text": String,
## "chips": Array of {"text", "color"}}; empty = no tag.
var intent: Dictionary = {}
## Predicted end state from CombatOutcome (hp_after, block_after, statuses...): drawn as
## the HP ghost, status ghosts and a DOWN mark. Empty = no preview.
var outcome: Dictionary = {}
## What the last SEND IT did to this combatant ("" = nothing yet), drawn under the HP
## number until the player acts (H21: after SEND IT nothing showed what happened; the
## motion pass adds floating numbers on top of this).
var last_turn: String = ""
## Horizontal position of the wheel centre as a fraction of the view's width (of the
## width right of `left_reserve`).
var center_x: float = 0.5
## Pixels kept free on the left for controls: the wheel centres in the rest.
var left_reserve: float = 0.0
## Nudge arrows are drawn and clickable (the player's wheel and every enemy wheel).
var show_arrows: bool = true
## Key hints drawn by the arrows (the wheel the nudge keys drive): {direction: "[Q]"}.
var arrow_hints: Dictionary = {}
## The ring the nudge keys drive on this wheel (its arrows are marked).
var key_ring: int = RC.RingScope.OUTER
## Drop zones valid for the card being played (drawn as dashed outlines), and the zone
## the player points at now.
var valid_zones: Array[Dictionary] = []
var hover_zone: Dictionary = {}
## The arrow under the mouse (lit on hover).
var _mouse_zone: Dictionary = {}

## Share of the view's smaller side used as the wheel radius.
const RADIUS_SHARE := 0.26
## Space kept round the disc for the values drawn outside the slices (px).
const DISC_MARGIN := 30.0
## The wheel never shrinks below this radius (px).
const MIN_RADIUS := 60.0
## Everything drawn round the disc (values, satellites, HP arc and numbers) stays within
## radius + EXTENT (layout checks use it: nothing zine may cover it).
const EXTENT := 66.0
const DEG_PER_TICK := 360.0 / RC.TICKS
## Nudge arrows: angle off the top, radius beyond the rim, half-length (degrees), and the
## inner ring's arrows one tier further out.
const ARROW_ANGLE := 40.0
const ARROW_RADIUS := 48.0
const ARROW_INNER_RADIUS := 74.0
const ARROW_SPAN := 13.0
const ARROW_HIT := 18.0
## Satellite marker hit radius (px at text scale 1.0).
const SATELLITE_HIT := 14.0
## Slice values sit this far outside the rim; satellites dock beyond them with this gap.
const VALUE_OUT := 16.0
const SATELLITE_GAP := 12.0
## At big text the wheel never shrinks below this share of its unconstrained size (H22:
## at 1.6 it went from 126 to 62 px and names were cut).
const RADIUS_FLOOR := 0.8
## At the biggest text the wheel keeps at least this share of its 1.0-scale radius: the
## title row and the HP block grow with the text and the view's height is fixed (H23).
const BIG_TEXT_RADIUS_KEEP := 0.75
## A satellite's hex token radius (px at text scale 1.0).
const SATELLITE_TOKEN := 11.0
## Tokens below this sine of their angle (the bottom sector) keep to the side of the HP
## block, whose half width is about this (px at text scale 1.0).
const BOTTOM_SECTOR_SIN := 0.8
const HP_BLOCK_HALF := 90.0
## Aim quality pips on the tag (1 = half power, 2 = good, 3 = perfect).
const TIER_PIPS := {RC.PrecisionTier.PARTIAL: 1, RC.PrecisionTier.GOOD: 2, RC.PrecisionTier.PERFECT: 3}
const PIP_RADIUS := 3.0
## Tag rows kept on screen: the title and at most this many chip rows (the rest fold into
## a "+N" chip; the tooltip lists them all).
const TAG_CHIP_ROWS := 2
## HP arc and number below the rim (px): the arc's outer edge, then the number's offset.
const HP_ARC_OUT := 40.0
const HP_TEXT_GAP := 44.0
## Gap between the HP number and the last-turn line (px).
const LAST_TURN_GAP := 4.0
## Lettering sizes at text scale 1.0.
const INTENT_FONT_SIZE := 15
const CHIP_FONT_SIZE := 13
const HUB_FONT_SIZE := 10
const NAME_FONT_SIZE := 13
const VALUE_FONT_SIZE := 20
const HP_FONT_SIZE := 22
const INTENT_HEIGHT := 30.0
const CHIP_HEIGHT := 20.0
## The widest a tag may get before its chips wrap (fraction of the view width).
const TAG_MAX_SHARE := 0.96
const HP_COLOR := Color("#3DFF8B")
const LOSS_COLOR := Color("#FF4D4D")
const TARGET_COLOR := Palette.CELL_ACID


func _init() -> void:
	custom_minimum_size = Vector2(330, 330)
	# PASS: hover tooltips on slices; clicks still reach the scene.
	mouse_filter = Control.MOUSE_FILTER_PASS
	tooltip_text = " "


static func _ts() -> float:
	return Settings.text_scale


static func _fs(base: int) -> int:
	return roundi(base * _ts())


## Hover: what is under the mouse (a nudge arrow, a slice, a satellite, the hub).
func _get_tooltip(at_position: Vector2) -> String:
	if combatant == null:
		return ""
	if _intent_rect_local().has_point(at_position):
		return String(intent.get("tooltip", ""))
	var z := zone_at(global_position + at_position)
	match String(z.get("kind", "")):
		"arrow":
			var which := "clockwise" if int(z["direction"]) > 0 else "anticlockwise"
			var ring := " the inner ring" if int(z["ring"]) == RC.RingScope.INNER else ""
			return "Nudge %s%s one tick %s.\nDrop a nudge card here to aim it this way." % [combatant.display_name, ring, which]
		"satellite":
			var sat := _satellite(StringName(z["id"]))
			if sat == null:
				return ""
			var land: Dictionary = satellite_landings.get(sat.id, {})
			return "%s (%d HP): takes hits aimed at the slice it guards.%s" % [sat.display_name, sat.hp,
				("\nIts needle lands on %s." % String(land["text"])) if not land.is_empty() else ""]
		"slot":
			return _slice_label(int(z["slot"]))
		"hub":
			var lines := PackedStringArray([combatant.display_name])
			if combatant.block > 0:
				lines.append("Block %d: soaks damage this turn." % combatant.block)
			if combatant.shield > 0:
				lines.append("Shield %d: soaks damage, lasts." % combatant.shield)
			if combatant.resistance > 0:
				lines.append("Resistance %d: absorbs nudges and spins tick for tick; Flip and Respin are blocked." % combatant.resistance)
			if combatant.wheel.hub_id != &"" and lookup != null:
				lines.append(Codex.describe(lookup.get_content(combatant.wheel.hub_id)))
			return "\n".join(lines)
	return ""


func _slice_label(i: int) -> String:
	var wheel := combatant.wheel
	var slice := lookup.get_content(wheel.slot_slice_ids[i]) as SliceData
	var parts := PackedStringArray([Codex.describe(slice) if slice != null else "?"])
	var status: int = wheel.slice_statuses[i]
	if status != RC.Status.NONE:
		parts.append(Codex.status_text(status))
	if wheel.slot_firmware_ids[i] != &"":
		parts.append(Codex.describe(lookup.get_content(wheel.slot_firmware_ids[i])))
	return "\n".join(parts)


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


# --- Geometry ---------------------------------------------------------------------------

## The wheel's disc (slices and needles) on screen.
func wheel_rect() -> Rect2:
	var center := _center()
	var r := _radius() + 22
	return Rect2(global_position + center - Vector2(r, r), Vector2(r * 2, r * 2))


## Centre of the disc on screen.
func global_center() -> Vector2:
	return global_position + _center()


## Radius (px) within which everything drawn round the disc lies (values, satellites,
## the HP arc and its numbers).
func extent_radius() -> float:
	return _radius() + maxf(EXTENT, HP_TEXT_GAP + _fs(HP_FONT_SIZE) + LAST_TURN_GAP + _fs(HUB_FONT_SIZE))


## Whether `r` (global) covers any of the wheel's drawing (a circle test, not a box).
func covers(r: Rect2) -> bool:
	if combatant == null:
		return false
	var c := global_center()
	var nearest := Vector2(clampf(c.x, r.position.x, r.end.x), clampf(c.y, r.position.y, r.end.y))
	return nearest.distance_to(c) < extent_radius()


## Slot index under a global point on the outer ring band, or -1 outside the wheel.
func slot_at_global(point: Vector2) -> int:
	if combatant == null or combatant.wheel == null:
		return -1
	var local := point - global_position - _center()
	var dist := local.length()
	var radius := _radius()
	if dist < radius - _band() - 4 or dist > radius + 30:
		return -1
	# Mirror of _ang(): screen angle -> ticks from the pointer's zero.
	var x := -(rad_to_deg(atan2(local.y, local.x)) + 90.0) / DEG_PER_TICK
	var tick := posmod(roundi(x) + combatant.wheel.rotation, RC.TICKS)
	return WheelMath.slice_at(tick, combatant.wheel.slice_count)


## Whether a global point is inside the wheel disc (hub included).
func contains_global(point: Vector2) -> bool:
	return wheel_rect().has_point(point)


## Centre of a nudge arrow on screen.
func arrow_center(ring: int, direction: int) -> Vector2:
	var r := _radius() + (ARROW_INNER_RADIUS if ring == RC.RingScope.INNER else ARROW_RADIUS)
	var a := deg_to_rad(-90.0 + ARROW_ANGLE * signf(direction))
	return global_position + _center() + Vector2(cos(a), sin(a)) * r


## Where a zone sits on screen (the aim line from a card ends there).
func zone_center(zone: Dictionary) -> Vector2:
	match String(zone.get("kind", "")):
		"arrow":
			return arrow_center(int(zone["ring"]), int(zone["direction"]))
		"satellite":
			var sat := _satellite(StringName(zone["id"]))
			return _satellite_pos(sat) if sat != null else global_center()
		"slot":
			var tps := combatant.wheel.ticks_per_slice()
			var a := _ang(int(zone["slot"]) * tps - combatant.wheel.rotation)
			return global_center() + Vector2(cos(a), sin(a)) * (_radius() - _band() * 0.5)
	return global_center()


## Nudge arrows this wheel offers: [{ring, direction}].
func arrows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if combatant == null or not show_arrows or not combatant.is_alive():
		return out
	var rings: Array[int] = [RC.RingScope.OUTER]
	if combatant.wheel.has_inner_ring():
		rings.append(RC.RingScope.INNER)
	for ring in rings:
		for d in [-1, 1]:
			out.append({"ring": ring, "direction": d})
	return out


## What the player points at: {"kind": "arrow", ring, direction} / {"kind": "satellite",
## id} / {"kind": "slot", slot} / {"kind": "hub"} / {} (nothing).
func zone_at(point: Vector2) -> Dictionary:
	if combatant == null:
		return {}
	# Satellites first (H22: at big text a satellite near the top sat inside an arrow's hit
	# area and couldn't be aimed at).
	for sat in satellites:
		var sp := _satellite_pos(sat)
		if sp.distance_to(point) <= SATELLITE_HIT * maxf(1.0, _ts()):
			# Which side of the satellite: the clockwise side is +1 (a nudge or Undock aimed
			# at a satellite takes its way from the side it is dropped on).
			var cw := (sp - global_center()).orthogonal() * -1.0
			return {"kind": "satellite", "id": sat.id, "direction": 1 if (point - sp).dot(cw) >= 0.0 else -1}
	for ar in arrows():
		if arrow_center(int(ar["ring"]), int(ar["direction"])).distance_to(point) <= ARROW_HIT * maxf(1.0, _ts()):
			return {"kind": "arrow", "ring": ar["ring"], "direction": ar["direction"]}
	var slot := slot_at_global(point)
	if slot >= 0:
		return {"kind": "slot", "slot": slot}
	if global_center().distance_to(point) < _radius():
		return {"kind": "hub"}
	return {}


func _satellite(id: StringName) -> CombatantState:
	for s in satellites:
		if s.id == id:
			return s
	return null


func _satellite_pos(sat: CombatantState) -> Vector2:
	var tps := combatant.wheel.ticks_per_slice()
	var a := _ang(sat.dock_slot * tps - combatant.wheel.rotation)
	var p := global_center() + Vector2(cos(a), sin(a)) * (_radius() + _satellite_out())
	# In the bottom sector the HP number, NEXT plate and last-turn line sit under the disc:
	# a token there moves to the side of them (H23: it covered "40/40").
	if sin(a) > BOTTOM_SECTOR_SIN:
		var side := 1.0 if cos(a) >= 0.0 else -1.0
		p.x = global_center().x + side * maxf(absf(p.x - global_center().x), HP_BLOCK_HALF * _ts() + SATELLITE_TOKEN * _ts())
	return p


## How far outside the rim satellites dock: past the slice values (H22: they sat on them).
static func _satellite_out() -> float:
	return VALUE_OUT + _fs(VALUE_FONT_SIZE) * 0.5 + SATELLITE_GAP * _ts()


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var z := zone_at((event as InputEventMouseButton).global_position)
		if String(z.get("kind", "")) == "arrow":
			arrow_pressed.emit(int(z["ring"]), int(z["direction"]))
			accept_event()
			return
		zone_clicked.emit(z)
	elif event is InputEventMouseMotion:
		var z := zone_at((event as InputEventMouseMotion).global_position)
		var hot := String(z.get("kind", "")) == "arrow"
		mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND if hot else Control.CURSOR_ARROW
		var mz: Dictionary = z if hot else {}
		if mz != _mouse_zone:
			_mouse_zone = mz
			arrow_hovered.emit(mz)
			queue_redraw()


# --- Drag and drop (cards) -----------------------------------------------------------------

func _can_drop_data(at_position: Vector2, data: Variant) -> bool:
	if not (data is Dictionary) or not (data as Dictionary).has("hand_index"):
		return false
	var z := zone_at(global_position + at_position)
	drag_hovered.emit(z, data)
	return not z.is_empty()


func _drop_data(at_position: Vector2, data: Variant) -> void:
	drag_dropped.emit(zone_at(global_position + at_position), data)


func _notification(what: int) -> void:
	if what == NOTIFICATION_MOUSE_EXIT:
		if not _mouse_zone.is_empty():
			_mouse_zone = {}
			arrow_hovered.emit({})
			queue_redraw()
		if get_viewport() != null and get_viewport().gui_is_dragging():
			drag_hovered.emit({}, get_viewport().gui_get_drag_data())


func _corporation_of(c: CombatantState) -> StringName:
	var data := lookup.get_content(c.source_id) if lookup != null else null
	return data.corporation_id if data != null and "corporation_id" in data else &""


## Vertical position of the wheel centre as a fraction of the view's height.
const CENTER_Y := 0.56
## Width of the slice band as a share of the radius.
const BAND_SHARE := 0.34


func _center() -> Vector2:
	# The centre sits at CENTER_Y, raised when the HP number and the last-turn line need
	# the room below (H23: the fixed centre left 210 px above and pinned the wheel small).
	var cy := minf(size.y * CENTER_Y, size.y - _bottom_need() - _radius())
	return Vector2(left_reserve + (size.x - left_reserve) * center_x, cy) + shake


## Room kept under the disc for the HP number and the last-turn line (px).
static func _bottom_need() -> float:
	return HP_TEXT_GAP + _fs(HP_FONT_SIZE) + _fs(HUB_FONT_SIZE) + LAST_TURN_GAP + DISC_MARGIN * 0.2


func _radius() -> float:
	var r := minf(size.x, size.y) * RADIUS_SHARE
	if left_reserve > 0.0:
		var avail := size.x - left_reserve
		r = minf(r, minf(avail * center_x, avail * (1.0 - center_x)) - DISC_MARGIN)
	# Vertically the disc (r above with its band, r below), the tag above and the HP number
	# and last-turn line below share the view's height; the centre moves to fit (_center).
	# Everything fits at r_full; below that the tag may clamp under the arrows down to
	# RADIUS_FLOOR of the unconstrained size, as long as its title row still fits (H23).
	var span := 2.0 + BAND_SHARE
	var r_full := (size.y - _bottom_need() - INTENT_HEIGHT - _tag_reserve()) / span
	var r_title := (size.y - _bottom_need() - INTENT_HEIGHT * _ts()) / span
	r = minf(r, maxf(r_full, minf(r_title, r * RADIUS_FLOOR)))
	return maxf(MIN_RADIUS, r)


## Height kept for the tag at the current text scale (title and TAG_CHIP_ROWS rows).
static func _tag_reserve() -> float:
	return INTENT_HEIGHT * _ts() + _chip_row_cap() * (CHIP_HEIGHT * _ts() + 2.0)


## Chip rows kept: fewer at big text so the wheel doesn't shrink away (H22).
static func _chip_row_cap() -> int:
	return 1 if _ts() > BIG_TEXT else TAG_CHIP_ROWS


## Above this text scale the tag keeps one chip row.
const BIG_TEXT := 1.3


## Width of the slice bar band.
func _band() -> float:
	return _radius() * BAND_SHARE


## Screen angle of a position `x` ticks round from the top, clockwise on screen when the
## wheel's rotation grows (H20: +1 turns the wheel clockwise, as a right nudge reads).
static func _ang(x: float) -> float:
	return deg_to_rad(-x * DEG_PER_TICK - 90.0)


func _tick_angle(tick: float, rotation_ticks: int) -> float:
	return _ang(tick - rotation_ticks)


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


# --- Drawing --------------------------------------------------------------------------------

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
	var status_ghosts := {}
	for st in outcome.get("statuses", []):
		status_ghosts[int(st["slot"])] = int(st["after"])
	# Slices: neon bars, icon inside, value outside, the perfect arrow at the outer edge.
	for i in wheel.slice_count:
		var slice := lookup.get_content(wheel.slot_slice_ids[i]) as SliceData
		var a0 := _tick_angle(i * tps - tps / 2.0, wheel.rotation)
		var a1 := _tick_angle(i * tps + tps / 2.0, wheel.rotation)
		var mid := _tick_angle(i * tps, wheel.rotation)
		var sc := Palette.slice_color(slice.slice_type)
		var wedge := _wedge(center, inner, radius, minf(a0, a1) + 0.03, maxf(a0, a1) - 0.03)
		if slice.slice_type == RC.SliceType.MISS:
			draw_colored_polygon(wedge, _col(Color(sc, 0.18)))
			_draw_dashed_arc(center, radius - 1, minf(a0, a1) + 0.03, maxf(a0, a1) - 0.03, line, 1.5)
			_draw_dashed_arc(center, inner + 1, minf(a0, a1) + 0.03, maxf(a0, a1) - 0.03, line, 1.5)
		else:
			# Translucent neon: the city shows through, a bright rim keeps the shape.
			draw_colored_polygon(wedge, _col(Color(sc, 0.5)))
			var closed := wedge.duplicate()
			closed.append(wedge[0])
			draw_polyline(closed, _col(Color(sc.lightened(0.35), 0.95)), 1.8, true)
		if _zone_is(valid_zones, {"kind": "slot", "slot": i}):
			var hot := _zone_is([hover_zone], {"kind": "slot", "slot": i})
			draw_polyline(wedge, _col(TARGET_COLOR if hot else Color(TARGET_COLOR, 0.55)), 3.0 if hot else 1.5, true)
		var dir := Vector2(cos(mid), sin(mid))
		SliceIcon.draw_on_slice(self, center + dir * (inner + band * 0.42), band * 0.36, slice.slice_type, sc)
		if slice.base_output > 0:
			var vs := _fs(VALUE_FONT_SIZE)
			draw_string(Palette.display(), center + dir * (radius + VALUE_OUT) + Vector2(-vs, vs * 0.4), str(slice.base_output), HORIZONTAL_ALIGNMENT_CENTER, vs * 2, vs, _col(sc.lightened(0.35)))
		var tip := center + dir * (radius - 3)
		var base := center + dir * (radius - 10)
		var side := dir.orthogonal() * 4.0
		draw_colored_polygon(PackedVector2Array([tip, base + side, base - side]), _col(Palette.PAPER))
		var status: int = wheel.slice_statuses[i]
		var sp := center + dir * (inner + band * 0.5) + dir.orthogonal() * band * 0.42
		if status != RC.Status.NONE:
			draw_circle(sp, 7, Palette.NIGHT_SKY)
			draw_string(Palette.mono(), sp + Vector2(-7, 5), Palette.STATUS_GLYPHS.get(status, ""), HORIZONTAL_ALIGNMENT_CENTER, 14, 11, _col(Palette.CELL_ACID))
		if status_ghosts.has(i):
			# The status this turn will leave on the slice: a dashed acid ring (or a cross
			# when it clears).
			_draw_dashed_arc(sp, 10, 0, TAU, _col(Palette.CELL_ACID), 1.5)
			var g: int = status_ghosts[i]
			draw_string(Palette.mono(), sp + Vector2(-7, 5), Palette.STATUS_GLYPHS.get(g, "×") if g != RC.Status.NONE else "×", HORIZONTAL_ALIGNMENT_CENTER, 14, 11, _col(Palette.CELL_ACID))
		if wheel.slot_firmware_ids[i] != &"":
			var fp := center + dir * (inner + 5) - dir.orthogonal() * band * 0.3
			draw_rect(Rect2(fp - Vector2(3, 3), Vector2(6, 6)), _col(Palette.NET_CYAN))
	for sat in satellites:
		var satp := _satellite_pos(sat) - global_position
		var sat_col := _col(Palette.CELL_ACID if sat.is_player else Palette.RESIST_GOLD)
		# A hex token with the slice its own needle lands on (its wheel, GDD 2.10) and its HP
		# on a plate beside it; the name and the slice words are the tooltip (H22).
		var tok_r := SATELLITE_TOKEN * _ts()
		var hex := PackedVector2Array()
		for k in 7:
			var ha := TAU * k / 6.0 + PI / 6.0
			hex.append(satp + Vector2(cos(ha), sin(ha)) * tok_r)
		draw_colored_polygon(hex, Color(Palette.NIGHT_SKY, 0.9))
		draw_polyline(hex, sat_col, 2.0)
		var land: Dictionary = satellite_landings.get(sat.id, {})
		if not land.is_empty():
			SliceIcon.draw_icon(self, satp, tok_r * 0.6, int(land["type"]), Palette.slice_color(int(land["type"])))
		var sat_out: Dictionary = outcome.get("satellites", {}).get(sat.id, {})
		var sat_text := "%d" % sat.hp
		if not sat_out.is_empty() and int(sat_out.get("hp_after", sat.hp)) != sat.hp:
			sat_text += " >%d" % int(sat_out["hp_after"]) if bool(sat_out.get("alive_after", true)) else " >x"
		var out_dir := (satp - _center()).normalized()
		var lfs := _fs(HUB_FONT_SIZE + 1)
		var lw := Palette.mono().get_string_size(sat_text, HORIZONTAL_ALIGNMENT_LEFT, -1, lfs).x
		var lp := satp + out_dir * (tok_r + lfs) - Vector2(lw * 0.5, -lfs * 0.35)
		draw_rect(Rect2(lp - Vector2(3, lfs), Vector2(lw + 6, lfs + 5)), Color(Palette.NIGHT_SKY, 0.85))
		draw_string(Palette.mono(), lp, sat_text, HORIZONTAL_ALIGNMENT_LEFT, -1, lfs, sat_col)
		if sat.id == targeted_satellite:
			_draw_crosshair(satp, (SATELLITE_TOKEN + 5.0) * _ts())
		if _zone_is(valid_zones, {"kind": "satellite", "id": sat.id}):
			var hot := _zone_is([hover_zone], {"kind": "satellite", "id": sat.id})
			draw_arc(satp, (SATELLITE_TOKEN + 3.0) * _ts(), 0, TAU, 20, _col(TARGET_COLOR if hot else Color(TARGET_COLOR, 0.55)), 3.0 if hot else 1.5)
			# A play with a way (a nudge card, Undock) marks each side: drop on the side it
			# should turn to (the clockwise side is +1).
			var cw := (satp - _center()).normalized().orthogonal() * -1.0
			for z in valid_zones:
				if String(z.get("kind", "")) == "satellite" and z.get("id") == sat.id and z.has("direction"):
					var d := float(z["direction"])
					var side_hot := hot and int(hover_zone.get("direction", 0)) == int(d)
					var tip := satp + cw * d * 21.0
					var back := satp + cw * d * 13.0
					var n := cw.orthogonal() * 5.0
					draw_colored_polygon(PackedVector2Array([tip, back + n, back - n]), _col(TARGET_COLOR if side_hot else Color(TARGET_COLOR, 0.55)))
	draw_arc(center, radius, 0, TAU, 96, Color(line, 0.9), 1.5)
	draw_arc(center, inner, 0, TAU, 96, Color(line, 0.6), 1.0)
	if wheel.has_inner_ring():
		var ring_r := inner - 12
		for k in RC.RING_SEGMENTS:
			var seg := lookup.get_content(wheel.ring_segment_ids[k]) as RingSegmentData
			var s0 := _tick_angle(k * 10 - 5, wheel.inner_rotation)
			var e0 := _tick_angle(k * 10 + 5, wheel.inner_rotation)
			draw_arc(center, ring_r, minf(s0, e0), maxf(s0, e0), 12, Color(line, 0.35 if k % 2 == 0 else 0.2), 9.0)
			var m := _tick_angle(k * 10, wheel.inner_rotation)
			draw_string(Palette.mono(), center + Vector2(cos(m), sin(m)) * (ring_r - 14) + Vector2(-8, 4), seg.display_name if seg != null else "?", HORIZONTAL_ALIGNMENT_LEFT, -1, mini(_fs(9), 12), _col(Palette.PAPER))
	# Pointers: short white gauge needles, hub just outside the rim, tip just past its edge.
	var pcol := Color(_col(Palette.PAPER), pointer_alpha)
	for p in wheel.pointer_ticks:
		var a := _ang(p)
		var dir := Vector2(cos(a), sin(a))
		var hub := center + dir * (radius + band * 0.55)
		var ntip := center + dir * (radius - band * 0.2)
		draw_colored_polygon(PackedVector2Array([ntip, hub + dir.orthogonal() * 4.0, hub - dir.orthogonal() * 4.0]), pcol)
		draw_circle(hub, 9, Palette.NIGHT_SKY)
		draw_arc(hub, 9, 0, TAU, 20, pcol, 2.5)
		draw_circle(hub, 3, pcol)
		if wheel.pointer_orbit != 0:
			for k in range(1, 4):
				var oa := _ang(posmod(p + wheel.pointer_orbit * k, RC.TICKS))
				draw_circle(center + Vector2(cos(oa), sin(oa)) * (radius + band * 0.55), 3, Color(Palette.PAPER, 0.5 - k * 0.12))
	# Telegraphed migration (GDD 2.11, 9.2): next turn's needles, dashed and flickering.
	for p in wheel.pending_pointer_ticks:
		var a := _ang(p)
		var ntip := center + Vector2(cos(a), sin(a)) * (radius - band * 0.2)
		var hub := center + Vector2(cos(a), sin(a)) * (radius + band * 0.55)
		var mcol := Color(_col(Palette.CELL_ACID), 1.2 - pointer_alpha)
		var n := 6
		for k in n:
			if k % 2 == 0:
				draw_line(hub.lerp(ntip, float(k) / n), hub.lerp(ntip, float(k + 1) / n), mcol, 3.0)
		draw_string(Palette.mono(), hub + Vector2(10, -4), "next", HORIZONTAL_ALIGNMENT_LEFT, -1, _fs(HUB_FONT_SIZE), mcol)
	_draw_ghost(center, radius, wheel)
	_draw_inner_ghost(center, radius, wheel)
	_draw_hp(center, radius)
	_draw_hub(center, inner, line)
	if highlighted and combatant.is_alive():
		_draw_crosshair(center, radius + 56)
		# A crosshair mark by the top-right bracket names the reticle without words.
		var cm := center + Vector2(cos(-PI * 0.25), sin(-PI * 0.25)) * (radius + 56 + 16)
		draw_arc(cm, 7, 0, TAU, 16, _col(TARGET_COLOR), 2.0)
		draw_line(cm + Vector2(-11, 0), cm + Vector2(11, 0), _col(TARGET_COLOR), 2.0)
		draw_line(cm + Vector2(0, -11), cm + Vector2(0, 11), _col(TARGET_COLOR), 2.0)
	if _zone_is(valid_zones, {"kind": "hub"}):
		var hot := _zone_is([hover_zone], {"kind": "hub"})
		draw_arc(center, inner - 4, 0, TAU, 48, _col(TARGET_COLOR if hot else Color(TARGET_COLOR, 0.55)), 3.0 if hot else 1.5)
	# Intent: a taped paper tag above the needle (what resolves next and its results).
	var tag := _intent_rect_local()
	if tag.has_area():
		_intent_tag(tag)
	_draw_arrows()  # after the tag: the arrows stay on top at big text (H22)


## Ghost preview (GDD 9.2): where the wheel ends up after the hovered card or nudge. A
## dashed acid arc runs from the slice that will arrive to the needle, with an arrowhead in
## the direction the wheel turns and the arriving slice's icon.
func _draw_ghost(center: Vector2, radius: float, wheel: WheelState) -> void:
	if ghost_rotation == null or wheel.pointer_ticks.is_empty():
		return
	var p0: int = wheel.pointer_ticks[0]
	var delta := int(ghost_rotation) - wheel.rotation
	if delta == 0:
		return
	var a_needle := _ang(p0)
	var a_from := _ang(p0 + delta)
	var r := radius + GHOST_OUT  # on the rim, inside the values (H22: it crossed a value)
	_draw_dashed_arc(center, r, minf(a_needle, a_from), maxf(a_needle, a_from), _col(Palette.CELL_ACID), 2.0)
	# Arrowhead at the needle, pointing the way the rim moves.
	var tangent := Vector2(-sin(a_needle), cos(a_needle)) * signf(a_needle - a_from)
	var tip := center + Vector2(cos(a_needle), sin(a_needle)) * r
	var normal := tangent.orthogonal()
	draw_colored_polygon(PackedVector2Array([tip + tangent * 8.0, tip - tangent * 4.0 + normal * 6.0, tip - tangent * 4.0 - normal * 6.0]), _col(Palette.CELL_ACID))
	var slot := WheelMath.slice_at(WheelMath.tick_at(int(ghost_rotation), p0), wheel.slice_count)
	var slice := lookup.get_content(wheel.slot_slice_ids[slot]) as SliceData
	var from := center + Vector2(cos(a_from), sin(a_from)) * r
	draw_circle(from, 11, Palette.NIGHT_SKY)
	if slice != null:
		SliceIcon.draw_icon(self, from, 8, slice.slice_type, Palette.slice_color(slice.slice_type))


## The inner ring's ghost (H21): a dashed arc inside the band from the segment that will
## arrive to the needle, arrowhead the way the ring turns.
func _draw_inner_ghost(center: Vector2, radius: float, wheel: WheelState) -> void:
	if ghost_inner_rotation == null or wheel.pointer_ticks.is_empty() or not wheel.has_inner_ring():
		return
	var delta := int(ghost_inner_rotation) - wheel.inner_rotation
	if delta == 0:
		return
	var p0: int = wheel.pointer_ticks[0]
	var a_needle := _ang(p0)
	var a_from := _ang(p0 + delta)
	var r := radius - _band() - INNER_GHOST_INSET
	_draw_dashed_arc(center, r, minf(a_needle, a_from), maxf(a_needle, a_from), _col(Palette.CELL_ACID), 2.0)
	var tangent := Vector2(-sin(a_needle), cos(a_needle)) * signf(a_needle - a_from)
	var tip := center + Vector2(cos(a_needle), sin(a_needle)) * r
	var normal := tangent.orthogonal()
	draw_colored_polygon(PackedVector2Array([tip + tangent * 7.0, tip - tangent * 3.0 + normal * 5.0, tip - tangent * 3.0 - normal * 5.0]), _col(Palette.CELL_ACID))


## The outer ghost arc runs this far outside the rim (px), inside the values.
const GHOST_OUT := 5.0
## The inner ghost runs this far inside the slice band (px).
const INNER_GHOST_INSET := 12.0


func _draw_arrows() -> void:
	for ar in arrows():
		var ring: int = ar["ring"]
		var d: int = ar["direction"]
		var c := arrow_center(ring, d) - global_position
		var zone := {"kind": "arrow", "ring": ring, "direction": d}
		var hot := _zone_is([hover_zone, _mouse_zone], zone)
		var droppable := _zone_is(valid_zones, zone)
		var col := Palette.PAPER
		if droppable:
			col = TARGET_COLOR
		var width := 4.0 if hot else 2.5
		var r := _radius() + (ARROW_INNER_RADIUS if ring == RC.RingScope.INNER else ARROW_RADIUS)
		var mid := -90.0 + ARROW_ANGLE * d
		var from := deg_to_rad(mid - ARROW_SPAN * d)
		var to := deg_to_rad(mid + ARROW_SPAN * d)
		draw_circle(c, ARROW_HIT * 0.9, Color(Palette.NIGHT_SKY, 0.75 if hot else 0.55))
		draw_arc(_center(), r, minf(from, to), maxf(from, to), 10, _col(col), width, true)
		var tip := _center() + Vector2(cos(to), sin(to)) * r
		var tangent := Vector2(-sin(to), cos(to)) * float(d)
		var normal := tangent.orthogonal()
		draw_colored_polygon(PackedVector2Array([tip + tangent * 7.0, tip - tangent * 3.0 + normal * 6.0, tip - tangent * 3.0 - normal * 6.0]), _col(col))
		if ring == RC.RingScope.INNER:
			draw_string(Palette.mono(), c + Vector2(-8, 18), "IN", HORIZONTAL_ALIGNMENT_CENTER, 16, _fs(HUB_FONT_SIZE), _col(col))
		if ring == key_ring and arrow_hints.has(d):
			var hint := String(arrow_hints[d])
			var fs := _fs(HUB_FONT_SIZE + 1)
			var w := Palette.mono().get_string_size(hint, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			draw_string(Palette.mono(), c + Vector2(-w * 0.5 + d * 22.0, -10), hint, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, _col(Palette.CELL_ACID))


## HP as a segmented arc under the wheel with the numbers in its gap; the preview shows
## the HP the end of the turn leaves: lost segments in red, healed ones bright.
func _draw_hp(center: Vector2, radius: float) -> void:
	var hp_col := _col(HP_COLOR)
	var segs := 20
	var frac := float(combatant.hp) / maxf(1.0, combatant.max_hp)
	var after := int(outcome.get("hp_after", combatant.hp))
	var frac_after := float(after) / maxf(1.0, combatant.max_hp)
	for k in segs:
		var a0 := PI * 0.1 + PI * 0.8 * k / segs
		var a1 := a0 + PI * 0.8 / segs * 0.8
		if absf((a0 + a1) * 0.5 - PI * 0.5) < 0.34:
			continue
		var f := float(k) / segs
		var col := Color(1, 1, 1, 0.1)
		if f < minf(frac, frac_after):
			col = hp_col
		elif f < frac:
			col = _col(LOSS_COLOR)
		elif f < frac_after:
			col = _col(HP_COLOR.lightened(0.5))
		draw_colored_polygon(_wedge(center, radius + 32, radius + HP_ARC_OUT, a0, a1), col)
	# The number is the HP now (it agrees with the top bar); the forecast after SEND IT is a
	# separate dashed plate with an arrow (H22: "60→49" read as a result).
	var hs := _fs(HP_FONT_SIZE)
	var base_y := radius + HP_TEXT_GAP + hs - HP_FONT_SIZE
	var text := "%d/%d" % [combatant.hp, combatant.max_hp]
	var tw := Palette.display().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, hs).x
	draw_string(Palette.display(), center + Vector2(-tw * 0.5, base_y), text, HORIZONTAL_ALIGNMENT_LEFT, -1, hs, hp_col)
	if after != combatant.hp:
		var fs := _fs(HUB_FONT_SIZE + 3)
		var ftext := "NEXT %d" % maxi(0, after)
		var fw := Palette.mono().get_string_size(ftext, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + 22.0
		var fr := Rect2(center + Vector2(tw * 0.5 + 8.0, base_y - hs * 0.75), Vector2(fw, fs + 6.0))
		var fcol := _col(LOSS_COLOR) if after < combatant.hp else _col(HP_COLOR)
		draw_rect(fr, Color(Palette.NIGHT_SKY, 0.8))
		_draw_dashed_rect(fr, fcol)
		var ay := fr.position.y + fr.size.y * 0.5
		draw_colored_polygon(PackedVector2Array([Vector2(fr.position.x + 5, ay - 5), Vector2(fr.position.x + 13, ay), Vector2(fr.position.x + 5, ay + 5)]), fcol)
		draw_string(Palette.mono(), Vector2(fr.position.x + 17, fr.position.y + fs), ftext, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, fcol)
	if last_turn != "":
		# The past, greyed: what the last SEND IT did.
		var box := (radius + HP_ARC_OUT) * 2.0
		var ls := _fs(HUB_FONT_SIZE)
		while ls > 7 and Palette.mono().get_string_size(last_turn, HORIZONTAL_ALIGNMENT_LEFT, -1, ls).x > box:
			ls -= 1  # a long line shrinks to its box (H22: 329 px in a 220 px box at 1.6)
		draw_string(Palette.mono(), center + Vector2(-box * 0.5, base_y + LAST_TURN_GAP + ls), last_turn, HORIZONTAL_ALIGNMENT_CENTER, box, ls, _col(Color(Palette.PAPER, 0.6)))


func _draw_dashed_rect(r: Rect2, col: Color) -> void:
	var pts := [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y), r.position]
	for k in 4:
		var a: Vector2 = pts[k]
		var b: Vector2 = pts[k + 1]
		var n := maxi(2, int(a.distance_to(b) / 6.0))
		for i in n:
			if i % 2 == 0:
				draw_line(a.lerp(b, float(i) / n), a.lerp(b, float(i + 1) / n), col, 1.5)


func _draw_hub(center: Vector2, inner: float, line: Color) -> void:
	var hub_lines: Array[String] = []
	if combatant.block > 0:
		hub_lines.append("BLOCK %d" % combatant.block)
	if combatant.shield > 0:
		hub_lines.append("SHIELD %d" % combatant.shield)
	if combatant.resistance > 0 or combatant.hub_resistance > 0 or combatant.wheel.passive_resistance > 0:
		hub_lines.append("RESIST %d" % combatant.resistance)
	if combatant.wheel.frozen:
		hub_lines.append("FROZEN")
	if combatant.wheel.hub_id != &"":
		var hub_data := lookup.get_content(combatant.wheel.hub_id) if lookup != null else null
		var hub_name: String = TextDb.t(hub_data, "display_name") if hub_data != null and "display_name" in hub_data else String(combatant.wheel.hub_id)
		hub_lines.append(hub_name + (" (BREACHED)" if combatant.is_hub_breached() else ""))
	hub_lines.append_array(extra_lines)
	var hw := (inner - 10) * 2.0
	var fs := _fs(HUB_FONT_SIZE)
	var step := fs + 2
	var top := -6.0 - hub_lines.size() * step * 0.5
	var name := combatant.display_name.to_upper()
	var name_size := _fs(NAME_FONT_SIZE)
	while name_size > 7 and Palette.marker().get_string_size(name, HORIZONTAL_ALIGNMENT_LEFT, -1, name_size).x > hw:
		name_size -= 1  # long names shrink to fit the hub
	draw_string(Palette.marker(), center + Vector2(-hw * 0.5, top), name, HORIZONTAL_ALIGNMENT_CENTER, hw, name_size, _col(line.lightened(0.2)))
	for i in hub_lines.size():
		var col := _col(Palette.RESIST_GOLD) if hub_lines[i].begins_with("RESIST") else _col(Palette.PAPER)
		var lfs := fs
		while lfs > 6 and Palette.mono().get_string_size(hub_lines[i], HORIZONTAL_ALIGNMENT_LEFT, -1, lfs).x > hw:
			lfs -= 1  # shrink to the hub (H23: "Breaker Core" was cut to "Breake")
		var line_text: String = hub_lines[i]
		while line_text.length() > 3 and Palette.mono().get_string_size(line_text, HORIZONTAL_ALIGNMENT_LEFT, -1, lfs).x > hw:
			line_text = line_text.substr(0, line_text.length() - 2) + "…"
		draw_string(Palette.mono(), center + Vector2(-hw * 0.5, top + 16 + i * step), line_text, HORIZONTAL_ALIGNMENT_CENTER, hw, lfs, col)
	if not bool(outcome.get("alive_after", true)) and combatant.is_alive():
		# This turn takes it down: a red cross over the hub.
		var r := inner * 0.55
		draw_line(center + Vector2(-r, -r), center + Vector2(r, r), _col(LOSS_COLOR), 6.0)
		draw_line(center + Vector2(-r, r), center + Vector2(r, -r), _col(LOSS_COLOR), 6.0)


## Target reticle: four bracket arcs on the diagonals with a tick at each (clear of the HP
## numbers and the arrows).
const RETICLE_ARC := 0.28


func _draw_crosshair(c: Vector2, r: float) -> void:
	var col := _col(TARGET_COLOR)
	for k in 4:
		var a := PI * 0.25 + k * PI * 0.5
		draw_arc(c, r, a - RETICLE_ARC, a + RETICLE_ARC, 8, col, 3.0, true)
		var d := Vector2(cos(a), sin(a))
		draw_line(c + d * (r - 8), c + d * (r + 6), col, 3.0)


## Whether `zone` is in `zones` (same kind and same fields).
static func _zone_is(zones: Array, zone: Dictionary) -> bool:
	for z in zones:
		if z is Dictionary and not (z as Dictionary).is_empty() and String(z.get("kind", "")) == String(zone["kind"]):
			var same := true
			for key in zone:
				if key != "kind" and z.get(key) != zone[key]:
					same = false
			if same:
				return true
	return false


# --- The tag ----------------------------------------------------------------------------------

## Chip rows of the tag (wrapped to the view width).
func _chip_rows() -> Array:
	var rows: Array = []
	var chips: Array = intent.get("chips", [])
	if chips.is_empty():
		return rows
	var max_w := size.x * TAG_MAX_SHARE
	var fs := _fs(CHIP_FONT_SIZE)
	var row: Array = []
	var w := 0.0
	for chip in chips:
		var cw := _chip_width(String(chip["text"]), fs)
		if not row.is_empty() and w + cw > max_w:
			rows.append(row)
			row = []
			w = 0.0
		row.append(chip)
		w += cw
	if not row.is_empty():
		rows.append(row)
	var cap := _chip_row_cap()
	if rows.size() > cap:
		# Fold the overflow into a "+N" chip on the last kept row.
		var hidden := 0
		for k in range(cap, rows.size()):
			hidden += (rows[k] as Array).size()
		rows = rows.slice(0, cap)
		var last: Array = rows[cap - 1]
		if not last.is_empty():
			hidden += 1
			last.pop_back()
		last.append({"text": "+%d" % hidden, "color": Palette.INK, "ink": Palette.PAPER})
	return rows


static func _chip_width(text: String, fs: int) -> float:
	return Palette.mono().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + 12.0


## The intent tag's rect in view space (empty without an intent): a title row and one row
## per line of result chips, grown upwards from just above the pointer hub.
func _intent_rect_local() -> Rect2:
	if combatant == null or intent.is_empty() or String(intent.get("text", "")) == "":
		return Rect2()
	var ts := _ts()
	var title_h := INTENT_HEIGHT * ts
	var chip_h := CHIP_HEIGHT * ts
	var rows := _chip_rows()
	var h := title_h + rows.size() * (chip_h + 2.0)
	var w := Palette.marker().get_string_size(String(intent["text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, _fs(INTENT_FONT_SIZE)).x + (20.0 + 22.0 * ts if int(intent.get("type", -1)) >= 0 else 16.0)
	if TIER_PIPS.has(int(intent.get("tier", -1))):
		w += PIP_RADIUS * 2.6 * ts * 3 + 4 * ts
	var fs := _fs(CHIP_FONT_SIZE)
	for row in rows:
		var rw := 8.0
		for chip in row:
			rw += _chip_width(String(chip["text"]), fs)
		w = maxf(w, rw)
	w = minf(w, size.x * TAG_MAX_SHARE)
	var bottom := _center().y - _radius() - _band() - INTENT_HEIGHT
	var x := clampf(_center().x - w * 0.5, 0.0, maxf(0.0, size.x - w))
	return Rect2(Vector2(x, maxf(0.0, bottom - h)), Vector2(w, h))


## The intent tag on screen (layout checks: it never covers a wheel), or an empty rect.
func intent_rect() -> Rect2:
	var r := _intent_rect_local()
	return Rect2(global_position + r.position, r.size) if r.has_area() else r


func _intent_tag(r: Rect2) -> void:
	var type := int(intent.get("type", -1))
	var text := String(intent["text"])
	var ts := _ts()
	var f := Palette.marker()
	var w := r.size.x
	draw_rect(Rect2(r.position + Vector2(3, 4), r.size), Palette.SHADOW)
	draw_rect(r, Palette.NOTE_PAPER)
	draw_rect(r, Color(Palette.INK, 0.5), false, 1.0)
	draw_rect(Rect2(r.position + Vector2(w * 0.5 - 14, -5), Vector2(28, 9)), Palette.NOTE_TAPE)
	var tx := r.position.x + 8
	var title_h := INTENT_HEIGHT * ts
	if type >= 0:
		SliceIcon.draw_icon(self, r.position + Vector2(17, title_h * 0.5), 9 * ts, type, Palette.slice_color(type))
		tx += 22 * ts
	var tier := int(intent.get("tier", -1))
	if TIER_PIPS.has(tier):
		# Aim quality as pips (readable without words): filled = how well the needle sits.
		for k in 3:
			var pc := Vector2(tx + PIP_RADIUS * ts + k * (PIP_RADIUS * 2.6 * ts), r.position.y + title_h * 0.5)
			if k < int(TIER_PIPS[tier]):
				draw_circle(pc, PIP_RADIUS * ts, Palette.INK)
			else:
				draw_arc(pc, PIP_RADIUS * ts, 0, TAU, 10, Palette.INK, 1.2)
		tx += PIP_RADIUS * 2.6 * ts * 3 + 4 * ts
	draw_string(f, Vector2(tx, r.position.y + title_h * 0.7), text, HORIZONTAL_ALIGNMENT_LEFT, r.end.x - tx - 4, _fs(INTENT_FONT_SIZE), Palette.INK)
	var fs := _fs(CHIP_FONT_SIZE)
	var chip_h := CHIP_HEIGHT * ts
	var y := r.position.y + title_h
	for row in _chip_rows():
		var x := r.position.x + 4
		for chip in row:
			var cw := _chip_width(String(chip["text"]), fs)
			var cr := Rect2(Vector2(x, y), Vector2(cw - 4, chip_h))
			draw_rect(cr, Color(chip.get("color", Palette.INK)))
			draw_string(Palette.mono(), Vector2(cr.position.x + 4, cr.position.y + chip_h * 0.75), String(chip["text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(chip.get("ink", Palette.PAPER)))
			x += cw
		y += chip_h + 2.0


func _draw_dashed_arc(center: Vector2, radius: float, start: float, end: float, color: Color, width: float) -> void:
	var span := end - start
	var dashes := maxi(3, int(absf(span) / 0.12))
	for i in dashes:
		if i % 2 == 1:
			continue
		var a := start + span * i / dashes
		var b := start + span * (i + 1) / dashes
		draw_arc(center, radius, a, b, 4, color, width)
