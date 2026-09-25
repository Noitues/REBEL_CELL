class_name TerminalWindow
extends PanelContainer
## A terminal window over the night city (STYLE_GUIDE 4, "Neon city"): deep navy glass,
## a thin cyan frame with bright corner brackets and an optional mono title with a pink
## underline ("NODE STATUS", "SYSTEM ONLINE"). Put content in `body`.

var title: String = ""
var accent: Color = Palette.NET_CYAN
var body: VBoxContainer


func _init(p_title: String = "", p_accent: Color = Palette.NET_CYAN) -> void:
	title = p_title
	accent = p_accent
	theme_type_variation = &"TerminalPanel"
	material = UiTheme.crt_material()
	var outer := VBoxContainer.new()
	outer.add_theme_constant_override("separation", 6)
	outer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(outer)
	if title != "":
		var head := Label.new()
		head.text = title.to_upper()
		head.add_theme_color_override("font_color", accent.lerp(Palette.PAPER, 0.35))
		head.add_theme_font_size_override("font_size", 15)
		head.name = "TerminalTitle"
		outer.add_child(head)
		var rule := ColorRect.new()
		rule.color = Color(Palette.CELL_PINK, 0.8)
		rule.custom_minimum_size = Vector2(0, 2)
		rule.mouse_filter = Control.MOUSE_FILTER_IGNORE
		outer.add_child(rule)
	body = VBoxContainer.new()
	body.add_theme_constant_override("separation", 4)
	outer.add_child(body)


func _draw() -> void:
	# Corner brackets, drawn over the frame edge.
	var r := Rect2(Vector2.ZERO, size)
	var k := 12.0
	var col := accent
	for c in [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)]:
		var sx := 1.0 if c.x <= r.position.x else -1.0
		var sy := 1.0 if c.y <= r.position.y else -1.0
		draw_line(c, c + Vector2(k * sx, 0), col, 2.0)
		draw_line(c, c + Vector2(0, k * sy), col, 2.0)
