class_name StreetR2SignCanvas
extends Control
## Street r2 renderer, sign half (view glue): draws one sign draw list (`StreetR2Signs`: `{w, h, ops}`, ops grad / fill / rect / line /
## ellipse / text / ad; glow and holo_shift are post filters of the plate and are not drawn) into a SubViewport texture with the Godot fonts.
## Also the font table and the `measure` Callable the draw lists are made with.

var spec: Dictionary = {}
var fonts: Dictionary = {}
var _ad_k: float = 0.5


## The fonts by the draw lists' names (`anton`, `mono`), loaded from the paths of the render config.
static func load_fonts() -> Dictionary:
	var s: Dictionary = StreetR2RenderConfigData.shipped().signs
	return {"anton": load(String(s["font_anton"])), "mono": load(String(s["font_mono"]))}


## The `measure(font, size, text) -> [w, h]` Callable of the sign rules, in the glyph boxes of the Godot fonts (`signs.measure_h_k` turns the
## font height into the plate's glyph-box height).
static func make_measure(font_table: Dictionary = {}) -> Callable:
	var table := font_table if not font_table.is_empty() else load_fonts()
	var hk := float(StreetR2RenderConfigData.shipped().signs["measure_h_k"])
	return func(font: String, size: int, text: String) -> Array:
		var f: Font = table[font]
		var sz := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, size)
		return [int(ceil(sz.x)), int(round(sz.y * hk))]


## The pixel size of a draw list (`ad` lists carry none: the sign's aspect decides).
static func size_of(sp: Dictionary, aspect: float) -> Vector2i:
	if sp["w"] != null:
		return Vector2i(int(sp["w"]), int(sp["h"]))
	var sz: Array = StreetR2Signs.size_for(aspect)
	return Vector2i(int(sz[0]), int(sz[1]))


## Sets up the canvas for `sp` at pixel size `px`.
func setup(sp: Dictionary, font_table: Dictionary, px: Vector2i) -> void:
	spec = sp
	fonts = font_table
	_ad_k = float(StreetR2RenderConfigData.shipped().signs["ad_col_k"])
	size = Vector2(px)
	custom_minimum_size = size


func _draw() -> void:
	for op: Dictionary in spec.get("ops", []):
		match String(op["op"]):
			"grad":
				var top := _c(op["top"])
				var bot := _c(op["bot"])
				var w := float(op["w"])
				var h := float(op["h"])
				draw_polygon(PackedVector2Array([Vector2(0, 0), Vector2(w, 0), Vector2(w, h), Vector2(0, h)]), PackedColorArray([top, top, bot, bot]))
			"fill":
				draw_rect(Rect2(0, 0, float(op["w"]), float(op["h"])), _c(op["col"]))
			"rect":
				var b: Array = op["box"]
				var r := Rect2(float(b[0]), float(b[1]), float(b[2]) - float(b[0]), float(b[3]) - float(b[1]))
				if op["fill"] != null:
					draw_rect(r, _c(op["fill"]))
				if op["outline"] != null:
					var wd := float(op["width"])
					draw_rect(r.grow(-wd * 0.5), _c(op["outline"]), false, wd)
			"line":
				var pts := PackedVector2Array()
				for p: Array in op["pts"]:
					pts.append(Vector2(float(p[0]), float(p[1])))
				draw_polyline(pts, _c(op["fill"]), maxf(1.0, float(op["width"])))
			"ellipse":
				var e: Array = op["box"]
				var cen := Vector2((float(e[0]) + float(e[2])) * 0.5, (float(e[1]) + float(e[3])) * 0.5)
				draw_arc(cen, (float(e[2]) - float(e[0])) * 0.5, 0.0, TAU, 48, _c(op["outline"]), float(op["width"]))
			"text":
				_text(op)
			"ad":
				_ad(String(op["name"]))


func _text(op: Dictionary) -> void:
	var f: Font = fonts[String(op["font"])]
	var px := int(op["size"])
	var s := String(op["s"])
	var w := f.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	var xy: Array = op["xy"]
	var anchor := String(op["anchor"])
	var x := float(xy[0])
	if anchor.begins_with("m"):
		x -= w * 0.5
	var base := float(xy[1]) + (f.get_ascent(px) - f.get_descent(px)) * 0.5
	draw_string(f, Vector2(x, base), s, HORIZONTAL_ALIGNMENT_LEFT, -1, px, _c(op["fill"]))


## An ad plate: the plate's own concept art is not in the repo, so the placeholder is a hue field of the ad's name with the name set large.
func _ad(ad_name: String) -> void:
	var w := size.x
	var h := size.y
	var hue := fposmod(float(ad_name.hash() % 997) / 997.0, 1.0)
	var top := Color.from_hsv(hue, 0.7, 0.55 * _ad_k * 2.0)
	var bot := Color.from_hsv(hue, 0.8, 0.12)
	draw_polygon(PackedVector2Array([Vector2(0, 0), Vector2(w, 0), Vector2(w, h), Vector2(0, h)]), PackedColorArray([top, top, bot, bot]))
	var f: Font = fonts["anton"]
	var px := int(minf(h * 0.4, w * 0.18))
	var s := ad_name.to_upper()
	var tw := f.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	draw_string(f, Vector2((w - tw) * 0.5, h * 0.5 + px * 0.35), s, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color(1, 0.95, 1))


static func _c(a: Array) -> Color:
	return Color(float(a[0]) / 255.0, float(a[1]) / 255.0, float(a[2]) / 255.0)
