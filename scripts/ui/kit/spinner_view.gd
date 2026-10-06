class_name SpinnerView
extends Control
## Spinner viewer (modal): the wheel drawn large, each slice a pad with its icon and
## value. Right-click opens a slice's detail popup (type, output, firmware, stronger
## same-type slices from the Mainframe catalogue). With an `action` ("UPGRADE") left click
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
## B5 (loadout's SPINNER tab, round 44 `deck_viewer_spinner.png`): the window (px), the wheel's pool and its size (the
## combat's own D4 wheel at about r = 220 at 1080p: WheelView sizes its disc to its box), the rows' column width, the
## pool's dimming and the slice rows' glyph box.
const D4_WINDOW := Vector2(1160, 580)
const D4_POOL := Vector2(600, 440)
const D4_ROWS_W := 500.0
const D4_POOL_DIM := Color(0.02, 0.02, 0.05, 0.55)
## The D4 wheel's box reaches this far past the pool's top and foot (px): WheelView keeps room round its disc for
## the needle and the HP line, which the pool's own margins already give, so the disc comes to r = 220 at 1080p.
const D4_WHEEL_GROW := 40.0
const D4_GLYPH := 22.0
## The pads over the D4 wheel's slices and its inner ring plates (px).
const D4_PAD := 56.0
const D4_RING_PAD := 30.0

## B5: the combat's own wheel in the loadout's SPINNER tab (null: the drawn wheel of the Mainframe's pickers).
var d4: WheelView = null
var _d4_combatant: CombatantState = null
var _rows: VBoxContainer = null
var _slice_rows: VBoxContainer = null
var _core_rows: VBoxContainer = null


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
	# H24 S4: the viewer shows its words as given: the title comes translated, the action
	# is a key ("UPGRADE") translated where shown.
	TextDb.shown_as_given(self)
	window = CrtWindow.new(p_title, Palette.CELL_PINK).with_kind(CrtWindow.kind_for(Palette.CELL_PINK), Palette.CELL_PINK)  # B5: the v2 terminal
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


## B5 (review section c, round 44 `deck_viewer_spinner.png`): the loadout's SPINNER tab shows the combat's own D4
## wheel (WheelView, `c` the operative's display combatant: LoadoutView.display_combatant) at combat size in a dimmed
## pool of the city, and beside it the slices as glyph rows (read clockwise from the needle), then FIRMWARE // HUB.
## The slot pads (details), the hub and inner ring pads (details, the Rank 3 swaps' drop targets) sit over the D4
## wheel's own slices and plates. Call before the view enters the tree.
func use_d4(c: CombatantState) -> void:
	_d4_combatant = c
	var crt := window as CrtWindow
	window.custom_minimum_size = D4_WINDOW
	window.position = Vector2((1280.0 - D4_WINDOW.x) * 0.5, minf(SubtitleStrip.top_below(50.0), CANVAS_BOTTOM - D4_WINDOW.y))
	var row := HBoxContainer.new()
	row.name = "D4Row"
	row.add_theme_constant_override(&"separation", UiTheme.SP_L)
	var at := _wheel.get_index()
	window.body.remove_child(_wheel)
	window.body.add_child(row)
	window.body.move_child(row, at)
	row.add_child(_wheel)
	_wheel.custom_minimum_size = D4_POOL
	for pad in _pads:
		pad.remove_theme_stylebox_override("focus")  # the theme's lime brackets over the D4 wheel's slice
	d4 = WheelView.new()
	d4.name = "D4Wheel"
	d4.show_arrows = false
	d4.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_wheel.add_child(d4)
	_wheel.move_child(d4, 0)
	d4.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	d4.offset_top = -D4_WHEEL_GROW
	d4.offset_bottom = D4_WHEEL_GROW
	_rows = VBoxContainer.new()
	_rows.name = "Rows"
	_rows.custom_minimum_size.x = D4_ROWS_W
	_rows.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_rows.add_theme_constant_override(&"separation", UiTheme.SP_S)
	# The rows scroll beside the pool when they outgrow it (big text, a ring class).
	var rows_scroll := ScrollContainer.new()
	rows_scroll.name = "RowsScroll"
	rows_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	rows_scroll.follow_focus = true
	rows_scroll.custom_minimum_size = Vector2(D4_ROWS_W, D4_POOL.y)
	rows_scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	rows_scroll.add_child(_rows)
	row.add_child(rows_scroll)
	_rows.add_child(_caption(tr("SLICES  //  read clockwise from the needle")))
	_slice_rows = VBoxContainer.new()
	_slice_rows.name = "SliceRows"
	_rows.add_child(_slice_rows)
	for i in slices.size():
		var s := _slice(i)
		var type := s.slice_type if s != null else RC.SliceType.NULL
		var words := tr(String(Codex.SLICE_TYPE_TEXT.get(type, ""))) if s != null else ""  # what the slice does (round 44)
		_slice_rows.add_child(_glyph_row(CodexBook.atlas_glyph("Slices", {"slice": type}), Palette.slice_color(type), _slice_text(i), words))
	_rows.add_child(_caption(tr("FIRMWARE  //  HUB")))
	_core_rows = VBoxContainer.new()
	_core_rows.name = "CoreRows"
	_rows.add_child(_core_rows)
	for i in firmware.size():
		if firmware[i] == &"":
			continue
		var fw := lookup.get_content(firmware[i])
		_core_rows.add_child(_glyph_row(CodexBook.atlas_glyph("Firmware", {"id": firmware[i]}), Palette.CELL_ACID,
			"%s  //  %s" % [TextDb.t(fw, "display_name") if fw != null else String(firmware[i]), _slice_text(i)], _rule_line(fw)))
	if crt != null:
		crt.tag_label.text = ""


