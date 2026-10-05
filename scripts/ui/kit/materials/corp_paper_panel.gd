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
	_paper.draw.connect(func() -> void: _paper.draw_rect(Rect2(Vector2.ZERO, size), Color.WHITE))
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
	content.position = Vector2(UiTheme.SP_L, LETTERHEAD_H + UiTheme.SP_M)
	content.size = Vector2(size.x - UiTheme.SP_L * 2.0, maxf(size.y - LETTERHEAD_H - UiTheme.SP_L * 2.0, 0.0))
	stamp_slot.size = STAMP_SLOT
	stamp_slot.position = Vector2(size.x - STAMP_SLOT.x - UiTheme.SP_M, size.y - STAMP_SLOT.y - UiTheme.SP_M)
	queue_redraw()
	_paper.queue_redraw()


## The drop shadow under the sheet.
func _draw() -> void:
	var sh := Palette.SHADOW
	draw_rect(Rect2(SHADOW_OFFSET, size), sh)


## The letterhead (corp name over a rule in the corp colour), on its own layer over the paper.
func _draw_letterhead(on: Control) -> void:
	var font := Palette.body_medium()
	var px := UiTheme.font_px(UiTheme.LABEL)
	on.draw_string(font, Vector2(UiTheme.SP_L, LETTERHEAD_H - UiTheme.SP_M), corp_name, HORIZONTAL_ALIGNMENT_LEFT, -1, px, corp_color.darkened(0.35))
	on.draw_rect(Rect2(UiTheme.SP_L, LETTERHEAD_H - RULE_PX - UiTheme.SP_XS, size.x - UiTheme.SP_L * 2.0, RULE_PX), corp_color.darkened(0.35))


func _draw_stamp() -> void:

	if stamp == "":
		return
	var font := Palette.display()
	var px := UiTheme.font_px(UiTheme.HEADING)
	var sz := font.get_string_size(stamp, HORIZONTAL_ALIGNMENT_LEFT, -1, px)
	var col := Palette.HARM_INK
	col.a = 0.85
	stamp_slot.draw_set_transform(STAMP_SLOT * 0.5, deg_to_rad(STAMP_TILT_DEG))
	stamp_slot.draw_rect(Rect2(-sz * 0.5 - Vector2(8, 2), sz + Vector2(16, 4)), col, false, 3.0)
	stamp_slot.draw_string(font, Vector2(-sz.x * 0.5, sz.y * 0.32), stamp, HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)
	stamp_slot.draw_set_transform(Vector2.ZERO, 0.0)


