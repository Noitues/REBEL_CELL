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

## The design canvas's bottom less a margin (px): the window never runs off it.
const CANVAS_BOTTOM := 718.0

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
var close_button: Button
var hint_label: Label
## The selected slot's price in pick mode ("150 CYCLES"; pink when unaffordable).
var price_label: Label
## slot -> price (Callable) and the Cycles to spend; unset = no prices shown.
var price_of: Callable = Callable()
var budget: int = -1
## The hub core and inner ring shown in the middle (loadout view, H20); null / empty =
## the slice count only.
var hub: HubCoreData = null
var ring: Array[RingSegmentData] = []
var _core_pads: Array[Button] = []

## Inner ring band and hub disc radii (px), inside the slices' inner edge.
const RING_OUTER := 90.0
const RING_INNER := 56.0
const HUB_RADIUS := 50.0
## The hub name's font size and the smallest it shrinks to.
const HUB_FONT_SIZE := 13
const HUB_MIN_FONT_SIZE := 8


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
	window.custom_minimum_size = Vector2(700, 600)
	# Under the subtitles (H21), as far as the 720 canvas allows.
	window.position = Vector2(290, minf(SubtitleStrip.top_below(50.0), CANVAS_BOTTOM - window.custom_minimum_size.y))
	add_child(window)
	tab_row = HBoxContainer.new()
	window.body.add_child(tab_row)
	var hint := Label.new()
	hint.name = "Hint"
	hint_label = hint
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
			if (ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_RIGHT) or ev.is_action_pressed(&"inspect"):
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
	close_button = close_btn
	close_btn.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	close_btn.pressed.connect(close)
	bottom.add_child(close_btn)
	if action != "":
		_action_button = DripButton.new(action, "", DripButton.DRIP_PINK, 34, [[0, 26, 0.3]])
		_action_button.name = "ActionButton"
		_action_button.visible = false
		_action_button.pressed.connect(confirm)
		bottom.add_child(_action_button)
		price_label = Label.new()
		price_label.name = "Price"
		price_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		bottom.add_child(price_label)


func _ready() -> void:
	# Modal for keys and the pad (H20); inside the loadout view, the loadout view holds.
	if not (get_parent() is LoadoutView):
		UiFocus.hold(self)
	Settings.hints_changed.connect(_relabel)
	_relabel()
	_place_pads.call_deferred()
	if not _pads.is_empty():
		_pads[0].grab_focus.call_deferred()
	else:
		UiFocus.focus_first.call_deferred(self)


## Key hints follow the device in use and the binds (H20).
func _relabel() -> void:
	close_button.text = ("Close %s" % Settings.hint(&"ui_cancel")).strip_edges()
	var pick := Settings.key_text(&"ui_accept") if Settings.pad_active else "Left click"
	var more := Settings.key_text(&"inspect") if Settings.pad_active else "Right click"
	hint_label.text = ("%s: select the slot to %s. %s: details." % [pick, action.to_lower(), more]) if action != "" else "%s a slice for details." % ("Press" if Settings.pad_active else "Click")


## Pick mode prices (H20: the Miss slot costs more): `p_price_of(slot) -> int` and the
## Cycles on hand. Each pad's tooltip names its price; the selected slot's price shows
## beside the action, which is off when the slot costs more than `p_budget`.
func set_prices(p_price_of: Callable, p_budget: int) -> void:
	price_of = p_price_of
	budget = p_budget
	for i in _pads.size():
		_pads[i].tooltip_text = UiTip.fold("%s\n%d CYCLES" % [_slice_text(i), int(price_of.call(i))])
	_update_price()


## The selected slot's price, or -1 (no slot, or no prices).
func selected_price() -> int:
	return int(price_of.call(selected)) if selected >= 0 and price_of.is_valid() else -1


func _update_price() -> void:
	if price_label == null:
		return
	var price := selected_price()
	price_label.text = ("%d CYCLES" % price) if price >= 0 else ""
	var short := price >= 0 and budget >= 0 and price > budget
	price_label.add_theme_color_override("font_color", Palette.CELL_PINK if short else Palette.CELL_ACID)
	if _action_button != null:
		_action_button.disabled = short


