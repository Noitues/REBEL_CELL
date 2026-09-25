class_name SpinnerView
extends Control
## Spinner viewer (modal): the wheel drawn large, each slice a pad with its icon and
## value. Right-click opens a slice's detail popup (type, output, firmware, stronger
## same-type slices from the Modem catalogue). With an `action` ("UPGRADE") left click
## selects / deselects a slot, marked with a drippy circle, and the action appears in
## dripping marker next to Close; pressing it emits `slot_picked(index)`. Without an
## action, left click opens the detail. Emits `closed`. View only.

signal slot_picked(index: int)
signal closed

var slices: Array[StringName] = []
var firmware: Array[StringName] = []
var lookup: ContentLookup
var upgrades: Array[SliceData] = []
var action: String = ""
var selected: int = -1
var wheel_color: Color = Palette.CELL_PINK
var window: TerminalWindow
var tab_row: HBoxContainer
var _wheel: Control
var _pads: Array[Button] = []
var _action_button: DripButton = null
var _popup: Control = null
var _hot: int = -1


func _init(p_slices: Array[StringName], p_firmware: Array[StringName], p_lookup: ContentLookup, p_title: String = "SPINNER",
		p_action: String = "", p_upgrades: Array[SliceData] = []) -> void:
	slices = p_slices
	firmware = p_firmware
	lookup = p_lookup
	action = p_action
	upgrades = p_upgrades
	name = "SpinnerView"
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.72)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	window = TerminalWindow.new(p_title, Palette.CELL_PINK)
	window.position = Vector2(290, 50)
	window.custom_minimum_size = Vector2(700, 600)
	add_child(window)
	tab_row = HBoxContainer.new()
	window.body.add_child(tab_row)
	var hint := Label.new()
	hint.text = "Left click: select the slot to %s. Right click: details." % action.to_lower() if action != "" else "Click a slice for details."
	hint.add_theme_color_override("font_color", Palette.CELL_ACID)
	window.body.add_child(hint)
	_wheel = Control.new()
	_wheel.custom_minimum_size = Vector2(670, 440)
	_wheel.draw.connect(_draw_wheel)
	window.body.add_child(_wheel)
	for i in slices.size():
		var pad := Button.new()
		pad.flat = true
		pad.custom_minimum_size = Vector2(70, 70)
		pad.size = Vector2(70, 70)
		pad.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
		pad.tooltip_text = _slice_text(i)
		var index := i
		pad.pressed.connect(func() -> void: _on_left(index))
		pad.gui_input.connect(func(ev: InputEvent) -> void:
			if ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_RIGHT:
				open_slot(index)
				pad.accept_event())
		pad.mouse_entered.connect(func() -> void: _hot = index; _wheel.queue_redraw())
		pad.focus_entered.connect(func() -> void: _hot = index; _wheel.queue_redraw())
		_wheel.add_child(pad)
		_pads.append(pad)
	var bottom := HBoxContainer.new()
	bottom.add_theme_constant_override("separation", 20)
	window.body.add_child(bottom)
	var close_btn := Button.new()
	close_btn.name = "Close"
	close_btn.text = "Close [Esc]"
	close_btn.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	close_btn.pressed.connect(close)
	bottom.add_child(close_btn)
	if action != "":
		_action_button = DripButton.new(action, "", DripButton.DRIP_PINK, 34, [[0, 26, 0.3]])
		_action_button.name = "ActionButton"
		_action_button.visible = false
		_action_button.pressed.connect(confirm)
		bottom.add_child(_action_button)


func _ready() -> void:
	_place_pads.call_deferred()
	if not _pads.is_empty():
		_pads[0].grab_focus.call_deferred()
	else:
		UiFocus.focus_first.call_deferred(self)


func add_tab(text: String, on_pressed: Callable, active: bool = false) -> void:
	var b := Button.new()
	b.text = text
	b.name = "Tab" + text
	# Same colours for both tabs: the active one is dark with a border, the other in
	# reverse video (light block, dark text) without one.
	var fg := Palette.TERMINAL_TEXT
	var bg := Palette.TERMINAL_BG
	var style := UiTheme.box(bg if active else fg, fg if active else Color(0, 0, 0, 0), 2 if active else 0, 12, 4)
	for st in ["normal", "hover", "pressed", "hover_pressed", "disabled"]:
		b.add_theme_stylebox_override(st, style)
	var ink := fg if active else bg
	for key in ["font_color", "font_hover_color", "font_pressed_color", "font_hover_pressed_color", "font_focus_color", "font_disabled_color"]:
		b.add_theme_color_override(key, ink)
	if active:
		b.focus_mode = Control.FOCUS_NONE
		b.mouse_filter = Control.MOUSE_FILTER_IGNORE
	else:
		b.pressed.connect(on_pressed)
	tab_row.add_child(b)


func _on_left(index: int) -> void:
	if action == "":
		open_slot(index)
		return
	select(-1 if selected == index else index)


func select(index: int) -> void:
	selected = index
	if _action_button != null:
		_action_button.visible = selected >= 0
	_wheel.queue_redraw()


func confirm() -> void:
	if selected < 0:
		return
	slot_picked.emit(selected)
	close()


func _centre() -> Vector2:
	return Vector2(335, 220)


func _angle(i: int) -> float:
	return -PI * 0.5 + TAU * i / maxf(1.0, slices.size())


