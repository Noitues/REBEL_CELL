class_name Badge
extends Control
## One fact as a small hex badge and a short value (H20: facts that used to be text lines
## in a log or readout): a glyph or a defence asset's icon in the hex, the value beside it
## in the theme font (it follows the text scale), an optional mini meter under the value,
## and a tooltip that says what it means. Put several in an HFlowContainer so they wrap.
## Draw-only; the scene decides what it shows.

## Hex radius (px) at text scale 1.0.
const HEX_R := 10.0
## Gap between the hex and the value (px).
const GAP := 6.0
## Mini meter height and width (px).
const METER_H := 4.0
const METER_W := 64.0

var glyph: String = ""
var asset_id: StringName = &""
var text: String = ""
var color: Color = Palette.NET_CYAN
## 0..1 fills the mini meter; below 0 there is none.
var fill: float = -1.0
## A StatIcon drawn in the hex instead of the glyph (H21: the same icon as the stat's tag).
var icon_kind: StringName = &""


func _init(p_text: String = "", p_color: Color = Palette.NET_CYAN, p_glyph: String = "", p_tip: String = "", p_asset: StringName = &"") -> void:
	text = p_text
	color = p_color
	glyph = p_glyph
	asset_id = p_asset
	tooltip_text = UiTip.fold(p_tip)
	mouse_filter = Control.MOUSE_FILTER_PASS if p_tip != "" else Control.MOUSE_FILTER_IGNORE


## Adds a mini meter under the value, `value` of `maximum`.
func with_meter(value: float, maximum: float) -> Badge:
	fill = clampf(value / maxf(1.0, maximum), 0.0, 1.0)
	update_minimum_size()
	return self


## Draws StatIcon `kind` in the hex (the resource's own icon, as on its top-bar tag).
func with_icon(kind: StringName) -> Badge:
	icon_kind = kind
	queue_redraw()
	return self


func _font_size() -> int:
	return get_theme_font_size(&"font_size", &"Label")


func _scale() -> float:
	return maxf(1.0, _font_size() / float(UiTheme.BASE_SIZE))


func _get_minimum_size() -> Vector2:
	var font := get_theme_font(&"font", &"Label")
	var w := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, _font_size()).x
	if fill >= 0.0:
		w = maxf(w, METER_W)
	var r := HEX_R * _scale()
	return Vector2(r * 2.0 + GAP + w + 2.0, maxf(r * 2.0 + 2.0, font.get_height(_font_size()) + (METER_H + 2.0 if fill >= 0.0 else 0.0)))


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED:
		update_minimum_size()
		queue_redraw()


func _make_custom_tooltip(for_text: String) -> Object:
	return UiTip.make(for_text) if for_text != "" else null


func _draw() -> void:
	var r := HEX_R * _scale()
	var c := Vector2(r + 1.0, size.y * 0.5)
	var pts := PackedVector2Array()
	for k in 7:
		var t := PI / 6.0 + TAU * k / 6.0
		pts.append(c + Vector2(cos(t), sin(t)) * r)
	draw_colored_polygon(pts, Color(Palette.NIGHT_SKY, 0.92))
	draw_polyline(pts, color, 1.6)
	if asset_id != &"":
		AssetIcon.draw_icon(self, c, r * 0.8, asset_id, false)
	elif icon_kind != &"":
		StatIcon.draw(self, c, r * 0.62, icon_kind, color)
	elif glyph != "":
		draw_string(Palette.mono(), c + Vector2(-r, r * 0.42), glyph, HORIZONTAL_ALIGNMENT_CENTER, r * 2.0, int(r * 1.1), color)
	var font := get_theme_font(&"font", &"Label")
	var fs := _font_size()
	var x := r * 2.0 + GAP + 2.0
	var base := (size.y - (METER_H + 2.0 if fill >= 0.0 else 0.0)) * 0.5 + font.get_ascent(fs) * 0.5 - font.get_descent(fs) * 0.25
	draw_string(font, Vector2(x, base), text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, color.lerp(Palette.PAPER, 0.35))
	if fill >= 0.0:
		var bar := Rect2(x, size.y - METER_H - 1.0, size.x - x - 1.0, METER_H)
		draw_rect(bar, Color(Palette.PAPER, 0.15))
		draw_rect(Rect2(bar.position, Vector2(bar.size.x * fill, bar.size.y)), color)
