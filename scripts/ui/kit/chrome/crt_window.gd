class_name CrtWindow
extends TerminalWindow
## ART-10 4C: the v2 terminal panel (ART_BIBLE v2 §1.2 "CRT terminal", §4.13 "terminal panel
## (chamfered corner, `> TITLE` header)"; round 33 `ui_kit.jpg`): navy glass with its top-right
## corner cut, faint scanlines and hex-dump, an accent edge, a header strip reading
## `> TITLE` with an optional tag chip and the square marker, and a small bracket at the
## bottom left. Same API as TerminalWindow (`body`, `tag_label`, `title`, `accent`), so a
## screen swaps one for the other. `max_body` > 0 puts the body in a FitScroll (it sizes to
## its rows up to that height, then scrolls inside the panel with MORE BELOW). View only.

## Content margins (px at 1280x720): sides, top (under the header) and bottom.
const PAD_H := 14.0
const PAD_TOP := 8.0
const PAD_BOTTOM := 12.0
## The header strip's type step.
const HEADER_STEP := UiTheme.BODY

## The FitScroll round the body (null unless `max_body` was given).
var fit: FitScroll = null
## Draw the faint hex-dump on the glass.
var hex := true
var _bar: Control = null
var _outer: Control = null
var _square: ColorRect = null


func _init(p_title: String = "", p_accent: Color = Palette.NET_CYAN, max_body: float = 0.0) -> void:
	super(p_title, p_accent)
	material = null  # the glass draws its own scanlines (Chrome.draw_terminal)
	var box := StyleBoxEmpty.new()
	box.content_margin_left = PAD_H
	box.content_margin_right = PAD_H
	box.content_margin_top = PAD_TOP
	box.content_margin_bottom = PAD_BOTTOM
	add_theme_stylebox_override(&"panel", box)
	var outer := get_child(0) as VBoxContainer
	_outer = outer
	var head := find_child("TerminalTitle", true, false) as Label
	if head != null:
		_bar = head.get_parent() as Control
		head.text = "> " + title.to_upper()
		head.add_theme_font_override(&"font", Chrome.caps_font(HEADER_STEP))
		head.add_theme_font_size_override(&"font_size", Chrome.px(HEADER_STEP))
		head.add_theme_color_override(&"font_color", accent)
		head.add_theme_color_override(&"font_shadow_color", Palette.AUTO)
		tag_label.add_theme_font_override(&"font", Chrome.caps_font(UiTheme.CAPTION))
		tag_label.add_theme_font_size_override(&"font_size", Chrome.px(UiTheme.CAPTION))
		tag_label.add_theme_color_override(&"font_color", accent)
		_square = ColorRect.new()
		_square.name = "HeaderSquare"
		_square.color = accent
		_square.custom_minimum_size = Vector2(Chrome.SQUARE, Chrome.SQUARE)
		_square.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		_square.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_bar.add_child(_square)
		_bar.add_theme_constant_override(&"separation", 10)
		# The pink rule under M13's title gives way to the header strip.
		var rule := outer.get_child(1) as ColorRect
		if rule != null:
			rule.color = Color(accent, 0.55)
			rule.custom_minimum_size.y = 1
		outer.add_theme_constant_override(&"separation", 8)
	if max_body > 0.0:
		outer.remove_child(body)
		fit = FitScroll.new(body, max_body)
		outer.add_child(fit)


func _ready() -> void:
	Settings.changed.connect(queue_redraw)


func _exit_tree() -> void:
	if Settings.changed.is_connected(queue_redraw):
		Settings.changed.disconnect(queue_redraw)


## The header strip's height (px, local): down to the rule under the title bar.
func header_height() -> float:
	if _bar == null:
		return 0.0
	return _outer.position.y + _bar.position.y + _bar.size.y + 2.0


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	Chrome.draw_terminal(self, r, accent)
	var hh := header_height()
	if hex:
		Chrome.draw_hex(self, Rect2(Vector2(r.size.x * 0.55, hh + 4.0), Vector2(r.size.x * 0.45 - PAD_H, r.size.y - hh - PAD_BOTTOM)), accent)
	if hh > 0.0:
		draw_rect(Rect2(Vector2(1, 1), Vector2(r.size.x - Chrome.CHAMFER - 1.0, hh - 1.0)), Color(accent, 0.1))
		draw_rect(Rect2(Vector2(r.size.x - Chrome.CHAMFER, Chrome.CHAMFER * 0.5), Vector2(Chrome.CHAMFER - 1.0, hh - Chrome.CHAMFER * 0.5)), Color(accent, 0.1))
	if tag_label != null and tag_label.text != "":
		var local := Rect2(tag_label.position + _bar.position + _outer.position, tag_label.size).grow_individual(4, 0, 4, 0)
		draw_rect(local, accent, false, 1.0)
