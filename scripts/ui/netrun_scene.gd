extends Control
## Functional M2 netrun scene (placeholder look): start screen, map, combat (embedded
## CombatScene), rewards, Terminal events, Modem shop and the run summary. Every
## action goes through RunManager's NetrunSession; the scene only displays state.

const COMBAT_SCENE := preload("res://scenes/combat/combat_scene.tscn")
const NODE_LABELS := {RC.InfilNodeType.ROUTER: "Router", RC.InfilNodeType.TERMINAL: "Terminal",
	RC.InfilNodeType.MODEM: "Modem", RC.InfilNodeType.SERVER_RACK: "Server Rack"}

var _status: Label
var _panel_host: PanelContainer
var _log: RichTextLabel
var _panel: Control = null
var combat_scene: Control = null


func _ready() -> void:
	_build_ui()
	var args := OS.get_cmdline_user_args()
	if args.has("--demo-run") or args.has("--demo-combat"):
		# Dev shortcut for screenshots: godot --path . -- --demo-run (uses its own save slot)
		RunManager.save_slot = "demo"
		new_campaign(1)
		start_run(1)
		if args.has("--demo-combat"):
			enter_node(RunManager.netrun.available_nodes()[0])
		return
	if RunManager.has_active_run():
		_show_current()
	else:
		_show_start()


# --- Public API (used by buttons and the integration test) --------------------------

func new_campaign(seed: int) -> void:
	RunManager.new_campaign(seed)
	_log.append_text("[b]New campaign[/b] (seed %d): %d Schematics, %d rookies.\n" % [seed, RunManager.campaign.schematics, RunManager.campaign.roster.size()])
	_show_start()


func start_run(tier: int = 1) -> void:
	var s := RunManager.start_run(&"", tier)
	if s == null:
		_log.append_text("[color=orange]No living operative: recruit one at HQ (M3).[/color]\n")
		return
	_report(s.last_events)
	_show_current()


func resume() -> void:
	if RunManager.resume():
		_log.append_text("[b]Resumed.[/b]\n")
		_show_current()
	else:
		_log.append_text("[color=orange]Nothing to resume.[/color]\n")


func enter_node(node_id: StringName) -> void:
	var s := RunManager.netrun
	_report(s.enter_node(node_id))
	RunManager.after_step()
	_show_current()


func choose_reward(index: int, slot: int = -1) -> void:
	_report(RunManager.netrun.choose_reward(index, slot))
	RunManager.after_step()
	_show_current()


func skip_reward() -> void:
	_report(RunManager.netrun.skip_reward())
	RunManager.after_step()
	_show_current()


func choose_event(index: int) -> void:
	_report(RunManager.netrun.choose_event_option(index))
	RunManager.after_step()
	_show_current()


func buy(kind: String, index: int, slot: int = -1) -> void:
	_report(RunManager.netrun.buy(kind, index, slot))
	RunManager.after_step()
	_show_current()


func remove_card(deck_index: int) -> void:
	_report(RunManager.netrun.remove_card(deck_index))
	RunManager.after_step()
	_show_current()


func overwrite_slice(slot: int, stock_index: int) -> void:
	_report(RunManager.netrun.overwrite_slice(slot, stock_index))
	RunManager.after_step()
	_show_current()


func leave_shop() -> void:
	_report(RunManager.netrun.leave_shop())
	RunManager.after_step()
	_show_current()


func finish_run() -> void:
	RunManager.clear_run()
	_show_start()


func save_and_quit() -> void:
	RunManager.autosave()
	_log.append_text("Saved.\n")
	_show_start()


# --- Panels --------------------------------------------------------------------------

func _show_current() -> void:
	var s := RunManager.netrun
	if s == null:
		_show_start()
		return
	_refresh_status()
	match s.run.phase:
		RunState.Phase.MAP:
			_show_map()
		RunState.Phase.COMBAT:
			_show_combat()
		RunState.Phase.REWARD:
			_show_reward()
		RunState.Phase.EVENT:
			_show_event()
		RunState.Phase.SHOP:
			_show_shop()
		_:
			_show_end()


func _set_panel(p: Control) -> void:
	if _panel != null:
		_panel.queue_free()
	_panel = p
	combat_scene = null
	_panel_host.add_child(p)
	# The combat panel brings its own log; give it the height instead.
	_log.custom_minimum_size = Vector2(0, 50 if p.get_script() == COMBAT_SCENE.get_script() or p.has_method("attach_netrun") else 110)


