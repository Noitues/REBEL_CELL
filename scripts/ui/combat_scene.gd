extends Control
## Combat scene (M4 look): wireframe arena with zine HUD (STYLE_GUIDE 1, 4-5, GDD 9.2).
## Layout (1280x720 design canvas): Polaroid, RAM tally, Heat, Daemons and the inspect
## note on the left; the wheels in the middle where nothing zine ever covers them;
## preview and log strips on the right; card stickers along the bottom with the SEND IT
## stamp. Full keyboard play: 1-9 play cards, Q/E nudge, W nudge wheel, R ring, T card
## target, D card direction, F chosen slice, X respin, Tab target, Space end turn,
## Z rewind, right-click inspect, Esc settings. Random effects show odds, never the
## exact roll (GDD 2.10). Signal Up, Call Down: widgets call the engine only.

const ENEMY_CHOICES: Array[StringName] = [&"collections_agent", &"compliance_officer", &"dosage_dispenser"]
const CLASS_ID := &"breaker"
const RING_ID := &"rank:1"
## Seconds between resolution passes in the log playback (0 under headless / reduce-effects).
const PASS_DELAY := 0.35

@export var auto_start: bool = true

@onready var engine: CombatEngine = $CombatEngine

var background: WireframeBackground
var portrait: Polaroid
var heat_poster: HeatPoster
var ram_note: ZineNote
var daemon_note: ZineNote
var inspect_note: ZineNote
var preview_note: ZineNote
var log_note: ZineNote
var _status: Label
var _seed_spin: SpinBox
var _player_view: WheelView
var _enemy_views_box: VBoxContainer
var _enemy_views: Dictionary = {}
var _target_option: OptionButton
var _nudge_wheel_option: OptionButton
var _nudge_ring_option: OptionButton
var _card_target_option: OptionButton
var _direction_option: OptionButton
var _slot_option: OptionButton
var _respin_button: Button
var _hand_box: HBoxContainer
var _end_turn_button: ZineStamp
var _rewind_button: Button
var _picker_controls: Array[Control] = []
## The bottom controls row (layout tests check it fits the 1280-px canvas).
var controls_row: HFlowContainer
var _settings_panel: PauseMenu = null
var _menu_layer: CanvasLayer = null
## Canvas layer of the pause menu: above the combat scene and the netrun around it.
const MENU_LAYER := 10
var _arena: Control
var _zine_elements: Array[Control] = []
var _last_events: Array[Dictionary] = []
var _log_generation: int = 0
var tutorial: TutorialOverlay = null
## Where the tutorial sits: the log strip's place in the right column.
const TUTORIAL_RECT := Rect2(980, 287, 300, 250)
var _rewound: bool = false
var _migrate_tween: Tween = null
## Text of the last inspect (tests read it).
var last_inspect: String = ""


func _ready() -> void:
	UiTheme.apply(self)
	_build_ui()
	engine.state_changed.connect(_on_state_changed)
	engine.action_refused.connect(_on_action_refused)
	engine.fight_ended.connect(_on_fight_ended)
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


func start_fight(enemy_id: StringName, combat_seed: int) -> void:
	log_note.clear()
	log_note.append("[b]New fight:[/b] %s vs %s (seed %d)" % [CLASS_ID, enemy_id, combat_seed])
	engine.start_fight(CLASS_ID, [enemy_id], combat_seed, RING_ID)
	_start_music()


func end_turn() -> void:
	AudioDirector.play_sfx("stamp")
	engine.submit(CombatAction.end_turn())


func rewind() -> void:
	if engine.rewind() and tutorial != null and is_instance_valid(tutorial):
		var ev: Array[Dictionary] = [{"type": "rewind"}]
		tutorial.on_events(ev)


func nudge(direction: int) -> void:
	var wheel_id := _selected_nudge_wheel()
	var ring := RC.RingScope.INNER if _nudge_ring_option.selected == 1 else RC.RingScope.OUTER
	engine.submit(CombatAction.nudge(wheel_id, direction, ring))


## The RAM respin of your own wheel (GDD 2.5, 11.3).
func respin() -> void:
	engine.submit(CombatAction.respin())


func play_card(hand_index: int) -> void:
	if not engine.has_fight() or hand_index < 0 or hand_index >= engine.state().hand.size():
		return
	engine.submit(_card_action(hand_index))


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
	_nudge_ring_option.select((_nudge_ring_option.selected + 1) % 2)