## What a part does in one line: its Codex description past its name line ("" when none).
static func _rule_line(res: Resource) -> String:
	if res == null:
		return ""
	var lines := Codex.describe(res).split("\n", false)
	return lines[1] if lines.size() > 1 else (lines[0] if lines.size() == 1 else "")


func _caption(words: String) -> Label:
	var l := Chrome.caps_label(words, UiTheme.CAPTION, Palette.CELL_PINK)
	l.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	return l


## A glyph row (the tooltips' rows): the glyph in its tile, the name, its words under it.
func _glyph_row(glyph: StringName, col: Color, title: String, words: String) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.name = "Row"
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override(&"separation", UiTheme.SP_S)
	var side := D4_GLYPH * minf(Settings.text_scale, CodexBook.GLYPH_SCALE_MAX)
	var tile := Control.new()
	tile.custom_minimum_size = GlyphIcon.cell_size_for(side)
	tile.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	tile.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tile.draw.connect(func() -> void: CodexBook.draw_tile(tile, col))
	if glyph != &"":
		var g := GlyphIcon.make(glyph, side)
		g.fill = col
		tile.add_child(g)
	row.add_child(tile)
	var box := VBoxContainer.new()
	box.add_theme_constant_override(&"separation", 0)
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var t := Label.new()
	t.text = title.to_upper()
	t.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	t.add_theme_font_override(&"font", Palette.body_medium())
	t.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.LABEL))
	t.add_theme_color_override(&"font_color", Palette.TEXT_HI)
	box.add_child(t)
	if words != "":
		var w := Label.new()
		w.text = words
		w.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		w.add_theme_font_override(&"font", Palette.body())
		w.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.BODY))
		w.add_theme_color_override(&"font_color", Palette.TEXT_MID)
		UiWrap.whole_words(w)
		w.custom_minimum_size.x = D4_ROWS_W - tile.custom_minimum_size.x - UiTheme.SP_S
		box.add_child(w)
	row.add_child(box)
	return row


func _ready() -> void:
	# Modal for keys and the pad (H20); inside the loadout view, the loadout view holds.
	if not (get_parent() is LoadoutView):
		UiFocus.hold(self)
	if d4 != null:
		d4.show_combatant(_d4_combatant, [], [], lookup)
		d4.resized.connect(_place_pads)
	Settings.hints_changed.connect(_relabel)
	_relabel()
	_place_pads.call_deferred()
	if not _pads.is_empty():
		_pads[0].grab_focus.call_deferred()
	else:
		UiFocus.focus_first.call_deferred(self)


## Key hints follow the device in use and the binds (H20).
func _relabel() -> void:
	close_button.text = ("%s %s" % [tr("Close"), Settings.hint(&"ui_cancel")]).strip_edges()
	var pick := Settings.key_text(&"ui_accept") if Settings.pad_active else tr("Left click")
	var more := Settings.key_text(&"inspect") if Settings.pad_active else tr("Right click")
	hint_label.text = (tr("%s: select the slot to %s. %s: details.") % [pick, tr(action).to_lower(), more]) if action != "" else tr("%s a slice for details.") % (tr("Press") if Settings.pad_active else tr("Click"))


## Pick mode prices (H20: the NULL slot costs more): `p_price_of(slot) -> int` and the
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
	var price := selected_price()
	price_label.text = (tr("%d CYCLES") % price) if price >= 0 else ""
	var short := price >= 0 and budget >= 0 and price > budget
	price_label.add_theme_color_override("font_color", Palette.CELL_PINK if short else Palette.CELL_ACID)
	if _action_button != null:
		_action_button.disabled = short
		# Parity SHOP-08 (the M13 build's one graffiti line): the verb and the slot's price are one
		# tag, "UPGRADE · 100 CYCLES"; the price label keeps the number but is not shown twice.
		_action_button.set_tag_text(action_words(tr(action), price))
		price_label.visible = price < 0


