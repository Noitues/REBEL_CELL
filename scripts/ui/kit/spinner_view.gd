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
## Art pass W9F: the viewer's pad prompt bar (glyphs), shown while a pad is in use.
var prompts: PadPrompts
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
const HUB_FONT_SIZE := UiTheme.BODY
const HUB_MIN_FONT_SIZE := UiTheme.CAPTION
## The wheel's lettering (art pass W3, §4.2 steps): slice values, the slice count, a slice's
## popup title, ring segment tags and the HUB word.
const VALUE_FONT := UiTheme.TITLE
const COUNT_FONT := UiTheme.LABEL
const POPUP_FONT := UiTheme.HEADING
const RING_FONT := UiTheme.CAPTION
const HUB_WORD_FONT := UiTheme.CAPTION


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
	dim.color = Color(Palette.INK, 0.72)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	# H24 S4: the viewer shows its words as given: the title comes translated, the action
	# is a key ("UPGRADE") translated where shown.
	TextDb.shown_as_given(self)
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
	# Art pass W9F (§12): at big text the hint wraps inside the window (it ran off it at 2.0).
	UiWrap.whole_words(hint)
	hint.custom_minimum_size.x = _wheel_width()
	window.body.add_child(hint)
	# Art pass W9F (§5.2.4): the modal's own prompt bar while a pad is in use.
	prompts = PadPrompts.new()
	prompts.alignment = BoxContainer.ALIGNMENT_BEGIN
	window.body.add_child(prompts)
	_wheel = Control.new()
	_wheel.custom_minimum_size = Vector2(_wheel_width(), 440)
	_wheel.draw.connect(_draw_wheel)
	window.body.add_child(_wheel)
	for i in slices.size():
		var pad := Button.new()
		pad.name = "SlotPad%d" % i
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
		_action_button = DripButton.new(tr(action), "", DripButton.DRIP_PINK, 34, [[0, 26, 0.3]])
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
	# Art pass W9F (§6.8, §12): the mouse reads its words (UiTip.for_input), a pad player
	# the viewer's own prompt bar (glyphs), never "click" and never "[B]".
	close_button.text = tr("Close") if Settings.pad_active else ("%s %s" % [tr("Close"), Settings.hint(&"ui_cancel")]).strip_edges()
	hint_label.text = UiTip.for_input((tr("%s: select the slot to %s. %s: details.") % [tr("Left click"), tr(action).to_lower(), tr("Right click")]) if action != "" else tr("%s a slice for details.") % tr("Click"), "")
	hint_label.visible = hint_label.text != ""
	prompts.set_prompts(([[&"ui_accept", "Select"], [&"inspect", "Details"]] if action != "" else [[&"ui_accept", "Details"]]) + [[&"ui_cancel", "Close"]]) # TR


## Pick mode prices (H20: the Miss slot costs more): `p_price_of(slot) -> int` and the
## Cycles on hand. Each pad's tooltip names its price; the selected slot's price shows
## beside the action, which is off when the slot costs more than `p_budget`.
func set_prices(p_price_of: Callable, p_budget: int) -> void:
	price_of = p_price_of
	budget = p_budget
	for i in _pads.size():
		# ANIM-R5 combat 9 (the tooltip scan): translated once, shown as given.
		_pads[i].tooltip_text = UiTip.fold(tr("%s\n%d CYCLES") % [_slice_text(i), int(price_of.call(i))])
		_pads[i].tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_update_price()


## The selected slot's price, or -1 (no slot, or no prices).
func selected_price() -> int:
	return int(price_of.call(selected)) if selected >= 0 and price_of.is_valid() else -1


func _update_price() -> void:
	if price_label == null:
		return
	# Art pass W9F (critique 55, §6.7): the price is on the action itself ("UPGRADE · 150
	# CYCLES"); short of Cycles, the line beside it says NEED n · HAVE m in HARM.
	var price := selected_price()
	var short := price >= 0 and budget >= 0 and price > budget
	price_label.text = (tr("NEED %d · HAVE %d") % [price, budget]) if short else ""
	price_label.visible = short
	price_label.add_theme_color_override("font_color", Palette.HARM)
	if _action_button != null:
		_action_button.set_tag_text(action_text())
		_action_button.disabled = short


## The action's words: the action, with the selected slot's price when prices are shown.
func action_text() -> String:
	var price := selected_price()
	return tr(action) if price < 0 else tr("%s · %d CYCLES") % [tr(action), price]


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


## ANIM-4: a column right of the wheel, clear of its slices, for pieces the loadout view
## adds (the Rank 3 ring segment swaps). Position and width in the wheel area (px).
const SIDE_X := 566.0
const SIDE_Y := 16.0
const SIDE_W := 100.0
const SIDE_GAP := 6
var _side: VBoxContainer = null


