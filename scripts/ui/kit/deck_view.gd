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


func _init(p_deck: Array[StringName], p_lookup: ContentLookup, p_title: String = "DECK", p_action: String = "") -> void:
	deck = p_deck
	lookup = p_lookup
	action = p_action
	name = "DeckView"
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.72)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	window = TerminalWindow.new("%s // %d CARDS" % [p_title, deck.size()], Palette.CELL_PINK)
	window.custom_minimum_size = Vector2(900, 540)
	window.position = Vector2(190, 70)
	add_child(window)
	tab_row = HBoxContainer.new()
	window.body.add_child(tab_row)
	var hint := Label.new()
	hint.text = ("Left click: select a card to %s. Right click: details." % action.to_lower()) if action != "" else "Click a card for details."
	hint.add_theme_color_override("font_color", Palette.CELL_ACID)
	window.body.add_child(hint)
	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(880, 380)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.follow_focus = true
	window.body.add_child(scroll)
	var grid := HFlowContainer.new()
	grid.name = "DeckGrid"
	grid.custom_minimum_size.x = 860
	grid.add_theme_constant_override("h_separation", 14)
	grid.add_theme_constant_override("v_separation", 14)
	scroll.add_child(grid)
	for i in deck.size():
		var card := lookup.get_content(deck[i]) as CardData
		var sticker := ZineCard.new(TextDb.t(card, "display_name") if card != null else String(deck[i]), card.ram_cost if card != null else 0,
			TextDb.t(card, "description") if card != null else "", i)
		sticker.hotkey = ""
		var index := i
		sticker.pressed.connect(func() -> void: _on_left(index))
		sticker.inspected.connect(func() -> void: open_card(index))
		grid.add_child(sticker)
		_cards.append(sticker)
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
	# Start on the first card (not the header tabs).
	if not _cards.is_empty():
		_cards[0].grab_focus.call_deferred()
	else:
		UiFocus.focus_first.call_deferred(self)


## A header tab (the loadout view's DECK / SPINNER switch).
func add_tab(text: String, on_pressed: Callable, active: bool = false) -> void:
	var b := Button.new()
	b.text = text
	b.name = "Tab" + text
	# The active tab shows as pressed (pink); only the other tab switches.
	b.toggle_mode = true
	b.button_pressed = active
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
	card_picked.emit(selected)
	close()


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


## The card detail popup for deck index `index`: the card, its text, and Close.
func open_card(index: int) -> void:
	if _popup != null and is_instance_valid(_popup):
		_popup.queue_free()
	var card := lookup.get_content(deck[index]) as CardData
	var pop := TerminalWindow.new("CARD DETAIL", Palette.CELL_ACID)
	pop.name = "CardDetail"
	pop.position = Vector2(360, 130)
	pop.custom_minimum_size = Vector2(560, 0)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 18)
	pop.body.add_child(row)
	var big := ZineCard.new(TextDb.t(card, "display_name") if card != null else String(deck[index]), card.ram_cost if card != null else 0, TextDb.t(card, "description") if card != null else "", index)
	big.hotkey = ""
	big.custom_minimum_size = Vector2(170, 224)
	big.focus_mode = Control.FOCUS_NONE
	row.add_child(big)
	var info := VBoxContainer.new()
	info.custom_minimum_size.x = 320
	row.add_child(info)
	if card != null:
		for line in ["%s  //  %d RAM" % [TextDb.t(card, "display_name").to_upper(), card.ram_cost],
				["Common", "Uncommon", "Rare", "Boss"][clampi(card.rarity, 0, 3)] + (" // exhausts" if card.exhaust else ""), Codex.describe(card)]:
			var l := Label.new()
			l.text = line
			l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			l.custom_minimum_size.x = 320
			info.add_child(l)
	var close_btn := Button.new()
	close_btn.text = "Close"
	close_btn.pressed.connect(func() -> void: pop.queue_free(); _popup = null)
	pop.body.add_child(close_btn)
	add_child(pop)
	_popup = pop
	UiFocus.focus_first.call_deferred(pop)
