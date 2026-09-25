class_name PauseMenu
extends Control
## Pause menu (gap analysis 2.5): Resume, Options (the SettingsPanel inline), Codex,
## Save & quit to title, Quit to desktop (confirmed). Scenes open it on Esc; it never
## changes game state itself beyond asking RunManager to save and switch scenes.

signal resumed
signal quit_to_title

var settings_panel: SettingsPanel = null
var codex_note: ZineNote = null
var _menu: VBoxContainer
var _host: VBoxContainer
## Who had focus before the menu opened (the combat hand); it gets it back on close.
var _return_focus: Control = null


func _init() -> void:
	custom_minimum_size = Vector2(560, 400)
	var panel := ZinePanel.new("PAUSED", 0.0)
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(panel)
	_host = VBoxContainer.new()
	panel.content.add_child(_host)
	_menu = VBoxContainer.new()
	_host.add_child(_menu)
	_add("Resume [Esc]", func() -> void: resumed.emit())
	_add("Options", show_options)
	_add("Codex", show_codex)
	_add("Save & quit to title", func() -> void:
		if RunManager.campaign != null:
			RunManager.autosave()
		quit_to_title.emit())
	_add("Quit to desktop", func() -> void:
		var confirm := ConfirmDialog.new("Quit REBEL_CELL? Progress is autosaved.")
		confirm.position = Vector2(60, 120)
		add_child(confirm)
		confirm.confirmed.connect(func() -> void: RunManager.quit_game()))


func _notification(what: int) -> void:
	if what == NOTIFICATION_VISIBILITY_CHANGED or what == NOTIFICATION_READY:
		if is_visible_in_tree():
			var owner := UiFocus.owner_of(self)
			if owner != null and not is_ancestor_of(owner):
				_return_focus = owner
			UiFocus.focus_first(_menu)
		elif _return_focus != null and is_instance_valid(_return_focus) and _return_focus.is_visible_in_tree():
			_return_focus.grab_focus.call_deferred()
	elif what == NOTIFICATION_PREDELETE or what == NOTIFICATION_EXIT_TREE:
		if _return_focus != null and is_instance_valid(_return_focus) and _return_focus.is_inside_tree():
			_return_focus.grab_focus.call_deferred()


func _add(text: String, on_pressed: Callable) -> void:
	var b := Button.new()
	b.text = text
	b.pressed.connect(on_pressed)
	_menu.add_child(b)


func show_options() -> void:
	_close_sub()
	settings_panel = SettingsPanel.new()
	settings_panel.closed.connect(_close_sub)
	_host.add_child(settings_panel)
	UiFocus.focus_first(settings_panel)


func show_codex() -> void:
	_close_sub()
	codex_note = ZineNote.new("CODEX", Vector2(520, 220))
	var entries := Codex.entries(RunManager.lookup(), RunManager.profile)
	for section in entries:
		codex_note.append("[b]%s[/b]" % section)
		for item in entries[section]:
			codex_note.append("  %s - %s" % [item["title"], String(item["text"]).split("\n")[0]])
	_host.add_child(codex_note)
	var back := Button.new()
	back.text = "Back"
	back.name = "CodexBack"
	back.pressed.connect(_close_sub)
	_host.add_child(back)
	back.grab_focus.call_deferred()


func _close_sub() -> void:
	if settings_panel != null and is_instance_valid(settings_panel):
		settings_panel.queue_free()
	settings_panel = null
	if codex_note != null and is_instance_valid(codex_note):
		codex_note.queue_free()
		var back := _host.get_node_or_null("CodexBack")
		if back != null:
			back.queue_free()
	codex_note = null
	UiFocus.focus_first(_menu)


func _unhandled_input(event: InputEvent) -> void:
	if not visible or settings_panel != null:
		return
	if event.is_action_pressed("ui_cancel") or event.is_action_pressed("open_settings"):
		resumed.emit()
		get_viewport().set_input_as_handled()
