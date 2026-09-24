class_name UiTheme
extends RefCounted
## Builds the shared Theme (STYLE_GUIDE 3): Share Tech Mono for system text, Anton for
## display, Permanent Marker for the Cell's voice, scaled by Settings.text_scale.

const BASE_SIZE := 15


static func build(text_scale: float = 1.0) -> Theme:
	var t := Theme.new()
	var size := roundi(BASE_SIZE * text_scale)
	t.default_font = Palette.mono()
	t.default_font_size = size
	for kind in ["Button", "Label", "RichTextLabel", "OptionButton", "SpinBox", "LineEdit", "CheckButton", "HSlider"]:
		t.set_font_size("font_size", kind, size)
		t.set_font("font", kind, Palette.mono())
	t.set_color("font_color", "Label", Palette.PAPER)
	t.set_color("default_color", "RichTextLabel", Palette.PAPER)
	t.set_color("font_color", "Button", Palette.PAPER)
	t.set_color("font_hover_color", "Button", Palette.CELL_ACID)
	t.set_color("font_focus_color", "Button", Palette.CELL_ACID)
	var normal := StyleBoxFlat.new()
	normal.bg_color = Color(Palette.DESK_METAL, 0.85)
	normal.border_color = Palette.NET_CYAN
	normal.set_border_width_all(1)
	normal.set_corner_radius_all(3)
	normal.content_margin_left = 8
	normal.content_margin_right = 8
	normal.content_margin_top = 3
	normal.content_margin_bottom = 3
	t.set_stylebox("normal", "Button", normal)
	var hover := normal.duplicate()
	hover.border_color = Palette.CELL_PINK
	hover.set_border_width_all(2)
	t.set_stylebox("hover", "Button", hover)
	var focus := normal.duplicate()
	focus.border_color = Palette.CELL_ACID
	focus.set_border_width_all(2)
	t.set_stylebox("focus", "Button", focus)
	var pressed := normal.duplicate()
	pressed.bg_color = Color(Palette.CELL_PINK, 0.35)
	t.set_stylebox("pressed", "Button", pressed)
	var disabled := normal.duplicate()
	disabled.bg_color = Color(Palette.DESK_DARK, 0.6)
	disabled.border_color = Color(Palette.NET_CYAN, 0.3)
	t.set_stylebox("disabled", "Button", disabled)
	t.set_color("font_disabled_color", "Button", Color(Palette.PAPER, 0.4))
	var panel := StyleBoxFlat.new()
	panel.bg_color = Color(0, 0, 0, 0)
	t.set_stylebox("panel", "PanelContainer", panel)
	return t


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
