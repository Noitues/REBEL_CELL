extends Control
## Combat scene (M4 look, H20 play): wireframe arena, the spinners in the middle where
## nothing zine ever covers them, the Polaroid, Heat, Daemons, subtitles and the tutorial
## in the right column, the hand and SEND IT along the bottom (STYLE_GUIDE 1, 4-5, GDD 9.2).
## H20: cards are dragged onto what they aim at (a wheel, a nudge arrow, a slice, a
## satellite) or picked and then aimed; every wheel has curved nudge arrows; the tag over
## each spinner and the HP arcs, RAM bar and chips show the full outcome of the turn (and
## of the card or nudge being aimed) instead of text logs; refusals pop a short toast.
## Keyboard: 1-9 pick cards, arrows/Tab choose the target, Enter confirms, Esc cancels;
## Q/E nudge (W which wheel, R which ring), X respin, Tab target, Space end turn,
## Z rewind, right-click inspect, Esc settings. Pad: A picks and confirms, D-pad aims, B
## cancels. Random effects show odds, never the exact roll (GDD 2.10). Signal Up, Call
## Down: the views emit what the player points at; only this scene calls the engine.

const ENEMY_CHOICES: Array[StringName] = [&"collections_agent", &"compliance_officer", &"dosage_dispenser"]
const CLASS_ID := &"breaker"
const RING_ID := &"rank:1"
## Seconds between resolution passes in the log playback (0 under headless / reduce-effects).
const PASS_DELAY := 0.35
## Canvas layer of the pause menu: above the combat scene and the netrun around it.
const MENU_LAYER := 10
## Right column width at text scale 1.0 (Polaroid, Heat, Daemons, subtitles, tutorial).
const RIGHT_WIDTH := 300.0
## Subtitle dock in the right column: lines per page, one line's height and the speaker
## line plus margins at text scale 1.0 (px).
const SUBTITLE_LINES := 3
const SUBTITLE_LINE_PX := 22.0
const SUBTITLE_CHROME_PX := 52.0
## Gap between the dock and the tutorial (px); the tutorial needs this height.
const NOTE_GAP := 6.0
const TUTORIAL_MIN_HEIGHT := 140.0
## Where the tutorial sits before the layout is known.
const TUTORIAL_RECT := Rect2(980, 287, 300, 250)
## Sticker gap and the edge they keep (px).
const STICKER_GAP := 6.0
const STICKER_EDGE := 4.0
## Chip colours on the tags (the text says what they are; colour is a second cue).
const CHIP_HIT := Palette.CELL_PINK
const CHIP_LOSS := Color("#FF4D4D")
const CHIP_GAIN := Color("#3DFF8B")
const CHIP_GUARD := Palette.NET_CYAN
const CHIP_STATUS := Palette.CELL_ACID
const CHIP_RESIST := Palette.RESIST_GOLD
const CHIP_RUN := Palette.NOTE_YELLOW
## Smallest hand card scale when many cards must fit the row.
const MIN_CARD_SCALE := 0.6

@export var auto_start: bool = true

@onready var engine: CombatEngine = $CombatEngine

var background: WireframeBackground
var portrait: Polaroid
var heat_poster: HeatPoster
var ram_note: RamBar
var daemon_row: DaemonRow
var inspect_popup: InspectPopup
var toast: Toast
## Hidden text records (the tests read them; players see chips and tags).
var preview_note: ZineNote
var log_note: ZineNote
var _status: Label
var _seed_spin: SpinBox
var _player_view: WheelView
var _enemy_views_box: VBoxContainer
var _enemy_views: Dictionary = {}
## Hidden option buttons: the keyboard toggles (W which wheel Q/E nudge, R which ring) and
## the defaults play_card() uses; players aim cards by dragging instead.
var _target_option: OptionButton
var _nudge_wheel_option: OptionButton
var _nudge_ring_option: OptionButton
var _card_target_option: OptionButton
var _direction_option: OptionButton
var _slot_option: OptionButton
var _respin_button: Button
## Stickers beside SEND IT: RESPIN and UNDO.
var _stickers: Dictionary = {}
var _sticker_box: VBoxContainer
var _hand_box: HBoxContainer
var _end_turn_button: Button
var _rewind_button: Button
var _picker_controls: Array[Control] = []
var controls_row: HFlowContainer
var _settings_panel: PauseMenu = null
var _settings_button: Button
var _nudge_minus_button: Button
var _nudge_plus_button: Button
var _menu_layer: CanvasLayer = null
var _arena: Control
var _right: VBoxContainer
## The free part of the right column: subtitles on top, the tutorial under them.
var _notes_area: Control
var _zine_elements: Array[Control] = []
var _last_events: Array[Dictionary] = []
var _log_generation: int = 0
var tutorial: TutorialOverlay = null
var _rewound: bool = false
var _migrate_tween: Tween = null
## Text of the last inspect (tests read it).
var last_inspect: String = ""
## Card being aimed (hand index), -1 when none; its legal plays and the one pointed at.
var selecting: int = -1
var _options: Array[CombatAction] = []
var _option_index: int = -1
var _dragging: bool = false
## Draws the aim line (see _draw_aim_line).
var _aim_line: Control
## The aiming instruction over the hand.
var _aim_hint: Label
const AIM_HINT_FONT := 14
## Other cards fade while one is aimed.
const AIM_DIM := 0.45
const AIM_LINE_WIDTH := 3.0
## Pad triggers held down (axis -> bool): a squeeze toggles once.
var _trigger_down: Dictionary = {}
## Scale the hand's cards were built at (rebuilt when the room or text scale changes it).
var _hand_scale: float = 0.0


func _exit_tree() -> void:
	Dialogue.dock_bottom()


func _ready() -> void:
	UiTheme.apply(self)
	_build_ui()
	engine.state_changed.connect(_on_state_changed)
	engine.action_refused.connect(_on_action_refused)
	engine.fight_ended.connect(_on_fight_ended)
	Settings.hints_changed.connect(_refresh_key_hints)
	resized.connect(_relayout.call_deferred)
	_relayout.call_deferred()
	if auto_start:
		start_fight(ENEMY_CHOICES[0], int(_seed_spin.value))
	if RunManager.pending_tutorial or (not Settings.tutorial_done and RunManager.profile.runs_completed == 0 and not _instant_playback()):
		if RunManager.pending_tutorial:
			for child in _picker_controls:
				child.visible = false  # the fight picker is a dev tool, not the tutorial
		RunManager.pending_tutorial = false
		start_tutorial()


# --- Public (also used by the integration tests) ----------------------------------

func attach_netrun(netrun: NetrunSession) -> void:
	log_note.clear()
	for child in _picker_controls:
		child.visible = false
	engine.adopt_netrun(netrun)
	_start_music()
	_relayout.call_deferred()


func start_fight(enemy_id: StringName, combat_seed: int) -> void:
	log_note.clear()
	log_note.append("[b]New fight:[/b] %s vs %s (seed %d)" % [CLASS_ID, enemy_id, combat_seed])
	engine.start_fight(CLASS_ID, [enemy_id], combat_seed, RING_ID)
	_start_music()


func end_turn() -> void:
	cancel_selection()
	AudioDirector.play_sfx("stamp")
	var before := engine.state().duplicate_state() if engine.has_fight() else null
	_pending_last_turn = before
	engine.submit(CombatAction.end_turn())


## State before the SEND IT being resolved (for the last-turn lines).
var _pending_last_turn: CombatState = null
## Last-turn line per combatant id (kept until the player acts).
var _last_turn: Dictionary = {}


## What the last SEND IT did, per wheel: the real HP change since it was pressed (so
## CORRUPTED bites, heals and turn-start effects count, H22), what block and shield soaked,
## attacks evaded, and hits its satellites or drones took for it. Short and numeric; the
## motion pass animates it.
static func last_turn_lines(before: CombatState, after: CombatState, events: Array[Dictionary]) -> Dictionary:
	var soaked := {}
	var evaded := {}
	var guarded := {}
	# HP changed by the resolve itself (before the next turn starts); the rest of the real
	# change happened at the start of the next turn (a boss's Auto-Renew heal, H23), which
	# the NEXT forecast (the end of the resolve) doesn't include.
	var resolved := {}
	var starting := false
	# Block and shield gained, statuses put on its slices and statuses its Encrypted slices
	# absorbed (H23: a turn that defended for 5 and was afflicted read "NO CHANGE").
	var gained := {}
	var shielded := {}
	var guard_guard := {}
	var statuses := {}
	var absorbed := {}
	for e in events:
		var t := String(e.get("type", ""))
		var target := StringName(String(e.get("target", "")))
		if t == "turn_start":
			starting = true
		if t == "block" or t == "shield":
			# A satellite's or drone's guard counts on its host's line (H24: "collections
			# drone +3 BLOCK" was forecast, then LAST TURN said NO CHANGE).
			var guard := before.get_combatant(target)
			if guard != null and (guard.is_satellite or before.drones.has(guard)):
				var host_id := guard.host_id if guard.host_id != &"" else before.player.id
				guard_guard[host_id] = int(guard_guard.get(host_id, 0)) + int(e.get("amount", 0))
			elif t == "block":
				gained[target] = int(gained.get(target, 0)) + int(e.get("amount", 0))
			else:
				shielded[target] = int(shielded.get(target, 0)) + int(e.get("amount", 0))
		elif t == "status":
			var names: Array = statuses.get(target, [])
			var sname: String = String(TranslationServer.translate(String(Palette.STATUS_WORDS.get(int(e.get("status", 0)), RC.Status.keys()[int(e.get("status", 0))]))))
			if not names.has(sname):
				names.append(sname)
			statuses[target] = names
		elif t == "status_absorbed":
			absorbed[target] = int(absorbed.get(target, 0)) + 1
		if not starting:
			if t == "damage":
				resolved[target] = int(resolved.get(target, 0)) - int(e.get("hp_damage", 0))
			elif t == "corrupted":
				resolved[target] = int(resolved.get(target, 0)) - int(e.get("amount", 0))
			elif t == "heal":
				resolved[target] = int(resolved.get(target, 0)) + int(e.get("amount", 0))
		if t == "damage":
			soaked[target] = int(soaked.get(target, 0)) + int(e.get("blocked", 0)) + int(e.get("shielded", 0))
			var victim := before.get_combatant(target)
			if victim != null and (victim.is_satellite or before.drones.has(victim)):
				var host := victim.host_id if victim.host_id != &"" else before.player.id
				guarded[host] = int(guarded.get(host, 0)) + int(e.get("hp_damage", 0))
		elif t == "evaded":
			evaded[target] = int(evaded.get(target, 0)) + 1
	var out := {}
	var wheels: Array[CombatantState] = [before.player]
	for c in before.enemies:
		if not c.is_satellite:
			wheels.append(c)
	for c in wheels:
		var now := after.get_combatant(c.id)
		var parts := PackedStringArray()
		var dhp := (now.hp if now != null else 0) - c.hp
		var in_resolve := int(resolved.get(c.id, 0))
		var at_start := dhp - in_resolve
		if in_resolve < 0:
			parts.append(String(TranslationServer.translate("%d HP")) % in_resolve)
		elif in_resolve > 0:
			parts.append(String(TranslationServer.translate("+%d HP")) % in_resolve)
		if at_start != 0:
			parts.append(String(TranslationServer.translate("%s AT TURN START")) % signed(at_start))
		if int(soaked.get(c.id, 0)) > 0:
			parts.append(String(TranslationServer.translate("%d BLOCKED")) % int(soaked[c.id]))
		if int(evaded.get(c.id, 0)) > 0:
			parts.append(String(TranslationServer.translate("EVADED %d")) % int(evaded[c.id]))
		if int(guarded.get(c.id, 0)) > 0:
			parts.append(String(TranslationServer.translate("GUARD TOOK %d")) % int(guarded[c.id]))
		if int(gained.get(c.id, 0)) > 0:
			parts.append(String(TranslationServer.translate("+%d BLOCK")) % int(gained[c.id]))
		if int(shielded.get(c.id, 0)) > 0:
			parts.append(String(TranslationServer.translate("+%d SHIELD")) % int(shielded[c.id]))
		if int(guard_guard.get(c.id, 0)) > 0:
			parts.append(String(TranslationServer.translate("GUARD +%d BLOCK")) % int(guard_guard[c.id]))
		for sname in statuses.get(c.id, []):
			parts.append(String(TranslationServer.translate("GOT %s")) % sname)
		if int(absorbed.get(c.id, 0)) > 0:
			parts.append(String(TranslationServer.translate("ENCRYPTED STOPPED %d")) % int(absorbed[c.id]))
		# The RAM a new turn brings back (H24: RAM went from 6 to 10 with nothing saying so).
		if c.is_player and after.ram != before.ram:
			parts.append(String(TranslationServer.translate("RAM %s")) % signed(after.ram - before.ram))
		if parts.is_empty():
			parts.append(String(TranslationServer.translate("NO CHANGE")))
		out[c.id] = String(TranslationServer.translate("LAST TURN: ")) + " · ".join(parts)
	return out


