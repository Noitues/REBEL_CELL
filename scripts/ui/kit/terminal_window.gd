class_name TerminalWindow
extends PanelContainer
## A terminal window over the night city (STYLE_GUIDE 4, "Neon city"): deep navy glass,
## a thin cyan frame with bright corner brackets and an optional mono title with an accent
## underline ("NODE STATUS", "SYSTEM ONLINE"). Put content in `body`.

var title: String = ""
var accent: Color = Palette.NET_CYAN
var body: VBoxContainer
## Right-aligned tag in the title bar ("CYCLE", "120 CYCLES").
var tag_label: Label
var _head: Label = null
var _rule: ColorRect = null
## B5: the kit glass behind a plain TerminalWindow (CrtWindow has its own).
var _glass: CrtTerminalPanel = null


func _init(p_title: String = "", p_accent: Color = Palette.NET_CYAN) -> void:
	title = p_title
	accent = p_accent
	theme_type_variation = &"TerminalPanel"
	PaletteSkins.bind(self, _apply_skin)  # ART-12 12s-b: the accent follows a skin pick
	if not (self is CrtWindow):
		# B5 (B1c follow-up 2): the kit's CRT glass behind the window (the hex dump fades under its words), not the
		# shared crt_panel material; the window's box keeps its margins and its edge, with no fill of its own.
		_glass = CrtTerminalPanel.behind(self, p_accent)
		var sb := UiTheme.terminal_box(Color(p_accent, 0.0))
		sb.bg_color = Color(sb.bg_color, 0.0)
		sb.set_border_width_all(0)
		sb.shadow_size = 0  # the box's accent glow drew through its clear centre as a wash over the glass
		sb.shadow_color = Color(sb.shadow_color, 0.0)
		add_theme_stylebox_override(&"panel", sb)
	var outer := VBoxContainer.new()
	outer.add_theme_constant_override("separation", 6)
	outer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(outer)
	if title != "":
		var head := Label.new()
		head.text = title.to_upper()
		head.add_theme_color_override("font_color", skin_accent().lerp(Palette.PAPER, 0.35))
		_head = head
		head.add_theme_font_size_override("font_size", 15)
		head.name = "TerminalTitle"
		head.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var bar := HBoxContainer.new()
		bar.add_child(head)
		tag_label = Label.new()
		tag_label.add_theme_color_override("font_color", Palette.CELL_ACID)
		tag_label.add_theme_font_size_override("font_size", 14)
		bar.add_child(tag_label)
		outer.add_child(bar)
		var rule := ColorRect.new()
		_rule = rule
		rule.color = Color(skin_accent(), 0.8)  # ART-1 1A (v2 §1.2): the terminal's own edge colour, not the verb pink
		rule.custom_minimum_size = Vector2(0, 2)
		rule.mouse_filter = Control.MOUSE_FILTER_IGNORE
		outer.add_child(rule)
	body = VBoxContainer.new()
	body.add_theme_constant_override("separation", 4)
	outer.add_child(body)


## The accent as the active skin draws it (a corp colour is unchanged; the Cell's cyan follows
## the skin). ART-12 12s-b.
func skin_accent() -> Color:
	return PaletteSkins.chrome(accent)


## Re-values the colours this window caches (its title and rule) and redraws; CrtWindow adds
## its own. Runs on every Settings change.
func _apply_skin() -> void:
	if _head != null:
		_head.add_theme_color_override("font_color", skin_accent().lerp(Palette.PAPER, 0.35))
	if _rule != null:
		_rule.color = Color(skin_accent(), 0.8)
	if _glass != null:
		_glass.corp_color = accent
	queue_redraw()


func _draw() -> void:
	# Corner brackets, drawn over the frame edge.
	var r := Rect2(Vector2.ZERO, size)
	var k := 12.0
	var col := skin_accent()
	for c in [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)]:
		var sx := 1.0 if c.x <= r.position.x else -1.0
		var sy := 1.0 if c.y <= r.position.y else -1.0
		draw_line(c, c + Vector2(k * sx, 0), col, 2.0)
		draw_line(c, c + Vector2(0, k * sy), col, 2.0)
