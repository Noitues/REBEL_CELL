class_name CorpPaperPanel
extends Control
## The corp paper panel (ART-1 1B; ART_BIBLE v2 §1.2 "Corp paper": intercepted corp documents:
## the raid work order, the after-action raid report, the campaign audit dossier, seizure
## notices, the operative dossier on the map, event memos from corp speakers; never the
## Cell's own UI). Paper stock (`shaders/kit/corp_paper.gdshader`, scales like a 9-patch),
## an IBM Plex Sans Condensed Medium letterhead in the corp colour over a rule, Courier Prime
## fields (`add_field`), and a stamp slot for an Anton stamp (CLASSIFIED, CASE CLOSED,
## PROCESSED). Static: no motion. A view only.

const SHADER := preload("res://shaders/kit/corp_paper.gdshader")
const LETTERHEAD_H := 46.0
const RULE_PX := 2.0
const STAMP_TILT_DEG := -9.0
const STAMP_SLOT := Vector2(200, 56)
## The stamp box round its word (px, both sides together).
const STAMP_BOX_PAD := Vector2(16, 4)
const STAMP_LINE := 3.0
const SHADOW_OFFSET := Vector2(3, 5)

@export var corp_name: String = "SOLACE BIOSYSTEMS":
	set(v):
		corp_name = v
		queue_redraw()
@export var corp_color: Color = Palette.CORP_SOLACE:
	set(v):
		corp_color = v
		queue_redraw()
## The stamp word drawn in the slot ("" for none).
@export var stamp: String = "CLASSIFIED":
	set(v):
		stamp = v
		if stamp_slot != null:
			stamp_slot.queue_redraw()
@export var seed: int = 3
## D24: room above the letterhead (px) for a paper clip's bite; 0 for papers without a clip.
var top_pad: float = 0.0:
	set(v):
		top_pad = v
		queue_redraw()
## M14 BIG-TEXT b (art director, 4a): the letterhead's height (px; LETTERHEAD_H unless a sheet
## scales it), the room at its right the corp name keeps clear of (px from the sheet's right
## edge: a seal), and the text scale its name is lettered at (< 0: the player's).
var head_h: float = LETTERHEAD_H:
	set(v):
		head_h = v
		queue_redraw()
var name_reserve: float = 0.0:
	set(v):
		name_reserve = v
		queue_redraw()
var text_k: float = -1.0

var content: VBoxContainer = null
var stamp_slot: Control = null

var _paper: Control = null
var _mat: ShaderMaterial = null


func _init() -> void:
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	_paper = Control.new()
	_paper.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_paper.material = _mat
	_paper.draw.connect(func() -> void: _paper.draw_rect(Rect2(Vector2.ZERO, size), Palette.NO_TINT))
	add_child(_paper, false, Node.INTERNAL_MODE_FRONT)
	var head := Control.new()
	head.mouse_filter = Control.MOUSE_FILTER_IGNORE
	head.draw.connect(func() -> void: _draw_letterhead(head))
	add_child(head, false, Node.INTERNAL_MODE_FRONT)
	head.set_anchors_preset(Control.PRESET_FULL_RECT)
	_paper.set_anchors_preset(Control.PRESET_FULL_RECT)
	content = VBoxContainer.new()
	content.name = "Fields"
	content.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(content, false, Node.INTERNAL_MODE_FRONT)
	stamp_slot = Control.new()
	stamp_slot.name = "StampSlot"
	stamp_slot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	stamp_slot.draw.connect(_draw_stamp)
	add_child(stamp_slot, false, Node.INTERNAL_MODE_BACK)
	var clip_layer := Control.new()
	clip_layer.name = "ClipLayer"
	clip_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	clip_layer.draw.connect(func() -> void:
		if clip:
			PaperLie.draw_clip(clip_layer, Rect2(Vector2.ZERO, size), get_viewport_rect().size.y if is_inside_tree() else PaperLie.BOARD_H))
	add_child(clip_layer, false, Node.INTERNAL_MODE_BACK)
	clip_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	resized.connect(clip_layer.queue_redraw)


func _ready() -> void:
	resized.connect(_layout)
	_layout()


## The typewriter face (Courier Prime, 1A's `Palette.paper()`).
static func courier() -> Font:
	return Palette.paper()