func rewind() -> void:
	cancel_selection()
	if engine.rewind() and tutorial != null and is_instance_valid(tutorial):
		var ev: Array[Dictionary] = [{"type": "rewind"}]
		tutorial.on_events(ev)


## Keyboard / pad nudge: the wheel and ring the W and R toggles chose.
func nudge(direction: int) -> void:
	var ring := RC.RingScope.INNER if _nudge_ring_option.selected == 1 else RC.RingScope.OUTER
	nudge_wheel(_selected_nudge_wheel(), direction, ring)


## A nudge arrow: `direction` +1 turns the wheel clockwise, -1 anticlockwise.
func nudge_wheel(wheel_id: StringName, direction: int, ring: int = RC.RingScope.OUTER) -> void:
	engine.submit(CombatAction.nudge(wheel_id, direction, ring))


## The RAM respin of your own wheel (GDD 2.5, 11.3).
func respin() -> void:
	cancel_selection()
	if not engine.has_fight():
		return
	var before: String = _landing_title(engine.state(), engine.state().player)["text"]
	var ram_before := engine.state().ram
	engine.submit(CombatAction.respin())
	var spent := ram_before - engine.state().ram
	if spent > 0:
		# Where it landed, even when it's the same slice (H23: 8 RAM seemed to buy nothing).
		var after: String = _landing_title(engine.state(), engine.state().player)["text"]
		_show_note(tr("RESPIN -%d RAM: %s%s") % [spent, after, tr(" AGAIN") if after == before else ""])


## A note saying what an action just did, in the toast's spot.
func _show_note(text: String) -> void:
	var at := _toast_spot()
	toast.show_note(text, at.position, at.size.x)


## Where toasts go: the foot of the right column, under the subtitles (H24: over the hand
## it covered the cards; H21: above the hand it covered the HP arcs). Position = the
## toast's bottom centre, size.x = the width it may take.
func _toast_spot() -> Rect2:
	var area := _notes_area.get_global_rect() if _notes_area != null else get_global_rect()
	return Rect2(Vector2(area.get_center().x, area.end.y - TOAST_GAP), Vector2(area.size.x, 0.0))


## Room between a toast and the foot of its column (px).
const TOAST_GAP := 6.0


## Plays a card at once with the default aim (the current target, the hidden toggles):
## tests and scripted play. Players go through select_card() / dragging.
func play_card(hand_index: int) -> void:
	if not engine.has_fight() or hand_index < 0 or hand_index >= engine.state().hand.size():
		return
	cancel_selection()
	engine.submit(_card_action(hand_index))


## A card picked by click, key 1-9 or pad A: a card with one legal play plays now; one
## with several waits for its target (drop zones light up; Enter / A / a click on a zone
## confirms, Esc / B / right-click cancels).
func select_card(hand_index: int) -> void:
	if not engine.has_fight() or hand_index < 0 or hand_index >= engine.state().hand.size():
		return
	if selecting == hand_index and _option_index >= 0:
		confirm_selection()
		return
	var options := CardTargeting.options(engine.resolver, engine.state(), hand_index)
	if options.is_empty():
		_on_action_refused(engine.validate(_card_action(hand_index)))
		return
	if options.size() == 1 and not _dragging:
		cancel_selection()
		engine.submit(options[0])
		return
	_begin_targeting(hand_index, options)


## The legal plays of the card being aimed (tests read them).
func selection_options() -> Array[CombatAction]:
	return _options


## The play aimed at now (null when none).
func aimed_action() -> CombatAction:
	return _options[_option_index] if selecting >= 0 and _option_index >= 0 and _option_index < _options.size() else null


## Moves the aim to the next (+1) or previous (-1) legal play.
func step_selection(step: int) -> void:
	if selecting < 0 or _options.is_empty():
		return
	_option_index = posmod(_option_index + step, _options.size())
	_show_selection()


func confirm_selection() -> void:
	if selecting < 0 or _option_index < 0 or _option_index >= _options.size():
		return
	var action := _options[_option_index]
	cancel_selection()
	engine.submit(action)


func cancel_selection() -> void:
	if selecting < 0:
		return
	selecting = -1
	_options.clear()
	_option_index = -1
	for v in _views():
		v.valid_zones.clear()
		v.hover_zone = {}
		v.queue_redraw()
	_dim_hand()
	_clear_ghost()
	_show_end_turn_preview()


func cycle_target() -> void:
	if _target_option.item_count == 0:
		return
	var next := (_target_option.selected + 1) % _target_option.item_count
	_target_option.select(next)
	engine.submit(CombatAction.target(_target_option.get_item_metadata(next)))


func toggle_card_target() -> void:
	_card_target_option.select((_card_target_option.selected + 1) % 2)
	_rebuild_slot_option()


func toggle_ring() -> void:
	var driven := engine.state().get_combatant(_selected_nudge_wheel()) if engine.has_fight() else null
	if _nudge_ring_option.selected == 0 and driven != null and not driven.wheel.has_inner_ring():
		_on_action_refused("%s has no inner ring." % driven.display_name)
		return
	_nudge_ring_option.select((_nudge_ring_option.selected + 1) % 2)
	_sync_arrow_hints()


func toggle_nudge_wheel() -> void:
	_nudge_wheel_option.select((_nudge_wheel_option.selected + 1) % 2)
	# A wheel without an inner ring takes outer nudges (H22: LB/RB were refused silently).
	var driven := engine.state().get_combatant(_selected_nudge_wheel()) if engine.has_fight() else null
	if driven != null and not driven.wheel.has_inner_ring():
		_nudge_ring_option.select(0)
	_sync_arrow_hints()
	_refresh_status()


## Default card nudge direction for play_card() (players aim with the arrows instead).
func toggle_direction() -> void:
	_direction_option.select((_direction_option.selected + 1) % 2)


func set_direction(direction: int) -> void:
	_direction_option.select(0 if direction > 0 else 1)


## Default chosen slice for play_card(): -1 = none chosen.
func cycle_slot() -> void:
	if _slot_option.item_count == 0:
		return
	_slot_option.select((_slot_option.selected + 1) % _slot_option.item_count)


func set_slot(slot: int) -> void:
	if slot + 1 < _slot_option.item_count:
		_slot_option.select(slot + 1)


func selected_slot() -> int:
	return _slot_option.selected - 1


func selected_direction() -> int:
	return 1 if _direction_option.selected == 0 else -1


func start_tutorial() -> void:
	if tutorial != null and is_instance_valid(tutorial):
		return
	tutorial = TutorialOverlay.new(TUTORIAL_RECT.size)
	tutorial.position = TUTORIAL_RECT.position  # the right column: never on a wheel (GDD 9.2)
	add_child(tutorial)
	_relayout.call_deferred()
	tutorial.finished.connect(func() -> void: tutorial = null; _relayout.call_deferred())


func open_settings() -> void:
	if _settings_panel != null:
		_settings_panel.queue_free()
		_settings_panel = null
		return
	cancel_selection()
	_settings_panel = PauseMenu.new()
	# On a CanvasLayer of its own: inside a netrun the combat scene sits in a scroll area
	# that would clip the menu's bottom (H16). Centred on the viewport.
	if _menu_layer == null:
		_menu_layer = CanvasLayer.new()
		_menu_layer.layer = MENU_LAYER
		add_child(_menu_layer)
	var view := get_viewport_rect().size
	_settings_panel.position = ((view - PauseMenu.MENU_SIZE) / 2.0).floor()
	_settings_panel.resumed.connect(open_settings)
	_settings_panel.quit_to_title.connect(func() -> void: open_settings(); RunManager.go_to_title())
	_menu_layer.add_child(_settings_panel)
	UiTheme.apply(_settings_panel)  # the CanvasLayer cuts theme inheritance: font and text scale (H18)
	get_tree().paused = false


## Inspect (GDD 9.5): what is under a global point (a slice, a nudge arrow, a satellite,
## a hub, a card, a Daemon), shown beside it for keyboard and pad players; the mouse
## also has tooltips. Returns the text.
func inspect_at(global_point: Vector2) -> String:
	var text := ""
	var target := Rect2(global_point, Vector2.ZERO)
	if engine.has_fight():
		for v in _views():
			if v.combatant == null:
				continue
			var z := v.zone_at(global_point)
			if z.is_empty():
				continue
			if String(z["kind"]) == "hub":
				text = _describe_slot(v.combatant, -1)
			elif String(z["kind"]) == "slot":
				text = _describe_slot(v.combatant, int(z["slot"]))
			else:
				text = v._get_tooltip(global_point - v.global_position)
			target = v.wheel_rect()
			break
		if text == "":
			for c in _hand_box.get_children():
				if c is ZineCard and (c as Control).get_global_rect().has_point(global_point):
					text = (c as ZineCard).tooltip_text
					target = (c as Control).get_global_rect()
		if text == "" and daemon_row.get_global_rect().has_point(global_point):
			text = daemon_row.describe_all()
			target = daemon_row.get_global_rect()
	last_inspect = text
	inspect_popup.show_for(text, target, get_global_rect())
	return text


## Odds a random effect shows instead of a result (GDD 2.10): the slice type mix of a
## wheel, optionally leaving the Miss slice out (random non-Miss picks).
func odds_text(c: CombatantState, non_miss_only: bool = false) -> String:
	var parts := PackedStringArray()
	for chip in _odds_chips(c, non_miss_only):
		parts.append(String(chip["text"]))
	return "odds: " + " / ".join(parts)


func _odds_chips(c: CombatantState, non_miss_only: bool = false) -> Array[Dictionary]:
	var counts := {}
	var order: Array[String] = []
	var total := 0
	for id in c.wheel.slot_slice_ids:
		var slice := engine.content(id) as SliceData
		if slice == null or (non_miss_only and slice.slice_type == RC.SliceType.MISS):
			continue
		var key: String = "%s %s" % [Palette.SLICE_GLYPHS.get(slice.slice_type, "?"), tr(String(Palette.SLICE_WORDS.get(slice.slice_type, "?")))]
		if not counts.has(key):
			order.append(key)
		counts[key] = int(counts.get(key, 0)) + 1
		total += 1
	var out: Array[Dictionary] = []
	for key in order:
		out.append({"text": "%s %d%%" % [key, roundi(100.0 * counts[key] / maxf(1.0, total))], "color": Palette.NOTE_PAPER, "ink": Palette.INK})
	return out


