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
## Motion entry for the seconds between resolution passes in the log playback (0 under
## headless / reduce-effects); timings live in content/config/ui_motion.tres.
const PASS_MOTION := &"resolve_pass"
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
## ART-0 C (text scale 2.0): 130, not 140: at 2.0 a one-line subtitle dock left 138 px
## under it and the tutorial jumped over the subtitles (it pages its text in what it gets).
const TUTORIAL_MIN_HEIGHT := 130.0
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
## ANIM-R2 E4a: a hit's projectile is coloured by its side, never by the slice: the
## operative's (and its drones') hits in acid, the enemies' (and their satellites') in red.
const PLAYER_HIT_COLOR := Palette.CELL_ACID
const ENEMY_HIT_COLOR := CHIP_LOSS
## Smallest hand card scale when many cards must fit the row.
const MIN_CARD_SCALE := 0.6
## ART-1 1A: the most of the screen's height a hand card takes (the narrower Anton stickers
## freed width, the cards grew with it and the wheels shrank under BIG_TEXT_RADIUS_KEEP).
const HAND_HEIGHT_SHARE := 0.24

@export var auto_start: bool = true

@onready var engine: CombatEngine = $CombatEngine

var background: WireframeBackground
var portrait: Polaroid
var heat_poster: HeatPoster
## ART-2 2C: Heat on the backdrop (ART_BIBLE v2 §3.15 H1).
var heat_city: HeatCity
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
## ANIM-R3 A6h: the next step's action once the fight is over ("" label = none shown).
var _continue_button: Button
var _continue_label: String = ""
## The fight is over and the player chose to go on (the netrun moves to the next step).
signal continue_requested
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
	# ANIM-R6 A9: a fight left while its outcome waits for the replay lands it now (the netrun's
	# top bar and its DISPATCH line wait for `outcome_landed`). Nothing of this scene is
	# redrawn: it is leaving.
	if _outcome_held:
		_outcome_held = false
		outcome_landed.emit()
	Dialogue.dock_bottom()
	_restore_time_scale()


func _ready() -> void:
	UiTheme.apply(self)
	MotionSkip.register(self)  # ANIM-R5: the replay completes with every other motion
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
	skip_motion()
	AudioDirector.play_sfx("stamp")
	(_end_turn_button as DripButton).press_motion()
	var before := engine.state().duplicate_state() if engine.has_fight() else null
	_pending_last_turn = before
	_hold_slot = -1
	_pending_discard = _capture_hand() if Motion.animating() and engine.has_fight() else []
	_held_tags.clear()
	if Motion.animating() and engine.has_fight():
		# ANIM-R3 A6b: the forecast SEND IT carries out (never a hovered card's) stays up
		# through the replay, its lines ticked as they happen.
		_show_end_turn_preview()
		for v in _views():
			if v.combatant != null and not v.intent.is_empty():
				_held_tags[v.combatant.id] = v.intent.duplicate(true)
	if not engine.submit(CombatAction.end_turn()):
		_pending_discard = []
		_held_tags.clear()


## State before the SEND IT being resolved (for the last-turn lines).
var _pending_last_turn: CombatState = null
## ANIM-R1: the forecast waits while a SEND IT replays, and the status line shows the
## turn that was played (-1 = the state's turn).
var _hold_forecast: bool = false
## ANIM-R5 combat 1: the fight is over but its replay has not landed the outcome yet (VICTORY
## / DEFEAT): the status word, the next-step button, the Heat poster and the run's top bar
## (`outcome_landed`) wait for it.
var _outcome_held: bool = false
## Emitted when the fight's outcome lands on screen (the replay's end beat, a skip, or at
## once without motion); the netrun then moves its top bar on.
signal outcome_landed
var _shown_turn: int = -1
## Last-turn line per combatant id (kept until the player acts).
var _last_turn: Dictionary = {}
## ANIM-R3 A6f / A6j: the last turn's icon numbers and plate tooltips per wheel id.
var _last_icons: Dictionary = {}
var _last_tips: Dictionary = {}


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


## ANIM-R3 A6f: what the last SEND IT did to each wheel as numbers, for the icon row under
## its HP (ANIM-R4 C6c: sword 6 − shield 5 = 1): {id: {hit (the raw total of the hits aimed
## at it), soaked (what its block and shield took), evaded (what it evaded), hp (its HP
## change in the resolve), dealt (the HP the hits took)}}. Hits on its satellites and drones
## are theirs, not its.
static func last_turn_icons(before: CombatState, events: Array[Dictionary]) -> Dictionary:
	var out := {}
	var wheels: Array[CombatantState] = [before.player]
	for c in before.enemies:
		if not c.is_satellite:
			wheels.append(c)
	for c in wheels:
		out[c.id] = {"hit": 0, "soaked": 0, "evaded": 0, "hp": 0, "dealt": 0}
	for e in events:
		var t := String(e.get("type", ""))
		if t == "turn_start":
			break
		var id := StringName(String(e.get("target", "")))
		if not out.has(id):
			continue
		var d: Dictionary = out[id]
		match t:
			"damage":
				d["hit"] = int(d["hit"]) + int(e.get("amount", 0))
				d["soaked"] = int(d["soaked"]) + int(e.get("blocked", 0)) + int(e.get("shielded", 0))
				d["hp"] = int(d["hp"]) - int(e.get("hp_damage", 0))
				d["dealt"] = int(d["dealt"]) + int(e.get("hp_damage", 0))
			"evaded":
				d["hit"] = int(d["hit"]) + int(e.get("amount", 0))
				d["evaded"] = int(d["evaded"]) + int(e.get("amount", 0))
			"corrupted":
				d["hp"] = int(d["hp"]) - int(e.get("amount", 0))
			"heal":
				d["hp"] = int(d["hp"]) + int(e.get("amount", 0))
	return out


## ANIM-R3 A6j: the LAST TURN plate's tooltip per wheel: its line, then what each status it
## got does (GOT CORRUPTED said nothing about corruption).
static func last_turn_tips(lines: Dictionary, events: Array[Dictionary]) -> Dictionary:
	var got := {}
	for e in events:
		if String(e.get("type", "")) == "status":
			var id := StringName(String(e.get("target", "")))
			var list: Array = got.get(id, [])
			if not list.has(int(e.get("status", 0))):
				list.append(int(e.get("status", 0)))
			got[id] = list
	var out := {}
	for id in lines:
		var parts := PackedStringArray([String(lines[id]), TranslationServer.translate("What the last SEND IT did to this wheel; the icons: hits aimed at it -> what its guard took = its HP change.")])
		for st in got.get(id, []):
			parts.append(Codex.status_text(int(st)))
		out[id] = "\n".join(parts)
	return out


func rewind() -> void:
	cancel_selection()
	skip_motion()
	if engine.has_fight() and not engine.can_rewind():
		show_undo_block()
		return
	_rewind_from = engine.state().duplicate_state() if Motion.animating() and engine.has_fight() else null
	var ok := engine.rewind()
	_rewind_from = null
	if ok and tutorial != null and is_instance_valid(tutorial):
		var ev: Array[Dictionary] = [{"type": "rewind"}]
		tutorial.on_events(ev)


## ART-0 D12 (DECISIONS "Designer rulings: names for M14"): UNDO's words, and the block when there
## is nothing to undo since the last random event.
const UNDO_TIP := "Undo back to the last random event (free, unlimited this turn)." # TR
const UNDO_BLOCKED := "UNDO is blocked: a random event came since (a respin, a random pick)." # TR


## UNDO's tooltip: what it does, or why it is blocked now.
func _sync_undo_tip() -> void:
	if _rewind_button == null:
		return
	var blocked := engine == null or not engine.has_fight() or not engine.can_rewind()
	shown_tip(_rewind_button, tr(UNDO_BLOCKED) if blocked else tr(UNDO_TIP))


## ART-0 D12: an undo with nothing to undo shows its block on the UNDO sticker itself (its
## refusal note sits over it), not in the notes column.
func show_undo_block() -> void:
	if _rewind_button == null:
		return
	var r := _rewind_button.get_global_rect()
	toast.show_text(tr(UNDO_BLOCKED), Vector2(r.get_center().x, r.position.y - TOAST_GAP), _toast_spot().size.x)
	AudioDirector.play_sfx("click")


## Keyboard / pad nudge: the wheel and ring the W and R toggles chose.
func nudge(direction: int) -> void:
	var ring := RC.RingScope.INNER if _nudge_ring_option.selected == 1 else RC.RingScope.OUTER
	nudge_wheel(_selected_nudge_wheel(), direction, ring)


## A nudge arrow: `direction` +1 turns the wheel clockwise, -1 anticlockwise.
func nudge_wheel(wheel_id: StringName, direction: int, ring: int = RC.RingScope.OUTER) -> void:
	_submit(CombatAction.nudge(wheel_id, direction, ring))


## The RAM respin of your own wheel (GDD 2.5, 11.3).
func respin() -> void:
	cancel_selection()
	if not engine.has_fight():
		return
	var before: String = _landing_title(engine.state(), engine.state().player)["text"]
	var ram_before := engine.state().ram
	_submit(CombatAction.respin())
	var spent := ram_before - engine.state().ram
	if spent > 0 and fx_layer != null:
		# ART-2 2C: respin v3, the spent chips crack into cyan bits to the hub; RESPIN.
		fx_layer.respin_bits(CombatBeatFx.ram_pips(ram_note, engine.state().ram, ram_before), _player_view.global_center(), tr("RESPIN"))
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
	_submit(_card_action(hand_index))


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
		_acting = _card_action(hand_index)
		_on_action_refused(engine.validate(_acting))
		_acting = null
		return
	if options.size() == 1 and not _dragging:
		cancel_selection()
		_submit(options[0])
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
	var at := _drop_at
	_drop_at = Vector2.INF
	cancel_selection()
	_submit(action, at)


func cancel_selection() -> void:
	if selecting < 0:
		return
	selecting = -1
	_options.clear()
	_option_index = -1
	for v in _views():
		v.valid_zones.clear()
		v.hover_zone = {}
		v.stop_zone_pulse()
		v.queue_redraw()
	_stop_aim_motion()
	_dim_hand()
	_clear_ghost()
	_show_end_turn_preview()


func cycle_target() -> void:
	if _target_option.item_count == 0:
		return
	var next := (_target_option.selected + 1) % _target_option.item_count
	_target_option.select(next)
	_submit(CombatAction.target(_target_option.get_item_metadata(next)))


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
	tutorial.step_changed.connect(_relayout.call_deferred)  # ANIM-R6 A16: the box follows its step's text
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
## wheel, optionally leaving the NULL slice out (random non-NULL picks).
## The corporation whose words `c`'s wheel speaks (DECISIONS "names for M14" D3 / D4): an
## enemy's corporation, "" for the Cell's own wheels.
func corp_of(c: CombatantState) -> StringName:
	if c == null or c.is_player or engine == null:
		return &""
	var e := engine.content(c.source_id) as EnemyData
	return e.corporation_id if e != null else &""


func odds_text(c: CombatantState, non_null_only: bool = false) -> String:
	var parts := PackedStringArray()
	for chip in _odds_chips(c, non_null_only):
		parts.append(String(chip["text"]))
	return tr("odds: %s") % " / ".join(parts)


## ANIM-R5 combat 9: sets `c`'s tooltip to `text`, translated where it was built, and shows it
## as given (translate once; several were never translated at all).
static func shown_tip(c: Control, text: String) -> void:
	c.tooltip_text = text
	c.tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED


func _odds_chips(c: CombatantState, non_null_only: bool = false) -> Array[Dictionary]:
	var counts := {}
	var order: Array[String] = []
	var total := 0
	for id in c.wheel.slot_slice_ids:
		var slice := engine.content(id) as SliceData
		if slice == null or (non_null_only and slice.slice_type == RC.SliceType.NULL):
			continue
		var key: String = tr(Palette.slice_word(slice.slice_type, corp_of(c)))  # ART-2 2A: the word only; the glyph is the atlas one (SliceIcon)
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
	# ANIM-R4 C4: the nudge arrows' key hints ([Q] / [E], [LB] / [RB]) never sit on a tag.
	for w in wheels:
		if w.combatant == null:
			continue
		for hr in w.arrow_hint_rects():
			for other in wheels:
				if other.combatant != null and other.intent_rect().has_area() and hr.intersects(other.intent_rect()):
					out.append("%s's nudge key hint covers %s's tag" % [w.combatant.display_name, other.combatant.display_name])
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
	# ANIM-2 / ANIM-R1: a press during the SEND IT sequence skips it to the end state and
	# is consumed (MotionSkip: the one press predicate and consume rule).
	# ANIM-R4 C2 (MotionSkip.verdict, the one rule): a press that works the screen (a focus
	# move, the Settings key, a click on a usable button) ends the replay and passes on; an
	# open pause menu keeps its presses; the fight's own controls (SEND IT, RESPIN, UNDO, the
	# hand) keep theirs: a press on them only ends the replay, so the next turn is never
	# played blind.
	if replay_press(event) != MotionSkip.Verdict.IGNORE:
		return
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


## What a press does while the SEND IT replay plays (the scene's _input asks first): IGNORE
## (no replay, or not a press: the input goes on as usual), PASS (it ended the replay and
## passes on to what it works) or CONSUME (it ended the replay and nothing else sees it).
func replay_press(event: InputEvent) -> MotionSkip.Verdict:
	if not _skippable():
		return MotionSkip.Verdict.IGNORE
	var verdict := MotionSkip.verdict(event, self, replay_keeps())
	if verdict == MotionSkip.Verdict.IGNORE:
		return verdict
	# ANIM-R6 A1: whether the next step was on screen before this press (the skip below lands
	# a held outcome, which shows it).
	var was_shown := continue_shown()
	# ANIM-R5: every running motion completes with the replay (MotionSkip.complete_all).
	MotionSkip.complete_all(self, event)  # ANIM-R6 D1: helpers that let this press pass stay
	# ANIM-R3 A6h: the fight's next-step action works at once, replay or not (the press ends
	# the replay and goes on to it). ANIM-R6 A1: only when it was already shown; a press that
	# lands the outcome (and so shows the next step) only skips (STYLE_GUIDE 5.2: any press
	# skips and does nothing else), never also leaves the fight.
	if was_shown and _for_continue(event):
		return MotionSkip.Verdict.PASS
	if verdict == MotionSkip.Verdict.CONSUME:
		MotionSkip.consume(self, event)
	return verdict


## ANIM-R4 C2: the controls whose presses the SEND IT replay keeps (a press on them ends the
## replay and does nothing else): SEND IT, the stickers, the hand.
func replay_keeps() -> Array:
	return [_end_turn_button, _sticker_box, _hand_box]


## True when `event` is meant for the next-step action: a click on it, accept while it has
## focus, or SEND IT's key. ANIM-R5 combat 10: a click only when it would press the button
## (MotionSkip.button_at: shown, not covered, the clicking mouse button in its mask), so a
## right-click on JACK OUT / CONTINUE during the replay is consumed like any other press.
func _for_continue(event: InputEvent) -> bool:
	if not continue_shown():
		return false
	if event.is_action(&"end_turn"):
		return true
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		return MotionSkip.button_at(get_viewport(), mb.global_position, mb.button_index) == _continue_button
	return event.is_action(&"ui_accept") and _continue_button.has_focus()


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
		if c is ZineCard and not c.is_queued_for_deletion():
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
		if continue_shown():
			_continue_pressed()  # ANIM-R3 A6h: SEND IT's key goes on once the fight is over
		else:
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
			# ANIM-3 pick-up: the card pops as it leaves the hand.
			var picked := _card_node(i)
			if picked != null:
				Motion.pop(picked, &"card_pickup")
			var options := CardTargeting.options(engine.resolver, engine.state(), i)
			if options.is_empty():
				_dragging = false
				_acting = _card_action(i)
				_on_action_refused(engine.validate(_acting))
				_acting = null
			else:
				_begin_targeting(i, options)
	elif what == NOTIFICATION_DRAG_END:
		if _dragging:
			_dragging = false
			if not get_viewport().gui_is_drag_successful():
				_cancel_drag(selecting, get_global_mouse_position())


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
	_start_aim_motion()
	_show_aim_hint()
	# The card being aimed stays lifted (it holds focus while the aim moves).
	var aimed_card := _card_node(hand_index)
	if aimed_card != null and not _dragging:
		aimed_card.grab_focus()
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
		_submit(CombatAction.target(want))


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
		_cancel_drag(selecting, get_global_mouse_position())
		return
	_option_index = i
	_dragging = false
	# The card flies from where it was let go and snaps onto the zone (ANIM-3).
	_drop_at = get_global_mouse_position()
	confirm_selection()


