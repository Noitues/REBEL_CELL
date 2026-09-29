class_name InspectPopup
extends PanelContainer
## The inspect text for keyboard and pad players (H20): what a tooltip shows the mouse,
## shown beside the inspected thing until the player moves on. Terminal glass, clean
## system text. View only.

const WIDTH := 300.0
const MARGIN := 8.0

var label: RichTextLabel


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false
	var sb := StyleBoxFlat.new()
	sb.bg_color = Palette.TERMINAL_BG
	sb.border_color = Palette.TERMINAL_EDGE
	sb.set_border_width_all(1)
	sb.set_content_margin_all(MARGIN)
	add_theme_stylebox_override("panel", sb)
	label = RichTextLabel.new()
	label.fit_content = true
	label.bbcode_enabled = false
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_color_override("default_color", Palette.TERMINAL_TEXT)
	add_child(label)


## Shows `text` beside `target` (global rect), kept inside `bounds` (global).
func show_for(text: String, target: Rect2, bounds: Rect2) -> void:
	if text == "":
		hide()
		return
	label.text = text
	label.custom_minimum_size.x = WIDTH * Settings.text_scale
	reset_size()
	var sz := get_combined_minimum_size()
	var pos := Vector2(target.end.x + MARGIN, target.position.y)
	if pos.x + sz.x > bounds.end.x:
		pos.x = target.position.x - sz.x - MARGIN
	pos.x = clampf(pos.x, bounds.position.x, maxf(bounds.position.x, bounds.end.x - sz.x))
	pos.y = clampf(pos.y, bounds.position.y, maxf(bounds.position.y, bounds.end.y - sz.y))
	global_position = pos.floor()
	visible = true


func text() -> String:
	return label.get_parsed_text() if visible else ""


# --- W4 the card detail (ART_BIBLE 6.3; critique 54) --------------------------------------------
# The card at detail size (PAPER, its own component, taped beside the glass) shows the
# whole 3:2 illustration and every word of its rules; a GLASS notes panel beside it holds
# only what the face doesn't say: the card type and its stock, the rarity, and what the
# face's keywords mean. The face's title and rules text are never repeated (critique 54).

## The notes panel's width (columns of the body face at scale 1.0: ART_BIBLE 6.8 keeps
## tooltips 26-36 columns; the notes are a tooltip's big brother) and its gap to the card.
const NOTES_WIDTH := 300.0
const DETAIL_GAP := 24.0
## Keywords the rules text may use, and what each means (only shown when the card has the
## effect; statuses and slice kinds come from the Codex).
const KEYWORD_TEXT := {
	RC.EffectType.SPIN: "SPIN: turns the wheel clockwise by the ticks shown (counter-clockwise when negative).", # TR
	RC.EffectType.NUDGE: "NUDGE: moves a ring one tick either way; resistance can refuse it.", # TR
	RC.EffectType.FLIP: "FLIP: mirrors the wheel, so each slice swaps with the one opposite.", # TR
	RC.EffectType.RESPIN: "RESPIN: the wheel lands on a random tick.", # TR
	RC.EffectType.FREEZE: "FREEZE: the wheel skips its next respin.", # TR
	RC.EffectType.SNAP_TO_CENTER: "SNAP: the ring moves to the nearest slice centre, a PERFECT aim.", # TR
	RC.EffectType.MODIFY_RESISTANCE: "RESISTANCE: how many nudges a wheel shrugs off each turn.", # TR
	RC.EffectType.HUB_BREACH: "BREACH: the hub core's bonus and resistance are off while it lasts.", # TR
	RC.EffectType.GAIN_RAM: "RAM: what cards cost to play; it refills each turn.", # TR
	RC.EffectType.DRAIN_RAM: "RAM: what cards cost to play; it refills each turn.", # TR
	RC.EffectType.DRAW_CARDS: "DRAW: cards come from your pile to your hand at once.", # TR
	RC.EffectType.DOUBLE_NUDGE_CARDS: "NUDGE CARDS: every card whose effect is a nudge.", # TR
}
const EXHAUST_TEXT := "EXHAUST: once played, the card leaves your deck for this fight." # TR
const RARITY_WORDS: Array[String] = ["COMMON · photocopy stock", "UNCOMMON · glossy sticker", "RARE · holographic foil", "BOSS · holographic foil"] # TR