## Parity SHOP-08: the action's tag with the selected slot's price folded in ("UPGRADE · 100
## CYCLES"; the verb alone with no price). `verb` comes translated.
static func action_words(verb: String, price: int) -> String:
	return TranslationServer.translate("%s · %d CYCLES") % [verb, price] if price >= 0 else verb


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
		if d4 == null:
			pad.add_theme_stylebox_override("focus", StyleBoxEmpty.new())  # the drawn wheel lights its own focus
		pad.tooltip_text = UiTip.fold(Codex.describe(part))
		pad.pressed.connect(func() -> void: open_part(part))
		pad.focus_entered.connect(_wheel.queue_redraw)
		pad.focus_exited.connect(_wheel.queue_redraw)
		_wheel.add_child(pad)
		_core_pads.append(pad)
	if _core_rows != null:
		# B5: the hub core and the inner ring's segments as glyph rows under the Firmware.
		if hub != null:
			_core_rows.add_child(_glyph_row(CodexBook.atlas_glyph("Classes", {"hub": String(hub.id)}), Palette.CELL_PINK, TextDb.t(hub, "display_name"), _rule_line(hub)))
		for seg in ring:
			if seg != null:
				_core_rows.add_child(_glyph_row(CodexBook.atlas_glyph("Ring segments", {"id": seg.id}), Palette.NEON_VIOLET, TextDb.t(seg, "display_name"),
					_rule_line(seg)))
	_place_pads.call_deferred()
	_wheel.queue_redraw()


## ANIM-4: a column right of the wheel, clear of its slices, for pieces the loadout view
## adds (the Rank 3 ring segment swaps). Position and width in the wheel area (px).
const SIDE_X := 566.0
const SIDE_Y := 16.0
const SIDE_W := 100.0
const SIDE_GAP := 6
## ART-0 C: above this text scale the column scrolls inside the wheel area.
const SIDE_SCROLL_ABOVE := 1.6
var _side: VBoxContainer = null


## Adds `control` to the column right of the wheel.
## The side column's x in the wheel area: SIDE_X, or on the D4 tab the pool's right edge less its width.
func side_x() -> float:
	return D4_POOL.x - SIDE_W - SIDE_GAP if d4 != null else SIDE_X


func add_side(control: Control) -> void:
	if _side == null:
		_side = VBoxContainer.new()
		_side.name = "Side"
		# B5: on the D4 tab the column sits at the pool's right edge, clear of the D4 wheel's disc.
		_side.position = Vector2(side_x(), SIDE_Y)
		_side.custom_minimum_size.x = SIDE_W
		_side.add_theme_constant_override("separation", SIDE_GAP)
		if Settings.text_scale > SIDE_SCROLL_ABOVE:
			# ART-0 C (text scale 2.0): the column scrolls inside the wheel area (focus follows)
			# instead of running past the window's foot (five swaps took 564 px at 2.0).
			var scroll := ScrollContainer.new()
			scroll.name = "Side"
			_side.name = "SideList"
			_side.position = Vector2.ZERO
			scroll.position = Vector2(side_x(), SIDE_Y)
			scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
			scroll.follow_focus = true
			scroll.add_child(_side)
			_wheel.add_child(scroll)
			var fit := func() -> void: scroll.size = Vector2(SIDE_W, maxf(0.0, _wheel.size.y - SIDE_Y * 2.0))
			_wheel.resized.connect(fit)
			fit.call()
		else:
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
	tab_row.add_child(DeckView.tab_button(text, on_pressed, active, Palette.CELL_PINK))  # B5: the round 31 tab plates


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
	if d4 != null:
		_place_d4_pads()
		return
	for i in _pads.size():
		_pads[i].position = _centre() + Vector2(cos(_angle(i)), sin(_angle(i))) * 140.0 - Vector2(35, 35)
	var k0 := 0
	if hub != null and not _core_pads.is_empty():
		_core_pads[0].position = _centre() - _core_pads[0].size * 0.5
		k0 = 1
	for k in range(k0, _core_pads.size()):
		var a := _ring_angle(k - k0)
		_core_pads[k].position = _centre() + Vector2(cos(a), sin(a)) * (RING_INNER + RING_OUTER) * 0.5 - _core_pads[k].size * 0.5


