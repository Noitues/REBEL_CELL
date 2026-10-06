class_name SpinnerMini
extends Control
## The running operative's spinner in small (Animation pass ANIM-4b): its slots as wedges
## in their slice colours with the slice icons, a cyan square where a Firmware chip is
## socketed, and SPINNER under it. Each slot has a pad (`pad(k)`) with the slot's name as
## its tooltip: the drop targets of a Firmware chip or a slice upgrade dragged in the Mainframe,
## and of a Firmware chip taken from the loot. Not a focus stop (the pad's carry reticle
## reaches the slots); view only: it shows the slots, never changes them.
## Parity SHOP-06 (round 34 `firmware_socket`, round 32 `reward_screen_v2` FIRMWARE DROP): where a
## Firmware chip is on offer the wheel is also the socket choice (`make_pickable`; it replaces the
## "Chips go into:" dropdown whose list covered the info strip): one focus stop, a click on a
## slot or the arrows and A choose it; the chosen slot wears lime brackets, and while a chip is
## pointed at (`set_fits`, the rules' own answer from the screen) the slots it cannot go into grey
## out and are refused. `slot_chosen` says which; the screen buys or takes with it.

## Parity SHOP-06: a slot was chosen for the next chip (pickable), or refused (it does not fit).
signal slot_chosen(k: int)
signal refused(k: int)

## Parity SHOP-06: the chosen slot's bracket and outline (px at scale 1), a slot out of reach's
## shade (alpha), and the brackets' arm as a share of the wedge's depth.
const CHOSEN_LINE := 2.5
const UNFIT_SHADE := 0.62
const BRACKET_ARM := 0.45

## Wheel radii and the slot pads' size at scale 1 (px); SPINNER's lettering (px, grows with
## the text size up to CAPTION_MAX).
const RADIUS := 50.0
const INNER := 22.0
const PAD := 28.0
const ICON := 7.0
const FW_MARK := 7.0
const GAP := 0.04
const CAPTION_SIZE := 12
const CAPTION_MAX := 16
const CAPTION_GAP := 2.0
## The word under the wheel (a key, translated where drawn).
const CAPTION := "SPINNER" # TR

var slices: Array[StringName] = []
var firmware: Array[StringName] = []
var lookup: ContentLookup
var _pads: Array[Control] = []
## Parity SHOP-06: the socket choice (pickable only): the chosen slot, the slot the keys point
## at, the slot under the pointer, and which slots the pointed-at chip fits (empty: no chip).
var pickable: bool = false
var chosen: int = -1
var cursor: int = 0
var _hover: int = -1
var _fits: Array[bool] = []


func _init(p_slices: Array[StringName], p_firmware: Array[StringName], p_lookup: ContentLookup, tips: Array = []) -> void:
	name = "SpinnerMini"
	slices = p_slices
	firmware = p_firmware
	lookup = p_lookup
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	custom_minimum_size = Vector2(RADIUS * 2.0, RADIUS * 2.0 + CAPTION_GAP + _caption_height())
	for k in slices.size():
		var pad := Control.new()
		pad.name = "SlotPad%d" % k
		pad.size = Vector2(PAD, PAD)
		pad.custom_minimum_size = Vector2(PAD, PAD)
		pad.mouse_filter = Control.MOUSE_FILTER_PASS
		pad.focus_mode = Control.FOCUS_NONE
		pad.tooltip_text = String(tips[k]) if k < tips.size() else ""
		add_child(pad)
		_pads.append(pad)
	_place()


## Parity SHOP-06: makes the wheel the socket choice, slot `start` chosen (a focus stop).
func make_pickable(start: int = 0) -> void:
	pickable = true
	chosen = clampi(start, 0, maxi(0, slices.size() - 1))
	cursor = chosen
	focus_mode = Control.FOCUS_ALL
	mouse_filter = Control.MOUSE_FILTER_STOP
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	# the wheel draws its own focus (the cursor's slot), so the pad's focus scale leaves it be
	set_meta(UiFocus.META_NO_SCALE, true)
	KitState.track(self)
	focus_entered.connect(func() -> void: cursor = chosen; queue_redraw())
	focus_exited.connect(queue_redraw)
	mouse_exited.connect(func() -> void: _hover = -1; queue_redraw())
	queue_redraw()


