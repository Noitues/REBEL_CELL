extends Control
## Functional M1 combat scene: two (or more) wheels, hand, preview readouts, targeting,
## nudge, end turn, rewind and a log. Builds its widgets in code; placeholder look.
## Signal Up, Call Down: widgets call the engine, the engine reports state.

const ENEMY_CHOICES: Array[StringName] = [&"collections_agent", &"compliance_officer", &"dosage_dispenser"]
const CLASS_ID := &"breaker"
const RING_ID := &"rank:1"

@onready var engine: CombatEngine = $CombatEngine

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
var _preview_label: RichTextLabel
var _end_turn_button: Button
var _rewind_button: Button
var _log: RichTextLabel
var _turn_readouts: RichTextLabel


func _ready() -> void:
	_build_ui()
	engine.state_changed.connect(_on_state_changed)
	engine.action_refused.connect(_on_action_refused)
	engine.fight_ended.connect(_on_fight_ended)
	start_fight(ENEMY_CHOICES[0], int(_seed_spin.value))


# --- Public (also used by the integration test) ----------------------------------

func start_fight(enemy_id: StringName, combat_seed: int) -> void:
	_log.clear()
	_log.append_text("[b]New fight:[/b] %s vs %s (seed %d)\n" % [CLASS_ID, enemy_id, combat_seed])
	engine.start_fight(CLASS_ID, [enemy_id], combat_seed, RING_ID)


func end_turn() -> void:
	engine.submit(CombatAction.end_turn())


func rewind() -> void:
	engine.rewind()


func nudge(direction: int) -> void:
	var wheel_id := _selected_nudge_wheel()
	var ring := RC.RingScope.INNER if _nudge_ring_option.selected == 1 else RC.RingScope.OUTER
	engine.submit(CombatAction.nudge(wheel_id, direction, ring))


func play_card(hand_index: int) -> void:
	engine.submit(_card_action(hand_index))


func cycle_target() -> void:
	if _target_option.item_count == 0:
		return
	var next := (_target_option.selected + 1) % _target_option.item_count
	_target_option.select(next)
	engine.submit(CombatAction.target(_target_option.get_item_metadata(next)))


# --- Input -----------------------------------------------------------------------

func _unhandled_input(event: InputEvent) -> void:
	if not engine.has_fight():
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
	else:
		return
	get_viewport().set_input_as_handled()


# --- Engine callbacks --------------------------------------------------------------

func _on_state_changed(state: CombatState, events: Array[Dictionary]) -> void:
	for e in events:
		if e.has("text"):
			_log.append_text(String(e["text"]) + "\n")
	_refresh(state)


func _on_action_refused(reason: String) -> void:
	_log.append_text("[color=orange]%s[/color]\n" % reason)
	_preview_label.text = reason


func _on_fight_ended(outcome: int) -> void:
	_log.append_text("[b]%s[/b]\n" % ("VICTORY" if outcome == CombatState.Outcome.VICTORY else "DEFEAT"))


# --- UI ------------------------------------------------------------------------------

func _build_ui() -> void:
	var root := VBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(root)

	var top := HBoxContainer.new()
	root.add_child(top)
	top.add_child(_label("Fight:"))
	for enemy_id in ENEMY_CHOICES:
		var b := Button.new()
		b.text = String(enemy_id)
		b.pressed.connect(func() -> void: start_fight(enemy_id, int(_seed_spin.value)))
		top.add_child(b)
	top.add_child(_label("Seed:"))
	_seed_spin = SpinBox.new()
	_seed_spin.min_value = 0
	_seed_spin.max_value = 999999
	_seed_spin.value = 1
	top.add_child(_seed_spin)
	_status = _label("")
	top.add_child(_status)

	var middle := HBoxContainer.new()
	middle.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(middle)
	_player_view = WheelView.new()
	middle.add_child(_player_view)
	_enemy_views_box = VBoxContainer.new()
	middle.add_child(_enemy_views_box)
	var side := VBoxContainer.new()
	side.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	middle.add_child(side)
	_turn_readouts = RichTextLabel.new()
	_turn_readouts.bbcode_enabled = true
	_turn_readouts.custom_minimum_size = Vector2(300, 150)
	_turn_readouts.size_flags_vertical = Control.SIZE_EXPAND_FILL
	side.add_child(_label("End Turn preview (what will resolve):"))
	side.add_child(_turn_readouts)
	_log = RichTextLabel.new()
	_log.bbcode_enabled = true
	_log.scroll_following = true
	_log.custom_minimum_size = Vector2(300, 180)
	_log.size_flags_vertical = Control.SIZE_EXPAND_FILL
	side.add_child(_label("Log:"))
	side.add_child(_log)

	var controls := HBoxContainer.new()
	root.add_child(controls)
	controls.add_child(_label("Target (Tab):"))
	_target_option = OptionButton.new()
	_target_option.item_selected.connect(func(i: int) -> void: engine.submit(CombatAction.target(_target_option.get_item_metadata(i))))
	controls.add_child(_target_option)
	controls.add_child(_label("Nudge wheel:"))
	_nudge_wheel_option = OptionButton.new()
	_nudge_wheel_option.add_item("Own wheel")
	_nudge_wheel_option.add_item("Target wheel")
	controls.add_child(_nudge_wheel_option)
	_nudge_ring_option = OptionButton.new()
	_nudge_ring_option.add_item("Outer ring")
	_nudge_ring_option.add_item("Inner ring")
	controls.add_child(_nudge_ring_option)
	var left := Button.new()
	left.text = "Nudge -1 (Q)"
	left.pressed.connect(func() -> void: nudge(-1))
	controls.add_child(left)
	var right := Button.new()
	right.text = "Nudge +1 (E)"
	right.pressed.connect(func() -> void: nudge(1))
	controls.add_child(right)
	var controls2 := HBoxContainer.new()
	root.add_child(controls2)
	controls2.add_child(_label("Card target:"))
	_card_target_option = OptionButton.new()
	_card_target_option.add_item("Target wheel")
	_card_target_option.add_item("Own wheel")
	controls2.add_child(_card_target_option)
	controls2.add_child(_label("   "))
	_end_turn_button = Button.new()
	_end_turn_button.text = "End Turn (Space)"
	_end_turn_button.pressed.connect(end_turn)
	controls2.add_child(_end_turn_button)
	_rewind_button = Button.new()
	_rewind_button.text = "Rewind (Z / Ctrl+Z)"
	_rewind_button.pressed.connect(rewind)
	controls2.add_child(_rewind_button)

	_preview_label = RichTextLabel.new()
	_preview_label.bbcode_enabled = true
	_preview_label.custom_minimum_size = Vector2(0, 70)
	_preview_label.fit_content = true
	root.add_child(_label("Card preview (hover a card):"))
	root.add_child(_preview_label)
	_hand_box = HBoxContainer.new()
	root.add_child(_hand_box)


