class_name DeckView
extends Control
## Deck viewer (modal): every card in the deck as its sticker. Right-click opens a card's
## detail popup. With an `action` ("REMOVE", "UPGRADE") left click selects / deselects
## one card, marked with a hand-drawn X (remove) or a drippy circle (upgrade), and the
## action appears in dripping marker next to Close; pressing it emits `card_picked`.
## Without an action, left click opens the detail. Emits `closed`. View only.

signal card_picked(index: int)
signal closed

var deck: Array[StringName] = []
var lookup: ContentLookup
var action: String = ""
var selected: int = -1
var window: TerminalWindow
var tab_row: HBoxContainer
var _cards: Array[ZineCard] = []
var _action_button: DripButton = null
var _popup: Control = null
var close_button: Button
var hint_label: Label
## The card grid's width, gap, and the fewest cards a row keeps at big text (px).
const GRID_WIDTH := 860.0
const GRID_GAP := 14.0
const CARDS_PER_ROW := 4
## Card rarities in words (keys).
const RARITY_WORDS: Array[String] = ["Common", "Uncommon", "Rare", "Boss"] # TR


func _init(p_deck: Array[StringName], p_lookup: ContentLookup, p_title: String = "DECK", p_action: String = "") -> void:
	deck = p_deck
	lookup = p_lookup
	action = p_action
	name = "DeckView"
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var dim := ColorRect.new()
	dim.color = Palette.SCRIM
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	# H24 S4: the viewer shows its words as given: the title comes translated, the action
	# is a key ("REMOVE") translated where shown.
	TextDb.shown_as_given(self)
	window = TerminalWindow.new(tr("%s // %d CARDS") % [p_title, deck.size()], Palette.CELL_PINK)
	window.custom_minimum_size = Vector2(900, 540)
	window.position = Vector2(190, SubtitleStrip.top_below(70.0))  # under the subtitles (H21)
	add_child(window)
	tab_row = HBoxContainer.new()
	window.body.add_child(tab_row)
	var hint := Label.new()
	hint.name = "Hint"
	hint_label = hint
	hint.add_theme_color_override("font_color", Palette.CELL_ACID)
	window.body.add_child(hint)
	var scroll := ScrollContainer.new()
	_scroll = scroll
	scroll.custom_minimum_size = Vector2(880, 380)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.follow_focus = true
	window.body.add_child(scroll)
	# W4: the cards' tape and shadow reach past their rect; the grid keeps room for them
	# (the first row's titles were clipped by the header, critique 11).
	var pad := MarginContainer.new()
	pad.add_theme_constant_override("margin_top", UiTheme.SP_S)
	pad.add_theme_constant_override("margin_left", UiTheme.SP_XS)
	pad.add_theme_constant_override("margin_bottom", UiTheme.SP_S)
	scroll.add_child(pad)
	var grid := HFlowContainer.new()
	grid.name = "DeckGrid"
	grid.custom_minimum_size.x = GRID_WIDTH
	grid.add_theme_constant_override("h_separation", roundi(GRID_GAP))
	grid.add_theme_constant_override("v_separation", roundi(GRID_GAP))
	pad.add_child(grid)
	# Cards follow the text size (H21 #15) while a row still holds CARDS_PER_ROW of them, and
	# show what they do as pictograms.
	var ds := clampf(minf(Settings.text_scale, (GRID_WIDTH - GRID_GAP * (CARDS_PER_ROW - 1)) / (CARDS_PER_ROW * ZineCard.STICKER_SIZE.x)), 1.0, Settings.TEXT_SCALE_MAX)
	for i in deck.size():
		var card := lookup.get_content(deck[i]) as CardData
		var sticker := ZineCard.new(TextDb.t(card, "display_name") if card != null else String(deck[i]), card.ram_cost if card != null else 0,
			TextDb.t(card, "description") if card != null else "", i).scaled(ds).with_card(card)
		sticker.hotkey = ""
		# W4 (ART_BIBLE 6.3): the full face, every word; a long text grows the card.
		sticker.fit_whole = true
		var index := i
		sticker.pressed.connect(func() -> void: _on_left(index))
		sticker.inspected.connect(func() -> void: open_card(index))
		# The pad inspects with its inspect button (right click has no pad twin).
		sticker.gui_input.connect(func(ev: InputEvent) -> void:
			if ev.is_action_pressed(&"inspect"):
				open_card(index)
				sticker.accept_event())
		sticker.tooltip_text = UiTip.fold(Codex.describe(card)) if card != null else ""
		grid.add_child(sticker)
		_cards.append(sticker)
	var bottom := HBoxContainer.new()
	bottom.add_theme_constant_override("separation", 20)
	window.body.add_child(bottom)
	_bottom = bottom
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


## ANIM-4b: drag and drop inside the viewer, on a layer the screen owns (it sits over the
## viewer and outlives it, so a shred still plays as the viewer closes); in REMOVE mode the
## cards drag onto the SHRED tile beside Close.
var drops: DropLayer = null
## The SHRED tile in REMOVE mode with drops on (null otherwise).
var shred_tile: ZineCard = null


