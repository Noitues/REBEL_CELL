class_name SpinnerView
extends Control
## Spinner viewer (modal): the operative's wheel drawn large with the slice icons; each
## slice is a pickable pad. Picking one opens its detail popup: type, output, firmware,
## and the stronger same-type slices from the Modem catalogue (`upgrades`). In pick mode
## (`pick_label` set, e.g. "OVERWRITE WITH ATK 8") the popup carries that action and
## `slot_picked(index)` fires. Emits `closed` on Back / Esc. View only.

signal slot_picked(index: int)
signal closed

var slices: Array[StringName] = []
var firmware: Array[StringName] = []
var lookup: ContentLookup
var upgrades: Array[SliceData] = []
var pick_label: String = ""
var wheel_color: Color = Palette.CELL_PINK
var _wheel: Control
var _pads: Array[Button] = []
var _popup: Control = null
var _hot: int = -1


func _init(p_slices: Array[StringName], p_firmware: Array[StringName], p_lookup: ContentLookup, p_title: String = "SPINNER",
		p_pick_label: String = "", p_upgrades: Array[SliceData] = []) -> void:
	slices = p_slices
	firmware = p_firmware
	lookup = p_lookup
	pick_label = p_pick_label
	upgrades = p_upgrades
	name = "SpinnerView"
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.72)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var win := TerminalWindow.new(p_title, Palette.CELL_PINK)
	win.position = Vector2(290, 70)
	win.custom_minimum_size = Vector2(700, 560)
	add_child(win)
	if pick_label != "":
		var hint := Label.new()
		hint.text = "Pick the slot to overwrite."
		hint.add_theme_color_override("font_color", Palette.CELL_ACID)
		win.body.add_child(hint)
	_wheel = Control.new()
	_wheel.custom_minimum_size = Vector2(670, 440)
	_wheel.draw.connect(_draw_wheel)
	win.body.add_child(_wheel)
	for i in slices.size():
		var pad := Button.new()
		pad.flat = true
		pad.custom_minimum_size = Vector2(70, 70)
		pad.size = Vector2(70, 70)
		pad.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
		pad.tooltip_text = _slice_text(i)
		var index := i
		pad.pressed.connect(func() -> void: open_slot(index))
		pad.mouse_entered.connect(func() -> void: _hot = index; _wheel.queue_redraw())
		pad.focus_entered.connect(func() -> void: _hot = index; _wheel.queue_redraw())
		_wheel.add_child(pad)
		_pads.append(pad)
	var back := Button.new()
	back.text = "Back [Esc]"
	back.pressed.connect(close)
	win.body.add_child(back)


func _ready() -> void:
	_place_pads.call_deferred()
	UiFocus.focus_first.call_deferred(self)


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
	var r0 := 90.0
	var r1 := 190.0
	_wheel.draw_circle(c, r1 + 16, Color(0, 0, 0, 0.6))
	for i in n:
		var s := _slice(i)
		var type := s.slice_type if s != null else RC.SliceType.MISS
		var a0 := _angle(i) - PI / n + 0.02
		var a1 := _angle(i) + PI / n - 0.02
		var pts := PackedVector2Array()
		for k in 13:
			var a := lerpf(a0, a1, k / 12.0)
			pts.append(c + Vector2(cos(a), sin(a)) * r1)
		for k in 13:
			var a := lerpf(a1, a0, k / 12.0)
			pts.append(c + Vector2(cos(a), sin(a)) * r0)
		var col := Palette.slice_color(type)
		_wheel.draw_colored_polygon(pts, Color(col, 0.55 if i == _hot else 0.3))
		pts.append(pts[0])
		_wheel.draw_polyline(pts, Palette.CELL_ACID if i == _hot else col, 2.0 if i == _hot else 1.2)
		var mid := c + Vector2(cos(_angle(i)), sin(_angle(i))) * 140.0
		SliceIcon.draw_icon(_wheel, mid + Vector2(0, -8), 14, type, Palette.PAPER)
		if s != null and s.base_output > 0:
			_wheel.draw_string(Palette.display(), mid + Vector2(-20, 26), str(s.base_output), HORIZONTAL_ALIGNMENT_CENTER, 40, 20, Palette.PAPER)
		if i < firmware.size() and firmware[i] != &"":
			_wheel.draw_rect(Rect2(mid + Vector2(18, -26), Vector2(10, 10)), Palette.NET_CYAN)
	_wheel.draw_circle(c, r0 - 6, Color("#07080F"))
	_wheel.draw_arc(c, r1, 0, TAU, 64, wheel_color, 2.5)
	_wheel.draw_string(Palette.marker(), c + Vector2(-60, 8), "%d SLICES" % n, HORIZONTAL_ALIGNMENT_CENTER, 120, 18, wheel_color)


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
	var up_label := Label.new()
	up_label.text = "UPGRADES: " + (", ".join(ups) + " (at the Modem)" if not ups.is_empty() else "none stronger in the catalogue")
	up_label.add_theme_color_override("font_color", Palette.CELL_ACID)
	pop.body.add_child(up_label)
	var actions := HBoxContainer.new()
	pop.body.add_child(actions)
	if pick_label != "":
		var pick := Button.new()
		pick.text = pick_label
		pick.theme_type_variation = &"HotButton"
		pick.pressed.connect(func() -> void: slot_picked.emit(index); close())
		actions.add_child(pick)
	var back := Button.new()
	back.text = "Back"
	back.pressed.connect(func() -> void: pop.queue_free(); _popup = null)
	actions.add_child(back)
	add_child(pop)
	_popup = pop
	UiFocus.focus_first.call_deferred(pop)