## Adds `control` to the column right of the wheel.
func add_side(control: Control) -> void:
	if _side == null:
		_side = VBoxContainer.new()
		_side.name = "Side"
		_side.position = Vector2(SIDE_X, SIDE_Y)
		_side.custom_minimum_size.x = SIDE_W
		_side.add_theme_constant_override("separation", SIDE_GAP)
		_wheel.add_child(_side)
	_side.add_child(control)


## Slot `k`'s pad (null when there is no such slot).
func slot_pad(k: int) -> Button:
	return _pads[k] if k >= 0 and k < _pads.size() else null


## ANIM-4b: drag and drop in UPGRADE mode, on a layer the screen owns (over the viewer,
## outliving it): `chip` (the slice being installed) sits in the column right of the wheel
## and drags onto a slot pad, the same as selecting the slot and pressing UPGRADE; pressing
## the chip picks it up (then a slot is aimed, or clicked).
var drops: DropLayer = null


func enable_drops(layer: DropLayer, chip: Control, payload: Dictionary) -> void:
	if drops != null or layer == null:
		return
	drops = layer
	add_side(chip)
	drops.add_source(chip, payload, true)
	for k in _pads.size():
		drops.add_target("slot:%d" % k, [String(payload.get("kind", ""))], "slot", k, DropLayer.rect_of(_pads[k]))


## The pad of inner ring segment `k` (null when the ring has none).
func ring_pad(k: int) -> Button:
	return _wheel.get_node_or_null("RingPad%d" % k) as Button


func add_tab(text: String, on_pressed: Callable, active: bool = false) -> void:
	var b := Button.new()
	b.text = tr(text)
	b.name = "Tab" + text
	# Same colours for both tabs: the active one is dark with a border, the other in
	# reverse video (light block, dark text) without one.
	var fg := Palette.TERMINAL_TEXT
	var bg := Palette.TERMINAL_BG
	var style := UiTheme.box(bg if active else fg, fg if active else Color(Palette.INK, 0.0), 2 if active else 0, 12, 4)
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
	_draw_circle_on()
	_wheel.queue_redraw()


## Art pass W9F (ART_BIBLE §6.6, §13 `marker_stroke`): the marker circle round the picked slot
## draws itself on (CIRCLE_MOTION, T2); the drippy circle lands when the stroke closes.
## Reduce effects or headless: the circle at once (its end state).
const CIRCLE_MOTION := &"upgrade_circle_draw"
const STROKE_SHADER := "res://shaders/marker_stroke.gdshader"
## The circle's radii round a slot (px) and the stroke's width.
const CIRCLE_RADII := Vector2(62, 56)
const CIRCLE_STROKE_W := 8.0
## True once the circle round `selected` is drawn whole.
var circle_drawn: bool = true
var _stroke: ColorRect = null


func _draw_circle_on() -> void:
	if _stroke != null and is_instance_valid(_stroke):
		_stroke.queue_free()
	_stroke = null
	circle_drawn = true
	if selected < 0 or not Motion.live(CIRCLE_MOTION) or not is_inside_tree():
		return
	circle_drawn = false
	var am := _angle(selected)
	var at := _centre() + Vector2(cos(am), sin(am)) * 140.0
	var box := CIRCLE_RADII * 2.0 + Vector2.ONE * CIRCLE_STROKE_W * 2.0
	_stroke = ColorRect.new()
	_stroke.name = "CircleStroke"
	_stroke.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := ShaderMaterial.new()
	mat.shader = load(STROKE_SHADER)
	mat.set_shader_parameter(&"shape", 0)
	mat.set_shader_parameter(&"size_px", box)
	mat.set_shader_parameter(&"width_px", CIRCLE_STROKE_W)
	mat.set_shader_parameter(&"ink", DripButton.DRIP_PINK)
	mat.set_shader_parameter(&"progress", 0.0)
	_stroke.material = mat
	_stroke.position = at - box * 0.5
	_stroke.size = box
	_wheel.add_child(_stroke)
	var e := Motion.entry(CIRCLE_MOTION)
	var tw := _stroke.create_tween()
	tw.tween_method(func(k: float) -> void: mat.set_shader_parameter(&"progress", k), 0.0, 1.0, Motion.seconds(CIRCLE_MOTION)).set_ease(e.ease).set_trans(e.trans)
	var stroke := _stroke
	tw.tween_callback(func() -> void:
		circle_drawn = true
		if is_instance_valid(stroke):
			stroke.queue_free()
		if _stroke == stroke:
			_stroke = null
		_wheel.queue_redraw())