func toggle_nudge_wheel() -> void:
	_nudge_wheel_option.select((_nudge_wheel_option.selected + 1) % 2)


## Card nudge direction for cards that nudge (Fine Tune, Micro-Adjust, Jam...).
func toggle_direction() -> void:
	_direction_option.select((_direction_option.selected + 1) % 2)


func set_direction(direction: int) -> void:
	_direction_option.select(0 if direction > 0 else 1)


## Chosen slice for cards that pick one (Cleanse, Encrypt): -1 = none chosen.
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


## The guided first fight (onboarding). Steps follow the engine's events.
func start_tutorial() -> void:
	if tutorial != null and is_instance_valid(tutorial):
		return
	tutorial = TutorialOverlay.new(TUTORIAL_RECT.size)
	tutorial.position = TUTORIAL_RECT.position  # over the log strip: never on a wheel (GDD 9.2)
	add_child(tutorial)
	tutorial.finished.connect(func() -> void: tutorial = null)


func open_settings() -> void:
	if _settings_panel != null:
		_settings_panel.queue_free()
		_settings_panel = null
		return
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
	get_tree().paused = false


## Right-click inspect (GDD 9.5): the slice under a global point on any wheel, with its
## Firmware and status, or the wheel's hub/vitals when pointing at the centre.
func inspect_at(global_point: Vector2) -> String:
	var text := ""
	if engine.has_fight():
		var views: Array[WheelView] = [_player_view]
		for v in _enemy_views.values():
			views.append(v)
		for v in views:
			if v.combatant == null or not v.contains_global(global_point):
				continue
			var slot := v.slot_at_global(global_point)
			text = _describe_slot(v.combatant, slot)
			break
	last_inspect = text
	_refresh_inspect_note()
	return text


func _refresh_inspect_note() -> void:
	inspect_note.clear()
	if last_inspect != "":
		inspect_note.append(last_inspect)
		return
	var state := engine.state()
	if state == null:
		return
	var tips := PackedStringArray()
	if state.daemon_ids.is_empty():
		inspect_note.append("no Daemons. Right-click a slice to inspect.")
	for id in state.daemon_ids:
		var d := engine.content(id) as DaemonData
		if d != null:
			inspect_note.append("* " + d.display_name)
			tips.append(Codex.describe(d))
	inspect_note.tooltip_text = "\n\n".join(tips)


## Odds a random effect shows instead of a result (GDD 2.10): the slice type mix of a
## wheel, optionally leaving the Miss slice out (random non-Miss picks).
func odds_text(c: CombatantState, non_miss_only: bool = false) -> String:
	var counts := {}
	var total := 0
	for id in c.wheel.slot_slice_ids:
		var slice := engine.content(id) as SliceData
		if slice == null or (non_miss_only and slice.slice_type == RC.SliceType.MISS):
			continue
		var key: String = "%s %s" % [Palette.SLICE_GLYPHS.get(slice.slice_type, "?"), Palette.SLICE_NAMES.get(slice.slice_type, "?")]
		counts[key] = int(counts.get(key, 0)) + 1
		total += 1
	var parts := PackedStringArray()
	for key in counts:
		parts.append("%s %d%%" % [key, roundi(100.0 * counts[key] / maxf(1.0, total))])
	return "odds: " + " / ".join(parts)


## Layout rule (STYLE_GUIDE 4): zine elements never cover the wheels. Returns the
## names of offending elements (empty = the rule holds).
func layout_violations() -> Array[String]:
	var out: Array[String] = []
	var wheels: Array[WheelView] = [_player_view]
	for v in _enemy_views.values():
		wheels.append(v)
	var notes: Array = _zine_elements.duplicate()
	if tutorial != null and is_instance_valid(tutorial):
		notes.append(tutorial)
	for z in notes:
		if not is_instance_valid(z) or not z.visible:
			continue
		var zr: Rect2 = (z as Control).get_global_rect()
		for w in wheels:
			if w.combatant != null and zr.intersects(w.wheel_rect()):
				out.append("%s covers %s's wheel" % [z.name if z.name != "" else z.get_class(), w.combatant.display_name])
	for child in _hand_box.get_children():
		var cr: Rect2 = child.get_global_rect()
		for w in wheels:
			if w.combatant != null and cr.intersects(w.wheel_rect()):
				out.append("card covers %s's wheel" % w.combatant.display_name)
	return out


func player_wheel_color() -> Color:
	return _player_view.wheel_color


func enemy_wheel_colors() -> Array[Color]:
	var out: Array[Color] = []
	for v in _enemy_views.values():
		out.append(v.wheel_color)
	return out


