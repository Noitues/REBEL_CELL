class_name CorpMemo
extends Control
## ART-9 4A (ART_BIBLE v2 §1.2 "Corp paper", §4.11 "a corp-speaker event gets an intercepted memo
## taped over the Terminal"; round 31 `event_screen_memo`): an intercepted corp memo, slightly
## askew and taped at the top. The sheet is 1B's CorpPaperPanel (paper stock, the corp's
## letterhead over its rule, the CLASSIFIED stamp); on it INTERNAL MEMO and a TO / FROM / REF line
## in Courier Prime, then the body (the event's story: `body` holds its RichTextLabel). View only.

const TILT_DEG := -1.6
const PAD := Vector2(26, 18)
const TITLE_PX := 20
const META_PX := 12
const TAPE := Vector2(110, 22)
## The stamp word (a key, translated where set).
const STAMP := "CLASSIFIED" # TR
## Parity EVT-03 (round 31 `event_screen_memo`): DISPATCH's story on the same paper as a voice
## transcript: its head, its routing line and the concept's stamp (keys).
const TRANSCRIPT_HEAD := "VOICE TRANSCRIPT" # TR
const TRANSCRIPT_ROUTING := "TO: CELL OPERATIVE    FROM: DISPATCH    REF: VOICE LOG" # TR
const TRANSCRIPT_STAMP := "DO NOT FORWARD" # TR
## The memo's head and routing line (keys; set by `as_transcript`).
const MEMO_HEAD := "INTERNAL MEMO" # TR
var head_word: String = MEMO_HEAD
var routing: String = ""

var corp_name: String = ""
var corp_colour: Color = Palette.CORP_SOLACE
var text_scale: float = 1.0
var body: VBoxContainer
var sheet: CorpPaperPanel
var margins: MarginContainer


## A memo from corporation `p_corp` (its display name, on the routing line) in `p_colour` at
## text scale `ts`; M14 FOLLOW-UP: `p_letterhead` is its letterhead name
## (`CorpPaperPanel.letterhead_of`), "" to letter the display name.
func _init(p_corp: String = "", p_colour: Color = Palette.CORP_SOLACE, ts: float = 1.0, p_letterhead: String = "") -> void:
	name = "CorpMemo"
	corp_name = p_corp
	corp_colour = p_colour
	text_scale = ts
	rotation_degrees = TILT_DEG
	sheet = CorpPaperPanel.new()
	sheet.name = "Paper"
	sheet.corp_name = p_corp.to_upper()
	sheet.letterhead_name = p_letterhead.to_upper()
	# M14 FOLLOW-UP: the letterhead grows with the memo's text (as the raid papers'), so its name
	# stands whole on the sheet at 2.0 (it rose over the sheet's top edge, under the tape).
	sheet.text_k = ts
	sheet.head_h = head_h()
	sheet.corp_color = p_colour
	sheet.stamp = tr(STAMP)
	sheet.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(sheet)
	sheet.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	# the words on the sheet: a margin box (the memo is as tall as its words)
	margins = MarginContainer.new()
	margins.name = "Margins"
	margins.mouse_filter = Control.MOUSE_FILTER_IGNORE
	margins.add_theme_constant_override(&"margin_left", roundi(PAD.x * ts))
	margins.add_theme_constant_override(&"margin_right", roundi(PAD.x * ts))
	margins.add_theme_constant_override(&"margin_top", top_margin(1))
	margins.add_theme_constant_override(&"margin_bottom", roundi(CorpPaperPanel.STAMP_SLOT.y + PAD.y * ts))
	add_child(margins)
	margins.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margins.minimum_size_changed.connect(update_minimum_size)
	body = VBoxContainer.new()
	body.name = "MemoBody"
	margins.add_child(body)
	var over := Control.new()
	over.name = "MemoHead"
	over.mouse_filter = Control.MOUSE_FILTER_IGNORE
	over.draw.connect(_draw_head.bind(over))
	add_child(over)
	over.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	resized.connect(func() -> void: pivot_offset = size * 0.5)
	# M14 FIX-2: the routing line wraps to the sheet's width; the words start under its lines.
	resized.connect(_fit_routing)


## M14 FOLLOW-UP: the letterhead's height (px) at the memo's text scale.
func head_h() -> float:
	return CorpPaperPanel.LETTERHEAD_H * text_scale


## M14 FIX-2: the margin over the memo's words (px) under `route_lines` routing lines.
func top_margin(route_lines: int) -> int:
	var extra := maxi(0, route_lines - 1) * Palette.paper().get_height(meta_px())
	return roundi(head_h() + (TITLE_PX + META_PX) * 1.7 * text_scale + PAD.y * text_scale + extra)