## Shows the hub core and the inner ring in the middle of the wheel (the loadout view),
## each a pad with its tooltip; pressing one opens its detail.
func set_core(p_hub: HubCoreData, p_ring: Array[RingSegmentData]) -> void:
	hub = p_hub
	ring = p_ring
	for p in _core_pads:
		p.queue_free()
	_core_pads.clear()
	var parts: Array[Resource] = []
	if hub != null:
		parts.append(hub)
	for seg in ring:
		parts.append(seg)
	for k in parts.size():
		var part := parts[k]
		var pad := Button.new()
		pad.flat = true
		pad.name = "HubPad" if part is HubCoreData else "RingPad%d" % (k - (1 if hub != null else 0))
		pad.custom_minimum_size = Vector2(44, 44)
		pad.size = Vector2(44, 44)
		pad.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
		pad.tooltip_text = UiTip.fold(Codex.describe(part))
		pad.pressed.connect(func() -> void: open_part(part))
		pad.focus_entered.connect(_wheel.queue_redraw)
		pad.focus_exited.connect(_wheel.queue_redraw)
		_wheel.add_child(pad)
		_core_pads.append(pad)
	_place_pads.call_deferred()
	_wheel.queue_redraw()


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
	_update_price()
	_wheel.queue_redraw()


func confirm() -> void:
	if selected < 0 or (_action_button != null and _action_button.disabled):
		return
	# Out of the tree first: the screen behind takes focus again before the pick rebuilds it.
	var picked := selected
	close()
	slot_picked.emit(picked)


func _centre() -> Vector2:
	return Vector2(335, 220)


func _angle(i: int) -> float:
	return -PI * 0.5 - TAU * i / maxf(1.0, slices.size())  # slot order as in combat (H21: +1 anticlockwise on screen)


func _place_pads() -> void:
	for i in _pads.size():
		_pads[i].position = _centre() + Vector2(cos(_angle(i)), sin(_angle(i))) * 140.0 - Vector2(35, 35)
	var k0 := 0
	if hub != null and not _core_pads.is_empty():
		_core_pads[0].position = _centre() - _core_pads[0].size * 0.5
		k0 = 1
	for k in range(k0, _core_pads.size()):
		var a := _ring_angle(k - k0)
		_core_pads[k].position = _centre() + Vector2(cos(a), sin(a)) * (RING_INNER + RING_OUTER) * 0.5 - _core_pads[k].size * 0.5


## Middle angle of inner ring segment `k` (the segments share the circle evenly).
func _ring_angle(k: int) -> float:
	return -PI * 0.5 - TAU * (k + 0.5) / maxf(1.0, ring.size()) + PI / maxf(1.0, slices.size())


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
	elif UiFocus.is_device_input(event):
		get_viewport().set_input_as_handled()  # no hotkey reaches the screen behind


func close() -> void:
	closed.emit()
	UiFocus.release(self)


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
		_wheel.draw_colored_polygon(pts, Color(col, 0.7 if i == _hot else 0.5) if type != RC.SliceType.MISS else Color(col, 0.2))
		pts.append(pts[0])
		_wheel.draw_polyline(pts, Palette.CELL_ACID if i == _hot else col.lightened(0.3), 2.0 if i == _hot else 1.2)
		var am := _angle(i)
		SliceIcon.draw_on_slice(_wheel, c + Vector2(cos(am), sin(am)) * 140.0, 16, type, col)
		if s != null and s.base_output > 0:
			_wheel.draw_string(Palette.display(), c + Vector2(cos(am), sin(am)) * 208.0 + Vector2(-20, 10), str(s.base_output), HORIZONTAL_ALIGNMENT_CENTER, 40, 26, col.lightened(0.35))
		if i < firmware.size() and firmware[i] != &"":
			_wheel.draw_rect(Rect2(c + Vector2(cos(am), sin(am)) * 116.0 - Vector2(5, 5), Vector2(10, 10)), Palette.NET_CYAN)
	_wheel.draw_circle(c, r0 - 6, Color("#07080F"))
	_wheel.draw_arc(c, r1, 0, TAU, 64, wheel_color, 2.5)
	if hub == null and ring.is_empty():
		_wheel.draw_string(Palette.marker(), c + Vector2(-60, 8), "%d SLICES" % n, HORIZONTAL_ALIGNMENT_CENTER, 120, 18, wheel_color)
	_draw_core(c)
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


