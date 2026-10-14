class_name InputPrompt
extends RefCounted
## W4-PROMPTS (D-UX2): the one look of an input prompt. Every screen's "[ESC]", "[ENTER]", "[Q]"
## is this chip: the same plate, only the glyph text differs. The glyph is read from the action's
## current binding (InputMap through Settings.key_text), on the device in use, and refreshes on
## Settings.hints_changed; a device switch (pad glyphs) plugs in by changing `chip_text` alone.

## Meta on a chip: the action it shows.
const META_ACTION := &"input_action"
const CHIP_NAME := "InputChip"
const CHIP_PAD_X := 6
const CHIP_PAD_Y := 1
const CHIP_BORDER := 1
const CHIP_RADIUS := 3


## The glyph text for `action` ("[ESC]"), "" when the device has no binding for it.
static func chip_text(action: StringName) -> String:
	return Settings.hint(action).to_upper()


## One chip for `action`: a plate with the glyph text inside; its label is `chip_label(chip)`.
static func make_chip(action: StringName) -> PanelContainer:
	var chip := PanelContainer.new()
	chip.name = CHIP_NAME
	chip.set_meta(META_ACTION, action)
	chip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	chip.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	var box := StyleBoxFlat.new()
	box.bg_color = Color(Palette.VINYL_INK, 0.85)
	box.border_color = PaletteSkins.chrome(Palette.NET_CYAN)
	box.set_border_width_all(CHIP_BORDER)
	box.set_corner_radius_all(CHIP_RADIUS)
	box.content_margin_left = CHIP_PAD_X
	box.content_margin_right = CHIP_PAD_X
	box.content_margin_top = CHIP_PAD_Y
	box.content_margin_bottom = CHIP_PAD_Y
	chip.add_theme_stylebox_override(&"panel", box)
	var l := Label.new()
	l.name = "Glyph"
	l.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_font_override(&"font", Palette.mono())
	l.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.CAPTION))
	l.add_theme_color_override(&"font_color", Palette.TEXT_HI)
	l.text = chip_text(action)
	chip.add_child(l)
	chip.visible = l.text != ""
	var refresh := func() -> void:
		l.text = chip_text(action)
		sync_visible(chip)
	Settings.hints_changed.connect(refresh)
	chip.tree_exiting.connect(func() -> void:
		if Settings.hints_changed.is_connected(refresh):
			Settings.hints_changed.disconnect(refresh))
	return chip


## Shows the chip when it has a glyph and the control it follows (if any) is visible.
static func sync_visible(chip: Control) -> void:
	var l := chip_label(chip)
	var f: Variant = chip.get_meta(&"follows") if chip.has_meta(&"follows") else null
	var on := l != null and l.text != ""
	if on and f is Control and is_instance_valid(f):
		on = (f as Control).visible
	chip.visible = on


## The chip's glyph label (tests, relabels).
static func chip_label(chip: Control) -> Label:
	return chip.get_node_or_null("Glyph") as Label


## A verb with its chip: [verb][chip], for rows of prompts.
static func make_pair(action: StringName, verb: String) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.add_theme_constant_override(&"separation", UiTheme.SP_S)
	var v := Chrome.caps_label(verb, UiTheme.CAPTION, Palette.TEXT_MID)
	v.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(v)
	row.add_child(make_chip(action))
	return row


## Puts a chip for `action` right after `button` in its parent (the button keeps only its verb).
## The chip is shown only while `button` is. Returns the chip.
static func after(button: Control, action: StringName) -> PanelContainer:
	var chip := make_chip(action)
	chip.set_meta(&"follows", button)
	var parent := button.get_parent()
	parent.add_child(chip)
	parent.move_child(chip, button.get_index() + 1)
	button.visibility_changed.connect(func() -> void:
		if is_instance_valid(chip):
			sync_visible(chip))
	sync_visible(chip)
	return chip


## Puts a chip for `action` on `button`'s top-right corner (a button that has no room beside it,
## like SEND IT at the screen's edge). It hides with the button. Returns the chip.
static func corner(button: Control, action: StringName, margin: float = 8.0) -> PanelContainer:
	var chip := make_chip(action)
	button.add_child(chip)
	chip.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	chip.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	chip.offset_right = -margin
	chip.offset_top = margin
	return chip


## The chip `after` / `inside` put by `button` (null when none): tests and relayouts.
static func chip_of(button: Control) -> Control:
	var p := button.get_parent()
	if p != null:
		for c in p.get_children():
			if c.has_meta(META_ACTION) and c.has_meta(&"follows") and c.get_meta(&"follows") == button:
				return c as Control
	for c in button.get_children():
		if c.has_meta(META_ACTION):
			return c as Control
	return null


## Puts a chip for `action` inside `button`, at its right edge (for a wide menu line whose
## layout must not change). The chip ignores the mouse. Returns the chip.
static func inside(button: Control, action: StringName, margin: float = 8.0) -> PanelContainer:
	var chip := make_chip(action)
	button.add_child(chip)
	chip.set_anchors_and_offsets_preset(Control.PRESET_CENTER_RIGHT)
	chip.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	chip.grow_vertical = Control.GROW_DIRECTION_BOTH
	chip.offset_right = -margin
	return chip
