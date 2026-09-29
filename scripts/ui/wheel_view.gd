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
## Art pass W3 (ART_BIBLE §6.1): the wheel's hardware, WheelBezel's look for its owner
## (show_combatant sets it: the operative's stickered bezel, an enemy's notched corp bezel).
var look: Dictionary = {}
## The operative's class (its bezel ornament, hub pattern and glyph); "" = read from the
## combatant's source id.
var class_id: StringName = &""
## W5 seams: who the portrait shows (PortraitArt subject: the operative's Polaroid inset at
## the hub's top, an enemy's badge above its bezel) and final art that replaces the drawn
## face (null = PortraitArt draws it).
var portrait_subject: Dictionary = {}
var portrait_texture: Texture2D = null
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

# Motion (Animation pass ANIM-2): what the view shows while the scene replays a change
# the state already holds. NAN / null / empty / 1.0 = show the state itself. The state is
# never touched: these are the view's own numbers, and every one of them is back at its
# rest value when a motion ends or is skipped (stop_motion).
## A snapshot drawn instead of `combatant` (and its docked satellites) while a SEND IT
## replays from the state it started in; null = the combatant.
var shown_state: CombatantState = null
var shown_satellites: Array[CombatantState] = []
## Shown outer / inner rotation in ticks (fractional mid-spin).
var anim_rotation: float = NAN
var anim_inner_rotation: float = NAN
## Shown needle ticks (fractional mid-move); empty = the wheel's.
var anim_pointers: Array[float] = []
## Shown HP and the white lag bar trailing a loss.
var anim_hp: float = NAN
var lag_hp: float = NAN
## The needle (index) or docked satellite (id) pulsing as it resolves, and its scale.
var pulse_pointer: int = -1
var pulse_satellite: StringName = &""
var pulse_scale: float = 1.0
## Good landing: a ring growing off the rim (progress 0..1; 0 = none).
var ring_pulse: float = 0.0
## Miss landing: static over one slice (strength 0..1; 0 = none).
var miss_static: float = 0.0
var miss_slot: int = -1
## Slice blur while the wheel turns fast (0..1) and which way it turns.
var blur: float = 0.0
var _blur_dir: float = 1.0
## Orbit trails: [from tick, to tick] arcs fading at `trail_alpha`.
var trails: Array = []
var trail_alpha: float = 0.0
## FLIP: horizontal squash of the disc (1 = none).
var flip_squash: float = 1.0
## Drop zones pulse while a card is aimed (alpha factor of the unhovered zones).
var zone_pulse: float = 1.0
## Paper flip of the tag when its content changes (1 = flat on the wall).
var tag_flip: float = 1.0
## Tag flips started so far (tests read it: a flip can finish between two slow frames).
var tag_flips: int = 0
## A SEND IT replays: the tag, the NEXT plate and the forecast marks hide until it ends.
var replaying: bool = false
## LAST TURN plate reveal (0 hidden .. 1 in place).
var last_turn_shown: float = 1.0
# ANIM-R1 (the SEND IT replay's legibility): the landed slices, the break, satellite HP,
# the THIS TURN caption, an enemy's entrance and the hit flash. Rest values as above.
## Slices the needles landed on this replay: slot -> true when it is a MISS slice (drawn
## with a big grey X until the wheel turns on), and their pulse (0..1).
var landed: Dictionary = {}
var landing_pulse: float = 0.0
## The wheel broke this replay: the view shows its empty spot (DEFEATED) from now on.
var broken: bool = false
## Docked satellites' shown HP while a replay plays (id -> HP; missing = its state).
var anim_sat_hp: Dictionary = {}
## A caption on a plate where the tag goes (THIS TURN while the result holds), and its
## reveal (0..1).
var caption: String = ""
var caption_shown: float = 0.0
## An enemy entering from the right edge: px it still has to travel.
var enter_slide: float = 0.0
## A hit landing in the HP counter: the disc flashes (0..1).
var hit_flash: float = 0.0
## Running motion tweens by key, the queued nudge steps ({ring, to}) and the shown value
## the last queued step ends on per ring.
var _tweens: Dictionary = {}
var _nudge_queue: Array[Dictionary] = []
var _queue_end: Dictionary = {}
var _intent_sig: String = ""
var _last_shown_rot: float = NAN

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
## At the biggest text the wheel keeps at least this share of its 1.0-scale radius (ART_BIBLE
## §12: text yields before the wheels do; the lettering stops at WHEEL_TEXT_MAX).
const BIG_TEXT_RADIUS_KEEP := 0.7
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
const TAG_CHIP_ROWS := 1
## HP arc and number below the rim (px): the arc's outer edge, then the number's offset.
## Art pass W3 (§6.1, §3.5): the HP arc is a thick segmented band just outside the bezel,
## from HP_ARC_IN to HP_ARC_OUT past the rim (>= 10 px), in HP_SEGMENTS; the HP number sits
## HP_NUMBER_GAP under it (and under every needle's reach).
const HP_ARC_IN := 30.0
const HP_ARC_OUT := 42.0
const HP_SEGMENTS := 20
const HP_NUMBER_GAP := 4.0
## Kept for the layout rules' reach (the arc's outer edge and the number under it).
const HP_TEXT_GAP := HP_ARC_OUT + HP_NUMBER_GAP
## The HP number's outline (px) and the arc's hatch for a forecast loss (lines per segment).
const HP_OUTLINE := 5
const HP_HATCH := 2
## Gap between the HP number and the last-turn line (px).
const LAST_TURN_GAP := 4.0
## Padding round the LAST TURN plate (px).
const LAST_TURN_PAD := 4.0
## Lines LAST TURN may take before its font shrinks below its text-scale-1.0 size.
const LAST_TURN_LINES := 2
## Lettering sizes at text scale 1.0.
const INTENT_FONT_SIZE := 15
const CHIP_FONT_SIZE := 13
const HUB_FONT_SIZE := 10
const NAME_FONT_SIZE := 13
const VALUE_FONT_SIZE := 20
const HP_FONT_SIZE := UiTheme.HEADING
const INTENT_HEIGHT := 30.0
const CHIP_HEIGHT := 20.0
## The widest a tag may get before its chips wrap (fraction of the view width).
const TAG_MAX_SHARE := 0.96
## Gain and harm (§3.3): heals and good statuses, damage and bad ones (the HP itself reads Palette.hp_color).
const HP_COLOR := Palette.GAIN
const LOSS_COLOR := Palette.HARM
const TARGET_COLOR := Palette.CELL_ACID
## The rim's tick marks: their length (px) and strength.
const RIM_TICK := 5.0
const RIM_TICK_ALPHA := 0.45
## The dark platform round the bezel (px past the bezel's rim).
const PLATFORM_PAD := 14.0
## The ink outline round a slice value on the bezel (px).
const VALUE_OUTLINE := 4
## A needle's hub: where it stands out from the rim (share of the slice band) and its radius (px).
const NEEDLE_HUB_OUT := 0.55
const NEEDLE_HUB_R := 9.0


func _init() -> void:
	custom_minimum_size = Vector2(330, 330)
	# PASS: hover tooltips on slices; clicks still reach the scene.
	mouse_filter = Control.MOUSE_FILTER_PASS
	tooltip_text = " "
	# ANIM-R5 combat 9: _get_tooltip translates its words where it builds them (once).
	tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	set_process(false)


## The text scale the wheel's own lettering follows: the player's, up to WHEEL_TEXT_MAX.
## Art pass W3 (ART_BIBLE §12: "text yields before the wheels do"): the arena's height is
## fixed, so past WHEEL_TEXT_MAX the wheel's tag, hub, HP and LAST TURN stop growing and the
## wheels keep at least 70% of their 1.0 size; every word they carry is also in a tooltip,
## which follows the full text scale.
static func _ts() -> float:
	return minf(Settings.text_scale, WHEEL_TEXT_MAX)


## The largest text scale the wheel's lettering follows (see _ts).
const WHEEL_TEXT_MAX := BIG_TEXT


static func _fs(base: int) -> int:
	return roundi(base * _ts())


## Hover: what is under the mouse (a nudge arrow, a slice, a satellite, the hub).
func _get_tooltip(at_position: Vector2) -> String:
	if combatant == null:
		return ""
	if _intent_rect_local().has_point(at_position):
		var tip := String(intent.get("tooltip", ""))
		if was_text() != "":
			tip += "\n" + tr("Before this play: %s") % was_text()
		return tip
	# ANIM-R3 A6j: the plates under the disc say what they are.
	var lay := hp_layout()
	if (lay["next"] as Rect2).has_point(at_position):
		var next_hp := int(outcome.get("hp_after", combatant.hp))
		if lethal_forecast():
			# ANIM-R5 combat 3: the LETHAL plate says what it means.
			return tr("LETHAL: this turn takes you to 0 HP.") if combatant.is_player else tr("LETHAL: this turn takes it to 0 HP.")
		if combatant.is_player:
			return tr("NEXT %d: your HP after SEND IT, if you press it now (the tag above says why).") % next_hp
		return tr("NEXT %d: its HP after SEND IT, if you press it now (the tag above says why).") % next_hp
	if ((lay["last"] as Rect2).has_point(at_position) or (lay["icons"] as Rect2).has_point(at_position)) and last_turn != "":
		return last_turn_tip if last_turn_tip != "" else last_turn
	if (lay["net"] as Rect2).has_point(at_position):
		return net_tooltip()
	if (lay["hp"] as Rect2).has_point(at_position):
		return tr("HP now: %d of %d.") % [combatant.hp, combatant.max_hp]
	var z := zone_at(global_position + at_position)
	match String(z.get("kind", "")):
		"arrow":
			# ANIM-R5 combat 9: translated, and the wheel named in the player's language.
			var clockwise := int(z["direction"]) > 0
			var line := ""
			if int(z["ring"]) == RC.RingScope.INNER:
				line = tr("Nudge %s's inner ring one tick clockwise.") if clockwise else tr("Nudge %s's inner ring one tick anticlockwise.")
			else:
				line = tr("Nudge %s one tick clockwise.") if clockwise else tr("Nudge %s one tick anticlockwise.")
			return (line % shown_name()) + "\n" + tr("Drop a nudge card here to aim it this way.")
		"satellite":
			var sat := _satellite(StringName(z["id"]))
			if sat == null:
				return ""
			var land: Dictionary = satellite_landings.get(sat.id, {})
			return tr("%s (%d HP): takes hits aimed at the slice it guards.") % [name_of(sat), sat.hp] \
				+ (("\n" + tr("Its needle lands on %s.") % String(land["text"])) if not land.is_empty() else "")
		"slot":
			return _slice_label(int(z["slot"]))
		"hub":
			var lines := PackedStringArray([shown_name()])
			# How the fight is won and lost (H24: never stated).
			lines.append(tr("Bring its HP to 0 to win the fight.") if not combatant.is_player else tr("At 0 HP you lose the fight."))
			if combatant.block > 0:
				lines.append(tr("Block %d: soaks damage this turn.") % combatant.block)
			if combatant.shield > 0:
				lines.append(tr("Shield %d: soaks damage, lasts.") % combatant.shield)
			if combatant.resistance > 0:
				lines.append(tr("Resistance %d: absorbs nudges and spins tick for tick; Flip and Respin are blocked.") % combatant.resistance)
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
		# ANIM-R4 C6f: whose win it is, as its colour says.
		parts.append((tr("Good for you: %s") if status_good_for_you(status, combatant.is_player) else tr("Bad for you: %s")) % Codex.status_text(status))
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
	look = WheelBezel.operative_look(operative_class()) if c.is_player else WheelBezel.enemy_look(_corporation_of(c), is_boss())
	look["flicker_depth"] = Motion.amplitude(&"bezel_ambient")
	size_scale = BOSS_SCALE if is_boss() else 1.0
	# W5 (§7.2): a boss's hologram stands behind its wheel; any other enemy's bust hangs
	# above its bezel (badge_rect).
	var data := _enemy_data()
	var key := String(c.source_id)
	if data != null and data.is_boss and (backdrop == null or String(backdrop.get_meta(&"for", "")) != key):
		var holo := Hologram.for_enemy(data)
		holo.set_meta(&"for", key)
		set_backdrop(holo)
	elif (data == null or not data.is_boss) and backdrop != null:
		set_backdrop(null)
	if data != null and not data.is_boss and not c.is_player:
		if bust == null or String(bust.get_meta(&"for", "")) != key:
			if bust != null:
				bust.queue_free()
			bust = Hologram.for_enemy(data)
			bust.set_meta(&"for", key)
			add_child(bust)
	elif bust != null:
		bust.queue_free()
		bust = null
	_sync_ambient()
	queue_redraw()


## An enemy's portrait above its bezel (W5's Hologram in BUST mode); null for the operative
## and a boss (its nameplate carries its face).
var bust: Hologram = null


## This enemy's content (null for the operative or unknown content).
func _enemy_data() -> EnemyData:
	if combatant == null or combatant.is_player or lookup == null or not lookup.has(combatant.source_id):
		return null
	return lookup.get_content(combatant.source_id) as EnemyData


## Art pass W3 with W5 (§7.1): the operative's face follows the fight: HURT under a quarter HP,
## TRIUMPHANT once the fight is won (`triumphant`), FLATLINED once it is lost.
func expression() -> int:
	var c := _shown()
	if c == null:
		return PortraitArt.Expr.NEUTRAL
	if flatlined or not c.is_alive():
		return PortraitArt.Expr.FLATLINED
	if triumphant:
		return PortraitArt.Expr.TRIUMPHANT
	if shown_hp() / maxf(1.0, c.max_hp) < Palette.HP_HARM_BELOW:
		return PortraitArt.Expr.HURT
	return PortraitArt.Expr.NEUTRAL


## The fight is won (the scene sets it when VICTORY lands): the operative looks triumphant.
var triumphant: bool = false


## §6.1: a boss's wheel is this much bigger than a normal one (as far as its view allows).
const BOSS_SCALE := 1.2
## The wheel's size against a normal wheel's (BOSS_SCALE for a boss).
var size_scale: float = 1.0
## §7.2: what stands behind a boss's wheel (W5's Hologram in BOSS mode, set_backdrop);
## null for any other wheel.
var backdrop: Control = null


## W5 seam: puts `node` (a hologram, ≈40% of the screen high) behind this wheel, centred on
## it (it draws behind the wheel: show_behind_parent). The one before it goes.
func set_backdrop(node: Control) -> void:
	if backdrop != null and is_instance_valid(backdrop):
		backdrop.queue_free()
	backdrop = node
	if node == null:
		return
	node.show_behind_parent = true
	node.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(node)
	_place_backdrop()


## Centres the backdrop on the wheel (its top at the bezel's top half: the head above).
func _place_backdrop() -> void:
	if backdrop == null or not is_instance_valid(backdrop):
		return
	var vh := get_viewport_rect().size.y if is_inside_tree() else size.y
	var box := Hologram.boss_size(vh)
	backdrop.size = box
	# Its foot at the wheel's centre: the figure rises behind the wheel, its head above the
	# bezel (behind the tag); the wheel and its values draw over it.
	backdrop.position = _center() - Vector2(box.x * 0.5, box.y)




## The ambient clock (T0, `bezel_ambient`: 0..1 over its period) the class ornaments that
## move read (the Ghost's flicker, the Botnet's orbit); 0 at rest (reduce effects, headless).
var ambient_phase: float = 0.0


## True while something on this wheel loops on the ambient clock.
func ambient_on() -> bool:
	return WheelBezel.is_ambient(look) and Motion.live(&"bezel_ambient")


## Starts the ambient clock when it is needed; at rest otherwise.
func _sync_ambient() -> void:
	if not ambient_on():
		ambient_phase = 0.0
	if not heartbeat_on():
		heart_t = 0.0
	if ambient_on() or heartbeat_on():
		set_process(true)


## The operative's class id (its bezel's ornament): `class_id`, else the combatant's source
## id when that names a class.
func operative_class() -> StringName:
	if class_id != &"":
		return class_id
	return combatant.source_id if combatant != null else &""


## True when this wheel is a boss's (EnemyData.is_boss): 120% of normal, a nameplate, phase
## pips on its HP arc (§6.1).
func is_boss() -> bool:
	if combatant == null or combatant.is_player or lookup == null or not lookup.has(combatant.source_id):
		return false
	var data := lookup.get_content(combatant.source_id) as EnemyData
	return data != null and data.is_boss


## Who the wheel's portrait shows: `portrait_subject`, else the operative's class face or the
## enemy's own (PortraitArt).
func shown_subject() -> Dictionary:
	var c := _shown()
	if c == null:
		return portrait_subject
	if c.is_player:
		var base := portrait_subject if not portrait_subject.is_empty() else PortraitArt.operative_subject(operative_class())
		return PortraitArt.with_expression(base, expression())
	if not portrait_subject.is_empty():
		return portrait_subject
	var data := _enemy_data()
	return PortraitArt.enemy_data_subject(data) if data != null else PortraitArt.enemy_subject(c.source_id, shown_name(), _corporation_of(c), is_boss())


## Where the operative's Polaroid inset sits (local, unrotated); empty for an enemy.
func inset_rect() -> Rect2:
	var c := _shown()
	if c == null or not c.is_player:
		return Rect2()
	return WheelBezel.inset_rect(_center(), hub_radius())


## The bezel's outer radius (px): the slices' rim plus WheelBezel.BEZEL_W.
func bezel_radius() -> float:
	return _radius() + WheelBezel.BEZEL_W


## How far out from the centre a needle's hub reaches (px, its pulse included).
func needle_reach() -> float:
	return _radius() + _band() * NEEDLE_HUB_OUT + NEEDLE_HUB_R * maxf(1.0, Motion.amplitude(&"resolve_pulse"))


