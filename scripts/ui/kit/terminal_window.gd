class_name TerminalWindow
extends PanelContainer
## A GLASS window over the night city (ART_BIBLE §2 GLASS, §3.3 SCRIM, §4.2, §5.3; STYLE_GUIDE
## 4 "Neon city"): navy glass with faint scanlines (`UiTheme.crt_material`), a 1 px edge with
## bright corner brackets, an optional mono CAPS title with a `CELL_PINK` rule under it
## ("NODE STATUS", "SYSTEM ONLINE"), and a SCRIM behind the glass (the city behind it is
## blurred and dimmed, `GlassScrim`; opaque under high contrast). Put content in `body`.
##
## Type comes from the scale (§4.3 rule 1): the title at `label`, the title bar's tag at
## `body`, both times the text scale, restyled when the text scale changes. The window
## sizes to its content (a container lays it out at its minimum unless the caller expands
## it); `scroll_body(max)` caps the body's height, past which it scrolls inside the window
## with a MORE BELOW hint and never clips mid-row (§5.3). Glass never holds paper (§2).

## The title's step, and the tag's (§4.2). A title that doesn't fit its window on one line
## at TITLE_STEP steps down to FIT_STEP (§4.3 rule 3: the text shrinks a step), then wraps
## at word boundaries: a title never widens its window.
const TITLE_STEP := UiTheme.BODY
const FIT_STEP := UiTheme.CAPTION
const TAG_STEP := UiTheme.BODY
## The title rule's thickness (px) and the corner brackets' arm length and stroke (px).
const RULE_H := 2.0
const BRACKET := 12.0
const BRACKET_W := 2.0

var title: String = ""
var accent: Color = Palette.NET_CYAN
var body: VBoxContainer
## Right-aligned tag in the title bar ("CYCLE", "120 CYCLES").
var tag_label: Label
## The title's label (null without a title).
var title_label: Label = null
## The blur-and-dim behind the glass.
var scrim: GlassScrim
## The scrolling view round `body` once `scroll_body` capped it (null until then).
var fit: FitScroll = null
var _outer: VBoxContainer
## The title size this window set last (0 before the first restyle).
var _title_px: int = 0


func _init(p_title: String = "", p_accent: Color = Palette.NET_CYAN) -> void:
	title = p_title
	accent = p_accent
	theme_type_variation = &"TerminalPanel"
	material = UiTheme.crt_material()
	scrim = GlassScrim.new()
	scrim.show_behind_parent = true
	scrim.use_parent_material = false
	add_child(scrim)
	_outer = VBoxContainer.new()
	_outer.name = "Outer"
	_outer.add_theme_constant_override("separation", UiTheme.SP_XS)
	_outer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_outer)
	if title != "":
		title_label = Label.new()
		title_label.text = title.to_upper()
		title_label.add_theme_color_override("font_color", accent.lerp(Palette.PAPER, 0.35))
		title_label.name = "TerminalTitle"
		title_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		title_label.resized.connect(_fit_title)
		var bar := HBoxContainer.new()
		bar.name = "TitleBar"
		bar.add_child(title_label)
		tag_label = Label.new()
		tag_label.name = "TerminalTag"
		tag_label.add_theme_color_override("font_color", Palette.CELL_ACID)
		bar.add_child(tag_label)
		_outer.add_child(bar)
		var rule := ColorRect.new()
		rule.name = "TitleRule"
		rule.color = Palette.CELL_PINK
		rule.custom_minimum_size = Vector2(0, RULE_H)
		rule.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_outer.add_child(rule)
	body = VBoxContainer.new()
	body.name = "Body"
	body.add_theme_constant_override("separation", UiTheme.SP_XS)
	_outer.add_child(body)
	restyle()


func _ready() -> void:
	if not Settings.changed.is_connected(restyle):
		Settings.changed.connect(restyle)


## Sizes the title and tag from the type scale at the player's text scale (§4.3 rule 1).
func restyle() -> void:
	if tag_label != null:
		tag_label.add_theme_font_size_override("font_size", UiTheme.font_px(TAG_STEP))
	_fit_title()


## The title's size: TITLE_STEP when its words fit the label's width on one line, else
## FIT_STEP (wrapping at word boundaries if even that is too wide).
func _fit_title() -> void:
	if title_label == null:
		return
	# A subclass that sizes its own title (the map keys) keeps its size.
	if _title_px > 0 and title_label.get_theme_font_size(&"font_size") != _title_px:
		return
	title_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	var font := title_label.get_theme_font(&"font")
	var px := UiTheme.font_px(TITLE_STEP)
	var room := title_label.size.x
	if room > 0.0 and font.get_string_size(title_label.text, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x > room + 0.5:
		px = UiTheme.font_px(FIT_STEP)
	if px != _title_px:
		_title_px = px
		title_label.add_theme_font_size_override("font_size", px)


## Caps the body at `max_height` px: taller content scrolls inside the window with a scroll
## hint (§5.3). Returns the window. Call again to change the cap.
func scroll_body(max_height: float) -> TerminalWindow:
	if fit == null:
		var at := body.get_index()
		_outer.remove_child(body)
		fit = FitScroll.new(body, max_height)
		fit.size_flags_vertical = Control.SIZE_EXPAND_FILL
		_outer.add_child(fit)
		_outer.move_child(fit, at)
	else:
		fit.max_height = max_height
	return self


## The share of the window's height that holds nothing (0 when it is as tall as its
## content; §5.3 allows at most 0.25).
func empty_share() -> float:
	if size.y <= 0.0:
		return 0.0
	return clampf(1.0 - get_combined_minimum_size().y / size.y, 0.0, 1.0)


func _notification(what: int) -> void:
	# The container has laid the children in the glass's margins; the scrim covers the whole
	# window behind the glass.
	if what == NOTIFICATION_SORT_CHILDREN and scrim != null:
		fit_child_in_rect(scrim, Rect2(Vector2.ZERO, size))


func _draw() -> void:
	# Corner brackets, drawn over the frame edge.
	var r := Rect2(Vector2.ZERO, size)
	for c in [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)]:
		var sx := 1.0 if c.x <= r.position.x else -1.0
		var sy := 1.0 if c.y <= r.position.y else -1.0
		draw_line(c, c + Vector2(BRACKET * sx, 0), accent, BRACKET_W)
		draw_line(c, c + Vector2(0, BRACKET * sy), accent, BRACKET_W)