func _place_pads() -> void:
	for i in _pads.size():
		_pads[i].position = _centre() + Vector2(cos(_angle(i)), sin(_angle(i))) * 140.0 - Vector2(35, 35)


func _slice(i: int) -> SliceData:
	return lookup.get_content(slices[i]) as SliceData


func _slice_text(i: int) -> String:
	var s := _slice(i)
	if s == null:
		return String(slices[i])
	var t := "%s %s" % [Palette.SLICE_NAMES.get(s.slice_type, "?"), s.base_output if s.base_output > 0 else ""]
	if i < firmware.size() and firmware[i] != &"":
		t += " {%s}" % firmware[i]
	return t.strip_edges()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		if _popup != null and is_instance_valid(_popup):
			_popup.queue_free()
			_popup = null
		else:
			close()


func close() -> void:
	closed.emit()
	queue_free()


func _draw_wheel() -> void:
	var c := _centre()
	var n := slices.size()
	var r0 := 100.0
	var r1 := 180.0
	_wheel.draw_circle(c, r1 + 44, Color(0, 0, 0, 0.6))
	for i in n:
		var s := _slice(i)
		var type := s.slice_type if s != null else RC.SliceType.MISS
		var a0 := _angle(i) - PI / n + 0.03
		var a1 := _angle(i) + PI / n - 0.03
		var pts := PackedVector2Array()
		for k in 13:
			var a := lerpf(a0, a1, k / 12.0)
			pts.append(c + Vector2(cos(a), sin(a)) * r1)
		for k in 13:
			var a := lerpf(a1, a0, k / 12.0)
			pts.append(c + Vector2(cos(a), sin(a)) * r0)
		var col := Palette.slice_color(type)
		_wheel.draw_colored_polygon(pts, Color(col, 0.95 if i == _hot else 0.8) if type != RC.SliceType.MISS else Color(col, 0.2))
		pts.append(pts[0])
		_wheel.draw_polyline(pts, Palette.CELL_ACID if i == _hot else col.lightened(0.3), 2.0 if i == _hot else 1.2)
		var am := _angle(i)
		SliceIcon.draw_icon(_wheel, c + Vector2(cos(am), sin(am)) * 140.0, 16, type, Palette.PAPER)
		if s != null and s.base_output > 0:
			_wheel.draw_string(Palette.display(), c + Vector2(cos(am), sin(am)) * 208.0 + Vector2(-20, 10), str(s.base_output), HORIZONTAL_ALIGNMENT_CENTER, 40, 26, col.lightened(0.35))
		if i < firmware.size() and firmware[i] != &"":
			_wheel.draw_rect(Rect2(c + Vector2(cos(am), sin(am)) * 116.0 - Vector2(5, 5), Vector2(10, 10)), Palette.NET_CYAN)
	_wheel.draw_circle(c, r0 - 6, Color("#07080F"))
	_wheel.draw_arc(c, r1, 0, TAU, 64, wheel_color, 2.5)
	_wheel.draw_string(Palette.marker(), c + Vector2(-60, 8), "%d SLICES" % n, HORIZONTAL_ALIGNMENT_CENTER, 120, 18, wheel_color)
	if selected >= 0:
		var am := _angle(selected)
		HandMarks.draw_drip_circle(_wheel, c + Vector2(cos(am), sin(am)) * 140.0, Vector2(62, 56), DripButton.DRIP_PINK)


## The slice detail popup for slot `index`.
func open_slot(index: int) -> void:
	if _popup != null and is_instance_valid(_popup):
		_popup.queue_free()
	var s := _slice(index)
	var pop := TerminalWindow.new("SLICE %d DETAIL" % index, Palette.CELL_ACID)
	pop.name = "SliceDetail"
	pop.position = Vector2(400, 180)
	pop.custom_minimum_size = Vector2(480, 0)
	var icon := Control.new()
	icon.custom_minimum_size = Vector2(0, 64)
	var type := s.slice_type if s != null else RC.SliceType.MISS
	icon.draw.connect(func() -> void:
		SliceIcon.draw_icon(icon, Vector2(34, 32), 24, type, Palette.slice_color(type))
		icon.draw_string(Palette.display(), Vector2(76, 44), _slice_text(index), HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Palette.PAPER))
	pop.body.add_child(icon)
	var desc := Label.new()
	desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	desc.custom_minimum_size.x = 440
	desc.text = Codex.describe(s) if s != null else String(slices[index])
	pop.body.add_child(desc)
	var ups := PackedStringArray()
	for u in upgrades:
		if s != null and u.slice_type == s.slice_type and u.base_output > s.base_output:
			ups.append("%s %d" % [Palette.SLICE_NAMES.get(u.slice_type, "?"), u.base_output])
	if not ups.is_empty():
		var up_label := Label.new()
		up_label.text = "UPGRADES: " + ", ".join(ups)
		up_label.add_theme_color_override("font_color", Palette.CELL_ACID)
		pop.body.add_child(up_label)
	var close_btn := Button.new()
	close_btn.text = "Close"
	close_btn.pressed.connect(func() -> void: pop.queue_free(); _popup = null)
	pop.body.add_child(close_btn)
	add_child(pop)
	_popup = pop
	UiFocus.focus_first.call_deferred(pop)