## B5: the pads over the D4 wheel: a slot pad on each slice (WheelView.slot_spot), the hub's at the centre, an inner
## ring pad on each segment plate (where WheelView draws it: RING_PLATE_R at the segment's angle).
func _place_d4_pads() -> void:
	if not d4.is_inside_tree() or d4.combatant == null:
		return
	var origin := _wheel.global_position
	for i in _pads.size():
		_pads[i].custom_minimum_size = Vector2.ONE * D4_PAD
		_pads[i].size = Vector2.ONE * D4_PAD
		_pads[i].position = d4.slot_spot(i) - origin - _pads[i].size * 0.5
	var k0 := 0
	if hub != null and not _core_pads.is_empty():
		_core_pads[0].position = d4.global_center() - origin - _core_pads[0].size * 0.5
		k0 = 1
	var irot := d4.shown_inner_rotation()
	for k in range(k0, _core_pads.size()):
		var seg := k - k0
		var deg := fposmod((irot - seg * float(RC.TICKS) / float(RC.RING_SEGMENTS)) * WheelView.DEG_PER_TICK, 360.0)
		var at := WheelFace.at(d4.global_center(), d4.art_scale(), WheelView.RING_PLATE_R, deg)
		_core_pads[k].custom_minimum_size = Vector2.ONE * D4_RING_PAD
		_core_pads[k].size = Vector2.ONE * D4_RING_PAD
		_core_pads[k].position = at - origin - _core_pads[k].size * 0.5


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
	if d4 != null:
		# B5: the D4 wheel draws itself; under it the dimmed pool the window opens onto, its edge in the accent.
		var r := Rect2(Vector2.ZERO, _wheel.size)
		_wheel.draw_rect(r, D4_POOL_DIM)
		_wheel.draw_rect(r.grow(-0.5), Color(PaletteSkins.chrome(Palette.CELL_PINK), 0.35), false, 1.0)
		return
	var c := _centre()
	var n := slices.size()
	var r0 := 100.0
	var r1 := 180.0
	_wheel.draw_circle(c, r1 + 44, Color(0, 0, 0, 0.6))
	for i in n:
		var s := _slice(i)
		var type := s.slice_type if s != null else RC.SliceType.NULL
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
		_wheel.draw_colored_polygon(pts, Color(col, 0.7 if i == _hot else 0.5) if type != RC.SliceType.NULL else Color(col, 0.2))
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
		_wheel.draw_string(Palette.marker(), c + Vector2(-60, 8), tr("%d SLICES") % n, HORIZONTAL_ALIGNMENT_CENTER, 120, 18, wheel_color)
	_draw_core(c)
	if selected >= 0:
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
	var type := s.slice_type if s != null else RC.SliceType.NULL
	icon.draw.connect(func() -> void:
		SliceIcon.draw_icon(icon, Vector2(34, 32), 24, type, Palette.slice_color(type))
		icon.draw_string(Palette.display(), Vector2(76, 44), _slice_text(index), HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Palette.PAPER))
	pop.body.add_child(icon)
	var desc := Label.new()
	UiWrap.whole_words(desc)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
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
		_wheel.draw_string(Palette.mono(), at + Vector2(-20, 5), label, HORIZONTAL_ALIGNMENT_CENTER, 40, 13, Palette.PAPER)
	if hub != null:
		var hot_hub := not _core_pads.is_empty() and _core_pads[0].has_focus()
		_wheel.draw_circle(c, HUB_RADIUS, Color(Palette.NIGHT_SKY, 0.95))
		_wheel.draw_arc(c, HUB_RADIUS, 0, TAU, 48, Palette.CELL_ACID if hot_hub else wheel_color, 2.0)
		_wheel.draw_string(Palette.mono(), c + Vector2(-HUB_RADIUS, -4), tr("HUB"), HORIZONTAL_ALIGNMENT_CENTER, HUB_RADIUS * 2.0, 11, Color(Palette.PAPER, 0.7))
		# The hub's name shrinks to fit the disc.
		var hub_name := TextDb.t(hub, "display_name").to_upper()
		var fs := HUB_FONT_SIZE
		var w := Palette.marker().get_string_size(hub_name, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		if w > HUB_RADIUS * 2.0 - 8.0:
			fs = maxi(HUB_MIN_FONT_SIZE, floori(fs * (HUB_RADIUS * 2.0 - 8.0) / w))
		_wheel.draw_string(Palette.marker(), c + Vector2(-HUB_RADIUS + 4, 14), hub_name, HORIZONTAL_ALIGNMENT_CENTER, HUB_RADIUS * 2.0 - 8, fs, wheel_color)


## The detail popup of the hub core or an inner ring segment.
func open_part(part: Resource) -> void:
	if _popup != null and is_instance_valid(_popup):
		_popup.queue_free()
	var pop := TerminalWindow.new(tr("HUB CORE") if part is HubCoreData else tr("INNER RING SEGMENT"), Palette.NEON_VIOLET)
	pop.name = "CoreDetail"
	pop.position = Vector2(400, 180)
	pop.custom_minimum_size = Vector2(480, 0)
	var desc := Label.new()
	UiWrap.whole_words(desc)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
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
