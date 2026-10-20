class_name NodePage
extends VBoxContainer
## RG-02/03: the page of a REST or WORKSHOP node. A plain terminal window of buttons (placeholder look,
## the art pass restyles it). Mouse and keyboard: click a button, or press 1-9 to pick a wheel slot / offer,
## Enter confirms the open pick, Esc clears an open pick. The page only reads the
## session and emits signals; the scene calls the session (Signal Up, Call Down).

signal patch_pressed
signal rewire_confirmed(a: int, b: int)
signal undo_pressed
signal leave_pressed
## WORKSHOP: offer index and wheel slot to buy.
signal buy_confirmed(offer: int, slot: int)

var _s: NetrunSession
## REST: the picked source and target slots (-1 none). WORKSHOP: the picked offer and slot.
var _first: int = -1
var _second: int = -1
var _keys: Array[Button] = []


## Builds the page for the session's open node page (`run.phase`).
func setup(s: NetrunSession) -> void:
	_s = s
	name = "NodePage"
	for c in get_children():
		c.queue_free()
	_keys.clear()
	match s.run.phase:
		RunState.Phase.REST:
			_build_rest()
		RunState.Phase.WORKSHOP:
			_build_workshop()


func _label(text: String, node_name: String = "") -> Label:
	var l := Label.new()
	l.text = text
	UiWrap.whole_words(l)
	if node_name != "":
		l.name = node_name
	return l


func _button(text: String, node_name: String, tip: String = "") -> Button:
	var b := Button.new()
	b.text = text
	b.name = node_name
	b.tooltip_text = tip
	b.focus_mode = Control.FOCUS_ALL
	return b


func _name_of(id: StringName) -> String:
	if id == &"":
		return "-"
	var res := _s.lookup.get_content(id)
	return TextDb.t(res, "display_name") if res != null else String(id)


# --- REST ------------------------------------------------------------------------------------

func _build_rest() -> void:
	var win := TerminalWindow.new(tr("REST"), Palette.CELL_ACID) # TR
	win.name = "RestWindow"
	add_child(win)
	var op := _s.run.operative
	win.body.add_child(_label(tr("HP %d/%d") % [op.hp, op.max_hp], "RestHp")) # TR
	var done := _s.rest_done()
	var pv := _s.rest_patch_preview()
	var patch := _button(tr("PATCH  +%d HP -> %d/%d") % [pv["heal"], pv["hp_after"], pv["max_hp"]], "RestPatch", # TR
			tr("Heal %d%% of max HP. One mode per visit.") % _s.config.rest_heal_pct) # TR
	patch.disabled = done
	patch.pressed.connect(func() -> void: patch_pressed.emit())
	win.body.add_child(patch)
	win.body.add_child(_label(tr("REWIRE: pick a wheel slot, then the slot to swap its Firmware with.") if not done else tr("This REST is spent."), "RestHint")) # TR
	var row := VBoxContainer.new()
	row.name = "RestSlots"
	win.body.add_child(row)
	var after := _s.rest_rewire_preview(_first, _second) if _first >= 0 and _second >= 0 else op.slot_firmware_ids
	for i in op.slot_slice_ids.size():
		var txt := "%d  %s  [%s]" % [i + 1, _name_of(op.slot_slice_ids[i]), _name_of(after[i])]
		var b := _button(txt, "RestSlot%d" % i)
		var why := ""
		if _first >= 0 and i != _first:
			why = _s.rest_rewire_error(_first, i)
		b.disabled = done or (_first >= 0 and i != _first and why != "")
		b.tooltip_text = why
		b.toggle_mode = true
		b.button_pressed = i == _first or i == _second
		var idx := i
		b.pressed.connect(func() -> void: _pick_slot(idx))
		row.add_child(b)
		_keys.append(b)
	var foot := HBoxContainer.new()
	win.body.add_child(foot)
	var confirm := _button(tr("CONFIRM REWIRE"), "RestConfirm") # TR
	confirm.disabled = done or _first < 0 or _second < 0 or _s.rest_rewire_error(_first, _second) != ""
	confirm.pressed.connect(func() -> void: rewire_confirmed.emit(_first, _second))
	foot.add_child(confirm)
	var undo := _button(tr("UNDO"), "RestUndo") # TR
	undo.disabled = not done
	undo.pressed.connect(func() -> void: undo_pressed.emit())
	foot.add_child(undo)
	var leave := _button(tr("LEAVE"), "RestLeave") # TR
	leave.pressed.connect(func() -> void: leave_pressed.emit())
	foot.add_child(leave)


func _pick_slot(i: int) -> void:
	if _s.run.phase == RunState.Phase.WORKSHOP:
		_second = i
		setup(_s)
		return
	if _first < 0 or i == _first:
		_first = -1 if i == _first else i
		_second = -1
	else:
		_second = i
	setup(_s)


# --- WORKSHOP (filled in by RG-03) -----------------------------------------------------------

func _build_workshop() -> void:
	pass


## Keys 1-9 pick the n-th slot, Enter confirms, Esc steps back or leaves.
func _unhandled_key_input(event: InputEvent) -> void:
	if _s == null or not is_visible_in_tree() or not (event is InputEventKey) or not event.pressed or event.echo:
		return
	var k := event as InputEventKey
	if k.keycode >= KEY_1 and k.keycode <= KEY_9 and _s.run.phase == RunState.Phase.REST and not _s.rest_done():
		var i := k.keycode - KEY_1
		if i < _s.run.operative.slot_slice_ids.size() and not (_first >= 0 and i != _first and _s.rest_rewire_error(_first, i) != ""):
			_pick_slot(i)
			get_viewport().set_input_as_handled()
	elif k.keycode == KEY_ENTER or k.keycode == KEY_KP_ENTER:
		if _s.run.phase == RunState.Phase.REST and _first >= 0 and _second >= 0 and _s.rest_rewire_error(_first, _second) == "":
			rewire_confirmed.emit(_first, _second)
			get_viewport().set_input_as_handled()
	elif k.keycode == KEY_ESCAPE:
		if _first >= 0:
			_first = -1
			_second = -1
			setup(_s)
			get_viewport().set_input_as_handled()