func _show_start() -> void:
	_refresh_status()
	var box := VBoxContainer.new()
	box.add_child(_label("REBEL_CELL - netrun (M2 placeholder)"))
	var row := HBoxContainer.new()
	box.add_child(row)
	row.add_child(_label("Campaign seed:"))
	var seed_spin := SpinBox.new()
	seed_spin.min_value = 0
	seed_spin.max_value = 999999
	seed_spin.value = 1
	row.add_child(seed_spin)
	row.add_child(_button("New campaign", func() -> void: new_campaign(int(seed_spin.value))))
	if RunManager.has_save():
		box.add_child(_button("Resume saved game", resume))
	if RunManager.campaign != null:
		var living := RunManager.campaign.living_operatives()
		var info := "Campaign: Heat %d, Schematics %d, roster %d living." % [RunManager.campaign.heat, RunManager.campaign.schematics, living.size()]
		box.add_child(_label(info))
		for op in living:
			box.add_child(_label("  %s (%s) Rank %d, HP %d/%d, deck %d, daemons %d" % [op.name, op.class_id, op.rank, op.hp, op.max_hp, op.deck.size(), op.daemon_ids.size()]))
		if RunManager.has_active_run():
			box.add_child(_button("Continue the current run", _show_current))
		elif not living.is_empty():
			box.add_child(_button("Start a Tier 1 netrun", func() -> void: start_run(1)))
	_set_panel(box)


func _show_map() -> void:
	var s := RunManager.netrun
	var box := VBoxContainer.new()
	box.add_child(_label("Pick the next node (Heat cost shown; you must follow the links)."))
	var columns := HBoxContainer.new()
	box.add_child(columns)
	var available := s.available_nodes()
	for layer in s.run.map.layers:
		var col := VBoxContainer.new()
		col.custom_minimum_size = Vector2(150, 0)
		col.add_child(_label("Layer %d" % layer[0]["layer"]))
		for node in layer:
			var b := Button.new()
			var heat: int = node["heat"]
			var text: String = "%s%s" % [NODE_LABELS.get(node["type"], "?"), " (elite)" if node["elite"] and node["type"] == RC.InfilNodeType.ROUTER else ""]
			if heat != 0:
				text += " +%d Heat" % heat
			if node["id"] == s.run.current_node_id:
				text = "> " + text
			elif s.run.visited.has(node["id"]):
				text = "[done] " + text
			b.text = text
			b.tooltip_text = "%s -> %s" % [node["id"], ", ".join(node["next"])]
			b.disabled = not available.has(node["id"])
			var id: StringName = node["id"]
			b.pressed.connect(func() -> void: enter_node(id))
			col.add_child(b)
		columns.add_child(col)
	box.add_child(_button("Save & quit to start screen", save_and_quit))
	_set_panel(box)


func _show_combat() -> void:
	var s := RunManager.netrun
	var scene: Control = COMBAT_SCENE.instantiate()
	scene.auto_start = false
	scene.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_set_panel(scene)
	combat_scene = scene
	scene.attach_netrun(s)
	scene.engine.state_changed.connect(_on_combat_state_changed)


func _on_combat_state_changed(state: CombatState, _events: Array[Dictionary]) -> void:
	_refresh_status()
	if state.is_over():
		RunManager.after_step()
		_report(RunManager.netrun.last_events)
		# Leave the final combat state visible for a moment, then move on.
		var timer := get_tree().create_timer(0.8)
		timer.timeout.connect(_show_current)


func _show_reward() -> void:
	var s := RunManager.netrun
	var offer := s.current_reward()
	var box := VBoxContainer.new()
	box.add_child(_label("Reward: choose a %s" % offer["kind"]))
	var slot_option: OptionButton = null
	if offer["kind"] == "firmware":
		var row := HBoxContainer.new()
		row.add_child(_label("Socket into slot:"))
		slot_option = OptionButton.new()
		for i in s.run.operative.slot_slice_ids.size():
			var fw := s.run.operative.slot_firmware_ids[i]
			slot_option.add_item("%d: %s%s" % [i, s.run.operative.slot_slice_ids[i], (" {%s}" % fw) if fw != &"" else ""])
		row.add_child(slot_option)
		box.add_child(row)
	for i in offer["options"].size():
		var id := StringName(String(offer["options"][i]))
		var res := s.lookup.get_content(id)
		var b := Button.new()
		b.text = "%s - %s" % [res.get("display_name"), res.get("description")]
		var index: int = i
		b.pressed.connect(func() -> void: choose_reward(index, slot_option.selected if slot_option != null else -1))
		box.add_child(b)
	box.add_child(_button("Skip", skip_reward))
	_set_panel(box)


func _show_event() -> void:
	var s := RunManager.netrun
	var ev := s.current_event()
	var box := VBoxContainer.new()
	box.add_child(_label("[%s] %s" % [RC.Voice.keys()[ev.speaker], ev.title]))
	var text := RichTextLabel.new()
	text.fit_content = true
	text.custom_minimum_size = Vector2(600, 60)
	text.text = ev.text
	box.add_child(text)
	for i in ev.choices.size():
		var c := ev.choices[i]
		var b := Button.new()
		b.text = c.label
		b.disabled = c.cycle_cost > s.run.cycles
		var index := i
		b.pressed.connect(func() -> void: choose_event(index))
		box.add_child(b)
	_set_panel(box)


