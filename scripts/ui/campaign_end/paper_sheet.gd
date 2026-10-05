class_name PaperSheet
extends MarginContainer
## ART-11 4D: a typed sheet of corp paper on the dossier (ART_BIBLE v2 §1.2 "corp paper":
## intercepted corp documents; round 21 dossier21.py `sheet`): the stock with a soft fibre
## grain, a drop shadow on the folder, a slight tilt; its children are the typed lines. A seam
## for 1B's corp paper panel. Look only.

## The stock.
var stock: Color = Palette.END_REPORT
## The tilt (degrees) and the shadow's offset (px at 1.0).
var tilt: float = 0.0
const SHADOW_OFFSET := Vector2(5, 8)
## The fibre grain: marks per 10 000 px², their length (px) and alpha. Drawn from a hash of
## the sheet's size (decoration, no game RNG).
const FIBRES_PER_AREA := 14.0
const FIBRE_LEN := 5.0
const FIBRE_ALPHA := 0.07


func _init(p_stock: Color = Palette.END_REPORT, p_tilt: float = 0.0, pad: float = UiTheme.SP_L) -> void:
	stock = p_stock
	tilt = p_tilt
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var s := Settings.text_scale
	for side in ["left", "right", "top", "bottom"]:
		add_theme_constant_override("margin_" + side, roundi(pad * s))
	resized.connect(_on_resized)


func _on_resized() -> void:
	pivot_offset = size * 0.5
	rotation_degrees = tilt
	queue_redraw()


func _draw() -> void:
	var s := Settings.text_scale
	var r := Rect2(Vector2.ZERO, size)
	draw_rect(Rect2(r.position + SHADOW_OFFSET * s, r.size), Palette.SHADOW)
	draw_rect(r, PaperInk.opaque(stock))
	# The fibre grain.
	var n := int(size.x * size.y / 10000.0 * FIBRES_PER_AREA)
	var ink := Color(Palette.END_TYPE_INK, FIBRE_ALPHA)
	for i in n:
		var hx := _hash(i * 3 + 1)
		var hy := _hash(i * 3 + 2)
		var ha := _hash(i * 3 + 3) * PI
		var p := Vector2(hx * size.x, hy * size.y)
		draw_line(p, p + Vector2(cos(ha), sin(ha)) * FIBRE_LEN, ink, 1.0)
	draw_rect(r, PaperInk.edge(Color(Palette.INK, 0.25)), false, PaperInk.edge_width(1.0))


func _hash(i: int) -> float:
	return fposmod(sin(float(i) * 12.9898 + size.x * 0.017 + size.y * 0.031) * 43758.5453, 1.0)