# --- Input -----------------------------------------------------------------------

## Whether the last input came from the mouse: card previews follow the mouse (hover), and
## follow focus only when the player moves focus with the keyboard or a pad. Auto-focus at
## fight start must not replace the End Turn preview.
## True only right after a focus-navigation press (D-pad / arrows / Shift+Tab): then the
## newly focused card shows its preview. Any other input (a nudge, a card key, the mouse,
## the automatic refocus after a refresh) leaves the End Turn preview in place.
var _nav_focus: bool = false


func _input(event: InputEvent) -> void:
	if event is InputEventMouseMotion or event is InputEventMouseButton:
		_nav_focus = false
	elif event.is_pressed() and not event.is_echo():
		_nav_focus = event.is_action("ui_left") or event.is_action("ui_right") or event.is_action("ui_up") 			or event.is_action("ui_down") or event.is_action("ui_focus_prev") or event.is_action("ui_focus_next")


## Gives the hand focus (the first playable card, else SEND IT): the netrun scene calls it
## when it shows a fight.
func focus_hand() -> void:
	_link_hand_focus()
	UiFocus.focus_first(_hand_box, false, _end_turn_button.get_parent())


## Explicit D-pad neighbours in the hand: the cards are tilted stickers, so Godot's
## geometric search would jump to the pickers. Left/right walk the hand, the last card
## leads to SEND IT.
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
			c.focus_neighbor_right = c.get_path_to(_end_turn_button)
			c.focus_next = c.focus_neighbor_right
			_end_turn_button.focus_neighbor_left = _end_turn_button.get_path_to(c)


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
		# Pad / keyboard inspect: the focused control (a card, a wheel button) is inspected.
		var owner := get_viewport().gui_get_focus_owner()
		if owner != null:
			inspect_at(owner.get_global_rect().get_center())
		get_viewport().set_input_as_handled()
		return
	for i in 9:
		if event.is_action_pressed("card_%d" % (i + 1)):
			play_card(i)
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
	elif event.is_action_pressed("toggle_card_target"):
		toggle_card_target()
	elif event.is_action_pressed("toggle_ring"):
		toggle_ring()
	elif event.is_action_pressed("toggle_nudge_wheel"):
		toggle_nudge_wheel()
	elif event.is_action_pressed("toggle_direction"):
		toggle_direction()
	elif event.is_action_pressed("cycle_slot"):
		cycle_slot()
	elif event.is_action_pressed("respin"):
		respin()
	else:
		return
	get_viewport().set_input_as_handled()


# --- Engine callbacks --------------------------------------------------------------

func _on_state_changed(state: CombatState, events: Array[Dictionary]) -> void:
	_last_events = events
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


func _on_action_refused(reason: String) -> void:
	log_note.append("[color=#c05000]%s[/color]" % reason)
	preview_note.clear()
	preview_note.append(reason)


func _on_fight_ended(outcome: int) -> void:
	log_note.append("[b]%s[/b]" % ("VICTORY" if outcome == CombatState.Outcome.VICTORY else "DEFEAT"))
	if outcome == CombatState.Outcome.VICTORY:
		Fx.flash(Palette.CELL_ACID, 0.3)


