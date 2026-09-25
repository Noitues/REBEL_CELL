class_name DeckView
extends Control
## Deck viewer (modal): every card in the operative's deck as its sticker, in deck order.
## Picking a card opens its detail popup (big sticker, cost, text, codex line, upgrades).
## In pick mode (`pick_label` set, e.g. "REMOVE FOR 50") the popup carries that action and
## `card_picked(index)` fires; otherwise it is look-only. Emits `closed` on Back / Esc.
## Views only: the scene decides what a pick means.

signal card_picked(index: int)
signal closed

var deck: Array[StringName] = []
var lookup: ContentLookup
var pick_label: String = ""
var _grid: HFlowContainer
var _popup: Control = null


func _init(p_deck: Array[StringName], p_lookup: ContentLookup, p_title: String = "DECK", p_pick_label: String = "") -> void:
	deck = p_deck
	lookup = p_lookup
	pick_label = p_pick_label
	name = "DeckView"
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.72)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var win := TerminalWindow.new("%s // %d CARDS" % [p_title, deck.size()], Palette.CELL_PINK)
	win.custom_minimum_size = Vector2(900, 500)
	win.position = Vector2(190, 90)
	add_child(win)
	if pick_label != "":
		win.body.add_child(_hint("Pick a card, then confirm."))
	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(880, 400)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.follow_focus = true
	win.body.add_child(scroll)
	_grid = HFlowContainer.new()
	_grid.name = "DeckGrid"
	_grid.custom_minimum_size.x = 860
	_grid.add_theme_constant_override("h_separation", 14)
	_grid.add_theme_constant_override("v_separation", 14)
	scroll.add_child(_grid)
	for i in deck.size():
		var card := lookup.get_content(deck[i]) as CardData
		var sticker := ZineCard.new(TextDb.t(card, "display_name") if card != null else String(deck[i]), card.ram_cost if card != null else 0,
			TextDb.t(card, "description") if card != null else "", i)
		sticker.hotkey = ""
		var index := i
		sticker.pressed.connect(func() -> void: open_card(index))
		_grid.add_child(sticker)
	var back := Button.new()
	back.text = "Back [Esc]"
	back.pressed.connect(close)
	win.body.add_child(back)


func _ready() -> void:
	UiFocus.focus_first.call_deferred(self)


func _hint(text: String) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_color_override("font_color", Palette.CELL_ACID)
	return l


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


## The card detail popup for deck index `index`.
func open_card(index: int) -> void:
	if _popup != null and is_instance_valid(_popup):
		_popup.queue_free()
	var card := lookup.get_content(deck[index]) as CardData
	var pop := TerminalWindow.new("CARD DETAIL", Palette.CELL_ACID)
	pop.name = "CardDetail"
	pop.position = Vector2(390, 140)
	pop.custom_minimum_size = Vector2(500, 0)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 18)
	pop.body.add_child(row)
	var big := ZineCard.new(TextDb.t(card, "display_name") if card != null else String(deck[index]), card.ram_cost if card != null else 0, TextDb.t(card, "description") if card != null else "", index)
	big.hotkey = ""
	big.custom_minimum_size = Vector2(170, 224)
	big.focus_mode = Control.FOCUS_NONE
	row.add_child(big)
	var info := VBoxContainer.new()
	info.custom_minimum_size.x = 280
	row.add_child(info)
	for line in _detail_lines(card):
		var l := Label.new()
		l.text = line
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size.x = 280
		info.add_child(l)
	var actions := HBoxContainer.new()
	pop.body.add_child(actions)
	if pick_label != "":
		var pick := Button.new()
		pick.text = pick_label
		pick.theme_type_variation = &"HotButton"
		pick.pressed.connect(func() -> void: card_picked.emit(index); close())
		actions.add_child(pick)
	var back := Button.new()
	back.text = "Back"
	back.pressed.connect(func() -> void: pop.queue_free(); _popup = null)
	actions.add_child(back)
	add_child(pop)
	_popup = pop
	UiFocus.focus_first.call_deferred(pop)


func _detail_lines(card: CardData) -> PackedStringArray:
	var out := PackedStringArray()
	if card == null:
		out.append("Unknown card.")
		return out
	out.append("%s  //  %d RAM" % [TextDb.t(card, "display_name").to_upper(), card.ram_cost])
	out.append(["Common", "Uncommon", "Rare", "Boss"][clampi(card.rarity, 0, 3)] + (" // exhausts" if card.exhaust else ""))
	out.append(Codex.describe(card))
	out.append("UPGRADES: none (cards have no upgraded form yet)")
	return out