## §6.1: a boss's taped PAPER nameplate above its bezel (its portrait badge and its name in
## Anton), between the needles' reach and the tag, clear of the nudge arrows: {rect, badge,
## text, fs} (local), {} for any other wheel or when it has no room.
func nameplate() -> Dictionary:
	var c := _shown()
	if c == null or not is_boss() or defeated():
		return {}
	var text := shown_name().to_upper()
	var font := Palette.display()
	var side := WheelBezel.BADGE_SIDE
	var pad := NAMEPLATE_PAD
	# The room between the arrows' inner edges (they stand at ±ARROW_ANGLE off the top).
	var arrow_in := (_radius() + ARROW_RADIUS) * sin(deg_to_rad(ARROW_ANGLE)) - ARROW_HIT * maxf(1.0, _ts())
	var max_w := maxf(side, 2.0 * arrow_in - pad * 2.0)
	var fs := _fs(UiTheme.LABEL)
	while fs > UiTheme.CAPTION and side + pad * 4.0 + font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > max_w:
		fs -= 1
	var w := minf(max_w, side + pad * 4.0 + font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
	var h := maxf(side, fs * NAMEPLATE_LINE) + pad
	var bottom := _center().y - needle_reach() - WheelBezel.BADGE_GAP
	var r := Rect2(Vector2(_center().x - w * 0.5, bottom - h), Vector2(w, h))
	var tag := _intent_rect_local()
	if tag.has_area() and r.intersects(tag):
		return {}
	var badge := Rect2(r.position + Vector2(pad, (h - side) * 0.5), Vector2(side, side))
	return {"rect": r, "badge": badge, "text": text, "fs": fs}


## The nameplate's padding (px) and its lettering's line height (x its size).
const NAMEPLATE_PAD := 4.0
const NAMEPLATE_LINE := 1.3


func _draw_nameplate(plate: Dictionary) -> void:
	var r: Rect2 = plate["rect"]
	var fs := int(plate["fs"])
	draw_set_transform(r.get_center(), NAMEPLATE_TILT, Vector2.ONE)
	var local := Rect2(-r.size * 0.5, r.size)
	draw_rect(Rect2(local.position + Vector2(3, 4), local.size), Palette.SHADOW)
	draw_rect(local, Palette.PAPER)
	draw_rect(local, Color(Palette.INK, 0.5), false, 1.0)
	var tape := Vector2(local.size.y * 0.9, WheelBezel.BADGE_SIDE * 0.35)
	for sx: float in [-1.0, 1.0]:
		var at := Vector2(sx * (local.size.x * 0.5 - tape.x * 0.3), local.position.y)
		draw_set_transform(r.get_center() + at.rotated(NAMEPLATE_TILT), NAMEPLATE_TILT + sx * 0.5, Vector2.ONE)
		draw_rect(Rect2(-tape * 0.5, tape), Palette.NOTE_TAPE)
		draw_set_transform(r.get_center(), NAMEPLATE_TILT, Vector2.ONE)
	var badge: Rect2 = plate["badge"]
	var b := Rect2(badge.position - r.get_center(), badge.size)
	WheelBezel.draw_badge(self, b, shown_subject(), look, portrait_texture)
	var font := Palette.display()
	var x := b.end.x + NAMEPLATE_PAD * 2.0
	draw_string(font, Vector2(x, fs * 0.36), String(plate["text"]), HORIZONTAL_ALIGNMENT_LEFT, local.end.x - x - NAMEPLATE_PAD, fs, Palette.INK)
	draw_set_transform(Vector2.ZERO)


## The nameplate's tilt (rad): paper is never square (§2).
const NAMEPLATE_TILT := -0.03


## Where an enemy's portrait badge hangs above its bezel (local): between the needle reach
## and the tag, clear of the nudge arrows and their hints; empty when there is no room (or
## for the operative, whose portrait is inset in its hub).
func badge_rect() -> Rect2:
	var c := _shown()
	if c == null or c.is_player or defeated():
		return Rect2()
	var bottom := _center().y - needle_reach() - WheelBezel.BADGE_GAP
	var tag := _intent_rect_local()
	# As big as the room up to the tag allows, from BADGE_SIDE to W5's bust size.
	var room := bottom - tag_bottom() - WheelBezel.BADGE_GAP * 2.0 - 1.0
	var side := clampf(room, WheelBezel.BADGE_SIDE, Hologram.BUST_SIDE * _ts())
	var r := Rect2(Vector2(_center().x - side * 0.5, bottom - side), Vector2(side, side))
	if tag.has_area() and r.grow(WheelBezel.BADGE_GAP).intersects(tag):
		return Rect2()
	for ar in arrows():
		var ac := arrow_center(int(ar["ring"]), int(ar["direction"])) - global_position
		var hit := ARROW_HIT * maxf(1.0, _ts())
		if r.intersects(Rect2(ac - Vector2(hit, hit), Vector2(hit, hit) * 2.0)):
			return Rect2()
	return r


func set_ghost(outer: Variant, inner: Variant = null) -> void:
	ghost_rotation = outer
	ghost_inner_rotation = inner
	queue_redraw()


# --- Motion (Animation pass ANIM-2) ----------------------------------------------------------

## A spin's time grows with the square root of its distance, measured in half turns, and
## stays within this share of its entry's duration (the handoff's 0.25-0.6 s at 0.45 s).
const HALF_TURN := RC.TICKS / 2.0
const SPIN_MIN_SHARE := 0.55
const SPIN_MAX_SHARE := 1.35
## The last share of a spin settles back from its overshoot.
const SETTLE_SHARE := 0.3
## A spin's overshoot: its entry's amplitude x this many ticks.
const OVERSHOOT_TICKS := 0.1
## A nudge step travels over this share of its time, then recoils.
const NUDGE_TRAVEL_SHARE := 0.7
## Rewind scrub: the tape stutters in this many steps.
const SCRUB_STEPS := 5
## Slice blur: faint copies trail the slices this many ticks apart.
const BLUR_COPIES := 2
const BLUR_STEP := 0.6
## Miss static: flecks drawn over the slice, and their length (px).
const STATIC_FLECKS := 26
const STATIC_FLECK := 7.0
## Floating numbers keep inside this share of the inner disc's radius (clear of every
## needle, which only reaches the slice band).
const NUMBER_ROOM := 0.62
## ANIM-R1 replay numbers: they keep inside this share of the hub's radius, this far (px)
## off the hub's words, and never shrink below NUMBER_MIN_FONT px.
const NUMBER_HUB_SHARE := 0.9
const NUMBER_GAP := 2.0
const NUMBER_MIN_FONT := 10.0
## A landed slice's rim (px); the MISS X's arm as a share of the slice band, its width.
const LANDED_RIM := 4.0
const MISS_X_SHARE := 0.32
const MISS_X_WIDTH := 5.0
## The DEFEATED stamp's lettering (px at text scale 1.0) and tilt (rad).
const DEFEATED_FONT := 22
## §3.5: at 0 HP the wheel's own colour dims to this share under its DEFEATED / DEFEAT stamp.
const DEFEATED_DIM := 0.3
const STAMP_TILT := -0.2
## ANIM-R3 A6g: the skull under DEFEATED, its radius as a share of the stamp's lettering.
const SKULL_SHARE := 0.75
## ANIM-R3 A6j: a landing status's ring starts just round its mark (px; it grows by
## `status_mark`'s amplitude).
const STATUS_MARK_R := 9.0


## The rotation the view shows (ticks; the state's unless a motion runs).
func shown_rotation() -> float:
	return anim_rotation if not is_nan(anim_rotation) else float(_shown().wheel.rotation)


func shown_inner_rotation() -> float:
	return anim_inner_rotation if not is_nan(anim_inner_rotation) else float(_shown().wheel.inner_rotation)


## The needle ticks the view shows.
func shown_pointers() -> Array[float]:
	if not anim_pointers.is_empty():
		return anim_pointers
	var out: Array[float] = []
	for p in _shown().wheel.pointer_ticks:
		out.append(float(p))
	return out


## The HP the view shows.
func shown_hp() -> float:
	return anim_hp if not is_nan(anim_hp) else float(_shown().hp)


func _shown() -> CombatantState:
	return shown_state if shown_state != null else combatant


## True while any motion of this view still runs (its own tweens, queued nudges, and the
## kit's helpers on it: the Partial stutter, the Miss blink).
func motion_busy() -> bool:
	for k in _tweens:
		var tw: Tween = _tweens[k]
		if tw != null and tw.is_valid() and tw.is_running():
			return true
	for key in get_meta_list():
		if String(key) in [Motion.META_PREFIX + "shake", Motion.META_PREFIX + "modulate_a"]:
			var held: Array = get_meta(key)
			var htw: Tween = held[0]
			if htw != null and htw.is_valid() and htw.is_running():
				return true
	return not _nudge_queue.is_empty()


## Ends every motion of this view at once: the view shows the state as it is (skip,
## reduce effects, a new state arriving mid-motion). ANIM-R1 C3: the kit's helpers stop
## too (the Partial shake kept running), and with `sync_tag` the tag takes the content it
## shows now without a flip (a skip lands; only a replay that plays out flips the tags in).
func stop_motion(sync_tag: bool = true) -> void:
	# The kit's one-shot helpers (the migration flicker is the scene's loop and stays).
	for prop in [^"shake", ^"modulate:a"]:
		Motion._settle(self, prop)
	for k in _tweens:
		var tw: Tween = _tweens[k]
		if tw != null and tw.is_valid():
			tw.kill()
	_tweens.clear()
	_nudge_queue.clear()
	_queue_end.clear()
	shown_state = null
	shown_satellites = []
	anim_rotation = NAN
	anim_inner_rotation = NAN
	anim_pointers = []
	anim_hp = NAN
	lag_hp = NAN
	pulse_pointer = -1
	pulse_satellite = &""
	pulse_scale = 1.0
	ring_pulse = 0.0
	miss_static = 0.0
	miss_slot = -1
	blur = 0.0
	trails = []
	trail_alpha = 0.0
	flip_squash = 1.0
	tag_flip = 1.0
	replaying = false
	last_turn_shown = 1.0
	shake = Vector2.ZERO
	modulate.a = 1.0
	_last_shown_rot = NAN
	landed = {}
	landing_pulse = 0.0
	broken = false
	anim_sat_hp = {}
	caption = ""
	caption_shown = 0.0
	enter_slide = 0.0
	hit_flash = 0.0
	_hp_to = NAN
	replay_tag = {}
	tag_ticks = {}
	replay_tag_alpha = 1.0
	status_flash = {}
	needle_grow = {}
	hub_alpha = 1.0
	flatline_pop = 1.0  # the DEFEAT stamp itself stays (ANIM-R5 combat 2)
	if sync_tag:
		_intent_sig = intent_signature() if _intent_rect_local().has_area() else ""
	set_process(false)
	_sync_ambient()
	queue_redraw()


## A fresh tween for motion `key` (the one running under that key stops).
func _tw(key: StringName) -> Tween:
	var old: Tween = _tweens.get(key)
	if old != null and old.is_valid():
		old.kill()
	var tw := create_tween()
	_tweens[key] = tw
	return tw


func _end(key: StringName) -> void:
	_tweens.erase(key)


## Seconds a spin of `ticks` takes under `id`: its duration x sqrt(distance in half turns),
## within SPIN_MIN_SHARE..SPIN_MAX_SHARE of it.
static func spin_seconds(id: StringName, ticks: float) -> float:
	return Motion.seconds(id) * clampf(sqrt(absf(ticks) / HALF_TURN), SPIN_MIN_SHARE, SPIN_MAX_SHARE)


## A spin's travel at progress `p` (0..1) over `dist` ticks: the entry's ease to `dist`
## plus `over` ticks of overshoot, then a settle back. Exactly `dist` at p = 1.
static func spin_curve(p: float, dist: float, over: float, trans: int, ease: int) -> float:
	if p >= 1.0:
		return dist
	var run := 1.0 - SETTLE_SHARE
	var o := signf(dist) * over
	if p < run:
		return float(Tween.interpolate_value(0.0, 1.0, p / run, 1.0, trans, ease)) * (dist + o)
	var q := (p - run) / SETTLE_SHARE
	return dist + o * (1.0 - smoothstep(0.0, 1.0, q))


## Replays a turn: the outer ring runs from `from` ticks (and the inner ring from
## `inner_from`, when given) to the state's rotation with `id`'s timing (ANIM-2 spin:
## ease-out, overshoot of amplitude x OVERSHOOT_TICKS, settle), after `delay` seconds.
## Ends exactly on the core's tick; shows the end at once when motion doesn't play.
## ANIM-R4 C6e: returns when it lands (s from now: its delay and its turn; 0 when none).
func play_turn(id: StringName, from: float, inner_from: float = NAN, delay: float = 0.0) -> float:
	_nudge_queue.clear()
	_queue_end.clear()
	if combatant == null or not Motion.live(id):
		anim_rotation = NAN
		anim_inner_rotation = NAN
		_end(&"turn")
		queue_redraw()
		return 0.0
	var to := float(combatant.wheel.rotation)
	var inner_to := float(combatant.wheel.inner_rotation)
	var dist := to - from
	var inner_dist := inner_to - inner_from if not is_nan(inner_from) else 0.0
	if is_zero_approx(dist) and is_zero_approx(inner_dist):
		anim_rotation = NAN
		anim_inner_rotation = NAN
		return 0.0
	var e := Motion.entry(id)
	anim_rotation = from
	anim_inner_rotation = inner_from if not is_nan(inner_from) else NAN
	var over := Motion.amplitude(id) * OVERSHOOT_TICKS
	var secs := spin_seconds(id, maxf(absf(dist), absf(inner_dist)))
	var tw := _tw(&"turn")
	tw.tween_interval(delay)
	tw.tween_method(_turn_step.bind(from, dist, inner_from, inner_dist, over, e.trans, e.ease), 0.0, 1.0, secs)
	var settle := settle_seconds(id)
	if settle > 0.0:
		# Art pass W3 (critique gifs/03): a respin has weight: it rocks past its tick and back
		# (`<id>_settle`: its amplitude in ticks) before it rests.
		var rock := signf(dist if dist != 0.0 else inner_dist) * Motion.amplitude(StringName(String(id) + SETTLE_SUFFIX))
		tw.tween_method(_settle_step.bind(to, inner_to if not is_nan(inner_from) else NAN, rock), 0.0, 1.0, settle)
	tw.tween_callback(func() -> void:
		anim_rotation = NAN
		anim_inner_rotation = NAN
		_end(&"turn")
		queue_redraw())
	_blur_dir = signf(dist) if dist != 0.0 else 1.0
	set_process(true)
	return delay + secs + settle


## A spin's settle entry: `<id>` + this (e.g. wheel_respin_settle).
const SETTLE_SUFFIX := "_settle"


## Seconds a turn under `id` rocks and settles after it lands (its `_settle` entry; 0 when
## it has none or it doesn't play).
static func settle_seconds(id: StringName) -> float:
	var sid := StringName(String(id) + SETTLE_SUFFIX)
	return Motion.seconds(sid) if Motion.has(sid) and Motion.live(sid) else 0.0


## Seconds a whole turn of `ticks` under `id` takes: its spin and its settle.
static func turn_seconds(id: StringName, ticks: float) -> float:
	return spin_seconds(id, ticks) + settle_seconds(id)


func _settle_step(p: float, to: float, inner_to: float, rock: float) -> void:
	# One damped swing past the tick and back: out, back through, home.
	var swing := rock * sin(TAU * p) * (1.0 - p)
	anim_rotation = to + swing
	if not is_nan(inner_to):
		anim_inner_rotation = inner_to + swing
	queue_redraw()


func _turn_step(p: float, from: float, dist: float, inner_from: float, inner_dist: float, over: float, trans: int, ease: int) -> void:
	anim_rotation = from + spin_curve(p, dist, over, trans, ease)
	if not is_nan(inner_from):
		anim_inner_rotation = inner_from + spin_curve(p, inner_dist, over, trans, ease)
	queue_redraw()


## A nudge of `ring` by `direction` the state already holds: a one-tick step with a
## recoil (`wheel_nudge`). Steps queue behind each other; a long queue runs faster so it
## catches up, and the last queued step always ends on the state's tick (sync_nudges).
func play_nudge(ring: int, direction: int) -> void:
	var id := &"inner_ring_turn" if ring == RC.RingScope.INNER else &"wheel_nudge"
	if combatant == null or not Motion.live(id):
		stop_turns()
		return
	var core := float(combatant.wheel.inner_rotation if ring == RC.RingScope.INNER else combatant.wheel.rotation)
	var start: float = _queue_end.get(ring, core - direction)
	if not _queue_end.has(ring) and _tweens.has(&"turn"):
		start = shown_inner_rotation() if ring == RC.RingScope.INNER else shown_rotation()
	var to := start + direction
	_nudge_queue.append({"ring": ring, "to": to, "direction": direction})
	_queue_end[ring] = to
	if ring == RC.RingScope.INNER:
		if is_nan(anim_inner_rotation):
			anim_inner_rotation = start
	elif is_nan(anim_rotation):
		anim_rotation = start
	if not _tweens.has(&"nudge"):
		_next_nudge()


## Ends the queued steps on the state: when the last one would stop off the state's tick
## (a spin or snap in the same action), it goes to the state's tick instead.
func sync_nudges() -> void:
	if combatant == null:
		return
	for ring in _queue_end.keys():
		var core := float(combatant.wheel.inner_rotation if int(ring) == RC.RingScope.INNER else combatant.wheel.rotation)
		if not is_equal_approx(float(_queue_end[ring]), core):
			for k in range(_nudge_queue.size() - 1, -1, -1):
				if int(_nudge_queue[k]["ring"]) == int(ring):
					_nudge_queue[k]["to"] = core
					break
			_queue_end[ring] = core


## Where the queued steps of `ring` end (the state's tick once synced), NAN when none.
func queue_target(ring: int) -> float:
	return float(_queue_end.get(ring, NAN))


## Steps still waiting in the nudge queue (the one running excluded).
func queued_steps() -> int:
	return _nudge_queue.size()


func _next_nudge() -> void:
	if _nudge_queue.is_empty():
		_end(&"nudge")
		_queue_end.clear()
		anim_rotation = NAN
		anim_inner_rotation = NAN
		shake = Vector2.ZERO
		queue_redraw()
		return
	var step: Dictionary = _nudge_queue.pop_front()
	var ring := int(step["ring"])
	var id := &"inner_ring_turn" if ring == RC.RingScope.INNER else &"wheel_nudge"
	var e := Motion.entry(id)
	var from := shown_inner_rotation() if ring == RC.RingScope.INNER else shown_rotation()
	# A queue catches up: each waiting step shares the time of one.
	var secs := Motion.seconds(id) / float(1 + _nudge_queue.size())
	var tw := _tw(&"nudge")
	tw.tween_method(_nudge_step.bind(ring, from, float(step["to"]), float(step["direction"]), e.trans, e.ease), 0.0, 1.0, secs)
	tw.tween_callback(_next_nudge)


func _nudge_step(p: float, ring: int, from: float, to: float, direction: float, trans: int, ease: int) -> void:
	var q: float = Tween.interpolate_value(0.0, 1.0, minf(1.0, p / NUDGE_TRAVEL_SHARE), 1.0, trans, ease)
	var v := lerpf(from, to, q)
	if ring == RC.RingScope.INNER:
		anim_inner_rotation = v
	else:
		anim_rotation = v
	# The recoil: the disc kicks back against the step and returns.
	var r := maxf(0.0, (p - NUDGE_TRAVEL_SHARE) / (1.0 - NUDGE_TRAVEL_SHARE))
	shake = Vector2(-direction * Motion.amplitude(&"wheel_nudge") * sin(PI * r), 0.0)
	queue_redraw()


## Stops the turn and nudge motions (the rings show the state).
func stop_turns() -> void:
	for key in [&"turn", &"nudge"]:
		var tw: Tween = _tweens.get(key)
		if tw != null and tw.is_valid():
			tw.kill()
		_tweens.erase(key)
	_nudge_queue.clear()
	_queue_end.clear()
	anim_rotation = NAN
	anim_inner_rotation = NAN
	shake = Vector2.ZERO
	queue_redraw()


## FLIP: the disc squashes to a line and opens mirrored (`wheel_flip`), after `delay`.
func play_flip(delay: float = 0.0) -> void:
	if not Motion.live(&"wheel_flip"):
		flip_squash = 1.0
		return
	var e := Motion.entry(&"wheel_flip")
	var tw := _tw(&"flip")
	tw.tween_interval(delay)
	tw.tween_method(func(p: float) -> void: flip_squash = absf(cos(PI * p)); queue_redraw(), 0.0, 1.0, Motion.seconds(&"wheel_flip")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void: flip_squash = 1.0; _end(&"flip"); queue_redraw())


## Needles move from `from` ticks to the state's (`pointer_migrate`, or `pointer_orbit`
## with a fading trail arc when `trail`), after `delay`. Each takes the short way round.
func play_pointers(from: Array, id: StringName, trail: bool = false, delay: float = 0.0) -> float:
	var to := PackedInt32Array()
	if combatant != null:
		to = combatant.wheel.pointer_ticks
	if not Motion.live(id) or from.size() != to.size() or from.is_empty():
		anim_pointers = []
		return 0.0
	var starts: Array[float] = []
	var ends: Array[float] = []
	for k in to.size():
		var f := float(from[k])
		starts.append(f)
		ends.append(f + float(posmod(roundi(to[k] - f) + RC.TICKS / 2, RC.TICKS) - RC.TICKS / 2))
	anim_pointers = starts.duplicate()
	var e := Motion.entry(id)
	var tw := _tw(&"pointers")
	tw.tween_interval(delay)
	var secs := Motion.seconds(id) if not trail else Motion.seconds(&"orbit_trail")
	tw.tween_method(_pointer_step.bind(starts, ends), 0.0, 1.0, secs).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void: anim_pointers = []; _end(&"pointers"); queue_redraw())
	if trail and Motion.live(&"orbit_trail"):
		trails = []
		for k in starts.size():
			trails.append([starts[k], ends[k]])
		trail_alpha = Motion.amplitude(&"orbit_trail")
		var te := Motion.entry(&"orbit_trail")
		var ttw := _tw(&"trail")
		ttw.tween_interval(delay + secs)
		ttw.tween_method(func(a: float) -> void: trail_alpha = a; queue_redraw(), trail_alpha, 0.0, Motion.seconds(&"orbit_trail")).set_ease(te.ease).set_trans(te.trans)
		ttw.tween_callback(func() -> void: trails = []; _end(&"trail"))
	return delay + secs


func _pointer_step(p: float, starts: Array[float], ends: Array[float]) -> void:
	var out: Array[float] = []
	for k in starts.size():
		out.append(lerpf(starts[k], ends[k], p))
	anim_pointers = out
	queue_redraw()


