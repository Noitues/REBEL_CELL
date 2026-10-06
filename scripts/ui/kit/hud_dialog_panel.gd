class_name HudDialogPanel
extends PanelContainer
## ART-2 2D (ART_BIBLE v2 §4.13, round 33 `abandon_dialog`): the terminal panel a modal sits
## on: dark CRT glass with a chamfered corner, a header bar `> CONFIRM // <TITLE>` and, on a
## destructive confirm, a CANNOT UNDO tag with a HARM edge. Content goes in `body`. View only.

## Header lettering and height, padding (px at text scale 1.0).
const HEADER_FONT := 14
const HEADER_H := 26.0
const PAD := 22.0
## The CANNOT UNDO tag's lettering (px at text scale 1.0).
const TAG_FONT := 12
## The pip after the tag and its gap (px at text scale 1.0).
const PIP := 6.0
const PIP_GAP := 3.0

var title: String = ""
var destructive: bool = false
var body: VBoxContainer
## ART-10 4C: the header's words are drawn on this plain child, not under the panel's CRT
## material (a custom canvas shader samples the MSDF font atlas raw: the words came out dim
## and soft). A Node2D: the container never lays it out.
var _words: Node2D


func _init(p_title: String = "", p_destructive: bool = false) -> void:
	title = p_title
	destructive = p_destructive
	name = "DialogPanel"
	material = HudSkin.crt_material()
	var s := Settings.text_scale
	var sb := StyleBoxEmpty.new()
	sb.content_margin_left = PAD * s
	sb.content_margin_right = PAD * s
	sb.content_margin_top = HEADER_H * s + PAD * 0.6 * s
	sb.content_margin_bottom = PAD * 0.8 * s
	add_theme_stylebox_override("panel", sb)
	body = VBoxContainer.new()
	body.add_theme_constant_override("separation", 8)
	add_child(body)
	_words = Node2D.new()
	_words.name = "HeaderWords"
	_words.draw.connect(_draw_words)
	add_child(_words, false, Node.INTERNAL_MODE_FRONT)
	resized.connect(_words.queue_redraw)


## The edge colour: HARM on a destructive confirm, the terminal cyan otherwise.
func edge_color() -> Color:
	return Palette.HARM if destructive else PaletteSkins.chrome(HudSkin.TERMINAL_EDGE)


## The header's words ("> CONFIRM // QUIT"), translated.
func header_text() -> String:
	return "> %s  //  %s" % [tr("CONFIRM"), title.to_upper()] if title != "" else "> %s" % tr("CONFIRM")


func _draw() -> void:
	var s := Settings.text_scale
	var r := Rect2(Vector2.ZERO, size)
	var edge := edge_color()
	HudSkin.draw_terminal_panel(self, r, edge, HudSkin.TERMINAL_BG)
	var hh := HEADER_H * s
	draw_rect(Rect2(Vector2(1.0, 1.0), Vector2(size.x - HudSkin.CHAMFER * s - 2.0, hh)), Color(edge, 0.12))
	draw_line(Vector2(0.0, hh), Vector2(size.x, hh), Color(edge, 0.6), 1.0)


## The header's words and the CANNOT UNDO tag (on `_words`, unshaded).
func _draw_words() -> void:
	var s := Settings.text_scale
	var edge := edge_color()
	var hh := HEADER_H * s
	var f := HudSkin.mono()
	var hf := roundi(HEADER_FONT * s)
	_words.draw_string(f, Vector2(PAD * 0.5 * s, (hh + f.get_ascent(hf) - f.get_descent(hf)) * 0.5), header_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, hf, edge.lightened(0.2))
	if destructive:
		var tf := roundi(TAG_FONT * s)
		var tag := tr("CANNOT UNDO")
		var tw := f.get_string_size(tag, HORIZONTAL_ALIGNMENT_LEFT, -1, tf).x
		var tr_ := Rect2(Vector2(size.x - HudSkin.CHAMFER * s - tw - 20.0 * s, (hh - tf - 6.0) * 0.5), Vector2(tw + 10.0 * s, tf + 6.0))
		_words.draw_rect(tr_, edge, false, 1.0)
		# Round 33: a lit pip after the tag (term_panel's header square).
		_words.draw_rect(Rect2(Vector2(tr_.end.x + PIP_GAP * s, (hh - PIP * s) * 0.5), Vector2(PIP, PIP) * s), edge)
		_words.draw_string(f, tr_.position + Vector2(5.0 * s, 3.0 + f.get_ascent(tf)), tag, HORIZONTAL_ALIGNMENT_LEFT, -1, tf, edge)