## ANIM-4b (REMOVE mode): the deck's cards become drag sources of `layer` and a SHRED tile
## beside Close takes them; a drop there is the same as selecting the card and pressing
## REMOVE. Pressing the tile is REMOVE too (nothing happens with no card selected).
func enable_drops(layer: DropLayer) -> void:
	if drops != null or layer == null:
		return
	drops = layer
	if action != "REMOVE":
		return
	shred_tile = ZineCard.new(tr("SHRED"), -1, "", 0)
	shred_tile.name = "ShredTarget"
	shred_tile.as_tile(ZineCard.Look.CARD_TILE, Palette.CELL_ACID).tile_text(Settings.text_scale)
	shred_tile.icon_kind = "shred"
	shred_tile.hotkey = ""
	shred_tile.focus_mode = Control.FOCUS_NONE
	shred_tile.custom_minimum_size = SHRED_TILE * clampf(Settings.text_scale, 1.0, SHRED_GROW_MAX)
	shred_tile.tooltip_text = UiTip.fold(tr("Drag a card here to shred it (or select it and press REMOVE)."))
	shred_tile.pressed.connect(confirm)
	_bottom.add_child(shred_tile)
	# The window keeps its height: the card grid gives the tile its room.
	_scroll.custom_minimum_size.y = maxf(SCROLL_MIN, _scroll.custom_minimum_size.y - maxf(0.0, shred_tile.custom_minimum_size.y - BOTTOM_ROOM))
	for i in _cards.size():
		drops.add_source(_cards[i], {"kind": "deck_card", "index": i, "card": deck[i], "land": "shred", "motion": &"loadout_swap"})
	drops.add_target("shred", ["deck_card"], "shred", null, DropLayer.rect_of(shred_tile))


## The SHRED tile's size at text scale 1.0, and the most it grows (px).
const SHRED_TILE := Vector2(96, 110)
const SHRED_GROW_MAX := 1.3
## The bottom row's height without the tile (the REMOVE lettering and its drips) and the
## least height the card grid keeps (px).
const BOTTOM_ROOM := 64.0
const SCROLL_MIN := 240.0
var _bottom: HBoxContainer = null
var _scroll: ScrollContainer = null


## Deck card `i`'s sticker (null when there is none).
func card(i: int) -> ZineCard:
	return _cards[i] if i >= 0 and i < _cards.size() else null


func _ready() -> void:
	# Modal for keys and the pad (H20): nothing behind it takes focus; inside the loadout
	# view, the loadout view holds focus for both tabs.
	if not (get_parent() is LoadoutView):
		UiFocus.hold(self)
	Settings.hints_changed.connect(_relabel)
	_relabel()
	# Start on the first card (not the header tabs).
	if not _cards.is_empty():
		_cards[0].grab_focus.call_deferred()
	else:
		UiFocus.focus_first.call_deferred(self)


## Key hints follow the device in use and the binds (H20).
func _relabel() -> void:
	close_button.text = ("%s %s" % [tr("Close"), Settings.hint(&"ui_cancel")]).strip_edges()
	var pick := Settings.key_text(&"ui_accept") if Settings.pad_active else tr("Left click")
	var more := Settings.key_text(&"inspect") if Settings.pad_active else tr("Right click")
	hint_label.text = (tr("%s: select a card to %s. %s: details.") % [pick, tr(action).to_lower(), more]) if action != "" else tr("%s a card for details.") % (tr("Press") if Settings.pad_active else tr("Click"))


## A header tab (the loadout view's DECK / SPINNER switch).
func add_tab(text: String, on_pressed: Callable, active: bool = false) -> void:
	var b := Button.new()
	b.text = tr(text)
	b.name = "Tab" + text
	# Same colours for both tabs: the active one is dark with a border, the other in
	# reverse video (light block, dark text) without one.
	var fg := Palette.TERMINAL_TEXT
	var bg := Palette.TERMINAL_BG
	var style := UiTheme.box(bg if active else fg, fg if active else Color.TRANSPARENT, 2 if active else 0, 12, 4)
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
		open_card(index)
		return
	select(-1 if selected == index else index)


## Selects deck index `index` (-1 clears) and shows / hides the action.
func select(index: int) -> void:
	selected = index
	for i in _cards.size():
		_cards[i].mark = (ZineCard.Mark.CROSS if action == "REMOVE" else ZineCard.Mark.CIRCLE) if i == selected else ZineCard.Mark.NONE
	if _action_button != null:
		_action_button.visible = selected >= 0


func confirm() -> void:
	if selected < 0:
		return
	# Out of the tree first: the screen behind takes focus again before the pick rebuilds it.
	var picked := selected
	close()
	card_picked.emit(picked)


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


## The card detail popup for deck index `index`: the card, its text, and Close.
func open_card(index: int) -> void:
	if _popup != null and is_instance_valid(_popup):
		_popup.queue_free()
	var card := lookup.get_content(deck[index]) as CardData
	var pop := TerminalWindow.new(tr("CARD DETAIL"), Palette.CELL_ACID)
	pop.name = "CardDetail"
	pop.position = Vector2(360, 130)
	pop.custom_minimum_size = Vector2(560, 0)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 18)
	pop.body.add_child(row)
	var big := ZineCard.new(TextDb.t(card, "display_name") if card != null else String(deck[index]), card.ram_cost if card != null else 0, TextDb.t(card, "description") if card != null else "", index).with_card(card)
	big.hotkey = ""
	big.custom_minimum_size = Vector2(170, 224)
	big.focus_mode = Control.FOCUS_NONE
	row.add_child(big)
	var info := VBoxContainer.new()
	info.custom_minimum_size.x = 320
	row.add_child(info)
	if card != null:
		for line in [tr("%s  //  %d RAM") % [TextDb.t(card, "display_name").to_upper(), card.ram_cost],
				tr(RARITY_WORDS[clampi(card.rarity, 0, 3)]) + (tr(" // exhausts") if card.exhaust else ""), Codex.describe(card)]:
			var l := Label.new()
			l.text = line
			l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			l.custom_minimum_size.x = 320
			info.add_child(l)
	var close_btn := Button.new()
	close_btn.text = tr("Close")
	close_btn.pressed.connect(func() -> void: pop.queue_free(); _popup = null)
	pop.body.add_child(close_btn)
	add_child(pop)
	_popup = pop
	UiFocus.focus_first.call_deferred(pop)