## The detail notes for `card`: its type row, rarity row and keyword notes (never the
## face's own title or rules text; tests check).
static func card_notes(card: CardData) -> PackedStringArray:
	var out := PackedStringArray()
	if card == null:
		return out
	var t := CardArt.type_of(card)
	out.append("%s (%s)" % [TranslationServer.translate(String(CardArt.TYPE_WORDS[t])), TranslationServer.translate(String(CardArt.TYPE_STOCK_WORDS[t]))])
	out.append(TranslationServer.translate(String(CardArt.TYPE_TEXT[t])))
	out.append(TranslationServer.translate(RARITY_WORDS[clampi(card.rarity, 0, RARITY_WORDS.size() - 1)]))
	var seen := {}
	for e in card.effects:
		if e == null:
			continue
		var note := ""
		if e.type == RC.EffectType.APPLY_STATUS:
			note = String(Codex.STATUS_TEXT.get(e.status, ""))
		elif ZineCard.EFFECT_SLICE.has(e.type) and e.type != RC.EffectType.DEAL_DAMAGE:
			note = String(Codex.SLICE_TYPE_TEXT.get(ZineCard.EFFECT_SLICE[e.type], ""))
		elif KEYWORD_TEXT.has(e.type):
			note = String(KEYWORD_TEXT[e.type])
		if note != "" and not seen.has(note):
			seen[note] = true
			out.append(TranslationServer.translate(note))
	if card.exhaust:
		out.append(TranslationServer.translate(EXHAUST_TEXT))
	return out


## The card detail for `card` (title `title`, rules `rules` as translated for the face) at
## text scale `s`, fitting `room` (px): the detail-size card and its notes panel side by
## side. `on_close` runs when its Close is pressed.
static func card_detail(card: CardData, title: String, rules: String, s: float, room: Vector2, on_close: Callable) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.name = "CardDetail"
	row.add_theme_constant_override("separation", roundi(DETAIL_GAP * s))
	var notes_w := NOTES_WIDTH * s
	var card_room := Vector2(room.x - notes_w - DETAIL_GAP * s, room.y)
	var big := ZineCard.new(title, card.ram_cost if card != null else 0, rules, 0).with_card(card).as_detail(s, card_room)
	big.name = "DetailCard"
	big.focus_mode = Control.FOCUS_NONE
	big.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	# A long rules text grows the card (tall mode): the card scrolls inside its room.
	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.custom_minimum_size = Vector2(big.custom_minimum_size.x + UiTheme.SP_S * s, minf(room.y, big.custom_minimum_size.y + UiTheme.SP_S * s))
	var pad := MarginContainer.new()
	for side in ["margin_top", "margin_left"]:
		pad.add_theme_constant_override(side, UiTheme.SP_XS)
	pad.add_child(big)
	scroll.add_child(pad)
	row.add_child(scroll)
	var win := TerminalWindow.new(TranslationServer.translate("CARD NOTES"), Palette.CELL_ACID)
	win.name = "CardNotes"
	win.custom_minimum_size.x = notes_w
	win.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	for line in card_notes(card):
		var l := Label.new()
		l.theme_type_variation = UiTheme.BODY_TEXT
		l.text = line
		l.autowrap_mode = TextServer.AUTOWRAP_WORD
		l.custom_minimum_size.x = notes_w - UiTheme.PANEL_PAD_H * 2.0
		win.body.add_child(l)
	var close_btn := Button.new()
	close_btn.name = "Close"
	close_btn.text = TranslationServer.translate("Close")
	close_btn.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	close_btn.pressed.connect(on_close)
	win.body.add_child(close_btn)
	row.add_child(win)
	return row


## The detail card inside a detail row (tests, the scene).
static func detail_card(row: Control) -> ZineCard:
	return row.find_child("DetailCard", true, false) as ZineCard