func _label(text: String) -> Label:
	var l := Label.new()
	l.text = text
	return l


func _refresh(state: CombatState) -> void:
	var lookup := engine.resolver.lookup
	var cls := lookup.get_content(state.player.source_id) as ClassData
	_status.text = "  Turn %d | RAM %d/%d | free nudge %d | %s" % [state.turn, state.ram, cls.max_ram, state.free_nudges,
		"VICTORY" if state.outcome == CombatState.Outcome.VICTORY else ("DEFEAT" if state.outcome == CombatState.Outcome.DEFEAT else "player phase")]
	_player_view.show_combatant(state.player, [], engine.readouts(state.player), lookup)
	# Enemy wheels (satellites are drawn on their host).
	var wanted: Array[StringName] = []
	for e in state.enemies:
		if e.is_satellite:
			continue
		wanted.append(e.id)
		if not _enemy_views.has(e.id):
			var v := WheelView.new()
			_enemy_views[e.id] = v
			_enemy_views_box.add_child(v)
		var view: WheelView = _enemy_views[e.id]
		view.highlighted = e.id == state.target_id
		view.show_combatant(e, state.satellites_of(e.id), engine.readouts(e), lookup)
	for id in _enemy_views.keys():
		if not wanted.has(id):
			_enemy_views[id].queue_free()
			_enemy_views.erase(id)
	# Targets: every living enemy and satellite.
	_target_option.clear()
	var idx := 0
	for e in state.living_enemies(true):
		_target_option.add_item("%s (%d HP)" % [e.display_name, e.hp])
		_target_option.set_item_metadata(idx, e.id)
		if e.id == state.target_id:
			_target_option.select(idx)
		idx += 1
	# Hand.
	for child in _hand_box.get_children():
		child.queue_free()
	for i in state.hand.size():
		var card := lookup.get_content(state.hand[i]) as CardData
		var b := Button.new()
		b.text = "%s [%d]" % [card.display_name, card.ram_cost]
		b.tooltip_text = card.description
		b.disabled = state.is_over()
		var index := i
		b.pressed.connect(func() -> void: play_card(index))
		b.mouse_entered.connect(func() -> void: _show_card_preview(index))
		_hand_box.add_child(b)
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


func _show_card_preview(hand_index: int) -> void:
	if not engine.has_fight() or hand_index >= engine.state().hand.size():
		return
	var action := _card_action(hand_index)
	var result := engine.preview(action)
	if not result.ok():
		_preview_label.text = "[color=orange]%s[/color]" % result.error
		return
	var lines := PackedStringArray()
	for e in result.events:
		if e.has("text"):
			lines.append(String(e["text"]))
	var after := result.state
	for c in [after.player] + after.living_enemies(false):
		for r in engine.resolver.pointer_readouts(after, c):
			var slice: SliceData = r["slice"]
			lines.append("-> %s would land %s (%s)" % [c.display_name, slice.display_name, RC.PrecisionTier.keys()[r["tier"]]])
	_preview_label.text = "\n".join(lines)


func _show_end_turn_preview() -> void:
	var state := engine.state()
	if state.is_over():
		_turn_readouts.text = "Combat over."
		return
	var result := engine.preview_end_turn()
	var lines := PackedStringArray()
	for e in result.events:
		var t: String = e.get("type", "")
		if t in ["pointer", "damage", "block", "shield", "evaded", "bodyguard", "retrigger", "corrupted", "status_absorbed", "died", "combat_end", "heal", "miss"]:
			lines.append(String(e["text"]))
		elif t == "status":
			lines.append("%s gets %s on a random non-Miss slice." % [state.get_combatant(e["target"]).display_name, RC.Status.keys()[e["status"]]])
	var after := result.state
	lines.append("=> You: %d HP | %s" % [after.player.hp, ", ".join(_enemy_hp_summary(after))])
	_turn_readouts.text = "\n".join(lines)


func _enemy_hp_summary(state: CombatState) -> PackedStringArray:
	var out := PackedStringArray()
	for e in state.enemies:
		out.append("%s: %d HP" % [e.display_name, e.hp])
	return out
