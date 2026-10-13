class_name LegendChip
extends Button
## W2-A3: the "?" terminal chip beside the fight's Settings chip: it opens the CombatLegend.
## Same size and look as SettingsIconChip; focusable, so the pad reaches it. View only.


func _init() -> void:
	name = "LegendChip"
	flat = true
	focus_mode = Control.FOCUS_ALL
	for st in ["normal", "hover", "pressed", "focus", "disabled", "hover_pressed"]:
		add_theme_stylebox_override(st, StyleBoxEmpty.new())
	mouse_entered.connect(queue_redraw)
	mouse_exited.connect(queue_redraw)
	focus_entered.connect(queue_redraw)
	focus_exited.connect(queue_redraw)
	_refit()


func _ready() -> void:
	Settings.changed.connect(_refit)


func _exit_tree() -> void:
	if Settings.changed.is_connected(_refit):
		Settings.changed.disconnect(_refit)


func _refit() -> void:
	custom_minimum_size = Vector2.ONE * SettingsIconChip.side_px()
	queue_redraw()


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	var hot := is_hovered() or button_pressed
	HudSkin.draw_terminal_panel(self, r, HudSkin.TERMINAL_HI if hot else PaletteSkins.chrome(HudSkin.TERMINAL_EDGE), PaletteSkins.chrome(Palette.TERMINAL_BG_HOT) if hot else PaletteSkins.chrome(HudSkin.TERMINAL_BG))
	var fs := roundi(size.y * 0.62)
	var f := HudSkin.display()
	var w := f.get_string_size("?", HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	HighContrast.draw_text(self, f, Vector2((size.x - w) * 0.5, size.y * 0.5 + f.get_ascent(fs) * 0.5 - 1.0), "?", HORIZONTAL_ALIGNMENT_LEFT, -1, fs,
		HudSkin.TERMINAL_HI if hot else HudSkin.TERMINAL_TEXT)
	if has_focus():
		KitState.draw_frame(self, r, KitState.FOCUS)