## Ends the circle's stroke now (PageTransition.settle, a press).
func settle_motion() -> void:
	if not circle_drawn:
		if _stroke != null and is_instance_valid(_stroke):
			_stroke.queue_free()
		_stroke = null
		circle_drawn = true
		_wheel.queue_redraw()


func confirm() -> void:
	if selected < 0 or (_action_button != null and _action_button.disabled):
		return
	# Out of the tree first: the screen behind takes focus again before the pick rebuilds it.
	var picked := selected
	close()
	slot_picked.emit(picked)


## The wheel area's width (px): the window's body is this wide.
static func _wheel_width() -> float:
	return 670.0


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
	var t := "%s %s" % [tr(String(Palette.SLICE_NAMES.get(s.slice_type, "?"))), s.base_output if s.base_output > 0 else ""]
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
	_wheel.draw_circle(c, r1 + 44, Color(Palette.INK, 0.6))
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
			_wheel.draw_string(Palette.display(), c + Vector2(cos(am), sin(am)) * 208.0 + Vector2(-20, 10), str(s.base_output), HORIZONTAL_ALIGNMENT_CENTER, 40, letter_px(VALUE_FONT), col.lightened(0.35))
		if i < firmware.size() and firmware[i] != &"":
			_wheel.draw_rect(Rect2(c + Vector2(cos(am), sin(am)) * 116.0 - Vector2(5, 5), Vector2(10, 10)), Palette.NET_CYAN)
	_wheel.draw_circle(c, r0 - 6, Palette.NIGHT_SKY)
	_wheel.draw_arc(c, r1, 0, TAU, 64, wheel_color, 2.5)
	if hub == null and ring.is_empty():
		_wheel.draw_string(Palette.marker(), c + Vector2(-60, 8), tr("%d SLICES") % n, HORIZONTAL_ALIGNMENT_CENTER, 120, letter_px(COUNT_FONT), wheel_color)
	_draw_core(c)
	if selected >= 0 and circle_drawn:
		var am := _angle(selected)
		HandMarks.draw_drip_circle(_wheel, c + Vector2(cos(am), sin(am)) * 140.0, Vector2(62, 56), DripButton.DRIP_PINK)


## The slice detail popup for slot `index`.
func open_slot(index: int) -> void:
	if _popup != null and is_instance_valid(_popup):
		_popup.queue_free()
	var s := _slice(index)
	var pop := TerminalWindow.new(tr("SLICE %d DETAIL") % index, Palette.CELL_ACID)
	pop.name = "SliceDetail"
	pop.position = Vector2(400, 180)
	pop.custom_minimum_size = Vector2(480, 0)
	var icon := Control.new()
	icon.custom_minimum_size = Vector2(0, 64)
	var type := s.slice_type if s != null else RC.SliceType.MISS
	icon.draw.connect(func() -> void:
		SliceIcon.draw_icon(icon, Vector2(34, 32), 24, type, Palette.slice_color(type))
		icon.draw_string(Palette.display(), Vector2(76, 44), _slice_text(index), HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.font_px(POPUP_FONT), Palette.PAPER))
	pop.body.add_child(icon)
	var desc := Label.new()
	UiWrap.whole_words(desc)  # art pass W9F §4.3.3: whole words, never mid-word
	desc.custom_minimum_size.x = 440
	desc.text = Codex.describe(s) if s != null else String(slices[index])
	pop.body.add_child(desc)
	var ups := PackedStringArray()
	for u in upgrades:
		if s != null and u.slice_type == s.slice_type and u.base_output > s.base_output:
			ups.append("%s %d" % [tr(String(Palette.SLICE_NAMES.get(u.slice_type, "?"))), u.base_output])
	if not ups.is_empty():
		var up_label := Label.new()
		up_label.text = tr("UPGRADES: %s") % ", ".join(ups)
		up_label.add_theme_color_override("font_color", Palette.CELL_ACID)
		pop.body.add_child(up_label)
	var close_btn := Button.new()
	close_btn.text = tr("Close")
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
		_wheel.draw_string(Palette.mono(), at + Vector2(-20, 5), label, HORIZONTAL_ALIGNMENT_CENTER, 40, letter_px(RING_FONT), Palette.PAPER)
	if hub != null:
		var hot_hub := not _core_pads.is_empty() and _core_pads[0].has_focus()
		_wheel.draw_circle(c, HUB_RADIUS, Color(Palette.NIGHT_SKY, 0.95))
		_wheel.draw_arc(c, HUB_RADIUS, 0, TAU, 48, Palette.CELL_ACID if hot_hub else wheel_color, 2.0)
		# Art pass W9F (§4.3 rules 2-4): the hub's name fits the disc whole ("BREAKER COR"
		# clipped): one line at `body`, else `caption`, else folded onto two lines at a word
		# break, else its first word (the pad's tooltip keeps the whole name).
		var lay := hub_name_layout(TextDb.t(hub, "display_name").to_upper(), letter_px(HUB_FONT_SIZE), letter_px(HUB_MIN_FONT_SIZE))
		var lines: PackedStringArray = lay["lines"]
		var fs: int = lay["px"]
		var f := Palette.marker()
		var lh := f.get_height(fs)
		var top := c.y + HUB_TEXT_TOP - lh * (lines.size() - 1) * 0.5
		_wheel.draw_string(Palette.mono(), Vector2(c.x - HUB_RADIUS, top - lh * 0.5 - HUB_WORD_GAP), tr("HUB"), HORIZONTAL_ALIGNMENT_CENTER, HUB_RADIUS * 2.0, letter_px(HUB_WORD_FONT), Color(Palette.PAPER, 0.7))
		for k in lines.size():
			_wheel.draw_string(f, Vector2(c.x - HUB_TEXT_W * 0.5, top + lh * k + f.get_ascent(fs) - lh * 0.5), lines[k], HORIZONTAL_ALIGNMENT_CENTER, HUB_TEXT_W, fs, wheel_color)