## M14 FIX-2: the routing line's lettering (px): META_PX x the memo's text scale, never under
## the 1.0 size.
func meta_px() -> int:
	return maxi(META_PX, roundi(META_PX * text_scale))


## The routing line's words (translated): the transcript's, else the corp's TO / FROM / REF.
func routing_text() -> String:
	return tr(routing) if routing != "" else tr("TO: ALL TIER LEADS    FROM: %s    REF: INTERNAL") % corp_name.to_upper()


## The width (px) the routing line may take on the sheet (INF before the memo has a width).
func routing_room() -> float:
	var w := maxf(size.x, custom_minimum_size.x)
	return w - PAD.x * 2.0 * text_scale if w > 0.0 else INF


## M14 FIX-2: the routing line as lettered, one string per line, never smaller than at 1.0:
## it wraps at its fields, then folds a field too long for a line at its words.
func routing_lines() -> PackedStringArray:
	return wrap_routing(Palette.paper(), routing_text(), meta_px(), routing_room())


## The gap between the routing line's fields (TO / FROM / REF).
const FIELD_GAP := "    "


## M14 FIX-2: `text` (fields apart by FIELD_GAP) in lines no wider than `room` at `px`: whole
## fields packed greedily, a field wider than the room folded at its spaces (a word wider than
## the room stands alone on its line: never cut, never shrunk).
static func wrap_routing(f: Font, text: String, px: int, room: float) -> PackedStringArray:
	var out := PackedStringArray()
	var line := ""
	for field in text.split(FIELD_GAP, false):
		var word_run := field.strip_edges()
		if word_run == "":
			continue
		var joined := word_run if line == "" else line + FIELD_GAP + word_run
		if _width(f, joined, px) <= room:
			line = joined
			continue
		if line != "":
			out.append(line)
			line = ""
		if _width(f, word_run, px) <= room:
			line = word_run
			continue
		for word in word_run.split(" ", false):
			var with_word := word if line == "" else line + " " + word
			if line != "" and _width(f, with_word, px) > room:
				out.append(line)
				line = word
			else:
				line = with_word
		out.append(line)
		line = ""
	if line != "":
		out.append(line)
	return out


static func _width(f: Font, s: String, px: int) -> float:
	return f.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x


## M14 FIX-2: the words start under every routing line (the memo grows with them).
func _fit_routing() -> void:
	if margins == null:
		return
	var top := top_margin(routing_lines().size())
	if margins.get_theme_constant(&"margin_top") != top:
		margins.add_theme_constant_override(&"margin_top", top)
	var head := get_node_or_null(^"MemoHead") as Control
	if head != null:
		head.queue_redraw()


func _get_minimum_size() -> Vector2:
	return margins.get_combined_minimum_size() if margins != null else Vector2.ZERO


## Parity EVT-03: the sheet as DISPATCH's voice transcript (VOICE TRANSCRIPT, the Cell's routing
## line, DO NOT FORWARD) instead of a corp's internal memo.
func as_transcript() -> CorpMemo:
	head_word = TRANSCRIPT_HEAD
	routing = TRANSCRIPT_ROUTING
	sheet.stamp = tr(TRANSCRIPT_STAMP)
	_fit_routing()
	return self


## The tape, INTERNAL MEMO and the routing line, over the sheet under its letterhead.
func _draw_head(on: Control) -> void:
	var s := text_scale
	var r := Rect2(Vector2.ZERO, size)
	on.draw_rect(Rect2(Vector2((r.size.x - TAPE.x * s) * 0.5, -TAPE.y * s * 0.45), TAPE * s), Palette.NOTE_TAPE)
	var paper := Palette.paper_bold()
	var ts := roundi(TITLE_PX * s)
	var y := head_h() + 6.0 * s + paper.get_ascent(ts)
	HighContrast.draw_text(on, paper, Vector2(PAD.x * s, y), tr(head_word), HORIZONTAL_ALIGNMENT_LEFT, -1, ts, Palette.PAPER_TYPE_INK)
	var ms := meta_px()
	var meta := Palette.paper()
	y += paper.get_descent(ts) + meta.get_ascent(ms) + 4.0 * s
	# M14 FIX-2: wrapped and folded to the sheet's width (it was clipped at 2.0), never under 1.0.
	for line in routing_lines():
		HighContrast.draw_text(on, meta, Vector2(PAD.x * s, y), line, HORIZONTAL_ALIGNMENT_LEFT, -1, ms, Palette.TEXT_LO)
		y += meta.get_height(ms)
