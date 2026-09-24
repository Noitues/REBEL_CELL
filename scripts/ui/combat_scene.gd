extends Control
## Combat scene (M4 look): wireframe arena with zine HUD (STYLE_GUIDE 1, 4-5, GDD 9.2).
## Layout (1280x720 design canvas): Polaroid, RAM tally and Heat on the left; the wheels
## in the middle where nothing zine ever covers them; preview and log strips on the
## right; card stickers along the bottom with the SEND IT stamp. Full keyboard play:
## 1-9 play cards, Q/E nudge, W nudge wheel, R ring, T card target, Tab target, Space end
## turn, Z rewind, Esc settings. Signal Up, Call Down: widgets call the engine only.

const ENEMY_CHOICES: Array[StringName] = [&"collections_agent", &"compliance_officer", &"dosage_dispenser"]
const CLASS_ID := &"breaker"
const RING_ID := &"rank:1"

@export var auto_start: bool = true

@onready var engine: CombatEngine = $CombatEngine

var background: WireframeBackground
var portrait: Polaroid
var heat_poster: HeatPoster
var ram_note: ZineNote
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
var _hand_box: HBoxContainer
var _end_turn_button: ZineStamp
var _rewind_button: Button
var _picker_controls: Array[Control] = []
var _settings_panel: SettingsPanel = null
var _arena: Control
var _zine_elements: Array[Control] = []
var _last_events: Array[Dictionary] = []


func _ready() -> void:
	UiTheme.apply(self)
	_build_ui()
	engine.state_changed.connect(_on_state_changed)
	engine.action_refused.connect(_on_action_refused)
	engine.fight_ended.connect(_on_fight_ended)
	if auto_start:
		start_fight(ENEMY_CHOICES[0], int(_seed_spin.value))


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
	engine.rewind()


func nudge(direction: int) -> void:
	var wheel_id := _selected_nudge_wheel()
	var ring := RC.RingScope.INNER if _nudge_ring_option.selected == 1 else RC.RingScope.OUTER
	engine.submit(CombatAction.nudge(wheel_id, direction, ring))


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
	_refresh_toggle_labels()


func toggle_ring() -> void:
	_nudge_ring_option.select((_nudge_ring_option.selected + 1) % 2)
	_refresh_toggle_labels()


func toggle_nudge_wheel() -> void:
	_nudge_wheel_option.select((_nudge_wheel_option.selected + 1) % 2)
	_refresh_toggle_labels()


func open_settings() -> void:
	if _settings_panel != null:
		_settings_panel.queue_free()
		_settings_panel = null
		return
	_settings_panel = SettingsPanel.new()
	_settings_panel.position = Vector2(size.x / 2.0 - 180, 120)
	_settings_panel.closed.connect(open_settings)
	add_child(_settings_panel)


## Layout rule (STYLE_GUIDE 4): zine elements never cover the wheels. Returns the
## names of offending elements (empty = the rule holds).
func layout_violations() -> Array[String]:
	var out: Array[String] = []
	var wheels: Array[WheelView] = [_player_view]
	for v in _enemy_views.values():
		wheels.append(v)
	for z in _zine_elements:
		if not is_instance_valid(z) or not z.visible:
			continue
		var zr := z.get_global_rect()
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

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("open_settings"):
		open_settings()
		get_viewport().set_input_as_handled()
		return
	if not engine.has_fight():
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
	else:
		return
	get_viewport().set_input_as_handled()


# --- Engine callbacks --------------------------------------------------------------

func _on_state_changed(state: CombatState, events: Array[Dictionary]) -> void:
	_last_events = events
	for e in events:
		if e.has("text"):
			log_note.append(String(e["text"]))
	_refresh(state)
	_feedback(state, events)


func _on_action_refused(reason: String) -> void:
	log_note.append("[color=#c05000]%s[/color]" % reason)
	preview_note.clear()
	preview_note.append(reason)


