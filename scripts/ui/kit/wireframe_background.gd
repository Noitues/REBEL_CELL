class_name WireframeBackground
extends Control
## The net (STYLE_GUIDE 1): radial cyberspace background, perspective grid floor and a
## wireframe skyline in net_cyan. `corp_creep` (0-1) lets corporate wireframe creep over
## the scene as Heat rises (GDD 9.4). The floor scrolls slowly unless reduce-effects.

var corp_color: Color = Palette.CORP_SOLACE
var corp_creep: float = 0.0
var floor_offset: float = 0.0
var skyline_seed: int = 7

var _gradient: GradientTexture2D


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var g := Gradient.new()
	g.set_color(0, Palette.NET_BG_INNER)
	g.set_color(1, Palette.NET_BG_OUTER)
	_gradient = GradientTexture2D.new()
	_gradient.gradient = g
	_gradient.fill = GradientTexture2D.FILL_RADIAL
	_gradient.fill_from = Vector2(0.5, 0.45)
	_gradient.fill_to = Vector2(0.5, 1.1)


func _process(delta: float) -> void:
	if Settings.reduce_effects:
		return
	floor_offset = fmod(floor_offset + delta * 0.15, 1.0)
	queue_redraw()


func _draw() -> void:
	draw_texture_rect(_gradient, Rect2(Vector2.ZERO, size), false)
	var horizon := size.y * 0.58
	var vanish := Vector2(size.x * 0.5, horizon)
	var cyan := Color(Palette.NET_CYAN, 0.35)
	# Perspective floor: converging verticals and receding horizontals.
	for i in range(-12, 13):
		var x := size.x * 0.5 + i * size.x * 0.11
		draw_line(Vector2(x, size.y), vanish, cyan, 1.0)
	for k in 14:
		var t := fmod(float(k) / 14.0 + floor_offset, 1.0)
		var y := horizon + (size.y - horizon) * (t * t)
		draw_line(Vector2(0, y), Vector2(size.x, y), Color(Palette.NET_CYAN, 0.12 + 0.3 * t), 1.0)
	# Skyline: deterministic wireframe blocks on the horizon.
	var x := 0.0
	var i := 0
	while x < size.x:
		var w := 30.0 + float((skyline_seed * 31 + i * 17) % 60)
		var h := 20.0 + float((skyline_seed * 13 + i * 29) % 110)
		var col := Color(Palette.NET_CYAN, 0.45)
		if corp_creep > 0.0 and (i % 3) < int(corp_creep * 3.0 + 0.5):
			col = Color(corp_color, 0.6)
		draw_rect(Rect2(x, horizon - h, w, h), col, false, 1.0)
		draw_line(Vector2(x, horizon - h), Vector2(x + w * 0.5, horizon - h - 8), col, 1.0)
		draw_line(Vector2(x + w * 0.5, horizon - h - 8), Vector2(x + w, horizon - h), col, 1.0)
		x += w + 6
		i += 1
	draw_line(Vector2(0, horizon), Vector2(size.x, horizon), Color(Palette.NET_CYAN, 0.6), 1.5)