## Layout rule (STYLE_GUIDE 4, GDD 9.2): nothing zine covers a wheel, its values, its
## satellites or its HP arc; no tag covers another wheel; subtitles cover no tag.
## Returns the offenders.
func layout_violations() -> Array[String]:
	var out: Array[String] = []
	var wheels := _views()
	var covers: Array = []
	for z in _zine_elements:
		if is_instance_valid(z) and z.is_visible_in_tree():
			covers.append([z.name if z.name != "" else z.get_class(), z.get_global_rect()])
	if tutorial != null and is_instance_valid(tutorial):
		covers.append(["tutorial", tutorial.get_global_rect()])
	for child in _hand_box.get_children():
		covers.append(["card", (child as Control).get_global_rect()])
	for key in _stickers:
		if (_stickers[key] as Control).is_visible_in_tree():
			covers.append(["%s sticker" % key, (_stickers[key] as Control).get_global_rect()])
	if toast.visible:
		covers.append(["toast", toast.get_global_rect()])
	if Dialogue.bar.visible:
		covers.append(["subtitles", Rect2(Dialogue.bar.global_position, Dialogue.bar.size)])
	for cv in covers:
		for w in wheels:
			if w.combatant != null and w.covers(cv[1]):
				out.append("%s covers %s's wheel" % [cv[0], w.combatant.display_name])
	for w in wheels:
		if w.combatant == null or not w.intent_rect().has_area():
			continue
		for other in wheels:
			if other != w and other.combatant != null and other.covers(w.intent_rect()):
				out.append("%s's tag covers %s's wheel" % [w.combatant.display_name, other.combatant.display_name])
		for cv in covers:
			if cv[0] == "subtitles" and (cv[1] as Rect2).intersects(w.intent_rect()):
				out.append("subtitles cover %s's tag" % w.combatant.display_name)
		if not w.get_global_rect().grow(0.5).encloses(w.intent_rect()):
			out.append("%s's tag leaves its view" % w.combatant.display_name)
	return out


func player_wheel_color() -> Color:
	return _player_view.wheel_color


func enemy_wheel_colors() -> Array[Color]:
	var out: Array[Color] = []
	for v in _enemy_views.values():
		out.append(v.wheel_color)
	return out


# --- Input -----------------------------------------------------------------------

## True only right after a focus-navigation press (D-pad / arrows / Shift+Tab): then the
## newly focused card shows its preview. Any other input leaves the End Turn preview.
var _nav_focus: bool = false


func _input(event: InputEvent) -> void:
	if event is InputEventMouseMotion or event is InputEventMouseButton:
		_nav_focus = false
	elif event.is_pressed() and not event.is_echo():
		_nav_focus = event.is_action("ui_left") or event.is_action("ui_right") or event.is_action("ui_up") \
			or event.is_action("ui_down") or event.is_action("ui_focus_prev") or event.is_action("ui_focus_next")
	if selecting < 0 or _dragging or _settings_panel != null or not event.is_pressed() or event.is_echo():
		return
	# Aiming a card: the D-pad / arrows / Tab walk the legal targets, A / Enter confirms,
	# B / Esc / right-click cancels. Focus stays on the card meanwhile.
	if event.is_action("ui_left") or event.is_action("ui_up"):
		step_selection(-1)
	elif event.is_action("ui_right") or event.is_action("ui_down") or event.is_action("cycle_target"):
		step_selection(1)
	elif event.is_action("ui_accept"):
		confirm_selection()
	elif event.is_action("ui_cancel") or event.is_action("open_settings") or (event is InputEventMouseButton and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_RIGHT):
		cancel_selection()
	else:
		return
	get_viewport().set_input_as_handled()


## Gives the hand focus (the first playable card, else SEND IT): the netrun scene calls it
## when it shows a fight.
func focus_hand() -> void:
	_link_hand_focus()
	UiFocus.focus_first(_hand_box, false, _end_turn_button.get_parent())


## Explicit D-pad neighbours in the hand: the cards are tilted stickers, so Godot's
## geometric search would jump elsewhere. Left/right walk the hand, the last card leads to
## SEND IT, up leads to the stickers.
func _link_hand_focus() -> void:
	var cards: Array[Control] = []
	for c in _hand_box.get_children():
		if c is Control and not c.is_queued_for_deletion():
			cards.append(c)
	for i in cards.size():
		var c := cards[i]
		if i > 0:
			c.focus_neighbor_left = c.get_path_to(cards[i - 1])
			c.focus_previous = c.focus_neighbor_left
		if i + 1 < cards.size():
			c.focus_neighbor_right = c.get_path_to(cards[i + 1])
			c.focus_next = c.focus_neighbor_right
		else:
			# The last card leads to the stickers, then SEND IT.
			c.focus_neighbor_right = c.get_path_to(_respin_button)
			c.focus_next = c.focus_neighbor_right
			_respin_button.focus_neighbor_left = _respin_button.get_path_to(c)
			_rewind_button.focus_neighbor_left = _rewind_button.get_path_to(c)
	_respin_button.focus_neighbor_right = _respin_button.get_path_to(_end_turn_button)
	_rewind_button.focus_neighbor_right = _rewind_button.get_path_to(_end_turn_button)
	_respin_button.focus_neighbor_bottom = _respin_button.get_path_to(_rewind_button)
	_rewind_button.focus_neighbor_top = _rewind_button.get_path_to(_respin_button)
	_end_turn_button.focus_neighbor_left = _end_turn_button.get_path_to(_respin_button)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("open_settings"):
		open_settings()
		get_viewport().set_input_as_handled()
		return
	if not engine.has_fight():
		return
	if event.is_action_pressed("inspect") and event is InputEventMouseButton:
		inspect_at((event as InputEventMouseButton).global_position)
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("inspect"):
		# Pad / keyboard inspect: the focused control (a card, a sticker) is inspected.
		var owner := get_viewport().gui_get_focus_owner()
		if owner != null:
			inspect_at(owner.get_global_rect().get_center())
		get_viewport().set_input_as_handled()
		return
	if event is InputEventJoypadMotion:
		# The triggers toggle the nudge wheel / ring once per squeeze (a trigger sends a stream
		# of motion events while it moves).
		var m := event as InputEventJoypadMotion
		var down := m.axis_value >= Settings.PAD_SWITCH_DEADZONE
		var was: bool = _trigger_down.get(m.axis, false)
		_trigger_down[m.axis] = down
		if down and not was:
			if event.is_action("toggle_nudge_wheel"):
				toggle_nudge_wheel()
				get_viewport().set_input_as_handled()
			elif event.is_action("toggle_ring"):
				toggle_ring()
				get_viewport().set_input_as_handled()
		return
	for i in 9:
		if event.is_action_pressed("card_%d" % (i + 1)):
			select_card(i)
			get_viewport().set_input_as_handled()
			return
	if event.is_action_pressed("nudge_left"):
		nudge(-1)
	elif event.is_action_pressed("nudge_right"):
		nudge(1)
	elif event.is_action_pressed("end_turn"):
		end_turn()
	elif event.is_action_pressed("rewind"):
		rewind()
	elif event.is_action_pressed("cycle_target"):
		cycle_target()
	elif event.is_action_pressed("toggle_ring"):
		toggle_ring()
	elif event.is_action_pressed("toggle_nudge_wheel"):
		toggle_nudge_wheel()
	elif event.is_action_pressed("respin"):
		respin()
	else:
		return
	get_viewport().set_input_as_handled()


func _notification(what: int) -> void:
	if what == NOTIFICATION_DRAG_BEGIN:
		var data: Variant = get_viewport().gui_get_drag_data()
		if data is Dictionary and (data as Dictionary).has("hand_index") and engine != null and engine.has_fight():
			_dragging = true
			var i := int(data["hand_index"])
			var options := CardTargeting.options(engine.resolver, engine.state(), i)
			if options.is_empty():
				_dragging = false
				_on_action_refused(engine.validate(_card_action(i)))
			else:
				_begin_targeting(i, options)
	elif what == NOTIFICATION_DRAG_END:
		if _dragging:
			_dragging = false
			if not get_viewport().gui_is_drag_successful():
				cancel_selection()


# --- Aiming cards ------------------------------------------------------------------

func _begin_targeting(hand_index: int, options: Array[CombatAction]) -> void:
	selecting = hand_index
	_options = options
	# Arrows / D-pad step through the targets in screen order, left to right then top to
	# bottom (H22: list order jumped about); ties keep the list order.
	var keyed: Array = []
	for i in _options.size():
		var z := _zone_of(_options[i])
		var v := _view_of(z[0])
		var at: Vector2 = v.zone_center(z[1]) if v != null else Vector2.ZERO
		keyed.append([at.x, at.y, i])
	keyed.sort_custom(func(a: Array, b: Array) -> bool:
		if not is_equal_approx(a[0], b[0]):
			return a[0] < b[0]
		if not is_equal_approx(a[1], b[1]):
			return a[1] < b[1]
		return a[2] < b[2])
	var sorted: Array[CombatAction] = []
	for k in keyed:
		sorted.append(_options[int(k[2])])
	_options = sorted
	_option_index = 0
	var state := engine.state()
	for i in _options.size():
		if _options[i].wheel_id == state.target_id and _options[i].direction == 1:
			_option_index = i
			break
	for v in _views():
		v.valid_zones.clear()
		v.hover_zone = {}
	for a in _options:
		var z := _zone_of(a)
		var v := _view_of(z[0])
		if v != null and not WheelView._zone_is(v.valid_zones, z[1]):
			v.valid_zones.append(z[1])
	_show_aim_hint()
	# The card being aimed stays lifted (it holds focus while the aim moves).
	if hand_index < _hand_box.get_child_count() and not _dragging:
		(_hand_box.get_child(hand_index) as Control).grab_focus()
	if _dragging:
		_option_index = -1  # nothing aimed until the card is over a zone
		_show_end_turn_preview()
		_dim_hand()
		for v in _views():
			v.queue_redraw()
		return
	_show_selection()


## The view and zone an option lights up: [view id, zone].
func _zone_of(a: CombatAction) -> Array:
	var state := engine.state()
	var card := engine.content(state.hand[a.hand_index]) as CardData
	var aimed := state.get_combatant(a.wheel_id)
	if aimed == null:
		return [&"", {}]
	var slot_wheel := CardTargeting.slot_wheel_of(state, card, aimed)
	if slot_wheel != null and a.slot_index >= 0:
		return [slot_wheel.id, {"kind": "slot", "slot": a.slot_index}]
	if aimed.is_satellite:
		if CardTargeting.uses_direction(card):
			return [aimed.host_id, {"kind": "satellite", "id": aimed.id, "direction": CardTargeting.screen_direction(card, a)}]
		return [aimed.host_id, {"kind": "satellite", "id": aimed.id}]
	if CardTargeting.uses_direction(card):
		var ring := a.ring
		if ring < 0:
			ring = RC.RingScope.OUTER if CardTargeting.chooses_ring(card) else RC.RingScope.INNER
		return [aimed.id, {"kind": "arrow", "ring": ring, "direction": a.direction}]
	return [aimed.id, {"kind": "hub"}]


## The option a zone on `view_id` stands for (-1 = none): an exact match, else any play
## aimed at that wheel as a whole.
func _option_for(view_id: StringName, zone: Dictionary) -> int:
	if zone.is_empty():
		return -1
	var whole := -1
	for i in _options.size():
		var z := _zone_of(_options[i])
		if z[0] != view_id:
			continue
		if WheelView._zone_is([zone], z[1]):
			return i
		if String((z[1] as Dictionary).get("kind", "")) == "hub" and whole < 0:
			whole = i
	return whole


func _on_view_zone(view_id: StringName, zone: Dictionary) -> void:
	if selecting >= 0:
		var i := _option_for(view_id, zone)
		if i >= 0:
			_option_index = i
			confirm_selection()
		return
	# Not aiming: clicking an enemy wheel (or one of its satellites) targets it.
	if not engine.has_fight() or view_id == engine.state().player.id or zone.is_empty():
		return
	var want: StringName = StringName(zone["id"]) if String(zone.get("kind", "")) == "satellite" else view_id
	if engine.state().target_id != want:
		engine.submit(CombatAction.target(want))


func _on_view_arrow(view_id: StringName, ring: int, direction: int) -> void:
	if selecting >= 0:
		_on_view_zone(view_id, {"kind": "arrow", "ring": ring, "direction": direction})
		return
	nudge_wheel(view_id, direction, ring)