## A dashed acid line from the aimed card to the zone it plays on, with a ring there.
func _draw_aim_line() -> void:
	var card_node := _card_node(selecting)
	if selecting < 0 or _option_index < 0 or card_node == null:
		return
	var z := _zone_of(_options[_option_index])
	var v := _view_of(z[0])
	if v == null:
		return
	var origin := _aim_line.get_global_rect().position
	var card := card_node.get_global_rect()
	var from := Vector2(card.get_center().x, card.position.y) - origin
	# ANIM-3: the line draws in from the card each time the aim moves.
	var to := from.lerp(v.zone_center(z[1]) - origin, _aim_draw)
	var n := maxi(2, int(from.distance_to(to) / 14.0))
	for k in n:
		if k % 2 == 0:
			_aim_line.draw_line(from.lerp(to, float(k) / n), from.lerp(to, float(k + 1) / n), Palette.CELL_ACID, AIM_LINE_WIDTH)
	_aim_line.draw_arc(to, 12.0, 0, TAU, 20, Palette.CELL_ACID, AIM_LINE_WIDTH)


## Fades the cards not being aimed (and restores them).
func _dim_hand() -> void:
	for c in _hand_box.get_children():
		if c is ZineCard and not _returning.has((c as ZineCard).drag_index):
			(c as Control).modulate.a = AIM_DIM if selecting >= 0 and (c as ZineCard).drag_index != selecting else 1.0
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
		# ART-0 F (ported from art-pass W9F, §6.8 / §12): input-aware words, one call.
		_aim_hint.text = UiTip.for_input(tr("Drop or click on a glowing target  ·  right-click cancels"),
			tr("%s / %s: choose a glowing target  ·  %s: play  ·  %s: cancel") % [Settings.key_text(&"ui_left"), Settings.key_text(&"ui_right"), Settings.key_text(&"ui_accept"), Settings.key_text(&"ui_cancel")])
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
	if aimed_view != null:
		_aim_at(aimed_view.zone_center(z[1]))
	_preview_action(_options[_option_index])


# --- Engine callbacks --------------------------------------------------------------

func _on_state_changed(state: CombatState, events: Array[Dictionary]) -> void:
	_last_events = events
	var before_turn := _pending_last_turn
	var before_action := _before_action
	var rewind_from := _rewind_from
	var play := _pending_play
	var discard := _pending_discard
	_before_action = null
	_rewind_from = null
	_pending_play = {}
	_pending_discard = []
	if _pending_last_turn != null:
		_last_turn = last_turn_lines(_pending_last_turn, state, events)
		_last_icons = last_turn_icons(_pending_last_turn, events)
		_last_tips = last_turn_tips(_last_turn, events)
		_pending_last_turn = null
	elif not events.is_empty():
		_last_turn.clear()  # the player acted: the result gives way to the new preview
		_last_icons.clear()
		_last_tips.clear()
	for e in state.enemies:
		RunManager.record_seen(e.source_id)
	_play_log(events)
	# ANIM-2 / ANIM-3: the state is final now; motion replays it on top. A replay still
	# running ends first, except queued nudge steps, which a new nudge joins.
	var live := Motion.animating() and not events.is_empty()
	# ART-0 C (art pass W9s, ART_BIBLE §10): an instant resolve speed shows the end state at
	# once, as a skip would.
	var sequence := live and before_turn != null and _has_event(events, "resolve_start") and not Motion.resolve_instant()
	if not (live and _only_nudges(events)):
		skip_motion()
	# ANIM-R1 C5e: while a SEND IT replays, the next turn's forecast (tags, NEXT plates) and
	# its TURN number wait for the replay's end, so nothing of the new turn reads as the
	# result (and no forecast from before SEND IT lingers into it).
	_hold_forecast = sequence
	# ANIM-R5 combat 1: a SEND IT that ends the fight keeps its outcome (the status word, the
	# next-step button, Heat, the run's top bar) until the replay lands it (`_land_outcome`).
	_outcome_held = sequence and state.is_over() and Motion.live(&"resolve_sequence")
	_shown_turn = before_turn.turn if sequence else -1
	# ANIM-R6 A5 / A8: while the replay plays, the portrait follows its HP rolls and the run's top
	# bar keeps the HP the turn started with until it lands.
	var replays := sequence and Motion.live(&"resolve_sequence")
	_replay_hp = before_turn.player.hp if replays else -1
	_replay_start_hp = _replay_hp
	# ANIM-R4 C6e: a card or respin that spins a wheel holds the forecast until it lands.
	_card_hold = live and not sequence and rewind_from == null and before_action != null and _spins(events)
	_refresh(state)
	_feedback(state, events, sequence)
	if live and _has_event(events, "combat_start"):
		# ANIM-R1 C5f: a new fight's enemies enter from the edge with their names.
		for v in _enemy_views.values():
			(v as WheelView).play_enter()
	if sequence:
		_play_resolve_sequence(before_turn, state, events, discard)
	elif live and rewind_from != null:
		_play_rewind(rewind_from)
	elif live and before_action != null:
		_play_action(before_action, state, events, play)
	else:
		_free_captures(play, discard)
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
	# The RAM bar flashes when RAM is what's missing (ANIM-R1 C6: its chips go red and
	# "COST > RAM" shows beside them; the refused card's cost, or the respin sticker,
	# pulses too). The toast stays.
	if reason.contains("RAM"):
		var need := _ram_need(_acting)
		ram_note.flash_short(need)
		if _acting != null and _acting.type == CombatAction.Type.PLAY_CARD:
			var card := _card_node(_acting.hand_index)
			if card != null:
				card.pulse_cost()
		elif _acting != null and _acting.type == CombatAction.Type.RESPIN and _respin_button != null:
			Motion.pop(_respin_button, &"ram_refusal_pop")
	AudioDirector.play_sfx("click")


## The RAM `action` costs (0 when unknown or free).
func _ram_need(action: CombatAction) -> int:
	if action == null or not engine.has_fight():
		return 0
	var state := engine.state()
	match action.type:
		CombatAction.Type.PLAY_CARD:
			if action.hand_index >= 0 and action.hand_index < state.hand.size():
				var card := engine.content(state.hand[action.hand_index]) as CardData
				return card.ram_cost if card != null else 0
		CombatAction.Type.RESPIN:
			return engine.resolver.config.respin_ram_cost
		CombatAction.Type.NUDGE:
			return engine.resolver.config.extra_nudge_ram_cost
	return 0


## The action being sent or checked now (a refusal names what it cost), null otherwise.
var _acting: CombatAction = null


func _on_fight_ended(outcome: int) -> void:
	log_note.append("[b]%s[/b]" % ("VICTORY" if outcome == CombatState.Outcome.VICTORY else "DEFEAT"))
	# With motion, the VICTORY beat of the replay flashes (after the last hit lands).
	if outcome == CombatState.Outcome.VICTORY and not motion_busy():
		_victory_flash()


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
			delay += Motion.seconds(PASS_MOTION)
		if delay <= 0.0:
			log_note.append(text)
		else:
			# ANIM-R6 A10: a bound method of this scene (dropped with it), no lambda holding it.
			get_tree().create_timer(delay).timeout.connect(_append_log.bind(generation, text))


## One line of the log playback, unless a newer playback started since (`generation`).
func _append_log(generation: int, text: String) -> void:
	if generation == _log_generation and is_instance_valid(log_note):
		log_note.append(text)


func _instant_playback() -> bool:
	return DisplayServer.get_name() == "headless" or not Fx.effects_enabled()


## Precision and action feedback (STYLE_GUIDE 5, GDD 10): Perfect = latch + wheel-local
## inversion + 2-frame freeze (+ a limited flash); Good = click; Weak = stutter shake;
## NULL slice = static burst. Nudges tick, spins run down, flips clack. Telegraphed
## migrations flicker the boss pointers until they move.
func _feedback(state: CombatState, events: Array[Dictionary], replayed: bool = false) -> void:
	for e in events:
		if replayed and String(e.get("type", "")) in ["pointer", "boss_phase"]:
			continue  # the SEND IT replay lands each needle (and a boss phase) on its beat
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
				var is_null_slice: bool = _slice_type_of(state, e) == RC.SliceType.NULL
				var tier := int(e.get("tier", RC.PrecisionTier.GOOD))
				AudioDirector.play_precision(tier, is_null_slice)
				if is_null_slice:
					_flicker_view(_player_view)
					_bark("null", state)
				elif tier == RC.PrecisionTier.PERFECT:
					_perfect_feedback(_player_view)
					_bark("perfect", state)
				elif tier == RC.PrecisionTier.WEAK:
					_stutter_view(_player_view)
			"boss_phase":
				_boss_phase_feedback(state)
			"damage":
				if hurt_bark_due(e, state):
					_bark("hurt", state)
			"deploy":
				_bark("deploy", state)
			"combat_end":
				if replayed and _outcome_held:
					continue  # ANIM-R5 combat 1: the replay barks when VICTORY / DEFEAT lands
				_bark("victory" if int(e.get("outcome", 0)) == CombatState.Outcome.VICTORY else "defeat", state)
			"boss_migrate_telegraph":
				if _enemy_views.has(e.get("target")):
					_start_migrate_flicker(_enemy_views[e["target"]])
			"deploy", "botnet_seed":
				AudioDirector.play_sfx("click")


## True when damage event `e` in `state` calls for the operative's "hurt" bark: it took HP
## and is at half or below. ANIM-R5 combat 2: never on the hit that flatlines it (a "Keep
## going" under DEFEAT).
static func hurt_bark_due(e: Dictionary, state: CombatState) -> bool:
	return e.get("target") == state.player.id and int(e.get("hp_damage", 0)) > 0 and state.player.hp * 2 <= state.player.max_hp \
		and state.player.is_alive() and state.outcome != CombatState.Outcome.DEFEAT


## Operative barks (GDD 8.6): at most one per turn per trigger, chosen by class and turn.
var _barked_turn: Dictionary = {}
## ANIM-R6 B5: the screen a bark belongs to (Dialogue scope: the netrun's fight screen).
const BARK_SCOPE := "combat"


func _bark(trigger: String, state: CombatState) -> void:
	var key := "%s:%d" % [trigger, state.turn]
	# ANIM-R6 A2: barks play with motion (Motion.animating: the same as not _instant_playback
	# in the game; the tests' forced motion hears them too).
	if _barked_turn.has(key) or not Motion.animating():
		return
	_barked_turn[key] = true
	# ANIM-R6 B5: the fight's own lines end with the fight (Dialogue scope): the defeat bark
	# replayed after DISPATCH's "Operative lost" on the run's end, a dead operative speaking last.
	Dialogue.bark(state.player.source_id, trigger, state.turn + hash(engine.session.combat_seed), BARK_SCOPE)


## A boss enters a phase: the alarm, a limited flash in its corporation's colour
## (`boss_phase_flash`: amplitude = strength; nothing when motion doesn't play) and a bark.
func _boss_phase_feedback(state: CombatState) -> void:
	AudioDirector.play_sfx("alarm")
	if Motion.live(&"boss_phase_flash") and fx_layer != null:
		# ART-0 E (ported from art-pass W6, ART_BIBLE v2 5.3): a T3 ring on the boss's own
		# wheel, never the screen.
		var hue := Palette.corp_color(RunManager.campaign.corporation_id) if RunManager.campaign != null else Palette.CORP_SOLACE
		for boss in state.enemies:
			var bv: WheelView = _view_of(boss.id) if boss.phase_index > 0 else null
			if bv != null:
				fx_layer.wheel_burst(bv.global_center(), bv.disc_radius(), CombatFxLayer.BURST_PHASE, hue, bv.hp_ring_spot())
	_bark("boss", state)


## The VICTORY flash (ANIM-R2 E5): a short local white flash on each beaten enemy's wheel
## (`victory_flash`: amplitude = its alpha), never the whole screen.
func _victory_flash() -> void:
	if not Motion.live(&"victory_flash"):
		return
	for v in _enemy_views.values():
		var wv := v as WheelView
		fx_layer.disc_flash(wv.global_center(), wv.disc_radius(), Color.WHITE, &"victory_flash")


func _slice_type_of(state: CombatState, e: Dictionary) -> int:
	var slot := int(e.get("slice_index", 0))
	var slice := engine.content(state.player.wheel.slot_slice_ids[slot]) as SliceData
	return slice.slice_type if slice != null else RC.SliceType.SHIM


func _perfect_feedback(view: WheelView) -> void:
	# ANIM-R1 C1: with motion off (reduce effects, headless, the entry disabled) the end
	# state shows at once: no inversion, no flash, no freeze.
	if not Motion.live(&"precision_perfect"):
		view.inverted = false
		view.queue_redraw()
		return
	view.inverted = true
	view.queue_redraw()
	# ART-0 E (ported from art-pass W6, ART_BIBLE v2 5.3): a T3 burst on this wheel only,
	# never the screen.
	if fx_layer != null:
		fx_layer.wheel_burst(view.global_center(), view.disc_radius(), CombatFxLayer.BURST_PERFECT)
	Fx.freeze_frames()
	# ANIM-R5 combat 11: the scene may leave the tree between the frames (a fight left
	# mid-freeze): no await that resumes on a freed scene; each frame is a one-shot connection
	# to this scene's method (dropped with the scene), checked in the tree before the next.
	get_tree().process_frame.connect(_perfect_frame.bind(view, PERFECT_INVERT_FRAMES), CONNECT_ONE_SHOT)


## Frames the Perfect inversion shows (drawing, as the 2-frame freeze).
const PERFECT_INVERT_FRAMES := 2


## One frame of the Perfect inversion has passed; `left` more to go.
func _perfect_frame(view: WheelView, left: int) -> void:
	if left > 1 and is_inside_tree():
		get_tree().process_frame.connect(_perfect_frame.bind(view, left - 1), CONNECT_ONE_SHOT)
		return
	if is_instance_valid(view):
		view.inverted = false
		view.queue_redraw()


func _stutter_view(view: WheelView) -> void:
	if not Fx.effects_enabled():
		return
	Motion.shake(view, &"precision_weak", ^"shake")


func _flicker_view(view: WheelView) -> void:
	if not Fx.effects_enabled():
		return
	Motion.blink(view, &"precision_blink")


## Migration flicker (GDD 9.2): the current pointers fade in and out while the dashed
## "next" pointers show where they go; stops when the state no longer has a pending move.
func _start_migrate_flicker(view: WheelView) -> void:
	if _migrate_tween != null and _migrate_tween.is_valid():
		_migrate_tween.kill()
	if not Motion.live(&"pointer_flicker"):
		view.pointer_alpha = 0.6
		view.queue_redraw()
		return
	_migrate_tween = Motion.loop_pulse(view, ^"pointer_alpha", &"pointer_flicker")


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
	# ART-2 2C §3.15: Heat on the backdrop (H1, the city reacts), behind every wheel.
	heat_city = HeatCity.new()
	heat_city.name = "HeatCity"
	add_child(heat_city)
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
	shown_tip(_status, tr("The turn, and the free nudges left this turn (each extra nudge costs RAM)."))
	top.add_child(_status)
	_settings_button = _button(tr("Settings"), open_settings)
	_settings_button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED  # ANIM-R6 A12: its words come translated
	shown_tip(_settings_button, tr("Pause: options, codex, save and quit."))
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
	shown_tip(heat_poster, tr("Heat: the corporation's attention. Thresholds bring raids and harder rules."))
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
	preview_note = ZineNote.new(tr("WHAT WILL RESOLVE"), Vector2(RIGHT_WIDTH, 150))
	preview_note.name = "PreviewNote"
	preview_note.visible = false
	_right.add_child(preview_note)
	log_note = ZineNote.new(tr("LOG"), Vector2(RIGHT_WIDTH, 150))
	log_note.name = "LogStrip"
	log_note.visible = false
	_right.add_child(log_note)

	# The hidden option row keeps the keyboard toggles and play_card()'s defaults.
	var controls := HFlowContainer.new()
	controls_row = controls
	controls.visible = false
	root.add_child(controls)
	_target_option = OptionButton.new()
	_target_option.item_selected.connect(func(i: int) -> void: _submit(CombatAction.target(_target_option.get_item_metadata(i))))
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
	(_end_turn_button as DripButton).glyph = true  # ANIM-R1 C7: the drawn ▶▶ end-turn mark
	shown_tip(_end_turn_button, tr("End the turn: every needle resolves at once (defensive, then offensive, then statuses). The tags show the outcome."))
	_end_turn_button.pressed.connect(end_turn)
	bottom.add_child(_end_turn_button)
	_zine_elements.append(_end_turn_button)
	# ANIM-R3 A6h: once the fight is over, SEND IT, RESPIN and UNDO go and the next step's
	# action takes their place at once (the netrun names it: LOOT, CONTINUE).
	_continue_button = DripButton.new("CONTINUE", "[%s]" % Settings.key_text(&"end_turn"), DripButton.DRIP_PINK, 40, DripButton.SEND_IT_DRIPS)
	_continue_button.name = "Continue"
	_continue_button.visible = false
	_continue_button.pressed.connect(_continue_pressed)
	TextDb.shown_as_given(_continue_button)  # ANIM-R4 C1: its tooltip arrives translated (show_continue)
	bottom.add_child(_continue_button)
	_zine_elements.append(_continue_button)

	# The motion overlay: over the arena and the hand, under the toast and popups.
	fx_layer = CombatFxLayer.new()
	fx_layer.name = "MotionLayer"
	add_child(fx_layer)
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
	# ANIM-R6 A16: the tutorial wants the height its step's text needs (the box is sized to
	# its text; a longer one shows in pages).
	var want := maxf(TUTORIAL_MIN_HEIGHT, tutorial.needed_height(area.size.x)) if tutoring else TUTORIAL_MIN_HEIGHT
	while tutoring and lines > 1 and area.size.y - dock_h - NOTE_GAP < want:
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
	tutorial.fit(Vector2(area.size.x, minf(bottom - top, want)))


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
	# ANIM-R6 A12: its word translated once here (the button shows it as given).
	_settings_button.text = ("%s %s" % [tr("Settings"), Settings.hint(&"open_settings")]).strip_edges()
	(_end_turn_button as DripButton).set_key_hint(Settings.hint(&"end_turn"))
	(_continue_button as DripButton).set_key_hint(Settings.hint(&"end_turn"))
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
	_portrait_name = [operative_name, _name_of(state.player)]
	# ANIM-R6 A8: while a SEND IT replays, the portrait (its glitch, its HP tooltip) shows the
	# HP the replay has reached, not the turn's end.
	_sync_portrait(state.player.hp if _replay_hp < 0 else _replay_hp, state.player.max_hp)
	ram_note.set_ram(state.ram, state.max_ram)
	daemon_row.set_daemons(state.daemon_ids, lookup)
	if not _outcome_held:
		_sync_heat()  # ANIM-R5 combat 1: a fight's Heat moves once its outcome has landed
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
	_sync_over(state.is_over() and not _outcome_held)
	# ANIM-R6 A15: VICTORY stands once it has landed (at once without a replay); a fight that
	# goes on (a new one) shows none.
	if state.outcome != CombatState.Outcome.VICTORY:
		fx_layer.release_word()
	elif not _outcome_held and fx_layer.held_word.is_empty():
		_hold_victory.call_deferred(true)  # the views lay out first (it stands above the enemy's disc)
	_player_view.flatlined = state.outcome == CombatState.Outcome.DEFEAT and not _outcome_held
	# ANIM-R1 C7: nothing left to spend: the ▶▶ mark pulses gently (off under reduce effects).
	(_end_turn_button as DripButton).set_ready(state.ram <= 0 and not state.is_over())
	_rewind_button.disabled = not engine.can_rewind()
	_sync_undo_tip()
	_link_hand_focus()
	_nav_focus = false  # the refocus below is automatic, not the player moving focus
	UiFocus.focus_first(_hand_box, true, _end_turn_button.get_parent())
	_respin_button.disabled = state.is_over() or state.ram < engine.resolver.config.respin_ram_cost
	_sync_stickers()
	_sync_arrow_hints()
	selecting = -1
	_options.clear()
	_option_index = -1
	_sync_arrows(state)
	for v in _views():
		v.valid_zones.clear()
		v.hover_zone = {}
		v.last_turn = String(_last_turn.get(v.combatant.id, "")) if v.combatant != null else ""
		v.last_turn_icons = _last_icons.get(v.combatant.id, {}) if v.combatant != null else {}
		v.last_turn_tip = String(_last_tips.get(v.combatant.id, "")) if v.combatant != null else ""
	toast.hide()
	inspect_popup.hide()
	_show_end_turn_preview()