## Parity SHOP-06: the chosen slot (-1 when the wheel is not the socket choice).
func selected() -> int:
	return chosen


## Parity SHOP-06: chooses slot `k` for the next chip: refused when the pointed-at chip does not
## fit it (KitState's refused flash), else it becomes the choice.
func choose(k: int) -> void:
	if not pickable or k < 0 or k >= slices.size():
		return
	cursor = k
	if not slot_fits(k):
		KitState.refuse(self)
		refused.emit(k)
		queue_redraw()
		return
	chosen = k
	slot_chosen.emit(k)
	queue_redraw()


## Parity SHOP-06: which slots the chip pointed at fits (the screen asks the rules); an empty
## list clears the marks (no chip pointed at).
func set_fits(fits: Array[bool]) -> void:
	_fits = fits
	queue_redraw()


## Parity SHOP-06: true when slot `k` takes the pointed-at chip (always, with no chip).
func slot_fits(k: int) -> bool:
	return _fits.is_empty() or k >= _fits.size() or _fits[k]


## Parity SHOP-06: the slot under local point `p` (-1 off the wedges).
func slot_at(p: Vector2) -> int:
	var d := p - centre()
	if d.length() < INNER or d.length() > RADIUS + 3.0 or slices.is_empty():
		return -1
	var n := slices.size()
	var best := -1
	var gap := TAU
	for k in n:
		var g := absf(angle_difference(d.angle(), angle(k)))
		if g < gap:
			gap = g
			best = k
	return best


func _gui_input(event: InputEvent) -> void:
	if not pickable:
		return
	if event is InputEventMouseMotion:
		var h := slot_at((event as InputEventMouseMotion).position)
		if h != _hover:
			_hover = h
			queue_redraw()
	elif event is InputEventMouseButton and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
		if (event as InputEventMouseButton).pressed:
			choose(slot_at((event as InputEventMouseButton).position))
		accept_event()
	elif event.is_action_pressed(&"ui_accept"):
		choose(cursor)
		accept_event()
	elif event.is_action_pressed(&"ui_right", true) and cursor + 1 < slices.size():
		cursor += 1
		queue_redraw()
		accept_event()
	elif event.is_action_pressed(&"ui_left", true) and cursor > 0:
		cursor -= 1
		queue_redraw()
		accept_event()
	# At an end (and up / down) the move is not taken: focus goes on to the next control.


func _get_tooltip(at_position: Vector2) -> String:
	var k := slot_at(at_position)
	return _pads[k].tooltip_text if k >= 0 and k < _pads.size() else tooltip_text


## Slot `k`'s pad (null when there is no such slot).
func pad(k: int) -> Control:
	return _pads[k] if k >= 0 and k < _pads.size() else null


## The wheel's centre (local).
func centre() -> Vector2:
	return Vector2(size.x * 0.5 if size.x > 0.0 else RADIUS, RADIUS)


## Middle angle of slot `k` (slot order as the spinner view and combat: +1 anticlockwise).
func angle(k: int) -> float:
	return -PI * 0.5 - TAU * k / maxf(1.0, slices.size())


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED:
		_place()


func _place() -> void:
	var mid := (RADIUS + INNER) * 0.5
	for k in _pads.size():
		_pads[k].position = centre() + Vector2(cos(angle(k)), sin(angle(k))) * mid - _pads[k].size * 0.5
	queue_redraw()


func _caption_height() -> float:
	return Palette.mono().get_height(_caption_size())


func _caption_size() -> int:
	return mini(CAPTION_MAX, roundi(CAPTION_SIZE * Settings.text_scale))