## Pass-by-pass playback (GDD 5.6 spirit): the log strip reveals each resolution pass
## after a short beat so the three passes read as three moments. Instant when headless or
## under reduce-effects; the wheels always show the final state at once.
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
	for enemy_id in ENEMY_CHOICES:
		var b := Button.new()
		b.text = String(enemy_id)
		b.pressed.connect(func() -> void: start_fight(enemy_id, int(_seed_spin.value)))
		top.add_child(b)
		_picker_controls.append(b)
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
	_status.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(_status)
	top.add_child(_button("Settings [Esc]", open_settings))

	var middle := HBoxContainer.new()
	middle.size_flags_vertical = Control.SIZE_EXPAND_FILL
	middle.add_theme_constant_override("separation", 8)
	root.add_child(middle)
	var left := VBoxContainer.new()
	left.custom_minimum_size = Vector2(176, 0)
	middle.add_child(left)
	portrait = Polaroid.new("Breaker", "[BREAKER PORTRAIT]", -3.0)
	portrait.name = "Polaroid"
	left.add_child(portrait)
	ram_note = ZineNote.new("RAM", Vector2(170, 54))
	ram_note.name = "RamTally"
	left.add_child(ram_note)
	heat_poster = HeatPoster.new(false)
	heat_poster.name = "HeatPoster"
	if RunManager.campaign != null:
		heat_poster.hot_color = Palette.corp_color(RunManager.campaign.corporation_id)
	left.add_child(heat_poster)
	# One note serves both: the installed Daemons by default, the inspect text on right-click
	# (the left column must stay within the 720-px canvas next to the netrun status bars).
	inspect_note = ZineNote.new("DAEMONS / INSPECT", Vector2(170, 104))
	inspect_note.name = "InspectNote"
	daemon_note = inspect_note
	left.add_child(inspect_note)
	_zine_elements.append_array([portrait, ram_note, heat_poster, inspect_note])

	_arena = HBoxContainer.new()
	_arena.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_arena.size_flags_vertical = Control.SIZE_EXPAND_FILL
	middle.add_child(_arena)
	_player_view = WheelView.new()
	_player_view.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_arena.add_child(_player_view)
	_enemy_views_box = VBoxContainer.new()
	_enemy_views_box.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_arena.add_child(_enemy_views_box)

	var right := VBoxContainer.new()
	right.custom_minimum_size = Vector2(300, 0)
	middle.add_child(right)
	preview_note = ZineNote.new("WHAT WILL RESOLVE", Vector2(290, 150))
	preview_note.name = "PreviewNote"
	preview_note.size_flags_vertical = Control.SIZE_EXPAND_FILL
	right.add_child(preview_note)
	log_note = ZineNote.new("LOG", Vector2(290, 150))
	log_note.name = "LogStrip"
	log_note.size_flags_vertical = Control.SIZE_EXPAND_FILL
	right.add_child(log_note)
	_zine_elements.append_array([preview_note, log_note])

	var controls := HFlowContainer.new()  # wraps at large text scales (GDD 9.6)
	controls_row = controls
	root.add_child(controls)
	_target_option = OptionButton.new()
	_target_option.item_selected.connect(func(i: int) -> void: engine.submit(CombatAction.target(_target_option.get_item_metadata(i))))
	controls.add_child(_target_option)
	_nudge_wheel_option = OptionButton.new()
	_nudge_wheel_option.add_item("Nudge own [W]")
	_nudge_wheel_option.add_item("Nudge tgt [W]")
	controls.add_child(_nudge_wheel_option)
	_nudge_ring_option = OptionButton.new()
	_nudge_ring_option.add_item("Outer [R]")
	_nudge_ring_option.add_item("Inner [R]")
	controls.add_child(_nudge_ring_option)
	controls.add_child(_button("-1 [%s]" % Settings.key_text(&"nudge_left"), func() -> void: nudge(-1)))
	controls.add_child(_button("+1 [%s]" % Settings.key_text(&"nudge_right"), func() -> void: nudge(1)))
	_card_target_option = OptionButton.new()
	_card_target_option.add_item("Card>tgt [T]")
	_card_target_option.add_item("Card>own [T]")
	_card_target_option.item_selected.connect(func(_i: int) -> void: _rebuild_slot_option())
	controls.add_child(_card_target_option)
	_direction_option = OptionButton.new()
	_direction_option.add_item("Dir + [D]")
	_direction_option.add_item("Dir - [D]")
	controls.add_child(_direction_option)
	_slot_option = OptionButton.new()
	_slot_option.add_item("Slice auto [F]")
	controls.add_child(_slot_option)
	_respin_button = _button("Respin [%s]" % Settings.key_text(&"respin"), respin)
	_respin_button.mouse_entered.connect(_show_respin_odds)
	_respin_button.mouse_exited.connect(_show_end_turn_preview)
	controls.add_child(_respin_button)
	_rewind_button = _button("Undo [%s]" % Settings.key_text(&"rewind"), rewind)
	controls.add_child(_rewind_button)

	var bottom := HBoxContainer.new()
	bottom.add_theme_constant_override("separation", 10)
	root.add_child(bottom)
	_hand_box = HBoxContainer.new()
	_hand_box.add_theme_constant_override("separation", 10)
	_hand_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bottom.add_child(_hand_box)
	_end_turn_button = ZineStamp.new("SEND IT", Palette.CELL_PINK)
	_end_turn_button.name = "SendIt"
	_end_turn_button.pressed.connect(end_turn)
	bottom.add_child(_end_turn_button)
	_zine_elements.append(_end_turn_button)


func _label(text: String) -> Label:
	var l := Label.new()
	l.text = text
	return l