## ANIM-R3 A6h: the netrun names the step after the fight (LOOT, CONTINUE); the action shows
## in SEND IT's place once the fight is over (at once, the replay may still play) and takes
## focus.
## ANIM-R4 C1: `label` is the key ("LOOT", "CONTINUE"): the drip lettering translates it
## once where it draws it, and the tooltip is that translation shown as given (it was
## translated by the netrun, then again by the button: "[[ĿÔÔŢ]]").
func show_continue(label: String) -> void:
	_continue_label = label
	if _continue_button == null:
		return
	(_continue_button as DripButton).set_tag_text(label)
	_continue_button.tooltip_text = tr(label)
	_style_continue()
	_sync_over(engine.has_fight() and engine.state().is_over() and not _outcome_held)


## ANIM-R5 combat 2: the next step after a defeat (JACK OUT) wears its own look, never
## SEND IT's pink drips (a lost fight read as one that goes on); a win keeps the drips.
func _style_continue() -> void:
	var b := _continue_button as DripButton
	var lost := engine.has_fight() and engine.state().outcome == CombatState.Outcome.DEFEAT
	b.paint = JACK_OUT_PAINT if lost else DripButton.DRIP_PINK
	b.drips = [] if lost else DripButton.SEND_IT_DRIPS
	b.queue_redraw()


## ANIM-R5 combat 2: JACK OUT's lettering (paper, no drips).
const JACK_OUT_PAINT := Palette.PAPER


## ANIM-R6 A8: the nudge arrows stay while a fight's outcome waits for its replay (they went
## the moment SEND IT ended the fight) and go when it lands.
func _sync_arrows(state: CombatState) -> void:
	var over := state.is_over() and not _outcome_held
	for v in _views():
		if v.show_arrows == over:
			v.show_arrows = not over
			v.queue_redraw()


## ANIM-R6 A8: the operative's portrait at `hp`: it glitches at a quarter HP or less and its
## tooltip says the HP (during a replay, the HP the replay has reached).
func _sync_portrait(hp: int, max_hp: int) -> void:
	if portrait == null:
		return
	portrait.glitch = hp * 4 <= max_hp
	shown_tip(portrait, tr("%s (%s): %d/%d HP.") % [_portrait_name[0], _portrait_name[1], hp, max_hp])
	portrait.queue_redraw()


## The portrait's caption for its tooltip ("Kez (Breaker)"), and the operative's HP the SEND IT
## replay has reached (-1 when none plays: the state's).
var _portrait_name: Array = ["", ""]
var _replay_hp: int = -1
## The operative's HP when the SEND IT replaying now was pressed (-1 = none plays): the top
## bar keeps it until the replay lands its turn.
var _replay_start_hp: int = -1


## The HP the run's top bar shows during a fight (ANIM-R6 A5): the operative's HP in the fight
## (the run's is written when the fight ends), as far as the SEND IT replay has landed it.
func top_bar_hp() -> int:
	if not engine.has_fight():
		return -1
	return engine.state().player.hp if _replay_start_hp < 0 else _replay_start_hp


## Emitted when the HP the top bar shows during a fight changes on screen (a replay lands its
## turn, or an action changes it at once).
signal shown_hp_changed


## The Heat poster and the arena's corporate creep show the campaign's Heat now.
func _sync_heat() -> void:
	var heat := RunManager.campaign.heat if RunManager.campaign != null else 0
	var heat_max := engine.resolver.config.heat_max
	heat_poster.set_heat(heat, heat_max, HeatRules.band_levels(RunManager.campaign, engine.resolver.config))
	background.corp_creep = clampf(float(heat) / maxf(1.0, heat_max), 0.0, 1.0)
	var levels := HeatRules.band_levels(RunManager.campaign, engine.resolver.config)
	heat_city.set_band(Palette.heat_band(heat, levels), _enemy_views_box.get_global_rect().get_center() if _enemy_views_box != null else Vector2.INF)


## ANIM-R5 combat 1: the outcome lands (the replay's VICTORY / DEFEAT beat, a skip, the
## replay's end): the status line says it, the next-step button replaces SEND IT, the Heat
## poster rolls, a lost fight keeps its DEFEAT stamp, and the netrun is told
## (`outcome_landed`: its top bar moves on).
## ANIM-R6 A2: `instant` (a skip, the next step pressed): the DEFEAT stamp shows whole at
## once (no pop after the press that skipped), and the VICTORY / DEFEAT bark the skipped end
## beat would have said is said here (`_bark` says it once).
func _land_outcome(instant: bool = false) -> void:
	if not _outcome_held:
		return
	_outcome_held = false
	if not engine.has_fight():
		outcome_landed.emit()
		return
	var state := engine.state()
	_refresh_status()
	_sync_heat()
	_sync_over(state.is_over())
	_sync_arrows(state)
	_sync_portrait(state.player.hp, state.player.max_hp)
	var lost := state.outcome == CombatState.Outcome.DEFEAT
	if lost and (instant or not _player_view.flatlined):
		if instant:
			_player_view.show_flatline()
		else:
			_player_view.play_flatline()
	if state.outcome == CombatState.Outcome.VICTORY and fx_layer != null and fx_layer.held_word.is_empty():
		_hold_victory(true)  # ANIM-R6 A15: a skipped end beat still leaves VICTORY standing
	if state.is_over():
		_bark("victory" if state.outcome == CombatState.Outcome.VICTORY else "defeat", state)
	outcome_landed.emit()


## True while a fight's outcome waits for its replay to land it (the netrun holds its top
## bar until `outcome_landed`).
func outcome_pending() -> bool:
	return _outcome_held


func _sync_over(over: bool) -> void:
	if _continue_button == null:
		return
	_end_turn_button.visible = not over
	_sticker_box.visible = not over
	var show := over and _continue_label != ""
	var was := _continue_button.visible
	_continue_button.visible = show
	if show and not was and is_inside_tree():
		_continue_button.grab_focus.call_deferred()


## True when the next step's action is on screen (the fight is over).
func continue_shown() -> bool:
	return _continue_button != null and _continue_button.is_visible_in_tree()


func _continue_pressed() -> void:
	if not continue_shown():
		return
	skip_motion()
	continue_requested.emit()


## The status line: turn, free nudges, and on a pad the triggers that pick which wheel and
## ring the nudge buttons drive.
func _refresh_status() -> void:
	if not engine.has_fight():
		return
	var state := engine.state()
	var text := tr("TURN %d · FREE NUDGE %d") % [state.turn if _shown_turn < 0 else _shown_turn, state.free_nudges]
	if _outcome_held:
		pass  # ANIM-R5 combat 1: the outcome's word waits for its beat (no key hints: SEND IT is spent)
	elif state.outcome == CombatState.Outcome.VICTORY:
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
	# ANIM-R4 C3: the old cards are freed at once (queued, they sat as orphans until the frame
	# ended); only while a card's own press is being handled (it plays itself) or a drag is
	# under way is the card queued instead.
	for child in _hand_box.get_children():
		_hand_box.remove_child(child)
		if _card_pressing > 0 or _dragging:
			child.queue_free()
		else:
			child.free()
	_gap = null
	# ANIM-3: a played card leaves a gap in its slot while it flies, so no card moves under
	# the cursor; the hand keeps the scale it had with that card in it.
	var hold := _hold_slot if Motion.animating() and _hold_slot >= 0 and _hold_slot <= state.hand.size() else -1
	var s := _card_scale_for(state.hand.size() + (1 if hold >= 0 else 0))
	_hand_scale = s
	for i in state.hand.size():
		if i == hold:
			_add_gap(s)
		var card := lookup.get_content(state.hand[i]) as CardData
		var c := _make_card(card, i, s)
		c.disabled = state.is_over() or state.ram < card.ram_cost
		c.short_ram = not state.is_over() and state.ram < card.ram_cost  # ART-2 2C: the grey dot and NEED tag
		var several := CardTargeting.options(engine.resolver, state, i).size() > 1
		shown_tip(c, "%s\n%s" % [Codex.describe(card), UiTip.for_input(tr("Drag it onto a glowing target, or click it and then the target."), tr("Press it, then pick a glowing target.")) if several
			else UiTip.for_input(tr("Click to play."), tr("Press it to play."))])
		var index := i
		c.pressed.connect(_card_pressed.bind(index))
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
	if hold == state.hand.size():
		_add_gap(s)


## A hand card was pressed: it is picked (and may play itself, rebuilding the hand while
## its own signal runs: _build_hand then queues it rather than freeing it).
var _card_pressing: int = 0


func _card_pressed(index: int) -> void:
	_card_pressing += 1
	select_card(index)
	_card_pressing -= 1


## A hand card sticker for `card` at hand index `i` and scale `s` (no signals: the hand
## connects its own; flights use the bare copy).
func _make_card(card: CardData, i: int, s: float) -> ZineCard:
	var c := ZineCard.new(TextDb.t(card, "display_name"), card.ram_cost, TextDb.t(card, "description"), i).scaled(s).with_card(card)
	if Settings.pad_active:
		c.hotkey = ""
		c.pad_hint = Settings.key_text(&"ui_accept")
	c.drag_index = i
	return c


## Card scale: the text scale, shrunk when the hand would not fit beside SEND IT.
func _card_scale_for(count: int) -> float:
	var n := maxi(1, count)
	var sep := float(_hand_box.get_theme_constant("separation"))
	var width := size.x if size.x > 0.0 else get_viewport_rect().size.x
	var room := width - _end_turn_button.get_combined_minimum_size().x - _sticker_box.get_combined_minimum_size().x - sep * 3.0
	var fit := (room - sep * (n - 1)) / n / ZineCard.STICKER_SIZE.x
	var height := size.y if size.y > 0.0 else get_viewport_rect().size.y
	fit = minf(fit, height * HAND_HEIGHT_SHARE / ZineCard.STICKER_SIZE.y)
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
		lines.append(tr("Guarded by %s (%d HP): it takes hits aimed at this slice.") % [_name_of(guard), guard.hp])
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
	var was := _forecast_tags()
	_preview_result(action, state, result)
	_mark_was(was)


## ANIM-R5 combat 7: the tags as the End Turn forecast shows them now (view -> its tag), so a
## preview can show what each tag said before it.
func _forecast_tags() -> Dictionary:
	_show_end_turn_preview()
	var out := {}
	for v in _views():
		out[v] = v.intent.duplicate(true)
	preview_note.clear()  # the hidden note keeps the preview's own lines
	return out


## ANIM-R5 combat 7: each tag a preview changed keeps what it said before (`was`), shown
## struck through under a WAS row; an unchanged tag shows none.
func _mark_was(was: Dictionary) -> void:
	for v in _views():
		var old: Dictionary = was.get(v, {})
		v.was_tag = old if tag_changed(old, v.intent) else {}
		v.queue_redraw()


## True when tag `now` says something other than `old` (its title or a chip; the "YOU PLAY
## X" chip a preview adds doesn't count). Two empty tags are the same.
static func tag_changed(old: Dictionary, now: Dictionary) -> bool:
	if old.is_empty() or String(old.get("text", "")) == "":
		return false
	return _tag_words(old) != _tag_words(now)


static func _tag_words(tag: Dictionary) -> PackedStringArray:
	var out := PackedStringArray([String(tag.get("text", ""))])
	for c in tag.get("chips", []):
		if not bool((c as Dictionary).get("play", false)):
			out.append(String(c.get("text", "")))
	return out


## The preview of `action` (its result `result` from `state`) on the tags, arcs and RAM.
func _preview_result(action: CombatAction, state: CombatState, result: CombatResult) -> void:
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
			var non_null := false
			for e in card.effects:
				if e != null and e.slice_pick == RC.SlicePick.RANDOM_NON_NULL:
					non_null = true
			var chips: Array = [{"text": tr("RANDOM: ODDS"), "color": Palette.INK, "ink": Palette.PAPER}]
			chips.append_array(_odds_chips(target, non_null))
			v.intent = {"type": -1, "text": tr("%s rolls") % TextDb.t(card, "display_name"), "chips": chips,
				"tooltip": tr("A random effect: the roll is hidden until you play it. %s") % odds_text(target, non_null)}
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


## The wheel a hovered card or nudge acts on says so first on its tag ("PLAYING JOLT"), so the
## changes read as that play's (H24: a hovered card seemed to spin the enemy onto
## CRITICAL by itself).
func _mark_preview_source(action: CombatAction, card: CardData) -> void:
	var target := engine.state().get_combatant(action.wheel_id)
	var host := (target.host_id if target != null and target.is_satellite else action.wheel_id)
	var v := _view_of(host)
	if v == null or v.intent.is_empty():
		return
	var what := TextDb.t(card, "display_name").to_upper() if card != null else tr("NUDGE")
	# ANIM-R2 E9: plain words ("IF JOLT" was cryptic). ANIM-R3 A6j: says who plays it.
	# ANIM-R6 A13: on the tag's tape with a card mark ("YOUR JOLT", beside WAS), not as a chip
	# among the enemy's own results ("YOU PLAY JOLT" there read as the enemy playing it).
	v.play_note = what
	v.intent["tooltip"] = tr("Your %s, if you play it:") % what + "\n" + String(v.intent.get("tooltip", ""))
	v.queue_redraw()


func _show_respin_odds() -> void:
	if not engine.has_fight():
		return
	var was := _forecast_tags()
	var cost := engine.resolver.config.respin_ram_cost
	ram_note.set_pending(-cost)
	var chips: Array = [{"text": tr("RESPIN: ODDS"), "color": Palette.INK, "ink": Palette.PAPER}]
	chips.append_array(_odds_chips(engine.state().player))
	_player_view.intent = {"type": -1, "text": tr("Respin for %d RAM") % cost, "chips": chips,
		"tooltip": tr("Respin your wheel for %d RAM: a random result (UNDO stops here). %s") % [cost, odds_text(engine.state().player)]}
	_player_view.queue_redraw()
	_mark_was(was)
	preview_note.clear()
	preview_note.append("Respin your wheel for %d RAM (a random event: UNDO stops here)." % cost)
	preview_note.append(odds_text(engine.state().player))


