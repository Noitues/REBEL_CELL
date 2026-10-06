class_name CrtWindow
extends TerminalWindow
## ART-10 4C: the v2 terminal window (ART_BIBLE v2 §1.2 "CRT terminal", §4.13 "terminal panel
## (`> TITLE` header)"; round 33 `ui_kit.jpg`): Group 1B's CrtTerminalPanel is the glass
## (navy, scanlines, the scrolling hex dump, the accent edge glow), and over it a header strip
## reading `> TITLE` with an optional tag chip and the square marker, and a small bracket at
## the bottom left. High contrast: opaque black and a solid edge (§5.6), no glass. Same API as TerminalWindow (`body`, `tag_label`, `title`, `accent`), so a
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
## Group 1B's terminal glass (behind the content) and the header strip drawn over it.
var glass: CrtTerminalPanel = null
var _glass_host: Control = null
var _frame: Control = null
var _head_label: Label = null


func _init(p_title: String = "", p_accent: Color = Palette.NET_CYAN, max_body: float = 0.0) -> void:
	super(p_title, p_accent)
	material = null  # the kit glass draws the scanlines
	# The glass sits in a host the PanelContainer lays out at its content rect; the glass
	# itself is placed over the whole window (_place_glass), then the header strip over it.
	_glass_host = Control.new()
	_glass_host.name = "GlassHost"
	_glass_host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_glass_host)
	move_child(_glass_host, 0)
	glass = CrtTerminalPanel.new()
	glass.name = "Glass"
	glass.prompt = false
	glass.caret = false
	glass.accent_kind = CrtTerminalPanel.Accent.CORP
	glass.corp_color = p_accent  # the glass routes it through the skin
	glass.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_glass_host.add_child(glass)
	_frame = Control.new()
	_frame.name = "HeaderStrip"
	_frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_frame.draw.connect(_draw_frame)
	_glass_host.add_child(_frame)
	resized.connect(_place_glass)
	var box := StyleBoxEmpty.new()
	box.content_margin_left = PAD_H
	box.content_margin_right = PAD_H
	box.content_margin_top = PAD_TOP
	box.content_margin_bottom = PAD_BOTTOM
	add_theme_stylebox_override(&"panel", box)
	var outer := get_child(1) as VBoxContainer
	_outer = outer
	# A window sized past its rows (a menu's scroll, a fixed-height panel) gives the room to
	# its body.
	outer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var head := find_child("TerminalTitle", true, false) as Label
	if head != null:
		_bar = head.get_parent() as Control
		head.text = "> " + title.to_upper()
		head.add_theme_font_override(&"font", Chrome.caps_font(HEADER_STEP))
		head.add_theme_font_size_override(&"font_size", Chrome.px(HEADER_STEP))
		_head_label = head
		head.add_theme_color_override(&"font_color", skin_accent())
		head.add_theme_color_override(&"font_shadow_color", Palette.AUTO)
		# A long title wraps at its words (it never widens the window: the M13 title was 15 px
		# whatever the text scale).
		UiWrap.whole_words(head)
		tag_label.add_theme_font_override(&"font", Chrome.caps_font(UiTheme.CAPTION))
		tag_label.add_theme_font_size_override(&"font_size", Chrome.px(UiTheme.CAPTION))
		tag_label.add_theme_color_override(&"font_color", skin_accent())
		_square = ColorRect.new()
		_square.name = "HeaderSquare"
		_square.color = skin_accent()
		_square.custom_minimum_size = Vector2(Chrome.SQUARE, Chrome.SQUARE)
		_square.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		_square.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_bar.add_child(_square)
		_bar.add_theme_constant_override(&"separation", 10)
		# The pink rule under M13's title gives way to the header strip.
		var rule := outer.get_child(1) as ColorRect
		if rule != null:
			rule.color = Color(skin_accent(), 0.55)
			_rule = rule
			rule.custom_minimum_size.y = 1
		outer.add_theme_constant_override(&"separation", 8)
	if max_body > 0.0:
		outer.remove_child(body)
		fit = FitScroll.new(body, max_body)
		outer.add_child(fit)


## ART-9 4A: the glass's accent by kind (CrtTerminalPanel.Accent) and its corp colour: the
## Mainframe's clerk and strips, the loot's PAYOUT and FIRMWARE DROP, the event terminal (the
## corp colour, red for DISPATCH) and the deck viewer.
func with_kind(kind: int, corp: Color) -> CrtWindow:
	glass.accent_kind = kind
	glass.corp_color = corp
	return self


## ART-9 4A: the CRT accent for a colour the screens use (corp colours go in as CORP).
static func kind_for(col: Color) -> int:
	if col == Palette.CELL_ACID:
		return CrtTerminalPanel.Accent.FIRMWARE
	if col == Palette.HARM:
		return CrtTerminalPanel.Accent.DISPATCH
	if col == Palette.NET_CYAN or col == Palette.CELL_PINK:
		return CrtTerminalPanel.Accent.CELL
	return CrtTerminalPanel.Accent.CORP


func _ready() -> void:
	Settings.changed.connect(_settings_changed)
	glass.hex_dump = hex
	_place_glass()


func _exit_tree() -> void:
	if Settings.changed.is_connected(_settings_changed):
		Settings.changed.disconnect(_settings_changed)


func _settings_changed() -> void:
	_apply_skin()
	_place_glass()
	queue_redraw()


## Re-values what the header caches (its words, tag, square and rule) for the active skin.
func _apply_skin() -> void:
	super()
	if _head_label != null:
		_head_label.add_theme_color_override(&"font_color", skin_accent())
		tag_label.add_theme_color_override(&"font_color", skin_accent())
	if _square != null:
		_square.color = skin_accent()
	if _rule != null:
		_rule.color = Color(skin_accent(), 0.55)
	if _frame != null:
		_frame.queue_redraw()


## The glass over the whole window (its host is inset by the content margins).
func _place_glass() -> void:
	if glass == null:
		return
	var inset := Vector2(PAD_H, PAD_TOP)
	glass.position = -inset
	glass.size = size
	glass.visible = not Settings.high_contrast
	_frame.position = -inset
	_frame.size = size
	_frame.queue_redraw()


## The header strip's height (px, local): down to the rule under the title bar.
func header_height() -> float:
	if _bar == null:
		return 0.0
	return _outer.position.y + _bar.position.y + _bar.size.y + 2.0


## High contrast: the opaque terminal (the glass is hidden).
func _draw() -> void:
	if Settings.high_contrast:
		Chrome.draw_terminal(self, Rect2(Vector2.ZERO, size), skin_accent())


## The header strip, its tag chip and the foot bracket, over the glass, under the content.
func _draw_frame() -> void:
	var r := Rect2(Vector2.ZERO, size)
	var hh := header_height()
	if hh > 0.0:
		_frame.draw_rect(Rect2(Vector2(1, 1), Vector2(r.size.x - 2.0, hh - 1.0)), Color(skin_accent(), 0.1))
	if tag_label != null and tag_label.text != "" and _bar != null:
		var local := Rect2(tag_label.position + _bar.position + _outer.position, tag_label.size).grow_individual(4, 0, 4, 0)
		_frame.draw_rect(local, skin_accent(), false, 1.0)
	var foot := Vector2(r.position.x - 3.0, r.end.y + 3.0)
	_frame.draw_polyline(PackedVector2Array([foot + Vector2(0, -Chrome.FOOT_TICK), foot, foot + Vector2(Chrome.FOOT_TICK, 0)]), Color(skin_accent(), 0.7), Chrome.EDGE_W)
