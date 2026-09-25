class_name UiTheme
extends RefCounted
## Builds the shared Theme (STYLE_GUIDE 3-4): Share Tech Mono for system text, Anton for
## display, Permanent Marker for the Cell's voice, scaled by Settings.text_scale.
## Controls look like neon terminal panels laid over the night city: deep navy glass,
## thin cyan edges, hot-pink hover glow, acid focus ring (always visible for pads).
## Type variations: "MenuItem" (a "> ITEM" line in a terminal menu), "TerminalPanel"
## (a PanelContainer framed like a terminal window), "GlassPanel" (the screen's content
## area: lighter glass so the city shows through), "HudLabel" (the status strip),
## "LogText" (the system log strip), "HeaderLabel" (a screen title).

const BASE_SIZE := 15


static func build(text_scale: float = 1.0) -> Theme:
	var t := Theme.new()
	var size := roundi(BASE_SIZE * text_scale)
	t.default_font = Palette.mono()
	t.default_font_size = size
	for kind in ["Button", "Label", "RichTextLabel", "OptionButton", "SpinBox", "LineEdit", "CheckButton", "CheckBox", "HSlider", "TabBar", "PopupMenu", "TooltipLabel"]:
		t.set_font_size("font_size", kind, size)
		t.set_font("font", kind, Palette.mono())
	for kind in ["normal_font_size", "bold_font_size", "italics_font_size", "mono_font_size"]:
		t.set_font_size(kind, "RichTextLabel", size)
	t.set_color("font_color", "Label", Palette.TERMINAL_TEXT)
	t.set_color("default_color", "RichTextLabel", Palette.TERMINAL_TEXT)
	t.set_color("font_shadow_color", "Label", Color(0, 0, 0, 0.6))
	t.set_constant("shadow_offset_x", "Label", 1)
	t.set_constant("shadow_offset_y", "Label", 1)
	_buttons(t)
	_menu_item(t, size)
	_fields(t)
	_panels(t)
	_bars(t)
	var header := "HeaderLabel"
	t.set_type_variation(header, "Label")
	t.set_font(&"font", header, Palette.mono())
	t.set_font_size(&"font_size", header, roundi(22 * text_scale))
	t.set_color(&"font_color", header, Palette.PAPER)
	return t


## A terminal box: deep glass, thin edge, square corners.
static func box(bg: Color, edge: Color, border: int = 1, margin_h: float = 10, margin_v: float = 4) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = bg
	s.border_color = edge
	s.set_border_width_all(border)
	s.set_corner_radius_all(0)
	s.content_margin_left = margin_h
	s.content_margin_right = margin_h
	s.content_margin_top = margin_v
	s.content_margin_bottom = margin_v
	s.anti_aliasing = false
	return s


static func _buttons(t: Theme) -> void:
	var normal := box(Palette.TERMINAL_BG, Palette.TERMINAL_EDGE)
	var hover := box(Palette.TERMINAL_BG_HOT, Palette.CELL_PINK)
	hover.shadow_color = Color(Palette.CELL_PINK, 0.35)
	hover.shadow_size = 6
	var pressed := box(Color(Palette.CELL_PINK, 0.55), Palette.CELL_PINK)
	var disabled := box(Color(Palette.TERMINAL_BG, 0.55), Color(Palette.TERMINAL_EDGE, 0.25))
	# Focus draws over the normal box: an acid ring outside the edge, readable on pads.
	var focus := box(Color(0, 0, 0, 0), Palette.CELL_ACID, 2)
	focus.draw_center = false
	focus.set_expand_margin_all(2)
	focus.shadow_color = Color(Palette.CELL_ACID, 0.25)
	focus.shadow_size = 5
	for kind in ["Button", "OptionButton", "CheckButton", "CheckBox"]:
		t.set_stylebox("normal", kind, normal)
		t.set_stylebox("hover", kind, hover)
		t.set_stylebox("pressed", kind, pressed)
		t.set_stylebox("hover_pressed", kind, pressed)
		t.set_stylebox("disabled", kind, disabled)
		t.set_stylebox("focus", kind, focus)
		t.set_color("font_color", kind, Palette.TERMINAL_TEXT)
		t.set_color("font_hover_color", kind, Palette.PAPER)
		t.set_color("font_focus_color", kind, Palette.CELL_ACID)
		t.set_color("font_pressed_color", kind, Palette.PAPER)
		t.set_color("font_hover_pressed_color", kind, Palette.PAPER)
		t.set_color("font_disabled_color", kind, Color(Palette.TERMINAL_TEXT, 0.35))
		t.set_color("icon_normal_color", kind, Palette.NET_CYAN)
		t.set_color("icon_hover_color", kind, Palette.CELL_PINK)
		t.set_color("icon_focus_color", kind, Palette.CELL_ACID)
	# Toggles sit flat in lists (no box of their own).
	var flat := box(Color(0, 0, 0, 0), Color(0, 0, 0, 0), 0, 4, 2)
	for kind in ["CheckButton", "CheckBox"]:
		t.set_stylebox("normal", kind, flat)
		t.set_stylebox("pressed", kind, flat)
		t.set_stylebox("disabled", kind, flat)
		var hot := box(Color(Palette.CELL_PINK, 0.12), Color(0, 0, 0, 0), 0, 4, 2)
		t.set_stylebox("hover", kind, hot)
		t.set_stylebox("hover_pressed", kind, hot)


