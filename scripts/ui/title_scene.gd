extends Control
## Title / main menu (gap analysis 2.5): Continue, Campaigns (three save slots with a
## summary, new / load / delete with confirmation), Tutorial, Codex, Stats &
## achievements, Options, Quit. Cyberdeck world with the graffiti tag. Every action goes
## through RunManager; the scene only displays state.

const SLOTS: Array[String] = ["1", "2", "3"]

var background: CyberdeckBackground
var _panel_host: VBoxContainer
var _panel: Control = null
var panel_name: String = ""
var _confirm: ConfirmDialog = null


func _ready() -> void:
	UiTheme.apply(self)
	background = CyberdeckBackground.new()
	add_child(background)
	var root := VBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.add_theme_constant_override("separation", 8)
	add_child(root)
	var header := HBoxContainer.new()
	header.add_child(GraffitiTag.new("REBEL_CELL"))
	var v := Label.new()
	v.text = "  v%s" % ProjectSettings.get_setting("application/config/version", "dev")
	header.add_child(v)
	root.add_child(header)
	_panel_host = VBoxContainer.new()
	_panel_host.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(_panel_host)
	AudioDirector.play_music("hq")
	var args := OS.get_cmdline_user_args()
	if args.has("--demo-options"):
		show_options()
	elif args.has("--demo-slots"):
		show_slots()
	else:
		show_main()


# --- Panels -----------------------------------------------------------------------------------

func _set_panel(p: Control, name: String) -> void:
	if _panel != null:
		_panel.queue_free()
	_panel = p
	panel_name = name
	_panel_host.add_child(p)
	UiWrap.fit(p)
	UiFocus.link_layout(p)
	UiFocus.focus_first(p)


func show_main() -> void:
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 6)
	var latest := RunManager.latest_slot()
	if latest != "":
		var summary := RunManager.slot_summary(latest)
		box.add_child(_button("Continue (slot %s: %s)" % [latest, _describe(summary)], func() -> void: load_slot(latest)))
	box.add_child(_button("Campaigns", show_slots))
	box.add_child(_button("Tutorial", start_tutorial))
	box.add_child(_button("Codex", show_codex))
	box.add_child(_button("Stats & achievements", show_stats))
	box.add_child(_button("Options", show_options))
	box.add_child(_button("Quit", confirm_quit))
	var p := RunManager.profile
	box.add_child(_label("%d campaigns, %d won, %d lost | best ICE %s | %d achievements" % [p.campaigns_started, p.campaigns_won, p.campaigns_lost, ProfileState.ice_text(p.best_ice), p.achievements.size()]))
	_set_panel(box, "main")


func show_slots() -> void:
	var box := VBoxContainer.new()
	box.add_child(_label("Campaign slots"))
	for slot in SLOTS:
		var row := HFlowContainer.new()
		var summary := RunManager.slot_summary(slot)
		row.add_child(_label("Slot %s: %s" % [slot, _describe(summary)]))
		var s := slot
		if summary.is_empty():
			row.add_child(_button("New campaign", func() -> void: new_in_slot(s)))
		else:
			row.add_child(_button("Load", func() -> void: load_slot(s)))
			row.add_child(_button("Delete", func() -> void: confirm_delete(s)))
		box.add_child(row)
	box.add_child(_button("Back", show_main))
	_set_panel(box, "slots")


func show_codex() -> void:
	var box := VBoxContainer.new()
	var note := ZineNote.new("CODEX", Vector2(900, 420)).make_reference()
	var entries := Codex.entries(RunManager.lookup(), RunManager.profile)
	for section in entries:
		note.append("[b]%s[/b]" % section)
		for item in entries[section]:
			note.append("  %s - %s" % [item["title"], String(item["text"]).split("\n")[0]])
	box.add_child(note)
	box.add_child(_button("Back", show_main))
	_set_panel(box, "codex")