## The End Turn preview as it stands (GDD 2.10): what every needle lands on and the full
## outcome, on the tags, HP arcs and the RAM bar. The hidden note keeps the text.
func _show_end_turn_preview() -> void:
	if not engine.has_fight():
		return
	var state := engine.state()
	preview_note.clear()
	for v in _views():
		v.was_tag = {}  # ANIM-R5 combat 7: the forecast itself has no "before"
		v.play_note = ""  # ANIM-R6 A13: nor a card being previewed
	if _card_hold and not state.is_over() and not _hold_forecast:
		# ANIM-R4 C6e: the tags wait for the card's spin to land (the notes still read now).
		var held := engine.preview_end_turn()
		for e in held.events:
			if e.has("text") and String(e.get("type", "")) != "pass":
				preview_note.append(String(e["text"]))
		for v in _views():
			v.intent = {}
			v.outcome = {}
			v.queue_redraw()
		ram_note.set_pending(0)
		return
	if state.is_over() or _hold_forecast:
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
			preview_note.append("%s gets %s on a random non-NULL slice (%s)." % [owner.display_name, RC.Status.keys()[e["status"]], odds_text(owner, true)])
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
			random_picks[StringName(String(e.get("target", "")))] = int(e.get("status", RC.Status.NONE))
	# ANIM-R5 combat 8: an INFECT names what it puts on whom on its own tag ("PUTS ☠
	# CORRUPTED ON YOU"), from the replay's own beats (who acted).
	var afflicts := afflict_chips(state, events)
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
		var chips := _chips_for(o, id, state, events)
		var sats := {}
		var landings := {}
		for sat in state.satellites_of(id):
			sats[sat.id] = o.of(sat.id)
			var ls := landing.get_combatant(sat.id)
			var rs := engine.resolver.pointer_readouts(landing, ls if ls != null else sat)
			if not rs.is_empty():
				var sl: SliceData = rs[0]["slice"]
				landings[sat.id] = {"type": sl.slice_type, "tier": int(rs[0]["tier"]),
					"text": "%s (%s)" % [tr(Palette.slice_word(sl.slice_type, corp_of(sat))), tr(String(Palette.TIER_WORDS.get(int(rs[0]["tier"]), "")))]}
		view.satellite_landings = landings
		var d := o.of(id)
		var shown_statuses: Array = d.get("statuses", [])
		if random_picks.has(id):
			shown_statuses = []
			chips = chips.filter(func(ch: Dictionary) -> bool: return not bool(ch.get("status", false)))
			chips.append(random_status_chip(int(random_picks[id]), id == state.player.id))
			chips.append(odds_lead_chip())
			chips.append_array(_odds_chips(c, true))
			chips = ranked_chips(chips)
		if afflicts.has(id):
			chips.append_array(afflicts[id])
			chips = ranked_chips(chips)
		view.outcome = {"hp_after": int(d.get("hp_after", c.hp)), "alive_after": bool(d.get("alive_after", true)),
			"statuses": shown_statuses, "satellites": sats}
		view.intent = {"type": title["type"], "tier": title.get("tier", -1), "text": title["text"], "chips": chips, "tooltip": _chips_tooltip(chips)}
		view.queue_redraw()
	ram_note.set_pending(o.ram_delta)


## ANIM-R4 C6f: the chip for a status a random slice will get: which status (its glyph and
## word) on a random slice, in green when that is good for you and red when bad ("? RANDOM
## STATUS" said neither whose nor which).
## ANIM-R5 combat 8: it says who gets it ("☠ YOU GET CORRUPTED"; "CORRUPTED · RANDOM SLICE"
## with odds after it read as a list to decode), and the odds after it follow a lead chip
## that says what they are (odds_lead_chip).
static func random_status_chip(status: int, on_player: bool) -> Dictionary:
	var good := WheelView.status_good_for_you(status, on_player)
	var word := String(TranslationServer.translate(String(Palette.STATUS_WORDS.get(status, ""))))
	var who := String(TranslationServer.translate("YOU GET %s") if on_player else TranslationServer.translate("GETS %s")) % word
	return {"text": "%s %s" % [Palette.STATUS_GLYPHS.get(status, "?"), who],
		"color": CHIP_GAIN if good else CHIP_LOSS, "ink": Palette.INK if good else Palette.PAPER, "status": true,
		"rank": CHIP_RANK_HP if good else CHIP_RANK_HURTS_YOU,
		"tooltip": String(TranslationServer.translate("Good for you: %s") if good else TranslationServer.translate("Bad for you: %s")) % Codex.status_text(status)}


## ANIM-R5 combat 8: the chip before a random status's odds, saying what they are.
static func odds_lead_chip() -> Dictionary:
	return {"text": String(TranslationServer.translate("ON A RANDOM SLICE:")), "color": Palette.INK, "ink": Palette.PAPER,
		"tooltip": String(TranslationServer.translate("It lands on one slice at random; the odds by slice type follow."))}


## ANIM-R5 combat 8: per acting wheel (id), a chip for each status it puts on another wheel
## in `events` (from `state`): "PUTS ☠ CORRUPTED ON YOU" / "... ON <NAME>", in the colour of
## whose win it is. Who acts comes from the replay's beats (ResolveBeats: the INFECT's
## attacker), so the tag says what the replay shows.
func afflict_chips(state: CombatState, events: Array[Dictionary]) -> Dictionary:
	var out := {}
	var seen := {}
	for b in ResolveBeats.build(state, events, engine.resolver.lookup):
		if b["kind"] != "status" or b["phase"] == "act":
			continue
		var src := StringName(String(b["source"]))
		var tgt := StringName(String(b["target"]))
		if src == &"" or src == tgt:
			continue
		var host := state.get_combatant(src)
		if host != null and host.is_satellite:
			src = host.host_id
		var status := int(b["status"])
		var key := "%s>%s>%d" % [src, tgt, status]
		if seen.has(key):
			continue
		seen[key] = true
		var victim := state.get_combatant(tgt)
		var on_player := victim != null and victim.is_player
		var good := WheelView.status_good_for_you(status, on_player)
		var word := "%s %s" % [Palette.STATUS_GLYPHS.get(status, "?"), tr(String(Palette.STATUS_WORDS.get(status, "")))]
		var text := tr("PUTS %s ON YOU") % word if on_player else tr("PUTS %s ON %s") % [word, _name_of(victim).to_upper() if victim != null else "?"]
		var list: Array = out.get(src, [])
		list.append({"text": text, "color": CHIP_GAIN if good else CHIP_LOSS, "ink": Palette.INK if good else Palette.PAPER, "status": true,
			"rank": CHIP_RANK_HURTS_YOU if on_player and not good else CHIP_RANK_DEALT,
			"beats": ForecastTicks.filter(["status", "absorbed"], StringName(String(b["source"])), tgt),
			"tooltip": String(tr("Good for you: %s") if good else tr("Bad for you: %s")) % Codex.status_text(status)})
		out[src] = list
	return out


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
			parts.append("%s · %s" % [tr(Palette.slice_word(slice.slice_type, corp_of(c))), tr(String(Palette.TIER_WORDS.get(r["tier"], "")))])
		elif rs.size() == 2:
			parts.append("%s %s" % [tr(Palette.slice_word(slice.slice_type, corp_of(c))), tr(String(Palette.TIER_NAMES.get(r["tier"], ""))).to_lower()])
		else:
			parts.append("%s·%s" % [tr(String(Palette.SLICE_NAMES.get(slice.slice_type, "?"))), tr(String(Palette.TIER_NAMES.get(r["tier"], ""))).left(1)])
	return {"type": type, "tier": tier if rs.size() == 1 else -1, "text": " + ".join(parts)}


## Result chips for one combatant (and, on the operative, the run-wide results).
## ANIM-R3 A6b: each chip names the beats that make it happen ("beats": ForecastTicks
## filter), so a held forecast ticks each line as the replay does it.
## ANIM-R6 A4: `events` (the resolve's) give each hit's applied number and where HP losses
## no hit names come from.
func _chips_for(o: CombatOutcome, id: StringName, state: CombatState, events: Array[Dictionary] = []) -> Array:
	var hits := hit_totals(events)
	var self_hp := hp_sources(events)
	var chips: Array = []
	var d := o.of(id)
	if d.is_empty():
		return chips
	var me := state.get_combatant(id)
	var mine_is_player := me != null and me.is_player
	# Who takes the hits: "HITS YOU 14" on an enemy's tag, "HITS <NAME> 12" on yours.
	# ANIM-R6 A4: the number is what the hits take off (after block and shield: the victim's
	# "N BLOCKED" says the rest), and a hit that takes the last HP says so ("HITS YOU 8 → 1
	# LEFT"): every number shown is the one the resolve applies.
	var mine_hits: Dictionary = hits.get(id, {})
	for tgt in mine_hits:
		var victim := state.get_combatant(StringName(String(tgt)))
		var who := tr("YOU") if victim != null and victim.is_player else (_name_of(victim).to_upper() if victim != null else "?")
		var h: Dictionary = mine_hits[tgt]
		chips.append({"text": hit_chip_text(who, int(h["through"]), int(h["applied"])), "color": CHIP_HIT, "ink": Palette.INK,
			"rank": CHIP_RANK_HURTS_YOU if victim != null and victim.is_player else CHIP_RANK_DEALT,
			"tooltip": clamp_tip(int(h["through"]), int(h["applied"])),
			"beats": ForecastTicks.filter(["damage", "evaded"], id, StringName(String(tgt)))})
	# ANIM-R6 A4: this wheel's own HP loss is never summed again on its own tag ("YOU TAKE 11"
	# beside "HITS YOU 8" disagreed; the NEXT plate under its HP carries the total): only the
	# losses no hit names say where they come from (a CORRUPTED slice's bite), and heals.
	var bite := int(self_hp.get(id, {}).get("corrupted", 0))
	if bite > 0:
		var word := "%s %s" % [Palette.STATUS_GLYPHS.get(RC.Status.CORRUPTED, "?"), tr(String(Palette.STATUS_WORDS.get(RC.Status.CORRUPTED, "")))]
		chips.append({"text": (tr("%s BITES YOU %d") if mine_is_player else tr("%s BITES IT %d")) % [word, bite], "color": CHIP_LOSS, "ink": Palette.PAPER,
			"rank": CHIP_RANK_HURTS_YOU if mine_is_player else CHIP_RANK_HP, "beats": ForecastTicks.filter(["corrupted"], &"", id, true)})
	var healed := int(self_hp.get(id, {}).get("heal", 0))
	if healed > 0:
		chips.append({"text": tr("+%d HP") % healed, "color": CHIP_GAIN, "ink": Palette.INK, "rank": CHIP_RANK_HP,
			"beats": ForecastTicks.filter(["heal"], &"", id, true)})
	# Anything else that moves its HP (a boss phase's refill): said as an HP change.
	var rest := int(d["hp_after"]) - int(d["hp_before"]) + int(self_hp.get(id, {}).get("hit", 0)) + bite - healed
	if rest != 0:
		chips.append({"text": tr("HP %s") % signed(rest), "color": CHIP_GAIN if rest > 0 else CHIP_LOSS, "ink": Palette.INK if rest > 0 else Palette.PAPER,
			"rank": CHIP_RANK_HP})
	# What block and shield soak, beside the loss (H24: 14 hit, 11 taken read as a sum to do).
	if int(d.get("soaked", 0)) > 0:
		chips.append({"text": tr("%d BLOCKED") % int(d["soaked"]), "color": CHIP_GUARD, "ink": Palette.INK,
			"beats": ForecastTicks.filter(["damage"], &"", id)})
	for key in ["block", "shield"]:
		var delta := int(d[key + "_after"]) - int(d[key + "_before"])
		if delta != 0:
			chips.append({"text": "%s %s" % [signed(delta), tr("BLOCK") if key == "block" else tr("SHIELD")], "color": CHIP_GUARD, "ink": Palette.INK,
				"beats": ForecastTicks.filter([key, "damage"], &"", id)})
	var ev := int(d["evade_after"]) - int(d["evade_before"])
	if ev != 0:
		chips.append({"text": tr("%s EVADE") % signed(ev), "color": CHIP_GUARD, "ink": Palette.INK,
			"beats": ForecastTicks.filter(["evade", "evaded"], &"", id)})
	if int(d["resistance_after"]) != int(d["resistance_before"]):
		chips.append({"text": tr("RESIST %d→%d") % [int(d["resistance_before"]), int(d["resistance_after"])], "color": CHIP_RESIST, "ink": Palette.INK})
	if bool(d["breached"]):
		chips.append({"text": tr("HUB BREACH"), "color": CHIP_RESIST, "ink": Palette.INK, "beats": ForecastTicks.filter(["breach"], &"", id)})
	var mine := id == state.player.id
	for st in d["statuses"]:
		var after := int(st["after"])
		var tag: String = tr(String(Palette.STATUS_WORDS.get(after, ""))) if after != RC.Status.NONE else tr("CLEARS %s") % tr(String(Palette.STATUS_WORDS.get(int(st["before"]), "")))
		# ANIM-R4 C6f: green when it is good for you, red when bad (a status landing on your
		# wheel, a clear of a bad one...).
		var good := WheelView.status_good_for_you(after, mine) if after != RC.Status.NONE else not WheelView.status_good_for_you(int(st["before"]), mine)
		chips.append({"text": "%s %s" % [Palette.STATUS_GLYPHS.get(after, "×"), tag], "color": CHIP_GAIN if good else CHIP_LOSS,
			"ink": Palette.INK if good else Palette.PAPER, "status": true, "beats": ForecastTicks.filter(["status", "absorbed"], &"", id)})
	# ANIM-R5 combat 3: the operative going down is the fight's DEFEAT: one chip says it (DOWN
	# and DEFEAT side by side said it twice).
	var lost_here := id == state.player.id and o.outcome == CombatState.Outcome.DEFEAT
	if bool(d["alive_before"]) and not bool(d["alive_after"]) and not lost_here:
		chips.append({"text": tr("DOWN"), "color": CHIP_LOSS, "ink": Palette.PAPER, "rank": CHIP_RANK_HP, "beats": ForecastTicks.filter(["died"], &"", id)})
	if int(d.get("phase_after", 0)) != int(d.get("phase_before", 0)):
		chips.append({"text": tr("PHASE %d") % (int(d["phase_after"]) + 1), "color": CHIP_RESIST, "ink": Palette.INK, "beats": ForecastTicks.filter(["phase"], &"", id)})
	if int(d.get("pointers_after", 0)) > int(d.get("pointers_before", 0)):
		chips.append({"text": tr("+%d NEEDLE") % (int(d["pointers_after"]) - int(d["pointers_before"])), "color": CHIP_RESIST, "ink": Palette.INK,
			"beats": ForecastTicks.filter(["phase"], &"", id)})
	if bool(d.get("slices_changed", false)):
		chips.append({"text": tr("NEW SLICES"), "color": CHIP_RESIST, "ink": Palette.INK})
	# Satellites docked here: what they deal and take.
	for sat in state.satellites_of(id):
		var sd := o.of(sat.id)
		if sd.is_empty():
			continue
		var name := _name_of(sat).to_lower()
		var sat_hits: Dictionary = hits.get(sat.id, {})
		for tgt in sat_hits:
			# ANIM-R6 A4: whom it hits and what that takes off, as its host's hits say it.
			var victim := state.get_combatant(StringName(String(tgt)))
			var who := tr("YOU") if victim != null and victim.is_player else (_name_of(victim).to_upper() if victim != null else "?")
			var h: Dictionary = sat_hits[tgt]
			chips.append({"text": "%s %s" % [name, hit_chip_text(who, int(h["through"]), int(h["applied"]))], "color": CHIP_HIT, "ink": Palette.INK,
				"rank": CHIP_RANK_HURTS_YOU if victim != null and victim.is_player else CHIP_RANK_DEALT, "tooltip": clamp_tip(int(h["through"]), int(h["applied"])),
				"beats": ForecastTicks.filter(["damage", "evaded"], sat.id, StringName(String(tgt)))})
		if bool(sd["alive_before"]) and not bool(sd["alive_after"]):
			chips.append({"text": tr("%s DOWN") % name, "color": CHIP_LOSS, "ink": Palette.PAPER, "rank": CHIP_RANK_HP, "beats": ForecastTicks.filter(["died"], &"", sat.id)})
		elif int(sd["hp_after"]) != int(sd["hp_before"]):
			var shp := int(sd["hp_after"]) - int(sd["hp_before"])
			chips.append({"text": tr("%s %s HP") % [name, signed(shp)], "color": CHIP_LOSS if shp < 0 else CHIP_GAIN, "ink": Palette.PAPER if shp < 0 else Palette.INK,
				"rank": CHIP_RANK_HP, "beats": ForecastTicks.filter(ResolveBeats.HP_KINDS, &"", sat.id, true)})
		for key in ["block", "shield"]:
			var sdelta := int(sd[key + "_after"]) - int(sd[key + "_before"])
			if sdelta != 0:
				chips.append({"text": "%s %s %s" % [name, signed(sdelta), tr("BLOCK") if key == "block" else tr("SHIELD")], "color": CHIP_GUARD, "ink": Palette.INK,
					"beats": ForecastTicks.filter([key, "damage"], &"", sat.id)})
		for st in sd["statuses"]:
			var sw: String = tr(String(Palette.STATUS_WORDS.get(int(st["after"]), ""))) if int(st["after"]) != RC.Status.NONE else tr("CLEARED")
			chips.append({"text": "%s %s %s" % [name, Palette.STATUS_GLYPHS.get(int(st["after"]), "×"), sw], "color": CHIP_STATUS, "ink": Palette.INK, "status": true,
				"beats": ForecastTicks.filter(["status", "absorbed"], &"", sat.id)})
		if int(sd.get("dock_after", -1)) != int(sd.get("dock_before", -1)):
			chips.append({"text": tr("%s MOVES") % name, "color": CHIP_RESIST, "ink": Palette.INK})
	if id == state.player.id:
		if o.ram_delta != 0:
			chips.append({"text": tr("RAM %s") % signed(o.ram_delta), "color": CHIP_GUARD, "ink": Palette.INK, "beats": ForecastTicks.filter(["ram"])})
		if o.cards_drawn > 0:
			chips.append({"text": tr("DRAW %d") % o.cards_drawn, "color": CHIP_RUN, "ink": Palette.INK, "beats": ForecastTicks.filter(["draw"])})
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
			chips.append({"text": tr("+%d DRONE") % o.drones_gained, "color": CHIP_STATUS, "ink": Palette.INK, "beats": ForecastTicks.filter(["spawn"])})
		if o.double_nudge_next:
			chips.append({"text": tr("2× NUDGE CARDS NEXT"), "color": CHIP_RUN, "ink": Palette.INK})
		if o.outcome == CombatState.Outcome.VICTORY:
			chips.append({"text": tr("VICTORY"), "color": CHIP_GAIN, "ink": Palette.INK, "beats": ForecastTicks.filter(["end"])})
		elif o.outcome == CombatState.Outcome.DEFEAT:
			chips.append({"text": tr("DEFEAT"), "color": CHIP_LOSS, "ink": Palette.PAPER, "rank": CHIP_RANK_HURTS_YOU, "beats": ForecastTicks.filter(["end"])})
	return ranked_chips(chips)