func _button(text: String, on_pressed: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.pressed.connect(on_pressed)
	return b


## The wheel cards aim at under the current card-target toggle.
func _card_target_wheel() -> CombatantState:
	var state := engine.state()
	if state == null:
		return null
	if _card_target_option.selected == 1:
		return state.player
	return state.get_combatant(state.target_id)


func _rebuild_slot_option() -> void:
	var keep := _slot_option.selected
	_slot_option.clear()
	_slot_option.add_item("Slice auto [F]")
	var c := _card_target_wheel()
	if c != null:
		for i in c.wheel.slot_slice_ids.size():
			var slice := engine.content(c.wheel.slot_slice_ids[i]) as SliceData
			var status: int = c.wheel.slice_statuses[i]
			_slot_option.add_item("%d %s%s" % [i, Palette.SLICE_NAMES.get(slice.slice_type, "?") if slice != null else "?", Palette.STATUS_GLYPHS.get(status, "")])
	_slot_option.select(keep if keep >= 0 and keep < _slot_option.item_count else 0)


func _refresh(state: CombatState) -> void:
	var lookup := engine.resolver.lookup
	_status.text = "  Turn %d | RAM %d/%d | free nudge %d | %s" % [state.turn, state.ram, state.max_ram, state.free_nudges,
		"VICTORY" if state.outcome == CombatState.Outcome.VICTORY else ("DEFEAT" if state.outcome == CombatState.Outcome.DEFEAT else "player phase")]
	portrait.caption = "%s  HP %d/%d" % [state.player.display_name, state.player.hp, state.player.max_hp]
	if state.player.source_id != &"":
		portrait.placeholder_label = "[%s PORTRAIT]" % String(state.player.source_id).to_upper()
	portrait.glitch = state.player.hp * 4 <= state.player.max_hp
	portrait.queue_redraw()
	ram_note.clear()
	var tally := ""
	for i in state.ram:
		tally += "|" if (i + 1) % 5 != 0 else "/ "
	ram_note.append("[b]%s[/b] %d/%d" % [tally, state.ram, state.max_ram])
	_refresh_inspect_note()
	var heat := RunManager.campaign.heat if RunManager.campaign != null else 0
	heat_poster.set_heat(heat, engine.resolver.config.heat_max, engine.resolver.config.major_heat_levels())
	background.corp_creep = clampf(float(heat) / 100.0, 0.0, 1.0)
	_player_view.show_combatant(state.player, state.satellites_of(state.player.id), engine.readouts(state.player), lookup)
	var reveal := int(state.flags.get("reveal_phases", 0)) > 0
	var wanted: Array[StringName] = []
	var any_pending := false
	for e in state.enemies:
		if e.is_satellite:
			continue
		wanted.append(e.id)
		if not _enemy_views.has(e.id):
			var v := WheelView.new()
			v.size_flags_vertical = Control.SIZE_EXPAND_FILL
			_enemy_views[e.id] = v
			_enemy_views_box.add_child(v)
		var view: WheelView = _enemy_views[e.id]
		view.highlighted = e.id == state.target_id
		var lines: Array[String] = []
		if reveal:
			var edata := lookup.get_content(e.source_id) as EnemyData
			for p in engine.resolver.upcoming_phases(state, e):
				var parts := PackedStringArray()
				if not p.pointer_ticks.is_empty():
					parts.append(str(Array(CombatResolver.phase_layout(state, edata, p.pointer_ticks))))
				if p.pointer_behavior == RC.PointerBehavior.ORBIT and p.orbit_ticks_per_turn != 0:
					parts.append("%+d/turn" % p.orbit_ticks_per_turn)
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
	for child in _hand_box.get_children():
		child.queue_free()
	for i in state.hand.size():
		var card := lookup.get_content(state.hand[i]) as CardData
		var c := ZineCard.new(card.display_name, card.ram_cost, card.description, i)
		c.disabled = state.is_over() or state.ram < card.ram_cost
		c.tooltip_text = Codex.describe(card)
		var index := i
		c.pressed.connect(func() -> void: play_card(index))
		c.mouse_entered.connect(func() -> void: _show_card_preview(index))
		c.focus_entered.connect(func() -> void:
			if _nav_focus:
				_show_card_preview(index))
		c.mouse_exited.connect(_clear_ghost)
		c.focus_exited.connect(_clear_ghost)
		_hand_box.add_child(c)
	_end_turn_button.disabled = state.is_over()
	_rewind_button.disabled = not engine.can_rewind()
	_link_hand_focus()
	_nav_focus = false  # the refocus below is automatic, not the player moving focus
	UiFocus.focus_first(_hand_box, true, _end_turn_button.get_parent())
	_respin_button.text = "Respin %d [%s]" % [engine.resolver.config.respin_ram_cost, Settings.key_text(&"respin")]
	_respin_button.disabled = state.is_over() or state.ram < engine.resolver.config.respin_ram_cost
	_show_end_turn_preview()


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


## Whether a card has a random effect (Respin, random slice picks): show odds, not rolls.
func _card_is_random(card: CardData) -> bool:
	for e in card.effects:
		if e != null and (e.type == RC.EffectType.RESPIN or e.slice_pick == RC.SlicePick.RANDOM_NON_MISS):
			return true
	return false


## Card hover: the card's result in the preview strip and a dashed ghost arc on the
## wheel it moves (GDD 9.2, STYLE_GUIDE 4). Random effects show odds instead.
func _show_card_preview(hand_index: int) -> void:
	if not engine.has_fight() or hand_index >= engine.state().hand.size():
		return
	var action := _card_action(hand_index)
	var card := engine.content(engine.state().hand[hand_index]) as CardData
	var result := engine.preview(action)
	preview_note.clear()
	if not result.ok():
		preview_note.append("[color=#c05000]%s[/color]" % result.error)
		return
	var random := card != null and _card_is_random(card)
	var target := engine.resolver.card_target(engine.state(), card, action) if card != null else null
	for e in result.events:
		if not e.has("text"):
			continue
		var t: String = e.get("type", "")
		if random and t == "respin" and target != null:
			preview_note.append("%s respins: %s" % [target.display_name, odds_text(target)])
		elif random and t == "status" and target != null:
			preview_note.append("%s gets %s on a random non-Miss slice: %s" % [target.display_name, RC.Status.keys()[e["status"]], odds_text(target, true)])
		else:
			preview_note.append(String(e["text"]))
	if random:
		preview_note.append("[i]random effect: the roll is hidden until you play it[/i]")
		_clear_ghost()
		return
	var after := result.state
	for c in [after.player] + after.living_enemies(false):
		for r in engine.resolver.pointer_readouts(after, c):
			var slice: SliceData = r["slice"]
			preview_note.append("-> %s lands %s %s (%s)" % [c.display_name, Palette.SLICE_GLYPHS.get(slice.slice_type, "?"), slice.display_name, Palette.TIER_NAMES.get(r["tier"], "?")])
	_clear_ghost()
	if after.player.wheel.rotation != engine.state().player.wheel.rotation:
		_player_view.set_ghost(after.player.wheel.rotation, after.player.wheel.inner_rotation)
	for e in after.living_enemies(false):
		var before := engine.state().get_combatant(e.id)
		if before != null and e.wheel.rotation != before.wheel.rotation and _enemy_views.has(e.id):
			_enemy_views[e.id].set_ghost(e.wheel.rotation)


func _show_respin_odds() -> void:
	if not engine.has_fight():
		return
	preview_note.clear()
	preview_note.append("Respin your wheel for %d RAM (a random event: sets a checkpoint)." % engine.resolver.config.respin_ram_cost)
	preview_note.append(odds_text(engine.state().player))


func _show_end_turn_preview() -> void:
	if not engine.has_fight():
		return
	var state := engine.state()
	preview_note.clear()
	if state.is_over():
		preview_note.append("Combat over.")
		return
	var result := engine.preview_end_turn()
	for e in result.events:
		var t: String = e.get("type", "")
		if t in ["pointer", "damage", "block", "shield", "evaded", "bodyguard", "retrigger", "corrupted", "status_absorbed", "died", "combat_end", "heal", "miss", "boss_phase", "deploy", "stolen_intent", "boss_migrate_telegraph"]:
			preview_note.append(String(e["text"]))
		elif t == "status":
			var owner := state.get_combatant(e["target"])
			if e.get("random", false):
				preview_note.append("%s gets %s on a random non-Miss slice (%s)." % [owner.display_name, RC.Status.keys()[e["status"]], odds_text(owner, true)])
			else:
				preview_note.append(String(e["text"]))  # a fixed slot: say which
	var after := result.state
	var summary := PackedStringArray()
	for e in after.enemies:
		if not e.is_satellite or e.is_alive():
			summary.append("%s %d HP" % [e.display_name, e.hp])
	preview_note.append("[b]=> You %d HP | %s[/b]" % [after.player.hp, ", ".join(summary)])
