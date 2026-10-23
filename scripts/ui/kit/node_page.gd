class_name NodePage
extends VBoxContainer
## RG-02/03: the page of a REST or WORKSHOP node. Look (art, nodes round 2: the event page's layout): the window is a CRT terminal in the
## kind's hue (`RouteInk.accent_of`), the rows are the event page's choice stickers (the number on the yellow tab), the verbs are vinyl
## stickers; the scene stands the kind sticker and its icon beside it (`netrun_scene._show_node_page`). Every element,
## name and string is the placeholder page's. Mouse and keyboard: click a button, or press 1-9 to pick a wheel slot / offer,
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

## Look (px at text scale 1): the choice stickers' width, the gaps between them, the verbs' lettering and the grid's columns.
const ROW_W := 380.0
const ROW_GAP := 14.0
const BLOCK_GAP := 10.0
const VERB_PX := 30
## The offers' share of a slot row's width (three offers stand in the width of two slots).
const OFFER_SHARE := 0.62
const SLOT_COLUMNS := 2
const OFFER_COLUMNS := 3
## The verbs' tint and the dim of a spent verb.
const SPENT_ALPHA := 0.55


## Builds the page for the session's open node page (`run.phase`).
func setup(s: NetrunSession) -> void:
	_s = s
	name = "NodePage"
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	size_flags_vertical = Control.SIZE_SHRINK_BEGIN
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
	l.add_theme_font_override(&"font", Palette.mono())
	l.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.LABEL))
	l.add_theme_color_override(&"font_color", Palette.TEXT_MID)
	return l


## The kind's CRT window (the event page's way: a corp-style accent in the kind's hue).
func _window(title: String, kind: String, node_name: String) -> CrtWindow:
	var col := RouteInk.accent_of(kind)
	var win := CrtWindow.new(title, col).with_kind(CrtWindow.kind_for(col), col)
	win.name = node_name
	win.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_child(win)
	return win


## A vinyl verb sticker that is the page's button (named, pressable, disabled when spent).
func _verb(text: String, fill: int, node_name: String, tip: String = "") -> HoloSticker:
	var os := minf(Settings.text_scale, ShopItem.OBJECT_MAX_SCALE)
	var b := HoloSticker.verb_word(text, fill, os, VERB_PX)
	b.name = node_name
	b.tooltip_text = tip
	return b


## A spent verb dims and shows the sticker's disabled state.
func _spend(b: HoloSticker, spent: bool) -> void:
	b.disabled = spent
	if spent:
		b.sticker.set_state(VinylSticker.State.DISABLED)
		b.modulate.a = SPENT_ALPHA


## A row as the event page's choice sticker: the button keeps its name and words, the plate is drawn behind it and the number
## stands on the yellow tab (so the words no longer lead with it).
func _choice(text: String, node_name: String, number: int, width: float, tip: String = "") -> Button:
	var b := _button(text, node_name, tip)
	b.theme_type_variation = ChoiceSticker.TYPE
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.autowrap_mode = TextServer.AUTOWRAP_WORD
	b.custom_minimum_size.x = width * minf(Settings.text_scale, ShopItem.OBJECT_MAX_SCALE)
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	b.add_child(ChoiceSticker.new(number, Settings.text_scale))
	return b