## ANIM-R6 A4: per attacker, per victim, what its hits in `events` take off: {src: {tgt:
## {through (after block and shield), applied (the HP it really took: less when the victim
## had fewer HP left)}}}. Evaded hits take nothing and are left out.
static func hit_totals(events: Array[Dictionary]) -> Dictionary:
	var out := {}
	for e in events:
		if String(e.get("type", "")) != "damage":
			continue
		var src := StringName(String(e.get("attacker", "")))
		var tgt := StringName(String(e.get("target", "")))
		if src == &"" or tgt == &"":
			continue
		var per: Dictionary = out.get(src, {})
		var h: Dictionary = per.get(tgt, {"through": 0, "applied": 0})
		h["through"] = int(h["through"]) + maxi(0, int(e.get("amount", 0)) - int(e.get("blocked", 0)) - int(e.get("shielded", 0)))
		h["applied"] = int(h["applied"]) + int(e.get("hp_damage", 0))
		per[tgt] = h
		out[src] = per
	return out


## ANIM-R6 A4: per combatant, what moves its HP in `events`: {id: {hit (HP its hits took),
## corrupted (its CORRUPTED slices' bites), heal}}.
static func hp_sources(events: Array[Dictionary]) -> Dictionary:
	var out := {}
	for e in events:
		var t := String(e.get("type", ""))
		var key := ""
		var amount := 0
		match t:
			"damage":
				key = "hit"
				amount = int(e.get("hp_damage", 0))
			"corrupted":
				key = "corrupted"
				amount = int(e.get("amount", 0))
			"heal":
				key = "heal"
				amount = int(e.get("amount", 0))
		if key == "":
			continue
		var id := StringName(String(e.get("target", "")))
		var d: Dictionary = out.get(id, {"hit": 0, "corrupted": 0, "heal": 0})
		d[key] = int(d[key]) + amount
		out[id] = d
	return out


## ANIM-R6 A4: a hit chip's words: "HITS YOU 8", or, when the victim had fewer HP left than it
## gets through, "HITS YOU 8 → 1 LEFT" (the HP it really takes; never a sum to do).
static func hit_chip_text(who: String, through: int, applied: int) -> String:
	if applied < through:
		return String(TranslationServer.translate("HITS %s %d → %d LEFT")) % [who, through, applied]
	return String(TranslationServer.translate("HITS %s %d")) % [who, through]


## ANIM-R6 A4: the note a clamped hit's chip carries ("" when it isn't clamped).
static func clamp_tip(through: int, applied: int) -> String:
	if applied >= through:
		return ""
	return String(TranslationServer.translate("It gets %d through, but only %d HP are left to take.")) % [through, applied]


## ANIM-R1 C8: chips in order of importance, stable within a rank: damage to you, damage
## dealt, HP changes, then guards, statuses, odds and the rest. A tag that folds its
## overflow ("+N MORE") hides the least important ones.
const CHIP_RANK_HURTS_YOU := 0
const CHIP_RANK_DEALT := 1
const CHIP_RANK_HP := 2
const CHIP_RANK_REST := 3


static func ranked_chips(chips: Array) -> Array:
	var out: Array = []
	for r in CHIP_RANK_REST + 1:
		for c in chips:
			if int((c as Dictionary).get("rank", CHIP_RANK_REST)) == r:
				out.append(c)
	return out


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
		return TranslationServer.translate("What this wheel's needles land on. Nothing else changes this turn.")
	var parts := PackedStringArray()
	for c in chips:
		parts.append(String(c["text"]))
	# ANIM-R4 C6f: a chip's own note (a random status: whose win it is and what it does).
	var notes := PackedStringArray()
	for c in chips:
		if String(c.get("tooltip", "")) != "":
			notes.append(String(c["tooltip"]))
	var extra := ("\n" + "\n".join(notes)) if not notes.is_empty() else ""
	return String(TranslationServer.translate("When you SEND IT: %s.")) % ", ".join(parts) + extra + "\n" \
		+ String(TranslationServer.translate("HITS = damage this wheel deals and to whom; HP = health change; BLOCK / SHIELD soak damage; glyphs = statuses on a slice (dashed ring on the wheel).")) + "\n" \
		+ String(TranslationServer.translate("The dots: ●○○ half power (a needle near a slice's edge), ●●○ good aim, ●●● perfect aim (dead centre)."))


# --- Stickers and hints ---------------------------------------------------------------

## Stickers by the player spinner: RESPIN and UNDO (nudges are the arrows on every
## wheel; cards are aimed by dragging).
func _build_stickers() -> void:
	var specs := [
		["respin", "RESPIN", Palette.STICKER_PINK, 3.0, respin],
		["undo", "UNDO", Palette.NOTE_PAPER, -3.0, rewind],
	]
	for sp in specs:
		var b := StickerButton.new(tr(String(sp[1])), sp[2], sp[3])  # ANIM-R6 A12: translated from the first frame
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
	_sync_undo_tip()


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
	shown_tip(_respin_button, tr("Respin your wheel for %d RAM: a random result (UNDO stops here).") % cost)
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


# --- Motion (Animation pass ANIM-2 / ANIM-3) -----------------------------------------------
# The engine's state is final the moment an action returns; motion replays its events on
# top of it (the same `events` the engine returned: the replay never runs a rule, GDD
# 2.10). Headless, under reduce effects or for a disabled entry nothing is captured or
# played and the screen shows the end state at once. Any press during the SEND IT
# sequence skips to that end state.

## Emitted when the SEND IT sequence (or a skip) has brought the screen to the end state.
signal motion_settled

## The overlay the replay draws on (numbers, hit lines, stamps, flights, piles).
var fx_layer: CombatFxLayer
## Captured before an action goes to the engine (only while motion plays).
var _before_action: CombatState = null
var _pending_play: Dictionary = {}
var _pending_discard: Array = []
var _rewind_from: CombatState = null
## Where a dragged card was let go (INF = not dragged).
var _drop_at: Vector2 = Vector2.INF
## The SEND IT sequence: its tween, when it started and how long it runs.
var _seq: Tween = null
var _seq_started: float = 0.0
var _seq_total: float = 0.0
## Other replay steps waiting to play (card effects after a flight), killed by a skip.
var _motion_tweens: Array[Tween] = []
## Floating numbers stacked on each view during a replay (view -> count).
var _numbers_on: Dictionary = {}
## The aim line's draw-in (0..1) and its tween.
var _aim_draw: float = 1.0
var _aim_tween: Tween = null
var _aim_target: Vector2 = Vector2.INF
## Hand slot kept open for a card in flight (-1 = none), its gap node, and hand indices of
## cards gliding back from a cancelled drag.
var _hold_slot: int = -1
var _gap: Control = null
var _gap_waiting: bool = false
var _returning: Dictionary = {}
## The deal-in of the new hand waits for the draw beat.
var _deal_waiting: bool = false
## A floating number rises at most this share of the hub room (it stays in the hub).
const NUMBER_RISE_SHARE := 0.7


func _process(_delta: float) -> void:
	if _seq != null:
		# ART-0 C (art pass W3 / W9s, §10): the replay runs at the resolve speed; holding
		# fast-forward speeds it further, frame by frame.
		_apply_resolve_speed()
	# A gap closes once the cursor is off the hand (the hand never moves under it).
	if _gap_waiting and is_instance_valid(_gap):
		if not _hand_box.get_global_rect().has_point(get_global_mouse_position()):
			_close_gap()
	elif not _gap_waiting and _seq == null:
		set_process(false)


## ART-0 C (ported from art-pass W3 / W9s): whether this scene has changed the engine's
## clock for a replay, and what the clock was.
var _speeding: bool = false
var _base_time_scale: float = 1.0


## The SEND IT replay's clock factor now: Motion.resolve_time_scale_now() (1 at 1x, 0.5 at
## 2x, at most FAST_FORWARD_TIME_SCALE while fast-forward is held). The replay's schedule
## stays in 1x seconds (one hit at a time holds at every speed); the engine's clock runs it
## faster, so every tween, sprite and timer of the replay keeps its place. Instant never
## plays one.
static func resolve_clock() -> float:
	return Motion.resolve_time_scale_now()


func _apply_resolve_speed() -> void:
	var k := resolve_clock()
	if k <= 0.0:
		return
	if not _speeding:
		if is_equal_approx(k, 1.0):
			return
		_base_time_scale = Engine.time_scale
		_speeding = true
	Engine.time_scale = _base_time_scale / k


## The engine's clock back to what it was (the replay ended, was skipped, or the scene left).
func _restore_time_scale() -> void:
	if not _speeding:
		return
	Engine.time_scale = _base_time_scale
	_speeding = false


## True while any combat motion still plays (the SEND IT sequence, flights, wheels).
func motion_busy() -> bool:
	if _seq != null or (fx_layer != null and fx_layer.busy()):
		return true
	for v in _views():
		if v.motion_busy():
			return true
	return false


## Seconds the SEND IT sequence still needs (0 when none plays).
func motion_seconds_left() -> float:
	if _seq == null:
		return 0.0
	return maxf(0.0, _seq_total - (Time.get_ticks_msec() / 1000.0 - _seq_started))


## Brings every motion to its end state at once (a skip): the sequence, flights, wheels,
## the hand's deal and the RAM chips. The state was final all along.
func skip_motion() -> void:
	var had := _seq != null
	_restore_time_scale()
	if _seq != null and _seq.is_valid():
		_seq.kill()
	_seq = null
	_hold_city(false)
	for tw in _motion_tweens:
		if tw != null and tw.is_valid():
			tw.kill()
	_motion_tweens.clear()
	if fx_layer != null:
		fx_layer.clear()
	_release_forecast()
	for v in _views():
		# A skip lands: the forecast is already on the tags, which don't flip (C3).
		v.stop_motion()
		v.inverted = false
	_numbers_on.clear()
	_deal_waiting = false
	if _hand_box != null:
		for c in _hand_box.get_children():
			if c is ZineCard:
				(c as ZineCard).finish_deal()
	_returning.clear()
	if is_instance_valid(_gap):
		_gap.queue_free()
	_gap = null
	_gap_waiting = false
	if ram_note != null:
		ram_note.finish_motion()
	_release_card_hold()
	_land_outcome(true)
	if had:
		_dim_hand()
		_show_end_turn_preview()
		motion_settled.emit()


## ANIM-R6 A14: while a SEND IT replays, the arena's city waits to land its bake (the
## wireframe switched to the full city mid-turn); it lands between turns.
func _hold_city(on: bool) -> void:
	if background != null and background.city != null:
		background.city.hold_landing = on


## True while the arena's city waits for the replay to land its bake (tests).
func city_held() -> bool:
	return background != null and background.city != null and background.city.hold_landing


func _skippable() -> bool:
	return _seq != null


## MotionSkip (ANIM-R5): the SEND IT replay plays.
func motion_running() -> bool:
	return _skippable()


## MotionSkip (ANIM-R5): the replay at its end state.
func complete_motion() -> void:
	skip_motion()


## MotionSkip (ANIM-R5): a press on the fight's own controls only ends the replay.
func motion_keeps() -> Array:
	return replay_keeps()


## ANIM-R4 C6e: a card's (or a respin's) spin is turning: the forecast tags wait (hidden)
## until it lands, so they never tell where it lands before it does.
var _card_hold: bool = false


## True when `events` turn a wheel or move its needles (a spin, a respin, a snap, a flip).
static func _spins(events: Array[Dictionary]) -> bool:
	for e in events:
		if String(e.get("type", "")) in ["spin", "respin", "snap", "flip", "orbit", "boss_migrate"]:
			return true
	return false


## The spin has landed (or was skipped): the forecast shows.
func _release_card_hold() -> void:
	if not _card_hold:
		return
	_card_hold = false
	_show_end_turn_preview()


## True while the forecast waits for a card's spin (tests).
func card_forecast_held() -> bool:
	return _card_hold


## The replay is over (played out or skipped): the next turn's forecast goes on the
## views and the status line shows the state's turn. True when anything was held.
func _release_forecast() -> bool:
	if not _hold_forecast and _shown_turn < 0 and _replay_start_hp < 0:
		return false
	_hold_forecast = false
	_shown_turn = -1
	# ANIM-R6 A5 / A8: the turn has landed: the portrait and the run's top bar show its HP.
	var hp_held := _replay_start_hp >= 0
	_replay_hp = -1
	_replay_start_hp = -1
	if engine.has_fight():
		_sync_portrait(engine.state().player.hp, engine.state().player.max_hp)
	_refresh_status()
	_show_end_turn_preview()
	if hp_held:
		shown_hp_changed.emit()
	return true



static func _has_event(events: Array[Dictionary], type: String) -> bool:
	for e in events:
		if String(e.get("type", "")) == type:
			return true
	return false


## True when the action only nudged (its steps join the wheel's queue).
static func _only_nudges(events: Array[Dictionary]) -> bool:
	var any := false
	for e in events:
		var t := String(e.get("type", ""))
		if t == "nudge":
			any = true
		elif t != "ram":
			return false
	return any


## Sends `action` to the engine; while motion plays, first keeps what the replay needs
## (the state before it, and a played card's copy, slot and target zone).
func _submit(action: CombatAction, from_point: Vector2 = Vector2.INF) -> bool:
	if Motion.animating() and engine.has_fight():
		_before_action = engine.state().duplicate_state()
		if action.type == CombatAction.Type.PLAY_CARD:
			_capture_play(action, from_point)
	_acting = action
	var ok := engine.submit(action)
	_acting = null
	if not ok:
		_before_action = null
		_free_captures(_pending_play, [])
		_pending_play = {}
		_hold_slot = -1
	return ok


## The hand card with hand index `i` (null when none: gaps are not cards).
func _card_node(i: int) -> ZineCard:
	if i < 0 or _hand_box == null:
		return null
	for c in _hand_box.get_children():
		if c is ZineCard and (c as ZineCard).drag_index == i and not c.is_queued_for_deletion():
			return c
	return null


## A copy of hand card `i` for a flight, with where it sits now.
func _card_copy(i: int) -> Dictionary:
	var node := _card_node(i)
	var state := engine.state()
	if node == null or i >= state.hand.size():
		return {}
	var card := engine.content(state.hand[i]) as CardData
	var copy := _make_card(card, i, _hand_scale if _hand_scale > 0.0 else 1.0)
	copy.variant = node.variant
	return {"copy": copy, "rect": node.get_global_rect(), "rot": node.rotation, "exhaust": card.exhaust}