## HP runs from what it shows to `to` (`hp_drain`); a loss leaves a white lag bar that
## drains after it (`hp_lag`). ANIM-R3 A6d: one roll per hit: a roll still running ends on
## its own value first, so the counter never passes through a value no hit left.
func play_hp(to: float) -> void:
	if not Motion.live(&"hp_drain"):
		anim_hp = to
		lag_hp = NAN
		_hp_to = NAN
		queue_redraw()
		return
	var running: Tween = _tweens.get(&"hp")
	if running != null and running.is_valid() and running.is_running() and not is_nan(_hp_to):
		anim_hp = _hp_to
	var from := shown_hp()
	if is_nan(lag_hp) or lag_hp < from:
		lag_hp = from
	var e := Motion.entry(&"hp_drain")
	var tw := _tw(&"hp")
	_hp_to = to
	tw.tween_method(_set_anim_hp, from, to, Motion.seconds(&"hp_drain")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void: _hp_to = NAN; _end(&"hp"))
	if to >= from:
		lag_hp = NAN
		return
	var le := Motion.entry(&"hp_lag")
	var lag := _tw(&"lag")
	lag.tween_interval(Motion.delay_of(&"hp_lag"))
	lag.tween_method(func(v: float) -> void: lag_hp = v; queue_redraw(), lag_hp, to, Motion.seconds(&"hp_lag")).set_ease(le.ease).set_trans(le.trans)


func _set_anim_hp(v: float) -> void:
	anim_hp = v
	_sync_ambient()
	queue_redraw()


## The HP roll (and its lag bar) ends on its value now (ANIM-R3 A5: the result never shows
## while a counter still rolls). True when a roll was running.
func finish_hp() -> bool:
	var was := false
	for key in [&"hp", &"lag"]:
		var tw: Tween = _tweens.get(key)
		if tw != null and tw.is_valid() and tw.is_running():
			was = true
			tw.kill()
		_tweens.erase(key)
	if not is_nan(_hp_to):
		anim_hp = _hp_to
	_hp_to = NAN
	lag_hp = NAN
	queue_redraw()
	return was


## True while the HP counter still rolls.
func hp_rolling() -> bool:
	var tw: Tween = _tweens.get(&"hp")
	return tw != null and tw.is_valid() and tw.is_running()


## Where the running HP roll ends (NAN when none runs).
var _hp_to: float = NAN


## The needle `index` (or docked satellite `sat`) pulses as it resolves (`resolve_pulse`).
func play_pulse(index: int, sat: StringName = &"") -> void:
	if not Motion.live(&"resolve_pulse"):
		return
	pulse_pointer = index if sat == &"" else -1
	pulse_satellite = sat
	var amp := Motion.amplitude(&"resolve_pulse")
	var d := Motion.seconds(&"resolve_pulse")
	var e := Motion.entry(&"resolve_pulse")
	var tw := _tw(&"pulse")
	tw.tween_method(func(v: float) -> void: pulse_scale = v; queue_redraw(), 1.0, amp, d * Motion.POP_GROW_SHARE).set_ease(Tween.EASE_OUT)
	tw.tween_method(func(v: float) -> void: pulse_scale = v; queue_redraw(), amp, 1.0, d * (1.0 - Motion.POP_GROW_SHARE)).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void: pulse_pointer = -1; pulse_satellite = &""; pulse_scale = 1.0; _end(&"pulse"))


## Good landing: a ring grows off the rim and fades (`precision_good_ring`).
func play_good_ring() -> void:
	if not Motion.live(&"precision_good_ring"):
		return
	ring_pulse = 0.001
	var e := Motion.entry(&"precision_good_ring")
	var tw := _tw(&"ring")
	tw.tween_method(func(v: float) -> void: ring_pulse = v; queue_redraw(), 0.001, 1.0, Motion.seconds(&"precision_good_ring")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void: ring_pulse = 0.0; _end(&"ring"); queue_redraw())


## Miss landing: static over slice `slot` only (`precision_miss_static`).
func play_miss_static(slot: int) -> void:
	if not Motion.live(&"precision_miss_static"):
		return
	miss_slot = slot
	miss_static = 1.0
	var e := Motion.entry(&"precision_miss_static")
	var tw := _tw(&"static")
	tw.tween_method(func(v: float) -> void: miss_static = v; queue_redraw(), 1.0, 0.0, Motion.seconds(&"precision_miss_static")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void: miss_static = 0.0; miss_slot = -1; _end(&"static"))


## Rewind: the rings and HP scrub back from `from_*` to the state (the checkpoint side)
## in SCRUB_STEPS tape stutters (`rewind_scrub`); every shown value stays between the two
## states, so it never crosses the checkpoint.
func play_rewind(from_rotation: float, from_inner: float, from_hp: float) -> void:
	stop_turns()
	if combatant == null or not Motion.live(&"rewind_scrub"):
		return
	var to := float(combatant.wheel.rotation)
	var inner_to := float(combatant.wheel.inner_rotation)
	var hp_to := float(combatant.hp)
	anim_rotation = from_rotation
	anim_inner_rotation = from_inner
	anim_hp = from_hp
	var tw := _tw(&"turn")
	tw.tween_method(_rewind_step.bind(Vector3(from_rotation, from_inner, from_hp), Vector3(to, inner_to, hp_to)), 0.0, 1.0, Motion.seconds(&"rewind_scrub"))
	tw.tween_callback(func() -> void: anim_rotation = NAN; anim_inner_rotation = NAN; anim_hp = NAN; _end(&"turn"); queue_redraw())


func _rewind_step(p: float, from: Vector3, to: Vector3) -> void:
	anim_rotation = scrub_value(from.x, to.x, p)
	anim_inner_rotation = scrub_value(from.y, to.y, p)
	anim_hp = scrub_value(from.z, to.z, p)
	queue_redraw()


## The rewind scrub's value at `p` (0..1) from `from` to `to`: SCRUB_STEPS stutters,
## each a jump then a hold. Always between `from` and `to`.
static func scrub_value(from: float, to: float, p: float) -> float:
	var steps := float(SCRUB_STEPS)
	var q := clampf(ceilf(p * steps) / steps, 0.0, 1.0)
	return lerpf(from, to, q)


## Enemy death: the disc is gone while its pieces fall (the scene draws them), then the
## dead wheel's ghost fades back in (`dead_wheel_fade`).
func play_break() -> void:
	if not Motion.live(&"enemy_break"):
		return
	# ANIM-R1: an enemy's spot shows DEFEATED from the break on (the replay still draws the
	# state it started from).
	broken = combatant != null and not combatant.is_player
	modulate.a = 0.0
	var tw := _tw(&"break")
	tw.tween_interval(Motion.seconds(&"enemy_break"))
	tw.tween_property(self, "modulate:a", Motion.amplitude(&"dead_wheel_fade"), Motion.seconds(&"dead_wheel_fade"))
	tw.tween_callback(func() -> void: modulate.a = 1.0; _end(&"break"))


## The LAST TURN plate slides up into place and fades in (`last_turn_reveal`).
func reveal_last_turn() -> void:
	if not Motion.live(&"last_turn_reveal"):
		last_turn_shown = 1.0
		queue_redraw()
		return
	last_turn_shown = 0.0
	var e := Motion.entry(&"last_turn_reveal")
	var tw := _tw(&"last_turn")
	tw.tween_method(func(v: float) -> void: last_turn_shown = v; queue_redraw(), 0.0, 1.0, Motion.seconds(&"last_turn_reveal")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void: _end(&"last_turn"))


# --- ANIM-R1: the SEND IT replay's legibility --------------------------------------------------

## A needle latched on slice `slot`: the slice pulses in its colour (`landing_pulse`: from
## full to its amplitude, where it stays until the wheel turns on); a MISS slice gets a big
## grey X. Nothing plays when motion doesn't.
func play_landing(slot: int) -> void:
	if not Motion.live(&"landing_pulse"):
		return
	var c := _shown()
	var is_miss := false
	if c != null and lookup != null and slot >= 0 and slot < c.wheel.slot_slice_ids.size():
		var slice := lookup.get_content(c.wheel.slot_slice_ids[slot]) as SliceData
		is_miss = slice != null and slice.slice_type == RC.SliceType.MISS
	landed[slot] = is_miss
	var e := Motion.entry(&"landing_pulse")
	var tw := _tw(&"landing")
	tw.tween_method(func(v: float) -> void: landing_pulse = v; queue_redraw(), 1.0, Motion.amplitude(&"landing_pulse"), Motion.seconds(&"landing_pulse")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void: _end(&"landing"))


## The landed marks go (the wheel turns on to the next landing).
func clear_landing() -> void:
	var tw: Tween = _tweens.get(&"landing")
	if tw != null and tw.is_valid():
		tw.kill()
	_tweens.erase(&"landing")
	landed = {}
	landing_pulse = 0.0
	queue_redraw()


## True when this view shows a beaten enemy (its empty spot and DEFEATED).
func defeated() -> bool:
	return combatant != null and not combatant.is_player and (broken or not combatant.is_alive())


## Satellite `id`'s shown HP during a replay.
func set_sat_hp(id: StringName, hp: int) -> void:
	anim_sat_hp[id] = hp
	queue_redraw()


## A satellite or drone docks during a replay (its token appears and pops).
func add_shown_satellite(c: CombatantState) -> void:
	if c == null:
		return
	var list: Array[CombatantState] = []
	for s in shown_satellites:
		if s.id != c.id:
			list.append(s)
	list.append(c)
	shown_satellites = list
	play_pulse(-1, c.id)
	queue_redraw()


## A satellite or drone goes down during a replay: its token vanishes.
func remove_shown_satellite(id: StringName) -> void:
	var list: Array[CombatantState] = []
	for s in shown_satellites:
		if s.id != id:
			list.append(s)
	shown_satellites = list
	queue_redraw()


## A caption on a plate where the tag goes (THIS TURN while the result holds); it fades in
## (`result_caption`).
func show_caption(text: String) -> void:
	caption = text
	if not Motion.live(&"result_caption"):
		caption_shown = 1.0
		queue_redraw()
		return
	caption_shown = 0.0
	var e := Motion.entry(&"result_caption")
	var tw := _tw(&"caption")
	tw.tween_method(func(v: float) -> void: caption_shown = v; queue_redraw(), 0.0, 1.0, Motion.seconds(&"result_caption")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void: _end(&"caption"))


## ANIM-R3 A6b: the forecast stays up through a SEND IT replay. The tag that showed when SEND
## IT was pressed (`replay_tag`, a copy of `intent`; each chip numbered `tick_i`) keeps its
## place; each of its lines gets a tick as the replay does what it said (`tick_chip`,
## `forecast_tick`), its tape then reads THIS TURN, and it fades (`fade_replay_tag`,
## `forecast_fade`) before the next forecast flips in. Empty = none.
var replay_tag: Dictionary = {}
## Ticked chips of the replay tag: tick_i -> the tick's pop (0 landing .. 1 settled).
var tag_ticks: Dictionary = {}
var replay_tag_alpha: float = 1.0
## ANIM-R3 A6j: a status just put on a slice during the replay: slot -> its mark's ring
## (1 as it lands .. 0).
var status_flash: Dictionary = {}


## Keeps forecast `tag` (what the tag showed when SEND IT was pressed) on screen for the
## replay.
func hold_forecast_tag(tag: Dictionary) -> void:
	replay_tag = tag.duplicate(true) if not tag.is_empty() and String(tag.get("text", "")) != "" else {}
	var chips: Array = replay_tag.get("chips", [])
	for k in chips.size():
		(chips[k] as Dictionary)["tick_i"] = k
	tag_ticks = {}
	replay_tag_alpha = 1.0


## The tag drawn now: the held forecast while a replay plays, else the live one.
func tag_intent() -> Dictionary:
	return replay_tag if replaying and not replay_tag.is_empty() else intent


## Ticks line `i` of the held forecast: it happened (a check pops on it).
func tick_chip(i: int) -> void:
	if tag_ticks.has(i):
		return
	if not Motion.live(&"forecast_tick"):
		tag_ticks[i] = 1.0
		queue_redraw()
		return
	tag_ticks[i] = 0.0
	var e := Motion.entry(&"forecast_tick")
	var tw := _tw(StringName("tick_%d" % i))
	tw.tween_method(_set_tick.bind(i), 0.0, 1.0, Motion.seconds(&"forecast_tick")).set_ease(e.ease).set_trans(e.trans)


func _set_tick(v: float, i: int) -> void:
	tag_ticks[i] = v
	queue_redraw()


## The held forecast fades away (the replay has read it out).
func fade_replay_tag() -> void:
	if replay_tag.is_empty():
		return
	if not Motion.live(&"forecast_fade"):
		replay_tag_alpha = 0.0
		queue_redraw()
		return
	var e := Motion.entry(&"forecast_fade")
	var tw := _tw(&"tag_fade")
	tw.tween_method(func(v: float) -> void: replay_tag_alpha = v; queue_redraw(), replay_tag_alpha, 0.0, Motion.seconds(&"forecast_fade")).set_ease(e.ease).set_trans(e.trans)


## A status lands on slice `slot` during the replay: the view's own snapshot shows it on
## that slice from now on, with a ring round its mark (`status_mark`).
func show_slice_status(slot: int, status: int) -> void:
	if shown_state == null or slot < 0 or slot >= shown_state.wheel.slice_statuses.size():
		return
	shown_state.wheel.slice_statuses[slot] = status
	if not Motion.live(&"status_mark"):
		queue_redraw()
		return
	status_flash[slot] = 1.0
	var e := Motion.entry(&"status_mark")
	var tw := _tw(StringName("status_%d" % slot))
	tw.tween_method(_set_status_flash.bind(slot), 1.0, 0.0, Motion.seconds(&"status_mark")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void: status_flash.erase(slot); queue_redraw())


func _set_status_flash(v: float, slot: int) -> void:
	status_flash[slot] = v
	queue_redraw()


func hide_caption() -> void:
	var tw: Tween = _tweens.get(&"caption")
	if tw != null and tw.is_valid():
		tw.kill()
	_tweens.erase(&"caption")
	caption = ""
	caption_shown = 0.0
	queue_redraw()


## A new enemy enters from the right edge with its name on a plate (`enemy_enter`: px it
## travels), so it never reads as a beaten one coming back.
func play_enter() -> void:
	if not Motion.live(&"enemy_enter"):
		enter_slide = 0.0
		return
	var e := Motion.entry(&"enemy_enter")
	enter_slide = Motion.amplitude(&"enemy_enter")
	var tw := _tw(&"enter")
	tw.tween_interval(Motion.delay_of(&"enemy_enter"))
	tw.tween_method(func(v: float) -> void: enter_slide = v; queue_redraw(), enter_slide, 0.0, Motion.seconds(&"enemy_enter")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void: enter_slide = 0.0; _end(&"enter"); queue_redraw())


## A hit arrives in the HP counter: the disc flashes (`hit_flash`) and shakes (`hit_shake`;
## no shake under reduce effects: Motion shows the rest state then).
func play_hit() -> void:
	if not Motion.live(&"hit_flash"):
		return
	var e := Motion.entry(&"hit_flash")
	var tw := _tw(&"hit")
	tw.tween_method(func(v: float) -> void: hit_flash = v; queue_redraw(), 1.0, 0.0, Motion.seconds(&"hit_flash")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void: hit_flash = 0.0; _end(&"hit"))
	Motion.shake(self, &"hit_shake", ^"shake")


## A boss phase set new needles (MULTIPLY): they fan out from the first old needle to
## `ticks` (`pointer_migrate`) and stay until the wheel shows its state again.
func play_phase_needles(ticks: Array) -> void:
	if ticks.is_empty():
		return
	var old := shown_pointers()
	var start := old[0] if not old.is_empty() else 0.0
	var starts: Array[float] = []
	var ends: Array[float] = []
	for k in ticks.size():
		var f: float = old[k] if k < old.size() else start
		starts.append(f)
		ends.append(f + float(posmod(roundi(float(ticks[k]) - f) + RC.TICKS / 2, RC.TICKS) - RC.TICKS / 2))
	if not Motion.live(&"pointer_migrate"):
		anim_pointers = ends
		queue_redraw()
		return
	anim_pointers = starts.duplicate()
	var e := Motion.entry(&"pointer_migrate")
	var tw := _tw(&"pointers")
	tw.tween_method(_pointer_step.bind(starts, ends), 0.0, 1.0, Motion.seconds(&"pointer_migrate")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void: _end(&"pointers"))
	# Art pass W3 (§6.1, critique gifs/06): a needle the phase adds draws itself on (from its
	# hub outward, a ring closing on it) rather than just appearing (`needle_draw`).
	if Motion.live(&"needle_draw"):
		var de := Motion.entry(&"needle_draw")
		for k in range(old.size(), ticks.size()):
			needle_grow[k] = 0.0
		var gw := _tw(&"needle_draw")
		gw.tween_method(_set_needle_grow.bind(old.size(), ticks.size()), 0.0, 1.0, Motion.seconds(&"needle_draw")).set_delay(Motion.delay_of(&"needle_draw")).set_ease(de.ease).set_trans(de.trans)
		gw.tween_callback(func() -> void: needle_grow = {}; _end(&"needle_draw"); queue_redraw())


## A phase's new needles drawing on: needle index -> its growth (0 hub only .. 1 whole).
var needle_grow: Dictionary = {}


func _set_needle_grow(v: float, from: int, to: int) -> void:
	for k in range(from, to):
		needle_grow[k] = v
	queue_redraw()


## Where a replay number of `band` ("hp": damage and heals, above the name; "guard": block,
## shield and evade, under the hub's lines) goes, and the font size that keeps `text`
## inside the hub (ANIM-R1: numbers never overlap the name, and at 1.6 they spilled over
## the slices). Returns {at (global), fs, room (px the number may drift)}.
func number_slot(band: String, text: String, crit: bool, icon: int = -1) -> Dictionary:
	var c := global_center()
	var r := hub_radius() * NUMBER_HUB_SHARE
	var ext := hub_text_extent()
	# The number's box sits against the hub's words (where the hub is widest): its top at
	# the foot of the lines (guard), or its foot at the top of the name (HP). It is as big
	# as the font allows while every corner stays inside the hub.
	var edge := minf(ext.y + NUMBER_GAP, r - NUMBER_MIN_FONT) if band == "guard" else maxf(ext.x - NUMBER_GAP, -r + NUMBER_MIN_FONT)
	var side := 1.0 if band == "guard" else -1.0
	var fs := CombatFxLayer.number_font(crit)
	var mid := edge + side * fs * 0.5
	while fs > NUMBER_MIN_FONT:
		mid = edge + side * fs * 0.5
		var hw := (Palette.display().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + CombatFxLayer.NUMBER_OUTLINE + CombatFxLayer.glyph_width(fs, icon)) * 0.5
		var far := maxf(absf(mid - fs * 0.5), absf(mid + fs * 0.5))
		if hw * hw + far * far <= r * r:
			break
		fs -= 1
	mid = edge + side * fs * 0.5
	return {"at": c + Vector2(0.0, mid), "fs": int(fs), "room": 0.0}


## Where a word stamp goes (BLOCKED, EVADED, NO DAMAGE...): in the HP band above the name,
## where the hit's number would have been, and the width it may take there so its box stays
## inside the hub. Returns {at (global), max_w, max_fs}. ANIM-R5 combat 6: with `text` (and
## its mark `icon`), the stamp as drawn (tilted) must fit above the name inside the hub; when
## it can't (a hub with BLOCK / SHIELD lines pushes the name up: NO DAMAGE sat on the name
## after a turn both sides defended) it goes beside the HP number, in the NEXT plate's place
## (empty while a replay plays), where it also says what it is about.
func stamp_slot(text: String = "", icon: String = "") -> Dictionary:
	var r := hub_radius() * NUMBER_HUB_SHARE
	var edge := hub_text_extent().x - NUMBER_GAP
	# As tall as the room over the name allows (never over the name), down to the floor.
	var h := clampf(edge + r, CombatFxLayer.WORD_STAMP_MIN * CombatFxLayer.WORD_BOX_H, CombatFxLayer.WORD_STAMP_FONT * _ts() * CombatFxLayer.WORD_BOX_H)
	edge = maxf(edge, -r + h)
	var mid := edge - h * 0.5
	var far := absf(mid) + h * 0.5
	var hub := {"at": global_center() + Vector2(0.0, mid), "max_w": 2.0 * sqrt(maxf(r * r - far * far, NUMBER_MIN_FONT * NUMBER_MIN_FONT)),
		"max_fs": int(h / CombatFxLayer.WORD_BOX_H)}
	if text == "" or _stamp_fits_hub(hub, text, icon):
		return hub
	var lay := hp_layout()
	var hp: Rect2 = lay["hp"]
	var left := hp.end.x + STAMP_HP_GAP
	var room := maxf(size.x - left - STAMP_HP_GAP, CombatFxLayer.WORD_STAMP_MIN * 4.0)
	var fs := CombatFxLayer.word_stamp_font(text, room, roundi(CombatFxLayer.WORD_STAMP_FONT * _ts() * STAMP_HP_SHARE), icon)
	var w := Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + fs * CombatFxLayer.WORD_BOX_PAD * 2.0 + CombatFxLayer.stamp_icon_width(fs, icon)
	return {"at": global_position + Vector2(left + w * 0.5, hp.get_center().y), "max_w": room, "max_fs": fs, "beside_hp": true}