static func _menu_item(t: Theme, size: int) -> void:
	var v := "MenuItem"
	t.set_type_variation(v, "Button")
	var clear := box(Color(0, 0, 0, 0), Color(0, 0, 0, 0), 0, 12, 5)
	var hot := box(Color(Palette.CELL_PINK, 0.16), Palette.CELL_PINK, 0, 12, 5)
	hot.border_width_left = 3
	var pressed := box(Color(Palette.CELL_PINK, 0.4), Palette.CELL_PINK, 0, 12, 5)
	pressed.border_width_left = 3
	t.set_stylebox("normal", v, clear)
	t.set_stylebox("hover", v, hot)
	t.set_stylebox("pressed", v, pressed)
	t.set_stylebox("hover_pressed", v, pressed)
	t.set_stylebox("disabled", v, clear)
	var focus := box(Color(Palette.CELL_ACID, 0.08), Palette.CELL_ACID, 0, 12, 5)
	focus.border_width_left = 3
	t.set_stylebox("focus", v, focus)
	t.set_constant("h_separation", v, 8)
	t.set_icon("icon", v, chevron())
	t.set_font_size("font_size", v, size + 2)
	t.set_color("font_color", v, Palette.TERMINAL_TEXT)


static func _fields(t: Theme) -> void:
	var field := box(Color(0.0, 0.02, 0.06, 0.95), Color(Palette.TERMINAL_EDGE, 0.5), 1, 8, 3)
	var field_focus := box(Color(0.0, 0.02, 0.06, 0.95), Palette.CELL_ACID, 2, 8, 3)
	t.set_stylebox("normal", "LineEdit", field)
	t.set_stylebox("focus", "LineEdit", field_focus)
	t.set_stylebox("read_only", "LineEdit", field)
	t.set_color("font_color", "LineEdit", Palette.PAPER)
	t.set_color("font_placeholder_color", "LineEdit", Color(Palette.TERMINAL_TEXT, 0.35))
	t.set_color("caret_color", "LineEdit", Palette.CELL_ACID)
	t.set_color("selection_color", "LineEdit", Color(Palette.CELL_PINK, 0.4))
	var popup := box(Color(0.02, 0.04, 0.1, 0.98), Palette.TERMINAL_EDGE, 1, 6, 6)
	t.set_stylebox("panel", "PopupMenu", popup)
	t.set_stylebox("hover", "PopupMenu", box(Color(Palette.CELL_PINK, 0.3), Color(0, 0, 0, 0), 0))
	t.set_color("font_color", "PopupMenu", Palette.TERMINAL_TEXT)
	t.set_color("font_hover_color", "PopupMenu", Palette.PAPER)
	t.set_stylebox("panel", "TooltipPanel", box(Color(0.02, 0.03, 0.08, 0.97), Palette.CELL_PINK, 1, 8, 5))
	t.set_color("font_color", "TooltipLabel", Palette.PAPER)