func _capture_play(action: CombatAction, from_point: Vector2) -> void:
	var cap := _card_copy(action.hand_index)
	if cap.is_empty():
		return
	if from_point != Vector2.INF:
		# Dragged: it leaves from where it was let go, upright.
		var r: Rect2 = cap["rect"]
		cap["rect"] = Rect2(from_point - r.size * 0.5, r.size)
		cap["rot"] = 0.0
	var z := _zone_of(action)
	var v := _view_of(z[0])
	cap["to"] = v.zone_center(z[1]) if v != null else (cap["rect"] as Rect2).get_center()
	cap["hub"] = v.global_center() if v != null else Vector2.INF  # ART-2 2C: dissolve A spirals into the hub
	cap["zone"] = z
	_pending_play = cap
	_hold_slot = action.hand_index


func _capture_hand() -> Array:
	var out: Array = []
	for i in engine.state().hand.size():
		var cap := _card_copy(i)
		if not cap.is_empty():
			out.append(cap)
	return out


func _free_captures(play: Dictionary, discard: Array) -> void:
	if play.has("copy") and is_instance_valid(play["copy"]):
		(play["copy"] as Node).free()
	for d in discard:
		if is_instance_valid(d["copy"]):
			(d["copy"] as Node).free()


## Runs `c` after `delay` seconds of motion (a skip drops it).
func _after(delay: float, c: Callable) -> void:
	if delay <= 0.0:
		c.call()
		return
	var tw := create_tween()
	tw.tween_interval(delay)
	tw.tween_callback(c)
	_motion_tweens.append(tw)


## Where the deck and discard piles sit: the two ends of the hand row.
func _deck_spot() -> Vector2:
	var r := _hand_box.get_global_rect()
	# ANIM-R6 A17: far enough in that a card dealt from it, at the hand's size, starts whole on
	# screen (the first card clipped at the left edge as it dealt in).
	var card := ZineCard.STICKER_SIZE * (_hand_scale if _hand_scale > 0.0 else Settings.text_scale) * 0.5
	var half := (CombatFxLayer.PILE_SIZE * Settings.text_scale * 0.5).max(card)
	return Vector2(r.position.x + half.x + STICKER_EDGE, r.end.y - half.y - STICKER_EDGE)


func _discard_spot() -> Vector2:
	var r := _hand_box.get_global_rect()
	# ANIM-R3 A7: far enough inside the hand's row that a discarded card, at the size it
	# lands with, stays off RESPIN / UNDO beside it (flights overlapped them).
	var card := ZineCard.STICKER_SIZE * (_hand_scale if _hand_scale > 0.0 else Settings.text_scale) * CombatFxLayer.DISCARD_SCALE * 0.5
	var half := (CombatFxLayer.PILE_SIZE * Settings.text_scale * 0.5).max(card)
	return Vector2(r.end.x - half.x - STICKER_EDGE, r.end.y - half.y - STICKER_EDGE)


# --- Card targeting (ANIM-3) ---

func _start_aim_motion() -> void:
	for v in _views():
		if not v.valid_zones.is_empty():
			v.start_zone_pulse()
	ram_note.set_aiming(true)
	_aim_target = Vector2.INF


func _stop_aim_motion() -> void:
	if ram_note != null:
		ram_note.set_aiming(false)
	if fx_layer != null:
		fx_layer.hide_reticle()
	if _aim_tween != null and _aim_tween.is_valid():
		_aim_tween.kill()
	_aim_draw = 1.0
	_aim_target = Vector2.INF


## The aim moved to `at` (global): the line draws in again (`aim_line_draw`) and the
## reticle glides there (`target_snap`), for mouse, keys and pad alike.
func _aim_at(at: Vector2) -> void:
	if at == _aim_target:
		return
	_aim_target = at
	fx_layer.aim_reticle(at)
	if _aim_tween != null and _aim_tween.is_valid():
		_aim_tween.kill()
	if not Motion.live(&"aim_line_draw"):
		_aim_draw = 1.0
		_aim_line.queue_redraw()
		return
	var e := Motion.entry(&"aim_line_draw")
	_aim_draw = 0.0
	_aim_tween = create_tween()
	_aim_tween.tween_method(_set_aim_draw, 0.0, 1.0, Motion.seconds(&"aim_line_draw")).set_ease(e.ease).set_trans(e.trans)


func _set_aim_draw(v: float) -> void:
	_aim_draw = v
	_aim_line.queue_redraw()


## A drag let go on nothing (or on no legal target): the card glides home to its slot
## (`drag_cancel_return`), then shows there again; the aim ends.
func _cancel_drag(hand_index: int, at: Vector2) -> void:
	var node := _card_node(hand_index)
	var cap := _card_copy(hand_index) if Motion.animating() and node != null else {}
	cancel_selection()
	if node == null or cap.is_empty():
		return
	_returning[hand_index] = true
	node.modulate.a = 0.0
	fx_layer.return_card(cap["copy"], at, node.get_global_rect(), node.rotation, _returned.bind(hand_index, node))


func _returned(hand_index: int, node: ZineCard) -> void:
	_returning.erase(hand_index)
	if is_instance_valid(node):
		node.modulate.a = 1.0
	_dim_hand()


## The gap a played card leaves (see _build_hand).
func _add_gap(s: float) -> void:
	_gap = Control.new()
	_gap.name = "HandGap"
	_gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_gap.custom_minimum_size = ZineCard.STICKER_SIZE * s
	_hand_box.add_child(_gap)


## The played card has landed: its gap closes now, or once the cursor leaves the hand.
func _release_gap() -> void:
	_hold_slot = -1
	if not is_instance_valid(_gap):
		return
	_gap_waiting = true
	set_process(true)