## Whether stamp `text` at `spot` (a stamp_slot) stays inside the hub and above the name as
## drawn (tilted by CombatFxLayer.WORD_TILT).
func _stamp_fits_hub(spot: Dictionary, text: String, icon: String) -> bool:
	var box := stamp_bounds(spot, text, icon)
	var c := global_center()
	var r := hub_radius() * NUMBER_HUB_SHARE
	for p in [box.position, Vector2(box.end.x, box.position.y), box.end, Vector2(box.position.x, box.end.y)]:
		if (p as Vector2).distance_to(c) > r:
			return false
	return box.end.y <= c.y + hub_text_extent().x


## The screen bounds (global) of stamp `text` drawn at `spot` (a stamp_slot), tilt included.
static func stamp_bounds(spot: Dictionary, text: String, icon: String = "") -> Rect2:
	var fs := CombatFxLayer.word_stamp_font(text, float(spot["max_w"]), int(spot["max_fs"]), icon)
	var w := Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + fs * CombatFxLayer.WORD_BOX_PAD * 2.0 + CombatFxLayer.stamp_icon_width(fs, icon)
	var h := fs * CombatFxLayer.WORD_BOX_H
	var t := absf(CombatFxLayer.WORD_TILT)
	var ext := Vector2(w * cos(t) + h * sin(t), w * sin(t) + h * cos(t))
	return Rect2(Vector2(spot["at"]) - ext * 0.5, ext)


## A stamp beside the HP number: the gap from it (px) and its lettering's share of a hub
## stamp's size.
const STAMP_HP_GAP := 8.0
const STAMP_HP_SHARE := 0.8


## The hub's words from the top of the name to the foot of its last line (local y, from
## the centre): numbers keep off them.
func hub_text_extent() -> Vector2:
	var lay := hub_layout()
	var top: float = lay["top"]
	var ns := int(lay["name_size"])
	var n := int(lay["count"])
	var y0 := top - (int(lay["name_count"]) - 1) * (ns + 1) - ns * 0.8
	var y1 := top + 16.0 + (n - 1) * float(lay["step"]) + float(lay["fs"]) * 0.3 if n > 0 else top + ns * 0.3
	return Vector2(y0, y1)


## The hub's words as laid out (local y from the centre): {top (the last name line's
## baseline), step, fs, width, name (hub_name_lines), name_size, name_count, lines, count,
## inset_alpha}. Art pass W3 (§6.1): under the operative's Polaroid inset when the words fit
## below it; a crowded hub (many lines) keeps its words where they were and fades the inset.
func hub_layout() -> Dictionary:
	var c := _shown()
	var hr := hub_radius()
	var hw := (hr - 10) * 2.0
	var lines := _hub_lines(c)
	var n := lines.size()
	var fs := _fs(HUB_FONT_SIZE)
	var step := fs + 2
	var name_lines := hub_name_lines(hw)
	var ns := int(name_lines[0])
	var name_count := name_lines.size() - 1
	var top := -6.0 - n * step * 0.5
	var inset_alpha := 0.0
	var ir := inset_rect()
	if ir.has_area():
		inset_alpha = 1.0
		var need := ir.end.y - _center().y + HUB_INSET_GAP + (name_count - 1) * (ns + 1) + ns * 0.8
		var foot := maxf(top, need) + (16.0 + (n - 1) * step + fs * 0.3 if n > 0 else ns * 0.3)
		if foot <= hr * HUB_TEXT_SHARE:
			top = maxf(top, need)
		else:
			inset_alpha = INSET_CROWDED_ALPHA
	return {"top": top, "step": step, "fs": fs, "width": hw, "name": name_lines, "name_size": ns, "name_count": name_count,
		"lines": lines, "count": n, "inset_alpha": inset_alpha}


## The gap under the Polaroid inset before the name (px), how far down the hub its words
## may reach (share of the hub radius), and the inset's alpha when the words need its room.
const HUB_INSET_GAP := 3.0
const HUB_TEXT_SHARE := 0.92
const INSET_CROWDED_ALPHA := 0.35


## Where the HP number sits (global): a damage number travels into it.
func hp_counter_spot() -> Vector2:
	var r: Rect2 = hp_layout()["hp"]
	return global_position + r.get_center()


## A point on the HP ring (global) where the HP shown now ends: hit lines end there.
func hp_ring_spot() -> Vector2:
	var c := _shown()
	var frac := clampf(shown_hp() / maxf(1.0, c.max_hp), 0.0, 1.0)
	var a := PI * 0.1 + PI * 0.8 * frac
	return global_center() + Vector2(cos(a), sin(a)) * (_radius() + (HP_ARC_IN + HP_ARC_OUT) * 0.5)


## Valid drop zones pulse while a card is aimed (`drop_zone_pulse`); the hovered one stays
## bright. Off: `stop_zone_pulse`.
func start_zone_pulse() -> void:
	stop_zone_pulse()
	if not Motion.live(&"drop_zone_pulse"):
		return
	var e := Motion.entry(&"drop_zone_pulse")
	var d := Motion.seconds(&"drop_zone_pulse")
	var tw := _tw(&"zones")
	tw.set_loops()
	tw.tween_method(func(v: float) -> void: zone_pulse = v; queue_redraw(), 1.0, Motion.amplitude(&"drop_zone_pulse"), d).set_ease(e.ease).set_trans(e.trans)
	tw.tween_method(func(v: float) -> void: zone_pulse = v; queue_redraw(), Motion.amplitude(&"drop_zone_pulse"), 1.0, d).set_ease(e.ease).set_trans(e.trans)


func stop_zone_pulse() -> void:
	var tw: Tween = _tweens.get(&"zones")
	if tw != null and tw.is_valid():
		tw.kill()
	_tweens.erase(&"zones")
	zone_pulse = 1.0
	queue_redraw()


## Where needle `index` stands on screen (its hub, as shown).
func pointer_spot(index: int) -> Vector2:
	var ps := shown_pointers()
	if ps.is_empty():
		return global_center()
	var a := _ang(ps[clampi(index, 0, ps.size() - 1)])
	return global_center() + Vector2(cos(a), sin(a)) * (_radius() + _band() * NEEDLE_HUB_OUT)


## Where docked satellite `id` stands on screen (its token), the centre when it's gone.
func satellite_spot(id: StringName) -> Vector2:
	for s in (shown_satellites if shown_state != null else satellites):
		if s.id == id:
			return _satellite_pos(s)
	for s in satellites:
		if s.id == id:
			return _satellite_pos(s)
	return global_center()


## ANIM-R4 C6b: where a hit leaves from: on slice `slot`'s band right under needle
## `index` (the slice the needle landed on), or the slice's middle when the needle stands
## elsewhere (a neighbour rule resolved the slice beside it), as shown.
func needle_slot_spot(index: int, slot: int) -> Vector2:
	var c := _shown()
	var ps := shown_pointers()
	if c == null or slot < 0 or index < 0 or index >= ps.size():
		return slot_spot(slot)
	var rot := shown_rotation()
	var under := WheelMath.slice_at(roundi(ps[index] + rot), c.wheel.slice_count)
	if under != slot:
		return slot_spot(slot)
	var a := _ang(ps[index])
	return global_center() + Vector2(cos(a), sin(a)) * (_radius() - _band() * 0.5)


## ANIM-R4 C6g: the room over the disc (global rect: from the view's top to the band's
## outer edge less the tag's gap), where a beaten side's VICTORY stands clear of the wheel
## and its crack (the tag is gone once the fight is over).
func room_above_disc() -> Rect2:
	var top := global_position.y
	var bottom := global_position.y + _center().y - _radius() - VALUE_OUT - _fs(VALUE_FONT_SIZE)
	return Rect2(Vector2(global_position.x, top), Vector2(size.x, maxf(0.0, bottom - top)))


## The middle of slice `slot` on screen (at its status mark), as shown.
func slot_spot(slot: int) -> Vector2:
	var c := _shown()
	var tps := c.wheel.ticks_per_slice()
	var a := _ang(slot * tps - shown_rotation())
	var dir := Vector2(cos(a), sin(a))
	return global_center() + dir * (_radius() - _band() * 0.5)


## Where the `k`-th floating number of a burst starts (global) and how far it may rise:
## inside the inner disc, clear of every needle (they only reach the slice band); numbers
## side by side step left and right.
func number_anchor(k: int) -> Vector2:
	var room := number_room()
	var step: float = [0.0, -0.5, 0.5][posmod(k, 3)] * room
	return global_center() + Vector2(step, room * 0.35)


## The radius (px) floating numbers keep within, round the centre.
func number_room() -> float:
	return (_radius() - _band()) * NUMBER_ROOM


## The pieces a broken wheel falls apart into, as shown (global): ANIM-R3 A6g, the real
## wheel: each slice's band keeps its art (its translucent neon fill, bright rim, icon and
## value: [polygon, fill, {type, slice_col, icon_at, icon_r, value, value_at, value_fs,
## rim}]), and the dark hub cracks into a wedge per slice ([polygon, fill, {rim}]).
func slice_pieces() -> Array:
	var out: Array = []
	var c := _shown()
	if c == null or lookup == null:
		return out
	var center := global_center()
	var radius := _radius()
	var band := _band()
	var inner := radius - band
	var tps := c.wheel.ticks_per_slice()
	var rot := shown_rotation()
	for i in c.wheel.slice_count:
		var slice := lookup.get_content(c.wheel.slot_slice_ids[i]) as SliceData
		var a0 := _tick_angle(i * tps - tps / 2.0, rot)
		var a1 := _tick_angle(i * tps + tps / 2.0, rot)
		var mid := _tick_angle(i * tps, rot)
		var dir := Vector2(cos(mid), sin(mid))
		var sc := Palette.slice_color(slice.slice_type) if slice != null else wheel_color
		var miss := slice != null and slice.slice_type == RC.SliceType.MISS
		var art := {"rim": sc.lightened(0.35), "slice_col": sc, "value": "", "value_fs": _fs(VALUE_FONT_SIZE)}
		if slice != null:
			art["type"] = slice.slice_type
			art["icon_at"] = center + dir * (inner + band * 0.42)
			art["icon_r"] = band * 0.36
			if slice.base_output > 0:
				art["value"] = str(slice.base_output)
				art["value_at"] = center + dir * (radius + VALUE_OUT)
		out.append([_wedge(center, inner, radius, minf(a0, a1) + 0.03, maxf(a0, a1) - 0.03), Color(sc, 0.18 if miss else 0.5), art])
		var fan := PackedVector2Array([center])
		for k in 11:
			var a := lerpf(minf(a0, a1), maxf(a0, a1), k / 10.0)
			fan.append(center + Vector2(cos(a), sin(a)) * (inner - 3.0))
		out.append([fan, HUB_FILL, {"rim": Color(wheel_color, 0.6)}])
	return out


## The hub disc's fill (the break's hub pieces too).
const HUB_FILL := Palette.NIGHT_SKY


## The hub's radius on screen.
func hub_radius() -> float:
	return _radius() - _band()


func _process(delta: float) -> void:
	# Slice blur follows the turn speed (ticks per second) against `wheel_spin_blur`'s
	# amplitude, fading in and out over its duration.
	var rot := shown_rotation() if combatant != null else 0.0
	var speed := 0.0
	if not is_nan(_last_shown_rot) and delta > 0.0:
		speed = absf(rot - _last_shown_rot) / delta
	_last_shown_rot = rot
	var want := 1.0 if Motion.live(&"wheel_spin_blur") and speed > Motion.amplitude(&"wheel_spin_blur") else 0.0
	var rate := delta / maxf(0.001, Motion.seconds(&"wheel_spin_blur"))
	var was := blur
	blur = move_toward(blur, want, rate)
	if blur != was:
		queue_redraw()
	var looping := false
	if ambient_on():
		ambient_phase = fposmod(ambient_phase + delta / maxf(0.001, Motion.seconds(&"bezel_ambient")), 1.0)
		looping = true
	else:
		ambient_phase = 0.0
	if heartbeat_on():
		heart_t = fposmod(heart_t + delta, maxf(0.001, Motion.seconds(&"hp_heartbeat") + Motion.delay_of(&"hp_heartbeat")))
		looping = true
	else:
		heart_t = 0.0
	if looping:
		queue_redraw()
		return
	if not _tweens.has(&"turn") and blur <= 0.0:
		_last_shown_rot = NAN
		set_process(false)


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
## The disc's radius with its needles' band (px): a break's local flash covers it.
func disc_radius() -> float:
	return _radius() + _band() * NEEDLE_HUB_OUT


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
			var a := _ang(int(zone["slot"]) * tps - shown_rotation())
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
	# The nearest satellite or arrow within reach wins (H24: at 1.6 the inner ring's arrow
	# answered as the outer one, 26 px away, and a drone next to an arrow took its clicks).
	var best := {}
	var best_d := INF
	for sat in satellites:
		var sp := _satellite_pos(sat)
		var d := sp.distance_to(point)
		if d <= SATELLITE_HIT * maxf(1.0, _ts()) and d < best_d:
			# Which side of the satellite: the clockwise side is +1 (a nudge or Undock aimed
			# at a satellite takes its way from the side it is dropped on).
			var cw := (sp - global_center()).orthogonal() * -1.0
			best = {"kind": "satellite", "id": sat.id, "direction": 1 if (point - sp).dot(cw) >= 0.0 else -1}
			best_d = d
	for ar in arrows():
		var d := arrow_center(int(ar["ring"]), int(ar["direction"])).distance_to(point)
		if d <= ARROW_HIT * maxf(1.0, _ts()) and d < best_d:
			best = {"kind": "arrow", "ring": ar["ring"], "direction": ar["direction"]}
			best_d = d
	if not best.is_empty():
		return best
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
	var a := _ang(sat.dock_slot * tps - shown_rotation())
	var p := global_center() + Vector2(cos(a), sin(a)) * (_radius() + satellite_out(a))
	# ANIM-R2 E7: a token under the tag turns round the rim, away from the top, until it is
	# clear of it (at 1.6 a drone's hex sat on the tag's chips).
	var tag := intent_rect()
	if tag.has_area():
		var tok0 := SATELLITE_TOKEN * _ts()
		var turn := signf(cos(a)) if absf(cos(a)) > 0.001 else 1.0
		for k in SAT_TAG_STEPS:
			if not tag.intersects(Rect2(p - Vector2(tok0, tok0), Vector2(tok0, tok0) * 2.0)):
				break
			a += turn * SAT_TAG_STEP
			p = global_center() + Vector2(cos(a), sin(a)) * (_radius() + satellite_out(a))
	# In the bottom sector the HP number, NEXT plate and last-turn line sit under the disc:
	# a token there moves to the side of them (H23: it covered "40/40").
	# Beside the measured HP number, NEXT plate and LAST TURN plate whenever the token would
	# meet them (H23: it covered "40/40"; H24: a fixed 90 px half width left it on NEXT).
	var tok := SATELLITE_TOKEN * _ts()
	var side := 1.0 if cos(a) >= 0.0 else -1.0
	var reach := HP_BLOCK_HALF * _ts() if sin(a) > BOTTOM_SECTOR_SIN else 0.0
	for r in _hp_block_rects():
		var gr := Rect2(r.position + global_position, r.size).grow(tok)
		if sin(a) > BOTTOM_SECTOR_SIN or gr.has_point(p):
			reach = maxf(reach, ((gr.end.x - global_center().x) if side > 0.0 else (global_center().x - gr.position.x)) - tok)
	if reach > 0.0:
		p.x = global_center().x + side * maxf(absf(p.x - global_center().x), reach + tok + SATELLITE_GAP * _ts())
	return p


## How far outside the rim a satellite at screen angle `a` docks: past the slice value
## drawn at that angle (H22: they sat on them). ANIM-R2 E7: the value's box is wider than
## tall, so the distance follows the angle (a token by a side value clears the widest value,
## two digits, not only half its height: at 1.6 "8" met the drone's hex).
static func satellite_out(a: float) -> float:
	var vs := _fs(VALUE_FONT_SIZE)
	var half := Vector2(Palette.display().get_string_size(VALUE_WIDEST, HORIZONTAL_ALIGNMENT_LEFT, -1, vs).x * 0.5, vs * 0.5)
	var reach := absf(cos(a)) * half.x + absf(sin(a)) * half.y
	return VALUE_OUT + reach + SATELLITE_TOKEN * _ts() + VALUE_TOKEN_GAP * _ts()


## The widest slice value a satellite keeps clear of, and the gap between them (px at 1.0).
const VALUE_WIDEST := "88"
const VALUE_TOKEN_GAP := 3.0
## A token under the tag turns round the rim by this much (rad) a step, at most this often.
const SAT_TAG_STEP := 0.06
const SAT_TAG_STEPS := 16


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
	if what == NOTIFICATION_RESIZED:
		_place_backdrop()
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
	var cy := minf(size.y * CENTER_Y, size.y - bottom_need() - _radius())
	return Vector2(left_reserve + (size.x - left_reserve) * center_x + enter_slide, cy) + shake


## Room kept under the disc for the HP number and the last-turn line (px).
static func _bottom_need() -> float:
	return HP_TEXT_GAP + _fs(HP_FONT_SIZE) + _fs(HUB_FONT_SIZE) + LAST_TURN_GAP + DISC_MARGIN * 0.2


## This wheel's room under its disc: _bottom_need, plus the operative's net line (§6.2: what
## it receives, once, under its HP).
func bottom_need() -> float:
	return _bottom_need() + (net_line_height() if combatant != null and combatant.is_player else 0.0)


## The net line's row height (px): its lettering and a gap.
static func net_line_height() -> float:
	return _fs(NET_FONT_SIZE) * NET_LINE_SHARE + LAST_TURN_GAP


## The net line's lettering (§4.2 `body`) and its row's height (x its size).
const NET_FONT_SIZE := UiTheme.BODY
const NET_LINE_SHARE := 1.3
## The minus the net line writes (the typographic one, as the equations).
const MINUS := "−"


## Art pass W3 (§6.2): what the operative receives if SEND IT is pressed now, set by the scene
## (CombatScene.net_line_for): {net, hit, soaked, evaded}; {} = nothing (or not the operative).
var net_line: Dictionary = {}


## The net line as tokens: [{text} or {icon (a StatIcon kind)}, color], e.g. "−3", the heart,
## "(7 − 4)": the glyph and the numbers stand apart (§12). Empty while a replay plays.
func net_tokens() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if net_line.is_empty() or replaying or combatant == null or not combatant.is_player:
		return out
	var net := int(net_line.get("net", 0))
	var hit := int(net_line.get("hit", 0))
	var soaked := int(net_line.get("soaked", 0))
	var evaded := int(net_line.get("evaded", 0))
	var col := LOSS_COLOR if net < 0 else (HP_COLOR if net > 0 else Palette.TEXT_MID)
	out.append({"text": (MINUS + str(-net)) if net < 0 else ("+%d" % net if net > 0 else "0"), "color": col})
	out.append({"icon": StatIcon.HP, "color": col})
	if hit > 0 and (soaked > 0 or evaded > 0):
		var parts := "(" + str(hit)
		if soaked > 0:
			parts += " " + MINUS + " " + str(soaked)
		if evaded > 0:
			parts += " " + MINUS + " " + str(evaded)
		out.append({"text": parts + ")", "color": Palette.TEXT_HI})
		var rest := net + maxi(0, hit - soaked - evaded)
		if rest != 0:
			out.append({"text": "· " + (("+%d" % rest) if rest > 0 else MINUS + str(-rest)), "color": HP_COLOR if rest > 0 else LOSS_COLOR})
	return out


## The net line as plain words (tests, tooltip): its tokens, the heart as "♥".
func net_text() -> String:
	var parts := PackedStringArray()
	for t in net_tokens():
		parts.append(String(t["text"]) if t.has("text") else "♥")
	return " ".join(parts)


func net_tooltip() -> String:
	return tr("If you SEND IT now: your HP changes by %s (hits aimed at you, less what your guard takes).") % net_text()