func _show_shop() -> void:
	var s := RunManager.netrun
	var shop := s.run.shop
	var box := VBoxContainer.new()
	box.add_child(_label("Modem - %d Cycles" % s.run.cycles))
	for kind in ["cards", "firmware", "daemons"]:
		var prices: Array = shop.get(kind.trim_suffix("s") + "_prices", [])
		for i in shop.get(kind, []).size():
			var id := StringName(String(shop[kind][i]))
			var res := s.lookup.get_content(id)
			var row := HBoxContainer.new()
			row.add_child(_label("%s: %s (%d Cycles) - %s" % [kind, res.get("display_name"), prices[i], res.get("description")]))
			var slot_option: OptionButton = null
			if kind == "firmware":
				slot_option = OptionButton.new()
				for k in s.run.operative.slot_slice_ids.size():
					slot_option.add_item("slot %d: %s" % [k, s.run.operative.slot_slice_ids[k]])
				row.add_child(slot_option)
			var index: int = i
			var k: String = kind
			row.add_child(_button("Buy", func() -> void: buy(k, index, slot_option.selected if slot_option != null else -1)))
			box.add_child(row)
	var removal := HBoxContainer.new()
	removal.add_child(_label("Remove a card (%d Cycles):" % s.card_removal_price()))
	var deck_option := OptionButton.new()
	for i in s.run.operative.deck.size():
		deck_option.add_item("%d: %s" % [i, s.run.operative.deck[i]])
	removal.add_child(deck_option)
	removal.add_child(_button("Remove", func() -> void: remove_card(deck_option.selected)))
	box.add_child(removal)
	var overwrite := HBoxContainer.new()
	overwrite.add_child(_label("Overwrite a slice (100; Miss slot 150):"))
	var slot_pick := OptionButton.new()
	for i in s.run.operative.slot_slice_ids.size():
		slot_pick.add_item("slot %d: %s" % [i, s.run.operative.slot_slice_ids[i]])
	overwrite.add_child(slot_pick)
	var slice_pick := OptionButton.new()
	for sid in shop.get("slices", []):
		slice_pick.add_item(String(sid))
	overwrite.add_child(slice_pick)
	overwrite.add_child(_button("Overwrite", func() -> void: overwrite_slice(slot_pick.selected, slice_pick.selected)))
	box.add_child(overwrite)
	box.add_child(_button("Leave the Modem", leave_shop))
	_set_panel(box)


func _show_end() -> void:
	var s := RunManager.netrun
	var box := VBoxContainer.new()
	var won := s.run.outcome == RunState.Outcome.COMPLETED
	box.add_child(_label("NETRUN %s" % ("COMPLETE" if won else "FAILED - operative lost")))
	box.add_child(_label("Combats won %d, elites %d, Cycles %d, banked Schematics %d, Heat gained %d." % [s.run.combats_won, s.run.elites_defeated, s.run.cycles, s.run.banked_schematics, s.run.heat_gained]))
	box.add_child(_label("Campaign: Heat %d, Schematics %d, Armory %d." % [s.campaign.heat, s.campaign.schematics, s.campaign.armory.size()]))
	box.add_child(_button("Back to HQ", finish_run))
	_set_panel(box)


# --- Helpers --------------------------------------------------------------------------

func _refresh_status() -> void:
	var c := RunManager.campaign
	if c == null:
		_status.text = "No campaign."
		return
	var s := RunManager.netrun
	var text := "Heat %d/%d | Schematics %d | Armory %d" % [c.heat, RunManager.resolver.config.heat_max, c.schematics, c.armory.size()]
	if s != null and not s.run.is_over():
		var op := s.run.operative
		text += " || Run T%d seed %d | %s HP %d/%d Rank %d | Cycles %d | banked %d | node %s" % [s.run.tier, s.run.run_seed, op.name, op.hp, op.max_hp, op.rank, s.run.cycles, s.run.banked_schematics, s.run.current_node_id]
	_status.text = text


func _report(events: Array[Dictionary]) -> void:
	for e in events:
		if e.has("text"):
			_log.append_text(String(e["text"]) + "\n")


func _build_ui() -> void:
	var root := VBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(root)
	_status = Label.new()
	root.add_child(_status)
	_panel_host = PanelContainer.new()
	_panel_host.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(_panel_host)
	_log = RichTextLabel.new()
	_log.bbcode_enabled = true
	_log.scroll_following = true
	_log.custom_minimum_size = Vector2(0, 110)
	root.add_child(_log)


func _label(text: String) -> Label:
	var l := Label.new()
	l.text = text
	return l


func _button(text: String, on_pressed: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.pressed.connect(on_pressed)
	return b