func _on_fight_ended(outcome: int) -> void:
	log_note.append("[b]%s[/b]" % ("VICTORY" if outcome == CombatState.Outcome.VICTORY else "DEFEAT"))
	if outcome == CombatState.Outcome.VICTORY:
		Fx.flash(Palette.CELL_ACID, 0.3)


## Precision and action feedback (STYLE_GUIDE 5, GDD 10): Perfect = latch + wheel-local
## inversion + 2-frame freeze (+ a limited flash); Good = click; Partial = stutter shake;
## Miss slice = static burst. Nudges tick, spins run down, flips clack.
func _feedback(state: CombatState, events: Array[Dictionary]) -> void:
	for e in events:
		match String(e.get("type", "")):
			"nudge":
				AudioDirector.play_sfx("tick")
			"spin":
				AudioDirector.play_spin(int(e.get("moved", 0)))
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
				elif tier == RC.PrecisionTier.PERFECT:
					_perfect_feedback(_player_view)
				elif tier == RC.PrecisionTier.PARTIAL:
					_stutter_view(_player_view)
			"boss_phase":
				AudioDirector.play_sfx("alarm")
				Fx.flash(Palette.CORP_SOLACE, 0.3)


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


func _start_music() -> void:
	var boss := false
	if engine.has_fight():
		for e in engine.state().enemies:
			var data := engine.content(e.source_id) as EnemyData
			if data != null and (data.is_boss or data.is_mini_boss):
				boss = true
	AudioDirector.play_music("boss" if boss else "combat")
	var band := 0
	if RunManager.campaign != null:
		for t in [25, 50, 75]:
			if RunManager.campaign.heat >= t:
				band += 1
	AudioDirector.set_heat_layers(band)


# --- UI ------------------------------------------------------------------------------

func _build_ui() -> void:
	background = WireframeBackground.new()
	add_child(background)
	var root := VBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.add_theme_constant_override("separation", 4)
	add_child(root)

	var top := HBoxContainer.new()
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
	ram_note = ZineNote.new("RAM", Vector2(170, 64))
	ram_note.name = "RamTally"
	left.add_child(ram_note)
	heat_poster = HeatPoster.new(false)
	heat_poster.name = "HeatPoster"
	left.add_child(heat_poster)
	_zine_elements.append_array([portrait, ram_note, heat_poster])

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

	var controls := HBoxContainer.new()
	root.add_child(controls)
	controls.add_child(_label("Target [Tab]"))
	_target_option = OptionButton.new()
	_target_option.item_selected.connect(func(i: int) -> void: engine.submit(CombatAction.target(_target_option.get_item_metadata(i))))
	controls.add_child(_target_option)
	_nudge_wheel_option = OptionButton.new()
	_nudge_wheel_option.add_item("Nudge own [W]")
	_nudge_wheel_option.add_item("Nudge target [W]")
	controls.add_child(_nudge_wheel_option)
	_nudge_ring_option = OptionButton.new()
	_nudge_ring_option.add_item("Outer [R]")
	_nudge_ring_option.add_item("Inner [R]")
	controls.add_child(_nudge_ring_option)
	controls.add_child(_button("-1 [Q]", func() -> void: nudge(-1)))
	controls.add_child(_button("+1 [E]", func() -> void: nudge(1)))
	_card_target_option = OptionButton.new()
	_card_target_option.add_item("Cards: target [T]")
	_card_target_option.add_item("Cards: own [T]")
	controls.add_child(_card_target_option)
	_rewind_button = _button("Rewind [Z]", rewind)
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


func _refresh_toggle_labels() -> void:
	pass  # OptionButtons show their own selection; nothing else to sync.