## The net line's width at `fs` (px).
func net_width(fs: int) -> float:
	var w := 0.0
	for t in net_tokens():
		w += fs * NET_ICON_SHARE if t.has("icon") else Palette.mono().get_string_size(String(t["text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		w += fs * NET_GAP_SHARE
	return maxf(0.0, w - fs * NET_GAP_SHARE)


## The heart's room and the gap between tokens (shares of the lettering).
const NET_ICON_SHARE := 1.1
const NET_GAP_SHARE := 0.3


func _draw_net_line(r: Rect2, fs: int) -> void:
	draw_rect(r.grow_individual(3.0, 0.0, 3.0, 0.0), Color(Palette.NIGHT_SKY, NET_PLATE_ALPHA))
	var x := r.position.x
	var mid := r.position.y + r.size.y * 0.5
	var f := Palette.mono()
	for t in net_tokens():
		var col := _col(Color(t["color"]))
		if t.has("icon"):
			StatIcon.draw(self, Vector2(x + fs * NET_ICON_SHARE * 0.5, mid), fs * 0.45, StringName(t["icon"]), col, true)
			x += fs * NET_ICON_SHARE
		else:
			var s := String(t["text"])
			draw_string(f, Vector2(x, mid + f.get_ascent(fs) * 0.5 - f.get_descent(fs) * 0.25), s, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
			x += f.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		x += fs * NET_GAP_SHARE


## The plate under the net line (alpha of the night ink).
const NET_PLATE_ALPHA := 0.8


func _radius() -> float:
	var r := minf(size.x, size.y) * RADIUS_SHARE * size_scale
	if left_reserve > 0.0:
		var avail := size.x - left_reserve
		r = minf(r, minf(avail * center_x, avail * (1.0 - center_x)) - DISC_MARGIN)
	# Vertically the disc (r above, r below), the tag above it (its bottom tag_bottom(): past
	# the band and the tag's gap, and never nearer than TAG_CLEAR, so it never covers the
	# nudge arrows or their key hints; art pass W3, §6.2) with its tape, and the HP number,
	# the net line and LAST TURN below share the view's height; the centre moves to fit.
	var avail := size.y - bottom_need() - _tag_reserve() - tape_height()
	var r_full := minf((avail - INTENT_HEIGHT) / (2.0 + BAND_SHARE), (avail - TAG_CLEAR) / 2.0)
	r = minf(r, r_full)
	return maxf(MIN_RADIUS, r)


## §6.2: a tag's bottom edge (local y): past the slice band and the tag's gap, at radius +
## TAG_CLEAR or wider (the nudge arrows and their key hints sit under it).
func tag_bottom() -> float:
	return _center().y - _radius() - maxf(_band() + INTENT_HEIGHT, TAG_CLEAR)


## §6.2 / STYLE_GUIDE 4: a tag sits at radius + this or wider (the arrows, their hints and the
## values stay clear under it).
const TAG_CLEAR := EXTENT


## Height kept for the tag at the current text scale (title and TAG_CHIP_ROWS rows).
static func _tag_reserve() -> float:
	return INTENT_HEIGHT * _ts() + _chip_row_cap() * (CHIP_HEIGHT * _ts() + 2.0)


## Chip rows kept: fewer at big text so the wheel doesn't shrink away (H22).
static func _chip_row_cap() -> int:
	return TAG_CHIP_ROWS  # §6.2: one chip row at every text size; the rest folds into "+N MORE"


## Above this text scale the tag keeps one chip row.
const BIG_TEXT := 1.3


## Width of the slice bar band.
func _band() -> float:
	return _radius() * BAND_SHARE


## Screen angle of a position `x` ticks round from the top, clockwise on screen when the
## wheel's rotation grows (H20: +1 turns the wheel clockwise, as a right nudge reads).
static func _ang(x: float) -> float:
	return deg_to_rad(-x * DEG_PER_TICK - 90.0)


func _tick_angle(tick: float, rotation_ticks: float) -> float:
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
	if shown_state == null:
		_draw_view()
		return
	# A SEND IT replay draws the snapshot it started from (the view's own copy; the state
	# is untouched), then puts the live combatant back.
	var real := combatant
	var real_sats := satellites
	combatant = shown_state
	satellites = shown_satellites
	_draw_view()
	combatant = real
	satellites = real_sats


func _draw_view() -> void:
	var wheel := combatant.wheel
	var center := _center()
	var radius := _radius()
	var band := _band()
	var inner := radius - band
	var line := _col(wheel_color if combatant.is_alive() else Color(wheel_color, 0.3))
	var tps := wheel.ticks_per_slice()
	var rot := shown_rotation()
	# Platform so the wheel reads over the city.
	draw_circle(center, radius + WheelBezel.BEZEL_W + PLATFORM_PAD, Color(Palette.NIGHT_SKY, 0.55))
	if defeated():
		# ANIM-R1: a beaten enemy leaves its empty spot with a DEFEATED stamp (a new enemy
		# can never read as this one coming back).
		_draw_defeated(center, radius, inner)
		_draw_hp(center, radius)
		return
	# Art pass W3 (§6.1): the bezel says whose wheel it is (it never flips with the disc).
	WheelBezel.draw_bezel(self, center, radius, bezel_radius(), look, Settings.high_contrast)
	# §7.1: the operative's class ornament on its bezel (T0 ambient where it moves).
	WheelBezel.draw_ornament(self, center, radius, bezel_radius(), look, ambient_phase)
	if flip_squash < 1.0:
		# FLIP: the disc squashes to a line about its centre and opens mirrored.
		draw_set_transform(Vector2(center.x * (1.0 - flip_squash), 0.0), 0.0, Vector2(flip_squash, 1.0))
	if inverted:
		draw_circle(center, radius + 24, Color(Palette.PAPER, 0.9))
	draw_circle(center, inner - 3, HUB_FILL)
	WheelBezel.draw_hub_pattern(self, center, inner - 3, look)
	WheelBezel.draw_class_hub(self, center, inner - 3, look)
	var status_ghosts := {}
	if not replaying:
		for st in outcome.get("statuses", []):
			status_ghosts[int(st["slot"])] = int(st["after"])
	# Slices: neon bars, icon inside, value outside, the perfect arrow at the outer edge.
	for i in wheel.slice_count:
		var slice := lookup.get_content(wheel.slot_slice_ids[i]) as SliceData
		var a0 := _tick_angle(i * tps - tps / 2.0, rot)
		var a1 := _tick_angle(i * tps + tps / 2.0, rot)
		var mid := _tick_angle(i * tps, rot)
		var sc := Palette.slice_color(slice.slice_type)
		if blur > 0.0:
			# Fast turn: faint copies trail each slice against the way it turns.
			for k in range(1, BLUR_COPIES + 1):
				var back := -_blur_dir * BLUR_STEP * k
				var b0 := _tick_angle(i * tps - tps / 2.0 + back, rot)
				var b1 := _tick_angle(i * tps + tps / 2.0 + back, rot)
				draw_colored_polygon(_wedge(center, inner, radius, minf(b0, b1), maxf(b0, b1)), _col(Color(sc, 0.22 * blur / k)))
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
			draw_polyline(wedge, _col(TARGET_COLOR if hot else Color(TARGET_COLOR, 0.55 * zone_pulse)), 3.0 if hot else 1.5, true)
		if i == miss_slot and miss_static > 0.0:
			_draw_static(center, inner, radius, minf(a0, a1), maxf(a0, a1))
		var dir := Vector2(cos(mid), sin(mid))
		SliceIcon.draw_on_slice(self, center + dir * (inner + band * 0.42), band * 0.36, slice.slice_type, sc)
		if slice.base_output > 0:
			var vs := _fs(VALUE_FONT_SIZE)
			var vat := center + dir * (radius + VALUE_OUT) + Vector2(-vs, vs * 0.4)
			# On the bezel (paper stickers or corp metal): an ink outline keeps it readable.
			draw_string_outline(Palette.display(), vat, str(slice.base_output), HORIZONTAL_ALIGNMENT_CENTER, vs * 2, vs, VALUE_OUTLINE, _col(Palette.NIGHT_SKY))
			draw_string(Palette.display(), vat, str(slice.base_output), HORIZONTAL_ALIGNMENT_CENTER, vs * 2, vs, _col(sc.lightened(0.35)))
		var tip := center + dir * (radius - 3)
		var base := center + dir * (radius - 10)
		var side := dir.orthogonal() * 4.0
		draw_colored_polygon(PackedVector2Array([tip, base + side, base - side]), _col(Palette.PAPER))
		var status: int = wheel.slice_statuses[i]
		var sp := center + dir * (inner + band * 0.5) + dir.orthogonal() * band * 0.42
		# ANIM-R4 C6f: a status wears its good / bad colour for the operative (green: good for
		# you, red: bad for you), on its mark, its ring and the slice's rim as it lands.
		var scol := status_color(status, combatant.is_player)
		if status != RC.Status.NONE:
			draw_circle(sp, 7, Palette.NIGHT_SKY)
			draw_arc(sp, 7, 0, TAU, 16, _col(scol), 1.5, true)
			draw_string(Palette.mono(), sp + Vector2(-7, 5), Palette.STATUS_GLYPHS.get(status, ""), HORIZONTAL_ALIGNMENT_CENTER, 14, 11, _col(scol))
		if status_flash.has(i):
			# ANIM-R3 A6j: a status just landed here (CORRUPTED...): its mark rings out and the
			# slice's rim lights, so the slice it hit is seen as it lands.
			var fl := float(status_flash[i])
			draw_arc(sp, STATUS_MARK_R + Motion.amplitude(&"status_mark") * (1.0 - fl), 0, TAU, 24, _col(Color(scol, 0.35 + 0.65 * fl)), 3.0, true)
			var sclosed := wedge.duplicate()
			sclosed.append(wedge[0])
			draw_polyline(sclosed, _col(Color(scol, fl)), 3.0, true)
		if status_ghosts.has(i):
			# The status this turn will leave on the slice: a dashed acid ring (or a cross
			# when it clears).
			_draw_dashed_arc(sp, 10, 0, TAU, _col(Palette.CELL_ACID), 1.5)
			var g: int = status_ghosts[i]
			draw_string(Palette.mono(), sp + Vector2(-7, 5), Palette.STATUS_GLYPHS.get(g, "×") if g != RC.Status.NONE else "×", HORIZONTAL_ALIGNMENT_CENTER, 14, 11, _col(Palette.CELL_ACID))
		if wheel.slot_firmware_ids[i] != &"":
			var fp := center + dir * (inner + 5) - dir.orthogonal() * band * 0.3
			draw_rect(Rect2(fp - Vector2(3, 3), Vector2(6, 6)), _col(Palette.NET_CYAN))
	# Art pass W3 (critique gifs/03): tick marks round the rim turn with the wheel, so a spin's
	# ticks are seen passing the needle.
	for t in RC.TICKS:
		var ta := _tick_angle(float(t), rot)
		var td := Vector2(cos(ta), sin(ta))
		draw_line(center + td * (radius - RIM_TICK), center + td * radius, _col(Color(Palette.PAPER, RIM_TICK_ALPHA)), 1.0, true)
	_draw_landed(center, radius, inner, tps, rot)
	draw_arc(center, radius, 0, TAU, 96, Color(line, 0.9), 1.5)
	draw_arc(center, inner, 0, TAU, 96, Color(line, 0.6), 1.0)
	if hit_flash > 0.0:
		# A hit landed in the HP counter: the disc flashes.
		draw_circle(center, radius, _col(Color(LOSS_COLOR, hit_flash * Motion.amplitude(&"hit_flash"))))
	if wheel.has_inner_ring():
		var ring_r := inner - 12
		var irot := shown_inner_rotation()
		for k in RC.RING_SEGMENTS:
			var seg := lookup.get_content(wheel.ring_segment_ids[k]) as RingSegmentData
			var s0 := _tick_angle(k * 10 - 5, irot)
			var e0 := _tick_angle(k * 10 + 5, irot)
			draw_arc(center, ring_r, minf(s0, e0), maxf(s0, e0), 12, Color(line, 0.35 if k % 2 == 0 else 0.2), 9.0)
			var m := _tick_angle(k * 10, irot)
			draw_string(Palette.mono(), center + Vector2(cos(m), sin(m)) * (ring_r - 14) + Vector2(-8, 4), TextDb.t(seg, "display_name") if seg != null else "?", HORIZONTAL_ALIGNMENT_LEFT, -1, mini(_fs(9), 12), _col(Palette.PAPER))
	if ring_pulse > 0.0:
		# Good landing: a clean ring grows off the rim and fades.
		draw_arc(center, radius + Motion.amplitude(&"precision_good_ring") * ring_pulse, 0, TAU, 64, _col(Color(Palette.PAPER, 1.0 - ring_pulse)), 3.0, true)
	for t in trails:
		# Orbit trail: the arc a needle just swept, fading.
		var ta := _ang(float(t[0]))
		var tb := _ang(float(t[1]))
		_draw_dashed_arc(center, radius + band * NEEDLE_HUB_OUT, minf(ta, tb), maxf(ta, tb), Color(_col(Palette.PAPER), trail_alpha), 3.0)
	# Pointers: short white gauge needles, hub just outside the rim, tip just past its edge.
	var pcol := Color(_col(Palette.PAPER), pointer_alpha)
	var ps := shown_pointers()
	for pk in ps.size():
		var p: float = ps[pk]
		var a := _ang(p)
		var dir := Vector2(cos(a), sin(a))
		var hub := center + dir * (radius + band * NEEDLE_HUB_OUT)
		var ntip := center + dir * (radius - band * 0.2)
		var hub_r := NEEDLE_HUB_R * (pulse_scale if pk == pulse_pointer else 1.0)
		if needle_grow.has(pk):
			var g := clampf(float(needle_grow[pk]), 0.0, 1.0)
			ntip = hub.lerp(ntip, g)
			draw_arc(hub, hub_r + Motion.amplitude(&"needle_draw") * (1.0 - g), 0, TAU, 24, Color(_col(Palette.CELL_ACID), 1.0 - g), 3.0, true)
		if pk == pulse_pointer:
			# The needle resolving now: its hub swells and glows.
			draw_circle(hub, hub_r + 5.0, Color(_col(Palette.CELL_ACID), 0.35))
		draw_colored_polygon(PackedVector2Array([ntip, hub + dir.orthogonal() * 4.0, hub - dir.orthogonal() * 4.0]), pcol)
		draw_circle(hub, hub_r, Palette.NIGHT_SKY)
		draw_arc(hub, hub_r, 0, TAU, 20, pcol, 2.5)
		draw_circle(hub, 3, pcol)
		if wheel.pointer_orbit != 0:
			for k in range(1, 4):
				var oa := _ang(fposmod(p + wheel.pointer_orbit * k, RC.TICKS))
				draw_circle(center + Vector2(cos(oa), sin(oa)) * (radius + band * NEEDLE_HUB_OUT), 3, Color(Palette.PAPER, 0.5 - k * 0.12))
	# Telegraphed migration (GDD 2.11, 9.2): next turn's needles, dashed and flickering.
	for p in wheel.pending_pointer_ticks:
		var a := _ang(p)
		var ntip := center + Vector2(cos(a), sin(a)) * (radius - band * 0.2)
		var hub := center + Vector2(cos(a), sin(a)) * (radius + band * NEEDLE_HUB_OUT)
		var mcol := Color(_col(Palette.CELL_ACID), 1.2 - pointer_alpha)
		var n := 6
		for k in n:
			if k % 2 == 0:
				draw_line(hub.lerp(ntip, float(k) / n), hub.lerp(ntip, float(k + 1) / n), mcol, 3.0)
		draw_string(Palette.mono(), hub + Vector2(10, -4), tr("next"), HORIZONTAL_ALIGNMENT_LEFT, -1, _fs(HUB_FONT_SIZE), mcol)
	if not replaying:
		_draw_ghost(center, radius, wheel)
		_draw_inner_ghost(center, radius, wheel)
	if flip_squash < 1.0:
		draw_set_transform(Vector2.ZERO)
	_draw_hp(center, radius)
	_draw_hub(center, inner, line)
	var plate := nameplate()
	if not plate.is_empty():
		_draw_nameplate(plate)
	else:
		var badge := badge_rect()
		if badge.has_area():
			# Art pass W3 (§6.1, §7.2): the enemy's portrait hangs above its bezel: W5's
			# hologram bust in a machined, notched frame.
			if bust != null:
				WheelBezel.draw_badge_frame(self, badge, look)
			else:
				WheelBezel.draw_badge(self, badge, shown_subject(), look, portrait_texture)
		if bust != null:
			bust.visible = badge.has_area()
			bust.position = badge.position
			bust.custom_minimum_size = badge.size
			bust.size = badge.size
	if flatlined and combatant.is_player:
		_draw_flatlined(center, radius, inner)
	if highlighted and combatant.is_alive():
		_draw_crosshair(center, radius + 56)
		# A crosshair mark by the top-right bracket names the reticle without words.
		var cm := center + Vector2(cos(-PI * 0.25), sin(-PI * 0.25)) * (radius + 56 + 16)
		draw_arc(cm, 7, 0, TAU, 16, _col(TARGET_COLOR), 2.0)
		draw_line(cm + Vector2(-11, 0), cm + Vector2(11, 0), _col(TARGET_COLOR), 2.0)
		draw_line(cm + Vector2(0, -11), cm + Vector2(0, 11), _col(TARGET_COLOR), 2.0)
	if _zone_is(valid_zones, {"kind": "hub"}):
		var hot := _zone_is([hover_zone], {"kind": "hub"})
		draw_arc(center, inner - 4, 0, TAU, 48, _col(TARGET_COLOR if hot else Color(TARGET_COLOR, 0.55 * zone_pulse)), 3.0 if hot else 1.5)
	# Intent: a taped paper tag above the needle (what resolves next and its results).
	var tag := _intent_rect_local()
	_check_tag_change(tag)
	var held := replaying and not replay_tag.is_empty() and tag.has_area()
	if held:
		# ANIM-R3 A6b: the forecast stays through the replay, its lines ticked as they happen
		# (its tape reads THIS TURN once the result holds), then fades.
		if replay_tag_alpha > 0.0:
			_intent_tag(tag, replay_tag_alpha)
	elif replaying and caption != "" and caption_shown > 0.0:
		_draw_caption(caption, caption_shown)
	elif enter_slide > 0.0 and not tag.has_area():
		# An enemy entering with no forecast yet: its own name on the plate where its tag
		# will go. ANIM-R2 E7: a forecast is never hidden by it (the tag slides in with the
		# wheel; the name is in its hub).
		_draw_caption(shown_name().to_upper(), 1.0)
	if tag.has_area() and not replaying:
		if tag_flip < 1.0:
			# Paper flip: the tag turns on its tape (top edge) as its content changes.
			var s := cos(deg_to_rad((1.0 - tag_flip) * Motion.amplitude(&"intent_flip")))
			draw_set_transform(Vector2(0.0, tag.position.y * (1.0 - s)), 0.0, Vector2(1.0, s))
		_intent_tag(tag)
		draw_set_transform(Vector2.ZERO)
	_draw_arrows()  # after the tag: the arrows stay on top at big text (H22)
	_draw_satellites()


## The tag's content as text (title and chips): a change flips the tag, the same content
## re-set on every hover doesn't (ANIM-2: chips don't jitter).
func intent_signature() -> String:
	if replaying or intent.is_empty() or String(intent.get("text", "")) == "":
		return ""
	var parts := PackedStringArray([String(intent.get("text", ""))])
	for chip in intent.get("chips", []):
		parts.append(String(chip.get("text", "")))
	return "|".join(parts)


func _check_tag_change(tag: Rect2) -> void:
	var sig := intent_signature() if tag.has_area() else ""
	if sig == _intent_sig:
		return
	_intent_sig = sig
	if sig != "":
		_flip_tag.call_deferred()


## Starts the tag's paper flip (`intent_flip`).
func _flip_tag() -> void:
	if not Motion.live(&"intent_flip"):
		tag_flip = 1.0
		return
	var e := Motion.entry(&"intent_flip")
	tag_flip = 0.0
	tag_flips += 1
	var tw := _tw(&"tag")
	tw.tween_method(func(v: float) -> void: tag_flip = v; queue_redraw(), 0.0, 1.0, Motion.seconds(&"intent_flip")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void: tag_flip = 1.0; _end(&"tag"))


## True while the tag flips (tests: the same content never starts a flip).
func tag_flipping() -> bool:
	return _tweens.has(&"tag")


## The slices the needles landed on (ANIM-R1): a thick rim in the slice's colour, bright
## as they latch; a MISS slice gets a big grey X.
func _draw_landed(center: Vector2, radius: float, inner: float, tps: float, rot: float) -> void:
	if landed.is_empty():
		return
	for slot in landed:
		var i := int(slot)
		if i < 0 or i >= combatant.wheel.slice_count:
			continue
		var slice := lookup.get_content(combatant.wheel.slot_slice_ids[i]) as SliceData
		var sc := Palette.slice_color(slice.slice_type) if slice != null else wheel_color
		var a0 := _tick_angle(i * tps - tps / 2.0, rot)
		var a1 := _tick_angle(i * tps + tps / 2.0, rot)
		var wedge := _wedge(center, inner, radius, minf(a0, a1), maxf(a0, a1))
		draw_colored_polygon(wedge, _col(Color(sc.lightened(0.3), 0.55 * landing_pulse)))
		var closed := wedge.duplicate()
		closed.append(wedge[0])
		draw_polyline(closed, _col(Color(sc.lightened(0.4), maxf(0.6, landing_pulse))), LANDED_RIM, true)
		if bool(landed[slot]):
			# MISS: a big grey X across the slice.
			var m := (a0 + a1) * 0.5
			var mid := center + Vector2(cos(m), sin(m)) * (inner + radius) * 0.5
			var arm := (radius - inner) * MISS_X_SHARE
			var grey := _col(Palette.slice_color(RC.SliceType.MISS).lightened(0.3))
			draw_line(mid + Vector2(-arm, -arm), mid + Vector2(arm, arm), Color(Palette.INK, 0.8), MISS_X_WIDTH + 3.0)
			draw_line(mid + Vector2(-arm, arm), mid + Vector2(arm, -arm), Color(Palette.INK, 0.8), MISS_X_WIDTH + 3.0)
			draw_line(mid + Vector2(-arm, -arm), mid + Vector2(arm, arm), grey, MISS_X_WIDTH)
			draw_line(mid + Vector2(-arm, arm), mid + Vector2(arm, -arm), grey, MISS_X_WIDTH)


## A beaten enemy's empty spot: a dashed ring where the disc was, its name and DEFEATED.
func _draw_defeated(center: Vector2, radius: float, inner: float) -> void:
	_draw_dashed_arc(center, radius, 0.0, TAU, _col(Color(wheel_color, DEFEATED_DIM)), 2.0)
	_draw_dashed_arc(center, inner, 0.0, TAU, _col(Color(wheel_color, 0.3)), 1.5)
	var hw := (inner - 10) * 2.0
	var name_lines := hub_name_lines(hw)
	var name_size := int(name_lines[0])
	for k in name_lines.size() - 1:
		var ny := -inner * 0.45 - (name_lines.size() - 2 - k) * (name_size + 1)
		draw_string(Palette.marker(), center + Vector2(-hw * 0.5, ny), String(name_lines[k + 1]), HORIZONTAL_ALIGNMENT_CENTER, hw, name_size, _col(Color(wheel_color, 0.7)))
	var word := tr("DEFEATED")
	var fs := _fs(DEFEATED_FONT)
	var font := Palette.marker()
	var ww := font.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	while fs > NUMBER_MIN_FONT and ww + fs > radius * 1.8:
		fs -= 1
		ww = font.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var box := Rect2(-ww * 0.5 - fs * 0.3, -fs * 0.7, ww + fs * 0.6, fs * 1.4)
	# ANIM-R4 C6g: in the beaten wheel's own colour, on its own side (red read as pink under
	# VICTORY, and as the operative's loss).
	var dcol := defeated_color()
	draw_set_transform(center, STAMP_TILT, Vector2.ONE)
	draw_rect(box, Color(Palette.NIGHT_SKY, 0.85))
	draw_rect(box, dcol, false, 3.0)
	draw_string(font, Vector2(-ww * 0.5, fs * 0.35), word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, dcol)
	draw_set_transform(Vector2.ZERO)
	# ANIM-R3 A6g: a skull under the stamp marks the beaten side without words.
	var sr := minf(fs * SKULL_SHARE, inner * 0.3)
	draw_skull(self, center + Vector2(0.0, fs * 0.9 + sr * 1.2), sr, dcol)


## ANIM-R5 combat 2: the operative's wheel once the fight is lost: the disc goes dark and a
## DEFEAT stamp with a skull stays on it while the fight waits for JACK OUT (the replay's
## DEFEAT faded after a second and left a wheel that looked as if the fight went on). It
## pops in (`defeat_stamp`: from amplitude x its size).
var flatlined: bool = false
var flatline_pop: float = 1.0
## The DEFEAT stamp's lettering at text scale 1.0 (px) and the veil over the disc (alpha).
const FLATLINE_FONT := 34
const FLATLINE_VEIL := 1.0 - DEFEATED_DIM


## The DEFEAT stamp lands on the operative's wheel (and stays).
func play_flatline() -> void:
	flatlined = true
	if not Motion.live(&"defeat_stamp"):
		flatline_pop = 1.0
		queue_redraw()
		return
	var e := Motion.entry(&"defeat_stamp")
	flatline_pop = 0.0
	var tw := _tw(&"flatline")
	tw.tween_method(func(v: float) -> void: flatline_pop = v; queue_redraw(), 0.0, 1.0, Motion.seconds(&"defeat_stamp")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void: flatline_pop = 1.0; _end(&"flatline"))


## The DEFEAT stamp's box (local, unrotated, at full size) and its font size.
func flatline_box() -> Dictionary:
	var center := _center()
	var radius := _radius()
	var word := tr("DEFEAT")
	var font := Palette.marker()
	var fs := _fs(FLATLINE_FONT)
	var ww := font.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	while fs > NUMBER_MIN_FONT and ww + fs > radius * 1.8:
		fs -= 1
		ww = font.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	return {"word": word, "fs": fs, "box": Rect2(center + Vector2(-ww * 0.5 - fs * 0.3, -fs * 0.7), Vector2(ww + fs * 0.6, fs * 1.4))}


func _draw_flatlined(center: Vector2, radius: float, inner: float) -> void:
	var p := clampf(flatline_pop, 0.0, 1.0)
	draw_circle(center, radius + 2.0, Color(Palette.NIGHT_SKY, FLATLINE_VEIL * p))
	var fb := flatline_box()
	var fs := int(fb["fs"])
	var box: Rect2 = fb["box"]
	var col := _col(LOSS_COLOR)
	var sc := lerpf(Motion.amplitude(&"defeat_stamp"), 1.0, p) if Motion.live(&"defeat_stamp") else 1.0
	draw_set_transform(center, STAMP_TILT, Vector2.ONE * sc)
	var local := Rect2(box.position - center, box.size)
	draw_rect(local, Color(Palette.NIGHT_SKY, 0.9 * p))
	draw_rect(local, Color(col, p), false, 4.0)
	draw_string(Palette.marker(), Vector2(local.position.x + fs * 0.3, fs * 0.35), String(fb["word"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(col, p))
	draw_set_transform(Vector2.ZERO)
	var sr := minf(fs * SKULL_SHARE, inner * 0.3)
	draw_skull(self, center + Vector2(0.0, fs * 0.9 + sr * 1.2), sr, Color(col, p))


## ANIM-R5 combat 3: true when the forecast has this (living) wheel at 0 after SEND IT.
func lethal_forecast() -> bool:
	return combatant != null and not replaying and combatant.is_alive() and not outcome.is_empty() and not bool(outcome.get("alive_after", true))


## The LETHAL plate's skull: its radius as a share of the plate's lettering.
const LETHAL_SKULL_SHARE := 0.42


## ANIM-R4 C6g: the colour a beaten wheel's DEFEATED stamp and skull wear: its own.
func defeated_color() -> Color:
	return _col(wheel_color)


## ANIM-R4 C6f: true when `status` on a slice is good for that slice's owner (OVERCLOCKED
## boosts it, ENCRYPTED guards it); CORRUPTED and PARASITE are bad for it.
static func status_good_for_owner(status: int) -> bool:
	return status in [RC.Status.OVERCLOCKED, RC.Status.ENCRYPTED]


## ANIM-R4 C6f: true when `status` on a wheel is good for the operative (on its own wheel:
## good for the owner; on an enemy's: bad for the owner).
static func status_good_for_you(status: int, on_player: bool) -> bool:
	return status_good_for_owner(status) == on_player


## The colour a status shows in (ANIM-R4 C6f): green when it is good for the operative, red
## when bad (the glyph says which status; the colour says whose win it is).
static func status_color(status: int, on_player: bool) -> Color:
	return HP_COLOR if status_good_for_you(status, on_player) else LOSS_COLOR


## A skull mark centred at `c`, `r` px in radius, in `col` (ANIM-R3 A6g: the defeated side):
## a round cranium, a jaw with teeth, dark eye holes and a nose.
static func draw_skull(ci: CanvasItem, c: Vector2, r: float, col: Color) -> void:
	ci.draw_circle(c + Vector2(0, -r * 0.15), r, Palette.NIGHT_SKY)
	ci.draw_circle(c + Vector2(0, -r * 0.15), r * 0.86, col)
	ci.draw_rect(Rect2(c + Vector2(-r * 0.5, r * 0.35), Vector2(r, r * 0.55)), col)
	for k in 3:
		ci.draw_line(c + Vector2(-r * 0.25 + k * r * 0.25, r * 0.45), c + Vector2(-r * 0.25 + k * r * 0.25, r * 0.9), Palette.NIGHT_SKY, maxf(1.0, r * 0.1))
	for sx in [-1.0, 1.0]:
		ci.draw_circle(c + Vector2(sx * r * 0.36, -r * 0.1), r * 0.24, Palette.NIGHT_SKY)
	ci.draw_colored_polygon(PackedVector2Array([c + Vector2(0, r * 0.12), c + Vector2(-r * 0.12, r * 0.34), c + Vector2(r * 0.12, r * 0.34)]), Palette.NIGHT_SKY)


## A caption on a paper plate where the tag goes (THIS TURN, an entering enemy's name).
func _draw_caption(text: String, shown: float) -> void:
	var fs := _fs(INTENT_FONT_SIZE)
	var font := Palette.marker()
	var w := minf(size.x * TAG_MAX_SHARE, font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + 16.0)
	var h := INTENT_HEIGHT * _ts()
	var bottom := tag_bottom()
	var r := Rect2(Vector2(clampf(_center().x - w * 0.5, 0.0, maxf(0.0, size.x - w)), maxf(0.0, bottom - h)), Vector2(w, h))
	var a := clampf(shown, 0.0, 1.0)
	draw_rect(Rect2(r.position + Vector2(3, 4), r.size), Color(Palette.SHADOW, Palette.SHADOW.a * a))
	draw_rect(r, Color(Palette.INK, 0.92 * a))
	draw_rect(r, Color(Palette.PAPER, 0.8 * a), false, 1.5)
	draw_string(font, Vector2(r.position.x, r.position.y + h * 0.7), text, HORIZONTAL_ALIGNMENT_CENTER, w, fs, Color(Palette.PAPER, a))


## Miss landing: static flecks over one slice only (hash scatter, a new pattern each frame).
func _draw_static(center: Vector2, r0: float, r1: float, a0: float, a1: float) -> void:
	var frame := Engine.get_process_frames()
	var strength := miss_static * Motion.amplitude(&"precision_miss_static")
	for k in STATIC_FLECKS:
		var h := hash(Vector3i(k, frame, miss_slot))
		var u := float(h & 0xFF) / 255.0
		var v := float((h >> 8) & 0xFF) / 255.0
		var a := lerpf(a0, a1, u)
		var r := lerpf(r0, r1, v)
		var p := center + Vector2(cos(a), sin(a)) * r
		var t := Vector2(-sin(a), cos(a)) * STATIC_FLECK * 0.5
		var col := Palette.PAPER if k % 2 == 0 else Palette.INK
		draw_line(p - t, p + t, Color(col, strength), 2.0)


## Satellite tokens, their HP plates and their aim marks: drawn after the tag and the arrows
## (they are hit-tested first, and at 1.3+ the tag hid a drone and its HP, H23).
func _draw_satellites() -> void:
	for sat in satellites:
		var satp := _satellite_pos(sat) - global_position
		var sat_col := _col(Palette.CELL_ACID if sat.is_player else Palette.RESIST_GOLD)
		# A hex token with the slice its own needle lands on (its wheel, GDD 2.10) and its HP
		# on a plate beside it; the name and the slice words are the tooltip (H22).
		var tok_r := SATELLITE_TOKEN * _ts() * (pulse_scale if sat.id == pulse_satellite else 1.0)
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
		var sat_text := "%d" % int(anim_sat_hp.get(sat.id, sat.hp))
		if not replaying and not sat_out.is_empty() and int(sat_out.get("hp_after", sat.hp)) != sat.hp:
			sat_text += " >%d" % int(sat_out["hp_after"]) if bool(sat_out.get("alive_after", true)) else " >x"
		var lfs := _fs(HUB_FONT_SIZE + 1)
		var plate := satellite_plate_rect(sat, sat_text)
		draw_rect(plate, Color(Palette.NIGHT_SKY, 0.85))
		draw_string(Palette.mono(), plate.position + Vector2(3, lfs), sat_text, HORIZONTAL_ALIGNMENT_LEFT, -1, lfs, sat_col)
		if sat.id == targeted_satellite:
			_draw_crosshair(satp, (SATELLITE_TOKEN + 5.0) * _ts())
		if _zone_is(valid_zones, {"kind": "satellite", "id": sat.id}):
			var hot := _zone_is([hover_zone], {"kind": "satellite", "id": sat.id})
			draw_arc(satp, (SATELLITE_TOKEN + 3.0) * _ts(), 0, TAU, 20, _col(TARGET_COLOR if hot else Color(TARGET_COLOR, 0.55 * zone_pulse)), 3.0 if hot else 1.5)
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


## Where a satellite's HP plate goes (local): outward from the wheel, else to either side,
## else inward, the first that keeps clear of the tag (H23: at 1.3+ the plate sat under it).
func satellite_plate_rect(sat: CombatantState, text: String) -> Rect2:
	var satp := _satellite_pos(sat) - global_position
	var tok_r := SATELLITE_TOKEN * _ts()
	var lfs := _fs(HUB_FONT_SIZE + 1)
	var lw := Palette.mono().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, lfs).x
	var out_dir := (satp - _center()).normalized()
	var avoid: Array[Rect2] = _hp_block_rects()
	var tag := _intent_rect_local()
	if tag.has_area():
		avoid.append(tag)
	# Sideways first under the disc (H24: outward pointed down onto LAST TURN).
	var side := Vector2(signf(out_dir.x) if out_dir.x != 0.0 else 1.0, 0.0)
	var dirs: Array[Vector2] = [out_dir, out_dir.orthogonal(), -out_dir.orthogonal(), -out_dir]
	if out_dir.y > BOTTOM_SECTOR_SIN:
		dirs.push_front(side)
	else:
		dirs.append(side)
	var first := Rect2()
	for dir in dirs:
		var c := satp + dir * (tok_r + maxf(lfs, lw * 0.5 * absf(dir.x)) + 4.0)
		var r := Rect2(c - Vector2(lw * 0.5 + 3.0, lfs * 0.5 + 2.0), Vector2(lw + 6.0, lfs + 5.0))
		if first.size == Vector2.ZERO:
			first = r
		var clear := true
		for a in avoid:
			if r.intersects(a):
				clear = false
				break
		if clear:
			return r
	return first


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
		var hr := arrow_hint_rect(ring, d)
		if hr.has_area():
			# ANIM-R4 C4: the key hint sits where it is clear of the tag (arrow_hint_rect).
			var fs := _fs(HUB_FONT_SIZE + 1)
			draw_string(Palette.mono(), hr.position + Vector2(0.0, Palette.mono().get_ascent(fs)), String(arrow_hints[d]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs, _col(Palette.CELL_ACID))


## ANIM-R4 C4: where the key hint of nudge arrow (`ring`, `d`) is drawn (local rect of its
## words; empty when it has none). Above the arrow on its outer side as before, unless that
## touches the tag (at 1.3 / 1.6 a tag with two chip rows reaches down past the arrows):
## then beside the arrow on its outer side, then under it; the first spot clear of the tag
## and inside the view wins (the first one when none is).
func arrow_hint_rect(ring: int, d: int) -> Rect2:
	if ring != key_ring or not arrow_hints.has(d) or String(arrow_hints[d]) == "":
		return Rect2()
	var fs := _fs(HUB_FONT_SIZE + 1)
	var f := Palette.mono()
	var sz := Vector2(f.get_string_size(String(arrow_hints[d]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x, f.get_height(fs))
	var c := arrow_center(ring, d) - global_position
	var above := Rect2(c + Vector2(-sz.x * 0.5 + d * HINT_SIDE, -HINT_RISE - f.get_ascent(fs)), sz)
	var beside := Rect2(Vector2(c.x + ARROW_HIT + HINT_GAP if d > 0 else c.x - ARROW_HIT - HINT_GAP - sz.x, c.y - sz.y * 0.5), sz)
	var under := Rect2(c + Vector2(-sz.x * 0.5 + d * HINT_SIDE, ARROW_HIT + HINT_GAP), sz)
	var tag := _intent_rect_local().grow(HINT_GAP)
	var room := Rect2(Vector2.ZERO, size)
	for r in [above, beside, under]:
		if not (tag.has_area() and (r as Rect2).intersects(tag)) and room.encloses(r):
			return r
	return above


## ANIM-R4 C4: a key hint's offsets from its arrow (px): sideways (outward), its baseline's
## rise over the arrow's centre, and the gap it keeps from the arrow's circle and the tag.
const HINT_SIDE := 22.0
const HINT_RISE := 10.0
const HINT_GAP := 3.0


## ANIM-R4 C4: the key hints on screen now (global rects), for the layout rules.
func arrow_hint_rects() -> Array[Rect2]:
	var out: Array[Rect2] = []
	for ar in arrows():
		var r := arrow_hint_rect(int(ar["ring"]), int(ar["direction"]))
		if r.has_area():
			out.append(Rect2(global_position + r.position, r.size))
	return out


## A forecast loss segment's HARM fill alpha, and an empty segment's.
const HP_GHOST_ALPHA := 0.35
const HP_EMPTY_ALPHA := 0.1
## The share of its step a segment fills (the rest is the gap between segments).
const HP_SEG_FILL := 0.8


## §3.5: the HP colour for the HP shown now (GAIN, WARN under half, HARM under a quarter).
func hp_color_now() -> Color:
	var c := _shown()
	if c == null:
		return HP_COLOR
	return Palette.hp_color(shown_hp() / maxf(1.0, c.max_hp))


## The HP arc's segments as drawn now: [{a0, a1 (rad), state}], state "full" (HP now and
## after), "ghost" (lost if SEND IT is pressed now: hatched HARM), "heal" (gained), "lag"
## (just lost: the white lag draining) or "empty".
func hp_segments() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var c := _shown()
	if c == null:
		return out
	var mx := maxf(1.0, c.max_hp)
	var hp_now := shown_hp()
	var frac := hp_now / mx
	var after := int(outcome.get("hp_after", c.hp)) if not replaying and is_nan(anim_hp) else roundi(hp_now)
	var frac_after := float(after) / mx
	var frac_lag := (lag_hp / mx) if not is_nan(lag_hp) else frac
	for k in HP_SEGMENTS:
		var a0 := PI * 0.1 + PI * 0.8 * k / HP_SEGMENTS
		var a1 := a0 + PI * 0.8 / HP_SEGMENTS * HP_SEG_FILL
		var f := float(k) / HP_SEGMENTS
		var state := "empty"
		if f < minf(frac, frac_after):
			state = "full"
		elif f < frac:
			state = "ghost"
		elif f < frac_after:
			state = "heal"
		elif f < frac_lag:
			state = "lag"
		out.append({"a0": a0, "a1": a1, "state": state})
	return out


## The heartbeat's clock (s into its period) and whether it beats (§3.5: under a quarter HP,
## T1 `hp_heartbeat`; static under reduce effects).
var heart_t: float = 0.0


func heartbeat_on() -> bool:
	var c := combatant
	if c == null or not c.is_alive() or defeated() or not Motion.live(&"hp_heartbeat"):
		return false
	return shown_hp() / maxf(1.0, c.max_hp) < Palette.HP_HARM_BELOW


## How much the HP arc swells now (px): `hp_heartbeat`'s amplitude at the top of a beat (its
## duration), still for the rest of the period (its delay); 0 when it doesn't beat.
func heartbeat_swell() -> float:
	if not heartbeat_on():
		return 0.0
	var beat := Motion.seconds(&"hp_heartbeat")
	if heart_t >= beat or beat <= 0.0:
		return 0.0
	return Motion.amplitude(&"hp_heartbeat") * sin(PI * heart_t / beat)


## A boss's phase pips on its HP arc (§6.1): one per phase threshold, filled once passed.
func _draw_phase_pips(center: Vector2, r0: float, r1: float) -> void:
	for pip in phase_pips():
		var a: float = pip["a"]
		var at := center + Vector2.from_angle(a) * (r0 + r1) * 0.5
		var s := (r1 - r0) * PIP_SHARE
		var diamond := PackedVector2Array([at + Vector2(0, -s), at + Vector2(s, 0), at + Vector2(0, s), at + Vector2(-s, 0)])
		draw_colored_polygon(diamond, Palette.RESIST_GOLD if bool(pip["passed"]) else Palette.NIGHT_SKY)
		diamond.append(diamond[0])
		draw_polyline(diamond, Palette.RESIST_GOLD, 2.0, true)


## A phase pip's half size as a share of the arc's width.
const PIP_SHARE := 0.75


## A boss's phase pips: [{a (rad on the arc), pct (the threshold), passed}]; empty for any
## other wheel.
func phase_pips() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var c := _shown()
	if c == null or c.is_player or lookup == null or not lookup.has(c.source_id):
		return out
	var data := lookup.get_content(c.source_id) as EnemyData
	if data == null or not data.is_boss:
		return out
	for i in data.phases.size():
		var p := data.phases[i]
		if p == null:
			continue
		out.append({"a": PI * 0.1 + PI * 0.8 * p.hp_threshold_pct, "pct": p.hp_threshold_pct, "passed": c.phase_index > i})
	return out


## HP as a segmented arc under the wheel with the number under it; the preview shows the HP
## the end of the turn leaves: lost segments hatched in HARM, healed ones bright.
func _draw_hp(center: Vector2, radius: float) -> void:
	var hp_col := _col(hp_color_now())
	var beat := heartbeat_swell()
	var r0 := radius + HP_ARC_IN - beat * 0.5
	var r1 := radius + HP_ARC_OUT + beat * 0.5
	for seg in hp_segments():
		var a0: float = seg["a0"]
		var a1: float = seg["a1"]
		var wedge := _wedge(center, r0, r1, a0, a1)
		match String(seg["state"]):
			"full":
				draw_colored_polygon(wedge, hp_col)
			"ghost":
				# §3.5: a forecast loss is a hatched ghost segment in HARM.
				draw_colored_polygon(wedge, _col(Color(LOSS_COLOR, HP_GHOST_ALPHA)))
				for h in HP_HATCH:
					var t := (h + 1.0) / (HP_HATCH + 1.0)
					var aa := lerpf(a0, a1, t)
					draw_line(center + Vector2.from_angle(aa - (a1 - a0) * 0.3) * r0, center + Vector2.from_angle(aa + (a1 - a0) * 0.3) * r1, _col(LOSS_COLOR), 2.0, true)
				var closed := wedge.duplicate()
				closed.append(wedge[0])
				draw_polyline(closed, _col(LOSS_COLOR), 1.0, true)
			"heal":
				draw_colored_polygon(wedge, _col(HP_COLOR.lightened(0.5)))
			"lag":
				# The two-stage drain: the white lag drains after the fill (ANIM-2).
				draw_colored_polygon(wedge, _col(Palette.PAPER))
			_:
				draw_colored_polygon(wedge, Color(Palette.TEXT_HI, HP_EMPTY_ALPHA))
	_draw_phase_pips(center, r0, r1)
	# The number is the HP now (it agrees with the top bar); the forecast after SEND IT is a
	# separate dashed plate with an arrow (H22: "60→49" read as a result).
	var lay := hp_layout()
	var hs := _fs(HP_FONT_SIZE)
	var hp_rect: Rect2 = lay["hp"]
	var after := int(outcome.get("hp_after", combatant.hp)) if not replaying and is_nan(anim_hp) else roundi(shown_hp())
	var hp_at := Vector2(hp_rect.position.x, hp_rect.end.y)
	draw_string_outline(Palette.display(), hp_at, String(lay["hp_text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, hs, HP_OUTLINE, Palette.NIGHT_SKY)
	draw_string(Palette.display(), hp_at, String(lay["hp_text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, hs, hp_col)
	if not replaying and is_nan(anim_hp) and (after != combatant.hp or bool(lay.get("lethal", false))):
		var fs := _fs(HUB_FONT_SIZE + 3)
		var ftext := String(lay["next_text"])
		var fr: Rect2 = lay["next"]
		var fcol := _col(LOSS_COLOR) if after < combatant.hp else _col(HP_COLOR)
		var lethal := bool(lay.get("lethal", false))
		draw_rect(fr, _col(LOSS_COLOR) if lethal else Color(Palette.NIGHT_SKY, 0.8))
		if lethal:
			draw_rect(fr, _col(Palette.PAPER), false, 1.5)
			fcol = _col(Palette.PAPER)
		else:
			_draw_dashed_rect(fr, fcol)
		var ay := fr.position.y + fr.size.y * 0.5
		draw_colored_polygon(PackedVector2Array([Vector2(fr.position.x + 5, ay - 5), Vector2(fr.position.x + 13, ay), Vector2(fr.position.x + 5, ay + 5)]), fcol)
		draw_string(Palette.mono(), Vector2(fr.position.x + 17, fr.position.y + fs), ftext, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, fcol)
		if lethal:
			# The skull sits in the gap before LETHAL.
			var head := tr("NEXT %d") % maxi(0, after)
			var gx := fr.position.x + 17 + Palette.mono().get_string_size(head + "  ", HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			draw_skull(self, Vector2(gx, ay), fs * LETHAL_SKULL_SHARE, fcol)
	if (lay["icons"] as Rect2).has_area():
		_draw_icon_row(lay["icons"], int(lay["icons_fs"]), clampf(last_turn_shown, 0.0, 1.0))
	if (lay["net"] as Rect2).has_area():
		_draw_net_line(lay["net"], int(lay["net_fs"]))
	if last_turn != "":
		# What the last SEND IT did, on a dark plate across the view's width, on up to two
		# lines, never smaller than at text scale 1.0 unless it can't fit (H24: tiny grey text
		# was the only word on the most important moment, and shrank as the text grew).
		var lr: Rect2 = lay["last"]
		var ls := int(lay["last_fs"])
		# ANIM-2: it slides up into place and fades in once a SEND IT has played out.
		var reveal := clampf(last_turn_shown, 0.0, 1.0)
		lr.position.y += (1.0 - last_turn_shown) * Motion.amplitude(&"last_turn_reveal")
		draw_rect(lr, Color(Palette.NIGHT_SKY, 0.8 * reveal))
		var lines: PackedStringArray = lay["last_lines"]
		for i in lines.size():
			draw_string(Palette.mono(), Vector2(lr.position.x, lr.position.y + LAST_TURN_PAD * 0.5 + ls * (i + 1)), lines[i], HORIZONTAL_ALIGNMENT_CENTER, lr.size.x, ls, _col(Color(Palette.PAPER, 0.92 * reveal)))


## Where the HP number, the NEXT plate and the LAST TURN plate go (local rects), with their
## texts: one layout for drawing and for keeping satellite tokens and plates off them.
func hp_layout() -> Dictionary:
	var center := _center()
	var radius := _radius()
	var hs := _fs(HP_FONT_SIZE)
	# Art pass W3 (§6.1): under the arc and under every needle's reach (a multi-needle boss
	# never sweeps a needle over its HP).
	var base_y := center.y + maxf(radius + HP_ARC_OUT, needle_reach()) + HP_NUMBER_GAP + hs * 0.8
	var text := "%d/%d" % [roundi(shown_hp()), combatant.max_hp]
	var tw := Palette.display().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, hs).x
	var out := {"hp_text": text, "hp": Rect2(center.x - tw * 0.5, base_y - hs * 0.8, tw, hs * 0.8), "next": Rect2(), "next_text": "",
		"last": Rect2(), "last_lines": PackedStringArray(), "last_fs": 0, "icons": Rect2(), "icons_fs": 0}
	var row_y := base_y + LAST_TURN_GAP
	var items := icon_row_items()
	if not items.is_empty():
		# ANIM-R3 A6f: the last turn as icons left of the HP number (ANIM-R4 notation: sword 6 − shield 5 = 1),
		# shrinking to fit the room there.
		var ifs := _fs(HUB_FONT_SIZE + 3)
		var room := center.x - tw * 0.5 - ICON_ROW_GAP - left_reserve
		var iw := icon_row_width(items, ifs)
		while ifs > ICON_ROW_MIN_FONT and iw > room:
			ifs -= 1
			iw = icon_row_width(items, ifs)
		out["icons"] = Rect2(Vector2(maxf(left_reserve, center.x - tw * 0.5 - ICON_ROW_GAP - iw), base_y - hs * 0.75), Vector2(iw, ifs + 6.0))
		out["icons_fs"] = ifs
	var after := int(outcome.get("hp_after", combatant.hp))
	out["lethal"] = lethal_forecast()
	if after != combatant.hp or bool(out["lethal"]):
		var fs := _fs(HUB_FONT_SIZE + 3)
		var ftext := tr("NEXT %d") % maxi(0, after)
		if bool(out["lethal"]):
			# ANIM-R5 combat 3: the turn that takes this wheel to 0 says so by its HP (a skull
			# and LETHAL on a solid red plate; the red cross over the hub struck through its
			# name and read as "disabled").
			ftext += "    " + tr("LETHAL")
		var fw := Palette.mono().get_string_size(ftext, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + 22.0
		out["next_text"] = ftext
		var x := center.x + tw * 0.5 + 8.0
		if x + fw <= size.x - 2.0:
			out["next"] = Rect2(Vector2(x, base_y - hs * 0.75), Vector2(fw, fs + 6.0))
		else:
			# Art pass W3: no room beside the (heading) HP number: the plate takes its own row
			# under it, never on the number.
			out["next"] = Rect2(Vector2(clampf(center.x - fw * 0.5, 0.0, maxf(0.0, size.x - fw)), row_y), Vector2(fw, fs + 6.0))
			row_y += fs + 6.0 + LAST_TURN_GAP
	out["net"] = Rect2()
	if not net_tokens().is_empty():
		# §6.2: what the operative receives, once, on its own row under its HP.
		var nfs := _fs(NET_FONT_SIZE)
		var nw := net_width(nfs)
		out["net"] = Rect2(Vector2(clampf(center.x - nw * 0.5, 0.0, maxf(0.0, size.x - nw)), row_y), Vector2(nw, nfs * NET_LINE_SHARE))
		out["net_fs"] = nfs
		row_y += nfs * NET_LINE_SHARE + LAST_TURN_GAP
	out["row_y"] = row_y
	if last_turn != "":
		var box := 2.0 * minf(center.x - left_reserve, size.x - center.x) - LAST_TURN_PAD * 2.0
		var font := Palette.mono()
		# One line, shrinking to the text-scale-1.0 size; then a second line where the view
		# has the room under it; only then smaller (the wheel keeps its size for the rare
		# long line).
		var top_y := row_y
		var ls := _fs(HUB_FONT_SIZE)
		var room_lines := clampi(floori((size.y - top_y - LAST_TURN_PAD) / maxf(1.0, HUB_FONT_SIZE)), 1, LAST_TURN_LINES)
		var lines := _wrap_last_turn(last_turn, box, ls)
		while lines.size() > 1 and ls > HUB_FONT_SIZE:
			ls -= 1
			lines = _wrap_last_turn(last_turn, box, ls)
		var fits := func(n: int, f: int) -> bool: return n * f + LAST_TURN_PAD <= size.y - top_y
		while (lines.size() > room_lines or not fits.call(lines.size(), ls)) and ls > 7:
			ls -= 1
			lines = _wrap_last_turn(last_turn, box, ls)
		var lw := 0.0
		for l in lines:
			lw = maxf(lw, minf(box, font.get_string_size(l, HORIZONTAL_ALIGNMENT_LEFT, -1, ls).x))
		var top := row_y
		out["last"] = Rect2(center.x - lw * 0.5 - LAST_TURN_PAD, top, lw + LAST_TURN_PAD * 2.0, ls * lines.size() + LAST_TURN_PAD)
		out["last_lines"] = lines
		out["last_fs"] = ls
	return out


## ANIM-R3 A6f: what the last SEND IT did to this wheel as numbers (the scene's
## CombatScene.last_turn_icons): {hit (the hits' raw total), soaked (what block and shield
## took), evaded (what was evaded), hp (the HP change in the resolve)}; empty = none. It
## stays with LAST TURN until the player acts.
var last_turn_icons: Dictionary = {}
## Tooltip words for the LAST TURN plate and the icon row (the scene's: each status named
## in it explained).
var last_turn_tip: String = ""
## Room between the icon row and the HP number, and the row's smallest lettering (px).
const ICON_ROW_GAP := 8.0
const ICON_ROW_MIN_FONT := 8


## The icon row's items: [{icon (a slice type, -1 = none), text, color, sep (a joining sign
## before it)}]; empty when the turn did nothing to it. ANIM-R4 C6c: the one notation for a
## hit meeting a guard (CombatFxLayer.draw_equation, as where a hit struck): sword and the
## hits aimed at it, minus the shield and what its guard took (minus the evade mark and what
## it evaded), = what got through; an HP change the hits don't explain (a heal, corruption)
## follows after a dot. No arrow ("11 -> 11 = 0" read as a formula to decode).
func icon_row_items() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var d := last_turn_icons
	if d.is_empty() or last_turn == "":
		return out
	var hit := int(d.get("hit", 0))
	var soaked := int(d.get("soaked", 0))
	var evaded := int(d.get("evaded", 0))
	var hp := int(d.get("hp", 0))
	if hit <= 0 and hp == 0:
		return out
	var through := maxi(0, hit - soaked - evaded)
	if hit > 0:
		out.append({"icon": RC.SliceType.ATTACK, "text": str(hit), "color": LOSS_COLOR, "sep": ""})
		if soaked > 0:
			out.append({"icon": RC.SliceType.DEFEND, "text": str(soaked), "color": Palette.NET_CYAN, "sep": CombatFxLayer.EQ_MINUS})
		if evaded > 0:
			out.append({"icon": RC.SliceType.EVADE, "text": str(evaded), "color": Palette.NET_CYAN, "sep": CombatFxLayer.EQ_MINUS})
		out.append({"icon": -1, "text": str(through), "color": LOSS_COLOR if through > 0 else Palette.NET_CYAN, "sep": "="})
	# The rest of the HP change (a heal, corruption): what the hits took off is `dealt`.
	var rest := hp + int(d.get("dealt", 0))
	if hit <= 0 or rest != 0:
		var hp_text := ("+%d" % rest) if rest > 0 else ("-%d" % absi(rest))
		out.append({"icon": RC.SliceType.HEAL if rest > 0 else -1, "text": hp_text if hit <= 0 else hp_text + " " + tr("HP"),
			"color": HP_COLOR if rest > 0 else LOSS_COLOR, "sep": "·" if hit > 0 else ""})
	return out



static func icon_row_width(items: Array[Dictionary], fs: int) -> float:
	return CombatFxLayer.equation_width(items, fs, Palette.mono())


func _draw_icon_row(r: Rect2, fs: int, alpha: float) -> void:
	var items := icon_row_items()
	draw_rect(r.grow_individual(3.0, 0.0, 3.0, 0.0), Color(Palette.NIGHT_SKY, 0.8 * alpha))
	var shown: Array = []
	for it in items:
		var c := (it as Dictionary).duplicate()
		c["color"] = _col(Color(it["color"]))
		shown.append(c)
	CombatFxLayer.draw_equation(self, Vector2(r.position.x, r.position.y + r.size.y * 0.5), shown, fs, Palette.mono(), alpha)


## LAST TURN wrapped at its " · " breaks to `width` px at font size `fs`.
static func _wrap_last_turn(text: String, width: float, fs: int) -> PackedStringArray:
	var font := Palette.mono()
	var parts := text.split(" · ")
	var lines := PackedStringArray()
	var line := ""
	for p in parts:
		var trial := p if line == "" else line + " · " + p
		if line != "" and font.get_string_size(trial, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > width:
			lines.append(line)
			line = p
		else:
			line = trial
	if line != "":
		lines.append(line)
	return lines


## The rects under the disc that satellite tokens and plates keep off (local).
func _hp_block_rects() -> Array[Rect2]:
	var lay := hp_layout()
	var out: Array[Rect2] = [lay["hp"]]
	for k in ["next", "last", "icons"]:
		if (lay[k] as Rect2).has_area():
			out.append(lay[k])
	return out


func _draw_dashed_rect(r: Rect2, col: Color) -> void:
	var pts := [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y), r.position]
	for k in 4:
		var a: Vector2 = pts[k]
		var b: Vector2 = pts[k + 1]
		var n := maxi(2, int(a.distance_to(b) / 6.0))
		for i in n:
			if i % 2 == 0:
				draw_line(a.lerp(b, float(i) / n), a.lerp(b, float(i + 1) / n), col, 1.5)


## The hub name's font size and lines for a hub `width` px wide: one line shrinking to
## its text-scale-1.0 size, then two lines split at the middle space, then smaller (H24:
## "BILLING DAEMON" drew at 10 px at 1.6 and 13 px at 1.0). [size, line, line?]
func hub_name_lines(width: float) -> Array:
	var name := shown_name().to_upper()
	var font := Palette.marker()
	var fs := _fs(NAME_FONT_SIZE)
	while fs > NAME_FONT_SIZE and font.get_string_size(name, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > width:
		fs -= 1
	if font.get_string_size(name, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x <= width:
		return [fs, name]
	var words := name.split(" ")
	if words.size() > 1:
		var best := 1
		var best_w := INF
		for cut in range(1, words.size()):
			var a := " ".join(words.slice(0, cut))
			var b := " ".join(words.slice(cut))
			var w := maxf(font.get_string_size(a, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x, font.get_string_size(b, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
			if w < best_w:
				best_w = w
				best = cut
		var l1 := " ".join(words.slice(0, best))
		var l2 := " ".join(words.slice(best))
		while fs > 7 and maxf(font.get_string_size(l1, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x, font.get_string_size(l2, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x) > width:
			fs -= 1
		return [fs, l1, l2]
	while fs > 7 and font.get_string_size(name, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > width:
		fs -= 1
	return [fs, name]


## The combatant's name in the player's language (generated Mirrors keep runtime names).
func shown_name() -> String:
	return name_of(combatant)


## `c`'s name in the player's language (a satellite's too; ANIM-R5 combat 9).
func name_of(c: CombatantState) -> String:
	var data: Resource = null
	if lookup != null and c.source_id != &"" and lookup.has(c.source_id):
		data = lookup.get_content(c.source_id)
	if data == null or not ("display_name" in data) or String(data.display_name) != c.display_name:
		return c.display_name
	return TextDb.t(data, "display_name")


## The hub's lines under the name for `c` (block, shield, resistance, frozen, its hub
## core, extra lines), and which one is the resistance line (-1 for none).
func _hub_lines(c: CombatantState) -> Array[String]:
	# Drawn words go through tr() (H23: drawn text never translated; the scrambled
	# storyboard still showed them in English).
	var hub_lines: Array[String] = []
	if c == null:
		return hub_lines
	if c.block > 0:
		hub_lines.append(tr("BLOCK %d") % c.block)
	if c.shield > 0:
		hub_lines.append(tr("SHIELD %d") % c.shield)
	if c.resistance > 0 or c.hub_resistance > 0 or c.wheel.passive_resistance > 0:
		hub_lines.append(tr("RESIST %d") % c.resistance)
	if c.wheel.frozen:
		hub_lines.append(tr("FROZEN"))
	if c.wheel.hub_id != &"":
		var hub_data := lookup.get_content(c.wheel.hub_id) if lookup != null else null
		var hub_name: String = TextDb.t(hub_data, "display_name") if hub_data != null and "display_name" in hub_data else String(c.wheel.hub_id)
		hub_lines.append(hub_name + (tr(" (BREACHED)") if c.is_hub_breached() else ""))
	hub_lines.append_array(extra_lines)
	return hub_lines


## Art pass W3 (§6.1): the hub's words and inset (1 shown .. 0 cleared) while a stamp holds
## there (`clear_hub`).
var hub_alpha: float = 1.0


## Clears the hub for a stamp that starts in `delay` s and shows for `seconds`: its words and
## inset fade out (`hub_clear`), and come back once it is done. Nothing when motion doesn't
## play (the end state is a hub with its words).
func clear_hub(delay: float, seconds: float) -> void:
	if not Motion.live(&"hub_clear"):
		hub_alpha = 1.0
		return
	var fade := Motion.seconds(&"hub_clear")
	var tw := _tw(&"hub_clear")
	tw.tween_interval(maxf(0.0, delay))
	tw.tween_method(_set_hub_alpha, hub_alpha, 0.0, fade)
	tw.tween_interval(maxf(0.0, seconds - fade * 2.0))
	tw.tween_method(_set_hub_alpha, 0.0, 1.0, fade)
	tw.tween_callback(func() -> void: hub_alpha = 1.0; _end(&"hub_clear"))


func _set_hub_alpha(v: float) -> void:
	hub_alpha = v
	queue_redraw()


func _hub_fade(c: Color) -> Color:
	return Color(c, c.a * hub_alpha)


func _draw_hub(center: Vector2, _inner: float, line: Color) -> void:
	var lay := hub_layout()
	var hub_lines: Array[String] = lay["lines"]
	var resist_line := -1
	if combatant.resistance > 0 or combatant.hub_resistance > 0 or combatant.wheel.passive_resistance > 0:
		resist_line = (1 if combatant.block > 0 else 0) + (1 if combatant.shield > 0 else 0)
	var hw: float = lay["width"]
	var fs := int(lay["fs"])
	var step: float = lay["step"]
	var top: float = lay["top"]
	var name_lines: Array = lay["name"]
	var name_size := int(lay["name_size"])
	var name_count := int(lay["name_count"])
	if hub_alpha <= 0.0:
		return  # §6.1: the hub is cleared for its stamp
	if float(lay["inset_alpha"]) > 0.0:
		# Art pass W3 (§6.1): the operative's Polaroid mini-portrait at the hub's top.
		WheelBezel.draw_inset(self, inset_rect(), shown_subject(), portrait_texture, float(lay["inset_alpha"]) * hub_alpha)
		WheelBezel.draw_glyph_badge(self, inset_rect(), look, float(lay["inset_alpha"]) * hub_alpha)
	for k in name_count:
		# The last line sits where a one-line name does; a first line goes above it.
		var ny := top - (name_count - 1 - k) * (name_size + 1)
		draw_string(Palette.marker(), center + Vector2(-hw * 0.5, ny), String(name_lines[k + 1]), HORIZONTAL_ALIGNMENT_CENTER, hw, name_size, _hub_fade(_col(line.lightened(0.2))))
	for i in hub_lines.size():
		var col := _col(Palette.RESIST_GOLD) if i == resist_line else _col(Palette.PAPER)
		var lfs := fs
		while lfs > 6 and Palette.mono().get_string_size(hub_lines[i], HORIZONTAL_ALIGNMENT_LEFT, -1, lfs).x > hw:
			lfs -= 1  # shrink to the hub (H23: "Breaker Core" was cut to "Breake")
		var line_text: String = hub_lines[i]
		while line_text.length() > 3 and Palette.mono().get_string_size(line_text, HORIZONTAL_ALIGNMENT_LEFT, -1, lfs).x > hw:
			line_text = line_text.substr(0, line_text.length() - 2) + "…"
		draw_string(Palette.mono(), center + Vector2(-hw * 0.5, top + 16 + i * step), line_text, HORIZONTAL_ALIGNMENT_CENTER, hw, lfs, _hub_fade(col))


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

## Chip rows of the tag (wrapped to the view width), at chip_font().
func _chip_rows() -> Array:
	return _chip_rows_at(chip_font())


## The chips' font size (ANIM-R2 E7): the text size's, but at big text (one chip row kept)
## the chips shrink, down to their size at BIG_TEXT, before any folds into "+N MORE" (at
## 1.6 "+3 MORE" hid the forecast's own results).
func chip_font() -> int:
	var fs := _fs(CHIP_FONT_SIZE)
	if _ts() <= BIG_TEXT:
		return fs
	var floor_fs := roundi(CHIP_FONT_SIZE * BIG_TEXT)
	while fs > floor_fs and _folds(_chip_rows_at(fs)):
		fs -= 1
	return fs


static func _folds(rows: Array) -> bool:
	if rows.is_empty():
		return false
	var last: Array = rows[rows.size() - 1]
	return not last.is_empty() and bool((last[last.size() - 1] as Dictionary).get("more", false))


func _chip_rows_at(fs: int) -> Array:
	var rows: Array = []
	var chips: Array = tag_intent().get("chips", [])
	if chips.is_empty():
		return rows
	var max_w := size.x * TAG_MAX_SHARE
	var cap := _chip_row_cap()
	# ANIM-R1 C8: the chips come in order of importance (the scene sorts them: damage to
	# you, damage dealt, HP, then the rest), and the fold keeps that order: the rows fill in
	# order, and once a chip no longer fits the kept rows, it and every chip after it fold
	# into "+N MORE" (room for which is kept on the last row). The first chip always shows.
	var row: Array = []
	var w := 0.0
	for i in chips.size():
		var chip: Dictionary = chips[i]
		var cw := _chip_w(String(chip["text"]), fs)
		if not row.is_empty() and w + cw > max_w:
			rows.append(row)
			row = []
			w = 0.0
		if rows.size() >= cap:
			return _fold_rows(rows, chips.size() - i, fs, max_w)
		var more := 0.0
		if rows.size() == cap - 1 and i < chips.size() - 1:
			more = _chip_w(tr("+%d MORE") % (chips.size() - i - 1), fs)
		if rows.size() == cap - 1 and not row.is_empty() and w + cw + more > max_w and i < chips.size() - 1:
			# This chip would leave no room to say what else there is.
			rows.append(row)
			return _fold_rows(rows, chips.size() - i, fs, max_w)
		row.append(chip)
		w += cw
	if not row.is_empty():
		rows.append(row)
	return rows


## Adds the "+N MORE" chip to the last of `rows` (H23: a bare "+4" was a mystery); every
## folded chip is listed in the tag's tooltip.
func _fold_rows(rows: Array, hidden: int, fs: int, max_w: float) -> Array:
	var cap := _chip_row_cap()
	rows = rows.slice(0, cap)
	var last: Array = rows[rows.size() - 1]
	var w := 0.0
	for c in last:
		w += _chip_w(String(c["text"]), fs)
	while last.size() > 1 and w + _chip_w(tr("+%d MORE") % hidden, fs) > max_w:
		var gone: Dictionary = last.pop_back()
		w -= _chip_w(String(gone["text"]), fs)
		hidden += 1
	last.append({"text": tr("+%d MORE") % hidden, "color": Palette.INK, "ink": Palette.PAPER, "more": true})
	return rows


static func _chip_width(text: String, fs: int) -> float:
	return Palette.mono().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + 12.0


## ANIM-R5 combat 4: a chip's width on this tag: a held forecast (its lines get ticks) keeps
## room at each chip's end for its tick, so a tick never sits on the chip's words ("YOU
## TAKE 3 H✓", DOWN hidden).
func _chip_w(text: String, fs: int) -> float:
	return _chip_width(text, fs) + (tick_room() if _ticking() else 0.0)


## True while the tag drawn is a held forecast whose lines tick.
func _ticking() -> bool:
	return replaying and not replay_tag.is_empty()


## The room a tick takes at a chip's end (px).
func tick_room() -> float:
	return CHIP_HEIGHT * _ts() * TICK_SHARE * 2.0 + TICK_GAP * 2.0


## The tag's chips as drawn in tag rect `r` (local): [{chip, rect (the chip), text (its
## words), tick (its tick's disc bounds; empty when it has no room for one)}].
func chip_layout(r: Rect2) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var ts := _ts()
	var fs := chip_font()
	var chip_h := CHIP_HEIGHT * ts
	var y := r.position.y + INTENT_HEIGHT * ts
	var font := Palette.mono()
	var room := tick_room() if _ticking() else 0.0
	for row in _chip_rows_at(fs):
		var x := r.position.x + 4
		for chip in row:
			var cw := _chip_w(String(chip["text"]), fs)
			var cr := Rect2(Vector2(x, y), Vector2(cw - 4, chip_h))
			var tw := font.get_string_size(String(chip["text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			var text := Rect2(Vector2(cr.position.x + 4, cr.position.y + chip_h * 0.75 - font.get_ascent(fs)), Vector2(tw, font.get_height(fs)))
			var tick := Rect2()
			if room > 0.0:
				var rr := chip_h * TICK_SHARE
				var c := Vector2(cr.end.x - TICK_GAP - rr, cr.position.y + chip_h * 0.5)
				tick = Rect2(c - Vector2(rr + 1.5, rr + 1.5), Vector2(rr + 1.5, rr + 1.5) * 2.0)
			out.append({"chip": chip, "rect": cr, "text": text, "tick": tick})
			x += cw
		y += chip_h + 2.0
	return out


## The intent tag's rect in view space (empty without an intent): a title row and one row
## per line of result chips, grown upwards from just above the pointer hub.
func _intent_rect_local() -> Rect2:
	return _tag_geometry()["rect"]


## The tag's rect (local) and its WAS row (ANIM-R5 combat 7; empty when none or no room).
func _tag_geometry() -> Dictionary:
	var it := tag_intent()
	if combatant == null or it.is_empty() or String(it.get("text", "")) == "":
		return {"rect": Rect2(), "was": Rect2()}
	var ts := _ts()
	var title_h := INTENT_HEIGHT * ts
	var chip_h := CHIP_HEIGHT * ts
	var fs := chip_font()
	var rows := _chip_rows_at(fs)
	var h := title_h + rows.size() * (chip_h + 2.0)
	var w := Palette.marker().get_string_size(String(it["text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, _fs(INTENT_FONT_SIZE)).x + (20.0 + 22.0 * ts if int(it.get("type", -1)) >= 0 else 16.0)
	if TIER_PIPS.has(int(it.get("tier", -1))):
		w += PIP_RADIUS * 2.6 * ts * 3 + 4 * ts
	for row in rows:
		var rw := 8.0
		for chip in row:
			rw += _chip_w(String(chip["text"]), fs)
		w = maxf(w, rw)
	# ANIM-R3 A6j: the tape's words never run past the tag (IF YOU SEND IT spilled over a
	# short tag's title).
	w = maxf(w, tape_width())
	w = minf(w, size.x * TAG_MAX_SHARE)
	var bottom := tag_bottom()
	var x := clampf(_center().x - w * 0.5, 0.0, maxf(0.0, size.x - w))
	var top_min := tape_height() - TAPE_INSET * ts
	# The tape stands above the tag (off its title): the tag keeps room for it in the view.
	var rect := Rect2(Vector2(x, maxf(top_min, bottom - h)), Vector2(w, h))
	# ANIM-R5 combat 7: a preview that changed this tag says what it said before on its tape
	# (WAS, struck through), where IF YOU SEND IT stood: the tag keeps its size, so it fits
	# at every text size (a row of its own had no room under the screen's top).
	var was := Rect2()
	if was_text() != "":
		var th := tape_height()
		was = Rect2(Vector2(rect.position.x, rect.position.y - th + TAPE_INSET * ts), Vector2(w, th))
	return {"rect": rect, "was": was}


## ANIM-R5 combat 7: the tag before the play or nudge being previewed (the scene sets it
## when a hover changes this tag; {} = unchanged). The tag shows it struck through under a
## WAS row, so a flip reads as a change ("CRITICAL · HITS YOU 14" was "ATTACK · HITS YOU 6").
var was_tag: Dictionary = {}
## What the tag said before the preview, as one line ("" = nothing to show).
func was_text() -> String:
	if replaying or was_tag.is_empty() or String(was_tag.get("text", "")) == "":
		return ""
	var parts := PackedStringArray([String(was_tag["text"])])
	for chip in was_tag.get("chips", []):
		if not bool((chip as Dictionary).get("play", false)):
			parts.append(String(chip["text"]))
	return " · ".join(parts)


## The WAS tape's rect (global), empty when it doesn't show.
func was_rect() -> Rect2:
	var r: Rect2 = _tag_geometry()["was"]
	return Rect2(global_position + r.position, r.size) if r.has_area() else r


func _draw_was(r: Rect2, alpha: float) -> void:
	var fs := _fs(HUB_FONT_SIZE)
	var font := Palette.mono()
	var head := tr("WAS") + " "
	var hw := font.get_string_size(head, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var x := r.position.x + TAPE_PAD
	var base := r.position.y + fs
	draw_rect(r, Color(Palette.NOTE_TAPE, alpha))
	draw_string(font, Vector2(x, base), head, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(Palette.INK, alpha))
	var room := r.end.x - x - hw - TAPE_PAD
	var line := was_text()
	while line.length() > 3 and font.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > room:
		line = line.substr(0, line.length() - 2) + "…"
	var lw := font.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var ink := Color(Palette.INK, WAS_INK * alpha)
	draw_string(font, Vector2(x + hw, base), line, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, ink)
	var sy := base - fs * 0.32
	draw_line(Vector2(x + hw, sy), Vector2(x + hw + lw, sy), ink, 1.5)


## The WAS row's words' strength (alpha): a ghost of the tag before.
const WAS_INK := 0.6


## The tape on a tag (ANIM-R3 A6j): its height, and its width for the widest words it
## carries (IF YOU SEND IT, THIS TURN) plus padding; it overlaps the tag by TAPE_INSET px.
static func tape_height() -> float:
	return _fs(HUB_FONT_SIZE) + 3.0


static func tape_width() -> float:
	var fs := _fs(HUB_FONT_SIZE)
	var w := 0.0
	for t in [forecast_caption(), TranslationServer.translate("THIS TURN")]:
		w = maxf(w, Palette.mono().get_string_size(String(t), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
	return w + TAPE_PAD * 2.0


const TAPE_INSET := 3.0
const TAPE_PAD := 6.0


## The intent tag on screen (layout checks: it never covers a wheel), or an empty rect.
func intent_rect() -> Rect2:
	var r := _intent_rect_local()
	return Rect2(global_position + r.position, r.size) if r.has_area() else r


func _intent_tag(r: Rect2, alpha: float = 1.0) -> void:
	var it := tag_intent()
	var type := int(it.get("type", -1))
	var text := String(it["text"])
	var ts := _ts()
	var f := Palette.marker()
	var w := r.size.x
	var fade := func(c: Color) -> Color: return Color(c, c.a * alpha)
	draw_rect(Rect2(r.position + Vector2(3, 4), r.size), fade.call(Palette.SHADOW))
	draw_rect(r, fade.call(Palette.NOTE_PAPER))
	draw_rect(r, fade.call(Color(Palette.INK, 0.5)), false, 1.0)
	# ANIM-R1 / R2 E4d: the tape says what the tag is, a forecast of what SEND IT does now
	# ("IF YOU SEND IT"; "NEXT TURN" read as "not this turn" before the first SEND IT), so
	# it never reads as the result of the turn just played. ANIM-R3 A6b: once a replay's
	# result holds, the same tag's tape reads THIS TURN (its lines ticked). A6j: the tape
	# stands above the tag, off the title, and the tag is never narrower than its words.
	var cap_fs := _fs(HUB_FONT_SIZE)
	var cap_text := caption if replaying and caption != "" and not replay_tag.is_empty() else forecast_caption()
	var cap_w := minf(w, Palette.mono().get_string_size(cap_text, HORIZONTAL_ALIGNMENT_LEFT, -1, cap_fs).x + TAPE_PAD * 2.0)
	var th := tape_height()
	var tape := Rect2(r.position + Vector2((w - cap_w) * 0.5, -th + TAPE_INSET * ts), Vector2(cap_w, th))
	var was_tape: Rect2 = _tag_geometry()["was"]
	if was_tape.has_area() and not replaying:
		_draw_was(was_tape, alpha)
	else:
		draw_rect(tape, fade.call(Palette.NOTE_TAPE))
		draw_string(Palette.mono(), Vector2(tape.position.x, tape.position.y + cap_fs), cap_text, HORIZONTAL_ALIGNMENT_CENTER, cap_w, cap_fs, fade.call(Palette.INK))
	var tx := r.position.x + 8
	var title_h := INTENT_HEIGHT * ts
	if type >= 0:
		SliceIcon.draw_icon(self, r.position + Vector2(17, title_h * 0.5 + TAPE_INSET * ts * 0.5), 9 * ts, type, fade.call(Palette.slice_color(type)))
		tx += 22 * ts
	var tier := int(it.get("tier", -1))
	if TIER_PIPS.has(tier):
		# Aim quality as pips (readable without words): filled = how well the needle sits.
		for k in 3:
			var pc := Vector2(tx + PIP_RADIUS * ts + k * (PIP_RADIUS * 2.6 * ts), r.position.y + title_h * 0.5 + TAPE_INSET * ts * 0.5)
			if k < int(TIER_PIPS[tier]):
				draw_circle(pc, PIP_RADIUS * ts, fade.call(Palette.INK))
			else:
				draw_arc(pc, PIP_RADIUS * ts, 0, TAU, 10, fade.call(Palette.INK), 1.2)
		tx += PIP_RADIUS * 2.6 * ts * 3 + 4 * ts
	draw_string(f, Vector2(tx, r.position.y + title_h * 0.7 + TAPE_INSET * ts * 0.5), text, HORIZONTAL_ALIGNMENT_LEFT, r.end.x - tx - 4, _fs(INTENT_FONT_SIZE), fade.call(Palette.INK))
	var fs := chip_font()
	var chip_h := CHIP_HEIGHT * ts
	var boxes := chip_layout(r)
	var shown := {}
	for bx in boxes:
		if (bx["chip"] as Dictionary).has("tick_i"):
			shown[int(bx["chip"]["tick_i"])] = true
	for bx in boxes:
		var chip: Dictionary = bx["chip"]
		var cr: Rect2 = bx["rect"]
		draw_rect(cr, fade.call(Color(chip.get("color", Palette.INK))))
		draw_string(Palette.mono(), Vector2(cr.position.x + 4, cr.position.y + chip_h * 0.75), String(chip["text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs, fade.call(Color(chip.get("ink", Palette.PAPER))))
		var tick := _chip_tick(chip, shown)
		if tick >= 0.0 and (bx["tick"] as Rect2).has_area():
			_draw_tick((bx["tick"] as Rect2).get_center(), chip_h, tick, alpha)


## A held forecast chip's tick (ANIM-R3 A6b): its pop 0..1, or -1 when not ticked. The fold
## chip ("+N MORE") ticks once every chip it hides has.
func _chip_tick(chip: Dictionary, shown: Dictionary) -> float:
	if replay_tag.is_empty() or not replaying:
		return -1.0
	if chip.has("tick_i"):
		return float(tag_ticks.get(int(chip["tick_i"]), -1.0))
	if bool(chip.get("more", false)):
		var least := 1.0
		for c in replay_tag.get("chips", []):
			var i := int((c as Dictionary).get("tick_i", -1))
			if i < 0 or shown.has(i):
				continue
			if not tag_ticks.has(i):
				return -1.0
			least = minf(least, float(tag_ticks[i]))
		return least
	return -1.0


## A tick centred on `c` (local; ANIM-R5 combat 4: in the room kept at its chip's end): an
## acid disc with a check, popping in from `forecast_tick`'s amplitude scale.
func _draw_tick(c: Vector2, chip_h: float, pop: float, alpha: float) -> void:
	var sc := lerpf(Motion.amplitude(&"forecast_tick"), 1.0, clampf(pop, 0.0, 1.0)) if Motion.live(&"forecast_tick") else 1.0
	var rr := chip_h * TICK_SHARE * sc
	draw_circle(c, rr + 1.5, Color(Palette.INK, alpha))
	draw_circle(c, rr, Color(Palette.CELL_ACID, alpha))
	draw_polyline(PackedVector2Array([c + Vector2(-rr * 0.5, 0.0), c + Vector2(-rr * 0.12, rr * 0.4), c + Vector2(rr * 0.55, -rr * 0.45)]),
		Color(Palette.INK, alpha), maxf(1.5, rr * 0.3), true)


## A tick's radius as a share of a chip's height.
const TICK_SHARE := 0.32  # drawing, not motion (ANIM-R4 C5): the tick disc's radius as a share of the chip height
## The gap either side of a tick in its chip's end room (px).
const TICK_GAP := 2.0


## The forecast tag's tape caption (translated).
static func forecast_caption() -> String:
	return TranslationServer.translate("IF YOU SEND IT")


func _draw_dashed_arc(center: Vector2, radius: float, start: float, end: float, color: Color, width: float) -> void:
	var span := end - start
	var dashes := maxi(3, int(absf(span) / 0.12))
	for i in dashes:
		if i % 2 == 1:
			continue
		var a := start + span * i / dashes
		var b := start + span * (i + 1) / dashes
		draw_arc(center, radius, a, b, 4, color, width)
