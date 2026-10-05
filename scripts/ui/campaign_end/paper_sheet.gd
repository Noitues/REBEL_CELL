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
	resized.connect(_on_resized)


func _on_resized() -> void:
	pivot_offset = size * 0.5
	_paper.position = Vector2.ZERO
	_paper.size = size
	_mat.set_shader_parameter(&"panel", Vector4(0, 0, size.x, size.y))
	_mat.set_shader_parameter(&"stock", PaperInk.opaque(stock))
	_mat.set_shader_parameter(&"fibre", Palette.KRAFT_FIBRE)
	_mat.set_shader_parameter(&"seed", float(get_index() + 3))
	_paper.queue_redraw()
	queue_redraw()


func _draw() -> void:
	draw_rect(Rect2(SHADOW_OFFSET * Settings.text_scale, size), Palette.SHADOW)
	if PaperInk.on():
		draw_rect(Rect2(Vector2.ZERO, size), PaperInk.edge(Palette.INK), false, PaperInk.edge_width(1.0))