func _on_view_drag_hover(view_id: StringName, zone: Dictionary) -> void:
	if selecting < 0:
		return
	var i := _option_for(view_id, zone)
	if i == _option_index:
		return
	_option_index = i
	if i < 0:
		for v in _views():
			v.hover_zone = {}
			v.queue_redraw()
		_clear_ghost()
		_show_end_turn_preview()
		_aim_line.queue_redraw()
		return
	_show_selection()


func _on_view_drop(view_id: StringName, zone: Dictionary) -> void:
	var i := _option_for(view_id, zone)
	if selecting < 0 or i < 0:
		_dragging = false
		cancel_selection()
		return
	_option_index = i
	_dragging = false
	confirm_selection()


## A dashed acid line from the aimed card to the zone it plays on, with a ring there.
func _draw_aim_line() -> void:
	if selecting < 0 or _option_index < 0 or selecting >= _hand_box.get_child_count():
		return
	var z := _zone_of(_options[_option_index])
	var v := _view_of(z[0])
	if v == null:
		return
	var origin := _aim_line.get_global_rect().position
	var card := (_hand_box.get_child(selecting) as Control).get_global_rect()
	var from := Vector2(card.get_center().x, card.position.y) - origin
	var to := v.zone_center(z[1]) - origin
	var n := maxi(2, int(from.distance_to(to) / 14.0))
	for k in n:
		if k % 2 == 0:
			_aim_line.draw_line(from.lerp(to, float(k) / n), from.lerp(to, float(k + 1) / n), Palette.CELL_ACID, AIM_LINE_WIDTH)
	_aim_line.draw_arc(to, 12.0, 0, TAU, 20, Palette.CELL_ACID, AIM_LINE_WIDTH)


## Fades the cards not being aimed (and restores them).
func _dim_hand() -> void:
	for c in _hand_box.get_children():
		(c as Control).modulate.a = AIM_DIM if selecting >= 0 and c.get_index() != selecting else 1.0
	_aim_line.queue_redraw()
	if selecting < 0 and _aim_hint != null:
		_aim_hint.visible = false


