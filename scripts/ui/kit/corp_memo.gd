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

var corp_name: String = ""
var corp_colour: Color = Palette.CORP_SOLACE
var text_scale: float = 1.0
var body: VBoxContainer
var sheet: CorpPaperPanel
var margins: MarginContainer


func _init(p_corp: String = "", p_colour: Color = Palette.CORP_SOLACE, ts: float = 1.0) -> void:
	name = "CorpMemo"
	corp_name = p_corp
	corp_colour = p_colour
	text_scale = ts
	rotation_degrees = TILT_DEG
	sheet = CorpPaperPanel.new()
	sheet.name = "Paper"
	sheet.corp_name = p_corp.to_upper()
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
	margins.add_theme_constant_override(&"margin_top", roundi(CorpPaperPanel.LETTERHEAD_H + (TITLE_PX + META_PX) * 1.7 * ts + PAD.y * ts))
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


func _get_minimum_size() -> Vector2:
	return margins.get_combined_minimum_size() if margins != null else Vector2.ZERO


## The tape, INTERNAL MEMO and the routing line, over the sheet under its letterhead.
func _draw_head(on: Control) -> void:
	var s := text_scale
	var r := Rect2(Vector2.ZERO, size)
	on.draw_rect(Rect2(Vector2((r.size.x - TAPE.x * s) * 0.5, -TAPE.y * s * 0.45), TAPE * s), Palette.NOTE_TAPE)
	var paper := Palette.paper_bold()
	var ts := roundi(TITLE_PX * s)
	var y := CorpPaperPanel.LETTERHEAD_H + 6.0 * s + paper.get_ascent(ts)
	on.draw_string(paper, Vector2(PAD.x * s, y), tr("INTERNAL MEMO"), HORIZONTAL_ALIGNMENT_LEFT, -1, ts, Palette.PAPER_TYPE_INK)
	var ms := roundi(META_PX * s)
	y += paper.get_descent(ts) + Palette.paper().get_ascent(ms) + 4.0 * s
	on.draw_string(Palette.paper(), Vector2(PAD.x * s, y), tr("TO: ALL TIER LEADS    FROM: %s    REF: INTERNAL") % corp_name.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, r.size.x - PAD.x * 2.0 * s, ms, Palette.TEXT_LO)