## The inner ring (segments as bands, their names) and the hub core (its name) in the
## middle of the wheel.
func _draw_core(c: Vector2) -> void:
	var n := ring.size()
	for k in n:
		var mid := _ring_angle(k)
		var half := PI / n - 0.04
		var pts := PackedVector2Array()
		for q in 13:
			var a := lerpf(mid - half, mid + half, q / 12.0)
			pts.append(c + Vector2(cos(a), sin(a)) * RING_OUTER)
		for q in 13:
			var a := lerpf(mid + half, mid - half, q / 12.0)
			pts.append(c + Vector2(cos(a), sin(a)) * RING_INNER)
		var hot := k + (1 if hub != null else 0) < _core_pads.size() and _core_pads[k + (1 if hub != null else 0)].has_focus()
		_wheel.draw_colored_polygon(pts, Color(Palette.NEON_VIOLET, 0.45 if hot else 0.28))
		pts.append(pts[0])
		_wheel.draw_polyline(pts, Palette.CELL_ACID if hot else Palette.NEON_VIOLET, 1.5)
		var label := ring[k].display_name.left(3).to_upper() if ring[k] != null else "?"
		var at := c + Vector2(cos(mid), sin(mid)) * (RING_INNER + RING_OUTER) * 0.5
		_wheel.draw_string(Palette.mono(), at + Vector2(-20, 5), label, HORIZONTAL_ALIGNMENT_CENTER, 40, 13, Palette.PAPER)
	if hub != null:
		var hot_hub := not _core_pads.is_empty() and _core_pads[0].has_focus()
		_wheel.draw_circle(c, HUB_RADIUS, Color(Palette.NIGHT_SKY, 0.95))
		_wheel.draw_arc(c, HUB_RADIUS, 0, TAU, 48, Palette.CELL_ACID if hot_hub else wheel_color, 2.0)
		_wheel.draw_string(Palette.mono(), c + Vector2(-HUB_RADIUS, -4), "HUB", HORIZONTAL_ALIGNMENT_CENTER, HUB_RADIUS * 2.0, 11, Color(Palette.PAPER, 0.7))
		# The hub's name shrinks to fit the disc.
		var hub_name := hub.display_name.to_upper()
		var fs := HUB_FONT_SIZE
		var w := Palette.marker().get_string_size(hub_name, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		if w > HUB_RADIUS * 2.0 - 8.0:
			fs = maxi(HUB_MIN_FONT_SIZE, floori(fs * (HUB_RADIUS * 2.0 - 8.0) / w))
		_wheel.draw_string(Palette.marker(), c + Vector2(-HUB_RADIUS + 4, 14), hub_name, HORIZONTAL_ALIGNMENT_CENTER, HUB_RADIUS * 2.0 - 8, fs, wheel_color)


## The detail popup of the hub core or an inner ring segment.
func open_part(part: Resource) -> void:
	if _popup != null and is_instance_valid(_popup):
		_popup.queue_free()
	var pop := TerminalWindow.new("HUB CORE" if part is HubCoreData else "INNER RING SEGMENT", Palette.NEON_VIOLET)
	pop.name = "CoreDetail"
	pop.position = Vector2(400, 180)
	pop.custom_minimum_size = Vector2(480, 0)
	var desc := Label.new()
	desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	desc.custom_minimum_size.x = 440
	desc.text = Codex.describe(part)
	pop.body.add_child(desc)
	var close_btn := Button.new()
	close_btn.text = "Close"
	close_btn.pressed.connect(func() -> void: pop.queue_free(); _popup = null)
	pop.body.add_child(close_btn)
	add_child(pop)
	_popup = pop
	UiFocus.focus_first.call_deferred(pop)