## Art pass W9F: the hub name's room (px, the disc's chord a little inside it), where its
## first line sits below the centre, and the gap under the HUB word.
const HUB_TEXT_W := HUB_RADIUS * 2.0 - 12.0
const HUB_TEXT_TOP := 12.0
const HUB_WORD_GAP := 2.0
## Art pass W9F (§4.2, §12, as the combat wheels): the wheel's lettering follows the text
## scale up to LETTER_GROW_MAX, and never reads smaller on screen than its step however far
## the loadout scales the wheel down (`draw_scale`).
const LETTER_GROW_MAX := 1.3
## The scale the wheel is drawn at on screen (LoadoutView sets it; 1 in its own window).
var draw_scale: float = 1.0:
	set(v):
		draw_scale = maxf(0.01, v)
		if _wheel != null:
			_wheel.queue_redraw()


## The wheel-local size of type step `step`: step x the text scale (up to LETTER_GROW_MAX),
## divided by `draw_scale`, so it reads at that size on screen.
func letter_px(step: int) -> int:
	return ceili(step * minf(Settings.text_scale, LETTER_GROW_MAX) / draw_scale)


## Art pass W9F: how the hub's `name` fits the disc: {lines, px}. One line at `big`, then at
## `small`; then two lines at a word break at `small`; else the first word (never a clipped
## or broken word, never under `small`, the caption step).
static func hub_name_layout(hub_name: String, big: int = HUB_FONT_SIZE, small: int = HUB_MIN_FONT_SIZE) -> Dictionary:
	var f := Palette.marker()
	for fs in [big, small]:
		if f.get_string_size(hub_name, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x <= HUB_TEXT_W:
			return {"lines": PackedStringArray([hub_name]), "px": fs}
	var words := hub_name.split(" ", false)
	for cut in range(words.size() - 1, 0, -1):
		var a := " ".join(words.slice(0, cut))
		var b := " ".join(words.slice(cut))
		var fits_a := f.get_string_size(a, HORIZONTAL_ALIGNMENT_LEFT, -1, small).x <= HUB_TEXT_W
		var fits_b := f.get_string_size(b, HORIZONTAL_ALIGNMENT_LEFT, -1, small).x <= HUB_TEXT_W
		if fits_a and fits_b:
			return {"lines": PackedStringArray([a, b]), "px": small}
	return {"lines": PackedStringArray([words[0] if not words.is_empty() else hub_name]), "px": small}


## The detail popup of the hub core or an inner ring segment.
func open_part(part: Resource) -> void:
	if _popup != null and is_instance_valid(_popup):
		_popup.queue_free()
	var pop := TerminalWindow.new(tr("HUB CORE") if part is HubCoreData else tr("INNER RING SEGMENT"), Palette.NEON_VIOLET)
	pop.name = "CoreDetail"
	pop.position = Vector2(400, 180)
	pop.custom_minimum_size = Vector2(480, 0)
	var desc := Label.new()
	UiWrap.whole_words(desc)  # art pass W9F §4.3.3: whole words, never mid-word
	desc.custom_minimum_size.x = 440
	desc.text = Codex.describe(part)
	pop.body.add_child(desc)
	var close_btn := Button.new()
	close_btn.text = tr("Close")
	close_btn.pressed.connect(func() -> void: pop.queue_free(); _popup = null)
	pop.body.add_child(close_btn)
	add_child(pop)
	_popup = pop
	UiFocus.focus_first.call_deferred(pop)