## While a card is aimed: what to do, over the hand (H22: players didn't know to click a
## glowing target).
func _show_aim_hint() -> void:
	if _aim_hint == null:
		return
	_aim_hint.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	if Settings.pad_active:
		_aim_hint.text = tr("%s / %s: choose a glowing target  ·  %s: play  ·  %s: cancel") % [Settings.key_text(&"ui_left"), Settings.key_text(&"ui_right"), Settings.key_text(&"ui_accept"), Settings.key_text(&"ui_cancel")]
	else:
		_aim_hint.text = tr("Drop or click on a glowing target  ·  right-click cancels")
	# Over the enemy side, above both the hand and the RAM row, shrunk to the room to the
	# screen's edge (H24: at 1.6 it ran over "RAM 6/12" and off the screen).
	var hand := _hand_box.get_global_rect()
	var right := _enemy_views_box.get_global_rect()
	var x := right.position.x + 8.0
	var room := get_global_rect().end.x - x - AIM_HINT_MARGIN
	var fs := roundi(AIM_HINT_FONT * Settings.text_scale)
	var font := _aim_hint.get_theme_font("font")
	while fs > STATUS_MIN_FONT and font.get_string_size(_aim_hint.text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > room:
		fs -= 1
	_aim_hint.add_theme_font_size_override("font_size", fs)
	# Sized from the font itself: the label's minimum lags a font change by a frame.
	var hs := Vector2(font.get_string_size(_aim_hint.text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x, font.get_height(fs))
	_aim_hint.size = hs
	var top := hand.position.y
	if ram_note != null and ram_note.is_visible_in_tree():
		top = minf(top, ram_note.get_global_rect().position.y)
	_aim_hint.global_position = Vector2(clampf(x, 0.0, maxf(0.0, get_global_rect().end.x - hs.x)), top - hs.y - 4.0)
	_aim_hint.visible = true


## Room kept between the aim hint and the screen's right edge (px).
const AIM_HINT_MARGIN := 8.0


## Lights the aimed zone and previews that play.
func _show_selection() -> void:
	_dim_hand()
	if selecting < 0 or _option_index < 0:
		return
	var z := _zone_of(_options[_option_index])
	var aimed_view := _view_of(z[0])
	for v in _views():
		v.hover_zone = z[1] if v == aimed_view else {}
		v.queue_redraw()
	_preview_action(_options[_option_index])


# --- Engine callbacks --------------------------------------------------------------

func _on_state_changed(state: CombatState, events: Array[Dictionary]) -> void:
	_last_events = events
	if _pending_last_turn != null:
		_last_turn = last_turn_lines(_pending_last_turn, state, events)
		_pending_last_turn = null
	elif not events.is_empty():
		_last_turn.clear()  # the player acted: the result gives way to the new preview
	for e in state.enemies:
		RunManager.record_seen(e.source_id)
	_play_log(events)
	_refresh(state)
	_feedback(state, events)
	if tutorial != null and is_instance_valid(tutorial):
		tutorial.on_events(events)
	if engine.can_rewind() == false and _rewound:
		_rewound = false
	for e in events:
		if e.get("type", "") == "pointer" and e.get("owner") == state.player.id and int(e.get("tier", -1)) == RC.PrecisionTier.PERFECT:
			RunManager.record_perfect()


## A refused action: a toast over the hand says why (and the hidden record keeps it).
func _on_action_refused(reason: String) -> void:
	if reason == "":
		return
	log_note.append("[color=#c05000]%s[/color]" % reason)
	preview_note.clear()
	preview_note.append(reason)
	var at := _toast_spot()
	toast.show_text(tr(reason), at.position, at.size.x)
	# The RAM bar flashes when RAM is what's missing.
	if reason.contains("RAM"):
		ram_note.flash_short()
	AudioDirector.play_sfx("click")


func _on_fight_ended(outcome: int) -> void:
	log_note.append("[b]%s[/b]" % ("VICTORY" if outcome == CombatState.Outcome.VICTORY else "DEFEAT"))
	if outcome == CombatState.Outcome.VICTORY:
		Fx.flash(Palette.CELL_ACID, 0.3)


## Pass-by-pass playback into the hidden log record (instant when headless or under
## reduce-effects).
func _play_log(events: Array[Dictionary]) -> void:
	_log_generation += 1
	var generation := _log_generation
	var delay := 0.0
	var instant := _instant_playback()
	for e in events:
		if not e.has("text"):
			continue
		var text := String(e["text"])
		if instant:
			log_note.append(text)
			continue
		var t: String = e.get("type", "")
		if t == "pass" or t == "turn_start" or t == "resolve_start":
			delay += PASS_DELAY
		if delay <= 0.0:
			log_note.append(text)
		else:
			get_tree().create_timer(delay).timeout.connect(func() -> void:
				if generation == _log_generation and is_instance_valid(log_note):
					log_note.append(text))


func _instant_playback() -> bool:
	return DisplayServer.get_name() == "headless" or not Fx.effects_enabled()


## Precision and action feedback (STYLE_GUIDE 5, GDD 10): Perfect = latch + wheel-local
## inversion + 2-frame freeze (+ a limited flash); Good = click; Partial = stutter shake;
## Miss slice = static burst. Nudges tick, spins run down, flips clack. Telegraphed
## migrations flicker the boss pointers until they move.
func _feedback(state: CombatState, events: Array[Dictionary]) -> void:
	for e in events:
		match String(e.get("type", "")):
			"nudge":
				AudioDirector.play_sfx("tick")
			"spin", "respin":
				AudioDirector.play_spin(int(e.get("moved", 6)))
			"flip":
				AudioDirector.play_sfx("clack")
			"pointer":
				if e.get("owner") != state.player.id:
					continue
				var is_miss: bool = _slice_type_of(state, e) == RC.SliceType.MISS
				var tier := int(e.get("tier", RC.PrecisionTier.GOOD))
				AudioDirector.play_precision(tier, is_miss)
				if is_miss:
					_flicker_view(_player_view)
					_bark("miss", state)
				elif tier == RC.PrecisionTier.PERFECT:
					_perfect_feedback(_player_view)
					_bark("perfect", state)
				elif tier == RC.PrecisionTier.PARTIAL:
					_stutter_view(_player_view)
			"boss_phase":
				AudioDirector.play_sfx("alarm")
				Fx.flash(Palette.corp_color(RunManager.campaign.corporation_id) if RunManager.campaign != null else Palette.CORP_SOLACE, 0.3)
				_bark("boss", state)
			"damage":
				if e.get("target") == state.player.id and int(e.get("hp_damage", 0)) > 0 and state.player.hp * 2 <= state.player.max_hp:
					_bark("hurt", state)
			"deploy":
				_bark("deploy", state)
			"combat_end":
				_bark("victory" if int(e.get("outcome", 0)) == CombatState.Outcome.VICTORY else "defeat", state)
			"boss_migrate_telegraph":
				if _enemy_views.has(e.get("target")):
					_start_migrate_flicker(_enemy_views[e["target"]])
			"deploy", "botnet_seed":
				AudioDirector.play_sfx("click")


## Operative barks (GDD 8.6): at most one per turn per trigger, chosen by class and turn.
var _barked_turn: Dictionary = {}


func _bark(trigger: String, state: CombatState) -> void:
	var key := "%s:%d" % [trigger, state.turn]
	if _barked_turn.has(key) or _instant_playback():
		return
	_barked_turn[key] = true
	Dialogue.bark(state.player.source_id, trigger, state.turn + hash(engine.session.combat_seed))


func _slice_type_of(state: CombatState, e: Dictionary) -> int:
	var slot := int(e.get("slice_index", 0))
	var slice := engine.content(state.player.wheel.slot_slice_ids[slot]) as SliceData
	return slice.slice_type if slice != null else RC.SliceType.ATTACK


func _perfect_feedback(view: WheelView) -> void:
	view.inverted = true
	view.queue_redraw()
	Fx.flash(Palette.CELL_PINK, 0.35, 0.12)
	Fx.freeze_frames(2)
	await get_tree().process_frame
	await get_tree().process_frame
	if is_instance_valid(view):
		view.inverted = false
		view.queue_redraw()


func _stutter_view(view: WheelView) -> void:
	if not Fx.effects_enabled():
		return
	var tw := create_tween()
	for i in 3:
		tw.tween_property(view, "shake", Vector2(4 if i % 2 == 0 else -4, 0), 0.03)
	tw.tween_property(view, "shake", Vector2.ZERO, 0.03)
	tw.tween_callback(view.queue_redraw)


func _flicker_view(view: WheelView) -> void:
	if not Fx.effects_enabled():
		return
	var tw := create_tween()
	tw.tween_property(view, "modulate:a", 0.4, 0.04)
	tw.tween_property(view, "modulate:a", 1.0, 0.08)


## Migration flicker (GDD 9.2): the current pointers fade in and out while the dashed
## "next" pointers show where they go; stops when the state no longer has a pending move.
func _start_migrate_flicker(view: WheelView) -> void:
	if _migrate_tween != null and _migrate_tween.is_valid():
		_migrate_tween.kill()
	if not Fx.effects_enabled():
		view.pointer_alpha = 0.6
		view.queue_redraw()
		return
	_migrate_tween = create_tween().set_loops()
	_migrate_tween.tween_property(view, "pointer_alpha", 0.2, 0.25)
	_migrate_tween.tween_callback(view.queue_redraw)
	_migrate_tween.tween_property(view, "pointer_alpha", 1.0, 0.25)
	_migrate_tween.tween_callback(view.queue_redraw)


func _stop_migrate_flicker() -> void:
	if _migrate_tween != null and _migrate_tween.is_valid():
		_migrate_tween.kill()
	_migrate_tween = null
	for v in _enemy_views.values():
		v.pointer_alpha = 1.0


func _start_music() -> void:
	var boss := false
	if engine.has_fight():
		for e in engine.state().enemies:
			var data := engine.content(e.source_id) as EnemyData
			if data != null and (data.is_boss or data.is_mini_boss):
				boss = true
	AudioDirector.play_music("boss" if boss else "combat")
	var band := RunManager.campaign.heat_majors_crossed(RunManager.config()) if RunManager.campaign != null else 0
	AudioDirector.set_heat_layers(band)


# --- UI ------------------------------------------------------------------------------

func _build_ui() -> void:
	background = WireframeBackground.new()
	background.city.dim = 0.55  # the arena: wheels first, city second
	add_child(background)
	var root := VBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.add_theme_constant_override("separation", 4)
	add_child(root)

	var top := HFlowContainer.new()  # wraps at large text scales
	root.add_child(top)
	var fight_label := _label("Fight:")
	top.add_child(fight_label)
	_picker_controls.append(fight_label)
	# One dropdown (H24: a button per enemy left the status line ~100 px at 1.6).
	var pick := OptionButton.new()
	pick.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED  # content ids, dev only
	for enemy_id in ENEMY_CHOICES:
		pick.add_item(String(enemy_id))
	pick.item_selected.connect(func(i: int) -> void: start_fight(ENEMY_CHOICES[i], int(_seed_spin.value)))
	top.add_child(pick)
	_picker_controls.append(pick)
	var seed_label := _label("Seed:")
	top.add_child(seed_label)
	_picker_controls.append(seed_label)
	_seed_spin = SpinBox.new()
	_seed_spin.min_value = 0
	_seed_spin.max_value = 999999
	_seed_spin.value = 1
	top.add_child(_seed_spin)
	_picker_controls.append(_seed_spin)
	_status = _label("")
	_status.clip_text = true
	# Its text is built from translated parts (not translated again), and shrinks to its
	# width (H24: at 1.6 the switch keys ran under Settings).
	_status.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_status.resized.connect(_fit_status)
	_status.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_status.mouse_filter = Control.MOUSE_FILTER_PASS
	_status.tooltip_text = "The turn, and the free nudges left this turn (each extra nudge costs RAM)."
	top.add_child(_status)
	_settings_button = _button("Settings", open_settings)
	_settings_button.tooltip_text = "Pause: options, codex, save and quit." 
	top.add_child(_settings_button)

	var middle := HBoxContainer.new()
	middle.size_flags_vertical = Control.SIZE_EXPAND_FILL
	middle.add_theme_constant_override("separation", 8)
	root.add_child(middle)

	_arena = HBoxContainer.new()
	_arena.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_arena.size_flags_vertical = Control.SIZE_EXPAND_FILL
	middle.add_child(_arena)
	var player_col := VBoxContainer.new()
	player_col.size_flags_vertical = Control.SIZE_EXPAND_FILL
	player_col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	player_col.add_theme_constant_override("separation", 0)
	_arena.add_child(player_col)
	_player_view = WheelView.new()
	_player_view.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_player_view.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	player_col.add_child(_player_view)
	_connect_view(_player_view)
	ram_note = RamBar.new()
	ram_note.name = "RamTally"
	player_col.add_child(ram_note)
	_enemy_views_box = VBoxContainer.new()
	_enemy_views_box.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_enemy_views_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_arena.add_child(_enemy_views_box)

	# Right column: the Polaroid and Heat, the Daemons, then the subtitles and the tutorial.
	_right = VBoxContainer.new()
	_right.custom_minimum_size = Vector2(RIGHT_WIDTH, 0)
	middle.add_child(_right)
	var side_top := HBoxContainer.new()
	side_top.add_theme_constant_override("separation", 10)
	_right.add_child(side_top)
	portrait = Polaroid.new("Breaker", "[BREAKER PORTRAIT]", -3.0)
	portrait.name = "Polaroid"
	portrait.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	side_top.add_child(portrait)
	heat_poster = HeatPoster.new(false)
	heat_poster.name = "HeatPoster"
	heat_poster.tooltip_text = "Heat: the corporation's attention. Thresholds bring raids and harder rules."
	if RunManager.campaign != null:
		heat_poster.hot_color = Palette.corp_color(RunManager.campaign.corporation_id)
	side_top.add_child(heat_poster)
	daemon_row = DaemonRow.new()
	daemon_row.name = "DaemonRow"
	_right.add_child(daemon_row)
	_notes_area = Control.new()
	_notes_area.name = "NotesArea"
	_notes_area.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_notes_area.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_right.add_child(_notes_area)
	_zine_elements.append_array([portrait, heat_poster])
	# Hidden text records.
	preview_note = ZineNote.new("WHAT WILL RESOLVE", Vector2(RIGHT_WIDTH, 150))
	preview_note.name = "PreviewNote"
	preview_note.visible = false
	_right.add_child(preview_note)
	log_note = ZineNote.new("LOG", Vector2(RIGHT_WIDTH, 150))
	log_note.name = "LogStrip"
	log_note.visible = false
	_right.add_child(log_note)

	# The hidden option row keeps the keyboard toggles and play_card()'s defaults.
	var controls := HFlowContainer.new()
	controls_row = controls
	controls.visible = false
	root.add_child(controls)
	_target_option = OptionButton.new()
	_target_option.item_selected.connect(func(i: int) -> void: engine.submit(CombatAction.target(_target_option.get_item_metadata(i))))
	controls.add_child(_target_option)
	_nudge_wheel_option = OptionButton.new()
	_nudge_wheel_option.add_item("Nudge own")
	_nudge_wheel_option.add_item("Nudge tgt")
	controls.add_child(_nudge_wheel_option)
	_nudge_ring_option = OptionButton.new()
	_nudge_ring_option.add_item("Outer")
	_nudge_ring_option.add_item("Inner")
	controls.add_child(_nudge_ring_option)
	_nudge_minus_button = _button("-1", func() -> void: nudge(-1))
	controls.add_child(_nudge_minus_button)
	_nudge_plus_button = _button("+1", func() -> void: nudge(1))
	controls.add_child(_nudge_plus_button)
	_card_target_option = OptionButton.new()
	_card_target_option.add_item("Card>tgt")
	_card_target_option.add_item("Card>own")
	_card_target_option.item_selected.connect(func(_i: int) -> void: _rebuild_slot_option())
	controls.add_child(_card_target_option)
	_direction_option = OptionButton.new()
	_direction_option.add_item("Dir +")
	_direction_option.add_item("Dir -")
	controls.add_child(_direction_option)
	_slot_option = OptionButton.new()
	_slot_option.add_item("Slice auto")
	controls.add_child(_slot_option)

	var bottom := HBoxContainer.new()
	bottom.add_theme_constant_override("separation", 10)
	root.add_child(bottom)
	_hand_box = HBoxContainer.new()
	_hand_box.add_theme_constant_override("separation", 10)
	_hand_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bottom.add_child(_hand_box)
	# RESPIN and UNDO stand between the hand and SEND IT, clear of every wheel.
	_sticker_box = VBoxContainer.new()
	_sticker_box.name = "Stickers"
	_sticker_box.alignment = BoxContainer.ALIGNMENT_CENTER
	_sticker_box.add_theme_constant_override("separation", int(STICKER_GAP))
	bottom.add_child(_sticker_box)
	_build_stickers()
	_end_turn_button = DripButton.new("SEND IT", "[%s]" % Settings.key_text(&"end_turn"), DripButton.DRIP_PINK, 50, DripButton.SEND_IT_DRIPS)
	_end_turn_button.name = "SendIt"
	_end_turn_button.tooltip_text = "End the turn: every needle resolves at once (defensive, then offensive, then statuses). The tags show the outcome."
	_end_turn_button.pressed.connect(end_turn)
	bottom.add_child(_end_turn_button)
	_zine_elements.append(_end_turn_button)

	toast = Toast.new()
	toast.name = "Toast"
	add_child(toast)
	inspect_popup = InspectPopup.new()
	inspect_popup.name = "InspectPopup"
	add_child(inspect_popup)
	# The aim line: from the card being aimed to the zone it would play on. Drawn under the
	# wheel views (H24: on top it crossed the HP number and the NEXT plate).
	_aim_line = Control.new()
	_aim_line.name = "AimLine"
	_aim_line.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_aim_line.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_aim_line.draw.connect(_draw_aim_line)
	add_child(_aim_line)
	move_child(_aim_line, root.get_index())
	_aim_hint = Label.new()
	_aim_hint.name = "AimHint"
	_aim_hint.visible = false
	_aim_hint.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_aim_hint.add_theme_color_override("font_color", Palette.CELL_ACID)
	_aim_hint.add_theme_color_override("font_outline_color", Palette.NIGHT_SKY)
	_aim_hint.add_theme_constant_override("outline_size", 6)
	add_child(_aim_hint)
	_refresh_key_hints()


func _connect_view(v: WheelView) -> void:
	v.arrow_pressed.connect(func(ring: int, direction: int) -> void:
		if v.combatant != null:
			_on_view_arrow(v.combatant.id, ring, direction))
	v.arrow_hovered.connect(func(zone: Dictionary) -> void:
		if v.combatant != null and selecting < 0:
			_preview_nudge(v.combatant.id, zone))
	v.zone_clicked.connect(func(zone: Dictionary) -> void:
		if v.combatant != null:
			_on_view_zone(v.combatant.id, zone))
	v.drag_hovered.connect(func(zone: Dictionary, _data: Dictionary) -> void:
		if v.combatant != null:
			_on_view_drag_hover(v.combatant.id, zone))
	v.drag_dropped.connect(func(zone: Dictionary, _data: Dictionary) -> void:
		if v.combatant != null:
			_on_view_drop(v.combatant.id, zone))


func _label(text: String) -> Label:
	var l := Label.new()
	l.text = text
	return l


func _button(text: String, on_pressed: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.pressed.connect(on_pressed)
	return b


func _views() -> Array[WheelView]:
	var out: Array[WheelView] = [_player_view]
	for v in _enemy_views.values():
		out.append(v)
	return out


func _view_of(id: StringName) -> WheelView:
	if engine.has_fight() and id == engine.state().player.id:
		return _player_view
	return _enemy_views.get(id)


## Lays out the right column's free area: the subtitle dock on top (paged so it never
## grows past it), the tutorial under it (GDD 9.2: nothing on a wheel or a tag).
func _relayout() -> void:
	if not is_inside_tree() or _notes_area == null:
		return
	var area := _notes_area.get_global_rect()
	var ts := Settings.text_scale
	var tutoring := tutorial != null and is_instance_valid(tutorial)
	# Shorter subtitle pages while the tutorial needs the room under them.
	var lines := SUBTITLE_LINES
	var dock_h := (SUBTITLE_CHROME_PX + lines * SUBTITLE_LINE_PX) * ts
	while tutoring and lines > 1 and area.size.y - dock_h - NOTE_GAP < TUTORIAL_MIN_HEIGHT:
		lines -= 1
		dock_h = (SUBTITLE_CHROME_PX + lines * SUBTITLE_LINE_PX) * ts
	Dialogue.dock_at(Rect2(area.position, Vector2(area.size.x, dock_h)), lines)
	_place_stickers()
	if engine.has_fight() and absf(_card_scale_for(engine.state().hand.size()) - _hand_scale) > 0.01:
		var had_focus := UiFocus.owner_of(self) != null and _hand_box.is_ancestor_of(UiFocus.owner_of(self))
		_build_hand(engine.state())
		_link_hand_focus()
		if had_focus:
			UiFocus.focus_first(_hand_box, true, _end_turn_button.get_parent())
	if tutorial == null or not is_instance_valid(tutorial):
		return
	var origin := get_global_rect().position
	var top := area.position.y + dock_h + NOTE_GAP
	var bottom := area.end.y
	if bottom - top < TUTORIAL_MIN_HEIGHT:
		top = area.position.y  # no room under the subtitles: the tutorial takes the area
	if bottom - top < TUTORIAL_MIN_HEIGHT:
		return
	tutorial.position = Vector2(area.position.x, top) - origin
	tutorial.fit(Vector2(area.size.x, bottom - top))


## The wheel cards aim at under the hidden card-target toggle (play_card's default).
func _card_target_wheel() -> CombatantState:
	var state := engine.state()
	if state == null:
		return null
	if _card_target_option.selected == 1:
		return state.player
	return state.get_combatant(state.target_id)


## Rewrites every key hint from the current binds and device (GDD 9.5, H19, H20). The hand
## is rebuilt for its hotkeys, so the focused card keeps focus (H21: the first pad press
## used to leave the pad with nothing focused).
func _refresh_key_hints() -> void:
	if not is_instance_valid(_nudge_wheel_option):
		return
	var focused := -1
	var owner := UiFocus.owner_of(self) if is_inside_tree() else null
	if owner != null and owner.get_parent() == _hand_box:
		focused = owner.get_index()
	_nudge_minus_button.text = "-1 %s" % Settings.hint(&"nudge_left")
	_nudge_plus_button.text = "+1 %s" % Settings.hint(&"nudge_right")
	_settings_button.text = "Settings %s" % Settings.hint(&"open_settings")
	(_end_turn_button as DripButton).set_key_hint(Settings.hint(&"end_turn"))
	_sync_stickers()
	_sync_arrow_hints()
	if engine != null and engine.has_fight() and is_inside_tree():
		_build_hand(engine.state())
		_link_hand_focus()
		if focused >= 0:
			var cards := _hand_box.get_children()
			if not cards.is_empty():
				(cards[mini(focused, cards.size() - 1)] as Control).grab_focus()
		_refresh_status()
		_relayout.call_deferred()


func _rebuild_slot_option() -> void:
	var keep := _slot_option.selected
	_slot_option.clear()
	_slot_option.add_item("Slice auto")
	var c := _card_target_wheel()
	if c != null:
		for i in c.wheel.slot_slice_ids.size():
			var slice := engine.content(c.wheel.slot_slice_ids[i]) as SliceData
			_slot_option.add_item("%d %s" % [i, tr(String(Palette.SLICE_NAMES.get(slice.slice_type, "?"))) if slice != null else "?"])
	_slot_option.select(keep if keep >= 0 and keep < _slot_option.item_count else 0)


func _refresh(state: CombatState) -> void:
	var lookup := engine.resolver.lookup
	_refresh_status()
	var operative_name := state.player.display_name
	if engine.netrun != null and engine.netrun.run != null and engine.netrun.run.operative != null:
		operative_name = engine.netrun.run.operative.name
	portrait.caption = operative_name
	if state.player.source_id != &"":
		portrait.placeholder_label = "[%s PORTRAIT]" % String(state.player.source_id).to_upper()
	if engine.netrun != null and engine.netrun.run != null and engine.netrun.run.operative != null:
		# The same face as the operative's dossier (H20 #23).
		portrait.set_operative(engine.netrun.run.operative.class_id, engine.netrun.run.operative.id)
	portrait.glitch = state.player.hp * 4 <= state.player.max_hp
	portrait.tooltip_text = "%s (%s): %d/%d HP." % [operative_name, state.player.display_name, state.player.hp, state.player.max_hp]
	portrait.queue_redraw()
	ram_note.set_ram(state.ram, state.max_ram)
	daemon_row.set_daemons(state.daemon_ids, lookup)
	var heat := RunManager.campaign.heat if RunManager.campaign != null else 0
	var heat_max := engine.resolver.config.heat_max
	heat_poster.set_heat(heat, heat_max, engine.resolver.config.major_heat_levels())
	background.corp_creep = clampf(float(heat) / maxf(1.0, heat_max), 0.0, 1.0)
	_player_view.show_combatant(state.player, state.satellites_of(state.player.id), engine.readouts(state.player), lookup)
	var reveal := int(state.flags.get("reveal_phases", 0)) > 0
	var wanted: Array[StringName] = []
	var any_pending := false
	var target := state.get_combatant(state.target_id)
	for e in state.enemies:
		if e.is_satellite:
			continue
		wanted.append(e.id)
		if not _enemy_views.has(e.id):
			var v := WheelView.new()
			v.size_flags_vertical = Control.SIZE_EXPAND_FILL
			_connect_view(v)
			_enemy_views[e.id] = v
			_enemy_views_box.add_child(v)
		var view: WheelView = _enemy_views[e.id]
		view.highlighted = e.id == state.target_id
		view.targeted_satellite = target.id if target != null and target.is_satellite and target.host_id == e.id else &""
		var lines: Array[String] = []
		if reveal:
			var edata := lookup.get_content(e.source_id) as EnemyData
			for p in engine.resolver.upcoming_phases(state, e):
				var parts := PackedStringArray()
				if not p.pointer_ticks.is_empty():
					parts.append(str(Array(CombatResolver.phase_layout(state, edata, p.pointer_ticks))))
				if p.pointer_behavior == RC.PointerBehavior.ORBIT and p.orbit_ticks_per_turn != 0:
					parts.append(tr("%s/turn") % signed(p.orbit_ticks_per_turn))
				var where := " ".join(parts)
				lines.append("@%d%%: %s %s" % [roundi(p.hp_threshold_pct * 100), RC.PointerBehavior.keys()[p.pointer_behavior], where])
		view.extra_lines = lines
		if not e.wheel.pending_pointer_ticks.is_empty():
			any_pending = true
		view.show_combatant(e, state.satellites_of(e.id), engine.readouts(e), lookup)
	if not any_pending:
		_stop_migrate_flicker()
	for id in _enemy_views.keys():
		if not wanted.has(id):
			_enemy_views[id].queue_free()
			_enemy_views.erase(id)
	_target_option.clear()
	var idx := 0
	for e in state.living_enemies(true):
		_target_option.add_item("%s (%d HP)" % [e.display_name, e.hp])
		_target_option.set_item_metadata(idx, e.id)
		if e.id == state.target_id:
			_target_option.select(idx)
		idx += 1
	_rebuild_slot_option()
	_build_hand(state)
	_end_turn_button.disabled = state.is_over()
	_rewind_button.disabled = not engine.can_rewind()
	_link_hand_focus()
	_nav_focus = false  # the refocus below is automatic, not the player moving focus
	UiFocus.focus_first(_hand_box, true, _end_turn_button.get_parent())
	_respin_button.disabled = state.is_over() or state.ram < engine.resolver.config.respin_ram_cost
	_sync_stickers()
	_sync_arrow_hints()
	selecting = -1
	_options.clear()
	_option_index = -1
	for v in _views():
		v.valid_zones.clear()
		v.hover_zone = {}
		v.show_arrows = not state.is_over()
		v.last_turn = String(_last_turn.get(v.combatant.id, "")) if v.combatant != null else ""
	toast.hide()
	inspect_popup.hide()
	_show_end_turn_preview()


## The status line: turn, free nudges, and on a pad the triggers that pick which wheel and
## ring the nudge buttons drive.
func _refresh_status() -> void:
	if not engine.has_fight():
		return
	var state := engine.state()
	var text := tr("TURN %d · FREE NUDGE %d") % [state.turn, state.free_nudges]
	if state.outcome == CombatState.Outcome.VICTORY:
		text += " · " + tr("VICTORY")
	elif state.outcome == CombatState.Outcome.DEFEAT:
		text += " · " + tr("DEFEAT")
	else:
		# One key pair nudges; the switches say what they switch to (H23: "YOURS [W] OUTER
		# [R]" read as a second nudge pair, and OUTER showed on wheels with one ring).
		var mine := _nudge_wheel_option.selected == 0
		var inner := _nudge_ring_option.selected == 1
		text += tr(" · %s/%s NUDGE %s%s") % [Settings.key_text(&"nudge_left"), Settings.key_text(&"nudge_right"), tr("YOUR WHEEL") if mine else tr("THE TARGET"), tr(" (INNER RING)") if inner else ""]
		text += tr(" · %s: NUDGE %s") % [Settings.key_text(&"toggle_nudge_wheel"), tr("THE TARGET") if mine else tr("YOUR WHEEL")]
		var wheel := state.get_combatant(_selected_nudge_wheel())
		if wheel != null and wheel.wheel.has_inner_ring():
			text += tr(" · %s: %s RING") % [Settings.key_text(&"toggle_ring"), tr("OUTER") if inner else tr("INNER")]
	_status.text = text
	_fit_status()


## The status line's font: its themed size, smaller until the line fits its width.
func _fit_status() -> void:
	if _status == null or _status.size.x <= 0.0 or _fitting_status:
		return
	# Changing the font resizes the label, which calls this again: once is enough.
	_fitting_status = true
	_status.remove_theme_font_size_override("font_size")
	var fs := _status.get_theme_font_size("font_size")
	var font := _status.get_theme_font("font")
	while fs > STATUS_MIN_FONT and font.get_string_size(_status.text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > _status.size.x:
		fs -= 1
	_status.add_theme_font_size_override("font_size", fs)
	_fitting_status = false


## The smallest the status line's font shrinks to (px).
const STATUS_MIN_FONT := 10
var _fitting_status := false


func _build_hand(state: CombatState) -> void:
	var lookup := engine.resolver.lookup
	for child in _hand_box.get_children():
		_hand_box.remove_child(child)
		child.queue_free()
	var s := _card_scale_for(state.hand.size())
	_hand_scale = s
	for i in state.hand.size():
		var card := lookup.get_content(state.hand[i]) as CardData
		var c := ZineCard.new(TextDb.t(card, "display_name"), card.ram_cost, TextDb.t(card, "description"), i).scaled(s).with_card(card)
		if Settings.pad_active:
			c.hotkey = ""
			c.pad_hint = Settings.key_text(&"ui_accept")
		c.drag_index = i
		c.disabled = state.is_over() or state.ram < card.ram_cost
		var several := CardTargeting.options(engine.resolver, state, i).size() > 1
		c.tooltip_text = "%s\n%s" % [Codex.describe(card), "Drag it onto a glowing target, or click it and then the target." if several else "Click to play."]
		var index := i
		c.pressed.connect(func() -> void: select_card(index))
		c.mouse_entered.connect(func() -> void:
			if selecting < 0:
				_preview_card(index))
		c.focus_entered.connect(func() -> void:
			if _nav_focus and selecting < 0:
				_preview_card(index))
		c.mouse_exited.connect(func() -> void:
			if selecting < 0:
				_clear_ghost()
				_show_end_turn_preview())
		_hand_box.add_child(c)


## Card scale: the text scale, shrunk when the hand would not fit beside SEND IT.
func _card_scale_for(count: int) -> float:
	var n := maxi(1, count)
	var sep := float(_hand_box.get_theme_constant("separation"))
	var width := size.x if size.x > 0.0 else get_viewport_rect().size.x
	var room := width - _end_turn_button.get_combined_minimum_size().x - _sticker_box.get_combined_minimum_size().x - sep * 3.0
	var fit := (room - sep * (n - 1)) / n / ZineCard.STICKER_SIZE.x
	return clampf(minf(Settings.text_scale, fit), MIN_CARD_SCALE, Settings.TEXT_SCALE_MAX)


func _selected_nudge_wheel() -> StringName:
	if _nudge_wheel_option.selected == 1 and engine.state().target_id != &"":
		return engine.state().target_id
	return &"player"


func _card_action(hand_index: int) -> CombatAction:
	var state := engine.state()
	var wheel_id: StringName = &"player" if _card_target_option.selected == 1 else state.target_id
	var a := CombatAction.play_card(hand_index, wheel_id, selected_slot())
	a.ring = RC.RingScope.INNER if _nudge_ring_option.selected == 1 else RC.RingScope.OUTER
	a.direction = selected_direction()
	return a


func _describe_slot(c: CombatantState, slot: int) -> String:
	var lookup := engine.resolver.lookup
	if slot < 0:
		var lines := PackedStringArray([Codex.describe(lookup.get_content(c.source_id))])
		if c.wheel.hub_id != &"":
			lines.append(Codex.describe(lookup.get_content(c.wheel.hub_id)))
		if c.wheel.has_inner_ring():
			for id in c.wheel.ring_segment_ids:
				lines.append(Codex.describe(lookup.get_content(id)))
		return "\n".join(lines)
	var lines := PackedStringArray(["%s slot %d" % [c.display_name, slot]])
	lines.append(Codex.describe(lookup.get_content(c.wheel.slot_slice_ids[slot])))
	if c.wheel.slot_firmware_ids[slot] != &"":
		lines.append(Codex.describe(lookup.get_content(c.wheel.slot_firmware_ids[slot])))
	var status: int = c.wheel.slice_statuses[slot]
	if status != RC.Status.NONE:
		lines.append(Codex.status_text(status))
	var guard := engine.state().satellite_at(c.id, slot)
	if guard != null:
		lines.append("Guarded by %s (%d HP): it takes hits aimed at this slice." % [guard.display_name, guard.hp])
	return "\n".join(lines)


func _clear_ghost() -> void:
	_player_view.set_ghost(null)
	for v in _enemy_views.values():
		v.set_ghost(null)


# --- Previews: the tags, the HP arcs, the RAM bar ------------------------------------

## Card hover (not aiming yet): the card's result with its default aim.
func _preview_card(hand_index: int) -> void:
	if not engine.has_fight() or hand_index >= engine.state().hand.size():
		return
	var options := CardTargeting.options(engine.resolver, engine.state(), hand_index)
	var action := _card_action(hand_index)
	for a in options:
		if a.wheel_id == engine.state().target_id and a.direction == 1:
			action = a
			break
	if not options.is_empty() and engine.validate(action) != "":
		action = options[0]
	_preview_action(action)


## A nudge arrow under the mouse: the nudge's result.
func _preview_nudge(wheel_id: StringName, zone: Dictionary) -> void:
	if zone.is_empty():
		_clear_ghost()
		_show_end_turn_preview()
		return
	_preview_action(CombatAction.nudge(wheel_id, int(zone["direction"]), int(zone["ring"])))


## Shows what `action` then the End Turn resolve would do: ghost arcs where wheels move,
## the tags and chips from the resolved state, the RAM change. Random effects show odds on
## the wheel they roll (GDD 2.10).
func _preview_action(action: CombatAction) -> void:
	var state := engine.state()
	var result := engine.preview(action)
	preview_note.clear()
	if result == null or not result.ok():
		var reason := result.error if result != null else "No fight."
		preview_note.append("[color=#c05000]%s[/color]" % reason)
		_show_end_turn_preview()
		return
	for e in result.events:
		if e.has("text"):
			preview_note.append(String(e["text"]))
	_clear_ghost()
	var card := engine.content(state.hand[action.hand_index]) as CardData if action.type == CombatAction.Type.PLAY_CARD else null
	if card != null and CardTargeting.is_random(card):
		var target := engine.resolver.card_target(state, card, action)
		_show_end_turn_preview()
		ram_note.set_pending(-card.ram_cost)
		var host := (target.host_id if target.is_satellite else target.id) if target != null else &""
		var v := _view_of(host)
		if target != null and v != null:
			var non_miss := false
			for e in card.effects:
				if e != null and e.slice_pick == RC.SlicePick.RANDOM_NON_MISS:
					non_miss = true
			var chips: Array = [{"text": tr("RANDOM: ODDS"), "color": Palette.INK, "ink": Palette.PAPER}]
			chips.append_array(_odds_chips(target, non_miss))
			v.intent = {"type": -1, "text": tr("%s rolls") % TextDb.t(card, "display_name"), "chips": chips,
				"tooltip": "A random effect: the roll is hidden until you play it. %s" % odds_text(target, non_miss)}
			v.queue_redraw()
		preview_note.append("[i]random effect: the roll is hidden until you play it[/i]")
		return
	var after := result.state
	if after.player.wheel.rotation != state.player.wheel.rotation or after.player.wheel.inner_rotation != state.player.wheel.inner_rotation:
		_player_view.set_ghost(after.player.wheel.rotation, after.player.wheel.inner_rotation)
	for e in after.living_enemies(false):
		var before := state.get_combatant(e.id)
		if before != null and e.wheel.rotation != before.wheel.rotation and _enemy_views.has(e.id):
			_enemy_views[e.id].set_ghost(e.wheel.rotation)
	var turn := engine.preview_turn_after(action)
	if turn == null:
		_show_outcome(after, after, result.events)
		return
	var events: Array[Dictionary] = result.events.duplicate()
	events.append_array(turn.events)
	_show_outcome(after, turn.state, events)
	_mark_preview_source(action, card)


## The wheel a hovered card or nudge acts on says so first on its tag ("IF JOLT"), so the
## changes read as that play's (H24: a hovered card seemed to spin the enemy onto
## CRITICAL by itself).
func _mark_preview_source(action: CombatAction, card: CardData) -> void:
	var target := engine.state().get_combatant(action.wheel_id)
	var host := (target.host_id if target != null and target.is_satellite else action.wheel_id)
	var v := _view_of(host)
	if v == null or v.intent.is_empty():
		return
	var what := TextDb.t(card, "display_name").to_upper() if card != null else tr("NUDGE")
	var chips: Array = (v.intent.get("chips", []) as Array).duplicate()
	chips.push_front({"text": tr("IF %s") % what, "color": CHIP_RUN, "ink": Palette.INK})
	v.intent["chips"] = chips
	v.intent["tooltip"] = _chips_tooltip(chips)
	v.queue_redraw()


func _show_respin_odds() -> void:
	if not engine.has_fight():
		return
	_show_end_turn_preview()
	var cost := engine.resolver.config.respin_ram_cost
	ram_note.set_pending(-cost)
	var chips: Array = [{"text": tr("RESPIN: ODDS"), "color": Palette.INK, "ink": Palette.PAPER}]
	chips.append_array(_odds_chips(engine.state().player))
	_player_view.intent = {"type": -1, "text": tr("Respin for %d RAM") % cost, "chips": chips,
		"tooltip": "Respin your wheel for %d RAM: a random result (sets a checkpoint). %s" % [cost, odds_text(engine.state().player)]}
	_player_view.queue_redraw()
	preview_note.clear()
	preview_note.append("Respin your wheel for %d RAM (a random event: sets a checkpoint)." % cost)
	preview_note.append(odds_text(engine.state().player))


## The End Turn preview as it stands (GDD 2.10): what every needle lands on and the full
## outcome, on the tags, HP arcs and the RAM bar. The hidden note keeps the text.
func _show_end_turn_preview() -> void:
	if not engine.has_fight():
		return
	var state := engine.state()
	preview_note.clear()
	if state.is_over():
		preview_note.append("Combat over.")
		for v in _views():
			v.intent = {}
			v.outcome = {}
			v.queue_redraw()
		ram_note.set_pending(0)
		return
	var result := engine.preview_end_turn()
	for e in result.events:
		var t: String = e.get("type", "")
		if t == "status" and e.get("random", false):
			var owner := state.get_combatant(e["target"])
			preview_note.append("%s gets %s on a random non-Miss slice (%s)." % [owner.display_name, RC.Status.keys()[e["status"]], odds_text(owner, true)])
		elif e.has("text") and t != "pass":
			preview_note.append(String(e["text"]))
	var after := result.state
	var summary := PackedStringArray()
	for e in after.enemies:
		if not e.is_satellite or e.is_alive():
			summary.append("%s %d HP" % [e.display_name, e.hp])
	preview_note.append("[b]=> You %d HP | %s[/b]" % [after.player.hp, ", ".join(summary)])
	_show_outcome(state, after, result.events)


## Puts an outcome on screen: each spinner's tag (what its needles land on in `landing`,
## then chips for every change between now and `resolved`), the HP and status ghosts, and
## the RAM bar's pending change.
func _show_outcome(landing: CombatState, resolved: CombatState, events: Array[Dictionary]) -> void:
	var state := engine.state()
	var o := CombatOutcome.between(state, resolved, events)
	# Random slice picks during the resolve (DOSE, Citations, Solar Flares) show odds, not
	# the slot the roll picked (GDD 2.10).
	var random_picks := {}
	for e in events:
		if String(e.get("type", "")) == "status" and bool(e.get("random", false)):
			random_picks[StringName(String(e.get("target", "")))] = true
	var views := {state.player.id: _player_view}
	for id in _enemy_views:
		views[id] = _enemy_views[id]
	for id in views:
		var c := state.get_combatant(id)
		var view: WheelView = views[id]
		if c == null or not c.is_alive():
			view.intent = {}
			view.outcome = {}
			view.queue_redraw()
			continue
		var lc := landing.get_combatant(id)
		var title := _landing_title(landing, lc if lc != null else c)
		var chips := _chips_for(o, id, state)
		var sats := {}
		var landings := {}
		for sat in state.satellites_of(id):
			sats[sat.id] = o.of(sat.id)
			var ls := landing.get_combatant(sat.id)
			var rs := engine.resolver.pointer_readouts(landing, ls if ls != null else sat)
			if not rs.is_empty():
				var sl: SliceData = rs[0]["slice"]
				landings[sat.id] = {"type": sl.slice_type, "tier": int(rs[0]["tier"]),
					"text": "%s (%s)" % [tr(String(Palette.SLICE_WORDS.get(sl.slice_type, "?"))), tr(String(Palette.TIER_WORDS.get(int(rs[0]["tier"]), "")))]}
		view.satellite_landings = landings
		var d := o.of(id)
		var shown_statuses: Array = d.get("statuses", [])
		if random_picks.has(id):
			shown_statuses = []
			chips = chips.filter(func(ch: Dictionary) -> bool: return not bool(ch.get("status", false)))
			chips.append({"text": "? " + tr("RANDOM STATUS"), "color": CHIP_STATUS, "ink": Palette.INK})
			chips.append_array(_odds_chips(c, true))
		view.outcome = {"hp_after": int(d.get("hp_after", c.hp)), "alive_after": bool(d.get("alive_after", true)),
			"statuses": shown_statuses, "satellites": sats}
		view.intent = {"type": title["type"], "tier": title.get("tier", -1), "text": title["text"], "chips": chips, "tooltip": _chips_tooltip(chips)}
		view.queue_redraw()
	ram_note.set_pending(o.ram_delta)


## The tag's title: the slice each needle lands on and how well.
func _landing_title(s: CombatState, c: CombatantState) -> Dictionary:
	var parts := PackedStringArray()
	var type := -1
	var tier := -1
	var rs := engine.resolver.pointer_readouts(s, c)
	for r in rs:
		var slice: SliceData = r["slice"]
		if type < 0:
			type = slice.slice_type
			tier = int(r["tier"])
		if rs.size() <= 1:
			parts.append("%s · %s" % [tr(String(Palette.SLICE_WORDS.get(slice.slice_type, "?"))), tr(String(Palette.TIER_WORDS.get(r["tier"], "")))])
		elif rs.size() == 2:
			parts.append("%s %s" % [tr(String(Palette.SLICE_WORDS.get(slice.slice_type, "?"))), tr(String(Palette.TIER_NAMES.get(r["tier"], ""))).to_lower()])
		else:
			parts.append("%s·%s" % [tr(String(Palette.SLICE_NAMES.get(slice.slice_type, "?"))), tr(String(Palette.TIER_NAMES.get(r["tier"], ""))).left(1)])
	return {"type": type, "tier": tier if rs.size() == 1 else -1, "text": " + ".join(parts)}


## Result chips for one combatant (and, on the operative, the run-wide results).
func _chips_for(o: CombatOutcome, id: StringName, state: CombatState) -> Array:
	var chips: Array = []
	var d := o.of(id)
	if d.is_empty():
		return chips
	# Who takes the hits: "HITS YOU 14" on an enemy's tag, "HITS <NAME> 12" on yours.
	var to: Dictionary = d.get("dealt_to", {})
	for tgt in to:
		var victim := state.get_combatant(StringName(String(tgt)))
		var who := tr("YOU") if victim != null and victim.is_player else (_name_of(victim).to_upper() if victim != null else "?")
		chips.append({"text": tr("HITS %s %d") % [who, int(to[tgt])], "color": CHIP_HIT, "ink": Palette.INK})
	if to.is_empty() and int(d["dealt"]) > 0:
		chips.append({"text": tr("HITS %d") % int(d["dealt"]), "color": CHIP_HIT, "ink": Palette.INK})
	var dhp := int(d["hp_after"]) - int(d["hp_before"])
	if dhp < 0:
		# Said as damage taken (H23: "−11 HP" under the player's DEFEND read as DEFEND costing
		# 11 HP).
		var victim_self := state.get_combatant(id)
		var taker := tr("YOU TAKE") if victim_self != null and victim_self.is_player else tr("TAKES")
		chips.append({"text": tr("%s %d HP") % [taker, -dhp], "color": CHIP_LOSS, "ink": Palette.PAPER})
	elif dhp > 0:
		chips.append({"text": tr("+%d HP") % dhp, "color": CHIP_GAIN, "ink": Palette.INK})
	# What block and shield soak, beside the loss (H24: 14 hit, 11 taken read as a sum to do).
	if int(d.get("soaked", 0)) > 0:
		chips.append({"text": tr("%d BLOCKED") % int(d["soaked"]), "color": CHIP_GUARD, "ink": Palette.INK})
	for key in ["block", "shield"]:
		var delta := int(d[key + "_after"]) - int(d[key + "_before"])
		if delta != 0:
			chips.append({"text": "%s %s" % [signed(delta), tr("BLOCK") if key == "block" else tr("SHIELD")], "color": CHIP_GUARD, "ink": Palette.INK})
	var ev := int(d["evade_after"]) - int(d["evade_before"])
	if ev != 0:
		chips.append({"text": tr("%s EVADE") % signed(ev), "color": CHIP_GUARD, "ink": Palette.INK})
	if int(d["resistance_after"]) != int(d["resistance_before"]):
		chips.append({"text": tr("RESIST %d→%d") % [int(d["resistance_before"]), int(d["resistance_after"])], "color": CHIP_RESIST, "ink": Palette.INK})
	if bool(d["breached"]):
		chips.append({"text": tr("HUB BREACH"), "color": CHIP_RESIST, "ink": Palette.INK})
	for st in d["statuses"]:
		var after := int(st["after"])
		var tag: String = tr(String(Palette.STATUS_WORDS.get(after, ""))) if after != RC.Status.NONE else tr("CLEARS %s") % tr(String(Palette.STATUS_WORDS.get(int(st["before"]), "")))
		chips.append({"text": "%s %s" % [Palette.STATUS_GLYPHS.get(after, "×"), tag], "color": CHIP_STATUS, "ink": Palette.INK, "status": true})
	if bool(d["alive_before"]) and not bool(d["alive_after"]):
		chips.append({"text": tr("DOWN"), "color": CHIP_LOSS, "ink": Palette.PAPER})
	if int(d.get("phase_after", 0)) != int(d.get("phase_before", 0)):
		chips.append({"text": tr("PHASE %d") % (int(d["phase_after"]) + 1), "color": CHIP_RESIST, "ink": Palette.INK})
	if int(d.get("pointers_after", 0)) > int(d.get("pointers_before", 0)):
		chips.append({"text": tr("+%d NEEDLE") % (int(d["pointers_after"]) - int(d["pointers_before"])), "color": CHIP_RESIST, "ink": Palette.INK})
	if bool(d.get("slices_changed", false)):
		chips.append({"text": tr("NEW SLICES"), "color": CHIP_RESIST, "ink": Palette.INK})
	# Satellites docked here: what they deal and take.
	for sat in state.satellites_of(id):
		var sd := o.of(sat.id)
		if sd.is_empty():
			continue
		var name := _name_of(sat).to_lower()
		if int(sd["dealt"]) > 0:
			chips.append({"text": tr("%s HITS %d") % [name, int(sd["dealt"])], "color": CHIP_HIT, "ink": Palette.INK})
		if bool(sd["alive_before"]) and not bool(sd["alive_after"]):
			chips.append({"text": tr("%s DOWN") % name, "color": CHIP_LOSS, "ink": Palette.PAPER})
		elif int(sd["hp_after"]) != int(sd["hp_before"]):
			var shp := int(sd["hp_after"]) - int(sd["hp_before"])
			chips.append({"text": tr("%s %s HP") % [name, signed(shp)], "color": CHIP_LOSS if shp < 0 else CHIP_GAIN, "ink": Palette.PAPER if shp < 0 else Palette.INK})
		for key in ["block", "shield"]:
			var sdelta := int(sd[key + "_after"]) - int(sd[key + "_before"])
			if sdelta != 0:
				chips.append({"text": "%s %s %s" % [name, signed(sdelta), tr("BLOCK") if key == "block" else tr("SHIELD")], "color": CHIP_GUARD, "ink": Palette.INK})
		for st in sd["statuses"]:
			var sw: String = tr(String(Palette.STATUS_WORDS.get(int(st["after"]), ""))) if int(st["after"]) != RC.Status.NONE else tr("CLEARED")
			chips.append({"text": "%s %s %s" % [name, Palette.STATUS_GLYPHS.get(int(st["after"]), "×"), sw], "color": CHIP_STATUS, "ink": Palette.INK, "status": true})
		if int(sd.get("dock_after", -1)) != int(sd.get("dock_before", -1)):
			chips.append({"text": tr("%s MOVES") % name, "color": CHIP_RESIST, "ink": Palette.INK})
	if id == state.player.id:
		if o.ram_delta != 0:
			chips.append({"text": tr("RAM %s") % signed(o.ram_delta), "color": CHIP_GUARD, "ink": Palette.INK})
		if o.cards_drawn > 0:
			chips.append({"text": tr("DRAW %d") % o.cards_drawn, "color": CHIP_RUN, "ink": Palette.INK})
		if o.heat != 0:
			# Scaled one change at a time, as the netrun applies them.
			var heat := 0
			for h in o.heat_events:
				heat += HeatRules.scaled_delta(RunManager.campaign, h, RunManager.config()) if RunManager.campaign != null else h
			chips.append({"text": tr("HEAT %s") % signed(heat), "color": heat_poster.hot_color, "ink": Palette.INK})
		if o.cycles != 0:
			chips.append({"text": tr("CYCLES %s") % signed(o.cycles), "color": CHIP_RUN, "ink": Palette.INK})
		if o.schematics != 0:
			chips.append({"text": tr("SCHEMATICS %s") % signed(o.schematics), "color": CHIP_RUN, "ink": Palette.INK})
		if o.free_nudges_next_turn != 0:
			chips.append({"text": tr("FREE NUDGE %s NEXT") % signed(o.free_nudges_next_turn), "color": CHIP_RUN, "ink": Palette.INK})
		if o.damage_bonus_delta != 0:
			chips.append({"text": tr("DAMAGE %s") % signed(o.damage_bonus_delta), "color": CHIP_RUN, "ink": Palette.INK})
		if o.drones_gained > 0:
			chips.append({"text": tr("+%d DRONE") % o.drones_gained, "color": CHIP_STATUS, "ink": Palette.INK})
		if o.double_nudge_next:
			chips.append({"text": tr("2× NUDGE CARDS NEXT"), "color": CHIP_RUN, "ink": Palette.INK})
		if o.outcome == CombatState.Outcome.VICTORY:
			chips.append({"text": tr("VICTORY"), "color": CHIP_GAIN, "ink": Palette.INK})
		elif o.outcome == CombatState.Outcome.DEFEAT:
			chips.append({"text": tr("DEFEAT"), "color": CHIP_LOSS, "ink": Palette.PAPER})
	return chips


## A combatant's name through TextDb (translations), falling back to its runtime name.
func _name_of(c: CombatantState) -> String:
	var data: Resource = engine.content(c.source_id) if c.source_id != &"" and engine.resolver.lookup.has(c.source_id) else null
	# Generated combatants (REBEL_CELL Mirrors) keep their runtime names.
	if data == null or not ("display_name" in data) or String(data.display_name) != c.display_name:
		return c.display_name
	return TextDb.t(data, "display_name")


## A signed whole number ("+3", "-2", "0") for translated "%s" keys: Godot's
## pseudolocalisation doesn't skip "%+d" placeholders (H24: they broke the scramble).
static func signed(n: int) -> String:
	return "+%d" % n if n > 0 else "%d" % n


static func _chips_tooltip(chips: Array) -> String:
	if chips.is_empty():
		return "What this wheel's needles land on. Nothing else changes this turn."
	var parts := PackedStringArray()
	for c in chips:
		parts.append(String(c["text"]))
	return "When you SEND IT: " + ", ".join(parts) + ".\nHITS = damage this wheel deals and to whom; HP = health change; BLOCK / SHIELD soak damage; glyphs = statuses on a slice (dashed ring on the wheel).\nThe dots: ●○○ half power (a needle near a slice's edge), ●●○ good aim, ●●● perfect aim (dead centre)."


# --- Stickers and hints ---------------------------------------------------------------

## Stickers by the player spinner: RESPIN and UNDO (nudges are the arrows on every
## wheel; cards are aimed by dragging).
func _build_stickers() -> void:
	var specs := [
		["respin", "RESPIN", Palette.STICKER_PINK, 3.0, respin],
		["undo", "UNDO", Palette.NOTE_PAPER, -3.0, rewind],
	]
	for sp in specs:
		var b := StickerButton.new(sp[1], sp[2], sp[3])
		b.pre_translated = true  # labels come from _sticker_text (translated there)
		b.drawn_icon = String(sp[0])
		b.name = "Sticker_" + String(sp[0])
		b.pressed.connect(sp[4])
		_sticker_box.add_child(b)
		_stickers[sp[0]] = b
	_respin_button = _stickers["respin"]
	_rewind_button = _stickers["undo"]
	_respin_button.mouse_entered.connect(_show_respin_odds)
	_respin_button.focus_entered.connect(func() -> void:
		if _nav_focus:
			_show_respin_odds())
	_respin_button.mouse_exited.connect(_show_end_turn_preview)
	_rewind_button.tooltip_text = "Undo back to the last random event (free, unlimited this turn)."


## Sticker label with its bound key (the action each sticker runs).
const STICKER_ACTIONS := {"respin": &"respin", "undo": &"rewind"}


func _sticker_text(key: String, label: String) -> String:
	var h := Settings.hint(STICKER_ACTIONS[key])
	return label if h == "" else "%s %s" % [label, h]


## The stickers sit in their box beside SEND IT (the box lays them out).
func _place_stickers() -> void:
	_sticker_box.queue_sort()


func _sync_stickers() -> void:
	if _stickers.is_empty():
		return
	var cost := engine.resolver.config.respin_ram_cost if engine != null and engine.has_fight() else 0
	(_stickers["respin"] as StickerButton).set_label(_sticker_text("respin", tr("RESPIN %d RAM") % cost if cost > 0 else tr("RESPIN")))
	(_stickers["undo"] as StickerButton).set_label(_sticker_text("undo", tr("UNDO")))
	_respin_button.tooltip_text = "Respin your wheel for %d RAM: a random result (sets a checkpoint)." % cost
	for key in _stickers:
		(_stickers[key] as StickerButton).refit()
	_place_stickers()


## The nudge keys drive one wheel (W switches own / target) and one ring (R): its arrows
## carry the key hints.
func _sync_arrow_hints() -> void:
	if engine == null or not engine.has_fight():
		return
	var driven := _selected_nudge_wheel()
	var ring := RC.RingScope.INNER if _nudge_ring_option.selected == 1 else RC.RingScope.OUTER
	for v in _views():
		var mine := v.combatant != null and ((driven == &"player" and v == _player_view) or v.combatant.id == driven)
		v.arrow_hints = {-1: Settings.hint(&"nudge_left"), 1: Settings.hint(&"nudge_right")} if mine else {}
		v.key_ring = ring
		v.queue_redraw()