## The grid a page's choice stickers stand in (their theme gives the plate its room and lettering).
func _grid(node_name: String, columns: int) -> GridContainer:
	var g := GridContainer.new()
	g.name = node_name
	g.columns = columns
	var os := minf(Settings.text_scale, ShopItem.OBJECT_MAX_SCALE)
	g.add_theme_constant_override(&"h_separation", roundi(ROW_GAP * os * 2.0))
	g.add_theme_constant_override(&"v_separation", roundi(ROW_GAP * os))
	g.theme = ChoiceSticker.theme_for(Settings.text_scale)
	return g



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
	var win := _window(tr("REST"), CityMapOverlay.KIND_REST, "RestWindow") # TR
	var os := minf(Settings.text_scale, ShopItem.OBJECT_MAX_SCALE)
	win.body.add_theme_constant_override(&"separation", roundi(BLOCK_GAP * os))
	var op := _s.run.operative
	var done := _s.rest_done()
	var pv := _s.rest_patch_preview()
	var top := HBoxContainer.new()
	top.add_theme_constant_override(&"separation", roundi(ROW_GAP * os))
	win.body.add_child(top)
	var hp := _label(tr("HP %d/%d") % [op.hp, op.max_hp], "RestHp") # TR
	hp.add_theme_color_override(&"font_color", Palette.TEXT_HI)
	hp.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hp.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	top.add_child(hp)
	var patch := _verb(tr("PATCH  +%d HP -> %d/%d") % [pv["heal"], pv["hp_after"], pv["max_hp"]], VinylSticker.Fill.PINK, "RestPatch", # TR
			tr("Heal %d%% of max HP. One mode per visit.") % _s.config.rest_heal_pct) # TR
	_spend(patch, done)
	patch.pressed.connect(func() -> void: patch_pressed.emit())
	top.add_child(patch)
	win.body.add_child(_label(tr("REWIRE: pick a wheel slot, then the slot to swap its Firmware with.") if not done else tr("This REST is spent."), "RestHint")) # TR
	var row := _grid("RestSlots", SLOT_COLUMNS)
	win.body.add_child(row)
	var after := _s.rest_rewire_preview(_first, _second) if _first >= 0 and _second >= 0 else op.slot_firmware_ids
	for i in op.slot_slice_ids.size():
		var txt := "%s  [%s]" % [_name_of(op.slot_slice_ids[i]), _name_of(after[i])]
		var b := _choice(txt, "RestSlot%d" % i, i + 1, ROW_W)
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
	foot.add_theme_constant_override(&"separation", roundi(ROW_GAP * os))
	win.body.add_child(foot)
	var confirm := _verb(tr("CONFIRM REWIRE"), VinylSticker.Fill.PINK, "RestConfirm") # TR
	_spend(confirm, done or _first < 0 or _second < 0 or _s.rest_rewire_error(_first, _second) != "")
	confirm.pressed.connect(func() -> void: rewire_confirmed.emit(_first, _second))
	foot.add_child(confirm)
	var undo := _verb(tr("UNDO"), VinylSticker.Fill.WHITE, "RestUndo") # TR
	_spend(undo, not done)
	undo.pressed.connect(func() -> void: undo_pressed.emit())
	foot.add_child(undo)
	foot.add_child(_spacer())
	foot.add_child(_leave("RestLeave"))


## The foot's spring.
func _spacer() -> Control:
	var c := Control.new()
	c.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return c


## LEAVE: the holographic sticker (the Mainframe's), named per page.
func _leave(node_name: String) -> HoloSticker:
	var os := minf(Settings.text_scale, ShopItem.OBJECT_MAX_SCALE)
	var b := HoloSticker.new(tr("LEAVE"), "", os, VinylSticker.Fill.HOLO, VERB_PX) # TR
	b.name = node_name
	b.add_fold_room()
	b.pressed.connect(func() -> void: leave_pressed.emit())
	return b


func _pick_slot(i: int) -> void:
	if _first < 0 or i == _first:
		_first = -1 if i == _first else i
		_second = -1
	else:
		_second = i
	setup(_s)


# --- WORKSHOP --------------------------------------------------------------------------------