func show_stats() -> void:
	var p := RunManager.profile
	var box := VBoxContainer.new()
	var note := ZineNote.new("STATS", Vector2(900, 200)).make_reference()
	note.append("Campaigns: %d started, %d won, %d lost. Runs completed: %d. Operatives lost: %d. Raids: %d won / %d lost." % [
		p.campaigns_started, p.campaigns_won, p.campaigns_lost, p.runs_completed, p.operatives_lost, p.raids_won, p.raids_lost])
	note.append("Best ICE: %s. Perfects: %d. Racks captured: %d. Cycles earned: %d. Assisted wins: %d." % [ProfileState.ice_text(p.best_ice), int(p.stats.get("perfects", 0)), int(p.stats.get("racks", 0)), int(p.stats.get("cycles", 0)), int(p.stats.get("assisted_wins", 0))])
	var per_corp := PackedStringArray()
	for cid in RunManager.lookup().ids_of_class(&"CorporationData"):
		var corp := RunManager.lookup().get_content(cid) as CorporationData
		if corp != null and (not corp.generated_from_profile or CampaignRules.corporation_available(p, RunManager.lookup(), corp)):
			per_corp.append("%s %s" % [corp.display_name, ProfileState.ice_text(p.best_ice_for(corp.id))])
	note.append("Best ICE by corporation: %s." % ", ".join(per_corp))
	note.append("[b]Achievements[/b]")
	for d in Achievements.DEFS:
		var have := p.achievements.has(d["id"])
		note.append("%s %s - %s" % ["[x]" if have else "[ ]", d["title"], d["text"]])
	box.add_child(note)
	var history := ZineNote.new("RUN HISTORY", Vector2(900, 160)).make_reference()
	if p.run_history.is_empty():
		history.append("no runs yet")
	for r in p.run_history:
		var corp := RunManager.lookup().get_content(StringName(String(r.get("corporation", "")))) as CorporationData
		history.append("%s T%d %s: %s, %d Cycles, %d banked" % [corp.display_name if corp != null else r.get("corporation", "?"), int(r.get("tier", 1)), r.get("site", "?"), r.get("outcome", "?"), int(r.get("cycles", 0)), int(r.get("banked", 0))])
	box.add_child(history)
	box.add_child(_button("Back", show_main))
	_set_panel(box, "stats")


func show_options() -> void:
	var box := VBoxContainer.new()
	var panel := SettingsPanel.new()
	panel.closed.connect(show_main)
	box.add_child(panel)
	_set_panel(box, "options")


# --- Actions ---------------------------------------------------------------------------------

func new_in_slot(slot: String) -> void:
	RunManager.save_slot = slot
	RunManager.reset()
	RunManager.change_scene(RunManager.HQ_SCENE)


func load_slot(slot: String) -> void:
	RunManager.save_slot = slot
	RunManager.reset()
	if RunManager.resume():
		if RunManager.has_active_run():
			RunManager.go_to_netrun()
		else:
			RunManager.change_scene(RunManager.HQ_SCENE)
	else:
		show_slots()


func confirm_delete(slot: String) -> void:
	_ask("Delete the campaign in slot %s? This cannot be undone." % slot, func() -> void:
		RunManager.delete_slot(slot)
		show_slots())


func confirm_quit() -> void:
	_ask("Quit REBEL_CELL?", RunManager.quit_game)


func start_tutorial() -> void:
	RunManager.pending_tutorial = true
	RunManager.change_scene(RunManager.COMBAT_SCENE)


func _ask(question: String, on_yes: Callable) -> void:
	if _confirm != null and is_instance_valid(_confirm):
		_confirm.queue_free()
	_confirm = ConfirmDialog.new(question)
	_confirm.position = Vector2(size.x / 2.0 - 210, 200)
	_confirm.confirmed.connect(on_yes)
	add_child(_confirm)


func confirm_visible() -> bool:
	return _confirm != null and is_instance_valid(_confirm) and _confirm.is_inside_tree()


# --- Helpers ----------------------------------------------------------------------------------

func _describe(summary: Dictionary) -> String:
	if summary.is_empty():
		return "empty"
	return "%s, Heat %d, ICE %d, %d runs, %s%s" % [summary.get("corporation", "?"), int(summary.get("heat", 0)), int(summary.get("ice", 0)),
		int(summary.get("runs", 0)), String(summary.get("state", "active")), (" (run in progress)" if summary.get("in_run", false) else "")]


func _label(text: String) -> Label:
	var l := Label.new()
	l.text = text
	return l


func _button(text: String, on_pressed: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(320, 0)
	b.pressed.connect(on_pressed)
	return b