func _close_gap() -> void:
	_gap_waiting = false
	var gap := _gap
	_gap = null
	if not is_instance_valid(gap):
		return
	if not Motion.live(&"hand_reflow"):
		gap.queue_free()
		return
	var e := Motion.entry(&"hand_reflow")
	var tw := gap.create_tween()
	tw.tween_property(gap, "custom_minimum_size:x", 0.0, Motion.seconds(&"hand_reflow")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(gap.queue_free)


## Deals hand cards from index `from` in from the deck pile with a fan (`card_draw`: its
## delay staggers them, its amplitude spreads the fan in degrees).
func _deal_hand(from: int) -> void:
	_deal_waiting = false
	var cards: Array[ZineCard] = []
	for c in _hand_box.get_children():
		if c is ZineCard and (c as ZineCard).drag_index >= from:
			cards.append(c)
	if cards.is_empty():
		return
	var pile := _deck_spot()
	var n := cards.size()
	var stagger := Motion.delay_of(&"card_draw")
	fx_layer.pile(pile, stagger * n + Motion.seconds(&"card_draw"))
	for k in n:
		var fan := (k - (n - 1) * 0.5) * Motion.amplitude(&"card_draw")
		cards[k].deal_from(pile, fan, stagger * k)


# --- Replays (ANIM-2) ---

## A player action's replay: a played card flies to its zone and stamps (then its effect
## plays), wheels turn / step / flip, needles move, and the effect's beats (numbers,
## stamps, deaths) play once the card has landed.
func _play_action(before: CombatState, state: CombatState, events: Array[Dictionary], play: Dictionary) -> void:
	var delay := 0.0
	if play.has("copy"):
		delay = fx_layer.play_card(play["copy"], play["rect"], float(play["rot"]), play["to"], bool(play["exhaust"]), _release_gap, play.get("hub", Vector2.INF))
	else:
		_hold_slot = -1
	var lands := _animate_wheels(before, events, delay)
	if _card_hold:
		# ANIM-R4 C6e: the forecast comes back once the spin has landed (never a spoiler of
		# where a card's or a respin's spin lands while it turns).
		_after(maxf(lands, delay), _release_card_hold)
	var beats := ResolveBeats.build(before, events, engine.resolver.lookup)
	var sch := ResolveBeats.schedule(beats, Motion.seconds(&"resolve_sequence"), Motion.seconds(&"resolve_beat"), 0.0, 0.0, 0.0,
		death_lead(), beat_timing())
	var times: PackedFloat32Array = sch["times"]
	for k in beats.size():
		var b := beats[k]
		if b["kind"] in ["spin", "nudge", "flip", "snap", "land"]:
			continue  # the wheels replay those
		if b["kind"] == "draw":
			_hide_new_cards(state.hand.size() - int(b["amount"]))
		_after(delay + times[k], _play_beat.bind(b, before, state))


## Wheels replay what the action did to them: nudges step through the queue, spins and
## respins turn from the old rotation, flips squash, moved needles glide, all after
## `delay` (the card's flight). Returns when the last turn or needle move lands (s from
## now; 0 when none plays).
func _animate_wheels(before: CombatState, events: Array[Dictionary], delay: float) -> float:
	var lands := 0.0
	for v in _views():
		if v.combatant == null:
			continue
		var c0 := before.get_combatant(v.combatant.id)
		if c0 == null:
			continue
		var nudges: Array[Dictionary] = []
		var kind := ""
		for e in events:
			if StringName(String(e.get("target", ""))) != v.combatant.id:
				continue
			match String(e.get("type", "")):
				"nudge":
					nudges.append(e)
				"spin", "snap":
					if kind != "respin":
						kind = "spin"
				"respin":
					kind = "respin"
				"flip":
					v.play_flip(delay)
				"nudge_absorbed":
					fx_layer.nudge_resist(v.pointer_spot(0), tr("RESIST"), delay)  # ART-2 2C: nudge + resistance
		var moved := c0.wheel.rotation != v.combatant.wheel.rotation or c0.wheel.inner_rotation != v.combatant.wheel.inner_rotation
		if kind == "" and not nudges.is_empty() and delay <= 0.0:
			for e in nudges:
				v.play_nudge(int(e.get("ring", RC.RingScope.OUTER)), int(e.get("direction", 1)))
			v.sync_nudges()
		elif moved:
			var id := &"wheel_respin" if kind == "respin" else &"wheel_spin"
			if kind == "" and not nudges.is_empty():
				id = &"wheel_nudge"
			lands = maxf(lands, v.play_turn(id, float(c0.wheel.rotation), float(c0.wheel.inner_rotation), delay))
		if Array(c0.wheel.pointer_ticks) != Array(v.combatant.wheel.pointer_ticks):
			lands = maxf(lands, v.play_pointers(Array(c0.wheel.pointer_ticks), &"pointer_migrate", false, delay))
	return lands


func _hide_new_cards(from: int) -> void:
	if not Motion.live(&"card_draw"):
		return
	_deal_waiting = true
	for c in _hand_box.get_children():
		if c is ZineCard and (c as ZineCard).drag_index >= from:
			(c as ZineCard).modulate.a = 0.0


## The SEND IT sequence: the old hand to the discard pile; the needles latch (precision
## landings); every resolve event on its beat in the engine's order (pulses, hit lines,
## numbers, HP drains, stamps, deaths); the turn start (wheels spin to the next landing,
## needles move, RAM refills, the new hand deals in); the LAST TURN plate. Fits
## `resolve_sequence` seconds at 1x; any press skips to the end.
## ANIM-R1 C5: the landed slices pulse and hold (`resolve_landing_hold`) before anything
## resolves; hits fly from the attacker's slice to the victim's HP ring, their numbers
## travel into the HP counter; the result holds (`resolve_result_hold`) under THIS TURN
## with LAST TURN and NO DAMAGE / ALL BLOCKED stamps before the wheels turn on; the
## forecast flips in (NEXT TURN) when it ends.
func _play_resolve_sequence(before: CombatState, after: CombatState, events: Array[Dictionary], discard: Array) -> void:
	if not Motion.live(&"resolve_sequence"):
		_free_captures({}, discard)
		_release_forecast()
		return
	# ANIM-R5 combat 5: a wheel going down acts before its HP reaches 0 (same moment).
	var beats := ResolveBeats.doomed_first(before, ResolveBeats.build(before, events, engine.resolver.lookup))
	var sch := sequence_schedule(beats)
	var times: PackedFloat32Array = sch["times"]
	var result_at := float(sch["result_at"])
	var hold := Motion.seconds(&"resolve_result_hold")
	# ANIM-R3 A6a: a wheel every hit of which was soaked says ALL BLOCKED on its last hit's
	# impact (not later); the result stamps the rest (NO DAMAGE).
	_impact_stamped.clear()
	var stamps := result_stamps(beats, before)
	for id in stamps:
		if String(stamps[id]) != tr("ALL BLOCKED"):
			continue
		for k in range(beats.size() - 1, -1, -1):
			var b := beats[k]
			if b["phase"] != "turn_start" and ResolveBeats.is_hit(b) and StringName(String(b["target"])) == id:
				b["final_stamp"] = stamps[id]
				b["final_hold"] = maxf(Motion.seconds(&"number_float"), result_at + hold - times[k] - CombatFxLayer.impact_seconds())
				_impact_stamped[id] = true
				break
	# The screen goes back to where SEND IT was pressed: the wheels as they landed, the
	# HP they had. ANIM-R3 A6b: the forecast that showed then stays (its lines tick as the
	# replay does them, then it fades); the next one is withheld.
	var fade_at := float(sch["spin_at"]) if float(sch["spin_at"]) >= 0.0 else result_at + hold
	var cap := result_at
	for v in _views():
		if v.combatant == null:
			continue
		var c0 := before.get_combatant(v.combatant.id)
		if c0 == null:
			continue
		# The view's own copy: statuses landing mid-replay mark its slices (A6j).
		v.shown_state = c0.duplicate_state()
		v.shown_satellites = before.satellites_of(c0.id)
		v.anim_hp = c0.hp
		v.replaying = true
		v.last_turn_shown = 0.0
		v.hold_forecast_tag(_held_tags.get(c0.id, {}))
		if not v.replay_tag.is_empty():
			var ticks := ForecastTicks.schedule(v.replay_tag.get("chips", []), beats, times, beat_timing(), cap)
			for i in ticks:
				_after_seq(float(ticks[i]), v.tick_chip.bind(int(i)))
			_after_seq(fade_at, v.fade_replay_tag)
		v.queue_redraw()
	_held_tags.clear()
	ram_note.hold(before.ram)
	_hide_new_cards(0)
	var discard_spot := _discard_spot()
	var stagger := Motion.delay_of(&"card_draw")
	if not discard.is_empty():
		fx_layer.pile(discard_spot, stagger * discard.size() + Motion.seconds(&"card_discard"))
	for k in discard.size():
		fx_layer.discard_card(discard[k]["copy"], discard[k]["rect"], float(discard[k]["rot"]), discard_spot, stagger * k)
	_numbers_on.clear()
	_seq = create_tween().set_parallel(true)
	_hold_city(true)  # ANIM-R6 A14: the city never switches in mid-replay
	_seq_started = Time.get_ticks_msec() / 1000.0
	_apply_resolve_speed()  # ART-0 C: the resolve speed from the first frame
	set_process(true)
	var end_at := outcome_time(beats, times)
	_seq_total = maxf(float(sch["total"]), end_at)
	for k in beats.size():
		_seq.tween_callback(_play_beat.bind(beats[k], before, after)).set_delay(beat_delay(beats, times, k, end_at))
	_seq.tween_callback(_show_result.bind(beats, before, after)).set_delay(result_at)
	for c in _seq_calls:
		_seq.tween_callback(c[1]).set_delay(float(c[0]))
	_seq_calls.clear()
	_seq.tween_callback(_finish_sequence).set_delay(_seq_total)


## Calls queued for the SEND IT sequence being built ([seconds, callable]).
var _seq_calls: Array = []
## ANIM-R3 A6a: wheels whose ALL BLOCKED stamped on a hit's impact (the result doesn't
## stamp them again).
var _impact_stamped: Dictionary = {}
## ANIM-R3 A6b: the forecast tags showing when SEND IT was pressed (view id -> tag), held
## for the replay.
var _held_tags: Dictionary = {}


func _after_seq(seconds: float, c: Callable) -> void:
	_seq_calls.append([seconds, c])


## When each beat of a SEND IT plays (ResolveBeats.schedule with the sequence's budget,
## the beat gap, the landing hold, the result hold, a wheel death's wait for its HP at 0,
## and a tail for the spin to the next landing).
static func sequence_schedule(beats: Array[Dictionary]) -> Dictionary:
	var spin_time := maxf(WheelView.spin_seconds(&"wheel_respin", RC.TICKS * SPIN_TICKS_TYPICAL),
		Motion.delay_of(&"enemy_turn_spin") + WheelView.spin_seconds(&"enemy_turn_spin", RC.TICKS * SPIN_TICKS_TYPICAL))
	return ResolveBeats.schedule(beats, Motion.seconds(&"resolve_sequence"), Motion.seconds(&"resolve_beat"), spin_time,
		Motion.seconds(&"resolve_landing_hold"), Motion.seconds(&"resolve_result_hold"), death_lead(), beat_timing())


## The replay's timing (ANIM-R2, ResolveBeats.schedule): hits `hit_line` apart (never two
## projectiles at once), their impact, a partly blocked hit's absorb, a number's travel
## into the HP counter and the roll, and the break's wait at HP 0. ANIM-R4 C6a: the other
## side's hits wait for every roll plus `resolve_side_gap`; another attacker on the same
## side (a drone, a satellite) waits `resolve_attacker_gap`.
static func beat_timing() -> Dictionary:
	var arrive := number_arrive()
	return {"hit_gap": Motion.seconds(&"hit_line"), "impact": CombatFxLayer.impact_seconds(), "absorb": Motion.seconds(&"hit_absorb"),
		"settle": arrive + Motion.seconds(&"hp_drain"),
		"arrive": arrive, "break_delay": Motion.delay_of(&"enemy_break"),
		"side_gap": Motion.seconds(&"resolve_side_gap"), "attacker_gap": Motion.seconds(&"resolve_attacker_gap")}


## How long a wheel's death waits after the hit that killed it (C5f: its HP is seen at 0
## first): the hit's number travelling into the HP counter, the HP rolling down, then
## `enemy_break`'s delay at 0.
static func death_lead() -> float:
	return number_arrive() + Motion.seconds(&"hp_drain") + Motion.delay_of(&"enemy_break")


## ANIM-R6 D8: how long a hit's number takes to travel into the HP counter: its delay and
## seconds while `number_to_hp` plays, 0 when it doesn't (switched off, reduce effects,
## headless: the number is in at once). "arrive", "settle" and the death's lead all count
## it the same way (settle and the lead counted its time even when it did not play).
static func number_arrive() -> float:
	return Motion.delay_of(&"number_to_hp") + Motion.seconds(&"number_to_hp") if Motion.live(&"number_to_hp") else 0.0


## ANIM-R5 combat 1: when the outcome (VICTORY / DEFEAT) lands: at its own beat, but never
## before every HP roll of the resolve has ended (DEFEAT stamped while the HP still read 1).
## -1 when the beats end no fight.
## ANIM-R6 A3: the end beat counts in any phase (a fight that ends at the turn's start, its
## ON_TURN_START trigger's kill, landed its outcome at 0 s), and waits for every HP roll before
## it, whatever its phase.
static func outcome_time(beats: Array[Dictionary], times: PackedFloat32Array) -> float:
	var timing := beat_timing()
	var end := -1
	for k in mini(beats.size(), times.size()):
		if beats[k]["kind"] == "end":
			end = k
	if end < 0:
		return -1.0
	var settled := 0.0
	for k in end + 1:
		settled = maxf(settled, times[k] + ResolveBeats.settle_after(beats[k], timing))
	return maxf(times[end], settled)


## ANIM-R6 A3: when beat `k` of `beats` plays in the replay (`times` from sequence_schedule,
## `end_at` from outcome_time): the end beat at the outcome's time, every other at its own;
## never negative.
static func beat_delay(beats: Array[Dictionary], times: PackedFloat32Array, k: int, end_at: float) -> float:
	var t := times[k] if k < times.size() else 0.0
	if beats[k]["kind"] == "end":
		t = maxf(t, end_at)
	return maxf(0.0, t)


## A turn-start respin runs two to three turns (the core adds two full turns and a roll):
## the sequence keeps room for the longest.
const SPIN_TICKS_TYPICAL := 3.0


## The result holds (ANIM-R1 C5d/e): THIS TURN over each wheel, the LAST TURN plates slide
## up, and a wheel whose HP this turn didn't change stamps NO DAMAGE (ALL BLOCKED when it
## was hit and every hit was soaked or evaded), before the wheels turn on.
func _show_result(beats: Array[Dictionary], before: CombatState, _after: CombatState) -> void:
	# ANIM-R3 A5: the result never shows while a counter still rolls (under load a frame can
	# land THIS TURN a frame or two early): numbers still on their way arrive, rolls end.
	fx_layer.arrive_all()
	for v in _views():
		if v.combatant != null and not v.defeated():
			v.finish_hp()
			if v.shown_state != null:
				v.anim_hp = float(_resolve_hp(beats, before, v.combatant.id))
	var stamps := result_stamps(beats, before)
	for v in _views():
		if v.combatant == null:
			continue
		v.reveal_last_turn()
		if not v.defeated():
			v.show_caption(tr("THIS TURN"))
		if stamps.has(v.combatant.id) and not v.defeated() and not _impact_stamped.has(v.combatant.id):
			var spot := v.stamp_slot(String(stamps[v.combatant.id]), CombatFxLayer.GUARD_NULL)
			fx_layer.word_stamp(spot["at"], String(stamps[v.combatant.id]), CHIP_GUARD, Motion.seconds(&"resolve_result_hold"), float(spot["max_w"]),
				int(spot["max_fs"]), 0.0, CombatFxLayer.GUARD_NULL)


## The HP `id` ends the resolve on (before the next turn starts): the last resolve-phase HP
## beat's, else what it started with.
static func _resolve_hp(beats: Array[Dictionary], before: CombatState, id: StringName) -> int:
	var c := before.get_combatant(id)
	var hp := c.hp if c != null else 0
	for b in beats:
		if b["phase"] == "turn_start":
			break
		if StringName(String(b["target"])) == id and int(b["hp_after"]) >= 0 and String(b["kind"]) in ResolveBeats.HP_KINDS:
			hp = int(b["hp_after"])
	return hp


## Wheels (the operative and the enemies, not satellites) that took no HP-changing beat in
## the resolve, from the beats: id -> the word they stamp ("ALL BLOCKED" when hits came and
## none got through, else "NO DAMAGE"). A wheel hurt and healed back stamps nothing.
func result_stamps(beats: Array[Dictionary], before: CombatState) -> Dictionary:
	var out := {}
	var wheels: Array[CombatantState] = [before.player]
	for e in before.enemies:
		if not e.is_satellite and e.is_alive():
			wheels.append(e)
	for c in wheels:
		# ANIM-R2 E4f: any HP change stamps nothing (damage and an equal heal net to zero, but
		# a hit landed: "NO DAMAGE" would be false).
		var changed := false
		var hit := false
		for b in beats:
			if b["phase"] == "turn_start" or StringName(String(b["target"])) != c.id:
				continue
			if b["kind"] in ResolveBeats.HP_KINDS and int(b["amount"]) > 0:
				changed = true
			if b["kind"] == "evaded" or (b["kind"] == "damage" and int(b["soaked"]) > 0):
				hit = true
		if not changed:
			out[c.id] = tr("ALL BLOCKED") if hit else tr("NO DAMAGE")
	return out


func _finish_sequence() -> void:
	_seq = null
	_restore_time_scale()
	_hold_city(false)
	# The forecast goes on first, so the tags flip in with it (C5e).
	_release_forecast()
	for v in _views():
		v.stop_motion(false)
	_numbers_on.clear()
	if _deal_waiting:
		for c in _hand_box.get_children():
			if c is ZineCard:
				(c as ZineCard).finish_deal()
		_deal_waiting = false
	ram_note.finish_motion()
	_show_end_turn_preview()
	_land_outcome()
	motion_settled.emit()


## Rewind: a quick reverse scrub with VHS lines back to the state the engine restored.
func _play_rewind(from: CombatState) -> void:
	fx_layer.vhs(_arena.get_global_rect())
	for v in _views():
		var c0 := from.get_combatant(v.combatant.id) if v.combatant != null else null
		if c0 != null:
			v.play_rewind(float(c0.wheel.rotation), float(c0.wheel.inner_rotation), float(c0.hp))


## The view a combatant is drawn on (a satellite's or drone's host), or null.
func _host_view(id: StringName, s: CombatState) -> WheelView:
	var c := s.get_combatant(id)
	if c == null:
		return null
	if c.is_satellite and c.host_id != &"":
		return _view_of(c.host_id)
	if s.drones.has(c):
		return _player_view
	return _view_of(id)


## Where a beat's actor stands: the slice its resolving needle landed on (ANIM-R1: hits
## fly from the attacker's slice), else its needle's hub, or its satellite token. ANIM-R3
## A1: a drone deployed during the resolve is found in the state it ends on.
func _source_spot(b: Dictionary, s: CombatState, after: CombatState = null) -> Vector2:
	var src := StringName(String(b["source"]))
	var v := _host_view(src, s)
	if v == null and after != null:
		v = _host_view(src, after)
	if v == null:
		return Vector2.INF
	if v.combatant != null and v.combatant.id != src:
		return v.satellite_spot(src)
	if int(b.get("source_slot", -1)) >= 0:
		# ANIM-R4 C6b: from the landed slice, right under the needle that resolves it.
		return v.needle_slot_spot(int(b["pointer_index"]), int(b["source_slot"]))
	return v.pointer_spot(maxi(0, int(b["pointer_index"])))


## The floating number a beat shows first (see numbers_for), or {} when it shows none.
func number_for(b: Dictionary, s: CombatState, _k: int = 0, after: CombatState = null) -> Dictionary:
	var list := numbers_for(b, s, after)
	return list[0] if not list.is_empty() else {}


## The floating numbers a beat shows (ANIM-R1 C5c): HP changes (red loss, green heal) sit
## in the hub above its name and travel into the HP counter; guards sit under the hub's
## lines. Each is sized to stay inside the hub, never on the name, and never on another
## number (a new one in the same band sends the one resting there on). ANIM-R3 A6e: a guard
## is a glyph and a number from the blocker (a shield and "5" under the wheel's own guard
## lines, or at the drone's or satellite's token), never a word badge; a hit soaked or
## evaded whole shows "0" with its glyph where it struck (see _play_beat), no number here.
## Each: {at, rise, text, color, crit, id, view, fs, band (the view's band key), travel,
## icon (a slice type, -1 = none), hp (HP numbers only)}. ANIM-R3 A1: `after` finds the
## host of a drone deployed during this resolve.
func numbers_for(b: Dictionary, s: CombatState, after: CombatState = null) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var target := StringName(String(b["target"]))
	# ANIM-R3 A1: a drone deployed (a satellite launched) during this resolve isn't in the
	# state it started from: its host is found in the state it ends on.
	var v := _host_view(target, s)
	if v == null and after != null:
		v = _host_view(target, after)
	if v == null:
		return out
	var amount := int(b["amount"])
	var kind := String(b["kind"])
	var crit := bool(b["crit"]) and kind == "damage"
	if v.combatant != null and v.combatant.id != target:
		# ANIM-R2 E4b: a satellite's or drone's HP change shows at its own token (in the hub it
		# read as the host's HP, which didn't move).
		var fs := roundi(CombatFxLayer.number_font(false) * SAT_NUMBER_SHARE)
		var tok := v.satellite_spot(target)
		if kind in ResolveBeats.HP_KINDS and amount > 0:
			var heal := kind == "heal"
			var at := tok + Vector2(0.0, -(WheelView.SATELLITE_TOKEN * Settings.text_scale + fs * 0.6))
			out.append({"at": at, "rise": 0.0, "text": (tr("+%d HP") % amount) if heal else "-%d" % amount,
				"color": WheelView.HP_COLOR if heal else WheelView.LOSS_COLOR, "crit": false, "id": &"number_float", "view": v, "fs": fs,
				"band": "%d:sat:%s" % [v.get_instance_id(), target], "travel": false, "hub": false, "hp": amount, "icon": -1})
		var guard := _guard_of(b)
		if not guard.is_empty():
			# The token's own guard pops beside it (a satellite guards itself).
			var gat := tok + Vector2(WheelView.SATELLITE_TOKEN * Settings.text_scale + fs * 0.9, 0.0)
			out.append({"at": gat, "rise": 0.0, "text": String(guard["text"]), "color": CHIP_GUARD, "crit": false, "id": &"block_number", "view": v,
				"fs": fs, "band": "%d:satguard:%s" % [v.get_instance_id(), target], "travel": false, "hub": false, "icon": int(guard["icon"])})
		return out
	match kind:
		"damage", "corrupted":
			if amount > 0:
				var n := _number(v, "hp", "-%d" % amount, WheelView.LOSS_COLOR, &"number_float", crit, true)
				n["hp"] = amount
				if int(b["soaked"]) > 0 and ResolveBeats.is_hit(b):
					# ANIM-R4 C6c: the hit meets its guard where it struck (the equation, sword
					# raw − shield soaked = through); what gets through then pops fresh in the
					# hub `hit_absorb` later and travels into the HP (the raw number no longer
					# morphs into it in the same spot).
					n["after"] = Motion.seconds(&"hit_absorb")
				out.append(n)
	var guard := _guard_of(b)
	if not guard.is_empty():
		out.append(_number(v, "guard", String(guard["text"]), CHIP_GUARD, &"block_number", false, false, int(guard["icon"])))
	if kind == "heal" and amount > 0:
		var n := _number(v, "hp", tr("+%d HP") % amount, WheelView.HP_COLOR, &"heal_number", false, true)
		n["hp"] = amount
		out.append(n)
	return out


## The guard a beat shows as a glyph and a number (ANIM-R3 A6e): a block, shield or evade
## gained ("+3"); {} when none. {text, icon}. ANIM-R4 C6c: a hit's soaked part is no guard
## number any more: the hit's equation where it struck says it (sword 8 − shield 8 = 0).
func _guard_of(b: Dictionary) -> Dictionary:
	var amount := int(b["amount"])
	match String(b["kind"]):
		"block":
			return {"text": signed(amount), "icon": RC.SliceType.DEFRAG}
		"shield":
			if amount > 0:
				return {"text": signed(amount), "icon": RC.SliceType.SANDBOX}
		"evade":
			return {"text": signed(amount), "icon": RC.SliceType.DETOUR}
	return {}


func _number(v: WheelView, band: String, text: String, color: Color, id: StringName, crit: bool, travel: bool, icon: int = -1) -> Dictionary:
	var slot := v.number_slot(band, text, crit, icon)
	return {"at": slot["at"], "rise": minf(Motion.amplitude(id), float(slot["room"])), "text": text, "color": color, "crit": crit,
		"id": id, "view": v, "fs": int(slot["fs"]), "band": "%d:%s" % [v.get_instance_id(), band], "travel": travel, "hub": true, "icon": icon}


## A satellite's number: its size as a share of a hub number's.
const SAT_NUMBER_SHARE := 0.75


## The colour of `id`'s hits (ANIM-R2 E4a): the operative's side or the enemies'. ANIM-R3
## A1: a drone deployed during the resolve is looked up in `after`.
static func hit_color(id: StringName, s: CombatState, after: CombatState = null) -> Color:
	var c := s.get_combatant(id) if s != null else null
	var in_s := c != null
	if c == null and after != null:
		c = after.get_combatant(id)
	if c != null and (c.is_player or (s.drones.has(c) if in_s else after.drones.has(c))):
		return PLAYER_HIT_COLOR
	return ENEMY_HIT_COLOR


## What a hit that dealt nothing stamps at its victim: "N BLOCKED" (all soaked) or
## "EVADED N" ("" when it dealt something, or isn't a hit). ANIM-R3 A6a: the replay shows
## these as a glyph and "0" where the hit struck (`zero_mark`); the words stay for the log.
func hit_stamp_for(b: Dictionary) -> String:
	match String(b["kind"]):
		"evaded":
			return tr("EVADED %d") % int(b["amount"])
		"damage":
			if int(b["amount"]) <= 0 and int(b["soaked"]) > 0:
				return tr("%d BLOCKED") % int(b["soaked"])
	return ""


## ANIM-R3 A6a: what a hit that dealt nothing shows where it struck: {text "0", icon (the
## guard's glyph: ANIM-R4 C6c, the shield for any soak, block or shield; the evade mark
## when evaded)}; {} for any other beat.
static func zero_mark(b: Dictionary) -> Dictionary:
	match String(b["kind"]):
		"evaded":
			return {"text": "0", "icon": RC.SliceType.DETOUR}
		"damage":
			if int(b["amount"]) <= 0 and int(b["soaked"]) > 0:
				return {"text": "0", "icon": RC.SliceType.DEFRAG}
	return {}


## ANIM-R4 C6c: the one notation for a hit meeting a guard (the mark where it struck, as the
## icon row under the HP): [sword raw, − shield soaked (or − evade mark evaded), = what got
## through], CombatFxLayer.draw_equation items; [] for a hit no guard touched (its number
## says it) or any other beat.
static func hit_equation(b: Dictionary) -> Array:
	var kind := String(b["kind"])
	if not ResolveBeats.is_hit(b):
		return []
	var raw := int(b.get("raw", b["amount"])) if kind == "damage" else int(b["amount"])
	var items: Array = [{"icon": RC.SliceType.SHIM, "text": str(raw), "color": WheelView.LOSS_COLOR, "sep": ""}]
	if kind == "evaded":
		items.append({"icon": RC.SliceType.DETOUR, "text": str(raw), "color": CHIP_GUARD, "sep": CombatFxLayer.EQ_MINUS})
		items.append({"icon": -1, "text": "0", "color": CHIP_GUARD, "sep": "="})
		return items
	var soaked := int(b["soaked"])
	if soaked <= 0:
		return []
	var through := maxi(0, raw - soaked)
	items.append({"icon": RC.SliceType.DEFRAG, "text": str(soaked), "color": CHIP_GUARD, "sep": CombatFxLayer.EQ_MINUS})
	items.append({"icon": -1, "text": str(through), "color": WheelView.LOSS_COLOR if through > 0 else CHIP_GUARD, "sep": "="})
	# ANIM-R6 A4: a victim with fewer HP left than gets through says so (the HP number that
	# follows is what it really takes).
	var applied := int(b["amount"])
	if kind == "damage" and applied < through:
		items.append(clamp_item(applied))
	return items


## ANIM-R6 A4: the "→ N LEFT" part of a hit that takes a victim's last HP (fewer than it gets
## through), for an equation (CombatFxLayer.draw_equation).
static func clamp_item(applied: int) -> Dictionary:
	return {"icon": -1, "text": String(TranslationServer.translate("%d LEFT")) % applied, "color": WheelView.LOSS_COLOR, "sep": CLAMP_ARROW}


## The sign before a clamped hit's "N LEFT" (drawing).
const CLAMP_ARROW := "→"


## ANIM-R3 A6c: what rides with a hit: {label (what it deals), from (the slice's own value
## when the aim changed it, "" otherwise: "12" shrinks into "6" at half power), scale (bigger
## on a PERFECT landing)}. ANIM-R6 A4: never a fraction ("6 ½" rode, then 6 came off): the
## label is the whole number the hit deals.
func ride_for(b: Dictionary, s: CombatState) -> Dictionary:
	var kind := String(b["kind"])
	var raw := int(b.get("raw", b["amount"])) if kind == "damage" else int(b["amount"])
	var out := {"label": str(raw), "from": "", "scale": 1.0}
	var tier := int(b.get("source_tier", -1))
	var slot := int(b.get("source_slot", -1))
	var src := s.get_combatant(StringName(String(b["source"]))) if s != null else null
	var base := -1
	if src != null and slot >= 0 and slot < src.wheel.slot_slice_ids.size():
		var slice := engine.content(src.wheel.slot_slice_ids[slot]) as SliceData
		if slice != null and slice.slice_type in [RC.SliceType.SHIM, RC.SliceType.OVERFLOW]:
			base = slice.base_output
	if tier == RC.PrecisionTier.PERFECT:
		# ANIM-R4 C5: a PERFECT hit's riding size is `ride_perfect`'s amplitude.
		out["scale"] = Motion.amplitude(&"ride_perfect")
	if base > 0 and base != raw and tier in [RC.PrecisionTier.WEAK, RC.PrecisionTier.PERFECT]:
		out["from"] = str(base)
	return out


func _play_beat(b: Dictionary, before: CombatState, after: CombatState) -> void:
	var kind := String(b["kind"])
	var target := StringName(String(b["target"]))
	var tv := _host_view(target, after)
	if tv == null:
		tv = _host_view(target, before)
	match kind:
		"land":
			_land(b, before)
			return
		"spin":
			if tv != null and b["phase"] == "turn_start":
				var c0 := before.get_combatant(target)
				tv.shown_state = null
				tv.shown_satellites = []
				tv.anim_sat_hp = {}
				tv.clear_landing()
				tv.hide_caption()
				if c0 != null and tv.combatant != null and tv.combatant.id == target:
					var mine := tv == _player_view
					tv.play_turn(&"wheel_respin" if mine else &"enemy_turn_spin", float(c0.wheel.rotation),
						float(c0.wheel.inner_rotation), 0.0 if mine else Motion.delay_of(&"enemy_turn_spin"))
			return
		"orbit", "migrate":
			var c0 := before.get_combatant(target)
			if tv != null and c0 != null:
				tv.shown_state = null
				tv.play_pointers(Array(c0.wheel.pointer_ticks), &"pointer_orbit" if kind == "orbit" else &"pointer_migrate", kind == "orbit")
			return
		"ram":
			# ART-2 2C: RAM gain, bits from the TURN banner down the centre gap into the new chips.
			fx_layer.ram_gain(Vector2(get_global_rect().get_center().x, get_global_rect().position.y), CombatBeatFx.ram_pips(ram_note, ram_note.shown_ram, ram_note.ram))
			ram_note.play_refill()
			return
		"draw":
			if _deal_waiting:
				_deal_hand(maxi(0, engine.state().hand.size() - int(b["amount"])))
			return
		"end":
			_end_beat(int(engine.state().outcome))
			return
		"died":
			_death_beat(target, before, after)
			return
		"breach":
			if tv != null:
				fx_layer.glass(tv.global_center(), tv.hub_radius(), tv.wheel_color)
			return
		"spawn":
			_spawn_beat(target, int(b["hp_after"]), after)
			CombatBeatFx.spawn(fx_layer, b, tv)  # ART-2 2C: drone deploy
			return
		"phase":
			_phase_beat(b, after)
			return
		"nudge", "flip", "snap":
			return
	# The resolving needle pulses; a hit flies from its slice to its victim's HP ring.
	var src := StringName(String(b["source"]))
	var sv := _host_view(src, before)
	if sv == null:
		sv = _host_view(src, after)  # ANIM-R3 A1: a drone deployed during this resolve
	if sv != null:
		if sv.combatant != null and sv.combatant.id != src:
			sv.play_pulse(-1, src)
		elif int(b["pointer_index"]) >= 0:
			sv.play_pulse(int(b["pointer_index"]))
	if tv == null:
		return
	var on_host := tv.combatant != null and tv.combatant.id == target
	var victim_at := tv.hp_ring_spot() if on_host else tv.satellite_spot(target)
	# ANIM-R2 E4a: every hit (and a status put on a slice) flies from its attacker's landed
	# slice to its victim, one at a time, thick, in its side's colour, its raw number riding
	# with it (ANIM-R3 A6c: with its aim's multiplier); what it does shows on impact.
	var impact := 0.0
	if sv != null and ResolveBeats.flies(b):
		var line_to := tv.slot_spot(int(b["slot"])) if kind in ["status", "absorbed"] and int(b["slot"]) >= 0 and on_host else victim_at
		var ride := ride_for(b, before) if kind in ["damage", "evaded"] else {"label": "", "from": "", "scale": 1.0}
		fx_layer.hit_line(_source_spot(b, before, after), line_to, hit_color(src, before, after), String(ride["label"]), String(ride["from"]), float(ride["scale"]))
		impact = CombatFxLayer.impact_seconds()
	# ART-2 2C: the beat's locked effect (0/1 shards, walls, heal, evade, corrupt; D16 origin).
	CombatBeatFx.play(fx_layer, b, tv, _player_view, _view_of(engine.state().target_id), _source_spot(b, before, after) if sv != null else Vector2.INF, on_host, impact, hit_color(src, before, after))
	# ANIM-R3 A6a: a hit that got nothing through shows "0" with its glyph where it struck
	# (the arrowhead on the HP ring, or the token); the wheel whose every hit was soaked says
	# ALL BLOCKED (with its mark) on its last hit's impact.
	var zero := zero_mark(b)
	var eq := hit_equation(b)
	if not eq.is_empty():
		# ANIM-R4 C6c: the hit meets its guard where it struck, in the one notation (sword 8 −
		# shield 8 = 0; sword 14 − shield 5 = 9).
		fx_layer.impact(victim_at, String(zero.get("text", "")), int(zero.get("icon", -1)), CHIP_GUARD, impact, eq)
	if b.has("final_stamp") and on_host:
		var spot := tv.stamp_slot(String(b["final_stamp"]), CombatFxLayer.GUARD_NULL)
		fx_layer.word_stamp(spot["at"], String(b["final_stamp"]), CHIP_GUARD, float(b.get("final_hold", Motion.seconds(&"number_float"))),
			float(spot["max_w"]), int(spot["max_fs"]), impact, CombatFxLayer.GUARD_NULL)
	if kind == "status" and int(b["slot"]) >= 0 and on_host:
		# ANIM-R4 C6f: its glyph lands on the slice in its good / bad colour for you.
		var scol := WheelView.status_color(int(b["status"]), tv.combatant != null and tv.combatant.is_player)
		fx_layer.stamp(tv.slot_spot(int(b["slot"])), String(Palette.STATUS_GLYPHS.get(int(b["status"]), "?")), scol, motion_seconds_left(), impact)
		# ANIM-R3 A6j: the slice keeps the status's mark from the moment it lands.
		_after(impact, tv.show_slice_status.bind(int(b["slot"]), int(b["status"])))
	elif kind == "absorbed" and int(b["slot"]) >= 0 and on_host:
		_after(impact, fx_layer.ring.bind(tv.slot_spot(int(b["slot"])), CombatFxLayer.STAMP_DISC, CHIP_RESIST, &"precision_good_ring"))
	var hp_after := int(b["hp_after"])
	var hp_waits := false
	for n in numbers_for(b, before, after):
		if bool(n["travel"]) and on_host and hp_after >= 0:
			# ANIM-R4 C6b/c: the number appears when its projectile has arrived (and a guarded
			# hit's equation has been read), fresh, then travels.
			fx_layer.travel_number(n["at"], tv.hp_counter_spot(), n["text"], n["color"], n["crit"], int(n["fs"]), String(n["band"]),
				_hp_arrives.bind(tv, hp_after), impact + float(n.get("after", 0.0)))
			hp_waits = true
		else:
			fx_layer.number(n["at"], n["text"], n["color"], n["id"], Vector2.UP, n["crit"], n["rise"], int(n["fs"]), String(n["band"]), impact, int(n.get("icon", -1)))
	if hp_after >= 0:
		if not on_host:
			_after(impact, tv.set_sat_hp.bind(target, hp_after))
		elif not hp_waits:
			_after(impact, tv.play_hp.bind(float(hp_after)))


## A number reached `v`'s HP counter: the HP rolls to `hp` with the white lag bar, and a
## loss flashes and shakes the wheel.
func _hp_arrives(v: WheelView, hp: int) -> void:
	if not is_instance_valid(v):
		return
	var lost := float(hp) < v.shown_hp()
	v.play_hp(float(hp))
	if lost:
		v.play_hit()
	if v == _player_view and _replay_hp >= 0 and engine.has_fight():
		# ANIM-R6 A8: the portrait follows the replay's HP.
		_replay_hp = hp
		_sync_portrait(hp, engine.state().player.max_hp)


## A satellite launched or a drone deployed during the replay: its token docks (with the
## HP it starts on) and pops.
func _spawn_beat(id: StringName, hp: int, after: CombatState) -> void:
	var c := after.get_combatant(id)
	var v := _host_view(id, after)
	if c == null or v == null or v.combatant == null or v.combatant.id == id:
		return
	var shown := c.duplicate_state()
	shown.hp = maxi(hp, 0)
	v.add_shown_satellite(shown)
	fx_layer.ring(v.satellite_spot(id), WheelView.SATELLITE_TOKEN * Settings.text_scale, Palette.RESIST_GOLD, &"precision_good_ring")


## A boss enters a phase: PHASE N stamps on its hub (with the alarm and flash), new
## needles fan out (MULTIPLY), satellites it launches dock.
func _phase_beat(b: Dictionary, after: CombatState) -> void:
	var v := _view_of(StringName(String(b["target"])))
	_boss_phase_feedback(after)
	if v == null:
		return
	var word := tr("PHASE %d") % (int(b.get("phase_index", 0)) + 1)
	fx_layer.word_stamp(v.global_center(), word, CHIP_RESIST, Motion.seconds(&"number_float"), v.hub_radius() * 2.0 * WheelView.NUMBER_HUB_SHARE)
	if int(b.get("behavior", -1)) == RC.PointerBehavior.MULTIPLY:
		v.play_phase_needles(b.get("ticks", []))
		# ART-2 2C §3.16: "2 NEEDLES", a temporary label under PHASE N.
		fx_layer.temp_label(v.global_center() + Vector2(0, v.hub_radius() * 0.5), tr("%d NEEDLES") % (b.get("ticks", []) as Array).size(), CHIP_RESIST)
	for sp in b.get("spawned", []):
		_spawn_beat(StringName(String(sp.get("id", ""))), int(sp.get("hp", 0)), after)


## A needle latches: its slice pulses in its colour (a NULL slice gets a big grey X,
## ANIM-R1 C5a); the player's landings show their precision (Perfect: inversion + freeze +
## a limited flash; Good: a clean ring; Weak: a stutter; NULL: static over that slice
## only), with their sound and bark; every needle pulses.
func _land(b: Dictionary, s: CombatState) -> void:
	var owner := StringName(String(b["source"]))
	var v := _host_view(owner, s)
	if v == null:
		return
	if v.combatant != null and v.combatant.id != owner:
		v.play_pulse(-1, owner)
		return
	v.play_pulse(int(b["pointer_index"]))
	v.play_landing(int(b["slot"]))
	if owner != s.player.id:
		return
	var slot := int(b["slot"])
	var slice := engine.content(s.player.wheel.slot_slice_ids[clampi(slot, 0, s.player.wheel.slot_slice_ids.size() - 1)]) as SliceData
	var is_null_slice := slice != null and slice.slice_type == RC.SliceType.NULL
	var tier := int(b["tier"])
	AudioDirector.play_precision(tier, is_null_slice)
	if not is_null_slice:
		v.play_precision(tier, slot, int(b["pointer_index"]))  # ART-2 2A: the landing's shape (ART_BIBLE 3.19)
	if is_null_slice:
		v.play_null_static(slot)
		_bark("null", s)
	elif tier == RC.PrecisionTier.PERFECT:
		_perfect_feedback(v)
		_bark("perfect", s)
	elif tier == RC.PrecisionTier.WEAK:
		_stutter_view(v)
	else:
		v.play_good_ring()


## A wheel goes down (its HP was seen reaching 0 first: the schedule waits): an enemy's
## cracks along its slice borders and falls, leaving its DEFEATED spot; a satellite bursts
## off its host and its token goes; the operative's wheel breaks too (defeat).
func _death_beat(id: StringName, before: CombatState, after: CombatState = null) -> void:
	var c := before.get_combatant(id)
	var v := _host_view(id, before)
	if (c == null or v == null) and after != null:
		c = after.get_combatant(id)
		v = _host_view(id, after)
	if c == null or v == null:
		return
	if v.combatant != null and v.combatant.id != id:
		fx_layer.drone_destroyed(v.satellite_spot(id), Palette.SLICE_TROJAN)  # ART-2 2C: drone destroyed v3
		v.remove_shown_satellite(id)
		return
	v.anim_hp = 0.0
	# ANIM-R2 E5: a short white flash on the breaking wheel only (a full-screen flash read as
	# a rendering fault).
	fx_layer.disc_flash(v.global_center(), v.disc_radius(), Color.WHITE, &"victory_flash")
	fx_layer.shards(v.slice_pieces(), tr("DELETED") if not c.is_player else "")  # ART-2 2C: enemy defeated v2
	v.play_break()
	AudioDirector.play_sfx("clack")


## VICTORY / DEFEAT lands once the last hit has (ANIM-R2 E5): VICTORY centred over the
## enemies' side (never on the operative's wheel), DEFEAT over the operative's. The break
## flashed its own wheel already (no full-screen flash). ANIM-R5 combat 1-2: the outcome
## lands here (the status word, the next step, Heat, the top bar, the bark); DEFEAT is the
## operative's wheel's own stamp, which stays while the fight waits (it faded after 1 s and
## left a fight that looked as if it went on).
func _end_beat(outcome: int) -> void:
	var won := outcome == CombatState.Outcome.VICTORY
	if won:
		_hold_victory(false)
	_land_outcome()  # ANIM-R6 A2: the bark comes with the outcome (a skip barks there too)


## ANIM-R6 A15: VICTORY lands over the enemies' side and stays at full strength until the
## fight is left for its loot (it read for ~1 s, then faded to a ghost); `instant` (a skip,
## no replay) shows it landed at once.
func _hold_victory(instant: bool) -> void:
	if fx_layer == null:
		return
	var word := tr("VICTORY")
	fx_layer.hold_word(end_word_spot(true), word, Palette.CELL_ACID, end_word_size(true, word), instant)


## Where VICTORY (the enemies' side) or DEFEAT (the operative's wheel) lands (global).
## ANIM-R4 C6g: VICTORY stands in the room above the first enemy's disc (the tag is gone),
## never over the breaking wheel and its crack or its DEFEATED stamp.
func end_word_spot(won: bool) -> Vector2:
	if not won:
		return _player_view.global_center()
	var room := _victory_room()
	if room.has_area():
		return room.get_center()
	if _enemy_views_box != null and _enemy_views_box.get_global_rect().has_area():
		return _enemy_views_box.get_global_rect().get_center()
	return _arena.get_global_rect().get_center()


## ANIM-R4 C6g: VICTORY's lettering size (px), fitting its room above the beaten wheel
## (-1 = the stamp's own size: DEFEAT, or when there is no room).
func end_word_size(won: bool, word: String) -> int:
	var room := _victory_room()
	if not won or not room.has_area():
		return -1
	return CombatFxLayer.word_fit(word, room.size)


func _victory_room() -> Rect2:
	for v in _enemy_views.values():
		var wv := v as WheelView
		if wv != null and wv.is_visible_in_tree():
			return wv.room_above_disc()
	return Rect2()


## Plays the break of `id`'s wheel alone (the motion lab's --demo-anim=enemy_break).
func demo_break(id: StringName) -> void:
	var v := _view_of(id)
	if v != null:
		fx_layer.shards(v.slice_pieces())
		v.play_break()