## The picked offer is `_first`, the wheel slot it replaces `_second`.
func _build_workshop() -> void:
	var win := _window(tr("WORKSHOP"), CityMapOverlay.KIND_WORKSHOP, "WorkshopWindow") # TR
	var os := minf(Settings.text_scale, ShopItem.OBJECT_MAX_SCALE)
	win.body.add_theme_constant_override(&"separation", roundi(BLOCK_GAP * os))
	var offers: Array = _s.run.node_state.get("offers", [])
	var spent := int(_s.run.node_state.get("bought", 0)) >= _s.config.workshop_buys_per_visit
	var cyc := _label(tr("Cycles: %d") % _s.run.cycles, "WorkshopCycles") # TR
	cyc.add_theme_color_override(&"font_color", Palette.TEXT_HI)
	win.body.add_child(cyc)
	win.body.add_child(_label(tr("This Workshop is spent.") if spent else tr("Pick a slice, then the wheel slot it replaces."), "WorkshopHint")) # TR
	var offer_box := _grid("WorkshopOffers", OFFER_COLUMNS)
	win.body.add_child(offer_box)
	for i in offers.size():
		var b := _choice(_name_of(StringName(String(offers[i]))), "WorkshopOffer%d" % i, i + 1, ROW_W * OFFER_SHARE)
		b.toggle_mode = true
		b.button_pressed = i == _first
		b.disabled = spent
		var idx := i
		b.pressed.connect(func() -> void: _pick_offer(idx))
		offer_box.add_child(b)
	var slot_box := _grid("WorkshopSlots", SLOT_COLUMNS)
	win.body.add_child(slot_box)
	var op := _s.run.operative
	for i in op.slot_slice_ids.size():
		var why := _s.workshop_error(_first, i) if _first >= 0 else ""
		var b := _choice("%s  (%d)" % [_name_of(op.slot_slice_ids[i]), _s.workshop_price(i)], "WorkshopSlot%d" % i, i + 1, ROW_W, why)
		b.toggle_mode = true
		b.button_pressed = i == _second
		b.disabled = spent or _first < 0 or why != ""
		var idx := i
		b.pressed.connect(func() -> void: _pick_target(idx))
		slot_box.add_child(b)
	var foot := HBoxContainer.new()
	foot.add_theme_constant_override(&"separation", roundi(ROW_GAP * os))
	win.body.add_child(foot)
	var ready := not spent and _first >= 0 and _second >= 0 and _s.workshop_error(_first, _second) == ""
	var buy_text := tr("BUY") # TR
	if ready:
		var pv := _s.workshop_preview(_first, _second)
		buy_text = tr("BUY  %d Cycles (%d left)") % [pv["price"], pv["cycles_after"]] # TR
	var buy := _verb(buy_text, VinylSticker.Fill.PINK, "WorkshopBuy")
	_spend(buy, not ready)
	buy.pressed.connect(func() -> void: buy_confirmed.emit(_first, _second))
	foot.add_child(buy)
	foot.add_child(_spacer())
	foot.add_child(_leave("WorkshopLeave"))


func _pick_offer(i: int) -> void:
	_first = -1 if i == _first else i
	_second = -1
	setup(_s)


func _pick_target(i: int) -> void:
	_second = -1 if i == _second else i
	setup(_s)


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
	elif k.keycode >= KEY_1 and k.keycode <= KEY_9 and _s.run.phase == RunState.Phase.WORKSHOP:
		var wi := k.keycode - KEY_1
		if _first < 0 and wi < _s.run.node_state.get("offers", []).size():
			_pick_offer(wi)
			get_viewport().set_input_as_handled()
		elif _first >= 0 and wi < _s.run.operative.slot_slice_ids.size() and _s.workshop_error(_first, wi) == "":
			_pick_target(wi)
			get_viewport().set_input_as_handled()
	elif k.keycode == KEY_ENTER or k.keycode == KEY_KP_ENTER:
		if _s.run.phase == RunState.Phase.WORKSHOP and _first >= 0 and _second >= 0 and _s.workshop_error(_first, _second) == "":
			buy_confirmed.emit(_first, _second)
			get_viewport().set_input_as_handled()
		elif _s.run.phase == RunState.Phase.REST and _first >= 0 and _second >= 0 and _s.rest_rewire_error(_first, _second) == "":
			rewire_confirmed.emit(_first, _second)
			get_viewport().set_input_as_handled()
	elif k.keycode == KEY_ESCAPE:
		if _first >= 0:
			_first = -1
			_second = -1
			setup(_s)
			get_viewport().set_input_as_handled()