func _refresh(state: CombatState) -> void:
	var lookup := engine.resolver.lookup
	var cls := lookup.get_content(state.player.source_id) as ClassData
	_status.text = "  Turn %d | RAM %d/%d | free nudge %d | %s" % [state.turn, state.ram, cls.max_ram, state.free_nudges,
		"VICTORY" if state.outcome == CombatState.Outcome.VICTORY else ("DEFEAT" if state.outcome == CombatState.Outcome.DEFEAT else "player phase")]
	portrait.caption = "%s  HP %d/%d" % [state.player.display_name, state.player.hp, state.player.max_hp]
	portrait.glitch = state.player.hp * 4 <= state.player.max_hp
	portrait.queue_redraw()
	ram_note.clear()
	var tally := ""
	for i in state.ram:
		tally += "|" if (i + 1) % 5 != 0 else "/ "
	ram_note.append("[b]%s[/b] %d/%d" % [tally, state.ram, cls.max_ram])
	var heat := RunManager.campaign.heat if RunManager.campaign != null else 0
	heat_poster.set_heat(heat, engine.resolver.config.heat_max)
	background.corp_creep = clampf(float(heat) / 100.0, 0.0, 1.0)
	_player_view.show_combatant(state.player, [], engine.readouts(state.player), lookup)
	var wanted: Array[StringName] = []
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
		view.show_combatant(e, state.satellites_of(e.id), engine.readouts(e), lookup)
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
	for child in _hand_box.get_children():
		child.queue_free()
	for i in state.hand.size():
		var card := lookup.get_content(state.hand[i]) as CardData
		var c := ZineCard.new(card.display_name, card.ram_cost, card.description, i)
		c.disabled = state.is_over() or state.ram < card.ram_cost
		var index := i
		c.pressed.connect(func() -> void: play_card(index))
		c.mouse_entered.connect(func() -> void: _show_card_preview(index))
		c.focus_entered.connect(func() -> void: _show_card_preview(index))
		c.mouse_exited.connect(_clear_ghost)
		c.focus_exited.connect(_clear_ghost)
		_hand_box.add_child(c)
	_end_turn_button.disabled = state.is_over()
	_rewind_button.disabled = not engine.can_rewind()
	_show_end_turn_preview()


func _selected_nudge_wheel() -> StringName:
	if _nudge_wheel_option.selected == 1 and engine.state().target_id != &"":
		return engine.state().target_id
	return &"player"


func _card_action(hand_index: int) -> CombatAction:
	var state := engine.state()
	var wheel_id: StringName = &"player" if _card_target_option.selected == 1 else state.target_id
	var a := CombatAction.play_card(hand_index, wheel_id)
	a.ring = RC.RingScope.INNER if _nudge_ring_option.selected == 1 else RC.RingScope.OUTER
	a.direction = 1
	return a


func _clear_ghost() -> void:
	_player_view.set_ghost(null)
	for v in _enemy_views.values():
		v.set_ghost(null)


## Card hover: the card's result in the preview strip and a dashed ghost arc on the
## wheel it moves (GDD 9.2, STYLE_GUIDE 4).
func _show_card_preview(hand_index: int) -> void:
	if not engine.has_fight() or hand_index >= engine.state().hand.size():
		return
	var action := _card_action(hand_index)
	var result := engine.preview(action)
	preview_note.clear()
	if not result.ok():
		preview_note.append("[color=#c05000]%s[/color]" % result.error)
		return
	for e in result.events:
		if e.has("text"):
			preview_note.append(String(e["text"]))
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


func _show_end_turn_preview() -> void:
	var state := engine.state()
	preview_note.clear()
	if state.is_over():
		preview_note.append("Combat over.")
		return
	var result := engine.preview_end_turn()
	for e in result.events:
		var t: String = e.get("type", "")
		if t in ["pointer", "damage", "block", "shield", "evaded", "bodyguard", "retrigger", "corrupted", "status_absorbed", "died", "combat_end", "heal", "miss", "boss_phase"]:
			preview_note.append(String(e["text"]))
		elif t == "status":
			preview_note.append("%s gets %s on a random non-Miss slice." % [state.get_combatant(e["target"]).display_name, RC.Status.keys()[e["status"]]])
	var after := result.state
	var summary := PackedStringArray()
	for e in after.enemies:
		summary.append("%s %d HP" % [e.display_name, e.hp])
	preview_note.append("[b]=> You %d HP | %s[/b]" % [after.player.hp, ", ".join(summary)])