## Adds a `LABEL: value` field line in Courier Prime.
func add_field(label: String, value: String) -> Label:
	var l := Label.new()
	l.text = "%s: %s" % [label, value]
	l.add_theme_font_override(&"font", courier())
	l.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.BODY))
	l.add_theme_color_override(&"font_color", Palette.PAPER_TYPE_INK)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD
	content.add_child(l)
	return l


func _layout() -> void:
	_mat.set_shader_parameter(&"panel", Vector4(0, 0, size.x, size.y))
	_mat.set_shader_parameter(&"stock", Palette.PAPER)
	_mat.set_shader_parameter(&"fibre", Palette.KRAFT_FIBRE)
	_mat.set_shader_parameter(&"seed", float(seed))
	content.position = Vector2(UiTheme.SP_L, top_pad + head_h + UiTheme.SP_M)
	content.size = Vector2(size.x - UiTheme.SP_L * 2.0, maxf(size.y - top_pad - head_h - UiTheme.SP_L * 2.0, 0.0))
	stamp_slot.size = STAMP_SLOT
	stamp_slot.position = Vector2(size.x - STAMP_SLOT.x - UiTheme.SP_M, size.y - STAMP_SLOT.y - UiTheme.SP_M)
	# Parity fix (overlap defects, RAID-11): a stamp wider than its slot (big text) stays on
	# the paper, its right edge SP_M in from the paper's.
	var half := stamp_extent(stamp) * 0.5
	var c := (stamp_slot.position + STAMP_SLOT * 0.5).min(size - Vector2(UiTheme.SP_M, UiTheme.SP_M) - half)
	stamp_slot.position = c - STAMP_SLOT * 0.5
	queue_redraw()
	_paper.queue_redraw()


## The drop shadow under the sheet. B5 (review D24): the soft 6 px contact shadow of paper lying on the world
## (PaperLie), in place of the hard offset copy.
func _draw() -> void:
	PaperLie.draw_contact_shadow(self, Rect2(Vector2.ZERO, size), get_viewport_rect().size.y if is_inside_tree() else PaperLie.BOARD_H)


## B5 (D24): the sheet wears the concepts' paper clip (top right), over its letterhead and fields.
@export var clip: bool = true:
	set(v):
		clip = v
		if stamp_slot != null:
			stamp_slot.queue_redraw()


## The letterhead (corp name over a rule in the corp colour), on its own layer over the paper.
## BIG-TEXT b (4a): the name fits the width left of `name_reserve` (`letterhead_fit`).
func _draw_letterhead(on: Control) -> void:
	var font := Palette.body_medium()
	var fit := letterhead_fit()
	var px: int = fit["px"]
	var lines: PackedStringArray = fit["lines"]
	var base := top_pad + head_h - UiTheme.SP_M
	for i in lines.size():
		var y := base - font.get_height(px) * float(lines.size() - 1 - i)
		on.draw_string(font, Vector2(UiTheme.SP_L, y), lines[i], HORIZONTAL_ALIGNMENT_LEFT, -1, px, corp_color.darkened(0.35))
	on.draw_rect(Rect2(UiTheme.SP_L, top_pad + head_h - RULE_PX - UiTheme.SP_XS, size.x - UiTheme.SP_L * 2.0, RULE_PX), corp_color.darkened(0.35))


## BIG-TEXT b (4a): the width (px) the corp name may take: from the letterhead's left margin to
## `name_reserve` from the right edge (the side margin at least).
func name_width() -> float:
	return size.x - UiTheme.SP_L - maxf(UiTheme.SP_L, name_reserve)


## BIG-TEXT b (4a): the corp name as the letterhead draws it: {"px": int, "lines": PackedStringArray}.
func letterhead_fit() -> Dictionary:
	var k := text_k if text_k > 0.0 else Settings.text_scale
	return fit_name(Palette.body_medium(), corp_name, UiTheme.font_px_at(UiTheme.LABEL, k), UiTheme.font_px_at(UiTheme.LABEL, 1.0),
		name_width(), head_h - UiTheme.SP_M)


