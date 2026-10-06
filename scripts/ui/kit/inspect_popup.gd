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
	PaletteSkins.track_box(sb)  # ART-12 12s-b: the glass and edge follow the skin
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


# --- S-CARDFACE (DECK-02): the card detail, ported from art-pass 5355432 (art-m13-final) -------------------

## The card's notes beside it (px at text scale 1), the gap between them, the card at the detail's
## size (x the hand sticker) and the notes' least room before they scroll (px at scale 1).
const NOTES_WIDTH := 300.0
## B5: a card note's glyph box (px at 1.0; the tooltips' rows are 26 px at 1080p).
const NOTE_GLYPH := 18.0
const DETAIL_GAP := 24.0
const DETAIL_CARD := 2.0
const NOTES_MIN_H := 120.0
## The face's kind band in words (the band groups what a card does first; G16: not a rule of its own).
const KIND_TEXT := {"wheel": "WHEEL: it turns, nudges or flips a wheel.", "hack": "HACK: it harms the target or plants a status on it.", # TR
	"system": "SYSTEM: guards, RAM, draws and the rest."} # TR
## Rarity in words, with what the face shows for it.
const RARITY_NOTES: Array[String] = ["COMMON · one pip", "UNCOMMON · two pips", "RARE · three pips, holo die-cut", "BOSS"] # TR
## Keywords the rules text may use, and what each means (only shown when the card has the effect;
## statuses and slice kinds come from the Codex).
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


## The detail notes for `card`: its kind, its rarity and its keyword notes (never the face's own title
## or rules text: the detail-size face shows them whole).
static func card_notes(card: CardData) -> PackedStringArray:
	var out := PackedStringArray()
	for r in card_note_rows(card):
		out.append(String(r[0]))
	return out


## B5 (review section c: "Card detail notes as tooltip glyph rows"): each note with its glyph: [text, atlas glyph
## (&"" for none), its colour]: the card's first effect for its kind, the status's or slice's glyph for theirs, the
## effect's glyph for a keyword; rarity and EXHAUST carry none (their words are the note).
static func card_note_rows(card: CardData) -> Array:
	var out: Array = []
	if card == null:
		return out
	var first := card.effects[0].type if not card.effects.is_empty() and card.effects[0] != null else -1
	var notes := _card_note_texts(card)
	for i in notes.size():
		var text: String = notes[i]
		var glyph := &""
		var col := Palette.GLYPH_FILL
		if i == 0 and first >= 0:
			glyph = CodexBook.atlas_glyph("Cards", {"effect": first})
		else:
			for e in card.effects:
				if e == null:
					continue
				if e.type == RC.EffectType.APPLY_STATUS and TranslationServer.translate(String(Codex.STATUS_TEXT.get(e.status, ""))) == text:
					glyph = CodexBook.atlas_glyph("Statuses & precision", {"status": e.status})
					col = CodexBook.glyph_fill("Statuses & precision", {"status": e.status})
				elif ZineCard.EFFECT_SLICE.has(e.type) and TranslationServer.translate(String(Codex.SLICE_TYPE_TEXT.get(ZineCard.EFFECT_SLICE[e.type], ""))) == text:
					glyph = CodexBook.atlas_glyph("Slices", {"slice": ZineCard.EFFECT_SLICE[e.type]})
					col = Palette.slice_color(ZineCard.EFFECT_SLICE[e.type])
				elif KEYWORD_TEXT.has(e.type) and TranslationServer.translate(String(KEYWORD_TEXT[e.type])) == text:
					glyph = CodexBook.atlas_glyph("Cards", {"effect": e.type})
		out.append([text, glyph, col])
	return out


static func _card_note_texts(card: CardData) -> PackedStringArray:
	var out := PackedStringArray()
	if card == null:
		return out
	var probe := ZineCard.new("", 0, "", 0).with_card(card)
	out.append(TranslationServer.translate(String(KIND_TEXT[CardFace.kind_of(probe)])))
	probe.free()
	out.append(TranslationServer.translate(RARITY_NOTES[clampi(card.rarity, 0, RARITY_NOTES.size() - 1)]))
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


## The card detail for `card` (`title`, `rules` as translated for the face) at text scale `s`: the
## card at DETAIL_CARD x the hand's size (its face shows every word) beside its CARD NOTES, which scroll
## past `notes_h` px. View only.
static func card_detail(card: CardData, title: String, rules: String, s: float, notes_h: float) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.name = "CardDetailRow"
	row.add_theme_constant_override("separation", roundi(DETAIL_GAP * s))
	var big := ZineCard.new(title, card.ram_cost if card != null else 0, rules, 0).with_card(card)
	big.name = "DetailCard"
	big.hotkey = ""
	big.fit_whole = true
	big.text_scale = s
	big.custom_minimum_size = ZineCard.STICKER_SIZE * DETAIL_CARD
	big.focus_mode = Control.FOCUS_NONE
	big.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# the face's die-cut, shadow and curl reach past the card's rect: room for them (Close sat on them)
	var cut := MarginContainer.new()
	cut.name = "DetailCardRoom"
	var reach := ceili(CardFace.FACE_AT.x * big.custom_minimum_size.x / CardFace.FACE.x)
	for side in [&"margin_left", &"margin_top", &"margin_right", &"margin_bottom"]:
		cut.add_theme_constant_override(side, reach)
	cut.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	cut.add_child(big)
	row.add_child(cut)
	var notes := VBoxContainer.new()
	notes.name = "CardNotes"
	notes.add_theme_constant_override("separation", roundi(UiTheme.SP_S * s))
	var head := Label.new()
	head.name = "NotesHead"
	head.text = TranslationServer.translate("CARD NOTES")
	head.add_theme_font_override(&"font", Palette.mono())
	head.add_theme_color_override(&"font_color", Palette.CELL_ACID)
	notes.add_child(head)
	for r in card_note_rows(card):
		# B5 (review section c): each note a tooltip glyph row: its glyph in a navy tile, then the words.
		var note_row := HBoxContainer.new()
		note_row.name = "NoteRow"
		note_row.add_theme_constant_override("separation", roundi(UiTheme.SP_S * s))
		var side := NOTE_GLYPH * minf(s, CodexBook.GLYPH_SCALE_MAX)
		var tile := Control.new()
		tile.name = "Tile"
		tile.custom_minimum_size = GlyphIcon.cell_size_for(side)
		tile.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
		tile.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var edge: Color = r[2]
		tile.draw.connect(func() -> void: CodexBook.draw_tile(tile, edge))
		if StringName(r[1]) != &"":
			var g := GlyphIcon.make(StringName(r[1]), side)
			g.fill = r[2]
			tile.add_child(g)
		note_row.add_child(tile)
		var l := Label.new()
		l.theme_type_variation = UiTheme.BODY_TEXT
		l.text = String(r[0])
		UiWrap.whole_words(l)  # ART-0 F: whole words, never mid-word
		l.custom_minimum_size.x = NOTES_WIDTH * s - tile.custom_minimum_size.x - UiTheme.SP_S * s
		note_row.add_child(l)
		notes.add_child(note_row)
	var scroll := ScrollContainer.new()
	scroll.name = "NotesScroll"
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.custom_minimum_size = Vector2(NOTES_WIDTH * s, maxf(NOTES_MIN_H * s, notes_h))
	scroll.add_child(notes)
	row.add_child(scroll)
	return row
