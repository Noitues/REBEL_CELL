class_name PaperSheet
extends MarginContainer
## ART-11 4D: a typed sheet of corp paper in the dossier (ART_BIBLE v2 §1.2 "corp paper":
## intercepted corp documents; round 21 dossier21.py `sheet`): 1B's corp paper stock
## (`shaders/kit/corp_paper.gdshader`, as CorpPaperPanel draws it: fibres, tooth, toner speckle,
## handled edges) with a drop shadow on the folder; its children are the typed lines, laid out
## by the container (CorpPaperPanel places its fields by hand, so the dossier's flowing sheets
## keep this container and share the material). Look only.

## The stock (a Palette paper token) and the tilt its holder gives it (TiltBox, degrees).
var stock: Color = Palette.END_REPORT
var tilt: float = 0.0
## The shadow's offset (px at 1.0).
const SHADOW_OFFSET := Vector2(5, 8)

var _paper: Control = null
var _mat: ShaderMaterial = null


func _init(p_stock: Color = Palette.END_REPORT, p_tilt: float = 0.0, pad: float = UiTheme.SP_L) -> void:
	stock = p_stock
	tilt = p_tilt
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var s := Settings.text_scale
	for side in ["left", "right", "top", "bottom"]:
		add_theme_constant_override("margin_" + side, roundi(pad * s))
	_mat = ShaderMaterial.new()
	_mat.shader = CorpPaperPanel.SHADER
	_paper = Control.new()
	_paper.name = "Stock"
	_paper.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_paper.material = _mat
	_paper.draw.connect(func() -> void: _paper.draw_rect(Rect2(Vector2.ZERO, _paper.size), Palette.TEXT_HI))
	add_child(_paper, false, Node.INTERNAL_MODE_FRONT)
	# B5 (review D24): the concepts' paper clip over the sheet's top right, drawn after its typed lines.
	_clip = Control.new()
	_clip.name = "Clip"
	_clip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_clip.draw.connect(func() -> void:
		if clip:
			PaperLie.draw_clip(_clip, Rect2(Vector2.ZERO, size), _screen_h()))
	add_child(_clip, false, Node.INTERNAL_MODE_BACK)
	resized.connect(_on_resized)


## B5 (D24): the sheet wears the paper clip.
var clip: bool = true
var _clip: Control = null


func _screen_h() -> float:
	return get_viewport_rect().size.y if is_inside_tree() else PaperLie.BOARD_H


## M14 parity END-06: the stock covers the whole sheet. A MarginContainer fits every child,
## its internal ones too, inside its margins: the stock was laid inset by the pads (the report's
## right pad is the post-its' room), so the shadow showed round it as a dark band and the typed
## lines ran to the stock's very edge. It is laid again after each sort.
func _notification(what: int) -> void:
	if what == NOTIFICATION_SORT_CHILDREN and _paper != null:
		_paper.position = Vector2.ZERO
		_paper.size = size
		_clip.position = Vector2.ZERO
		_clip.size = size
		_clip.queue_redraw()


func _on_resized() -> void:
	pivot_offset = size * 0.5
	_paper.position = Vector2.ZERO
	_paper.size = size
	_mat.set_shader_parameter(&"panel", Vector4(0, 0, size.x, size.y))
	_mat.set_shader_parameter(&"stock", PaperInk.opaque(stock))
	_mat.set_shader_parameter(&"fibre", Palette.KRAFT_FIBRE)
	_mat.set_shader_parameter(&"seed", float(get_index() + 3))
	_paper.queue_redraw()
	_clip.position = Vector2.ZERO
	_clip.size = size
	_clip.queue_redraw()
	queue_redraw()


func _draw() -> void:
	# B5 (D24): the soft 6 px contact shadow of paper lying on the folder.
	PaperLie.draw_contact_shadow(self, Rect2(Vector2.ZERO, size), _screen_h())
	if PaperInk.on():
		draw_rect(Rect2(Vector2.ZERO, size), PaperInk.edge(Palette.INK), false, PaperInk.edge_width(1.0))