static func _panels(t: Theme) -> void:
	var clear := StyleBoxFlat.new()
	clear.bg_color = Color(0, 0, 0, 0)
	t.set_stylebox("panel", "PanelContainer", clear)
	var v := "TerminalPanel"
	t.set_type_variation(v, "PanelContainer")
	var p := box(Palette.TERMINAL_BG, Palette.TERMINAL_EDGE, 1, 14, 10)
	p.shadow_color = Color(0, 0, 0, 0.5)
	p.shadow_size = 8
	p.shadow_offset = Vector2(3, 4)
	t.set_stylebox("panel", v, p)
	var g := "GlassPanel"
	t.set_type_variation(g, "PanelContainer")
	var glass := box(Color(0.02, 0.04, 0.1, 0.8), Color(Palette.TERMINAL_EDGE, 0.35), 1, 12, 8)
	t.set_stylebox("panel", g, glass)
	var hud := "HudLabel"
	t.set_type_variation(hud, "Label")
	var strip := box(Color(0, 0, 0, 0.82), Palette.CELL_PINK, 0, 10, 5)
	strip.border_width_bottom = 2
	t.set_stylebox("normal", hud, strip)
	t.set_color("font_color", hud, Palette.PAPER)
	var lg := "LogText"
	t.set_type_variation(lg, "RichTextLabel")
	var log_box := box(Color(0.01, 0.03, 0.07, 0.9), Color(Palette.TERMINAL_EDGE, 0.4), 1, 12, 6)
	log_box.border_width_left = 3
	log_box.border_color = Color(Palette.NET_CYAN, 0.6)
	t.set_stylebox("normal", lg, log_box)
	t.set_stylebox("focus", lg, box(Color(0, 0, 0, 0), Palette.CELL_ACID, 2))
	t.set_color("default_color", lg, Color(Palette.TERMINAL_TEXT, 0.9))
	# Tabs (options, codex): terminal tabs with a pink active underline.
	var tab := box(Palette.TERMINAL_BG, Color(Palette.TERMINAL_EDGE, 0.4), 1, 10, 4)
	var tab_on := box(Palette.TERMINAL_BG_HOT, Palette.CELL_PINK, 0, 10, 4)
	tab_on.border_width_bottom = 3
	t.set_stylebox("tab_unselected", "TabBar", tab)
	t.set_stylebox("tab_hovered", "TabBar", box(Palette.TERMINAL_BG_HOT, Palette.CELL_PINK, 1, 10, 4))
	t.set_stylebox("tab_selected", "TabBar", tab_on)
	t.set_stylebox("tab_focus", "TabBar", box(Color(0, 0, 0, 0), Palette.CELL_ACID, 2, 10, 4))
	t.set_color("font_selected_color", "TabBar", Palette.PAPER)
	t.set_color("font_unselected_color", "TabBar", Palette.TERMINAL_TEXT)
	t.set_color("font_hovered_color", "TabBar", Palette.PAPER)


static func _bars(t: Theme) -> void:
	for kind in ["VScrollBar", "HScrollBar"]:
		var track := box(Color(0, 0, 0, 0.35), Color(0, 0, 0, 0), 0, 3, 3)
		var grab := box(Color(Palette.NET_CYAN, 0.45), Color(0, 0, 0, 0), 0, 3, 3)
		var grab_hot := box(Color(Palette.CELL_PINK, 0.8), Color(0, 0, 0, 0), 0, 3, 3)
		t.set_stylebox("scroll", kind, track)
		t.set_stylebox("grabber", kind, grab)
		t.set_stylebox("grabber_highlight", kind, grab_hot)
		t.set_stylebox("grabber_pressed", kind, grab_hot)
	var slider := box(Color(Palette.NET_CYAN, 0.18), Color(0, 0, 0, 0), 0, 0, 3)
	var fill := box(Color(Palette.CELL_PINK, 0.85), Color(0, 0, 0, 0), 0, 0, 3)
	t.set_stylebox("slider", "HSlider", slider)
	t.set_stylebox("grabber_area", "HSlider", fill)
	t.set_stylebox("grabber_area_highlight", "HSlider", fill)


static var _chevron: ImageTexture = null


## The "> " marker in front of terminal menu items (white, tinted by the icon colours).
static func chevron() -> Texture2D:
	if _chevron != null:
		return _chevron
	var img := Image.create(10, 14, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	for y in 14:
		var x := y if y < 7 else 13 - y
		for w in 3:
			var px := x + w - 1
			if px >= 0 and px < 10:
				img.set_pixel(px, y, Color.WHITE)
	_chevron = ImageTexture.create_from_image(img)
	return _chevron


static var _roots: Array[WeakRef] = []
static var _listening: bool = false


## Applies the theme to `root` and re-applies it while `root` lives and Settings change.
## One static listener serves every root (bound callables are not distinct connections).
static func apply(root: Control) -> void:
	root.theme = build(Settings.text_scale)
	_roots.append(weakref(root))
	if not _listening:
		_listening = true
		Settings.changed.connect(UiTheme._reapply_all)


static func _reapply_all() -> void:
	var alive: Array[WeakRef] = []
	var theme := build(Settings.text_scale)
	for ref in _roots:
		var root: Object = ref.get_ref()
		if root != null and is_instance_valid(root):
			root.theme = theme
			alive.append(ref)
	_roots = alive