func _draw() -> void:
	var c := centre()
	var n := slices.size()
	draw_circle(c, RADIUS + 3.0, Color(0, 0, 0, 0.55))
	for k in n:
		var sd := lookup.get_content(slices[k]) as SliceData if lookup != null else null
		var type := sd.slice_type if sd != null else RC.SliceType.NULL
		var col := Palette.slice_color(type)
		var a0 := angle(k) - PI / n + GAP
		var a1 := angle(k) + PI / n - GAP
		var pts := PackedVector2Array()
		for q in 9:
			var a := lerpf(a0, a1, q / 8.0)
			pts.append(c + Vector2(cos(a), sin(a)) * RADIUS)
		for q in 9:
			var a := lerpf(a1, a0, q / 8.0)
			pts.append(c + Vector2(cos(a), sin(a)) * INNER)
		draw_colored_polygon(pts, Color(col, 0.55) if type != RC.SliceType.NULL else Color(col, 0.22))
		pts.append(pts[0])
		draw_polyline(pts, col.lightened(0.3), 1.2, true)
		var am := angle(k)
		SliceIcon.draw_on_slice(self, c + Vector2(cos(am), sin(am)) * (RADIUS + INNER) * 0.5, ICON, type, col)
		if k < firmware.size() and firmware[k] != &"":
			var at := c + Vector2(cos(am), sin(am)) * (INNER + FW_MARK * 0.5)
			draw_rect(Rect2(at - Vector2.ONE * FW_MARK * 0.5, Vector2.ONE * FW_MARK), Palette.NET_CYAN)
		if pickable:
			_draw_pick_marks(k, pts)
	draw_circle(c, INNER - 3.0, Palette.NIGHT_SKY)
	if pickable and chosen >= 0 and chosen < n:
		_draw_brackets(chosen)
	var fs := _caption_size()
	var font := Palette.mono()
	draw_string(font, Vector2(0, RADIUS * 2.0 + CAPTION_GAP + font.get_ascent(fs)), tr(CAPTION), HORIZONTAL_ALIGNMENT_CENTER, size.x, fs, Palette.TERMINAL_TEXT)


## Parity SHOP-06: a slot's marks while the wheel is the socket choice: greyed when the
## pointed-at chip does not fit it, its edge lit under the keys' cursor (focus) or the pointer.
func _draw_pick_marks(k: int, outline: PackedVector2Array) -> void:
	if not slot_fits(k):
		var shade := outline.slice(0, outline.size() - 1)
		draw_colored_polygon(shade, Color(Palette.NIGHT_SKY, UNFIT_SHADE))
	var st := KitState.FOCUS if has_focus() and k == cursor else (KitState.HOVER if k == _hover else KitState.IDLE)
	if st != KitState.IDLE:
		draw_polyline(outline, KitState.edge_color(st), 1.5, true)


## Parity SHOP-06 (round 34 `firmware_socket`): lime brackets round the chosen slot: its outer
## corners and inner corners, the arms along the rim and the sides.
func _draw_brackets(k: int) -> void:
	var c := centre()
	var n := slices.size()
	var a0 := angle(k) - PI / n + GAP
	var a1 := angle(k) + PI / n - GAP
	var col := Palette.CELL_ACID
	var depth := (RADIUS - INNER) * BRACKET_ARM
	var sweep := (a1 - a0) * BRACKET_ARM * 0.5
	for side: Array in [[a0, 1.0], [a1, -1.0]]:
		var a: float = side[0]
		var dir: float = side[1]
		var rim := PackedVector2Array()
		for q in 5:
			var t := a + dir * sweep * q / 4.0
			rim.append(c + Vector2(cos(t), sin(t)) * (RADIUS + CHOSEN_LINE))
		draw_polyline(rim, col, CHOSEN_LINE, true)
		var out := Vector2(cos(a), sin(a))
		draw_line(c + out * (RADIUS + CHOSEN_LINE), c + out * (RADIUS + CHOSEN_LINE - depth), col, CHOSEN_LINE, true)
		draw_line(c + out * (INNER - CHOSEN_LINE * 0.5), c + out * (INNER - CHOSEN_LINE * 0.5 + depth), col, CHOSEN_LINE, true)