## BIG-TEXT b (art director, 4a): `name` in `width` px: one line at `max_px`, else smaller down to
## `min_px` (the size at text 1.0, never below); else two lines (the words split where the first
## line is fullest) at the largest size both fit and stand in `room` px above the last baseline;
## else ellipsized at `min_px` (two lines when they stand in the room). Pure.
static func fit_name(font: Font, name: String, max_px: int, min_px: int, width: float, room: float) -> Dictionary:
	var lo := mini(min_px, max_px)
	for px in range(max_px, lo - 1, -1):
		if font.get_string_size(name, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x <= width:
			return {"px": px, "lines": PackedStringArray([name])}
	var words := name.split(" ", false)
	if words.size() > 1:
		for px in range(max_px, lo - 1, -1):
			if font.get_height(px) + font.get_ascent(px) > room:
				continue
			var two := _wrap_two(font, words, px, width)
			if font.get_string_size(two[1], HORIZONTAL_ALIGNMENT_LEFT, -1, px).x <= width and font.get_string_size(two[0], HORIZONTAL_ALIGNMENT_LEFT, -1, px).x <= width:
				return {"px": px, "lines": two}
	var lines := PackedStringArray([name])
	if words.size() > 1 and font.get_height(lo) + font.get_ascent(lo) <= room:
		lines = _wrap_two(font, words, lo, width)
	for i in lines.size():
		lines[i] = ellipsize(font, lines[i], lo, width)
	return {"px": lo, "lines": lines}


## The words split in two lines, the first holding as many as fit `width` at `px` (at least one).
static func _wrap_two(font: Font, words: PackedStringArray, px: int, width: float) -> PackedStringArray:
	var n := 1
	while n < words.size() - 1 and font.get_string_size(" ".join(words.slice(0, n + 1)), HORIZONTAL_ALIGNMENT_LEFT, -1, px).x <= width:
		n += 1
	return PackedStringArray([" ".join(words.slice(0, n)), " ".join(words.slice(n))])


## The ellipsis a cut name ends in.
const ELLIPSIS := "…"


## `text` cut to fit `width` at `px`, ending in an ellipsis when cut. Pure.
static func ellipsize(font: Font, text: String, px: int, width: float) -> String:
	if font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x <= width:
		return text
	var t := text
	while t.length() > 1 and font.get_string_size(t.strip_edges() + ELLIPSIS, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x > width:
		t = t.left(t.length() - 1)
	return t.strip_edges() + ELLIPSIS


## Parity fix (overlap defects, RAID-02 / RAID-11): the bounding size (px) of the stamp for
## `word` as drawn (its box, tilted): what a sheet keeps clear of its words.
static func stamp_extent(word: String) -> Vector2:
	if word == "":
		return Vector2.ZERO
	var sz := Palette.display().get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.font_px(UiTheme.HEADING))
	var box := sz + STAMP_BOX_PAD + Vector2(STAMP_LINE, STAMP_LINE)
	var a := absf(deg_to_rad(STAMP_TILT_DEG))
	return Vector2(box.x * cos(a) + box.y * sin(a), box.x * sin(a) + box.y * cos(a))


## How far above the sheet's foot the stamp for `word` reaches (px): a sheet's words end
## above it.
static func stamp_reach(word: String) -> float:
	var half := stamp_extent(word).y * 0.5
	return UiTheme.SP_M + maxf(STAMP_SLOT.y * 0.5, half) + half


## The stamp's bounding rect as drawn, in the panel's px (empty without a stamp).
func stamp_rect() -> Rect2:
	if stamp == "" or stamp_slot == null:
		return Rect2()
	var e := stamp_extent(stamp)
	return Rect2(stamp_slot.position + STAMP_SLOT * 0.5 - e * 0.5, e)


func _draw_stamp() -> void:

	if stamp == "":
		return
	var font := Palette.display()
	var px := UiTheme.font_px(UiTheme.HEADING)
	var sz := font.get_string_size(stamp, HORIZONTAL_ALIGNMENT_LEFT, -1, px)
	var col := Palette.HARM_INK
	col.a = 0.85
	stamp_slot.draw_set_transform(STAMP_SLOT * 0.5, deg_to_rad(STAMP_TILT_DEG))
	stamp_slot.draw_rect(Rect2(-(sz + STAMP_BOX_PAD) * 0.5, sz + STAMP_BOX_PAD), col, false, STAMP_LINE)
	stamp_slot.draw_string(font, Vector2(-sz.x * 0.5, sz.y * 0.32), stamp, HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)
	stamp_slot.draw_set_transform(Vector2.ZERO, 0.0)


